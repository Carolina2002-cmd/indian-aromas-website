"""Builds index.html for the INDIAN AROMAS website from build/data.py.

Usage: python3 build/build.py
"""
import json
import math
import os
import sys
from html import escape

sys.path.insert(0, os.path.dirname(__file__))
from data import CATEGORIES, CHANNEL, FESTIVALS, SHORTS, VIDEOS  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = {c["key"]: c for c in CATEGORIES}
FEST = {f["key"]: f for f in FESTIVALS}
SHORT_LABEL = {"mithai": "Mithai", "bakery": "Cakes", "mains": "Sabzi & dal", "street": "Chaat",
               "healthy": "Breakfast", "vrat": "Vrat", "sides": "Achaar"}


def text_on(hexc):
    """Ink text on light colors, white on dark ones (WCAG contrast)."""
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    lum = 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
    return "#2B1430" if lum > 0.24 else "#FFFFFF"


def item(row, kind):
    vid, views, en, hi, cat, fests = row
    return {"id": vid, "views": views, "en": en, "hi": hi, "cat": cat, "fests": fests, "kind": kind,
            "img": f"assets/img/{'videos' if kind == 'video' else 'shorts'}/{vid}.jpg",
            "url": f"https://www.youtube.com/{'watch?v=' if kind == 'video' else 'shorts/'}{vid}"}


ALL = [item(r, "video") for r in VIDEOS] + [item(r, "short") for r in SHORTS]
BY_ID = {i["id"]: i for i in ALL}


def views(n):
    if n >= 1000:
        s = f"{n / 1000:.1f}".rstrip("0").rstrip(".")
        return f"{s}K views"
    return f"{n} views"


def icon(name, cls="icon"):
    paths = {
        "play": '<path d="M8 5.5v13l11-6.5z" fill="currentColor" stroke="none"/>',
        "bell": '<path d="M10.3 21a1.9 1.9 0 0 0 3.4 0"/><path d="M3.3 15.3A1 1 0 0 0 4 17h16a1 1 0 0 0 .7-1.7C19.4 14 18 12.6 18 8A6 6 0 0 0 6 8c0 4.6-1.4 6-2.7 7.3"/>',
        "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
        "x": '<path d="M18 6 6 18M6 6l12 12"/>',
        "copy": '<rect x="8" y="8" width="13" height="13" rx="2"/><path d="M4 16V5a1 1 0 0 1 1-1h11"/>',
        "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
        "external": '<path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
        "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10Z"/><path d="M2 21c0-3 1.9-5.4 5.2-6.1C9.6 14.4 12 13 13 12"/>',
        "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/><path d="M12 17.5s-3-1.7-3-3.6a1.6 1.6 0 0 1 3-.8 1.6 1.6 0 0 1 3 .8c0 1.9-3 3.6-3 3.6Z"/>',
        "cake": '<path d="M20 21v-8a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8"/><path d="M4 16s.5-1 2-1 2.5 2 4 2 2.5-2 4-2 2.5 2 4 2 2-1 2-1"/><path d="M2 21h20M7 8v3M12 8v3M17 8v3M7 4h.01M12 4h.01M17 4h.01"/>',
        "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
        "sparkles": '<path d="M9.9 15.5A2 2 0 0 0 8.5 14l-6.1-1.6a.5.5 0 0 1 0-1L8.5 10A2 2 0 0 0 9.9 8.5l1.6-6.1a.5.5 0 0 1 1 0L14 8.5a2 2 0 0 0 1.5 1.4l6.1 1.6a.5.5 0 0 1 0 1L15.5 14a2 2 0 0 0-1.4 1.4l-1.6 6.1a.5.5 0 0 1-1 0Z"/>',
        "package": '<path d="M11 21.7a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.7l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.7z"/><path d="M12 22V12M3.3 7 12 12l8.7-5M7.5 4.3l9 5.1"/>',
        "trophy": '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6M18 9h1.5a2.5 2.5 0 0 0 0-5H18M4 22h16M10 14.7V17c0 .6-.5 1-1 1.2C7.8 18.8 7 20.2 7 22M14 14.7V17c0 .6.5 1 1 1.2 1.2.6 2 2 2 3.8"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>',
        "share": '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/>',
        "chef": '<path d="M17 21a1 1 0 0 0 1-1v-5.4a1 1 0 0 1 .6-.9 4 4 0 0 0-2.7-7.5 4 4 0 0 0-7.8 0 4 4 0 0 0-2.7 7.5 1 1 0 0 1 .6.9V20a1 1 0 0 0 1 1z"/><path d="M6 17h12"/>',
        "shuffle": '<path d="m18 14 4 4-4 4M18 2l4 4-4 4"/><path d="M2 18h1.97a4 4 0 0 0 3.3-1.7l5.47-8.6A4 4 0 0 1 16.03 6H22"/><path d="M2 6h1.97a4 4 0 0 1 3.6 2.2M22 18h-6.04a4 4 0 0 1-3.3-1.8l-.36-.45"/>',
    }
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{paths[name]}</svg>')


