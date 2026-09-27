"""Opening, stalemate, Verdun, Kitchener's Army, the bombardment."""
import math

import cairo
import numpy as np

from engine import art as A
from engine import people as P
from engine.core import (H, W, clamp, draw_text, ease_in_out, ease_out, hash01, hexc, lerp, mix, poly, ramp,
                         radial_glow, set_rgba, text_width, vgrad)
from ww1 import art as R
from ww1 import cards as C
from ww1 import maps as M
from .common import camera, shake


# ---------------------------------------------------------------- 0. opening intertitle
def card_open(ctx, S):
    C.intertitle(ctx, S, ["Picardy, France.", None, "The 1st of July, 1916."], [72, 0, 64],
                 ["fell_i", "fell", "fell"])


# ---------------------------------------------------------------- 1. dawn in the front line
def dawn_trench(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.1, (0, 20), (-30, 0))
    A.sky(ctx, [(0, (0.55, 0.55, 0.55)), (0.7, (0.85, 0.84, 0.8)), (1, (0.95, 0.93, 0.88))], 620)
    A.clouds(ctx, t, 60, 360, (1, 1, 1), seed=201, speed=5, lo=0.5, hi=0.85, alpha=0.6)
    # the German line across no man's land, under the last of the bombardment
    R.cratered_ground(ctx, 600, t, (0.55, 0.52, 0.47), seed=11, height=30, craters=0)
    A.haze(ctx, 520, 660, (0.92, 0.91, 0.88), 0.7)
    for k in range(6):
        R.shrapnel_burst(ctx, 300 + k * 260 + hash01(k, 1) * 80, 380 + hash01(k, 2) * 80, t, 0.3 + k * 1.1,
                         0.8, seed=k)
    # the trench: rear wall, fire step, parapet of sandbags, ladders
    ctx.rectangle(0, 640, W, H)
    ctx.set_source(vgrad(ctx, 0, 640, 0, H, [(0, (0.36, 0.31, 0.24)), (1, (0.16, 0.13, 0.1))]))
    ctx.fill()
    R.sandbags(ctx, -40, W + 40, 700, rows=4, bw=64, bh=26, color=(0.62, 0.56, 0.44), seed=3)
    for lx in (330, 900, 1480):
        R.ladder(ctx, lx, 1060, 560, 50)
    # men waiting on the fire step: steel helmets, fixed bayonets
    for i in range(9):
        x = 60 + i * 210 + (hash01(i, 5) - 0.5) * 40
        if any(abs(x - lx - 25) < 60 for lx in (330, 900, 1480)):
            x += 70
        P.soldier(ctx, x, 1080, 380 + 20 * hash01(i, 6), 0.05 * math.sin(t + i), 1, (0.09, 0.085, 0.075),
                  pack=True, lean=4, helmet="brodie", bayonet=True, rifle_pose="slope", stride=0.1)
    # officer with whistle, raising it as the minutes run out
    ox = 1720
    P.soldier(ctx, ox, 1080, 400, 0.0, -1, (0.08, 0.075, 0.07), pack=False, lean=2, helmet="brodie", rifle=False,
              stride=0.1)
    up = ease_out(ramp(t, S.dur - 3.0, S.dur - 2.0))
    ctx.set_line_width(22)
    ctx.move_to(ox - 10, 1080 - 400 * 0.78)
    ctx.line_to(ox - 40 - 30 * up, 1080 - 400 * (0.62 + 0.28 * up))
    set_rgba(ctx, (0.08, 0.075, 0.07))
    ctx.stroke()
    ctx.restore()


# ---------------------------------------------------------------- 2. title
def title(ctx, S):
    C.intertitle(ctx, S, ["THE BATTLE", "OF THE SOMME", None, "1st July – 18th November, 1916"],
                 [120, 120, 0, 52], ["fell_sc", "fell_sc", "fell", "fell_i"], spacing=1.2)


