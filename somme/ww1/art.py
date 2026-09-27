"""Artwork for 1916: trenches, wire, shell-torn ground, guns, the Mark I tank,
the Lochnagar/Hawthorn mines, shattered woods, and the Thiepval Memorial."""
import functools
import math

import cairo
import numpy as np

from engine import art as A
from engine import people as P
from engine.core import H, W, clamp, hash01, lerp, mix, poly, radial_glow, ramp, set_rgba, smooth_poly, vgrad


# ------------------------------------------------------------------ ground
def cratered_ground(ctx, y, t=0.0, color=(0.28, 0.24, 0.19), seed=1, height=60, craters=18, x0=-50, x1=W + 50,
                    rim=(0.42, 0.37, 0.3), mud=False):
    """Undulating shell-torn ground from y to bottom, with craters."""
    prof = A.ridge_profile(seed, 200, 0.6)
    pts = [(lerp(x0, x1, i / 199), y - v * height) for i, v in enumerate(prof)]
    ctx.move_to(x0, H + 20)
    for p in pts:
        ctx.line_to(*p)
    ctx.line_to(x1, H + 20)
    ctx.close_path()
    ctx.set_source(vgrad(ctx, 0, y - height, 0, H, [(0, mix(color, (1, 1, 1), 0.08)), (1, mix(color, (0, 0, 0), 0.4))]))
    ctx.fill()
    r = np.random.default_rng(seed + 50)
    for _ in range(craters):
        d = r.random()
        cy = lerp(y + 10, H + 40, d ** 1.3)
        cx = x0 + r.random() * (x1 - x0)
        rw = (20 + 140 * d) * (0.6 + r.random() * 0.8)
        rh = rw * (0.18 + 0.1 * d)
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(1, rh / rw)
        ctx.arc(0, 0, rw * 1.15, 0, 6.283)
        ctx.restore()
        set_rgba(ctx, rim, 0.55)
        ctx.fill()
        ctx.save()
        ctx.translate(cx, cy + rh * 0.1)
        ctx.scale(1, rh / rw)
        ctx.arc(0, 0, rw, 0, 6.283)
        ctx.restore()
        if mud:
            ctx.set_source(vgrad(ctx, 0, cy - rh, 0, cy + rh, [(0, (0.55, 0.55, 0.52)), (1, (0.25, 0.26, 0.26))]))
        else:
            set_rgba(ctx, mix(color, (0, 0, 0), 0.45))
        ctx.fill()


def stump(ctx, x, y, h, color=(0.1, 0.09, 0.08), seed=0, alpha=1.0):
    """A shell-shattered tree: bare trunk, splintered top, a broken limb or two."""
    w = h * 0.07
    sp = [(x - w, y), (x - w * 0.7, y - h * 0.6)]
    for k in range(5):
        sp.append((x - w * 0.6 + k * w * 0.3, y - h * (0.85 + 0.15 * hash01(seed, k))))
    sp += [(x + w * 0.6, y - h * 0.62), (x + w, y)]
    poly(ctx, sp)
    set_rgba(ctx, color, alpha)
    ctx.fill()
    for k in range(int(1 + 2 * hash01(seed, 9))):
        by = y - h * (0.35 + 0.35 * hash01(seed, k, 3))
        dirn = 1 if hash01(seed, k, 4) > 0.5 else -1
        L = h * (0.15 + 0.2 * hash01(seed, k, 5))
        ctx.move_to(x, by)
        ctx.line_to(x + dirn * L, by - L * (0.4 + 0.5 * hash01(seed, k, 6)))
        ctx.set_line_width(w * 0.45)
        set_rgba(ctx, color, alpha)
        ctx.stroke()


