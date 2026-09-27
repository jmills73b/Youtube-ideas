"""Invasion, the Task Force, first blows, Belgrano and Sheffield."""
import math

import cairo

from engine import art as A
from engine import maps as M
from engine import people as P
from engine import vessels as V
from engine.core import (H, W, clamp, draw_text, ease_in_out, ease_out, hash01, hexc, lerp, mix, poly, ramp,
                         radial_glow, set_rgba, smooth, vgrad)
from .common import (camera, date_stamp, lower_third, shake, teletext, tt_mosaic_islands)


# ---------------------------------------------------------------- 12. night landing (Operation Rosario)
def night_landing(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.1, (0, 0), (-40, 10))
    hz = 560
    A.sky(ctx, [(0, hexc("03060D")), (0.8, hexc("0D1626")), (1, hexc("1A2233"))], hz)
    A.stars(ctx, 220, seed=12, alpha=0.7, y1=hz, t=t)
    # distant Stanley on the hill, a few lights
    A.ridge(ctx, 61, hz + 4, 60, (0.04, 0.05, 0.08), x0=-50, x1=1300, rough=0.4)
    for k in range(14):
        lx, ly = 250 + k * 55 + hash01(k, 3) * 30, hz - 8 - hash01(k, 4) * 30
        radial_glow(ctx, lx, ly, 10, (1, 0.8, 0.45), 0.7 * (0.6 + 0.4 * math.sin(t * 3 + k)))
    fl, pos = A.starshell(ctx, 1150, 120, t, 0.3, fall=10, drift=6, life=12)
    fl2, _ = A.starshell(ctx, 650, 60, t, 2.4, fall=11, drift=-5, life=12)
    lit = max(fl, fl2)
    A.sea(ctx, t, hz, mix(hexc("0E1A2A"), hexc("5C5A50"), lit * 0.5), hexc("020406"), seed=13, strokes=500,
          hi=(1.0, 0.9, 0.7), hi_alpha=0.12 + 0.25 * lit)
    A.reflection(ctx, pos[0] if pos != (0, 0) else 1150, hz, 160, (1, 0.9, 0.7), 0.25 * lit, t)
    # amphibious tractors heading for the beach
    for k, (x0, y, L, sp) in enumerate(((620, 630, 170, 34), (330, 700, 240, 40), (-20, 800, 330, 46))):
        x = x0 + t * sp
        bob = math.sin(t * 2 + k) * 3
        V.wake(ctx, x, y + bob, L, 1, t, 0.35)
        V.amtrac(ctx, x, y + bob + L * 0.18, L, 1, mix((0.05, 0.06, 0.05), (0.3, 0.3, 0.24), lit * 0.8))
        radial_glow(ctx, x + L * 0.25, y + bob - L * 0.35, 8, (1, 0.9, 0.6), 0.5 * (0.5 + 0.5 * math.sin(t * 9 + k)))
    # beach
    ctx.move_to(W * 0.55, H + 10)
    ctx.curve_to(W * 0.7, 900, W * 0.85, 820, W + 20, 790)
    ctx.line_to(W + 20, H + 10)
    ctx.close_path()
    set_rgba(ctx, mix((0.04, 0.04, 0.04), (0.35, 0.32, 0.25), lit * 0.7))
    ctx.fill()
    A.tracer(ctx, (1760, 840), (900, 700), t, 3.0, speed=0.9, n=7, gap=0.07)
    A.tracer(ctx, (1700, 820), (820, 660), t, 4.6, speed=0.9, n=6, gap=0.08)
    A.darken(ctx, 0.25 * (1 - lit))
    ctx.restore()
    date_stamp(ctx, S, "02 APR 1982", t_in=0.3)
    lower_third(ctx, S, "OPERATION ROSARIO", "Argentine landings near Stanley", t_in=1.0, accent=M.ARG)


