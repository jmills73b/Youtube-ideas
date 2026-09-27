"""Maps in the style of early-1980s television news graphics."""
import functools
import json
import math
import os

import cairo
import numpy as np

from .core import (H, W, ROOT, clamp, draw_text, fbm, hexc, lerp, mix, rgba_to_surface, set_rgba,
                   smooth, text_width, vgrad)

GEO = os.path.join(ROOT, "assets", "geo")

SEA_TOP = hexc("0F2447")
SEA_BOT = hexc("1C3D6E")
LAND = hexc("D9C9A0")
LAND_DARK = hexc("B7A57A")
COAST = hexc("6E6040")
GRID = (0.75, 0.85, 1.0)
BRIT = hexc("E0303F")
ARG = hexc("8CC6F0")
LABEL = (1, 1, 1)

# Key places, (lon, lat)
PLACES = {
    "stanley": (-57.855, -51.6975),
    "govhouse": (-57.866, -51.694),
    "yorke_bay": (-57.79, -51.675),
    "mullet_creek": (-57.87, -51.73),
    "san_carlos": (-59.025, -51.505),
    "port_san_carlos": (-59.0, -51.48),
    "ajax_bay": (-59.07, -51.54),
    "goose_green": (-58.972, -51.827),
    "darwin": (-58.957, -51.812),
    "teal_inlet": (-58.43, -51.566),
    "fitzroy": (-58.257, -51.783),
    "bluff_cove": (-58.2, -51.73),
    "mt_kent": (-58.107, -51.673),
    "mt_longdon": (-57.97, -51.66),
    "two_sisters": (-58.03, -51.673),
    "mt_harriet": (-58.0, -51.7),
    "tumbledown": (-57.95, -51.69),
    "wireless_ridge": (-57.92, -51.667),
    "mt_william": (-57.925, -51.7),
    "pebble": (-59.55, -51.31),
    "falklands": (-59.2, -51.75),
    "grytviken": (-36.51, -54.28),
    "south_georgia": (-36.6, -54.35),
    "ascension": (-14.36, -7.94),
    "portsmouth": (-1.09, 50.8),
    "buenos_aires": (-58.38, -34.6),
    "rio_grande": (-67.75, -53.78),
    "rio_gallegos": (-69.31, -51.61),
    "belgrano_sunk": (-61.53, -55.4),
    "sheffield_hit": (-56.93, -53.07),
    "tez_centre": (-59.5, -51.67),
    "uk": (-2.0, 53.5),
    "wp_biscay": (-12.0, 44.0),
    "wp_canaries": (-21.0, 22.0),
    "wp_capeverde": (-24.0, 10.0),
    "camilla_creek": (-58.93, -51.75),
}


@functools.lru_cache(maxsize=None)
def rings(name):
    return [np.asarray(r, dtype=np.float64) for r in json.load(open(os.path.join(GEO, name + ".json")))]


def _ring_bbox(name):
    return [(r[:, 0].min(), r[:, 1].min(), r[:, 0].max(), r[:, 1].max()) for r in rings(name)]


_bbox_cache = {}


def ring_bboxes(name):
    if name not in _bbox_cache:
        _bbox_cache[name] = _ring_bbox(name)
    return _bbox_cache[name]


