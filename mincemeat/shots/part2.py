"""The voyage, Huelva, the Germans deceived, Sicily, and the grave."""
import math

import cairo

from engine import art as A
from engine import people as P
from engine import vessels as V
from engine.core import (H, W, clamp, draw_text, ease_in_out, ease_out, hash01, hexc, lerp, mix, poly, radial_glow,
                         ramp, set_rgba, vgrad)
from ww2 import art as R
from ww2 import docs as D
from ww2 import maps as M
from .common import camera, card, plate, quote


# ---------------------------------------------------------------- 7. the drive north
def night_drive(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.06, (0, 0), (0, 10))
    A.sky(ctx, [(0, (0.06, 0.06, 0.08)), (1, (0.3, 0.3, 0.33))], 600)
    radial_glow(ctx, 1500, 160, 200, (0.9, 0.9, 1.0), 0.35)
    ctx.arc(1500, 160, 34, 0, 6.283)
    set_rgba(ctx, (0.92, 0.92, 0.9))
    ctx.fill()
    A.stars(ctx, 220, seed=71, alpha=0.6, y1=520, t=t)
    A.ridge(ctx, 72, 600, 90, (0.12, 0.12, 0.13), rough=0.5)
    ctx.rectangle(0, 600, W, H)
    set_rgba(ctx, (0.1, 0.1, 0.11))
    ctx.fill()
    # the road, running towards the horizon
    poly(ctx, [(880, 600), (1040, 600), (1700, H), (220, H)])
    set_rgba(ctx, (0.2, 0.2, 0.21))
    ctx.fill()
    for k in range(10):   # centre line rushing past
        u = ((k / 10) + t * 0.6) % 1.0
        y0 = lerp(600, H, u ** 2)
        y1 = lerp(600, H, min(1, (u + 0.03)) ** 2)
        w0 = lerp(2, 16, u)
        ctx.rectangle(W / 2 + 0 - w0 / 2, y0, w0, y1 - y0)
        set_rgba(ctx, (0.55, 0.55, 0.5), 0.6)
        ctx.fill()
    # trees flicking past
    for k in range(8):
        u = ((k / 8) + t * 0.35) % 1.0
        for side in (-1, 1):
            x = W / 2 + side * lerp(120, 1400, u ** 1.6)
            h = lerp(40, 900, u ** 1.6)
            y = lerp(600, H + 200, u ** 1.6)
            R.cypress(ctx, x, y, h, (0.05, 0.05, 0.06))
    # the van from behind: blackout-masked rear lamps, headlamp slits lighting the road ahead
    vx, vy = W / 2 + math.sin(t * 0.7) * 10, 880
    poly(ctx, [(vx - 190, vy + 160), (vx - 175, vy - 150), (vx + 175, vy - 150), (vx + 190, vy + 160)])
    set_rgba(ctx, (0.03, 0.03, 0.035))
    ctx.fill()
    ctx.rectangle(vx - 170, vy + 150, 340, 30)
    set_rgba(ctx, (0.03, 0.03, 0.03))
    ctx.fill()
    for side in (-1, 1):
        radial_glow(ctx, vx + side * 150, vy + 110, 26, (1, 0.2, 0.15), 0.8)
    g = cairo.LinearGradient(0, 600, 0, vy - 150)
    g.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.0)
    g.add_color_stop_rgba(1, 1, 0.95, 0.8, 0.25)
    poly(ctx, [(vx - 140, vy - 150), (vx + 140, vy - 150), (vx + 60, 620), (vx - 60, 620)])
    ctx.set_source(g)
    ctx.fill()
    ctx.restore()
    plate(ctx, S, "London to the Clyde, 17th–18th April 1943", "Driven by racing driver St John Horsfall",
          t_in=0.5)


