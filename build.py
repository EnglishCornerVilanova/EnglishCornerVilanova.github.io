#!/usr/bin/env python3
"""
English Corner — static site builder.

Reads  : src/template.html + content/<lang>.json + site.json
Writes : dist/  (index.html = default language, /es/, /en/, assets, sitemap…)

    python3 build.py            # build once
    python3 build.py --serve    # build, then serve dist/ on :8000 and rebuild on change
"""

from __future__ import annotations

import datetime
import hashlib
import html
import json
import os
import subprocess
import urllib.request
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
DIST = ROOT / "dist"

MISSING_MARK: set[str] = set()

# Instagram — the feed is read at BUILD time, never by visitors' browsers.
# On Behold's free plan every request to the feed URL counts as a "view"
# (1,200 a month, then the account pauses until the next month). Reading it
# here costs one view per build; the 6-hour cache below keeps the dev server,
# which rebuilds on every save, from spending the quota. Photos are copied
# into the site so visitors never contact a third-party server.
IG_CACHE = ROOT / ".cache" / "instagram"
IG_TTL = 6 * 3600
IG_POSTS: list[dict] | None = None
UA = {"User-Agent": "EnglishCornerBuild/1.0"}
IG_AVATAR = "/assets/img/logo-192.png"   # foto de perfil; el logo si no hay feed

# Horario — se lee de la ficha de Google (Places API) al construir, igual que
# Instagram: la clave solo vive en el servidor de construcción y los visitantes
# nunca contactan con Google. Sin clave, o si Google no responde, se usa el
# horario de site.json. Así, lo que se cambie en la ficha (meses, vacaciones,
# festivos) llega a la web con la publicación diaria.
PLACES_CACHE = ROOT / ".cache" / "google" / "horario.json"
HOURS: dict | None = None
DAYS_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
HOURS_I18N = {
    "ca": {"days": ["dilluns", "dimarts", "dimecres", "dijous", "divendres", "dissabte", "diumenge"],
           "and": " i ", "range": "de {a} a {b}", "closed": "tancat"},
    "es": {"days": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
           "and": " y ", "range": "de {a} a {b}", "closed": "cerrado"},
    "en": {"days": DAYS_EN, "and": " and ", "range": "{a} to {b}", "closed": "closed"},
}

LEGAL_DIR = CONTENT / "legal"
NBSP = "\u00a0"

ICONS = {
    "primaria": '<svg viewBox="0 0 24 24"><path d="M8.5 7V5.5A2.5 2.5 0 0 1 11 3h2a2.5 2.5 0 0 1 2.5 2.5V7"/><rect x="5" y="7" width="14" height="14" rx="4"/><path d="M9 21v-4a1.5 1.5 0 0 1 1.5-1.5h3A1.5 1.5 0 0 1 15 17v4"/><path d="M9 11h6"/></svg>',
    "adolescents": '<svg viewBox="0 0 24 24"><path d="M4 15v-3a8 8 0 0 1 16 0v3"/><rect x="3" y="14" width="4.5" height="7" rx="2"/><rect x="16.5" y="14" width="4.5" height="7" rx="2"/></svg>',
    "adults": '<svg viewBox="0 0 24 24"><path d="M4 9h13v6a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5V9z"/><path d="M17 11h1.5a2.5 2.5 0 0 1 0 5H17"/><path d="M8 3.5c0 1.2 1 1.3 1 2.5M12 3.5c0 1.2 1 1.3 1 2.5"/></svg>',
    "examens": '<svg viewBox="0 0 24 24"><path d="M2.5 9.5 12 5l9.5 4.5L12 14 2.5 9.5z"/><path d="M6.5 11.6V16c0 1.4 2.5 3 5.5 3s5.5-1.6 5.5-3v-4.4"/><path d="M21.5 9.5V15"/></svg>',
    "estiu": '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.6 4.6 6 6M18 18l1.4 1.4M2.5 12h2M19.5 12h2M4.6 19.4 6 18M18 6l1.4-1.4"/></svg>',
    "particulars": '<svg viewBox="0 0 24 24"><circle cx="12" cy="7.5" r="3.5"/><path d="M5 20.5c.8-3.6 3.6-6 7-6s6.2 2.4 7 6"/></svg>',
}

GENERATED_BANNER = (
    "<!-- ─────────────────────────────────────────────────────────────\n"
    "     GENERATED FILE — do not edit by hand.\n"
    "     Source: src/template.html + content/{lang}.json\n"
    "     Rebuild: python3 build.py\n"
    "     ───────────────────────────────────────────────────────── -->\n"
)


