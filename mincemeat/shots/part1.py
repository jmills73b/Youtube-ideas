"""Opening, the problem, the idea, Glyndwr Michael, Major Martin, the letters."""
import math

import cairo

from engine import art as A
from engine import people as P
from engine.core import (H, W, clamp, draw_text, ease_in_out, ease_out, hash01, hexc, lerp, mix, poly, radial_glow,
                         ramp, set_rgba, vgrad)
from ww2 import art as R
from ww2 import docs as D
from ww2 import maps as M
from .common import camera, card, plate, quote


# ---------------------------------------------------------------- 1. dawn off Huelva
def dawn_sea(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.1, (0, 20), (-40, 0))
    hz = 560
    A.sky(ctx, [(0, (0.3, 0.32, 0.36)), (0.7, (0.75, 0.74, 0.72)), (1, (0.95, 0.9, 0.82))], hz)
    A.clouds(ctx, t, 80, 380, (0.95, 0.95, 0.95), seed=601, speed=5, lo=0.5, hi=0.85, alpha=0.6)
    A.sun(ctx, 1450, hz + 6, 34, (1, 0.97, 0.9), glow=5, alpha=0.8)
    # the low coast by Punta Umbria, the town beyond
    ctx.move_to(-20, hz + 4)
    ctx.curve_to(400, hz - 12, 900, hz - 18, 1300, hz - 6)
    ctx.line_to(1300, hz + 6)
    ctx.line_to(-20, hz + 6)
    ctx.close_path()
    set_rgba(ctx, (0.35, 0.34, 0.32))
    ctx.fill()
    R.spanish_town(ctx, hz - 4, 150, 700, (0.55, 0.54, 0.5), (0.4, 0.38, 0.35), seed=2)
    A.sea(ctx, t, hz, (0.62, 0.62, 0.6), (0.18, 0.19, 0.2), seed=602, strokes=520, hi=(1, 1, 1), hi_alpha=0.22)
    A.reflection(ctx, 1450, hz, 180, (1, 0.97, 0.9), 0.35, t)
    R.fishing_boat(ctx, lerp(760, 880, S.u), 700, 220, t, (0.14, 0.14, 0.14))
    # something floating: a life jacket, far off, rising and falling
    fx, fy = 1180, 780 + math.sin(t * 1.3) * 6
    ctx.save()
    ctx.translate(fx, fy)
    ctx.scale(1, 0.35)
    ctx.arc(0, 0, 26, 0, 6.283)
    ctx.restore()
    set_rgba(ctx, (0.75, 0.74, 0.7))
    ctx.fill()
    ctx.restore()
    plate(ctx, S, "Off Huelva, Spain", "30th April 1943", t_in=1.0)


def title(ctx, S):
    t = S.t
    D.desk(ctx)
    D.folder(ctx, 460, 150, 1000, 760, "OPERATION MINCEMEAT", "N.I.D. 17(M)  ·  1943", angle=-0.03)
    D.stamp(ctx, "MOST SECRET", 1250, 290, 64, -0.18, ramp(t, 0.5, 0.8))
    D.lamp_light(ctx, W / 2, 500, 1100, 0.6)


