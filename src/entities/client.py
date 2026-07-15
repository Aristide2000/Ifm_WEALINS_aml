"""
Entité Client- WEALINS aml
cela représente un preneur d'assurance vie UC 
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from config.pays_risque import get_classification_pays

@dataclass
class Client:
    """
    Cette classe represente un client WEALINS.
    Chaque attribut est justifié par une source
    réglementaire ou métier.
    
    """
    
    # Identification
    id_client:          str
    nom:                str
    prenom:             str
    date_naissance:     date 
    nationalite:        str  # ça nous ramene a ces questions I07,I08,I09
    pays_residence:     str  # ça nous ramene a ces questions I02,I05,I06
    
    # Profil 
    profession:         str  # ça nous ramene a ces questions I16
    secteur_activite:   str
    patrimoine_declare: float
    revenus_declare:    float
    segment:            str
    
    # Structure juridique
    type_client:        str  # c'est un particulier ou une entreprise ça va nous renvoyer a la question I04
    structure_juridique:str  # c'est physique, holding, un trust ça va nous renvoyer a la question I12
    
    # Statut sensibles 
    
    est_pep:            bool = False # cela nous ramene a la question I15
    type_pep:           Optional[str] = None
    est_mep:            bool = False # critère supplémentaire Wealins
    est_sous_sanctions: bool = False # cela nous ramene a la question I14
    est_declare_crf:    bool = False # cela nous ramene a la question I13
    
    # Screening 
    screening_worldcheck: str = "clear" # cela nous ramene a la question I17

    # clear | hit | pending
    
    # Dates
    date_entree_relation: date = field(
        default_factory=date.today
    )
    
    # Propriétés calculées
    
    @property
    def risque_pays_residence(self) -> str:
        """
        Retourne le niveau de risque du pays de residence
        on va l'utiliser pour le I02
        """
        return get_classification_pays(self.pays_residence)
    
    @property
    def est_profil_sensible(self) -> bool:
        """
        Vrai si le client a un profil sensible
        declenche une vigilance renforcée
        """
        return (
            self.est_pep or
            self.est_mep or
            self.est_sous_sanctions or
            self.est_declare_crf or
            self.risque_pays_residence in ["ELEVE", "INTERDIT"]
            
        )
        
    @property
    def classification_risque_base(self) -> str:
        """
        Classification de base avant scoring LC18/9
        """
        if self.est_sous_sanctions:
            return "HIGH"
        if self.est_pep or self.est_declare_crf:
            return "HIGH"
        if self.risque_pays_residence == "INTERDIT":
            return "HIGH"
        if self.risque_pays_residence == "ELEVE":
            return "HIGH"
        if self.est_mep:
            return "HIGH"
        if self.risque_pays_residence == "MOYEN":
            return "MEDIUM"
        return "LOW"
    
    def __str__(self) -> str:
        return (
            f"Client({self.id_client}) — "
            f"{self.prenom} {self.nom} — "
            f"{self.pays_residence} — "
            f"Risque: {self.classification_risque_base}"
        )
        