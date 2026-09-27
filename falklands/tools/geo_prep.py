"""One-off: reduce raw coastline downloads to the small JSON files in assets/geo.

Sources (see RESEARCH.md):
  * geoBoundaries FLK ADM0 (high-resolution Falklands coastline, CC BY 4.0)
  * Natural Earth 50m / 10m land (public domain)

Usage: python3 tools/geo_prep.py <FLK_hi.geojson> <ne_50m_land.geojson> <ne_10m_land.geojson>
"""
import json
import os
import sys

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "geo")


def dp(points, tol):
    """Iterative Douglas-Peucker simplification."""
    pts = np.asarray(points, dtype=float)
    if len(pts) < 5:
        return pts
    keep = np.zeros(len(pts), dtype=bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        p, q = pts[a], pts[b]
        seg = pts[a + 1:b]
        d = q - p
        n = np.hypot(*d)
        if n == 0:
            dist = np.hypot(*(seg - p).T)
        else:
            dist = np.abs(d[0] * (seg[:, 1] - p[1]) - d[1] * (seg[:, 0] - p[0])) / n
        i = int(np.argmax(dist))
        if dist[i] > tol:
            k = a + 1 + i
            keep[k] = True
            stack.append((a, k))
            stack.append((k, b))
    return pts[keep]


def area(r):
    x, y = r[:, 0], r[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def rings_of(geojson):
    out = []
    for f in geojson["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            out.append(poly[0])  # outer rings only; lakes are irrelevant here
    return out


def reduce(rings, tol, min_area, bbox=None):
    res = []
    for r in rings:
        r = np.asarray(r, dtype=float)
        if bbox is not None:
            x0, y0, x1, y1 = bbox
            if r[:, 0].max() < x0 or r[:, 0].min() > x1 or r[:, 1].max() < y0 or r[:, 1].min() > y1:
                continue
        if area(r) < min_area:
            continue
        s = dp(r, tol)
        if len(s) >= 4:
            res.append([[round(x, 4), round(y, 4)] for x, y in s])
    return res


def main(flk, ne50, ne10):
    os.makedirs(OUT, exist_ok=True)
    flk_rings = rings_of(json.load(open(flk)))
    falk = reduce(flk_rings, 0.0012, 2e-6)
    json.dump(falk, open(os.path.join(OUT, "falklands.json"), "w"), separators=(",", ":"))
    print("falklands", len(falk), sum(len(r) for r in falk))

    world = reduce(rings_of(json.load(open(ne50))), 0.05, 0.02)
    json.dump(world, open(os.path.join(OUT, "world50.json"), "w"), separators=(",", ":"))
    print("world", len(world), sum(len(r) for r in world))

    # South Atlantic region (Argentina, Chile, South Georgia) from 10m data;
    # Falklands themselves come from the high-res file above.
    sa = reduce(rings_of(json.load(open(ne10))), 0.01, 0.0005, bbox=(-82, -62, -20, -20))
    sa = [r for r in sa if not (-62 < np.mean([p[0] for p in r]) < -57 and -53 < np.mean([p[1] for p in r]) < -50.5)]
    json.dump(sa, open(os.path.join(OUT, "southatlantic.json"), "w"), separators=(",", ":"))
    print("south atlantic", len(sa), sum(len(r) for r in sa))


if __name__ == "__main__":
    main(*sys.argv[1:4])
