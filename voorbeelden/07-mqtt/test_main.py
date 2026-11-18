import os
import sqlite3
import tempfile

os.environ["WEERSTATION_DB"] = os.path.join(tempfile.gettempdir(), "weerstation-test.db")
os.environ["WEERSTATION_SLEUTEL"] = "test-sleutel"
if os.path.exists(os.environ["WEERSTATION_DB"]):
    os.remove(os.environ["WEERSTATION_DB"])

import bcrypt
from fastapi.testclient import TestClient

import database
from main import app


def nieuw():
    return TestClient(app)


def maak(email, wachtwoord, beheerder=False):
    wachtwoord_hash = bcrypt.hashpw(wachtwoord.encode(), bcrypt.gensalt()).decode()
    if beheerder:
        return database.voeg_beheerder_toe("Beheer", email, wachtwoord_hash)
    return database.voeg_gebruiker_toe("Leerling", email, wachtwoord_hash)


def meld_aan(client, email, wachtwoord):
    return client.post(
        "/login",
        data={"email": email, "wachtwoord": wachtwoord},
        follow_redirects=False,
    )


def test_zonder_login_gaat_naar_login():
    response = nieuw().get("/", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_fout_wachtwoord_en_onbekende_gebruiker():
    maak("leerling@school.be", "geheim123")
    client = nieuw()
    onbekend = client.post(
        "/login",
        data={"email": "niemand@school.be", "wachtwoord": "geheim123"},
    )
    fout = client.post(
        "/login",
        data={"email": "leerling@school.be", "wachtwoord": "verkeerd1"},
    )
    assert onbekend.status_code == 401
    assert fout.status_code == 401
    assert "Onbekend e-mailadres of wachtwoord." in onbekend.text
    assert "Onbekend e-mailadres of wachtwoord." in fout.text


def test_gebruiker_ziet_alleen_eigen_station():
    maak("eigenaar@school.be", "geheim123")
    database.koppel_station(1, "eigenaar@school.be")
    client = nieuw()
    meld_aan(client, "eigenaar@school.be", "geheim123")
    response = client.get("/")
    assert response.status_code == 200
    assert "Klaslokaal" in response.text
    assert "17,8" in response.text
    assert "7,4" not in response.text
    assert "Speelplaats" not in response.text


def test_ander_station_blijft_verborgen():
    maak("eigenaar2@school.be", "geheim123")
    database.koppel_station(1, "eigenaar2@school.be")
    client = nieuw()
    meld_aan(client, "eigenaar2@school.be", "geheim123")
    response = client.get("/?station_id=2")
    assert "Dit station is niet van jou." in response.text
    assert "7,4" not in response.text


def test_gebruiker_krijgt_403_op_beheer():
    maak("gewone@school.be", "geheim123")
    client = nieuw()
    meld_aan(client, "gewone@school.be", "geheim123")
    assert client.get("/beheer").status_code == 403
    geweigerd = client.post("/beheer", data={"station_id": 1, "email": "gewone@school.be"})
    assert geweigerd.status_code == 403


def test_beheerder_koppelt_een_station():
    maak("baas@school.be", "geheim123", beheerder=True)
    maak("nieuw@school.be", "geheim123")
    client = nieuw()
    meld_aan(client, "baas@school.be", "geheim123")
    response = client.post("/beheer", data={"station_id": 2, "email": "nieuw@school.be"})
    assert response.status_code == 200
    assert "nieuw@school.be" in response.text
    eigenaar = nieuw()
    meld_aan(eigenaar, "nieuw@school.be", "geheim123")
    pagina = eigenaar.get("/")
    assert "Speelplaats" in pagina.text
    assert "7,4" in pagina.text


def test_metingen_is_een_lijst():
    response = nieuw().get("/metingen")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_nieuwe_meting_komt_terug():
    response = nieuw().post("/metingen", json={"temp": 21.5, "luchtdruk": 1013})
    assert response.status_code == 200
    ontvangen = response.json()["ontvangen"]
    assert ontvangen["temp"] == 21.5
    assert ontvangen["luchtdruk"] == 1013


def test_onvolledige_meting_wordt_geweigerd():
    response = nieuw().post("/metingen", json={"temp": 21.5})
    assert response.status_code == 422


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


def test_meting_blijft_bewaard():
    nieuw().post("/metingen", json={"temp": 12.3, "luchtdruk": 1002.5})
    verbinding = sqlite3.connect(os.environ["WEERSTATION_DB"])
    rij = verbinding.execute("SELECT temp FROM meting WHERE temp = 12.3").fetchone()
    verbinding.close()
    assert rij is not None
