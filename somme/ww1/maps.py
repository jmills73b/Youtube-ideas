"""Maps in the manner of 1916: an engraved atlas map of the Western Front and
British trench maps of the Somme battlefield (German trenches printed in red).

Front lines are schematic: they follow the village-by-village record of what was
held on each date (see RESEARCH.md) rather than surveyed trench lines.
"""
import functools
import json
import math
import os

import cairo
import numpy as np

from engine import maps as EM
from engine.core import H, W, clamp, draw_text, fbm, lerp, mix, ramp, rgba_to_surface, set_rgba, text_width

from . import ROOT

GEO = os.path.join(ROOT, "assets", "geo")
PAPER = (0.9, 0.86, 0.75)
INK = (0.2, 0.15, 0.1)
SEPIA = (0.36, 0.25, 0.15)
BRIT = (0.14, 0.24, 0.52)
FRENCH = (0.36, 0.52, 0.75)       # "horizon blue"
GERMAN = (0.72, 0.1, 0.08)        # British trench maps printed German trenches in red
WATER = (0.35, 0.5, 0.62)


@functools.lru_cache(maxsize=None)
def battlefield():
    return json.load(open(os.path.join(GEO, "battlefield.json")))


@functools.lru_cache(maxsize=None)
def wf_rings():
    return [np.asarray(r) for r in json.load(open(os.path.join(GEO, "westfront_land.json")))]


def P(name):
    b = battlefield()
    if name in b["places"]:
        return tuple(b["places"][name])
    return tuple(b["woods"][name])


# ------------------------------------------------------------------ front lines (lon, lat), north to south
WESTERN_FRONT = [(2.75, 51.13), (2.87, 51.03), (2.95, 50.9), (2.93, 50.8), (2.88, 50.69), (2.78, 50.58),
                 (2.8, 50.47), (2.8, 50.37), (2.82, 50.29), (2.7, 50.16), (2.66, 50.1), (2.7, 50.02),
                 (2.81, 49.94), (2.78, 49.82), (2.79, 49.7), (2.84, 49.58), (2.95, 49.55), (3.33, 49.4),
                 (3.7, 49.44), (3.9, 49.4), (4.03, 49.3), (4.4, 49.2), (4.95, 49.2), (5.3, 49.24),
                 (5.45, 49.2), (5.6, 49.1), (5.54, 48.89), (5.75, 48.9), (6.05, 48.9), (6.3, 48.75),
                 (6.7, 48.6), (7.0, 48.35), (7.1, 48.1), (7.15, 47.85), (7.15, 47.6), (7.1, 47.5)]

HINDENBURG_LINE = [(2.78, 50.29), (2.9, 50.2), (2.98, 50.18), (3.1, 50.05), (3.2, 49.93), (3.29, 49.85),
                   (3.33, 49.75), (3.36, 49.66), (3.45, 49.52), (3.5, 49.43)]

# The Somme battlefield. Allied front on successive dates.
LINE_JUL1 = [(2.64, 50.14), (2.652, 50.118), (2.657, 50.1), (2.65, 50.087), (2.648, 50.078), (2.662, 50.067),
             (2.672, 50.058), (2.678, 50.047), (2.683, 50.035), (2.692, 50.022), (2.7, 50.01), (2.708, 50.0),
             (2.72, 49.99), (2.745, 49.99), (2.77, 49.992), (2.79, 49.99), (2.805, 49.975), (2.808, 49.955),
             (2.8, 49.935), (2.79, 49.915), (2.772, 49.895), (2.765, 49.87)]
LINE_JUL14 = [(2.64, 50.14), (2.652, 50.118), (2.657, 50.1), (2.65, 50.087), (2.648, 50.078), (2.662, 50.067),
              (2.672, 50.058), (2.678, 50.047), (2.683, 50.035), (2.693, 50.03), (2.715, 50.031), (2.735, 50.03),
              (2.75, 50.036), (2.768, 50.037), (2.79, 50.035), (2.803, 50.031), (2.812, 50.022), (2.814, 50.004),
              (2.822, 49.994), (2.835, 49.978), (2.86, 49.957), (2.9, 49.93), (2.892, 49.905), (2.84, 49.885),
              (2.79, 49.868)]
LINE_SEP30 = [(2.64, 50.14), (2.652, 50.118), (2.657, 50.1), (2.65, 50.087), (2.648, 50.078), (2.662, 50.067),
              (2.672, 50.066), (2.69, 50.068), (2.72, 50.069), (2.745, 50.07), (2.77, 50.066), (2.8, 50.06),
              (2.822, 50.059), (2.843, 50.059), (2.857, 50.046), (2.869, 50.031), (2.878, 50.011),
              (2.9, 50.0), (2.925, 49.99), (2.935, 49.96), (2.905, 49.926), (2.89, 49.9), (2.84, 49.878),
              (2.79, 49.862)]
