"""Classification des pays selon la methodologie officielle de WEALINS S.A.
"""

# Pays interdis 

PAYS_INTERDITS = [
     "Afghanistan", "Algeria", "Angola", "Belarus",
    "Bolivia", "British Virgin Islands", "Bulgaria",
    "Cameroon", "Central African Republic",
    "Congo, Democratic Republic of",
    "Congo, Republic of the", "Cote d'Ivoire",
    "Cuba", "Egypt", "Haiti", "Iran", "Iraq",
    "Israel", "Kenya", "Korea, North", "Kuwait",
    "Laos", "Lebanon", "Libya", "Mali", "Monaco",
    "Mozambique", "Myanmar/Burma", "Namibia", "Nepal",
    "Nicaragua", "Nigeria", "Pakistan",
    "Papua New Guinea", "Russia", "Somalia",
    "South Sudan", "Sudan", "Syria",
    "Trinidad and Tobago", "Ukraine", "Vanuatu",
    "Venezuela", "Vietnam", "Yemen", "Zimbabwe"
]

# PAYS A RISQUE ELEVE

PAYS_ELEVE = [
    "Albania", "American Samoa", "Anguilla",
    "Antigua and Barbuda", "Argentina", "Armenia",
    "Azerbaijan", "Bahamas, The", "Bahrain",
    "Bangladesh", "Barbados", "Belize", "Benin",
    "Bermuda", "Bosnia and Herzegovina", "Botswana",
    "Brazil", "British Indian Ocean Territory",
    "Brunei", "Burkina Faso", "Burundi", "Cambodia",
    "Cayman Islands", "Chad", "China", "Colombia",
    "Comoros", "Cook Islands", "Costa Rica", "Croatia",
    "Djibouti", "Dominica", "Dominican Republic",
    "Ecuador", "El Salvador", "Equatorial Guinea",
    "Eritrea", "Eswatini", "Ethiopia",
    "Federated States of Micronesia", "Fiji",
    "Gabon", "Gambia, The", "Ghana", "Gibraltar",
    "Grenada", "Guam", "Guatemala", "Guinea",
    "Guinea-Bissau", "Guyana", "Honduras",
    "Hong Kong", "India", "Indonesia", "Jamaica",
    "Jordan", "Kazakhstan", "Kiribati", "Kosovo",
    "Kyrgyzstan", "Labuan Island (Malaysia)",
    "Lesotho", "Liberia", "Macedonia", "Madagascar",
    "Malawi", "Malaysia", "Maldives",
    "Marshall Islands", "Mauritania", "Mauritius",
    "Mexico", "Moldova", "Mongolia", "Montenegro",
    "Montserrat", "Morocco", "Nauru", "Niger",
    "Niue", "Norfolk Island", "Northern Marian Islands",
    "Oman", "Palau", "Panama", "Paraguay", "Peru",
    "Philippines", "Pitcairn islands", "Qatar",
    "Romania", "Rwanda", "Saint Kitts and Nevis",
    "Saint Lucia", "Saint Vincent and the Grenadines",
    "Samoa", "Sao Tome and Principe", "Saudi Arabia",
    "Senegal", "Serbia", "Sierra Leone",
    "Solomon Islands", "South Africa",
    "South Georgia and the South Sandwich Islands",
    "Sri Lanka", "St Helena", "Suriname", "Tajikistan",
    "Tanzania", "Thailand", "Timor-Leste", "Togo",
    "Tonga", "Tunisia", "Turkey", "Turkmenistan",
    "Turks and Caicos Islands", "Tuvalu", "Uganda",
    "United Arab Emirates", "US Virgin Islands",
    "Uzbekistan", "Wallis and Futuna",
    "Western Sahara", "Zambia"
]

# PAYS A RISQUE MOYEN 
PAYS_MOYEN = [
    "Andorra", "Aruba", "Australia", "Bhutan",
    "Cabo Verde", "Canada", "Chile", "Curacao",
    "Cyprus", "Faroe Islands", "French Guiana",
    "French Polynesia", "French Southern Territories",
    "Georgia", "Greece", "Greenland", "Guadeloupe",
    "Guernsey", "Holy See (Vatican City)", "Hungary",
    "Isle of Man", "Japan", "Jersey", "Korea, South",
    "La Réunion", "Latvia", "Liechtenstein",
    "Lithuania", "Macau", "Malta", "Martinique",
    "Mayotte", "Netherland Antilles", "New Caledonia",
    "New Zealand", "Porto Rico", "Saint Bathelemy",
    "Saint Martin (France)", "Saint-Pierre-et-Miquelon",
    "San Marino", "Seychelles", "Singapore",
    "Sint Maarten (NL)", "Slovenia",
    "Svalbard and Jan Mayen islands", "Taiwan",
    "Tokelau", "United Kingdom",
    "United States of America", "Uruguay"
]

