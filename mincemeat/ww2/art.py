"""Wartime artwork: S-class submarine, blacked-out London, the Admiralty,
the Andalusian coast, landing craft, and the grave at Huelva."""
import math

import cairo
import numpy as np

from engine import art as A
from engine import people as P
from engine.core import H, W, draw_text, hash01, lerp, mix, poly, radial_glow, ramp, set_rgba, vgrad


# ------------------------------------------------------------------ HMS Seraph (S-class submarine)
def submarine(ctx, x, y, L, facing=1, color=(0.12, 0.13, 0.14), alpha=1.0, light=None, crew=0, t=0.0,
              deck_load=False):
    """British S-class submarine, surfaced, in side view: long low casing, conning tower with bridge,
    periscope standards and 3-inch gun forward of the tower. y = waterline."""
    ctx.save()
    ctx.rectangle(-4000, -4000, 12000, y + 4000 + 3)
    ctx.clip()
    ctx.translate(x, y)
    ctx.scale(facing * L, L)
    ctx.translate(-0.5, 0)
    set_rgba(ctx, color, alpha)
    # hull above water: casing with sheer rising to a raked bow
    poly(ctx, [(0.0, 0.005), (0.02, -0.022), (0.2, -0.03), (0.8, -0.03), (0.93, -0.036), (1.0, -0.05),
               (0.99, 0.005)])
    ctx.fill()
    # conning tower / bridge fairwater
    poly(ctx, [(0.43, -0.03), (0.44, -0.085), (0.5, -0.095), (0.575, -0.09), (0.59, -0.03)])
    ctx.fill()
    # periscope standards and W/T mast
    for px, ph, pw in ((0.49, 0.16, 0.006), (0.515, 0.19, 0.006), (0.545, 0.13, 0.004)):
        ctx.rectangle(px, -ph, pw, ph - 0.09)
        ctx.fill()
    # 3-inch gun on its platform
    ctx.rectangle(0.64, -0.048, 0.03, 0.018)
    ctx.fill()
    ctx.move_to(0.66, -0.045)
    ctx.line_to(0.72, -0.052)
    ctx.set_line_width(0.006)
    ctx.stroke()
    # guard rails
    ctx.set_line_width(0.0015)
    for u in np.linspace(0.1, 0.42, 10):
        ctx.move_to(u, -0.03)
        ctx.line_to(u, -0.045)
    ctx.move_to(0.1, -0.045)
    ctx.line_to(0.42, -0.045)
    ctx.stroke()
    for i in range(crew):  # figures on the casing
        u = 0.3 + i * 0.03
        ctx.save()
        ctx.translate(u, -0.03)
        ctx.scale(1 / L, 1 / L)
        P.standing_figure(ctx, 0, 0, L * 0.05, color, alpha, seed=i)
        ctx.restore()
    if deck_load:   # the canister on the casing
        ctx.rectangle(0.33, -0.042, 0.06, 0.013)
        set_rgba(ctx, mix(color, (0.6, 0.6, 0.6), 0.3), alpha)
        ctx.fill()
    ctx.restore()


