"""THE PROMOTERS - render the picture and mix the sound.

  python3 tts.py              # voices -> build/timeline.json, dialogue.wav, env.npy
  python3 film.py --stills    # one PNG per shot, for review
  python3 film.py             # full render + mix -> build/video.mp4, build/mix.wav
"""
import argparse
import functools
import json
import math
import os
import subprocess
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.append(os.path.join(os.path.dirname(HERE), "falklands"))

from PIL import Image, ImageFilter  # noqa: E402

from engine import fx  # noqa: E402
from engine.core import (FPS, H, W, clamp, draw_text, ease_out, hash01, lerp, mix, new_canvas, poly, ramp,  # noqa: E402
                         rgba_to_surface, set_rgba, surface_to_rgb, text_width, vgrad)
import toons as T  # noqa: E402

BUILD = os.path.join(HERE, "build")
WALL = (0.82, 0.8, 0.7)
CARPET = (0.42, 0.44, 0.47)


# ------------------------------------------------------------------ timeline
@functools.lru_cache(maxsize=1)
def timeline():
    tl = json.load(open(os.path.join(BUILD, "timeline.json")))
    env = np.load(os.path.join(BUILD, "env.npy"))
    beats = tl["beats"]
    # group consecutive beats with the same shot into runs
    runs = []
    for b in beats:
        if runs and runs[-1]["shot"] == b["shot"]:
            runs[-1]["end"] = b["end_pause"]
            runs[-1]["beats"].append(b)
        else:
            runs.append({"shot": b["shot"], "start": b["start"], "end": b["end_pause"], "beats": [b]})
    return tl["total"], runs, env


class Ctx:
    def __init__(self, run, T_, frame, env, idx):
        self.run, self.T, self.frame, self.env = run, T_, frame, env
        self.t = T_ - run["start"]
        self.dur = run["end"] - run["start"]
        self.idx = idx
        self.beat = run["beats"][0]
        for b in run["beats"]:
            if b["start"] <= T_:
                self.beat = b
        self.first = all(r["shot"] != run["shot"] for r in timeline()[1][:idx])

    def speaking(self, who):
        b = self.beat
        if b["who"] == who and b["start"] <= self.T <= b["end"] + 0.05:
            return float(self.env[min(self.frame, len(self.env) - 1)])
        return 0.0

    def talking(self, who):
        b = self.beat
        return 1.0 if (b["who"] == who and b["start"] <= self.T <= b["end"]) else 0.0

    def beat_t(self):
        return self.T - self.beat["start"]

    def silent(self):
        return self.beat["who"] is None

    def beat_index(self):
        return self.run["beats"].index(self.beat)


# ------------------------------------------------------------------ handheld documentary camera
def handheld(ctx, S, amp=1.0, zoom=1.0, focus=(W / 2, H / 2)):
    t = S.T
    dx = (math.sin(t * 0.9) * 9 + math.sin(t * 2.3 + 1) * 4 + math.sin(t * 5.1) * 1.5) * amp
    dy = (math.sin(t * 0.7 + 2) * 6 + math.sin(t * 1.9) * 3) * amp
    rot = math.sin(t * 0.5) * 0.004 * amp
    ctx.translate(focus[0] + dx, focus[1] + dy)
    ctx.rotate(rot)
    ctx.scale(zoom, zoom)
    ctx.translate(-focus[0], -focus[1])


def snap_zoom(S, at, z=1.3, dur=0.18):
    """The mockumentary 'crash zoom' onto a face."""
    a = S.t - at
    if a < 0:
        return 1.0
    return lerp(1.0, z, ease_out(min(1.0, a / dur)))


# ------------------------------------------------------------------ sets
def ceiling(ctx, y1=230):
    ctx.rectangle(0, 0, W, y1)
    set_rgba(ctx, (0.88, 0.88, 0.86))
    ctx.fill()
    ctx.set_line_width(2)
    for x in range(0, W, 160):
        ctx.move_to(x, 0)
        ctx.line_to(x, y1)
    for y in range(0, y1, 80):
        ctx.move_to(0, y)
        ctx.line_to(W, y)
    set_rgba(ctx, (0.7, 0.7, 0.68))
    ctx.stroke()
    for x in (240, 900, 1560):   # fluorescent tubes
        ctx.rectangle(x, 70, 320, 34)
        set_rgba(ctx, (1, 1, 0.97))
        ctx.fill()


