# De site op een server

De computer op school draait de site alleen zolang jouw SSH-venster open is, en alleen voor wie dat adres in de klas bereikt. Een server is een computer die aan blijft en een adres heeft dat ook buiten school werkt.

De klas zet daar één site op. Niet één site per leerling. Twintig programma's kunnen niet samen poort `8000` op hetzelfde adres innemen. Eén map, één `weerstation.db`, één ingester, één website.

Je leerkracht geeft het adres en één account. Je meldt je aan met `ssh`, op dezelfde manier als op de schoolcomputer. Bestanden en `sudo` doet de leerkracht. Jij kijkt mee en controleert daarna of de site blijft antwoorden.

## Dezelfde code

Op de server staat dezelfde repository als op je laptop. De leerkracht kiest welke repository dat is en zorgt dat het account op de server die mag clonen. Een private repository heeft ook hier een token nodig, zoals in het vorige hoofdstuk.

SQLite blijft het bestand `weerstation.db`. De tabellen veranderen niet. Elke query in `database.py` blijft zoals je ze geschreven hebt. Een apart databaseprogramma zou dezelfde tabellen kunnen bewaren, maar dan moet elke query mee veranderen. Dat doen we niet.

De leerkracht maakt op de server, in de map van de repository, twee bestanden die niet in Git horen.

`broker.py`, gekopieerd met `scp`, met één andere id:

```python
MQTT_CLIENT_ID = "ingester-server"
```

Er draait één ingester voor deze database. Een tweede ingester met dezelfde id valt weg. Een tweede ingester met een andere id schrijft elke meting een tweede keer in hetzelfde bestand. Stop daarom de ingester op je laptop zodra deze server de metingen bewaart.

`.env` bevat de sessiesleutel. Op je laptop volstond `alleen-op-deze-laptop`. Op een server die anderen kunnen bereiken, niet. De leerkracht maakt de sleutel in de home-map, niet in de projectmap. Een bestand `secrets.py` in de projectmap zou de module `secrets` van Python verbergen.

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

De uitvoer komt in `.env`, zonder aanhalingstekens. `chmod 600` maakt het bestand alleen leesbaar voor dit account. `.env` staat al in `.gitignore`.

```text
WEERSTATION_SLEUTEL=plak-hier-de-hex
```

De virtuele omgeving wordt op de server gemaakt, zoals op de schoolcomputer: `python3 -m venv .venv`, `source .venv/bin/activate`, `python -m pip install -r requirements.txt`.

## Twee diensten

Een dienst is een programma dat de computer zelf start. Niemand hoeft aangemeld te blijven. Na een herstart komen de twee programma's terug. Er zijn er twee, omdat de site en de ingester twee programma's zijn.

De leerkracht zet deze bestanden op de server in `/etc/systemd/system/`. `GEBRUIKER` wordt overal de echte accountnaam. De sleutel staat niet in deze bestanden. Die leest de website uit `.env`.

`weerstation-web.service`:

```ini
[Unit]
Description=Weerstation website
After=network.target

[Service]
User=GEBRUIKER
WorkingDirectory=/home/GEBRUIKER/weerstation
EnvironmentFile=/home/GEBRUIKER/weerstation/.env
ExecStart=/home/GEBRUIKER/weerstation/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

`weerstation-ingester.service`:

```ini
[Unit]
Description=Weerstation ingester
After=network.target

[Service]
User=GEBRUIKER
WorkingDirectory=/home/GEBRUIKER/weerstation
ExecStart=/home/GEBRUIKER/weerstation/.venv/bin/python ingester.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

`--host 0.0.0.0` en poort `8000` maken de site bereikbaar op `http://adres:8000`. De leerkracht zet die poort open. HTTPS stellen we hier niet in.

De leerkracht start ze en laat ze terugkomen na een herstart:

```bash
sudo systemctl enable --now weerstation-web weerstation-ingester
```

Jij leest de toestand, zonder `sudo`:

```bash
systemctl status weerstation-web
systemctl status weerstation-ingester
```

Beide horen `active (running)` te tonen. Bij de ingester hoort in het log `MQTT verbonden` te staan.

## Nakijken buiten de sessie

Meld af met `exit`. Open op je telefoon, via mobiele data en niet via de wifi van school, `http://adres:8000`. Je ziet het aanmeldscherm. De SSH-vensters zijn dicht. De pagina antwoordt toch.

Meld je aan als beheerder. Vernieuw even later nog eens. Een meting die intussen binnenkwam, staat erbij. De ingester schrijft door terwijl niemand aangemeld is.

`POST /metingen` blijft open, zoals in de vorige hoofdstukken. De ingester is de weg waarlangs metingen binnenkomen. De pagina zelf blijft achter de login.

## Klaar als

- `systemctl status` toont de website en de ingester als `active (running)`.
- Na `exit` opent `http://adres:8000` nog het aanmeldscherm, ook buiten de schoolwifi.
- `.env` en `broker.py` staan niet op GitHub.
- Er draait één ingester voor deze database. De client-id op de server is `ingester-server`.

??? note "Als het niet lukt"

    **`systemctl status` toont `failed`.** Lees de laatste regels. Ontbreekt `.env` of `broker.py`, dan start de dienst niet. Een tikfout in het pad `/home/GEBRUIKER/weerstation` doet hetzelfde. De leerkracht verbetert het bestand en voert `sudo systemctl restart weerstation-web` of `weerstation-ingester` uit.

    **De status is `active`, de browser wacht eindeloos.** SSH bereikt de server wel. Poort `8000` is dan nog dicht op de server of bij de provider. Dat zet de leerkracht open. De pagina is `http://adres:8000`, niet `https://`.

    **De ingester is `active` en zegt `timed out`.** Het brokeradres in `broker.py` op de server klopt niet. Het is hetzelfde adres als op je laptop.

    **Elke meting staat er dubbel.** Er draait nog een ingester mee, op een laptop of op de schoolcomputer, met een andere client-id en dezelfde database. Stop die andere. Voor deze server hoort alleen `ingester-server` te schrijven.

    **`cannot import name 'token_hex'` bij het maken van de sleutel.** Je stond in de projectmap en daar ligt nog `secrets.py`. Ga naar de home-map en voer het commando daar uit. Hernoem dat bestand daarna naar `broker.py`, zoals in het MQTT-hoofdstuk.