# ══════════════════════════════════════════════════════════════════
#  Tiny template engine:  {{ path }}   {{# list }}…{{/ list }}
# ══════════════════════════════════════════════════════════════════

TAG = re.compile(r"\{\{\s*(#|/)?\s*([^{}]+?)\s*\}\}")


def _lookup(path: str, scopes: list, root: dict, globals_: dict):
    """Resolve one placeholder name against the scope stack."""
    path = path.strip()

    # {{ . }} / {{ .field }} — current loop item
    if path.startswith("."):
        if not scopes:
            return ""
        item = scopes[-1]["item"]
        key = path[1:]
        if key == "":
            return item
        return _walk(item, key.split("."))

    # {{ @index }} etc. — loop meta first, then build globals
    if path.startswith("@"):
        key = path[1:]
        for sc in reversed(scopes):
            if key in sc["meta"]:
                return sc["meta"][key]
        return globals_.get(key, "")

    return _walk(root, path.split("."))


def _walk(node, parts):
    for p in parts:
        if node is None:
            return ""
        if isinstance(node, list):
            try:
                node = node[int(p)]
            except (ValueError, IndexError):
                return ""
        elif isinstance(node, dict):
            node = node.get(p)
        else:
            return ""
    return "" if node is None else node


def _resolve_list(path: str, scopes: list, root: dict, globals_: dict):
    value = _lookup(path, scopes, root, globals_)
    return value if isinstance(value, list) else []


def render(tpl: str, root: dict, globals_: dict, scopes: list | None = None) -> str:
    scopes = scopes or []
    out = []
    pos = 0

    while True:
        m = TAG.search(tpl, pos)
        if not m:
            out.append(tpl[pos:])
            break

        out.append(tpl[pos : m.start()])
        kind, name = m.group(1), m.group(2)

        if kind == "#":
            body, pos = _block(tpl, m.end(), name)
            items = _resolve_list(name, scopes, root, globals_)
            for i, item in enumerate(items):
                meta = {
                    "index": str(i),
                    "index1": str(i + 1),
                    "index2": f"{i + 1:02d}",
                    "first": i == 0,
                    "last": i == len(items) - 1,
                }
                out.append(render(body, root, globals_, scopes + [{"item": item, "meta": meta}]))
            continue

        if kind == "/":
            raise ValueError(f"Unexpected closing tag {{{{/ {name} }}}}")

        value = _lookup(name, scopes, root, globals_)
        out.append("" if value is None else str(value))
        pos = m.end()

    return "".join(out)


def _block(tpl: str, start: int, name: str) -> tuple[str, int]:
    """Return (inner body, index just past the matching close tag)."""
    depth, pos = 1, start
    while True:
        m = TAG.search(tpl, pos)
        if not m:
            raise ValueError(f"Unclosed block {{{{# {name} }}}}")
        if m.group(1) == "#":
            depth += 1
        elif m.group(1) == "/":
            depth -= 1
            if depth == 0:
                return tpl[start : m.start()], m.end()
        pos = m.end()


# ══════════════════════════════════════════════════════════════════
#  Build
# ══════════════════════════════════════════════════════════════════

def load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def plain_text(value: str) -> str:
    """The copy may carry <b>, <br>: reduce it to one line of plain text."""
    text = re.sub(r"<br\s*/?>", " ", str(value))
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    return re.sub(r"\s+", " ", text).strip()


def strip_tags(value: str) -> str:
    """Plain text escaped for an HTML attribute (meta tags, alt)."""
    return html.escape(plain_text(value), quote=True)


def page_url(site: dict, lang: str) -> str:
    return site["origin"] + ("/" if lang == site["defaultLang"] else f"/{lang}/")


def home_href(site: dict, lang: str) -> str:
    return "/" if lang == site["defaultLang"] else f"/{lang}/"


def build_alternates(site: dict, paths: dict) -> str:
    """hreflang for one page; `paths` maps each language to that page's path."""
    rows = [
        f'<link rel="alternate" hreflang="{l}" href="{site["origin"] + paths[l]}">'
        for l in site["langs"]
    ]
    rows.append(f'<link rel="alternate" hreflang="x-default" href="{site["origin"] + paths[site["defaultLang"]]}">')
    return "\n".join(rows)


