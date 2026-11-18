# Metingen op de pagina

`database.py` bewaart veertien metingen. De pagina leest ze nog niet. Ze toont één waarde uit een lijst, en die lijst is weg na een herstart.

Dit hoofdstuk laat de pagina het klaslokaal lezen. Eerst als tabel, daarna als grafiek van de temperatuur. De speelplaats blijft in de database. Welk station van wie is, komt bij het inloggen.

## Schrijven en lezen

Zet bovenaan `database.py` deze import bij de andere:

```python
from datetime import datetime, timezone
```

Zet deze functies onder `start` en boven `toon`.

```python
def naam_van_station(station_id):
    verbinding = verbind()
    rij = verbinding.execute(
        "SELECT naam FROM station WHERE id = ?",
        (station_id,),
    ).fetchone()
    verbinding.close()
    if rij is None:
        return None
    return rij["naam"]


def metingen_van_station(station_id):
    verbinding = verbind()
    rijen = verbinding.execute(
        """
        SELECT tijd, temp, luchtdruk
        FROM meting
        WHERE station_id = ?
        ORDER BY tijd
        """,
        (station_id,),
    ).fetchall()
    verbinding.close()
    return rijen


def alle_metingen():
    verbinding = verbind()
    rijen = verbinding.execute(
        """
        SELECT station_id, tijd, temp, luchtdruk
        FROM meting
        ORDER BY tijd, station_id
        """
    ).fetchall()
    verbinding.close()
    return [dict(rij) for rij in rijen]


def voeg_meting_toe(station_id, temp, luchtdruk):
    tijd = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    verbinding = verbind()
    verbinding.execute(
        "INSERT INTO meting (station_id, tijd, temp, luchtdruk) VALUES (?, ?, ?, ?)",
        (station_id, tijd, temp, luchtdruk),
    )
    verbinding.commit()
    verbinding.close()
    return {"temp": temp, "luchtdruk": luchtdruk, "tijd": tijd}
```

`naam_van_station` geeft `None` terug als dat nummer niet bestaat. `metingen_van_station` geeft de rijen van één station, gesorteerd op tijd. `voeg_meting_toe` zet de tijd er zelf bij, in UTC, en bewaart de rij met `commit`.

Een POST heeft nog altijd alleen `temp` en `luchtdruk`. Het programma kiest het klaslokaal en de tijd.

## De pagina

Vervang `main.py` door dit bestand. De lijst `metingen = [...]` is weg.

```python
import json

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import database

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

database.start()


class Meting(BaseModel):
    temp: float
    luchtdruk: float


def komma(getal):
    return f"{getal:.1f}".replace(".", ",")


def voor_tabel(rij):
    return {
        "tijd": rij["tijd"].replace("T", " ").replace("Z", "")[:16],
        "temperatuur": komma(rij["temp"]),
        "luchtdruk": komma(rij["luchtdruk"]),
    }


def voor_grafiek(rij):
    return {"tijd": rij["tijd"][11:16], "temp": rij["temp"]}


@app.get("/")
def home(request: Request):
    station_id = 1
    rijen = database.metingen_van_station(station_id)
    grafiek = [voor_grafiek(rij) for rij in rijen]
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "station": database.naam_van_station(station_id),
            "metingen": [voor_tabel(rij) for rij in rijen],
            "grafiek_json": json.dumps(grafiek),
        },
    )


@app.get("/metingen")
def lijst_metingen():
    return database.alle_metingen()


@app.post("/metingen")
def nieuwe_meting(meting: Meting):
    return {"ontvangen": database.voeg_meting_toe(1, meting.temp, meting.luchtdruk)}
```

`database.start()` maakt de tabellen en de voorbeeldrijen als het bestand er nog niet is. `komma` zet de punt om voor de tabel. De grafiek krijgt de getallen zelf, dus de as gebruikt een punt. `json.dumps` maakt daar tekst van die de browser kan lezen.

Vervang `templates/index.html`.