# ---------------------------------------------------------------- 2. the problem
def med_map(ctx, S):
    t = S.t
    t_q = S.at("problem", 1)
    mp = M.Map(lerp(10.0, 12.0, S.u), 38.5, lerp(58, 66, ease_in_out(S.u)))
    M.base(ctx, mp)
    for n in ("SPAIN", "FRANCE", "ITALY", "ALGERIA", "TUNISIA", "GREECE"):
        M.label(ctx, mp, n, size=34, alpha=0.7, font="oldstd", tracking=0.3)
    a = ramp(t, 0.3, 0.9)
    x, y = mp.p("TUNIS")
    draw_text(ctx, "Axis surrender in Tunisia: May 1943", x - 40, y + 120, "courier_r", 32, M.INK, "cm", a)
    M.arrow(ctx, [mp.p("TUNIS"), mp.xy(12.4, 37.1), mp.xy(13.8, 37.2)], ease_in_out(ramp(t, 1.0, 3.0)), M.INK, 18)
    x, y = mp.p("SICILY")
    ctx.arc(x, y, 95, 0, 6.283)
    ctx.set_line_width(6)
    set_rgba(ctx, M.RED, ramp(t, 2.6, 3.2))
    ctx.stroke()
    M.label(ctx, mp, "SICILY", dy=-120, size=44, color=M.RED, alpha=ramp(t, 2.6, 3.2))
    M.title_box(ctx, "The Next Target", "Allied planning, early 1943", ramp(t, 0.2, 0.7))
    a = ramp(t, t_q, t_q + 0.5)
    if a > 0:
        ctx.rectangle(0, 0, W, H)
        ctx.set_source_rgba(0, 0, 0, 0.72 * a)
        ctx.fill()
        draw_text(ctx, "“Everybody but a bloody fool", W / 2, 480, "oldstd", 76, (0.96, 0.95, 0.9), "cb", a)
        draw_text(ctx, "would know that it's Sicily.”", W / 2, 580, "oldstd", 76, (0.96, 0.95, 0.9), "cb", a)
        draw_text(ctx, "Attributed to Winston Churchill", W / 2, 690, "courier_r", 36, (0.8, 0.8, 0.76), "cb",
                  ramp(t, t_q + 0.8, t_q + 1.3))


def threats_map(ctx, S):
    t = S.t
    mp = M.Map(14.5, 38.6, 64)
    M.base(ctx, mp)
    for n in ("SPAIN", "FRANCE", "ITALY", "TUNISIA", "GREECE"):
        M.label(ctx, mp, n, size=34, alpha=0.7, font="oldstd", tracking=0.3)
    src = mp.xy(12.0, 34.0)
    for i, (tgt, name) in enumerate(((mp.xy(9.8, 39.6), "SARDINIA ?"), (mp.xy(21.2, 37.6), "GREECE ?"))):
        M.arrow(ctx, [src, ((src[0] + tgt[0]) / 2, (src[1] + tgt[1]) / 2 - 60), tgt],
                ease_in_out(ramp(t, 0.3 + i * 0.5, 2.0 + i * 0.5)), M.INK, 16, dashed=True)
        draw_text(ctx, name, tgt[0], tgt[1] - 70, "oldstd_b", 44, M.INK, "cm", ramp(t, 1.8 + i * 0.5, 2.3 + i * 0.5),
                  0.1)
    M.title_box(ctx, "The Deception", "Make the enemy look elsewhere", ramp(t, 0.2, 0.7))


# ---------------------------------------------------------------- 3. the idea
def trout_memo(ctx, S):
    t = S.t
    t2 = S.at("idea", 1)
    D.desk(ctx, 5)
    ctx.save()
    camera(ctx, S, 1.0, 1.12, (0, 40), (0, -60))
    D.sheet(ctx, 410, 40, 1100, 1300, angle=0.015, seed=3)
    D.typed(ctx, ["NAVAL INTELLIGENCE DIVISION", "", "Memorandum on deception, September 1939",
                  "(the 'Trout Memo')"], 110, 120, 32, progress=ramp(t, 0.2, 2.0))
    ctx.move_to(110, 300)
    ctx.line_to(990, 300)
    ctx.set_line_width(2)
    set_rgba(ctx, D.INK, 0.6)
    ctx.stroke()
    D.typed(ctx, ["[ likens deception to trout fishing, and lists", "  some fifty schemes ]"], 110, 380,
            30, progress=ramp(t, 1.2, 3.2), seed=2, color=(0.45, 0.1, 0.08))
    D.typed(ctx, ["No. 28.  A suggestion (not a very nice one).", "",
                  "...a corpse dressed as an airman, with", "despatches in his pockets, could be dropped",
                  "on the coast..."], 110, 560, 32, progress=ramp(t, t2 - 0.2, t2 + 3.0), seed=4)
    ctx.restore()
    ctx.restore()
    D.lamp_light(ctx, W / 2, 500, 1100, 0.55)
    plate(ctx, S, "The Trout Memo, 1939", "Issued under Admiral John Godfrey; credited to Ian Fleming", t_in=0.8,
          t_out=t2 - 0.2)


