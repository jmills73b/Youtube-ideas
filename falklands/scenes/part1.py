"""Opening, geography, history, road to war, the junta."""
import math

import cairo

from engine import art as A
from engine import maps as M
from engine import people as P
from engine import vessels as V
from engine.core import (H, W, clamp, draw_text, ease_in_out, ease_out, hash01, hexc, lerp, mix, poly, ramp,
                         set_rgba, smooth, text_width, typed, vgrad)
from .common import (brig, camera, date_stamp, lower_third, paper, stamp, title_text, typewriter)


# ---------------------------------------------------------------- 1. storm at sea
def storm_sea(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.12, (40, 10), (-30, 20))
    hz = 640
    A.sky(ctx, [(0, hexc("141820")), (0.45, hexc("3A3A44")), (0.8, hexc("B57A4E")), (1, hexc("E0A160"))], hz)
    A.sun(ctx, 1380, 610, 34, (1.0, 0.8, 0.5), glow=6, alpha=0.9)
    A.clouds(ctx, t, 40, 330, (0.09, 0.09, 0.12), seed=3, speed=10, lo=0.35, hi=0.7, alpha=0.95)
    A.clouds(ctx, t, 260, 560, (0.2, 0.17, 0.18), seed=4, speed=16, lo=0.42, hi=0.75, alpha=0.85)
    A.clouds(ctx, t, 470, 620, (0.62, 0.42, 0.3), seed=5, speed=22, lo=0.5, hi=0.8, alpha=0.6)
    A.ridge(ctx, 12, hz + 2, 46, (0.22, 0.17, 0.18), x0=980, x1=2100, rough=0.45,
            shape=lambda u: math.sin(min(1, u * 1.6) * math.pi / 2))
    A.sea(ctx, t, hz, hexc("6B4C3C"), hexc("0B0F14"), seed=8, strokes=700, hi=(1.0, 0.75, 0.5), hi_alpha=0.28,
          chop=1.6)
    A.reflection(ctx, 1380, hz, 210, (1.0, 0.8, 0.5), 0.35, t, rows=18)
    x = lerp(520, 820, S.u)
    V.wake(ctx, x, 726, 560, 1, t, alpha=0.3)
    V.ship(ctx, "type21", x, 726, 560, 1, (0.05, 0.05, 0.07), light=(0.9, 0.55, 0.35),
           roll=math.sin(t * 0.9) * 1.6)
    # albatross
    for k in range(2):
        bx = (300 + k * 260 + t * (38 + k * 9)) % (W + 200) - 100
        by = 300 + k * 70 + math.sin(t * 0.6 + k) * 16
        ctx.set_line_width(3)
        ctx.move_to(bx - 26, by - 4)
        ctx.curve_to(bx - 14, by - 10, bx - 5, by - 2, bx, by)
        ctx.curve_to(bx + 5, by - 2, bx + 14, by - 10, bx + 26, by - 4)
        ctx.set_source_rgba(0.08, 0.08, 0.1, 0.9)
        ctx.stroke()
    # foreground swell
    ctx.move_to(-50, H + 10)
    for i in range(0, W + 100, 20):
        y = 960 + math.sin(i * 0.004 + t * 0.8) * 34 + math.sin(i * 0.011 - t * 1.3) * 12
        ctx.line_to(i, y)
    ctx.line_to(W + 50, H + 10)
    ctx.close_path()
    ctx.set_source(vgrad(ctx, 0, 900, 0, H, [(0, (0.08, 0.08, 0.1)), (1, (0.02, 0.02, 0.03))]))
    ctx.fill()
    A.rain(ctx, t, alpha=0.08, n=180)
    ctx.restore()
    date_stamp(ctx, S, "SOUTH ATLANTIC  1982", t_in=1.4, t_out=S.dur - 0.3)


