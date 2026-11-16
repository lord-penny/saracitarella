# Crea una pagina per ogni opera (opere/<nome>/index.html) e la sitemap,
# leggendo opere.json. Serve ai motori di ricerca: ogni quadro ha il suo
# indirizzo, titolo e descrizione. Si avvia da solo quando cambia opere.json.
import html
import json
import re
import shutil
import unicodedata
from urllib.parse import quote
from datetime import date
from pathlib import Path

SITO = 'https://saracitarella.it'
RADICE = Path(__file__).resolve().parents[2]
DATI = json.loads((RADICE / 'opere.json').read_text(encoding='utf-8'))
CARTELLA = RADICE / 'opere'
OGGI = date.today().isoformat()


def slug(t):
    t = unicodedata.normalize('NFD', str(t).lower())
    t = ''.join(c for c in t if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:60].strip('-')


def e(t):
    return html.escape(str(t or ''), quote=True)


def misure(o):
    if not o.get('larghezza') or not o.get('altezza'):
        return ''
    s = f"{o['larghezza']}×{o['altezza']}"
    if o.get('profondita'):
        s += f"×{o['profondita']}"
    return s + ' cm'


def prezzo(o):
    if o.get('disponibile') is False:
        return ''
    if not o.get('prezzo'):
        return 'Su richiesta'
    return '€ ' + f"{int(o['prezzo']):,}".replace(',', '.')


def web(src, lato):
    # versione leggera creata da versioni.py, se esiste
    p = Path(src)
    v = Path('immagini/web') / str(lato) / (p.stem + '.webp')
    return str(v) if src.startswith('immagini/opere/') and (RADICE / v).exists() else src


