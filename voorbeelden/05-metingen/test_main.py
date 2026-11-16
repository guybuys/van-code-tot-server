import os
import sqlite3
import tempfile

os.environ["WEERSTATION_DB"] = os.path.join(tempfile.gettempdir(), "weerstation-test.db")
if os.path.exists(os.environ["WEERSTATION_DB"]):
    os.remove(os.environ["WEERSTATION_DB"])

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_home():
    client.post("/metingen", json={"temp": 21.7, "luchtdruk": 1004.3})
    response = client.get("/")
    assert response.status_code == 200
    assert "21,7" in response.text
    assert "1004,3" in response.text


def test_metingen_is_een_lijst():
    response = client.get("/metingen")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_nieuwe_meting_komt_terug():
    response = client.post(
        "/metingen",
        json={"temp": 21.5, "luchtdruk": 1013},
    )
    assert response.status_code == 200
    ontvangen = response.json()["ontvangen"]
    assert ontvangen["temp"] == 21.5
    assert ontvangen["luchtdruk"] == 1013


def test_onvolledige_meting_wordt_geweigerd():
    response = client.post("/metingen", json={"temp": 21.5})
    assert response.status_code == 422


def test_meting_blijft_bewaard():
    client.post("/metingen", json={"temp": 12.3, "luchtdruk": 1002.5})
    verbinding = sqlite3.connect(os.environ["WEERSTATION_DB"])
    rij = verbinding.execute(
        "SELECT temp FROM meting WHERE temp = 12.3"
    ).fetchone()
    verbinding.close()
    assert rij is not None
