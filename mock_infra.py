"""Infra simulée du TP infractl.

    web     port 8080 : répond tout de suite
    api     port 8081 : répond en 1 s
    lent    port 8082 : répond en 3 s
    db      port 5432 : éteint, rien n'écoute
    webhook port 9000 : affiche les messages reçus (bonus)

Si la variable API_TOKEN est définie au lancement, l'api exige
l'en-tête "Authorization: Bearer <API_TOKEN>" (bonus).

Lancement : python3 mock_infra.py   (Ctrl+C pour arrêter)
"""
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

API_TOKEN = os.environ.get("API_TOKEN")


def make_handler(name, delay, need_token=False):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            time.sleep(delay)
            if need_token and API_TOKEN:
                if self.headers.get("Authorization") != f"Bearer {API_TOKEN}":
                    return self.send_json(401, {"error": "token invalide"})
            self.send_json(200, {"service": name, "status": "up"})

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode()
            print(f"[{name}] message reçu : {body}", flush=True)
            self.send_json(200, {"received": True})

        def send_json(self, code, data):
            payload = json.dumps(data).encode()
            try:
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except (BrokenPipeError, ConnectionResetError):
                pass  # le client a abandonné (timeout côté infractl)

        def log_message(self, format, *args):
            print(f"[{name}] {self.address_string()} {format % args}", flush=True)

    return Handler


SERVICES = [
    ("web", 8080, 0, False),
    ("api", 8081, 1, True),
    ("lent", 8082, 3, False),
    ("webhook", 9000, 0, False),
]


def main():
    servers = []
    for name, port, delay, need_token in SERVICES:
        try:
            server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(name, delay, need_token))
        except OSError:
            # port déjà pris (mock déjà lancé, Docker...) : on continue sans ce service
            print(f"{name:8} port {port} déjà utilisé : service non lancé", flush=True)
            continue
        threading.Thread(target=server.serve_forever, daemon=True).start()
        servers.append(server)
        print(f"{name:8} http://127.0.0.1:{port}  (délai {delay} s)", flush=True)
    if not servers:
        print("Aucun service lancé : mock_infra.py tourne sans doute déjà dans un autre terminal.")
        return
    print("db       127.0.0.1:5432  éteint")
    if API_TOKEN:
        print("api : token exigé")
    print("Ctrl+C pour arrêter", flush=True)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for server in servers:
            server.shutdown()


if __name__ == "__main__":
    main()
