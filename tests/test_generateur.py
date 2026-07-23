"""Tests pour le générateur de données."""

from src.data.generateur import (
    generer_clients,
    generer_contrats,
    generer_transactions,
    generer_dataset_complet,
)


def test_generer_clients():
    clients = generer_clients(100)
    assert len(clients) == 100
    assert "id_client" in clients.columns
    assert "est_pep" in clients.columns
    assert "patrimoine_declare" in clients.columns
    assert clients["patrimoine_declare"].min() >= 125_000


def test_generer_contrats():
    clients = generer_clients(50)
    contrats = generer_contrats(clients)
    assert len(contrats) >= 50
    assert "id_contrat" in contrats.columns
    assert "prime_initiale" in contrats.columns
    assert contrats["prime_initiale"].min() >= 250_000


def test_generer_transactions():
    from src.data.generateur import generer_fonds_uc
    clients      = generer_clients(20)
    contrats     = generer_contrats(clients)
    fonds        = generer_fonds_uc(contrats)
    transactions = generer_transactions(contrats, fonds)
    assert len(transactions) >= len(contrats)
    assert "code_type_evt" in transactions.columns
    assert "OUV" in transactions["code_type_evt"].values
    assert "ARB" in transactions["code_type_evt"].values


def test_dataset_complet():
    dataset = generer_dataset_complet(
        nb_clients=50,
        save=False
    )
    assert "clients" in dataset
    assert "contrats" in dataset
    assert "transactions" in dataset
    assert len(dataset["clients"]) == 50
    assert dataset["transactions"]["est_suspect"].sum() > 0