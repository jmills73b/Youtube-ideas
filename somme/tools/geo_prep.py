"""One-off: build the small geo assets for the Somme film.

Sources:
  * Natural Earth 10m land and 10m European rivers (public domain)
  * French commune boundaries (github.com/gregoiredavid/france-geojson, from IGN
    ADMIN EXPRESS, Licence Ouverte) - used only to take village positions as
    commune centroids.

Usage: python3 tools/geo_prep.py <ne_10m_land> <ne_10m_rivers_europe> <communes-80> <communes-62>
"""
import json
import os
import sys
import unicodedata

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "falklands", "tools"))
from geo_prep import dp, reduce, rings_of  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "geo")

# (display name, commune name, departement); None commune = explicit coordinates
PLACES = [
    ("ALBERT", "Albert", "80"), ("BAPAUME", "Bapaume", "62"), ("THIEPVAL", "Thiepval", "80"),
    ("BEAUMONT-HAMEL", "Beaumont-Hamel", "80"), ("GOMMECOURT", "Gommecourt", "62"),
    ("HÉBUTERNE", "Hébuterne", "62"), ("LA BOISSELLE", "Ovillers-la-Boisselle", "80"),
    ("FRICOURT", "Fricourt", "80"), ("MAMETZ", "Mametz", "80"), ("MONTAUBAN", "Montauban-de-Picardie", "80"),
    ("MARICOURT", "Maricourt", "80"), ("POZIÈRES", "Pozières", "80"), ("LONGUEVAL", "Longueval", "80"),
    ("BAZENTIN", "Bazentin", "80"), ("FLERS", "Flers", "80"), ("GUILLEMONT", "Guillemont", "80"),
    ("GINCHY", "Ginchy", "80"), ("COMBLES", "Combles", "80"), ("COURCELETTE", "Courcelette", "80"),
    ("MARTINPUICH", "Martinpuich", "80"), ("LE SARS", "Sars", "62"), ("BEAUCOURT", "Beaucourt-sur-l'Ancre", "80"),
    ("GRANDCOURT", "Grandcourt", "80"), ("MIRAUMONT", "Miraumont", "80"), ("AUTHUILLE", "Authuille", "80"),
    ("AVELUY", "Aveluy", "80"), ("PÉRONNE", "Péronne", "80"), ("AMIENS", "Amiens", "80"),
    ("CONTALMAISON", "Contalmaison", "80"), ("GUEUDECOURT", "Gueudecourt", "80"), ("LESBŒUFS", "Lesbœufs", "80"),
    ("MORVAL", "Morval", "80"), ("SAILLY-SAILLISEL", "Sailly-Saillisel", "80"),
    ("BOUCHAVESNES", "Bouchavesnes-Bergen", "80"), ("CURLU", "Curlu", "80"), ("FRISE", "Frise", "80"),
    ("BRAY", "Bray-sur-Somme", "80"), ("AUCHONVILLERS", "Auchonvillers", "80"), ("PUISIEUX", "Puisieux", "62"),
    ("LE TRANSLOY", "Transloy", "62"), ("BIACHES", "Biaches", "80"), ("BARLEUX", "Barleux", "80"),
    ("ESTRÉES", "Estrées-Deniécourt", "80"), ("FOUCAUCOURT", "Foucaucourt-en-Santerre", "80"),
    ("DOMPIERRE", "Dompierre-Becquincourt", "80"), ("HARDECOURT", "Hardecourt-aux-Bois", "80"),
    ("CLÉRY", "Clery-sur-Somme", "80"), ("ARRAS", "Arras", "62"), ("CORBIE", "Corbie", "80"),
    # Serre is a hamlet of Puisieux; St-Pierre-Divion is in Thiepval commune (published coordinates)
    ("SERRE", None, (2.6693, 50.1032)),
]

WOODS = {  # approximate centres of the woods that gave their names to the fighting
    "DELVILLE WOOD": (2.808, 50.028), "HIGH WOOD": (2.778, 50.048), "MAMETZ WOOD": (2.757, 50.012),
    "TRÔNES WOOD": (2.808, 50.004), "THIEPVAL WOOD": (2.672, 50.055), "BERNAFAY WOOD": (2.795, 49.999),
}

# The Ancre (not in Natural Earth): traced down its valley from Miraumont to Corbie
ANCRE = [(2.742, 50.099), (2.726, 50.088), (2.708, 50.078), (2.69, 50.075), (2.676, 50.07), (2.667, 50.062),
         (2.662, 50.052), (2.665, 50.042), (2.662, 50.031), (2.651, 50.006), (2.638, 49.992), (2.622, 49.981),
         (2.595, 49.972), (2.56, 49.955), (2.527, 49.935), (2.51, 49.918)]


def norm(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def centroid(f):
    g = f["geometry"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    pts = np.array([p for poly in polys for p in poly[0]])
    return round(float(pts[:, 0].mean()), 4), round(float(pts[:, 1].mean()), 4)


def main(land, rivers, c80, c62):
    os.makedirs(OUT, exist_ok=True)
    wf = reduce(rings_of(json.load(open(land))), 0.01, 0.002, bbox=(-6, 42, 12, 56))
    json.dump(wf, open(os.path.join(OUT, "westfront_land.json"), "w"), separators=(",", ":"))
    riv = []
    for f in json.load(open(rivers))["features"]:
        if f["properties"].get("name") == "Somme":
            g = f["geometry"]
            lines = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
            for ln in lines:
                riv.append([[round(x, 4), round(y, 4)] for x, y in dp(ln, 0.0015)])
    communes = {"80": json.load(open(c80))["features"], "62": json.load(open(c62))["features"]}
    places = {}
    for name, commune, dep in PLACES:
        if commune is None:
            places[name] = dep
            continue
        hits = [f for f in communes[dep] if norm(f["properties"]["nom"]) == norm(commune)]
        if not hits:  # a few villages sit just over the departement line
            other = "62" if dep == "80" else "80"
            hits = [f for f in communes[other] if norm(f["properties"]["nom"]) == norm(commune)]
        assert hits, commune
        places[name] = centroid(hits[0])
    json.dump({"somme": riv, "ancre": ANCRE, "places": places, "woods": WOODS},
              open(os.path.join(OUT, "battlefield.json"), "w"), ensure_ascii=False, indent=0)
    print(len(wf), "land rings;", len(riv), "Somme segments;", len(places), "places")


if __name__ == "__main__":
    main(*sys.argv[1:5])