def build_schema(site: dict, data: dict, lang: str) -> str:
    s = data["shared"]
    schema = {
        "@context": "https://schema.org",
        "@type": "LanguageSchool",
        "@id": site["origin"] + "/#school",
        "name": site["name"],
        "url": page_url(site, lang),
        "inLanguage": lang,
        "description": plain_text(data["meta"]["description"]),
        "image": site["origin"] + "/assets/img/og-image.jpg",
        "logo": site["origin"] + "/assets/img/icon-512.png",
        "telephone": site["phoneE164"],
        "email": s["email"],
        "priceRange": "€€",
        "foundingDate": str(site["foundedYear"]),
        "address": {
            "@type": "PostalAddress",
            "streetAddress": site["address"]["street"],
            "postalCode": site["address"]["postalCode"],
            "addressLocality": site["address"]["locality"],
            "addressRegion": site["address"]["region"],
            "addressCountry": "ES",
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": site["geo"]["lat"],
            "longitude": site["geo"]["lng"],
        },
        "areaServed": [{"@type": "Place", "name": n} for n in site["areaServed"]],
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": [DAYS_EN[d] for d in days],
                "opens": opens,
                "closes": closes,
            }
            for (opens, closes), days in hours_by_interval().items()
        ],
        "sameAs": [u for u in (site["social"]["instagram"], site["social"]["facebook"])
                   if u and "TODO" not in u],
        "knowsLanguage": site["langs"],
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def deep_merge(base: dict, over: dict) -> dict:
    """`over` wins; nested dicts are merged rather than replaced."""
    out = dict(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def shared_from_site(site: dict) -> dict:
    """Single-source-of-truth values injected into every language."""
    return {
        "shared": {
            "phone": site["phoneDisplay"],
            "phoneHref": site["phoneHref"],
            "landline": site["landlineDisplay"],
            "landlineHref": site["landlineHref"],
            "whatsapp": site["whatsapp"],
            "email": site["email"],
        },
        "social": {
            "instagramHandle": site["social"]["instagramHandle"],
            "instagramUrl": site["social"]["instagram"],
            "facebookUrl": site["social"]["facebook"],
        },
    }


def cambridge_mark(data: dict) -> tuple[str, bool]:
    """The official Cambridge preparation-centre lockup, when the centre has
    supplied it. It is a licensed mark: we never draw a lookalike. Until the
    real file is dropped in, a plain typographic seal stands in."""
    for name in ("cambridge-preparation-centre.svg", "cambridge-preparation-centre.png"):
        path = STATIC / "assets" / "img" / name
        if path.exists():
            alt = strip_tags(data["creds"]["markAlt"])
            w, h = 160, 46
            if name.endswith(".png"):   # medidas reales, leídas de la cabecera PNG
                head = path.read_bytes()[:24]
                w, h = int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")
            return (
                f'<img class="cred-mark" src="/assets/img/{name}" alt="{alt}" '
                f'width="{w}" height="{h}" decoding="async">',
                True,
            )
    return (
        '<span class="cred-seal" aria-hidden="true">'
        '<svg viewBox="0 0 24 24"><path d="M12 2l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 15.4 '
        '6.8 18.1l1-5.8L3.5 8.2l5.9-.9z"/></svg></span>',
        False,
    )


def load_env() -> None:
    """Local secrets live in a git-ignored .env (KEY=value per line). In CI the
    same names arrive as environment variables from the repository secrets."""
    f = ROOT / ".env"
    if not f.exists():
        return
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _get(url: str, timeout: int = 15):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)


def _dim(value, default: int) -> int:
    """Width/height arrive from a third-party feed and end up inside HTML
    attributes, so they are forced to a sane positive integer."""
    try:
        n = int(value)
        return n if 0 < n <= 10000 else default
    except (TypeError, ValueError):
        return default


def _im(tool: str) -> list[str] | None:
    """ImageMagick 7 ships one `magick` binary; version 6 (Ubuntu, and so the
    GitHub build server) ships separate `convert` and `identify`."""
    if shutil.which("magick"):
        return ["magick"] if tool == "convert" else ["magick", "identify"]
    return [tool] if shutil.which(tool) else None


def _trim_letterbox(path: Path) -> tuple[int, int] | None:
    """Reel covers come padded to 9:16 with pure-black bands above and below
    the real picture. Trimming them removes only padding, never content.
    Needs ImageMagick; without it the cover is kept as delivered."""
    convert, identify = _im("convert"), _im("identify")
    if not convert or not identify:
        return None
    try:
        subprocess.run([*convert, str(path), "-fuzz", "12%", "-trim", "+repage", str(path)],
                       check=True, capture_output=True, timeout=30)
        out = subprocess.run([*identify, "-format", "%w %h", str(path)],
                             check=True, capture_output=True, text=True, timeout=30).stdout
        w, h = (int(v) for v in out.split())
        return w, h
    except Exception:
        return None


