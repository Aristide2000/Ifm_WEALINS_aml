"""
Générateur de données synthétiques — Wealins AML
Structure inspirée du format Penelop / Lifeware Wealins
Données 100% fictives — aucune donnée réelle

Sources :
- Pays et poids    : prov math client prices report (interne Wealins)
- Structure client : données internes Wealins (15 248 physique / 1 015 moral)
- Produits         : Liste des produits autorisés Wealins (sept. 2025)
- Fonds UC         : présentation département Investment Wealins S.A.
"""

import random
import pandas as pd
import numpy as np
from faker import Faker
from datetime import date, timedelta
from config.pays_risque import (
    get_score_pays,
    get_classification_pays,
    PAYS_LISTE,
    PAYS_POIDS,
)

# ─── Configuration ────────────────────────────────────────────
fake = Faker('fr_FR')
random.seed(42)
np.random.seed(42)

# ─── Produits Wealins ─────────────────────────────────────────
# Source : Liste des produits autorisés Wealins (sept. 2025)
PRODUITS = {
    # Produits actifs
    "WEALIFE_BE": {"label": "Wealins Life Belgium",           "type": "AV",  "statut": "actif",  "marche": "Belgium"},
    "WEALIFE_FR": {"label": "Wealins Life France",            "type": "AV",  "statut": "actif",  "marche": "France"},
    "WEACAP_FR":  {"label": "Wealins Capi France",            "type": "CAP", "statut": "actif",  "marche": "France"},
    "WEALIFE_LU": {"label": "Wealins Life Luxembourg",        "type": "AV",  "statut": "actif",  "marche": "Luxembourg"},
    "WEACAP_LU":  {"label": "Wealins Capi Luxembourg",        "type": "CAP", "statut": "actif",  "marche": "Luxembourg"},
    "WEALIFE_MC": {"label": "Wealins Life Monaco",            "type": "AV",  "statut": "actif",  "marche": "Monaco"},
    "WEACAP_MC":  {"label": "Wealins Capi Monaco",            "type": "CAP", "statut": "actif",  "marche": "Monaco"},
    "WEALIFE_IT": {"label": "Wealins Life Italy +",           "type": "AV",  "statut": "actif",  "marche": "Italy"},
    "WEALIFE_PT": {"label": "Wealins Life Portugal",          "type": "AV",  "statut": "actif",  "marche": "Portugal"},
    "WEALIFE_ES": {"label": "Wealins Life Spain",             "type": "AV",  "statut": "actif",  "marche": "Spain"},
    "WEACAP_FI":  {"label": "Wealins Capitalisation Finland", "type": "CAP", "statut": "actif",  "marche": "Finland"},
    "WEALIFE_FI": {"label": "Wealins Life Finland",           "type": "AV",  "statut": "actif",  "marche": "Finland"},
    "WEALIFE_SE": {"label": "Wealins Life Sweden",            "type": "AV",  "statut": "actif",  "marche": "Sweden"},
    "WEALIFE_NO": {"label": "Wealins Life Norway",            "type": "AV",  "statut": "actif",  "marche": "Norway"},
    "PLAT_SER":   {"label": "Platinum Serenity",              "type": "AV",  "statut": "actif",  "marche": "Luxembourg"},
    "EPLAT_BRD":  {"label": "ePlatinum Birdie",               "type": "AV",  "statut": "actif",  "marche": "Luxembourg"},
    "EPLAT_BE":   {"label": "ePlatinum Belgium",              "type": "AV",  "statut": "actif",  "marche": "Belgium"},
    # Produit générique fabriqué — contrats historiques allemands
    "WEALINS_DE": {"label": "Wealins Germany",                "type": "AV",  "statut": "legacy", "marche": "Germany"},
}

# ─── États contrat (format Lifeware) ─────────────────────────
ETATS_CONTRAT = {
    "ENC": "En cours",
    "TER": "Terminé",
    "SUS": "Suspendu",
    "RES": "Résilié",
}

# ─── Modes de gestion (format Lifeware) ──────────────────────
MODES_GESTION = {
    "C": "Conseillée",
    "L": "Libre",
}

# ─── Types d'événements (format Penelop) ─────────────────────
TYPES_EVT = {
    "OUV": "Ouverture / Souscription",
    "VLC": "Versement libre complémentaire",
    "RAP": "Rachat partiel",
    "RAT": "Rachat total",
    "ARB": "Arbitrage",
    "DCS": "Décès",
    "ECH": "Échéance",
    "NAN": "Nantissement",
    "CHB": "Changement bénéficiaire",
}

