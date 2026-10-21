# VS Code

VS Code is de editor voor deze cursus. Daarin schrijf je de code, open je de terminal en start je het programma.

De website gebruikt Python op je laptop. Dat is de gewone Python, niet MicroPython.

## VS Code installeren

Controleer of VS Code al geïnstalleerd is. Zoek in het startmenu naar **Visual Studio Code**.

Staat het er niet, installeer het dan van [code.visualstudio.com](https://code.visualstudio.com). In het installatievenster mag je de standaardkeuzes laten staan. Vink **Open with Code** aan als je die optie ziet: dan kan je later met de rechtermuisknop een map in VS Code openen.

Visual Studio Code en Visual Studio zijn twee verschillende programma's. Je gebruikt Visual Studio Code.

## De Python-extensie

1. Open VS Code.
2. Open de extensies via het icoon links, of met `Ctrl+Shift+X`.
3. Zoek `Python`.
4. Installeer de extensie van Microsoft, de uitgever heet `ms-python`.

Die extensie laat VS Code zien welke Python je gebruikt. Fouten in je code verschijnen dan terwijl je typt.

## Python controleren

Open de terminal in VS Code via **Terminal → New Terminal**, of met `` Ctrl+` ``.

Het vervolgmenu naast de `+` in het terminalpaneel laat je een tweede terminal openen. Die heb je later nodig: één terminal houdt het programma draaiende, in de andere typ je commando's.

Typ:

```powershell
python --version
```

Je hebt Python 3.10 of hoger nodig. Zie je een versie zoals `Python 3.12.4`, dan is dit hoofdstuk voor jou klaar zodra de extensie geïnstalleerd is.

??? note "Er gebeurt niets, of de Microsoft Store opent"

    Windows heeft soms een aliassen die `python` naar de Store stuurt, ook als Python voor de lessen al geïnstalleerd is.

    1. Installeer Python van [python.org/downloads](https://www.python.org/downloads/) als `py --version` ook geen versie toont. Zet tijdens de installatie **Add python.exe to PATH** aan.
    2. Zoek in de Windows-instellingen naar **Manage app execution aliases**.
    3. Zet de aliassen `python.exe` en `python3.exe` uit.
    4. Sluit VS Code volledig en open het opnieuw.
    5. Typ opnieuw `python --version`.

    Werkt `python` niet en `py` wel, gebruik dan in de rest van de cursus `py` waar `python` staat. Voorbeeld: `py --version`.

## Een map openen

VS Code werkt per map. **File → Open Folder** opent de map van je project. Dat wordt de repository uit het volgende hoofdstuk. Maak die map nog niet met de hand aan: GitHub doet dat bij het clonen.

## Klaar als

- VS Code start.
- De extensie Python van Microsoft is geïnstalleerd.
- In de terminal van VS Code toont `python --version` Python 3.10 of hoger.
