# Sito di Sara Citarella

Sito statico, pubblicato con GitHub Pages. Niente database e niente installazioni: opere, biografia, ritratto ed email stanno in `opere.json`, le foto in `immagini/opere/`.

Le opere si aggiungono dal pannello Pages CMS (app.pagescms.org), anche da telefono.

```
index.html        la pagina
style.css         l'aspetto
app.js            legge opere.json, dispone la griglia e dipinge le iniziali del logo
opere.json        opere e testi del sito (si modifica dal pannello)
immagini/opere/   foto delle opere e ritratto
.pages.yml        configurazione del pannello Pages CMS (app.pagescms.org)
```

## Cosa sapere

- Le opere sono ordinate dalla più recente. Il numero di catalogo (01, 02…) parte dalla più vecchia.
- Senza foto, un'opera compare come riquadro grigio "Foto in arrivo", nelle sue proporzioni reali.
- `disponibile: false` mostra "Venduta" e nasconde il prezzo. Senza `prezzo` il prezzo non compare.
- Per nascondere un'opera senza cancellarla: `"pubblicata": false` in `opere.json`.
- Se `email_contatto` è compilata, compare nei contatti e il pulsante "Chiedi informazioni" apre una mail. Altrimenti porta a Instagram.
- Ogni opera ha un link diretto da condividere, per esempio `saracitarella.it/#opera-comfort-zone`.
- Le foto caricate vengono ottimizzate da sole (lato lungo massimo 2400 px, stesso nome e formato) da `.github/workflows/foto.yml`. Si possono caricare gli originali.

## Da completare

- Foto originali delle opere e ritratto, dal pannello.
- Descrizioni: quelle attuali vengono da Gigarte e alcune sono parziali.
- Email di contatto.

## SEO
- `index.html`: titolo, descrizione, Open Graph, dati strutturati (Person, WebSite), favicon.
- `opere/<nome>/`: una pagina per opera con il proprio indirizzo, generata da `.github/scripts/pagine.py` insieme a `sitemap.xml`. La GitHub Action "Pagine delle opere" le rigenera da sola quando cambia `opere.json`: non vanno modificate a mano.
- `immagini/web/{480,1000,1800}/`: versioni WebP leggere delle foto, create da `.github/scripts/versioni.py` (Action "Ottimizza foto"). Il sito le usa e ripiega sull originale se mancano.
- Dopo una modifica a `style.css` o `app.js`, aggiornare il numero `?v=` in `index.html`.
- Font ospitati in `font/` (niente Google Fonts, per il GDPR). Pagina `privacy/`. Content-Security-Policy nel `<head>` di ogni pagina: se si aggiunge un servizio esterno va aggiornata.