# ---------------------------------------------------------------- 3. the Western Front (atlas map)
CITIES = [("PARIS", (2.35, 48.86)), ("LONDON", (-0.12, 51.5)), ("BRUSSELS", (4.35, 50.85)),
          ("VERDUN", (5.39, 49.16)), ("AMIENS", (2.3, 49.89)), ("REIMS", (4.03, 49.26)), ("YPRES", (2.88, 50.85))]


def _atlas(ctx, S, pr, front_progress=1.0, extra_cities=()):
    M.atlas_base(ctx, pr, S.t)
    for name, ll in (("FRANCE", (1.9, 47.6)), ("BELGIUM", (4.6, 50.35)), ("GERMANY", (7.6, 50.4)),
                     ("ENGLAND", (-1.6, 52.0)), ("NETHERLANDS", (5.6, 52.1)), ("SWITZERLAND", (7.7, 46.9))):
        x, y = pr.xy(*ll)
        draw_text(ctx, name, x, y, "fell_sc", 44, M.SEPIA, "cm", 0.8, 0.4)
    x, y = pr.xy(-0.6, 50.35)
    draw_text(ctx, "The Channel", x, y, "fell_i", 36, M.SEPIA, "cm", 0.9)
    M.trench_line(ctx, pr.arr(M.WESTERN_FRONT), front_progress, M.GERMAN, 7)
    for name, ll in CITIES + list(extra_cities):
        x, y = pr.xy(*ll)
        if -50 < x < W + 50 and -50 < y < H + 50:
            M.place(ctx, pr, ll, name.title(), size=32)


def western_front(ctx, S):
    t = S.t
    t_ch = S.at("stalemate", 1)
    k = ease_in_out(ramp(t, t_ch, t_ch + 3.0))
    pr = M.Proj(lerp(3.2, 2.9, k), lerp(49.4, 49.7, k), lerp(170, 300, k))
    _atlas(ctx, S, pr, ease_in_out(ramp(t, 0.3, 4.5)), [("CHANTILLY", (2.47, 49.19))])
    M.cartouche(ctx, "The Western Front", "Winter 1915–16", ramp(t, 0.2, 0.7))
    a = ramp(t, t_ch + 0.5, t_ch + 1.2)
    if a > 0:
        # the Somme sector: British north of the river, French astride it
        x, y = pr.xy(2.72, 50.05)
        ctx.arc(x, y, 95, 0, 6.283)
        ctx.set_line_width(4)
        ctx.set_dash([12, 8])
        set_rgba(ctx, M.INK, a)
        ctx.stroke()
        ctx.set_dash([])
        draw_text(ctx, "The Somme", x - 110, y + 10, "fell_i", 40, M.INK, "rb", a)
        EMarrow(ctx, [pr.xy(2.2, 50.2), pr.xy(2.45, 50.12), pr.xy(2.62, 50.07)], a, M.BRIT)
        EMarrow(ctx, [pr.xy(2.3, 49.75), pr.xy(2.55, 49.85), pr.xy(2.7, 49.93)], a, M.FRENCH)
        draw_text(ctx, "British", pr.xy(2.15, 50.25)[0], pr.xy(2.15, 50.25)[1], "fell_sc", 34, M.BRIT, "rb", a)
        draw_text(ctx, "French", pr.xy(2.25, 49.7)[0], pr.xy(2.25, 49.7)[1] + 30, "fell_sc", 34, M.FRENCH, "rb", a)
        C.plate(ctx, S, "Chantilly, December 1915", "The Allies agree a joint offensive for 1916", t_in=t_ch + 0.4)


def EMarrow(ctx, pts, a, color):
    from engine import maps as EM
    EM.arrow(ctx, pts, a, color, 12, 32, a)