YT_ICON = ('<svg class="icon icon--yt" viewBox="0 0 28 20" aria-hidden="true" focusable="false"><rect width="28" height="20" rx="5" fill="currentColor"/>'
           '<path d="M11.2 5.6v8.8l7.6-4.4z" fill="var(--yt-play, #fff)"/></svg>')

BOWL_MARK = """<svg class="bowl-mark" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
<circle cx="32" cy="32" r="31" fill="#FFE3EF"/>
<g fill="none" stroke="#D10F6A" stroke-width="3.2" stroke-linecap="round" class="steam">
<path d="M23 25c-3-4 3-6 0-10s2-6 0-9"/><path d="M32 23c-3-4 3-6 0-10s2-6 0-9"/><path d="M41 25c-3-4 3-6 0-10s2-6 0-9"/></g>
<path d="M9 31h46c0 11-10 19-23 19S9 42 9 31z" fill="#F7A21B"/>
<path d="M11.5 38h41" stroke="#D10F6A" stroke-width="4"/>
<path d="M20 52h24" stroke="#5B2A86" stroke-width="3.5" stroke-linecap="round"/>
<circle cx="24" cy="33.5" r="1.8" fill="#2E9B57"/><circle cx="33" cy="34" r="1.8" fill="#D62839"/><circle cx="41" cy="33.4" r="1.8" fill="#2E9B57"/></svg>"""


def mandala(cls, petals=12, color="currentColor"):
    """A simple rangoli-style mandala drawn from rotated petals."""
    out = []
    for ring, (r, l, w, n) in enumerate([(30, 34, 12, petals), (62, 30, 10, petals * 2), (94, 26, 8, petals * 2)]):
        for k in range(n):
            a = 360 / n * k + (ring * 360 / n / 2)
            out.append(f'<ellipse cx="0" cy="-{r + l / 2}" rx="{w / 2}" ry="{l / 2}" transform="rotate({a:.2f})"/>')
    dots = "".join(f'<circle cx="0" cy="-128" r="4" transform="rotate({360 / (petals * 2) * k:.2f})"/>' for k in range(petals * 2))
    return (f'<svg class="{cls}" viewBox="-140 -140 280 280" aria-hidden="true" focusable="false"><g fill="none" stroke="{color}" stroke-width="2.4">'
            f'<circle r="20"/><circle r="56"/>{"".join(out)}</g><g fill="{color}">{dots}<circle r="8"/></g></svg>')


def ladoo_jar():
    """A glass jar holding 100 ladoo spots; filled spots = subscribers / 100."""
    filled = round(CHANNEL["subscribers"] / 100)
    rows, per, r = 10, 10, 10.5
    circles = []
    n = 0
    for row in range(rows):
        y = 262 - row * 19.5
        off = 0 if row % 2 == 0 else r
        for col in range(per):
            x = 47 + off + col * 21.5
            if x > 250:
                continue
            n += 1
            on = n <= filled
            circles.append(
                f'<g class="ladoo{" ladoo--on" if on else ""}" style="--d:{n * 12}ms"><circle cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>'
                + (f'<circle cx="{x - 3:.1f}" cy="{y - 3:.1f}" r="1.6" class="ladoo__dot"/><circle cx="{x + 3.5:.1f}" cy="{y + 1:.1f}" r="1.4" class="ladoo__dot"/>' if on else "")
                + "</g>")
    return f"""<svg class="jar" viewBox="0 0 300 330" role="img" aria-labelledby="jar-title">
<title id="jar-title">Ladoo jar: {filled} of 100 ladoos filled. Each ladoo is 100 subscribers.</title>
<defs><clipPath id="jar-clip"><path d="M40 70h220v190c0 22-18 40-40 40H80c-22 0-40-18-40-40z"/></clipPath>
<linearGradient id="glass" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity=".75"/><stop offset=".25" stop-color="#fff" stop-opacity=".15"/><stop offset="1" stop-color="#fff" stop-opacity=".4"/></linearGradient></defs>
<rect x="56" y="22" width="188" height="34" rx="10" fill="#D10F6A"/><rect x="56" y="22" width="188" height="12" rx="6" fill="#F05A9C"/>
<path d="M68 56h164l12 14H56z" fill="#F7A21B"/>
<g clip-path="url(#jar-clip)">{''.join(circles)}</g>
<path d="M40 70h220v190c0 22-18 40-40 40H80c-22 0-40-18-40-40z" fill="url(#glass)" stroke="#5B2A86" stroke-width="4"/>
<path d="M62 92v150" stroke="#fff" stroke-width="8" stroke-linecap="round" opacity=".7"/>
<rect x="88" y="150" width="124" height="54" rx="10" fill="#FFF7FA" stroke="#5B2A86" stroke-width="3"/>
<text x="150" y="176" text-anchor="middle" class="jar__label">10,000</text>
<text x="150" y="194" text-anchor="middle" class="jar__sub">LADOO GOAL</text></svg>"""