def ld_sicuro(dati):
    # JSON-LD dentro <script>: < > & diventano sequenze \u, così un titolo
    # scritto dal pannello non può mai chiudere il tag e iniettare codice
    return (json.dumps(dati, ensure_ascii=False)
            .replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026'))


def assoluto(src):
    return f"{SITO}/{src.lstrip('/')}" if src else ''


opere = [o for o in DATI.get('opere', []) if o and o.get('titolo') and o.get('pubblicata') is not False]
email = DATI.get('email_contatto') or ''

# Pagine vecchie di opere tolte: si cancellano
if CARTELLA.exists():
    shutil.rmtree(CARTELLA)
CARTELLA.mkdir()

tutte = [(slug(o['titolo']), o['titolo']) for o in opere]

voci = []
for o in opere:
    nome = slug(o['titolo'])
    vicine = ''.join(f'<li><a href="/opere/{n}/">{e(t)}</a></li>' for n, t in tutte if n != nome)
    url = f'{SITO}/opere/{nome}/'
    foto = [f for f in [o.get('immagine'), *(o.get('galleria') or [])] if f]
    tecnica = ', '.join(x for x in [o.get('tecnica'), (o.get('supporto') or '').lower() and 'su ' + o['supporto'].lower()] if x)
    venduta = o.get('disponibile') is False
    sommario = ' · '.join(x for x in [tecnica, misure(o), str(o.get('anno') or '')] if x)
    desc = (o.get('descrizione') or '').strip().replace('\n', ' ')
    meta = f"«{o['titolo']}», opera di Sara Citarella, pittrice contemporanea a Napoli. {sommario}."
    if desc:
        meta += ' ' + desc
    meta = meta[:300]

    righe = [('Tecnica', o.get('tecnica')), ('Supporto', o.get('supporto')), ('Misure', misure(o)),
             ('Anno', o.get('anno')), ('Stato', 'Venduta' if venduta else 'Disponibile'), ('Prezzo', prezzo(o))]
    dl = ''.join(f'<dt>{e(k)}</dt><dd>{e(v)}</dd>' for k, v in righe if v)
    paragrafi = ''.join(f'<p>{e(p)}</p>' for p in (o.get('descrizione') or '').split('\n') if p.strip())
    if email:
        oggetto = quote('Informazioni su «' + o['titolo'] + '»')
        cta = f'<a class="cta" href="mailto:{e(email)}?subject={oggetto}">Chiedi informazioni</a>'
    else:
        cta = '<a class="cta" href="https://www.instagram.com/saracitarella.art" target="_blank" rel="noopener">Chiedi informazioni<span class="sr"> (si apre in una nuova scheda)</span></a>'
    altre = ''.join(f'<img src="/{e(web(f, 480))}" alt="{e(o["titolo"])}, Sara Citarella: foto {i + 2}" loading="lazy">' for i, f in enumerate(foto[1:]))
    img = (f'<img src="/{e(web(foto[0], 1800))}" alt="{e(o["titolo"])}, {e(tecnica)}, Sara Citarella">' if foto else '')

    opera_ld = {
        '@context': 'https://schema.org',
        '@type': 'VisualArtwork',
        'name': o['titolo'],
        'url': url,
        'creator': {'@type': 'Person', 'name': 'Sara Citarella', 'url': SITO + '/'},
        'artform': 'Pittura',
    }
    if foto: opera_ld['image'] = [assoluto(f) for f in foto]
    if o.get('anno'): opera_ld['dateCreated'] = str(o['anno'])
    if o.get('tecnica'): opera_ld['artMedium'] = o['tecnica']
    if o.get('supporto'): opera_ld['artworkSurface'] = o['supporto']
    if o.get('larghezza'): opera_ld['width'] = {'@type': 'Distance', 'name': f"{o['larghezza']} cm"}
    if o.get('altezza'): opera_ld['height'] = {'@type': 'Distance', 'name': f"{o['altezza']} cm"}
    if desc: opera_ld['description'] = desc
    if not venduta and o.get('prezzo'):
        opera_ld['offers'] = {'@type': 'Offer', 'price': str(o['prezzo']), 'priceCurrency': 'EUR',
                              'availability': 'https://schema.org/InStock', 'url': url}

    pagina = f'''<!doctype html>
<html lang="it" style="--tela-colori: conic-gradient(#f7f6f2 0 25%, #1f3bff 0 50%, #ff1f3d 0 75%, #ffd60a 0)">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(o['titolo'])} · Sara Citarella, pittrice a Napoli</title>
<meta name="description" content="{e(meta)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#111111">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/immagini/icona-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="article">
<meta property="og:locale" content="it_IT">
<meta property="og:site_name" content="Sara Citarella">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{e(o['titolo'])} · Sara Citarella">
<meta property="og:description" content="{e(meta)}">
{f'<meta property="og:image" content="{e(assoluto(foto[0]))}">' if foto else ''}
<meta name="twitter:card" content="summary_large_image">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="stylesheet" href="/font/font.css?v={OGGI}">
<link rel="stylesheet" href="/style.css?v={OGGI}">
<script type="application/ld+json">{ld_sicuro(opera_ld)}</script>
</head>
<body class="pagina-opera">
<a class="salta" href="#contenuto">Salta al contenuto</a>
<nav class="barra visibile sheet-barra" aria-label="Menu">
  <a class="barra-logo" href="/" aria-label="Sara Citarella, vai alla home"><span><b class="dip">S</b>ara</span> <span><b class="dip">C</b>itarella</span></a>
  <a class="torna" href="/#opere">← <span class="lungo">Tutte le </span>opere</a>
</nav>
<main class="sheet" id="contenuto">
  <div class="sheet-media">
    <figure class="sheet-img">{img}</figure>
    {f'<div class="pagina-altre">{altre}</div>' if altre else ''}
  </div>
  <div class="sheet-info">
    <p class="kicker">Sara Citarella{' · ' + e(o.get('anno')) if o.get('anno') else ''}</p>
    <h1>{e(o['titolo'])}</h1>
    <dl>{dl}</dl>
    <div class="sheet-desc">{paragrafi}</div>
    {cta}
  </div>
</main>
<nav class="altre-opere wrap" aria-label="Altre opere">
  <h2>Altre opere</h2>
  <ul>{vicine}</ul>
</nav>
<footer class="foot wrap">
  <span>© Sara Citarella · <a href="/">saracitarella.it</a> · <a href="/privacy/">Privacy</a> · <a href="/accessibilita/">Accessibilità</a></span>
  <span class="firma">Made in Napoli with <span class="cuore" role="img" aria-label="love">♥</span> da <a href="https://morric.it" target="_blank" rel="noopener">Morric<span class="sr"> (si apre in una nuova scheda)</span></a></span>
</footer>
</body>
</html>
'''
    (CARTELLA / nome).mkdir(exist_ok=True)
    (CARTELLA / nome / 'index.html').write_text(pagina, encoding='utf-8')
    voci.append((url, foto, o['titolo']))

# Link alle pagine delle opere dentro la home (nella griglia, finché lo
# script non la disegna): così Google le trova anche senza la sitemap
casa = RADICE / 'index.html'
pagina_home = casa.read_text(encoding='utf-8')
link = ''.join(f'\n      <a class="msg wrap" href="opere/{n}/">{e(t)}</a>' for n, t in tutte)
pagina_home = re.sub(r'<!--opere-->.*?<!--/opere-->', lambda m: f'<!--opere-->{link}\n      <!--/opere-->', pagina_home, flags=re.S)
casa.write_text(pagina_home, encoding='utf-8')

# Sitemap con home, pagine delle opere e foto
def immagini(foto, titolo):
    return ''.join(f'\n    <image:image><image:loc>{e(assoluto(f))}</image:loc></image:image>' for f in foto)

home_foto = [x for x in [DATI.get('ritratto')] + [s.get('immagine') for s in DATI.get('studio') or [] if s] if x]
xml = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
       f'  <url>\n    <loc>{SITO}/</loc>\n    <lastmod>{OGGI}</lastmod>{immagini(home_foto, "Sara Citarella")}\n  </url>']
for url, foto, titolo in voci:
    xml.append(f'  <url>\n    <loc>{url}</loc>\n    <lastmod>{OGGI}</lastmod>{immagini(foto, titolo)}\n  </url>')
xml.append('</urlset>\n')
(RADICE / 'sitemap.xml').write_text('\n'.join(xml), encoding='utf-8')
print(f'{len(voci)} pagine di opere e sitemap aggiornate')
