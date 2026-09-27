"""Zero hour, the first day, attrition, tanks, mud, the cost and the legacy."""
import math

import cairo
import numpy as np

from engine import art as A
from engine import maps as EM
from engine import people as P
from engine.core import (H, W, clamp, draw_text, ease_in_out, ease_out, hash01, hexc, lerp, mix, poly, ramp,
                         radial_glow, set_rgba, text_width, vgrad)
from ww1 import art as R
from ww1 import cards as C
from ww1 import maps as M
from .common import camera, shake
from .part1 import _atlas


# ---------------------------------------------------------------- 9. the mines
def mines(ctx, S):
    t = S.t
    t1 = 0.6
    t2 = S.word("zero", 1, "more mines") - 0.05
    ctx.save()
    camera(ctx, S, 1.0, 1.06, (0, 0), (0, 10))
    shake(ctx, S, t1 + 0.1, 16, 1.4)
    shake(ctx, S, t2 + 0.3, 7, 1.0)
    hz = 600
    A.sky(ctx, [(0, (0.62, 0.62, 0.6)), (1, (0.93, 0.92, 0.88))], hz)
    A.clouds(ctx, t, 60, 330, (1, 1, 1), seed=301, speed=5, lo=0.52, hi=0.85, alpha=0.5)
    # distant ridge towards La Boisselle: the second, greater eruption
    A.ridge(ctx, 302, hz - 20, 50, (0.6, 0.58, 0.54), rough=0.4)
    R.mine(ctx, 380, hz - 40, t, t2, size=0.45, seed=7)
    # Hawthorn Ridge and the German line along its crest
    prof = A.ridge(ctx, 303, hz + 60, 120, (0.42, 0.39, 0.33), x0=-60, x1=W + 60, rough=0.35,
                   shape=lambda u: 0.4 + 0.6 * math.sin(u * math.pi) ** 1.5, top_color=(0.55, 0.52, 0.45))
    for k in range(46):   # the German front line: white chalk spoil thrown up along the crest
        x = 260 + k * 30
        yy = prof[int(clamp((x + 60) / (W + 120), 0, 0.999) * len(prof))][1] + 6
        ctx.save()
        ctx.translate(x, yy)
        ctx.scale(1, 0.3)
        ctx.arc(0, 0, 18 + 8 * hash01(k, 1), math.pi, 2 * math.pi)
        ctx.restore()
        set_rgba(ctx, (0.9, 0.88, 0.82), 0.9)
        ctx.fill()
    R.mine(ctx, 1080, hz - 40, t, t1, size=0.9, seed=3)
    R.cratered_ground(ctx, 820, t, (0.33, 0.3, 0.25), seed=21, height=30, craters=10)
    R.wire(ctx, -20, W + 20, 900, 60, seed=6)
    A.haze(ctx, hz - 40, hz + 140, (0.9, 0.89, 0.85), 0.35)
    ctx.restore()
    C.clock_text(ctx, S, "7.20 a.m.", 0.2, t2 - 0.4)
    C.clock_text(ctx, S, "7.28 a.m.", t2 - 0.2, S.dur)
    C.plate(ctx, S, "Hawthorn Ridge", "The mine is blown ten minutes before zero hour", t_in=1.4, t_out=t2 - 0.3)
    C.plate(ctx, S, "Lochnagar, La Boisselle", "The largest of the mines", t_in=S.word("zero", 1, "Lochnagar"))