# ---------------------------------------------------------------- 8. HMS Seraph sails
def seraph_sails(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.08, (20, 0), (-30, 0))
    hz = 600
    A.sky(ctx, [(0, (0.4, 0.42, 0.45)), (1, (0.8, 0.8, 0.78))], hz)
    A.clouds(ctx, t, 60, 420, (0.92, 0.92, 0.92), seed=81, speed=10, lo=0.45, hi=0.8, alpha=0.7)
    A.ridge(ctx, 82, hz, 200, (0.3, 0.31, 0.3), rough=0.55, x0=-50, x1=1100, top_color=(0.45, 0.46, 0.44))
    A.ridge(ctx, 83, hz, 120, (0.38, 0.39, 0.38), rough=0.5, x0=900, x1=W + 50)
    A.sea(ctx, t, hz, (0.45, 0.47, 0.48), (0.12, 0.13, 0.14), seed=84, strokes=420, hi=(1, 1, 1), hi_alpha=0.18)
    x = lerp(760, 1100, S.u)
    V.wake(ctx, x, 760, 900, 1, t, 0.35)
    R.submarine(ctx, x, 760, 900, 1, (0.1, 0.105, 0.11), crew=3, t=t)
    ctx.restore()
    plate(ctx, S, "H.M. Submarine Seraph", "Sails from the Clyde, 19th April 1943 · Lt Bill Jewell", t_in=0.5)


def route_map(ctx, S):
    t = S.t
    mp = M.Map(-6.0, 46.5, 48)
    M.base(ctx, mp)
    for n in ("SPAIN", "FRANCE", "PORTUGAL"):
        M.label(ctx, mp, n, size=34, alpha=0.7, font="oldstd", tracking=0.3)
    # schematic track: down the Clyde, round the north of Ireland, then south into the Atlantic
    pts = [mp.p("HOLY LOCH"), mp.xy(-5.1, 55.4), mp.xy(-6.6, 55.75), mp.xy(-9.8, 55.0), mp.xy(-11.8, 52.5),
           mp.xy(-12.5, 46.0), mp.xy(-10.8, 40.5), mp.xy(-9.6, 37.0), mp.xy(-7.4, 36.95)]
    M.arrow(ctx, pts, ease_in_out(ramp(t, 0.2, 2.8)), M.INK, 12)
    M.label(ctx, mp, "HOLY LOCH", dx=30, dy=0, size=30, anchor="lm", dot=True, alpha=ramp(t, 0.2, 0.6))
    M.label(ctx, mp, "HUELVA", dx=26, dy=-10, size=34, anchor="lm", dot=True, color=M.RED, alpha=ramp(t, 2.4, 2.9))
    M.label(ctx, mp, "GIBRALTAR", dx=10, dy=40, size=26, anchor="lm", dot=True, alpha=ramp(t, 2.4, 2.9))
    M.title_box(ctx, "Holy Loch to Huelva", "19th–30th April 1943", ramp(t, 0.2, 0.7))


# ---------------------------------------------------------------- 9. 04.30, 30th April
def release(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.1, (0, 0), (30, 10))
    hz = 560
    A.sky(ctx, [(0, (0.08, 0.08, 0.1)), (0.8, (0.25, 0.25, 0.28)), (1, (0.4, 0.38, 0.38))], hz)
    A.sun(ctx, 420, 200, 30, (0.92, 0.92, 0.9), glow=6, alpha=0.9)
    A.stars(ctx, 260, seed=91, alpha=0.7, y1=hz, t=t)
    # the lights of Huelva on the horizon
    for k in range(26):
        lx = 900 + k * 34 + hash01(k, 1) * 20
        radial_glow(ctx, lx, hz - 3, 7, (1, 0.9, 0.7), 0.6 * (0.6 + 0.4 * math.sin(t * 2 + k)))
    A.sea(ctx, t, hz, (0.26, 0.26, 0.28), (0.06, 0.06, 0.07), seed=92, strokes=450, hi=(0.9, 0.9, 0.95),
          hi_alpha=0.25)
    A.reflection(ctx, 420, hz, 160, (0.92, 0.92, 0.9), 0.3, t, rows=18)
    R.submarine(ctx, 800, 780, 1300, -1, (0.02, 0.02, 0.025), crew=5, t=t, deck_load=True)
    ctx.restore()
    plate(ctx, S, "04.30, 30th April 1943", "Off Huelva: Psalm 39 is read, and the body committed to the sea",
          t_in=0.5)


