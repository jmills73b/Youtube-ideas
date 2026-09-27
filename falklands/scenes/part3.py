"""San Carlos, the land campaign, surrender, cost and legacy."""
import math

import cairo

from engine import art as A
from engine import maps as M
from engine import people as P
from engine import vessels as V
from engine.core import (H, W, clamp, draw_text, ease_in_out, ease_out, hash01, hexc, lerp, mix, poly, ramp,
                         radial_glow, set_rgba, smooth, text_width, vgrad)
from .common import (camera, date_stamp, lower_third, shake, teletext, title_text, tt_mosaic_islands)


# ---------------------------------------------------------------- 22. San Carlos landings map
def sancarlos_map(ctx, S):
    t = S.t
    m = M.FlatMap(lerp(-59.12, -59.08, S.u), -51.53, lerp(1500, 1650, ease_in_out(S.u)), W / 2, H / 2)
    m.draw_base(ctx, t, grid_step=0.1)
    names = [((-59.34, -51.62), "FALKLAND SOUND", -0.95, (0.85, 0.92, 1)), ((-59.6, -51.62), "WEST FALKLAND", 0, None),
             ((-58.85, -51.58), "EAST FALKLAND", 0, None)]
    for ll, text, rot, col in names:
        x, y = m.xy(*ll)
        a = ramp(t, 0.2, 0.6)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(rot)
        if col:
            M.label(ctx, text, 0, 0, 26, col, a, "cm", "cond", tracking=0.3)
        else:
            M.label(ctx, text, 0, 0, 34, (0.3, 0.26, 0.18), a, "cm", "oswald", tracking=0.18, shadow=None)
        ctx.restore()
    # ships in the anchorage
    for i, (lo, la, hd) in enumerate(((-59.06, -51.51, 2.0), (-59.05, -51.525, 1.9), (-59.075, -51.5, 2.2),
                                      (-59.1, -51.485, 2.4), (-59.14, -51.47, 2.6))):
        x, y = m.xy(lo, la)
        M.ship_icon(ctx, x, y, hd, 15, M.BRIT, ramp(t, 0.6 + i * 0.15, 0.9 + i * 0.15))
    beaches = [("port_san_carlos", "PORT SAN CARLOS", (-59.25, -51.4), 26, -26),
               ("san_carlos", "SAN CARLOS", (-59.22, -51.43), 26, 20),
               ("ajax_bay", "AJAX BAY", (-59.2, -51.44), -26, 30)]
    for i, (key, name, src, dx, dy) in enumerate(beaches):
        x, y = m.pxy(key)
        pts = [m.xy(-59.13, -51.3), m.xy(-59.17, -51.39), m.xy(-59.13, -51.46), (x, y)]
        M.arrow(ctx, pts, ease_in_out(ramp(t, 0.8 + i * 0.4, 2.8 + i * 0.4)), M.BRIT, 11, 28)
        M.label(ctx, name, x + dx, y + dy, 24, alpha=ramp(t, 2.4 + i * 0.3, 2.8 + i * 0.3),
                anchor="lm" if dx > 0 else "rm", box=True)
    M.legend(ctx, [("BRITISH FORCES", M.BRIT)], 1480, 90, ramp(t, 0.6, 1.0))
    M.news_caption(ctx, "21 MAY 1982", "3 Commando Brigade lands at San Carlos", ramp(t, 0.2, 0.7))


# ---------------------------------------------------------------- 23. Bomb Alley
def _jet_pass(ctx, t, t0, y, kind="skyhawk", n=2, dur=1.5, bomb_to=None, color=(0.16, 0.17, 0.15)):
    """Low-level pass left to right; returns lead jet position or None."""
    a = t - t0
    lead = None
    for k in range(n):
        u = (a - k * 0.35) / dur
        if not 0 <= u <= 1:
            continue
        x = lerp(-300, W + 300, u)
        yy = y + k * 40 + math.sin(u * 6) * 4
        V.jet(ctx, kind, x, yy, 170 - k * 20, 1, color, (0.7, 0.7, 0.65), pitch=-3)
        if k == 0:
            lead = (x, yy)
    if bomb_to is not None:
        rel = t0 + dur * 0.38
        bu = (t - rel) / 0.6
        if 0 <= bu <= 1:
            bx = lerp(lerp(-300, W + 300, 0.38) + 60, bomb_to[0], bu)
            by = lerp(y + 20, bomb_to[1], bu * bu)
            ctx.save()
            ctx.translate(bx, by)
            ctx.rotate(0.4 + bu)
            ctx.scale(14, 5)
            ctx.arc(0, 0, 1, 0, 6.283)
            ctx.restore()
            ctx.set_source_rgb(0.08, 0.08, 0.08)
            ctx.fill()
    return lead


