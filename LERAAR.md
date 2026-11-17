# Voor de leerkracht

De site in `docs/` is voor de leerlingen. Dit bestand is de aanpak, zodat de volgorde ook zonder het gesprek terug te vinden is. Welk leerplandoel in welk onderdeel zit, staat in `LEERDOELEN.md`.

## Volgorde

Eerst de werkomgeving, dan een backend die ze kunnen testen, daarna pas de pagina.

1. **VS Code.** Editor, terminal, Python 3.10+ zichtbaar in die terminal.
2. **Git en GitHub.** Eén private repository `weerstation` per leerling, gecloned naar `C:\dev\weerstation` (buiten OneDrive). De leerling voegt jou toe als collaborator. De eerste push is een README met naam en klas, plus een `.gitignore` voor `.venv/`, `__pycache__/` en `.env`.
3. **FastAPI.** JSON-routes, nog geen HTML. Vier manieren om te testen: browser, `/docs`, `curl.exe`, pytest met `TestClient`.
4. HTML, daarna CSS. Nog met vaste cijfers.
5. Die pagina door FastAPI laten serveren (Jinja).
6. Databases vergelijken (SQL, InfluxDB, MongoDB) en SQL kiezen. SQLite lokaal.
7. Tabel, daarna één grafiek.
8. Wachtwoorden, login en twee rollen: `gebruiker` en `beheerder`.
9. MQTT-ingester. Een apart programma, niet de FastAPI-app. De site leest de database, de ingester schrijft metingen. Zo zien ze twee programma's op dezelfde database. Dat verschil hoort in dit hoofdstuk, niet in de introductie.
10. SSH en de NUC.
11. Eén gezamenlijke deploy.

HTML komt bewust na de eerste API. De leerlingen kennen Python. Een JSON-antwoord kunnen ze testen voor er een pagina bestaat. `/docs` geeft meteen iets om aan te klikken.

Één repository voor de hele site. Het bord hoort niet in de cursustekst. In de les mag je één programma even tonen, zodat ze zien dat het bericht niet van het bord afhangt. Een hoofdstuk wordt het niet. Nu publiceert een Arduino Uno R4 WiFi voor de vierdejaars, in `arduino/weerstation_mqtt/`. Dezelfde berichten staan in MicroPython voor een ESP32, in `esp32/weerstation_mqtt/`. Voor het zesde jaar telt alleen het bericht.

Twee topics per station:

- `weerstation/N/meting`, niet retained: `{"temp":21.5,"luchtdruk":1013.2}`. Die namen zijn dezelfde als de BMP280. Een extra sensor, zoals windsnelheid, wordt later een extra veld. De eerste API blijft twee verplichte velden.
- `weerstation/N/info`, retained, één keer na verbinden: `{"naam","leden","breedte","lengte"}`. De coördinaten zijn een vast punt dat ze intypen, geen GPS. De broker bewaart dit bericht, dus een nieuwe luisteraar krijgt het meteen.

In het databasehoofdstuk kiezen we vaste kolommen zolang elk station `temp` en `luchtdruk` stuurt. Een JSON-kolom komt pas als stations verschillende sensoren sturen. `leden` zit in het info-bericht en nog niet in de tabel `station`. Die tabel heeft `naam`, `breedte` en `lengte`.

## Repository delen

Leerlingen maken de repository op hun eigen account, private, en nodigen jouw GitHub-gebruikersnaam uit via Settings → Collaborators. Jij aanvaardt de uitnodiging. Zonder die aanvaarding zie je een private repository niet.

Zeg de gebruikersnaam in de les. Ze staat bewust niet in de cursustekst.

## FastAPI, kort voor jezelf

De leerlingen schrijven gewone `def`-functies. Geen `async`.

- `GET /` geeft in het eerste API-hoofdstuk `{"status": "ok", "service": "weerstation"}`. Vanaf het hoofdstuk over de pagina geeft `GET /` de HTML. De JSON-lijst blijft op `GET /metingen`.
- `GET /metingen` geeft een lijst in het geheugen.
- `POST /metingen` voegt een meting toe. FastAPI leest de JSON en vult het type `Meting`.
- Een POST zonder een verplicht veld krijgt status **422**. Het programma crasht niet.
- `Meting` staat in het hoofdstuk ook uitgeschreven met `__init__` en `self`. Die versie typen ze niet. `BaseModel` schrijft die constructor. Zo hangt Pydantic aan de klassen die ze al kennen.
- De lijst verdwijnt bij een herstart. Dat is de brug naar de database. Vanaf dat hoofdstuk staat dezelfde informatie in `weerstation.db`.

