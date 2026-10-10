"""Flat cartoon caricatures for THE PROMOTERS (parody).

character() draws a figure from the waist up with origin at the base of the
neck and unit s = head height. mouth 0..1 drives lip-sync, blink 0..1 closes
the eyes, look -1..1 moves the pupils (0 = straight down the lens).
"""
import math

from engine.core import hash01, mix, poly, set_rgba

INK = (0.1, 0.09, 0.09)

LOOKS = {
    "DANA": dict(skin=(0.93, 0.74, 0.64), suit=(0.09, 0.09, 0.1), shirt=(0.16, 0.16, 0.17), head_w=0.88,
                 shoulders=1.35, hair=None, stubble=True, brow=0.16, teeth=False),
    "EDDIE": dict(skin=(0.86, 0.62, 0.46), suit=(0.14, 0.2, 0.4), shirt=(0.96, 0.96, 0.97), head_w=0.76,
                  shoulders=1.15, hair=(0.24, 0.16, 0.1), stubble=False, brow=-0.05, teeth=True),
    "GARY": dict(skin=(0.95, 0.8, 0.7), suit=(0.62, 0.55, 0.4), shirt=(0.85, 0.87, 0.9), head_w=0.8,
                 shoulders=1.05, hair=(0.55, 0.5, 0.45), stubble=False, brow=0.0, teeth=False, glasses=True),
}


def _ellipse(ctx, x, y, rx, ry):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(rx, ry)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def _arm(ctx, pts, s, color, hand_color):
    ctx.set_line_width(0.26 * s)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    set_rgba(ctx, color)
    ctx.stroke()
    _ellipse(ctx, pts[-1][0], pts[-1][1], 0.11 * s, 0.11 * s)
    set_rgba(ctx, hand_color)
    ctx.fill()