def instagram_posts(site: dict) -> list[dict] | None:
    """Latest posts from the Behold JSON feed, cached for IG_TTL seconds.
    Returns None when no feed is configured or nothing could ever be read,
    in which case the page keeps its placeholder grid."""
    url = (os.environ.get("INSTAGRAM_FEED") or site.get("instagramFeed") or "").strip()
    if not url:
        return None
    meta = IG_CACHE / "posts.json"
    cached = json.loads(meta.read_text(encoding="utf-8")) if meta.exists() else None
    fresh = (
        cached is not None
        and cached.get("feed") == url
        and time.time() - meta.stat().st_mtime < IG_TTL
        and os.environ.get("IG_REFRESH") != "1"
    )
    if not fresh:
        try:
            with _get(url) as r:
                feed = json.load(r)
            IG_CACHE.mkdir(parents=True, exist_ok=True)
            profile = None
            if feed.get("profilePictureUrl"):
                try:
                    with _get(feed["profilePictureUrl"]) as r:
                        kind = r.headers.get("Content-Type", "")
                        body = r.read()
                    profile = "perfil." + ("webp" if "webp" in kind else "png" if "png" in kind else "jpg")
                    (IG_CACHE / profile).write_bytes(body)
                except Exception:
                    profile = None
            posts = []
            for p in feed.get("posts", [])[:6]:
                sizes = p.get("sizes") or {}
                pick = sizes.get("medium") or sizes.get("small") or {}
                src = pick.get("mediaUrl") or p.get("thumbnailUrl")
                if not src:
                    continue
                with _get(src) as r:
                    kind = r.headers.get("Content-Type", "")
                    body = r.read()
                ext = "webp" if "webp" in kind else "png" if "png" in kind else "jpg"
                name = f"post-{len(posts) + 1}.{ext}"
                (IG_CACHE / name).write_bytes(body)
                w, h = _dim(pick.get("width"), 560), _dim(pick.get("height"), 700)
                if p.get("mediaType") == "VIDEO":
                    w, h = _trim_letterbox(IG_CACHE / name) or (w, h)
                alt = (p.get("altText") or p.get("prunedCaption") or "").strip()
                posts.append({"file": name, "href": p.get("permalink") or "",
                              "alt": re.sub(r"\s+", " ", alt)[:140],
                              # real proportions, so the grid never crops a post
                              "w": w, "h": h})
            meta.write_text(json.dumps({"feed": url, "posts": posts, "profile": profile}, ensure_ascii=False),
                            encoding="utf-8")
            cached = {"feed": url, "posts": posts, "profile": profile}
            print(f"  · instagram: {len(posts)} publicaciones leídas del feed")
        except Exception as exc:
            if cached and cached.get("feed") == url:
                print(f"  ⚠ instagram: el feed no responde ({exc}); uso la última copia")
            else:
                print(f"  ⚠ instagram: el feed no responde ({exc}); se mantienen los huecos")
                return None
    out = DIST / "assets" / "ig"
    out.mkdir(parents=True, exist_ok=True)
    for p in cached["posts"]:
        shutil.copy2(IG_CACHE / p["file"], out / p["file"])
    global IG_AVATAR
    if cached.get("profile") and (IG_CACHE / cached["profile"]).exists():
        shutil.copy2(IG_CACHE / cached["profile"], out / cached["profile"])
        IG_AVATAR = f"/assets/ig/{cached['profile']}"
    return cached["posts"] or None


def ig_grid(data: dict) -> str:
    """Real posts when the feed is available, the placeholders otherwise."""
    if not IG_POSTS:
        return "\n      ".join(
            f'<div class="ig-cell"><div class="ph ph-{p["tone"]}"><div class="ph-inner">'
            f'<span>{p["label"]}</span></div></div></div>'
            for p in data["insta"]["posts"]
        )
    fallback = strip_tags(data["insta"]["postAlt"])
    return "\n      ".join(
        f'<a class="ig-cell" href="{html.escape(p["href"], quote=True)}" target="_blank" rel="noopener">'
        f'<img src="/assets/ig/{p["file"]}" alt="{html.escape(p["alt"], quote=True) or fallback}" '
        f'width="{_dim(p.get("w"), 560)}" height="{_dim(p.get("h"), 700)}" loading="lazy" decoding="async"></a>'
        for p in IG_POSTS
    )


