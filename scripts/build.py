"""
Parse playlists/*.toml and
- outputs "API" files to `build/api`
- outputs html files to `build/playlists`

Usage:
$ python scripts/build.py
"""
import json
import os
import toml
import requests

from pathlib import Path
from jinja2 import Template

with open('scripts/_playlist.html') as tfile:
    template = Template(tfile.read())

# dataset attributes to expose on our "API"
DATASET_ATTRS = [
    "id",
    "title",
    "description",
    "owner",
    "organization"
]
BUILD_OUT_DIR = os.getenv('BUILD_OUT_DIR', 'build')
API_OUT_DIR = os.getenv('API_OUT_DIR', 'api')
PLAYLIST_OUT_DIR = os.getenv('PLAYLIST_OUT_DIR', 'playlists')
api_out_dir = Path(BUILD_OUT_DIR) / Path(API_OUT_DIR)
playlist_out_dir = Path(BUILD_OUT_DIR) / Path(PLAYLIST_OUT_DIR)

path = Path("playlists/")

for playlist in path.glob("*.toml"):
    data = toml.load(playlist)
    datasets = []
    for did in data.get("datasets", []):
        r = requests.get(f"https://www.data.gouv.fr/api/1/datasets/{did}")
        if r.ok:
            d_data = r.json()
            dataset = {k: d_data.get(k) for k in DATASET_ATTRS}
            datasets.append(dataset)
        else:
            print(f"Wrong response ({r.status_code}) for '{did}'")
    playlist_api = {
        "slug": playlist.stem,
        "title": data.get("title"),
        "datasets": datasets
    }

    # write API
    api_out_dir.mkdir(exist_ok=True, parents=True)
    out_path = api_out_dir / f'{playlist.stem}.json'
    with out_path.open('w') as out_file:
        out_file.write(json.dumps(playlist_api))

    # write HTML
    playlist_out_dir = playlist_out_dir / playlist.stem
    playlist_out_dir.mkdir(exist_ok=True, parents=True)
    out_path = playlist_out_dir / 'index.html'
    html = template.render(playlist=playlist_api)
    with out_path.open('w') as out_file:
        out_file.write(html)