# ---------------------------------------------------------------- 4. Verdun
def verdun(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.08, (20, 0), (-20, 10))
    A.sky(ctx, [(0, (0.12, 0.12, 0.14)), (0.7, (0.35, 0.33, 0.32)), (1, (0.6, 0.52, 0.45))], 700)
    for k in range(14):  # gun flashes along the heights
        tk = (k * 0.53) % 3.3 + 0.2 * k
        bx = 100 + (k * 173) % 1700
        A.flash(ctx, bx, 560 + (k % 3) * 30, t, tk, r=260, dur=0.6, color=(1, 0.75, 0.45))
    A.ridge(ctx, 221, 640, 110, (0.16, 0.15, 0.14), rough=0.5)
    # the ruined town and its cathedral's twin towers
    for i in range(18):
        x = 300 + i * 70
        h = 60 + 70 * hash01(i, 3)
        poly(ctx, [(x, 760), (x, 760 - h), (x + 20, 760 - h - 20 * hash01(i, 4)), (x + 55, 760 - h * 0.7), (x + 60, 760)])
        set_rgba(ctx, (0.05, 0.045, 0.04))
        ctx.fill()
    for tx in (900, 990):
        ctx.rectangle(tx, 480, 60, 290)
        ctx.fill()
        poly(ctx, [(tx - 6, 480), (tx + 30, 440), (tx + 66, 480)])
        ctx.fill()
    ctx.rectangle(0, 760, W, H)
    set_rgba(ctx, (0.04, 0.035, 0.03))
    ctx.fill()
    fl, _ = A.starshell(ctx, 1400, 120, t, 0.5, fall=12, drift=-5, life=10)
    A.smoke(ctx, 700, 700, t, seed=4, rate=6, life=8, rise=30, size=50, alpha=0.6, wind=10, color=(0.15, 0.14, 0.13))
    A.smoke(ctx, 1300, 700, t, seed=5, rate=6, life=8, rise=30, size=50, alpha=0.6, wind=10, color=(0.15, 0.14, 0.13))
    ctx.restore()
    C.plate(ctx, S, "Verdun, 21st February 1916", "Germany attacks the French army", t_in=0.4)


def verdun_map(ctx, S):
    t = S.t
    pr = M.Proj(3.9, 49.55, 330)
    _atlas(ctx, S, pr)
    # French divisions drawn away to Verdun
    for i in range(3):
        y0 = 49.55 + i * 0.25
        EMarrow(ctx, [pr.xy(2.95, y0 - 0.2), pr.xy(4.1, 49.35 + i * 0.05), pr.xy(5.15, 49.2)],
                ease_in_out(ramp(t, 0.4 + i * 0.4, 2.8 + i * 0.4)), M.FRENCH)
    x, y = pr.xy(5.39, 49.16)
    for k in range(8):
        R.shell_burst(ctx, x + 30 + (hash01(k, 1) - 0.5) * 120, y - 20 + (hash01(k, 2) - 0.5) * 60, t,
                      0.3 + k * 0.7, 0.25, seed=k)
    a = ramp(t, 2.0, 2.6)
    x, y = pr.xy(2.72, 50.04)
    ctx.arc(x, y, 80, 0, 6.283)
    ctx.set_line_width(5)
    set_rgba(ctx, M.BRIT, a)
    ctx.stroke()
    draw_text(ctx, "The Somme: now a mainly British battle", x - 100, y - 20, "fell_i", 38, M.BRIT, "rb", a)
    M.cartouche(ctx, "Verdun Draws in the French", None, ramp(t, 0.2, 0.7))


