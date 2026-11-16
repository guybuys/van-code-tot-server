// Arduino Uno R4 WiFi
// Stuurt temperatuur en luchtdruk naar een EMQX-broker.
//
// Wifi en MQTT staan in MqttVerbinding.h. Die tab laat je dicht.
// In deze sketch lees je de sensor en maak je het bericht.
//
// De matrix toont de verbinding vanzelf.
// mqtt.fout() zet een uitroepteken, mqtt.wisFout() haalt het weg.
//
// SIMULEER_SENSOR 1: verzonnen metingen, geen BMP280 nodig.
// SIMULEER_SENSOR 0: echte BMP280.
// Bibliotheken bij een echte sensor (Bibliotheekbeheer):
// - Adafruit BMP280 Library
// - Adafruit Unified Sensor
//
// I2C is hetzelfde als op de Uno R3:
// SDA = A4, SCL = A5.
// De twee pinnen naast AREF heten op de print SCL en SDA en zijn dezelfde draden.
// De Qwiic-connector is een andere I2C-bus. Die gebruikt deze sketch niet.
// BMP280: VCC -> 3.3V, GND -> GND, SDA -> A4, SCL -> A5.

#define SIMULEER_SENSOR 0

#include "MqttVerbinding.h"

#if !SIMULEER_SENSOR
#include <Wire.h>
#include <Adafruit_BMP280.h>
#endif

const unsigned long MEET_INTERVAL_MS = 10000;

MqttVerbinding mqtt;
#if !SIMULEER_SENSOR
Adafruit_BMP280 bmp;
#endif

bool sensorOk = false;
unsigned long laatsteMeting = 0;

float temperatuur;
float luchtdruk;

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000) {
  }

  mqtt.begin();
  sensorOk = startSensor();
}

void loop() {
  if (!sensorOk) {
    sensorOk = startSensor();
    delay(2000);
    return;
  }

  mqtt.houdOpen();

  unsigned long nu = millis();
  if (nu - laatsteMeting >= MEET_INTERVAL_MS) {
    laatsteMeting = nu;
    publiceerMeting();
  }
}

bool startSensor() {
#if SIMULEER_SENSOR
  temperatuur = 21.0;
  luchtdruk = 1013.0;
  randomSeed(analogRead(A0));
  mqtt.wisFout();
  Serial.println("Gesimuleerde sensor. Zet SIMULEER_SENSOR op 0 voor de BMP280.");
  return true;
#else
  if (bmp.begin(0x76) || bmp.begin(0x77)) {
    mqtt.wisFout();
    Serial.println("BMP280 gevonden op A4 (SDA) en A5 (SCL)");
    return true;
  }

  mqtt.fout();
  Serial.println("BMP280 niet gevonden. Controleer 3.3V, SDA op A4, SCL op A5, adres 0x76 of 0x77.");
  return false;
#endif
}

void leesSensor() {
#if SIMULEER_SENSOR
  temperatuur += random(-2, 3) / 10.0;
  luchtdruk += random(-4, 5) / 10.0;
  temperatuur = constrain(temperatuur, 18.0, 26.0);
  luchtdruk = constrain(luchtdruk, 1000.0, 1025.0);
#else
  temperatuur = bmp.readTemperature();
  luchtdruk = bmp.readPressure() / 100.0;
#endif
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
  mqtt.verstuur(bericht);
}
