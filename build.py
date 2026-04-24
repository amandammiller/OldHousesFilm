#!/usr/bin/env python3
"""Scans Images/ and generates index.html."""

import os
import urllib.parse
from PIL import Image, ImageOps

IMAGES_DIR = "Images"
WEB_DIR = "Images_web"
OUTPUT = "index.html"
SUPPORTED = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_W = {"landscape": 1800, "portrait": 1050}
WEBP_QUALITY = 82


def make_web_image(src_path, location, filename, orientation):
    """Generate a resized WebP copy and return its URL-encoded src path."""
    dst_dir = os.path.join(WEB_DIR, location)
    os.makedirs(dst_dir, exist_ok=True)
    stem = os.path.splitext(filename)[0]
    dst_path = os.path.join(dst_dir, stem + ".webp")

    if not os.path.exists(dst_path) or os.path.getmtime(src_path) > os.path.getmtime(dst_path):
        with Image.open(src_path) as img:
            img = ImageOps.exif_transpose(img)  # bake in rotation
            max_w = MAX_W[orientation]
            if img.width > max_w:
                ratio = max_w / img.width
                img = img.resize((max_w, int(img.height * ratio)), Image.LANCZOS)
            img.save(dst_path, "WEBP", quality=WEBP_QUALITY)

    return f"{WEB_DIR}/{urllib.parse.quote(location)}/{urllib.parse.quote(stem + '.webp')}"


def get_locations():
    locations = []
    for name in sorted(os.listdir(IMAGES_DIR)):
        path = os.path.join(IMAGES_DIR, name)
        if not os.path.isdir(path):
            continue
        photos = sorted(
            f for f in os.listdir(path)
            if os.path.splitext(f)[1].lower() in SUPPORTED
        )
        if photos:
            locations.append((name, photos))
    return locations