```html
<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <title>Weerstation</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <main>
    {% if station %}
    <h1>{{ station }}</h1>
    <p>De metingen van dit station. De tijd staat in UTC.</p>
    <table>
      <thead>
        <tr>
          <th>Tijd</th>
          <th>Temperatuur</th>
          <th>Luchtdruk</th>
        </tr>
      </thead>
      <tbody>
        {% for meting in metingen %}
        <tr>
          <td>{{ meting.tijd }}</td>
          <td>{{ meting.temperatuur }} °C</td>
          <td>{{ meting.luchtdruk }} hPa</td>
        </tr>
        {% else %}
        <tr>
          <td colspan="3">Er zijn nog geen metingen voor dit station.</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% if metingen %}
    <h2>Temperatuur</h2>
    <canvas id="grafiek"></canvas>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.6/dist/chart.umd.min.js"></script>
    <script>
      const punten = {{ grafiek_json | safe }};
      new Chart(document.getElementById("grafiek"), {
        type: "line",
        data: {
          labels: punten.map(function (punt) { return punt.tijd; }),
          datasets: [{
            label: "Temperatuur (°C)",
            data: punten.map(function (punt) { return punt.temp; }),
            borderColor: "#3f51b5",
            tension: 0.2
          }]
        }
      });
    </script>
    {% endif %}
    {% else %}
    <h1>Weerstation</h1>
    <p>Dit station staat niet in de database.</p>
    {% endif %}
  </main>
</body>
</html>
```

`{% for meting in metingen %}` maakt een rij per meting. `{% else %}` hoort bij die lus. De zin verschijnt als het station geen metingen heeft. De grafiek komt er dan niet bij.

`| safe` laat de aanhalingstekens in de JSON staan. Zonder die filter vervangt Jinja ze, en het script in de browser stopt.

Zet onderaan `static/style.css`:

```css
canvas {
  max-width: 100%;
}
```

De grafiek tekent alleen de temperatuur. Luchtdruk zit rond 1013 en temperatuur rond 18. Op dezelfde as wordt de temperatuur een platte lijn. De luchtdruk blijft in de tabel.

Het script onder de tabel is JavaScript. Het draait in de browser. Chart.js tekent de lijn. Python heeft de getallen al gekozen. Voor die bibliotheek heb je internet nodig.

## Nakijken

Start de server opnieuw:

```powershell
python -m uvicorn main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Je ziet Klaslokaal, zeven rijen, en een lijn die overdag stijgt en daarna zakt.

Voeg via [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) een meting toe. Vernieuw de pagina. De rij staat erbij. Stop de server met `Ctrl+C` en start hem opnieuw. De rij staat er nog.

## De test

Vervang `test_main.py`. De eerste regels kiezen een ander databasebestand, en ze staan bóven `import main`. Python leest een bestand van boven naar beneden. `main.py` opent de database op het moment dat de test hem importeert.

```python
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
```

De laatste test opent het testbestand en zoekt de temperatuur. Een lijst in het geheugen staat niet in dat bestand. Je eigen `weerstation.db` blijft onaangeroerd.

```powershell
pytest
```

Vijf tests passed.

## Bewaren op GitHub

```powershell
git add database.py main.py test_main.py templates/index.html static/style.css
git commit -m "Toon de metingen uit de database in een tabel en een grafiek"
git push
```

## Klaar als

- [http://127.0.0.1:8000](http://127.0.0.1:8000) toont zeven metingen van Klaslokaal en een grafiek van de temperatuur.
- Een meting via `/docs` blijft staan nadat je de server herstart.
- `pytest` eindigt met 5 geslaagde tests.
- De aangepaste bestanden staan op GitHub. `weerstation.db` niet.

In [Inloggen](inloggen.md) ziet een gebruiker alleen zijn eigen station.

??? note "Als het niet lukt"

    **De pagina toont nog één rij met 18,2 °C.** `main.py` gebruikt nog de lijst. Vervang het bestand door dat uit dit hoofdstuk en herstart de server.

    **De tabel staat er, de grafiek niet.** Chart.js komt van internet. Controleer de verbinding en vernieuw met `Ctrl+F5`. Blijft het vlak leeg, open dan de pagina op een netwerk dat `cdn.jsdelivr.net` toelaat.

    **De pagina toont veertien rijen.** De query in `metingen_van_station` filtert niet op `station_id`. Het klaslokaal heeft zeven metingen, plus elke meting die je zelf toevoegde.

    **De test voegt rijen toe aan `weerstation.db`.** De regels met `WEERSTATION_DB` staan onder `import main`, of ze ontbreken. Ze horen bovenaan `test_main.py`.

    **`jinja2.exceptions.TemplateSyntaxError`.** Een `{% if %}` of `{% for %}` heeft geen bijpassende `{% endif %}` of `{% endfor %}`. Vergelijk `templates/index.html` met het bestand in dit hoofdstuk.
