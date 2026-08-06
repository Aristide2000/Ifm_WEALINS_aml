"""
Modèles ML AML — Wealins
Isolation Forest + XGBoost + SHAP
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import xgboost as xgb
import shap
import pickle
import os


# ─── Feature Engineering ──────────────────────────────────────
def creer_features(
    clients_df: pd.DataFrame,
    contrats_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
    scores_df: pd.DataFrame = None,
) -> pd.DataFrame:
    """
    Crée les features ML à partir des données brutes.

    Returns:
        DataFrame avec une ligne par contrat
        et toutes les features calculées
    """

    features = []

    for _, contrat in contrats_df.iterrows():

        # Client associé
        client_rows = clients_df[
            clients_df["id_client"] == contrat["id_client"]
        ]
        if len(client_rows) == 0:
            continue
        client = client_rows.iloc[0]

        # Transactions du contrat
        trx = transactions_df[
            transactions_df["id_contrat"] == contrat["id_contrat"]
        ]
        rachats    = trx[trx["code_type_evt"] == "RAP"]
        versements = trx[trx["code_type_evt"].isin(["OUV", "VLC"])]

        # Score LC 18/9
        score_lc189 = 0
        if scores_df is not None:
            score_rows = scores_df[
                scores_df["id_contrat"] == contrat["id_contrat"]
            ]
            if len(score_rows) > 0:
                score_lc189 = score_rows.iloc[0]["score_total"]

        # Délai minimum avant rachat
        date_sousc       = pd.to_datetime(
            contrat["date_souscription"]
        ).date()
        delai_min_rachat = 9999
        if len(rachats) > 0:
            for _, r in rachats.iterrows():
                date_r = pd.to_datetime(r["date_effet"]).date()
                delai  = (date_r - date_sousc).days
                delai_min_rachat = min(delai_min_rachat, delai)

        # Ratio rachat / prime
        ratio_rachat = (
            contrat["somme_rachats"] / contrat["prime_initiale"]
            if contrat["prime_initiale"] > 0 else 0
        )

        # Perte acceptée
        perte_acceptee = (
            rachats["perte_acceptee"].any()
            if len(rachats) > 0 else False
        )

        # Tiers payeur
        tiers_payeur = trx["est_tiers_payeur"].any()

        # Risque pays
        from config.pays_risque import get_score_pays
        risque_pays_client = get_score_pays(
            client["pays_residence"]
        )
        risque_pays_banque = get_score_pays(
            contrat["pays_intermediaire"]
        )

        # Label
        est_suspect = (
            trx["est_suspect"].any()
            if "est_suspect" in trx.columns else False
        )

        features.append({
            # Identifiants
            "id_contrat":             contrat["id_contrat"],
            "id_client":              client["id_client"],

            # Features client
            "est_pep":                int(client["est_pep"]),
            "est_mep":                int(client["est_mep"]),
            "est_sous_sanctions":     int(client["est_sous_sanctions"]),
            "risque_pays_client":     risque_pays_client,
            "patrimoine_declare":     client["patrimoine_declare"],
            "revenus_declare":        client["revenus_declare"],
            "est_structure_morale":   int(
                client["structure_juridique"] == "moral"
            ),
            "screening_hit":          int(
                client["screening_worldcheck"] == "hit"
            ),

            # Features contrat
            "prime_initiale":         contrat["prime_initiale"],
            "flag_nantissement":      int(contrat["flag_nantissement"]),
            "risque_pays_banque":     risque_pays_banque,

            # Features transactions
            "nb_transactions":        len(trx),
            "nb_rachats":             len(rachats),
            "nb_versements":          len(versements),
            "ratio_rachat_prime":     round(ratio_rachat, 4),
            "delai_min_rachat_jours": delai_min_rachat,
            "perte_acceptee":         int(perte_acceptee),
            "tiers_payeur":           int(tiers_payeur),

            # Score réglementaire
            "score_lc189":            score_lc189,
            "is_high_lc189":          int(score_lc189 > 15),
            "is_medium_lc189":        int(10 < score_lc189 <= 15),

            # Label
            "est_suspect":            int(est_suspect),
        })

    return pd.DataFrame(features)


# ─── Isolation Forest ─────────────────────────────────────────
def entrainer_isolation_forest(
    features_df: pd.DataFrame,
    contamination: float = 0.05,
) -> tuple:
    """
    Entraîne un Isolation Forest pour détecter les anomalies.

    Returns:
        (modele, features_df avec scores)
    """

    cols_features = [
        c for c in features_df.columns
        if c not in ["id_contrat", "id_client", "est_suspect"]
    ]

    X = features_df[cols_features].fillna(0)

    modele = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100,
    )
    modele.fit(X)

    scores_bruts = modele.decision_function(X)

    # Normaliser entre 0 et 1 — 1 = très suspect
    scores_norm = 1 - (
        (scores_bruts - scores_bruts.min()) /
        (scores_bruts.max() - scores_bruts.min())
    )

    features_df                          = features_df.copy()
    features_df["score_isolation_forest"] = scores_norm
    features_df["prediction_if"]          = modele.predict(X)

    nb_anomalies = (features_df["prediction_if"] == -1).sum()
    print(f"\n Isolation Forest :")
    print(f"   Anomalies detectees : {nb_anomalies}")
    print(f"   Score moyen         : {scores_norm.mean():.3f}")
    print(f"   Score max           : {scores_norm.max():.3f}")

    return modele, features_df


# ─── XGBoost ──────────────────────────────────────────────────
def entrainer_xgboost(
    features_df: pd.DataFrame,
) -> tuple:
    """
    Entraîne un XGBoost pour la classification supervisée.

    Returns:
        (modele, metriques, feature_importance)
    """

    cols_features = [
        c for c in features_df.columns
        if c not in [
            "id_contrat", "id_client", "est_suspect",
            "score_isolation_forest", "prediction_if"
        ]
    ]

    X = features_df[cols_features].fillna(0)
    y = features_df["est_suspect"]

    if y.nunique() < 2:
        print("  Pas assez de labels pour XGBoost")
        return None, None, None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    scale_pos = (y_train == 0).sum() / (y_train == 1).sum()

    modele = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        scale_pos_weight=scale_pos,
        random_state=42,
        eval_metric="auc",
        verbosity=0,
    )
    modele.fit(X_train, y_train)

    y_pred_proba = modele.predict_proba(X_test)[:, 1]
    auc          = roc_auc_score(y_test, y_pred_proba)

    print(f"\n XGBoost :")
    print(f"   AUC          : {auc:.3f}")
    print(f"   Train size   : {len(X_train)}")
    print(f"   Test size    : {len(X_test)}")

    metriques = {
        "auc":        auc,
        "n_train":    len(X_train),
        "n_test":     len(X_test),
        "n_suspects": int(y.sum()),
    }

    importance = pd.DataFrame({
        "feature":    cols_features,
        "importance": modele.feature_importances_,
    }).sort_values("importance", ascending=False)

    print(f"\n Top 5 features importantes :")
    for _, row in importance.head(5).iterrows():
        print(f"   {row['feature']:35s} : {row['importance']:.3f}")

    return modele, metriques, importance


# ─── SHAP Values ──────────────────────────────────────────────
def calculer_shap(
    modele_xgb,
    features_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calcule les SHAP values pour l'explicabilité.

    Returns:
        DataFrame avec SHAP values par contrat
    """

    cols_features = [
        c for c in features_df.columns
        if c not in [
            "id_contrat", "id_client", "est_suspect",
            "score_isolation_forest", "prediction_if"
        ]
    ]

    X = features_df[cols_features].fillna(0)

    explainer  = shap.TreeExplainer(modele_xgb)
    shap_values = explainer.shap_values(X)

    shap_df = pd.DataFrame(
        shap_values,
        columns=cols_features
    )
    shap_df["id_contrat"] = features_df["id_contrat"].values

    return shap_df


