# Metingen tonen in Thonny

Dit script luistert naar EMQX en print elk bericht als tekst. Het publiceert niets.

Open de map `toon_metingen` in Thonny en voer `toon_metingen.py` uit. Stoppen doe je met de stopknop.

## Invullen

Kopieer `secrets.py.example` naar `secrets.py` als dat bestand er nog niet is. Vul hetzelfde IP-adres, dezelfde gebruikersnaam en hetzelfde wachtwoord in als bij de Arduino.

De topics staan bovenaan `toon_metingen.py`:

```python
TOPICS = [
    "weerstation/1/meting",
    "weerstation/2/meting",
]
```

Zet er een regel bij per extra station. Eén topic `weerstation/+/meting` ontvangt alle stations tegelijk.

## Pakket

In Thonny: **Extra → Beheer pakketten**, zoek `paho-mqtt` en installeer het. Of in de shell van Thonny:

```text
pip install paho-mqtt
```