def wire(ctx, x0, x1, y, h=40, seed=0, color=(0.08, 0.07, 0.06), alpha=1.0, stakes=True):
    """Barbed-wire entanglement: screw pickets and looping strands."""
    r = np.random.default_rng(seed)
    ctx.set_line_width(1.4)
    if stakes:
        x = x0
        while x < x1:
            ctx.move_to(x, y)
            ctx.line_to(x + (r.random() - 0.5) * 8, y - h * (0.8 + 0.4 * r.random()))
            x += 40 + r.random() * 40
        set_rgba(ctx, color, alpha)
        ctx.set_line_width(3)
        ctx.stroke()
    ctx.set_line_width(1.3)
    for strand in range(4):
        x = x0
        ctx.move_to(x, y - h * (0.2 + 0.2 * strand))
        while x < x1:
            step = 14 + r.random() * 16
            cy = y - h * (0.15 + 0.22 * strand) + (r.random() - 0.5) * h * 0.4
            ctx.curve_to(x + step * 0.3, cy - h * 0.35 * r.random(), x + step * 0.7, cy + h * 0.35 * r.random(),
                         x + step, cy)
            x += step
    set_rgba(ctx, color, alpha * 0.9)
    ctx.stroke()


def sandbags(ctx, x0, x1, y, rows=4, bw=46, bh=20, color=(0.55, 0.48, 0.36), seed=0, alpha=1.0, jitter=1.0):
    """A sandbag parapet built up from y (bottom) in courses."""
    r = np.random.default_rng(seed)
    for row in range(rows):
        yy = y - (row + 1) * bh * 0.85
        off = (row % 2) * bw * 0.5
        x = x0 - off
        while x < x1:
            w = bw * (0.9 + 0.2 * r.random())
            c = mix(color, (0, 0, 0), 0.1 + 0.25 * r.random())
            ctx.save()
            ctx.translate(x + w / 2, yy + bh / 2 + (r.random() - 0.5) * 3 * jitter)
            ctx.rotate((r.random() - 0.5) * 0.08 * jitter)
            ctx.scale(w / 2, bh / 2)
            ctx.arc(0, 0, 1, 0, 6.283)
            ctx.restore()
            set_rgba(ctx, c, alpha)
            ctx.fill_preserve()
            ctx.set_line_width(1.2)
            set_rgba(ctx, mix(c, (0, 0, 0), 0.5), alpha * 0.6)
            ctx.stroke()
            x += w * 0.95


def ladder(ctx, x, y_bottom, y_top, w=46, color=(0.35, 0.27, 0.18), alpha=1.0):
    ctx.set_line_width(6)
    ctx.move_to(x, y_bottom)
    ctx.line_to(x + 8, y_top)
    ctx.move_to(x + w, y_bottom)
    ctx.line_to(x + w + 8, y_top)
    n = 7
    for i in range(1, n):
        yy = lerp(y_bottom, y_top, i / n)
        xx = lerp(0, 8, i / n)
        ctx.move_to(x + xx, yy)
        ctx.line_to(x + xx + w, yy)
    set_rgba(ctx, color, alpha)
    ctx.stroke()


# ------------------------------------------------------------------ explosions
def shell_burst(ctx, x, y, t, t0, size=1.0, seed=0, color=(0.38, 0.35, 0.31)):
    """High-explosive burst on the ground: flash, earth fountain, drifting smoke."""
    a = t - t0
    if a < 0:
        return
    A.flash(ctx, x, y - 20 * size, t, t0, r=220 * size, dur=0.5, color=(1, 0.85, 0.6))
    if a < 1.6:   # thrown earth
        u = a / 1.6
        for k in range(22):
            ang = -math.pi / 2 + (hash01(seed, k) - 0.5) * 1.6
            sp = 260 * size * (0.4 + hash01(seed, k, 2))
            px = x + math.cos(ang) * sp * a
            py = y + math.sin(ang) * sp * a + 380 * size * a * a
            if py < y + 5:
                ctx.arc(px, py, (3 + 5 * hash01(seed, k, 3)) * size, 0, 6.283)
                set_rgba(ctx, (0.18, 0.14, 0.1), 1 - u)
                ctx.fill()
    A.smoke(ctx, x, y - 10 * size, t, seed=seed, rate=18, life=5, rise=34 * size, size=22 * size, alpha=0.55,
            start=t0, stop=t0 + 0.9, wind=14, color=color, grow=3.5, spread=1.6)
    # stop emitting after the burst: fade by limiting emission window
    return


