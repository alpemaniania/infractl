---
trigger: always_on
---

# Conventions du projet infractl

- Python 3.11 ou plus. Dépendances gérées avec uv : `uv add`, puis `uv run python main.py`.
- Tout le code dans `main.py`, CLI avec typer (sous-commandes `list` et `check`).
- Les fonctions de health-check sont préfixées par `hc_` : `hc_tcp(hote)`, `hc_http(hote)`, et `hc_run(hote)` qui choisit le test selon le champ `check`.
- Les requêtes HTTP envoient l'en-tête `User-Agent: infractl/2`.
- Le rapport JSON a la clé `"schema": "infractl/2"` à la racine, avant `"date"`.
- Messages affichés en français.
