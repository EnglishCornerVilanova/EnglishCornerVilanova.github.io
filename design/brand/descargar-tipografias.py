#!/usr/bin/env python3
"""Tipografías servidas desde la propia web, no desde Google.

    python3 design/brand/descargar-tipografias.py

Pide a Google la hoja de estilos de las familias que usa la web, se queda con
los subconjuntos latinos, descarga los .woff2 a static/assets/fonts/ y escribe
las reglas @font-face dentro de site.css, entre las marcas «tipografías».
Así ningún visitante contacta con Google y las letras no cambian."""
import re, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
FUENTES = RAIZ / 'static/assets/fonts'
CSS = RAIZ / 'static/assets/css/site.css'
INICIO, FIN = '/* tipografías:inicio (design/brand/descargar-tipografias.py) */', '/* tipografías:fin */'
SUBCONJUNTOS = ('latin', 'latin-ext')   # catalán y castellano; fuera cirílico, griego y vietnamita
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
# Se piden como fuentes VARIABLES (rangos de grosor): un solo archivo por
# familia y subconjunto en vez de uno por grosor.
URL = ('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800'
       '&family=Instrument+Sans:wght@400..700&family=Special+Elite&display=swap')


def main():
    FUENTES.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(URL, headers=UA)
    hoja = urllib.request.urlopen(req, timeout=30).read().decode()

    bloques, sub_actual, vistos = [], None, {}
    for trozo in hoja.split('/*'):
        nombre = trozo.split('*/')[0].strip() if '*/' in trozo else None
        cuerpo = trozo.split('*/', 1)[1] if '*/' in trozo else trozo
        if nombre:
            sub_actual = nombre
        for regla in re.findall(r'@font-face\s*\{[^}]*\}', cuerpo):
            if sub_actual not in SUBCONJUNTOS:
                continue
            familia = re.search(r"font-family:\s*'([^']+)'", regla).group(1)
            peso = re.search(r'font-weight:\s*([^;]+);', regla).group(1).strip().replace(' ', '-')
            url = re.search(r'url\((https://[^)]+)\)', regla).group(1)
            archivo = f"{familia.lower().replace(' ', '-')}-{sub_actual}.woff2"
            if url not in vistos:
                datos = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
                (FUENTES / archivo).write_bytes(datos)
                vistos[url] = archivo
                print(f'  · {archivo}  {len(datos)/1024:.0f} kB  (grosores {peso})')
            archivo = vistos[url]
            bloques.append(regla.replace(url, f'/assets/fonts/{archivo}').strip())

    css = CSS.read_text(encoding='utf-8')
    nuevo = (INICIO + '\n'
             '/* Letras servidas desde esta misma web: ningún visitante contacta con\n'
             '   Google para verlas. Generado, no editar a mano. */\n'
             + '\n'.join(bloques) + '\n' + FIN)
    if INICIO in css:
        css = re.sub(re.escape(INICIO) + r'.*?' + re.escape(FIN), lambda _: nuevo, css, flags=re.S)
    else:
        css = nuevo + '\n\n' + css
    CSS.write_text(css, encoding='utf-8')
    print(f'  {len(bloques)} reglas @font-face escritas en site.css')


if __name__ == '__main__':
    main()