def office(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.08, (0, 0), (-30, 10))
    R.office(ctx, t)
    ctx.restore()
    plate(ctx, S, "Cholmondeley (MI5) and Montagu (Naval Intelligence)", "London, 1943", t_in=0.6)


# ---------------------------------------------------------------- 4. Glyndwr Michael
def london(ctx, S):
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.1, (20, 0), (-40, 0))
    R.london_street(ctx, t)
    ctx.restore()
    plate(ctx, S, "St Pancras, London", "January 1943", t_in=0.5, t_out=S.at("michael", 1) - 0.1)
    plate(ctx, S, "Glyndwr Michael", "Born Aberbargoed, Wales, 1909 · died January 1943",
          t_in=S.at("michael", 1) + 0.3)


# ---------------------------------------------------------------- 5. Major William Martin
def wallet(ctx, S):
    t = S.t
    t_items = S.at("martin", 1)
    t_pam = S.at("martin", 2)
    D.desk(ctx, 8)
    ctx.save()
    camera(ctx, S, 1.0, 1.1, (0, 0), (-60, 20))
    # identity card
    D.sheet(ctx, 180, 160, 560, 360, angle=-0.05, tone=(0.88, 0.86, 0.8), seed=4)
    draw_text(ctx, "NAVAL IDENTITY CARD", 280, 60, "oldstd_b", 32, D.INK, "cb", 0.9, 0.1)
    D.typed(ctx, ["Rank: Captain (A/Major) R.M.", "Name: W. MARTIN", "Ship: H.Q. Combined Ops."], 150, 130, 22,
            progress=ramp(t, 0.3, 2.2))
    D.portrait_photo(ctx, 20, 100, 110, 150, 0.0, sitter="man")
    ctx.restore()
    items = [
        (lambda: D.portrait_photo(ctx, 900, 120, 230, 300, 0.08, "woman", "Pam"), 0.0),
        (lambda: _letter(ctx, 1200, 160, "My darling...", "Pam", 0.12), 0.8),
        (lambda: D.ticket(ctx, 820, 560, -0.2, "PRINCE OF WALES THEATRE", "STALLS", "22 APR 1943"), 2.2),
        (lambda: D.ticket(ctx, 900, 610, 0.1, "PRINCE OF WALES THEATRE", "STALLS", "22 APR 1943"), 2.4),
        (lambda: _bill(ctx, 1320, 560, "S.J. PHILLIPS, JEWELLERS", ["1 Diamond Engagement Ring"], -0.06), 3.2),
        (lambda: _bill(ctx, 260, 620, "LLOYDS BANK LIMITED", ["...your overdraft of", "£79. 19s. 2d."], 0.05), 4.6),
    ]
    for fn, dt in items:
        if t > t_items + dt:
            fn()
    ctx.restore()
    D.lamp_light(ctx, W / 2, 500, 1200, 0.5)
    plate(ctx, S, "Captain (Acting Major) William Martin, R.M.", "A life built from paper", t_in=0.5,
          t_out=t_items - 0.1)
    plate(ctx, S, "“Pam”", "Photograph posed by MI5 clerk Jean Leslie", t_in=t_pam)