# ---------------------------------------------------------------- 13. invasion map
def invasion_map(ctx, S):
    t = S.t
    t_sg = S.at("invasion", 2)
    m = M.FlatMap(lerp(-57.84, -57.83, S.u), -51.7, lerp(4300, 4700, ease_in_out(S.u)), W / 2 - 60, H / 2)
    m.draw_base(ctx, t, night=0.55, grid_step=0.05)
    gh = m.pxy("govhouse")
    places = [((-57.922, -51.681), "MOODY BROOK", 18, -30), (M.PLACES["govhouse"], "GOVERNMENT HOUSE", 20, 36),
              ((-57.777, -51.686), "AIRPORT", 18, -30)]
    for ll, name, dx, dy in places:
        x, y = m.xy(*ll)
        M.marker(ctx, x, y, "square", M.BRIT, 9, ramp(t, 0.4, 0.8))
        M.label(ctx, name, x + dx, y + dy, 26, alpha=ramp(t, 0.4, 0.8), box=True)
    x, y = m.pxy("stanley")
    M.label(ctx, "STANLEY", x + 10, y + 70, 40, (1, 1, 1), ramp(t, 0.2, 0.6), "lm", "oswald", tracking=0.2)
    # Argentine commandos via Mullet Creek; marines via Yorke Bay
    a1 = [m.xy(-57.85, -51.78), m.xy(-57.87, -51.735), m.xy(-57.89, -51.71), m.xy(-57.915, -51.686)]
    a2 = [m.xy(-57.87, -51.735), m.xy(-57.866, -51.705), gh]
    a3 = [m.xy(-57.72, -51.64), m.xy(-57.79, -51.672), m.xy(-57.805, -51.69), m.xy(-57.84, -51.697)]
    M.arrow(ctx, a1, ease_in_out(ramp(t, 0.8, 3.0)), M.ARG, 12, 30)
    M.arrow(ctx, a2, ease_in_out(ramp(t, 2.2, 3.8)), M.ARG, 12, 30)
    M.arrow(ctx, a3, ease_in_out(ramp(t, 2.8, 5.0)), M.ARG, 14, 34)
    M.legend(ctx, [("ARGENTINE FORCES", M.ARG), ("ROYAL MARINES", M.BRIT)], 1440, 90, ramp(t, 1.0, 1.5))
    M.news_caption(ctx, "2 APRIL 1982", "Stanley falls after three hours", ramp(t, 0.2, 0.7) * (1 - ramp(t, t_sg - 0.4, t_sg)),
                   accent=M.ARG)
    # South Georgia inset
    a = ramp(t, t_sg, t_sg + 0.5)
    if a > 0:
        bx, by, bw, bh = 1180, 560, 660, 420
        ctx.save()
        ctx.rectangle(bx, by, bw, bh)
        ctx.clip()
        sg = M.FlatMap(-36.7, -54.4, 300, bx + bw / 2, by + bh / 2 + 10)
        ctx.push_group()
        sg.draw_base(ctx, t, night=0.4, relief=False)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(a)
        x, y = sg.pxy("grytviken")
        M.arrow(ctx, [(x + 200, y + 140), (x + 90, y + 70), (x + 12, y + 8)],
                ease_in_out(ramp(t, t_sg + 0.4, t_sg + 1.8)), M.ARG, 10, 26, a)
        M.marker(ctx, x, y, "square", M.BRIT, 8, a)
        M.label(ctx, "GRYTVIKEN", x - 16, y - 30, 26, alpha=a, anchor="rm", box=True)
        ctx.restore()
        ctx.rectangle(bx, by, bw, bh)
        ctx.set_line_width(4)
        ctx.set_source_rgba(1, 1, 1, 0.8 * a)
        ctx.stroke()
        M.label(ctx, "3 APRIL: SOUTH GEORGIA", bx + 20, by + 36, 30, (1, 0.85, 0.3), a, "lm", "oswald", box=True)


# ---------------------------------------------------------------- 14. teletext: Britain stunned
def teletext_invaded(ctx, S):
    lines = [
        (2, 0, "  FALKLANDS CRISIS                      ", "yellow", "blue", True),
        (5, 1, "ARGENTINA SEIZES", "white", None, True),
        (7, 1, "THE FALKLANDS", "white", None, True),
        (10, 1, "Argentine forces have taken control", "cyan", None, False),
        (11, 1, "of the Falkland Islands after a three-", "cyan", None, False),
        (12, 1, "hour fight with Royal Marines.", "cyan", None, False),
        (14, 1, "The Commons is to sit on a Saturday", "white", None, False),
        (15, 1, "for the first time since Suez.", "white", None, False),
        (17, 1, "Naval task force to sail - PM", "yellow", None, False),
        (24, 0, " Headlines ", "red", None, False),
        (24, 12, " Crisis ", "green", None, False),
        (24, 21, " Sport ", "yellow", None, False),
        (24, 30, " Weather ", "cyan", None, False),
    ]
    teletext(ctx, S, 101, "Sat 03 Apr", lines, reveal=(0.1, 1.6),
             mosaic=tt_mosaic_islands(27, 5, 12, 5, "green"))