# ---------------------------------------------------------------- 10. over the top
def over_the_top(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.06, 1.0, (0, -20), (0, 10))
    hz = 480
    A.sky(ctx, [(0, (0.6, 0.6, 0.58)), (1, (0.9, 0.89, 0.85))], hz)
    # German parapet on the far rise, machine guns firing
    R.cratered_ground(ctx, hz + 20, t, (0.45, 0.42, 0.36), seed=31, height=24, craters=0)
    for k in range(40):
        ctx.save()
        ctx.translate(900 + k * 26, hz + 10)
        ctx.scale(1, 0.3)
        ctx.arc(0, 0, 16, math.pi, 2 * math.pi)
        ctx.restore()
        set_rgba(ctx, (0.88, 0.86, 0.8), 0.9)
        ctx.fill()
    for k, mx in enumerate((1080, 1360, 1640)):
        f = 1 if int(t * 9 + k * 3) % 2 == 0 else 0
        if t > 1.0:
            radial_glow(ctx, mx, hz - 2, 26, (1, 0.95, 0.7), 0.9 * f)
    A.haze(ctx, hz - 30, hz + 90, (0.9, 0.89, 0.85), 0.35)
    # no man's land: craters, wire, shell bursts, smoke drifting across
    R.cratered_ground(ctx, 620, t, (0.36, 0.32, 0.26), seed=32, height=40, craters=14)
    R.wire(ctx, 700, W + 40, 640, 40, seed=9)
    for k in range(6):
        R.shell_burst(ctx, 500 + k * 240, 610 + (k % 2) * 40, t, 0.6 + k * 0.9, 0.7, seed=k + 20)
    # waves of infantry walking forward; some fall
    R.advancing_line(ctx, t, 640, 60, n=9, spacing=150, speed=34, h=150, color=(0.12, 0.11, 0.1), seed=3,
                     falls=[(2, 2.2), (5, 3.1), (7, 4.0), (1, 5.4)])
    R.advancing_line(ctx, max(0, t - 1.2), 760, -260, n=8, spacing=200, speed=34, h=210, color=(0.09, 0.085, 0.08),
                     seed=4, falls=[(3, 3.4), (6, 4.6)])
    # our own trench in the foreground: parapet and men going up the ladders
    R.sandbags(ctx, -40, W + 40, H + 10, rows=4, bw=90, bh=34, color=(0.5, 0.45, 0.35), seed=12)
    for i, lx in enumerate((200, 820, 1450)):
        R.ladder(ctx, lx, H + 40, 900, 60)
        u = ((t * 0.9 + i * 0.37) % 1.0)
        y = lerp(H + 260, 930, u)
        P.soldier(ctx, lx + 30 + u * 60, y, 320, u * 4, 1, (0.07, 0.065, 0.06), pack=True, lean=24, helmet="brodie",
                  bayonet=True, rifle_pose="slope", stride=0.6)
    ctx.restore()
    C.clock_text(ctx, S, "7.30 a.m.", 0.2, S.dur - 0.3)


# ---------------------------------------------------------------- 11-12. two battalions (intertitles)
def card_accrington(ctx, S):
    C.intertitle(ctx, S, ["SERRE", None, "11th Battalion, East Lancashire Regiment", "— “the Accrington Pals” —",
                          "About 720 went forward.", "585 were killed or wounded", "in about half an hour."],
                 [90, 0, 48, 44, 56, 56, 56], ["fell_sc", "fell", "fell", "fell_i", "fell", "fell", "fell"], spacing=1.3)


def card_newfoundland(ctx, S):
    C.intertitle(ctx, S, ["BEAUMONT-HAMEL", None, "1st Newfoundland Regiment", "801 went forward.",
                          "68 answered the next roll call."],
                 [90, 0, 50, 60, 60], ["fell_sc", "fell", "fell", "fell", "fell"], spacing=1.35)


# ---------------------------------------------------------------- 13. first day on the map
FIRST_DAY_VILLAGES = ["GOMMECOURT", "SERRE", "BEAUMONT-HAMEL", "THIEPVAL", "LA BOISSELLE", "FRICOURT", "MAMETZ",
                      "MONTAUBAN", "MARICOURT", "ALBERT", "POZIÈRES", "CURLU", "FRISE", "HÉBUTERNE", "CONTALMAISON",
                      "LONGUEVAL", "BAPAUME", "PÉRONNE", "BRAY", "DOMPIERRE"]