# ---------------------------------------------------------------- 10. Huelva
def huelva(ctx, S):
    t = S.t
    t_bur = S.at("spain", 1)
    ctx.save()
    if t < t_bur - 0.3:
        camera(ctx, S, 1.0, 1.06, (0, 0), (-30, 0))
        hz = 640
        A.sky(ctx, [(0, (0.5, 0.55, 0.6)), (1, (0.9, 0.9, 0.88))], hz)
        R.spanish_town(ctx, hz, -40, W + 40, seed=5)
        for k, px in enumerate((150, 640, 1300, 1780)):
            R.palm(ctx, px, hz + 30, 300 + 60 * hash01(k, 3), (0.2, 0.2, 0.2), t, seed=k)
        ctx.rectangle(0, hz, W, H)
        set_rgba(ctx, (0.62, 0.6, 0.55))
        ctx.fill()
        for i in range(6):   # townspeople in the square
            P.standing_figure(ctx, 300 + i * 260 + math.sin(t * 0.3 + i) * 20, 980, 280, (0.12, 0.12, 0.12), seed=i)
        ctx.restore()
        plate(ctx, S, "Huelva, Andalusia", "Neutral Spain: home to German agents and informers", t_in=0.5,
              t_out=t_bur - 0.3)
        return
    camera(ctx, S, 1.02, 1.08, (0, 0), (0, 10))
    hz = 700
    A.sky(ctx, [(0, (0.55, 0.58, 0.62)), (1, (0.9, 0.88, 0.84))], hz)
    # cemetery wall and cypresses
    ctx.rectangle(0, hz - 140, W, 140)
    set_rgba(ctx, (0.85, 0.84, 0.8))
    ctx.fill()
    for k in range(6):
        R.cypress(ctx, 150 + k * 330, hz - 60, 380 + 80 * hash01(k, 2), (0.3, 0.33, 0.3))
    ctx.rectangle(0, hz, W, H)
    set_rgba(ctx, (0.6, 0.58, 0.52))
    ctx.fill()
    # coffin under the Union flag, bearers, mourners
    cx = W / 2
    ctx.rectangle(cx - 220, 820, 440, 70)
    set_rgba(ctx, (0.25, 0.2, 0.16))
    ctx.fill()
    ctx.save()
    ctx.rectangle(cx - 230, 800, 460, 40)
    ctx.clip()
    P.flag(ctx, "union", cx - 230, 800, 460, 230, 0.0, amp=0.0)
    ctx.restore()
    for i in range(4):
        P.standing_figure(ctx, cx - 180 + i * 120, 1000, 300, (0.1, 0.1, 0.1), seed=i + 10)
    for i in range(7):
        P.standing_figure(ctx, 120 + i * 90 + (i > 3) * 1150, 1040, 330, (0.14, 0.14, 0.14), seed=i + 20)
    ctx.restore()
    plate(ctx, S, "Nuestra Señora de la Soledad cemetery", "2nd May 1943: buried with military honours",
          t_in=0.4)


def photographing(ctx, S):
    t = S.t
    D.desk(ctx, 14)
    ctx.save()
    camera(ctx, S, 1.0, 1.1, (0, 0), (0, -20))
    D.sheet(ctx, 520, 300, 820, 620, angle=0.0, seed=31)
    D.typed(ctx, ["WAR OFFICE,", "WHITEHALL, LONDON, S.W.1.", "", "My dear Alex,"], 80, 80, 30)
    ctx.set_line_width(2)
    for k in range(8):
        ctx.move_to(80, 300 + k * 36)
        ctx.line_to(740, 300 + k * 36)
    set_rgba(ctx, D.INK, 0.35)
    ctx.stroke()
    ctx.restore()
    # copy camera on a stand above the letter
    ctx.set_line_width(18)
    ctx.move_to(1560, 1080)
    ctx.line_to(1560, 120)
    ctx.line_to(1160, 120)
    set_rgba(ctx, (0.06, 0.06, 0.06))
    ctx.stroke()
    ctx.rectangle(1040, 120, 240, 150)
    ctx.fill()
    ctx.rectangle(1110, 270, 100, 60)
    ctx.fill()
    # flash of the copy lamps each time a page is photographed
    k = (t % 2.2)
    if k < 0.15:
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgba(1, 1, 1, 0.35 * (1 - k / 0.15))
        ctx.fill()
    ctx.restore()
    D.lamp_light(ctx, 930, 600, 1000, 0.55)
    plate(ctx, S, "Opened, copied, resealed", "The copies went to the Abwehr, and on to Berlin", t_in=0.5)


