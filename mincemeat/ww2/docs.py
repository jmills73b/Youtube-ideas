"""Secret files, typed letters, stamps, photographs and the other paper of 1943.

All documents shown in the film are reconstructions: quoted words are taken
from published texts (see RESEARCH.md); letterheads and layout are
illustrative.
"""
import functools
import math

import cairo
import numpy as np

from engine.core import (H, W, clamp, draw_text, fbm, hash01, lerp, mix, poly, ramp, rgba_to_surface, set_rgba,
                         text_width, vgrad)

INK = (0.1, 0.09, 0.1)
RED = (0.72, 0.1, 0.08)
PAPER = (0.93, 0.91, 0.84)
MANILA = (0.8, 0.68, 0.45)
DESK = (0.27, 0.18, 0.12)


@functools.lru_cache(maxsize=8)
def _tex(w, h, seed, tone, dark):
    n = fbm(w, h, seed, 5, 4)
    fib = np.random.default_rng(seed).random((h, w)).astype(np.float32)
    k = ((n - 0.5) * 0.12 + (fib - 0.5) * 0.05)[:, :, None]
    col = np.array(tone, dtype=np.float32) * (1 - k) + np.array(dark, dtype=np.float32) * k
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    arr[:, :, :3] = (np.clip(col, 0, 1) * 255).astype(np.uint8)
    arr[:, :, 3] = 255
    return rgba_to_surface(arr)


def desk(ctx, seed=3):
    """Dark wooden desktop with grain."""
    ctx.set_source_surface(_tex(W, H, seed, DESK, (0.08, 0.05, 0.03)), 0, 0)
    ctx.paint()
    ctx.set_line_width(1.2)
    r = np.random.default_rng(seed)
    for i in range(70):
        y = r.random() * H
        ctx.move_to(0, y)
        for x in range(0, W + 60, 60):
            ctx.line_to(x, y + math.sin(x * 0.004 + i) * 8)
    ctx.set_source_rgba(0.05, 0.03, 0.02, 0.25)
    ctx.stroke()


def lamp_light(ctx, x, y, r=900, alpha=0.55):
    """Pool of desk-lamp light with darkness beyond."""
    g = cairo.RadialGradient(x, y, 50, x, y, r)
    g.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.0)
    g.add_color_stop_rgba(0.6, 0, 0, 0, alpha * 0.4)
    g.add_color_stop_rgba(1, 0, 0, 0, alpha)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(g)
    ctx.fill()


def sheet(ctx, x, y, w, h, angle=0.0, tone=PAPER, seed=1, shadow=True):
    """A sheet of paper; returns with the context transformed to its top-left corner (call ctx.restore())."""
    ctx.save()
    ctx.translate(x + w / 2, y + h / 2)
    ctx.rotate(angle)
    ctx.translate(-w / 2, -h / 2)
    if shadow:
        ctx.rectangle(10, 14, w, h)
        ctx.set_source_rgba(0, 0, 0, 0.45)
        ctx.fill()
    ctx.rectangle(0, 0, w, h)
    ctx.save()
    ctx.clip()
    ctx.set_source_surface(_tex(int(w) + 2, int(h) + 2, seed, tone, (0.55, 0.45, 0.3)), 0, 0)
    ctx.paint()
    ctx.restore()
    return ctx


def typed(ctx, lines, x, y, size=30, color=INK, progress=1.0, font="courier_r", line_h=1.5, seed=0):
    """Typewritten lines, revealed character by character."""
    total = sum(len(l) for l in lines)
    shown = int(total * clamp(progress))
    for i, l in enumerate(lines):
        if shown <= 0:
            break
        part = l[:shown]
        shown -= len(l)
        a = 0.82 + 0.18 * hash01(seed, i)
        draw_text(ctx, part, x, y + i * size * line_h, font, size, color, "lb", a)


def stamp(ctx, text, x, y, size, angle=-0.12, alpha=1.0, color=RED, box=True):
    if alpha <= 0:
        return
    sc = 1 + (1 - clamp(alpha)) * 0.5
    w = text_width(text, "stencil", size, 0.1) + size * 0.9
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.scale(sc, sc)
    if box:
        ctx.rectangle(-w / 2, -size * 0.85, w, size * 1.5)
        ctx.set_line_width(size * 0.08)
        set_rgba(ctx, color, 0.85 * clamp(alpha))
        ctx.stroke()
    draw_text(ctx, text, 0, size * 0.32, "stencil", size, color, "cb", 0.85 * clamp(alpha), 0.1)
    ctx.restore()


