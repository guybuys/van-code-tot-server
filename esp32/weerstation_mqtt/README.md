# Weerstation op een ESP32 met MicroPython

Zelfde programma als de Uno R4-sketch, nu in MicroPython. Een BMP280 meet temperatuur (°C) en luchtdruk (hPa). Het bord stuurt die waarden elke 10 seconden als JSON naar EMQX.

Voorbeeldbericht:

```json
{"temp":21.5,"luchtdruk":1013.2}
```

## Invullen

Kopieer `secrets.py.example` naar `secrets.py` als dat bestand er nog niet is. Vul daarin het wifi-netwerk, het IP-adres van EMQX, de MQTT-gebruikersnaam en het wachtwoord in. `secrets.py` blijft op de computer en gaat niet naar GitHub.

Elk bord krijgt een eigen `MQTT_CLIENT_ID` en een eigen `MQTT_TOPIC`, bijvoorbeeld `weerstation/2/meting`. Gebruik niet hetzelfde topic als een Uno die al publiceert.

Het programma gebruikt poort 1883, MQTT met gebruikersnaam en wachtwoord, zonder TLS. `umqtt.simple` zit in de standaard MicroPython-firmware voor de ESP32.

## Zonder BMP280

Bovenaan `main.py` staat `SIMULEER_SENSOR = True`. Dan publiceert het bord temperatuur rond 21 °C en luchtdruk rond 1013 hPa, met een kleine stap bij elke meting. `bmp280.py` hoeft dan niet op het bord te staan.

Zet die regel op `False` zodra de BMP280 aangesloten is, en zet `bmp280.py` mee op het bord.

## Bedrading BMP280

Op een gewone ESP32-devkit staan de pinnen als GPIO-nummer op de print, niet als SDA of SCL.

| BMP280 | ESP32-devkit |
|---|---|
| VCC | 3V3 |
| GND | GND |
| SDA | GPIO 21 |
| SCL | GPIO 22 |

SDO naar GND geeft adres 0x76. SDO naar 3V3 geeft adres 0x77. Het programma probeert beide.

Op een ESP32-S3 zijn de I2C-pinnen vaak GPIO 8 (SDA) en GPIO 9 (SCL). Pas `SDA_PIN` en `SCL_PIN` bovenaan `main.py` aan als de print andere nummers toont.

## Op het bord zetten

In Thonny kies je rechtsonder de interpreter **MicroPython (ESP32)**.

Sla deze bestanden op het bord op via Bestand → Opslaan als → MicroPython-apparaat:

- `secrets.py`
- `main.py`
- `bmp280.py`, alleen als `SIMULEER_SENSOR` op `False` staat

`main.py` start opnieuw bij een reset. Stoppen terwijl je in Thonny zit: de stopknop. In de shell verschijnt het bericht ook als de broker nog niet bereikbaar is.

## Een meting toevoegen

In `lees_sensor()` lees je de extra sensor. In `publiceer_meting()` komt er een veld bij in de JSON, bijvoorbeeld `luchtvochtigheid`.
