# SSH en de computer op school

De site draait tot nu toe op je laptop. Sluit je die, dan is de pagina weg. Op school staat een andere computer. Die blijft in de klas staan. Met SSH open je een terminal op die computer, vanuit je eigen laptop.

SSH is geen website en geen bureaublad op afstand. Je typt commando's. Het antwoord komt van de andere computer. De verbinding is versleuteld. Je ziet de bestanden van die computer, niet die van je laptop.

Je leerkracht geeft in de les vier gegevens. Die staan bewust niet in deze tekst.

- het adres
- de gebruikersnaam
- het wachtwoord
- een poort, voor jou alleen

De poort is een getal zoals `8014`. Elke leerling krijgt een ander getal. Op één computer kan maar één programma luisteren op poort `8000`.

## Verbinden

Op je laptop, in PowerShell:

```powershell
ssh
```

Zie je een uitleg over het gebruik, dan staat de SSH-client erop. Zie je dat het commando niet bestaat, installeer dan in Windows onder **Instellingen → Apps → Optionele onderdelen** de **OpenSSH-client**. Sluit de terminal en open ze opnieuw.

Verbind. Vul het adres en de gebruikersnaam van je leerkracht in.

```powershell
ssh gebruiker@adres
```

De eerste keer vraagt de computer of je de vingerafdruk vertrouwt. Typ `yes` en druk op Enter. Dat antwoord wordt onthouden.

Daarna vraagt ze het wachtwoord. Je ziet geen tekens terwijl je typt, ook geen bolletjes. Dat hoort zo. Enter bevestigt.

De prompt verandert. Je bent niet meer op je laptop. Controleer dat:

```bash
whoami
pwd
ls
python3 --version
```

`whoami` toont de gebruikersnaam van de schoolcomputer. `pwd` toont een pad zoals `/home/gebruiker`, niet `C:\dev`. `python3 --version` moet 3.10 of hoger zijn. Het commando heet hier `python3`. `python` alleen bestaat op deze computer vaak niet.

`exit` verbreekt de verbinding. Je bent terug op je laptop. De bestanden op de schoolcomputer blijven daar. De bestanden op je laptop staan niet op de schoolcomputer, tot je ze daar zelf naartoe haalt.

## De repository op de schoolcomputer

Verbind opnieuw met `ssh`. Clone je private repository. De map op de schoolcomputer mag je home-map zijn. OneDrive speelt hier geen rol.

```bash
git clone https://github.com/jouw-naam/weerstation.git
cd weerstation
```

GitHub aanvaardt in deze terminal je gewone accountwachtwoord niet. Het wachtwoord dat `git` vraagt, is een token.