# ─── Sauvegarder les modèles ──────────────────────────────────
def sauvegarder_modeles(
    modele_if,
    modele_xgb,
    path: str = "results/models/",
) -> None:
    """Sauvegarde les modèles entraînés."""

    os.makedirs(path, exist_ok=True)

    with open(f"{path}isolation_forest.pkl", "wb") as f:
        pickle.dump(modele_if, f)

    if modele_xgb is not None:
        modele_xgb.save_model(f"{path}xgboost.json")

    print(f"\n Modeles sauvegardes dans {path}")


# ─── Pipeline ML complet ──────────────────────────────────────
def pipeline_ml(
    clients_df: pd.DataFrame,
    contrats_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
    scores_df: pd.DataFrame = None,
    save: bool = True,
) -> dict:
    """
    Pipeline ML complet :
    Features → Isolation Forest → XGBoost → SHAP
    """

    print("\n Feature Engineering...")
    features_df = creer_features(
        clients_df, contrats_df,
        transactions_df, scores_df
    )
    print(f"   {len(features_df)} contrats — "
          f"{len(features_df.columns)} features")

    print("\n Isolation Forest...")
    modele_if, features_df = entrainer_isolation_forest(features_df)

    print("\n XGBoost...")
    modele_xgb, metriques, importance = entrainer_xgboost(features_df)

    shap_df = None
    if modele_xgb is not None:
        print("\n SHAP Values...")
        shap_df = calculer_shap(modele_xgb, features_df)
        print("   SHAP calcule")

    if save:
        sauvegarder_modeles(modele_if, modele_xgb)

    return {
        "features":   features_df,
        "modele_if":  modele_if,
        "modele_xgb": modele_xgb,
        "metriques":  metriques,
        "importance": importance,
        "shap":       shap_df,
    }