def build():
    locations = get_locations()
    location_names = [name for name, _ in locations]

    photo_items = []
    for location, photos in locations:
        for photo in photos:
            path = os.path.join(IMAGES_DIR, location, photo)
            fallback_src = f"{IMAGES_DIR}/{urllib.parse.quote(location)}/{urllib.parse.quote(photo)}"
            with Image.open(path) as img:
                w, h = img.size
                exif_orientation = img.getexif().get(274, 1)
            if exif_orientation in (5, 6, 7, 8):
                w, h = h, w
            orientation = "portrait" if h > w else "landscape"
            webp_src = make_web_image(path, location, photo, orientation)
            photo_items.append(
                f'    <figure class="{orientation}" data-location="{location}">\n'
                f'      <picture>\n'
                f'        <source srcset="{webp_src}" type="image/webp">\n'
                f'        <img src="{fallback_src}" alt="{location}" loading="lazy">\n'
                f'      </picture>\n'
                f'      <figcaption>{location}</figcaption>\n'
                f'    </figure>'
            )

    side_nav_buttons = '\n'.join(
        f'    <button data-filter="{name}">{name}</button>'
        for name in location_names
    )

    dropdown_options = '\n'.join(
        f'        <option value="{name}">{name}</option>'
        for name in location_names
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Old Houses on Film</title>
  <meta property="og:title" content="Old Houses on Film | Photos by Amanda Miller">
  <meta property="og:description" content="photos by Amanda Miller · Minolta X-700">
  <meta property="og:type" content="website">
  <meta property="og:url" content="https://amandammiller.github.io/OldHousesFilm">
  <meta property="og:image" content="https://amandammiller.github.io/OldHousesFilm/Images/Cotswolds%2C%20England/01--01.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://amandammiller.github.io/OldHousesFilm/Images/Cotswolds%2C%20England/01--01.jpg">
  <link rel="icon" type="image/png" href="Images/Favicon_light.png" media="(prefers-color-scheme: light)">
  <link rel="icon" type="image/png" href="Images/Favicon_dark.png" media="(prefers-color-scheme: dark)">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@300;400&family=Inter:wght@400&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg: #FAFFEF;
      --fg: rgb(24, 54, 107);
      --fg-muted: #4F74B5;
      --accent: #4F74B5;
      --toggle-bg: #FAFFEF;
      --toggle-border: #4F74B5;
      --toggle-inactive: #4F74B5;
    }}

    @media (prefers-color-scheme: dark) {{
      :root:not([data-theme="light"]) {{
        --bg: #0f1f3d;
        --fg: #FAFFEF;
        --fg-muted: rgba(250, 255, 239, 0.6);
        --toggle-bg: #0f1f3d;
        --toggle-border: #4F74B5;
        --toggle-inactive: #FAFFEF;
      }}
    }}

    :root[data-theme="dark"] {{
      --bg: #0f1f3d;
      --fg: #FAFFEF;
      --fg-muted: rgba(250, 255, 239, 0.6);
      --toggle-bg: #0f1f3d;
      --toggle-border: #4F74B5;
      --toggle-inactive: #FAFFEF;
    }}

    body {{
      background-color: var(--bg);
      color: var(--fg);
      max-width: 900px;
      margin: 0 auto;
      padding: 2rem 1rem 5rem;
      transition: background-color 0.3s, color 0.3s;
    }}

    header {{
      margin-bottom: 2.5rem;
      text-align: center;
    }}

    header h1 {{
      font-family: 'EB Garamond', Garamond, serif;
      font-size: 2.4rem;
      font-weight: 300;
      text-transform: lowercase;
      margin-bottom: 0.4rem;
    }}

    header p {{
      font-family: 'Inter', sans-serif;
      font-size: 0.95rem;
      color: var(--fg-muted);
    }}

    /* ── Mobile/tablet dropdown ── */
    .mobile-nav {{
      display: flex;
      position: fixed;
      bottom: 0.75rem;
      left: 0.75rem;
    }}

    .mobile-nav select {{
      font-family: 'Inter', sans-serif;
      font-size: 0.85rem;
      color: var(--fg);
      background: var(--bg);
      border: 1.5px solid var(--accent);
      border-radius: 999px;
      height: 34px;
      padding: 0 2.2rem 0 1.1rem;
      appearance: none;
      -webkit-appearance: none;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6'%3E%3Cpath d='M1 1l4 4 4-4' stroke='%234F74B5' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
      background-repeat: no-repeat;
      background-position: right 0.8rem center;
      cursor: pointer;
    }}

    /* ── Desktop floating left nav ── */
    .side-nav {{
      display: none;
      position: fixed;
      left: 2rem;
      top: 50%;
      transform: translateY(-50%);
      flex-direction: column;
      gap: 0.4rem;
      align-items: flex-start;
    }}

    .side-nav button {{
      font-family: 'Inter', sans-serif;
      font-size: 0.78rem;
      background: none;
      border: none;
      color: var(--fg-muted);
      cursor: pointer;
      padding: 0.25rem 0.7rem;
      border-radius: 999px;
      text-align: left;
      white-space: nowrap;
      transition: color 0.15s, background 0.15s;
    }}

    .side-nav button:hover {{ color: var(--fg); }}

    .side-nav button:focus-visible {{
      outline: 2px solid var(--accent);
      outline-offset: 2px;
    }}

    .side-nav button.active {{
      background: var(--accent);
      color: #FAFFEF;
    }}

    @media (min-width: 380px) {{
      #theme-toggle {{ right: 0.75rem; }}
    }}

    @media (max-width: 1334px) {{
      body {{ padding-left: 1.875rem; padding-right: 1.875rem; }}
      .mobile-nav select {{ height: 36px; }}
    }}

    @media (min-width: 1335px) {{
      .side-nav {{ display: flex; }}
      .mobile-nav {{ display: none; }}
    }}

    @media (prefers-reduced-motion: reduce) {{
      body, .gallery, #theme-toggle, #theme-toggle button {{ transition: none; }}
    }}

    @media (max-width: 379px) {{
      .mobile-nav {{
        bottom: 3.5rem;
        left: 50%;
        transform: translateX(-50%);
      }}
      #theme-toggle {{
        left: 50%;
        transform: translateX(-50%);
      }}
    }}

    /* ── Gallery ── */
    .gallery {{
      display: flex;
      flex-direction: column;
      gap: 6rem;
      transition: opacity 0.15s ease-in-out;
    }}

    .gallery.fading {{ opacity: 0; }}

    figure {{
      display: flex;
      flex-direction: column;
      margin: 0 auto;
    }}

    figure.portrait {{ max-width: 525px; }}

    figure img {{
      width: 100%;
      height: auto;
      display: block;
    }}

    figure[hidden] {{ display: none; }}

    figcaption {{
      font-family: 'Inter', sans-serif;
      margin-top: 0.5rem;
      font-size: 0.85rem;
      color: var(--fg-muted);
    }}

    /* ── Theme toggle ── */
    #theme-toggle {{
      position: fixed;
      bottom: 0.75rem;
      display: flex;
      align-items: center;
      background: var(--toggle-bg);
      border: 1.5px solid var(--toggle-border);
      transition: background 0.3s, border-color 0.3s;
      border-radius: 999px;
      padding: 3px;
      gap: 2px;
      font-family: 'Inter', sans-serif;
      font-size: 0.8rem;
    }}

    #theme-toggle button {{
      padding: 0 0.85rem;
      height: 28px;
      border-radius: 999px;
      border: none;
      background: none;
      color: var(--toggle-inactive);
      font-family: inherit;
      font-size: inherit;
      cursor: pointer;
      transition: background 0.3s, color 0.3s;
      user-select: none;
    }}

    #theme-toggle button:focus-visible {{
      outline: 2px solid var(--accent);
      outline-offset: 2px;
    }}

    #theme-toggle button.active {{
      background: #4F74B5;
      color: #FAFFEF;
    }}
  </style>
