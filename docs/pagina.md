# De pagina uit FastAPI

`start index.html` opent een bestand op jouw laptop. Het adres begint met `file:///`. Een bezoeker heeft dat bestand niet. Je programma moet de pagina sturen, op dezelfde manier als het JSON stuurt op `/metingen`.

De vorm blijft de CSS uit het vorige hoofdstuk. De cijfers komen uit de lijst `metingen`.

## Jinja

Jinja vult een HTML-bestand in. FastAPI leest dat bestand en stuurt het resultaat naar de browser.

Installeer het pakket in de omgeving van het project. De prompt begint met `(.venv)`.

```powershell
python -m pip install jinja2
```

## Twee mappen

Maak een map `templates` en verplaats `index.html` daarnaartoe. Maak een map `static` en verplaats `style.css` daarnaartoe. Verwijder de twee bestanden uit de root. Anders bewerk je straks een bestand dat de server niet leest.

`templates` is voor de pagina. Jinja leest die map. `static` is voor bestanden die ongewijzigd meegaan, zoals de CSS.

In `templates/index.html` wordt de link naar de CSS:

```html
<link rel="stylesheet" href="/static/style.css">
```

De browser vraagt die CSS aan je programma, op `http://127.0.0.1:8000/static/style.css`. De bestandsnaam alleen zoekt naast het HTML-bestand. Dat pad bestond bij `file:///`. Op de server bestaat het niet, en de pagina blijft kaal.

`style.css` zelf verandert niet.

## De cijfers uit de lijst

Vervang in de tabel de twee vaste waarden door een plek die Jinja invult:

```html
<td>{{ temperatuur }} °C</td>
<td>{{ luchtdruk }} hPa</td>
```

`{{ temperatuur }}` wordt de tekst die je in Python meegeeft. De naam in de accolades is dezelfde als de naam in Python. De rest van de pagina blijft zoals in het HTML-hoofdstuk.

## De route

Vervang `main.py` door dit bestand. De lijst, `Meting` en de routes voor `/metingen` herken je.

```python
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

metingen = [
    {"temp": 18.2, "luchtdruk": 1013.2},
]


class Meting(BaseModel):
    temp: float
    luchtdruk: float


@app.get("/")
def home(request: Request):
    laatste = metingen[-1]
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "temperatuur": f"{laatste['temp']:.1f}".replace(".", ","),
            "luchtdruk": f"{laatste['luchtdruk']:.1f}".replace(".", ","),
        },
    )


@app.get("/metingen")
def lijst_metingen():
    return metingen


@app.post("/metingen")
def nieuwe_meting(meting: Meting):
    metingen.append(meting.model_dump())
    return {"ontvangen": meting.model_dump()}
```

`mount` koppelt het adres `/static` aan de map `static`. `Jinja2Templates` leest de map `templates`.

`request` is de vraag die de browser stuurde. `TemplateResponse` verwacht dat argument. `metingen[-1]` is de laatste meting. Bij de start is dat de meting van 18,2 °C.

In de lijst staat een punt, `18.2`. Op de pagina hoort een komma, `18,2`. `f"{laatste['temp']:.1f}"` maakt tekst met één cijfer na de punt. `replace` zet die punt om in een komma.

## Nakijken

Start de server als hij nog niet draait:

```powershell
python -m uvicorn main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Je ziet de witte kolom, met 18,2 °C en 1013,2 hPa. Het adres begint met `http://`, niet met `file:///`.

Voeg via [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) een meting toe, bijvoorbeeld temperatuur 21,5 en luchtdruk 1013. Vernieuw `/`. De tabel toont 21,5 °C. Een geheel getal komt terug met één cijfer na de komma, dus 1013,0. Dat is dezelfde waarde.

De lijst verdwijnt nog altijd als het programma herstart. Bewaren komt later.

## De test

`test_home` verwachtte JSON op `/`. Die route stuurt nu HTML. Vervang `test_main.py` door dit bestand. De andere drie tests zijn dezelfde.

```python
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
```

De test voegt zelf een meting toe en kijkt of de pagina die toont. `response.text` is de HTML als tekst. Pytest start de server niet. Draait uvicorn nog, dan mag dat blijven.

```powershell
pytest
```

Vier tests passed.

## Bewaren op GitHub

```powershell
git add main.py test_main.py templates/index.html static/style.css
git add -u index.html style.css
git commit -m "Laat FastAPI de pagina serveren"
git push
```

De tweede `git add` bewaart dat de oude bestanden uit de root weg zijn. In `git status` staan `templates/` en `static/`, en geen `index.html` meer naast `main.py`.

## Klaar als

- [http://127.0.0.1:8000](http://127.0.0.1:8000) toont de witte kolom met 18,2 °C en 1013,2 hPa.
- Na een POST via `/docs` toont een vernieuwde pagina de nieuwe meting.
- `pytest` eindigt met 4 geslaagde tests.
- `templates/index.html` en `static/style.css` staan op GitHub. De oude bestanden in de root zijn weg.

De lijst verdwijnt nog bij een herstart. In [Database](database.md) blijven de metingen in een bestand staan.

??? note "Als het niet lukt"

    **De pagina is kaal.** De `link` wijst nog naar `style.css`, of dat bestand staat niet in `static`. Open [http://127.0.0.1:8000/static/style.css](http://127.0.0.1:8000/static/style.css). Je hoort daar de CSS als tekst te zien.

    **`jinja2 must be installed`.** De omgeving is niet actief, of het pakket ontbreekt. Activeer `.venv` en voer `python -m pip install jinja2` opnieuw uit.

    **`TemplateNotFound`.** `index.html` staat niet in de map `templates`, of de terminal staat niet in `C:\dev\weerstation`.

    **Je ziet JSON op `/`.** `home` geeft nog het oude woordenboek terug. Bewaar `main.py` en laat `--reload` herstarten.

    **De tabel verandert niet na een POST.** De pagina is geopend met `start index.html`. Gebruik het adres `http://127.0.0.1:8000`.

    **De eerste test faalt op `response.json()`.** `test_home` is nog de oude test. Vervang `test_main.py` door het bestand uit dit hoofdstuk.
