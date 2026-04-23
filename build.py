#!/usr/bin/env python3
"""Scans Images/ and generates index.html."""

import os
import urllib.parse

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
            src = f"{IMAGES_DIR}/{urllib.parse.quote(location)}/{urllib.parse.quote(photo)}"
            photo_items.append(
                f'    <figure>\n'
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
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      font-family: sans-serif;
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem 1rem;
    }}

    header {{
      margin-bottom: 2.5rem;
    }}

    header h1 {{
      font-size: 2rem;
      margin-bottom: 0.4rem;
    }}

    header p {{
      font-size: 1rem;
      color: #555;
    }}

    .gallery {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1.5rem;
    }}

    figure {{
      display: flex;
      flex-direction: column;
    }}

    figure img {{
      width: 100%;
      height: auto;
      display: block;
    }}

    figcaption {{
      margin-top: 0.4rem;
      font-size: 0.85rem;
      color: #444;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Old Houses on Film</h1>
    <p>Taken on a Minolta X-700</p>
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