def wheel():
    n = len(CATEGORIES)
    seg = 360 / n
    parts = []
    for i, c in enumerate(CATEGORIES):
        a0, a1 = math.radians(i * seg - 90), math.radians((i + 1) * seg - 90)
        x0, y0, x1, y1 = 150 * math.cos(a0), 150 * math.sin(a0), 150 * math.cos(a1), 150 * math.sin(a1)
        mid = i * seg + seg / 2
        # Labels on the lower half are turned the other way so they never read upside down.
        flip = 90 < mid < 270
        rot, y_hi, y_en = (mid + 180, 114, 83) if flip else (mid, -92, -70)
        parts.append(f'<path d="M0 0L{x0:.2f} {y0:.2f}A150 150 0 0 1 {x1:.2f} {y1:.2f}Z" fill="{c["color"]}"/>'
                     f'<g transform="rotate({rot:.2f})" fill="{text_on(c["color"])}"><text y="{y_hi}" text-anchor="middle" class="wheel__hi" lang="hi">{c["hi"]}</text>'
                     f'<text y="{y_en}" text-anchor="middle" class="wheel__en">{SHORT_LABEL[c["key"]]}</text></g>')
    studs = "".join(f'<circle cx="{144 * math.cos(math.radians(k * 360 / 28)):.2f}" cy="{144 * math.sin(math.radians(k * 360 / 28)):.2f}" r="3.2"/>' for k in range(28))
    return f"""<div class="wheel-wrap"><svg class="wheel-pointer" viewBox="0 0 40 46" aria-hidden="true"><path d="M20 46 2 8a18 18 0 1 1 36 0z" fill="#5B2A86"/><circle cx="20" cy="17" r="7" fill="#FFD23F"/></svg>
<svg class="wheel" viewBox="-160 -160 320 320" aria-hidden="true" focusable="false"><circle r="158" fill="#5B2A86"/>
<g class="wheel__spin" id="wheel-spin">{''.join(parts)}<g fill="#FFD23F">{studs}</g></g>
<circle r="34" fill="#FFF7FA" stroke="#5B2A86" stroke-width="5"/><text y="7" text-anchor="middle" class="wheel__center">?</text></svg></div>"""


def recipe_card(it, extra_cls=""):
    c = CAT[it["cat"]]
    fests = " ".join(it["fests"])
    badge = '<span class="badge-short">Short</span>' if it["kind"] == "short" else ""
    search = escape(f'{it["en"]} {it["hi"]} {c["en"]} {" ".join(FEST[f]["en"] for f in it["fests"])}'.lower())
    return f"""<article class="recipe-card {extra_cls}" data-cat="{it['cat']}" data-fests="{fests}" data-kind="{it['kind']}" data-views="{it['views']}" data-search="{search}">
<div class="recipe-card__media"><img src="{it['img']}" alt="" loading="lazy" decoding="async" width="{640 if it['kind'] == 'video' else 360}" height="{360 if it['kind'] == 'video' else 640}">{badge}<span class="play-dot">{icon('play')}</span></div>
<div class="recipe-card__body"><span class="chip" style="--c:{c['color']}">{escape(c['en'])}</span>
<h3 class="recipe-card__title"><a href="{it['url']}" data-play="{it['id']}" data-kind="{it['kind']}" data-title="{escape(it['en'])}">{escape(it['en'])}</a></h3>
<p class="recipe-card__hi" lang="hi">{it['hi']}</p><p class="recipe-card__meta">{views(it['views'])}</p></div></article>"""


def shelf_item(it):
    return f"""<li class="shelf__item"><a href="{it['url']}" data-play="{it['id']}" data-kind="{it['kind']}" data-title="{escape(it['en'])}">
<span class="shelf__img"><img src="{it['img']}" alt="" loading="lazy" decoding="async" width="360" height="640"></span>
<span class="tag"><span class="tag__name">{escape(it['en'])}</span><span class="tag__price">{views(it['views'])}</span></span></a></li>"""