# ---------------------------------------------------------------- 5. recruiting poster
def poster(ctx, S):
    t = S.t
    cream = (0.93, 0.88, 0.74)
    red = (0.7, 0.12, 0.1)
    navy = (0.12, 0.15, 0.3)
    ctx.rectangle(0, 0, W, H)
    set_rgba(ctx, (0.25, 0.22, 0.18))
    ctx.fill()
    px, py, pw, ph = 460, 40, 1000, 1000
    ctx.save()
    camera(ctx, S, 1.0, 1.06, (0, 10), (0, -10))
    ctx.rectangle(px, py, pw, ph)
    set_rgba(ctx, cream)
    ctx.fill()
    ctx.rectangle(px + 30, py + 30, pw - 60, ph - 60)
    ctx.set_line_width(6)
    set_rgba(ctx, navy)
    ctx.stroke()
    draw_text(ctx, "YOUR KING & COUNTRY", W / 2, py + 170, "oldstd_b", 76, red, "cb", 1, 0.02)
    draw_text(ctx, "NEED YOU", W / 2, py + 290, "oldstd_b", 120, navy, "cb", 1, 0.04)
    # a column of volunteers in service caps
    ctx.save()
    ctx.rectangle(px + 40, py + 330, pw - 80, 470)
    ctx.clip()
    ctx.rectangle(px + 40, py + 700, pw - 80, 100)
    set_rgba(ctx, mix(cream, navy, 0.15))
    ctx.fill()
    R.marching_column(ctx, px - 160, py + 760, 12, 400, t, navy, spacing=150, speed=40, helmet="cap")
    ctx.restore()
    draw_text(ctx, "A CALL TO ARMS", W / 2, py + 880, "oldstd_b", 70, red, "cb", 1, 0.06)
    draw_text(ctx, "ENLIST TO-DAY · GOD SAVE THE KING", W / 2, py + 950, "oldstd", 40, navy, "cb", 1, 0.08)
    ctx.restore()
    C.plate(ctx, S, "Kitchener's Army", "Volunteers of 1914–15", t_in=0.8, y=900, x=60)


# ---------------------------------------------------------------- 6. a Pals battalion marches away
def _terrace(ctx, x0, x1, base, h, color, roof, seed=0):
    x = x0
    i = 0
    while x < x1:
        w = 150
        ctx.rectangle(x, base - h, w, h)
        set_rgba(ctx, mix(color, (0, 0, 0), 0.08 * (i % 2)))
        ctx.fill()
        poly(ctx, [(x - 4, base - h), (x + w + 4, base - h), (x + w - 10, base - h - 50), (x + 10, base - h - 50)])
        set_rgba(ctx, roof)
        ctx.fill()
        ctx.rectangle(x + w - 30, base - h - 80, 18, 40)
        ctx.fill()
        for (wx, wy) in ((x + 25, base - h + 30), (x + 90, base - h + 30), (x + 25, base - h * 0.45)):
            ctx.rectangle(wx, wy, 35, 45)
            set_rgba(ctx, (0.12, 0.11, 0.1))
            ctx.fill()
        ctx.rectangle(x + 95, base - 85, 30, 85)
        ctx.fill()
        x += w
        i += 1


def pals_march(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.06, (30, 0), (-30, 0))
    A.sky(ctx, [(0, (0.6, 0.6, 0.6)), (1, (0.88, 0.87, 0.84))], 700)
    # mill chimneys of a northern town
    for cx, ch in ((260, 520), (1500, 460), (1750, 380)):
        poly(ctx, [(cx - 22, 700), (cx - 12, 700 - ch), (cx + 12, 700 - ch), (cx + 22, 700)])
        set_rgba(ctx, (0.35, 0.33, 0.3))
        ctx.fill()
        A.smoke(ctx, cx, 700 - ch, t, seed=int(cx), rate=4, life=8, rise=20, size=16, alpha=0.4, wind=30,
                color=(0.4, 0.38, 0.35))
    _terrace(ctx, -60, W + 60, 760, 250, (0.45, 0.4, 0.36), (0.28, 0.27, 0.27))
    ctx.rectangle(0, 760, W, H)
    set_rgba(ctx, (0.5, 0.48, 0.44))
    ctx.fill()
    # the battalion: service caps, rifles at the slope
    R.marching_column(ctx, -500, 930, 16, 300, t, (0.12, 0.11, 0.1), spacing=130, speed=60, helmet="cap")
    # townspeople cheering them off
    P.crowd(ctx, -60, W + 60, 1110, 250, t, (0.15, 0.14, 0.13), seed=41, density=0.9, wave=1.0, rows=1)
    ctx.restore()
    C.plate(ctx, S, "The Pals Battalions", "Friends, neighbours and workmates who enlisted together", t_in=0.6)