def desk(ctx, x, y, w=420, monitor=True, papers=True, seed=0):
    ctx.rectangle(x, y, w, 22)
    set_rgba(ctx, (0.62, 0.56, 0.46))
    ctx.fill()
    ctx.rectangle(x + 10, y + 22, w - 20, 160)
    set_rgba(ctx, (0.5, 0.45, 0.37))
    ctx.fill()
    if monitor:
        ctx.rectangle(x + w * 0.35, y - 170, 190, 140)
        set_rgba(ctx, (0.2, 0.2, 0.22))
        ctx.fill()
        ctx.rectangle(x + w * 0.35 + 12, y - 158, 166, 112)
        set_rgba(ctx, (0.55, 0.65, 0.75))
        ctx.fill()
        ctx.rectangle(x + w * 0.35 + 80, y - 30, 30, 30)
        set_rgba(ctx, (0.2, 0.2, 0.22))
        ctx.fill()
    if papers:
        for k in range(3):
            ctx.rectangle(x + 20 + k * 14, y - 14 - k * 5, 110, 14)
            set_rgba(ctx, (0.95, 0.95, 0.93))
            ctx.fill()


def fight_poster(ctx, x, y, s=1.0):
    w, h = 300 * s, 420 * s
    ctx.rectangle(x, y, w, h)
    ctx.set_source(vgrad(ctx, 0, y, 0, y + h, [(0, (0.12, 0.12, 0.16)), (1, (0.45, 0.1, 0.1))]))
    ctx.fill()
    draw_text(ctx, "JOSHUA", x + w / 2, y + h * 0.3, "oswald", 58 * s, (1, 1, 1), "cb", 1, 0.05)
    draw_text(ctx, "vs", x + w / 2, y + h * 0.42, "oswald_r", 34 * s, (0.95, 0.8, 0.3), "cb", 1)
    draw_text(ctx, "FURY", x + w / 2, y + h * 0.58, "oswald", 70 * s, (1, 1, 1), "cb", 1, 0.05)
    draw_text(ctx, "11 DEC · CARDIFF", x + w / 2, y + h * 0.8, "cond", 26 * s, (0.95, 0.8, 0.3), "cb", 1, 0.1)


def motivational(ctx, x, y):
    ctx.rectangle(x, y, 260, 200)
    set_rgba(ctx, (0.12, 0.12, 0.14))
    ctx.fill()
    ctx.rectangle(x + 20, y + 20, 220, 110)
    ctx.set_source(vgrad(ctx, 0, y + 20, 0, y + 130, [(0, (0.4, 0.55, 0.75)), (1, (0.85, 0.75, 0.6))]))
    ctx.fill()
    draw_text(ctx, "TEAMWORK", x + 130, y + 165, "cond", 30, (1, 1, 1), "cb", 1, 0.25)


def office_bg(ctx, variant=0):
    ctx.rectangle(0, 0, W, H)
    set_rgba(ctx, WALL)
    ctx.fill()
    ceiling(ctx)
    ctx.rectangle(0, 760, W, H)
    set_rgba(ctx, CARPET)
    ctx.fill()
    ctx.rectangle(0, 750, W, 14)
    set_rgba(ctx, (0.3, 0.3, 0.3))
    ctx.fill()
    if variant == 0:
        fight_poster(ctx, 1280, 300, 0.9)
        motivational(ctx, 300, 330)
        ctx.rectangle(1640, 380, 200, 380)   # filing cabinet
        set_rgba(ctx, (0.55, 0.57, 0.58))
        ctx.fill()
        for k in range(4):
            ctx.rectangle(1700, 410 + k * 90, 80, 10)
            set_rgba(ctx, (0.35, 0.35, 0.36))
            ctx.fill()
        desk(ctx, 600, 700, 520)
    else:
        ctx.rectangle(200, 280, 520, 330)    # window blinds
        set_rgba(ctx, (0.9, 0.93, 0.95))
        ctx.fill()
        ctx.set_line_width(4)
        for k in range(16):
            ctx.move_to(200, 290 + k * 20)
            ctx.line_to(720, 290 + k * 20)
        set_rgba(ctx, (0.7, 0.72, 0.72))
        ctx.stroke()
        fight_poster(ctx, 1450, 300, 0.75)
        ctx.arc(1050, 400, 26, 0, 6.283)   # pot plant
        set_rgba(ctx, (0.3, 0.5, 0.3))
        ctx.fill()
        desk(ctx, 820, 700, 520)