def stand_item(it):
    return f"""<li class="stand"><a href="{it['url']}" data-play="{it['id']}" data-kind="{it['kind']}" data-title="{escape(it['en'])}">
<span class="stand__img"><img src="{it['img']}" alt="" loading="lazy" decoding="async" width="640" height="360"></span><span class="stand__plate" aria-hidden="true"></span>
<span class="stand__name">{escape(it['en'])}</span><span class="stand__meta">{views(it['views'])}</span></a></li>"""


def plate_item(rank, it):
    return f"""<li class="plate-card"><a href="{it['url']}" data-play="{it['id']}" data-kind="{it['kind']}" data-title="{escape(it['en'])}">
<span class="plate"><img src="{it['img']}" alt="" loading="lazy" decoding="async" width="640" height="360"></span>
<span class="rank" aria-label="Rank {rank}">#{rank}</span><span class="plate-card__name">{escape(it['en'])}</span>
<span class="plate-card__hi" lang="hi">{it['hi']}</span><span class="plate-card__meta">{views(it['views'])}</span></a></li>"""


def festival_card(f):
    items = [i for i in ALL if f["key"] in i["fests"]]
    items.sort(key=lambda i: (i["kind"] != "video", -i["views"]))
    links = "".join(
        f'<li><a href="{i["url"]}" data-play="{i["id"]}" data-kind="{i["kind"]}" data-title="{escape(i["en"])}">'
        f'<img src="{i["img"]}" alt="" loading="lazy" width="96" height="54"><span>{escape(i["en"])}</span></a></li>' for i in items[:4])
    return f"""<li class="fest" data-months="{','.join(map(str, f['months']))}" style="--c:{f['color']};--t:{text_on(f['color'])}">
<div class="fest__top"><p class="fest__hi" lang="hi">{f['hi']}</p><h3 class="fest__en">{escape(f['en'])}</h3><p class="fest__when">{escape(f['when'])}</p>
<p class="fest__now" hidden>In season now</p></div><ul class="fest__list">{links}</ul></li>"""


def thali():
    picks = ["dwKv-0gZwRY", "Cv2dyFZ3sPQ", "d2DpmsP29jI", "1zH4ukMflJo", "iubLfRb9dew", "3OA_xz2O7WM", "N0n_1d4kDVM"]
    bowls = "".join(f'<span class="katori-img" style="--i:{k}"><img src="{BY_ID[v]["img"]}" alt="" width="200" height="200"></span>' for k, v in enumerate(picks))
    return f"""<div class="thali" aria-hidden="true"><div class="thali__steam"><span></span><span></span><span></span></div>
<div class="thali__plate"><div class="thali__ring">{bowls}</div>
<span class="katori-img katori-img--center"><img src="{BY_ID['HsEw0jzgWVI']['img']}" alt="" width="320" height="320"></span></div>
<p class="thali__note">Rasmalai Modak Cake: 63K views</p></div>"""


def dabba():
    btns = []
    for i, c in enumerate(CATEGORIES):
        count = sum(1 for x in ALL if x["cat"] == c["key"])
        btns.append(f'<button type="button" class="katori" style="--i:{i};--c:{c["color"]};--t:{text_on(c["color"])}" data-filter="{c["key"]}" aria-pressed="false">'
                    f'<span class="katori__hi" lang="hi">{c["hi"]}</span><span class="katori__en">{SHORT_LABEL[c["key"]]}</span>'
                    f'<span class="visually-hidden">: {escape(c["en"])}, {count} recipes</span></button>')
    return f"""<div class="dabba" role="group" aria-label="Filter recipes by type"><div class="dabba__tin">
{''.join(btns)}<button type="button" class="katori katori--all" data-filter="all" aria-pressed="true"><span class="katori__hi" lang="hi">सब</span><span class="katori__en">All {len(ALL)}</span></button></div></div>"""


