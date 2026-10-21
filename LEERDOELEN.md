# Leerplandoelen in deze cursus

Overzicht voor de leerkracht. Dit bestand staat niet op de cursussite. Het leerplan zelf zit niet in de repository.

De nummers zijn de leerplandoelen uit Informatica- en communicatiewetenschappen, derde graad, versie oktober 2024. Een doel kan in meerdere onderdelen terugkomen. **Klaar** betekent dat het hoofdstuk geschreven is. **Onder constructie** betekent dat het onderdeel gepland is en het doel daar bewust een plaats krijgt.

Deze cursus is niet de enige plaats waar een doel aan bod komt. Algoritmiek, numerieke methodes, computersystemen en netwerken zitten hier niet in. Die zijn in de rest van de graad al aan de orde geweest.

## Per onderdeel

| Onderdeel | Stand | Doelen |
|---|---|---|
| Introductie | klaar | Geen doel. De pagina schetst het weerstation. |
| VS Code | klaar | Geen doel. Zonder editor en terminal starten de andere delen niet. |
| Git en GitHub | klaar | LPD 8, het stuk versiebeheer en samenwerken. |
| Een eerste API | klaar | LPD 1, 4, 9, 11, 12 en 13. LPD 14 alleen als fouten lezen. |
| HTML | onder constructie | LPD 10, de structuur van de pagina. |
| CSS | onder constructie | LPD 10, de vorm. Responsive blijft een uitbreiding. |
| De pagina uit FastAPI | onder constructie | LPD 7, 10 en 11. De presentatielaag wordt de HTML-pagina. |
| Databases | onder constructie | LPD 4, 6, 7 en 12. Ontwerp van gebruiker, station en meting, daarna SQL. |
| Metingen op de pagina | onder constructie | LPD 9, 10 en 11. Eerst een tabel, daarna een grafiek. |
| Wachtwoorden, login en rollen | onder constructie | LPD 8, 9 en 13. Hash, sessie, en het verschil tussen gebruiker en beheerder. |
| MQTT | onder constructie | LPD 4, 7 en 11. Een apart programma schrijft metingen in de database. |
| SSH en de computer op school | onder constructie | Geen extra leerplandoel. Nodig om het systeem van de laptop los te maken. |
| De site op een server | onder constructie | Geen extra leerplandoel. Zelfde systeem, nu bereikbaar buiten de klas. |

## Per leerplandoel

### LPD 1. Een gestructureerde programmeertaal, met softwarebibliotheken

Python, en bibliotheken in plaats van alles zelf te schrijven.

- Een eerste API (klaar): FastAPI, uvicorn en pydantic.

### LPD 4. Externe gegevens in- en uitvoeren

JSON, een database, en later berichten van het weerstation. Niet elk bestandsformaat uit de wenk moet aan bod komen.

- Een eerste API (klaar): JSON ontvangen en teruggeven.
- Databases (onder constructie): metingen blijven bewaard.
- MQTT (onder constructie): het station stuurt metingen binnen.

### LPD 6. Ontwerp van een softwaremodule, objectgeoriënteerd

Een klein ontwerp vóór de tabellen: welke gegevens bij gebruiker, station en meting horen, en welke verantwoordelijkheid elke module heeft. Een klassendiagram op papier volstaat.

- Databases (onder constructie).

### LPD 7. Modulair ontwerp met een 3-lagenarchitectuur

Presentatie, domein en data blijven uit elkaar. Lage koppeling: de pagina werkt zonder broker, de ingester werkt zonder de pagina.

- De pagina uit FastAPI (onder constructie): presentatielaag.
- Databases (onder constructie): datalaag, en het domein dat beslist wat een geldige meting is.
- MQTT (onder constructie): de ingester is een tweede programma, geen code in de webroute.

### LPD 8. Herbruikbare modules, en samenwerking

Het doel gaat over modules die iemand anders kan lezen en verder gebruiken. Versiebeheer staat in de wenk bij dit doel.

- Git en GitHub (klaar): commits, een gedeelde repository, niets van `.venv` of `.env` op GitHub.
- Wachtwoorden, login en rollen (onder constructie): de controle "van wie is dit station?" zit in één module, die de pagina en de tests allebei gebruiken.

### LPD 9. Gebruiksvriendelijkheid

Validatie, een begrijpelijke fout, en een interface die een fout voorkomt in plaats van te crashen.

- Een eerste API (klaar): een meting zonder luchtvochtigheid krijgt status 422. Het programma blijft draaien.
- Metingen op de pagina (onder constructie): een lege periode of een ontbrekend station krijgt een leesbare boodschap, geen lege grafiek zonder uitleg.
- Wachtwoorden, login en rollen (onder constructie): een fout wachtwoord en een onbekende gebruiker krijgen dezelfde boodschap. Een gebruiker ziet geen stations van iemand anders.

### LPD 10. Een webinterface met hedendaagse webtechnologie

HTML voor de structuur, CSS voor de vorm. Responsive is een wenk, geen minimumeis.

- HTML (onder constructie).
- CSS (onder constructie).
- De pagina uit FastAPI (onder constructie): dezelfde pagina, nu door het programma geleverd.
- Metingen op de pagina (onder constructie): tabel en grafiek.

### LPD 11. Client-side of server-side scripts bij een modulair ontwerp

Het doel vraagt één van beide. Deze cursus doet server-side als basis. Het stuk JavaScript voor de grafiek is extra, en dekt de client-side kant.

- Een eerste API (klaar): server-side routes.
- De pagina uit FastAPI (onder constructie): de server bouwt de HTML.
- Metingen op de pagina (onder constructie): een script in de browser tekent de grafiek.
- MQTT (onder constructie): server-side ingester.

### LPD 12. Hulpbronnen gebruiken, en documentatie bij eigen modules

Twee kanten. Hulpbronnen zijn al deels aanwezig. Documentatie bij de eigen modules nog niet.

- Een eerste API (klaar): `/docs` en de foutmeldingen van de bibliotheek. De leerlingen schrijven nog geen documentatie bij een eigen module.
- Databases (onder constructie): de databasecursus van je collega als naslag, en een korte beschrijving bij het eigen ontwerp van de drie modules.

### LPD 13. Eigen implementaties testen

Fouten vinden in het eigen programma: een geslaagd geval en een geval dat geweigerd moet worden.

- Een eerste API (klaar): pytest met een geldige meting en een onvolledige meting.
- Wachtwoorden, login en rollen (onder constructie): een beheerder ziet alle stations, een gebruiker krijgt 403 op `/beheer` en op het station van iemand anders.

### LPD 14. Debuggen

De bron van een fout opzoeken. De wenk noemt onder meer stap voor stap gaan en breakpoints.

- Een eerste API (klaar, gedeeltelijk): een mislukte pytest toont welke waarde verschilde, en de terminal toont waarom de server niet start. Breakpoints zitten in dit hoofdstuk niet.
- Geen apart hoofdstuk gepland. Als de klas daar tijd voor heeft, hoort een breakpoint bij een fout in de eigen datalaag, niet bij een nieuw theoretisch deel.

## Doelen die deze cursus niet afvinkt

LPD 2, 3 en 5 blijven bij algoritmiek en numerieke methodes. LPD 15 tot en met 20 en LPD 22 blijven bij computersystemen en netwerken.

LPD 21, encryptie in een netwerk, wordt niet afgevinkt omdat een wachtwoord gehasht wordt. Hashen hoort bij login en LPD 9. Het is geen netwerkencryptie. HTTPS op de server later evenmin, zolang de leerlingen die stap niet zelf onderzoeken.