def shrapnel_burst(ctx, x, y, t, t0, size=1.0, seed=0):
    """Airburst shrapnel: a flash and a hanging white-grey puff (as in the 1916 film)."""
    a = t - t0
    if a < 0:
        return
    A.flash(ctx, x, y, t, t0, r=120 * size, dur=0.35, color=(1, 0.95, 0.8))
    k = min(1, a * 3)
    r = 40 * size * (0.5 + k) * (1 + 0.1 * a)
    alpha = 0.8 * math.exp(-a / 4)
    ctx.save()
    ctx.translate(x + a * 10, y - a * 4)
    for j in range(5):
        ang = j * 1.3 + seed
        rr = r * (0.55 + 0.25 * hash01(seed, j))
        g = cairo.RadialGradient(math.cos(ang) * r * 0.3, math.sin(ang) * r * 0.2, 0,
                                 math.cos(ang) * r * 0.3, math.sin(ang) * r * 0.2, rr)
        g.add_color_stop_rgba(0, 0.85, 0.84, 0.8, alpha)
        g.add_color_stop_rgba(1, 0.85, 0.84, 0.8, 0)
        ctx.set_source(g)
        ctx.arc(math.cos(ang) * r * 0.3, math.sin(ang) * r * 0.2, rr, 0, 6.283)
        ctx.fill()
    ctx.restore()


def mine(ctx, x, y, t, t0, size=1.0, seed=3):
    """The great mines of 1 July: a dome of chalk and earth heaving up, then a towering column."""
    a = t - t0
    if a < 0:
        return 0.0
    k = A.flash(ctx, x, y, t, t0, r=900 * size, dur=1.2, color=(1, 0.9, 0.7))
    # heaving dome (first ~0.5 s)
    if a < 0.8:
        u = a / 0.8
        rw, rh = 420 * size * (0.5 + u), 300 * size * math.sin(min(1, u * 1.5) * math.pi / 2)
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(1, rh / rw if rw else 1)
        ctx.arc(0, 0, rw, math.pi, 2 * math.pi)
        ctx.restore()
        set_rgba(ctx, (0.35, 0.3, 0.24), 0.9 * (1 - u * 0.3))
        ctx.fill()
    # column of earth and chalk: rising then spreading like a tree
    for j in range(140):
        born = (j / 140) * 1.4
        age = a - born * 0.3
        if age <= 0:
            continue
        ang = -math.pi / 2 + (hash01(seed, j) - 0.5) * (0.35 + 0.6 * hash01(seed, j, 7))
        sp = 900 * size * (0.35 + 0.65 * hash01(seed, j, 2))
        px = x + math.cos(ang) * sp * age * 0.9
        py = y + math.sin(ang) * sp * age + 160 * size * age * age
        if py > y + 20:
            continue
        rr = (30 + 90 * hash01(seed, j, 3)) * size * (0.6 + 0.9 * min(age, 2.5))
        chalk = hash01(seed, j, 4) < 0.35
        col = (0.78, 0.76, 0.7) if chalk else (0.22, 0.18, 0.14)
        al = 0.85 * math.exp(-max(0, age - 2.0) / 2.5)
        g = cairo.RadialGradient(px, py, rr * 0.1, px, py, rr)
        g.add_color_stop_rgba(0, *col, al)
        g.add_color_stop_rgba(0.6, *col, al * 0.7)
        g.add_color_stop_rgba(1, *col, 0)
        ctx.set_source(g)
        ctx.arc(px, py, rr, 0, 6.283)
        ctx.fill()
    return k


