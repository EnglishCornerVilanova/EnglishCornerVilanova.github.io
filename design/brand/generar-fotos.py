#!/usr/bin/env python3
"""Fotos del local para la sección «Sobre nosaltres».

    python3 design/brand/generar-fotos.py

Reduce los originales (sin recortar nada) y escribe
static/assets/photos/local-entrada-*.{jpg,webp} y local-aparador-*.{jpg,webp}.
La entrada, con el rótulo y la bandera, va al marco grande: es la que
identifica el local desde la calle."""
from pathlib import Path
from PIL import Image
import shutil, subprocess

RAIZ = Path(__file__).resolve().parents[2]
ORIG = RAIZ / 'design/brand/fotos'
SALIDA = RAIZ / 'static/assets/photos'

# Las fotos van ENTERAS: no se recorta nada. Cada marco toma la proporción de
# su foto, así que aquí solo se cambia el tamaño.
# (original, anchos a exportar, nombre)
TRABAJOS = [
    ('entrada-original.jpg', (640, 960), 'local-entrada'),
    ('aparador-original.jpg', (420, 640), 'local-aparador'),
]


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    for archivo, anchos, nombre in TRABAJOS:
        im = Image.open(ORIG / archivo).convert('RGB')
        for w in anchos:
            h = round(im.height * w / im.width)
            jpg = SALIDA / f'{nombre}-{w}.jpg'
            im.resize((w, h), Image.LANCZOS).save(jpg, quality=78, optimize=True, progressive=True)
            if shutil.which('cwebp'):
                subprocess.run(['cwebp', '-quiet', '-q', '76', str(jpg),
                                '-o', str(SALIDA / f'{nombre}-{w}.webp')], check=True)
        print(f'  · {nombre}: {im.size[0]}×{im.size[1]} → {", ".join(str(w) for w in anchos)} px')


if __name__ == '__main__':
    main()