# ------------------------------------------------------------------ flat regional map
class FlatMap:
    """Local equirectangular projection. zoom = pixels per degree of latitude."""

    def __init__(self, lon, lat, zoom, cx=W / 2, cy=H / 2):
        self.lon0, self.lat0, self.zoom, self.cx, self.cy = lon, lat, zoom, cx, cy
        self.k = math.cos(math.radians(lat))

    def xy(self, lon, lat):
        return (self.cx + (lon - self.lon0) * self.k * self.zoom, self.cy - (lat - self.lat0) * self.zoom)

    def pxy(self, key):
        return self.xy(*PLACES[key])

    def xy_arr(self, a):
        return np.stack([self.cx + (a[:, 0] - self.lon0) * self.k * self.zoom,
                         self.cy - (a[:, 1] - self.lat0) * self.zoom], axis=1)

    def view_bbox(self, margin=50):
        lon_half = (W / 2 + margin) / (self.k * self.zoom)
        lat_half = (H / 2 + margin) / self.zoom
        # cx/cy may be off-centre; widen generously
        return (self.lon0 - lon_half * 1.6, self.lat0 - lat_half * 1.6, self.lon0 + lon_half * 1.6,
                self.lat0 + lat_half * 1.6)

    def land_path(self, ctx, sources=("falklands", "southatlantic")):
        x0, y0, x1, y1 = self.view_bbox()
        min_px = 1.2
        for name in sources:
            for r, bb in zip(rings(name), ring_bboxes(name)):
                if bb[2] < x0 or bb[0] > x1 or bb[3] < y0 or bb[1] > y1:
                    continue
                if (bb[2] - bb[0]) * self.k * self.zoom < min_px and (bb[3] - bb[1]) * self.zoom < min_px:
                    continue
                p = self.xy_arr(r)
                # drop sub-pixel vertices for speed
                step = max(1, int(len(p) / max(8, ((bb[2] - bb[0]) * self.k * self.zoom +
                                                  (bb[3] - bb[1]) * self.zoom) * 1.5)))
                p = p[::step]
                ctx.move_to(*p[0])
                for q in p[1:]:
                    ctx.line_to(q[0], q[1])
                ctx.close_path()

    def draw_base(self, ctx, t=0.0, night=0.0, grid_step=None, relief=True):
        sea_top = mix(SEA_TOP, (0.02, 0.04, 0.09), night)
        sea_bot = mix(SEA_BOT, (0.04, 0.08, 0.16), night)
        ctx.rectangle(0, 0, W, H)
        ctx.set_source(vgrad(ctx, 0, 0, 0, H, [(0, sea_top), (1, sea_bot)]))
        ctx.fill()
        _sea_lines(ctx, t, night)
        if grid_step:
            self.graticule(ctx, grid_step, alpha=0.12)
        # coastal shelf glow
        ctx.new_path()
        self.land_path(ctx)
        ctx.set_line_width(14)
        ctx.set_source_rgba(0.45, 0.65, 0.85, 0.10 * (1 - night * 0.5))
        ctx.stroke_preserve()
        ctx.set_line_width(6)
        ctx.set_source_rgba(0.55, 0.75, 0.95, 0.12 * (1 - night * 0.5))
        ctx.stroke()
        # drop shadow
        ctx.save()
        ctx.translate(5, 7)
        self.land_path(ctx)
        ctx.set_source_rgba(0, 0, 0, 0.35)
        ctx.fill()
        ctx.restore()
        land = mix(LAND, (0.35, 0.36, 0.42), night)
        land_d = mix(LAND_DARK, (0.25, 0.26, 0.32), night)
        self.land_path(ctx)
        ctx.set_source(vgrad(ctx, 0, 0, 0, H, [(0, land), (1, land_d)]))
        ctx.fill_preserve()
        if relief:
            ctx.save()
            ctx.clip_preserve()
            ctx.set_source_surface(_relief_surface(), 0, 0)
            ctx.paint_with_alpha(0.55)
            ctx.restore()
        ctx.set_line_width(1.6)
        set_rgba(ctx, mix(COAST, (0.1, 0.1, 0.15), night))
        ctx.stroke()

    def graticule(self, ctx, step, alpha=0.15):
        x0, y0, x1, y1 = self.view_bbox()
        ctx.set_line_width(1)
        lon = math.floor(x0 / step) * step
        while lon <= x1:
            a, b = self.xy(lon, y0), self.xy(lon, y1)
            ctx.move_to(*a)
            ctx.line_to(*b)
            lon += step
        lat = math.floor(y0 / step) * step
        while lat <= y1:
            a, b = self.xy(x0, lat), self.xy(x1, lat)
            ctx.move_to(*a)
            ctx.line_to(*b)
            lat += step
        ctx.set_source_rgba(*GRID, alpha)
        ctx.stroke()

    def circle_nm(self, ctx, key_or_ll, nm, color, alpha, progress=1.0, dash=True, width=3):
        lon, lat = PLACES[key_or_ll] if isinstance(key_or_ll, str) else key_or_ll
        rdeg = nm / 60.0
        n = 180
        pts = []
        for i in range(int(n * progress) + 1):
            a = 2 * math.pi * i / n - math.pi / 2
            pts.append(self.xy(lon + rdeg * math.cos(a) / math.cos(math.radians(lat)),
                               lat + rdeg * math.sin(a)))
        if len(pts) < 2:
            return
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        if dash:
            ctx.set_dash([18, 10])
        ctx.set_line_width(width)
        set_rgba(ctx, color, alpha)
        ctx.stroke()
        ctx.set_dash([])