def bomb_alley(ctx, S):
    t = S.t
    passes = [0.5, 3.6, 6.8]
    hit_t = passes[2] + 1.0
    ctx.save()
    camera(ctx, S, 1.0, 1.08, (0, 0), (-20, 10))
    shake(ctx, S, hit_t, 12, 1.0)
    for p in passes[:2]:
        shake(ctx, S, p + 1.0, 5, 0.6)
    hz = 540
    A.sky(ctx, [(0, hexc("6D7780")), (1, hexc("B9BDB8"))], hz)
    A.clouds(ctx, t, 30, 360, (0.85, 0.86, 0.86), seed=111, speed=9, lo=0.45, hi=0.8, alpha=0.75)
    A.ridge(ctx, 112, hz + 5, 150, (0.38, 0.4, 0.34), x0=-50, x1=1000, rough=0.45, top_color=(0.52, 0.53, 0.45),
            shape=lambda u: math.sin(min(1.0, (1 - u) * 1.3) * math.pi / 2))
    A.ridge(ctx, 113, hz + 5, 120, (0.34, 0.36, 0.3), x0=900, x1=W + 60, rough=0.45, top_color=(0.5, 0.5, 0.42),
            shape=lambda u: math.sin(min(1.0, u * 1.3) * math.pi / 2))
    A.sea(ctx, t, hz, hexc("6E7A74"), hexc("26302D"), seed=114, strokes=450, hi=(1, 1, 1), hi_alpha=0.16)
    V.ship(ctx, "canberra", 330, 575, 420, 1, (0.9, 0.9, 0.88), light=(1, 1, 1), upper_color=(0.93, 0.93, 0.9))
    V.ship(ctx, "galahad", 1450, 568, 250, -1, hexc("4A5156"), light=(0.9, 0.9, 0.9))
    fx_, fy_, L = 920, 760, 720
    V.wake(ctx, fx_, fy_, L, 1, t, 0.3)
    V.ship(ctx, "type21", fx_, fy_, L, 1, hexc("3D4448"), light=(0.9, 0.92, 0.95), list_deg=ramp(t, hit_t, S.dur) * 4)
    # Rapier trail from the hillside
    ru = ramp(t, passes[1] + 0.1, passes[1] + 1.0)
    if 0 < ru < 1 or (t > passes[1] + 1.0 and t < passes[1] + 3.0):
        ctx.move_to(260, hz - 60)
        ctx.curve_to(420, hz - 200, 700, hz - 190, lerp(260, 900, ru), lerp(hz - 60, hz - 120, ru))
        ctx.set_line_width(4)
        ctx.set_source_rgba(0.95, 0.95, 0.95, 0.6 * (1 - ramp(t, passes[1] + 1.5, passes[1] + 3)))
        ctx.stroke()
    targets = [(1180, 720), (720, 735), (fx_ - L * 0.05, fy_ - 30)]
    for i, p in enumerate(passes):
        lead = _jet_pass(ctx, t, p, 400 + i * 20, "skyhawk", 2, 1.5, bomb_to=targets[i])
        if lead:
            A.tracer(ctx, (fx_ + L * 0.3, fy_ - L * 0.07), (lead[0] + 60, lead[1] + 20), t, p + 0.2, speed=1.6, n=6,
                     gap=0.08)
            A.tracer(ctx, (fx_ + L * 0.3, fy_ - L * 0.07), (lead[0] + 140, lead[1] + 10), t, p + 0.55, speed=1.6, n=6,
                     gap=0.08)
        if i < 2:
            A.splash(ctx, targets[i][0], targets[i][1], t, p + 0.95, h=260, w=80, dur=3.2)
    hx, hy = targets[2]
    k = A.flash(ctx, hx, hy, t, hit_t, r=380, dur=1.2)
    A.smoke(ctx, hx, hy - 10, t, seed=11, rate=8, life=10, rise=40, size=40, alpha=0.85, start=hit_t + 0.1,
            wind=28, color=(0.08, 0.08, 0.08))
    if t > hit_t:
        A.fire(ctx, hx, hy + 6, t, 70, 60, seed=5, intensity=min(1, (t - hit_t) * 2))
    ctx.restore()
    if k > 0:
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgba(1, 0.95, 0.85, k * 0.4)
        ctx.fill()
    lower_third(ctx, S, "'BOMB ALLEY'", "San Carlos Water · 21–25 May 1982", t_in=0.4,
                t_out=S.at("sancarlos", 2) - 0.1)
    # the losses
    t_l = S.at("sancarlos", 2)
    a = ramp(t, t_l, t_l + 0.4)
    if a > 0:
        losses = [("HMS ARDENT", "21 MAY"), ("HMS ANTELOPE", "24 MAY"), ("HMS COVENTRY", "25 MAY"),
                  ("ATLANTIC CONVEYOR", "25 MAY")]
        bx, by, bw = 1250, 90, 590
        ctx.rectangle(bx, by, bw, 110 + 66 * len(losses))
        ctx.set_source_rgba(0.04, 0.06, 0.12, 0.85 * a)
        ctx.fill()
        ctx.rectangle(bx, by, bw, 6)
        set_rgba(ctx, M.BRIT, a)
        ctx.fill()
        draw_text(ctx, "SHIPS LOST", bx + 30, by + 62, "oswald", 40, (1, 1, 1), "lb", a, 0.08)
        for i, (name, date) in enumerate(losses):
            ai = ramp(t, t_l + 0.3 + i * 0.7, t_l + 0.6 + i * 0.7)
            y = by + 124 + i * 66
            draw_text(ctx, name, bx + 30, y, "cond", 36, (1, 1, 1), "lb", ai, 0.04)
            draw_text(ctx, date, bx + bw - 30, y, "cond_r", 32, (0.8, 0.85, 0.95), "rb", ai, 0.04)


