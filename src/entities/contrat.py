"""
Entité Contrat WEALINS
Représente un contrat d'assurance vie UC
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from config.pays_risque import get_classification_pays


@dataclass
class FondsUC:
    """Représente un fonds sous-jacent UC."""

    id_fonds:         str
    code_isin:        str
    designation:      str
    type_fonds:       str       # "OPCVM" | "FID" | "FAS" | "PE"
    juridiction:      str
    liquidite:        str       # "haute" | "moyenne" | "faible"
    poids_pct:        float     # % du contrat
    valeur_euro:      float
    est_offshore:     bool = False
    flag_mandat:      bool = False

    @property
    def risque_juridiction(self) -> str:
        """Retourne le risque de la juridiction du fonds."""
        return get_classification_pays(self.juridiction)

    @property
    def est_suspect(self) -> bool:
        """True si le fonds présente des caractéristiques suspectes."""
        return (
            self.est_offshore or
            self.risque_juridiction in ["ELEVE", "INTERDIT"] or
            self.type_fonds == "PE"
        )


@dataclass
class Contrat:
    """
    Représente un contrat d'assurance vie UC Wealins.
    """

    # ─── Identification ───────────────────────────
    id_contrat:           str
    num_contrat:          str
    id_client:            str

    # ─── Produit ──────────────────────────────────
    produit:              str        # "WEACFR" | "WEALIFE"
    type_produit:         str        # "AV" | "CAP"
    regime_fiscal:        str        # "AV" | "CAP"
    mode_gestion:         str        # "C" | "L"

    # ─── Financier ────────────────────────────────
    prime_initiale:       float
    somme_versements:     float
    somme_rachats:        float
    valeur_actuelle:      float

    # ─── Dates ────────────────────────────────────
    date_souscription:    date
    date_derniere_revue:  Optional[date] = None
    date_prochaine_revue: Optional[date] = None

    # ─── Flags ────────────────────────────────────
    flag_nantissement:    bool = False
    statut:               str = "actif"   # "actif" | "racheté" | "clôturé"

    # ─── Intermédiaire ────────────────────────────
    intermediaire:        str = ""
    pays_intermediaire:   str = "France"

    # ─── Scoring AML ──────────────────────────────
    score_lc189:          int = 0
    risque_contrat:       str = "LOW"
    remediation_ouverte:  bool = False

    # ─── Fonds UC ─────────────────────────────────
    fonds: list = field(default_factory=list)

    # ─── Propriétés calculées ─────────────────────

    @property
    def duree_jours(self) -> int:
        """Durée du contrat en jours depuis souscription."""
        return (date.today() - self.date_souscription).days

    @property
    def taux_rachat(self) -> float:
        """Ratio rachats / versements."""
        if self.somme_versements == 0:
            return 0.0
        return self.somme_rachats / self.somme_versements

    @property
    def est_contrat_suspect(self) -> bool:
        """True si le contrat présente des signaux suspects."""
        return (
            self.risque_contrat == "HIGH" or
            self.flag_nantissement or
            self.taux_rachat > 0.8
        )

    @property
    def a_fonds_offshore(self) -> bool:
        """True si le contrat contient des fonds offshore."""
        return any(f.est_offshore for f in self.fonds)

    @property
    def segment_prime(self) -> str:
        """Segment selon le montant de la prime initiale."""
        if self.prime_initiale >= 2_500_000:
            return "TRES_ELEVE"
        elif self.prime_initiale >= 250_000:
            return "ELEVE"
        else:
            return "STANDARD"

    def __str__(self) -> str:
        return (
            f"Contrat({self.id_contrat}) — "
            f"Client: {self.id_client} — "
            f"Prime: {self.prime_initiale:,.0f}€ — "
            f"Risque: {self.risque_contrat}"
        )