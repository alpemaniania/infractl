from pathlib import Path
import typer
import yaml

app = typer.Typer()


def charger(fichier):
    texte = Path(fichier).read_text(encoding="utf-8")
    inventaire = yaml.safe_load(texte)
    return inventaire["hosts"]


@app.callback()
def main():
    pass


@app.command("list")
def lister(group: str = ""):
    hotes = charger("inventory.yaml")
    for hote in hotes:
        if group == "" or hote["group"] == group:
            print(hote["name"], hote["address"] + ":" + str(hote["port"]), hote["group"])


if __name__ == "__main__":
    app()