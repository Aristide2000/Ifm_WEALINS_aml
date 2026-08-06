"""
Rules Engine AML — Wealins
Détection basée sur les règles métier
tirées directement de la procédure AML/FT
section 5.2 — Transactions atypiques
"""

import pandas as pd
from datetime import date, timedelta
from config.pays_risque import get_classification_pays


# ─── Définition des règles ────────────────────────────────────
REGLES = {
    "R01": {
        "nom":         "Rachat précoce",
        "description": "Rachat dans les 6 mois suivant la souscription",
        "score":       0.75,
        "niveau":      "HIGH",
        "source":      "Procédure AML section 5.2",
    },
    "R02": {
        "nom":         "Perte acceptée",
        "description": "Rachat avec pénalités disproportionnées acceptées",
        "score":       0.80,
        "niveau":      "HIGH",
        "source":      "LC 18/9 — Question I45",
    },
    "R03": {
        "nom":         "Pays interdit",
        "description": "Transaction vers ou depuis un pays interdit",
        "score":       1.00,
        "niveau":      "CRITICAL",
        "source":      "Classification pays Wealins",
    },
    "R04": {
        "nom":         "Tiers payeur",
        "description": "Paiement effectué par un tiers non justifié",
        "score":       0.65,
        "niveau":      "MEDIUM",
        "source":      "Procédure AML section 5.2",
    },
    "R05": {
        "nom":         "PEP avec rachat",
        "description": "Client PEP effectuant un rachat",
        "score":       0.85,
        "niveau":      "HIGH",
        "source":      "Procédure AML — Vigilance renforcée PEP",
    },
    "R06": {
        "nom":         "Score LC189 élevé",
        "description": "Score LC 18/9 supérieur à 15",
        "score":       0.70,
        "niveau":      "HIGH",
        "source":      "LC 18/9 — Seuil HIGH",
    },
    "R07": {
        "nom":         "Pays élevé dans les flux",
        "description": "Banque origine ou destination dans pays à risque élevé",
        "score":       0.60,
        "niveau":      "MEDIUM",
        "source":      "LC 18/9 — Questions I20 / I47",
    },
    "R08": {
        "nom":         "Structure opaque",
        "description": "Client avec structure juridique complexe (personne morale)",
        "score":       0.55,
        "niveau":      "MEDIUM",
        "source":      "LC 18/9 — Question I12",
    },
    "R09": {
        "nom":         "Rachat précoce et perte combinés",
        "description": "Rachat précoce ET perte acceptée simultanément",
        "score":       0.95,
        "niveau":      "CRITICAL",
        "source":      "LC 18/9 — Question I50",
    },
    "R10": {
        "nom":         "Rachats multiples",
        "description": "Plus de 2 rachats sur les 2 dernières années",
        "score":       0.65,
        "niveau":      "MEDIUM",
        "source":      "LC 18/9 — Question I44",
    },
    "R11": {
        "nom":         "Arbitrages fréquents",
        "description": "Plus de 3 arbitrages sur les 12 derniers mois",
        "score":       0.60,
        "niveau":      "MEDIUM",
        "source":      "Procédure AML section 5.2",
    },
    "R12": {
        "nom":         "Arbitrage vers fonds offshore",
        "description": "Arbitrage vers un fonds dans une juridiction à risque",
        "score":       0.75,
        "niveau":      "HIGH",
        "source":      "LC 18/9 — Questions I35/I36",
    },
}


# ─── Fonction utilitaire ──────────────────────────────────────
def _creer_alerte(
    id_contrat: str,
    code_regle: str,
    detail: str,
) -> dict:
    """Crée une alerte AML."""
    regle = REGLES[code_regle]
    return {
        "id_contrat":     id_contrat,
        "code_regle":     code_regle,
        "nom_regle":      regle["nom"],
        "description":    regle["description"],
        "detail":         detail,
        "score_risque":   regle["score"],
        "niveau":         regle["niveau"],
        "source":         regle["source"],
        "date_detection": str(date.today()),
    }


