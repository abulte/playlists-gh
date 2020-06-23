"""
Parse playlists/*.toml and outputs "API" files to `build/`

Usage:
$ python scripts/to_api.py
"""
import json
import os
import toml
import requests
from pathlib import Path

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
OUT_DIR = Path(BUILD_OUT_DIR) / Path(API_OUT_DIR)

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
    OUT_DIR.mkdir(exist_ok=True, parents=True)
    out_path = OUT_DIR / f'{playlist.stem}.json'
    with out_path.open('w') as out_file:
        out_file.write(json.dumps(playlist_api))
