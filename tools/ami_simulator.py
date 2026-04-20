"""
Simulateur Asterisk AMI pour tester la détection de tonalité fax.

Écoute sur le port 5038 et simule les réponses AMI :
  - Login / Logoff
  - Originate → événements AMD/FaxDetect aléatoires

Usage: python tools/ami_simulator.py
"""

import random
import socket
import threading
import time
import sys

HOST = "127.0.0.1"
PORT = 5038

# Scénarios de simulation
SCENARIOS = [
    {
        "name": "FAX (CNG détecté)",
        "amd_status": "MACHINE",
        "amd_cause": "TONEFAX-1100",
        "fax_detected": True,
        "hangup_cause": 16,
    },
    {
        "name": "FAX (CED détecté)",
        "amd_status": "MACHINE",
        "amd_cause": "TONEFAX-2100",
        "fax_detected": True,
        "hangup_cause": 16,
    },
    {
        "name": "VOIX humaine",
        "amd_status": "HUMAN",
        "amd_cause": "HUMAN-50-50",
        "fax_detected": False,
        "hangup_cause": 16,
    },
    {
        "name": "Répondeur",
        "amd_status": "MACHINE",
        "amd_cause": "LONGGREETING-3000-3000",
        "fax_detected": False,
        "hangup_cause": 16,
    },
    {
        "name": "Pas de réponse",
        "amd_status": "",
        "amd_cause": "",
        "fax_detected": False,
        "hangup_cause": 19,
    },
    {
        "name": "Occupé",
        "amd_status": "",
        "amd_cause": "",
        "fax_detected": False,
        "hangup_cause": 17,
    },
]