def build():
    c = CHANNEL
    pct = c["subscribers"] / c["goal"] * 100
    longs = [i for i in ALL if i["kind"] == "video"]
    shorts = [i for i in ALL if i["kind"] == "short"]
    grid = sorted(ALL, key=lambda i: -i["views"])
    oven = [BY_ID[x] for x in ["wg1MF9vxToc", "u6Aql6jqp_Y", "N0n_1d4kDVM", "9AOnApUYvNA", "sniBruPRQnY", "hofmLGy2Egg",
                               "i9epGJ7Axig", "a9Mph5B8BF0", "U_0p-QmNIA4", "u1wsQ2GR1tU", "FDl-Z88X6lg", "D2ZhMsimUHs"]]
    stands = [BY_ID[x] for x in ["HsEw0jzgWVI", "dwKv-0gZwRY", "PUYuCA8PvMM", "eurQ3nzq6xE", "Bx9tbRBp5ZY", "2xDgzC2iHlg",
                                 "P9nwexqTgpc", "RS70qBgAHzo"]]
    food = sorted([i for i in longs if i["cat"] != "bakery"], key=lambda i: -i["views"])[:8]
    reel = shorts[:16]
    ld = {"@context": "https://schema.org", "@type": "Person", "name": c["owner"],
          "brand": {"@type": "Brand", "name": c["name"]}, "sameAs": [c["url"]],
          "description": "Vegetarian Indian recipes, festival sweets and decorated cakes on the INDIAN AROMAS YouTube channel."}
    collab_types = [
        ("users", "Cook-along with a creator", "Two kitchens, one recipe. A split-screen video or a recipe swap between our channels."),
        ("calendar", "Festival special series", "Holi, Ganesh Chaturthi, Diwali and Christmas menus, planned weeks ahead of the festival."),
        ("package", "Product & ingredient features", "Kitchen appliances, baking tools, spices and dairy, used honestly inside a real recipe."),
        ("cake", "Cake & decorating showcases", "Themed cakes for launches, celebrations and campaigns, from matki cakes to painting cakes."),
        ("trophy", "Recipe challenges", "Viewer challenges, regional recipe swaps and festival cook-offs that get people cooking along."),
    ]
    collab_cards = "".join(f'<li class="idea">{icon(ic)}<h3>{escape(t)}</h3><p>{escape(d)}</p></li>' for ic, t, d in collab_types)

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>INDIAN AROMAS by Deepali Saxena | Vegetarian Indian Recipes &amp; Cakes</title>
<meta name="description" content="Pure vegetarian Indian recipes, festival sweets and decorated cakes by Deepali Saxena. {c['videos']} videos on the INDIAN AROMAS YouTube channel. Subscribe and cook along!">
<meta name="theme-color" content="#D10F6A">
<meta property="og:type" content="website">
<meta property="og:title" content="INDIAN AROMAS by Deepali Saxena">
<meta property="og:description" content="Vegetarian Indian recipes, festival sweets and showstopper cakes. Subscribe on YouTube and cook along.">
<meta property="og:image" content="assets/img/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="assets/img/favicon.svg" type="image/svg+xml">
<link rel="preload" href="assets/fonts/yatra-one-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/mukta-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/css/style.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<aside class="ribbon" aria-label="Channel highlights"><p>Pure vegetarian <span aria-hidden="true">·</span> Festival specials <span aria-hidden="true">·</span> Cakes &amp; Indian sweets <span aria-hidden="true">·</span> <a href="{c['subscribe_url']}" target="_blank" rel="noopener">Subscribe free on YouTube</a></p></aside>
<header class="site-header">
<div class="wrap site-header__row">
<a class="brand" href="#top">{BOWL_MARK}<span class="brand__text"><span class="brand__name">INDIAN AROMAS</span><span class="brand__by">by Deepali Saxena</span></span></a>
<nav class="site-nav" aria-label="Main"><ul>
<li><a href="#recipes">Recipes</a></li><li><a href="#bakery">Bakery</a></li><li><a href="#festivals">Festivals</a></li><li><a href="#spin">Kya Banaun?</a></li><li><a href="#collab">Collaborate</a></li></ul></nav>
<a class="btn btn--yt site-header__sub" href="{c['subscribe_url']}" target="_blank" rel="noopener">{YT_ICON}<span>Subscribe</span></a>
</div>
<div class="toran" aria-hidden="true"></div>
</header>

<main id="main">
<section class="hero" id="top">
{mandala('mandala mandala--hero-a')}{mandala('mandala mandala--hero-b', petals=10)}
<div class="wrap hero__grid">
<div class="hero__text">
<p class="hand hero__kicker" lang="hi">घर का स्वाद, दिल से</p>
<h1 class="hero__title">From the <span class="hl hl--pink">kadai</span> to the <span class="hl hl--marigold">cake stand</span></h1>
<p class="hero__lede"><strong>INDIAN AROMAS</strong> by Deepali Saxena is a pure vegetarian home kitchen on YouTube: halwai-style sweets, everyday sabzi and dal, street-food favourites, festival specials and cakes decorated for celebrations, all made step by step.</p>
<div class="btn-row">
<a class="btn btn--yt btn--lg" href="{c['subscribe_url']}" target="_blank" rel="noopener">{YT_ICON}<span>Subscribe on YouTube</span></a>
<a class="btn btn--outline btn--lg" href="#recipes">{icon('search')}<span>Find a recipe</span></a></div>
<ul class="stats"><li><strong>{c['videos']}</strong> videos</li><li><strong>{c['subscribers_label']}</strong> subscribers</li><li><strong>63K</strong> views on the Modak Cake</li></ul>
</div>
{thali()}
</div></section>

