from pathlib import Path
import json
from datetime import datetime
import logging
import socket
import time
import requests
import typer
import yaml

app = typer.Typer()

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(message)s"
)


def charger(f):
    texte = Path(f).read_text(encoding="utf-8")
    data = yaml.safe_load(texte)

    hosts = data["hosts"]

    return hosts


def verifier(host):
    debut = time.perf_counter()

    try:
        type_check = host["check"]

        if type_check == "tcp":
            adresse = host["address"]
            port = host["port"]

            connexion = socket.create_connection(
                (adresse, port),
                timeout=2
            )

            connexion.close()

        else:
            adresse = host["address"]
            port = str(host["port"])

            if "path" in host:
                chemin = host["path"]
            else:
                chemin = "/"

            url = "http://" + adresse + ":" + port + chemin

            reponse = requests.get(url, timeout=2)
            reponse.raise_for_status()

    except (TimeoutError, requests.Timeout):
        message = host["name"] + " : pas de réponse en 2 s"
        logging.error(message)

        resultat = {}
        resultat["host"] = host["name"]
        resultat["status"] = "KO"
        resultat["check"] = host["check"]
        resultat["error"] = "timeout"

        return resultat

    except (ConnectionRefusedError, requests.ConnectionError):
        message = host["name"] + " : connexion refusée"
        logging.error(message)

        resultat = {}
        resultat["host"] = host["name"]
        resultat["status"] = "KO"
        resultat["check"] = host["check"]
        resultat["error"] = "refusé"

        return resultat

    except (OSError, requests.RequestException) as erreur:
        message = host["name"] + " : " + str(erreur)
        logging.error(message)

        resultat = {}
        resultat["host"] = host["name"]
        resultat["status"] = "KO"
        resultat["check"] = host["check"]
        resultat["error"] = str(erreur)

        return resultat

    fin = time.perf_counter()
    temps = fin - debut
    temps_ms = round(temps * 1000)

    resultat = {}
    resultat["host"] = host["name"]
    resultat["status"] = "OK"
    resultat["check"] = host["check"]
    resultat["ms"] = temps_ms

    return resultat


@app.callback()
def main():
    pass


@app.command("list")
def lister(group: str = ""):
    hosts = charger("inventory.yaml")

    for h in hosts:
        afficher = False

        if group == "":
            afficher = True
        elif h["group"] == group:
            afficher = True

        if afficher:
            adresse = h["address"] + ":" + str(h["port"])

            print(
                h["name"],
                adresse,
                h["group"]
            )


@app.command()
def check(
    group: str = "",
    dry_run: bool = False,
    output: str = ""
):
    hosts = charger("inventory.yaml")

    if dry_run:
        print("dry-run : rien n'est testé")

        for h in hosts:
            afficher = False

            if group == "":
                afficher = True
            elif h["group"] == group:
                afficher = True

            if afficher:
                adresse = h["address"] + ":" + str(h["port"])

                print(
                    h["name"],
                    h["check"],
                    adresse
                )

        raise typer.Exit()

    ko = False
    resultats = []

    for h in hosts:

        if group != "":
            if h["group"] != group:
                continue

        resultat = verifier(h)

        resultats.append(resultat)

        statut = resultat["status"]

        if statut == "OK":
            nom = resultat["host"]
            check_type = resultat["check"]
            temps = resultat["ms"]

            print(
                nom,
                "OK",
                check_type,
                temps,
                "ms"
            )

        else:
            nom = resultat["host"]
            check_type = resultat["check"]
            erreur = resultat["error"]

            print(
                nom,
                "KO",
                check_type,
                erreur
            )

            ko = True

    if output != "":
        rapport = {}

        maintenant = datetime.now()
        date_maintenant = maintenant.isoformat(
            timespec="seconds"
        )

        rapport["date"] = date_maintenant

        liste_resultats = resultats
        rapport["results"] = liste_resultats

        texte = json.dumps(
            rapport,
            indent=2,
            ensure_ascii=False
        )

        fichier_sortie = Path(output)

        fichier_sortie.write_text(
            texte,
            encoding="utf-8"
        )

        message = "rapport écrit dans " + output
        logging.info(message)

    if ko:
        code_erreur = 1
        raise typer.Exit(code=code_erreur)


if __name__ == "__main__":
    app()
