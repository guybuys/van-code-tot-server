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
