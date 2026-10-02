# infractl : dossier de départ du TP

Ce dépôt contient l'infra simulée et l'inventaire du TP. Votre code va dans ce même dossier.

```bash
git clone <url-du-depot> infractl
cd infractl
uv init --no-package
uv add requests pyyaml typer
uv run python main.py           # affiche « Hello from infractl! »
```

Dans un second terminal, depuis ce dossier :

```bash
python3 mock_infra.py           # à laisser tourner
```

| Fichier | Rôle |
|---|---|
| `mock_infra.py` | Infra simulée : web (8080), api (8081), lent (8082), webhook (9000). db (5432) est éteint |
| `inventory.yaml` | Les six hôtes à vérifier |

Faites un commit à la fin de chaque palier : `git add -A && git commit -m "palier 1"`. Co-authored si c'est le cas.