@functools.lru_cache(maxsize=4)
def blurred_bg(variant):
    surf, ctx = new_canvas()
    office_bg(ctx, variant)
    arr = (surface_to_rgb(surf) * 255).astype(np.uint8)
    img = Image.fromarray(arr).filter(ImageFilter.GaussianBlur(9))
    rgba = np.dstack([np.asarray(img), np.full((H, W), 255, np.uint8)])
    return rgba_to_surface(rgba)


def lower_third(ctx, S, name, role, t_in=0.4, t_out=4.2):
    if not S.first:
        return
    a = min(ramp(S.t, t_in, t_in + 0.25), 1 - ramp(S.t, t_out - 0.25, t_out))
    if a <= 0:
        return
    ctx.save()
    ctx.identity_matrix()
    draw_text(ctx, name, 140, 900, "cond", 54, (1, 1, 1), "lb", a, 0.02, shadow=(2, 2, 0.8))
    draw_text(ctx, role, 140, 950, "cond_r", 38, (1, 1, 1), "lb", a, 0.02, shadow=(2, 2, 0.8))
    ctx.restore()


def card(ctx, lines, a=1.0):
    ctx.rectangle(0, 0, W, H)
    set_rgba(ctx, (0, 0, 0))
    ctx.fill()
    total = sum(sz * 1.5 for _, sz, _ in lines)
    y = H / 2 - total / 2
    for text, sz, f in lines:
        y += sz * 1.5
        if text:
            draw_text(ctx, text, W / 2, y - sz * 0.35, f, sz, (1, 1, 1), "cb", a)


# ------------------------------------------------------------------ shots
def card_open(ctx, S):
    t = S.t
    if t < 2.7:
        a = min(ramp(t, 0.1, 0.4), 1 - ramp(t, 2.4, 2.7))
        card(ctx, [("In September 2026, Netflix announced", 44, "cond_r"),
                   ("Anthony Joshua vs Tyson Fury.", 44, "cond_r"),
                   ("11 December. Cardiff.", 44, "cond_r"), ("", 20, "cond_r"),
                   ("Then the promoters started talking.", 44, "cond_r")], a)
    else:
        a = min(ramp(t, 2.8, 3.1), 1 - ramp(t, S.dur - 0.3, S.dur))
        card(ctx, [("the promoters", 110, "cond_r"), ("", 30, "cond_r"),
                   ("a parody", 34, "cond_r")], a)


def _th(ctx, S, who, variant, x, pose_talk="gesture", extra=None, look_dir=0.55):
    ctx.save()
    zoom = 1.0
    if S.silent():
        zoom = snap_zoom(S, S.beat["start"] - S.run["start"], 1.22)
    handheld(ctx, S, 0.8, zoom, focus=(x, 420))
    ctx.set_source_surface(blurred_bg(variant), 0, 0)
    ctx.paint()
    m = S.speaking(who)
    talk = S.talking(who)
    look = 0.0 if (S.silent() or S.beat["text"] in ("This. This is promoting.", "Anyone else?",
                                                     "Took most of August.", "I checked the spelling. Twice.",
                                                     "Different folder. Blue one.")) else look_dir
    pose = pose_talk if talk else "rest"
    T.character(ctx, who, x, 640, 330, mouth=m, blink=T.blink_at(S.T, len(who)), look=look, pose=pose,
                t=S.T, talk=talk)
    if extra:
        extra(ctx, S, x)
    ctx.restore()


