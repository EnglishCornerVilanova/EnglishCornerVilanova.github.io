#!/usr/bin/env python3
"""Extrae solo la bandera del logo (sin "English Corner" debajo) para la barra
de navegación y el pie, donde el nombre ya va escrito al lado.
Mide dónde empieza el bloque de texto (filas con muchos píxeles negros) y dónde
acaba la bandera (rojo/azul). En la franja en que se solapan solo conserva las
columnas a la izquierda del texto: ahí está la punta de la diagonal roja."""
import sys
from pathlib import Path
from PIL import Image

src = Path(sys.argv[1]); out = Path(sys.argv[2])
im = Image.open(src).convert('RGBA'); W, H = im.size; px = im.load()

def kind(p):
    r, g, b, a = p
    if a < 128: return None
    mx, mn = max(r, g, b), min(r, g, b)
    if (mx - mn) / 255 > 0.25: return 'f'
    if (0.299*r + 0.587*g + 0.114*b) / 255 < 0.35: return 't'
    return None

rows = []
for y in range(0, H, 2):
    f = t = 0
    for x in range(0, W, 2):
        k = kind(px[x, y]); f += k == 'f'; t += k == 't'
    rows.append((y, f, t))
text_top = next(y for y, f, t in rows if t > 60)
flag_bottom = max(y for y, f, t in rows if f > 3)
text_left = min(x for y in range(text_top, min(H, text_top + 200), 2)
                for x in range(0, W, 2) if kind(px[x, y]) == 't')
cut_x = text_left - 20                                   # margen antes de la "E"
for y in range(text_top - 4, H):
    for x in range(W):
        if y > flag_bottom + 6 or x >= cut_x:
            px[x, y] = (0, 0, 0, 0)
im = im.crop(im.getbbox())
im.save(out)
print(f"bandera: {im.size[0]}x{im.size[1]} (texto desde y={text_top}, punta hasta y={flag_bottom}, corte en x={cut_x})")