# ---------------------------------------------------------------- 24. Goose Green
def goose_map(ctx, S):
    t = S.t
    t_h = S.word("goosegreen", 0, "Their commander")
    m = M.FlatMap(-58.955, lerp(-51.775, -51.79, S.u), lerp(3000, 3300, ease_in_out(S.u)), W / 2, H / 2)
    m.draw_base(ctx, t, grid_step=0.02)
    for key, name, dx, dy in (("darwin", "DARWIN", 24, -6), ("goose_green", "GOOSE GREEN", 24, 10),
                              ("camilla_creek", "CAMILLA CREEK HOUSE", 20, -10)):
        x, y = m.pxy(key)
        M.marker(ctx, x, y, "square", (0.95, 0.95, 0.95), 9, ramp(t, 0.3, 0.7))
        M.label(ctx, name, x + dx, y + dy, 28, alpha=ramp(t, 0.3, 0.7), box=True)
    # Argentine defensive line across the isthmus
    a = ramp(t, 0.6, 1.0)
    p0, p1 = m.xy(-58.995, -51.8), m.xy(-58.945, -51.797)
    ctx.move_to(*p0)
    ctx.line_to(*p1)
    ctx.set_line_width(8)
    ctx.set_dash([4, 10])
    set_rgba(ctx, M.ARG, a)
    ctx.stroke()
    ctx.set_dash([])
    M.label(ctx, "ARGENTINE POSITIONS", (p0[0] + p1[0]) / 2 - 170, p0[1] + 34, 24, M.ARG, a, "cm", box=True)
    pts = [m.pxy("camilla_creek"), m.xy(-58.965, -51.775), m.xy(-58.965, -51.795), m.xy(-58.96, -51.81),
           m.pxy("goose_green")]
    M.arrow(ctx, pts, ease_in_out(ramp(t, 0.8, 5.0)), M.BRIT, 16, 40)
    x, y = m.pxy("camilla_creek")
    M.label(ctx, "2 PARA", x - 30, y + 40, 32, M.BRIT, ramp(t, 0.8, 1.2), "rm", "oswald", box=True)
    M.news_caption(ctx, "GOOSE GREEN", "28–29 May 1982", ramp(t, 0.2, 0.6))
    lower_third(ctx, S, "LT COL H. JONES VC", "Commanding officer, 2 Para · killed 28 May 1982", t_in=t_h + 0.2)


# ---------------------------------------------------------------- 25. the yomp
def yomp(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.02, 1.08, (20, 0), (-30, 0))
    hz = 560
    A.sky(ctx, [(0, hexc("59636C")), (0.8, hexc("A2A7A6")), (1, hexc("C4C2B6"))], hz)
    A.clouds(ctx, t, 20, 330, (0.35, 0.37, 0.4), seed=121, speed=16, lo=0.4, hi=0.75, alpha=0.8)
    A.clouds(ctx, t, 200, 520, (0.75, 0.76, 0.75), seed=122, speed=22, lo=0.5, hi=0.8, alpha=0.5)
    A.ridge(ctx, 123, hz, 150, (0.42, 0.45, 0.47), rough=0.5,
            shape=lambda u: 0.3 + 0.7 * math.exp(-((u - 0.7) / 0.18) ** 2))
    A.haze(ctx, hz - 120, hz + 40, (0.75, 0.76, 0.74), 0.4)
    A.ridge(ctx, 124, hz + 70, 90, (0.45, 0.42, 0.3), rough=0.45, top_color=(0.55, 0.52, 0.38))
    ctx.rectangle(0, hz + 60, W, H)
    ctx.set_source(vgrad(ctx, 0, hz + 60, 0, H, [(0, hexc("7C7350")), (1, hexc("3B3524"))]))
    ctx.fill()
    # stone run: river of grey boulders
    r_ = [(hash01(i, 1), hash01(i, 2), hash01(i, 3)) for i in range(140)]
    for u, v, s in r_:
        x = lerp(700, 1500, u) + v * 260 - 130
        y = lerp(hz + 80, H + 40, u ** 1.2)
        rr = (6 + 20 * s) * (0.4 + (y - hz) / (H - hz))
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(1.4, 0.7)
        ctx.arc(0, 0, rr, 0, 6.283)
        ctx.restore()
        ctx.set_source_rgb(0.42 + 0.1 * s, 0.42 + 0.1 * s, 0.4 + 0.1 * s)
        ctx.fill()
        ctx.save()
        ctx.translate(x, y + rr * 0.25)
        ctx.scale(1.4, 0.35)
        ctx.arc(0, 0, rr, 0, math.pi)
        ctx.restore()
        ctx.set_source_rgba(0.1, 0.1, 0.08, 0.5)
        ctx.fill()
    A.ground_texture(ctx, hz + 70, H, (0.3, 0.3, 0.2), seed=125, alpha=0.35, n=500, tuft=(0.3, 0.28, 0.15))
    # the column: mid-ground then foreground
    for row, (y, h, n, sp, col) in enumerate(((hz + 120, 120, 8, 22, (0.2, 0.21, 0.18)),
                                              (H - 60, 330, 4, 48, (0.07, 0.075, 0.06)))):
        for i in range(n):
            x = -200 + i * (W + 400) / n + t * sp + row * 170
            x = (x % (W + 400)) - 200
            phase = (t * sp + i * 97) / (h * 0.28) * math.pi
            P.soldier(ctx, x, y + (i % 2) * 8, h * (0.95 + 0.1 * hash01(i, row)), phase, 1, col, lean=20)
    A.rain(ctx, t, 0.14, 260, angle=0.3)
    ctx.restore()
    lower_third(ctx, S, "THE YOMP", "San Carlos to Stanley · some 50 miles on foot", t_in=0.6)