# ---------------------------------------------------------------- 2. title
def title(ctx, S):
    t = S.t
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(vgrad(ctx, 0, 0, 0, H, [(0, hexc("05070C")), (1, hexc("0E1422"))]))
    ctx.fill()
    m = M.FlatMap(-59.1, -51.75, lerp(330, 370, S.u), W / 2, H / 2 + 40)
    m.land_path(ctx, ("falklands",))
    ctx.set_source_rgba(0.1, 0.13, 0.2, 0.9)
    ctx.fill_preserve()
    ctx.set_line_width(1.5)
    ctx.set_source_rgba(0.35, 0.45, 0.6, 0.5)
    ctx.stroke()
    a = ramp(t, 0.2, 1.2)
    title_text(ctx, "THE FALKLANDS WAR", W / 2, 560, 150, a)
    lw = 900 * ease_out(ramp(t, 0.8, 2.0))
    ctx.rectangle(W / 2 - lw / 2, 600, lw, 6)
    set_rgba(ctx, M.BRIT, a)
    ctx.fill()
    draw_text(ctx, "2 APRIL  –  14 JUNE 1982", W / 2, 690, "oswald", 54, (0.92, 0.92, 0.92), "cb",
              ramp(t, 1.4, 2.3), 0.12, shadow=(3, 3, 0.7))
    draw_text(ctx, "FALKLAND ISLANDS  ·  ISLAS MALVINAS", W / 2, 380, "cond", 34, (0.65, 0.75, 0.9), "cb",
              ramp(t, 0.9, 1.8), 0.25)


# ---------------------------------------------------------------- 3. globe
def globe(ctx, S):
    t = S.t
    ctx.rectangle(0, 0, W, H)
    ctx.set_source_rgb(0.01, 0.015, 0.03)
    ctx.fill()
    A.stars(ctx, 260, seed=9, alpha=0.6, y1=H, t=t)
    k = ease_in_out(ramp(t, 0.0, 5.5))
    g = M.Globe(lerp(-12, -36, k), lerp(28, -24, k), lerp(470, 560, k), W / 2 + 120, H / 2 + lerp(0, -40, k))
    g.draw(ctx, t)
    route = ["portsmouth", "wp_biscay", "wp_canaries", "wp_capeverde", "ascension", "falklands"]
    p = ease_in_out(ramp(t, 2.2, 6.2))
    g.route(ctx, route, p, M.BRIT, 5)
    for key, name, a0, dx, dy in (("portsmouth", "BRITAIN", 0.8, 18, -16), ("falklands", "FALKLAND ISLANDS", 1.4, 22, 4)):
        x, y = g.pxy(key)
        a = ramp(t, a0, a0 + 0.5)
        M.marker(ctx, x, y, "dot", M.BRIT if key == "portsmouth" else (1, 1, 1), 8, a, t, pulse=key == "falklands")
        M.label(ctx, name, x + dx, y + dy, 30, alpha=a, box=True)
    x, y = g.xy(-64.5, -38.0)
    M.label(ctx, "ARGENTINA", x, y, 28, (0.3, 0.26, 0.18), ramp(t, 2.0, 2.6), "cm", "oswald", tracking=0.2,
            shadow=None)
    if p > 0.5:
        mx, my = g.xy(-17.0, 8.0)
        M.label(ctx, "c. 8,000 MILES", mx + 26, my, 40, (1, 0.85, 0.3), ramp(t, 4.6, 5.2), "lm", "oswald", box=True)
    # 300 miles from Argentina
    a2 = ease_in_out(ramp(t, 6.0, 7.2))
    if a2 > 0:
        a_ = g.xy(-68.3, -51.2)
        b_ = g.pxy("falklands")
        ctx.move_to(*a_)
        ctx.line_to(lerp(a_[0], b_[0], a2), lerp(a_[1], b_[1], a2))
        ctx.set_line_width(4)
        ctx.set_dash([10, 7])
        set_rgba(ctx, M.ARG)
        ctx.stroke()
        ctx.set_dash([])
        M.label(ctx, "300 MILES", a_[0] - 10, a_[1] + 44, 32, (0.75, 0.9, 1), ramp(t, 6.6, 7.2), "rm", "oswald",
                box=True)
    M.news_caption(ctx, "THE SOUTH ATLANTIC", "Britain to the Falklands", ramp(t, 0.4, 1.0))


