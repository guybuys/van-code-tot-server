# ESP32 met MicroPython
# Stuurt temperatuur en luchtdruk naar een EMQX-broker.
# Zelfde bericht als de Uno R4-sketch.
#
# SIMULEER_SENSOR True: verzonnen metingen, geen BMP280 nodig.
# SIMULEER_SENSOR False: echte BMP280. Zet dan ook bmp280.py op het bord.
#
# Op een gewone ESP32-devkit staan de I2C-pinnen als GPIO-nummer op de print,
# niet als SDA of SCL:
# SDA = GPIO 21, SCL = GPIO 22.
# Op een ESP32-S3 zijn dat vaak GPIO 8 (SDA) en GPIO 9 (SCL). Pas de twee
# regels hieronder aan als je bord andere nummers heeft.
# BMP280: VCC -> 3V3, GND -> GND, SDA -> GPIO 21, SCL -> GPIO 22.
# SDO naar GND is adres 0x76. SDO naar 3V3 is adres 0x77.

SIMULEER_SENSOR = True
SDA_PIN = 21
SCL_PIN = 22
MEET_INTERVAL_S = 10

import random
import time

import network
from umqtt.simple import MQTTClient

import secrets

if not SIMULEER_SENSOR:
    import bmp280

temperatuur = 21.0
luchtdruk = 1013.0
sensor = None
client = None
wlan = network.WLAN(network.STA_IF)


def start_sensor():
    global temperatuur, luchtdruk, sensor
    if SIMULEER_SENSOR:
        temperatuur = 21.0
        luchtdruk = 1013.0
        print("Gesimuleerde sensor. Zet SIMULEER_SENSOR op False voor de BMP280.")
        return True

    sensor = bmp280.start(SDA_PIN, SCL_PIN)
    if sensor is None:
        print(
            "BMP280 niet gevonden. Controleer 3V3, SDA op GPIO %s, SCL op GPIO %s, adres 0x76 of 0x77."
            % (SDA_PIN, SCL_PIN)
        )
        return False

    print("BMP280 gevonden op GPIO %s (SDA) en GPIO %s (SCL)." % (SDA_PIN, SCL_PIN))
    return True


def lees_sensor():
    global temperatuur, luchtdruk
    if SIMULEER_SENSOR:
        temperatuur += random.randint(-2, 2) / 10.0
        luchtdruk += random.randint(-4, 4) / 10.0
        temperatuur = min(26.0, max(18.0, temperatuur))
        luchtdruk = min(1025.0, max(1000.0, luchtdruk))
        return

    temperatuur, luchtdruk = sensor.lees()


def verbind_wifi():
    wlan.active(True)
    if wlan.isconnected():
        print("WiFi verbonden, IP-adres van dit bord:", wlan.ifconfig()[0])
        return True

    print("Verbinden met WiFi", secrets.WIFI_SSID)
    wlan.connect(secrets.WIFI_SSID, secrets.WIFI_WACHTWOORD)
    for _ in range(15):
        if wlan.isconnected():
            print("WiFi verbonden, IP-adres van dit bord:", wlan.ifconfig()[0])
            return True
        print("WiFi lukt nog niet, nieuwe poging...")
        time.sleep(2)

    print("WiFi niet verbonden.")
    return False


def verbind_mqtt():
    global client
    print("Verbinden met EMQX op %s:%s" % (secrets.MQTT_BROKER, secrets.MQTT_POORT))
    try:
        nieuw = MQTTClient(
            secrets.MQTT_CLIENT_ID,
            secrets.MQTT_BROKER,
            port=secrets.MQTT_POORT,
            user=secrets.MQTT_GEBRUIKER,
            password=secrets.MQTT_WACHTWOORD,
            keepalive=60,
        )
        nieuw.connect()
    except OSError as fout:
        print("MQTT-verbinding mislukt:", fout)
        client = None
        time.sleep(2)
        return False

    client = nieuw
    print("MQTT verbonden")
    return True


def publiceer_meting():
    global client
    lees_sensor()
    bericht = '{"temp":%.1f,"luchtdruk":%.1f}' % (temperatuur, luchtdruk)
    print(secrets.MQTT_TOPIC, bericht)
    if client is None:
        return
    try:
        client.publish(secrets.MQTT_TOPIC, bericht)
    except OSError as fout:
        print("Publiceren mislukt:", fout)
        client = None


def main():
    sensor_ok = start_sensor()
    if sensor_ok:
        if verbind_wifi():
            verbind_mqtt()

    laatste = time.ticks_ms()
    while True:
        if not sensor_ok:
            sensor_ok = start_sensor()
            time.sleep(2)
            continue

        if not wlan.isconnected():
            verbind_wifi()
        if client is None and wlan.isconnected():
            verbind_mqtt()

        nu = time.ticks_ms()
        if time.ticks_diff(nu, laatste) >= MEET_INTERVAL_S * 1000:
            laatste = nu
            publiceer_meting()
        time.sleep(0.2)


main()
