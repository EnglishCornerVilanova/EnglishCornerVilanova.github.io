#!/usr/bin/env python3
"""Marca redonda de la barra: un recorte circular de la escena de Londres del
banner definitivo, con los pájaros borrados y cielo añadido por arriba para que
la aguja del Big Ben no toque el borde.

    python3 design/brand/generar-marca.py

Escribe static/assets/img/marca-{64,128,192}.{png,webp} y el maestro en
design/brand/marca-master.png."""
from pathlib import Path
from PIL import Image, ImageDraw
import subprocess, shutil

RAIZ = Path(__file__).resolve().parents[2]
BANNER = RAIZ / 'design/brand/banner-definitivo.png'
SALIDA = RAIZ / 'static/assets/img'
ESCENA = 0.272            # el primer cromo del banner
PAJAROS = [((255, 10, 435, 118), (255, 255, 255)),   # bandada sobre la nube
           ((34, 158, 88, 195), (168, 221, 246))]    # gaviota sobre el cielo
CIELO = 100               # filas de cielo añadidas por arriba
CENTRO, RADIO = (230, 295), 205
TAMANOS = (64, 128, 192)


def borrar(im, caja, fondo, umbral=12):
    x0, y0, x1, y1 = caja
    px = im.load()
    for x in range(x0, x1):
        for y in range(y0, y1):
            if max(abs(px[x, y][i] - fondo[i]) for i in range(3)) > umbral:
                px[x, y] = fondo


def main():
    banner = Image.open(BANNER).convert('RGB')
    escena = banner.crop((0, 0, int(banner.width * ESCENA), banner.height))
    for caja, fondo in PAJAROS:
        borrar(escena, caja, fondo)

    alto = Image.new('RGB', (escena.width, escena.height + CIELO))
    alto.paste(escena, (0, CIELO))
    alto.paste(escena.crop((0, 0, escena.width, 1)).resize((escena.width, CIELO)), (0, 0))

    cx, cy = CENTRO
    recorte = alto.crop((cx - RADIO, cy - RADIO, cx + RADIO, cy + RADIO))
    maestro = recorte.resize((768, 768), Image.LANCZOS).convert('RGBA')
    mascara = Image.new('L', (768 * 4, 768 * 4), 0)
    ImageDraw.Draw(mascara).ellipse([0, 0, 768 * 4 - 1, 768 * 4 - 1], fill=255)
    maestro.putalpha(mascara.resize((768, 768), Image.LANCZOS))
    aro = Image.new('RGBA', (768, 768), (0, 0, 0, 0))
    ImageDraw.Draw(aro).ellipse([0, 0, 767, 767], outline=(18, 21, 28, 46), width=7)
    maestro = Image.alpha_composite(maestro, aro)
    maestro.save(RAIZ / 'design/brand/marca-master.png')

    for n in TAMANOS:
        png = SALIDA / f'marca-{n}.png'
        maestro.resize((n, n), Image.LANCZOS).save(png)
        if shutil.which('cwebp'):
            subprocess.run(['cwebp', '-quiet', '-q', '92', str(png), '-o', str(SALIDA / f'marca-{n}.webp')], check=True)
    print('marca redonda generada:', ', '.join(f'marca-{n}' for n in TAMANOS))


if __name__ == '__main__':
    main()