# ---------------------------------------------------------------- 7. the bombardment
def guns(ctx, S):
    t = S.t
    t_count = S.at("bombardment", 1)
    ctx.save()
    camera(ctx, S, 1.02, 1.1, (0, 0), (-40, 10))
    A.sky(ctx, [(0, (0.12, 0.12, 0.12)), (0.8, (0.42, 0.4, 0.37)), (1, (0.62, 0.58, 0.52))], 720)
    for k in range(10):  # the horizon flickers with distant fire
        A.flash(ctx, 150 + k * 180, 700, t, (k * 0.37) % 2.0 + (k // 3) * 1.7, r=320, dur=0.5, color=(1, 0.8, 0.5))
    ctx.rectangle(0, 720, W, H)
    ctx.set_source(vgrad(ctx, 0, 720, 0, H, [(0, (0.2, 0.18, 0.15)), (1, (0.07, 0.06, 0.05))]))
    ctx.fill()
    pieces = [(260, 860, 190, "how", 0.3), (720, 900, 170, "fg", 1.0), (1160, 870, 200, "how", 1.7),
              (1600, 910, 160, "fg", 2.3)]
    for i, (x, y, s, kind, t0) in enumerate(pieces):
        period = 2.8
        fire_t = t0 + math.floor(max(0, t - t0) / period) * period if t >= t0 else t0
        rec = max(0, 1 - (t - fire_t) / 0.4) if t >= fire_t else 0
        if kind == "how":
            tip = R.howitzer(ctx, x, y, s, 1, rec, (0.06, 0.055, 0.05))
        else:
            tip = R.field_gun(ctx, x, y, s, 1, rec, (0.06, 0.055, 0.05))
        R.muzzle_flash(ctx, tip, t, fire_t, s / 170)
        for j in range(3):  # gun crew
            P.soldier(ctx, x - s * (0.9 + j * 0.35), y, s * 0.95, 0.4 * j, 1, (0.05, 0.045, 0.04), pack=False,
                      lean=12, rifle=False, helmet="brodie", stride=0.2)
    ctx.restore()
    a = ramp(t, t_count, t_count + 0.5)
    if a > 0:
        n = int(1_500_000 * ease_out(ramp(t, t_count, t_count + 3.5)))
        draw_text(ctx, f"{n:,}", W / 2, 260, "oldstd_b", 150, (0.96, 0.94, 0.88), "cb", a, 0.02,
                  shadow=(4, 5, 0.8))
        draw_text(ctx, "shells in seven days", W / 2, 340, "fell_i", 56, (0.92, 0.9, 0.84), "cb", a,
                  shadow=(3, 3, 0.8))
    C.plate(ctx, S, "24th June – 1st July 1916", "The preliminary bombardment", t_in=0.5,
            t_out=t_count - 0.1)


# ---------------------------------------------------------------- 8. why it failed: section drawing
def dugout_section(ctx, S):
    t = S.t
    M.paper(ctx, 12)
    ink = M.INK
    gy = 420
    ctx.save()
    camera(ctx, S, 1.0, 1.05, (0, 0), (0, -20))
    # chalk and earth in section
    ctx.rectangle(0, gy, W, H - gy)
    set_rgba(ctx, (0.84, 0.8, 0.68))
    ctx.fill()
    ctx.set_line_width(1)
    for i in range(-H, W, 16):
        ctx.move_to(i, gy)
        ctx.line_to(i + (H - gy), H)
    set_rgba(ctx, ink, 0.18)
    ctx.stroke()
    ctx.move_to(0, gy)
    ctx.line_to(W, gy)
    ctx.set_line_width(3)
    set_rgba(ctx, ink)
    ctx.stroke()
    # German front trench, parapet and wire
    tx = 640
    ctx.rectangle(tx, gy, 120, 170)
    set_rgba(ctx, (0.9, 0.86, 0.75))
    ctx.fill()
    ctx.rectangle(tx, gy, 120, 170)
    ctx.set_line_width(3)
    set_rgba(ctx, ink)
    ctx.stroke()
    R.sandbags(ctx, tx - 110, tx, gy, rows=2, bw=36, bh=16, color=(0.8, 0.75, 0.62), seed=2, jitter=0.4)
    R.wire(ctx, 140, 520, gy, 55, seed=4, color=ink)
    # stair and deep dugout
    ctx.move_to(tx + 120, gy + 170)
    ctx.line_to(tx + 360, gy + 440)
    ctx.line_to(tx + 420, gy + 440)
    ctx.line_to(tx + 180, gy + 170)
    ctx.close_path()
    set_rgba(ctx, (0.9, 0.86, 0.75))
    ctx.fill_preserve()
    ctx.set_line_width(2.5)
    set_rgba(ctx, ink)
    ctx.stroke()
    for k in range(12):
        u = k / 12
        ctx.move_to(lerp(tx + 120, tx + 360, u), lerp(gy + 170, gy + 440, u))
        ctx.line_to(lerp(tx + 180, tx + 420, u), lerp(gy + 170, gy + 440, u))
    ctx.set_line_width(1.5)
    ctx.stroke()
    cx0, cy0, cw, chh = tx + 330, gy + 440, 560, 160
    ctx.rectangle(cx0, cy0, cw, chh)
    set_rgba(ctx, (0.92, 0.88, 0.78))
    ctx.fill_preserve()
    ctx.set_line_width(3)
    set_rgba(ctx, ink)
    ctx.stroke()
    for bx in range(int(cx0 + 20), int(cx0 + cw), 90):   # timber frames
        ctx.move_to(bx, cy0)
        ctx.line_to(bx, cy0 + chh)
    ctx.set_line_width(2)
    ctx.stroke()
    for i in range(5):  # the garrison waits it out
        P.soldier(ctx, cx0 + 70 + i * 95, cy0 + chh - 4, 120, 0.2 * i, -1 if i % 2 else 1, ink, pack=False,
                  lean=20, helmet="stahl", stride=0.05, rifle=i % 2 == 0)
    # the bombardment above: shrapnel airbursts and duds
    for k in range(7):
        R.shrapnel_burst(ctx, 200 + k * 190, 230 + (k % 3) * 40, t, 0.2 + k * 0.45, 0.9, seed=k)
    for dx in (260, 430, 1250):
        ctx.save()
        ctx.translate(dx, gy - 4)
        ctx.rotate(0.6)
        ctx.rectangle(-8, -30, 16, 44)
        ctx.arc(0, -30, 8, math.pi, 0)
        set_rgba(ctx, ink)
        ctx.fill()
        ctx.restore()
    ctx.restore()

    def note(text, x, y, lx, ly, t0):
        a = ramp(t, t0, t0 + 0.5)
        if a <= 0:
            return
        draw_text(ctx, text, x, y, "fell_i", 38, ink, "lb", a)
        ctx.move_to(x + 10, y + 10)
        ctx.line_to(lx, ly)
        ctx.set_line_width(1.5)
        set_rgba(ctx, ink, a)
        ctx.stroke()

    t1 = S.at("bombardment", 2)
    t2 = S.at("bombardment", 3)
    note("Shrapnel: little use against wire or dugouts", 1000, 150, 900, 250, t1 + 0.6)
    note("Up to a third of shells failed to explode", 90, 620, 260, 430, t1 + 2.2)
    note("Wire left largely uncut", 120, 760, 330, 450, t2 + 0.1)
    note("Deep dugouts in the chalk", 1320, 780, 1250, 900, t2 + 1.2)
    M.cartouche(ctx, "Section of a German Front Line", "Somme, June 1916 · schematic", ramp(t, 0.2, 0.7), x=60,
                y=40)