# ─── Rôles contrat (format Lifeware) ─────────────────────────
ROLES_CONTRAT = {
    "S":   "Souscripteur / Preneur",
    "A":   "Assuré",
    "B":   "Bénéficiaire en cas de décès",
    "BV":  "Bénéficiaire en cas de vie",
    "BA":  "Bénéficiaire acceptant",
    "M":   "Mandataire",
    "UBO": "Bénéficiaire effectif (UBO)",
    "DO":  "Donateur",
}

# ─── Fonds UC ─────────────────────────────────────────────────
# Source : présentation département Investment Wealins S.A.
# FID : 66.3% / FAS : 20.9% / External : 12.8%
FONDS_UC = [
    # FID — Fonds Interne Dédié (66.3%)
    {"code": "FID_UBS", "designation": "UBS Luxembourg FID Patrimoine",    "type": "FID",   "juridiction": "Luxembourg",    "liquidite": "faible",      "est_offshore": False, "poids": 33.0},
    {"code": "FID_BNP", "designation": "BNP Paribas Wealth FID",           "type": "FID",   "juridiction": "Luxembourg",    "liquidite": "faible",      "est_offshore": False, "poids": 33.3},
    # FAS — Fonds d'Assurance Spécialisé (20.9%)
    {"code": "FAS_IND", "designation": "Indosuez Wealth Management FAS",   "type": "FAS",   "juridiction": "Luxembourg",    "liquidite": "moyenne",     "est_offshore": False, "poids": 10.5},
    {"code": "FAS_ROT", "designation": "Rothschild & Co Gestion FAS",      "type": "FAS",   "juridiction": "Luxembourg",    "liquidite": "moyenne",     "est_offshore": False, "poids": 10.4},
    # OPCVM — External Funds (12.8%)
    {"code": "LU0104884860", "designation": "Pictet-Water P EUR",          "type": "OPCVM", "juridiction": "Luxembourg",    "liquidite": "haute",       "est_offshore": False, "poids": 2.5},
    {"code": "LU0255977539", "designation": "Pictet-Biotech R EUR",        "type": "OPCVM", "juridiction": "Luxembourg",    "liquidite": "haute",       "est_offshore": False, "poids": 2.5},
    {"code": "FR0010392225", "designation": "Varenne Capital Partners",    "type": "OPCVM", "juridiction": "France",        "liquidite": "haute",       "est_offshore": False, "poids": 2.5},
    {"code": "FR0010923383", "designation": "H2O Multistrategies R",       "type": "OPCVM", "juridiction": "France",        "liquidite": "haute",       "est_offshore": False, "poids": 2.5},
    {"code": "FR001400OJI4", "designation": "DNCA Flexibonds C",           "type": "OPCVM", "juridiction": "France",        "liquidite": "haute",       "est_offshore": False, "poids": 3.0},
    {"code": "XS2428662824", "designation": "BNP Paribas Certificat",      "type": "OPCVM", "juridiction": "Luxembourg",    "liquidite": "moyenne",     "est_offshore": False, "poids": 0.3},
    # Private Equity (cas rare)
    {"code": "PE_CAY_01",    "designation": "Cayman Growth Fund I",        "type": "PE",    "juridiction": "Cayman Islands","liquidite": "très faible", "est_offshore": True,  "poids": 0.2},
    {"code": "PE_LUX_01",    "designation": "Luxembourg PE SICAR",         "type": "PE",    "juridiction": "Luxembourg",    "liquidite": "très faible", "est_offshore": False, "poids": 0.3},
]

POIDS_FONDS = {"FID": 66.3, "FAS": 20.9, "OPCVM": 12.8}

# ─── Intermédiaires — marchés officiels Wealins ───────────────
# Source : Liste des produits autorisés Wealins (sept. 2025)
INTERMEDIAIRES = [
    {"nom": "Valoria Capital",          "pays": "France",      "type": "courtier"},
    {"nom": "Patrimoine & Conseil",     "pays": "Belgium",     "type": "courtier"},
    {"nom": "Nordic Wealth Partners",   "pays": "Norway",      "type": "courtier"},
    {"nom": "Milano Fiduciaria",        "pays": "Italy",       "type": "fiduciaire"},
    {"nom": "Iberia Patrimonio",        "pays": "Spain",       "type": "courtier"},
    {"nom": "Lux Private Office",       "pays": "Luxembourg",  "type": "family_office"},
    {"nom": "Porto Investimentos",      "pays": "Portugal",    "type": "courtier"},
    {"nom": "Helsinki Wealth Advisors", "pays": "Finland",     "type": "courtier"},
    {"nom": "Stockholm Capital",        "pays": "Sweden",      "type": "courtier"},
    {"nom": "Rhine Capital Advisors",   "pays": "Germany",     "type": "courtier"},
    {"nom": "Copenhagen Finance",       "pays": "Denmark",     "type": "courtier"},
    {"nom": "Monaco Patrimoine",        "pays": "Monaco",      "type": "family_office"},
]