# ---------------------------------------------------------------- 15. Portsmouth, 5 April
def portsmouth(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.06, (20, 0), (-20, 0))
    hz = 600
    A.sky(ctx, [(0, hexc("6F7C88")), (0.7, hexc("B7BCBD")), (1, hexc("D7D5CC"))], hz)
    A.clouds(ctx, t, 30, 420, (0.9, 0.9, 0.9), seed=71, speed=10, lo=0.45, hi=0.8, alpha=0.8)
    A.clouds(ctx, t, 120, 480, (0.5, 0.52, 0.56), seed=72, speed=14, lo=0.55, hi=0.85, alpha=0.6)
    A.ridge(ctx, 73, hz + 2, 36, (0.45, 0.48, 0.5), rough=0.4)   # Gosport shore
    A.sea(ctx, t, hz, hexc("7C8683"), hexc("2E3A3A"), seed=74, strokes=420, hi=(1, 1, 1), hi_alpha=0.18)
    x = lerp(620, 1080, S.u)
    y = 735
    L = 1180
    V.wake(ctx, x, y, L, 1, t, 0.35)
    V.ship(ctx, "hermes", x, y, L, 1, hexc("454D52"), light=(0.9, 0.9, 0.9))
    deck = y - 0.074 * L
    for k, u in enumerate((0.12, 0.2, 0.28, 0.36, 0.7, 0.78)):
        V.jet(ctx, "harrier", x - L / 2 + u * L, deck - 10, 58, 1, hexc("4A5258"), (0.8, 0.8, 0.8))
    V.helicopter(ctx, "seaking", x - L / 2 + 0.44 * L, deck - 2, 80, 1, t, hexc("3F4A4F"))
    for k in range(120):  # ship's company lining the deck
        sx = x - L / 2 + 0.02 * L + k * (0.9 * L / 120)
        if 0.49 * L < sx - (x - L / 2) < 0.65 * L:
            continue
        ctx.rectangle(sx, deck - 9, 3, 8)
        ctx.arc(sx + 1.5, deck - 11, 2, 0, 6.283)
    ctx.set_source_rgba(0.1, 0.12, 0.2, 0.9)
    ctx.fill()
    # harbour wall + Round Tower + crowd
    ctx.move_to(-20, 860)
    ctx.line_to(760, 885)
    ctx.line_to(760, H + 20)
    ctx.line_to(-20, H + 20)
    ctx.close_path()
    ctx.set_source(vgrad(ctx, 0, 860, 0, H, [(0, hexc("8C8474")), (1, hexc("4F4A40"))]))
    ctx.fill()
    P.round_tower(ctx, -40, 870, 330)
    P.crowd(ctx, 300, 1100, H + 30, 230, t, hexc("2B2A2C"), seed=21, density=0.7, wave=1.0,
            flags="union", flag_every=4, rows=2)
    P.crowd(ctx, 1050, W + 60, H + 40, 250, t + 2, hexc("222124"), seed=22, density=0.7, wave=1.0,
            flags="union", flag_every=5, rows=1)
    for k in range(3):
        bx = (200 + k * 400 + t * 50) % (W + 200) - 100
        by = 200 + k * 60 + math.sin(t + k) * 10
        ctx.set_line_width(3)
        ctx.move_to(bx - 18, by - 3)
        ctx.curve_to(bx - 9, by - 8, bx - 3, by - 1, bx, by)
        ctx.curve_to(bx + 3, by - 1, bx + 9, by - 8, bx + 18, by - 3)
        ctx.set_source_rgba(0.95, 0.95, 0.95, 0.9)
        ctx.stroke()
    ctx.restore()
    lower_third(ctx, S, "THE TASK FORCE SAILS", "HMS Hermes leaves Portsmouth · 5 April 1982", t_in=0.5)


# ---------------------------------------------------------------- 16. route south
def _sample(pts, f):
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts[:-1], pts[1:])]
    total = sum(seg)
    target, acc = total * clamp(f), 0
    for (a, b), s in zip(zip(pts[:-1], pts[1:]), seg):
        if acc + s >= target and s > 0:
            k = (target - acc) / s
            return (lerp(a[0], b[0], k), lerp(a[1], b[1], k)), math.atan2(b[1] - a[1], b[0] - a[0])
        acc += s
    return pts[-1], 0.0


