"""
Questionnaire LC 18/9 - CAA Luxembourg
51 questions de scoring AML/FT 
WEALINS S.A.
"""
# Seuil de classification

SEUILS= {
    "LOW": (0, 10),
    "MEDIUM": (11, 15),
    "HIGH": (16, float('inf'))
}

# Questions qui forcent high automatiquement
QUESTIONS_HIGH_AUTO = [
    "I04",   # Personne morale
    "I11",   # Documents identité manquants
    "I12",   # Montage spécial (trust)
    "I13",   # Déclaration CRF
    "I14",   # Sanctions internationales
    "I15",   # PEP
    "I16",   # Profession sensible
    "I17",   # Background check négatif
    "I18",   # Non-conformité fiscale
    "I51",   # Élément atypique global
]

# Critères supplémentaires forçant high

CRITERES_HIGH_SUPPLEMENTAIRES = [
    "est_mep", # Media Exposed Person
    "encours_sup_25m", # Encours > 25 millions €
]

#  Définition des 51 questions
QUESTIONS = {
    "I01": {
        "libelle": "Type de police individuelle",
        "type": "choix",
        "reponses": {
            "AV": {"score": 0, "label": "Assurance vie"},
            "CAP": {"score": 0, "label": "Capitalisation"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I02": {
        "libelle": "Pays de résidence actuel du preneur",
        "type": "choix",
        "reponses": {
            "a": {"score": 0,  "label": "Luxembourg"},
            "b": {"score": 0,  "label": "Pays risque faible"},
            "c": {"score": 2,  "label": "Pays risque moyen"},
            "d": {"score": 4,  "label": "Pays risque élevé"},
        },
        "force_high": False,
        "force_medium": ["c"],
        "force_high_reponses": ["d"],
        "manuel": True,
    },

    "I03": {
        "libelle": "Le preneur est différent du bénéficiaire effectif",
        "type": "boolean",
        "reponses": {
            True:  {"score": 0, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I04": {
        "libelle": "Le preneur est une personne morale",
        "type": "boolean",
        "reponses": {
            True:  {"score": 0, "label": "Oui → HIGH automatique"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": True,
        "manuel": True,
    },

    "I05": {
        "libelle": "Pays de résidence du bénéficiaire effectif",
        "type": "choix",
        "reponses": {
            "a": {"score": 0, "label": "Luxembourg"},
            "b": {"score": 0, "label": "Pays risque faible"},
            "c": {"score": 2, "label": "Pays risque moyen"},
            "d": {"score": 4, "label": "Pays risque élevé"},
        },
        "force_high": False,
        "force_high_reponses": ["d"],
        "manuel": True,
    },

    "I06": {
        "libelle": "Pays de résidence de l'assuré",
        "type": "choix",
        "reponses": {
            "a": {"score": 0, "label": "Luxembourg"},
            "b": {"score": 0, "label": "Pays risque faible"},
            "c": {"score": 2, "label": "Pays risque moyen"},
            "d": {"score": 4, "label": "Pays risque élevé"},
        },
        "force_high": False,
        "force_high_reponses": ["d"],
        "manuel": True,
    },

    "I07": {
        "libelle": "Nationalité du preneur",
        "type": "choix",
        "reponses": {
            "a": {"score": 0, "label": "Luxembourg"},
            "b": {"score": 0, "label": "Pays risque faible"},
            "c": {"score": 2, "label": "Pays risque moyen"},
            "d": {"score": 4, "label": "Pays risque élevé"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I08": {
        "libelle": "Nationalité du bénéficiaire effectif",
        "type": "choix",
        "reponses": {
            "a": {"score": 0, "label": "Luxembourg"},
            "b": {"score": 0, "label": "Pays risque faible"},
            "c": {"score": 2, "label": "Pays risque moyen"},
            "d": {"score": 4, "label": "Pays risque élevé"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I09": {
        "libelle": "Nationalité de l'assuré",
        "type": "choix",
        "reponses": {
            "a": {"score": 0, "label": "Luxembourg"},
            "b": {"score": 0, "label": "Pays risque faible"},
            "c": {"score": 2, "label": "Pays risque moyen"},
            "d": {"score": 4, "label": "Pays risque élevé"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I10": {
        "libelle": "Le client ou assuré a changé pendant la vie du contrat",
        "type": "boolean",
        "reponses": {
            True:  {"score": 2, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I11": {
        "libelle": "Documents identité non obtenus / régularisés",
        "type": "boolean",
        "reponses": {
            True:  {"score": 4, "label": "Oui → HIGH automatique"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": True,
        "manuel": True,
    },

    "I12": {
        "libelle": "Montage spécial (trust ou construction juridique)",
        "type": "boolean",
        "reponses": {
            True:  {"score": 4, "label": "Oui → HIGH automatique"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": True,
        "manuel": True,
    },

    "I13": {
        "libelle": "Contrat déclaré à la CRF",
        "type": "boolean",
        "reponses": {
            True:  {"score": 4, "label": "Oui → HIGH automatique"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": True,
        "manuel": False,
    },

    "I14": {
        "libelle": "Client sur liste de sanctions internationales",
        "type": "boolean",
        "reponses": {
            True:  {"score": 4, "label": "Oui → HIGH automatique"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": True,
        "manuel": False,
    },

    "I15": {
        "libelle": "Client ou partie au contrat est PEP",
        "type": "boolean",
        "reponses": {
            True:  {"score": 4, "label": "Oui → HIGH automatique"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": True,
        "manuel": False,
    },

    "I16": {
        "libelle": "Client exerce une profession sensible",
        "type": "boolean",
        "reponses": {
            True:  {"score": 4, "label": "Oui → HIGH automatique"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": True,
        "manuel": True,
    },

    "I17": {
        "libelle": "Background check a révélé des éléments de risque",
        "type": "boolean",
        "reponses": {
            True:  {"score": 4, "label": "Oui → HIGH automatique"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": True,
        "manuel": True,
    },

    "I18": {
        "libelle": "Non-conformité fiscale du client",
        "type": "boolean",
        "reponses": {
            True:  {"score": 4, "label": "Oui → HIGH automatique"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": True,
        "manuel": True,
    },

    "I19": {
        "libelle": "Contrats multiples avec mêmes caractéristiques",
        "type": "boolean",
        "reponses": {
            True:  {"score": 2, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": True,
    },

    "I20": {
        "libelle": "Pays de la banque d'où provient la prime",
        "type": "choix",
        "reponses": {
            "a": {"score": 0, "label": "Luxembourg"},
            "b": {"score": 0, "label": "Pays risque faible"},
            "c": {"score": 2, "label": "Pays risque moyen"},
            "d": {"score": 4, "label": "Pays risque élevé"},
        },
        "force_high": False,
        "force_high_reponses": ["d"],
        "manuel": True,
    },

    "I21": {
        "libelle": "Banque hors pays résidence sans justification",
        "type": "boolean",
        "reponses": {
            True:  {"score": 3, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": True,
    },

    "I22": {
        "libelle": "Prime entre 250k€ et 2.5M€",
        "type": "boolean",
        "reponses": {
            True:  {"score": 2, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I23": {
        "libelle": "Prime supérieure à 2.5M€",
        "type": "boolean",
        "reponses": {
            True:  {"score": 4, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I24": {
        "libelle": "Paiement en cash, chèque porteur ou titres porteur",
        "type": "boolean",
        "reponses": {
            True:  {"score": 1, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
            "NA":  {"score": 0, "label": "N/A"},
        },
        "force_high": False,
        "manuel": True,
    },

    "I25": {
        "libelle": "Contrat prévoit des versements additionnels",
        "type": "boolean",
        "reponses": {
            True:  {"score": 0, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I26": {
        "libelle": "Versements additionnels ne correspondent pas au profil",
        "type": "boolean",
        "reponses": {
            True:  {"score": 2, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I27": {
        "libelle": "La prime présente des éléments atypiques",
        "type": "boolean",
        "reponses": {
            True:  {"score": 3, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": True,
    },

    "I28": {
        "libelle": "Clause bénéficiaire non exclusivement famille",
        "type": "boolean",
        "reponses": {
            True:  {"score": 1, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
            "NA":  {"score": 0, "label": "N/A"},
        },
        "force_high": False,
        "manuel": True,
    },

    "I29": {
        "libelle": "Clause bénéficiaire en faveur d'une personne morale",
        "type": "boolean",
        "reponses": {
            True:  {"score": 1, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
            "NA":  {"score": 0, "label": "N/A"},
        },
        "force_high": False,
        "manuel": True,
    },

    "I30": {
        "libelle": "Clause bénéficiaire personne physique si preneur PM",
        "type": "boolean",
        "reponses": {
            True:  {"score": 2, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
            "NA":  {"score": 0, "label": "N/A"},
        },
        "force_high": False,
        "manuel": True,
    },

    "I31": {
        "libelle": "Bénéficiaire irrévocable hors famille ou banque",
        "type": "boolean",
        "reponses": {
            True:  {"score": 2, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
            "NA":  {"score": 0, "label": "N/A"},
        },
        "force_high": False,
        "manuel": True,
    },

    "I32": {
        "libelle": "Contrat nanti en faveur d'un tiers non bancaire",
        "type": "boolean",
        "reponses": {
            True:  {"score": 2, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I33": {
        "libelle": "Contrat cédé ou droits transférés sans justification",
        "type": "boolean",
        "reponses": {
            True:  {"score": 2, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I34": {
        "libelle": "Adresse courrier différente de la résidence",
        "type": "boolean",
        "reponses": {
            True:  {"score": 1, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I35": {
        "libelle": "Investissement 50-100% en instruments non cotés",
        "type": "boolean",
        "reponses": {
            True:  {"score": 4, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
            "NA":  {"score": 0, "label": "N/A"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I36": {
        "libelle": "Investissement 10-50% en instruments non cotés",
        "type": "boolean",
        "reponses": {
            True:  {"score": 2, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
            "NA":  {"score": 0, "label": "N/A"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I37": {
        "libelle": "Client lié aux actifs non cotés sous-jacents",
        "type": "boolean",
        "reponses": {
            True:  {"score": 4, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I38": {
        "libelle": "Intermédiaire dans un pays à risque élevé",
        "type": "boolean",
        "reponses": {
            True:  {"score": 2, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I39": {
        "libelle": "Intermédiaire dans pays différent du client",
        "type": "boolean",
        "reponses": {
            True:  {"score": 1, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I40": {
        "libelle": "Changement d'intermédiaire à l'initiative du client",
        "type": "boolean",
        "reponses": {
            True:  {"score": 2, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I41": {
        "libelle": "Intermédiaire autorisé à collecter les primes",
        "type": "boolean",
        "reponses": {
            True:  {"score": 1, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I42": {
        "libelle": "Contrat distribué via internet ou à distance",
        "type": "boolean",
        "reponses": {
            True:  {"score": 2, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I43": {
        "libelle": "Contrat annulé pendant la période de rétractation",
        "type": "boolean",
        "reponses": {
            True:  {"score": 2, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I44": {
        "libelle": "Nombre de rachats sur les 2 dernières années",
        "type": "nombre",
        "reponses": {
            0: {"score": 0, "label": "Aucun"},
            1: {"score": 1, "label": "1 rachat"},
            2: {"score": 2, "label": "2 rachats"},
            3: {"score": 3, "label": "3 rachats ou plus"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I45": {
        "libelle": "Paiement avec pénalités économiquement disproportionnées",
        "type": "boolean",
        "reponses": {
            True:  {"score": 3, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I46": {
        "libelle": "Paiement fractionné sur plusieurs comptes",
        "type": "boolean",
        "reponses": {
            True:  {"score": 4, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I47": {
        "libelle": "Pays de la banque vers laquelle le paiement est fait",
        "type": "choix",
        "reponses": {
            "a": {"score": 0, "label": "Luxembourg"},
            "b": {"score": 0, "label": "Pays risque faible"},
            "c": {"score": 2, "label": "Pays risque moyen"},
            "d": {"score": 4, "label": "Pays risque élevé"},
            "NA": {"score": 0, "label": "N/A"},
        },
        "force_high": False,
        "force_high_reponses": ["d"],
        "manuel": True,
    },

    "I48": {
        "libelle": "Pas de lien économique entre résidence et pays banque",
        "type": "boolean",
        "reponses": {
            True:  {"score": 2, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
            "NA":  {"score": 0, "label": "N/A"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I49": {
        "libelle": "Changement clause bénéficiaire dans les 6 mois avant échéance",
        "type": "boolean",
        "reponses": {
            True:  {"score": 3, "label": "Oui"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": False,
        "manuel": False,
    },

    "I50": {
        "libelle": "Paiement avec autre élément atypique",
        "type": "boolean",
        "reponses": {
            True:  {"score": 4, "label": "Oui → HIGH automatique"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": True,
        "manuel": True,
    },

    "I51": {
        "libelle": "Dossier présente un autre élément atypique",
        "type": "boolean",
        "reponses": {
            True:  {"score": 4, "label": "Oui → HIGH automatique"},
            False: {"score": 0, "label": "Non"},
        },
        "force_high": True,
        "manuel": True,
    },
}

# Fonction principale de scoring

def calculer_score (reponses : dict) -> dict:
    """
    Calcule du score LC18/9  et la  classification. 
    
    Args:
        reponses (dict): Dictionnaire contenant les réponses aux questions. 
                         Les clés sont les identifiants des questions (ex: "I01", "I02", ...), 
                         et les valeurs sont les réponses correspondantes.
                         
    Returns : 
        dict avec score, classification, flags
        
    """
    score_total = 0 
    flags_high_auto = []
    details = {}

    for questions_id, valeur in reponses.items():
        # Ignore les questions non définies
        if questions_id not in QUESTIONS:
            continue

        question = QUESTIONS[questions_id]
        
        # Récupérer le score de la réponse
        score_question = 0
        if valeur in question["reponses"]:
            score_question = question["reponses"][valeur]["score"]
            
        score_total += score_question
        details[questions_id] = score_question
        
        #Vérifier si cette réponse force un score HIGH 
        if question.get("force_high") and valeur == True:
            flags_high_auto.append(questions_id)
            
        # Vérifier force_high sur réponses spécifiques
        if "force_high_reponses" in question:
            if valeur in question["force_high_reponses"]:
                flags_high_auto.append(questions_id)
    
    # Déterminer la classification 
    if flags_high_auto:
        classification = "HIGH"
    elif score_total <= 10:
        classification = "LOW"
    elif score_total <= 15:
        classification = "MEDIUM"
    else:
        classification = "HIGH"
        
    return {
        "score_total": score_total,
        "classification": classification,
        "flags_high_auto": flags_high_auto,
        "details": details,
    }               
    
def get_classification(score: int) -> str:
    """Retourne la classification selon le score."""
    if score <= 10:
        return "LOW"
    elif score <= 15:
        return "MEDIUM"
    else:
        return "HIGH"
    
    