# ---------------------------------------------------------------- 4. the islands
def islands_map(ctx, S):
    t = S.t
    m = M.FlatMap(lerp(-59.25, -59.05, S.u), -51.78, lerp(360, 410, ease_in_out(S.u)), W / 2, H / 2 + 20)
    m.draw_base(ctx, t, grid_step=0.5)
    labels = [
        ("WEST FALKLAND", (-60.3, -51.74), 0.3, 0),
        ("EAST FALKLAND", (-58.85, -51.6), 0.6, 0),
        ("FALKLAND SOUND", (-59.37, -51.68), 0.9, -0.93),
    ]
    for text, ll, a0, rot in labels:
        x, y = m.xy(*ll)
        a = ramp(t, a0, a0 + 0.6)
        if rot:
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(rot)
            M.label(ctx, text, 0, 0, 26, (0.85, 0.92, 1), a, "cm", "cond", tracking=0.3)
            ctx.restore()
        else:
            M.label(ctx, text, x, y, 36, (0.3, 0.26, 0.18), a, "cm", "oswald", tracking=0.18, shadow=None)
    x, y = m.pxy("stanley")
    M.marker(ctx, x, y, "star", (1, 0.85, 0.2), 12, ramp(t, 1.2, 1.6), t)
    M.label(ctx, "STANLEY", x + 22, y - 26, 32, alpha=ramp(t, 1.2, 1.6), box=True)
    a = ramp(t, 1.8, 2.4)
    if a > 0:
        bx, by = 1340, 760
        ctx.rectangle(bx, by, 480, 190)
        ctx.set_source_rgba(0.04, 0.07, 0.15, 0.8 * a)
        ctx.fill()
        ctx.rectangle(bx, by, 480, 6)
        set_rgba(ctx, M.BRIT, a)
        ctx.fill()
        draw_text(ctx, "POPULATION 1982", bx + 30, by + 58, "cond", 30, (0.75, 0.82, 0.95), "lb", a, 0.1)
        draw_text(ctx, "c. 1,800", bx + 30, by + 140, "oswald", 76, (1, 1, 1), "lb", a, 0.04)
        draw_text(ctx, "mostly of British descent", bx + 30, by + 176, "cond_r", 26, (0.8, 0.85, 0.95), "lb", a)
    M.news_caption(ctx, "THE FALKLAND ISLANDS", "Islas Malvinas", ramp(t, 0.2, 0.8))


# ---------------------------------------------------------------- 5. history (parchment)
SEPIA = (0.3, 0.2, 0.12)
PAPER_TONE = (0.9, 0.84, 0.7)


def _engraved_islands(ctx, m, clip_box):
    x0, y0, x1, y1 = clip_box
    ctx.save()
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.clip()
    for w, col, a in ((44, SEPIA, 0.22), (40, PAPER_TONE, 1), (30, SEPIA, 0.3), (26, PAPER_TONE, 1),
                      (18, SEPIA, 0.38), (14, PAPER_TONE, 1), (7, SEPIA, 0.5), (4, PAPER_TONE, 1)):
        m.land_path(ctx, ("falklands",))
        ctx.set_line_width(w)
        set_rgba(ctx, col, a)
        ctx.stroke()
    m.land_path(ctx, ("falklands",))
    ctx.set_source_rgba(0.86, 0.78, 0.6, 1)
    ctx.fill_preserve()
    ctx.save()
    ctx.clip_preserve()
    ctx.new_path()
    ctx.set_line_width(1)
    for i in range(-H, W, 9):
        ctx.move_to(i, y0)
        ctx.line_to(i + (y1 - y0), y1)
    ctx.set_source_rgba(*SEPIA, 0.25)
    ctx.stroke()
    ctx.restore()
    m.land_path(ctx, ("falklands",))
    ctx.set_line_width(1.8)
    set_rgba(ctx, SEPIA, 0.9)
    ctx.stroke()
    ctx.restore()
    ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
    ctx.set_line_width(3)
    set_rgba(ctx, SEPIA, 0.9)
    ctx.stroke()
    ctx.rectangle(x0 + 10, y0 + 10, x1 - x0 - 20, y1 - y0 - 20)
    ctx.set_line_width(1)
    ctx.stroke()