def globe_route(ctx, S):
    t = S.t
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgb(0.01, 0.015, 0.03)
    ctx.fill()
    A.stars(ctx, 260, seed=19, alpha=0.6, y1=H, t=t)
    k = ease_in_out(S.u)
    g = M.Globe(lerp(-18, -30, k), lerp(18, -12, k), 540, W / 2 + 180, H / 2)
    g.draw(ctx, t)
    keys = ["portsmouth", "wp_biscay", "wp_canaries", "wp_capeverde", "ascension", "falklands"]
    ll = [M.PLACES[k] for k in keys]
    path = []
    for a, b in zip(ll[:-1], ll[1:]):
        path.extend(M.great_circle(a, b, 40)[:-1])
    path.append(ll[-1])
    xs, ys, _ = g.proj([p[0] for p in path], [p[1] for p in path])
    pts = list(zip(xs, ys))
    prog = ease_in_out(ramp(t, 0.3, 6.5))
    g.route(ctx, keys, 1.0, M.BRIT, 3, dash=[10, 8], glow=False, alpha=0.6)
    for i in range(7):
        f = prog - i * 0.035
        if f <= 0:
            continue
        (sx, sy), hd = _sample(pts, f)
        M.ship_icon(ctx, sx, sy, hd, 13 if i else 17, M.BRIT)
    for key, name, a0, dx, dy in (("portsmouth", "PORTSMOUTH", 0.2, 20, -18), ("ascension", "ASCENSION ISLAND", 2.5, 24, 0),
                                  ("falklands", "FALKLANDS", 5.5, 22, 10)):
        x, y = g.pxy(key)
        a = ramp(t, a0, a0 + 0.5)
        M.marker(ctx, x, y, "dot", (1, 1, 1), 8, a, t, pulse=(key == "ascension"))
        M.label(ctx, name, x + dx, y + dy, 30, alpha=a, box=True)
    x, y = g.pxy("ascension")
    M.label(ctx, "staging post", x + 24, y + 36, 24, (0.8, 0.86, 1), ramp(t, 3.0, 3.5), "lm", "cond_r", box=True)
    a = ramp(t, 1.0, 1.6)
    if a > 0:
        bx, by = 90, 700
        ctx.rectangle(bx, by, 520, 250)
        ctx.set_source_rgba(0.04, 0.07, 0.15, 0.82 * a)
        ctx.fill()
        ctx.rectangle(bx, by, 520, 6)
        set_rgba(ctx, M.BRIT, a)
        ctx.fill()
        draw_text(ctx, "THE TASK FORCE", bx + 30, by + 56, "cond", 30, (0.75, 0.82, 0.95), "lb", a, 0.1)
        n = int(round(lerp(0, 100, ease_out(ramp(t, 1.2, 4.0)))))
        draw_text(ctx, f"{n}+ SHIPS", bx + 30, by + 140, "oswald", 76, (1, 1, 1), "lb", a, 0.03)
        draw_text(ctx, "incl. requisitioned liners", bx + 30, by + 186, "cond_r", 28, (0.8, 0.85, 0.95), "lb", a)
        draw_text(ctx, "Canberra and QE2", bx + 30, by + 222, "cond_r", 28, (0.8, 0.85, 0.95), "lb", a)
    M.news_caption(ctx, "8,000 MILES SOUTH", "April – May 1982", ramp(t, 0.2, 0.7))


# ---------------------------------------------------------------- 17. South Georgia retaken
def south_georgia(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.08, (0, 10), (-30, 0))
    hz = 700
    A.sky(ctx, [(0, hexc("7E93A8")), (1, hexc("D6DEE3"))], hz)
    A.clouds(ctx, t, 40, 300, (0.95, 0.96, 0.98), seed=81, speed=8, lo=0.5, hi=0.85, alpha=0.7)
    A.ridge(ctx, 82, hz - 40, 520, (0.55, 0.62, 0.72), rough=0.62, top_color=(0.98, 0.99, 1.0),
            shape=lambda u: 0.35 + 0.65 * math.sin(u * math.pi) ** 0.8)
    A.ridge(ctx, 83, hz, 260, (0.3, 0.35, 0.42), rough=0.6, top_color=(0.88, 0.92, 0.96), x0=-200, x1=1000,
            shape=lambda u: math.sin(min(1.0, (1 - u) * 1.6) * math.pi / 2))
    A.sea(ctx, t, hz, hexc("485C68"), hexc("101E26"), seed=84, strokes=380, hi=(1, 1, 1), hi_alpha=0.18)
    # shore with church and whaling station
    ctx.move_to(1000, hz + 4)
    ctx.curve_to(1200, hz - 10, 1500, hz - 20, W + 20, hz - 16)
    ctx.line_to(W + 20, hz + 40)
    ctx.line_to(1000, hz + 8)
    ctx.close_path()
    ctx.set_source_rgb(0.9, 0.92, 0.94)
    ctx.fill()
    for k in range(4):
        ctx.rectangle(1360 + k * 90, hz - 40 - (k % 2) * 16, 70, 44 + (k % 2) * 16)
        ctx.set_source_rgb(0.45 - k * 0.03, 0.28, 0.2)
        ctx.fill()
    P.church_norwegian(ctx, 1180, hz - 8, 80)
    P.flagpole(ctx, "ensign", 1760, hz - 10, 200, 110, t, raise_frac=ease_out(ramp(t, 1.0, 4.5)), amp=0.1)
    V.ship(ctx, "type21", lerp(520, 560, S.u), 790, 720, 1, hexc("2E3438"), light=(0.9, 0.92, 0.95))
    hx = lerp(-100, 900, ramp(t, 0.0, S.dur))
    V.helicopter(ctx, "seaking", hx, 330 + math.sin(t * 1.5) * 8, 170, 1, t, hexc("2C3438"))
    A.snow(ctx, t, 0.45, 150)
    ctx.restore()
    lower_third(ctx, S, "SOUTH GEORGIA RETAKEN", "25 April 1982 · Operation Paraquet", t_in=0.5)