def folder(ctx, x, y, w, h, title, sub=None, angle=0.0, alpha=1.0):
    """Buff file folder with typed label and red 'MOST SECRET' stamp."""
    ctx.save()
    ctx.translate(x + w / 2, y + h / 2)
    ctx.rotate(angle)
    ctx.translate(-w / 2, -h / 2)
    ctx.rectangle(14, 18, w, h)
    ctx.set_source_rgba(0, 0, 0, 0.5 * alpha)
    ctx.fill()
    poly(ctx, [(0, 30), (w * 0.3, 30), (w * 0.34, 0), (w * 0.62, 0), (w * 0.66, 30), (w, 30), (w, h), (0, h)])
    ctx.save()
    ctx.clip()
    ctx.set_source_surface(_tex(int(w) + 2, int(h) + 2, 7, MANILA, (0.45, 0.33, 0.18)), 0, 0)
    ctx.paint_with_alpha(alpha)
    ctx.restore()
    ctx.rectangle(w * 0.2, h * 0.3, w * 0.6, h * 0.28)
    set_rgba(ctx, (0.95, 0.94, 0.9), alpha)
    ctx.fill()
    draw_text(ctx, title, w / 2, h * 0.3 + h * 0.18, "courier", h * 0.08, INK, "cb", alpha, 0.05)
    if sub:
        draw_text(ctx, sub, w / 2, h * 0.3 + h * 0.25, "courier_r", h * 0.04, INK, "cb", alpha)
    ctx.restore()


def paperclip(ctx, x, y, s=1.0, angle=0.3):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.scale(s, s)
    ctx.set_line_width(4)
    ctx.move_to(0, 70)
    ctx.line_to(0, 10)
    ctx.arc(12, 10, 12, math.pi, 0)
    ctx.line_to(24, 80)
    ctx.arc(12, 80, 12, 0, math.pi)
    ctx.line_to(0, 25)
    ctx.set_source_rgba(0.7, 0.72, 0.75, 0.95)
    ctx.stroke()
    ctx.restore()


def portrait_photo(ctx, x, y, w, h, angle=0.0, sitter="woman", caption=None, alpha=1.0):
    """A small studio photograph (stylised; not a likeness of any real person)."""
    ctx.save()
    ctx.translate(x + w / 2, y + h / 2)
    ctx.rotate(angle)
    ctx.translate(-w / 2, -h / 2)
    ctx.rectangle(8, 12, w, h)
    ctx.set_source_rgba(0, 0, 0, 0.45 * alpha)
    ctx.fill()
    ctx.rectangle(0, 0, w, h)
    set_rgba(ctx, (0.96, 0.95, 0.92), alpha)
    ctx.fill()
    m = w * 0.07
    ctx.rectangle(m, m, w - 2 * m, h - 2 * m - (h * 0.1 if caption else 0))
    ctx.set_source(vgrad(ctx, 0, m, 0, h, [(0, (0.72, 0.72, 0.7)), (1, (0.35, 0.35, 0.34))]))
    ctx.fill()
    ih = h - 2 * m - (h * 0.1 if caption else 0)
    cx, cy = w / 2, m + ih * 0.42
    s = ih
    ctx.save()
    ctx.rectangle(m, m, w - 2 * m, ih)
    ctx.clip()
    col = (0.13, 0.12, 0.12)
    # shoulders
    ctx.move_to(cx - s * 0.45, m + ih)
    ctx.curve_to(cx - s * 0.4, cy + s * 0.25, cx - s * 0.2, cy + s * 0.2, cx, cy + s * 0.2)
    ctx.curve_to(cx + s * 0.2, cy + s * 0.2, cx + s * 0.4, cy + s * 0.25, cx + s * 0.45, m + ih)
    ctx.close_path()
    set_rgba(ctx, (0.25, 0.25, 0.26) if sitter == "woman" else (0.18, 0.18, 0.2), alpha)
    ctx.fill()
    # neck + face
    ctx.rectangle(cx - s * 0.05, cy + s * 0.05, s * 0.1, s * 0.18)
    set_rgba(ctx, (0.62, 0.6, 0.57), alpha)
    ctx.fill()
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(0.78, 1)
    ctx.arc(0, 0, s * 0.14, 0, 6.283)
    ctx.restore()
    ctx.fill()
    if sitter == "woman":   # 1940s rolled hairstyle
        ctx.save()
        ctx.translate(cx, cy - s * 0.04)
        ctx.scale(1.2, 1)
        ctx.arc(0, 0, s * 0.15, math.pi * 0.95, math.pi * 2.05)
        ctx.restore()
        set_rgba(ctx, col, alpha)
        ctx.fill()
        for side in (-1, 1):
            ctx.arc(cx + side * s * 0.15, cy + s * 0.05, s * 0.07, 0, 6.283)
            ctx.fill()
    else:                    # officer's cap
        ctx.rectangle(cx - s * 0.17, cy - s * 0.2, s * 0.34, s * 0.07)
        set_rgba(ctx, col, alpha)
        ctx.fill()
        ctx.save()
        ctx.translate(cx, cy - s * 0.18)
        ctx.scale(1, 0.35)
        ctx.arc(0, 0, s * 0.2, math.pi, 2 * math.pi)
        ctx.restore()
        ctx.fill()
    ctx.restore()
    if caption:
        draw_text(ctx, caption, w / 2, h - m * 0.6, "courier_r", h * 0.06, INK, "cb", alpha)
    ctx.restore()