def th_dana(ctx, S):
    _th(ctx, S, "DANA", 0, W * 0.45, look_dir=0.6)
    lower_third(ctx, S, "DANA WHITE", "Promoter (he says)")


def _badge(ctx, S, x):
    bx, by = x - 300, 900
    ctx.save()
    ctx.translate(bx, by)
    ctx.rotate(-0.06)
    ctx.rectangle(-110, -70, 220, 140)
    set_rgba(ctx, (0.85, 0.12, 0.12))
    ctx.fill()
    ctx.rectangle(-104, -30, 208, 94)
    set_rgba(ctx, (1, 1, 1))
    ctx.fill()
    draw_text(ctx, "HELLO my name is", 0, -40, "cond", 22, (1, 1, 1), "cb", 1)
    draw_text(ctx, "DANA", 0, 22, "oswald", 52, (0.1, 0.1, 0.3), "cb", 1)
    draw_text(ctx, "(not a company)", 0, 56, "cond_r", 22, (0.1, 0.1, 0.3), "cb", 1)
    ctx.restore()


def th_dana_badge(ctx, S):
    _th(ctx, S, "DANA", 0, W * 0.45, look_dir=0.6, extra=_badge)


def th_eddie(ctx, S):
    _th(ctx, S, "EDDIE", 1, W * 0.56, look_dir=-0.6)
    lower_third(ctx, S, "EDDIE HEARN", "Promoter (contractually)")


def _binder(ctx, S, x, colour=(0.95, 0.95, 0.93), label="CONTRACT", open_page=True):
    lift = ease_out(ramp(S.t, 0.0, 0.5))
    bx, by = x, 1010 - 80 * lift
    ctx.save()
    ctx.translate(bx, by)
    ctx.rotate(-0.04)
    ctx.rectangle(-260, -170, 520, 340)
    set_rgba(ctx, mix(colour, (0, 0, 0), 0.15))
    ctx.fill()
    ctx.rectangle(-250, -160, 500, 320)
    set_rgba(ctx, colour)
    ctx.fill()
    draw_text(ctx, label, 0, -95, "oswald", 54, (0.15, 0.15, 0.2), "cb", 1, 0.15)
    if open_page:
        ctx.rectangle(-200, -60, 400, 200)
        set_rgba(ctx, (1, 1, 1))
        ctx.fill()
        ctx.set_line_width(3)
        for k in range(6):
            ctx.move_to(-180, -30 + k * 30)
            ctx.line_to(180 - (k % 3) * 40, -30 + k * 30)
        set_rgba(ctx, (0.6, 0.6, 0.62))
        ctx.stroke()
        hl = ramp(S.t, 0.6, 1.2)
        ctx.rectangle(-185, 34, 260 * hl, 30)
        ctx.set_source_rgba(1, 0.92, 0.1, 0.75)
        ctx.fill()
        draw_text(ctx, "...DANA WHITE...", -175, 58, "courier", 26, (0.1, 0.1, 0.1), "lb", hl)
        draw_text(ctx, "p. 40", 175, 125, "cond_r", 22, (0.4, 0.4, 0.4), "rb", 1)
    ctx.restore()


def th_eddie_binder(ctx, S):
    _th(ctx, S, "EDDIE", 1, W * 0.56, pose_talk="binder", look_dir=-0.6, extra=_binder)


def th_eddie_binder2(ctx, S):
    _th(ctx, S, "EDDIE", 1, W * 0.56, pose_talk="binder", look_dir=-0.6,
        extra=lambda c, s_, x: _binder(c, s_, x, (0.35, 0.55, 0.85), "IN WRITING", False))


def office_phone(ctx, S):
    ctx.save()
    handheld(ctx, S, 1.2)
    office_bg(ctx, 0)
    # Eddie at the back desk, typing
    T.character(ctx, "EDDIE", 1060, 640, 130, blink=T.blink_at(S.T, 5), look=0.6, t=S.T)
    desk(ctx, 600, 700, 700, monitor=False)
    # Dana in the foreground filming a promo on his phone
    m = S.speaking("DANA")
    T.character(ctx, "DANA", 1350, 900, 270, mouth=m, blink=T.blink_at(S.T, 4), look=0.9, pose="phone", t=S.T,
                talk=S.talking("DANA"))
    ctx.restore()