# ---------------------------------------------------------------- 18. Black Buck
def vulcan(ctx, S):
    t = S.t
    tb = S.word("firstblows", 1, "to bomb")
    if t < tb + 0.3:
        ctx.save()
        camera(ctx, S, 1.0, 1.1, (0, 0), (20, -10))
        A.sky(ctx, [(0, hexc("02040A")), (0.7, hexc("0A1428")), (1, hexc("1B2A40"))], H)
        A.stars(ctx, 400, seed=31, alpha=0.9, y1=H, t=t)
        # moon + cloud deck below
        radial_glow(ctx, 1650, 170, 120, (0.9, 0.92, 1), 0.35)
        ctx.arc(1650, 170, 34, 0, 6.283)
        ctx.set_source_rgb(0.92, 0.93, 0.96)
        ctx.fill()
        A.clouds(ctx, t, 760, H + 40, (0.35, 0.4, 0.5), seed=32, speed=60, lo=0.35, hi=0.7, alpha=0.9, base=6)
        ang = -0.62
        bob = math.sin(t * 0.8) * 6
        vx, vy = 780 + math.sin(t * 0.5) * 12, 560 + bob
        tx, ty = 1250, 300 + math.sin(t * 0.7 + 1) * 4
        V.victor_plan(ctx, tx, ty, 380, ang, (0.14, 0.16, 0.2), (0.55, 0.6, 0.72))
        # hose from Victor to Vulcan probe
        ux, uy = math.cos(ang), math.sin(ang)
        hose0 = (tx - ux * 190 * 0.4, ty - uy * 190 * 0.4)
        probe = (vx + ux * 400 * 0.56, vy + uy * 400 * 0.56)
        ctx.move_to(*hose0)
        ctx.curve_to(hose0[0] - 80, hose0[1] + 60, probe[0] + 40, probe[1] - 70, *probe)
        ctx.set_line_width(4)
        ctx.set_source_rgb(0.15, 0.16, 0.18)
        ctx.stroke()
        ctx.arc(probe[0], probe[1], 9, 0, 6.283)
        ctx.fill()
        V.vulcan_plan(ctx, vx, vy, 400, ang, (0.13, 0.14, 0.18), (0.55, 0.6, 0.72))
        lw = (vx - ux * 400 * 0.32 + uy * 400 * 0.55, vy - uy * 400 * 0.32 - ux * 400 * 0.55)
        rw = (vx - ux * 400 * 0.32 - uy * 400 * 0.55, vy - uy * 400 * 0.32 + ux * 400 * 0.55)
        for (px, py, c) in ((lw[0], lw[1], (1, 0.2, 0.2)), (rw[0], rw[1], (0.2, 1, 0.3))):
            radial_glow(ctx, px, py, 14, c, 0.9 * (0.5 + 0.5 * math.sin(t * 6)))
        ctx.restore()
        lower_third(ctx, S, "OPERATION BLACK BUCK", "1 May 1982 · Vulcan XM607, refuelled by Victor tankers",
                    t_in=0.6, t_out=tb + 0.2)
        date_stamp(ctx, S, "01 MAY 1982", t_in=0.4, t_out=tb + 0.2)
        if t < tb - 0.3:
            return
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgba(0, 0, 0, ramp(t, tb - 0.3, tb + 0.3))
        ctx.fill()
        return
    # runway at Stanley, from above: a stick of 21 bombs across the runway
    tt = t - tb - 0.3
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgb(0.05, 0.06, 0.05)
    ctx.fill()
    ctx.save()
    ctx.set_source_surface(A.noise_surface(W, H, (0.2, 0.22, 0.16), 41, 0.4, 0.9, 0.6), 0, 0)
    ctx.paint()
    ctx.restore()
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.rotate(-0.25)
    ctx.rectangle(-1100, -70, 2200, 140)
    ctx.set_source_rgb(0.2, 0.2, 0.2)
    ctx.fill()
    for i in range(-20, 21):
        ctx.rectangle(i * 55, -3, 30, 6)
    ctx.set_source_rgb(0.55, 0.55, 0.5)
    ctx.fill()
    ctx.restore()
    for i in range(21):
        u = i / 20
        bx = lerp(250, 1700, u)
        by = lerp(150, 950, u) + math.sin(i * 1.7) * 30
        t0 = 0.2 + i * 0.09
        if tt > t0 + 0.2:
            ctx.arc(bx, by, 26, 0, 6.283)
            ctx.set_source_rgba(0.02, 0.02, 0.02, 0.8)
            ctx.fill()
        A.flash(ctx, bx, by, tt, t0, r=150, dur=0.9)
        A.smoke(ctx, bx, by, tt, seed=i, rate=4, life=4, rise=20, size=24, alpha=0.4, start=t0 + 0.1, wind=40,
                color=(0.3, 0.28, 0.25))
    M.news_caption(ctx, "STANLEY AIRFIELD", "21 bombs · one hits the runway", ramp(tt, 0.2, 0.7))


