"""Maps in the manner of a 1943 War Office / newspaper war map: cream land,
pale ruled sea, bold capitals, heavy black arrows for real moves and dashed
arrows for threats that never came."""
import functools
import json
import math
import os

import numpy as np

from engine import maps as EM
from engine.core import H, W, draw_text, fbm, lerp, rgba_to_surface, set_rgba, text_width

from . import ROOT

LAND = (0.9, 0.87, 0.78)
SEA = (0.78, 0.82, 0.83)
INK = (0.1, 0.1, 0.11)
RED = (0.72, 0.1, 0.08)
AXIS = (0.2, 0.2, 0.22)

PLACES = {
    "SICILY": (14.2, 37.55), "SARDINIA": (9.0, 40.1), "CORSICA": (9.1, 42.15), "GREECE": (22.0, 39.3),
    "CRETE": (24.9, 35.25), "HUELVA": (-6.95, 37.26), "GIBRALTAR": (-5.35, 36.14), "MALTA": (14.4, 35.9),
    "TUNIS": (10.18, 36.8), "ALGIERS": (3.06, 36.75), "MADRID": (-3.7, 40.42), "LONDON": (-0.12, 51.5),
    "HOLY LOCH": (-4.93, 55.99), "ROME": (12.5, 41.9), "MESSINA": (15.55, 38.19), "SYRACUSE": (15.29, 37.07),
    "GELA": (14.25, 37.07), "LICATA": (13.94, 37.1), "PALERMO": (13.36, 38.12), "KALAMATA": (22.11, 37.04),
    "ARAXOS": (21.4, 38.17), "ATHENS": (23.73, 37.98), "BERLIN": (13.4, 52.52), "PARIS": (2.35, 48.86),
    "PUNTA UMBRÍA": (-6.96, 37.18), "BAY OF BISCAY": (-6.0, 45.5), "SPAIN": (-4.0, 39.8), "FRANCE": (2.5, 46.8),
    "ITALY": (12.6, 42.9), "TUNISIA": (9.5, 34.0), "ALGERIA": (3.0, 34.5), "PORTUGAL": (-8.1, 39.6),
}


@functools.lru_cache(maxsize=None)
def rings():
    return [np.asarray(r) for r in json.load(open(os.path.join(ROOT, "assets", "geo", "europe_med.json")))]


class Map:
    def __init__(self, lon, lat, zoom):
        self.m = EM.FlatMap(lon, lat, zoom)

    def xy(self, lon, lat):
        return self.m.xy(lon, lat)

    def p(self, name):
        return self.m.xy(*PLACES[name])

    def land_path(self, ctx):
        for r in rings():
            p = self.m.xy_arr(r)
            if p[:, 0].max() < -50 or p[:, 0].min() > W + 50 or p[:, 1].max() < -50 or p[:, 1].min() > H + 50:
                continue
            ctx.move_to(*p[0])
            for q in p[1:]:
                ctx.line_to(q[0], q[1])
            ctx.close_path()


@functools.lru_cache(maxsize=2)
def _paper(seed=11):
    n = fbm(W, H, seed, 6, 5)
    arr = np.zeros((H, W, 4), dtype=np.uint8)
    arr[:, :, :3] = 255
    arr[:, :, 3] = (np.abs(n - 0.5) * 2 * 40).astype(np.uint8)
    return rgba_to_surface(arr)


def base(ctx, mp, grid=5.0):
    ctx.rectangle(0, 0, W, H)
    set_rgba(ctx, SEA)
    ctx.fill()
    ctx.set_line_width(1)
    for y in range(0, H, 5):
        ctx.move_to(0, y + 0.5)
        ctx.line_to(W, y + 0.5)
    ctx.set_source_rgba(0.3, 0.4, 0.45, 0.12)
    ctx.stroke()
    for w, a in ((10, 0.15), (5, 0.25)):
        mp.land_path(ctx)
        ctx.set_line_width(w)
        ctx.set_source_rgba(0.25, 0.35, 0.4, a)
        ctx.stroke()
    mp.land_path(ctx)
    set_rgba(ctx, LAND)
    ctx.fill_preserve()
    ctx.set_line_width(2)
    set_rgba(ctx, INK)
    ctx.stroke()
    if grid:
        mp.m.graticule(ctx, grid, alpha=0.0)
        x0, y0, x1, y1 = mp.m.view_bbox()
        ctx.set_line_width(1)
        lon = math.floor(x0 / grid) * grid
        while lon <= x1:
            a, b = mp.xy(lon, y0), mp.xy(lon, y1)
            ctx.move_to(*a)
            ctx.line_to(*b)
            lon += grid
        lat = math.floor(y0 / grid) * grid
        while lat <= y1:
            a, b = mp.xy(x0, lat), mp.xy(x1, lat)
            ctx.move_to(*a)
            ctx.line_to(*b)
            lat += grid
        set_rgba(ctx, INK, 0.18)
        ctx.stroke()
    ctx.set_source_surface(_paper(), 0, 0)
    ctx.paint()


def label(ctx, mp, name, text=None, dx=0, dy=0, size=34, alpha=1.0, anchor="cm", font="oldstd_b", color=INK,
          dot=False, tracking=0.12):
    x, y = mp.p(name)
    if dot:
        ctx.arc(x, y, 7, 0, 6.283)
        set_rgba(ctx, color, alpha)
        ctx.fill()
    draw_text(ctx, text or name, x + dx, y + dy, font, size, color, anchor, alpha, tracking)


def arrow(ctx, pts, progress, color=INK, width=16, dashed=False, alpha=1.0):
    if not dashed:
        EM.arrow(ctx, pts, progress, color, width, width * 2.6, alpha, outline=False)
        return
    # a threat that never materialised: hollow dashed arrow
    path = EM.catmull(pts, 20)
    n = max(2, int(len(path) * max(0.0, min(1.0, progress))))
    ctx.move_to(*path[0])
    for p in path[1:n]:
        ctx.line_to(*p)
    ctx.set_line_width(width * 0.55)
    ctx.set_dash([width * 1.4, width])
    set_rgba(ctx, color, alpha)
    ctx.stroke()
    ctx.set_dash([])
    if progress > 0.9 and n >= 2:
        (x0, y0), (x1, y1) = path[n - 2], path[n - 1]
        a = math.atan2(y1 - y0, x1 - x0)
        s = width * 2.2
        ctx.move_to(x1 + math.cos(a) * s * 0.4, y1 + math.sin(a) * s * 0.4)
        ctx.line_to(x1 + math.cos(a + 2.5) * s, y1 + math.sin(a + 2.5) * s)
        ctx.line_to(x1 + math.cos(a - 2.5) * s, y1 + math.sin(a - 2.5) * s)
        ctx.close_path()
        ctx.set_line_width(4)
        ctx.stroke()


def title_box(ctx, title, sub=None, alpha=1.0, x=70, y=60):
    w = max(text_width(title, "oldstd_b", 52, 0.1), text_width(sub or "", "courier_r", 30)) + 80
    h = 96 if not sub else 144
    ctx.rectangle(x, y, w, h)
    set_rgba(ctx, (0.97, 0.95, 0.9), 0.95 * alpha)
    ctx.fill_preserve()
    ctx.set_line_width(4)
    set_rgba(ctx, INK, alpha)
    ctx.stroke()
    draw_text(ctx, title, x + 40, y + 70, "oldstd_b", 52, INK, "lb", alpha, 0.1)
    if sub:
        draw_text(ctx, sub, x + 40, y + 118, "courier_r", 30, INK, "lb", alpha)
