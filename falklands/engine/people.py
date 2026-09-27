"""Figures, crowds, flags and buildings."""
import functools
import math

import cairo
import numpy as np

from .core import hash01, hexc, mix, poly, set_rgba

# ------------------------------------------------------------------ flags
UNION_BLUE = hexc("012169")
UNION_RED = hexc("C8102E")
ARG_BLUE = hexc("74ACDF")
ARG_SUN = hexc("F6B40E")


def _union(ctx, w, h):
    ctx.rectangle(0, 0, w, h)
    ctx.set_source_rgb(*UNION_BLUE)
    ctx.fill()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    for lw, col in ((h * 0.2, (1, 1, 1)), (h * 0.0667, UNION_RED)):
        ctx.set_line_width(lw)
        ctx.move_to(0, 0)
        ctx.line_to(w, h)
        ctx.move_to(w, 0)
        ctx.line_to(0, h)
        ctx.set_source_rgb(*col)
        ctx.stroke()
    for lw, col in ((h / 3, (1, 1, 1)), (h / 5, UNION_RED)):
        ctx.set_line_width(lw)
        ctx.move_to(w / 2, 0)
        ctx.line_to(w / 2, h)
        ctx.move_to(0, h / 2)
        ctx.line_to(w, h / 2)
        ctx.set_source_rgb(*col)
        ctx.stroke()


def _argentina(ctx, w, h):
    for i, c in enumerate((ARG_BLUE, (1, 1, 1), ARG_BLUE)):
        ctx.rectangle(0, i * h / 3, w, h / 3 + 1)
        ctx.set_source_rgb(*c)
        ctx.fill()
    cx, cy, r = w / 2, h / 2, h * 0.1
    ctx.set_line_width(h * 0.012)
    for k in range(32):
        a = k * math.pi / 16
        rr = r * (1.9 if k % 2 == 0 else 1.6)
        ctx.move_to(cx + math.cos(a) * r, cy + math.sin(a) * r)
        ctx.line_to(cx + math.cos(a) * rr, cy + math.sin(a) * rr)
    ctx.set_source_rgb(*ARG_SUN)
    ctx.stroke()
    ctx.arc(cx, cy, r, 0, 6.283)
    ctx.fill()


def _white_ensign(ctx, w, h):
    ctx.rectangle(0, 0, w, h)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    ctx.set_line_width(h * 0.16)
    ctx.move_to(w * 0.5 + w * 0.0, 0)
    ctx.move_to(0, h / 2)
    ctx.line_to(w, h / 2)
    ctx.move_to(w * 0.5, 0)
    ctx.line_to(w * 0.5, h)
    ctx.set_source_rgb(*UNION_RED)
    ctx.stroke()
    ctx.save()
    ctx.rectangle(0, 0, w / 2 - h * 0.08, h / 2 - h * 0.08)
    ctx.clip()
    ctx.scale(0.46, 0.42)
    _union(ctx, w, h)
    ctx.restore()


def _white(ctx, w, h):
    ctx.rectangle(0, 0, w, h)
    ctx.set_source_rgb(0.95, 0.94, 0.9)
    ctx.fill()


FLAG_FUNCS = {"union": _union, "argentina": _argentina, "ensign": _white_ensign, "white": _white}


@functools.lru_cache(maxsize=32)
def _flag_surface(kind, w, h):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    c = cairo.Context(s)
    FLAG_FUNCS[kind](c, w, h)
    return s


