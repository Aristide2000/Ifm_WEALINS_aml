"""
Test pour le questionnaire LC18/9
"""

from config.questions_lc189 import(
    calculer_score,
    get_classification,
    QUESTIONS_HIGH_AUTO,
    QUESTIONS,
    SEUILS
)

def test_nombre_questions():
    """
    Vérifier qu'on a bien 51 questions dans le questionnaire LC18/9
    """
    assert len(QUESTIONS) == 51
    
def test_client_faible_risque():
    """
    Client standard français avec un profil de risque faible
    """
    reponses = {
        "I01": "AV",
        "I02": "b",   # Pays faible
        "I04": False,
        "I11": False,
        "I12": False,
        "I13": False,
        "I14": False,
        "I15": False,
        "I16": False,
        "I17": False,
        "I18": False,
        "I22": True,  
        "I51": False, 
    }
    
    resultat = calculer_score(reponses)
    assert resultat["classification"] == "LOW"
    assert resultat["score_total"] == 2
    
def test_client_pep_force_high():
    """
    Client PEP avec des réponses qui déclenchent un score HIGH automatiquement
    """
    reponses = {
        "I02": "b",
        "I15": True,   # PEP → force HIGH
        "I22": True,
    }
    
    resultat = calculer_score(reponses)
    assert resultat["classification"] == "HIGH"
    assert "I15" in resultat["flags_high_auto"]
    
def test_client_medium():
    """
    client avec un score entre 11 et 15 
    """ 
    reponses = {
        "I02": "c",   
        "I20": "c",   
        "I22": True,  
        "I21": True,  
        "I39": True,  
        "I34": True, 
    }
    resultat = calculer_score(reponses)
    assert resultat["classification"] == "MEDIUM"
    assert 11 <= resultat["score_total"] <= 15
    
def test_rachat_suspect():
    """
    Rachat avec perte acceptée cela nous donne un score élevé
    """
    reponses = {
        "I02": "b",
        "I44": 3,      
        "I45": True,   
        "I50": True,
    }
    resultat = calculer_score(reponses)
    assert resultat["classification"] == "HIGH"
    
def test_sanctions_force_high():
    """
    Client sous sanctions cela nous donne un score élevé
    """
    reponses = {
        "I14": True, # Des sanctions renvoie a un risque elevé
    }
    resultat = calculer_score(reponses)
    assert resultat["classification"] == "HIGH"
    assert "I14" in resultat["flags_high_auto"]
    
def test_classification_seuil():
    """
    Tester les seuils de classification. 
    """
    assert get_classification(0)  == "LOW"
    assert get_classification(10) == "LOW"
    assert get_classification(11) == "MEDIUM"
    assert get_classification(15) == "MEDIUM"
    assert get_classification(16) == "HIGH"
    assert get_classification(30) == "HIGH"
    