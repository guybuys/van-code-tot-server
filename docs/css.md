# CSS

De pagina uit het vorige hoofdstuk heeft een structuur. Het lettertype, de marges en de tabel kiest de browser. CSS is een tweede bestand dat zegt hoe die structuur eruitziet. De cijfers blijven dezelfde.

## Het bestand koppelen

Maak `style.css` naast `index.html`. Zet in `index.html`, onder de regel met `title`, deze regel:

```html
<link rel="stylesheet" href="style.css">
```

`href` is het pad naar het CSS-bestand. Omdat het naast `index.html` staat, volstaat de bestandsnaam. Zonder deze regel leest de browser je CSS niet.

## De regels

Een CSS-regel heeft een kiezer en een blok met eigenschappen. De kiezer `main` raakt het element `<main>`. `background` is de eigenschap, `white` de waarde.

```css
main {
  background: white;
}
```

Zet dit in `style.css`:

```css
body {
  margin: 0;
  font-family: system-ui, sans-serif;
  background: #e7ecf2;
  color: #1c2430;
}

main {
  box-sizing: border-box;
  max-width: 40rem;
  margin: 2rem auto;
  padding: 1.5rem 2rem 2rem;
  background: white;
}

h1 {
  margin-top: 0;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 0.6rem 0.8rem;
  text-align: left;
  border-bottom: 1px solid #d5dde6;
}

th {
  color: #526070;
  font-weight: 600;
}
```

`body` geldt voor de hele pagina. `margin: 0` haalt de standaardrand van de browser weg. `system-ui` is het lettertype van de laptop. `#e7ecf2` en `#1c2430` zijn kleuren, geschreven als hexadecimaal getal.

`main` wordt een witte kolom. `max-width: 40rem` beperkt de breedte. `box-sizing: border-box` telt de `padding` daarbij, zodat de kolom in het venster blijft. `margin: 2rem auto` zet de kolom in het midden. `padding` is de ruimte binnen de witte kolom.

`border-collapse: collapse` trekt de tabelranden aan elkaar. Elke cel krijgt ruimte en een lijn eronder. De kolomtitels zijn iets donkerder grijs dan de waarden.

Bewaar `index.html` en `style.css`. Vernieuw de pagina in de browser. Blijft het oude beeld staan, druk dan `Ctrl+F5`.

## Bewaren op GitHub

```powershell
git add index.html style.css
git commit -m "Geef de pagina een leesbare vorm"
git push
```

## Klaar als

- `index.html` verwijst naar `style.css`, en beide bestanden staan naast elkaar.
- De pagina toont een witte kolom op een grijze achtergrond.
- De tabel heeft ruimte in de cellen en een lijn tussen de rijen.
- `index.html` en `style.css` staan op GitHub.

??? note "Als het niet lukt"

    **Er verandert niets.** De `link`-regel ontbreekt, `href` wijst naar een andere naam, of `style.css` is niet bewaard. Open `index.html` in de browser, niet `style.css`. Daarna `Ctrl+F5`.

    **De browser toont de CSS als tekst.** Je hebt `style.css` geopend. Ga terug naar `index.html`.

    **Alleen een deel ziet er anders uit.** De kiezer moet overeenkomen met de tag in de HTML. `main`, `table`, `th` en `td` zijn de namen uit het vorige hoofdstuk.