def first_day_map(ctx, S):
    t = S.t
    t_toll = S.at("slaughter", 3)
    pr = M.Proj(2.745, 50.02, lerp(5200, 5500, S.u))
    M.trench_base(ctx, pr, t, villages=FIRST_DAY_VILLAGES)
    M.front_band(ctx, pr, M.LINE_JUL1)
    # gains of 1 July: the southern flank and the French astride the river
    south = [(2.72, 49.99), (2.745, 49.99), (2.77, 49.992), (2.79, 49.99), (2.805, 49.975), (2.808, 49.955),
             (2.8, 49.935), (2.79, 49.915)]
    south_after = [(2.722, 49.997), (2.748, 50.004), (2.775, 50.012), (2.795, 50.005), (2.822, 49.985),
                   (2.84, 49.955), (2.83, 49.93), (2.8, 49.915)]
    a = ramp(t, 1.0, 2.0)
    M.gained_ground(ctx, pr, south, south_after, M.BRIT, 0.45 * a)
    # attacks all along the front: success in the south, repulse in the north
    attacks = [((2.646, 50.1), (2.667, 50.1), False), ((2.644, 50.08), (2.662, 50.078), False),
               ((2.668, 50.052), (2.69, 50.066), False), ((2.68, 50.03), (2.702, 50.027), False),
               ((2.735, 49.985), (2.746, 50.0), True), ((2.77, 49.985), (2.78, 50.006), True),
               ((2.8, 49.95), (2.83, 49.955), True), ((2.79, 49.92), (2.82, 49.925), True)]
    for i, (p0, p1, ok) in enumerate(attacks):
        prog = ease_in_out(ramp(t, 0.2 + i * 0.15, 1.6 + i * 0.15))
        col = M.FRENCH if p0[1] < 49.96 else M.BRIT
        pts = [pr.xy(*p0), pr.xy(*p1)] if ok else [pr.xy(*p0), pr.xy(lerp(p0[0], p1[0], 0.45), lerp(p0[1], p1[1], 0.45))]
        EM.arrow(ctx, pts, prog, col, 11, 30)
        if not ok and prog >= 1:
            x, y = pts[-1]
            ctx.set_line_width(6)
            for d in (-1, 1):
                ctx.move_to(x + 22, y - 22 * d)
                ctx.line_to(x + 50, y + 22 * d)
            set_rgba(ctx, M.GERMAN)
            ctx.stroke()
    M.legend(ctx, 1460, 80, [("British front", M.BRIT), ("German trenches", M.GERMAN), ("French", M.FRENCH)],
             ramp(t, 0.3, 0.8))
    M.cartouche(ctx, "1st July 1916", "Gains in the south; repulse in the north", ramp(t, 0.2, 0.7))
    a = ramp(t, t_toll, t_toll + 0.5)
    if a > 0:
        ctx.rectangle(0, 0, W, H)
        set_rgba(ctx, (0.05, 0.045, 0.04), 0.8 * a)
        ctx.fill()
        draw_text(ctx, "57,470", W / 2, 520, "oldstd_b", 190, (0.95, 0.93, 0.88), "cb", a)
        draw_text(ctx, "British casualties on the first day", W / 2, 610, "fell_i", 56, (0.9, 0.88, 0.82), "cb", a)
        a2 = ramp(t, t_toll + 2.0, t_toll + 2.5)
        draw_text(ctx, "19,240 killed", W / 2, 760, "oldstd_b", 110, (0.88, 0.2, 0.15), "cb", a2)


# ---------------------------------------------------------------- 14. attrition: the front creeps forward
ATTRITION_VILLAGES = ["THIEPVAL", "POZIÈRES", "CONTALMAISON", "BAZENTIN", "LONGUEVAL", "GUILLEMONT", "GINCHY",
                      "MONTAUBAN", "FRICOURT", "LA BOISSELLE", "MARTINPUICH", "FLERS", "COURCELETTE", "COMBLES",
                      "ALBERT", "BEAUMONT-HAMEL", "MAMETZ"]


def attrition_map(ctx, S):
    t = S.t
    t_baz = S.at("attrition", 1)
    pr = M.Proj(lerp(2.75, 2.77, S.u), 50.02, 7600)
    M.trench_base(ctx, pr, t, villages=ATTRITION_VILLAGES)
    k = ease_in_out(ramp(t, t_baz + 0.3, t_baz + 3.0))
    line = M.blend_lines(M.LINE_JUL1, M.LINE_JUL14, k)
    M.gained_ground(ctx, pr, M.LINE_JUL1, line, M.BRIT, 0.35)
    M.front_band(ctx, pr, line)
    a = ramp(t, t_baz + 0.6, t_baz + 1.2)
    x, y = pr.xy(2.775, 50.028)
    draw_text(ctx, "14th July: Bazentin Ridge", x - 60, y + 110, "fell_i", 40, M.BRIT, "cb", a)
    for name, (lo, la) in (("Delville Wood", M.P("DELVILLE WOOD")), ("High Wood", M.P("HIGH WOOD"))):
        x, y = pr.xy(lo, la)
        draw_text(ctx, name, x + 30, y - 30, "fell_i", 34, M.INK, "lb", ramp(t, t_baz + 1.5, t_baz + 2.0))
    M.cartouche(ctx, "July 1916", "The battle of attrition", ramp(t, 0.2, 0.7))