# PAYS A RISQUE FAIBLE
PAYS_FAIBLE = [
     "Austria", "Belgium", "Czechia", "Denmark",
    "Estonia", "Finland", "France", "Germany",
    "Iceland", "Ireland", "Italy", "Luxembourg",
    "Netherlands", "Norway", "Poland", "Portugal",
    "Slovakia", "Spain", "Sweden", "Switzerland"
]

# DICTIONNAIRE PRINCIPAL 
CLASSIFICATION_PAYS = {}

for pays in PAYS_INTERDITS:
    CLASSIFICATION_PAYS[pays] = "INTERDIT"  
    
for pays in PAYS_ELEVE:
    CLASSIFICATION_PAYS[pays] = "ELEVE"
    
for pays in PAYS_MOYEN:
    CLASSIFICATION_PAYS[pays] = "MOYEN"  
    
for pays in PAYS_FAIBLE:
    CLASSIFICATION_PAYS[pays] = "FAIBLE"
    
# CODE ISO --> NOM DU PAYS
CODE_ISO_PAYS = {
    "BE": "Belgium",
    "FR": "France",
    "MC": "Monaco",
    "LU": "Luxembourg",
    "IT": "Italy",
    "PT": "Portugal",
    "ES": "Spain",
    "FI": "Finland",
    "SE": "Sweden",
    "NO": "Norway",
    "DE": "Germany",    
    "DK": "Denmark",    
}
    
def get_classification_pays(pays: str) -> str:
    """
    Retourne le niveau de risque d'un pays.
       
    Args:
        pays: Nom du pays ou code ISO (FR, BE, LU...)
           
    Returns:
        " FAIBLE" | "MOYEN" | "ELEVE" | "INTERDIT" | "INCONNU"
    """
    # Essai direct par nom 
    if pays in CLASSIFICATION_PAYS:
        return CLASSIFICATION_PAYS[pays]
        
    # Essai par code ISO
    if pays in CODE_ISO_PAYS:
        nom_pays = CODE_ISO_PAYS[pays]
        if nom_pays in CLASSIFICATION_PAYS:
            return CLASSIFICATION_PAYS[nom_pays]
            
    return "INCONNU"

def get_score_pays(pays: str) -> int:
    """
    Retourne le score numérique d'un pays pour le calcul du LC 18/9
    
    Returns:
        0  =FAIBLE
        2  =MOYEN
        4  =ELEVE
        19 = INTERDIT
    """
    scores = {
        "FAIBLE": 0,
        "MOYEN": 2,
        "ELEVE": 4,
        "INTERDIT": 19,
        "INCONNU": 2, # Par precaution
    }
    return scores.get(get_classification_pays(pays), 2) 

def est_pays_interdit(pays: str) -> bool :
    """
    Retourne True si le pays est interdit.
    """
    return get_classification_pays(pays) == "INTERDIT"


# STATISTIQUES
STATS_PAYS = {
    "total" : len(CLASSIFICATION_PAYS),
    "interdits" : len(PAYS_INTERDITS),
    "eleves" : len(PAYS_ELEVE),
    "moyens" : len(PAYS_MOYEN),
    "faibles" : len(PAYS_FAIBLE)
}

# PAYS WEALINS- marchés officials 
PAYS_WEALINS = {
    "France":      48.56,
    "Belgium":     19.13,
    "Portugal":     5.68,
    "Italy":        5.24,
    "Finland":      5.15,
    "Sweden":       4.87,
    "Luxembourg":   4.62,
    "Germany":      1.14,
    "Norway":       1.07,
    "Denmark":      0.58,
    "Spain":        0.45,
    "Monaco":       0.44,
    
}

PAYS_LISTE = list(PAYS_WEALINS.keys())
PAYS_POIDS = list(PAYS_WEALINS.values())


