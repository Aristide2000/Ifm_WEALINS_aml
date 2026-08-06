"""Tests pour le rules engine AML."""

import pandas as pd
from datetime import date
from src.detection.rules_engine import (
    appliquer_regles,
    REGLES,
)


def make_client(est_pep=False, sanctions=False,
                structure="physique"):
    return pd.Series({
        "id_client":            "CLI_001",
        "pays_residence":       "France",
        "nationalite":          "France",
        "est_pep":              est_pep,
        "type_pep":             "PPE1" if est_pep else None,
        "est_sous_sanctions":   sanctions,
        "structure_juridique":  structure,
        "est_declare_crf":      False,
        "screening_worldcheck": "clear",
    })


def make_contrat(pays_inter="France", nantissement=False):
    return pd.Series({
        "id_contrat":         "BA000001",
        "id_client":          "CLI_001",
        "prime_initiale":     500_000,
        "pays_intermediaire": pays_inter,
        "flag_nantissement":  nantissement,
        "date_souscription":  "2024-01-01",
    })


def make_transactions(rachat_precoce=False,
                      perte=False,
                      pays_suspect=False,
                      tiers=False):
    trx = [{
        "id_transaction":      "EVT_001",
        "id_contrat":          "BA000001",
        "code_type_evt":       "OUV",
        "date_effet":          "2024-01-01",
        "montant_total_brut":  500_000,
        "montant_total_net":   500_000,
        "pays_banque_origine": "France",
        "pays_banque_dest":    None,
        "est_tiers_payeur":    False,
        "perte_acceptee":      False,
    }]
    if rachat_precoce:
        trx.append({
            "id_transaction":      "EVT_002",
            "id_contrat":          "BA000001",
            "code_type_evt":       "RAP",
            "date_effet":          "2024-03-01",
            "montant_total_brut":  -400_000,
            "montant_total_net":   -388_000,
            "pays_banque_origine": "Russia" if pays_suspect
                                   else "France",
            "pays_banque_dest":    "Cayman Islands",
            "est_tiers_payeur":    tiers,
            "perte_acceptee":      perte,
        })
    return pd.DataFrame(trx)


def test_client_propre_aucune_alerte():
    """Client standard sans anomalie."""
    alertes = appliquer_regles(
        make_client(),
        make_contrat(),
        make_transactions()
    )
    codes = [a["code_regle"] for a in alertes]
    assert "R01" not in codes
    assert "R02" not in codes
    assert "R03" not in codes


def test_rachat_precoce_r01():
    """Rachat dans les 6 mois → R01."""
    alertes = appliquer_regles(
        make_client(),
        make_contrat(),
        make_transactions(rachat_precoce=True)
    )
    codes = [a["code_regle"] for a in alertes]
    assert "R01" in codes


def test_perte_acceptee_r02():
    """Perte acceptée → R02."""
    alertes = appliquer_regles(
        make_client(),
        make_contrat(),
        make_transactions(rachat_precoce=True, perte=True)
    )
    codes = [a["code_regle"] for a in alertes]
    assert "R02" in codes


def test_pays_interdit_r03():
    """Pays interdit → R03 CRITICAL."""
    alertes = appliquer_regles(
        make_client(),
        make_contrat(),
        make_transactions(
            rachat_precoce=True,
            pays_suspect=True
        )
    )
    codes = [a["code_regle"] for a in alertes]
    assert "R03" in codes
    r03 = [a for a in alertes if a["code_regle"] == "R03"][0]
    assert r03["niveau"] == "CRITICAL"


def test_pep_avec_rachat_r05():
    """PEP avec rachat → R05."""
    alertes = appliquer_regles(
        make_client(est_pep=True),
        make_contrat(),
        make_transactions(rachat_precoce=True)
    )
    codes = [a["code_regle"] for a in alertes]
    assert "R05" in codes


def test_pattern_blanchiment_r09():
    """Rachat précoce + perte → R09 CRITICAL."""
    alertes = appliquer_regles(
        make_client(),
        make_contrat(),
        make_transactions(
            rachat_precoce=True,
            perte=True
        )
    )
    codes = [a["code_regle"] for a in alertes]
    assert "R09" in codes
    r09 = [a for a in alertes if a["code_regle"] == "R09"][0]
    assert r09["niveau"] == "CRITICAL"


def test_nb_regles():
    """Vérifier qu'on a bien 12 règles."""
    assert len(REGLES) == 12