def _letter(ctx, x, y, first, sign, angle):
    D.sheet(ctx, x, y, 420, 520, angle, (0.95, 0.94, 0.9), seed=9)
    draw_text(ctx, first, 40, 80, "oldstd", 34, (0.15, 0.15, 0.35), "lb", 0.9)
    ctx.set_line_width(1.6)
    for k in range(9):
        ctx.move_to(40, 130 + k * 40)
        for xx in range(40, 380, 20):
            ctx.line_to(xx, 130 + k * 40 + math.sin(xx * 0.3 + k) * 4)
    set_rgba(ctx, (0.15, 0.15, 0.35), 0.7)
    ctx.stroke()
    draw_text(ctx, sign, 300, 490, "oldstd", 38, (0.15, 0.15, 0.35), "lb", 0.9)
    ctx.restore()


def _bill(ctx, x, y, head, lines, angle):
    D.sheet(ctx, x, y, 460, 300, angle, (0.94, 0.93, 0.88), seed=12)
    draw_text(ctx, head, 230, 60, "oldstd_b", 28, D.INK, "cb", 0.9, 0.06)
    ctx.move_to(30, 80)
    ctx.line_to(430, 80)
    ctx.set_line_width(2)
    set_rgba(ctx, D.INK, 0.6)
    ctx.stroke()
    for i, l in enumerate(lines):
        draw_text(ctx, l, 40, 140 + i * 50, "courier_r", 28, D.INK, "lb", 0.9)
    ctx.restore()


# ---------------------------------------------------------------- 6. the letters
def letters(ctx, S):
    t = S.t
    t_mb = S.at("letters", 2)
    D.desk(ctx, 11)
    ctx.save()
    if t < t_mb - 0.3:
        camera(ctx, S, 1.0, 1.06, (0, 0), (0, -30))
        D.sheet(ctx, 360, 30, 1200, 1400, angle=-0.01, seed=21)
        D.typed(ctx, ["WAR OFFICE,", "WHITEHALL, LONDON, S.W.1.", "", "23rd April, 1943.", "",
                      "PERSONAL AND MOST SECRET.", "", "My dear Alex,", "",
                      "I am taking advantage of sending you a", "personal letter by hand of one of",
                      "Mountbatten's officers, to give you the", "inside history of our recent exchange of",
                      "cables about Mediterranean operations", "and their attendant cover plans..."], 120, 110, 30,
                progress=ramp(t, 0.2, 5.0))
        a = ramp(t, S.at("letters", 1) - 0.2, S.at("letters", 1) + 0.4)
        draw_text(ctx, "[ the letter goes on to discuss landings in Greece,", 120, 870, "courier_r", 30,
                  (0.45, 0.1, 0.08), "lb", a)
        draw_text(ctx, "  with Sicily as the cover target ]", 120, 915, "courier_r", 30, (0.45, 0.1, 0.08), "lb", a)
        draw_text(ctx, "Archie Nye", 780, 1010, "oldstd", 44, (0.12, 0.12, 0.3), "lb", ramp(t, 4.6, 5.1))
        ctx.restore()
    else:
        tt = t - t_mb
        D.sheet(ctx, 330, 60, 1260, 900, angle=0.02, seed=22)
        D.typed(ctx, ["COMBINED OPERATIONS HEADQUARTERS,", "1A, RICHMOND TERRACE,", "WHITEHALL, S.W.1.",
                      "", "21st April, 1943.", "", "Dear Admiral of the Fleet,"], 120, 110, 30,
                progress=ramp(tt, 0.0, 1.2))
        line = "He might bring some sardines with him - they are \"on points\" here!"
        D.typed(ctx, [line], 120, 600, 32, progress=ramp(tt, 1.0, 3.0), seed=5)
        a = ramp(tt, 3.0, 3.6)
        ctx.rectangle(110, 570, 1100 * a, 42)
        ctx.set_source_rgba(0.95, 0.85, 0.2, 0.35)
        ctx.fill()
        draw_text(ctx, "Yours sincerely, Louis Mountbatten", 520, 760, "oldstd", 40, (0.12, 0.12, 0.3), "lb",
                  ramp(tt, 2.0, 2.5))
        ctx.restore()
        D.stamp(ctx, "SARDINES = SARDINIA ?", 1450, 870, 44, -0.1, ramp(tt, 3.6, 3.9))
    D.lamp_light(ctx, W / 2, 500, 1200, 0.45)
    plate(ctx, S, "Lt-Gen. Sir Archibald Nye to Gen. Sir Harold Alexander", "Reconstruction of the planted letter (opening words verbatim)",
          t_in=0.6, t_out=t_mb - 0.3)
    plate(ctx, S, "Lord Louis Mountbatten to Admiral Sir Andrew Cunningham", "Chief of Combined Operations",
          t_in=t_mb + 0.3)