</head>
<body>

  <nav class="side-nav" aria-label="Filter by location">
    <button class="active" data-filter="all">All locations</button>
{side_nav_buttons}
  </nav>

  <header>
    <h1>Old Houses on Film</h1>
    <p>photos by Amanda Miller ✳&#xFE0E; Minolta X-700</p>
  </header>

  <div class="mobile-nav">
    <select id="location-select" aria-label="Filter by location">
      <option value="all">All locations</option>
{dropdown_options}
    </select>
  </div>

  <main class="gallery">
{chr(10).join(photo_items)}
  </main>

  <div id="theme-toggle" role="group" aria-label="Color theme">
    <button id="opt-light" aria-pressed="false">Light</button>
    <button id="opt-dark" aria-pressed="false">Dark</button>
  </div>

  <script>
    // ── Theme ──
    const root = document.documentElement;
    const optLight = document.getElementById('opt-light');
    const optDark  = document.getElementById('opt-dark');

    function isDark() {{
      if (root.dataset.theme) return root.dataset.theme === 'dark';
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }}

    function applyTheme(dark) {{
      root.dataset.theme = dark ? 'dark' : 'light';
      optLight.classList.toggle('active', !dark);
      optDark.classList.toggle('active', dark);
      optLight.setAttribute('aria-pressed', String(!dark));
      optDark.setAttribute('aria-pressed', String(dark));
      localStorage.setItem('theme', dark ? 'dark' : 'light');
    }}

    const saved = localStorage.getItem('theme');
    applyTheme(saved ? saved === 'dark' : isDark());

    // Initialise aria-pressed on side nav
    document.querySelectorAll('.side-nav button').forEach(btn => {{
      btn.setAttribute('aria-pressed', btn.classList.contains('active') ? 'true' : 'false');
    }});

    optLight.addEventListener('click', () => applyTheme(false));
    optDark.addEventListener('click',  () => applyTheme(true));

    // ── Filter ──
    const figures = Array.from(document.querySelectorAll('.gallery figure'));
    const gallery = document.querySelector('.gallery');

    function filter(value) {{
      gallery.classList.add('fading');
      setTimeout(() => {{
        figures.forEach(fig => {{
          fig.hidden = value !== 'all' && fig.dataset.location !== value;
        }});
        gallery.classList.remove('fading');
        window.scrollTo({{ top: 0, behavior: 'smooth' }});
      }}, 150);
    }}

    // Side nav
    document.querySelectorAll('.side-nav button').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.side-nav button').forEach(b => {{
          b.classList.remove('active');
          b.setAttribute('aria-pressed', 'false');
        }});
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');
        document.getElementById('location-select').value = btn.dataset.filter;
        filter(btn.dataset.filter);
      }});
    }});

    // Dropdown
    document.getElementById('location-select').addEventListener('change', e => {{
      const val = e.target.value;
      document.querySelectorAll('.side-nav button').forEach(b => {{
        b.classList.toggle('active', b.dataset.filter === val);
      }});
      filter(val);
    }});
  </script>
</body>
</html>
"""

    with open(OUTPUT, "w") as f:
        f.write(html)

    total = sum(len(p) for _, p in locations)
    print(f"Built {OUTPUT} — {len(locations)} locations, {total} photos")


if __name__ == "__main__":
    build()
