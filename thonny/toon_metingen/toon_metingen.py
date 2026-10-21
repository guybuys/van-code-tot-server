# Toont MQTT-berichten van een of meer weerstations als tekst.
# Stoppen: de stopknop in Thonny.

import paho.mqtt.client as mqtt

import secrets

# Eén regel per weerstation.
# "weerstation/+/meting" luistert naar elk station op dat pad.
TOPICS = [
    "weerstation/1/meting",
    "weerstation/2/meting",
]

CLIENT_ID = "thonny-toon-metingen"


def verbinding_mislukt(reason_code):
    if hasattr(reason_code, "is_failure"):
        return reason_code.is_failure
    return int(reason_code) != 0


def on_connect(client, userdata, flags, reason_code, properties=None):
    if verbinding_mislukt(reason_code):
        print("Verbinding met EMQX mislukt:", reason_code)
        return

    print("Verbonden met", secrets.MQTT_BROKER)
    for topic in TOPICS:
        client.subscribe(topic)
        print("Luistert naar", topic)


def on_message(client, userdata, message):
    tekst = message.payload.decode("utf-8", errors="replace")
    print(message.topic, tekst)


def maak_client():
    if hasattr(mqtt, "CallbackAPIVersion"):
        return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    return mqtt.Client(client_id=CLIENT_ID)


def main():
    client = maak_client()
    client.username_pw_set(secrets.MQTT_GEBRUIKER, secrets.MQTT_WACHTWOORD)
    client.on_connect = on_connect
    client.on_message = on_message

    print("Verbinden met", secrets.MQTT_BROKER, "poort", secrets.MQTT_POORT)
    client.connect(secrets.MQTT_BROKER, secrets.MQTT_POORT, keepalive=60)
    client.loop_forever()


main()
