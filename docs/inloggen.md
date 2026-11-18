# Inloggen

De pagina toont het klaslokaal aan iedereen die `http://127.0.0.1:8000` opent. Een wachtwoord heeft nu pas zin: de metingen horen bij iemand.

Een gewone gebruiker ziet alleen zijn eigen station. Een beheerder ziet ze allemaal. Die controle zit in het programma. Een link die je verbergt, houdt niemand tegen: wie `/beheer` intypt, komt er toch.

## Een hash

Een wachtwoord dat als leesbare tekst in `weerstation.db` staat, leest iedereen die het bestand kopieert. Een hash is eenrichting. Uit de hash lees je het wachtwoord niet terug. Controleren is het ingetypte wachtwoord opnieuw hashen en vergelijken.

`bcrypt` maakt de hash, en een salt. De salt zorgt dat twee hashes van hetzelfde wachtwoord er verschillend uitzien. Typ dit eens in een tijdelijk bestand en voer het uit. Je bewaart het bestand niet.

```python
import bcrypt

wachtwoord = "geheim123".encode()
eerste = bcrypt.hashpw(wachtwoord, bcrypt.gensalt())
tweede = bcrypt.hashpw(wachtwoord, bcrypt.gensalt())
print(eerste)
print(tweede)
print(bcrypt.checkpw(wachtwoord, eerste))
print(bcrypt.checkpw(wachtwoord, tweede))
```

Je ziet twee verschillende regels, en twee keer `True`. In de database bewaren we de hash als tekst, met `.decode()`.

Installeer de pakketten in de omgeving van het project:

```powershell
python -m pip install bcrypt python-multipart itsdangerous
```

`bcrypt` maakt de hash. `python-multipart` leest een formulier. `itsdangerous` ondertekent de cookie van de sessie.

## Accounts

Een registratie zet de rol altijd op `gebruiker`. Het formulier heeft geen veld voor de rol. Wie daar beheerder zou kunnen kiezen, maakt iedereen beheerder. De eerste beheerder komt uit een script, verderop.

Een fout wachtwoord en een onbekend e-mailadres krijgen dezelfde zin: `Onbekend e-mailadres of wachtwoord.` Zo verklapt de site niet welk van de twee fout was.

Zet deze functies in `database.py`, boven `toon`.

```python
def als_dict(rij):
    if rij is None:
        return None
    return dict(rij)


def voeg_account_toe(naam, email, wachtwoord_hash, rol):
    verbinding = verbind()
    try:
        cursor = verbinding.execute(
            """
            INSERT INTO gebruiker (naam, email, wachtwoord_hash, rol)
            VALUES (?, ?, ?, ?)
            """,
            (naam, email, wachtwoord_hash, rol),
        )
        verbinding.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        verbinding.close()


def voeg_gebruiker_toe(naam, email, wachtwoord_hash):
    return voeg_account_toe(naam, email, wachtwoord_hash, "gebruiker")


def voeg_beheerder_toe(naam, email, wachtwoord_hash):
    return voeg_account_toe(naam, email, wachtwoord_hash, "beheerder")


def gebruiker_van_email(email):
    verbinding = verbind()
    rij = verbinding.execute(
        "SELECT id, naam, email, wachtwoord_hash, rol FROM gebruiker WHERE email = ?",
        (email,),
    ).fetchone()
    verbinding.close()
    return als_dict(rij)


def gebruiker_van_id(gebruiker_id):
    verbinding = verbind()
    rij = verbinding.execute(
        "SELECT id, naam, email, rol FROM gebruiker WHERE id = ?",
        (gebruiker_id,),
    ).fetchone()
    verbinding.close()
    return als_dict(rij)


def stations_van_gebruiker(gebruiker_id):
    verbinding = verbind()
    rijen = verbinding.execute(
        """
        SELECT id, naam
        FROM station
        WHERE gebruiker_id = ?
        ORDER BY id
        """,
        (gebruiker_id,),
    ).fetchall()
    verbinding.close()
    return [dict(rij) for rij in rijen]


def alle_stations():
    verbinding = verbind()
    rijen = verbinding.execute(
        """
        SELECT station.id, station.naam, gebruiker.email
        FROM station
        LEFT JOIN gebruiker ON gebruiker.id = station.gebruiker_id
        ORDER BY station.id
        """
    ).fetchall()
    verbinding.close()
    return [dict(rij) for rij in rijen]


def station_van_gebruiker(station_id, gebruiker_id):
    verbinding = verbind()
    rij = verbinding.execute(
        """
        SELECT id, naam
        FROM station
        WHERE id = ? AND gebruiker_id = ?
        """,
        (station_id, gebruiker_id),
    ).fetchone()
    verbinding.close()
    return als_dict(rij)


def koppel_station(station_id, email):
    gebruiker = gebruiker_van_email(email)
    if gebruiker is None:
        return False
    verbinding = verbind()
    cursor = verbinding.execute(
        "UPDATE station SET gebruiker_id = ? WHERE id = ?",
        (gebruiker["id"], station_id),
    )
    verbinding.commit()
    gewijzigd = cursor.rowcount == 1
    verbinding.close()
    return gewijzigd
```

