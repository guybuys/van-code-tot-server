# Database

De lijst in `main.py` verdwijnt als je het programma stopt. Een database bewaart de rijen in een bestand. Afsluiten wist ze niet.

Het weerstation zelf stuurt nog geen metingen. Dat programma komt later. Tot dan zet je voorbeeldmetingen in de database. Zonder die rijen heeft de volgende pagina niets om te tonen.

## Drie soorten

Een meting hoort bij een station. Een station hoort later bij een gebruiker. De vraag die we stellen is: de metingen van dit station, op deze dag.

**SQL** legt de gegevens in tabellen. Een rij is één station of één meting. SQLite is SQL in één bestand, `weerstation.db`. Er hoeft geen apart databaseprogramma te draaien. Een server kan dezelfde tabellen later in PostgreSQL zetten. De vragen lijken op elkaar. In deze cursus blijft het bestand `weerstation.db`, ook op de server.

**InfluxDB** is gemaakt voor een lange reeks metingen in de tijd. Die database kan zelf gemiddelden per uur uitrekenen. Voor twee stations en één schooldag volstaat een SQL-vraag.

**MongoDB** bewaart documenten. Elk station kan daar andere velden in hebben. Onze stations sturen allebei temperatuur en luchtdruk. Vaste kolommen maken de tabel op de pagina duidelijk. Een extra sensor wordt later een extra kolom.

Deze cursus gebruikt SQLite.

## Drie tabellen

`gebruiker` is iemand die later inlogt. De tabel maken we al. Er komen nog geen rijen in. Een wachtwoord bewaren we dan als hash, niet als leesbare tekst. Dat is het volgende grote hoofdstuk na de grafiek.

`station` is een weerstation op een vaste plaats. Er zit geen GPS-module in. De coördinaten typ je zelf. Het klaslokaal en de speelplaats zijn twee punten bij de school.

`meting` is één moment: tijd, temperatuur en luchtdruk. De tijd staat in UTC. `2026-11-16T06:00:00Z` is 07:00 uur in de winter in België.

Een gebruiker heeft nul of meer stations. Een station heeft nul of meer metingen.

```mermaid
erDiagram
  GEBRUIKER ||--o{ STATION : heeft
  STATION ||--o{ METING : levert
```

## Voorbeeldmetingen

De dag is 16 november 2026. Om de twee uur, van 06:00 tot 18:00 UTC, komt er een meting. Zeven per station, veertien in totaal.

Het klaslokaal blijft rond 18 °C. De speelplaats gaat van 7,4 °C 's morgens naar 13,8 °C in de namiddag. De luchtdruk daalt bij allebei van ongeveer 1016 hPa naar 1013 hPa. Buiten en binnen hebben hetzelfde weer. De temperatuur verschilt, want het lokaal is binnen.

## Het programma

Maak `database.py` naast `main.py`. `sqlite3` zit bij Python. Je installeert geen extra pakket.

