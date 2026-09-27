"""Painterly environment + effects: skies, sea, clouds, terrain, smoke, fire,
flares, tracer, explosions, weather. All deterministic in time t."""
import functools
import math

import cairo
import numpy as np

from .core import (H, W, clamp, fbm, hash01, hexc, lerp, mix, noise_surface, paint_surface,
                   poly, radial_glow, set_rgba, smooth, vgrad)


# ---------------------------------------------------------------- sky
def sky(ctx, stops, horizon=H):
    ctx.rectangle(0, 0, W, horizon + 2)
    ctx.set_source(vgrad(ctx, 0, 0, 0, horizon, stops))
    ctx.fill()


def sun(ctx, x, y, r, color, glow=3.5, alpha=1.0):
    radial_glow(ctx, x, y, r * glow, color, 0.55 * alpha)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    set_rgba(ctx, color, alpha)
    ctx.fill()


@functools.lru_cache(maxsize=16)
def _cloud_layer(seed, w, h, color, lo, hi, alpha, octaves, base):
    return noise_surface(w, h, color, seed, lo, hi, alpha, octaves, base)


def clouds(ctx, t, y0, y1, color, seed=1, speed=8.0, lo=0.5, hi=0.8, alpha=0.9, stretch=2.2, base=4):
    """Band of drifting fbm clouds between y0 and y1 (mirror-tiled, so no seams)."""
    h = int(y1 - y0)
    tile_w = 2200
    surf = _cloud_layer(seed, tile_w, max(h, 8), tuple(color), lo, hi, alpha, 5, base)
    off = (t * speed) % (2 * tile_w)
    mask = vgrad(ctx, 0, 0, 0, h, [(0, (0, 0, 0), 0), (0.25, (0, 0, 0), 1), (0.75, (0, 0, 0), 1),
                                   (1, (0, 0, 0), 0)])
    ctx.save()
    ctx.rectangle(0, y0, W, h)
    ctx.clip()
    x = -off
    i = 0
    while x < W:
        if x + tile_w > 0:
            ctx.save()
            ctx.translate(x, y0)
            if i % 2:
                ctx.translate(tile_w, 0)
                ctx.scale(-1, 1)
            ctx.set_source_surface(surf, 0, 0)
            ctx.mask(mask)
            ctx.restore()
        x += tile_w
        i += 1
    ctx.restore()


def stars(ctx, n=300, seed=3, alpha=1.0, y1=H * 0.7, t=0):
    r = np.random.default_rng(seed)
    xs, ys = r.random(n) * W, r.random(n) ** 1.4 * y1
    ss, tw = r.random(n), r.random(n) * 6.28
    for x, y, s, p in zip(xs, ys, ss, tw):
        a = alpha * (0.35 + 0.65 * s) * (0.75 + 0.25 * math.sin(t * 2.5 + p))
        ctx.arc(x, y, 0.6 + 1.3 * s * s, 0, 6.283)
        ctx.set_source_rgba(0.9, 0.93, 1.0, a)
        ctx.fill()


# ---------------------------------------------------------------- sea
def sea(ctx, t, horizon, top, bottom, seed=7, strokes=520, hi=(1, 1, 1), hi_alpha=0.18, speed=1.0,
        y_end=H, chop=1.0):
    ctx.rectangle(0, horizon, W, y_end - horizon)
    ctx.set_source(vgrad(ctx, 0, horizon, 0, y_end, [(0, top), (1, bottom)]))
    ctx.fill()
    r = np.random.default_rng(seed)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(strokes):
        d = r.random() ** 1.9            # 0 = horizon, 1 = foreground
        y = horizon + d * (y_end - horizon)
        L = (8 + 90 * d) * (0.5 + r.random())
        ph = r.random() * 6.28
        x = (r.random() * (W + 400) + t * (6 + 40 * d) * speed * (1 if i % 2 else -0.4)) % (W + 400) - 200
        yy = y + math.sin(t * (0.9 + r.random()) + ph) * (1 + 5 * d) * chop
        a = hi_alpha * (0.3 + 0.7 * d) * (0.5 + 0.5 * math.sin(t * 1.3 + ph))
        ctx.set_line_width(0.6 + 3.2 * d)
        ctx.move_to(x, yy)
        ctx.curve_to(x + L * 0.3, yy - 1.5 * d, x + L * 0.7, yy - 1.5 * d, x + L, yy)
        ctx.set_source_rgba(*hi[:3], a)
        ctx.stroke()


def reflection(ctx, x, y, w, color, alpha=0.35, t=0, rows=14):
    """Broken shimmer reflection beneath a bright source or silhouette."""
    for i in range(rows):
        d = i / rows
        yy = y + 3 + i * 5
        ww = w * (1 - d * 0.5) * (0.6 + 0.4 * math.sin(t * 3 + i * 1.7))
        ctx.rectangle(x - ww / 2, yy, ww, 2.2)
        ctx.set_source_rgba(*color[:3], alpha * (1 - d))
        ctx.fill()