# ---------------------------------------------------------------- 19. periscope: General Belgrano
def periscope(ctx, S):
    t = S.t
    t_hit = S.word("belgrano", 0, "torpedoed") + 1.6
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()
    cx, cy, R = W / 2, H / 2, 500
    ctx.save()
    ctx.arc(cx, cy, R, 0, 6.283)
    ctx.clip()
    bob = math.sin(t * 0.9) * 14 + math.sin(t * 2.3) * 4
    hz = cy + 40 + bob
    pan = lerp(160, -40, ease_in_out(ramp(t, 0, 3.0)))
    tint_sky = [(0, (0.42, 0.46, 0.43)), (1, (0.72, 0.75, 0.7))]
    A.sky(ctx, tint_sky, hz)
    A.clouds(ctx, t, hz - 420, hz - 60, (0.8, 0.82, 0.78), seed=91, speed=6, lo=0.5, hi=0.85, alpha=0.5)
    A.sea(ctx, t, hz, (0.4, 0.44, 0.41), (0.08, 0.1, 0.09), seed=92, strokes=420, hi=(0.9, 0.95, 0.9),
          hi_alpha=0.2)
    sink = ramp(t, t_hit + 1.5, S.dur + 4) * 0.6
    listing = ramp(t, t_hit + 0.5, S.dur) * 9
    bx = cx + pan
    V.ship(ctx, "corvette", bx - 520, hz, 200, 1, (0.2, 0.22, 0.21))
    V.ship(ctx, "corvette", bx + 470, hz + 2, 180, -1, (0.22, 0.24, 0.23))
    V.ship(ctx, "belgrano", bx, hz + 1, 560, -1, (0.14, 0.15, 0.15), light=(0.6, 0.65, 0.6), list_deg=listing,
           sink=sink)
    for k, dx in enumerate((-90, 120)):
        th = t_hit + k * 0.6
        A.flash(ctx, bx + dx, hz - 10, t, th, r=260, dur=1.2, color=(0.95, 0.95, 0.85))
        A.splash(ctx, bx + dx, hz, t, th, h=220, w=60, dur=3.0, color=(0.85, 0.88, 0.85))
        A.smoke(ctx, bx + dx, hz - 20, t, seed=k + 5, rate=5, life=10, rise=26, size=26, alpha=0.6, start=th + 0.2,
                wind=-12, color=(0.12, 0.13, 0.12))
    # torpedo tracks
    tr = ramp(t, t_hit - 1.8, t_hit)
    if 0 < tr < 1:
        for k, dx in enumerate((-90, 120, 300)):
            y0, y1 = H + 50, hz + 6
            yy = lerp(y0, y1, tr)
            ctx.move_to(bx + dx * 0.3, y0)
            ctx.line_to(lerp(bx + dx * 0.3, bx + dx, tr), yy)
            ctx.set_line_width(5)
            ctx.set_source_rgba(0.9, 0.95, 0.9, 0.35)
            ctx.stroke()
    ctx.restore()
    # reticle
    ctx.set_line_width(2)
    ctx.set_source_rgba(0.05, 0.05, 0.05, 0.9)
    ctx.move_to(cx - R, hz)
    ctx.line_to(cx + R, hz)
    ctx.move_to(cx, cy - R)
    ctx.line_to(cx, cy + R)
    ctx.stroke()
    for i in range(-10, 11):
        L = 18 if i % 5 == 0 else 9
        ctx.move_to(cx + i * 40, hz - L)
        ctx.line_to(cx + i * 40, hz + L)
        ctx.move_to(cx - L, cy + i * 40)
        ctx.line_to(cx + L, cy + i * 40)
    ctx.stroke()
    brg = 250 - pan / 20
    for i in range(-4, 5):
        v = int(round(brg / 10) * 10 + i * 10) % 360
        x = cx + (v - brg) * 20
        if abs(x - cx) < R - 60:
            draw_text(ctx, f"{v:03d}", x, cy - R + 50, "vt", 34, (0.05, 0.05, 0.05), "cb", 0.9)
    # housing
    g = cairo.RadialGradient(cx, cy, R - 6, cx, cy, R + 60)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(0.1, 0, 0, 0, 1)
    ctx.set_source(g)
    ctx.arc(cx, cy, R + 400, 0, 6.283)
    ctx.fill()
    ctx.arc(cx, cy, R, 0, 6.283)
    ctx.set_line_width(10)
    ctx.set_source_rgb(0.12, 0.12, 0.12)
    ctx.stroke()
    draw_text(ctx, "HMS CONQUEROR", 90, 110, "vt", 52, (0.75, 0.85, 0.75), "lb", ramp(t, 0.3, 0.8))
    draw_text(ctx, "02 MAY 1982", 90, 160, "vt", 44, (0.75, 0.85, 0.75), "lb", ramp(t, 0.3, 0.8))
    tf = t_hit - 2.0
    if tf < t < t_hit + 1.5:
        draw_text(ctx, "3 x Mk 8 TORPEDOES", W - 90, 110, "vt", 48, (0.95, 0.4, 0.3), "rb",
                  0.5 + 0.5 * (int(t * 3) % 2))
    lower_third(ctx, S, "ARA GENERAL BELGRANO", "323 killed · sunk outside the British exclusion zone",
                t_in=S.at("belgrano", 1) - 0.2, accent=M.ARG)


