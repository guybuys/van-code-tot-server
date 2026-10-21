# Weerstation op een Arduino Uno R4 WiFi

Testsketch voor 4TW. Een BMP280 meet temperatuur (°C) en luchtdruk (hPa). Het bord stuurt die waarden elke 10 seconden als JSON naar EMQX.

Voorbeeldbericht:

```json
{"temp":21.5,"luchtdruk":1013.2}
```

## Invullen

Kopieer `secrets.h.example` naar `secrets.h` als dat bestand er nog niet is. Vul daarin het wifi-netwerk, het IP-adres van EMQX, de MQTT-gebruikersnaam en het wachtwoord in. `secrets.h` blijft op de computer en gaat niet naar GitHub.

Elk bord krijgt een eigen `MQTT_CLIENT_ID` en een eigen `MQTT_TOPIC`, bijvoorbeeld `weerstation/2/meting`.

De sketch gebruikt poort 1883, MQTT met gebruikersnaam en wachtwoord, zonder TLS.

## Bibliotheken

In de Arduino IDE, bord **Arduino Uno R4 WiFi**:

- ArduinoMqttClient
- Adafruit BMP280 Library
- Adafruit Unified Sensor

## Bedrading BMP280

| BMP280 | Uno R4 WiFi |
|---|---|
| VCC | 3.3V |
| GND | GND |
| SDA | SDA |
| SCL | SCL |

De seriële monitor staat op 115200 baud. Daar verschijnt het bericht ook als de broker nog niet bereikbaar is.

## Een meting toevoegen

In `leesSensor()` lees je de extra sensor. In `maakBericht()` komt er een veld bij in de JSON, bijvoorbeeld `luchtvochtigheid`. De buffer is 160 tekens. Wordt het bericht langer, vergroot dan die buffer.
