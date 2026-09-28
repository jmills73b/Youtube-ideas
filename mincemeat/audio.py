"""Score, sound effects and final mix for the Operation Mincemeat film.

Reuses the synthesis toolkit from ../falklands/audio.py. The score is an
original score in a 1940s manner: minor-key string pads, a light plucked
"intrigue" figure under the planning scenes, a pulse for the voyage and
the invasion, and a hymn-like close.

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
import ww2  # noqa: E402,F401  (puts the shared engine on sys.path)

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
RNG = np.random.default_rng(1943)

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


def pluck_line(notes, t0, total, beat, gain=0.18):
    """Plucked-string figure (pizzicato-like): quick attack, fast decay."""
    out = np.zeros(int(total * SR) + SR)
    t = t0
    for name in notes:
        if name is not None:
            n = int(0.5 * SR)
            f = hz(name)
            tt = np.arange(n) / SR
            v = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt / 0.12)
            i0 = int(t * SR)
            seg = out[i0:i0 + n]
            seg += v[:len(seg)] * gain
        t += beat
    return np.stack([out, out * 0.9], axis=1)


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
    ch += run(0.0, T("problem"), ["Dm", "Bb", "Gm7", "A7"], 6.0)
    ch += run(T("problem"), T("seraph"), ["Dm", "Gm7", "Eb", "A7", "Dm", "Bb", "Gm7", "A7"], 5.0)
    ch += run(T("seraph"), T("husky"), ["Dm", "Bb", "F/A", "C", "Dm", "Eb", "Dsus", "A7"], 5.5)
    ch += run(T("husky"), T("legacy"), ["F", "C", "Dm", "Bb"], 5.0)
    ch += run(T("legacy"), total, ["Dm", "Bb", "F", "C", "Gm7", "Dsus", "Dm"], 7.0)

    mix = pad(ch, total, lambda t: 1100, gain=0.14)
    mix += sub_drone(ch, total, 0.2)
    # the intrigue figure under the planning
    figure = ["D4", None, "F4", "A4", None, "G#4", "A4", None, "D4", None, "F4", "E4", None, "C#4", "D4", None]
    t = T("idea")
    while t < T("seraph") - 2:
        mix += pluck_line(figure, t, total, 0.3, 0.12)
        t += 0.3 * len(figure)
    mix += ostinato(T("seraph"), T("spain") + 1, total, 66, "D2", gain=0.22)
    mix += ostinato(T("husky"), T("legacy") - 1, total, 84, "D2", gain=0.26)
    for h in (T("problem"), T("seraph"), T("swallowed"), T("husky")):
        t0, v = timpani(h - 0.05, 0.45)
        i0 = int(t0 * SR)
        mix[i0:i0 + len(v), 0] += v[:len(mix) - i0]
        mix[i0:i0 + len(v), 1] += v[:len(mix) - i0]
    hymn = [("F4", 1.5), ("F4", 0.5), ("G4", 1.0), ("A4", 1.0), ("A#4", 2.0), ("A4", 2.0), ("G4", 1.0), ("F4", 1.0),
            ("E4", 1.0), ("F4", 1.0), ("D4", 3.0), (None, 1.0), ("A4", 1.5), ("G4", 0.5), ("F4", 1.0), ("E4", 1.0),
            ("D4", 2.0), ("C#4", 1.0), ("D4", 5.0)]
    mix += melody(hymn, T("legacy") + 0.3, total, 0.10)
    return mix[:int(total * SR)]


# ------------------------------------------------------------------ 1943 sound effects
def _clicks(d, rate_fn, band=(1500, 6000), dur=0.015, gain=0.5):
    n = int(d * SR)
    out = np.zeros(n)
    t = 0.05
    while t < d:
        m = int(dur * SR)
        s_ = noise(m) * np.exp(-np.arange(m) / SR / (dur / 4))
        i0 = int(t * SR)
        out[i0:i0 + m] += s_[:n - i0] * RNG.uniform(0.6, 1.0)
        t += rate_fn()
    return bp(out, *band) * gain


def fx_typewriter(d):
    v = _clicks(d, lambda: RNG.uniform(0.07, 0.2) if RNG.random() > 0.05 else 0.6, (1200, 7000), 0.02, 0.8)
    n = len(v)
    t = 2.5
    while t < d - 0.5:   # carriage return bell
        m = int(0.6 * SR)
        tt = np.arange(m) / SR
        b = np.sin(2 * np.pi * 2100 * tt) * np.exp(-tt / 0.2) * 0.15
        i0 = int(t * SR)
        v[i0:i0 + m] += b[:n - i0]
        t += RNG.uniform(3, 5)
    return v


def fx_clock(d):
    return _clicks(d, lambda: 1.0, (2000, 6000), 0.01, 0.5)


def fx_teleprinter(d):
    return _clicks(d, lambda: 1 / 6.67, (800, 5000), 0.03, 0.6) + lp(noise(int(d * SR)), 150) * 0.05


def fx_shutter(d=1.0):
    n = int(1.0 * SR)
    out = np.zeros(n)
    for t0 in (0.0, 0.09):
        m = int(0.03 * SR)
        out[int(t0 * SR):int(t0 * SR) + m] += hp(noise(m), 1500) * np.exp(-np.arange(m) / SR / 0.006)
    return out * 0.8


def fx_stamp(d=1.0):
    n = int(1.0 * SR)
    tt = np.arange(n) / SR
    return lp(noise(n), 500) * np.exp(-tt / 0.03) * 0.9


def fx_bells(d):
    n = int(d * SR)
    out = np.zeros(n)
    t = 0.5
    while t < d - 1:
        m = int(3.0 * SR)
        tt = np.arange(m) / SR
        f = 440 * RNG.choice([1.0, 1.26, 1.5])
        b = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 2.76 * tt)) * np.exp(-tt / 1.2) * 0.1
        i0 = int(t * SR)
        out[i0:i0 + m] += b[:n - i0]
        t += 2.2
    return out


def fx_diesel(d):
    n = int(d * SR)
    t = np.arange(n) / SR
    v = saw(24, n) * 0.4 * (0.8 + 0.2 * np.sin(2 * np.pi * 6 * t))
    return lp(v, 300) + lp(noise(n), 200) * 0.05


def fx_planes(d):
    n = int(d * SR)
    t = np.arange(n) / SR
    v = saw(85, n) * 0.2 + saw(86.3, n) * 0.2
    return lp(v, 600) * (0.4 + 0.6 * np.sin(np.pi * np.clip(t / d, 0, 1)))


def fx_birds(d):
    n = int(d * SR)
    out = np.zeros(n)
    t = 0.3
    while t < d - 0.5:
        m = int(RNG.uniform(0.08, 0.2) * SR)
        tt = np.arange(m) / SR
        f = RNG.uniform(3000, 5000) + 800 * np.sin(2 * np.pi * RNG.uniform(8, 20) * tt)
        s_ = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / tt[-1]) * 0.06
        i0 = int(t * SR)
        out[i0:i0 + m] += s_[:n - i0]
        t += RNG.uniform(0.3, 1.2)
    return out


def fx_guns_far(d):
    n = int(d * SR)
    out = lp(noise(n), 120) * 0.06
    t = 0.2
    while t < d:
        b = FA.fx_boom(3.0, 260, 0.6) * RNG.uniform(0.35, 1.0)
        i0 = int(t * SR)
        out[i0:i0 + len(b)] += b[:n - i0] * 0.5
        t += RNG.uniform(0.6, 1.8)
    return out


FA.SFX.update({
    "typewriter": (fx_typewriter, True), "clock": (fx_clock, True), "teleprinter": (fx_teleprinter, True),
    "shutter": (lambda d: fx_shutter(), False), "stamp": (lambda d: fx_stamp(), False), "bells": (fx_bells, True),
    "diesel": (fx_diesel, True), "planes": (fx_planes, True), "birds": (fx_birds, True),
    "guns_far": (fx_guns_far, True), "crowd": (fx_crowd, True), "rain": (fx_rain, True), "wind": (fx_wind, True),
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