def character(ctx, who, x, y, s, mouth=0.0, blink=0.0, look=0.0, pose="rest", t=0.0, talk=0.0, prop=None):
    L = LOOKS[who]
    skin, suit, shirt = L["skin"], L["suit"], L["shirt"]
    sw = L["shoulders"] * s
    ctx.save()
    ctx.translate(x, y)
    # gentle idle sway; a bit more when talking
    ctx.rotate(math.sin(t * 1.3 + hash01(len(who))) * 0.012 + talk * math.sin(t * 7) * 0.012)
    # ---- torso
    ctx.move_to(-sw, 2.4 * s)
    ctx.curve_to(-sw, 0.5 * s, -sw * 0.92, 0.15 * s, -0.35 * s, 0.05 * s)
    ctx.line_to(0.35 * s, 0.05 * s)
    ctx.curve_to(sw * 0.92, 0.15 * s, sw, 0.5 * s, sw, 2.4 * s)
    ctx.close_path()
    set_rgba(ctx, suit)
    ctx.fill()
    # shirt V and lapels
    poly(ctx, [(-0.3 * s, 0.05 * s), (0.3 * s, 0.05 * s), (0.0, 0.95 * s)])
    set_rgba(ctx, shirt)
    ctx.fill()
    for side in (-1, 1):
        poly(ctx, [(side * 0.3 * s, 0.05 * s), (side * 0.55 * s, 0.25 * s), (side * 0.18 * s, 1.1 * s),
                   (0.0, 0.95 * s)])
        set_rgba(ctx, mix(suit, (0, 0, 0), 0.25))
        ctx.fill()
    if who == "GARY":   # cardigan buttons
        for k in range(4):
            _ellipse(ctx, 0.0, 1.15 * s + k * 0.3 * s, 0.035 * s, 0.035 * s)
            set_rgba(ctx, (0.3, 0.25, 0.2))
            ctx.fill()
    # ---- neck
    nw = 0.3 * s if who == "DANA" else 0.2 * s
    ctx.rectangle(-nw, -0.25 * s, 2 * nw, 0.35 * s)
    set_rgba(ctx, mix(skin, (0, 0, 0), 0.12))
    ctx.fill()
    # ---- arms (behind/around body)
    hand = mix(skin, (0, 0, 0), 0.05)
    sl = (-sw * 0.85, 0.45 * s)
    sr = (sw * 0.85, 0.45 * s)
    wave = math.sin(t * 6) * 0.12 * s * talk
    if pose == "gesture":
        _arm(ctx, [sr, (sw * 0.95, 1.4 * s), (0.45 * s, 1.05 * s + wave)], s, suit, hand)
    elif pose == "phone":
        _arm(ctx, [sr, (sw * 1.25, 0.9 * s), (sw * 1.35, -0.35 * s)], s, suit, hand)
        ctx.save()
        ctx.translate(sw * 1.35, -0.55 * s)
        ctx.rotate(-0.1)
        ctx.rectangle(-0.17 * s, -0.3 * s, 0.34 * s, 0.6 * s)
        set_rgba(ctx, (0.08, 0.08, 0.1))
        ctx.fill()
        ctx.restore()
    elif pose == "hand_up":
        up = min(1.0, max(0.0, prop if isinstance(prop, float) else 1.0))
        hx = sw * 1.05
        hy = 1.3 * s - up * 2.6 * s
        _arm(ctx, [sr, (sw * 1.1, 0.4 * s - up * 0.8 * s), (hx, hy)], s, suit, hand)
    elif pose == "marker":
        _arm(ctx, [sr, (sw * 1.2, 0.6 * s), (sw * 1.6, -0.2 * s)], s, suit, hand)
    elif pose == "binder":
        _arm(ctx, [sl, (-sw * 0.9, 1.4 * s), (-0.55 * s, 1.0 * s)], s, suit, hand)
        _arm(ctx, [sr, (sw * 0.9, 1.4 * s), (0.55 * s, 1.0 * s)], s, suit, hand)
    elif pose == "mug":
        _arm(ctx, [sr, (sw * 0.95, 1.45 * s), (0.4 * s, 1.15 * s)], s, suit, hand)
        ctx.rectangle(0.28 * s, 0.8 * s, 0.3 * s, 0.34 * s)
        set_rgba(ctx, (0.92, 0.92, 0.9))
        ctx.fill()
    # ---- head
    hw, hh = L["head_w"] * s / 2, s / 2
    hx, hy = 0.0, -0.75 * s
    for side in (-1, 1):   # ears
        _ellipse(ctx, side * hw * 0.98, hy + 0.05 * s, 0.09 * s, 0.14 * s)
        set_rgba(ctx, mix(skin, (0, 0, 0), 0.08))
        ctx.fill()
    if who == "DANA":   # broad jaw, domed shaved head
        ctx.move_to(hx - hw, hy - 0.1 * s)
        ctx.curve_to(hx - hw, hy - hh * 1.25, hx + hw, hy - hh * 1.25, hx + hw, hy - 0.1 * s)
        ctx.curve_to(hx + hw * 1.05, hy + hh * 0.6, hx + hw * 0.6, hy + hh, hx, hy + hh)
        ctx.curve_to(hx - hw * 0.6, hy + hh, hx - hw * 1.05, hy + hh * 0.6, hx - hw, hy - 0.1 * s)
        ctx.close_path()
    else:
        _ellipse(ctx, hx, hy, hw, hh)
    set_rgba(ctx, skin)
    ctx.fill()
    if who == "DANA":   # scalp shine and stubble
        _ellipse(ctx, hx - hw * 0.3, hy - hh * 0.75, hw * 0.28, hh * 0.1)
        ctx.set_source_rgba(1, 1, 1, 0.35)
        ctx.fill()
        ctx.move_to(hx - hw * 0.95, hy + 0.05 * s)
        ctx.curve_to(hx - hw, hy + hh * 0.7, hx - hw * 0.5, hy + hh, hx, hy + hh)
        ctx.curve_to(hx + hw * 0.5, hy + hh, hx + hw, hy + hh * 0.7, hx + hw * 0.95, hy + 0.05 * s)
        ctx.curve_to(hx + hw * 0.4, hy + hh * 0.35, hx - hw * 0.4, hy + hh * 0.35, hx - hw * 0.95, hy + 0.05 * s)
        ctx.close_path()
        ctx.set_source_rgba(0.35, 0.3, 0.3, 0.28)
        ctx.fill()
    if L["hair"] and who == "EDDIE":   # swept-back volume
        ctx.move_to(hx - hw * 1.02, hy - 0.05 * s)
        ctx.curve_to(hx - hw * 1.15, hy - hh * 1.5, hx + hw * 0.6, hy - hh * 1.65, hx + hw * 1.05, hy - hh * 0.55)
        ctx.curve_to(hx + hw * 0.8, hy - hh * 0.75, hx - hw * 0.2, hy - hh * 0.85, hx - hw * 0.85, hy - hh * 0.2)
        ctx.close_path()
        set_rgba(ctx, L["hair"])
        ctx.fill()
    if who == "GARY":   # thinning top, tufts at the sides
        for side in (-1, 1):
            _ellipse(ctx, side * hw * 0.85, hy - hh * 0.25, hw * 0.25, hh * 0.3)
            set_rgba(ctx, L["hair"])
            ctx.fill()
    # ---- face
    ey = hy - hh * 0.1
    ex = hw * 0.38
    for side in (-1, 1):
        cx = hx + side * ex
        open_ = max(0.08, 1 - blink)
        _ellipse(ctx, cx, ey, 0.085 * s, 0.07 * s * open_)
        set_rgba(ctx, (0.98, 0.98, 0.96))
        ctx.fill()
        if open_ > 0.3:
            _ellipse(ctx, cx + look * 0.04 * s, ey, 0.04 * s, 0.045 * s * open_)
            set_rgba(ctx, INK)
            ctx.fill()
        # eyebrows: Dana furrowed, Eddie raised
        ctx.set_line_width(0.045 * s)
        tilt = L["brow"] * side
        ctx.move_to(cx - 0.1 * s, ey - 0.13 * s - tilt * 0.3 * s * -side)
        ctx.line_to(cx + 0.1 * s, ey - 0.13 * s + tilt * 0.3 * s * -side)
        set_rgba(ctx, (0.25, 0.2, 0.18) if who != "DANA" else (0.45, 0.35, 0.3))
        ctx.stroke()
    if L.get("glasses"):
        ctx.set_line_width(0.025 * s)
        for side in (-1, 1):
            ctx.rectangle(hx + side * ex - 0.13 * s, ey - 0.09 * s, 0.26 * s, 0.18 * s)
        ctx.move_to(hx - ex + 0.13 * s, ey)
        ctx.line_to(hx + ex - 0.13 * s, ey)
        set_rgba(ctx, INK)
        ctx.stroke()
    # nose
    ctx.set_line_width(0.03 * s)
    ctx.move_to(hx + 0.02 * s, ey + 0.05 * s)
    ctx.line_to(hx - 0.05 * s, ey + 0.22 * s)
    ctx.line_to(hx + 0.04 * s, ey + 0.24 * s)
    set_rgba(ctx, mix(skin, (0, 0, 0), 0.35))
    ctx.stroke()
    # mouth
    my = hy + hh * 0.55
    mw = 0.17 * s if who != "EDDIE" else 0.21 * s
    o = 0.015 * s + 0.12 * s * mouth
    if who == "EDDIE":   # the grin: wide, teeth on show
        ctx.move_to(hx - mw, my - 0.02 * s)
        ctx.curve_to(hx - mw * 0.5, my + o * 1.2 + 0.03 * s, hx + mw * 0.5, my + o * 1.2 + 0.03 * s, hx + mw,
                     my - 0.02 * s)
        ctx.close_path()
        set_rgba(ctx, (0.35, 0.1, 0.1))
        ctx.fill_preserve()
        ctx.save()
        ctx.clip()
        ctx.rectangle(hx - mw, my - 0.03 * s, 2 * mw, 0.06 * s)
        set_rgba(ctx, (1, 1, 1))
        ctx.fill()
        ctx.restore()
    else:
        _ellipse(ctx, hx, my, mw * (1 - 0.3 * mouth), max(0.012 * s, o / 2))
        set_rgba(ctx, (0.3, 0.08, 0.08))
        ctx.fill()
    ctx.restore()


def blink_at(t, seed):
    """Blink for ~0.12 s every 2.5-5 s."""
    period = 2.5 + 2.5 * hash01(seed, 1)
    ph = (t + hash01(seed, 2) * period) % period
    return 1.0 if ph < 0.12 else 0.0
