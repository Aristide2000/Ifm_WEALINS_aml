"""
Tests pour les entités OOP
"""

from datetime import date
from src.entities.client import Client
from src.entities.contrat import Contrat, FondsUC

def make_client_standard():
    return Client(
        id_client="CLI_001",
        nom="Dupont",
        prenom="Jean",
        date_naissance=date(1970, 1, 1),
        nationalite="France",
        pays_residence="France",
        profession="Chef entreprise",
        secteur_activite="Finance",
        patrimoine_declare=2_000_000,
        revenus_declare=300_000,
        segment="HNWI",
        type_client="particulier",
        structure_juridique="physique",
    )

def test_client_faible_risque():
    client = make_client_standard()
    assert client.risque_pays_residence == "FAIBLE"
    assert client.est_profil_sensible == False
    assert client.classification_risque_base == "LOW"


def test_client_pep():
    client = make_client_standard()
    client.est_pep = True
    client.type_pep = "PPE1"
    assert client.est_profil_sensible == True
    assert client.classification_risque_base == "HIGH"


def test_client_sanctions():
    client = make_client_standard()
    client.est_sous_sanctions = True
    assert client.classification_risque_base == "HIGH"


def test_client_pays_interdit():
    client = make_client_standard()
    client.pays_residence = "Monaco"
    assert client.risque_pays_residence == "INTERDIT"
    assert client.classification_risque_base == "HIGH"
    
    
    from src.entities.contrat import Contrat, FondsUC


def make_contrat_standard():
    """Contrat standard — profil simple"""
    return Contrat(
        id_contrat="BA000001",
        num_contrat="BA000001",
        id_client="CLI_001",
        produit="WEALIFE",
        type_produit="AV",
        regime_fiscal="AV",
        mode_gestion="C",
        prime_initiale=500_000,
        somme_versements=500_000,
        somme_rachats=0,
        valeur_actuelle=520_000,
        date_souscription=date(2022, 1, 1),
    )


def test_contrat_basique():
    contrat = make_contrat_standard()
    assert contrat.taux_rachat == 0.0
    assert contrat.segment_prime == "ELEVE"
    assert contrat.est_contrat_suspect == False
    assert contrat.duree_jours > 0


def test_contrat_fonds_offshore():
    contrat = make_contrat_standard()
    fonds = FondsUC(
        id_fonds="F001",
        code_isin="PE_CAY_01",
        designation="Cayman Fund",
        type_fonds="PE",
        juridiction="Cayman Islands",
        liquidite="faible",
        poids_pct=50.0,
        valeur_euro=250_000,
        est_offshore=True,
    )
    contrat.fonds.append(fonds)
    assert contrat.a_fonds_offshore == True
    assert fonds.est_suspect == True
    assert fonds.risque_juridiction == "ELEVE"