"""Shared drawing utilities: canvas, colour, easing, text, noise."""
import functools
import math
import os

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
FPS = 30

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

FONTS = {
    "stencil": "StardosStencil-Bold.ttf",
    "stencil_r": "StardosStencil-Regular.ttf",
    "oswald": "Oswald-Bold.ttf",
    "oswald_r": "Oswald-Regular.ttf",
    "cond": "RobotoCondensed-Bold.ttf",
    "cond_r": "RobotoCondensed-Regular.ttf",
    "serif": "PT_Serif-Web-Regular.ttf",
    "serif_b": "PT_Serif-Web-Bold.ttf",
    "serif_i": "PT_Serif-Web-Italic.ttf",
    "type": "SpecialElite-Regular.ttf",
    "courier": "CourierPrime-Bold.ttf",
    "vt": "VT323-Regular.ttf",
    "bebas": "BebasNeue-Regular.ttf",
    "black": "ArchivoBlack-Regular.ttf",
}


# ---------------------------------------------------------------- maths
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_in_out(t):
    t = clamp(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def ramp(t, a, b):
    """0 before a, 1 after b, smooth in between."""
    if b <= a:
        return 1.0 if t >= a else 0.0
    return smooth((t - a) / (b - a))


def fade_window(t, a, b, fin=0.4, fout=0.4):
    return min(ramp(t, a, a + fin), 1 - ramp(t, b - fout, b))


def hexc(h, a=None):
    h = h.lstrip("#")
    c = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return c if a is None else c + (a,)


def mix(c1, c2, t):
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def rng(*seed):
    return np.random.default_rng(abs(hash(seed)) % (2 ** 32))


def hash01(*vals):
    """Deterministic pseudo-random in [0,1) from integers/floats."""
    x = 0.0
    for i, v in enumerate(vals):
        x += v * (12.9898 + 31.7 * i)
    s = math.sin(x) * 43758.5453
    return s - math.floor(s)


# ---------------------------------------------------------------- canvas
def new_canvas(w=W, h=H):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    return surf, ctx


def surface_to_rgb(surf):
    """Cairo ARGB32 surface -> float32 HxWx3 RGB in [0,1] (assumes opaque)."""
    surf.flush()
    w, h = surf.get_width(), surf.get_height()
    buf = np.ndarray((h, surf.get_stride() // 4, 4), dtype=np.uint8, buffer=surf.get_data())[:, :w]
    return buf[:, :, 2::-1].astype(np.float32) * (1 / 255.0)


def rgba_to_surface(arr):
    """uint8 HxWx4 straight-alpha RGBA -> cairo ImageSurface (premultiplied)."""
    arr = np.asarray(arr, dtype=np.uint8)
    h, w = arr.shape[:2]
    a = arr[:, :, 3:4].astype(np.uint16)
    rgb = (arr[:, :, :3].astype(np.uint16) * a // 255).astype(np.uint8)
    bgra = np.empty((h, w, 4), dtype=np.uint8)
    bgra[:, :, 0] = rgb[:, :, 2]
    bgra[:, :, 1] = rgb[:, :, 1]
    bgra[:, :, 2] = rgb[:, :, 0]
    bgra[:, :, 3] = arr[:, :, 3]
    stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, w)
    if stride != w * 4:
        pad = np.zeros((h, stride // 4, 4), dtype=np.uint8)
        pad[:, :w] = bgra
        bgra = pad
    data = bytearray(bgra.tobytes())
    surf = cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, w, h, stride)
    # pycairo holds a reference to `data` for the lifetime of the surface
    return surf


def paint_surface(ctx, surf, x, y, alpha=1.0, scale=1.0):
    ctx.save()
    ctx.translate(x, y)
    if scale != 1.0:
        ctx.scale(scale, scale)
    ctx.set_source_surface(surf, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint_with_alpha(alpha)
    ctx.restore()


# ---------------------------------------------------------------- text
@functools.lru_cache(maxsize=64)
def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, FONTS[name]), int(round(size)))


@functools.lru_cache(maxsize=4096)
def text_surface(text, fname, size, color=(1, 1, 1), tracking=0.0, stroke=0, stroke_color=(0, 0, 0)):
    """Render text with PIL; returns (surface, width, height, ascent)."""
    f = font(fname, size)
    ascent, descent = f.getmetrics()
    pad = int(stroke + 4)
    if tracking == 0:
        l, t, r, b = f.getbbox(text, stroke_width=stroke)
        width = int(r) + 2 * pad
    else:
        width = int(sum(f.getlength(ch) + tracking * size for ch in text) - tracking * size) + 2 * pad
    height = ascent + descent + 2 * pad
    img = Image.new("RGBA", (max(width, 1), height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = tuple(int(c * 255) for c in color[:3]) + (255,)
    scol = tuple(int(c * 255) for c in stroke_color[:3]) + (255,)
    if tracking == 0:
        d.text((pad, pad), text, font=f, fill=col, stroke_width=stroke, stroke_fill=scol)
    else:
        x = pad
        for ch in text:
            d.text((x, pad), ch, font=f, fill=col, stroke_width=stroke, stroke_fill=scol)
            x += f.getlength(ch) + tracking * size
    return rgba_to_surface(np.array(img)), width, height, ascent + pad


def text_width(text, fname, size, tracking=0.0):
    return text_surface(text, fname, size, (1, 1, 1), tracking)[1] - 8


def draw_text(ctx, text, x, y, fname, size, color=(1, 1, 1), anchor="lb", alpha=1.0,
              tracking=0.0, stroke=0, stroke_color=(0, 0, 0), shadow=None):
    """anchor: first char l/c/r horizontal, second t/m/b(baseline) vertical."""
    if alpha <= 0.002 or not text:
        return 0
    surf, w, h, base = text_surface(text, fname, round(size), tuple(color[:3]), tracking, stroke,
                                    tuple(stroke_color[:3]))
    pad = int(stroke + 4)
    ha, va = anchor[0], anchor[1]
    ox = {"l": -pad, "c": -w / 2, "r": -w + pad}[ha]
    oy = {"t": -pad, "m": -h / 2, "b": -base}[va]
    if shadow:
        sx, sy, sa = shadow
        ssurf = text_surface(text, fname, round(size), (0, 0, 0), tracking, stroke, (0, 0, 0))[0]
        paint_surface(ctx, ssurf, round(x + ox + sx), round(y + oy + sy), alpha * sa)
    paint_surface(ctx, surf, round(x + ox), round(y + oy), alpha)
    return w - 2 * pad


def typed(text, progress):
    """Typewriter reveal of text for progress in [0,1]."""
    n = int(round(len(text) * clamp(progress)))
    return text[:n]


# ---------------------------------------------------------------- noise
@functools.lru_cache(maxsize=32)
def fbm(w, h, seed=0, octaves=5, base=4, persistence=0.55):
    """Fractal value noise in [0,1], shape (h, w)."""
    r = np.random.default_rng(seed)
    acc = np.zeros((h, w), dtype=np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        gw, gh = base * 2 ** o + 1, max(2, int(base * 2 ** o * h / w) + 1)
        grid = r.random((gh, gw)).astype(np.float32)
        img = Image.fromarray((grid * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        acc += amp * np.asarray(img, dtype=np.float32) / 255
        tot += amp
        amp *= persistence
    acc /= tot
    acc -= acc.min()
    acc /= max(acc.max(), 1e-6)
    return acc


def noise_surface(w, h, color, seed=0, lo=0.45, hi=0.75, alpha=1.0, octaves=5, base=4):
    """Cloud/texture layer: colour with alpha from thresholded fbm."""
    n = fbm(w, h, seed, octaves, base)
    a = np.clip((n - lo) / (hi - lo), 0, 1) * alpha
    arr = np.empty((h, w, 4), dtype=np.uint8)
    arr[:, :, 0] = int(color[0] * 255)
    arr[:, :, 1] = int(color[1] * 255)
    arr[:, :, 2] = int(color[2] * 255)
    arr[:, :, 3] = (a * 255).astype(np.uint8)
    return rgba_to_surface(arr)


# ---------------------------------------------------------------- paths
def poly(ctx, pts, close=True):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()


def smooth_poly(ctx, pts, close=True, tension=0.5):
    """Catmull-Rom spline through points."""
    n = len(pts)
    if n < 3:
        return poly(ctx, pts, close)
    P = list(pts)
    ctx.move_to(*P[0])
    rngi = range(n) if close else range(n - 1)
    for i in rngi:
        p0 = P[(i - 1) % n] if (close or i > 0) else P[i]
        p1 = P[i]
        p2 = P[(i + 1) % n]
        p3 = P[(i + 2) % n] if (close or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * tension / 3, p1[1] + (p2[1] - p0[1]) * tension / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * tension / 3, p2[1] - (p3[1] - p1[1]) * tension / 3)
        ctx.curve_to(*c1, *c2, *p2)
    if close:
        ctx.close_path()


def set_rgba(ctx, c, a=1.0):
    if len(c) == 4:
        ctx.set_source_rgba(c[0], c[1], c[2], c[3] * a)
    else:
        ctx.set_source_rgba(c[0], c[1], c[2], a)


def radial_glow(ctx, x, y, r, color, alpha=1.0, core=0.0):
    g = cairo.RadialGradient(x, y, r * core, x, y, r)
    g.add_color_stop_rgba(0, *color[:3], alpha)
    g.add_color_stop_rgba(0.35, *color[:3], alpha * 0.45)
    g.add_color_stop_rgba(1, *color[:3], 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def vgrad(ctx, x0, y0, x1, y1, stops):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for s in stops:
        off, c = s[0], s[1]
        a = s[2] if len(s) > 2 else (c[3] if len(c) == 4 else 1.0)
        g.add_color_stop_rgba(off, c[0], c[1], c[2], a)
    return g


def fill_rect_grad(ctx, x, y, w, h, stops, vertical=True):
    ctx.rectangle(x, y, w, h)
    ctx.set_source(vgrad(ctx, x, y, x if vertical else x + w, y + h if vertical else y, stops))
    ctx.fill()