<section class="goal" id="subscribe" aria-labelledby="goal-title">
<div class="wrap goal__grid">
<div class="goal__jar">{ladoo_jar()}</div>
<div class="goal__text">
<p class="hand" lang="hi">आइए, लड्डू का डिब्बा भरें!</p>
<h2 id="goal-title" class="section-title">Help fill the ladoo jar</h2>
<p class="lede">Each ladoo is 100 subscribers. The jar is <strong>{pct:.0f}% full</strong>, with {c['subscribers']:,} food lovers on the way to {c['goal']:,}. One click adds you to the next ladoo.</p>
<div class="progress" role="img" aria-label="{c['subscribers']:,} of {c['goal']:,} subscribers, {pct:.0f} percent"><span style="width:{pct:.1f}%"></span></div>
<p class="progress__labels"><span>{c['subscribers']:,} now</span><span>Goal {c['goal']:,}</span></p>
<ul class="reasons">
<li>{icon('leaf')}<span><strong>100% vegetarian</strong> recipes for every day and every festival</span></li>
<li>{icon('calendar')}<span><strong>Festival specials</strong> posted in time to cook them</span></li>
<li>{icon('cake')}<span><strong>Cakes and decorating tips</strong> from a home baker</span></li></ul>
<div class="btn-row"><a class="btn btn--yt btn--lg" href="{c['subscribe_url']}" target="_blank" rel="noopener">{YT_ICON}<span>Add my ladoo: Subscribe</span></a>
<button type="button" class="btn btn--ghost" data-share>{icon('share')}<span>Share with family</span></button></div>
<p class="fineprint">Subscriber count as of {c['as_of']}.</p>
</div></div></section>

<section class="explorer" id="recipes" aria-labelledby="recipes-title">
<div class="wrap">
<div class="explorer__head">
{dabba()}
<div class="explorer__intro">
<p class="hand" lang="hi">मसाला डब्बा खोलिए</p>
<h2 id="recipes-title" class="section-title">Open the masala dabba</h2>
<p class="lede">Every Indian kitchen has a round steel spice box. Ours holds {len(ALL)} recipes instead. Tap a katori (bowl) to see that kind of recipe, or search below.</p>
<label class="search" for="recipe-search">{icon('search')}<span class="visually-hidden">Search recipes</span>
<input id="recipe-search" type="search" placeholder="Search: paneer, cake, जलेबी..." autocomplete="off"></label>
<p class="explorer__status" id="explorer-status" aria-live="polite">Showing all {len(ALL)} recipes, most watched first.</p>
</div></div>
<div class="recipe-grid" id="recipe-grid">
{''.join(recipe_card(i) for i in grid)}
</div>
<p class="empty" id="recipe-empty" hidden>No recipes match that search. Try another word, or <a href="{c['url']}/search" target="_blank" rel="noopener">search the channel on YouTube</a>.</p>
<div class="center"><button type="button" class="btn btn--outline" id="show-more" hidden>Show more recipes</button></div>
</div></section>

<section class="bakery" id="bakery" aria-labelledby="bakery-title">
<div class="wrap">
<div class="section-head section-head--light">
<p class="hand" lang="hi">कुछ मीठा हो जाए!</p>
<h2 id="bakery-title" class="section-title">From the oven</h2>
<p class="lede">Tea-time cakes, cupcakes, bomboloni and showstopper celebration cakes, baked and decorated at home.</p></div>
<div class="cabinet">
<p class="cabinet__sign"><span>Indian Aromas</span> Bakery</p>
<div class="cabinet__glass">
<h3 class="shelf__title">Fresh today <span>(60-second Shorts)</span></h3>
<ul class="shelf">{''.join(shelf_item(i) for i in oven)}</ul>
<h3 class="shelf__title">Showstopper cakes <span>(full recipes)</span></h3>
<ul class="stands">{''.join(stand_item(i) for i in stands)}</ul>
</div></div></div></section>

<section class="kadai" id="kadai" aria-labelledby="kadai-title">
<div class="wrap">
<div class="section-head">
<p class="hand" lang="hi">कढ़ाई से सीधे</p>
<h2 id="kadai-title" class="section-title">From the kadai: fan favourites</h2>
<p class="lede">The Indian dishes viewers watch most, ranked by YouTube views.</p></div>
<ol class="plates">{''.join(plate_item(n + 1, i) for n, i in enumerate(food))}</ol>
</div></section>

