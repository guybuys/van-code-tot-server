# Een eerste API

Een API is een afspraak over vragen die je aan een programma kan stellen. Jij schrijft dat programma met [FastAPI](https://fastapi.tiangolo.com). Het wacht op een vraag en stuurt een antwoord, meestal in JSON.

Aan het einde van dit hoofdstuk doet jouw programma drie dingen:

- `GET /` antwoordt dat het weerstation-programma draait.
- `GET /metingen` geeft de lijst met metingen.
- `POST /metingen` voegt een meting toe. Ontbreekt de temperatuur of de luchtdruk, dan weigert het programma de vraag.

Je test dat op vier manieren. De lijst met metingen leeft alleen zolang het programma draait. Afsluiten wist wat je toevoegde. Bewaren in een database komt later.

## Virtuele omgeving

Installeer FastAPI niet in de algemene Python van je laptop. Een virtuele omgeving is een aparte Python voor dit project. Ze staat in de map `.venv`. Die map staat in `.gitignore` en gaat niet naar GitHub.

Ga in de terminal naar je repository. Als je de map in VS Code hebt openstaan, staat de terminal daar al.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

De prompt begint daarna met `(.venv)`.

??? note "PowerShell blokkeert het activate-script"

    Zie je een fout over *execution policy*, typ dan dit in dezelfde terminal en activeer opnieuw:

    ```powershell
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    .venv\Scripts\Activate.ps1
    ```

    `Process` geldt alleen voor dit venster. In een nieuwe terminal activeer je de omgeving opnieuw met `.venv\Scripts\Activate.ps1`.

Installeer daarna de pakketten voor dit hoofdstuk:

```powershell
python -m pip install fastapi uvicorn httpx2 pytest
```

`fastapi` is de bibliotheek waarmee je de routes schrijft. `uvicorn` is het programma dat je code op een poort zet. `httpx2` en `pytest` dienen voor de automatische test aan het einde.

Koppel die omgeving aan de editor. `Ctrl+Shift+P`, typ **Python: Select Interpreter**, en kies de interpreter waarvan het pad `.venv` bevat. Importfouten in de editor betekenen bijna altijd dat nog de andere Python geselecteerd is.

## Het programma

Maak `main.py` in de root van de repository, naast `README.md`.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

metingen = [
    {"temp": 18.2, "luchtdruk": 1013.2},
]


class Meting(BaseModel):
    temp: float
    luchtdruk: float


@app.get("/")
def home():
    return {"status": "ok", "service": "weerstation"}


@app.get("/metingen")
def lijst_metingen():
    return metingen


@app.post("/metingen")
def nieuwe_meting(meting: Meting):
    metingen.append(meting.model_dump())
    return {"ontvangen": meting.model_dump()}
```

`Meting` is een klasse, van dezelfde soort als de klassen die je al schreef. Uitgeschreven ziet ze er zo uit:

```python
class Meting:
    def __init__(self, temp, luchtdruk):
        self.temp = temp
        self.luchtdruk = luchtdruk
```

`self` is het object zelf. `__init__` hangt de twee waarden aan dat object. Daarna lees je `meting.temp` en `meting.luchtdruk`. Deze versie typ je niet. Ze toont wat de korte klasse in `main.py` voor je doet.

`(BaseModel)` achter de naam betekent dat `Meting` de `__init__` van `BaseModel` gebruikt. Die klasse komt uit Pydantic. `temp: float` is het veld, en het zegt dat de waarde een kommagetal is. FastAPI maakt het object met de JSON van de POST. De sleutels worden de parameters. `meting.model_dump()` geeft de velden terug als dictionary, dezelfde vorm als de rijen in de lijst `metingen`.

Ontbreekt een veld, of staat er tekst waar een getal hoort, dan is het antwoord status 422. `nieuwe_meting` draait dan niet.

Het teken `@` is een decorator. `app.get("/")` is die decorator. Hij zet de functie eronder op het object `app`, gekoppeld aan een GET-vraag voor `/`. `app.post("/metingen")` doet hetzelfde voor een POST. Bij het starten draait `home()` nog niet. Ze draait pas wanneer die vraag binnenkomt. De functies zelf zijn gewone functies met `def`.

`return` is het antwoord op die ene vraag. FastAPI zet een dictionary of een lijst om naar JSON. `return metingen` wordt de hele lijst. `return {"ontvangen": meting.model_dump()}` wordt alleen de meting die net binnenkwam. `metingen.append(...)` zet die meting in de lijst. Een volgende GET toont ze mee.

De namen `temp` en `luchtdruk` zijn de afspraak met iedereen die later een meting stuurt, ook het weerstation. Die namen veranderen we niet zomaar. Een extra sensor wordt een extra veld in die afspraak.

## De server starten

```powershell
python -m uvicorn main:app --reload
```

`main` is het bestand `main.py`. `app` is het FastAPI-object in dat bestand. `--reload` herstart het programma als je `main.py` bewaart.

Laat deze terminal open. De server stopt als je het venster sluit of `Ctrl+C` duwt. Vraagt Windows om netwerktoegang voor Python, sta die toe op privénetwerken.

Je ziet een regel met `http://127.0.0.1:8000`. `127.0.0.1` is je eigen laptop. Een klasgenoot kan dit adres niet openen. Dat blijft zo tot de site op een andere computer draait.

Open voor de tests hieronder een tweede terminal via de `+` in het terminalpaneel, en activeer daar ook de omgeving:

```powershell
.venv\Scripts\Activate.ps1
```

## Test 1. De browser

Ga in de browser naar [http://127.0.0.1:8000](http://127.0.0.1:8000).

Je krijgt JSON terug:

```json
{"status": "ok", "service": "weerstation"}
```

Open daarna [http://127.0.0.1:8000/metingen](http://127.0.0.1:8000/metingen). Je ziet de ene startmeting. Een browser kan deze twee vragen stellen omdat het allebei GET-vragen zijn. Een nieuwe meting toevoegen is een POST. Daarvoor gebruik je de volgende test.

## Test 2. De pagina /docs

FastAPI maakt op [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) een pagina uit je routes. Die heb je niet zelf geschreven.

1. Open **GET /metingen** en klik **Try it out**, daarna **Execute**. Het antwoord is de lijst.
2. Open **POST /metingen**, klik **Try it out**, en vul dit lichaam in:

```json
{
  "temp": 21.5,
  "luchtdruk": 1013
}
```

3. Klik **Execute**. De statuscode is `200`. In de response staat de meting die je stuurde. Een komma-getal kan als `1013.0` terugkomen. Dat is dezelfde waarde als `1013`.
4. Voer **GET /metingen** opnieuw uit. De nieuwe meting staat erbij.
5. Stuur nog een POST, dit keer zonder `luchtdruk`. De statuscode is `422`. Het programma is blijven draaien en heeft de meting niet toegevoegd. `422` betekent: de vraag is aangekomen, de inhoud klopt niet met `Meting`.

Bewaar je `main.py` terwijl de server met `--reload` draait, dan herstart het programma en is de toegevoegde meting weg. De startmeting van 18,2 °C blijft, die staat in de code.

## Test 3. curl

`curl` stuurt dezelfde soort vraag als de browser, vanuit de terminal. Zo test je zonder door menu's te klikken. Op Windows typ je `curl.exe`, zodat je het programma curl krijgt en niet de PowerShell-alias.

De server uit de eerste terminal moet draaien. In de tweede terminal:

```powershell
curl.exe http://127.0.0.1:8000/metingen
```

Maak voor de POST een bestand `body.json`:

```json
{"temp": 19.4, "luchtdruk": 1008.6}
```

```powershell
curl.exe -X POST http://127.0.0.1:8000/metingen -H "Content-Type: application/json" --data-binary "@body.json"
```

Een nieuwe GET toont ook deze meting. `body.json` is een testhulpmiddel. Je hoeft het niet te committen.

## Test 4. Een automatische test

De drie tests hierboven doe je zelf, terwijl de server draait. Een automatische test stelt de vragen in Python en controleert het antwoord. Daarvoor hoeft de server niet te draaien. Stop uvicorn gerust met `Ctrl+C`.

Maak `test_main.py`:

```python
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


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

`pytest` kijkt in de map van de terminal. Een bestand waarvan de naam met `test_` begint, wordt gelezen. Daarin voert pytest elke functie uit waarvan de naam ook met `test_` begint. In `test_main.py` zijn dat de vier functies hierboven. Het bestand roept ze zelf niet aan. Pytest doet dat.

`TestClient` stuurt de vraag rechtstreeks naar `app`. Daarvoor hoeft uvicorn niet te draaien. `response.json()` is de return-waarde van de route. `assert` vergelijkt die met wat je verwacht. Klopt een vergelijking niet, dan stopt die ene test. Pytest toont de functie en de twee waarden.

```powershell
pytest
```

Vier tests passed is het doel. Een mislukte test toont de functie en de waarden die verschilden. Dat is een leesbaarder spoor dan enkel de fout in de browser.

## Bewaren op GitHub

Voer `git status` uit. `.venv/` mag niet in de lijst staan. Je commit `main.py` en `test_main.py`.

```powershell
git add main.py test_main.py
git commit -m "Voeg een eerste FastAPI met tests toe"
git push
```

## Klaar als

- [http://127.0.0.1:8000](http://127.0.0.1:8000) toont `status` en `service`.
- Via `/docs` voeg je een meting toe en zie je ze daarna in de lijst.
- Een POST zonder luchtdruk krijgt status `422`.
- `pytest` eindigt met 4 geslaagde tests.
- `main.py` en `test_main.py` staan op GitHub, `.venv` niet.

??? note "Als het niet lukt"

    **`Could not import module "main"`.** De terminal staat niet in de map waar `main.py` ligt. In VS Code staat het pad van de map links in de titelbalk. Open `C:\dev\weerstation` als dat nog niet zo is.

    **`Address already in use`.** Er draait al een uvicorn. Ga naar die terminal en duw `Ctrl+C`. Start daarna opnieuw.

    **De browser toont een fout, de terminal toont niets.** De server is gestopt, of de omgeving is in deze terminal niet geactiveerd. Het begin van de prompt toont `(.venv)` als dat wel zo is.

    **pytest vindt `fastapi` niet.** De omgeving is niet actief, of de interpreter in VS Code is een andere Python. Activeer `.venv` en voer `python -m pip install fastapi uvicorn httpx2 pytest` opnieuw uit.

    **De lijst op `/metingen` springt terug naar één meting.** Het programma is herstart. Met `--reload` gebeurt dat bij elke bewaring van `main.py`. De toegevoegde metingen staan nog nergens op schijf.

## Wat er nog ontbreekt

Elk programma op deze laptop kan een meting toevoegen. Er is geen gebruiker en geen wachtwoord. Zodra de site op een andere computer staat, volstaat de URL om metingen toe te voegen. Voor die tijd koppelen we metingen aan een account. Een wachtwoord bewaren we dan niet als leesbare tekst. Het wordt een hash: daaruit kan je het wachtwoord niet terug aflezen, en de site kan wel controleren of het ingetypte wachtwoord klopt.

De volgende hoofdstukken maken de pagina die deze gegevens toont. Eerst [HTML](html.md), nog met vaste cijfers.
