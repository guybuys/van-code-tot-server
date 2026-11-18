import paho.mqtt.client as mqtt

import database
import secrets

database.start()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        print("MQTT-verbinding mislukt, code", reason_code)
        return
    print("MQTT verbonden")
    client.subscribe("weerstation/+/info")
    client.subscribe("weerstation/+/meting")


def on_message(client, userdata, bericht):
    topic = bericht.topic
    tekst = bericht.payload.decode()
    if topic.endswith("/info"):
        gelukt = database.verwerk_info(topic, tekst)
    elif topic.endswith("/meting"):
        gelukt = database.verwerk_meting(topic, tekst)
    else:
        gelukt = False
    if gelukt:
        print(topic, tekst)
    else:
        print("Overgeslagen", topic, tekst)


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=secrets.MQTT_CLIENT_ID)
    client.username_pw_set(secrets.MQTT_GEBRUIKER, secrets.MQTT_WACHTWOORD)
    client.on_connect = on_connect
    client.on_message = on_message
    print("Verbinden met EMQX op %s:%s" % (secrets.MQTT_BROKER, secrets.MQTT_POORT))
    client.connect(secrets.MQTT_BROKER, secrets.MQTT_POORT)
    client.loop_forever()


if __name__ == "__main__":
    main()