# relief texture (subtle mottling on land)
@functools.lru_cache(maxsize=1)
def _relief_surface():
    n = fbm(W, H, seed=21, octaves=6, base=5)
    n2 = fbm(W, H, seed=22, octaves=4, base=12)
    v = (n * 0.7 + n2 * 0.3)
    arr = np.zeros((H, W, 4), dtype=np.uint8)
    dark = v < 0.5
    arr[:, :, 0:3] = np.where(dark[:, :, None], 60, 255).astype(np.uint8)
    arr[:, :, 3] = (np.abs(v - 0.5) * 2 * 60).astype(np.uint8)
    return rgba_to_surface(arr)


def _sea_lines(ctx, t, night):
    ctx.set_line_width(1)
    for i in range(0, H, 6):
        ctx.move_to(0, i + 0.5)
        ctx.line_to(W, i + 0.5)
    ctx.set_source_rgba(1, 1, 1, 0.018 * (1 - night))
    ctx.stroke()


# ------------------------------------------------------------------ globe
class Globe:
    def __init__(self, lon0, lat0, radius, cx=W / 2, cy=H / 2):
        self.lon0, self.lat0, self.R, self.cx, self.cy = lon0, lat0, radius, cx, cy
        self.l0, self.p0 = math.radians(lon0), math.radians(lat0)

    def proj(self, lon, lat):
        l, p = np.radians(lon), np.radians(lat)
        cosc = math.sin(self.p0) * np.sin(p) + math.cos(self.p0) * np.cos(p) * np.cos(l - self.l0)
        x = np.cos(p) * np.sin(l - self.l0)
        y = math.cos(self.p0) * np.sin(p) - math.sin(self.p0) * np.cos(p) * np.cos(l - self.l0)
        return self.cx + x * self.R, self.cy - y * self.R, cosc

    def xy(self, lon, lat):
        x, y, _ = self.proj(np.array([lon]), np.array([lat]))
        return float(x[0]), float(y[0])

    def pxy(self, key):
        return self.xy(*PLACES[key])

    def draw(self, ctx, t=0.0, land_alpha=1.0):
        R, cx, cy = self.R, self.cx, self.cy
        # halo
        g = cairo.RadialGradient(cx, cy, R * 0.95, cx, cy, R * 1.12)
        g.add_color_stop_rgba(0, 0.4, 0.6, 1.0, 0.35)
        g.add_color_stop_rgba(1, 0.4, 0.6, 1.0, 0)
        ctx.set_source(g)
        ctx.arc(cx, cy, R * 1.12, 0, 6.283)
        ctx.fill()
        g = cairo.RadialGradient(cx - R * 0.35, cy - R * 0.4, R * 0.1, cx, cy, R)
        g.add_color_stop_rgb(0, *mix(SEA_BOT, (1, 1, 1), 0.12))
        g.add_color_stop_rgb(1, *mix(SEA_TOP, (0, 0, 0), 0.3))
        ctx.set_source(g)
        ctx.arc(cx, cy, R, 0, 6.283)
        ctx.fill()
        ctx.save()
        ctx.arc(cx, cy, R, 0, 6.283)
        ctx.clip()
        # graticule
        ctx.set_line_width(1.1)
        for lon in range(-180, 180, 15):
            lat = np.linspace(-90, 90, 90)
            x, y, c = self.proj(np.full_like(lat, lon), lat)
            self._polyline(ctx, x, y, c)
        for latv in range(-75, 90, 15):
            lon = np.linspace(-180, 180, 181)
            x, y, c = self.proj(lon, np.full_like(lon, latv))
            self._polyline(ctx, x, y, c)
        ctx.set_source_rgba(*GRID, 0.16)
        ctx.stroke()
        # land
        for name in ("world50",):
            for r in rings(name):
                x, y, c = self.proj(r[:, 0], r[:, 1])
                if c.max() < 0:
                    continue
                # push hidden points to the limb
                hid = c < 0
                if hid.any():
                    dx, dy = x - cx, y - cy
                    d = np.hypot(dx, dy) + 1e-9
                    x = np.where(hid, cx + dx / d * R, x)
                    y = np.where(hid, cy + dy / d * R, y)
                ctx.move_to(x[0], y[0])
                for xi, yi in zip(x[1:], y[1:]):
                    ctx.line_to(xi, yi)
                ctx.close_path()
        ctx.set_source_rgba(*LAND, land_alpha)
        ctx.fill_preserve()
        ctx.set_line_width(1.2)
        ctx.set_source_rgba(*COAST, land_alpha)
        ctx.stroke()
        # terminator-style shading
        g = cairo.RadialGradient(cx - R * 0.3, cy - R * 0.35, R * 0.2, cx, cy, R * 1.05)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.10)
        g.add_color_stop_rgba(0.6, 0, 0, 0, 0.0)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.55)
        ctx.set_source(g)
        ctx.paint()
        ctx.restore()

    def _polyline(self, ctx, x, y, c):
        pen = False
        for xi, yi, ci in zip(x, y, c):
            if ci > 0:
                if pen:
                    ctx.line_to(xi, yi)
                else:
                    ctx.move_to(xi, yi)
                    pen = True
            else:
                pen = False

    def route(self, ctx, keys_or_lls, progress, color, width=5, dash=None, glow=True, alpha=1.0):
        pts = [PLACES[k] if isinstance(k, str) else k for k in keys_or_lls]
        path = []
        for a, b in zip(pts[:-1], pts[1:]):
            path.extend(great_circle(a, b, 60)[:-1])
        path.append(pts[-1])
        path = np.asarray(path)
        x, y, c = self.proj(path[:, 0], path[:, 1])
        return _partial_polyline(ctx, list(zip(x, y)), progress, color, width, dash, glow, alpha)


