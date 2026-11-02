# Crea le versioni leggere (WebP) di ogni foto in immagini/opere:
#   immagini/web/480/<nome>.webp   miniature (studio, mostre, anteprime)
#   immagini/web/1000/<nome>.webp  griglia delle opere, telefoni
#   immagini/web/1800/<nome>.webp  scheda dell'opera e foto a tutto schermo
# Il sito usa queste versioni e, se una manca, ripiega sulla foto originale.
# Con dei file come argomenti li rifà sempre; senza argomenti crea solo quelle mancanti.
import sys
from pathlib import Path
from PIL import Image, ImageOps

RADICE = Path(__file__).resolve().parents[2]
ORIGINALI = RADICE / 'immagini' / 'opere'
WEB = RADICE / 'immagini' / 'web'
MISURE = {480: 70, 1000: 74, 1800: 76}  # lato lungo: qualità
TIPI = {'.jpg', '.jpeg', '.png', '.webp'}

nomi = [Path(a) for a in sys.argv[1:]] or sorted(ORIGINALI.iterdir())
fatte = 0
for p in nomi:
    p = p if p.is_absolute() else RADICE / p
    if p.parent.resolve() != ORIGINALI.resolve() or p.suffix.lower() not in TIPI or not p.is_file():
        continue
    destinazioni = {lato: WEB / str(lato) / (p.stem + '.webp') for lato in MISURE}
    if not sys.argv[1:] and all(d.exists() for d in destinazioni.values()):
        continue
    with Image.open(p) as img:
        img = ImageOps.exif_transpose(img).convert('RGB')
        for lato, q in MISURE.items():
            v = img.copy()
            if max(v.size) > lato:
                v.thumbnail((lato, lato), Image.LANCZOS)
            destinazioni[lato].parent.mkdir(parents=True, exist_ok=True)
            v.save(destinazioni[lato], 'WEBP', quality=q, method=6)
    fatte += 1
    print(p.name, ' '.join(f'{l}:{destinazioni[l].stat().st_size // 1024}KB' for l in MISURE))

# versioni di foto che non esistono più
for d in WEB.glob('*/*.webp'):
    if not any((ORIGINALI / (d.stem + e)).exists() for e in TIPI):
        d.unlink()
        print('tolta', d.relative_to(RADICE))
print(f'{fatte} foto elaborate')
