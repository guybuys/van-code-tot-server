# Git en GitHub

Git bewaart momentopnames van je project. Zo'n momentopname heet een **commit**. GitHub bewaart die commits online, zodat je leerkracht je werk kan openen en jij niets kwijt bent als je laptop stuk gaat.

Je maakt één private repository voor de hele site. Die deel je met je leerkracht.

## Git installeren

Typ in de terminal van VS Code:

```powershell
git --version
```

Zie je een versienummer, dan staat Git erop. Zie je een fout dat het commando niet bestaat, installeer dan [Git for Windows](https://git-scm.com/download/win). De standaardkeuzes zijn goed. Als het installatieprogramma een editor vraagt, kies dan VS Code. Sluit VS Code daarna volledig en open het opnieuw, anders kent de terminal `git` nog niet.

Koppel Git eenmalig aan je naam. Gebruik het e-mailadres van je GitHub-account. Die maak je in de volgende stap als je er nog geen hebt.

```powershell
git config --global user.name "Voornaam Achternaam"
git config --global user.email "jouw-email@voorbeeld.com"
```

## Een repository op GitHub

1. Maak een account op [github.com](https://github.com) als je dat nog niet hebt. Gebruik een e-mailadres dat je kan openen. GitHub stuurt een bevestiging.
2. Klik op **New repository**.
3. Noem de repository `weerstation`.
4. Zet ze op **Private**.
5. Vink **Add a README file** aan.
6. Maak ze aan.

Een private repository is zichtbaar voor jou en voor de mensen die jij toevoegt. Je leerkracht ziet ze pas nadat jij de uitnodiging verstuurt en je leerkracht ze aanvaardt.

## Delen met je leerkracht

1. Open de repository op GitHub.
2. Ga naar **Settings → Collaborators** (onder Access).
3. Klik **Add people**.
4. Vul de GitHub-naam in die je leerkracht opgeeft.
5. Verstuur de uitnodiging.
6. Zeg het in de les zodra de uitnodiging weg is. Zonder aanvaarding blijft de repository voor je leerkracht dicht.

## Clonen

Clonen maakt een lokale kopie. Doe dat buiten OneDrive.

Maak de map `C:\dev` via de Verkenner. Mappen die OneDrive synchroniseert, vaak Bureaublad en Documenten, zorgen voor vergrendelde bestanden en conflicten in Git.

Kopieer op de GitHub-pagina van je repository de HTTPS-link. Die ziet eruit als `https://github.com/jouw-naam/weerstation.git`.

Open in VS Code een terminal en typ, met jouw link:

```powershell
cd C:\dev
git clone https://github.com/jouw-naam/weerstation.git
```

Er verschijnt een aanmeldvenster van GitHub. Meld je aan in de browser en kom terug naar VS Code.

Open daarna de map `C:\dev\weerstation` in VS Code via **File → Open Folder**. Alle volgende hoofdstukken gebeuren in deze map. De terminal opent dan al op de juiste plaats.

## De README

Open `README.md` en vervang de inhoud door:

```markdown
# Weerstation

- Naam: jouw naam
- Klas: jouw klas
```

Bewaar het bestand.

## .gitignore

Sommige bestanden horen niet op GitHub: de virtuele Python-omgeving, tijdelijke cache, en later wachtwoorden. Maak in de root van de repository een bestand `.gitignore` met deze inhoud:

```text
.venv/
__pycache__/
.env
```

Het bestand `.env` bestaat nog niet. De regel staat er al zodat wachtwoorden en sleutels later niet per ongeluk meegaan.

## Commit en push

Een commit bewaart een momentopname op je laptop. Een push stuurt de commits die GitHub nog niet heeft.

Kijk eerst wat er veranderd is:

```powershell
git status
```

Je ziet `README.md` en `.gitignore`. Daarna:

```powershell
git add README.md .gitignore
git commit -m "Zet naam en gitignore in de repository"
git push
```

Vernieuw de pagina van je repository op GitHub. Je naam en klas staan in de README.

In de zijbalk van VS Code, onder het vertakkingsicoon **Source Control**, zie je dezelfde wijzigingen. De commando's hierboven zijn de manier die we in de cursus gebruiken. Het paneel is handig om te controleren of je niets vergeten bent.

## Klaar als

- De repository `weerstation` staat op GitHub en is private.
- Je leerkracht is uitgenodigd als collaborator.
- Op GitHub tonen `README.md` je naam en klas, en `.gitignore` de drie regels hierboven.
- De map `C:\dev\weerstation` is de map die in VS Code openstaat.

??? note "Als het niet lukt"

    **`git` wordt niet herkend.** Sluit VS Code volledig na de installatie van Git en open daarna de map opnieuw.

    **`git push` vraagt een wachtwoord en weigert het daarna.** GitHub aanvaardt het wachtwoord van de website niet in de terminal. Gebruik het aanmeldvenster dat Git for Windows opent. Blijft dat venster weg, start dan `git push` opnieuw vanuit de map `C:\dev\weerstation`.

    **De leerkracht opent de link en ziet niets.** De repository is private en de uitnodiging is nog niet aanvaard, of de uitnodiging is naar een andere GitHub-naam gegaan.

    **Bestanden in OneDrive tonen conflict-kopieën.** Clone opnieuw naar `C:\dev`. Werk niet verder in de gesynchroniseerde map.
