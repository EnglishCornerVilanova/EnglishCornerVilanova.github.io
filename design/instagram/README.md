# Plantillas de Instagram

Misma identidad que la web: tokens de `static/assets/css/site.css`, fuentes de
`static/assets/fonts/` y bandera, logo y sello Cambridge de `design/brand/`
(copias reducidas en `assets/`, para que la carpeta funcione sola).

| Pieza | Uso | Tamaño |
|---|---|---|
| A · Anunci | Matrícula, horarios, novedades | 1080 × 1350 |
| B · Cambridge | Niveles, aprobados, convocatorias | 1080 × 1350 |
| C · Tip d'anglès | Vocabulario, gramática, errores típicos | 1080 × 1350 |
| D · Comunitat | Fotos reales, fiestas, hitos | 1080 × 1350 |
| S1 · Anunci | Story con adhesivo de enlace | 1080 × 1920 |
| S2 · Quiz | Story con adhesivo de encuesta | 1080 × 1920 |
| S3 · Cambridge | Story de niveles y prueba gratuita | 1080 × 1920 |

El feed va en 4:5 y no en 1:1: ocupa más pantalla y es el formato que usa hoy
la cuadrícula del perfil. Lo importante queda dentro del recorte 3:4 central.

## Uso

- **Ver y probar textos:** abrir `templates.html` con doble clic. Los textos se
  editan clicando encima; la casilla *Zones segures* muestra los recortes de
  Instagram y dónde van los adhesivos de las stories.
- **Exportar:** `python3 render.py` (o `python3 render.py A S2`). Sale a
  `export/png/` y `export/pdf/`. Solo necesita Chrome.

## Canva

1. Canva → *Crear diseño* → *Importar archivo* → el PDF de `export/pdf/`.
   El texto llega editable y las imágenes como elementos sueltos.
2. Comprobar que Canva ha reconocido las fuentes (Bricolage Grotesque,
   Instrument Sans, Special Elite). Si alguna sale sustituida, cambiarla a mano
   una vez y guardar el diseño como plantilla.
3. Comprobar el tamaño: el PDF mide 810 × 1013 pt (feed) y 810 × 1440 pt
   (story). Si Canva no lo interpreta como 1080 × 1350 / 1080 × 1920 px, usar
   *Redimensionar* antes de guardar la plantilla.

Colores para el kit de marca de Canva:

```
Rojo      #E8192C   Rojo texto  #B8121F   Rotulador  #FFCBD1
Azul      #012169   Tinta       #12151C   Tinta 2    #3D4351
Gris perla #F2F2F0  Blanco      #FFFFFF
Tonos: cielo #EAF2FF · rubor #FFEFEF · menta #EAF7EF / #1E7A4C · sol #FFF6E0 / #8A5B00
Niveles: A2 #5CC98F · B1 #5B8DEF · B2 #F5A623 / #B07B12 · C1 #E8192C
```

## Reglas

- Si Sonia no aporta foto, se busca en bancos con licencia libre para uso
  comercial sin atribución (Unsplash, Pexels, Pixabay, Openverse con CC0).
  Nunca una imagen sin licencia declarada. Cada post guarda `foto.txt` con la
  URL, el autor y la licencia.

- Las fotos que elige Sonia se respetan: van en un marco blanco redondeado, como
  las de la web. Recortes limpios en `assets/sonia/`.

- Nada que parezca un botón: la imagen de un post no se puede pulsar. Se pone el
  WhatsApp como dato y el enlace real va en la bio, en el caption o, en las
  stories, en el adhesivo de enlace.

- Base clara siempre. El azul marino solo como franja (cifras en D, cabecera en S3),
  igual que en la web.
- La firma (bandera + «English Corner» en Special Elite) arriba a la izquierda en
  todas las piezas.
- El sello *Cambridge Exam Preparation Centre* es el mismo que ya usa la web;
  si el acuerdo con Cambridge fija condiciones de uso en redes, mandan esas.
- Cifras (20+, 500+, 4,9) solo las que ya publica la web.