# ---------------------------------------------------------------- terrain
@functools.lru_cache(maxsize=64)
def ridge_profile(seed, n=240, rough=0.5, octaves=6):
    r = np.random.default_rng(seed)
    x = np.linspace(0, 1, n)
    y = np.zeros(n)
    amp = 1.0
    for o in range(octaves):
        k = 2 ** o * 2
        pts = r.random(k + 2)
        y += amp * np.interp(x * (k + 1), np.arange(k + 2), pts)
        amp *= rough
    y = (y - y.min()) / (y.max() - y.min() + 1e-9)
    return tuple(y)


def ridge(ctx, seed, base_y, height, color, x0=-50, x1=W + 50, rough=0.5, shape=None, top_color=None,
          crags=0, crag_seed=0):
    """Mountain/hill silhouette. shape(u)->multiplier shapes the skyline."""
    prof = ridge_profile(seed, 240, rough)
    n = len(prof)
    pts = []
    for i, v in enumerate(prof):
        u = i / (n - 1)
        m = shape(u) if shape else 1.0
        pts.append((lerp(x0, x1, u), base_y - v * height * m))
    ctx.move_to(x0, H + 10)
    for p in pts:
        ctx.line_to(*p)
    ctx.line_to(x1, H + 10)
    ctx.close_path()
    if top_color is not None:
        top = min(p[1] for p in pts)
        ctx.set_source(vgrad(ctx, 0, top, 0, base_y + 40, [(0, top_color), (1, color)]))
    else:
        set_rgba(ctx, color)
    ctx.fill()
    if crags:
        r = np.random.default_rng(crag_seed or seed + 1)
        for _ in range(crags):
            u = r.random()
            i = int(u * (n - 1))
            x, y = pts[i]
            w = 10 + r.random() * 40
            h = 8 + r.random() * 30
            ctx.move_to(x - w / 2, y + 6)
            ctx.line_to(x - w * 0.35, y - h * 0.7)
            ctx.line_to(x - w * 0.05, y - h)
            ctx.line_to(x + w * 0.3, y - h * 0.8)
            ctx.line_to(x + w / 2, y + 6)
            ctx.close_path()
            set_rgba(ctx, color)
            ctx.fill()
    return pts


def ground_texture(ctx, y0, y1, color, seed=11, alpha=0.25, n=400, tuft=(0.2, 0.25, 0.12), x1=W):
    """Grass/tussock strokes across a foreground band."""
    r = np.random.default_rng(seed)
    for _ in range(n):
        d = r.random()
        y = lerp(y0, y1, d ** 0.8)
        x = r.random() * x1
        h = 4 + 18 * d
        ctx.set_line_width(1 + 1.5 * d)
        for k in range(3):
            ang = -math.pi / 2 + (r.random() - 0.5) * 0.9
            ctx.move_to(x + k * 2, y)
            ctx.line_to(x + k * 2 + math.cos(ang) * h, y + math.sin(ang) * h)
        ctx.set_source_rgba(*tuft, alpha)
        ctx.stroke()


# ---------------------------------------------------------------- effects
@functools.lru_cache(maxsize=8)
def _puff(seed, size=160):
    """Soft, lumpy smoke sprite: fbm texture under a radial falloff (white, alpha only)."""
    n = fbm(size, size, seed=500 + seed, octaves=5, base=3)
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    d = np.sqrt((x - size / 2) ** 2 + (y - size / 2) ** 2) / (size / 2)
    fall = np.clip(1 - d, 0, 1) ** 1.2
    a = np.clip((n * 1.25 - 0.18) * fall * 1.6, 0, 1)
    arr = np.zeros((size, size, 4), dtype=np.uint8)
    arr[:, :, :3] = 255
    arr[:, :, 3] = (a * 255).astype(np.uint8)
    from .core import rgba_to_surface
    return rgba_to_surface(arr)