def history(ctx, S):
    t = S.t
    paper(ctx, 3, PAPER_TONE)
    ctx.save()
    camera(ctx, S, 1.0, 1.05, (0, 0), (-20, 0))
    box = (70, 90, 1010, 990)
    m = M.FlatMap(-59.1, -51.72, 265, 540, 470)
    _engraved_islands(ctx, m, box)
    draw_text(ctx, "Falkland's Islands", 540, 860, "serif_i", 52, SEPIA, "cb", 0.95)
    draw_text(ctx, "—  Isles Malouines  ·  Islas Malvinas  —", 540, 905, "serif_i", 28, SEPIA, "cb", 0.85)
    for (u, h, name) in ((-58.1, -51.52, "Port Louis"), (-60.1, -51.33, "Port Egmont")):
        x, y = m.xy(u, h)
        ctx.arc(x, y, 6, 0, 6.283)
        set_rgba(ctx, SEPIA)
        ctx.fill()
        draw_text(ctx, name, x + 12, y - 8, "serif_i", 26, SEPIA, "lb", 0.9)
    brig(ctx, lerp(260, 330, S.u), 800, 150, SEPIA, 0.95, t)
    # compass rose
    cx, cy = 880, 200
    for k in range(8):
        a = k * math.pi / 4
        r = 60 if k % 2 == 0 else 32
        ctx.move_to(cx, cy)
        ctx.line_to(cx + math.cos(a - 0.12) * 12, cy + math.sin(a - 0.12) * 12)
        ctx.line_to(cx + math.cos(a) * r, cy + math.sin(a) * r)
        ctx.close_path()
    set_rgba(ctx, SEPIA, 0.8)
    ctx.fill()
    draw_text(ctx, "N", cx, cy - 66, "serif_b", 26, SEPIA, "cb")
    # timeline
    entries = [
        (S.at("history", 1, 0.0), "1764", "France founds Port Louis"),
        (S.at("history", 1, 0.12), "1765", "Britain lands at Port Egmont"),
        (S.at("history", 1, 0.26), "1767", "France cedes its colony to Spain"),
        (S.at("history", 1, 0.4), "1774", "Britain withdraws, keeping its claim"),
        (S.word("history", 1, "after independence"), "1811", "Spain withdraws its garrison"),
        (S.word("history", 1, "Buenos Aires"), "1820s", "Buenos Aires claims the islands"),
        (S.at("history", 2, 0.05), "1833", "HMS Clio arrives; Argentine garrison leaves"),
        (S.word("history", 2, "Britain has governed"), "1833–1982", "Continuous British rule"),
    ]
    x0, y0 = 1090, 150
    ctx.move_to(x0 + 118, y0 - 20)
    ctx.line_to(x0 + 118, y0 + 8 * 96 - 30)
    ctx.set_line_width(2)
    set_rgba(ctx, SEPIA, 0.6)
    ctx.stroke()
    for i, (t0, year, text) in enumerate(entries):
        a = ramp(t, t0, t0 + 0.5)
        if a <= 0:
            continue
        y = y0 + i * 96
        hl = i == len(entries) - 1
        draw_text(ctx, year, x0 + 100, y + 30, "serif_b", 40 if not hl else 44, (0.55, 0.1, 0.08) if hl else SEPIA,
                  "rb", a)
        ctx.arc(x0 + 118, y + 18, 8, 0, 6.283)
        set_rgba(ctx, SEPIA, a)
        ctx.fill()
        draw_text(ctx, text, x0 + 142, y + 30, "serif_i", 32, SEPIA, "lb", a)
    ctx.restore()