# ------------------------------------------------------------------ London, January 1943
def london_street(ctx, t, rain=True):
    """Blacked-out street near King's Cross: terraces, gasholders, a dim lamp."""
    A.sky(ctx, [(0, (0.14, 0.14, 0.17)), (0.7, (0.32, 0.32, 0.34)), (1, (0.45, 0.44, 0.44))], 620)
    A.clouds(ctx, t, 40, 400, (0.5, 0.5, 0.52), seed=33, speed=6, lo=0.45, hi=0.8, alpha=0.6)
    for k in range(3):   # searchlights sweeping
        ang = -math.pi / 2 + math.sin(t * 0.25 + k * 2) * 0.5
        x0 = 300 + k * 650
        ctx.move_to(x0 - 8, 620)
        ctx.line_to(x0 + math.cos(ang - 0.02) * 1200, 620 + math.sin(ang - 0.02) * 1200)
        ctx.line_to(x0 + math.cos(ang + 0.02) * 1200, 620 + math.sin(ang + 0.02) * 1200)
        ctx.line_to(x0 + 8, 620)
        ctx.close_path()
        g = cairo.LinearGradient(x0, 620, x0 + math.cos(ang) * 1200, 620 + math.sin(ang) * 1200)
        g.add_color_stop_rgba(0, 0.9, 0.9, 0.85, 0.22)
        g.add_color_stop_rgba(1, 0.9, 0.9, 0.85, 0)
        ctx.set_source(g)
        ctx.fill()
    # gasholder frames
    for gx, gw in ((1350, 360), (1720, 300)):
        ctx.set_line_width(5)
        for k in range(9):
            xx = gx + k * gw / 8
            ctx.move_to(xx, 640)
            ctx.line_to(xx, 380)
        for yy in (380, 470, 560):
            ctx.move_to(gx, yy)
            ctx.line_to(gx + gw, yy)
        set_rgba(ctx, (0.2, 0.2, 0.21))
        ctx.stroke()
    # terraces
    x = -40
    i = 0
    while x < 1300:
        h = 300 + 60 * hash01(i, 1)
        ctx.rectangle(x, 700 - h, 150, h + 20)
        set_rgba(ctx, (0.13, 0.13, 0.14))
        ctx.fill()
        for c in range(2):
            ctx.rectangle(x + 30 + c * 70, 700 - h - 40, 18, 44)
            ctx.fill()
        x += 150
        i += 1
    ctx.rectangle(0, 700, W, H)
    ctx.set_source(vgrad(ctx, 0, 700, 0, H, [(0, (0.26, 0.26, 0.27)), (1, (0.1, 0.1, 0.11))]))
    ctx.fill()
    # wet reflections under the lamp
    lx = 980
    ctx.set_line_width(8)
    ctx.move_to(lx, H)
    ctx.line_to(lx, 520)
    ctx.line_to(lx + 40, 505)
    set_rgba(ctx, (0.05, 0.05, 0.05))
    ctx.stroke()
    radial_glow(ctx, lx + 40, 520, 320, (0.95, 0.9, 0.7), 0.5)
    for k in range(10):
        ctx.rectangle(lx + 30 - 30 + (k % 3) * 20, 760 + k * 28, 50 - k * 3, 4)
        ctx.set_source_rgba(0.9, 0.85, 0.7, 0.25 - k * 0.02)
        ctx.fill()
    if rain:
        A.rain(ctx, t, 0.25, 320, angle=0.12)


# ------------------------------------------------------------------ Room 13, the Admiralty
def office(ctx, t, figures=2):
    """A basement office at night: wall map, desk lamp, cigarette smoke, two officers."""
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(vgrad(ctx, 0, 0, 0, H, [(0, (0.16, 0.15, 0.14)), (1, (0.08, 0.07, 0.07))]))
    ctx.fill()
    # wall map of the Mediterranean
    ctx.rectangle(260, 150, 760, 440)
    set_rgba(ctx, (0.55, 0.53, 0.48))
    ctx.fill()
    ctx.rectangle(260, 150, 760, 440)
    ctx.set_line_width(10)
    set_rgba(ctx, (0.1, 0.08, 0.06))
    ctx.stroke()
    from . import maps as MM
    ctx.save()
    ctx.rectangle(265, 155, 750, 430)
    ctx.clip()
    mp = MM.Map(14.0, 40.0, 26)
    ctx.translate(640 - W / 2 * 0.4, 370 - H / 2 * 0.4)
    ctx.scale(0.4, 0.4)
    mp.land_path(ctx)
    set_rgba(ctx, (0.72, 0.7, 0.63))
    ctx.fill_preserve()
    ctx.set_line_width(4)
    set_rgba(ctx, (0.25, 0.25, 0.23))
    ctx.stroke()
    ctx.restore()
    # filing cabinets
    for k in range(2):
        ctx.rectangle(1250 + k * 190, 330, 170, 480)
        set_rgba(ctx, (0.2, 0.2, 0.2))
        ctx.fill()
        for d in range(4):
            ctx.rectangle(1300 + k * 190, 370 + d * 110, 70, 12)
            set_rgba(ctx, (0.55, 0.55, 0.5))
            ctx.fill()
    # desk
    poly(ctx, [(120, 800), (1800, 800), (1900, 1080), (20, 1080)])
    set_rgba(ctx, (0.13, 0.09, 0.06))
    ctx.fill()
    # desk lamp with pool of light
    lx, ly = 1100, 640
    ctx.set_line_width(12)
    ctx.move_to(lx, 800)
    ctx.line_to(lx - 40, 700)
    ctx.line_to(lx + 30, ly)
    set_rgba(ctx, (0.1, 0.1, 0.1))
    ctx.stroke()
    poly(ctx, [(lx - 30, ly - 30), (lx + 90, ly - 10), (lx + 70, ly + 40), (lx - 10, ly + 20)])
    ctx.fill()
    g = cairo.RadialGradient(lx + 40, 860, 20, lx + 40, 860, 700)
    g.add_color_stop_rgba(0, 1, 0.92, 0.7, 0.5)
    g.add_color_stop_rgba(1, 1, 0.92, 0.7, 0)
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(g)
    ctx.fill()
    for k in range(5):   # papers on the desk
        ctx.save()
        ctx.translate(700 + k * 120, 900 + (k % 2) * 20)
        ctx.rotate((hash01(k, 3) - 0.5) * 0.4)
        ctx.rectangle(-70, -45, 140, 90)
        set_rgba(ctx, (0.85, 0.83, 0.76))
        ctx.fill()
        ctx.restore()
    # two officers in naval/RAF uniform, one standing, one seated
    if figures:
        P.standing_figure(ctx, 560, 1000, 560, (0.07, 0.07, 0.08), seed=3)
        ctx.rectangle(525, 470, 70, 18)          # cap
        set_rgba(ctx, (0.07, 0.07, 0.08))
        ctx.fill()
        P.standing_figure(ctx, 1500, 1060, 480, (0.08, 0.08, 0.09), seed=5)
        A.smoke(ctx, 1545, 700, t, seed=4, rate=2, life=8, rise=22, size=12, alpha=0.3, wind=6,
                color=(0.8, 0.8, 0.78), grow=5)