# ---------------------------------------------------------------- 20. Sheffield
def sheffield(ctx, S):
    t = S.t
    t_launch = 0.9
    t_hit = 3.0
    ctx.save()
    camera(ctx, S, 1.0, 1.1, (0, 0), (-60, -10))
    shake(ctx, S, t_hit, 14, 1.2)
    hz = 600
    A.sky(ctx, [(0, hexc("5F6770")), (1, hexc("A9ADAC"))], hz)
    A.clouds(ctx, t, 20, 400, (0.4, 0.42, 0.45), seed=101, speed=12, lo=0.4, hi=0.8, alpha=0.8)
    A.sea(ctx, t, hz, hexc("56605F"), hexc("1B2224"), seed=102, strokes=520, hi=(1, 1, 1), hi_alpha=0.2)
    sx, sy, L = 1220, 740, 880
    V.wake(ctx, sx, sy, L, 1, t, 0.3)
    V.ship(ctx, "type42", sx, sy, L, 1, hexc("343B40"), light=(0.85, 0.88, 0.9), list_deg=ramp(t, t_hit, S.dur) * 3)
    # Super Etendard low and fast, left to right, then pulling away
    ex = lerp(-300, 900, ramp(t, 0.0, 1.8))
    ey = lerp(560, 470, ramp(t, 1.0, 1.8))
    if t < 1.9:
        V.jet(ctx, "etendard", ex, ey, 240, 1, hexc("3A3F3C"), (0.75, 0.75, 0.72), pitch=ramp(t, 1.0, 1.8) * 12,
              burner=0.4)
    # sea-skimming Exocet
    if t_launch < t < t_hit:
        u = (t - t_launch) / (t_hit - t_launch)
        mx = lerp(lerp(-300, 900, ramp(t_launch, 0.0, 1.8)), sx - L * 0.12, u)
        my = lerp(575, sy - 26, u) + math.sin(u * 20) * 2
        V.exocet(ctx, mx, my, 70, 1, t)
    hx, hy = sx - L * 0.1, sy - 40
    k = A.flash(ctx, hx, hy, t, t_hit, r=420, dur=1.4)
    A.smoke(ctx, hx, hy - 10, t, seed=7, rate=22, life=12, rise=62, size=28, alpha=0.7, start=t_hit + 0.05, wind=48,
            color=(0.06, 0.06, 0.06), grow=4.2, spread=1.8)
    if t > t_hit:
        A.fire(ctx, hx, hy + 10, t, 90, 80, seed=3, intensity=min(1, (t - t_hit) * 2))
    A.darken(ctx, 0.0)
    ctx.restore()
    if k > 0:
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgba(1, 0.95, 0.85, k * 0.5)
        ctx.fill()
    lower_third(ctx, S, "HMS SHEFFIELD", "4 May 1982 · hit by an Exocet missile · 20 killed", t_in=t_hit + 0.6)