def great_circle(a, b, n):
    lon1, lat1, lon2, lat2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    v1 = np.array([math.cos(lat1) * math.cos(lon1), math.cos(lat1) * math.sin(lon1), math.sin(lat1)])
    v2 = np.array([math.cos(lat2) * math.cos(lon2), math.cos(lat2) * math.sin(lon2), math.sin(lat2)])
    om = math.acos(clamp(float(v1 @ v2), -1, 1))
    out = []
    for i in range(n + 1):
        f = i / n
        if om < 1e-9:
            v = v1
        else:
            v = (math.sin((1 - f) * om) * v1 + math.sin(f * om) * v2) / math.sin(om)
        out.append((math.degrees(math.atan2(v[1], v[0])), math.degrees(math.asin(clamp(v[2], -1, 1)))))
    return out


# ------------------------------------------------------------------ overlays (screen space)
def _partial_polyline(ctx, pts, progress, color, width, dash, glow, alpha):
    if progress <= 0 or len(pts) < 2:
        return None
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:])]
    total = sum(seg)
    target = total * clamp(progress)
    out = [pts[0]]
    acc = 0
    for (a, b), s in zip(zip(pts[:-1], pts[1:]), seg):
        if acc + s >= target:
            f = (target - acc) / s if s else 0
            out.append((lerp(a[0], b[0], f), lerp(a[1], b[1], f)))
            break
        out.append(b)
        acc += s
    for pass_, (w, a) in enumerate(((width * 3.2, 0.25), (width, 1.0))):
        if pass_ == 0 and not glow:
            continue
        ctx.move_to(*out[0])
        for p in out[1:]:
            ctx.line_to(*p)
        ctx.set_line_width(w)
        if dash and pass_ == 1:
            ctx.set_dash(dash)
        set_rgba(ctx, color, a * alpha)
        ctx.stroke()
        ctx.set_dash([])
    return out[-1], (out[-1][0] - out[-2][0], out[-1][1] - out[-2][1]) if len(out) > 1 else (1, 0)


def catmull(points, n=16):
    pts = [points[0]] + list(points) + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(points[-1])
    return out