# ------------------------------------------------------------------ guns
def field_gun(ctx, x, y, s, facing=1, recoil=0.0, color=(0.1, 0.1, 0.09), alpha=1.0, elev=0.18):
    """18-pounder field gun: wheels, shield, long barrel on a cradle."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(facing * s, s)
    set_rgba(ctx, color, alpha)
    # trail
    poly(ctx, [(-0.05, -0.18), (-0.9, 0.0), (-0.85, 0.03), (0.0, -0.12)])
    ctx.fill()
    # barrel
    ctx.save()
    ctx.translate(0.0, -0.3)
    ctx.rotate(-elev)
    ctx.rectangle(-0.25 - recoil * 0.2, -0.035, 1.05, 0.07)
    ctx.fill()
    ctx.rectangle(-0.3 - recoil * 0.2, -0.06, 0.45, 0.12)
    ctx.fill()
    ctx.restore()
    # shield
    poly(ctx, [(0.05, -0.55), (0.14, -0.55), (0.16, -0.12), (0.03, -0.12)])
    ctx.fill()
    # wheel
    ctx.arc(0.0, -0.2, 0.2, 0, 6.283)
    ctx.set_line_width(0.035)
    ctx.stroke()
    for k in range(12):
        ang = k * math.pi / 6
        ctx.move_to(0, -0.2)
        ctx.line_to(math.cos(ang) * 0.2, -0.2 + math.sin(ang) * 0.2)
    ctx.set_line_width(0.012)
    ctx.stroke()
    ctx.restore()
    tip = (x + facing * s * (0.8 * math.cos(elev)), y - s * (0.3 + 0.8 * math.sin(elev)))
    return tip


def howitzer(ctx, x, y, s, facing=1, recoil=0.0, color=(0.1, 0.1, 0.09), alpha=1.0, elev=0.7):
    """Heavy howitzer on a steel bed: short, fat, steeply elevated barrel."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(facing * s, s)
    set_rgba(ctx, color, alpha)
    poly(ctx, [(-0.7, 0.0), (0.7, 0.0), (0.6, -0.12), (-0.6, -0.12)])
    ctx.fill()
    poly(ctx, [(-0.25, -0.12), (0.25, -0.12), (0.15, -0.42), (-0.15, -0.42)])
    ctx.fill()
    ctx.save()
    ctx.translate(0.0, -0.38)
    ctx.rotate(-elev)
    ctx.rectangle(-0.3 - recoil * 0.15, -0.09, 0.95, 0.18)
    ctx.fill()
    ctx.rectangle(0.55 - recoil * 0.15, -0.11, 0.1, 0.22)
    ctx.fill()
    ctx.restore()
    ctx.restore()
    return (x + facing * s * 0.65 * math.cos(elev), y - s * (0.38 + 0.65 * math.sin(elev)))


def muzzle_flash(ctx, tip, t, t0, size=1.0, facing=1):
    a = t - t0
    if a < 0 or a > 2.5:
        return 0.0
    k = max(0.0, 1 - a / 0.18)
    if k > 0:
        radial_glow(ctx, tip[0] + facing * 30 * size, tip[1] - 10 * size, 260 * size, (1, 0.8, 0.45), k)
        radial_glow(ctx, tip[0] + facing * 20 * size, tip[1] - 6 * size, 60 * size, (1, 1, 0.9), k)
    A.smoke(ctx, tip[0] + facing * 30 * size, tip[1], t, seed=int(t0 * 10) % 97, rate=18, life=2.3,
            rise=25 * size, size=20 * size, alpha=0.5, start=t0, wind=10 * facing, color=(0.7, 0.68, 0.64),
            grow=3)
    return k


# ------------------------------------------------------------------ Mark I tank
TANK_HULL = [(0.14, 0.0), (0.78, 0.0), (0.93, -0.12), (1.0, -0.3), (0.98, -0.36), (0.8, -0.4),
             (0.2, -0.4), (0.06, -0.34), (0.0, -0.24), (0.04, -0.1)]


