"""One-off: Mediterranean / Atlantic land outline for the Mincemeat film.

Source: Natural Earth 10m land (public domain).
Usage: python3 tools/geo_prep.py <ne_10m_land.geojson>
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "falklands", "tools"))
from geo_prep import reduce, rings_of  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "geo")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    med = reduce(rings_of(json.load(open(sys.argv[1]))), 0.012, 0.002, bbox=(-14, 28, 32, 60))
    json.dump(med, open(os.path.join(OUT, "europe_med.json"), "w"), separators=(",", ":"))
    print(len(med), "rings", sum(len(r) for r in med), "points")