# ---------------------------------------------------------------- 15. Delville Wood
def delville(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.1, (0, 0), (-30, 10))
    A.sky(ctx, [(0, (0.35, 0.34, 0.33)), (1, (0.72, 0.7, 0.66))], 700)
    for i in range(22):  # the wood reduced to stumps
        x = -40 + i * 95 + (hash01(i, 1) - 0.5) * 50
        R.stump(ctx, x, 720 + hash01(i, 2) * 30, 160 + 260 * hash01(i, 3), (0.14, 0.13, 0.12), seed=i)
    A.haze(ctx, 500, 760, (0.7, 0.68, 0.64), 0.4)
    for k in range(7):
        R.shell_burst(ctx, 200 + k * 250, 700 + (k % 2) * 30, t, 0.2 + k * 0.8, 0.8, seed=k + 40)
    R.cratered_ground(ctx, 760, t, (0.27, 0.24, 0.2), seed=41, height=40, craters=16)
    for i in range(6):
        x = 200 + i * 290
        R.stump(ctx, x, 1000, 380 + 150 * hash01(i, 9), (0.06, 0.055, 0.05), seed=i + 30)
    for i, x in enumerate((420, 980, 1480)):  # men holding the line in shell holes
        P.soldier(ctx, x, 1010, 300, 0.5, 1 if i % 2 else -1, (0.06, 0.055, 0.05), pack=False, lean=38, helmet="brodie",
                  bayonet=True, stride=0.3)
    ctx.restore()
    C.plate(ctx, S, "Delville Wood, 15th–20th July", "The South African Brigade", t_in=0.4)


# ---------------------------------------------------------------- 16. Pozieres
def pozieres(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.05, 1.0, (30, 0), (-10, 0))
    A.sky(ctx, [(0, (0.5, 0.49, 0.46)), (1, (0.82, 0.8, 0.75))], 680)
    # the village pounded to brick-dust: broken walls and rubble
    for i in range(12):
        x = 60 + i * 160
        h = 60 + 170 * hash01(i, 5)
        w = 50 + 60 * hash01(i, 6)
        poly(ctx, [(x, 720), (x, 720 - h), (x + w * 0.3, 720 - h * 0.8), (x + w * 0.6, 720 - h * 0.95),
                   (x + w, 720 - h * 0.4), (x + w, 720)])
        set_rgba(ctx, (0.3, 0.27, 0.23))
        ctx.fill()
        for j in range(3):
            ctx.rectangle(x + 8 + j * w * 0.3, 720 - h * 0.6, 10, 16)
            set_rgba(ctx, (0.7, 0.68, 0.64))
            ctx.fill()
    R.cratered_ground(ctx, 740, t, (0.4, 0.34, 0.27), seed=51, height=60, craters=20, rim=(0.55, 0.48, 0.38))
    for k in range(8):
        R.shell_burst(ctx, 150 + k * 230, 740 + (k % 3) * 40, t, 0.3 + k * 0.6, 0.9, seed=k + 60)
    for i in range(5):
        x = 150 + i * 330 + t * 25
        P.soldier(ctx, x, 1000 - (i % 2) * 40, 270, t * 5 + i, 1, (0.08, 0.075, 0.07), pack=True, lean=26,
                  helmet="brodie", bayonet=True, rifle_pose="slope", stride=0.7)
    ctx.restore()
    C.plate(ctx, S, "Pozières, 23rd July – 3rd September", "Three Australian divisions", t_in=0.4)


