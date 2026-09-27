"""Intertitles, posters and quotation cards in the manner of 1916."""
import math

import cairo

from engine.core import H, W, clamp, draw_text, lerp, mix, ramp, set_rgba, text_width, vgrad

CARD_BG = (0.06, 0.055, 0.05)
CARD_INK = (0.95, 0.93, 0.88)


def _flourish(ctx, x, y, s, flip_x=1, flip_y=1):
    """Small art-nouveau corner ornament."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(flip_x * s, flip_y * s)
    ctx.set_line_width(2.2 / s)
    ctx.move_to(0, 40)
    ctx.curve_to(0, 10, 10, 0, 40, 0)
    ctx.move_to(12, 40)
    ctx.curve_to(12, 22, 22, 12, 40, 12)
    ctx.move_to(0, 0)
    ctx.curve_to(18, 6, 26, 18, 22, 30)
    ctx.curve_to(18, 38, 8, 34, 10, 26)
    ctx.stroke()
    ctx.arc(22, 22, 3.5, 0, 6.283)
    ctx.fill()
    ctx.restore()


def frame_border(ctx, x0, y0, x1, y1, color=CARD_INK, alpha=1.0):
    set_rgba(ctx, color, alpha)
    ctx.set_line_width(3)
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.stroke()
    ctx.set_line_width(1.2)
    ctx.rectangle(x0 + 12, y0 + 12, x1 - x0 - 24, y1 - y0 - 24)
    ctx.stroke()
    for (cx, cy, fx, fy) in ((x0 + 22, y0 + 22, 1, 1), (x1 - 22, y0 + 22, -1, 1), (x0 + 22, y1 - 22, 1, -1),
                             (x1 - 22, y1 - 22, -1, -1)):
        _flourish(ctx, cx, cy, 1.4, fx, fy)
    # centre ornaments top and bottom
    for cy, d in ((y0, 1), (y1, -1)):
        ctx.move_to(W / 2 - 60, cy + d * 12)
        ctx.curve_to(W / 2 - 20, cy + d * 12, W / 2 - 14, cy + d * 30, W / 2, cy + d * 30)
        ctx.curve_to(W / 2 + 14, cy + d * 30, W / 2 + 20, cy + d * 12, W / 2 + 60, cy + d * 12)
        ctx.set_line_width(2)
        ctx.stroke()


def intertitle(ctx, S, lines, sizes=None, fonts=None, t_in=0.15, spacing=1.35, y_center=H / 2, fade_out=True):
    """Silent-film title card. lines: list of strings (None = spacer rule)."""
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(vgrad(ctx, 0, 0, 0, H, [(0, (0.09, 0.085, 0.075)), (0.5, CARD_BG), (1, (0.08, 0.075, 0.07))]))
    ctx.fill()
    a = ramp(S.t, t_in, t_in + 0.5)
    if fade_out:
        a = min(a, 1 - ramp(S.t, S.dur - 0.4, S.dur))
    frame_border(ctx, 150, 90, W - 150, H - 90, CARD_INK, 0.85 * a)
    sizes = sizes or [70] * len(lines)
    fonts = fonts or ["fell"] * len(lines)
    total = sum((s * spacing if l is not None else 40) for l, s in zip(lines, sizes))
    y = y_center - total / 2
    for l, s, f in zip(lines, sizes, fonts):
        if l is None:
            ctx.move_to(W / 2 - 120, y + 20)
            ctx.line_to(W / 2 + 120, y + 20)
            ctx.set_line_width(2)
            set_rgba(ctx, CARD_INK, 0.8 * a)
            ctx.stroke()
            y += 40
            continue
        y += s * spacing
        draw_text(ctx, l, W / 2, y - s * 0.35, f, s, CARD_INK, "cb", a, 0.02)


def quote_card(ctx, S, quote_lines, attribution, t_in=0.2):
    intertitle(ctx, S, [], t_in=t_in)
    a = ramp(S.t, t_in, t_in + 0.6)
    y = H / 2 - len(quote_lines) * 45
    draw_text(ctx, "“", 330, y + 40, "fell", 160, CARD_INK, "lb", a * 0.6)
    for i, l in enumerate(quote_lines):
        draw_text(ctx, l, W / 2, y + i * 90, "fell_i", 66, CARD_INK, "cb", a)
    draw_text(ctx, attribution, W / 2, y + len(quote_lines) * 90 + 50, "fell_sc", 40, (0.8, 0.78, 0.72), "cb",
              ramp(S.t, t_in + 0.8, t_in + 1.4), 0.06)


def stat_card(ctx, S, rows, title=None, t0s=None):
    """Numbers on a black card (casualty figures)."""
    intertitle(ctx, S, [], fade_out=True)
    if title:
        draw_text(ctx, title, W / 2, 250, "fell_sc", 58, CARD_INK, "cb", ramp(S.t, 0.1, 0.6), 0.12)
    n = len(rows)
    for i, (num, label) in enumerate(rows):
        t0 = t0s[i] if t0s else 0.4 + i * 0.8
        a = ramp(S.t, t0, t0 + 0.4)
        x = W / 2 + (i - (n - 1) / 2) * 580
        draw_text(ctx, num, x, 610, "oldstd_b", 104, CARD_INK, "cb", a)
        for j, part in enumerate(label.split("\n")):
            draw_text(ctx, part, x, 690 + j * 52, "fell_sc", 44, (0.85, 0.83, 0.78), "cb", a, 0.05)


def plate(ctx, S, title, sub=None, t_in=0.5, t_out=None, x=90, y=860):
    """Caption plate over a scene, in the manner of a 1916 film sub-title."""
    t_out = S.dur - 0.4 if t_out is None else t_out
    a = min(ramp(S.t, t_in, t_in + 0.4), 1 - ramp(S.t, t_out - 0.4, t_out))
    if a <= 0:
        return
    ctx.save()
    ctx.identity_matrix()
    w = max(text_width(title, "fell_sc", 46, 0.06), text_width(sub or "", "fell_i", 34)) + 90
    h = 84 if not sub else 132
    ctx.rectangle(x, y, w, h)
    set_rgba(ctx, CARD_BG, 0.82 * a)
    ctx.fill()
    ctx.set_line_width(2)
    set_rgba(ctx, CARD_INK, 0.8 * a)
    ctx.rectangle(x + 8, y + 8, w - 16, h - 16)
    ctx.stroke()
    draw_text(ctx, title, x + w / 2, y + 60, "fell_sc", 46, CARD_INK, "cb", a, 0.06)
    if sub:
        draw_text(ctx, sub, x + w / 2, y + 106, "fell_i", 34, (0.85, 0.82, 0.76), "cb", a)
    ctx.restore()


def clock_text(ctx, S, text, t_in, t_out, x=W - 110, y=140):
    a = min(ramp(S.t, t_in, t_in + 0.3), 1 - ramp(S.t, t_out - 0.3, t_out))
    if a <= 0:
        return
    ctx.save()
    ctx.identity_matrix()
    draw_text(ctx, text, x, y, "fell", 84, CARD_INK, "rb", a, 0.02, shadow=(3, 3, 0.8))
    ctx.restore()