# ---------------------------------------------------------------- 26. Sir Galahad, Fitzroy
def galahad(ctx, S):
    t = S.t
    hit = 1.9
    ctx.save()
    camera(ctx, S, 1.0, 1.1, (0, 0), (-50, 20))
    shake(ctx, S, hit, 12, 1.0)
    hz = 560
    A.sky(ctx, [(0, hexc("5E666D")), (1, hexc("B4B6AF"))], hz)
    A.clouds(ctx, t, 20, 380, (0.8, 0.8, 0.8), seed=131, speed=8, lo=0.45, hi=0.8, alpha=0.7)
    A.ridge(ctx, 132, hz + 4, 140, (0.36, 0.37, 0.33), rough=0.5, top_color=(0.5, 0.5, 0.44))
    A.sea(ctx, t, hz, hexc("717B78"), hexc("2A3331"), seed=133, strokes=420, hi=(1, 1, 1), hi_alpha=0.16)
    V.ship(ctx, "galahad", 1560, 590, 330, -1, hexc("4E5559"), light=(0.9, 0.9, 0.9))
    A.smoke(ctx, 1520, 540, t, seed=3, rate=3, life=10, rise=24, size=22, alpha=0.45, wind=20)
    gx, gy, L = 760, 740, 820
    V.ship(ctx, "galahad", gx, gy, L, 1, hexc("3C4246"), light=(0.9, 0.9, 0.9))
    for k, (dx, dy) in enumerate(((-0.12, 0.12), (0.05, 0.08))):
        px, py = gx + dx * L, gy - dy * L
        if k == 0:
            A.flash(ctx, px, py, t, hit, r=420, dur=1.3)
        A.smoke(ctx, px, py, t, seed=20 + k, rate=24, life=14, rise=55, size=34, alpha=0.55, start=hit + 0.05 + k * 0.4,
                wind=32, color=(0.05, 0.05, 0.05), grow=3.8, spread=2.2)
        if t > hit:
            A.fire(ctx, px, py + 10, t, 110, 110, seed=k, intensity=min(1, (t - hit) * 1.5))
    # life rafts
    for k in range(7):
        rx = gx - 300 + k * 90 + math.sin(t * 0.7 + k) * 6 + (t - hit) * 6 * (k % 2)
        ry = gy + 50 + (k % 3) * 22
        if t > hit + 1.0 + k * 0.4:
            ctx.save()
            ctx.translate(rx, ry)
            ctx.scale(1.0, 0.45)
            ctx.arc(0, 0, 22, 0, 6.283)
            ctx.restore()
            ctx.set_source_rgb(0.95, 0.45, 0.1)
            ctx.fill()
    # Sea Kings hovering in the smoke, blowing rafts clear
    for k, (x0, y0) in enumerate(((1120, 480), (300, 560))):
        if t > hit + 1.0:
            hx = x0 + math.sin(t * 0.5 + k) * 20
            hy = y0 + math.sin(t * 1.3 + k) * 8
            V.helicopter(ctx, "seaking", hx, hy, 220 - k * 30, -1 if k == 0 else 1, t, hexc("262D30"))
    _jet_pass(ctx, t, 0.2, 380, "skyhawk", 3, 1.4, color=(0.18, 0.19, 0.17))
    ctx.restore()
    lower_third(ctx, S, "RFA SIR GALAHAD", "Fitzroy · 8 June 1982", t_in=hit + 1.2)