# ---------------------------------------------------------------- 17. the tanks
def tanks(ctx, S):
    t = S.t
    t_num = S.at("tanks", 1)
    ctx.save()
    camera(ctx, S, 1.0, 1.08, (0, 0), (-40, 0))
    A.sky(ctx, [(0, (0.55, 0.55, 0.52)), (1, (0.86, 0.85, 0.8))], 620)
    # Flers on the skyline
    for i in range(10):
        x = 1100 + i * 80
        h = 40 + 60 * hash01(i, 7)
        w = 50 + 20 * hash01(i, 8)
        poly(ctx, [(x, 620), (x, 620 - h), (x + w * 0.25, 620 - h * 0.85), (x + w * 0.45, 620 - h),
                   (x + w * 0.7, 620 - h * 0.55), (x + w, 620 - h * 0.6), (x + w, 620)])
        set_rgba(ctx, (0.45, 0.43, 0.4))
        ctx.fill()
        ctx.rectangle(x + w * 0.2, 620 - h * 0.5, 8, 12)
        set_rgba(ctx, (0.8, 0.78, 0.72))
        ctx.fill()
    ctx.rectangle(1440, 470, 40, 150)
    ctx.fill()
    poly(ctx, [(1434, 470), (1460, 420), (1486, 470)])
    ctx.fill()
    R.cratered_ground(ctx, 640, t, (0.4, 0.36, 0.3), seed=61, height=40, craters=18)
    R.wire(ctx, 900, W + 40, 780, 50, seed=12)
    for k in range(5):
        R.shell_burst(ctx, 300 + k * 330, 660 + (k % 2) * 60, t, 0.5 + k * 1.1, 0.8, seed=k + 70)
    tx = lerp(300, 960, S.u)
    bob = math.sin(t * 2.2) * 6
    R.tank(ctx, tx, 860 + bob, 640, 1, t, (0.36, 0.33, 0.26), pitch=math.sin(t * 1.3) * 2.5)
    A.smoke(ctx, tx - 330, 700, t, seed=9, rate=6, life=4, rise=20, size=20, alpha=0.4, wind=-20,
            color=(0.3, 0.3, 0.3))
    for i in range(6):
        x = tx - 520 - i * 150
        P.soldier(ctx, x, 1010 - (i % 2) * 30, 250, t * 3 + i, 1, (0.08, 0.075, 0.07), pack=True, lean=16,
                  helmet="brodie", bayonet=True, rifle_pose="slope", stride=0.6)
    ctx.restore()
    C.plate(ctx, S, "Flers–Courcelette, 15th September 1916", "The first tanks in battle", t_in=0.4,
            t_out=t_num - 0.1)
    a = ramp(t, t_num, t_num + 0.4)
    if a > 0:
        rows = [("49", "tanks ready"), ("32", "reached the start"), ("18", "went into action")]
        for i, (n, lab) in enumerate(rows):
            ai = ramp(t, t_num + i * 1.1, t_num + i * 1.1 + 0.4)
            x = 380 + i * 500
            draw_text(ctx, n, x, 250, "oldstd_b", 130, (0.96, 0.94, 0.88), "cb", ai, shadow=(4, 5, 0.8))
            draw_text(ctx, lab, x, 320, "fell_i", 46, (0.95, 0.93, 0.87), "cb", ai, shadow=(3, 3, 0.8))


# ---------------------------------------------------------------- 18. Thiepval falls: front moves on
def thiepval_map(ctx, S):
    t = S.t
    pr = M.Proj(2.76, 50.04, 6200)
    M.trench_base(ctx, pr, t, villages=ATTRITION_VILLAGES + ["GRANDCOURT", "LE SARS", "GUEUDECOURT", "LESBŒUFS",
                                                             "MORVAL"])
    k = ease_in_out(ramp(t, 0.3, 3.0))
    line = M.blend_lines(M.LINE_JUL14, M.LINE_SEP30, k)
    M.gained_ground(ctx, pr, M.LINE_JUL1, line, M.BRIT, 0.35)
    M.front_band(ctx, pr, line)
    x, y = pr.p("THIEPVAL")
    a = ramp(t, 2.0, 2.5)
    ctx.arc(x, y, 50, 0, 6.283)
    ctx.set_line_width(5)
    set_rgba(ctx, M.BRIT, a)
    ctx.stroke()
    draw_text(ctx, "26th September", x + 60, y + 70, "fell_i", 40, M.BRIT, "lb", a)
    M.cartouche(ctx, "September 1916", "Thiepval falls at last", ramp(t, 0.2, 0.7))


# ---------------------------------------------------------------- 19. mud
def mud(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.08, (0, 10), (-30, 0))
    A.sky(ctx, [(0, (0.4, 0.41, 0.42)), (1, (0.7, 0.71, 0.7))], 600)
    A.clouds(ctx, t, 0, 400, (0.3, 0.31, 0.32), seed=401, speed=14, lo=0.35, hi=0.75, alpha=0.8)
    for i in range(9):
        R.stump(ctx, 100 + i * 220, 620, 100 + 160 * hash01(i, 4), (0.2, 0.2, 0.2), seed=i + 50)
    R.cratered_ground(ctx, 620, t, (0.3, 0.28, 0.25), seed=71, height=30, craters=22, mud=True, rim=(0.38, 0.35, 0.3))
    # a duckboard track across the mud
    for i in range(18):
        x = -40 + i * 120
        y = 880 + math.sin(i * 0.7) * 20
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(0.05 * math.sin(i))
        ctx.rectangle(0, 0, 112, 18)
        set_rgba(ctx, (0.35, 0.3, 0.24))
        ctx.fill()
        for j in range(6):
            ctx.rectangle(6 + j * 18, -2, 8, 22)
        set_rgba(ctx, (0.25, 0.21, 0.17))
        ctx.fill()
        ctx.restore()
    R.stretcher_party(ctx, lerp(1500, 1100, S.u), 890, 260, t)
    A.rain(ctx, t, 0.28, 360, angle=0.18, speed=1600)
    ctx.restore()
    C.plate(ctx, S, "Autumn 1916", "Rain turns the battlefield to mud", t_in=0.4)


