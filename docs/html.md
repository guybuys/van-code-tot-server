# HTML

Je API antwoordt met JSON. Een bezoeker leest dat niet. Die ziet een pagina. HTML beschrijft de structuur van die pagina: een titel, een zin, een tabel. De vorm komt in het volgende hoofdstuk. De cijfers typ je zelf. FastAPI vult ze later in.

## De pagina

Maak `index.html` in de root van je repository, naast `main.py`.

```html
<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <title>Weerstation</title>
</head>
<body>
  <main>
    <h1>Weerstation</h1>
    <p>De laatste meting van je station.</p>
    <table>
      <thead>
        <tr>
          <th>Grootheid</th>
          <th>Waarde</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Temperatuur</td>
          <td>18,2 °C</td>
        </tr>
        <tr>
          <td>Luchtdruk</td>
          <td>1013,2 hPa</td>
        </tr>
      </tbody>
    </table>
  </main>
</body>
</html>
```

`<!DOCTYPE html>` zegt dat dit moderne HTML is. `lang="nl"` zegt dat de pagina in het Nederlands is. In `head` staat wat de browser nodig heeft en de bezoeker niet ziet. `charset` zorgt dat `°` goed verschijnt. `title` is de naam op het tabblad.

In `body` staat wat je ziet. `h1` is de titel van de pagina, `p` een zin. De meting is een tabel: twee kolommen, twee rijen. `th` is een kolomtitel, `td` een waarde. Op de pagina schrijf je `18,2` met een komma. In de JSON van je API staat `18.2` met een punt. Dat zijn twee manieren om hetzelfde getal te tonen.

## Openen

Bewaar het bestand. In de terminal van VS Code, in je repository:

```powershell
start index.html
```

De browser opent de pagina. Het adres begint met `file:///`. De browser leest dan het bestand op je laptop. Je API krijgt geen vraag. `main.py` mag dicht blijven.

De tabel oogt kaal. De browser kiest zelf het lettertype en de marges. Dat verandert in [CSS](css.md).

## Bewaren op GitHub

```powershell
git add index.html
git commit -m "Voeg een HTML-pagina met vaste metingen toe"
git push
```

## Klaar als

- `index.html` opent in de browser en het tabblad heet Weerstation.
- Je ziet de titel, de zin, en een tabel met 18,2 °C en 1013,2 hPa.
- `index.html` staat op GitHub.

??? note "Als het niet lukt"

    **Je ziet de tags als tekst, of de pagina is leeg.** Het bestand is niet bewaard, of het heet `index.html.txt`. In VS Code staat de naam op het tabblad. Bewaar opnieuw met `Ctrl+S` en controleer in de Verkenner of de naam op `.html` eindigt.

    **`°` wordt een vreemd teken.** De regel `<meta charset="utf-8">` ontbreekt of staat niet in `head`.

    **`start` wordt niet herkend.** De terminal staat niet in de map van je repository. Links in de titelbalk van VS Code zie je die map. Open `C:\dev\weerstation` als dat nog niet zo is.
