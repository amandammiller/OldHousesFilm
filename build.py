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

    body {{
      background-color: #FAFFEF;
      color: rgb(24, 54, 107);
      max-width: 720px;
      margin: 0 auto;
      padding: 2rem 1rem;
    }}

    header {{
      margin-bottom: 2.5rem;
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
    }}

    header p + p {{
      margin-top: 0.25rem;
      font-size: 0.85rem;
      opacity: 0.75;
    }}

    .gallery {{
      display: flex;
      flex-direction: column;
      gap: 2.5rem;
    }}

    figure {{
      display: flex;
      flex-direction: column;
    }}

    figure.portrait {{
      max-width: 420px;
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
    }}
  </style>
</head>
<body>
  <header>
    <h1>Old Houses on Film</h1>
    <p>Taken on a Minolta X-700</p>
    <p>Photos by Amanda Miller</p>
  </header>
  <main class="gallery">
{chr(10).join(photo_items)}
  </main>
</body>
</html>
"""

    with open(OUTPUT, "w") as f:
        f.write(html)

    total = sum(len(p) for _, p in locations)
    print(f"Built {OUTPUT} — {len(locations)} locations, {total} photos")


if __name__ == "__main__":
    build()