# ---------------------------------------------------------------- 27. night battle in the mountains
def night_battle(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.1, (0, 0), (-40, 20))
    A.sky(ctx, [(0, hexc("020308")), (1, hexc("141C2C"))], H)
    A.stars(ctx, 200, seed=41, alpha=0.5, y1=500, t=t)
    l1, p1 = A.starshell(ctx, 700, 80, t, -2.0, fall=14, drift=8, life=14)
    l2, p2 = A.starshell(ctx, 1400, 40, t, 1.5, fall=12, drift=-6, life=14)
    lit = min(1, l1 + l2)
    # Tumbledown: jagged rock ridge, top edge caught by the flare light
    ridge_col = mix((0.02, 0.025, 0.035), (0.1, 0.1, 0.1), lit)
    top_col = mix((0.05, 0.06, 0.08), (0.55, 0.5, 0.42), lit)
    A.ridge(ctx, 141, 760, 360, ridge_col, rough=0.58, crags=30, crag_seed=5, top_color=top_col,
            shape=lambda u: 0.45 + 0.55 * math.sin(u * math.pi) ** 0.6)
    for k in range(6):  # shell bursts on the ridge
        bt = 0.4 + k * 0.9
        bx = 450 + hash01(k, 7) * 1000
        by = 470 + hash01(k, 8) * 110
        A.flash(ctx, bx, by, t, bt, r=170, dur=0.7, color=(1, 0.7, 0.4))
        A.smoke(ctx, bx, by, t, seed=k + 60, rate=3, life=4, rise=12, size=30, alpha=0.35, start=bt + 0.1,
                wind=10, color=(0.15, 0.14, 0.13))
    for i, (p0, p1_, t0, col) in enumerate((((1150, 470), (420, 900), 0.8, (1, 0.3, 0.1)),
                                            ((1320, 500), (700, 950), 2.2, (1, 0.3, 0.1)),
                                            ((350, 950), (1050, 480), 1.5, (1, 0.2, 0.15)),
                                            ((560, 1000), (1250, 460), 3.1, (1, 0.2, 0.15)))):
        A.tracer(ctx, p0, p1_, t, t0, speed=1.0, n=9, gap=0.06, color=col)
    # foreground slope in near-black, soldiers silhouetted against the lit ridge
    ctx.move_to(-20, 900)
    ctx.curve_to(500, 820, 1100, 760, W + 20, 700)
    ctx.line_to(W + 20, H + 20)
    ctx.line_to(-20, H + 20)
    ctx.close_path()
    set_rgba(ctx, (0.012, 0.012, 0.018))
    ctx.fill()
    for i in range(6):
        x = 120 + i * 250 + t * 26
        yb = 900 - (x / W) * 200 + 20
        P.soldier(ctx, x, yb, 230 - i * 6, t * 4.5 + i * 1.3, 1, (0.012, 0.012, 0.018), pack=False, lean=30,
                  stride=0.7)
    A.darken(ctx, 0.12 * (1 - lit))
    ctx.restore()
    date_stamp(ctx, S, "11-14 JUN 1982", t_in=0.3)


# ---------------------------------------------------------------- 28. the battle for Stanley (map)
def stanley_map(ctx, S):
    t = S.t
    t2 = S.word("mountains", 1, "then Tumbledown")
    m = M.FlatMap(lerp(-58.0, -57.97, S.u), -51.683, lerp(5000, 5300, ease_in_out(S.u)), W / 2, H / 2 + 20)
    m.draw_base(ctx, t, night=0.5, grid_step=0.02)
    peaks = [("mt_kent", "MT KENT"), ("mt_longdon", "MT LONGDON"), ("two_sisters", "TWO SISTERS"),
             ("mt_harriet", "MT HARRIET"), ("tumbledown", "TUMBLEDOWN"), ("wireless_ridge", "WIRELESS RIDGE"),
             ("mt_william", "MT WILLIAM")]
    for i, (key, name) in enumerate(peaks):
        x, y = m.pxy(key)
        a = ramp(t, 0.2 + i * 0.1, 0.5 + i * 0.1)
        M.marker(ctx, x, y, "peak", (0.85, 0.8, 0.7), 11, a)
        M.label(ctx, name, x, y + 34, 24, alpha=a, anchor="cm", box=True)
    x, y = m.pxy("stanley")
    M.marker(ctx, x, y, "star", (1, 0.85, 0.2), 14, ramp(t, 0.3, 0.6), t)
    M.label(ctx, "STANLEY", x, y + 44, 34, alpha=ramp(t, 0.3, 0.6), anchor="cm", font="oswald", box=True)
    night1 = [((-58.07, -51.64), "mt_longdon", "3 PARA"), ((-58.1, -51.662), "two_sisters", "45 CDO"),
              ((-58.08, -51.725), "mt_harriet", "42 CDO")]
    night2 = [((-57.985, -51.652), "wireless_ridge", "2 PARA"), ((-58.0, -51.692), "tumbledown", "SCOTS GDS"),
              ((-57.99, -51.712), "mt_william", "GURKHAS")]
    for group, t0 in ((night1, 0.6), (night2, t2)):
        for i, (src, key, unit) in enumerate(group):
            sx, sy = m.xy(*src)
            tx, ty = m.pxy(key)
            mx, my = (sx + tx) / 2, (sy + ty) / 2 - 20
            p = ease_in_out(ramp(t, t0 + i * 0.3, t0 + 1.8 + i * 0.3))
            M.arrow(ctx, [(sx, sy), (mx, my), (tx - (tx - sx) * 0.08, ty - (ty - sy) * 0.08)], p, M.BRIT, 11, 28)
            M.label(ctx, unit, sx - 8, sy - 26, 24, M.BRIT, ramp(t, t0 + i * 0.3, t0 + 0.4 + i * 0.3), "cm",
                    "oswald", box=True)
    M.news_caption(ctx, "11–12 JUNE", "First night: the outer ring", ramp(t, 0.2, 0.6) * (1 - ramp(t, t2 - 0.3, t2)))
    M.news_caption(ctx, "13–14 JUNE", "Second night: the inner ring", ramp(t, t2, t2 + 0.4))