def flag(ctx, kind, x, y, w, h, t, amp=0.08, strips=None, alpha=1.0, speed=5.0, shade=0.28):
    """Waving flag, hoist edge at x, top at y."""
    w, h = int(w), int(h)
    surf = _flag_surface(kind, w, h)
    strips = strips or max(12, min(48, w // 4))
    sw = w / strips
    for i in range(strips):
        u = i / strips
        ph = t * speed - u * 7
        dy = math.sin(ph) * amp * h * u
        light = math.cos(ph)
        ctx.save()
        ctx.rectangle(x + i * sw - 0.5, y + dy, sw + 1, h)
        ctx.clip()
        ctx.set_source_surface(surf, x, y + dy)
        ctx.paint_with_alpha(alpha)
        if light < 0:
            ctx.set_source_rgba(0, 0, 0, -light * shade * alpha)
        else:
            ctx.set_source_rgba(1, 1, 1, light * shade * 0.35 * alpha)
        ctx.paint()
        ctx.restore()


def flagpole(ctx, kind, x, y_base, pole_h, fw, t, color=(0.15, 0.15, 0.15), raise_frac=1.0, amp=0.08,
             alpha=1.0):
    ctx.set_line_width(max(2, fw * 0.03))
    ctx.move_to(x, y_base)
    ctx.line_to(x, y_base - pole_h)
    set_rgba(ctx, color, alpha)
    ctx.stroke()
    fh = fw / 2
    top = y_base - pole_h + 4
    y = top + (1 - raise_frac) * (pole_h - fh - 10)
    flag(ctx, kind, x, y, fw, fh, t, amp=amp, alpha=alpha)


# ------------------------------------------------------------------ soldiers
def _limb(ctx, pts, w, col, alpha):
    ctx.set_line_width(w)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    set_rgba(ctx, col, alpha)
    ctx.stroke()


def soldier(ctx, x, y, h, phase, facing=1, color=(0.08, 0.09, 0.08), alpha=1.0, pack=True,
            beret=False, lean=16.0, rifle=True, stride=1.0):
    """Walking infantryman with bergen (the 'yomp'). y = ground level."""
    f = facing
    bob = -abs(math.sin(phase)) * 0.018 * h
    hip = (x, y - 0.5 * h + bob)
    la = math.radians(lean) * f
    sh = (hip[0] + math.sin(la) * 0.3 * h, hip[1] - math.cos(la) * 0.3 * h)
    head = (sh[0] + math.sin(la) * 0.1 * h, sh[1] - math.cos(la) * 0.1 * h)
    back_col = mix(color, (0, 0, 0), 0.35)

    def leg(ph, col):
        a = math.sin(ph) * math.radians(26) * stride
        knee_bend = max(0.0, math.sin(ph + 1.3)) * math.radians(40)
        knee = (hip[0] + math.sin(a) * f * 0.25 * h, hip[1] + math.cos(a) * 0.25 * h)
        a2 = a - knee_bend
        foot = (knee[0] + math.sin(a2) * f * 0.25 * h, knee[1] + math.cos(a2) * 0.25 * h)
        _limb(ctx, [hip, knee, foot], 0.075 * h, col, alpha)
        _limb(ctx, [foot, (foot[0] + f * 0.06 * h, foot[1])], 0.05 * h, col, alpha)

    def arm(ph, col):
        a = -math.sin(ph) * math.radians(22)
        elbow = (sh[0] + math.sin(a + la * f * 0.3) * f * 0.17 * h, sh[1] + math.cos(a) * 0.17 * h)
        hand = (elbow[0] + f * 0.1 * h, elbow[1] - 0.05 * h)
        _limb(ctx, [sh, elbow, hand], 0.06 * h, col, alpha)
        return hand

    leg(phase + math.pi, back_col)
    arm(phase, back_col)
    # torso
    ctx.set_line_width(0.13 * h)
    ctx.move_to(*hip)
    ctx.line_to(*sh)
    set_rgba(ctx, color, alpha)
    ctx.stroke()
    if pack:
        ctx.save()
        ctx.translate(sh[0] - f * 0.1 * h, sh[1] + 0.02 * h)
        ctx.rotate(la)
        rr = 0.04 * h
        w_, h_ = 0.17 * h, 0.34 * h
        x0, y0 = -w_ / 2, -0.1 * h
        ctx.new_sub_path()
        ctx.arc(x0 + w_ - rr, y0 + rr, rr, -math.pi / 2, 0)
        ctx.arc(x0 + w_ - rr, y0 + h_ - rr, rr, 0, math.pi / 2)
        ctx.arc(x0 + rr, y0 + h_ - rr, rr, math.pi / 2, math.pi)
        ctx.arc(x0 + rr, y0 + rr, rr, math.pi, 1.5 * math.pi)
        ctx.close_path()
        set_rgba(ctx, mix(color, (0, 0, 0), 0.15), alpha)
        ctx.fill()
        ctx.restore()
    leg(phase, color)
    hand = arm(phase + math.pi, color)
    if rifle:
        ctx.set_line_width(0.028 * h)
        ctx.move_to(hand[0] - f * 0.12 * h, hand[1] + 0.1 * h)
        ctx.line_to(hand[0] + f * 0.2 * h, hand[1] - 0.14 * h)
        set_rgba(ctx, color, alpha)
        ctx.stroke()
    ctx.arc(head[0], head[1], 0.062 * h, 0, 6.283)
    set_rgba(ctx, color, alpha)
    ctx.fill()
    if beret:
        ctx.save()
        ctx.translate(head[0] - f * 0.02 * h, head[1] - 0.045 * h)
        ctx.scale(0.09 * h, 0.035 * h)
        ctx.arc(0, 0, 1, 0, 6.283)
        ctx.restore()
    else:
        ctx.arc(head[0], head[1] - 0.01 * h, 0.08 * h, math.pi, 2 * math.pi)
        ctx.close_path()
    set_rgba(ctx, color, alpha)
    ctx.fill()


def standing_figure(ctx, x, y, h, color, alpha=1.0, arm_up=0.0, t=0.0, seed=0, scarf=None, placard=None,
                    coat=True, face=None):
    """Standing civilian in a coat; optional waving arm, white headscarf, placard."""
    w = h * (0.24 + 0.05 * hash01(seed, 1))
    head_r = h * 0.068
    top = y - h
    neck_y = top + h * 0.17
    sh_y = top + h * 0.2
    hx, hy = x + (hash01(seed, 2) - 0.5) * h * 0.02, neck_y - head_r * 0.95
    # coat: rounded shoulders, slight flare to the hem
    ctx.move_to(x - w * 0.18, neck_y)
    ctx.curve_to(x - w * 0.42, sh_y - h * 0.01, x - w * 0.5, sh_y + h * 0.02, x - w * 0.5, sh_y + h * 0.1)
    ctx.line_to(x - w * 0.46, y - h * 0.34)
    ctx.line_to(x - w * 0.52, y - h * 0.08)
    ctx.line_to(x - w * 0.2, y - h * 0.07)
    ctx.line_to(x - w * 0.2, y)
    ctx.line_to(x - w * 0.06, y)
    ctx.line_to(x - w * 0.04, y - h * 0.07)
    ctx.line_to(x + w * 0.04, y - h * 0.07)
    ctx.line_to(x + w * 0.06, y)
    ctx.line_to(x + w * 0.2, y)
    ctx.line_to(x + w * 0.2, y - h * 0.07)
    ctx.line_to(x + w * 0.52, y - h * 0.08)
    ctx.line_to(x + w * 0.46, y - h * 0.34)
    ctx.line_to(x + w * 0.5, sh_y + h * 0.1)
    ctx.curve_to(x + w * 0.5, sh_y + h * 0.02, x + w * 0.42, sh_y - h * 0.01, x + w * 0.18, neck_y)
    ctx.close_path()
    set_rgba(ctx, color, alpha)
    ctx.fill()
    ctx.rectangle(x - w * 0.09, neck_y - head_r * 0.4, w * 0.18, head_r * 0.6)
    ctx.fill()
    ctx.save()
    ctx.translate(hx, hy)
    ctx.scale(0.86, 1.0)
    ctx.arc(0, 0, head_r, 0, 6.283)
    ctx.restore()
    set_rgba(ctx, face or color, alpha)
    ctx.fill()
    if scarf:
        r = head_r
        ctx.move_to(hx - r * 1.02, hy + r * 0.25)
        ctx.curve_to(hx - r * 1.15, hy - r * 1.35, hx + r * 1.15, hy - r * 1.35, hx + r * 1.02, hy + r * 0.25)
        ctx.curve_to(hx + r * 0.95, hy + r * 0.9, hx + r * 0.5, hy + r * 1.35, hx + r * 0.1, hy + r * 1.45)
        ctx.line_to(hx - r * 0.1, hy + r * 1.45)
        ctx.curve_to(hx - r * 0.5, hy + r * 1.35, hx - r * 0.95, hy + r * 0.9, hx - r * 1.02, hy + r * 0.25)
        ctx.close_path()
        set_rgba(ctx, scarf, alpha)
        ctx.fill()
        # face opening
        ctx.save()
        ctx.translate(hx, hy + r * 0.25)
        ctx.scale(0.62, 0.8)
        ctx.arc(0, 0, r, 0, 6.283)
        ctx.restore()
        set_rgba(ctx, face or mix(color, (0.55, 0.45, 0.4), 0.5), alpha)
        ctx.fill()
    if arm_up > 0:
        sway = math.sin(t * 5 + seed) * 0.35 * arm_up
        sx, sy = x + w * 0.38, sh_y + h * 0.04
        ex, ey = sx + math.sin(0.5 + sway) * h * 0.14, sy - h * 0.16
        qx, qy = ex + math.sin(0.2 + sway) * h * 0.04, ey - h * 0.15
        ctx.set_line_width(h * 0.06)
        ctx.move_to(sx, sy)
        ctx.line_to(ex, ey)
        ctx.line_to(qx, qy)
        set_rgba(ctx, color, alpha)
        ctx.stroke()
        ctx.arc(qx, qy, h * 0.035, 0, 6.283)
        ctx.fill()
    if placard:
        pw, ph = h * 0.26, h * 0.3
        px, py = x - pw / 2, top + h * 0.3
        ctx.rectangle(px, py, pw, ph)
        set_rgba(ctx, placard, alpha)
        ctx.fill()
        ctx.rectangle(px + pw * 0.12, py + ph * 0.1, pw * 0.76, ph * 0.66)
        set_rgba(ctx, mix(placard, (0, 0, 0), 0.18), alpha)
        ctx.fill()
        # portrait of a disappeared person
        ctx.arc(x, py + ph * 0.36, pw * 0.13, 0, 6.283)
        ctx.move_to(x - pw * 0.28, py + ph * 0.76)
        ctx.curve_to(x - pw * 0.28, py + ph * 0.52, x + pw * 0.28, py + ph * 0.52, x + pw * 0.28, py + ph * 0.76)
        ctx.close_path()
        set_rgba(ctx, mix(placard, (0, 0, 0), 0.6), alpha)
        ctx.fill()
        ctx.rectangle(px + pw * 0.1, py + ph * 0.82, pw * 0.8, ph * 0.06)
        ctx.fill()
        # hands holding it
        for s in (-1, 1):
            ctx.arc(x + s * pw * 0.5, py + ph * 0.55, h * 0.025, 0, 6.283)
            set_rgba(ctx, color, alpha)
            ctx.fill()


def crowd(ctx, x0, x1, y, h, t, color, seed=0, density=1.0, wave=0.5, flags=None, flag_every=7,
          alpha=1.0, rows=3, row_gap=0.18, scarf=None, placards=False):
    r = np.random.default_rng(seed)
    for row in range(rows):
        rh = h * (1 - row * 0.12)
        yy = y - (rows - 1 - row) * h * row_gap
        col = mix(color, (0.0, 0.0, 0.0), 0.25 * (rows - 1 - row) / max(1, rows - 1))
        n = int((x1 - x0) / (rh * 0.2) * density)
        xs = sorted(x0 + r.random(n) * (x1 - x0))
        for i, x in enumerate(xs):
            hh = rh * (0.85 + 0.25 * r.random())
            up = wave if r.random() < 0.35 else 0
            standing_figure(ctx, x, yy + r.random() * 6, hh, col, alpha, arm_up=up, t=t, seed=seed * 100 + i,
                            scarf=scarf if (scarf and r.random() < 0.9) else None,
                            placard=(0.93, 0.92, 0.88) if (placards and r.random() < 0.4) else None)
            if flags and i % flag_every == 3:
                fx = x + hh * 0.1
                ctx.set_line_width(2.5)
                ctx.move_to(fx, yy - hh * 0.55)
                ctx.line_to(fx + 4, yy - hh * 1.35)
                set_rgba(ctx, (0.1, 0.1, 0.1), alpha)
                ctx.stroke()
                fw = hh * 0.55
                flag(ctx, flags, fx + 4, yy - hh * 1.35, fw, fw * 0.6, t + i * 0.37, amp=0.12, alpha=alpha)


# ------------------------------------------------------------------ buildings
def casa_rosada(ctx, x, y, w, h, color=hexc("D99A8E"), shadow=hexc("9E6358"), win=(0.2, 0.15, 0.15),
                alpha=1.0, lit=0.0):
    """Stylised Casa Rosada facade (Buenos Aires), base at y."""
    top = y - h
    ctx.rectangle(x, top, w, h)
    set_rgba(ctx, color, alpha)
    ctx.fill()
    # central arch block
    cw = w * 0.16
    cx = x + w / 2 - cw / 2
    ctx.rectangle(cx, top - h * 0.18, cw, h * 1.18)
    set_rgba(ctx, mix(color, (1, 1, 1), 0.08), alpha)
    ctx.fill()
    # pediment
    poly(ctx, [(cx - 6, top - h * 0.18), (cx + cw / 2, top - h * 0.34), (cx + cw + 6, top - h * 0.18)])
    set_rgba(ctx, color, alpha)
    ctx.fill()
    # grand arch
    aw = cw * 0.5
    ax = cx + cw / 2
    ctx.move_to(ax - aw / 2, y)
    ctx.line_to(ax - aw / 2, y - h * 0.35)
    ctx.arc(ax, y - h * 0.35, aw / 2, math.pi, 0)
    ctx.line_to(ax + aw / 2, y)
    ctx.close_path()
    set_rgba(ctx, shadow, alpha)
    ctx.fill()
    # cornices
    for fy in (0.02, 0.36, 0.68):
        ctx.rectangle(x, top + h * fy, w, h * 0.035)
        set_rgba(ctx, mix(color, (1, 1, 1), 0.25), alpha)
        ctx.fill()
    # balustrade
    ctx.rectangle(x, top - h * 0.07, w, h * 0.07)
    set_rgba(ctx, color, alpha)
    ctx.fill()
    for i in range(int(w / 14)):
        ctx.rectangle(x + i * 14 + 4, top - h * 0.06, 5, h * 0.05)
    set_rgba(ctx, shadow, alpha * 0.6)
    ctx.fill()
    # arched windows
    n = 14
    for floor, (fy, fh) in enumerate(((0.1, 0.2), (0.44, 0.18), (0.75, 0.18))):
        for i in range(n):
            wx = x + (i + 0.5) * w / n
            if abs(wx - (x + w / 2)) < cw * 0.6:
                continue
            ww = w / n * 0.4
            wy = top + h * fy
            ctx.move_to(wx - ww / 2, wy + h * fh)
            ctx.line_to(wx - ww / 2, wy + ww / 2)
            ctx.arc(wx, wy + ww / 2, ww / 2, math.pi, 0)
            ctx.line_to(wx + ww / 2, wy + h * fh)
            ctx.close_path()
            c = mix(win, (1.0, 0.8, 0.45), lit * (0.5 + 0.5 * hash01(i, floor)))
            set_rgba(ctx, c, alpha)
            ctx.fill()


def house(ctx, x, y, w, h, wall, roof, alpha=1.0, chimney=True, lit=0.0, seed=0):
    rh = h * 0.55
    ctx.rectangle(x, y - h, w, h)
    set_rgba(ctx, wall, alpha)
    ctx.fill()
    poly(ctx, [(x - w * 0.06, y - h), (x + w / 2, y - h - rh), (x + w * 1.06, y - h)])
    set_rgba(ctx, roof, alpha)
    ctx.fill()
    if chimney:
        ctx.rectangle(x + w * 0.7, y - h - rh * 0.8, w * 0.1, rh * 0.5)
        set_rgba(ctx, mix(wall, (0, 0, 0), 0.3), alpha)
        ctx.fill()
    nw = max(1, int(w / 30))
    for i in range(nw):
        wx = x + (i + 0.5) * w / nw - w * 0.06
        ctx.rectangle(wx, y - h * 0.7, w * 0.12, h * 0.3)
        c = mix((0.15, 0.17, 0.2), (1.0, 0.82, 0.5), lit * hash01(seed, i))
        set_rgba(ctx, c, alpha)
        ctx.fill()


def cathedral(ctx, x, y, s, alpha=1.0, brick=hexc("7E4A3A"), roof=hexc("3F5A45")):
    """Christ Church Cathedral, Stanley: brick nave + square tower."""
    nave_w, nave_h = s * 1.6, s * 0.55
    ctx.rectangle(x, y - nave_h, nave_w, nave_h)
    set_rgba(ctx, brick, alpha)
    ctx.fill()
    poly(ctx, [(x - 6, y - nave_h), (x + nave_w * 0.1, y - nave_h - s * 0.3), (x + nave_w * 0.9, y - nave_h - s * 0.3),
               (x + nave_w + 6, y - nave_h)])
    set_rgba(ctx, roof, alpha)
    ctx.fill()
    tx, tw, th = x + nave_w, s * 0.42, s * 1.25
    ctx.rectangle(tx, y - th, tw, th)
    set_rgba(ctx, mix(brick, (0, 0, 0), 0.08), alpha)
    ctx.fill()
    poly(ctx, [(tx - 4, y - th), (tx + tw / 2, y - th - s * 0.28), (tx + tw + 4, y - th)])
    set_rgba(ctx, roof, alpha)
    ctx.fill()
    for i in range(5):
        wx = x + nave_w * (0.12 + i * 0.17)
        ctx.move_to(wx, y - nave_h * 0.25)
        ctx.line_to(wx, y - nave_h * 0.65)
        ctx.arc(wx + s * 0.04, y - nave_h * 0.65, s * 0.04, math.pi, 0)
        ctx.line_to(wx + s * 0.08, y - nave_h * 0.25)
        ctx.close_path()
    set_rgba(ctx, (0.15, 0.13, 0.12), alpha)
    ctx.fill()
    # whalebone arch in front
    ax = x - s * 0.35
    ctx.set_line_width(s * 0.05)
    for side in (-1, 1):
        ctx.move_to(ax + side * s * 0.2, y)
        ctx.curve_to(ax + side * s * 0.22, y - s * 0.3, ax + side * s * 0.1, y - s * 0.55, ax, y - s * 0.62)
    ctx.set_source_rgba(0.93, 0.9, 0.82, alpha)
    ctx.stroke()


def round_tower(ctx, x, y, s, color=hexc("8B8578"), alpha=1.0):
    """Portsmouth's Round Tower at the harbour mouth."""
    ctx.rectangle(x, y - s * 0.7, s * 1.2, s * 0.7)
    set_rgba(ctx, color, alpha)
    ctx.fill()
    for i in range(7):
        ctx.rectangle(x + i * s * 0.18, y - s * 0.78, s * 0.1, s * 0.09)
    ctx.fill()
    g = cairo.LinearGradient(x, 0, x + s * 1.2, 0)
    g.add_color_stop_rgba(0, 0, 0, 0, 0.25 * alpha)
    g.add_color_stop_rgba(0.4, 1, 1, 1, 0.08 * alpha)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.35 * alpha)
    ctx.rectangle(x, y - s * 0.7, s * 1.2, s * 0.7)
    ctx.set_source(g)
    ctx.fill()


def cross(ctx, x, y, h, color=(0.95, 0.95, 0.92), alpha=1.0):
    w = h * 0.12
    ctx.rectangle(x - w / 2, y - h, w, h)
    ctx.rectangle(x - h * 0.3, y - h * 0.78, h * 0.6, w)
    set_rgba(ctx, color, alpha)
    ctx.fill()


def church_norwegian(ctx, x, y, s, color=(0.94, 0.94, 0.92), roof=(0.25, 0.25, 0.28), alpha=1.0):
    """Grytviken's whalers' church (white timber, steeple)."""
    ctx.rectangle(x, y - s * 0.5, s * 1.1, s * 0.5)
    set_rgba(ctx, color, alpha)
    ctx.fill()
    poly(ctx, [(x - 5, y - s * 0.5), (x + s * 0.55, y - s * 0.85), (x + s * 1.1 + 5, y - s * 0.5)])
    set_rgba(ctx, roof, alpha)
    ctx.fill()
    ctx.rectangle(x + s * 1.1, y - s * 0.95, s * 0.28, s * 0.95)
    set_rgba(ctx, color, alpha)
    ctx.fill()
    poly(ctx, [(x + s * 1.08, y - s * 0.95), (x + s * 1.24, y - s * 1.45), (x + s * 1.4, y - s * 0.95)])
    set_rgba(ctx, roof, alpha)
    ctx.fill()