# ---------------------------------------------------------------- 21. exclusion zone / air war
def tez_map(ctx, S):
    t = S.t
    t_air = S.word("belgrano", 3, "The war")
    m = M.FlatMap(lerp(-62.5, -63.2, S.u), -52.3, lerp(92, 100, S.u), W / 2, H / 2)
    m.draw_base(ctx, t, grid_step=5)
    m.circle_nm(ctx, "tez_centre", 200, M.BRIT, 0.9, progress=ease_in_out(ramp(t, 0.1, 1.3)), width=4)
    x, y = m.xy(-59.5, -48.2)
    M.label(ctx, "TOTAL EXCLUSION ZONE (200 nm)", x, y, 26, M.BRIT, ramp(t, 0.8, 1.2), "cm", "cond", box=True)
    bx, by = m.pxy("belgrano_sunk")
    M.marker(ctx, bx, by, "sunk", M.ARG, 14, ramp(t, 0.5, 0.9))
    M.label(ctx, "BELGRANO SUNK", bx - 22, by + 34, 26, alpha=ramp(t, 0.5, 0.9), anchor="rm", box=True)
    sx, sy = m.pxy("sheffield_hit")
    M.marker(ctx, sx, sy, "sunk", M.BRIT, 14, ramp(t, 0.7, 1.1))
    M.label(ctx, "SHEFFIELD HIT", sx + 22, sy + 30, 26, alpha=ramp(t, 0.7, 1.1), box=True)
    # the fleet goes home
    M.arrow(ctx, [m.xy(-61.0, -48.9), m.xy(-63.6, -48.0), m.xy(-65.6, -47.6)], ease_in_out(ramp(t, 0.8, 2.6)),
            M.ARG, 12, 30)
    x, y = m.xy(-62.6, -48.1)
    M.label(ctx, "ARGENTINE FLEET RETURNS TO PORT", x + 40, y - 36, 26, M.ARG, ramp(t, 1.8, 2.3), "cm", box=True)
    # air bases and strike routes
    bases = [((-67.75, -53.78), "RIO GRANDE"), ((-69.31, -51.61), "RIO GALLEGOS"), ((-67.8, -49.3), "SAN JULIAN")]
    for i, (ll, name) in enumerate(bases):
        a = ramp(t, t_air - 0.4 + i * 0.2, t_air + i * 0.2)
        x, y = m.xy(*ll)
        M.marker(ctx, x, y, "square", M.ARG, 10, a)
        M.label(ctx, name, x - 18, y, 24, alpha=a, anchor="rm", box=True)
        tx, ty = m.xy(-59.2 + i * 0.3, -51.7 + (i - 1) * 0.25)
        mx, my = (x + tx) / 2, (y + ty) / 2 - 60
        M.arrow(ctx, [(x, y), (mx, my), (tx, ty)], ease_in_out(ramp(t, t_air + i * 0.25, t_air + 1.4 + i * 0.25)),
                M.ARG, 7, 22, 0.95, outline=False)
    x, y = m.pxy("falklands")
    M.label(ctx, "FALKLANDS", x, y + 70, 28, (1, 1, 1), ramp(t, 0.2, 0.6), "cm", "oswald", tracking=0.15)
    M.label(ctx, "ARGENTINA", *m.xy(-68.5, -47.6), 40, (0.3, 0.26, 0.18), ramp(t, 0.2, 0.6), "cm", "oswald",
            tracking=0.25, shadow=None)
    M.news_caption(ctx, "THE WAR AT SEA", "May 1982", ramp(t, 0.2, 0.6) * (1 - ramp(t, t_air - 0.3, t_air)))
    M.news_caption(ctx, "THE AIR WAR", "Strikes from mainland bases", ramp(t, t_air, t_air + 0.4), accent=M.ARG)
