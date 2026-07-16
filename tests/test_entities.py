"""
Tests pour les entités OOP
"""

from datetime import date
from src.entities.client import Client
from src.entities.contrat import Contrat, FondsUC
from src.entities.transaction import Transaction, TYPES_OPERATIONS


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
    

def make_transaction_ouverture():
    """Transaction d'ouverture standard"""
    return Transaction(
        id_transaction="EVT_000001",
        id_contrat="BA000001",
        code_type_evt="OUV",
        date_effet=date(2022, 1, 1),
        montant_brut=500_000,
        montant_net=500_000,
    )


def test_transaction_ouverture():
    trx = make_transaction_ouverture()
    assert trx.est_versement == True
    assert trx.est_rachat == False
    assert trx.est_arbitrage == False
    assert trx.libelle_type == "Ouverture / Souscription"
    assert trx.risque_pays_origine == "FAIBLE"


def test_transaction_rachat():
    trx = Transaction(
        id_transaction="EVT_000002",
        id_contrat="BA000001",
        code_type_evt="RAP",
        date_effet=date(2022, 3, 1),
        montant_brut=-100_000,
        montant_net=-97_000,
        montant_frais=3_000,
        pays_banque_dest="Cayman Islands",
        perte_acceptee=True,
        montant_penalite=3_000,
        est_suspect=True,
    )
    assert trx.est_rachat == True
    assert trx.perte_acceptee == True
    assert trx.risque_pays_destination == "ELEVE"
    assert trx.est_suspect == True
    
    
from src.entities.alerte_aml import AlerteAML, COMITE_PAR_RISQUE


def test_alerte_medium():
    alerte = AlerteAML(
        id_alerte="ALT_001",
        id_contrat="BA000001",
        date_detection=date(2022, 3, 1),
        type_alerte="rachat_suspect",
        source_detection="rules_engine",
        description="Rachat précoce détecté",
        score_risque=0.75,
        niveau_alerte="MEDIUM",
    )
    assert alerte.comite == "CAR"
    assert alerte.est_critique == False
    assert alerte.necessite_declaration_crf == False
    assert alerte.statut == "ouverte"


def test_alerte_critical():
    alerte = AlerteAML(
        id_alerte="ALT_002",
        id_contrat="BA000001",
        date_detection=date(2022, 3, 1),
        type_alerte="pays_interdit",
        source_detection="rules_engine",
        description="Transaction vers pays interdit",
        score_risque=1.0,
        niveau_alerte="CRITICAL",
    )
    assert alerte.comite == "COMPLIANCE"
    assert alerte.est_critique == True
    assert alerte.necessite_declaration_crf == True
    assert alerte.escalader() == "COMPLIANCE"