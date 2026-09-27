"""Score, sound effects and final mix for the Somme film.

Reuses the synthesis toolkit from ../falklands/audio.py. The score is an
original elegy: slow string pads in D minor / F major with a solo line, a low
pulse for the bombardment and the first day, and a quiet close.

  python3 audio.py  ->  build/mix.wav
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfiltfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ww1  # noqa: E402,F401  (puts the shared engine on sys.path)

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "falklands_audio", os.path.join(os.path.dirname(HERE), "falklands", "audio.py"))
FA = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(FA)
SR, bp, env_adsr, fx_boom, fx_crowd, fx_rain, fx_wind = FA.SR, FA.bp, FA.env_adsr, FA.fx_boom, FA.fx_crowd, \
    FA.fx_rain, FA.fx_wind
hp, hz, lp, melody, noise, ostinato, pad, saw, sub_drone, timpani = FA.hp, FA.hz, FA.lp, FA.melody, FA.noise, \
    FA.ostinato, FA.pad, FA.saw, FA.sub_drone, FA.timpani

BUILD = os.path.join(HERE, "build")
RNG = np.random.default_rng(1916)

FA.CHORDS.update({
    "Dm": ["D3", "A3", "D4", "F4", "A4"],
    "Gm7": ["G2", "D3", "F3", "A#3", "D4"],
    "Bb": ["A#2", "F3", "A#3", "D4", "F4"],
    "F/A": ["A2", "F3", "A3", "C4", "F4"],
    "C": ["C3", "G3", "C4", "E4", "G4"],
    "A7": ["A2", "E3", "G3", "C#4", "E4"],
    "F": ["F2", "C3", "F3", "A3", "C4"],
    "Dsus": ["D3", "A3", "D4", "G4", "A4"],
    "Eb": ["D#2", "A#2", "D#3", "G3", "A#3"],
})


def build_score(timing, total):
    seg = {s["id"]: s for s in timing["segments"]}
    T = lambda sid: seg[sid]["start"]  # noqa: E731

    def run(t0, t1, prog, step):
        out, t, i = [], t0, 0
        while t < t1 - 0.5:
            d = min(step, t1 - t)
            out.append((t, d, prog[i % len(prog)]))
            t += d
            i += 1
        return out

    ch = []
    ch += run(0.0, T("bombardment"), ["Dm", "Bb", "F/A", "C", "Dm", "Gm7", "A7", "Dm"], 6.5)
    ch += run(T("bombardment"), T("attrition"), ["Dm", "Eb", "Dm", "A7"], 5.0)
    ch += run(T("attrition"), T("cost"), ["Gm7", "Dm", "Bb", "A7"], 5.5)
    ch += run(T("cost"), total, ["Dm", "Bb", "F", "C", "Dm", "Gm7", "Dsus", "Dm"], 7.0)

    def cutoff(t):
        return 1300 if T("bombardment") <= t < T("attrition") else 900

    mix = pad(ch, total, cutoff, gain=0.15)
    mix += sub_drone(ch, total, 0.22)
    mix += ostinato(T("bombardment"), T("slaughter") + 2, total, 60, "D2", gain=0.28)
    for h in (T("zero"), T("slaughter"), T("tanks"), T("cost")):
        t, v = timpani(h - 0.05, 0.5)
        i0 = int(t * SR)
        mix[i0:i0 + len(v), 0] += v[:len(mix) - i0]
        mix[i0:i0 + len(v), 1] += v[:len(mix) - i0]
    opening = [("A4", 2.0), ("F4", 1.0), ("E4", 1.0), ("D4", 3.0), (None, 1.0), ("C4", 1.0), ("D4", 1.0),
               ("F4", 1.5), ("E4", 0.5), ("D4", 4.0)]
    mix += melody(opening, 4.5, total, 0.08)
    lament = [("D5", 2.0), ("C5", 1.0), ("A#4", 1.0), ("A4", 3.0), ("G4", 1.0), ("F4", 2.0), ("E4", 1.0),
              ("D4", 4.0), (None, 1.0), ("F4", 1.5), ("G4", 0.5), ("A4", 2.0), ("A#4", 1.0), ("A4", 1.0),
              ("G4", 2.0), ("E4", 1.0), ("F4", 1.0), ("D4", 6.0)]
    mix += melody(lament, T("legacy") + 0.3, total, 0.10)
    return mix[:int(total * SR)]


# ------------------------------------------------------------------ 1916 sound effects
def fx_projector(d):
    n = int(d * SR)
    t = np.arange(n) / SR
    clicks = (np.sin(2 * np.pi * 16 * t) > 0.96).astype(float)
    v = bp(clicks + 0.02 * noise(n), 1500, 6000) * 0.5 + lp(noise(n), 200) * 0.03
    return v * 0.6


def fx_larks(d):
    n = int(d * SR)
    out = np.zeros(n)
    t = 0.2
    while t < d - 0.5:
        m = int(RNG.uniform(0.05, 0.14) * SR)
        tt = np.arange(m) / SR
        f0 = RNG.uniform(2800, 4800)
        f = f0 + 900 * np.sin(2 * np.pi * RNG.uniform(20, 45) * tt)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / tt[-1]) * 0.08
        i0 = int(t * SR)
        out[i0:i0 + m] += s[:n - i0]
        t += RNG.uniform(0.06, 0.25)
    return out


def fx_guns(d, near=False):
    n = int(d * SR)
    out = lp(noise(n), 120) * (0.05 if near else 0.08)
    t = 0.1
    while t < d:
        b = fx_boom(3.0, 700 if near else 260, 0.9 if near else 0.6) * RNG.uniform(0.35, 1.0)
        i0 = int(t * SR)
        out[i0:i0 + len(b)] += b[:n - i0] * (1.0 if near else 0.55)
        t += RNG.uniform(0.25, 0.9) if not near else RNG.uniform(0.6, 1.6)
    return out


def fx_whistle(d=1.6):
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    trill = 1 + 0.03 * np.sign(np.sin(2 * np.pi * 28 * t))
    v = np.sin(2 * np.pi * np.cumsum(2900 * trill) / SR) * 0.25
    v += bp(noise(n), 2500, 3500) * 0.08
    return v * env_adsr(n, 0.02, 0.2) * ((t < 0.5) | (t > 0.65))


def fx_mine(d=6.0):
    n = int(6.0 * SR)
    t = np.arange(n) / SR
    rumble = lp(noise(n), 90) * np.exp(-t / 2.5)
    rumble /= np.max(np.abs(rumble)) + 1e-9
    crack = fx_boom(6.0, 1200, 1.0)
    debris = bp(noise(n), 400, 3000) * np.clip((t - 1.5) / 0.5, 0, 1) * np.exp(-(t - 1.5).clip(0) / 1.5) * 0.3
    return rumble * 0.9 + crack * 0.8 + debris


def fx_mg(d):
    """Maxim / MG 08 machine guns: bursts of ~9-10 rounds a second."""
    n = int(d * SR)
    out = np.zeros(n)
    for gun in range(3):
        t = 0.2 + gun * 0.35
        gap = 1 / RNG.uniform(8.5, 10.0)
        while t < d:
            burst = RNG.integers(8, 22)
            for k in range(burst):
                m = int(0.04 * SR)
                s = hp(noise(m), 400) * np.exp(-np.arange(m) / SR / 0.008) * (0.5 - gun * 0.12)
                i0 = int((t + k * gap) * SR)
                if i0 < n:
                    out[i0:i0 + m] += s[:n - i0]
            t += burst * gap + RNG.uniform(0.3, 1.0)
    return lp(out, 3500)


def fx_march(d):
    n = int(d * SR)
    out = np.zeros(n)
    beat = 60 / 116
    t = 0.0
    while t < d:
        m = int(0.08 * SR)
        s = lp(noise(m), 700) * np.exp(-np.arange(m) / SR / 0.02) * 0.4
        i0 = int(t * SR)
        out[i0:i0 + m] += s[:n - i0]
        t += beat
    return out


def fx_tank(d):
    n = int(d * SR)
    t = np.arange(n) / SR
    engine = saw(38, n) * 0.3 + saw(76.4, n) * 0.15
    engine = lp(engine * (0.8 + 0.2 * np.sin(2 * np.pi * 7 * t)), 500)
    clank = np.zeros(n)
    idx = (np.arange(0, d, 0.19) * SR).astype(int)
    clank[idx[idx < n]] = 1
    clank = bp(clank, 800, 4000) * 0.6
    return engine + clank


FA.SFX.update({
    "projector": (fx_projector, True), "larks": (fx_larks, True), "guns_far": (lambda d: fx_guns(d), True),
    "guns_near": (lambda d: fx_guns(d, True), True), "whistle": (lambda d: fx_whistle(), False),
    "mine": (lambda d: fx_mine(), False), "mg": (fx_mg, True), "march": (fx_march, True),
    "tank": (fx_tank, True), "crowd": (fx_crowd, True), "rain": (fx_rain, True), "wind": (fx_wind, True),
})


def build_sfx(total):
    spec = importlib.util.spec_from_file_location("somme_render", os.path.join(HERE, "render.py"))
    R = importlib.util.module_from_spec(spec)
    sys.path.remove(os.path.join(os.path.dirname(HERE), "falklands")) if os.path.join(
        os.path.dirname(HERE), "falklands") in sys.path[:1] else None
    sys.path.insert(0, HERE)
    spec.loader.exec_module(R)
    ShotCtx, Timing, build_timeline = R.ShotCtx, R.Timing, R.build_timeline
    timing = Timing(os.path.join(BUILD, "timing.json"))
    shots = build_timeline(timing)
    out = np.zeros(int(total * SR) + 10 * SR)
    for shot in shots:
        for cue in shot.get("sfx", []):
            when, kind, gain = cue[0], cue[1], cue[2]
            S = ShotCtx(shot, timing, shot["start"], 0)
            S.t = 0.0
            t_local = when(S) if callable(when) else when
            end_local = shot["end"] - shot["start"] + 0.6
            fn, ambient = FA.SFX[kind]
            d = max(0.5, end_local - t_local)
            v = fn(d)
            if ambient:
                v = v.copy()
                f = min(int(0.8 * SR), len(v) // 2)
                v[:f] *= np.linspace(0, 1, f)
                v[-f:] *= np.linspace(1, 0, f)
            i0 = int((shot["start"] + t_local) * SR)
            out[i0:i0 + len(v)] += v[:len(out) - i0] * gain
    return out[:int(total * SR)]


def main():
    timing = json.load(open(os.path.join(BUILD, "timing.json")))
    total = timing["total"]
    nar_path = os.path.join(BUILD, "narration48.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(BUILD, "narration.wav"), "-ar",
                    str(SR), "-af", "highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,"
                    "equalizer=f=3000:t=q:w=1.2:g=2", nar_path], check=True)
    nar, _ = sf.read(nar_path)
    n = int(total * SR)
    nar = np.pad(nar, (0, max(0, n - len(nar))))[:n]
    music = build_score(timing, total)
    sfx = build_sfx(total)
    env = sosfiltfilt(butter(1, 3.0, "low", fs=SR, output="sos"), np.abs(nar))
    duck = 1 - 0.55 * np.clip(env / 0.05, 0, 1)
    music = music / (np.max(np.abs(music)) + 1e-9)
    sfx = sfx / (np.max(np.abs(sfx)) + 1e-9)
    mix = nar[:, None] * 1.0 + music * 0.26 * duck[:, None] + sfx[:, None] * 0.30 * (0.55 + 0.45 * duck[:, None])
    f = int(1.0 * SR)
    mix[:f] *= np.linspace(0, 1, f)[:, None]
    f2 = int(3.0 * SR)
    mix[-f2:] *= np.linspace(1, 0, f2)[:, None]
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    sf.write(os.path.join(BUILD, "mix.wav"), mix.astype(np.float32), SR, subtype="FLOAT")
    print(f"mix.wav written ({total:.1f}s)", file=sys.stderr)


if __name__ == "__main__":
    main()
