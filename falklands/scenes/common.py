"""Helpers shared by scenes: camera, captions, teletext, documents."""
import functools
import math

import cairo
import numpy as np

from engine.core import (H, W, clamp, draw_text, ease_in_out, ease_out, fbm, hash01, hexc, lerp, mix,
                         noise_surface, poly, ramp, rgba_to_surface, set_rgba, text_width, typed, vgrad)
from engine import maps as M


def camera(ctx, S, z0=1.0, z1=1.08, p0=(0, 0), p1=(0, 0), ease=ease_in_out):
    """Slow push/pan across the shot (Ken Burns)."""
    k = ease(S.u)
    z = lerp(z0, z1, k)
    px, py = lerp(p0[0], p1[0], k), lerp(p0[1], p1[1], k)
    ctx.translate(W / 2 + px, H / 2 + py)
    ctx.scale(z, z)
    ctx.translate(-W / 2, -H / 2)


def shake(ctx, S, t0, amp=10, dur=0.8):
    a = S.t - t0
    if 0 <= a < dur:
        k = (1 - a / dur) ** 2 * amp
        ctx.translate((hash01(S.frame, 11) - 0.5) * 2 * k, (hash01(S.frame, 12) - 0.5) * 2 * k)


def lower_third(ctx, S, title, sub=None, t_in=0.6, t_out=None, accent=M.BRIT, y=858):
    """Early-80s TV name/place caption."""
    t_out = S.dur - 0.5 if t_out is None else t_out
    a = min(ramp(S.t, t_in, t_in + 0.45), 1 - ramp(S.t, t_out - 0.4, t_out))
    if a <= 0:
        return
    ctx.save()
    ctx.identity_matrix()
    x = 96 - (1 - ease_out(ramp(S.t, t_in, t_in + 0.6))) * 60
    tw = text_width(title, "oswald", 50, 0.05)
    sw = text_width(sub, "cond_r", 32, 0.03) if sub else 0
    w = max(tw, sw) + 70
    h = 78 if not sub else 128
    ctx.rectangle(x, y, w, h)
    ctx.set_source(vgrad(ctx, 0, y, 0, y + h, [(0, (0.05, 0.08, 0.18), 0.86 * a), (1, (0.02, 0.03, 0.08), 0.86 * a)]))
    ctx.fill()
    ctx.rectangle(x, y, 9, h)
    set_rgba(ctx, accent, a)
    ctx.fill()
    ctx.rectangle(x, y + h, w, 3)
    set_rgba(ctx, accent, a * 0.8)
    ctx.fill()
    draw_text(ctx, title, x + 34, y + 60, "oswald", 50, (1, 1, 1), "lb", a, 0.05)
    if sub:
        draw_text(ctx, sub, x + 34, y + 108, "cond_r", 32, (0.82, 0.86, 0.95), "lb", a, 0.03)
    ctx.restore()


def date_stamp(ctx, S, text, t_in=0.3, t_out=None, x=W - 96, y=110):
    t_out = S.dur - 0.4 if t_out is None else t_out
    a = min(ramp(S.t, t_in, t_in + 0.4), 1 - ramp(S.t, t_out - 0.4, t_out))
    if a <= 0:
        return
    ctx.save()
    ctx.identity_matrix()
    draw_text(ctx, text, x, y, "vt", 64, (1.0, 0.86, 0.35), "rb", a, 0.08, shadow=(3, 3, 0.8))
    ctx.restore()


def title_text(ctx, text, x, y, size, alpha, font="stencil", color=(1, 1, 1), anchor="cb", tracking=0.08):
    draw_text(ctx, text, x, y, font, size, color, anchor, alpha, tracking, shadow=(4, 5, 0.6))


# ------------------------------------------------------------------ teletext
TT = {
    "black": (0, 0, 0), "red": (1, 0.1, 0.1), "green": (0.1, 1, 0.1), "yellow": (1, 1, 0.1),
    "blue": (0.15, 0.2, 1), "magenta": (1, 0.1, 1), "cyan": (0.1, 1, 1), "white": (1, 1, 1),
}
TT_X0, TT_Y0 = 240, 22
CW, CH = 36, 41.4


