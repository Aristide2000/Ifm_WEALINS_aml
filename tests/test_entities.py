"""
Tests pour les entités OOP
"""

from datetime import date
from src.entities.client import Client

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