```python
import os
import sqlite3

DATABASE = os.environ.get("WEERSTATION_DB", "weerstation.db")

STATIONS = {
    "Klaslokaal": {
        "breedte": 51.0298,
        "lengte": 4.4765,
        "metingen": [
            ("2026-11-16T06:00:00Z", 17.8, 1016.2),
            ("2026-11-16T08:00:00Z", 18.1, 1016.0),
            ("2026-11-16T10:00:00Z", 18.6, 1015.4),
            ("2026-11-16T12:00:00Z", 19.2, 1014.8),
            ("2026-11-16T14:00:00Z", 19.4, 1014.2),
            ("2026-11-16T16:00:00Z", 18.9, 1013.8),
            ("2026-11-16T18:00:00Z", 18.4, 1013.5),
        ],
    },
    "Speelplaats": {
        "breedte": 51.0301,
        "lengte": 4.4769,
        "metingen": [
            ("2026-11-16T06:00:00Z", 7.4, 1016.4),
            ("2026-11-16T08:00:00Z", 8.6, 1016.1),
            ("2026-11-16T10:00:00Z", 11.2, 1015.2),
            ("2026-11-16T12:00:00Z", 13.1, 1014.6),
            ("2026-11-16T14:00:00Z", 13.8, 1014.1),
            ("2026-11-16T16:00:00Z", 12.4, 1013.9),
            ("2026-11-16T18:00:00Z", 10.1, 1013.6),
        ],
    },
}


def verbind():
    verbinding = sqlite3.connect(DATABASE)
    verbinding.row_factory = sqlite3.Row
    verbinding.execute("PRAGMA foreign_keys = ON")
    return verbinding


def maak_tabellen(verbinding):
    verbinding.execute(
        """
        CREATE TABLE IF NOT EXISTS gebruiker (
            id INTEGER PRIMARY KEY,
            naam TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            wachtwoord_hash TEXT NOT NULL,
            rol TEXT NOT NULL
        )
        """
    )
    verbinding.execute(
        """
        CREATE TABLE IF NOT EXISTS station (
            id INTEGER PRIMARY KEY,
            naam TEXT NOT NULL,
            breedte REAL,
            lengte REAL,
            gebruiker_id INTEGER,
            FOREIGN KEY (gebruiker_id) REFERENCES gebruiker (id)
        )
        """
    )
    verbinding.execute(
        """
        CREATE TABLE IF NOT EXISTS meting (
            id INTEGER PRIMARY KEY,
            station_id INTEGER NOT NULL,
            tijd TEXT NOT NULL,
            temp REAL NOT NULL,
            luchtdruk REAL NOT NULL,
            FOREIGN KEY (station_id) REFERENCES station (id)
        )
        """
    )


def vul_voorbeeld(verbinding):
    aantal = verbinding.execute("SELECT COUNT(*) AS aantal FROM station").fetchone()["aantal"]
    if aantal:
        return

    for naam, station in STATIONS.items():
        cursor = verbinding.execute(
            "INSERT INTO station (naam, breedte, lengte) VALUES (?, ?, ?)",
            (naam, station["breedte"], station["lengte"]),
        )
        verbinding.executemany(
            "INSERT INTO meting (station_id, tijd, temp, luchtdruk) VALUES (?, ?, ?, ?)",
            [
                (cursor.lastrowid, tijd, temp, luchtdruk)
                for tijd, temp, luchtdruk in station["metingen"]
            ],
        )


def start():
    verbinding = verbind()
    maak_tabellen(verbinding)
    vul_voorbeeld(verbinding)
    verbinding.commit()
    verbinding.close()


def toon():
    verbinding = verbind()
    stations = verbinding.execute("SELECT COUNT(*) AS aantal FROM station").fetchone()
    metingen = verbinding.execute("SELECT COUNT(*) AS aantal FROM meting").fetchone()
    print(f"{stations['aantal']} stations")
    print(f"{metingen['aantal']} metingen")
    laatste = verbinding.execute(
        """
        SELECT station.naam, meting.tijd, meting.temp, meting.luchtdruk
        FROM meting
        JOIN station ON station.id = meting.station_id
        ORDER BY meting.tijd, station.id
        """
    ).fetchall()
    for rij in laatste[-2:]:
        print(rij["naam"], rij["tijd"], rij["temp"], rij["luchtdruk"])
    verbinding.close()


if __name__ == "__main__":
    start()
    toon()
```

`DATABASE` is normaal `weerstation.db`. Een test kan een andere naam kiezen. Dat gebruiken we in het volgende hoofdstuk, zodat de test je voorbeeldmetingen laat staan.

`?` is een plaats voor een waarde. SQLite vult die in. De waarde wordt geen stuk van de SQL-zin. Een temperatuur met een aanhalingsteken kan de vraag dan niet openbreken.

`vul_voorbeeld` stopt zodra er al een station in het bestand staat. Het programma een tweede keer starten maakt geen dubbele rijen. `commit` schrijft de rijen naar het bestand.

`JOIN` plakt de naam van het station aan de meting. Zonder die regel zie je alleen een nummer.

## Nakijken

```powershell
python database.py
```

Je ziet:

```text
2 stations
14 metingen
Klaslokaal 2026-11-16T18:00:00Z 18.4 1013.5
Speelplaats 2026-11-16T18:00:00Z 10.1 1013.6
```

De getallen hebben hier een punt. Zo staan ze in de database. Op de pagina komt de komma terug.

Draai het programma nog eens. De aantallen blijven 2 en 14. In de map staat nu `weerstation.db`.

## Niet mee naar GitHub

Het bestand verandert zodra er een meting bij komt. Elke leerling heeft zijn eigen bestand. Zet deze regel in `.gitignore`, onder de regels die er al staan:

```text
weerstation.db
```

## Bewaren op GitHub

```powershell
git add database.py .gitignore
git commit -m "Bewaar stations en voorbeeldmetingen in SQLite"
git push
```

`git status` toont `weerstation.db` niet.

## Klaar als

- `python database.py` toont 2 stations en 14 metingen.
- Een tweede keer draaien houdt die aantallen.
- `database.py` staat op GitHub. `weerstation.db` niet.

In [Metingen op de pagina](metingen.md) leest de pagina deze rijen.

??? note "Als het niet lukt"

    **`unable to open database file`.** De terminal staat niet in `C:\dev\weerstation`. Links in de titelbalk van VS Code zie je de map.

    **Je ziet 4 stations, of 28 metingen.** Het bestand is gevuld en daarna nog eens gevuld. Verwijder `weerstation.db` en draai `python database.py` opnieuw. De controle op `aantal` hoort bovenaan `vul_voorbeeld`.

    **`git status` toont `weerstation.db`.** De regel in `.gitignore` ontbreekt, of de naam wijkt af. De regel is exact `weerstation.db`.