# ------------------------------------------------------------------ Andalusian coast
def spanish_town(ctx, base, x0, x1, color=(0.92, 0.9, 0.84), roof=(0.62, 0.38, 0.28), seed=0, tower=True):
    r = np.random.default_rng(seed)
    x = x0
    while x < x1:
        w = 60 + r.random() * 90
        h = 40 + r.random() * 70
        ctx.rectangle(x, base - h, w, h)
        set_rgba(ctx, mix(color, (0, 0, 0), 0.1 * r.random()))
        ctx.fill()
        poly(ctx, [(x - 3, base - h), (x + w + 3, base - h), (x + w - 8, base - h - 14), (x + 8, base - h - 14)])
        set_rgba(ctx, roof)
        ctx.fill()
        for k in range(int(w // 30)):
            ctx.rectangle(x + 10 + k * 30, base - h * 0.6, 10, 16)
            set_rgba(ctx, (0.2, 0.18, 0.16))
            ctx.fill()
        x += w + 4
    if tower:   # church tower with belfry
        tx = lerp(x0, x1, 0.55)
        ctx.rectangle(tx, base - 230, 60, 230)
        set_rgba(ctx, color)
        ctx.fill()
        ctx.rectangle(tx + 18, base - 205, 24, 40)
        set_rgba(ctx, (0.2, 0.18, 0.16))
        ctx.fill()
        poly(ctx, [(tx - 4, base - 230), (tx + 30, base - 290), (tx + 64, base - 230)])
        set_rgba(ctx, roof)
        ctx.fill()


def palm(ctx, x, y, h, color, t, seed=0):
    ctx.set_line_width(h * 0.04)
    ctx.move_to(x, y)
    ctx.curve_to(x + h * 0.06, y - h * 0.4, x - h * 0.02, y - h * 0.75, x + h * 0.03, y - h)
    set_rgba(ctx, color)
    ctx.stroke()
    tx, ty = x + h * 0.03, y - h
    for k in range(11):
        a = -math.pi / 2 + (k - 5) * 0.34 + math.sin(t * 1.1 + k + seed) * 0.03
        L = h * (0.32 + 0.06 * hash01(seed, k))
        ex, ey = tx + math.cos(a) * L, ty + math.sin(a) * L * 0.55 + h * 0.15 * abs(math.cos(a))
        ctx.move_to(tx, ty)
        ctx.curve_to(tx + math.cos(a) * L * 0.5, ty + math.sin(a) * L * 0.5 - h * 0.03, ex, ey - h * 0.02, ex, ey)
        ctx.set_line_width(h * 0.025)
        ctx.stroke()


def cypress(ctx, x, y, h, color=(0.12, 0.16, 0.12), alpha=1.0):
    ctx.move_to(x, y)
    ctx.curve_to(x - h * 0.09, y - h * 0.3, x - h * 0.05, y - h * 0.8, x, y - h)
    ctx.curve_to(x + h * 0.05, y - h * 0.8, x + h * 0.09, y - h * 0.3, x, y)
    set_rgba(ctx, color, alpha)
    ctx.fill()


def fishing_boat(ctx, x, y, L, t, color=(0.2, 0.18, 0.16), sail=True):
    bob = math.sin(t * 1.4) * 4
    ctx.save()
    ctx.translate(x, y + bob)
    ctx.rotate(math.sin(t * 1.1) * 0.03)
    poly(ctx, [(-L / 2, -L * 0.1), (L / 2, -L * 0.14), (L * 0.4, 0), (-L * 0.42, 0)])
    set_rgba(ctx, color)
    ctx.fill()
    ctx.move_to(0, -L * 0.12)
    ctx.line_to(0, -L * 0.8)
    ctx.set_line_width(max(2, L * 0.02))
    ctx.stroke()
    if sail:   # lateen sail
        poly(ctx, [(-L * 0.35, -L * 0.2), (L * 0.35, -L * 0.85), (L * 0.05, -L * 0.15)])
        set_rgba(ctx, mix(color, (0.9, 0.88, 0.8), 0.6))
        ctx.fill()
    P.standing_figure(ctx, -L * 0.2, -L * 0.1, L * 0.28, color, seed=2)
    ctx.restore()


# ------------------------------------------------------------------ 10 July 1943
def landing_craft(ctx, x, y, L, t, color=(0.15, 0.15, 0.15), ramp_down=0.0):
    """LCA-type assault landing craft seen from the side, bow to the right."""
    bob = math.sin(t * 2 + x * 0.01) * 4
    ctx.save()
    ctx.translate(x, y + bob)
    poly(ctx, [(-L / 2, -L * 0.12), (L * 0.42, -L * 0.12), (L / 2, -L * 0.02), (L * 0.45, 0), (-L * 0.48, 0)])
    set_rgba(ctx, color)
    ctx.fill()
    ctx.rectangle(-L * 0.35, -L * 0.2, L * 0.12, L * 0.08)
    ctx.fill()
    for k in range(6):   # helmets of the troops aboard
        ctx.arc(-L * 0.18 + k * L * 0.1, -L * 0.13, L * 0.03, math.pi, 2 * math.pi)
        ctx.fill()
    ctx.restore()
    A.splash(ctx, x + L * 0.5, y, (t * 1.3) % 2.2, 0.0, h=L * 0.15, w=L * 0.08, dur=2.2,
             color=(0.85, 0.85, 0.85))


def headstone_huelva(ctx, x, y, s, lines, extra, extra_alpha=0.0, t=0.0):
    """The white marble headstone of Major Martin in Huelva cemetery, with the
    1998 line added at the foot."""
    w, h = s * 0.62, s
    ctx.move_to(x - w / 2, y)
    ctx.line_to(x - w / 2, y - h * 0.86)
    ctx.curve_to(x - w / 2, y - h * 1.01, x + w / 2, y - h * 1.01, x + w / 2, y - h * 0.86)
    ctx.line_to(x + w / 2, y)
    ctx.close_path()
    ctx.set_source(vgrad(ctx, x - w / 2, 0, x + w / 2, 0, [(0, (0.96, 0.95, 0.92)), (1, (0.78, 0.77, 0.74))]))
    ctx.fill()
    # cross
    ctx.rectangle(x - s * 0.012, y - h * 0.9, s * 0.024, s * 0.12)
    ctx.rectangle(x - s * 0.045, y - h * 0.87, s * 0.09, s * 0.022)
    set_rgba(ctx, (0.35, 0.33, 0.3))
    ctx.fill()
    for i, (text, size) in enumerate(lines):
        draw_text(ctx, text, x, y - h * 0.7 + i * s * 0.057, "oldstd_b", s * size, (0.25, 0.23, 0.21), "cb", 0.95,
                  0.06)
    for i, (text, size) in enumerate(extra):
        draw_text(ctx, text, x, y - h * 0.13 + i * s * 0.05, "oldstd_b", s * size, (0.25, 0.23, 0.21), "cb",
                  extra_alpha, 0.06)