def office_look(ctx, S):
    ctx.save()
    z = snap_zoom(S, 0.05, 1.35)
    handheld(ctx, S, 1.0, z, focus=(760, 420))
    office_bg(ctx, 0)
    T.character(ctx, "DANA", 1500, 860, 170, mouth=0.4 + 0.3 * math.sin(S.T * 9), look=0.9, pose="phone", t=S.T)
    T.character(ctx, "EDDIE", 760, 820, 230, mouth=S.speaking("EDDIE"), blink=T.blink_at(S.T, 5), look=0.0,
                t=S.T)
    ctx.restore()


def _tally(ctx, x, y, n, scale=1.0):
    ctx.set_line_width(9 * scale)
    ctx.set_source_rgba(0.1, 0.25, 0.75, 1)
    for i in range(n):
        g, k = divmod(i, 5)
        gx = x + g * 170 * scale
        if k < 4:
            ctx.move_to(gx + k * 30 * scale, y)
            ctx.line_to(gx + k * 30 * scale + 6 * scale, y + 140 * scale)
        else:
            ctx.move_to(gx - 20 * scale, y + 120 * scale)
            ctx.line_to(gx + 120 * scale, y + 20 * scale)
        ctx.stroke()


def whiteboard(ctx, S):
    ctx.save()
    handheld(ctx, S, 0.8, 1.0)
    ctx.rectangle(0, 0, W, H)
    set_rgba(ctx, WALL)
    ctx.fill()
    ctx.rectangle(160, 120, 1300, 760)
    set_rgba(ctx, (0.6, 0.62, 0.64))
    ctx.fill()
    ctx.rectangle(180, 140, 1260, 720)
    set_rgba(ctx, (0.97, 0.98, 0.98))
    ctx.fill()
    draw_text(ctx, "BREACHES", 260, 300, "oswald", 110, (0.1, 0.25, 0.75), "lb", 1, 0.08)
    n = 6 if S.beat_index() >= 0 else 5
    n = 5 + (1 if S.t > 0.25 else 0)
    _tally(ctx, 300, 420, n, 1.4)
    draw_text(ctx, "(as of this morning)", 300, 760, "cond_r", 40, (0.3, 0.3, 0.35), "lb", 0.9)
    T.character(ctx, "EDDIE", 1640, 760, 260, mouth=S.speaking("EDDIE"), blink=T.blink_at(S.T, 5),
                look=-0.2 if S.beat_index() == 0 else 0.0, pose="marker", t=S.T, talk=S.talking("EDDIE"))
    ctx.restore()


def office_hand(ctx, S):
    ctx.save()
    k = ease_out(ramp(S.t, 0.6, 2.4))
    handheld(ctx, S, 0.9, lerp(1.0, 1.45, k), focus=(1300, 460))
    office_bg(ctx, 0)
    T.character(ctx, "EDDIE", 1300, 650, 140, blink=T.blink_at(S.T, 5), look=0.0, pose="hand_up",
                prop=float(ramp(S.t, 0.3, 1.4)), t=S.T)
    desk(ctx, 1040, 710, 520, monitor=False)
    T.character(ctx, "DANA", 480, 960, 300, look=-0.3, blink=T.blink_at(S.T, 4), t=S.T)
    ctx.restore()


def _printer(ctx, x, y, page_out):
    ctx.rectangle(x - 200, y - 150, 400, 150)
    set_rgba(ctx, (0.85, 0.85, 0.83))
    ctx.fill()
    ctx.rectangle(x - 200, y, 400, 80)
    set_rgba(ctx, (0.7, 0.7, 0.68))
    ctx.fill()
    ctx.rectangle(x - 160, y - 110, 320, 18)
    set_rgba(ctx, (0.25, 0.25, 0.27))
    ctx.fill()
    ph = 300 * page_out
    ctx.save()
    ctx.rectangle(x - 150, y - 110 - ph, 300, ph)
    ctx.clip()
    _release(ctx, x - 150, y - 110 - 300, 300, 300)
    ctx.restore()


