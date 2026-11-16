from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_home():
    client.post("/metingen", json={"temp": 19.4, "luchtdruk": 1008.6})
    response = client.get("/")
    assert response.status_code == 200
    assert "19,4" in response.text
    assert "1008,6" in response.text


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
