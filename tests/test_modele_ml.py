"""Tests pour les modèles ML."""

import pandas as pd
from src.data.generateur import generer_dataset_complet
from src.detection.modele_ml import (
    creer_features,
    entrainer_isolation_forest,
    entrainer_xgboost,
    pipeline_ml,
)


def get_dataset():
    return generer_dataset_complet(
        nb_clients=100,
        save=False
    )


def test_creer_features():
    dataset  = get_dataset()
    features = creer_features(
        dataset["clients"],
        dataset["contrats"],
        dataset["transactions"],
    )
    assert len(features) > 0
    assert "score_lc189" in features.columns
    assert "est_pep" in features.columns
    assert "delai_min_rachat_jours" in features.columns
    assert "est_suspect" in features.columns
    assert "est_structure_morale" in features.columns


def test_isolation_forest():
    dataset  = get_dataset()
    features = creer_features(
        dataset["clients"],
        dataset["contrats"],
        dataset["transactions"],
    )
    modele, features_avec_scores = entrainer_isolation_forest(features)
    assert modele is not None
    assert "score_isolation_forest" in features_avec_scores.columns
    assert features_avec_scores["score_isolation_forest"].min() >= 0
    assert features_avec_scores["score_isolation_forest"].max() <= 1


def test_xgboost():
    dataset  = get_dataset()
    features = creer_features(
        dataset["clients"],
        dataset["contrats"],
        dataset["transactions"],
    )
    _, features_if = entrainer_isolation_forest(features)
    modele, metriques, importance = entrainer_xgboost(features_if)
    if modele is not None:
        assert metriques["auc"] > 0.5
        assert len(importance) > 0


def test_pipeline_complet():
    dataset   = get_dataset()
    resultats = pipeline_ml(
        dataset["clients"],
        dataset["contrats"],
        dataset["transactions"],
        save=False,
    )
    assert "features" in resultats
    assert "modele_if" in resultats
    assert len(resultats["features"]) > 0