LINE_NOV18 = [(2.64, 50.14), (2.652, 50.118), (2.657, 50.1), (2.665, 50.092), (2.672, 50.086), (2.69, 50.087),
              (2.705, 50.08), (2.71, 50.074), (2.73, 50.076), (2.76, 50.074), (2.782, 50.073), (2.81, 50.07),
              (2.85, 50.063), (2.875, 50.05), (2.9, 50.038), (2.915, 50.032), (2.93, 50.01), (2.935, 49.995),
              (2.92, 49.955), (2.905, 49.926), (2.882, 49.9), (2.832, 49.876), (2.79, 49.86)]


def resample(pts, n=240):
    pts = np.asarray(pts, dtype=float)
    seg = np.hypot(*np.diff(pts, axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    u = np.linspace(0, s[-1], n)
    return np.stack([np.interp(u, s, pts[:, 0]), np.interp(u, s, pts[:, 1])], axis=1)


def blend_lines(a, b, k):
    return resample(a) * (1 - k) + resample(b) * k


# ------------------------------------------------------------------ projection
class Proj:
    def __init__(self, lon, lat, zoom, cx=W / 2, cy=H / 2):
        self.m = EM.FlatMap(lon, lat, zoom, cx, cy)

    def xy(self, lon, lat):
        return self.m.xy(lon, lat)

    def p(self, name):
        return self.m.xy(*P(name))

    def arr(self, pts):
        return self.m.xy_arr(np.asarray(pts, dtype=float))


@functools.lru_cache(maxsize=2)
def paper_surface(seed=9, tone=PAPER):
    n = fbm(W, H, seed, 6, 5)
    n2 = fbm(W, H, seed + 1, 3, 2)
    fib = np.random.default_rng(seed).random((H, W)).astype(np.float32)
    base = np.array(tone, dtype=np.float32)
    k = ((n - 0.5) * 0.10 + np.clip(n2 - 0.6, 0, 1) * 0.35 + (fib - 0.5) * 0.04)[:, :, None]
    col = base * (1 - k) + np.array([0.55, 0.42, 0.25], dtype=np.float32) * k
    arr = np.zeros((H, W, 4), dtype=np.uint8)
    arr[:, :, :3] = (np.clip(col, 0, 1) * 255).astype(np.uint8)
    arr[:, :, 3] = 255
    return rgba_to_surface(arr)


def paper(ctx, seed=9, tone=PAPER):
    ctx.set_source_surface(paper_surface(seed, tone), 0, 0)
    ctx.paint()


# ------------------------------------------------------------------ Western Front atlas map
def _land_path(ctx, pr):
    for r in wf_rings():
        p = pr.arr(r)
        if p[:, 0].max() < -50 or p[:, 0].min() > W + 50 or p[:, 1].max() < -50 or p[:, 1].min() > H + 50:
            continue
        ctx.move_to(*p[0])
        for q in p[1:]:
            ctx.line_to(q[0], q[1])
        ctx.close_path()


def atlas_base(ctx, pr, t=0.0):
    paper(ctx, 4)
    # sea: engraved horizontal hatching
    ctx.save()
    ctx.rectangle(0, 0, W, H)
    _land_path(ctx, pr)
    ctx.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    ctx.clip()
    ctx.set_line_width(1.1)
    for y in range(0, H, 7):
        ctx.move_to(0, y + 0.5)
        ctx.line_to(W, y + 0.5)
    set_rgba(ctx, SEPIA, 0.35)
    ctx.stroke()
    ctx.restore()
    for w, a in ((9, 0.12), (5, 0.18)):
        _land_path(ctx, pr)
        ctx.set_line_width(w)
        set_rgba(ctx, SEPIA, a)
        ctx.stroke()
    _land_path(ctx, pr)
    ctx.set_line_width(1.8)
    set_rgba(ctx, INK, 0.9)
    ctx.stroke()


def trench_line(ctx, pts_xy, progress=1.0, color=GERMAN, width=5, teeth=True, alpha=1.0):
    """A front line drawn as a crenellated trench trace (fire bays and traverses)."""
    pts = np.asarray(pts_xy, dtype=float)
    if len(pts) < 2 or progress <= 0:
        return
    seg = np.hypot(*np.diff(pts, axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    total = s[-1] * clamp(progress)
    n = max(2, int(total / 6))
    u = np.linspace(0, total, n)
    xs, ys = np.interp(u, s, pts[:, 0]), np.interp(u, s, pts[:, 1])
    ctx.move_to(xs[0], ys[0])
    for i in range(1, n):
        if teeth:
            dx, dy = xs[i] - xs[i - 1], ys[i] - ys[i - 1]
            L = math.hypot(dx, dy) or 1
            nx, ny = -dy / L, dx / L
            off = 4 if (i // 2) % 2 == 0 else -1
            ctx.line_to(xs[i] + nx * off, ys[i] + ny * off)
        else:
            ctx.line_to(xs[i], ys[i])
    ctx.set_line_width(width)
    set_rgba(ctx, color, alpha)
    ctx.stroke()


def place(ctx, pr, name, label=None, dx=12, dy=-10, size=30, alpha=1.0, anchor="lb", font="fell_sc", dot=True):
    x, y = pr.p(name) if isinstance(name, str) else pr.xy(*name)
    if dot:
        ctx.rectangle(x - 5, y - 5, 10, 10)
        set_rgba(ctx, INK, alpha)
        ctx.fill()
    text = label or (name.title() if isinstance(name, str) else "")
    draw_text(ctx, text, x + dx, y + dy, font, size, INK, anchor, alpha, 0.02)


# ------------------------------------------------------------------ trench map of the battlefield
def _grid(ctx, pr, alpha=0.35):
    lat_step = 914 / 111000.0
    lon_step = 914 / (111000.0 * math.cos(math.radians(50.0)))
    lon0, lat0 = 2.55, 49.8
    ctx.set_line_width(1)
    for i in range(0, 60):
        x, _ = pr.xy(lon0 + i * lon_step, lat0)
        ctx.move_to(x, 0)
        ctx.line_to(x, H)
    for j in range(0, 60):
        _, y = pr.xy(lon0, lat0 + j * lat_step)
        ctx.move_to(0, y)
        ctx.line_to(W, y)
    set_rgba(ctx, SEPIA, alpha * 0.5)
    ctx.stroke()
    ctx.set_line_width(2.2)
    for i in range(0, 60, 6):
        x, _ = pr.xy(lon0 + i * lon_step, lat0)
        ctx.move_to(x, 0)
        ctx.line_to(x, H)
    for j in range(0, 60, 6):
        _, y = pr.xy(lon0, lat0 + j * lat_step)
        ctx.move_to(0, y)
        ctx.line_to(W, y)
    set_rgba(ctx, SEPIA, alpha)
    ctx.stroke()
    letters = "ABCDEFGHIJKLMNOPQRSTUVWX"
    k = 0
    for j in range(0, 60, 6):
        for i in range(0, 60, 6):
            x, y = pr.xy(lon0 + (i + 0.3) * lon_step, lat0 + (j + 5.4) * lat_step)
            if -40 < x < W and -40 < y < H:
                draw_text(ctx, letters[(i // 6 + j // 6 * 3) % 24], x, y, "fell", 44, SEPIA, "lt", alpha * 0.9)
            k += 1


def _river(ctx, pr, pts, width=5):
    p = pr.arr(pts)
    ctx.move_to(*p[0])
    for q in p[1:]:
        ctx.line_to(q[0], q[1])
    ctx.set_line_width(width + 6)
    set_rgba(ctx, WATER, 0.25)
    ctx.stroke_preserve()
    ctx.set_line_width(width)
    set_rgba(ctx, WATER, 0.9)
    ctx.stroke()


def _wood(ctx, pr, name, r=26, alpha=1.0):
    x, y = pr.p(name)
    rng = np.random.default_rng(abs(hash(name)) % 1000)
    for _ in range(26):
        a, d = rng.random() * 6.283, rng.random() ** 0.5 * r
        tx, ty = x + math.cos(a) * d * 1.3, y + math.sin(a) * d
        ctx.arc(tx, ty, 3.2, 0, 6.283)
        set_rgba(ctx, (0.25, 0.35, 0.2), 0.8 * alpha)
        ctx.fill()
        ctx.move_to(tx, ty + 3)
        ctx.line_to(tx, ty + 7)
        ctx.set_line_width(1.2)
        ctx.stroke()


def _village(ctx, pr, name, size=1.0, alpha=1.0):
    x, y = pr.p(name)
    rng = np.random.default_rng(abs(hash(name)) % 997)
    for _ in range(9):
        bx, by = x + (rng.random() - 0.5) * 34 * size, y + (rng.random() - 0.5) * 24 * size
        ctx.rectangle(bx, by, 6 * size, 4 * size)
    set_rgba(ctx, INK, 0.85 * alpha)
    ctx.fill()


def trench_base(ctx, pr, t=0.0, villages=None, woods=True, labels=True, alpha=1.0, grid=True):
    paper(ctx, 9)
    if grid:
        _grid(ctx, pr)
    b = battlefield()
    # roads: Albert-Bapaume and Peronne-Bapaume
    for a_, b_ in (("ALBERT", "BAPAUME"), ("PÉRONNE", "BAPAUME"), ("ALBERT", "BRAY")):
        (x0, y0), (x1, y1) = pr.p(a_), pr.p(b_)
        ctx.move_to(x0, y0)
        ctx.line_to(x1, y1)
        ctx.set_line_width(7)
        set_rgba(ctx, (0.55, 0.4, 0.25), 0.55)
        ctx.stroke()
        ctx.move_to(x0, y0)
        ctx.line_to(x1, y1)
        ctx.set_line_width(3)
        set_rgba(ctx, PAPER, 0.9)
        ctx.stroke()
    for seg in b["somme"]:
        _river(ctx, pr, seg, 6)
    _river(ctx, pr, b["ancre"], 4)
    if woods:
        for w_ in b["woods"]:
            _wood(ctx, pr, w_)
    names = villages if villages is not None else list(b["places"].keys())
    for n in names:
        _village(ctx, pr, n)
        if labels:
            x, y = pr.p(n)
            draw_text(ctx, n.title().replace("-L'", "-l'"), x + 16, y - 12, "fell_sc", 26, INK, "lb", 0.9)


def front_band(ctx, pr, line_ll, german_side=1, alpha=1.0, progress=1.0, british=True):
    """German front + support trenches in red, British front in blue, from one front trace."""
    xy = pr.arr(resample(line_ll, 300))
    d = np.gradient(xy, axis=0)
    nrm = np.stack([-d[:, 1], d[:, 0]], axis=1)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
    # choose the normal that points east (towards the German side)
    sign = 1 if np.mean(nrm[:, 0]) > 0 else -1
    nrm *= sign * german_side
    trench_line(ctx, xy + nrm * 9, progress, GERMAN, 4.5, True, alpha)
    trench_line(ctx, xy + nrm * 24, progress, GERMAN, 2.5, True, alpha * 0.8)
    if british:
        trench_line(ctx, xy - nrm * 9, progress, BRIT, 3.5, True, alpha)


def gained_ground(ctx, pr, line_a, line_b, color=BRIT, alpha=0.35):
    a = pr.arr(resample(line_a, 200))
    b = pr.arr(resample(line_b, 200))[::-1]
    ctx.save()
    ctx.move_to(*a[0])
    for q in a[1:]:
        ctx.line_to(*q)
    for q in b:
        ctx.line_to(*q)
    ctx.close_path()
    ctx.clip()
    ctx.set_line_width(1.6)
    for i in range(-H, W, 10):
        ctx.move_to(i, 0)
        ctx.line_to(i + H, H)
    set_rgba(ctx, color, alpha)
    ctx.stroke()
    ctx.restore()


def legend(ctx, x, y, items, alpha=1.0):
    w = 400
    h = 64 + 50 * len(items)
    ctx.rectangle(x, y, w, h)
    set_rgba(ctx, PAPER, 0.92 * alpha)
    ctx.fill_preserve()
    ctx.set_line_width(2)
    set_rgba(ctx, INK, alpha)
    ctx.stroke()
    draw_text(ctx, "Reference", x + w / 2, y + 44, "fell_sc", 32, INK, "cb", alpha, 0.1)
    for i, (label, col) in enumerate(items):
        yy = y + 84 + i * 50
        trench_line(ctx, [(x + 24, yy), (x + 94, yy)], 1, col, 4, True, alpha)
        draw_text(ctx, label, x + 112, yy + 10, "fell", 30, INK, "lb", alpha)


def cartouche(ctx, title, sub=None, alpha=1.0, x=80, y=70):
    w = max(text_width(title, "fell_sc", 50, 0.06), text_width(sub or "", "fell_i", 34)) + 80
    h = 90 if not sub else 138
    ctx.rectangle(x, y, w, h)
    set_rgba(ctx, PAPER, 0.94 * alpha)
    ctx.fill_preserve()
    ctx.set_line_width(3)
    set_rgba(ctx, INK, alpha)
    ctx.stroke()
    ctx.rectangle(x + 8, y + 8, w - 16, h - 16)
    ctx.set_line_width(1)
    ctx.stroke()
    draw_text(ctx, title, x + w / 2, y + 66, "fell_sc", 50, INK, "cb", alpha, 0.06)
    if sub:
        draw_text(ctx, sub, x + w / 2, y + 112, "fell_i", 34, SEPIA, "cb", alpha)
