# MQTT

De website praat niet met de broker. Een tweede programma, `ingester.py`, doet dat. FastAPI leest de database. De ingester schrijft erin. Twee programma's, één bestand `weerstation.db`.

## Twee berichten

Elk station heeft een nummer `N` in het topic.

`weerstation/N/meting` is niet retained. Het bericht is `{"temp":21.5,"luchtdruk":1013.2}`. De ingester zet de tijd er zelf bij, in UTC. Het bord stuurt geen klok mee. Een oude meting mag niet op de broker blijven hangen, daarom is dit bericht niet retained.

`weerstation/N/info` is retained. Het bericht is `{"naam","leden","breedte","lengte"}`. De broker onthoudt het laatste info-bericht. Zodra de ingester zich abonneert, krijgt ze dat bericht, ook als het bord op dat moment niets stuurt. We bewaren naam, breedte en lengte. `leden` blijft in het bericht en komt nog niet in de tabel.

Een meting voor een nummer zonder station slaan we over. Eerst info, daarna metingen. Het retained info-bericht komt meestal meteen na het abonneren binnen.

## Het nummer

Het nummer in het topic is niet automatisch het id dat SQLite kiest. Een kolom `nummer` koppelt `weerstation/7` aan één station.

In `STATIONS` krijgt het klaslokaal `"nummer": 1` en de speelplaats `"nummer": 2`, naast breedte en lengte.

Vervang de INSERT van een station in `vul_voorbeeld` door:

```python
        cursor = verbinding.execute(
            "INSERT INTO station (naam, breedte, lengte, nummer) VALUES (?, ?, ?, ?)",
            (naam, station["breedte"], station["lengte"], station["nummer"]),
        )
```

Zet deze functie boven `start`, en roep ze aan vóór `vul_voorbeeld`.

```python
def zorg_voor_nummer(verbinding):
    kolommen = [rij["name"] for rij in verbinding.execute("PRAGMA table_info(station)")]
    if "nummer" not in kolommen:
        verbinding.execute("ALTER TABLE station ADD COLUMN nummer INTEGER")
    verbinding.execute("UPDATE station SET nummer = id WHERE nummer IS NULL")


def start():
    verbinding = verbind()
    maak_tabellen(verbinding)
    zorg_voor_nummer(verbinding)
    vul_voorbeeld(verbinding)
    verbinding.commit()
    verbinding.close()
```

Een database die je al had, krijgt de kolom erbij. Lege nummers worden het id. Klaslokaal wordt dan 1. Een bord op `weerstation/1` werkt dat station bij. Een nieuw station krijgt een vrij nummer, bijvoorbeeld 3.

Zet bovenaan `database.py` ook `import json`, bij de andere imports.

## Verwerken

Zet deze functies boven `koppel_station`. `verwerk_info` maakt het station of werkt de naam en de plaats bij. De eigenaar, `gebruiker_id`, blijft staan. `verwerk_meting` schrijft een rij via `voeg_meting_toe`. Die functie zet de UTC-tijd. Bestaat het nummer nog niet, dan geeft ze `False` terug en komt er geen rij.

```python
def nummer_uit_topic(topic, soort):
    delen = topic.split("/")
    if len(delen) != 3 or delen[0] != "weerstation" or delen[2] != soort:
        return None
    if not delen[1].isdigit():
        return None
    return int(delen[1])


def station_van_nummer(nummer):
    verbinding = verbind()
    rij = verbinding.execute(
        "SELECT id, naam, nummer FROM station WHERE nummer = ?",
        (nummer,),
    ).fetchone()
    verbinding.close()
    return als_dict(rij)


def verwerk_info(topic, bericht):
    nummer = nummer_uit_topic(topic, "info")
    if nummer is None:
        return False
    try:
        data = json.loads(bericht)
        naam = data["naam"]
        breedte = float(data["breedte"])
        lengte = float(data["lengte"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False
    verbinding = verbind()
    bestaand = verbinding.execute(
        "SELECT id FROM station WHERE nummer = ?",
        (nummer,),
    ).fetchone()
    if bestaand is None:
        verbinding.execute(
            "INSERT INTO station (naam, breedte, lengte, nummer) VALUES (?, ?, ?, ?)",
            (naam, breedte, lengte, nummer),
        )
    else:
        verbinding.execute(
            "UPDATE station SET naam = ?, breedte = ?, lengte = ? WHERE nummer = ?",
            (naam, breedte, lengte, nummer),
        )
    verbinding.commit()
    verbinding.close()
    return True


def verwerk_meting(topic, bericht):
    nummer = nummer_uit_topic(topic, "meting")
    if nummer is None:
        return False
    station = station_van_nummer(nummer)
    if station is None:
        return False
    try:
        data = json.loads(bericht)
        temp = float(data["temp"])
        luchtdruk = float(data["luchtdruk"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False
    voeg_meting_toe(station["id"], temp, luchtdruk)
    return True
```