def asset_version(rel: str) -> str:
    """Short content hash for cache-busting: the URL changes whenever the file
    does, so browsers never keep a stale stylesheet or script after a deploy."""
    return hashlib.sha1((STATIC / rel).read_bytes()).hexdigest()[:10]


def lang_redirect(site: dict, paths: dict) -> str:
    """Blocking <head> snippet: honour a previously chosen language, landing on
    this same page in that language (`paths` maps language → path)."""
    return (
        "(function(){try{"
        "var s=localStorage.getItem('ec-lang'),"
        "c=(document.documentElement.lang||'').slice(0,2),"
        f"m={json.dumps(paths)};"
        "if(s&&s!==c&&m[s]&&!location.hash)"
        "location.replace(m[s]+location.search);"
        "}catch(e){}})();"
    )


# ── Horario ─────────────────────────────────────────────────────────

def _hhmm(t: dict) -> str:
    return f"{int(t.get('hour', 0)):02d}:{int(t.get('minute', 0)):02d}"


def _week_from_periods(periods: list) -> list[list[list[str]]]:
    """Periodos de Google (día 0 = domingo) → semana que empieza en lunes."""
    week: list[list[list[str]]] = [[] for _ in range(7)]
    for p in periods:
        o, c = p.get("open") or {}, p.get("close")
        day = (int(o.get("day", 0)) - 1) % 7
        week[day].append([_hhmm(o), _hhmm(c)] if c else ["00:00", "24:00"])
    return [sorted(d) for d in week]


def _special_days(current: dict) -> list[dict]:
    """Festivos y vacaciones marcados en la ficha (Google da los próximos 7 días)."""
    out = []
    for s in current.get("specialDays", []):
        d = s.get("date") or {}
        try:
            day = datetime.date(int(d["year"]), int(d["month"]), int(d["day"]))
        except (KeyError, TypeError, ValueError):
            continue
        intervals = sorted([_hhmm(p["open"]), _hhmm(p["close"])]
                           for p in current.get("periods", [])
                           if (p.get("open") or {}).get("date") == d and p.get("close"))
        out.append({"date": day.isoformat(), "intervals": intervals})
    return out


def site_hours(site: dict) -> dict:
    week: list[list[list[str]]] = [[] for _ in range(7)]
    for h in site["openingHours"]:
        for day in h["days"]:
            week[DAYS_EN.index(day)].append([h["opens"], h["closes"]])
    return {"week": [sorted(d) for d in week], "special": [], "source": "site.json"}


