// Arduino Uno R4 WiFi
// Stuurt temperatuur en luchtdruk van een BMP280 naar een EMQX-broker.
//
// Bibliotheken (Bibliotheekbeheer):
// - ArduinoMqttClient
// - Adafruit BMP280 Library
// - Adafruit Unified Sensor
//
// BMP280 op I2C: VCC -> 3.3V, GND -> GND, SDA -> SDA, SCL -> SCL.

#include <WiFiS3.h>
#include <ArduinoMqttClient.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>

#include "secrets.h"

const unsigned long MEET_INTERVAL_MS = 10000;

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);
Adafruit_BMP280 bmp;

bool sensorOk = false;
unsigned long laatsteMeting = 0;

float temperatuur;
float luchtdruk;

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000) {
  }

  sensorOk = startSensor();
  verbindWifi();
  verbindMqtt();
}

void loop() {
  if (!sensorOk) {
    sensorOk = startSensor();
    delay(2000);
    return;
  }

  if (WiFi.status() != WL_CONNECTED) {
    verbindWifi();
  }
  if (!mqttClient.connected()) {
    verbindMqtt();
  }
  mqttClient.poll();

  unsigned long nu = millis();
  if (nu - laatsteMeting >= MEET_INTERVAL_MS) {
    laatsteMeting = nu;
    publiceerMeting();
  }
}

bool startSensor() {
  if (bmp.begin(0x76) || bmp.begin(0x77)) {
    Serial.println("BMP280 gevonden");
    return true;
  }

  Serial.println("BMP280 niet gevonden. Controleer 3.3V, SDA, SCL en het adres 0x76 of 0x77.");
  return false;
}

void verbindWifi() {
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("WiFi-module van de Uno R4 niet gevonden. Update de firmware via het Arduino-bordmenu.");
    return;
  }

  Serial.print("Verbinden met WiFi ");
  Serial.println(WIFI_SSID);

  while (WiFi.begin(WIFI_SSID, WIFI_WACHTWOORD) != WL_CONNECTED) {
    Serial.println("WiFi lukt nog niet, nieuwe poging...");
    delay(2000);
  }

  Serial.print("WiFi verbonden, IP-adres van dit bord: ");
  Serial.println(WiFi.localIP());
}

void verbindMqtt() {
  mqttClient.setId(MQTT_CLIENT_ID);
  mqttClient.setUsernamePassword(MQTT_GEBRUIKER, MQTT_WACHTWOORD);

  Serial.print("Verbinden met EMQX op ");
  Serial.print(MQTT_BROKER);
  Serial.print(":");
  Serial.println(MQTT_POORT);

  if (!mqttClient.connect(MQTT_BROKER, MQTT_POORT)) {
    Serial.print("MQTT-verbinding mislukt, foutcode ");
    Serial.println(mqttClient.connectError());
    delay(2000);
    return;
  }

  Serial.println("MQTT verbonden");
}

void leesSensor() {
  temperatuur = bmp.readTemperature();
  luchtdruk = bmp.readPressure() / 100.0;
}

// Een extra meting voeg je hier toe: een variabele in leesSensor()
// en een extra stuk in de JSON, bijvoorbeeld ,"luchtvochtigheid":%.1f
int maakBericht(char *bericht, size_t lengte) {
  return snprintf(bericht, lengte,
                  "{\"temp\":%.1f,\"luchtdruk\":%.1f}",
                  temperatuur, luchtdruk);
}

void publiceerMeting() {
  leesSensor();

  if (isnan(temperatuur) || isnan(luchtdruk)) {
    Serial.println("Sensor gaf geen geldige meting.");
    return;
  }

  char bericht[160];
  int lengte = maakBericht(bericht, sizeof(bericht));
  if (lengte <= 0 || lengte >= (int)sizeof(bericht)) {
    Serial.println("Bericht past niet in de buffer. Maak de buffer groter.");
    return;
  }

  Serial.print(MQTT_TOPIC);
  Serial.print(" ");
  Serial.println(bericht);

  if (!mqttClient.connected()) {
    return;
  }

  mqttClient.beginMessage(MQTT_TOPIC);
  mqttClient.print(bericht);
  mqttClient.endMessage();
}