def ticket(ctx, x, y, angle, top, mid, bottom, w=220, h=110, tone=(0.86, 0.72, 0.62)):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.rectangle(6, 8, w, h)
    ctx.set_source_rgba(0, 0, 0, 0.4)
    ctx.fill()
    # torn left edge
    pts = [(0, 0), (w, 0), (w, h), (0, h)]
    for k in range(12, 0, -1):
        pts.append((6 * (k % 2), h * k / 12))
    poly(ctx, pts)
    set_rgba(ctx, tone)
    ctx.fill()
    ctx.set_line_width(2)
    ctx.rectangle(12, 8, w - 20, h - 16)
    set_rgba(ctx, (0.4, 0.2, 0.15), 0.8)
    ctx.stroke()
    draw_text(ctx, top, w / 2 + 4, 34, "oldstd_b", 17, INK, "cb", 0.9)
    draw_text(ctx, mid, w / 2 + 4, 66, "oldstd_b", 26, INK, "cb", 0.95)
    draw_text(ctx, bottom, w / 2 + 4, 94, "courier_r", 16, INK, "cb", 0.9)
    ctx.restore()


def teleprinter_tape(ctx, text, x, y, progress, size=40, alpha=1.0):
    """Gummed teleprinter tape strip, as pasted onto signal forms."""
    shown = text[:int(len(text) * clamp(progress))]
    w = text_width(shown or " ", "courier", size, 0.15) + 40
    ctx.rectangle(x, y - size * 1.1, w, size * 1.5)
    set_rgba(ctx, (0.94, 0.9, 0.78), alpha)
    ctx.fill()
    draw_text(ctx, shown, x + 20, y, "courier", size, INK, "lb", alpha, 0.15)


def signal_form(ctx, x, y, w, h, header, lines, progress=1.0, angle=0.0):
    sheet(ctx, x, y, w, h, angle, (0.96, 0.93, 0.8), seed=5)
    draw_text(ctx, header, w / 2, 70, "oldstd_b", 34, INK, "cb", 0.9, 0.1)
    ctx.set_line_width(2)
    for i in range(5):
        ctx.move_to(40, 110 + i * 70)
        ctx.line_to(w - 40, 110 + i * 70)
    set_rgba(ctx, (0.4, 0.3, 0.3), 0.4)
    ctx.stroke()
    for i, l in enumerate(lines):
        p = clamp(progress * len(lines) - i)
        if p > 0:
            teleprinter_tape(ctx, l, 50, 170 + i * 70, p, 34)
    ctx.restore()