def _tt_cell(ctx, col, row, text, fg, bg=None, double=False, alpha=1.0):
    x = TT_X0 + col * CW
    y = TT_Y0 + row * CH
    hmul = 2 if double else 1
    if bg:
        ctx.rectangle(x, y, CW * len(text), CH * hmul)
        set_rgba(ctx, TT[bg], alpha)
        ctx.fill()
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1.42, hmul)
    for i, ch in enumerate(text):
        if ch != " ":
            draw_text(ctx, ch, (i * CW + CW / 2) / 1.42, CH * 0.82, "vt", 50, TT[fg], "cb", alpha)
    ctx.restore()


def teletext(ctx, S, page, header_date, lines, reveal=(0.2, 2.0), mosaic=None, clock0=18 * 3600 + 2 * 60 + 41):
    """A 40x25 teletext page. lines: (row, col, text, fg, bg, double)."""
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()
    clock = int(clock0 + S.t)
    hh, mm, ss = clock // 3600 % 24, clock // 60 % 60, clock % 60
    _tt_cell(ctx, 0, 0, f" P{page}  TELETEXT {page} {header_date}", "white")
    _tt_cell(ctx, 32, 0, f"{hh:02d}:{mm:02d}/{ss:02d}", "yellow")
    n = len(lines)
    for i, (row, col, text, fg, bg, dbl) in enumerate(lines):
        start = lerp(reveal[0], reveal[1], i / max(1, n - 1))
        if S.t < start:
            continue
        _tt_cell(ctx, col, row, text, fg, bg, dbl)
    if mosaic is not None:
        mosaic(ctx, S)


@functools.lru_cache(maxsize=4)
def _island_mask(cols, rows, lon, lat, zoom):
    s = cairo.ImageSurface(cairo.FORMAT_A8, cols * 2, rows * 3)
    c = cairo.Context(s)
    m = M.FlatMap(lon, lat, zoom, cols, rows * 1.5)
    m.land_path(c, ("falklands",))
    c.fill()
    s.flush()
    a = np.ndarray((rows * 3, s.get_stride()), dtype=np.uint8, buffer=s.get_data())[:, :cols * 2]
    return a > 90


def tt_mosaic_islands(col0, row0, cols, rows, color="green", alpha=1.0):
    """Teletext 'sextant' block graphic of the islands."""
    mask = _island_mask(cols, rows, -59.5, -51.72, cols * 2 / (3.9 * 0.62))

    def draw(ctx, S):
        bw, bh = CW / 2, CH / 3
        for r in range(rows * 3):
            for c in range(cols * 2):
                if mask[r, c]:
                    ctx.rectangle(TT_X0 + col0 * CW + c * bw, TT_Y0 + row0 * CH + r * bh, bw + 0.5, bh + 0.5)
        set_rgba(ctx, TT[color], alpha)
        ctx.fill()
    return draw


# ------------------------------------------------------------------ paper / documents
@functools.lru_cache(maxsize=4)
def paper_surface(seed=3, tone=(0.93, 0.89, 0.78), stain=(0.6, 0.45, 0.25)):
    n = fbm(W, H, seed, 6, 5)
    n2 = fbm(W, H, seed + 1, 3, 3)
    arr = np.zeros((H, W, 4), dtype=np.uint8)
    base = np.array(tone, dtype=np.float32)
    st = np.array(stain, dtype=np.float32)
    k = (np.clip(n2 - 0.55, 0, 1) * 1.2 + (n - 0.5) * 0.12)[:, :, None]
    col = base * (1 - k) + st * k
    arr[:, :, :3] = (np.clip(col, 0, 1) * 255).astype(np.uint8)
    arr[:, :, 3] = 255
    return rgba_to_surface(arr)


def paper(ctx, seed=3, tone=(0.93, 0.89, 0.78), stain=(0.6, 0.45, 0.25)):
    ctx.set_source_surface(paper_surface(seed, tone, stain), 0, 0)
    ctx.paint()