## Het tweede programma

```powershell
python -m pip install paho-mqtt
```

`paho-mqtt` is de bibliotheek die met de broker praat. Ze hoort niet in `main.py`.

Maak `ingester.py`.

```python
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
```

`on_connect` abonneert pas als de verbinding gelukt is. `+` is één stuk van het topic: elk nummer, zowel `info` als `meting`. `loop_forever` blijft luisteren. Dit programma serveert geen pagina.

Maak `secrets.py.example`.

```python
# Kopieer dit bestand naar secrets.py en vul de waarden in.
# secrets.py staat in .gitignore en gaat niet naar GitHub.
# De leerkracht geeft het adres, de gebruikersnaam en het wachtwoord.

MQTT_BROKER = "192.168.1.10"
MQTT_POORT = 1883
MQTT_GEBRUIKER = "GEBRUIKER"
MQTT_WACHTWOORD = "WACHTWOORD"
MQTT_CLIENT_ID = "ingester-laptop"
```

Kopieer dat bestand naar `secrets.py` en vul de waarden in die je van de leerkracht krijgt. Zet deze regel in `.gitignore`:

```text
secrets.py
```

`python ingester.py` verbindt. Laat dat venster open. De website draait in een andere terminal. Vernieuw de pagina om een nieuwe rij te zien. De pagina luistert zelf niet naar MQTT.

Zonder de brokergegevens lopen de tests hieronder toch. Die roepen `verwerk_info` aan, zonder netwerk.

## De test

Zet deze twee tests onderaan `test_main.py`, boven de laatste test mag ook. Ze gebruiken de database die de andere tests al kozen.

```python
def test_info_maakt_een_station_en_een_meting():
    assert database.verwerk_info(
        "weerstation/7/info",
        '{"naam":"Hal","leden":"A, B","breedte":51.03,"lengte":4.48}',
    )
    assert database.station_van_nummer(7)["naam"] == "Hal"
    assert database.verwerk_meting(
        "weerstation/7/meting",
        '{"temp":16.2,"luchtdruk":1011.4}',
    )
    assert database.verwerk_info(
        "weerstation/7/info",
        '{"naam":"Hal boven","breedte":51.03,"lengte":4.48}',
    )
    assert database.station_van_nummer(7)["naam"] == "Hal boven"
    rijen = database.metingen_van_station(database.station_van_nummer(7)["id"])
    assert len(rijen) == 1
    assert rijen[0]["temp"] == 16.2


def test_meting_zonder_station_blijft_weg():
    assert database.verwerk_meting("weerstation/9/meting", '{"temp":1,"luchtdruk":2}') is False
    assert database.verwerk_info("weerstation/9/anders", "{}") is False
    assert database.station_van_nummer(9) is None
```

```powershell
pytest
```

Twaalf tests passed. De tweede info-regel verandert de naam en laat de meting staan.

## Bewaren op GitHub

```powershell
git add database.py ingester.py secrets.py.example test_main.py .gitignore
git commit -m "Schrijf MQTT-berichten met een apart programma in de database"
git push
```

`git status` toont `secrets.py` niet.

## Klaar als

- `pytest` eindigt met 12 geslaagde tests.
- Een info-bericht voor een nieuw nummer maakt een station. Een meting zonder station maakt geen rij.
- `ingester.py` is een apart bestand. Er is geen MQTT-code in een route van `main.py`.
- `secrets.py` staat niet op GitHub.

??? note "Als het niet lukt"

    **`No module named 'secrets'`.** `secrets.py` ontbreekt. Kopieer `secrets.py.example` en vul de waarden in. De module `secrets` van Python is een andere. Jouw bestand in de projectmap wint zolang je de ingester vanuit die map start.

    **`no such column: nummer`.** `zorg_voor_nummer` draait niet vanuit `start`, of de server is niet herstart na het bewaren van `database.py`.

    **`name 'json' is not defined`.** Bovenaan `database.py` ontbreekt `import json`.

    **De terminal zegt `Overgeslagen` bij een meting.** Voor dat nummer is nog geen info-bericht verwerkt. Het retained bericht komt normaal meteen. Een nummer dat de broker niet kent, blijft overgeslagen.

    **De pagina verandert niet vanzelf.** Ze leest de database bij een vernieuwing. MQTT zit niet in de browser.

    **`git status` toont `secrets.py`.** De regel in `.gitignore` ontbreekt. De regel is exact `secrets.py`.