`voeg_gebruiker_toe` zet de rol zelf op `gebruiker`. `?` blijft de plaats voor een waarde. Bestaat het e-mailadres al, dan geeft de functie `None` terug. `station_van_gebruiker` vindt een station alleen als het van die gebruiker is. De query weigert het andere station, niet een verborgen menu.

## De sessie

Een sessie is een cookie. De browser stuurt ze bij elke vraag mee. In de cookie staat het id van de gebruiker, ondertekend met een sleutel. Wie de cookie wijzigt, maakt de ondertekening stuk, en de sessie is leeg.

`WEERSTATION_SLEUTEL` is die sleutel. De waarde `alleen-op-deze-laptop` volstaat zolang de site op jouw computer draait. Op de server wordt dat een echte sleutel, buiten de repository.

Vervang `main.py` door dit bestand. De routes voor `/metingen` blijven. Die JSON-route is nog open. De pagina is wat dit hoofdstuk afsluit. Het programma dat metingen van het bord schrijft, komt in het volgende hoofdstuk.

```python
import json
import os

import bcrypt
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

import database

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("WEERSTATION_SLEUTEL", "alleen-op-deze-laptop"),
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

database.start()

FOUT_AANMELDEN = "Onbekend e-mailadres of wachtwoord."


class Meting(BaseModel):
    temp: float
    luchtdruk: float


def hash_wachtwoord(wachtwoord):
    return bcrypt.hashpw(wachtwoord.encode(), bcrypt.gensalt()).decode()


def wachtwoord_klopt(wachtwoord, wachtwoord_hash):
    return bcrypt.checkpw(wachtwoord.encode(), wachtwoord_hash.encode())


def huidige_gebruiker(request):
    gebruiker_id = request.session.get("gebruiker_id")
    if gebruiker_id is None:
        return None
    return database.gebruiker_van_id(gebruiker_id)


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


def pagina(request, gebruiker, stations, station, geweigerd, rijen):
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "gebruiker": gebruiker,
            "beheerder": gebruiker["rol"] == "beheerder",
            "stations": stations,
            "station": station,
            "geweigerd": geweigerd,
            "metingen": [voor_tabel(rij) for rij in rijen],
            "grafiek_json": json.dumps([voor_grafiek(rij) for rij in rijen]),
        },
    )


@app.get("/login")
def login_pagina(request: Request):
    return templates.TemplateResponse(request, "login.html", {"fout": ""})


@app.post("/login")
def meld_aan(request: Request, email: str = Form(), wachtwoord: str = Form()):
    gebruiker = database.gebruiker_van_email(email)
    klopt = (
        gebruiker is not None
        and wachtwoord_klopt(wachtwoord, gebruiker["wachtwoord_hash"])
    )
    if not klopt:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"fout": FOUT_AANMELDEN},
            status_code=401,
        )
    request.session["gebruiker_id"] = gebruiker["id"]
    return RedirectResponse("/", status_code=303)


@app.get("/registreren")
def registratie_pagina(request: Request):
    return templates.TemplateResponse(request, "registreren.html", {"fout": ""})


@app.post("/registreren")
def registreer(
    request: Request,
    naam: str = Form(),
    email: str = Form(),
    wachtwoord: str = Form(),
):
    if len(wachtwoord) < 8:
        return templates.TemplateResponse(
            request,
            "registreren.html",
            {"fout": "Kies een wachtwoord van minstens 8 tekens."},
            status_code=400,
        )
    gebruiker_id = database.voeg_gebruiker_toe(naam, email, hash_wachtwoord(wachtwoord))
    if gebruiker_id is None:
        return templates.TemplateResponse(
            request,
            "registreren.html",
            {"fout": "Dit e-mailadres bestaat al."},
            status_code=400,
        )
    request.session["gebruiker_id"] = gebruiker_id
    return RedirectResponse("/", status_code=303)


@app.post("/afmelden")
def meld_af(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/")
def home(request: Request, station_id: int = None):
    gebruiker = huidige_gebruiker(request)
    if gebruiker is None:
        return RedirectResponse("/login", status_code=303)

    if gebruiker["rol"] == "beheerder":
        stations = database.alle_stations()
        if station_id is None and stations:
            station_id = stations[0]["id"]
        naam = database.naam_van_station(station_id) if station_id else None
        rijen = database.metingen_van_station(station_id) if naam else []
        return pagina(request, gebruiker, stations, naam, False, rijen)

    stations = database.stations_van_gebruiker(gebruiker["id"])
    if station_id is None and len(stations) == 1:
        station_id = stations[0]["id"]
    if station_id is None:
        return pagina(request, gebruiker, stations, None, False, [])
    eigen = database.station_van_gebruiker(station_id, gebruiker["id"])
    if eigen is None:
        return pagina(request, gebruiker, stations, None, True, [])
    rijen = database.metingen_van_station(station_id)
    return pagina(request, gebruiker, stations, eigen["naam"], False, rijen)


@app.get("/beheer")
def beheer_pagina(request: Request):
    gebruiker = huidige_gebruiker(request)
    if gebruiker is None:
        return RedirectResponse("/login", status_code=303)
    if gebruiker["rol"] != "beheerder":
        raise HTTPException(status_code=403)
    return templates.TemplateResponse(
        request,
        "beheer.html",
        {
            "gebruiker": gebruiker,
            "stations": database.alle_stations(),
            "fout": "",
        },
    )


@app.post("/beheer")
def koppel(request: Request, station_id: int = Form(), email: str = Form()):
    gebruiker = huidige_gebruiker(request)
    if gebruiker is None:
        return RedirectResponse("/login", status_code=303)
    if gebruiker["rol"] != "beheerder":
        raise HTTPException(status_code=403)
    fout = ""
    if not database.koppel_station(station_id, email):
        fout = "Dat station of dat e-mailadres staat niet in de database."
    return templates.TemplateResponse(
        request,
        "beheer.html",
        {
            "gebruiker": gebruiker,
            "stations": database.alle_stations(),
            "fout": fout,
        },
    )


@app.get("/metingen")
def lijst_metingen():
    return database.alle_metingen()


@app.post("/metingen")
def nieuwe_meting(meting: Meting):
    return {"ontvangen": database.voeg_meting_toe(1, meting.temp, meting.luchtdruk)}
```

