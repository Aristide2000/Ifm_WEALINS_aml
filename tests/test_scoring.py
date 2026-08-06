"""Tests pour le moteur de scoring LC 18/9"""

import pandas as pd
from datetime import date
from src.scoring.scoring_lc189 import scorer_contrat


def make_client(
    pays="France",
    est_pep=False,
    sanctions=False,
    structure="physique",
    profession="Chef d'entreprise",
    screening="clear",
):
    return pd.Series({
        "id_client":            "CLI_001",
        "pays_residence":       pays,
        "nationalite":          pays,
        "profession":           profession,
        "structure_juridique":  structure,
        "est_pep":              est_pep,
        "est_mep":              False,
        "est_sous_sanctions":   sanctions,
        "est_declare_crf":      False,
        "screening_worldcheck": screening,
    })


def make_contrat(prime=500_000):
    return pd.Series({
        "id_contrat":          "BA000001",
        "id_client":           "CLI_001",
        "type_produit":        "AV",
        "prime_initiale":      prime,
        "date_souscription":   date(2022, 1, 1),
        "flag_nantissement":   False,
        "pays_intermediaire":  "France",
    })


def make_transactions(
    avec_rachat=False,
    rachat_precoce=False,
    perte=False,
):
    trx = [{
        "id_transaction":   "EVT_001",
        "id_contrat":       "BA000001",
        "code_type_evt":    "OUV",
        "date_effet":       date(2022, 1, 1),
        "montant_total_brut": 500_000,
        "montant_total_net":  500_000,
        "est_tiers_payeur": False,
        "perte_acceptee":   False,
    }]
    if avec_rachat:
        trx.append({
            "id_transaction":   "EVT_002",
            "id_contrat":       "BA000001",
            "code_type_evt":    "RAP",
            "date_effet":       date(2022, 3, 1) if rachat_precoce
                                else date(2024, 1, 1),
            "montant_total_brut": -100_000,
            "montant_total_net":  -97_000,
            "est_tiers_payeur": False,
            "perte_acceptee":   perte,
        })
    return pd.DataFrame(trx)

def test_client_standard_low():
    """Client standard français → LOW"""
    score = scorer_contrat(
        make_client(),
        make_contrat(),
        make_transactions()
    )
    assert score["classification"] == "LOW"
    assert score["score_total"] <= 10


def test_client_pep_high():
    """Client PEP → HIGH automatique"""
    score = scorer_contrat(
        make_client(est_pep=True),
        make_contrat(),
        make_transactions()
    )
    assert score["classification"] == "HIGH"
    assert "I15" in score["flags_high_auto"]


def test_client_sanctions_high():
    """Client sous sanctions → HIGH"""
    score = scorer_contrat(
        make_client(sanctions=True),
        make_contrat(),
        make_transactions()
    )
    assert score["classification"] == "HIGH"
    assert "I14" in score["flags_high_auto"]


def test_client_moral_high():
    """Client moral → HIGH automatique I04"""
    score = scorer_contrat(
        make_client(structure="moral"),
        make_contrat(),
        make_transactions()
    )
    assert score["classification"] == "HIGH"
    assert "I04" in score["flags_high_auto"]


def test_rachat_suspect_high():
    """Rachat précoce avec perte → score élevé"""
    score = scorer_contrat(
        make_client(),
        make_contrat(),
        make_transactions(
            avec_rachat=True,
            rachat_precoce=True,
            perte=True
        )
    )
    assert score["classification"] == "HIGH"