# ─── Professions HNWI réalistes ───────────────────────────────
PROFESSIONS_HNWI = [
    {"profession": "Dirigeant PME",            "secteur": "Industrie",   "pep": False},
    {"profession": "Chef d'entreprise",         "secteur": "Commerce",    "pep": False},
    {"profession": "Entrepreneur tech",         "secteur": "Technologie", "pep": False},
    {"profession": "Promoteur immobilier",      "secteur": "Immobilier",  "pep": False},
    {"profession": "Médecin chirurgien",        "secteur": "Santé",       "pep": False},
    {"profession": "Avocat d'affaires",         "secteur": "Juridique",   "pep": False},
    {"profession": "Notaire",                   "secteur": "Juridique",   "pep": False},
    {"profession": "Expert comptable",          "secteur": "Finance",     "pep": False},
    {"profession": "Directeur financier",       "secteur": "Finance",     "pep": False},
    {"profession": "Gestionnaire de fonds",     "secteur": "Finance",     "pep": False},
    {"profession": "Banquier privé",            "secteur": "Finance",     "pep": False},
    {"profession": "Rentier",                   "secteur": "Patrimoine",  "pep": False},
    {"profession": "Héritier",                  "secteur": "Patrimoine",  "pep": False},
    {"profession": "Ancien ministre",           "secteur": "Politique",   "pep": True},
    {"profession": "Diplomate",                 "secteur": "Politique",   "pep": True},
    {"profession": "Parlementaire",             "secteur": "Politique",   "pep": True},
    {"profession": "Haut fonctionnaire",        "secteur": "Politique",   "pep": True},
    {"profession": "Directeur banque centrale", "secteur": "Finance",     "pep": True},
]

# ─── Structure juridique ──────────────────────────────────────
# Source : données internes Wealins
# Physique : 15 248 contrats (93.7%)
# Moral    :  1 015 contrats  (6.3%)
STRUCTURES = {
    "physique": 93.7,
    "moral":     6.3,
}


# ─── Générateur de clients ────────────────────────────────────
def generer_clients(n: int = 1000) -> pd.DataFrame:
    """
    Génère n clients HNWI fictifs calés sur Wealins.

    Sources :
    - Pays      : prov math client prices report
    - Statuts   : procédure AML/FT Wealins
    - Structure : données internes Wealins (93.7% / 6.3%)
    """

    clients = []

    for i in range(n):

        # Pays de résidence
        pays_residence = random.choices(
            PAYS_LISTE,
            weights=PAYS_POIDS,
            k=1
        )[0]

        # Profession et statut PEP
        profil = random.choices(
            PROFESSIONS_HNWI,
            weights=[
                3, 3, 2, 2,
                2, 2, 1, 1,
                2, 2, 1,
                2, 1,
                0.5, 0.3, 0.3, 0.2, 0.2
            ],
            k=1
        )[0]

        est_pep = profil["pep"]
        est_mep = (not est_pep) and random.random() < 0.01

        # Segment patrimoine
        segment = random.choices(
            ["mass_affluent", "HNWI"],
            weights=[0.30, 0.70],
            k=1
        )[0]

        if segment == "HNWI":
            patrimoine = np.random.lognormal(14.5, 0.7)
            patrimoine = max(1_000_000, patrimoine)
        else:
            patrimoine = np.random.lognormal(13.0, 0.4)
            patrimoine = max(125_000, min(999_999, patrimoine))

        # Structure juridique
        # Source : données internes Wealins
        structure = random.choices(
            list(STRUCTURES.keys()),
            weights=list(STRUCTURES.values()),
        )[0]

        # Nationalité
        nationalite = random.choices(
            [pays_residence, random.choice(PAYS_LISTE)],
            weights=[0.80, 0.20]
        )[0]

        clients.append({
            # Identification
            "id_client":            f"CLI_{i+1:04d}",
            "nom":                  fake.last_name(),
            "prenom":               fake.first_name(),
            "date_naissance":       fake.date_of_birth(
                                        minimum_age=30,
                                        maximum_age=80
                                    ),
            # Géographie
            "nationalite":          nationalite,
            "pays_residence":       pays_residence,
            "risque_pays":          get_score_pays(pays_residence),
            "classification_pays":  get_classification_pays(pays_residence),

            # Profil
            "profession":           profil["profession"],
            "secteur_activite":     profil["secteur"],
            "segment":              segment,
            "patrimoine_declare":   round(patrimoine, 2),
            "revenus_declare":      round(
                                        patrimoine * random.uniform(0.05, 0.12), 2
                                    ),

            # Structure juridique
            # Source : données internes Wealins (93.7% / 6.3%)
            "structure_juridique":  structure,

            # Statuts sensibles
            "est_pep":              est_pep,
            "type_pep":             "PPE1" if est_pep else None,
            "est_mep":              est_mep,
            "est_sous_sanctions":   random.random() < 0.001,
            "est_declare_crf":      False,

            # Screening
            "screening_worldcheck": random.choices(
                                        ["clear", "hit", "pending"],
                                        weights=[0.96, 0.02, 0.02]
                                    )[0],
            "screening_dowjones":   random.choices(
                                        ["clear", "hit", "pending"],
                                        weights=[0.97, 0.02, 0.01]
                                    )[0],

            # Dates
            "date_entree_relation": fake.date_between(
                                        start_date="-10y",
                                        end_date="-1y"
                                    ),
        })

    return pd.DataFrame(clients)