# ---------------------------------------------------------------- 6. Malvinas poster
def malvinas_poster(ctx, S):
    t = S.t
    for i, c in enumerate((M.ARG, (0.97, 0.97, 0.95), M.ARG)):
        ctx.rectangle(0, i * H / 3, W, H / 3 + 1)
        set_rgba(ctx, c)
        ctx.fill()
    cx, cy = W / 2, H / 2 + 30
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(t * 0.05)
    for k in range(32):
        a = k * math.pi / 16
        r1, r2 = 150, (560 if k % 2 == 0 else 470)
        w = 0.05
        ctx.move_to(math.cos(a - w) * r1, math.sin(a - w) * r1)
        ctx.line_to(math.cos(a) * r2, math.sin(a) * r2)
        ctx.line_to(math.cos(a + w) * r1, math.sin(a + w) * r1)
        ctx.close_path()
    set_rgba(ctx, P.ARG_SUN, 0.55)
    ctx.fill()
    ctx.restore()
    ctx.arc(cx, cy, 150, 0, 6.283)
    set_rgba(ctx, P.ARG_SUN, 0.95)
    ctx.fill()
    m = M.FlatMap(-59.2, -51.75, lerp(240, 262, S.u), cx, cy)
    ctx.save()
    ctx.translate(8, 10)
    m.land_path(ctx, ("falklands",))
    ctx.set_source_rgba(0.1, 0.12, 0.2, 0.5)
    ctx.fill()
    ctx.restore()
    m.land_path(ctx, ("falklands",))
    ctx.set_source_rgb(0.2, 0.4, 0.65)
    ctx.fill_preserve()
    ctx.set_line_width(3)
    ctx.set_source_rgb(0.08, 0.12, 0.25)
    ctx.stroke()
    a = ramp(t, 0.2, 0.8)
    draw_text(ctx, "LAS MALVINAS", W / 2, 210, "black", 130, (0.08, 0.12, 0.25), "cb", a, 0.03)
    draw_text(ctx, "SON ARGENTINAS", W / 2, 1010, "black", 110, (0.08, 0.12, 0.25), "cb", ramp(t, 0.8, 1.4), 0.03)


# ---------------------------------------------------------------- 7. UN / negotiations
def un_document(ctx, S):
    t = S.t
    paper(ctx, 5, (0.95, 0.93, 0.86), (0.55, 0.5, 0.35))
    ctx.save()
    camera(ctx, S, 1.02, 1.1, (0, 30), (0, -30))
    ctx.rotate(-0.012)
    draw_text(ctx, "UNITED NATIONS", W / 2, 150, "courier", 54, (0.1, 0.1, 0.12), "cb", 1, 0.25)
    draw_text(ctx, "GENERAL ASSEMBLY", W / 2, 205, "courier", 34, (0.1, 0.1, 0.12), "cb", 1, 0.25)
    ctx.rectangle(W / 2 - 330, 232, 660, 3)
    ctx.set_source_rgba(0.1, 0.1, 0.12, 0.8)
    ctx.fill()
    draw_text(ctx, "RESOLUTION 2065 (XX)  ·  16 DECEMBER 1965", W / 2, 300, "type", 38, (0.1, 0.1, 0.12), "cb")
    body = ("Invites the Governments of Argentina and the United Kingdom of Great Britain and Northern "
            "Ireland to proceed without delay with the negotiations ... with a view to finding a peaceful "
            "solution to the problem, bearing in mind ... the interests of the population of the Falkland "
            "Islands (Malvinas).")
    typewriter(ctx, body, 330, 400, 36, ramp(t, 0.3, 5.0), max_chars=58, seed=2)
    y = 760
    for i, (yr, txt) in enumerate((("1966-1981", "Talks drag on for fifteen years"),
                                   ("1980", "'Leaseback' plan proposed in London - and rejected"))):
        a = ramp(t, 2.0 + i * 1.2, 2.6 + i * 1.2)
        draw_text(ctx, yr, 330, y + i * 64, "type", 34, (0.55, 0.1, 0.1), "lb", a)
        draw_text(ctx, txt, 600, y + i * 64, "type", 34, (0.12, 0.1, 0.1), "lb", a)
    ts = S.word("road", 0, "but the")
    stamp(ctx, "ISLANDERS SAY NO", 1450, 900, 64, -0.12, ramp(t, ts, ts + 0.25))
    ctx.restore()