def google_hours(site: dict) -> dict | None:
    """Horario de la ficha de Google, con la misma caché de 6 h que Instagram.
    None si no hay clave o si Google no ha respondido nunca."""
    key = os.environ.get("GOOGLE_PLACES_KEY", "").strip()
    query = (site.get("googlePlaceQuery") or "").strip()
    if not key or not query:
        return None
    cached = json.loads(PLACES_CACHE.read_text(encoding="utf-8")) if PLACES_CACHE.exists() else None
    if (cached and time.time() - PLACES_CACHE.stat().st_mtime < IG_TTL
            and os.environ.get("IG_REFRESH") != "1"):
        return cached
    try:
        req = urllib.request.Request(
            "https://places.googleapis.com/v1/places:searchText",
            data=json.dumps({"textQuery": query}).encode(),
            headers={**UA, "Content-Type": "application/json", "X-Goog-Api-Key": key,
                     "X-Goog-FieldMask": "places.displayName,places.regularOpeningHours,"
                                         "places.currentOpeningHours"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            found = json.load(r).get("places", [])
        place = next((p for p in found
                      if "english corner" in ((p.get("displayName") or {}).get("text") or "").lower()), None)
        if not place or not (place.get("regularOpeningHours") or {}).get("periods"):
            raise ValueError("la ficha no aparece o no tiene horario")
        hours = {"week": _week_from_periods(place["regularOpeningHours"]["periods"]),
                 "special": _special_days(place.get("currentOpeningHours") or {}),
                 "source": "ficha de Google"}
        PLACES_CACHE.parent.mkdir(parents=True, exist_ok=True)
        PLACES_CACHE.write_text(json.dumps(hours), encoding="utf-8")
        return hours
    except Exception as exc:   # nunca se imprime la clave: solo el tipo de error
        print(f"  ⚠ horario: Google no responde ({type(exc).__name__}: {exc}); "
              + ("uso la última copia" if cached else "uso el de site.json"))
        return cached


def hours_by_interval() -> dict[tuple, list[int]]:
    out: dict[tuple, list[int]] = {}
    for day, intervals in enumerate(HOURS["week"]):
        for opens, closes in intervals:
            out.setdefault((opens, closes), []).append(day)
    return out


def _fmt_intervals(intervals: list, lang: str) -> str:
    parts = []
    for opens, closes in intervals:
        if lang == "ca":   # «de 15 a 21.15 h», «d'11 a 13 h»
            a, b = (t[:2].lstrip("0") + ("" if t[3:] == "00" else "." + t[3:]) for t in (opens, closes))
            # espacios de no separación: «a 21.15 h» nunca se parte entre líneas
            parts.append(("d'" if a == "1" or a.startswith(("1.", "11")) else "de ") + f"{a} a{NBSP}{b}{NBSP}h")
        elif lang == "es":
            parts.append(f"de {opens} a{NBSP}{closes}")
        else:
            parts.append(f"{opens}–{closes}")
    return HOURS_I18N[lang]["and"].join(parts)


def _fmt_days(days: list[int], lang: str) -> str:
    t = HOURS_I18N[lang]
    names = [t["days"][d] for d in days]
    if len(days) >= 3 and days == list(range(days[0], days[-1] + 1)):
        return t["range"].format(a=names[0], b=names[-1])
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + t["and"] + names[-1]


def hours_html(lang: str) -> str:
    """Una línea por grupo de días con el mismo horario, más los festivos
    y vacaciones de los próximos días que se hayan marcado en Google."""
    week = HOURS["week"]
    groups: dict[tuple, list[int]] = {}
    for day, intervals in enumerate(week):
        if intervals:
            groups.setdefault(tuple(map(tuple, intervals)), []).append(day)
    lines = []
    for intervals, days in sorted(groups.items(), key=lambda g: g[1][0]):
        text = f"{_fmt_days(days, lang)}: {_fmt_intervals(intervals, lang)}"
        lines.append(html.escape(text[0].upper() + text[1:]))
    today = datetime.date.today()
    for s in HOURS.get("special", []):
        day = datetime.date.fromisoformat(s["date"])
        if day < today or s["intervals"] == week[day.weekday()]:
            continue
        what = _fmt_intervals(s["intervals"], lang) if s["intervals"] else HOURS_I18N[lang]["closed"]
        name = HOURS_I18N[lang]["days"][day.weekday()]
        lines.append(f'<span class="hours-note">{html.escape(name[0].upper() + name[1:])} '
                     f'{day.day}/{day.month}: {html.escape(what)}</span>')
    return "<br>".join(lines)


# ── Páginas legales ─────────────────────────────────────────────────

def legal_pages(lang: str) -> dict:
    return load_json(LEGAL_DIR / f"{lang}.json")


def legal_href(site: dict, lang: str, key: str) -> str:
    page = next(p for p in legal_pages(lang)["pages"] if p["key"] == key)
    return home_href(site, lang) + page["slug"] + "/"


def legal_main(site: dict, lang: str, data: dict, page: dict) -> str:
    """Cuerpo de una página legal. Los textos viven en content/legal/<lang>.json;
    los datos del titular, en site.json, para escribirlos una sola vez."""
    a = site["address"]
    tokens = {
        "owner": site["legal"]["owner"],
        "nif": site["legal"]["nif"],
        "address": f'{a["street"]}, {a["postalCode"]} {a["locality"]} ({a["region"]})',
        "email": site["email"],
        "phone": site["phoneDisplay"],
        "site": site["origin"].split("://", 1)[-1],
        "mapButton": data["map"]["consentButton"],
    }
    legal = legal_pages(lang)
    body = "\n".join(f'  <h2>{html.escape(s["h"])}</h2>\n  {s["html"]}' for s in page["sections"])
    for key, value in tokens.items():
        body = body.replace(f"[[{key}]]", html.escape(value))
    for p in legal["pages"]:
        body = body.replace(f"[[href:{p['key']}]]", legal_href(site, lang, p["key"]))
    return (
        '<main id="main" class="legal-main">\n<article class="legal">\n'
        f'  <p class="legal-kicker"><a href="{home_href(site, lang)}">English Corner</a></p>\n'
        f'  <h1 class="display">{html.escape(page["title"])}</h1>\n'
        f'  <p class="legal-updated">{html.escape(legal["updated"])}</p>\n'
        f"{body}\n</article>\n</main>"
    )


def build_lang(site: dict, lang: str, template: str, legal_key: str | None = None,
               not_found: bool = False) -> str:
    """The home page, or with `legal_key` one of the legal pages: same head,
    nav and footer, with <main> swapped for the legal text."""
    data = deep_merge(shared_from_site(site), load_json(CONTENT / f"{lang}.json"))
    for item in data.get("courses", {}).get("items", []):
        item["iconSvg"] = ICONS.get(item.get("icon", ""), "")

    mark_html, mark_is_official = cambridge_mark(data)
    if not mark_is_official:
        MISSING_MARK.add(lang)

    legal = legal_pages(lang)
    home = home_href(site, lang)
    if legal_key or not_found:
        # Fuera de la portada, las anclas del menú y del pie llevan de vuelta a ella.
        for link in data["nav"]["items"] + [k for col in data["footer"]["cols"] for k in col.get("links", [])]:
            if link["href"].startswith("#"):
                link["href"] = home + link["href"]
    if legal_key:
        page = next(p for p in legal["pages"] if p["key"] == legal_key)
        paths = {l: legal_href(site, l, legal_key) for l in site["langs"]}
        data["meta"].update(title=f'{page["title"]} | English Corner', description=page["description"],
                            ogTitle=page["title"], ogDescription=page["description"])
        main = legal_main(site, lang, data, page)
        template = re.sub(r'<main id="main">.*?</main>', lambda _: main, template, count=1, flags=re.S)
        template = template.replace('<script type="application/ld+json">{{ @schema }}</script>', "")
    elif not_found:
        paths = {l: home_href(site, l) for l in site["langs"]}
        nf = data["notFound"]
        data["meta"].update(title=f'{nf["title"]} | English Corner', description=nf["lede"],
                            ogTitle=nf["title"], ogDescription=nf["lede"])
        main = (
            '<main id="main" class="legal-main">\n<article class="legal legal-404">\n'
            f'  <p class="legal-kicker"><a href="{home}">English Corner</a></p>\n'
            f'  <h1 class="display">{html.escape(nf["title"])}</h1>\n'
            f'  <p class="hero-lede">{html.escape(nf["lede"])}</p>\n'
            f'  <p><a class="btn btn--red" href="{home}">{html.escape(nf["cta"])}</a></p>\n'
            '</article>\n</main>'
        )
        template = re.sub(r'<main id="main">.*?</main>', lambda _: main, template, count=1, flags=re.S)
        template = template.replace('<script type="application/ld+json">{{ @schema }}</script>', "")
    else:
        paths = {l: home_href(site, l) for l in site["langs"]}

    lang_links = [
        {
            "code": l,
            "codeUpper": l.upper(),
            "name": site["langNames"][l],
            "href": paths[l],
            "currentAttr": ' aria-current="true"' if l == lang else "",
        }
        for l in site["langs"]
    ]
    legal_links = [
        {
            "href": legal_href(site, lang, p["key"]),
            "label": p["short"],
            "currentAttr": ' aria-current="page"' if p["key"] == legal_key else "",
        }
        for p in legal["pages"]
    ]

    globals_ = {
        "lang": lang,
        "langUpper": lang.upper(),
        "langLinks": lang_links,
        "legalLinks": legal_links,
        "legalNavLabel": legal["navLabel"],
        "home": home,
        "canonical": site["origin"] + paths[lang],
        "robots": '<meta name="robots" content="noindex, follow">' if (legal_key or not_found) else "",
        "origin": site["origin"],
        "ogLocale": site["ogLocales"][lang],
        "alternates": build_alternates(site, paths),
        "langRedirect": lang_redirect(site, paths),
        "hoursHtml": hours_html(lang),
        "mapsUrl": site["googleMaps"],
        "cambridgeMark": mark_html,
        "igGrid": ig_grid(data),
        "igAvatar": IG_AVATAR,
        "cssV": asset_version("assets/css/site.css"),
        "jsV": asset_version("assets/js/site.js"),
        "schema": "" if (legal_key or not_found) else build_schema(site, data, lang),
        "year": site["year"],
    }

    # Values that land inside attributes must not carry markup.
    data = json.loads(json.dumps(data))
    for key in ("title", "description", "ogTitle", "ogDescription"):
        data["meta"][key] = strip_tags(data["meta"][key])

    page = render(template, data, globals_)
    return page.replace("<!DOCTYPE html>\n", "<!DOCTYPE html>\n" + GENERATED_BANNER, 1)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sitemap(site: dict) -> str:
    urls = []
    for lang in site["langs"]:
        alts = "".join(
            f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{page_url(site, l)}"/>'
            for l in site["langs"]
        )
        urls.append(
            f"  <url>\n    <loc>{page_url(site, lang)}</loc>"
            f"{alts}\n    <changefreq>monthly</changefreq>\n"
            f"    <priority>{'1.0' if lang == site['defaultLang'] else '0.9'}</priority>\n  </url>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def build_manifest(site: dict) -> str:
    return json.dumps(
        {
            "name": site["name"],
            "short_name": site["name"],
            "start_url": "/",
            "display": "standalone",
            "background_color": "#FFFFFF",
            "theme_color": "#FFFFFF",
            "icons": [
                {"src": "/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
                {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"},
            ],
        },
        ensure_ascii=False,
        indent=2,
    )


def build() -> None:
    load_env()
    site = load_json(ROOT / "site.json")
    template = (SRC / "template.html").read_text(encoding="utf-8")

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(STATIC, DIST)

    global IG_POSTS, HOURS
    IG_POSTS = instagram_posts(site)
    HOURS = google_hours(site) or site_hours(site)
    print(f"  · horario: {HOURS['source']}")

    for lang in site["langs"]:
        base = DIST if lang == site["defaultLang"] else DIST / lang
        write(base / "index.html", build_lang(site, lang, template))
        pages = legal_pages(lang)["pages"]
        for p in pages:
            write(base / p["slug"] / "index.html", build_lang(site, lang, template, p["key"]))
        print(f"  · {(base / 'index.html').relative_to(ROOT)} + {len(pages)} páginas legales")

    write(DIST / "404.html", build_lang(site, site["defaultLang"], template, not_found=True))
    print("  · dist/404.html")

    write(DIST / "sitemap.xml", build_sitemap(site))
    write(DIST / "site.webmanifest", build_manifest(site))
    write(DIST / "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {site['origin']}/sitemap.xml\n")
    print("  · dist/sitemap.xml, robots.txt, site.webmanifest")
    warn_pending()


def warn_pending() -> None:
    """Surface anything still marked TODO so it cannot be shipped by accident."""
    hits = []
    for page in sorted(DIST.rglob("*.html")):
        for n, line in enumerate(page.read_text(encoding="utf-8").splitlines(), 1):
            if "TODO" in line:
                hits.append(f"{page.relative_to(ROOT)}:{n}")
            if "{{" in line:
                hits.append(f"{page.relative_to(ROOT)}:{n}  (placeholder not resolved)")
    if MISSING_MARK:
        print(
            "\n  ⚠ falta el logotipo oficial de Cambridge.\n"
            "     Es una marca licenciada: no se dibuja una imitación.\n"
            "     Descárgalo del portal del centro y guárdalo como\n"
            "     static/assets/img/cambridge-preparation-centre.svg (o .png).\n"
            "     Mientras tanto se muestra un sello tipográfico."
        )
    if hits:
        print("\n  ⚠ pendientes en la salida:")
        for h in hits[:20]:
            print(f"     {h}")
        if len(hits) > 20:
            print(f"     … y {len(hits) - 20} más")


def watched_files():
    for folder in (SRC, CONTENT, STATIC):
        yield from (p for p in folder.rglob("*") if p.is_file())
    yield ROOT / "site.json"


def serve(port: int = 8000) -> None:
    import http.server
    import socketserver
    import threading

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(DIST), **kw)

        def log_message(self, *a):
            pass

    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", port), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    print(f"\n  → http://127.0.0.1:{port}   (Ctrl-C to stop)\n")

    stamps = {p: p.stat().st_mtime for p in watched_files()}
    try:
        while True:
            time.sleep(0.6)
            now = {p: p.stat().st_mtime for p in watched_files()}
            if now != stamps:
                stamps = now
                print("  ↻ rebuilding…")
                try:
                    build()
                except Exception as exc:  # keep the server alive on a typo
                    print(f"  ✗ {exc}")
    except KeyboardInterrupt:
        print("\n  stopped.")


if __name__ == "__main__":
    print("\nEnglish Corner — building")
    build()
    if "--serve" in sys.argv:
        serve()
    else:
        print("\n  done. Preview with: python3 build.py --serve\n")
