# Controleert secrets.py: aanmelden, publiceren en hetzelfde bericht terug ontvangen.
# Het testtopic is weerstation/test/verbinding, niet een echt station.

import sys
import time

import paho.mqtt.client as mqtt

import secrets

TOPIC = "weerstation/test/verbinding"
WACHTEN_S = 8
CLIENT_ID = "thonny-test-verbinding"


def verbinding_mislukt(reason_code):
    if hasattr(reason_code, "is_failure"):
        return reason_code.is_failure
    return int(reason_code) != 0


def nog_voorbeeldwaarden():
    return (
        secrets.MQTT_GEBRUIKER == "GEBRUIKER"
        or secrets.MQTT_WACHTWOORD == "WACHTWOORD"
        or secrets.MQTT_BROKER == "192.168.1.10"
    )


def maak_client():
    if hasattr(mqtt, "CallbackAPIVersion"):
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    return mqtt.Client(client_id=CLIENT_ID)


def main():
    if nog_voorbeeldwaarden():
        print("secrets.py bevat nog voorbeeldwaarden. Vul broker, gebruiker en wachtwoord in.")

    ontvangen = []
    status = {"code": None}

    def on_connect(client, userdata, flags, reason_code, properties=None):
        status["code"] = reason_code
        if not verbinding_mislukt(reason_code):
            client.subscribe(TOPIC)

    def on_message(client, userdata, message):
        ontvangen.append(message.payload.decode("utf-8", errors="replace"))

    client = maak_client()
    client.username_pw_set(secrets.MQTT_GEBRUIKER, secrets.MQTT_WACHTWOORD)
    client.on_connect = on_connect
    client.on_message = on_message

    print("Verbinden met", secrets.MQTT_BROKER, "poort", secrets.MQTT_POORT)
    try:
        client.connect(secrets.MQTT_BROKER, secrets.MQTT_POORT, keepalive=60)
    except OSError as fout:
        print("De broker is niet bereikbaar:", fout)
        return 1

    client.loop_start()
    einde = time.monotonic() + WACHTEN_S
    while time.monotonic() < einde and status["code"] is None:
        time.sleep(0.05)

    if status["code"] is None:
        client.loop_stop()
        print("Geen antwoord van de broker. Controleer het IP-adres en poort 1883.")
        return 1

    if verbinding_mislukt(status["code"]):
        client.loop_stop()
        print("Aanmelden geweigerd. Controleer gebruikersnaam en wachtwoord.")
        print("Foutcode van de broker:", status["code"])
        return 1

    print("Aangemeld. Publiceren op", TOPIC)
    time.sleep(0.3)
    tekst = "test-verbinding"
    client.publish(TOPIC, tekst)

    einde = time.monotonic() + WACHTEN_S
    while time.monotonic() < einde and tekst not in ontvangen:
        time.sleep(0.05)

    client.loop_stop()
    client.disconnect()

    if tekst in ontvangen:
        print("Bericht terugontvangen:", TOPIC, tekst)
        return 0

    print("Aangemeld, maar het testbericht kwam niet terug.")
    print("Controleer of deze gebruiker op", TOPIC, "mag publiceren en ontvangen.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
