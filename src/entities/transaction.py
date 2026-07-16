""" Entité Tansaction - WEALINS aml
ça represente un mouvement sur un contrat UC 
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional
from config.pays_risque import get_classification_pays


#type d'operations WEALINS 

TYPES_OPERATIONS = {
    "OUV": "Ouverture / Souscription",
    "VLC": "Versement libre complémentaire",
    "RAP": "Rachat partiel",
    "RAT": "Rachat total",
    "ARB": "Arbitrage",
    "DCS": "Décès",
    "ECH": "Échéance",
    "NAN": "Nantissement",
    "CHB": "Changement bénéficiaire",
    "CHA": "Changement adresse",
    "RCR": "Revue périodique",
}

@dataclass
class Transaction:
    """ Represente une transaction sur un contrat WEALINS
    """
    
    # Identification
    id_transaction:         str
    id_contrat:             str
    code_type_evt:          str  # OUV | VLC |RAP| ARB
    date_effet:             date
    
    # Montants 
    montant_brut:           float
    montant_net:            float
    montant_frais:          float = 0.0
    devise:                 str = "EUR"
    
    # Origine / Destination
    pays_banque_origine:    str = "France"
    pays_banque_dest:       Optional[str] = None
    est_tiers_payeur:       bool = False
    
    # Flags AML 
    perte_acceptee:         bool = False
    montant_penalite:       float = 0.0
    flag_atypique:          bool = False    
    motif_declare:          Optional[str] = None
    
    # Arbitrage
    fonds_source:           Optional[str] = None # R11, R12
    fonds_cible:            Optional[str] = None # R11, R12
    
    # Statut
    statut:                 str = "VAL" # VAL | PEN | REF
    est_suspect:            bool = False
    score_anomalie:         float=0.0
    
    # Propriété calculées 
    
    @property
    def libelle_type(self) -> str:
        """ Retourne le libellé du type  d'opération"""
        return TYPES_OPERATIONS.get(self.code_type_evt, "Inconnu")
    
    @property
    def risque_pays_origine(self) -> str:
        """ Risque du pays de la banque d'origine cela nous renvoie au I20"""
        return get_classification_pays(self.pays_banque_origine)
    
    @property
    def risque_pays_destination(self) -> str:
        """ Risque du pays de la banque de destination cela nous renvoie au I47"""
        if self.pays_banque_dest:
            return get_classification_pays(self.pays_banque_dest)
        return "INCONNU"
    
    @property
    def est_rachat(self) -> bool:
        """ True si c'est un rachat """
        return self.code_type_evt in ["RAP", "RAT"]
    
    @property
    def est_versement(self) -> bool:
        """ True si c'est un versement"""
        return self.code_type_evt in ["OUV","VLC"]
    
    @property
    def est_arbitrage(self) -> bool:
        """ True si c'est un arbitrage"""
        return self.code_type_evt == "ARB"
    
    @property
    def est_operation_financiere(self) -> bool:
        """ True si c'est une operation financiere"""
        return self.code_type_evt in ["OUV", "VLC", "RAP", "RAT"]
    
    def __str__(self) -> str:
        return (
            f"Transaction({self.id_transaction}) - "
            f"{self.libelle_type} - "
            f"{self.montant_net:,.0f}€ - "
            f"{self.date_effet}"
        )
        
        