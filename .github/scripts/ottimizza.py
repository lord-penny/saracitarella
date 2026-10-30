# Ridimensiona e comprime le foto appena caricate, senza cambiare nome né formato,
# così opere.json non va toccato. Il lato lungo resta al massimo 2400 px.
import sys
from pathlib import Path
from PIL import Image, ImageOps

LATO = 2400

for nome in sys.argv[1:]:
    p = Path(nome)
    if not p.is_file() or p.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
        continue
    prima = p.stat().st_size
    with Image.open(p) as img:
        icc = img.info.get('icc_profile')
        img = ImageOps.exif_transpose(img)
        if max(img.size) > LATO:
            img.thumbnail((LATO, LATO), Image.LANCZOS)
        tmp = p.with_name(p.stem + '.tmp' + p.suffix)
        fmt = p.suffix.lower()
        if fmt in {'.jpg', '.jpeg'}:
            img.convert('RGB').save(tmp, 'JPEG', quality=86, optimize=True, progressive=True, icc_profile=icc)
        elif fmt == '.webp':
            img.save(tmp, 'WEBP', quality=86, method=6, icc_profile=icc)
        else:
            img.save(tmp, 'PNG', optimize=True, icc_profile=icc)
    dopo = tmp.stat().st_size
    if dopo < prima:
        tmp.replace(p)
        print(f'{p}: {prima // 1024} KB -> {dopo // 1024} KB')
    else:
        tmp.unlink()
        print(f'{p}: già leggera, lasciata com\'era')