def handle_client(conn, addr):
    print(f"[+] Connexion de {addr}")

    # Banner Asterisk
    conn.sendall(b"Asterisk Call Manager/6.0.0\r\n")

    buffer = ""
    action_id = ""
    logged_in = False

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            buffer += data.decode("utf-8", errors="replace")

            # Traiter les messages complets (séparés par \r\n\r\n)
            while "\r\n\r\n" in buffer:
                msg, buffer = buffer.split("\r\n\r\n", 1)
                lines = msg.strip().split("\r\n")
                headers = {}
                for line in lines:
                    if ":" in line:
                        k, _, v = line.partition(":")
                        headers[k.strip()] = v.strip()

                action = headers.get("Action", "").lower()
                action_id = headers.get("ActionID", "")

                if action == "login":
                    user = headers.get("Username", "")
                    secret = headers.get("Secret", "")
                    print(f"    Login: {user} / {'*' * len(secret)}")

                    if user == "faxcloud" and secret == "faxcloud2026":
                        resp = (
                            f"Response: Success\r\n"
                            f"ActionID: {action_id}\r\n"
                            f"Message: Authentication accepted\r\n"
                            f"\r\n"
                        )
                        logged_in = True
                        print("    → Auth OK")
                    else:
                        resp = (
                            f"Response: Error\r\n"
                            f"ActionID: {action_id}\r\n"
                            f"Message: Authentication failed\r\n"
                            f"\r\n"
                        )
                        print(f"    → Auth ECHEC ({user})")
                    conn.sendall(resp.encode())

                elif action == "logoff":
                    resp = (
                        f"Response: Goodbye\r\n"
                        f"ActionID: {action_id}\r\n"
                        f"Message: Thanks for all the fish.\r\n"
                        f"\r\n"
                    )
                    conn.sendall(resp.encode())
                    print("    Logoff")
                    return

                elif action == "originate":
                    channel = headers.get("Channel", "")
                    context = headers.get("Context", "")
                    timeout_ms = headers.get("Timeout", "15000")
                    numero = channel.split("/")[-1].split("@")[0]

                    print(f"    Originate: {channel} → {context}")
                    print(f"    Numéro: {numero}")

                    # Réponse immédiate
                    resp = (
                        f"Response: Success\r\n"
                        f"ActionID: {action_id}\r\n"
                        f"Message: Originate successfully queued\r\n"
                        f"\r\n"
                    )
                    conn.sendall(resp.encode())

                    # Simuler un délai d'appel (1-3 secondes)
                    delay = random.uniform(1.0, 3.0)
                    time.sleep(delay)

                    # Choisir un scénario aléatoire
                    scenario = random.choice(SCENARIOS)
                    print(f"    → Scénario: {scenario['name']}")

                    chan_name = f"Local/{numero}@{context}-00000001;1"
                    unique_id = f"1713600000.{random.randint(100, 999)}"

                    events = []

                    # Événement Newchannel
                    events.append(
                        f"Event: Newchannel\r\n"
                        f"Channel: {chan_name}\r\n"
                        f"Uniqueid: {unique_id}\r\n"
                        f"ActionID: {action_id}\r\n"
                        f"\r\n"
                    )

                    # Événement Answer
                    events.append(
                        f"Event: Newstate\r\n"
                        f"Channel: {chan_name}\r\n"
                        f"ChannelState: 6\r\n"
                        f"ChannelStateDesc: Up\r\n"
                        f"ActionID: {action_id}\r\n"
                        f"\r\n"
                    )

                    # AMD Status
                    if scenario["amd_status"]:
                        events.append(
                            f"Event: ChannelVarSet\r\n"
                            f"Channel: {chan_name}\r\n"
                            f"Variable: AMDSTATUS\r\n"
                            f"Value: {scenario['amd_status']}\r\n"
                            f"Uniqueid: {unique_id}\r\n"
                            f"ActionID: {action_id}\r\n"
                            f"\r\n"
                        )
                        if scenario["amd_cause"]:
                            events.append(
                                f"Event: ChannelVarSet\r\n"
                                f"Channel: {chan_name}\r\n"
                                f"Variable: AMDCAUSE\r\n"
                                f"Value: {scenario['amd_cause']}\r\n"
                                f"Uniqueid: {unique_id}\r\n"
                                f"ActionID: {action_id}\r\n"
                                f"\r\n"
                            )

                    # Fax Detected
                    if scenario["fax_detected"]:
                        events.append(
                            f"Event: ChannelVarSet\r\n"
                            f"Channel: {chan_name}\r\n"
                            f"Variable: FAXDETECTED\r\n"
                            f"Value: 1\r\n"
                            f"Uniqueid: {unique_id}\r\n"
                            f"ActionID: {action_id}\r\n"
                            f"\r\n"
                        )

                    # Hangup
                    events.append(
                        f"Event: Hangup\r\n"
                        f"Channel: {chan_name}\r\n"
                        f"Uniqueid: {unique_id}\r\n"
                        f"Cause: {scenario['hangup_cause']}\r\n"
                        f"Cause-txt: Normal Clearing\r\n"
                        f"ActionID: {action_id}\r\n"
                        f"\r\n"
                    )

                    # Envoyer les événements avec un petit délai entre chaque
                    for evt in events:
                        conn.sendall(evt.encode())
                        time.sleep(0.1)

                elif action == "sippeers":
                    resp = (
                        f"Response: Success\r\n"
                        f"ActionID: {action_id}\r\n"
                        f"EventList: start\r\n"
                        f"Message: Peer status list will follow\r\n"
                        f"\r\n"
                        f"Event: PeerEntry\r\n"
                        f"ActionID: {action_id}\r\n"
                        f"ObjectName: 100\r\n"
                        f"Callerid: \"Fax 1\" <0493095001>\r\n"
                        f"Status: OK\r\n"
                        f"\r\n"
                        f"Event: PeerEntry\r\n"
                        f"ActionID: {action_id}\r\n"
                        f"ObjectName: 101\r\n"
                        f"Callerid: \"Fax 2\" <0493095002>\r\n"
                        f"Status: OK\r\n"
                        f"\r\n"
                        f"Event: PeerlistComplete\r\n"
                        f"ActionID: {action_id}\r\n"
                        f"EventList: Complete\r\n"
                        f"ListItems: 2\r\n"
                        f"\r\n"
                    )
                    conn.sendall(resp.encode())
                    print("    → SIPpeers (2 simulés)")

                elif action == "pjsipshowendpoints":
                    resp = (
                        f"Response: Success\r\n"
                        f"ActionID: {action_id}\r\n"
                        f"EventList: start\r\n"
                        f"\r\n"
                        f"Event: EndpointList\r\n"
                        f"ActionID: {action_id}\r\n"
                        f"ObjectName: 100\r\n"
                        f"Endpoint: 100\r\n"
                        f"DeviceState: Not in use\r\n"
                        f"\r\n"
                        f"Event: EndpointListComplete\r\n"
                        f"ActionID: {action_id}\r\n"
                        f"EventList: Complete\r\n"
                        f"ListItems: 1\r\n"
                        f"\r\n"
                    )
                    conn.sendall(resp.encode())
                    print("    → PJSIPShowEndpoints (1 simulé)")

                else:
                    resp = (
                        f"Response: Error\r\n"
                        f"ActionID: {action_id}\r\n"
                        f"Message: Action '{action}' not supported\r\n"
                        f"\r\n"
                    )
                    conn.sendall(resp.encode())
                    print(f"    Action inconnue: {action}")

    except (ConnectionResetError, BrokenPipeError, OSError):
        pass
    finally:
        conn.close()
        print(f"[-] Déconnexion de {addr}")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((HOST, PORT))
    except OSError as e:
        print(f"Erreur: impossible d'écouter sur {HOST}:{PORT} — {e}")
        sys.exit(1)

    server.listen(5)
    print(f"{'=' * 50}")
    print(f"  Simulateur AMI Asterisk")
    print(f"  Écoute sur {HOST}:{PORT}")
    print(f"  Login: faxcloud / faxcloud2026")
    print(f"{'=' * 50}")
    print(f"  Scénarios aléatoires:")
    for s in SCENARIOS:
        print(f"    - {s['name']}")
    print(f"{'=' * 50}")
    print()

    try:
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\nArrêt du simulateur.")
    finally:
        server.close()


if __name__ == "__main__":
    main()