# ─── Moteur de règles principal ───────────────────────────────
def appliquer_regles(
    client: pd.Series,
    contrat: pd.Series,
    transactions: pd.DataFrame,
    score_lc189: int = 0,
) -> list:
    """
    Applique toutes les règles AML sur un contrat.

    Returns:
        Liste des alertes déclenchées
    """

    alertes    = []
    trx        = transactions[
        transactions["id_contrat"] == contrat["id_contrat"]
    ]
    rachats    = trx[trx["code_type_evt"] == "RAP"]
    arbitrages = trx[trx["code_type_evt"] == "ARB"]
    date_sousc = pd.to_datetime(
        contrat["date_souscription"]
    ).date()

    # ── R01 — Rachat précoce ──────────────────────
    for _, r in rachats.iterrows():
        date_r = pd.to_datetime(r["date_effet"]).date()
        delai  = (date_r - date_sousc).days
        if delai < 180:
            alertes.append(_creer_alerte(
                contrat["id_contrat"],
                "R01",
                f"Rachat après {delai} jours (< 180 jours)",
            ))
            break

    # ── R02 — Perte acceptée ──────────────────────
    if len(rachats) > 0 and rachats["perte_acceptee"].any():
        alertes.append(_creer_alerte(
            contrat["id_contrat"],
            "R02",
            "Rachat avec pénalités acceptées détecté",
        ))

    # ── R03 — Pays interdit ───────────────────────
    for _, t in trx.iterrows():
        if pd.notna(t.get("pays_banque_origine")) and \
           get_classification_pays(
               t["pays_banque_origine"]
           ) == "INTERDIT":
            alertes.append(_creer_alerte(
                contrat["id_contrat"],
                "R03",
                f"Origine fonds pays interdit : "
                f"{t['pays_banque_origine']}",
            ))
            break
        if pd.notna(t.get("pays_banque_dest")) and \
           get_classification_pays(
               t["pays_banque_dest"]
           ) == "INTERDIT":
            alertes.append(_creer_alerte(
                contrat["id_contrat"],
                "R03",
                f"Destination fonds pays interdit : "
                f"{t['pays_banque_dest']}",
            ))
            break

    # ── R04 — Tiers payeur ────────────────────────
    if trx["est_tiers_payeur"].any():
        alertes.append(_creer_alerte(
            contrat["id_contrat"],
            "R04",
            "Paiement par tiers détecté",
        ))

    # ── R05 — PEP avec rachat ─────────────────────
    if client["est_pep"] and len(rachats) > 0:
        alertes.append(_creer_alerte(
            contrat["id_contrat"],
            "R05",
            f"Client PEP ({client.get('type_pep', 'PPE')}) "
            f"avec {len(rachats)} rachat(s)",
        ))

    # ── R06 — Score LC 18/9 élevé ─────────────────
    if score_lc189 > 15:
        alertes.append(_creer_alerte(
            contrat["id_contrat"],
            "R06",
            f"Score LC 18/9 = {score_lc189} > 15",
        ))

    # ── R07 — Pays élevé dans les flux ────────────
    for _, t in trx.iterrows():
        if pd.notna(t.get("pays_banque_origine")) and \
           get_classification_pays(
               t["pays_banque_origine"]
           ) == "ELEVE":
            alertes.append(_creer_alerte(
                contrat["id_contrat"],
                "R07",
                f"Banque origine dans pays élevé : "
                f"{t['pays_banque_origine']}",
            ))
            break

    # ── R08 — Structure opaque ────────────────────
    if client["structure_juridique"] == "moral":
        alertes.append(_creer_alerte(
            contrat["id_contrat"],
            "R08",
            "Client avec structure juridique morale",
        ))

    # ── R09 — Rachat précoce + perte combinés ─────
    rachat_precoce = False
    perte          = False
    for _, r in rachats.iterrows():
        date_r = pd.to_datetime(r["date_effet"]).date()
        if (date_r - date_sousc).days < 180:
            rachat_precoce = True
        if r["perte_acceptee"]:
            perte = True
    if rachat_precoce and perte:
        alertes.append(_creer_alerte(
            contrat["id_contrat"],
            "R09",
            "Rachat précoce ET perte acceptée — "
            "pattern blanchiment classique",
        ))

    # ── R10 — Rachats multiples ───────────────────
    date_2ans      = date.today() - timedelta(days=730)
    rachats_recents = rachats[
        pd.to_datetime(rachats["date_effet"]).dt.date >= date_2ans
    ]
    if len(rachats_recents) > 2:
        alertes.append(_creer_alerte(
            contrat["id_contrat"],
            "R10",
            f"{len(rachats_recents)} rachats "
            f"sur les 2 dernières années",
        ))

    # ── R11 — Arbitrages fréquents ───────────────
    date_12mois = date.today() - timedelta(days=365)
    arb_recents = arbitrages[
        pd.to_datetime(arbitrages["date_effet"]).dt.date >= date_12mois
    ]
    if len(arb_recents) > 3:
        alertes.append(_creer_alerte(
            contrat["id_contrat"],
            "R11",
            f"{len(arb_recents)} arbitrages "
            f"sur les 12 derniers mois",
        ))

    # ── R12 — Arbitrage vers fonds offshore ──────
    for _, arb in arbitrages.iterrows():
        if pd.notna(arb.get("fonds_cible")):
            if "CAY" in str(arb["fonds_cible"]) or \
               "PE_CAY" in str(arb["fonds_cible"]):
                alertes.append(_creer_alerte(
                    contrat["id_contrat"],
                    "R12",
                    f"Arbitrage vers fonds suspect : "
                    f"{arb['fonds_cible']}",
                ))
                break

    return alertes


# ─── Analyse du portefeuille ──────────────────────────────────
def analyser_portefeuille(
    clients_df: pd.DataFrame,
    contrats_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
    scores_df: pd.DataFrame = None,
) -> pd.DataFrame:
    """
    Applique les règles sur tout le portefeuille.

    Returns:
        DataFrame de toutes les alertes générées
    """

    toutes_alertes = []

    for _, contrat in contrats_df.iterrows():

        client_rows = clients_df[
            clients_df["id_client"] == contrat["id_client"]
        ]
        if len(client_rows) == 0:
            continue

        client = client_rows.iloc[0]

        score_lc189 = 0
        if scores_df is not None:
            score_rows = scores_df[
                scores_df["id_contrat"] == contrat["id_contrat"]
            ]
            if len(score_rows) > 0:
                score_lc189 = score_rows.iloc[0]["score_total"]

        alertes = appliquer_regles(
            client, contrat, transactions_df, score_lc189
        )
        toutes_alertes.extend(alertes)

    alertes_df = pd.DataFrame(toutes_alertes)

    if len(alertes_df) > 0:
        print("\n Resultats du rules engine :")
        print(f"   Alertes generees : {len(alertes_df):,}")
        dist = alertes_df["niveau"].value_counts()
        for niveau, count in dist.items():
            print(f"   {niveau:10s} : {count:4d}")

    return alertes_df