# ---------------------------------------------------------------- 20. the end: November
def final_map(ctx, S):
    t = S.t
    t_end = S.word("mud", 2, "Five days")
    pr = M.Proj(2.77, 50.05, 5600)
    M.trench_base(ctx, pr, t, villages=ATTRITION_VILLAGES + ["GRANDCOURT", "LE SARS", "GUEUDECOURT", "LESBŒUFS",
                                                             "MORVAL", "SERRE", "BEAUCOURT", "SAILLY-SAILLISEL",
                                                             "LE TRANSLOY"])
    k = ease_in_out(ramp(t, 0.3, 2.6))
    line = M.blend_lines(M.LINE_SEP30, M.LINE_NOV18, k)
    M.gained_ground(ctx, pr, M.LINE_JUL1, line, M.BRIT, 0.35)
    M.front_band(ctx, pr, line)
    x, y = pr.p("BEAUMONT-HAMEL")
    a = ramp(t, 1.5, 2.0)
    ctx.arc(x, y, 45, 0, 6.283)
    ctx.set_line_width(5)
    set_rgba(ctx, M.BRIT, a)
    ctx.stroke()
    draw_text(ctx, "13th November", x - 50, y + 80, "fell_i", 38, M.BRIT, "cb", a)
    x, y = pr.p("SERRE")
    draw_text(ctx, "Serre: never taken", x + 40, y - 40, "fell_i", 34, M.GERMAN, "lb", ramp(t, 2.4, 2.9))
    # first snow over the map
    if t > t_end:
        A.snow(ctx, t, 0.8 * ramp(t, t_end, t_end + 1), 260, wind=30)
    M.cartouche(ctx, "18th November 1916", "The offensive is halted", ramp(t, t_end, t_end + 0.4))
    M.cartouche(ctx, "November 1916", "The Battle of the Ancre", ramp(t, 0.2, 0.7) * (1 - ramp(t, t_end - 0.3, t_end)))


# ---------------------------------------------------------------- 21. the cost
def cost_map(ctx, S):
    t = S.t
    pr = M.Proj(2.8, 50.02, 4200)
    M.trench_base(ctx, pr, t, villages=["ALBERT", "BAPAUME", "PÉRONNE", "THIEPVAL", "POZIÈRES", "FLERS", "COMBLES",
                                        "LE SARS", "SERRE", "BEAUMONT-HAMEL", "FRICOURT", "MARICOURT", "LE TRANSLOY",
                                        "SAILLY-SAILLISEL", "BOUCHAVESNES", "BIACHES"])
    M.gained_ground(ctx, pr, M.LINE_JUL1, M.LINE_NOV18, M.BRIT, 0.45 * ramp(t, 0.3, 1.2))
    M.front_band(ctx, pr, M.LINE_JUL1, alpha=0.35, british=False)
    M.front_band(ctx, pr, M.LINE_NOV18)
    draw_text(ctx, "141 days", W - 120, 180, "oldstd_b", 110, M.INK, "rb", ramp(t, 0.4, 1.0))
    draw_text(ctx, "ground won, 1st July – 18th November", W - 120, 240, "fell_i", 40, M.INK, "rb",
              ramp(t, 0.8, 1.4))


def card_cost(ctx, S):
    C.stat_card(ctx, S, [("c. 420,000", "British Empire"), ("c. 200,000", "French"), ("450,000+", "German")],
                title="Casualties: killed, wounded, missing and captured",
                t0s=[S.word("cost", 1, "The British") + 0.2, S.word("cost", 1, "the French"), S.word("cost", 1, "the Germans")])


