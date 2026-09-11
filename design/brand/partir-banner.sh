#!/bin/zsh
# Parte el banner en tres tiras verticales para las tres fotos montadas del
# hero ("recortes" del mismo banner). Provisional: banner de 180x75 cm.
# Uso: design/brand/partir-banner.sh [banner.jpg]
set -e
HERE="${0:A:h}"; ROOT="${HERE:h:h}"; OUT="$ROOT/static/assets/photos"
IN="${1:-$HERE/BANNER_ENGLIS_CORNER__180X_75_CMts_.jpg}"; T=$(mktemp -d)
magick "$IN" -crop 3x1@ +repage "$T/tira-%d.png"
for i in 0 1 2; do
  n=$((i+1))
  magick "$T/tira-$i.png" -resize 'x900>' -strip -quality 84 "$OUT/hero-$n.jpg"
  cwebp -quiet -q 82 "$OUT/hero-$n.jpg" -o "$OUT/hero-$n.webp"
  printf "  hero-%s: %s\n" $n "$(magick identify -format '%wx%h' "$OUT/hero-$n.jpg")"
done
rm -rf "$T"; echo "banner partido desde: $IN"
