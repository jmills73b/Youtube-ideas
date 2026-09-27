"""Render the Somme film's picture track.

Shots are anchored to narration sentences (build/timing.json), so picture and
voice stay locked. Frames are drawn with Cairo, graded in numpy, and piped to
ffmpeg by several worker processes in parallel.

  python3 render.py                 # full render -> build/video.mp4 (no audio)
  python3 render.py --stills        # one PNG per shot -> build/stills/
  python3 render.py --only NAME     # render stills for shots whose name contains NAME
"""
import argparse
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

import ww1  # noqa: E402,F401  (sets up the shared engine and period fonts)
from ww1 import fx as WFX  # noqa: E402
from engine import fx  # noqa: E402
from engine.core import FPS, H, W, new_canvas, surface_to_rgb  # noqa: E402
from shots import SHOTS  # noqa: E402

BUILD = os.path.join(HERE, "build")
XFADE = 0.6


class Timing:
    def __init__(self, path):
        self.data = json.load(open(path))
        self.total = self.data["total"]
        self.seg = {s["id"]: s for s in self.data["segments"]}

    def at(self, seg, sent=0, frac=0.0):
        """Global time of a point inside a sentence (frac by character position)."""
        s = self.seg[seg]
        if sent == "end":
            return s["sentences"][-1]["end"]
        if sent == "seg_end":
            return s["end"]
        st = s["sentences"][sent]
        return st["start"] + (st["end"] - st["start"]) * frac

    def word(self, seg, sent, word):
        """Approximate global time a word/phrase starts inside a sentence."""
        st = self.seg[seg]["sentences"][sent]
        i = st["text"].find(word)
        if i < 0:
            raise KeyError(word)
        return st["start"] + (st["end"] - st["start"]) * i / len(st["text"])


class ShotCtx:
    """What a scene function sees: local time plus narration-anchored helpers."""

    def __init__(self, shot, timing, T, frame):
        self.shot, self.timing = shot, timing
        self.T, self.frame = T, frame
        self.start, self.end = shot["start"], shot["end"]
        self.t = T - self.start
        fe = shot.get("fps_eff")
        if fe:   # hand-cranked cadence: motion advances in steps of 1/fe s
            self.t = int(self.t * fe) / fe
        self.dur = self.end - self.start
        self.u = self.t / self.dur if self.dur else 0

    def at(self, seg, sent=0, frac=0.0):
        return self.timing.at(seg, sent, frac) - self.start

    def word(self, seg, sent, word):
        return self.timing.word(seg, sent, word) - self.start


def build_timeline(timing):
    shots = []
    for s in SHOTS:
        a = s["start"]
        start = 0.0 if a is None else timing.at(*a) + s.get("offset", 0.0)
        shots.append({**s, "start": start})
    shots.sort(key=lambda s: s["start"])
    for i, s in enumerate(shots):
        s["end"] = shots[i + 1]["start"] if i + 1 < len(shots) else timing.total
    return shots


def render_shot(shot, timing, T, frame):
    surf, ctx = new_canvas()
    S = ShotCtx(shot, timing, T, frame)
    shot["fn"](ctx, S)
    img = surface_to_rgb(surf)
    look = shot.get("look", "silent")
    if look == "silent":
        img = WFX.silent(img, frame, shot.get("tint", "sepia"), shot.get("grain", 1.0))
    elif look == "print":
        img = WFX.print_(img, frame)
    elif look == "poster":
        img = fx.halftone(img, frame)
    elif look == "film":
        img = fx.film(img, frame, shot.get("grain", 1.0), warm=shot.get("warm", True))
    return img


def render_frame(shots, timing, frame):
    T = frame / FPS
    active = [s for s in shots if s["start"] - (XFADE if s.get("xfade", True) else 0) <= T < s["end"]]
    # the shot that owns T, plus the next one if it's fading in
    cur = [s for s in shots if s["start"] <= T < s["end"]]
    cur = cur[0] if cur else shots[-1]
    img = render_shot(cur, timing, T, frame)
    nxt = [s for s in active if s is not cur and s["start"] > T]
    if nxt:
        n = nxt[0]
        k = 1 - (n["start"] - T) / XFADE
        k = k * k * (3 - 2 * k)
        img2 = render_shot(n, timing, T, frame)
        img = img * (1 - k) + img2 * k
    # global fade in/out
    if T < 1.2:
        img = img * (T / 1.2)
    if T > timing.total - 2.5:
        img = img * max(0.0, (timing.total - T) / 2.5)
    return fx.finish(img)


_G = {}


def _init_worker():
    timing = Timing(os.path.join(BUILD, "timing.json"))
    _G["timing"] = timing
    _G["shots"] = build_timeline(timing)


def _render_chunk(args):
    idx, f0, f1 = args
    out = os.path.join(BUILD, "chunks", f"chunk_{idx:03d}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "14",
           "-pix_fmt", "yuv420p", "-g", str(FPS), out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for f in range(f0, f1):
        p.stdin.write(render_frame(_G["shots"], _G["timing"], f).tobytes())
    p.stdin.close()
    p.wait()
    return idx, f1 - f0, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--only", default=None)
    ap.add_argument("--at", type=float, default=None, help="relative position in shot for stills (0-1)")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    args = ap.parse_args()

    _init_worker()
    timing, shots = _G["timing"], _G["shots"]
    if args.stills or args.only is not None:
        os.makedirs(os.path.join(BUILD, "stills"), exist_ok=True)
        from PIL import Image
        for i, s in enumerate(shots):
            if args.only and args.only not in s["name"]:
                continue
            for rel in ([args.at] if args.at is not None else [0.2, 0.75]):
                T = s["start"] + (s["end"] - s["start"]) * rel
                frame = int(T * FPS)
                img = fx.finish(render_shot(s, timing, T, frame))
                path = os.path.join(BUILD, "stills", f"{i:02d}_{s['name']}_{int(rel*100)}.png")
                Image.fromarray(img).save(path)
                print(f"{s['start']:7.2f}-{s['end']:7.2f}  {path}")
        return

    for s in shots:
        print(f"{s['start']:7.2f}-{s['end']:7.2f} {s['end']-s['start']:5.1f}s  {s['name']}")
    f_start = int(args.start * FPS)
    f_end = int((args.end or timing.total) * FPS)
    os.makedirs(os.path.join(BUILD, "chunks"), exist_ok=True)
    for f in os.listdir(os.path.join(BUILD, "chunks")):
        os.remove(os.path.join(BUILD, "chunks", f))
    n_chunks = args.workers * 6
    step = math.ceil((f_end - f_start) / n_chunks)
    jobs = [(i, f_start + i * step, min(f_end, f_start + (i + 1) * step)) for i in range(n_chunks)
            if f_start + i * step < f_end]
    t0 = time.time()
    done = 0
    with Pool(args.workers, initializer=_init_worker) as pool:
        for idx, n, dt in pool.imap_unordered(_render_chunk, jobs):
            done += n
            el = time.time() - t0
            print(f"chunk {idx:3d}: {n} frames in {dt:.0f}s | {done}/{f_end-f_start} "
                  f"({done/(f_end-f_start)*100:.0f}%) eta {el/done*(f_end-f_start-done):.0f}s", flush=True)
    lst = os.path.join(BUILD, "chunks", "list.txt")
    with open(lst, "w") as f:
        for i, _, _ in jobs:
            f.write(f"file 'chunk_{i:03d}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    os.path.join(BUILD, "video.mp4")], check=True)
    print(f"done in {time.time()-t0:.0f}s -> build/video.mp4")


if __name__ == "__main__":
    main()