# ---------------------------------------------------------------- 29. Stanley, 14 June
def stanley_town(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.08, (0, 0), (20, -10))
    hz = 520
    A.sky(ctx, [(0, hexc("7A8792")), (1, hexc("D2D3CC"))], hz)
    A.clouds(ctx, t, 20, 360, (0.95, 0.95, 0.95), seed=151, speed=7, lo=0.45, hi=0.8, alpha=0.7)
    A.ridge(ctx, 152, hz, 110, (0.55, 0.58, 0.6), rough=0.5, top_color=(0.9, 0.92, 0.94))
    A.sea(ctx, t, hz, hexc("7E8B8C"), hexc("4B5758"), seed=153, strokes=200, hi=(1, 1, 1), hi_alpha=0.15,
          y_end=640)
    # the town on the south shore
    ctx.rectangle(0, 620, W, H)
    ctx.set_source(vgrad(ctx, 0, 620, 0, H, [(0, hexc("7B7A5E")), (1, hexc("45432F"))]))
    ctx.fill()
    walls = [(0.93, 0.92, 0.88), (0.85, 0.83, 0.75), (0.9, 0.9, 0.9)]
    roofs = [hexc("A8322B"), hexc("3E6B4A"), hexc("35577E"), hexc("B8482E"), hexc("6A7070")]
    for i in range(16):
        x = -40 + i * 125 + (i % 3) * 14
        if 760 < x < 1180:
            continue
        w_ = 90 + (i % 3) * 16
        h_ = 60 + (i % 2) * 20
        P.house(ctx, x, 680 + (i % 2) * 18, w_, h_, walls[i % 3], roofs[i % 5], seed=i)
    P.cathedral(ctx, 830, 700, 160)
    for i, (x, y) in enumerate(((330, 600), (1320, 610), (1650, 620), (140, 612))):
        P.flagpole(ctx, "white", x, y + 80, 150, 70, t + i, amp=0.12)
    P.flagpole(ctx, "union", 1100, 700, 260, 150, t, raise_frac=ease_out(ramp(t, S.dur * 0.55, S.dur)), amp=0.1)
    # troops walking in, wearing berets
    for i in range(6):
        x = -100 + i * 150 + t * 40
        P.soldier(ctx, x, H - 30 - (i % 2) * 10, 300, (t * 40 + i * 70) / 84 * math.pi, 1, (0.1, 0.1, 0.08),
                  beret=True, lean=8, pack=False)
    A.snow(ctx, t, 0.4, 120, wind=30)
    ctx.restore()
    lower_third(ctx, S, "STANLEY, 14 JUNE 1982", "General Menéndez surrenders to Major General Moore", t_in=0.5)


# ---------------------------------------------------------------- 30. teletext: surrender
def teletext_surrender(ctx, S):
    lines = [
        (2, 0, "  FALKLANDS                              ", "yellow", "blue", True),
        (5, 1, "ARGENTINES", "white", None, True),
        (7, 1, "SURRENDER", "white", None, True),
        (10, 1, "White flags are flying over Port", "cyan", None, False),
        (11, 1, "Stanley, the Prime Minister has", "cyan", None, False),
        (12, 1, "told the House of Commons.", "cyan", None, False),
        (14, 1, "Gen Menendez has surrendered his", "white", None, False),
        (15, 1, "forces to Maj Gen Jeremy Moore.", "white", None, False),
        (17, 1, "The conflict has lasted 74 days.", "yellow", None, False),
        (24, 0, " Headlines ", "red", None, False),
        (24, 12, " Falklands ", "green", None, False),
        (24, 24, " Sport ", "yellow", None, False),
        (24, 32, " TV ", "cyan", None, False),
    ]
    teletext(ctx, S, 101, "Mon 14 Jun", lines, reveal=(0.1, 1.6), mosaic=tt_mosaic_islands(26, 4, 13, 5, "green"),
             clock0=22 * 3600 + 41 * 60 + 7)


