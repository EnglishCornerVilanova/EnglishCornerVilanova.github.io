# English Corner — sitio web

Landing estática y trilingüe (català · castellano · English) para **English Corner**,
academia de inglés y centro preparador oficial de exámenes Cambridge en
Vilanova del Camí (Anoia, Barcelona).

El brief del cliente y la lista de pendientes están en `docs/`, que es
privada: existe solo en el ordenador de trabajo y no se publica en este
repositorio. **Léelos antes de tocar el diseño.**

---

## Arrancar

```bash
python3 build.py --serve
```

Sirve en <http://127.0.0.1:8000> y reconstruye solo al guardar cualquier
fichero de `src/`, `content/`, `static/` o `site.json`.

Para construir sin servidor:

```bash
python3 build.py
```

No hay dependencias: solo Python 3 de la instalación del sistema.

> **Abre siempre por el servidor, no con doble clic sobre el HTML.**
> Las rutas son absolutas (`/assets/...`), así que `file://` no carga estilos.

---

## Estructura

```
site.json              Datos del negocio: dominio, teléfono, dirección,
                       horarios, redes, idiomas. Fuente única de verdad.
content/
  ca.json              Todo el texto en catalán   (idioma por defecto)
  es.json              Todo el texto en castellano
  en.json              Todo el texto en inglés
src/
  template.html        La maqueta. Una sola, común a los tres idiomas.
static/                Se copia tal cual a dist/
  assets/css/site.css  Todo el CSS
  assets/js/site.js    Todo el JS (vanilla, sin dependencias)
  assets/img/          Logos, iconos, imagen de Open Graph
  favicon.ico
build.py               El generador
design/brand/          Originales del logo en alta. NO se publican.
docs/                  Notas privadas (solo en local, no se publican)
dist/                  SALIDA GENERADA — no editar, no versionar
```

---

## Cómo se hace cada cambio

| Quiero cambiar… | Toco… |
|---|---|
| Un texto, un titular, una descripción de curso | `content/<idioma>.json` |
| La franja de credenciales bajo el hero | `creds` en `content/<idioma>.json` |
| El feed de Instagram | `INSTAGRAM_FEED` en `.env` (local, no se sube) y como secreto en GitHub |
| El teléfono, la dirección, el horario, las redes | `site.json` |
| La maqueta, el orden de las secciones, el HTML | `src/template.html` |
| Colores, tipografía, espaciado, animaciones | `static/assets/css/site.css` |
| Comportamiento (menú, idioma, mapa) | `static/assets/js/site.js` |

Después, `python3 build.py`. **Nunca edites `dist/`**: se borra y se
regenera en cada build. Los ficheros generados llevan una cabecera que lo avisa.

### Añadir o quitar elementos de una lista

Cursos, niveles de examen, pilares del método, cifras, testimonios y enlaces
del pie son listas en el JSON. Añadir un elemento es añadir un objeto al array
en **los tres idiomas** — la maqueta los recorre sola.

---

## Los tres idiomas

Cada idioma es una página estática de verdad, no una traducción por JavaScript:

```
dist/index.html      → /        català   (por defecto)
dist/es/index.html   → /es/     castellano
dist/en/index.html   → /en/     English
```

Esto da `hreflang` correcto, indexación de las tres versiones y un selector
que funciona aunque el visitante tenga el JavaScript desactivado (son enlaces
normales).

- El selector guarda la elección en `localStorage` (`ec-lang`).
- Un visitante que ya eligió idioma aterriza en el suyo: lo hace un script
  bloqueante en el `<head>` para que no llegue a verse el idioma equivocado.
- **No** se redirige adivinando por `navigator.language`: eso redirigiría
  también a los buscadores. Si algún día se quiere, se activa en `site.js`.

**Cambiar el idioma por defecto** (el que vive en `/`): `defaultLang` en
`site.json`. Nada más — las rutas, el `hreflang`, el sitemap y el selector
se recalculan solos.

---

## El logotipo de Cambridge

La franja de credenciales, justo debajo del hero, tiene un hueco reservado.
Deja el archivo oficial en:

```
static/assets/img/cambridge-preparation-centre.svg    (o .png)
```

y `build.py` lo coloca solo en la próxima construcción. Mientras no exista,
se muestra un sello tipográfico y el build lo avisa.

**No se dibuja una imitación.** Es una marca registrada cuyo uso depende del
acuerdo del centro; el archivo autorizado lo entrega Cambridge en el portal
de centros preparadores.

---

## Antes de publicar

`python3 build.py` avisa al final de todo lo que sigue marcado `TODO` en la
salida. Ahora mismo son los usuarios de Instagram y Facebook. **No se
publica con avisos pendientes.**

Falta también, y es bloqueante en España: aviso legal, política de
privacidad y política de cookies. Ver `docs/PENDIENTE.md`.

---

## Publicar

`dist/` es un sitio estático plano: vale cualquier hosting (Netlify, Vercel,
Cloudflare Pages, GitHub Pages o un FTP de toda la vida).

1. Ajusta `origin` en `site.json` al dominio real — de ahí salen la URL
   canónica, los `hreflang`, el sitemap y las etiquetas de Open Graph.
2. `python3 build.py`
3. Sube el contenido de `dist/` a la raíz del dominio.

Si el hosting lo permite, sirve `/assets/` con caché larga; el HTML, corta.
