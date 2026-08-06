from src.data.generateur import generer_dataset_complet
from src.scoring.scoring_lc189 import scorer_portefeuille

data = generer_dataset_complet(nb_clients=50, save=False)
scores = scorer_portefeuille(
    data["clients"],
    data["contrats"],
    data["transactions"]
)
print(scores[["id_contrat", "score_total", "classification"]].head())