Testen, van minst naar meest formeel:

| Manier | Server moet draaien | Waar het goed voor is |
|---|---|---|
| Browser | ja | Een GET zien |
| `/docs` | ja | GET en POST aanklikken, ook de 422 |
| `curl.exe` | ja | Dezelfde vraag als tekst, zonder het menu |
| `pytest` | nee | Antwoord controleren en opnieuw kunnen afspelen |

Op Windows is het commando `curl.exe`. `curl` alleen is in PowerShell een alias en gedraagt zich anders. Voor de POST schrijven ze de JSON in `body.json`, zodat aanhalingstekens in PowerShell geen probleem zijn.

Het werkende voorbeeld staat in `voorbeelden/01-fastapi/`. Dat hoort niet op de cursussite. Leerlingen typen de code in hun eigen repository.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
pytest
python -m uvicorn main:app --reload
```

## HTML en CSS

`index.html` toont één meting met vaste cijfers. `style.css` zet die pagina in een witte kolom. De leerlingen openen het bestand met `start index.html`. FastAPI draait daarbij niet. Geen Jinja, geen media queries. Het voorbeeld na beide hoofdstukken staat in `voorbeelden/02-pagina/`.

## De pagina uit FastAPI

`index.html` verhuist naar `templates/`, `style.css` naar `static/`. De link wordt `/static/style.css`. `GET /` vult met Jinja de laatste meting uit de lijst in, met een komma op de pagina. Een POST via `/docs` en een vernieuwde `/` tonen die nieuwe meting. `test_home` stuurt zelf een meting en zoekt de komma-getallen in de HTML. De andere drie tests blijven. Het voorbeeld staat in `voorbeelden/03-pagina/`.

## Database

SQLite in `weerstation.db`, via `sqlite3` uit de standaardbibliotheek. PostgreSQL blijft voor de server. InfluxDB en MongoDB worden genoemd en niet gebruikt. Vaste kolommen, zolang elk station `temp` en `luchtdruk` stuurt.

Drie tabellen: `gebruiker`, `station`, `meting`. `gebruiker` krijgt nog geen rijen. Een leesbaar oefenwachtwoord in het bestand zou het hash-hoofdstuk onderuit halen. `gebruiker_id` bij de voorbeeldstations blijft leeg.

De voorbeeldmetingen zijn nodig omdat MQTT pas later schrijft. Twee stations, Klaslokaal en Speelplaats, op 16 november 2026, om de twee uur van 06:00 tot 18:00 UTC. Zeven rijen per station. Het lokaal blijft rond 18 °C. De speelplaats gaat van 7,4 °C naar 13,8 °C. De luchtdruk daalt bij beide van ongeveer 1016 hPa naar 1013 hPa. De coördinaten zijn afgeronde punten bij de school: 51,0298 en 4,4765 voor het lokaal. Het script vult alleen als `station` leeg is. `weerstation.db` staat in `.gitignore`. Queries gebruiken `?`.

Het hoofdstuk linkt niet naar de databasecursus van je collega. Die wijs je zelf aan als naslag.

Het voorbeeld staat in `voorbeelden/04-database/`.

## Metingen op de pagina

`GET /` toont station 1, het klaslokaal: een tabel en daarna één lijngrafiek van de temperatuur. Luchtdruk blijft in de tabel, omdat 1013 en 18 op dezelfde as de temperatuur plat trekken. De speelplaats zit in de database en nog niet op de pagina.

Chart.js 4.4.6 komt van `cdn.jsdelivr.net`. Zonder dat domein blijft de tabel werken en de grafiek leeg. Een lege reeks tekent geen grafiek en toont een zin. Een onbekend station ook.

`POST /metingen` schrijft naar station 1 en zet zelf de UTC-tijd. De vier oude tests blijven, plus een vijfde die de rij in het sqlite-bestand zoekt. De tests gebruiken `WEERSTATION_DB` in de temp-map, gezet vóór `import main`.

Het voorbeeld staat in `voorbeelden/05-metingen/`.

## Van MQTT naar de database

Dit hoofdstuk is er nog niet. De website praat niet met de broker. Een tweede programma, de ingester, doet dat. Zo zien ze twee programma's op dezelfde database.

1. Het bord publiceert naar EMQX.
2. De ingester is geabonneerd op `weerstation/+/info` en `weerstation/+/meting`.
3. Bij info maakt of werkt ze het station bij: naam, breedte en lengte. Het nummer in het topic wijst het station aan.
4. Bij een meting schrijft ze een rij: station, temperatuur en luchtdruk. De tijd zet de ingester zelf, in UTC. Het bord stuurt geen klok mee.
5. FastAPI leest alleen de database. De pagina toont de laatste rijen ook als de broker even weg is.

Lokaal is dat hetzelfde `weerstation.db`. Op de server wordt dat PostgreSQL, met dezelfde tabellen. De voorbeeldmetingen in de cursus blijven staan tot dit programma echt schrijft.

## Wachtwoorden

Nog geen hoofdstuk. Een hash uitleggen voor er een gebruikerstabel is, blijft los zand.

Het loginhoofdstuk krijgt drie delen, na SQLite:

1. Begrijpen. Wie `station.db` kopieert, leest leesbare wachtwoorden als die er als tekst in staan. Een hash is eenrichting. Een salt zorgt dat twee dezelfde wachtwoorden er verschillend uitzien. Controleren is het ingetypte wachtwoord opnieuw hashen en vergelijken.
2. Inbouwen. Registreren bewaart de hash. Inloggen maakt een sessie. De query filtert op de gebruiker. Een fout wachtwoord en een onbekende gebruiker krijgen dezelfde foutboodschap.
3. Rollen. Twee waarden in een kolom `rol`: `gebruiker` en `beheerder`. Leerlingen van de andere richting zijn gebruikers en zien alleen hun stations. De leerlingen van deze richting, en jij, zijn beheerders en zien alle stations. Dat is autorisatie: niet alleen wie je bent, maar wat je mag.

Een registratieformulier zet de rol altijd op `gebruiker`. De rol kiezen op dat formulier zou iedereen beheerder maken. De eerste beheerder komt uit een script of een SQL-opdracht bij het aanmaken van de database.

De les die ze moeten ervaren: een verborgen link is geen beveiliging. Een gebruiker die zelf `/beheer` intypt, krijgt status 403. Dezelfde weigering zit in de query voor een station dat niet van hem is. Daar hoort een pytest bij, met twee testaccounts.

Geen derde rol, geen rechtentabel, geen JWT en geen OAuth. In het project gebruiken we `bcrypt`, niet een zelf geschreven hash. De uitleg toont wel het principe.

De `.gitignore` bevat `.env` nu al, zodat die regel er staat voor er sleutels zijn.

## Cursus databases van je collega

Publiek: [Cursus Databases](https://stijnww.github.io/Cursus-Databases/). Zelfde soort MkDocs-site, inleidend niveau, tabellen en SQL. Praktijkcases is nog leeg. Overleg voor je leerlingen ernaar stuurt welke hoofdstukken bij ons project horen.

Nuttig als naslag, op het moment van het databasehoofdstuk, niet ervoor:

- [Inleiding](https://stijnww.github.io/Cursus-Databases/inleiding/), inclusief het korte onderscheid relationeel, NoSQL en tijdreeksen.
- [ER-diagrammen](https://stijnww.github.io/Cursus-Databases/er_diagrammen/) voor de woorden entiteit, relatie en één-op-veel.
- [SQL basis](https://stijnww.github.io/Cursus-Databases/sql_basis/) voor `SELECT`, `INSERT`, `UPDATE` en `DELETE`.
- [Joins](https://stijnww.github.io/Cursus-Databases/joins/) zodra een gebruiker zijn stations moet ophalen.

Normalisatie, indexen en transacties zijn verdieping. Die horen niet op het kritieke pad van het weerstation.

Ons hoofdstuk blijft nodig naast die cursus. Daar staan ons model (gebruiker, station, meting), de keuze voor SQL tegenover InfluxDB en MongoDB, en queries met parameters. Dat laatste staat bij de collega niet, en een webapp die SQL aan elkaar plakt is juist het risico. De oefening daar die `INSERT`s door Copilot laat schrijven, gebruiken we niet. Onze leerlingen schrijven die queries zelf.

De voorbeeldfoto op de startpagina is sfeer, en de SQL op die foto is slordig. Daar verwijzen we niet naar. Diagrammen uit die cursus, zoals de tabel en het ER-voorbeeld, zijn wél bruikbaar.

## Cursus bekijken

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
mkdocs serve
```

De site opent op `http://127.0.0.1:8000`. Publiceer pas als de eerste hoofdstukken in de klas zijn nagelezen.