# ---------------------------------------------------------------- 31. the cost
def casualties(ctx, S):
    t = S.t
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(vgrad(ctx, 0, 0, 0, H, [(0, hexc("0B0B0C")), (1, hexc("17161A"))]))
    ctx.fill()
    draw_text(ctx, "THE COST", W / 2, 230, "cond", 36, (0.7, 0.7, 0.72), "cb", ramp(t, 0.1, 0.6), 0.5)
    ctx.rectangle(W / 2 - 60, 262, 120, 3)
    ctx.set_source_rgba(0.75, 0.12, 0.12, ramp(t, 0.1, 0.6))
    ctx.fill()
    cols = [(255, "BRITISH", "Task Force personnel", S.word("legacy", 0, "two hundred")),
            (649, "ARGENTINE", "military personnel", S.word("legacy", 0, "six hundred")),
            (3, "FALKLAND ISLANDERS", "civilians killed in Stanley", S.word("legacy", 0, "three islanders"))]
    for i, (n, label, sub, t0) in enumerate(cols):
        x = W / 2 + (i - 1) * 560
        a = ramp(t, t0 - 0.2, t0 + 0.3)
        v = int(round(n * ease_out(ramp(t, t0 - 0.2, t0 + 1.4))))
        draw_text(ctx, f"{v}", x, 600, "serif_b", 190, (0.95, 0.94, 0.9), "cb", a)
        draw_text(ctx, label, x, 680, "cond", 38, (0.95, 0.94, 0.9), "cb", a, 0.2)
        draw_text(ctx, sub, x, 730, "serif_i", 28, (0.65, 0.65, 0.68), "cb", a)
    tt = cols[-1][3] + 1.5
    draw_text(ctx, "Many more were wounded on both sides.", W / 2, 900, "serif_i", 32, (0.6, 0.6, 0.62), "cb",
              ramp(t, tt, tt + 0.6))


# ---------------------------------------------------------------- 32. democracy returns
def democracy(ctx, S):
    t = S.t
    t2 = S.word("legacy", 1, "Within eighteen")
    ctx.save()
    camera(ctx, S, 1.0, 1.08, (0, 10), (0, -10))
    hz = 760
    A.sky(ctx, [(0, hexc("4A82BD")), (1, hexc("CADCEA"))], hz)
    A.clouds(ctx, t, 60, 360, (1, 1, 1), seed=161, speed=9, lo=0.52, hi=0.8, alpha=0.8)
    P.casa_rosada(ctx, 300, hz, 1320, 300, color=hexc("E3A89C"), shadow=hexc("A86E62"))
    P.flagpole(ctx, "argentina", W / 2, hz - 300 * 1.34, 150, 140, t)
    ctx.rectangle(0, hz, W, H - hz)
    ctx.set_source_rgb(0.28, 0.25, 0.22)
    ctx.fill()
    P.crowd(ctx, -60, W + 60, H + 30, 230, t, (0.12, 0.11, 0.11), seed=31, density=0.8, wave=0.8,
            flags="argentina", flag_every=6, rows=2)
    ctx.restore()
    lower_third(ctx, S, "17 JUNE 1982", "Galtieri is forced from office", t_in=0.3, t_out=t2 - 0.1, accent=M.ARG)
    lower_third(ctx, S, "10 DECEMBER 1983", "Raúl Alfonsín takes office as elected president", t_in=t2 + 0.2,
                accent=M.ARG)


# ---------------------------------------------------------------- 33. referendum and the claim
def referendum(ctx, S):
    t = S.t
    t_arg = S.word("legacy", 2, "Argentina still")
    m = M.FlatMap(-59.4, -51.75, lerp(330, 350, S.u), W / 2 - 330, H / 2 + 30)
    m.draw_base(ctx, t, grid_step=0.5)
    a = ramp(t, 0.3, 0.8)
    bx, by = 1180, 170
    ctx.rectangle(bx, by, 640, 430)
    ctx.set_source_rgba(0.04, 0.07, 0.15, 0.85 * a)
    ctx.fill()
    ctx.rectangle(bx, by, 640, 6)
    set_rgba(ctx, M.BRIT, a)
    ctx.fill()
    draw_text(ctx, "REFERENDUM · MARCH 2013", bx + 36, by + 64, "cond", 32, (0.75, 0.82, 0.95), "lb", a, 0.1)
    v = lerp(0, 99.8, ease_out(ramp(t, 0.5, 2.6)))
    draw_text(ctx, f"{v:.1f}%", bx + 36, by + 230, "oswald", 150, (1, 1, 1), "lb", a, 0.02)
    draw_text(ctx, "to remain a British Overseas Territory", bx + 36, by + 290, "cond_r", 32, (0.85, 0.88, 0.95),
              "lb", a)
    draw_text(ctx, "1,513 yes  ·  3 no", bx + 36, by + 350, "cond", 34, (1, 0.85, 0.3), "lb",
              ramp(t, 2.2, 2.8), 0.04)
    a2 = ramp(t, t_arg, t_arg + 0.5)
    if a2 > 0:
        bx2, by2 = 1180, 650
        ctx.rectangle(bx2, by2, 640, 230)
        ctx.set_source_rgba(0.04, 0.07, 0.15, 0.85 * a2)
        ctx.fill()
        ctx.rectangle(bx2, by2, 640, 6)
        set_rgba(ctx, M.ARG, a2)
        ctx.fill()
        draw_text(ctx, "ARGENTINA", bx2 + 36, by2 + 70, "oswald", 52, (1, 1, 1), "lb", a2, 0.06)
        draw_text(ctx, "maintains its claim to the", bx2 + 36, by2 + 130, "cond_r", 32, (0.85, 0.88, 0.95), "lb", a2)
        draw_text(ctx, "Islas Malvinas", bx2 + 36, by2 + 180, "serif_i", 40, M.ARG, "lb", a2)
        m.land_path(ctx, ("falklands",))
        ctx.set_line_width(4)
        ctx.set_source_rgba(*M.ARG, 0.8 * a2 * (0.6 + 0.4 * math.sin(t * 3)))
        ctx.stroke()
    M.news_caption(ctx, "THE ISLANDS TODAY", None, ramp(t, 0.2, 0.6))


