"""
Pipeline AML complet — Wealins
Connecte toutes les etapes :
Donnees -> Scoring -> Rules -> ML -> Alertes
"""

import pandas as pd
from datetime import date
from src.data.generateur import generer_dataset_complet
from src.scoring.scoring_lc189 import scorer_portefeuille
from src.detection.rules_engine import analyser_portefeuille
from src.detection.modele_ml import pipeline_ml


def run_pipeline(
    nb_clients: int = 1000,
    save: bool = True,
    verbose: bool = True,
) -> dict:
    """
    Lance le pipeline AML complet.
    """

    if verbose:
        print("=" * 50)
        print("  WEALINS AML PIPELINE")
        print(f"  {date.today()}")
        print("=" * 50)

    # ── Etape 1 — Donnees ─────────────────────────
    if verbose:
        print("\n ETAPE 1 - Donnees")

    dataset = generer_dataset_complet(
        nb_clients=nb_clients,
        save=save
    )

    clients      = dataset["clients"]
    contrats     = dataset["contrats"]
    transactions = dataset["transactions"]
    fonds        = dataset["fonds"]
    roles        = dataset["roles"]

    # ── Etape 2 — Scoring LC 18/9 ─────────────────
    if verbose:
        print("\n ETAPE 2 - Scoring LC 18/9")

    scores = scorer_portefeuille(
        clients, contrats, transactions
    )

    # Mettre a jour les contrats avec les scores
    if len(scores) > 0:
        contrats = contrats.merge(
            scores[["id_contrat",
                    "score_total",
                    "classification"]],
            on="id_contrat",
            how="left"
        )
        contrats["score_lc189"]    = contrats["score_total"].fillna(0)
        contrats["risque_contrat"] = contrats["classification"].fillna("LOW")

    # ── Etape 3 — Rules Engine ────────────────────
    if verbose:
        print("\n ETAPE 3 - Rules Engine")

    alertes_rules = analyser_portefeuille(
        clients, contrats, transactions, scores
    )

    # Alertes fonds offshore
    alertes_offshore = []
    for _, f in fonds.iterrows():
        if f["est_offshore"]:
            alertes_offshore.append({
                "id_contrat":     f["id_contrat"],
                "code_regle":     "R_OFFSHORE",
                "nom_regle":      "Fonds offshore detecte",
                "description":    "Fonds dans juridiction offshore",
                "detail":         f"Fonds {f['designation']} - {f['juridiction']}",
                "score_risque":   0.70,
                "niveau":         "HIGH",
                "source":         "Analyse fonds UC",
                "date_detection": str(date.today()),
            })

    if alertes_offshore:
        alertes_rules = pd.concat([
            alertes_rules,
            pd.DataFrame(alertes_offshore)
        ], ignore_index=True)
        if verbose:
            print(f"   + {len(alertes_offshore)} alertes fonds offshore")

    # ── Etape 4 — Modeles ML ──────────────────────
    if verbose:
        print("\n ETAPE 4 - Modeles ML")

    resultats_ml = pipeline_ml(
        clients, contrats, transactions,
        scores_df=scores,
        save=save,
    )

    # ── Etape 5 — Consolidation ───────────────────
    if verbose:
        print("\n ETAPE 5 - Consolidation")

    features = resultats_ml["features"]

    # Alertes ML
    alertes_ml = []
    if len(features) > 0:
        suspects_ml = features[
            features["score_isolation_forest"] > 0.7
        ]
        for _, row in suspects_ml.iterrows():
            alertes_ml.append({
                "id_contrat":     row["id_contrat"],
                "code_regle":     "ML_IF",
                "nom_regle":      "Anomalie ML",
                "description":    "Isolation Forest - score eleve",
                "detail":         f"Score IF = {row['score_isolation_forest']:.3f}",
                "score_risque":   row["score_isolation_forest"],
                "niveau":         "HIGH" if row["score_isolation_forest"] > 0.85
                                  else "MEDIUM",
                "source":         "Isolation Forest",
                "date_detection": str(date.today()),
            })

    alertes_ml_df = pd.DataFrame(alertes_ml)

    # Combiner toutes les alertes
    toutes_alertes = pd.concat(
        [alertes_rules, alertes_ml_df],
        ignore_index=True
    ) if len(alertes_ml_df) > 0 else alertes_rules

    # Sauvegarder
    if save and len(toutes_alertes) > 0:
        toutes_alertes.to_csv(
            "data/synthetic/alertes.csv",
            index=False
        )

    # ── Resume final ──────────────────────────────
    if verbose:
        print("\n" + "=" * 50)
        print("  RESUME FINAL")
        print("=" * 50)
        print(f"  Clients      : {len(clients):,}")
        print(f"  Contrats     : {len(contrats):,}")
        print(f"  Fonds UC     : {len(fonds):,}")
        print(f"  Transactions : {len(transactions):,}")
        print(f"  Roles        : {len(roles):,}")
        print(f"  Scores       : {len(scores):,}")
        if len(toutes_alertes) > 0:
            print(f"  Alertes      : {len(toutes_alertes):,}")
            dist = toutes_alertes["niveau"].value_counts()
            for niveau, count in dist.items():
                print(f"    {niveau:10s} : {count:4d}")
        print("=" * 50)

    return {
        "clients":      clients,
        "contrats":     contrats,
        "fonds":        fonds,
        "transactions": transactions,
        "roles":        roles,
        "scores":       scores,
        "alertes":      toutes_alertes,
        "features":     features,
        "modele_if":    resultats_ml["modele_if"],
        "modele_xgb":   resultats_ml["modele_xgb"],
        "importance":   resultats_ml["importance"],
        "shap":         resultats_ml["shap"],
    }


# ─── Point d'entree ───────────────────────────────────────────
if __name__ == "__main__":
    resultats = run_pipeline(nb_clients=1000)