# ---------------------------------------------------------------- 22. legacy
def card_debate(ctx, S):
    C.intertitle(ctx, S, ["Futile slaughter?", None, "Or the costly road to victory?"], [80, 0, 64],
                 ["fell_i", "fell", "fell_i"])


def card_quote(ctx, S):
    C.quote_card(ctx, S, ["The Somme was the muddy grave", "of the German field army."],
                 "Captain Hans von Hentig, German General Staff")


def hindenburg_map(ctx, S):
    t = S.t
    pr = M.Proj(3.0, 49.9, 800)
    _atlas(ctx, S, pr, 1.0, [("ARRAS", (2.78, 50.29)), ("ST QUENTIN", (3.29, 49.85)), ("SOISSONS", (3.33, 49.38)),
                             ("BAPAUME", (2.856, 50.102)), ("PÉRONNE", (2.928, 49.93))])
    M.trench_line(ctx, pr.arr(M.HINDENBURG_LINE), ease_in_out(ramp(t, 0.3, 2.0)), (0.1, 0.1, 0.1), 7)
    x, y = pr.xy(3.36, 49.62)
    draw_text(ctx, "Hindenburg Line", x + 30, y, "fell_i", 44, M.INK, "lb", ramp(t, 1.0, 1.5))
    for i in range(4):
        la = 50.15 - i * 0.2
        EM.arrow(ctx, [pr.xy(2.83, la), pr.xy(3.05, la - 0.06)], ease_in_out(ramp(t, 1.4 + i * 0.2, 2.6 + i * 0.2)),
                 M.GERMAN, 10, 28)
    M.cartouche(ctx, "February – March 1917", "The German army falls back", ramp(t, 0.2, 0.7))


def memorial(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.08, (0, 20), (0, 0))
    A.sky(ctx, [(0, hexc("4E6A8C")), (0.6, hexc("C9B39A")), (1, hexc("F0CFA0"))], 700)
    A.clouds(ctx, t, 80, 420, (1, 0.92, 0.85), seed=501, speed=4, lo=0.55, hi=0.85, alpha=0.6)
    A.sun(ctx, 1560, 690, 40, (1, 0.9, 0.7), glow=5)
    ctx.rectangle(0, 700, W, H)
    ctx.set_source(vgrad(ctx, 0, 700, 0, H, [(0, hexc("7D8A55")), (1, hexc("3D4A2A"))]))
    ctx.fill()
    R.thiepval_memorial(ctx, W / 2, 720, 260, t=t)
    # the Anglo-French cemetery in front: British headstones and French crosses
    for row in range(4):
        y = 800 + row * 60
        h = 30 + row * 12
        n = 16 + row * 2
        for i in range(n):
            x = W / 2 + (i - n / 2 + 0.5) * (70 + row * 18)
            if i % 2 == 0:
                R.headstone(ctx, x, y, h)
            else:
                P.cross(ctx, x, y, h * 1.1, (0.95, 0.95, 0.93))
    ctx.restore()
    C.plate(ctx, S, "The Thiepval Memorial", "72,000+ names of the missing", t_in=0.6)


def poppies(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.1, (0, 30), (0, 0))
    A.sky(ctx, [(0, hexc("6F8FB5")), (0.7, hexc("E8CFA4")), (1, hexc("F7DDAF"))], 640)
    A.sun(ctx, 1450, 620, 44, (1, 0.92, 0.72), glow=5)
    A.ridge(ctx, 511, 640, 40, (0.45, 0.5, 0.35), rough=0.4)
    R.thiepval_memorial(ctx, 700, 628, 60, t=t)
    ctx.rectangle(0, 640, W, H)
    ctx.set_source(vgrad(ctx, 0, 640, 0, H, [(0, hexc("A69A5A")), (1, hexc("5E6A32"))]))
    ctx.fill()
    A.ground_texture(ctx, 650, H, (0.3, 0.3, 0.2), seed=512, alpha=0.5, n=700, tuft=(0.45, 0.45, 0.25))
    R.poppies(ctx, -20, W + 20, 660, H + 40, t, n=420, seed=513)
    ctx.restore()


def card_end(ctx, S):
    C.intertitle(ctx, S, ["In memory of all who fell", "on the Somme, 1916.", None,
                          "Sources and further reading in the description.",
                          "Illustrations are artistic reconstructions."],
                 [64, 64, 0, 36, 32], ["fell_i", "fell_i", "fell", "fell", "fell"], fade_out=False)
