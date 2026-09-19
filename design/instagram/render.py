#!/usr/bin/env python3
"""Exporta les plantilles de templates.html a PNG i PDF amb Chrome sense finestra.

    python3 render.py            totes les peces
    python3 render.py A S2       només les indicades
    python3 render.py posts/2026-09-grups-adults   un post concret (post.png)

Surt a export/png/ (per publicar o com a fons) i export/pdf/ (per importar a
Canva: el text arriba editable). Sense dependències: només Python i Chrome.
"""
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE = HERE / "templates.html"
OUT = HERE / "export"

PIECES = {
    "A": ("feed-A-anunci", 1080, 1350),
    "B": ("feed-B-cambridge", 1080, 1350),
    "C": ("feed-C-tip", 1080, 1350),
    "D": ("feed-D-comunitat", 1080, 1350),
    "S1": ("story-1-anunci", 1080, 1920),
    "S2": ("story-2-quiz", 1080, 1920),
    "S3": ("story-3-cambridge", 1080, 1920),
}

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]


def chrome() -> str:
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    sys.exit("No trobo Chrome, Chromium ni Edge a /Applications.")


def run(args: list[str], output: Path, wait: float = 60) -> None:
    """Llança Chrome i espera que escrigui `output`.

    Amb --print-to-pdf, Chrome escriu el fitxer però de vegades no es tanca;
    per això no s'espera que acabi, sinó que el fitxer existeixi i no creixi.
    """
    output.unlink(missing_ok=True)
    # Perfil temporal: no toca el Chrome de l'usuari ni xoca si és obert.
    with tempfile.TemporaryDirectory() as profile:
        proc = subprocess.Popen(
            [chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
             "--no-first-run", f"--user-data-dir={profile}",
             "--allow-file-access-from-files", "--force-device-scale-factor=1",
             "--virtual-time-budget=4000", *args],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        deadline = time.monotonic() + wait
        last = -1
        try:
            while time.monotonic() < deadline:
                size = output.stat().st_size if output.exists() else -1
                if size > 0 and size == last:
                    return
                if proc.poll() is not None and size <= 0 and last <= 0:
                    break
                last = size
                time.sleep(0.5)
            sys.exit(f"Chrome no ha generat {output.name}.")
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()


def render_post(folder: Path) -> None:
    """Un post de posts/<data-tema>/: post.html → post.png a la mateixa carpeta."""
    page = folder / "post.html"
    if not page.exists():
        sys.exit(f"No hi ha post.html a {folder}")
    h = 1920 if 'class="canvas story' in page.read_text(encoding="utf-8") else 1350
    png = folder / "post.png"
    run([f"--window-size=1080,{h}", f"--screenshot={png}", page.as_uri()], png)
    print(f"{png.relative_to(HERE)}")


def main() -> None:
    posts = [Path(a).resolve() for a in sys.argv[1:] if Path(a).is_dir()]
    if posts:
        for folder in posts:
            render_post(folder)
        return

    wanted = sys.argv[1:] or list(PIECES)
    (OUT / "png").mkdir(parents=True, exist_ok=True)
    (OUT / "pdf").mkdir(parents=True, exist_ok=True)

    for key in wanted:
        if key not in PIECES:
            sys.exit(f"Peça desconeguda: {key}. Opcions: {', '.join(PIECES)}")
        name, w, h = PIECES[key]
        url = f"{PAGE.as_uri()}?t={key}"
        png = OUT / "png" / f"{name}.png"
        pdf = OUT / "pdf" / f"{name}.pdf"
        run([f"--window-size={w},{h}", f"--screenshot={png}", url], png)
        run(["--no-pdf-header-footer", "--print-to-pdf-no-header",
             f"--print-to-pdf={pdf}", url], pdf)
        print(f"{key:>2}  {png.relative_to(HERE)}  ·  {pdf.relative_to(HERE)}")


if __name__ == "__main__":
    main()
