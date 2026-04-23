#!/usr/bin/env python3
"""Scans Images/ and generates index.html."""

import os
import urllib.parse
from PIL import Image

IMAGES_DIR = "Images"
OUTPUT = "index.html"
SUPPORTED = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


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

    photo_items = []
    for location, photos in locations:
        for photo in photos:
            path = os.path.join(IMAGES_DIR, location, photo)
            src = f"{IMAGES_DIR}/{urllib.parse.quote(location)}/{urllib.parse.quote(photo)}"
            with Image.open(path) as img:
                w, h = img.size
            orientation = "portrait" if h > w else "landscape"
            photo_items.append(
                f'    <figure class="{orientation}">\n'
                f'      <img src="{src}" alt="{location}" loading="lazy">\n'
                f'      <figcaption>{location}</figcaption>\n'
                f'    </figure>'
            )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Old Houses on Film</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;500&family=Inter:wght@400&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg: #FAFFEF;
      --fg: rgb(24, 54, 107);
      --fg-muted: rgba(24, 54, 107, 0.65);
      --toggle-bg: rgba(24, 54, 107, 0.1);
      --toggle-hover: rgba(24, 54, 107, 0.2);
    }}

    @media (prefers-color-scheme: dark) {{
      :root:not([data-theme="light"]) {{
        --bg: #0f1f3d;
        --fg: #FAFFEF;
        --fg-muted: rgba(250, 255, 239, 0.6);
        --toggle-bg: rgba(250, 255, 239, 0.1);
        --toggle-hover: rgba(250, 255, 239, 0.2);
      }}
    }}

    :root[data-theme="dark"] {{
      --bg: #0f1f3d;
      --fg: #FAFFEF;
      --fg-muted: rgba(250, 255, 239, 0.6);
      --toggle-bg: rgba(250, 255, 239, 0.1);
      --toggle-hover: rgba(250, 255, 239, 0.2);
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
      font-weight: 500;
      margin-bottom: 0.4rem;
    }}

    header p {{
      font-family: 'Inter', sans-serif;
      font-size: 0.95rem;
      color: var(--fg-muted);
    }}

    .gallery {{
      display: flex;
      flex-direction: column;
      gap: 2.5rem;
    }}

    figure {{
      display: flex;
      flex-direction: column;
      margin: 0 auto;
    }}

    figure.portrait {{
      max-width: 525px;
    }}

    figure img {{
      width: 100%;
      height: auto;
      display: block;
    }}

    figcaption {{
      font-family: 'Inter', sans-serif;
      margin-top: 0.5rem;
      font-size: 0.85rem;
      color: var(--fg-muted);
    }}

    #theme-toggle {{
      position: fixed;
      bottom: 1.5rem;
      right: 1.5rem;
      width: 2.5rem;
      height: 2.5rem;
      border-radius: 50%;
      border: none;
      background: var(--toggle-bg);
      color: var(--fg);
      font-size: 1.1rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.2s;
    }}

    #theme-toggle:hover {{
      background: var(--toggle-hover);
    }}
  </style>
</head>
<body>
  <header>
    <h1>Old Houses on Film</h1>
    <p>Taken by Amanda Miller &bull; Minolta X-700</p>
  </header>
  <main class="gallery">
{chr(10).join(photo_items)}
  </main>

  <button id="theme-toggle" aria-label="Toggle dark mode"></button>

  <script>
    const root = document.documentElement;
    const btn = document.getElementById('theme-toggle');
    const ICONS = {{ light: '☀️', dark: '🌙' }};

    function isDark() {{
      if (root.dataset.theme) return root.dataset.theme === 'dark';
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }}

    function applyTheme(dark) {{
      root.dataset.theme = dark ? 'dark' : 'light';
      btn.textContent = dark ? ICONS.light : ICONS.dark;
      localStorage.setItem('theme', dark ? 'dark' : 'light');
    }}

    // Restore saved preference
    const saved = localStorage.getItem('theme');
    if (saved) {{
      applyTheme(saved === 'dark');
    }} else {{
      btn.textContent = isDark() ? ICONS.light : ICONS.dark;
    }}

    btn.addEventListener('click', () => applyTheme(!isDark()));
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