# ─── Générateur de contrats ───────────────────────────────────
def generer_contrats(clients_df: pd.DataFrame) -> pd.DataFrame:
    """Génère des contrats pour chaque client."""

    contrats    = []
    compteur_ba = 1

    for _, client in clients_df.iterrows():

        nb_contrats = random.choices(
            [1, 2, 3],
            weights=[0.72, 0.20, 0.08]
        )[0]

        for _ in range(nb_contrats):

            # Produit calé sur le marché du client
            produits_marche = [
                code for code, info in PRODUITS.items()
                if info["marche"] == client["pays_residence"]
            ]
            if not produits_marche:
                produits_marche = list(PRODUITS.keys())
            code_produit = random.choice(produits_marche)
            produit      = PRODUITS[code_produit]

            # Intermédiaire selon pays client
            inter_compatibles = [
                i for i in INTERMEDIAIRES
                if i["pays"] == client["pays_residence"]
            ]
            if not inter_compatibles:
                inter_compatibles = INTERMEDIAIRES
            intermediaire = random.choice(inter_compatibles)

            # Dates
            date_sousc = fake.date_between(
                start_date="-8y",
                end_date="-6m"
            )

            # Prime selon patrimoine
            prime = client["patrimoine_declare"] * random.uniform(0.10, 0.55)
            prime = max(250_000, round(prime / 1000) * 1000)

            # Versements complémentaires
            nb_vlc = random.choices(
                [0, 1, 2, 3],
                weights=[0.55, 0.28, 0.12, 0.05]
            )[0]
            somme_vlc = sum(
                round(prime * random.uniform(0.05, 0.25) / 1000) * 1000
                for _ in range(nb_vlc)
            )
            somme_versements = prime + somme_vlc

            # Rachats
            a_rachat = random.random() < 0.28
            somme_rachats = round(
                prime * random.uniform(0.08, 0.45) / 1000
            ) * 1000 if a_rachat else 0

            # Valeur actuelle
            perf          = random.uniform(0.88, 1.45)
            valeur_rachat = round(
                (somme_versements - somme_rachats) * perf / 100
            ) * 100
            valeur_acquise = round(
                valeur_rachat * random.uniform(0.15, 0.35) / 100
            ) * 100

            # Mode gestion
            if client["structure_juridique"] == "moral":
                mode_gestion = "C"
            else:
                mode_gestion = random.choices(
                    ["C", "L"],
                    weights=[0.78, 0.22]
                )[0]

            contrats.append({
                # Identification
                "id_contrat":          f"BA{compteur_ba:06d}",
                "num_contrat":         f"BA{compteur_ba:06d}",
                "id_client":           client["id_client"],
                "ref_intermediaire":   f"INT_{INTERMEDIAIRES.index(intermediaire)+1:04d}",

                # Produit
                "code_produit":        code_produit,
                "libelle_produit":     produit["label"],
                "type_produit":        produit["type"],
                "statut_produit":      produit["statut"],
                "code_regime_fiscal":  produit["type"],

                # État (format Lifeware)
                "code_etat_contrat":   random.choices(
                                           ["ENC", "TER", "SUS"],
                                           weights=[0.85, 0.10, 0.05]
                                       )[0],
                "code_mode_gestion":   mode_gestion,

                # Financier
                "prime_initiale":      prime,
                "somme_versements":    somme_versements,
                "somme_rachats":       somme_rachats,
                "valeur_rachat":       max(0, valeur_rachat),
                "valeur_acquise":      max(0, valeur_acquise),

                # Dates
                "date_souscription":   date_sousc,
                "date_effet_contrat":  date_sousc,
                "date_derniere_revue": None,
                "date_prochaine_revue":None,

                # Flags (format Lifeware)
                "flag_nantissement":   random.random() < 0.04,
                "flag_resynchro":      random.random() < 0.15,

                # Intermédiaire
                "nom_intermediaire":   intermediaire["nom"],
                "pays_intermediaire":  intermediaire["pays"],
                "type_intermediaire":  intermediaire["type"],

                # Scoring AML
                "score_lc189":         0,
                "risque_contrat":      "LOW",
                "remediation_ouverte": random.random() < 0.08,
            })

            compteur_ba += 1

    return pd.DataFrame(contrats)


