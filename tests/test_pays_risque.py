""" Tests pour la classification des pays """

from config.pays_risque import (
    get_classification_pays,
    get_score_pays,
    est_pays_interdit,
    STATS_PAYS
)

def test_pays_faible():
    assert get_classification_pays("France") == "FAIBLE"
    assert get_classification_pays("FR") == "FAIBLE"
    
def test_pays_moyen():
    assert get_classification_pays("United Kingdom") == "MOYEN"

def test_pays_eleve():
    assert get_classification_pays("China") == "ELEVE"
    
def test_pays_interdit():
    assert get_classification_pays("Russia") == "INTERDIT"
    assert est_pays_interdit("Monaco") == True
    
def test_score_pays():
    assert get_score_pays("France") == 0
    assert get_score_pays("United Kingdom") == 2
    assert get_score_pays("China") == 4
    assert get_score_pays("Russia") == 19

def test_stats():
    print(f"\nStats pays: {STATS_PAYS}")
    assert STATS_PAYS["total"] > 100
    