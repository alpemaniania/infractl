from pathlib import Path
import socket
import time
import requests
import typer
import yaml

app = typer.Typer()


def charger(fichier):
    texte = Path(fichier).read_text(encoding="utf-8")
    inventaire = yaml.safe_load(texte)
    return inventaire["hosts"]


def verifier(hote):
    debut = time.perf_counter()
    if hote["check"] == "tcp":
        with socket.create_connection((hote["address"], hote["port"]), timeout=2):
            pass
    else:
        url = "http://" + hote["address"] + ":" + str(hote["port"]) + hote.get("path", "/")
        reponse = requests.get(url, timeout=2)
        reponse.raise_for_status()
    ms = round((time.perf_counter() - debut) * 1000)
    return {"host": hote["name"], "status": "OK", "check": hote["check"], "ms": ms}


@app.callback()
def main():
    pass


@app.command("list")
def lister(group: str = ""):
    hotes = charger("inventory.yaml")
    for hote in hotes:
        if group == "" or hote["group"] == group:
            print(hote["name"], hote["address"] + ":" + str(hote["port"]), hote["group"])


@app.command()
def check(group: str = ""):
    hotes = charger("inventory.yaml")
    for hote in hotes:
        if group == "" or hote["group"] == group:
            resultat = verifier(hote)
            print(resultat["host"], resultat["status"], resultat["check"], resultat["ms"], "ms")


if __name__ == "__main__":
    app()