# ─── Générateur de fonds UC ───────────────────────────────────
def generer_fonds_uc(contrats_df: pd.DataFrame) -> pd.DataFrame:
    """
    Génère les fonds UC pour chaque contrat.
    Structure inspirée de support_composant Lifeware.
    Source : présentation département Investment Wealins S.A.
    """

    fonds_list = []

    for _, contrat in contrats_df.iterrows():

        nb_fonds = random.choices(
            [1, 2, 3, 4],
            weights=[0.40, 0.35, 0.18, 0.07]
        )[0]

        if contrat["code_mode_gestion"] == "C":
            # Gestion conseillée → FID ou FAS obligatoire
            fonds_principaux = [
                f for f in FONDS_UC
                if f["type"] in ["FID", "FAS"]
            ]
            fonds_selectionnes = [
                random.choices(
                    fonds_principaux,
                    weights=[f["poids"] for f in fonds_principaux]
                )[0]
            ]
            # Compléter avec OPCVM
            opcvm = [f for f in FONDS_UC if f["type"] == "OPCVM"]
            for _ in range(nb_fonds - 1):
                fonds_selectionnes.append(random.choice(opcvm))
        else:
            # Gestion libre → OPCVM ou PE
            fonds_libres = [
                f for f in FONDS_UC
                if f["type"] in ["OPCVM", "PE"]
            ]
            fonds_selectionnes = random.choices(
                fonds_libres,
                k=min(nb_fonds, len(fonds_libres))
            )

        poids = np.random.dirichlet(
            np.ones(len(fonds_selectionnes))
        )
        valeur_totale = contrat["valeur_rachat"]

        for fonds, poids_i in zip(fonds_selectionnes, poids):
            valeur_fonds    = round(valeur_totale * poids_i / 100) * 100
            valeur_cotation = round(random.uniform(80, 150), 6)
            nb_parts        = round(
                valeur_fonds / valeur_cotation, 2
            ) if valeur_cotation > 0 else 0

            fonds_list.append({
                "id_support":           f"SUP_{len(fonds_list)+1:06d}",
                "ref_support":          fonds["code"],
                "id_contrat":           contrat["id_contrat"],
                "code_isin":            fonds["code"],
                "designation":          fonds["designation"],
                "type_fonds":           fonds["type"],
                "juridiction":          fonds["juridiction"],
                "risque_juridiction":   get_classification_pays(
                                            fonds["juridiction"]
                                        ),
                "liquidite":            fonds["liquidite"],
                "est_offshore":         fonds["est_offshore"],
                "montant_euro":         valeur_fonds,
                "nombre_parts":         nb_parts,
                "valeur_cotation_euro": valeur_cotation,
                "poids_pct":            round(poids_i * 100, 2),
                "flag_mandat_gestion":  contrat["code_mode_gestion"] == "C",
                "date_valorisation":    fake.date_between(
                                            start_date="-30d",
                                            end_date="today"
                                        ),
            })

    return pd.DataFrame(fonds_list)