`Form()` leest de velden van het formulier. Dat is geen JSON. `request` moet `Request` zijn, geïmporteerd uit FastAPI. Zonder die import eist FastAPI een `?request=` in het adres.

`huidige_gebruiker` leest het id uit de sessie. Geen cookie, geen gebruiker, en `/` stuurt je naar `/login`. Een beheerder krijgt alle stations. Een gebruiker krijgt de query met zijn id. Een station van iemand anders wordt de zin `Dit station is niet van jou.` De temperaturen van dat station zitten niet in het antwoord.

`/beheer` van een gewone gebruiker stopt met status 403. De link op de pagina van de beheerder is alleen een snelkoppeling. De weigering zit in de functie.

## De formulieren

Maak `templates/login.html`.

```html
<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <title>Aanmelden</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <main>
    <h1>Aanmelden</h1>
    {% if fout %}
    <p class="fout">{{ fout }}</p>
    {% endif %}
    <form method="post" action="/login">
      <label>E-mail
        <input name="email" type="email" required>
      </label>
      <label>Wachtwoord
        <input name="wachtwoord" type="password" required>
      </label>
      <button type="submit">Aanmelden</button>
    </form>
    <p><a href="/registreren">Nog geen account</a></p>
  </main>
</body>
</html>
```

Maak `templates/registreren.html`.