def _release(ctx, x, y, w, h, hl=0.0):
    ctx.rectangle(x, y, w, h)
    set_rgba(ctx, (1, 1, 1))
    ctx.fill()
    draw_text(ctx, "PRESS RELEASE", x + 20, y + 44, "cond", 26, (0.6, 0.05, 0.08), "lb", 1, 0.1)
    ctx.set_line_width(3)
    for k in range(4):
        ctx.move_to(x + 20, y + 80 + k * 26)
        ctx.line_to(x + w - 30 - (k % 2) * 50, y + 80 + k * 26)
    set_rgba(ctx, (0.65, 0.65, 0.67))
    ctx.stroke()
    draw_text(ctx, "Promoters:", x + 20, y + 210, "cond", 22, (0.1, 0.1, 0.1), "lb", 1)
    if hl:
        ctx.rectangle(x + 16, y + 222, 190 * hl, 30)
        ctx.set_source_rgba(1, 0.92, 0.1, 0.75)
        ctx.fill()
    draw_text(ctx, "... DANA WHITE ...", x + 20, y + 246, "courier", 22, (0.1, 0.1, 0.1), "lb", 1)


def printer(ctx, S):
    ctx.save()
    handheld(ctx, S, 1.0)
    office_bg(ctx, 1)
    out = ramp(S.t, 0.2, 1.7)
    _printer(ctx, 700, 760, out)
    T.character(ctx, "EDDIE", 1250, 720, 230, mouth=S.speaking("EDDIE"), blink=T.blink_at(S.T, 5),
                look=-0.8 if S.silent() else -0.4, t=S.T, talk=S.talking("EDDIE"),
                pose="gesture" if S.talking("EDDIE") else "rest")
    ctx.restore()


def printer_look(ctx, S):
    ctx.save()
    z = snap_zoom(S, 0.0, 1.15)
    handheld(ctx, S, 0.9, z, focus=(W / 2, 450))
    ctx.set_source_surface(blurred_bg(1), 0, 0)
    ctx.paint()
    T.character(ctx, "EDDIE", W / 2, 640, 330, mouth=S.speaking("EDDIE"), blink=T.blink_at(S.T, 5), look=0.0,
                t=S.T, talk=S.talking("EDDIE"))
    ctx.save()
    ctx.translate(W / 2 - 170, 760)
    ctx.rotate(-0.08)
    _release(ctx, 0, 0, 340, 330, ramp(S.t, 0.3, 0.9))
    ctx.restore()
    ctx.restore()


def card_wednesday(ctx, S):
    card(ctx, [("Wednesday.", 80, "cond_r")], min(ramp(S.t, 0.1, 0.4), 1 - ramp(S.t, S.dur - 0.3, S.dur)))


