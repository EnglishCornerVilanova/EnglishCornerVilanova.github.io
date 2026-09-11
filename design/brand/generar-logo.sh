#!/bin/zsh
# Genera todas las versiones del logo a partir del ORIGINAL CON TRANSPARENCIA
# (design/brand/1.png, enviado por el cliente el 11/09/2026: franjas blancas de
# la bandera opacas, interior de las letras transparente).
# Uso: design/brand/generar-logo.sh [original.png]
set -e
HERE="${0:A:h}"; ROOT="${HERE:h:h}"; IMG="$ROOT/static/assets/img"
IN="${1:-$HERE/1.png}"; M="$HERE/logo-master-transparent.png"
[ "$(magick identify -format '%[channels]' "$IN")" != "${$(magick identify -format '%[channels]' "$IN")/a/}" ] || { echo "El original no tiene transparencia: $IN"; exit 1; }
magick "$IN" -trim +repage -background none -gravity center -extent '112%x112%' \
  -resize 1120x1120 -background none -gravity center -extent 1120x1120 "$M"
for s in 96 192 384 768; do
  magick "$M" -resize ${s}x${s} -strip "$IMG/logo-$s.png"
  cwebp -quiet -q 90 -alpha_q 100 "$IMG/logo-$s.png" -o "$IMG/logo-$s.webp"
done
magick "$M" -background white -alpha remove -alpha off -resize 180x180 -strip "$IMG/apple-touch-icon.png"
magick "$M" -background white -alpha remove -alpha off -resize 192x192 -strip "$IMG/icon-192.png"
magick "$M" -background white -alpha remove -alpha off -resize 512x512 -strip "$IMG/icon-512.png"
magick "$M" -background white -alpha remove -alpha off \
  \( -clone 0 -resize 16x16 \) \( -clone 0 -resize 32x32 \) \( -clone 0 -resize 48x48 \) -delete 0 "$ROOT/static/favicon.ico"
F="/System/Library/Fonts/Supplemental/Arial Bold.ttf"; F2="/System/Library/Fonts/Supplemental/Arial.ttf"
magick -size 1200x630 xc:'#FFFFFF' \( "$M" -resize 300x300 \) -gravity center -geometry +0-66 -composite \
  -font "$F"  -pointsize 46 -fill '#12151C' -gravity center -annotate +0+152 "Acadèmia d'anglès a Vilanova del Camí" \
  -font "$F2" -pointsize 28 -fill '#6E7684' -gravity center -annotate +0+208 "Centre preparador oficial d'exàmens Cambridge" \
  -fill '#E8192C' -draw 'rectangle 0,612 1200,630' -quality 88 -strip "$IMG/og-image.jpg"
echo "logo generado desde: $IN"
