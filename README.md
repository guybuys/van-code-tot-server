# Van code tot server

Cursus voor het zesde jaar. Leerlingen bouwen een echt softwaresysteem: van de editor op hun laptop tot een site die op een server blijft draaien.

Het project is een **weerstation**. Een ESP32 met MicroPython publiceert temperatuur en luchtvochtigheid. De site bewaart die metingen, toont ze in een tabel en een grafiek, en laat iemand inloggen. Een gewone gebruiker ziet alleen zijn eigen station. Een beheerder ziet alle stations.

De cursus volgt die weg in vaste stappen: VS Code, Git en GitHub, een API, HTML en CSS, een database, accounts en rollen, MQTT, en daarna de server. Het weerstation is het systeem dat ze onderweg maken. De stappen zelf zijn dezelfde voor een volgend project.

## Bekijken

De cursustekst staat in `docs/` en wordt een site met MkDocs.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
mkdocs serve
```

Op macOS en Linux activeer je de omgeving met `source .venv/bin/activate`. De site opent op `http://127.0.0.1:8000`.

Leerlingen werken niet in deze repository. Zij maken een eigen private repository met de naam `weerstation`.

## In deze repository

- `docs/` is de cursus.
- `voorbeelden/` bevat uitwerkingen om de stappen na te kijken. Leerlingen typen de code in hun eigen repository.
- `LERAAR.md` is de aanpak voor de leerkracht: volgorde, toetsen van de API, rollen, en de databasecursus die als naslag dient.
- `LEERDOELEN.md` koppelt de leerplandoelen aan de onderdelen. Een doel kan op meerdere plaatsen staan. Delen die nog geschreven worden, staan daar als onder constructie.

Het leerplan zit bewust niet in deze repository.