def meeting(ctx, S):
    t = S.t
    ctx.save()
    handheld(ctx, S, 0.7, lerp(1.0, 1.08, S.t / S.dur), focus=(W / 2, 500))
    ctx.rectangle(0, 0, W, H)
    set_rgba(ctx, (0.78, 0.8, 0.76))
    ctx.fill()
    ceiling(ctx, 180)
    # wall clock, ticking
    cx, cy = 1500, 330
    ctx.arc(cx, cy, 70, 0, 6.283)
    set_rgba(ctx, (1, 1, 1))
    ctx.fill_preserve()
    ctx.set_line_width(8)
    set_rgba(ctx, (0.2, 0.2, 0.2))
    ctx.stroke()
    sec = int(S.T) * 6
    for ang, L_, w_ in ((math.radians(sec - 90), 55, 3), (math.radians(80), 45, 7), (math.radians(210), 32, 8)):
        ctx.set_line_width(w_)
        ctx.move_to(cx, cy)
        ctx.line_to(cx + math.cos(ang) * L_, cy + math.sin(ang) * L_)
        ctx.stroke()
    draw_text(ctx, "MEETING ROOM 2", 380, 330, "cond", 34, (0.3, 0.3, 0.3), "lb", 0.8, 0.2)
    # Eddie alone, an empty chair opposite, two coffees
    T.character(ctx, "EDDIE", 660, 700, 230, mouth=S.speaking("EDDIE"), blink=T.blink_at(S.T, 5),
                look=0.0 if (S.beat["text"] == "So, no." or S.silent()) else 0.9, t=S.T,
                talk=S.talking("EDDIE"))
    ctx.rectangle(1080, 520, 220, 330)   # empty chair
    set_rgba(ctx, (0.25, 0.25, 0.3))
    ctx.fill()
    ctx.rectangle(260, 780, 1400, 40)    # table
    set_rgba(ctx, (0.55, 0.48, 0.38))
    ctx.fill()
    ctx.rectangle(300, 820, 1320, 300)
    set_rgba(ctx, (0.45, 0.39, 0.3))
    ctx.fill()
    for mx in (760, 1180):
        ctx.rectangle(mx, 720, 60, 62)
        set_rgba(ctx, (0.96, 0.96, 0.95))
        ctx.fill()
    # Gary the tea man drifts in
    gin = ease_out(ramp(S.T - S.run["start"], 2.0, 3.2))
    if gin > 0:
        T.character(ctx, "GARY", lerp(W + 250, 1560, gin), 720, 230, mouth=S.speaking("GARY"),
                    blink=T.blink_at(S.T, 7), look=-0.8, pose="mug", t=S.T, talk=S.talking("GARY"))
    ctx.restore()


def card_end(ctx, S):
    t = S.t
    a = min(ramp(t, 0.2, 0.6), 1 - ramp(t, S.dur - 0.6, S.dur))
    card(ctx, [("Joshua vs Fury.  11 December.  Cardiff.", 50, "cond_r"), ("", 20, "cond_r"),
               ("Promoted by: still being discussed.", 50, "cond_r")], a)
    a2 = min(ramp(t, 1.6, 2.2), a)
    for i, line in enumerate(["A parody. The characters are cartoon caricatures and the voices are synthetic.",
                              "Dialogue is invented, except where it echoes public statements reported in",
                              "September–October 2026. The contract itself has not been made public."]):
        draw_text(ctx, line, W / 2, 880 + i * 40, "cond_r", 28, (0.75, 0.75, 0.75), "cb", a2)


SHOTS = {k: v for k, v in globals().items() if k in (
    "card_open", "th_dana", "th_dana_badge", "th_eddie", "th_eddie_binder", "th_eddie_binder2", "office_phone",
    "office_look", "whiteboard", "office_hand", "printer", "printer_look", "card_wednesday", "meeting", "card_end")}
CARDS = {"card_open", "card_wednesday", "card_end"}


# ------------------------------------------------------------------ render
def render_frame(frame):
    total, runs, env = timeline()
    Tm = frame / FPS
    idx = max(i for i, r in enumerate(runs) if r["start"] <= Tm or i == 0)
    run = runs[idx]
    surf, ctx = new_canvas()
    S = Ctx(run, Tm, frame, env, idx)
    SHOTS[run["shot"]](ctx, S)
    img = surface_to_rgb(surf)
    if run["shot"] not in CARDS:   # broadcast-video look: cool office grade, light grain
        img = fx.film(img, frame, 0.35, warm=False, dust=False)
    if Tm > total - 1.0:
        img = img * max(0.0, (total - Tm) / 1.0)
    return fx.finish(img)