1. Open op je laptop [github.com](https://github.com) → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
2. Kies alleen de repository `weerstation`. Zet bij **Contents** de toegang op **Read-only**.
3. Kies een vervaldatum van hooguit 30 dagen. Maak de token aan.
4. GitHub toont de token één keer. Kopieer hem.
5. In de SSH-terminal is de username je GitHub-naam. Plak de token als wachtwoord. De terminal toont niets terwijl je plakt.

De token hoort nergens in een bestand van de repository.

Maak de virtuele omgeving op deze computer. Die van je laptop komt niet mee met Git, en een Windows-omgeving zou hier toch niet werken.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

De prompt begint daarna met `(.venv)`, net als op je laptop. Activeren heet hier `source .venv/bin/activate`, niet `Activate.ps1`.

## broker.py staat niet op GitHub

`broker.py` komt niet mee met `git clone`. Dat is de bedoeling. Je kopieert dat ene bestand van je laptop naar de schoolcomputer.

Laat de SSH-verbinding open. Open op je laptop een tweede terminal, buiten SSH, in een map die niet uitmaakt:

```powershell
scp C:\dev\weerstation\broker.py gebruiker@adres:weerstation/broker.py
```

`scp` vraagt hetzelfde wachtwoord als `ssh`. Het bestand belandt in de repository op de schoolcomputer en gaat niet naar GitHub.

In de SSH-terminal, in de map `weerstation`, wijzig in `broker.py` de regel `MQTT_CLIENT_ID`. Zet er je naam in, bijvoorbeeld `ingester-jan`. Twee ingesters met dezelfde id schoppen elkaar van de broker. De waarde op je laptop laat je met rust.

Nano opent het bestand in de terminal. Bewaar met `Ctrl+O` en Enter. Sluit met `Ctrl+X`.

```bash
nano broker.py
```

## Twee programma's, twee verbindingen

Stop op je laptop uvicorn en de ingester met `Ctrl+C`, als die nog draaien. Anders weet je straks niet welke computer de pagina maakt.

Je hebt twee SSH-terminals nodig. De tweede is een nieuwe `ssh gebruiker@adres` vanuit een nieuw venster op je laptop. Activeer in beide de omgeving:

```bash
cd weerstation
source .venv/bin/activate
```

In het eerste venster start je de site. Vervang `8014` door de poort die je kreeg. `--host 0.0.0.0` laat andere computers in de klas verbinden. Op je laptop volstond `127.0.0.1`, omdat de browser op dezelfde machine stond. `--reload` gebruik je hier niet.

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8014
```

In het tweede venster:

```bash
python ingester.py
```

Je hoort `MQTT verbonden` te zien, en daarna de retained info-berichten. Elke leerling heeft een eigen map en een eigen `weerstation.db`. Jouw ingester schrijft alleen in jouw bestand.

Open op je laptop een browser op `http://adres:8014`, met het adres en de poort van de schoolcomputer. Niet `127.0.0.1`. Meld je aan. De pagina komt van de schoolcomputer. Je laptop draait geen uvicorn.

## Wat er stopt

`Ctrl+C` in een SSH-venster stopt het programma in dat venster. Je blijft aangemeld. `exit`, of het venster sluiten, stopt het programma ook. De bestanden en `weerstation.db` blijven staan. Meld je later opnieuw aan, dan staan de rijen er nog, maar de pagina antwoordt pas als je uvicorn opnieuw start.

Dat is de grens van dit hoofdstuk. De computer op school kan de site draaien, maar alleen zolang jouw sessie open blijft. In het volgende hoofdstuk blijft één site draaien zonder dat er iemand aangemeld is.

## Klaar als

- `ssh` opent een terminal op de schoolcomputer, en `exit` brengt je terug naar je laptop.
- De browser opent de site via het adres en de poort van de schoolcomputer, terwijl je laptop geen uvicorn draait.
- `broker.py` staat op je laptop en op de schoolcomputer, en niet op GitHub.
- Na het sluiten van de SSH-vensters antwoordt de pagina niet meer. Na een nieuwe aanmelding staan de bestanden er nog.

??? note "Als het niet lukt"

    **`ssh` wordt niet herkend.** De OpenSSH-client ontbreekt in Windows. Installeer het optionele onderdeel en open de terminal opnieuw.

    **`Connection timed out`.** Het adres klopt niet, of deze laptop zit niet op het netwerk dat de schoolcomputer bereikt. Vergelijk het adres met wat de leerkracht gaf.

    **`Permission denied`.** Gebruikersnaam of wachtwoord klopt niet. Het wachtwoord verschijnt niet terwijl je typt. Typ het opnieuw.

    **`python3: command not found`.** Zeg het tegen je leerkracht. Python hoort op de schoolcomputer te staan. Installeer hem niet zelf met `sudo`.

    **`Authentication failed` bij `git clone`.** GitHub weigert je accountwachtwoord. Gebruik een fine-grained token als wachtwoord, met leestoegang tot `weerstation`.

    **`Address already in use`.** Jouw poort is bezet. Vraag een ander getal. Start uvicorn opnieuw met die poort.

    **SSH werkt, de browser niet.** In het uvicorn-commando moet `--host 0.0.0.0` staan. `127.0.0.1` antwoordt alleen op de schoolcomputer zelf. Klopt het commando wel, dan blokkeert het netwerk de poort. Zeg het tegen je leerkracht.

    **De ingester eindigt op `timed out`.** In `broker.py` op de schoolcomputer staat een ander brokeradres dan op je laptop. `scp` kopieert het werkende bestand. Pas daarna alleen `MQTT_CLIENT_ID` aan.

    **De ingester verbindt en valt meteen weg.** `MQTT_CLIENT_ID` is niet uniek. Zet je eigen naam erin en start `python ingester.py` opnieuw.
