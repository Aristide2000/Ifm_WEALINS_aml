""" 
Entité Alerte AML WEALINS
Représente une alerte générée par le systeme 
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

# types d'alertes possibles

TYPES_ALERTES = {
    "rachat_suspect":    "Rachat suspect (précoce ou avec perte)",
    "paiement_atypique": "Paiement atypique",
    "pays_interdit":     "Transaction avec pays interdit",
    "pep_detecte":       "PEP détecté",
    "sanctions":         "Client sous sanctions",
    "structuring":       "Fragmentation suspecte",
    "fonds_offshore":    "Fonds offshore opaque",
    "tiers_payeur":      "Paiement par tiers non justifié",
    "score_eleve":       "Score LC 18/9 élevé",
    "anomalie_ml":       "Anomalie détectée par ML",
}

# Comités selon le niveau de risque
COMITE_PAR_RISQUE = {
     "LOW":      "CAO",
    "MEDIUM":   "CAR",
    "HIGH":     "CAR",
    "CRITICAL": "COMPLIANCE",
}

@dataclass
class AlerteAML:
    """ 
    Représente une alerte AML générée par le système
    """
    
    # Identification
    id_alerte:           str
    id_contrat:          str
    date_detection:      date

    # Type et source 
    type_alerte:         str
    source_detection:    str     # "rules_engine" | "isolation_forest" | "xgboost"
    description:         str

    # Scoring 
    score_risque:        float   # 0 à 1
    niveau_alerte:       str     # LOW | MEDIUM | HIGH | CRITICAL

    # Workflow 
    statut:              str = "ouverte"   # ouverte | en_cours | clôturée
    decision:            Optional[str] = None
    commentaire:         Optional[str] = None
    date_cloture:        Optional[date] = None

    # Déclaration CRF 
    declaration_crf:     bool = False
    type_declaration:    Optional[str] = None  # SAR | STR | TFAR | TFTR
    reference_crf:       Optional[str] = None

    #  Transactions liées 
    id_transactions:     list = field(default_factory=list)

    #  SHAP / Explicabilité
    raisons_principales: list = field(default_factory=list)

    # Comité:calculé automatiquement 
    comite:              str = field(init=False)

    def __post_init__(self):
        """Calcule automatiquement le comité selon le niveau."""
        self.comite = COMITE_PAR_RISQUE.get(
            self.niveau_alerte, "CAR"
        )

    # Propriétés calculées 

    @property
    def libelle_type(self) -> str:
        """Retourne le libellé du type d'alerte."""
        return TYPES_ALERTES.get(
            self.type_alerte, "Alerte inconnue"
        )

    @property
    def necessite_declaration_crf(self) -> bool:
        """True si l'alerte nécessite une déclaration CRF."""
        return (
            self.niveau_alerte in ["HIGH", "CRITICAL"] or
            self.type_alerte in ["pays_interdit", "sanctions"]
        )

    @property
    def est_critique(self) -> bool:
        """True si l'alerte est critique."""
        return self.niveau_alerte == "CRITICAL"

    def escalader(self) -> str:
        """Retourne le comité vers lequel escalader."""
        return COMITE_PAR_RISQUE.get(
            self.niveau_alerte, "CAR"
        )

    def __str__(self) -> str:
        return (
            f"Alerte({self.id_alerte}) — "
            f"{self.libelle_type} — "
            f"Score: {self.score_risque:.2f} — "
            f"Niveau: {self.niveau_alerte} — "
            f"Comité: {self.comite}"
        )