# ---------------------------------------------------------------- 34. memorial at dawn
def memorial(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.12, (0, 20), (0, -10))
    hz = 600
    A.sky(ctx, [(0, hexc("2C3A5A")), (0.5, hexc("8B7A8C")), (0.85, hexc("E9A77A")), (1, hexc("F7D29A"))], hz)
    A.clouds(ctx, t, 150, 480, (0.95, 0.72, 0.62), seed=171, speed=4, lo=0.55, hi=0.85, alpha=0.6)
    A.sun(ctx, 1380, hz + 10 - ramp(t, 0, S.dur) * 40, 50, (1, 0.9, 0.7), glow=5)
    A.light_rays(ctx, 1380, hz - 20, t, (1, 0.85, 0.6), 0.07)
    A.sea(ctx, t, hz, hexc("C99472"), hexc("3B3A48"), seed=172, strokes=300, hi=(1, 0.9, 0.7), hi_alpha=0.3)
    A.reflection(ctx, 1380, hz, 220, (1, 0.85, 0.6), 0.4, t, rows=20)
    # hillside
    ctx.move_to(-20, 700)
    ctx.curve_to(400, 660, 900, 700, 1250, 860)
    ctx.curve_to(1450, 950, 1700, 1000, W + 20, 1010)
    ctx.line_to(W + 20, H + 20)
    ctx.line_to(-20, H + 20)
    ctx.close_path()
    ctx.set_source(vgrad(ctx, 0, 640, 0, H, [(0, hexc("4E4A3A")), (1, hexc("1C1A16"))]))
    ctx.fill()
    # rows of white crosses receding up the hillside, lit by the low sun
    for row in range(4, -1, -1):
        f = row / 4                  # 0 = front, 1 = back
        h = lerp(150, 34, f)
        gap = lerp(170, 52, f)
        y0 = lerp(1010, 730, f)
        x0 = lerp(-40, 40, f)
        x1 = lerp(1250, 820, f)
        n = int((x1 - x0) / gap)
        for i in range(n + 1):
            x = x0 + i * gap + (row % 2) * gap * 0.5
            y = y0 + (x - x0) * lerp(0.1, 0.12, f)
            ctx.save()
            ctx.translate(x + h * 0.25, y)
            ctx.scale(1.0, 0.25)
            ctx.arc(0, 0, h * 0.28, 0, 6.283)
            ctx.restore()
            ctx.set_source_rgba(0, 0, 0, 0.35)
            ctx.fill()
            P.cross(ctx, x, y, h, mix((0.93, 0.9, 0.85), (0.55, 0.5, 0.5), f * 0.5))
            ctx.rectangle(x + h * 0.02, y - h, h * 0.04, h)
            ctx.set_source_rgba(1, 0.72, 0.45, 0.45)
            ctx.fill()
    A.ground_texture(ctx, 700, H, (0.3, 0.3, 0.2), seed=173, alpha=0.3, n=300, tuft=(0.25, 0.22, 0.14), x1=1150)
    ctx.restore()


def end_card(ctx, S):
    t = S.t
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(vgrad(ctx, 0, 0, 0, H, [(0, hexc("07080C")), (1, hexc("11141C"))]))
    ctx.fill()
    a = ramp(t, 0.2, 1.2)
    draw_text(ctx, "In memory of all who died", W / 2, 400, "serif_i", 54, (0.9, 0.88, 0.84), "cb", a)
    draw_text(ctx, "2 APRIL – 14 JUNE 1982", W / 2, 470, "cond", 32, (0.65, 0.65, 0.7), "cb", a, 0.3)
    title_text(ctx, "THE FALKLANDS WAR", W / 2, 690, 90, ramp(t, 1.2, 2.2))
    draw_text(ctx, "Sources and further reading in the description", W / 2, 790, "cond_r", 30, (0.6, 0.62, 0.68),
              "cb", ramp(t, 1.8, 2.6), 0.04)
    draw_text(ctx, "Illustrations are artistic reconstructions", W / 2, 840, "cond_r", 26, (0.45, 0.47, 0.52),
              "cb", ramp(t, 1.8, 2.6), 0.04)
