"""
Moteur de scoring LC 18/9 — Wealins AML
Calcule automatiquement le score AML
d'un contrat selon les 51 questions officielles
"""

import pandas as pd
from datetime import date
from config.questions_lc189 import calculer_score, SEUILS
from config.pays_risque import get_classification_pays


def _get_reponse_pays(pays: str) -> str:
    """
    Convertit un pays en réponse LC 18/9.
    a = Luxembourg
    b = Pays faible
    c = Pays moyen
    d = Pays élevé
    """
    risque = get_classification_pays(pays)
    mapping = {
        "FAIBLE":   "b",
        "MOYEN":    "c",
        "ELEVE":    "d",
        "INTERDIT": "d",
        "INCONNU":  "b",
    }
    if pays == "Luxembourg":
        return "a"
    return mapping.get(risque, "b")


def scorer_contrat(
    client: pd.Series,
    contrat: pd.Series,
    transactions: pd.DataFrame,
) -> dict:
    """
    Calcule le score LC 18/9 d'un contrat.

    Args:
        client       : ligne du DataFrame clients
        contrat      : ligne du DataFrame contrats
        transactions : toutes les transactions

    Returns:
        dict avec score, classification, détails
    """

    # ─── Calculs préliminaires ────────────────────
    trx_contrat = transactions[
        transactions["id_contrat"] == contrat["id_contrat"]
    ]

    # Rachats
    rachats = trx_contrat[
        trx_contrat["code_type_evt"] == "RAP"
    ]

    # Nombre de rachats sur 2 ans
    nb_rachats_2ans = len(rachats[
        pd.to_datetime(rachats["date_effet"]).dt.date >=
        date.today().replace(year=date.today().year - 2)
    ])

    # Rachat précoce + perte + tiers payeur
    date_sousc     = pd.to_datetime(contrat["date_souscription"]).date()
    rachat_precoce = False
    perte_acceptee = False
    tiers_payeur   = False

    if len(rachats) > 0:
        for _, r in rachats.iterrows():
            date_rachat = pd.to_datetime(r["date_effet"]).date()
            delai       = (date_rachat - date_sousc).days
            if delai < 180:
                rachat_precoce = True
            if r["perte_acceptee"]:
                perte_acceptee = True

    if len(trx_contrat) > 0:
        tiers_payeur = trx_contrat["est_tiers_payeur"].any()

    # Prime
    prime = contrat["prime_initiale"]

    # Est personne morale
    est_moral = client["structure_juridique"] == "moral"

    # ─── Construction des réponses ────────────────
    reponses = {

        # Identité et géographie
        "I01": "CAP" if contrat["type_produit"] == "CAP" else "AV",
        "I02": _get_reponse_pays(client["pays_residence"]),
        "I03": False,
        "I04": est_moral,                    # → I04 Personne morale
        "I05": _get_reponse_pays(client["pays_residence"]),
        "I06": _get_reponse_pays(client["pays_residence"]),
        "I07": _get_reponse_pays(client["nationalite"]),
        "I08": _get_reponse_pays(client["nationalite"]),
        "I09": _get_reponse_pays(client["nationalite"]),
        "I10": False,

        # Documents et statuts sensibles
        "I11": False,                        # Documents toujours obtenus
        "I12": est_moral,                    # → I12 Montage spécial
        "I13": client["est_declare_crf"],    # → I13 Déclaré CRF
        "I14": client["est_sous_sanctions"], # → I14 Sanctions
        "I15": client["est_pep"],            # → I15 PEP
        "I16": client["profession"] in [     # → I16 Profession sensible
            "Ancien ministre", "Diplomate",
            "Parlementaire", "Haut fonctionnaire",
            "Directeur banque centrale",
        ],
        "I17": client["screening_worldcheck"] == "hit",  # → I17 Background check
        "I18": False,
        "I19": False,

        # Origine des fonds
        "I20": _get_reponse_pays(contrat["pays_intermediaire"]),
        "I21": (
            get_classification_pays(contrat["pays_intermediaire"])
            != "FAIBLE"
        ),
        "I22": 250_000 <= prime <= 2_500_000,
        "I23": prime > 2_500_000,
        "I24": False,
        "I25": False,
        "I26": False,
        "I27": tiers_payeur,

        # Clause bénéficiaire
        "I28": False,
        "I29": est_moral,
        "I30": False,
        "I31": False,
        "I32": contrat["flag_nantissement"],
        "I33": False,
        "I34": False,

        # Actifs non cotés
        "I35": False,
        "I36": False,
        "I37": False,

        # Intermédiaire
        "I38": (
            get_classification_pays(contrat["pays_intermediaire"])
            in ["ELEVE", "INTERDIT"]
        ),
        "I39": (
            contrat["pays_intermediaire"] != client["pays_residence"]
        ),
        "I40": False,
        "I41": False,
        "I42": False,
        "I43": False,

        # Rachats
        "I44": min(nb_rachats_2ans, 3),
        "I45": perte_acceptee,
        "I46": False,
        "I47": _get_reponse_pays(
            contrat["pays_intermediaire"]
        ) if len(rachats) > 0 else "NA",
        "I48": False,
        "I49": False,
        "I50": rachat_precoce and perte_acceptee,
        "I51": (
            client["est_sous_sanctions"] or
            get_classification_pays(
                client["pays_residence"]
            ) == "INTERDIT"
        ),
    }

    # ─── Calcul du score ──────────────────────────
    resultat = calculer_score(reponses)

    return {
        "id_contrat":      contrat["id_contrat"],
        "id_client":       client["id_client"],
        "score_total":     resultat["score_total"],
        "classification":  resultat["classification"],
        "flags_high_auto": resultat["flags_high_auto"],
        "reponses":        reponses,
        "details":         resultat["details"],
    }


def scorer_portefeuille(
    clients_df: pd.DataFrame,
    contrats_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Score tous les contrats du portefeuille.

    Returns:
        DataFrame avec scores et classifications
    """

    scores = []

    for _, contrat in contrats_df.iterrows():

        client_rows = clients_df[
            clients_df["id_client"] == contrat["id_client"]
        ]
        if len(client_rows) == 0:
            continue

        client = client_rows.iloc[0]
        score  = scorer_contrat(client, contrat, transactions_df)
        scores.append(score)

    scores_df = pd.DataFrame(scores)

    print("\n Résultats du scoring :")
    print(f"   Contrats scorés : {len(scores_df):,}")
    if len(scores_df) > 0:
        dist = scores_df["classification"].value_counts()
        for niveau, count in dist.items():
            pct = count / len(scores_df) * 100
            print(f"   {niveau:8s} : {count:4d} ({pct:.1f}%)")

    return scores_df