```html
<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <title>Registreren</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <main>
    <h1>Registreren</h1>
    {% if fout %}
    <p class="fout">{{ fout }}</p>
    {% endif %}
    <form method="post" action="/registreren">
      <label>Naam
        <input name="naam" required>
      </label>
      <label>E-mail
        <input name="email" type="email" required>
      </label>
      <label>Wachtwoord
        <input name="wachtwoord" type="password" required>
      </label>
      <button type="submit">Account maken</button>
    </form>
    <p><a href="/login">Al een account</a></p>
  </main>
</body>
</html>
```

Maak `templates/beheer.html`.

```html
<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <title>Beheer</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <main>
    <h1>Beheer</h1>
    <p>{{ gebruiker.naam }}</p>
    {% if fout %}
    <p class="fout">{{ fout }}</p>
    {% endif %}
    <table>
      <thead>
        <tr>
          <th>Station</th>
          <th>E-mail van de eigenaar</th>
        </tr>
      </thead>
      <tbody>
        {% for station in stations %}
        <tr>
          <td>{{ station.id }}. {{ station.naam }}</td>
          <td>{{ station.email or "niemand" }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    <form method="post" action="/beheer">
      <label>Nummer van het station
        <input name="station_id" type="number" required>
      </label>
      <label>E-mail van de gebruiker
        <input name="email" type="email" required>
      </label>
      <button type="submit">Koppelen</button>
    </form>
    <p><a href="/">Terug naar de metingen</a></p>
  </main>
</body>
</html>
```

Vervang `templates/index.html`. Bovenaan staan je naam, de knop afmelden, en de stations die je mag zien. De tabel en de grafiek blijven.

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
    <p>
      {{ gebruiker.naam }}
      {% if beheerder %}
      · <a href="/beheer">Beheer</a>
      {% endif %}
    </p>
    <form method="post" action="/afmelden">
      <button type="submit">Afmelden</button>
    </form>
    {% if stations %}
    <nav>
      {% for item in stations %}
      <a href="/?station_id={{ item.id }}">{{ item.naam }}</a>
      {% endfor %}
    </nav>
    {% endif %}
    {% if geweigerd %}
    <h1>Weerstation</h1>
    <p>Dit station is niet van jou.</p>
    {% elif station %}
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
    {% elif stations %}
    <h1>Kies een station</h1>
    {% else %}
    <h1>Weerstation</h1>
    <p>Je hebt nog geen station.</p>
    {% endif %}
  </main>
</body>
</html>
```

Zet onderaan `static/style.css`:

```css
label {
  display: block;
  margin: 0.8rem 0;
}

input,
button {
  font: inherit;
}

input {
  display: block;
  width: 100%;
  margin-top: 0.3rem;
  padding: 0.4rem 0.5rem;
}

button {
  margin-top: 0.6rem;
}

nav a {
  margin-right: 0.8rem;
}

.fout {
  color: #9b2c2c;
}
```

## De eerste beheerder

Maak `maak_beheerder.py`.

```python
import getpass