def smoke(ctx, x, y, t, seed=0, rate=6.0, life=9.0, rise=38.0, spread=1.0, size=30.0,
          color=(0.12, 0.11, 0.11), alpha=0.55, wind=18.0, start=0.0, grow=4.0, stop=None):
    """Billowing smoke column from (x,y); deterministic in t. Drawn with textured puffs.
    stop: optional time after which no new puffs are emitted."""
    if t < start:
        return
    n = int((t - start) * rate) + 1
    first = max(0, n - int(life * rate) - 1)
    for i in range(first, n):
        b = start + i / rate
        age = t - b
        if age < 0 or age > life or (stop is not None and b > stop):
            continue
        u = age / life
        j1, j2 = hash01(seed, i, 1) - 0.5, hash01(seed, i, 2) - 0.5
        px = x + wind * age * (0.6 + 0.8 * u) + j1 * 30 * spread * (0.3 + u) + math.sin(age * 0.7 + i) * 6
        py = y - rise * age * (1 - 0.25 * u) + j2 * 12
        r = size * (0.4 + grow * u ** 0.7) * (0.8 + 0.4 * hash01(seed, i, 3))
        a = alpha * min(1, age * 3) * (1 - u) ** 1.4
        shade = 0.8 + 0.4 * hash01(seed, i, 4)
        c = tuple(min(1, ch * shade) for ch in color[:3])
        sprite = _puff(i % 6)
        ctx.save()
        ctx.translate(px, py)
        ctx.rotate(hash01(seed, i, 5) * 6.283 + age * 0.15 * (1 if i % 2 else -1))
        k = 2 * r / 160
        ctx.scale(k, k)
        ctx.translate(-80, -80)
        ctx.set_source_rgba(*c, min(1.0, a * 1.5))
        ctx.mask_surface(sprite, 0, 0)
        ctx.restore()


def fire(ctx, x, y, t, w=60, h=70, seed=0, intensity=1.0):
    radial_glow(ctx, x, y - h * 0.3, w * 3.2, (1.0, 0.45, 0.1), 0.35 * intensity)
    for k in range(18):
        ph = hash01(seed, k) * 6.28
        fx = x + (hash01(seed, k, 2) - 0.5) * w * 1.1
        edge = 1 - abs(fx - x) / (w * 0.6)
        fh = h * (0.35 + 0.65 * edge) * (0.55 + 0.45 * math.sin(t * (6 + k * 0.7) + ph) ** 2)
        fw = w * (0.08 + 0.06 * hash01(seed, k, 4))
        sway = math.sin(t * 4 + ph) * fw * 1.2
        g = cairo.LinearGradient(fx, y, fx, y - fh)
        g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.9 * intensity)
        g.add_color_stop_rgba(0.35, 1, 0.6, 0.15, 0.8 * intensity)
        g.add_color_stop_rgba(0.8, 0.85, 0.2, 0.03, 0.35 * intensity)
        g.add_color_stop_rgba(1, 0.6, 0.1, 0.02, 0)
        ctx.move_to(fx - fw, y)
        ctx.curve_to(fx - fw * 1.2, y - fh * 0.45, fx + sway - fw * 0.4, y - fh * 0.75, fx + sway, y - fh)
        ctx.curve_to(fx + sway + fw * 0.3, y - fh * 0.7, fx + fw * 1.2, y - fh * 0.4, fx + fw, y)
        ctx.close_path()
        ctx.set_source(g)
        ctx.fill()


def flash(ctx, x, y, t, t0, r=260, dur=0.9, color=(1, 0.85, 0.55)):
    a = t - t0
    if a < 0 or a > dur:
        return 0.0
    k = (1 - a / dur) ** 2
    radial_glow(ctx, x, y, r * (0.6 + 0.8 * a / dur), color, k)
    radial_glow(ctx, x, y, r * 0.25, (1, 1, 0.95), k)
    return k


def splash(ctx, x, y, t, t0, h=180, w=70, dur=3.0, color=(0.92, 0.95, 0.97)):
    a = t - t0
    if a < 0 or a > dur:
        return
    u = a / dur
    hh = h * math.sin(min(1, u * 2.2) * math.pi / 2) * (1 - u * 0.4)
    alpha = 0.9 * (1 - u) ** 1.2
    for k in range(7):
        off = (k - 3) / 3
        top_x = x + off * w * (0.6 + u)
        top_y = y - hh * (1 - abs(off) * 0.5)
        ctx.move_to(x + off * w * 0.3 - 8, y)
        ctx.curve_to(x + off * w * 0.3, y - hh * 0.4, top_x - 10, top_y + 20, top_x, top_y)
        ctx.curve_to(top_x + 10, top_y + 20, x + off * w * 0.3 + 10, y - hh * 0.4, x + off * w * 0.3 + 8, y)
        ctx.close_path()
        ctx.set_source_rgba(*color, alpha * (1 - abs(off) * 0.3))
        ctx.fill()
    for k in range(18):  # spray droplets
        ang = -math.pi / 2 + (hash01(k, 9) - 0.5) * 2.2
        sp = h * (0.4 + hash01(k, 8))
        px = x + math.cos(ang) * sp * u * 1.2
        py = y + math.sin(ang) * sp * u * 1.2 + 260 * u * u
        ctx.arc(px, py, 2 + 3 * hash01(k, 7), 0, 6.283)
        ctx.set_source_rgba(*color, alpha)
        ctx.fill()