def arrow(ctx, pts, progress, color, width=14, head=34, alpha=1.0, outline=True):
    """Thick campaign arrow along screen-space points (smoothed), drawn up to progress."""
    if progress <= 0:
        return
    path = catmull(pts, 20)
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path[:-1], path[1:])]
    total = sum(seg)
    target = total * clamp(progress)
    shaft_end = max(0, target - head * 0.8)
    out, acc = [path[0]], 0
    tip, direction = path[0], (1, 0)
    for (a, b), s in zip(zip(path[:-1], path[1:]), seg):
        if s == 0:
            continue
        if acc + s >= target:
            f = (target - acc) / s
            tip = (lerp(a[0], b[0], f), lerp(a[1], b[1], f))
            direction = (b[0] - a[0], b[1] - a[1])
            break
        acc += s
        tip, direction = b, (b[0] - a[0], b[1] - a[1])
    acc = 0
    for (a, b), s in zip(zip(path[:-1], path[1:]), seg):
        if acc + s >= shaft_end:
            f = (shaft_end - acc) / s if s else 0
            out.append((lerp(a[0], b[0], f), lerp(a[1], b[1], f)))
            break
        out.append(b)
        acc += s
    d = math.hypot(*direction) or 1
    ux, uy = direction[0] / d, direction[1] / d
    px, py = -uy, ux
    headpts = [(tip[0] + ux * 4, tip[1] + uy * 4), (tip[0] - ux * head + px * head * 0.62, tip[1] - uy * head + py * head * 0.62),
               (tip[0] - ux * head * 0.8, tip[1] - uy * head * 0.8),
               (tip[0] - ux * head - px * head * 0.62, tip[1] - uy * head - py * head * 0.62)]
    for pass_ in (0, 1):
        col = (0.05, 0.05, 0.08) if pass_ == 0 else color
        extra = 5 if pass_ == 0 else 0
        if pass_ == 0 and not outline:
            continue
        if len(out) > 1:
            ctx.move_to(*out[0])
            for p in out[1:]:
                ctx.line_to(*p)
            ctx.set_line_width(width + extra)
            set_rgba(ctx, col, alpha * (0.6 if pass_ == 0 else 1))
            ctx.stroke()
        if progress > 0.02:
            ctx.move_to(*headpts[0])
            for p in headpts[1:]:
                ctx.line_to(*p)
            ctx.close_path()
            if pass_ == 0:
                ctx.set_line_width(extra)
                set_rgba(ctx, col, alpha * 0.6)
                ctx.stroke_preserve()
            set_rgba(ctx, col, alpha * (0.6 if pass_ == 0 else 1))
            ctx.fill()


def marker(ctx, x, y, kind="dot", color=(1, 1, 1), size=9, alpha=1.0, t=0.0, pulse=False):
    if alpha <= 0:
        return
    if pulse:
        ph = (t * 0.9) % 1.0
        ctx.arc(x, y, size * (1 + ph * 3.5), 0, 6.283)
        ctx.set_line_width(2.5)
        set_rgba(ctx, color, alpha * (1 - ph))
        ctx.stroke()
    if kind == "dot":
        ctx.arc(x, y, size, 0, 6.283)
        set_rgba(ctx, color, alpha)
        ctx.fill_preserve()
        ctx.set_line_width(2.5)
        ctx.set_source_rgba(0.05, 0.05, 0.1, alpha * 0.8)
        ctx.stroke()
    elif kind == "square":
        ctx.rectangle(x - size, y - size, size * 2, size * 2)
        set_rgba(ctx, color, alpha)
        ctx.fill_preserve()
        ctx.set_line_width(2.5)
        ctx.set_source_rgba(0.05, 0.05, 0.1, alpha * 0.8)
        ctx.stroke()
    elif kind == "peak":
        ctx.move_to(x, y - size * 1.3)
        ctx.line_to(x + size * 1.1, y + size * 0.7)
        ctx.line_to(x - size * 1.1, y + size * 0.7)
        ctx.close_path()
        set_rgba(ctx, color, alpha)
        ctx.fill_preserve()
        ctx.set_line_width(2)
        ctx.set_source_rgba(0.05, 0.05, 0.1, alpha * 0.8)
        ctx.stroke()
    elif kind == "star":
        for k in range(10):
            r = size * (1.5 if k % 2 == 0 else 0.62)
            a = -math.pi / 2 + k * math.pi / 5
            (ctx.move_to if k == 0 else ctx.line_to)(x + math.cos(a) * r, y + math.sin(a) * r)
        ctx.close_path()
        set_rgba(ctx, color, alpha)
        ctx.fill_preserve()
        ctx.set_line_width(2)
        ctx.set_source_rgba(0.05, 0.05, 0.1, alpha * 0.8)
        ctx.stroke()
    elif kind == "sunk":
        ctx.set_line_width(5)
        for s in (-1, 1):
            ctx.move_to(x - size, y - size * s)
            ctx.line_to(x + size, y + size * s)
        set_rgba(ctx, color, alpha)
        ctx.stroke()