def typewriter(ctx, text, x, y, size, progress, color=(0.12, 0.1, 0.1), line_h=1.45, max_chars=60, seed=0,
               font="type"):
    """Typed paragraph; returns y after last line. progress 0..1 across all chars."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    total = sum(len(l) for l in lines)
    shown = int(total * clamp(progress))
    yy = y
    for l in lines:
        if shown <= 0:
            break
        part = l[:shown]
        shown -= len(l)
        ink = 0.75 + 0.25 * hash01(seed, len(part))
        draw_text(ctx, part, x, yy, font, size, color, "lb", ink)
        yy += size * line_h
    return yy


def stamp(ctx, text, x, y, size, angle, alpha, color=(0.75, 0.1, 0.1)):
    if alpha <= 0:
        return
    w = text_width(text, "stencil", size, 0.08) + size
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    sc = 1 + (1 - clamp(alpha)) * 0.4
    ctx.scale(sc, sc)
    ctx.rectangle(-w / 2, -size * 0.85, w, size * 1.5)
    ctx.set_line_width(size * 0.09)
    set_rgba(ctx, color, alpha * 0.85)
    ctx.stroke()
    draw_text(ctx, text, 0, size * 0.3, "stencil", size, color, "cb", alpha * 0.85, 0.08)
    ctx.restore()


# ------------------------------------------------------------------ sailing ship (engraving)
def brig(ctx, x, y, s, ink=(0.25, 0.17, 0.1), alpha=1.0, t=0.0, hatch=True):
    """Two-masted brig-sloop in 18th/19th-century engraving style."""
    ctx.save()
    ctx.translate(x, y + math.sin(t * 1.2) * s * 0.01)
    ctx.rotate(math.sin(t * 0.9) * 0.02)
    ctx.scale(s, s)
    ctx.set_line_width(0.006)
    # hull
    ctx.move_to(-0.5, -0.08)
    ctx.curve_to(-0.45, 0.02, -0.3, 0.06, 0.0, 0.06)
    ctx.curve_to(0.3, 0.06, 0.48, 0.02, 0.56, -0.1)
    ctx.line_to(0.4, -0.06)
    ctx.line_to(-0.46, -0.07)
    ctx.close_path()
    set_rgba(ctx, ink, alpha)
    ctx.fill()
    # bowsprit
    ctx.move_to(0.45, -0.08)
    ctx.line_to(0.8, -0.2)
    ctx.stroke()
    for mx, mh in ((-0.12, 0.85), (0.22, 0.78)):
        ctx.move_to(mx, -0.07)
        ctx.line_to(mx, -mh)
        set_rgba(ctx, ink, alpha)
        ctx.stroke()
        # three square sails
        for k, (sy, sh, sw) in enumerate(((-0.2, 0.2, 0.3), (-0.42, 0.17, 0.25), (-0.6, 0.13, 0.19))):
            top = sy - sh
            ctx.move_to(mx - sw / 2, top)
            ctx.line_to(mx + sw / 2, top)
            ctx.curve_to(mx + sw / 2 + 0.03, top + sh * 0.5, mx + sw / 2 + 0.02, sy, mx + sw / 2, sy)
            ctx.line_to(mx - sw / 2, sy)
            ctx.curve_to(mx - sw / 2 + 0.02, sy - sh * 0.5, mx - sw / 2 + 0.03, top + sh * 0.5, mx - sw / 2, top)
            ctx.close_path()
            ctx.set_source_rgba(0.96, 0.92, 0.82, alpha)
            ctx.fill_preserve()
            set_rgba(ctx, ink, alpha)
            ctx.stroke()
            if hatch:
                ctx.save()
                ctx.move_to(mx - sw / 2, top)
                ctx.line_to(mx + sw / 2, top)
                ctx.line_to(mx + sw / 2, sy)
                ctx.line_to(mx - sw / 2, sy)
                ctx.close_path()
                ctx.clip()
                ctx.set_line_width(0.003)
                i = mx - sw / 2
                while i < mx + sw / 2:
                    if i > mx + sw * 0.1:
                        ctx.move_to(i, top)
                        ctx.line_to(i + 0.02, sy)
                    i += 0.012
                set_rgba(ctx, ink, alpha * 0.7)
                ctx.stroke()
                ctx.restore()
                ctx.set_line_width(0.006)
    # jibs
    poly(ctx, [(0.24, -0.72), (0.78, -0.21), (0.3, -0.12)])
    ctx.set_source_rgba(0.96, 0.92, 0.82, alpha)
    ctx.fill_preserve()
    set_rgba(ctx, ink, alpha)
    ctx.stroke()
    # ensign
    ctx.move_to(-0.46, -0.07)
    ctx.line_to(-0.52, -0.25)
    ctx.stroke()
    poly(ctx, [(-0.52, -0.25), (-0.66, -0.23 + math.sin(t * 4) * 0.01), (-0.64, -0.17), (-0.51, -0.19)])
    set_rgba(ctx, ink, alpha)
    ctx.fill()
    ctx.restore()