def briefcase(ctx, S):
    """Close on the water: a black leather briefcase, its chain running down out of sight."""
    t = S.t
    ctx.save()
    camera(ctx, S, 1.0, 1.12, (0, 0), (0, 20))
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(vgrad(ctx, 0, 0, 0, H, [(0, (0.55, 0.56, 0.56)), (1, (0.2, 0.21, 0.22))]))
    ctx.fill()
    A.sea(ctx, t, 0, (0.52, 0.53, 0.54), (0.2, 0.21, 0.22), seed=611, strokes=700, hi=(1, 1, 1), hi_alpha=0.3,
          speed=0.4, chop=2.0)
    bob = math.sin(t * 1.2) * 10
    rot = math.sin(t * 0.9) * 0.05
    ctx.save()
    ctx.translate(W / 2, 560 + bob)
    ctx.rotate(-0.12 + rot)
    # case body, flap and brass lock
    ctx.rectangle(-300, -190, 600, 380)
    set_rgba(ctx, (0.08, 0.075, 0.07))
    ctx.fill()
    ctx.rectangle(-300, -190, 600, 130)
    set_rgba(ctx, (0.12, 0.11, 0.1))
    ctx.fill()
    ctx.rectangle(-26, -70, 52, 34)
    set_rgba(ctx, (0.6, 0.55, 0.4))
    ctx.fill()
    ctx.set_line_width(12)
    ctx.move_to(-90, -190)
    ctx.curve_to(-90, -280, 90, -280, 90, -190)
    set_rgba(ctx, (0.08, 0.075, 0.07))
    ctx.stroke()
    # chain from the handle down into the water
    for k in range(16):
        cx = -60 - k * 22
        cy = -230 + k * 28 + math.sin(t * 2 + k * 0.6) * 3
        ctx.save()
        ctx.translate(cx, cy)
        ctx.rotate(0.9 + (k % 2) * 0.6)
        ctx.scale(1, 0.55)
        ctx.arc(0, 0, 13, 0, 6.283)
        ctx.restore()
        ctx.set_line_width(5)
        set_rgba(ctx, (0.45, 0.45, 0.45), max(0.0, 1 - k / 14))
        ctx.stroke()
    ctx.restore()
    # water washing over the lower edge
    wl = 700 + bob * 0.5
    ctx.move_to(-20, H + 20)
    for x in range(-20, W + 40, 20):
        ctx.line_to(x, wl + math.sin(x * 0.012 + t * 1.6) * 14 + math.sin(x * 0.031 - t * 2.3) * 6)
    ctx.line_to(W + 20, H + 20)
    ctx.close_path()
    ctx.set_source(vgrad(ctx, 0, wl - 20, 0, H, [(0, (0.42, 0.43, 0.44), 0.82), (1, (0.18, 0.19, 0.2), 0.95)]))
    ctx.fill()
    for k in range(60):
        x = (hash01(k, 1) * (W + 200) + t * 20) % (W + 200) - 100
        y = wl + 20 + hash01(k, 2) ** 1.5 * (H - wl)
        ctx.rectangle(x, y, 30 + 60 * hash01(k, 3), 2)
        ctx.set_source_rgba(1, 1, 1, 0.25)
        ctx.fill()
    ctx.restore()