<section class="festivals" id="festivals" aria-labelledby="fest-title">
<div class="wrap">
<div class="section-head">
<p class="hand" lang="hi">त्योहारों की थाली</p>
<h2 id="fest-title" class="section-title">Tyohar calendar</h2>
<p class="lede">A recipe for every festival and season. The ones in season right now are marked, so you can cook them in time.</p></div>
<ul class="fest-strip" id="fest-strip">{''.join(festival_card(f) for f in FESTIVALS)}</ul>
</div></section>

<section class="spin" id="spin" aria-labelledby="spin-title">
<div class="wrap spin__grid">
{wheel()}
<div class="spin__text">
<p class="hand" lang="hi">आज क्या बनाऊँ?</p>
<h2 id="spin-title" class="section-title">Kya banaun? Spin the tadka wheel</h2>
<p class="lede">Can't decide what to cook today? Spin the wheel and let the masala choose.</p>
<button type="button" class="btn btn--marigold btn--lg" id="spin-btn">{icon('shuffle')}<span>Spin the wheel</span></button>
<div class="spin__result" id="spin-result" aria-live="polite"><p class="spin__placeholder">Your recipe will appear here.</p></div>
</div></div></section>

<section class="reels" id="shorts" aria-labelledby="shorts-title">
<div class="wrap">
<div class="section-head section-head--row">
<div><p class="hand" lang="hi">एक मिनट की मिठास</p>
<h2 id="shorts-title" class="section-title">60-second treats</h2>
<p class="lede">Quick Shorts: jalebi, pickles, cupcakes and kitchen tricks.</p></div>
<a class="btn btn--outline" href="{c['url']}/shorts" target="_blank" rel="noopener">All Shorts on YouTube {icon('external')}</a></div>
<ul class="reel">{''.join(shelf_item(i) for i in reel)}</ul>
</div></section>

<section class="meet" id="about" aria-labelledby="meet-title">
<div class="wrap meet__grid">
<figure class="polaroid"><img src="assets/img/channel-logo.jpg" alt="The INDIAN AROMAS channel logo: a steaming bowl on a pink wooden background." width="400" height="400" loading="lazy"><figcaption class="hand">Namaste!</figcaption></figure>
<div class="meet__text">
<p class="hand">The cook behind the channel</p>
<h2 id="meet-title" class="section-title">Meet Deepali Saxena</h2>
<p class="lede">Deepali Saxena runs INDIAN AROMAS from her home kitchen. Over the past four years she has shared {c['videos']} videos: traditional sweets, everyday vegetarian meals, vrat recipes for fasting days and celebration cakes, many of them made for family festivals and birthdays.</p>
<blockquote class="quote"><p>“This is my channel ‘Indian Aromas’ which will delight you with some mouth watering Indian dishes (VEG).”</p><cite>From the INDIAN AROMAS channel</cite></blockquote>
<ul class="facts"><li><strong>{len(longs)}</strong> full recipes</li><li><strong>{c['videos'] - len(longs)}</strong> Shorts</li><li><strong>7</strong> kinds of recipes</li><li><strong>Hindi &amp; English</strong> titles</li></ul>
</div></div></section>