def starshell(ctx, x0, y0, t, t0, fall=18.0, drift=12.0, life=14.0):
    """Illumination flare descending under a parachute. Returns intensity."""
    a = t - t0
    if a < 0 or a > life:
        return 0.0, (0, 0)
    inten = min(1, a * 2) * (1 - (a / life) ** 3)
    flick = 0.85 + 0.15 * math.sin(a * 23) * math.sin(a * 7.3)
    x = x0 + drift * a
    y = y0 + fall * a
    ctx.set_line_width(2.2)
    ctx.move_to(x, y)
    for k in range(10):
        ctx.line_to(x - drift * k * 0.5 + math.sin(k + a) * 3, y - fall * k * 0.6)
    ctx.set_source_rgba(0.85, 0.85, 0.8, 0.25 * inten)
    ctx.stroke()
    radial_glow(ctx, x, y, 520 * inten, (1.0, 0.93, 0.75), 0.30 * inten * flick)
    radial_glow(ctx, x, y, 70, (1, 1, 0.9), 0.9 * inten * flick)
    ctx.arc(x, y, 5, 0, 6.283)
    ctx.set_source_rgba(1, 1, 1, inten)
    ctx.fill()
    return inten * flick, (x, y)


def tracer(ctx, p0, p1, t, t0, speed=1.4, color=(1.0, 0.35, 0.15), n=6, gap=0.09, arc=0.0, width=3.0):
    """Stream of tracer rounds from p0 to p1 fired from t0."""
    for k in range(n):
        a = (t - t0 - k * gap) * speed
        if a < 0 or a > 1:
            continue
        x = lerp(p0[0], p1[0], a)
        y = lerp(p0[1], p1[1], a) - arc * 4 * a * (1 - a)
        a2 = max(0, a - 0.05)
        x2 = lerp(p0[0], p1[0], a2)
        y2 = lerp(p0[1], p1[1], a2) - arc * 4 * a2 * (1 - a2)
        ctx.set_line_width(width * 3)
        ctx.move_to(x2, y2)
        ctx.line_to(x, y)
        ctx.set_source_rgba(*color, 0.25)
        ctx.stroke()
        ctx.set_line_width(width)
        ctx.move_to(x2, y2)
        ctx.line_to(x, y)
        ctx.set_source_rgba(1, 0.9, 0.7, 0.95)
        ctx.stroke()


def rain(ctx, t, alpha=0.18, n=260, angle=0.25, speed=1400, length=40, seed=5):
    r = np.random.default_rng(seed)
    ctx.set_line_width(1.2)
    for _ in range(n):
        x0, y0, s = r.random() * (W + 400), r.random() * H, 0.7 + r.random() * 0.6
        y = (y0 + t * speed * s) % (H + 100) - 50
        x = (x0 + y * angle) % (W + 200) - 100
        ctx.move_to(x, y)
        ctx.line_to(x - length * angle * s, y - length * s)
    ctx.set_source_rgba(0.85, 0.88, 0.92, alpha)
    ctx.stroke()


def snow(ctx, t, alpha=0.7, n=260, seed=6, wind=40):
    r = np.random.default_rng(seed)
    for _ in range(n):
        x0, y0, s = r.random() * W, r.random() * H, 0.4 + r.random()
        y = (y0 + t * 45 * s) % H
        x = (x0 + t * wind * s + math.sin(t + y0) * 12) % W
        ctx.arc(x, y, 1.0 + 1.8 * s, 0, 6.283)
        ctx.set_source_rgba(1, 1, 1, alpha * (0.4 + 0.4 * s))
        ctx.fill()


def haze(ctx, y0, y1, color, alpha=0.5):
    ctx.rectangle(0, y0, W, y1 - y0)
    ctx.set_source(vgrad(ctx, 0, y0, 0, y1, [(0, color, 0), (0.5, color, alpha), (1, color, 0)]))
    ctx.fill()


def darken(ctx, alpha, color=(0, 0, 0)):
    if alpha <= 0:
        return
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgba(*color, alpha)
    ctx.fill()


def light_rays(ctx, x, y, t, color=(1, 0.9, 0.7), alpha=0.12, n=9, length=1400, seed=2):
    for k in range(n):
        ang = math.pi / 2 + (hash01(seed, k) - 0.5) * 1.2 + math.sin(t * 0.1 + k) * 0.02
        w = 0.02 + 0.05 * hash01(seed, k, 2)
        ctx.move_to(x, y)
        ctx.line_to(x + math.cos(ang - w) * length, y + math.sin(ang - w) * length)
        ctx.line_to(x + math.cos(ang + w) * length, y + math.sin(ang + w) * length)
        ctx.close_path()
        g = cairo.RadialGradient(x, y, 0, x, y, length)
        g.add_color_stop_rgba(0, *color, alpha)
        g.add_color_stop_rgba(1, *color, 0)
        ctx.set_source(g)
        ctx.fill()