# ─── Générateur de transactions ───────────────────────────────
def generer_transactions(
    contrats_df: pd.DataFrame,
    fonds_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Génère les événements pour chaque contrat.
    Structure inspirée de evt_globaux Lifeware.
    """

    transactions = []
    compteur     = 1

    for _, contrat in contrats_df.iterrows():

        date_sousc = pd.to_datetime(
            contrat["date_souscription"]
        ).date()

        # OUV — Ouverture
        transactions.append({
            "id_transaction":      f"EVT_{compteur:06d}",
            "id_contrat":          contrat["id_contrat"],
            "code_type_evt":       "OUV",
            "libelle_evt":         "Ouverture / Souscription",
            "code_statut_evt":     "VAL",
            "date_effet":          date_sousc,
            "date_execution":      date_sousc,
            "montant_total_brut":  contrat["prime_initiale"],
            "montant_total_net":   contrat["prime_initiale"],
            "montant_frais":       0.0,
            "plus_value_taxable":  0.0,
            "devise":              "EUR",
            "pays_banque_origine": contrat["pays_intermediaire"],
            "pays_banque_dest":    None,
            "est_tiers_payeur":    random.random() < 0.03,
            "perte_acceptee":      False,
            "montant_penalite":    0.0,
            "flag_atypique":       False,
            "fonds_source":        None,
            "fonds_cible":         None,
            "est_suspect":         False,
        })
        compteur += 1

        # VLC — Versements complémentaires
        somme_restante = (
            contrat["somme_versements"] - contrat["prime_initiale"]
        )
        if somme_restante > 0:
            nb_vlc = random.choices(
                [1, 2, 3],
                weights=[0.65, 0.25, 0.10]
            )[0]
            for _ in range(nb_vlc):
                delai_vlc   = random.randint(180, 2000)
                date_vlc    = date_sousc + timedelta(days=delai_vlc)
                montant_vlc = round(somme_restante / nb_vlc / 1000) * 1000

                transactions.append({
                    "id_transaction":      f"EVT_{compteur:06d}",
                    "id_contrat":          contrat["id_contrat"],
                    "code_type_evt":       "VLC",
                    "libelle_evt":         "Versement libre complémentaire",
                    "code_statut_evt":     "VAL",
                    "date_effet":          date_vlc,
                    "date_execution":      date_vlc,
                    "montant_total_brut":  montant_vlc,
                    "montant_total_net":   montant_vlc,
                    "montant_frais":       0.0,
                    "plus_value_taxable":  0.0,
                    "devise":              "EUR",
                    "pays_banque_origine": contrat["pays_intermediaire"],
                    "pays_banque_dest":    None,
                    "est_tiers_payeur":    random.random() < 0.03,
                    "perte_acceptee":      False,
                    "montant_penalite":    0.0,
                    "flag_atypique":       False,
                    "fonds_source":        None,
                    "fonds_cible":         None,
                    "est_suspect":         False,
                })
                compteur += 1

        # ARB — Arbitrages
        fonds_contrat = fonds_df[
            fonds_df["id_contrat"] == contrat["id_contrat"]
        ]
        if len(fonds_contrat) > 1 and random.random() < 0.35:
            nb_arb = random.choices(
                [1, 2, 3],
                weights=[0.70, 0.22, 0.08]
            )[0]
            for _ in range(nb_arb):
                delai_arb   = random.randint(90, 1500)
                date_arb    = date_sousc + timedelta(days=delai_arb)
                fonds_liste = fonds_contrat["code_isin"].tolist()
                fonds_src   = random.choice(fonds_liste)
                fonds_rest  = [f for f in fonds_liste if f != fonds_src]
                if not fonds_rest:
                    continue
                fonds_cbl   = random.choice(fonds_rest)
                montant_arb = round(
                    contrat["valeur_rachat"] *
                    random.uniform(0.05, 0.30) / 1000
                ) * 1000

                transactions.append({
                    "id_transaction":      f"EVT_{compteur:06d}",
                    "id_contrat":          contrat["id_contrat"],
                    "code_type_evt":       "ARB",
                    "libelle_evt":         "Arbitrage entre fonds",
                    "code_statut_evt":     "VAL",
                    "date_effet":          date_arb,
                    "date_execution":      date_arb,
                    "montant_total_brut":  montant_arb,
                    "montant_total_net":   montant_arb,
                    "montant_frais":       round(montant_arb * 0.005, 2)
                                           if random.random() < 0.5 else 0.0,
                    "plus_value_taxable":  0.0,
                    "devise":              "EUR",
                    "pays_banque_origine": None,
                    "pays_banque_dest":    None,
                    "est_tiers_payeur":    False,
                    "perte_acceptee":      False,
                    "montant_penalite":    0.0,
                    "flag_atypique":       False,
                    "fonds_source":        fonds_src,
                    "fonds_cible":         fonds_cbl,
                    "est_suspect":         False,
                })
                compteur += 1

        # RAP — Rachats partiels
        if contrat["somme_rachats"] > 0:
            nb_rachats = random.choices(
                [1, 2, 3],
                weights=[0.72, 0.20, 0.08]
            )[0]
            for _ in range(nb_rachats):
                delai       = random.randint(180, 2000)
                date_rap    = date_sousc + timedelta(days=delai)
                perte       = random.random() < 0.07
                montant_rap = round(
                    contrat["somme_rachats"] / nb_rachats / 1000
                ) * 1000
                penalite    = round(montant_rap * 0.03, 2) if perte else 0.0
                pv          = round(
                    montant_rap * random.uniform(0.02, 0.15), 2
                ) if not perte else 0.0

                transactions.append({
                    "id_transaction":      f"EVT_{compteur:06d}",
                    "id_contrat":          contrat["id_contrat"],
                    "code_type_evt":       "RAP",
                    "libelle_evt":         "Rachat partiel",
                    "code_statut_evt":     "VAL",
                    "date_effet":          date_rap,
                    "date_execution":      date_rap,
                    "montant_total_brut":  -montant_rap,
                    "montant_total_net":   -(montant_rap - penalite),
                    "montant_frais":       penalite,
                    "plus_value_taxable":  pv,
                    "devise":              "EUR",
                    "pays_banque_origine": contrat["pays_intermediaire"],
                    "pays_banque_dest":    contrat["pays_intermediaire"],
                    "est_tiers_payeur":    random.random() < 0.02,
                    "perte_acceptee":      perte,
                    "montant_penalite":    penalite,
                    "flag_atypique":       delai < 180,
                    "fonds_source":        None,
                    "fonds_cible":         None,
                    "est_suspect":         delai < 90 and perte,
                })
                compteur += 1

    return pd.DataFrame(transactions)


# ─── Générateur de rôles ──────────────────────────────────────
def generer_roles(
    clients_df: pd.DataFrame,
    contrats_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Génère les rôles pour chaque contrat.
    Structure inspirée de roles Lifeware.
    """

    roles = []

    for _, contrat in contrats_df.iterrows():

        client_rows = clients_df[
            clients_df["id_client"] == contrat["id_client"]
        ]
        if len(client_rows) == 0:
            continue
        client = client_rows.iloc[0]

        # Souscripteur — toujours présent
        roles.append({
            "id_role":      f"ROLE_{len(roles)+1:06d}",
            "id_contrat":   contrat["id_contrat"],
            "id_client":    client["id_client"],
            "code_role":    "S",
            "libelle_role": "Souscripteur / Preneur",
        })

        # Assuré — souvent le même
        if random.random() < 0.85:
            roles.append({
                "id_role":      f"ROLE_{len(roles)+1:06d}",
                "id_contrat":   contrat["id_contrat"],
                "id_client":    client["id_client"],
                "code_role":    "A",
                "libelle_role": "Assuré",
            })

        # Bénéficiaire
        roles.append({
            "id_role":      f"ROLE_{len(roles)+1:06d}",
            "id_contrat":   contrat["id_contrat"],
            "id_client":    client["id_client"],
            "code_role":    "B",
            "libelle_role": "Bénéficiaire en cas de décès",
        })

        # UBO si personne morale
        if client["structure_juridique"] == "moral":
            roles.append({
                "id_role":      f"ROLE_{len(roles)+1:06d}",
                "id_contrat":   contrat["id_contrat"],
                "id_client":    client["id_client"],
                "code_role":    "UBO",
                "libelle_role": "Bénéficiaire effectif",
            })

    return pd.DataFrame(roles)


# ─── Injecter des patterns suspects ──────────────────────────
def injecter_patterns_suspects(
    contrats_df: pd.DataFrame,
    transactions_df: pd.DataFrame,
    taux: float = 0.05,
) -> pd.DataFrame:
    """Injecte des patterns suspects dans ~5% des contrats."""

    PAYS_SUSPECTS = [
        "Monaco",
        "Cayman Islands",
        "United Arab Emirates",
        "Hong Kong",
        "Panama",
    ]

    nb_suspects   = int(len(contrats_df) * taux)
    indices_susp  = random.sample(list(contrats_df.index), nb_suspects)
    compteur_susp = 1

    for idx in indices_susp:
        id_contrat = contrats_df.loc[idx, "id_contrat"]
        date_sousc = pd.to_datetime(
            contrats_df.loc[idx, "date_souscription"]
        ).date()
        montant    = contrats_df.loc[idx, "prime_initiale"]
        penalite   = round(montant * 0.04, 2)

        transactions_df = pd.concat([
            transactions_df,
            pd.DataFrame([{
                "id_transaction":      f"EVT_SUSP_{compteur_susp:04d}",
                "id_contrat":          id_contrat,
                "code_type_evt":       "RAP",
                "libelle_evt":         "Rachat partiel",
                "code_statut_evt":     "VAL",
                "date_effet":          date_sousc + timedelta(
                                           days=random.randint(30, 90)
                                       ),
                "date_execution":      date_sousc + timedelta(
                                           days=random.randint(30, 90)
                                       ),
                "montant_total_brut":  -montant * 0.8,
                "montant_total_net":   -(montant * 0.8 - penalite),
                "montant_frais":       penalite,
                "plus_value_taxable":  0.0,
                "devise":              "EUR",
                "pays_banque_origine": random.choice(PAYS_SUSPECTS),
                "pays_banque_dest":    random.choice(PAYS_SUSPECTS),
                "est_tiers_payeur":    True,
                "perte_acceptee":      True,
                "montant_penalite":    penalite,
                "flag_atypique":       True,
                "fonds_source":        None,
                "fonds_cible":         None,
                "est_suspect":         True,
            }])
        ], ignore_index=True)

        compteur_susp += 1

    return transactions_df


# ─── Générateur principal ─────────────────────────────────────
def generer_dataset_complet(
    nb_clients: int = 1000,
    save: bool = True,
) -> dict:
    """Génère le dataset complet Wealins AML."""

    print(" Génération des clients...")
    clients = generer_clients(nb_clients)
    print(f"    {len(clients):,} clients générés")

    print(" Génération des contrats...")
    contrats = generer_contrats(clients)
    print(f"    {len(contrats):,} contrats générés")

    print(" Génération des fonds UC...")
    fonds = generer_fonds_uc(contrats)
    print(f"    {len(fonds):,} fonds UC générés")

    print(" Génération des transactions...")
    transactions = generer_transactions(contrats, fonds)
    print(f"    {len(transactions):,} transactions générées")

    print(" Génération des rôles...")
    roles = generer_roles(clients, contrats)
    print(f"    {len(roles):,} rôles générés")

    print(" Injection des patterns suspects...")
    transactions = injecter_patterns_suspects(contrats, transactions)
    nb_suspects  = transactions["est_suspect"].sum()
    print(f"    {nb_suspects:,} transactions suspectes injectées")

    dataset = {
        "clients":      clients,
        "contrats":     contrats,
        "fonds":        fonds,
        "transactions": transactions,
        "roles":        roles,
    }

    if save:
        print(" Sauvegarde des données...")
        clients.to_csv("data/synthetic/clients.csv", index=False)
        contrats.to_csv("data/synthetic/contrats.csv", index=False)
        fonds.to_csv("data/synthetic/fonds_uc.csv", index=False)
        transactions.to_csv("data/synthetic/transactions.csv", index=False)
        roles.to_csv("data/synthetic/roles.csv", index=False)
        print("    Données sauvegardées dans data/synthetic/")

    print("\n Résumé du dataset :")
    print(f"   Clients      : {len(clients):,}")
    print(f"   Contrats     : {len(contrats):,}")
    print(f"   Fonds UC     : {len(fonds):,}")
    print(f"   Transactions : {len(transactions):,}")
    print(f"   Rôles        : {len(roles):,}")
    print(f"   Suspects     : {nb_suspects:,}")
    print(f"   Taux suspect : {nb_suspects/len(transactions)*100:.1f}%")

    print("\n Distribution des transactions :")
    dist = transactions["code_type_evt"].value_counts()
    for evt, count in dist.items():
        print(f"   {evt} : {count:,}")

    return dataset


# ─── Point d'entrée ───────────────────────────────────────────
if __name__ == "__main__":
    dataset = generer_dataset_complet(nb_clients=1000)