def _chunk(args):
    i, f0, f1 = args
    out = os.path.join(BUILD, "chunks", f"c{i:03d}.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s",
                          f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                          "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(render_frame(f).tobytes())
    p.stdin.close()
    p.wait()
    return i


# ------------------------------------------------------------------ sound
def mix_audio():
    import soundfile as sf
    total, runs, _ = timeline()
    dia, sr = sf.read(os.path.join(BUILD, "dialogue.wav"))
    SR = 48000
    dia = np.interp(np.arange(int(len(dia) * SR / sr)) / SR, np.arange(len(dia)) / sr, dia)
    n = int(total * SR) + SR
    out = np.zeros(n)
    out[:len(dia)] += dia
    rng = np.random.default_rng(7)
    tt = np.arange(n) / SR
    # office room tone: air handling + the fluorescent hum
    room = np.convolve(rng.standard_normal(n), np.ones(40) / 40, mode="same") * 0.02
    room += np.sin(2 * np.pi * 100 * tt) * 0.004
    for r in runs:
        i0, i1 = int(r["start"] * SR), int(r["end"] * SR)
        if r["shot"] not in CARDS:
            out[i0:i1] += room[i0:i1]
        if r["shot"] == "printer":   # printer whirr
            m = int(1.6 * SR)
            pr = (np.sign(np.sin(2 * np.pi * 37 * tt[:m])) * 0.03 + rng.standard_normal(m) * 0.01)
            out[i0 + int(0.2 * SR):i0 + int(0.2 * SR) + m] += pr
        if r["shot"] == "meeting":   # the clock
            for k in range(int(r["end"] - r["start"])):
                j = i0 + k * SR
                out[j:j + 300] += rng.standard_normal(300) * 0.05 * np.exp(-np.arange(300) / 60)
        if r["shot"] == "whiteboard":   # marker squeak
            m = int(0.25 * SR)
            j = i0 + int(0.2 * SR)
            out[j:j + m] += np.sin(2 * np.pi * (1800 + 400 * np.sin(np.arange(m) / SR * 30)) * np.arange(m) / SR) * 0.03
    # a plucked guitar sting for the opening title and the end card (original, Karplus-Strong)
    def pluck(f, d=1.6):
        N = int(SR / f)
        buf = rng.uniform(-1, 1, N)
        y = np.zeros(int(d * SR))
        for i in range(len(y)):
            y[i] = buf[i % N]
            buf[i % N] = 0.5 * (buf[i % N] + buf[(i + 1) % N]) * 0.996
        return y * 0.12

    seq = [196.0, 246.9, 293.7, 392.0, 329.6, 293.7, 246.9, 220.0]
    for r in runs:
        if r["shot"] in ("card_open", "card_end"):
            t0 = r["start"] + (2.8 if r["shot"] == "card_open" else 0.3)
            for k, f in enumerate(seq):
                j = int((t0 + k * 0.28) * SR)
                p = pluck(f)
                out[j:j + len(p)] += p[:max(0, n - j)]
    out = out[:int(total * SR)]
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.9
    sf.write(os.path.join(BUILD, "mix.wav"), np.stack([out, out], 1).astype(np.float32), SR, subtype="FLOAT")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    args = ap.parse_args()
    total, runs, _ = timeline()
    if args.stills:
        os.makedirs(os.path.join(BUILD, "stills"), exist_ok=True)
        for i, r in enumerate(runs):
            f = int((r["start"] + (r["end"] - r["start"]) * 0.6) * FPS)
            Image.fromarray(render_frame(f)).save(os.path.join(BUILD, "stills", f"{i:02d}_{r['shot']}.png"))
            print(f"{r['start']:6.2f}-{r['end']:6.2f} {r['shot']}")
        return
    os.makedirs(os.path.join(BUILD, "chunks"), exist_ok=True)
    nf = int(total * FPS)
    step = math.ceil(nf / 16)
    jobs = [(i, i * step, min(nf, (i + 1) * step)) for i in range(16) if i * step < nf]
    t0 = time.time()
    with Pool(os.cpu_count()) as p:
        for i in p.imap_unordered(_chunk, jobs):
            print(f"chunk {i} done ({time.time() - t0:.0f}s)", flush=True)
    with open(os.path.join(BUILD, "chunks", "list.txt"), "w") as f:
        for i, _, _ in jobs:
            f.write(f"file 'c{i:03d}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i",
                    os.path.join(BUILD, "chunks", "list.txt"), "-c", "copy", os.path.join(BUILD, "video.mp4")],
                   check=True)
    mix_audio()
    print("done")


if __name__ == "__main__":
    main()