import bcrypt

import database

database.start()

naam = input("Naam: ")
email = input("E-mail: ")
wachtwoord = getpass.getpass("Wachtwoord: ")
if len(wachtwoord) < 8:
    print("Kies een wachtwoord van minstens 8 tekens.")
else:
    wachtwoord_hash = bcrypt.hashpw(wachtwoord.encode(), bcrypt.gensalt()).decode()
    if database.voeg_beheerder_toe(naam, email, wachtwoord_hash) is None:
        print("Dit e-mailadres bestaat al.")
    else:
        print("Beheerder bewaard.")
```

De server mag hiervoor uit staan. In de terminal:

```powershell
python maak_beheerder.py
```

Kies een wachtwoord van minstens 8 tekens. Het script toont het wachtwoord niet. Start daarna de server en meld je aan op [http://127.0.0.1:8000](http://127.0.0.1:8000). Je ziet Klaslokaal en Speelplaats, en de link Beheer.

Op `/beheer` koppel je Klaslokaal aan een gewoon account. Dat account maak je via `/registreren`. Meld je daarna aan als die gebruiker. Je ziet één station. `http://127.0.0.1:8000/?station_id=2` toont `Dit station is niet van jou.` Typ je zelf `/beheer`, dan is het antwoord 403.

De voorbeeldstations hebben nog geen eigenaar tot je ze koppelt. Een nieuwe gebruiker ziet daarom eerst `Je hebt nog geen station.`

## De test

Vervang `test_main.py`. De tests maken zelf accounts in een tijdelijke database. Jouw `weerstation.db` en je beheerder blijven staan. De regels met `WEERSTATION_DB` horen boven `import main`.

```python
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


def test_meting_blijft_bewaard():
    nieuw().post("/metingen", json={"temp": 12.3, "luchtdruk": 1002.5})
    verbinding = sqlite3.connect(os.environ["WEERSTATION_DB"])
    rij = verbinding.execute("SELECT temp FROM meting WHERE temp = 12.3").fetchone()
    verbinding.close()
    assert rij is not None
```

```powershell
pytest
```

Tien tests passed.

## Bewaren op GitHub

```powershell
git add database.py main.py maak_beheerder.py test_main.py templates static/style.css
git commit -m "Laat een gebruiker alleen zijn eigen station zien"
git push
```

## Klaar als

- Zonder aanmelden opent `/` het formulier, niet de metingen.
- Een fout wachtwoord en een onbekend e-mailadres tonen dezelfde zin.
- Een gebruiker ziet alleen het station dat de beheerder koppelde.
- `/beheer` als gebruiker antwoordt met 403.
- `pytest` eindigt met 10 geslaagde tests.

In [MQTT](mqtt.md) schrijft een tweede programma de metingen van het bord in dezelfde database.

??? note "Als het niet lukt"

    **Je ziet Klaslokaal zonder aanmelden.** `home` is nog de oude functie. Vervang heel `main.py`.

    **`Field required` bij `query` en `request`.** `Request` is niet geïmporteerd, of alleen de functie `home` is geplakt. Het importblok bovenaan hoort bij het bestand uit dit hoofdstuk.

    **`Form data requires "python-multipart"`.** Het pakket ontbreekt. Voer `python -m pip install python-multipart` opnieuw uit in de actieve omgeving.

    **`No module named 'itsdangerous'`.** Zelfde stap, met `itsdangerous`. De sessie ondertekent de cookie daarmee.

    **`No module named 'bcrypt'`.** `python -m pip install bcrypt` in de omgeving waarvan de prompt met `(.venv)` begint.

    **Een gebruiker ziet de speelplaats.** `stations_van_gebruiker` filtert niet op `gebruiker_id`, of `home` gebruikt nog `alle_stations` voor iedereen.

    **`/beheer` lukt als gebruiker.** De controle op `rol` ontbreekt. Status 403 hoort vóór de template.
