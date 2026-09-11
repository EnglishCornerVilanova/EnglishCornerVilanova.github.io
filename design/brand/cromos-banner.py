#!/usr/bin/env python3
"""Cromos del hero: el banner en cuatro recortes que se solapan en contenido.
Cada cromo contiene sus elementos enteros (Londres y JOIN US · bandera, Tower
Bridge y palabras · título y chicos · cartel, chica tumbada y farola) y se coloca
en su posición real del banner, así que donde se superponen la imagen continúa.
Genera static/assets/photos/hero-1..4 y actualiza en site.css el bloque
"cromos", para que posiciones y recortes vayan siempre sincronizados.
Uso: design/brand/cromos-banner.py [banner.png]"""
import re, sys
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'design/brand/banner-definitivo.png'
OUT = ROOT / 'static/assets/photos'
CROMOS = [(0.000, 0.272), (0.252, 0.508), (0.426, 0.725), (0.645, 1.000)]   # fracciones del ancho
im = Image.open(SRC).convert('RGB'); W, H = im.size
for old in OUT.glob('hero-*'): old.unlink()
for i, (a, b) in enumerate(CROMOS, 1):
    p = im.crop((round(a * W), 0, round(b * W), H))
    h = min(H, 640); p = p.resize((round(p.width * h / p.height), h), Image.LANCZOS)
    p.save(OUT / f'hero-{i}.jpg', quality=84, optimize=True, progressive=True)
    p.save(OUT / f'hero-{i}.webp', quality=82, method=6)
    print(f"hero-{i}: {p.width}x{p.height}")
css = "/* cromos:inicio (generado por design/brand/cromos-banner.py) */\n"
css += "".join(f".hero-visual .frame-{i}{{left:{a*100:.2f}%;width:{(b-a)*100:.2f}%}}\n" for i, (a, b) in enumerate(CROMOS, 1))
css += f".hero-visual{{aspect-ratio:{W/H:.3f}/1.14}}\n/* cromos:fin */"
f = ROOT / 'static/assets/css/site.css'; s = f.read_text(encoding='utf-8')
s = re.sub(r'/\* cromos:inicio.*?/\* cromos:fin \*/', lambda m: css, s, flags=re.S) if 'cromos:inicio' in s else s + "\n" + css + "\n"
f.write_text(s, encoding='utf-8')