# ---------------------------------------------------------------- 8. HMS Endurance
def _iceberg(ctx, x, y, w, h, seed):
    pts = [(x - w / 2, y)]
    n = 7
    for i in range(1, n):
        u = i / n
        pts.append((x - w / 2 + w * u, y - h * (0.55 + 0.45 * hash01(seed, i)) * math.sin(u * math.pi) ** 0.4))
    pts.append((x + w / 2, y))
    poly(ctx, pts)
    ctx.set_source(vgrad(ctx, 0, y - h, 0, y, [(0, (0.97, 0.98, 1.0)), (1, (0.7, 0.8, 0.88))]))
    ctx.fill()
    poly(ctx, [(x, y), (x + w / 2, y)] + [(x - w / 2 + w * (i / n), pts[i][1]) for i in range(n - 1, n // 2, -1)])
    ctx.set_source_rgba(0.45, 0.6, 0.75, 0.35)
    ctx.fill()


def endurance(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.08, (30, 0), (-30, 0))
    hz = 620
    A.sky(ctx, [(0, hexc("7F97AD")), (0.7, hexc("C9D3DA")), (1, hexc("E6E7E2"))], hz)
    A.clouds(ctx, t, 60, 360, (0.95, 0.96, 0.97), seed=14, speed=6, lo=0.5, hi=0.85, alpha=0.7)
    A.ridge(ctx, 31, hz, 330, (0.62, 0.68, 0.76), rough=0.55, top_color=(0.97, 0.98, 1.0),
            shape=lambda u: 0.5 + 0.5 * math.sin(u * 3.0 + 0.5) ** 2)
    A.ridge(ctx, 32, hz + 2, 170, (0.4, 0.46, 0.54), rough=0.6, top_color=(0.9, 0.93, 0.97), x0=-100, x1=1200)
    A.sea(ctx, t, hz, hexc("5E7584"), hexc("122632"), seed=15, strokes=450, hi=(0.95, 0.97, 1), hi_alpha=0.22)
    _iceberg(ctx, 1500, hz + 10, 260, 90, 1)
    _iceberg(ctx, 260, hz + 30, 180, 60, 2)
    x = lerp(760, 980, S.u)
    y = 760
    V.wake(ctx, x, y, 640, 1, t, 0.4)
    V.ship(ctx, "endurance", x, y, 640, 1, (0.95, 0.95, 0.93), light=(0.75, 0.8, 0.9),
           hull_color=(0.72, 0.13, 0.1), upper_color=(0.93, 0.93, 0.9), roll=math.sin(t * 0.8) * 0.8,
           windows=((0.2, 0.24, 0.3), [(0.47, 0.74, 0.115, 0.018), (0.62, 0.74, 0.152, 0.012),
                                        (0.16, 0.4, 0.1, 0.03)]))
    _iceberg(ctx, 1750, 900, 380, 110, 3)
    A.snow(ctx, t, 0.5, 160)
    ctx.restore()
    lower_third(ctx, S, "HMS ENDURANCE", "Ice patrol ship · withdrawal announced, June 1981", t_in=0.8)


# ---------------------------------------------------------------- 9. Buenos Aires / Casa Rosada
def _palm(ctx, x, y, h, color, t, seed=0):
    ctx.set_line_width(h * 0.035)
    ctx.move_to(x, y)
    ctx.curve_to(x + h * 0.05, y - h * 0.4, x - h * 0.03, y - h * 0.7, x + h * 0.02, y - h)
    set_rgba(ctx, color)
    ctx.stroke()
    tx, ty = x + h * 0.02, y - h
    for k in range(11):
        a = -math.pi / 2 + (k - 5) * 0.34 + math.sin(t * 1.2 + k + seed) * 0.03
        L = h * (0.34 + 0.06 * hash01(seed, k))
        droop = h * 0.16 * abs(math.cos(a))
        ex, ey = tx + math.cos(a) * L, ty + math.sin(a) * L * 0.55 + droop
        mx, my = tx + math.cos(a) * L * 0.55, ty + math.sin(a) * L * 0.55 - h * 0.02
        nx, ny = -(ey - ty), (ex - tx)
        n = math.hypot(nx, ny) or 1
        nx, ny = nx / n * h * 0.03, ny / n * h * 0.03
        ctx.move_to(tx, ty)
        ctx.curve_to(mx + nx, my + ny, ex + nx * 0.3, ey + ny * 0.3, ex, ey)
        ctx.curve_to(ex - nx * 0.3, ey - ny * 0.3, mx - nx, my - ny, tx, ty)
        ctx.close_path()
        set_rgba(ctx, color)
        ctx.fill()


def casa_rosada(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.1, (0, 20), (0, -10))
    hz = 800
    A.sky(ctx, [(0, hexc("1E2140")), (0.55, hexc("6B4A6A")), (0.85, hexc("D98A62")), (1, hexc("F2B579"))], hz)
    A.clouds(ctx, t, 120, 420, (0.45, 0.3, 0.4), seed=41, speed=5, lo=0.5, hi=0.85, alpha=0.6)
    P.casa_rosada(ctx, 260, hz, 1400, 330, lit=0.9, win=(0.25, 0.16, 0.18))
    P.flagpole(ctx, "argentina", W / 2, hz - 330 * 1.34, 170, 150, t, amp=0.1)
    ctx.rectangle(0, hz, W, H - hz)
    ctx.set_source(vgrad(ctx, 0, hz, 0, H, [(0, hexc("3A2A30")), (1, hexc("120C10"))]))
    ctx.fill()
    for lx in (180, 560, 1360, 1740):
        ctx.set_line_width(6)
        ctx.move_to(lx, H)
        ctx.line_to(lx, 700)
        ctx.set_source_rgb(0.06, 0.05, 0.06)
        ctx.stroke()
        A.radial_glow(ctx, lx, 690, 70, (1.0, 0.8, 0.5), 0.8)
    _palm(ctx, 90, H, 520, (0.05, 0.04, 0.05), t, 1)
    _palm(ctx, 1830, H, 560, (0.05, 0.04, 0.05), t, 2)
    P.crowd(ctx, 300, 1620, H - 20, 150, t, (0.07, 0.05, 0.07), seed=5, density=0.7, wave=0.0, rows=2)
    ctx.restore()
    date_stamp(ctx, S, "BUENOS AIRES", t_in=0.3, t_out=S.at("junta", 0) - 0.2)
    lower_third(ctx, S, "GEN. LEOPOLDO GALTIERI", "Head of the junta · President from December 1981",
                t_in=S.at("junta", 0) + 0.3, accent=M.ARG)


# ---------------------------------------------------------------- 10. Mothers of the Plaza de Mayo
def madres(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.02, 1.1, (0, 0), (-40, 0))
    hz = 720
    A.sky(ctx, [(0, hexc("8C8F94")), (1, hexc("C9C8C2"))], hz)
    # Piramide de Mayo
    px = 1180
    poly(ctx, [(px - 70, hz), (px - 40, 330), (px, 290), (px + 40, 330), (px + 70, hz)])
    ctx.set_source(vgrad(ctx, 0, 290, 0, hz, [(0, (0.8, 0.8, 0.78)), (1, (0.62, 0.62, 0.6))]))
    ctx.fill()
    ctx.rectangle(px - 110, hz - 40, 220, 40)
    ctx.set_source_rgb(0.7, 0.7, 0.68)
    ctx.fill()
    ctx.rectangle(0, hz, W, H - hz)
    ctx.set_source(vgrad(ctx, 0, hz, 0, H, [(0, hexc("77736C")), (1, hexc("3B3935"))]))
    ctx.fill()
    # the painted headscarves on the plaza
    for k in range(10):
        x = 120 + k * 190 + (k % 2) * 40
        y = 1000 + (k % 3) * 20
        ctx.save()
        ctx.translate(x, y)
        ctx.scale(1, 0.35)
        ctx.arc(0, 0, 38, math.pi, 2 * math.pi)
        ctx.line_to(30, 40)
        ctx.line_to(-30, 40)
        ctx.close_path()
        ctx.restore()
        ctx.set_source_rgba(0.95, 0.95, 0.93, 0.8)
        ctx.fill()
    walk = t * 26
    for row, (y, h, col, n) in enumerate(((860, 280, (0.2, 0.2, 0.22), 9), (950, 340, (0.1, 0.1, 0.11), 7))):
        for i in range(n):
            x = (i * (W + 300) / n + walk * (1 if row else 0.7) + row * 90) % (W + 300) - 150
            P.standing_figure(ctx, x, y + math.sin(t * 4 + i) * 2, h * (0.92 + 0.12 * hash01(i, row)), col,
                              scarf=(0.96, 0.96, 0.94), placard=(0.93, 0.92, 0.88) if (i + row) % 2 == 0 else None,
                              seed=i + row * 10, face=(0.55, 0.45, 0.4))
    ctx.restore()
    a = ramp(t, 0.5, 1.0)
    if a > 0:
        bx, by = 1330, 90
        ctx.rectangle(bx - 60, by, 560, 170)
        ctx.set_source_rgba(0.97, 0.95, 0.9, 0.92 * a)
        ctx.fill()
        ctx.rectangle(bx - 60, by, 560, 170)
        ctx.set_line_width(3)
        ctx.set_source_rgba(0.1, 0.1, 0.1, a)
        ctx.stroke()
        draw_text(ctx, "INFLATION, 1981", bx - 32, by + 50, "cond", 30, (0.15, 0.15, 0.15), "lb", a, 0.1)
        draw_text(ctx, "OVER 100%", bx - 32, by + 140, "black", 76, (0.7, 0.1, 0.1), "lb", a)
    lower_third(ctx, S, "THE MOTHERS OF THE PLAZA DE MAYO", "Marching for the 'disappeared' of the Dirty War",
                t_in=1.2, accent=M.ARG)


# ---------------------------------------------------------------- 11. Malvinas rally
def rally(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.12, (0, 0), (30, 20))
    hz = 760
    A.sky(ctx, [(0, hexc("3E78B8")), (1, hexc("BFD6E8"))], hz)
    A.clouds(ctx, t, 60, 360, (1, 1, 1), seed=51, speed=9, lo=0.52, hi=0.8, alpha=0.8)
    P.casa_rosada(ctx, 300, hz, 1320, 300, color=hexc("E3A89C"), shadow=hexc("A86E62"))
    P.flagpole(ctx, "argentina", W / 2, hz - 300 * 1.34, 150, 140, t)
    ctx.rectangle(0, hz, W, H - hz)
    ctx.set_source_rgb(0.25, 0.22, 0.2)
    ctx.fill()
    P.crowd(ctx, -60, W + 60, 900, 190, t, (0.16, 0.14, 0.14), seed=8, density=0.8, wave=1.0,
            flags="argentina", flag_every=7, rows=3)
    P.crowd(ctx, -60, W + 60, H + 60, 260, t + 3, (0.08, 0.07, 0.07), seed=9, density=0.7, wave=1.0,
            flags="argentina", flag_every=6, rows=1)
    # banner held up over the front row
    by = 845 + math.sin(t * 2) * 6
    ctx.save()
    ctx.translate(W / 2 + 80, by)
    ctx.rotate(math.sin(t * 1.3) * 0.015)
    for sx in (-500, 500):
        ctx.rectangle(sx - 5, -60, 10, 300)
        ctx.set_source_rgb(0.08, 0.07, 0.07)
        ctx.fill()
    ctx.rectangle(-520, -70, 1040, 120)
    ctx.set_source_rgb(0.97, 0.96, 0.92)
    ctx.fill()
    draw_text(ctx, "MALVINAS ARGENTINAS", 0, 22, "black", 76, (0.12, 0.3, 0.6), "cb", 1, 0.02)
    ctx.restore()
    ctx.restore()
    date_stamp(ctx, S, "PLAZA DE MAYO", t_in=0.4)
