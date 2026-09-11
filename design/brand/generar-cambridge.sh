#!/bin/zsh
# Logo oficial "Cambridge Exam Preparation Centre" con fondo transparente.
# Técnica "quitar el blanco": cada píxel recupera su color real con la opacidad
# justa. Así las cintas, que se difuminan hacia el blanco, quedan con un borde
# transparente suave y sin halos, y el interior de las letras es transparente.
# Uso: design/brand/generar-cambridge.sh [original.jpg]
set -e
HERE="${0:A:h}"; ROOT="${HERE:h:h}"; IN="${1:-$HERE/cambridge-original.jpg}"; T=$(mktemp -d)
magick "$IN" -alpha off -colorspace sRGB -channel RGB -separate -evaluate-sequence min -negate "$T/opacidad.png"
magick "$IN" -alpha off -colorspace sRGB "$T/opacidad.png" \
  -channel RGB -fx '1-(1-u)/max(v,0.0001)' +channel \
  "$T/opacidad.png" -compose CopyOpacity -composite -compose Over \
  -channel A -level 3%,100% +channel -trim +repage "$HERE/cambridge-master-transparent.png"
magick "$HERE/cambridge-master-transparent.png" -resize x180 -strip "$ROOT/static/assets/img/cambridge-preparation-centre.png"
rm -rf "$T"; echo "logo de Cambridge generado desde: $IN"