def tank(ctx, x, y, L, facing=1, t=0.0, color=(0.3, 0.28, 0.22), alpha=1.0, male=True, tail=True, pitch=0.0):
    """British Mark I (Male) tank in side view: rhomboid hull with all-round tracks,
    a 6-pounder in the side sponson, and the twin-wheel steering tail."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(pitch) * facing)
    ctx.scale(facing * L, L)
    ctx.translate(-0.5, 0)
    if tail:
        ctx.set_line_width(0.012)
        ctx.move_to(0.06, -0.14)
        ctx.line_to(-0.14, -0.05)
        ctx.move_to(0.1, -0.2)
        ctx.line_to(-0.14, -0.08)
        set_rgba(ctx, mix(color, (0, 0, 0), 0.4), alpha)
        ctx.stroke()
        for wx in (-0.16, -0.07):
            ctx.arc(wx, -0.05, 0.05, 0, 6.283)
            set_rgba(ctx, mix(color, (0, 0, 0), 0.5), alpha)
            ctx.fill()
    poly(ctx, TANK_HULL)
    set_rgba(ctx, mix(color, (0, 0, 0), 0.35), alpha)
    ctx.fill()
    # hull side plate inside the track loop, with camouflage blotches
    inner = [(0.2, -0.05), (0.76, -0.05), (0.88, -0.14), (0.93, -0.29), (0.8, -0.34), (0.22, -0.34),
             (0.1, -0.3), (0.07, -0.2), (0.1, -0.1)]
    poly(ctx, inner)
    set_rgba(ctx, color, alpha)
    ctx.fill_preserve()
    ctx.save()
    ctx.clip()
    for k in range(9):
        cx, cy = 0.12 + 0.09 * k, -0.08 - 0.22 * hash01(k, 2)
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(0.07, 0.04)
        ctx.arc(0, 0, 1, 0, 6.283)
        ctx.restore()
        set_rgba(ctx, mix(color, (0.45, 0.35, 0.2) if k % 2 else (0.18, 0.2, 0.14), 0.6), alpha)
        ctx.fill()
    # rivets
    for rx in np.linspace(0.18, 0.84, 14):
        for ry in (-0.31, -0.08):
            ctx.new_sub_path()
            ctx.arc(rx, ry, 0.005, 0, 6.283)
    set_rgba(ctx, mix(color, (0, 0, 0), 0.5), alpha)
    ctx.fill()
    ctx.restore()
    # track plates moving
    ctx.set_line_width(0.004)
    off = (t * 0.3) % 0.03
    for k in range(34):
        u = 0.14 + ((k * 0.03 + off) % 0.66)
        ctx.move_to(u, 0.0)
        ctx.line_to(u, -0.03)
        ctx.move_to(u + 0.03, -0.37)
        ctx.line_to(u + 0.03, -0.4)
    set_rgba(ctx, (0.05, 0.05, 0.04), alpha)
    ctx.stroke()
    # sponson with 6-pounder (Male) or Vickers guns (Female)
    poly(ctx, [(0.38, -0.3), (0.62, -0.3), (0.66, -0.2), (0.62, -0.1), (0.4, -0.1), (0.35, -0.18)])
    set_rgba(ctx, mix(color, (0, 0, 0), 0.15), alpha)
    ctx.fill()
    ctx.set_line_width(0.028 if male else 0.014)
    ctx.move_to(0.64, -0.2)
    ctx.line_to(0.82, -0.2)
    set_rgba(ctx, (0.08, 0.08, 0.07), alpha)
    ctx.stroke()
    # cab and vision slits
    ctx.rectangle(0.72, -0.46, 0.12, 0.07)
    set_rgba(ctx, mix(color, (0, 0, 0), 0.2), alpha)
    ctx.fill()
    ctx.rectangle(0.76, -0.435, 0.05, 0.01)
    set_rgba(ctx, (0.05, 0.05, 0.05), alpha)
    ctx.fill()
    ctx.restore()


# ------------------------------------------------------------------ figures
def advancing_line(ctx, t, y0, x_start, n=9, spacing=150, speed=38, h=230, color=(0.08, 0.08, 0.07), seed=0,
                   falls=(), helmet="brodie", depth_jitter=30):
    """A wave of infantry walking forward at the steady pace ordered on 1 July.
    falls: list of (index, time) - that man stumbles and falls at that time."""
    fall_map = dict(falls)
    for i in range(n):
        x = x_start + i * spacing + t * speed + (hash01(seed, i) - 0.5) * 40
        y = y0 + (hash01(seed, i, 2) - 0.5) * depth_jitter
        hh = h * (0.92 + 0.12 * hash01(seed, i, 3))
        phase = (t * speed + i * 57) / (hh * 0.27) * math.pi
        if i in fall_map and t > fall_map[i]:
            a = t - fall_map[i]
            x = x_start + i * spacing + fall_map[i] * speed + (hash01(seed, i) - 0.5) * 40
            ang = min(1.0, a / 0.6) * 1.35
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(ang)
            P.soldier(ctx, 0, 0, hh, 0.3, 1, color, pack=True, lean=20, helmet=helmet, bayonet=True,
                      rifle_pose="slope", alpha=1.0)
            ctx.restore()
            continue
        P.soldier(ctx, x, y, hh, phase, 1, color, pack=True, lean=14, helmet=helmet, bayonet=True,
                  rifle_pose="slope", stride=0.8)


def stretcher_party(ctx, x, y, h, t, color=(0.08, 0.08, 0.07), facing=-1):
    ph = t * 3.2
    P.soldier(ctx, x, y, h, ph, facing, color, pack=False, lean=10, rifle=False, helmet="brodie")
    P.soldier(ctx, x + facing * h * 0.75, y, h, ph + math.pi, facing, color, pack=False, lean=10, rifle=False,
              helmet="brodie")
    sy = y - h * 0.45
    ctx.set_line_width(h * 0.03)
    ctx.move_to(x + facing * h * 0.1, sy)
    ctx.line_to(x + facing * h * 0.65, sy)
    set_rgba(ctx, color)
    ctx.stroke()
    ctx.rectangle(min(x + facing * h * 0.12, x + facing * h * 0.63), sy - h * 0.07, abs(facing * h * 0.51), h * 0.07)
    ctx.fill()


# ------------------------------------------------------------------ memorials
def thiepval_memorial(ctx, x, y, s, color=(0.62, 0.36, 0.28), stone=(0.85, 0.82, 0.74), alpha=1.0, t=0.0):
    """Lutyens' Memorial to the Missing of the Somme: interlocking arches rising in
    stepped tiers to a great central arch, brick with stone dressings, flags on top."""
    def block(x0, x1, y0, y1, arch_w=0.0, arch_h=0.0):
        ctx.rectangle(x + x0 * s, y - y1 * s, (x1 - x0) * s, (y1 - y0) * s)
        set_rgba(ctx, color, alpha)
        ctx.fill()
        ctx.rectangle(x + x0 * s, y - y1 * s, (x1 - x0) * s, 0.025 * s)
        set_rgba(ctx, stone, alpha)
        ctx.fill()

    def arch(cx, w, h, y0=0.0):
        ctx.move_to(x + (cx - w / 2) * s, y - y0 * s)
        ctx.line_to(x + (cx - w / 2) * s, y - (y0 + h - w / 2) * s)
        ctx.arc(x + cx * s, y - (y0 + h - w / 2) * s, w / 2 * s, math.pi, 0)
        ctx.line_to(x + (cx + w / 2) * s, y - y0 * s)
        ctx.close_path()

    tiers = [(-1.0, 1.0, 0.0, 0.62), (-0.72, 0.72, 0.62, 0.92), (-0.46, 0.46, 0.92, 1.18), (-0.28, 0.28, 1.18, 1.4)]
    for x0, x1, y0, y1 in tiers:
        block(x0, x1, y0, y1)
    # stone base and dressings
    ctx.rectangle(x - 1.05 * s, y - 0.06 * s, 2.1 * s, 0.06 * s)
    set_rgba(ctx, stone, alpha)
    ctx.fill()
    # arches: great central arch and the lesser arches of the flanks
    arch(0.0, 0.34, 0.95)
    for cx in (-0.62, 0.62):
        arch(cx, 0.2, 0.5)
    for cx in (-0.36, 0.36):
        arch(cx, 0.14, 0.66, 0.0)
    set_rgba(ctx, (0.08, 0.07, 0.07), alpha * 0.85)
    ctx.fill()
    # stone arch rings
    ctx.set_line_width(0.02 * s)
    ctx.arc(x, y - (0.95 - 0.17) * s, 0.19 * s, math.pi, 0)
    set_rgba(ctx, stone, alpha)
    ctx.stroke()
    # flagstaffs: Union flag and French tricolour fly on top
    for fx, kind in ((-0.12, "union"), (0.12, "tricolour")):
        px, py = x + fx * s, y - 1.4 * s
        ctx.move_to(px, py)
        ctx.line_to(px, py - 0.35 * s)
        ctx.set_line_width(0.008 * s)
        set_rgba(ctx, (0.2, 0.2, 0.2), alpha)
        ctx.stroke()
        fw, fh = 0.2 * s, 0.1 * s
        if kind == "union":
            P.flag(ctx, "union", px, py - 0.35 * s, fw, fh, t, amp=0.08, alpha=alpha)
        else:
            _tricolour(ctx, px, py - 0.35 * s, fw, fh, t, alpha)


def _tricolour(ctx, x, y, w, h, t, alpha):
    for i, c in enumerate(((0.0, 0.14, 0.58), (0.97, 0.97, 0.95), (0.9, 0.1, 0.15))):
        for k in range(8):
            u0 = (i + k / 8) / 3
            dy = math.sin(t * 5 - u0 * 7) * 0.08 * h * u0
            ctx.rectangle(x + u0 * w, y + dy, w / 24 + 1, h)
            set_rgba(ctx, c, alpha)
            ctx.fill()


def headstone(ctx, x, y, h, color=(0.92, 0.91, 0.87), alpha=1.0):
    """Commonwealth War Graves Commission headstone: upright, gently curved top."""
    w = h * 0.55
    ctx.move_to(x - w / 2, y)
    ctx.line_to(x - w / 2, y - h * 0.85)
    ctx.curve_to(x - w / 2, y - h * 1.02, x + w / 2, y - h * 1.02, x + w / 2, y - h * 0.85)
    ctx.line_to(x + w / 2, y)
    ctx.close_path()
    set_rgba(ctx, color, alpha)
    ctx.fill()
    ctx.arc(x, y - h * 0.62, w * 0.18, 0, 6.283)
    ctx.set_line_width(max(1, h * 0.02))
    set_rgba(ctx, mix(color, (0, 0, 0), 0.35), alpha * 0.6)
    ctx.stroke()


def poppies(ctx, x0, x1, y0, y1, t, n=260, seed=5, alpha=1.0, red=(0.78, 0.08, 0.06)):
    r = np.random.default_rng(seed)
    for _ in range(n):
        d = r.random()
        y = lerp(y0, y1, d ** 0.7)
        x = lerp(x0, x1, r.random())
        s = 3 + 16 * d
        sway = math.sin(t * 1.4 + x * 0.01) * 3 * d
        ctx.move_to(x, y + s * 3)
        ctx.line_to(x + sway, y)
        ctx.set_line_width(max(1, s * 0.12))
        set_rgba(ctx, (0.2, 0.28, 0.15), alpha)
        ctx.stroke()
        for k in range(4):
            ang = k * math.pi / 2 + r.random() * 0.4
            ctx.new_sub_path()
            ctx.arc(x + sway + math.cos(ang) * s * 0.45, y + math.sin(ang) * s * 0.3, s * 0.55, 0, 6.283)
        set_rgba(ctx, mix(red, (0, 0, 0), 0.15 * r.random()), alpha)
        ctx.fill()
        ctx.arc(x + sway, y, s * 0.2, 0, 6.283)
        set_rgba(ctx, (0.05, 0.05, 0.05), alpha)
        ctx.fill()


# ------------------------------------------------------------------ period poster figures
def marching_column(ctx, x0, y, n, h, t, color, spacing=None, speed=30, helmet="cap"):
    spacing = spacing or h * 0.42
    for i in range(n):
        x = x0 + i * spacing + t * speed
        ph = (t * speed + i * 40) / (h * 0.27) * math.pi
        P.soldier(ctx, x, y, h, ph, 1, color, pack=True, lean=6, helmet=helmet, rifle_pose="slope", stride=0.9)