# ---------------------------------------------------------------- 11. swallowed
def signal(ctx, S):
    t = S.t
    t_msg = S.at("swallowed", 1)
    D.desk(ctx, 17)
    ctx.save()
    camera(ctx, S, 1.0, 1.08, (0, 0), (0, -10))
    D.signal_form(ctx, 260, 120, 1400, 820, "MOST SECRET  ·  SIGNAL",
                  ["MINCEMEAT SWALLOWED", "ROD LINE AND SINKER"], progress=ramp(t, t_msg - 0.2, t_msg + 2.2))
    ctx.restore()
    D.stamp(ctx, "ULTRA", 1500, 860, 60, -0.1, ramp(t, 0.8, 1.1))
    D.lamp_light(ctx, W / 2, 500, 1100, 0.5)
    plate(ctx, S, "Decrypts from Bletchley Park", "German signals show the documents were believed", t_in=0.4,
          t_out=t_msg - 0.2)


def german_moves(ctx, S):
    t = S.t
    mp = M.Map(12.0, 43.0, 44)
    M.base(ctx, mp)
    for n in ("FRANCE", "ITALY", "GREECE", "SPAIN"):
        M.label(ctx, mp, n, size=32, alpha=0.7, font="oldstd", tracking=0.3)
    M.arrow(ctx, [mp.xy(1.0, 44.5), mp.xy(8.0, 45.8), mp.xy(15.5, 44.0), mp.xy(21.0, 40.5)],
            ease_in_out(ramp(t, 0.3, 3.0)), M.AXIS, 16)
    x, y = mp.xy(9.5, 46.6)
    draw_text(ctx, "1st Panzer Division: France to Greece", x, y - 20, "oldstd_b", 36, M.INK, "cb",
              ramp(t, 1.5, 2.0), 0.05)
    for i, (ll, txt, dx) in enumerate((((9.0, 40.1), "SARDINIA reinforced", -60), ((22.0, 38.3), "GREECE reinforced", 60))):
        x, y = mp.xy(*ll)
        a = ramp(t, 2.6 + i * 0.5, 3.1 + i * 0.5)
        ctx.arc(x, y, 70, 0, 6.283)
        ctx.set_line_width(6)
        set_rgba(ctx, M.AXIS, a)
        ctx.stroke()
        draw_text(ctx, txt, x + dx, y + 115, "oldstd_b", 34, M.INK, "rb" if dx < 0 else "lb", a, 0.05)
    x, y = mp.p("SICILY")
    draw_text(ctx, "SICILY", x, y + 10, "oldstd_b", 34, M.RED, "cm", ramp(t, 3.4, 3.9), 0.1)
    M.title_box(ctx, "The German Response", "May–June 1943", ramp(t, 0.2, 0.7))


# ---------------------------------------------------------------- 12. Sicily
def landings(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.08, (0, 0), (-40, 0))
    hz = 560
    A.sky(ctx, [(0, (0.3, 0.3, 0.32)), (1, (0.85, 0.82, 0.76))], hz)
    A.clouds(ctx, t, 60, 360, (0.9, 0.9, 0.9), seed=121, speed=6, lo=0.5, hi=0.85, alpha=0.5)
    A.ridge(ctx, 122, hz, 110, (0.35, 0.34, 0.32), rough=0.5, top_color=(0.5, 0.49, 0.46))
    A.sea(ctx, t, hz, (0.55, 0.56, 0.56), (0.15, 0.16, 0.17), seed=123, strokes=480, hi=(1, 1, 1), hi_alpha=0.2)
    for k, (sx, L) in enumerate(((300, 420), (1500, 520), (950, 360))):   # the invasion fleet offshore
        V.ship(ctx, "type21" if k != 1 else "canberra", sx, hz + 18, L, 1, (0.2, 0.2, 0.21))
    for k in range(5):
        R.landing_craft(ctx, 200 + k * 360 + t * 40, 760 + (k % 2) * 60, 280, t + k, (0.1, 0.1, 0.1))
    for k in range(4):
        x = 220 + k * 430
        A.smoke(ctx, x, hz + 10, t, seed=k, rate=3, life=10, rise=20, size=40, alpha=0.35, wind=12,
                color=(0.5, 0.5, 0.5))
    ctx.restore()
    plate(ctx, S, "Sicily, 10th July 1943", "Operation Husky", t_in=0.5)