def label(ctx, text, x, y, size=30, color=LABEL, alpha=1.0, anchor="lm", font="cond", box=False,
          box_color=(0.04, 0.07, 0.15), tracking=0.04, shadow=(2, 3, 0.7)):
    if alpha <= 0:
        return
    if box:
        w = text_width(text, font, size, tracking)
        pad = size * 0.35
        bx = {"l": x, "c": x - w / 2, "r": x - w}[anchor[0]] - pad
        by = y - size * 0.72 if anchor[1] == "m" else (y - size * 1.2 if anchor[1] == "b" else y - pad * 0.4)
        ctx.rectangle(bx, by, w + pad * 2, size * 1.44)
        set_rgba(ctx, box_color, 0.78 * alpha)
        ctx.fill()
    draw_text(ctx, text, x, y, font, size, color, anchor, alpha, tracking, shadow=shadow)


def ship_icon(ctx, x, y, heading, size=16, color=BRIT, alpha=1.0):
    """Small wedge ship glyph pointing along heading (radians, screen space)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(heading)
    ctx.move_to(size, 0)
    ctx.line_to(-size * 0.8, -size * 0.45)
    ctx.line_to(-size * 0.5, 0)
    ctx.line_to(-size * 0.8, size * 0.45)
    ctx.close_path()
    set_rgba(ctx, color, alpha)
    ctx.fill_preserve()
    ctx.set_line_width(2)
    ctx.set_source_rgba(0.05, 0.05, 0.1, alpha * 0.8)
    ctx.stroke()
    ctx.restore()


def news_caption(ctx, title, sub=None, alpha=1.0, x=90, y=86, accent=BRIT):
    """1980s news-style caption strap, top-left."""
    if alpha <= 0:
        return
    w = text_width(title, "oswald", 44, 0.06) + 60
    if sub:
        w = max(w, text_width(sub, "cond_r", 28, 0.04) + 60)
    slide = (1 - alpha) * 40
    ctx.rectangle(x - slide, y, w, 70 if not sub else 110)
    ctx.set_source_rgba(0.06, 0.1, 0.22, 0.88 * alpha)
    ctx.fill()
    ctx.rectangle(x - slide, y, 10, 70 if not sub else 110)
    set_rgba(ctx, accent, alpha)
    ctx.fill()
    draw_text(ctx, title, x + 30 - slide, y + 52, "oswald", 44, (1, 1, 1), "lb", alpha, 0.06)
    if sub:
        draw_text(ctx, sub, x + 30 - slide, y + 94, "cond_r", 28, (0.8, 0.86, 1.0), "lb", alpha, 0.04)


def legend(ctx, items, x, y, alpha=1.0):
    if alpha <= 0:
        return
    h = 44 * len(items) + 16
    w = max(text_width(t, "cond", 26, 0.04) for t, _ in items) + 90
    ctx.rectangle(x, y, w, h)
    ctx.set_source_rgba(0.04, 0.07, 0.15, 0.75 * alpha)
    ctx.fill()
    for i, (text, col) in enumerate(items):
        yy = y + 30 + i * 44
        ctx.rectangle(x + 18, yy - 9, 40, 18)
        set_rgba(ctx, col, alpha)
        ctx.fill()
        draw_text(ctx, text, x + 72, yy, "cond", 26, (1, 1, 1), "lm", alpha, 0.04)