<section class="collab" id="collab" aria-labelledby="collab-title">
<div class="wrap">
<div class="section-head section-head--light">
<p class="hand" lang="hi">मिलकर कुछ नया बनाएं</p>
<h2 id="collab-title" class="section-title">Let's cook up a collaboration</h2>
<p class="lede">INDIAN AROMAS welcomes collaborations with food creators, home bakers and brands that suit a vegetarian Indian kitchen. Here are a few ideas to start with.</p></div>
<ul class="ideas">{collab_cards}</ul>
<div class="collab__grid">
<div class="why">
<h3>Why work with INDIAN AROMAS</h3>
<ul>
<li><strong>{c['subscribers_label']}</strong><span>subscribers who love vegetarian food</span></li>
<li><strong>63K</strong><span>views on the most-watched video</span></li>
<li><strong>{c['videos']}</strong><span>videos across sweets, meals and baking</span></li>
<li><strong>Festival-ready</strong><span>specials planned around Indian festivals</span></li></ul>
<p class="why__note">Prefer to just say hello? Leave a comment on the <a href="{c['url']}/videos" target="_blank" rel="noopener">latest video</a>. Deepali reads them.</p>
</div>
<form class="recipe-card-form" id="collab-form" novalidate>
<p class="recipe-card-form__tab">Collaboration recipe card</p>
<div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" required autocomplete="name"></div>
<div class="field"><label for="f-org">Channel, brand or business</label><input id="f-org" name="org" required autocomplete="organization"></div>
<div class="field"><label for="f-email">Your email</label><input id="f-email" name="email" type="email" required autocomplete="email"></div>
<div class="field"><label for="f-type">Kind of collaboration</label><select id="f-type" name="type">{''.join(f'<option>{escape(t)}</option>' for _, t, _ in collab_types)}<option>Something else</option></select></div>
<div class="field"><label for="f-idea">Your idea</label><textarea id="f-idea" name="idea" rows="4" required placeholder="Tell us what you'd like to make together."></textarea></div>
<div class="field"><label for="f-when">Timing</label><select id="f-when" name="when"><option>Flexible</option><option>This month</option><option>Before the next festival</option></select></div>
<p class="form-error" id="form-error" role="alert" hidden></p>
<button type="submit" class="btn btn--pink btn--lg">{icon('sparkles')}<span>Prepare my message</span></button>
<div class="form-done" id="form-done" hidden tabindex="-1">
<h3>Your message is ready</h3>
<p id="done-help"></p>
<label for="f-message" class="visually-hidden">Your collaboration message</label>
<textarea id="f-message" rows="8" readonly></textarea>
<div class="btn-row"><a class="btn btn--pink" id="send-email" hidden>{icon('mail')}<span>Send by email</span></a>
<button type="button" class="btn btn--outline" id="copy-message">{icon('copy')}<span>Copy message</span></button>
<a class="btn btn--yt" href="{c['url']}/videos" target="_blank" rel="noopener">{YT_ICON}<span>Open the channel</span></a></div>
<p class="copy-status" id="copy-status" aria-live="polite"></p></div>
</form></div></div></section>

<section class="bell" aria-labelledby="bell-title">
<div class="wrap bell__inner">{icon('bell', 'icon bell__icon')}
<div><h2 id="bell-title" class="section-title">Subscribe and ring the bell</h2>
<p>New sweets, cakes and festival specials, straight to your YouTube home page. Cooked one of the recipes? Tell Deepali how it turned out in the comments, and share it with <strong>#IndianAromas</strong>.</p></div>
<a class="btn btn--light btn--lg" href="{c['subscribe_url']}" target="_blank" rel="noopener">{YT_ICON}<span>Subscribe on YouTube</span></a></div></section>
</main>

<footer class="site-footer">
<div class="wrap site-footer__grid">
<div><a class="brand brand--footer" href="#top">{BOWL_MARK}<span class="brand__text"><span class="brand__name">INDIAN AROMAS</span><span class="brand__by">by Deepali Saxena</span></span></a>
<p>Pure vegetarian Indian recipes, festival sweets and home-baked cakes.</p></div>
<nav aria-label="Footer"><ul><li><a href="#recipes">All recipes</a></li><li><a href="#bakery">Bakery</a></li><li><a href="#kadai">Fan favourites</a></li><li><a href="#festivals">Festival calendar</a></li><li><a href="#shorts">Shorts</a></li><li><a href="#collab">Collaborate</a></li></ul></nav>
<div><p><a href="{c['url']}" target="_blank" rel="noopener">youtube.com/{c['handle']}</a></p><p class="fineprint">All food photos are from INDIAN AROMAS videos.<br>© 2026 INDIAN AROMAS by Deepali Saxena</p></div>
</div></footer>

<aside aria-label="Subscribe"><a class="float-sub" id="float-sub" href="{c['subscribe_url']}" target="_blank" rel="noopener">{YT_ICON}<span>Subscribe</span></a></aside>

<dialog class="player" id="player" aria-labelledby="player-title">
<div class="player__head"><h2 id="player-title" class="player__title">Recipe</h2>
<button type="button" class="player__close" id="player-close">{icon('x')}<span class="visually-hidden">Close video</span></button></div>
<div class="player__frame" id="player-frame"></div>
<div class="player__foot"><p>Enjoying it? Subscribe so you never miss a recipe.</p>
<div class="btn-row"><a class="btn btn--yt" href="{c['subscribe_url']}" target="_blank" rel="noopener">{YT_ICON}<span>Subscribe</span></a>
<a class="btn btn--outline" id="player-yt" href="{c['url']}" target="_blank" rel="noopener">Watch on YouTube {icon('external')}</a></div></div>
</dialog>

<script>window.IA_CONFIG = {json.dumps({"email": c["collab_email"], "channel": c["url"], "subscribe": c["subscribe_url"], "categories": {k["key"]: k["en"] for k in CATEGORIES}})};</script>
<script src="assets/js/app.js" defer></script>
</body>
</html>
"""
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"index.html written: {len(ALL)} recipes ({len(longs)} videos, {len(shorts)} shorts), {len(html) // 1024} KB")


if __name__ == "__main__":
    build()