def sicily_map(ctx, S):
    t = S.t
    mp = M.Map(14.4, 37.6, 330)
    M.base(ctx, mp, grid=1.0)
    for i, (ll, via) in enumerate((((14.25, 37.07), (14.2, 36.6)), ((13.94, 37.1), (13.8, 36.6)),
                                   ((15.29, 37.07), (15.7, 36.7)), ((15.1, 36.8), (15.4, 36.4)))):
        M.arrow(ctx, [mp.xy(*via), mp.xy(*ll)], ease_in_out(ramp(t, 0.2 + i * 0.25, 1.4 + i * 0.25)), M.RED, 14)
    for n, dx, dy, anc in (("GELA", 0, 50, "cm"), ("LICATA", -10, 50, "rm"), ("SYRACUSE", 20, 0, "lm"),
                           ("PALERMO", 0, -40, "cm"), ("MESSINA", 20, 0, "lm")):
        M.label(ctx, mp, n, dx=dx, dy=dy, size=28, anchor=anc, dot=True, alpha=ramp(t, 0.5, 1.0))
    a = ramp(t, 2.0, 2.6)
    draw_text(ctx, "38 days", W - 120, 870, "oldstd_b", 110, M.INK, "rb", a)
    draw_text(ctx, "10th July – 17th August 1943", W - 120, 930, "courier_r", 34, M.INK, "rb", a)
    M.title_box(ctx, "The Invasion of Sicily", None, ramp(t, 0.2, 0.7))


def howard(ctx, S):
    quote(ctx, S, ["...perhaps the most successful", "single deception operation", "of the entire war."],
          "Sir Michael Howard, official historian of British wartime deception")


# ---------------------------------------------------------------- 13. the grave
def grave(ctx, S):
    t = S.t
    t_98 = S.at("legacy", 1)
    ctx.save()
    camera(ctx, S, 1.0, 1.06, (0, 0), (0, 20))
    hz = 620
    A.sky(ctx, [(0, hexc("5E7DA8")), (0.6, hexc("E3C29A")), (1, hexc("F2D6A8"))], hz)
    A.sun(ctx, 1600, hz - 20, 40, (1, 0.92, 0.72), glow=5)
    ctx.rectangle(0, hz - 160, W, 160)
    set_rgba(ctx, hexc("E8E1D2"))
    ctx.fill()
    for k in range(6):
        R.cypress(ctx, 120 + k * 336, hz - 60, 420 + 80 * hash01(k, 5), hexc("3F5A3B"))
    ctx.rectangle(0, hz, W, H)
    ctx.set_source(vgrad(ctx, 0, hz, 0, H, [(0, hexc("B9A98A")), (1, hexc("7A6A50"))]))
    ctx.fill()
    ctx.rectangle(W / 2 - 360, 1000, 720, 80)
    set_rgba(ctx, hexc("D8D2C4"))
    ctx.fill()
    lines = [("WILLIAM MARTIN", 0.07), ("BORN 29TH MARCH 1907", 0.04), ("DIED 24TH APRIL 1943", 0.04),
             ("BELOVED SON OF JOHN GLYNDWYR MARTIN", 0.032), ("AND THE LATE ANTONIA MARTIN", 0.032),
             ("OF CARDIFF, WALES", 0.032), ("DULCE ET DECORUM EST", 0.034), ("PRO PATRIA MORI", 0.034),
             ("R.I.P.", 0.034)]
    extra = [("GLYNDWR MICHAEL;", 0.04), ("SERVED AS MAJOR WILLIAM MARTIN, RM", 0.032)]
    R.headstone_huelva(ctx, W / 2, 1010, 720, lines, extra, ramp(t, t_98 + 0.3, t_98 + 1.2), t)
    ctx.restore()
    plate(ctx, S, "Huelva, today", "The grave is cared for by the Commonwealth War Graves Commission", t_in=0.6,
          t_out=t_98 - 0.1)


def end_card(ctx, S):
    card(ctx, S, ["In memory of Glyndwr Michael", "1909 – 1943", "",
                  "Sources and further reading in the description.",
                  "Documents shown are reconstructions."], [66, 44, 30, 34, 30],
         ["oldstd", "oldstd", "oldstd", "courier_r", "courier_r"], fade_out=False)
