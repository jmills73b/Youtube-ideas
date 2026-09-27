"""Score, sound effects and final mix.

Everything is synthesised here (no samples), in the idiom of early-1980s TV
documentary scores: detuned analogue-style string pads, a low ostinato for the
war sections, timpani hits, and a lone elegiac line for the ending.

  python3 audio.py   ->  build/mix.wav (48 kHz stereo)
"""
import json
import math
import os
import subprocess
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, sosfiltfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BUILD = os.path.join(HERE, "build")
SR = 48000
RNG = np.random.default_rng(1982)

NOTE = {n: i for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}
NOTE.update({"Db": 1, "Eb": 3, "Gb": 6, "Ab": 8, "Bb": 10})


def hz(name):
    """'D3' -> frequency."""
    n, o = name[:-1], int(name[-1])
    return 440.0 * 2 ** ((NOTE[n] + 12 * (o + 1) - 69) / 12)


def lp(x, cutoff, order=2):
    sos = butter(order, min(cutoff, SR * 0.45), "low", fs=SR, output="sos")
    return sosfilt(sos, x)


def hp(x, cutoff, order=2):
    sos = butter(order, cutoff, "high", fs=SR, output="sos")
    return sosfilt(sos, x)


def bp(x, lo, hi, order=2):
    sos = butter(order, [lo, min(hi, SR * 0.45)], "band", fs=SR, output="sos")
    return sosfilt(sos, x)


def env_adsr(n, a, r, sustain_to=None):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na) ** 1.5
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr) ** 1.5
    return e


def noise(n):
    return RNG.standard_normal(n)


def saw(freq, n, phase=0.0):
    t = np.arange(n) / SR
    return 2 * ((freq * t + phase) % 1.0) - 1


# ------------------------------------------------------------------ score
CHORDS = {
    "Dm": ["D3", "A3", "D4", "F4", "A4"],
    "Dm9": ["D3", "A3", "E4", "F4", "A4"],
    "Bb": ["A#2", "F3", "A#3", "D4", "F4"],
    "Bbmaj7": ["A#2", "F3", "A3", "D4", "F4"],
    "F": ["F2", "C3", "F3", "A3", "C4"],
    "C": ["C3", "G3", "C4", "E4", "G4"],
    "Gm": ["G2", "D3", "G3", "A#3", "D4"],
    "Eb": ["D#2", "A#2", "D#3", "G3", "A#3"],
    "A": ["A2", "E3", "A3", "C#4", "E4"],
    "Asus": ["A2", "E3", "A3", "D4", "E4"],
    "Am": ["A2", "E3", "A3", "C4", "E4"],
}


def pad(chord_seq, total, cutoff_fn, gain=1.0):
    """chord_seq: list of (start, dur, chord). Returns stereo pad."""
    out = np.zeros((int(total * SR) + SR, 2))
    for start, dur, name in chord_seq:
        n = int((dur + 2.5) * SR)
        i0 = int(start * SR)
        e = env_adsr(n, 1.6, 2.6)
        for k, note in enumerate(CHORDS[name]):
            f = hz(note)
            amp = 0.9 if k == 0 else 0.55
            for ch, det in enumerate((-1, 1)):
                v = np.zeros(n)
                for d in (-7, 0, 7):
                    cents = d + det * 3
                    v += saw(f * 2 ** (cents / 1200), n, phase=RNG.random())
                v = lp(v / 3, cutoff_fn(start))
                seg = out[i0:i0 + n, ch]
                seg += v[:len(seg)] * e[:len(seg)] * amp * gain
    return out


def sub_drone(chord_seq, total, gain=0.35):
    out = np.zeros(int(total * SR) + SR)
    for start, dur, name in chord_seq:
        n = int((dur + 2.5) * SR)
        i0 = int(start * SR)
        f = hz(CHORDS[name][0]) / 2
        t = np.arange(n) / SR
        v = np.sin(2 * np.pi * f * t) * env_adsr(n, 1.5, 2.5)
        seg = out[i0:i0 + n]
        seg += v[:len(seg)] * gain
    return np.stack([out, out], axis=1)


def ostinato(t0, t1, total, bpm=76, root="D2", gain=0.5):
    """Low staccato string pulse for the war sections."""
    out = np.zeros(int(total * SR) + SR)
    beat = 60 / bpm / 2
    pattern = [root, root, root, "F2", root, root, "C2", "A#1"]
    t = t0
    k = 0
    while t < t1:
        n = int(0.32 * SR)
        f = hz(pattern[k % len(pattern)])
        v = (saw(f, n) + saw(f * 1.003, n)) / 2
        e = np.exp(-np.arange(n) / SR / 0.09)
        e[:int(0.008 * SR)] *= np.linspace(0, 1, int(0.008 * SR))
        v = lp(v * e, 700)
        accent = 1.0 if k % 4 == 0 else 0.62
        fade = min(1, (t - t0) / 4, (t1 - t) / 3)
        i0 = int(t * SR)
        seg = out[i0:i0 + n]
        seg += v[:len(seg)] * gain * accent * max(0, fade)
        t += beat
        k += 1
    return np.stack([out * 0.9, out], axis=1)


def timpani(t, gain=1.0, f0=62):
    n = int(2.5 * SR)
    tt = np.arange(n) / SR
    f = f0 * (1 + 0.6 * np.exp(-tt / 0.03))
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-tt / 0.7)
    hit = lp(noise(n), 900) * np.exp(-tt / 0.05) * 0.5
    return t, (body + hit) * gain


def melody(notes, t0, total, gain=0.25):
    """Solo elegiac line: soft triangle wave with slow vibrato."""
    out = np.zeros(int(total * SR) + SR)
    t = t0
    for name, dur in notes:
        if name is None:
            t += dur
            continue
        n = int((dur + 0.8) * SR)
        tt = np.arange(n) / SR
        f = hz(name) * (1 + 0.004 * np.sin(2 * np.pi * 5.2 * tt) * np.clip(tt / 0.8, 0, 1))
        ph = np.cumsum(f) / SR
        tri = 2 * np.abs(2 * (ph % 1) - 1) - 1
        v = lp(tri + 0.15 * np.sin(2 * np.pi * ph * 2), 2400) * env_adsr(n, 0.35, 0.9)
        i0 = int(t * SR)
        seg = out[i0:i0 + n]
        seg += v[:len(seg)] * gain
        t += dur
    return np.stack([out * 0.95, out], axis=1)


def build_score(timing, total):
    seg = {s["id"]: s for s in timing["segments"]}
    T = lambda sid, k="start": seg[sid][k]  # noqa: E731

    def run(t0, t1, prog, step):
        seq = []
        t, i = t0, 0
        while t < t1 - 0.5:
            d = min(step, t1 - t)
            seq.append((t, d, prog[i % len(prog)]))
            t += d
            i += 1
        return seq

    chords = []
    chords += run(0.0, T("history"), ["Dm9", "Bbmaj7", "Dm9", "Asus"], 7.5)
    chords += run(T("history"), T("road"), ["Dm", "Bb", "F", "C"], 6.5)
    chords += run(T("road"), T("invasion"), ["Gm", "Dm", "Eb", "A"], 6.0)
    chords += run(T("invasion"), T("sancarlos"), ["Dm", "Bb", "Gm", "A"], 5.0)
    chords += run(T("sancarlos"), T("surrender"), ["Dm", "Eb", "Bb", "A"], 4.5)
    chords += run(T("surrender"), T("legacy"), ["F", "C", "Dm", "Bb"], 5.0)
    chords += run(T("legacy"), total, ["Dm", "Bbmaj7", "F", "C", "Dm9"], 7.0)

    def cutoff(t):
        if T("invasion") <= t < T("surrender"):
            return 1500
        if t >= T("legacy"):
            return 1100
        return 850

    mix = pad(chords, total, cutoff, gain=0.16)
    mix += sub_drone(chords, total, 0.22)
    mix += ostinato(T("invasion"), T("taskforce") + 2, total, 72, gain=0.30)
    mix += ostinato(T("belgrano"), T("surrender"), total, 76, gain=0.34)
    hits = [T("open", "start") + timing["segments"][0]["sentences"][2]["start"] - timing["segments"][0]["start"],
            T("invasion"), T("taskforce"), T("belgrano"), T("sancarlos"), T("fitzroy"), T("mountains"),
            T("surrender")]
    for h in hits:
        t, v = timpani(h - 0.05, 0.55)
        i0 = int(t * SR)
        mix[i0:i0 + len(v), 0] += v[:len(mix) - i0]
        mix[i0:i0 + len(v), 1] += v[:len(mix) - i0]
    lament = [("A4", 2.0), ("D5", 2.0), ("C5", 1.0), ("A#4", 1.0), ("A4", 3.0), ("G4", 1.0), ("F4", 2.0),
              ("E4", 1.0), ("D4", 4.0), (None, 1.0), ("F4", 1.5), ("G4", 0.5), ("A4", 2.0), ("A#4", 1.0),
              ("A4", 1.0), ("G4", 1.5), ("F4", 0.5), ("E4", 1.0), ("D4", 5.0)]
    mix += melody(lament, T("legacy") + 0.5, total, 0.10)
    return mix[:int(total * SR)]


# ------------------------------------------------------------------ sound effects
def fx_sea(d):
    n = int(d * SR)
    t = np.arange(n) / SR
    body = lp(np.cumsum(noise(n)) * 0.02, 500)
    body = hp(body, 40)
    wave = 0.55 + 0.45 * np.sin(2 * np.pi * t / 6.5) ** 2
    hiss = bp(noise(n), 1500, 6000) * 0.15 * wave
    v = body / (np.std(body) + 1e-9) * 0.25 * wave + hiss
    return v


def fx_wind(d):
    n = int(d * SR)
    t = np.arange(n) / SR
    v = bp(noise(n), 250, 1100)
    mod = 0.5 + 0.5 * np.sin(2 * np.pi * t / 7.3 + 1) * np.sin(2 * np.pi * t / 3.1)
    return v / (np.std(v) + 1e-9) * 0.2 * (0.4 + 0.6 * mod)


def fx_rain(d):
    n = int(d * SR)
    v = hp(noise(n), 3000) * 0.12
    drops = np.zeros(n)
    idx = RNG.integers(0, n, int(d * 40))
    drops[idx] = RNG.random(len(idx)) * 0.6
    drops = bp(drops, 2000, 8000)
    return v + drops


def fx_crowd(d):
    n = int(d * SR)
    t = np.arange(n) / SR
    v = np.zeros(n)
    for k in range(6):
        b = bp(noise(n), 300 + k * 150, 900 + k * 250)
        am = 0.5 + 0.5 * np.sin(2 * np.pi * (3 + k * 0.7) * t + k)
        v += b * am
    swell = 0.6 + 0.4 * np.sin(2 * np.pi * t / 4.5) ** 2
    return v / (np.std(v) + 1e-9) * 0.18 * swell


def fx_horn(d=3.0):
    n = int(d * SR)
    v = saw(110, n) + 0.7 * saw(138.6, n)
    return lp(v, 700) * env_adsr(n, 0.15, 0.6) * 0.35


def fx_gulls(d):
    n = int(d * SR)
    out = np.zeros(n)
    for k in range(int(d / 1.8)):
        t0 = RNG.random() * (d - 1)
        m = int(0.35 * SR)
        tt = np.arange(m) / SR
        f = 1400 + 900 * np.sin(np.pi * tt / 0.35)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.35) * 0.15
        i0 = int(t0 * SR)
        out[i0:i0 + m] += s[:n - i0]
    return out


def fx_jet(d=2.2):
    n = int(d * SR)
    t = np.arange(n) / SR
    c = d * 0.45
    amp = np.exp(-((t - c) / 0.45) ** 2)
    v = np.zeros(n)
    blocks = 40
    src = noise(n)
    for b in range(blocks):
        i0, i1 = b * n // blocks, (b + 1) * n // blocks
        cutoff = 5000 if t[i0] < c else 1400
        v[i0:i1] = lp(src[max(0, i0 - 2000):i1], cutoff)[-(i1 - i0):]
    f = np.where(t < c, 900, 520)
    tone = np.sin(2 * np.pi * np.cumsum(lp(f.astype(float), 3)) / SR) * 0.15
    return (v / (np.std(v) + 1e-9) * 0.5 + tone) * amp


def fx_boom(d=4.0, cutoff=900, sub=0.8):
    n = int(d * SR)
    t = np.arange(n) / SR
    e = np.exp(-t / 0.7)
    e[:int(0.005 * SR)] *= np.linspace(0, 1, int(0.005 * SR))
    v = lp(noise(n), cutoff) * e
    v = v / (np.max(np.abs(v)) + 1e-9)
    thump = np.sin(2 * np.pi * 45 * t * (1 + 0.8 * np.exp(-t / 0.05))) * np.exp(-t / 0.5) * sub
    return (v + thump) * 0.8


def fx_splash(d=2.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    return bp(noise(n), 300, 5000) * np.exp(-t / 0.4) * 0.4 + fx_boom(d, 400, 0.4) * 0.5


def fx_gunfire(d=1.2, shots=10, gap=0.075):
    n = int(d * SR)
    out = np.zeros(n)
    for k in range(shots):
        m = int(0.06 * SR)
        s = hp(noise(m), 300) * np.exp(-np.arange(m) / SR / 0.012)
        i0 = int(k * gap * SR)
        out[i0:i0 + m] += s[:n - i0] * (0.8 + 0.2 * RNG.random())
    return lp(out, 3000) * 0.5


def fx_flare(d=3.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    pop = hp(noise(n), 800) * np.exp(-t / 0.02) * 0.6
    fizz = bp(noise(n), 2000, 7000) * 0.06 * np.exp(-t / 2.0)
    return pop + fizz


def fx_engine(d):
    n = int(d * SR)
    t = np.arange(n) / SR
    v = lp(noise(n), 400)
    v = v / (np.std(v) + 1e-9) * 0.25
    hum = np.sin(2 * np.pi * 118 * t) * 0.05 + np.sin(2 * np.pi * 236 * t) * 0.02
    return v + hum


def fx_stick(d=4.5):
    n = int(d * SR)
    out = np.zeros(n)
    for k in range(21):
        b = fx_boom(2.0, 500, 0.5) * (0.5 + 0.2 * RNG.random())
        i0 = int((0.2 + k * 0.09) * SR)
        out[i0:i0 + len(b)] += b[:n - i0]
    return out * 0.6


def fx_ping(d=3.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    v = np.sin(2 * np.pi * 1450 * t) * np.exp(-t / 0.35) * 0.25
    echo = np.zeros(n)
    echo[int(0.6 * SR):] = v[:n - int(0.6 * SR)] * 0.3
    return v + echo


def fx_launch(d=2.0):
    n = int(d * SR)
    t = np.arange(n) / SR
    return lp(noise(n), 600) * np.exp(-t / 0.5) * 0.4


def fx_rotor(d):
    n = int(d * SR)
    t = np.arange(n) / SR
    slap = (0.5 + 0.5 * np.sin(2 * np.pi * 17 * t)) ** 4
    v = lp(noise(n), 900) * slap
    return v / (np.std(v) + 1e-9) * 0.12


def fx_fire(d=6.0):
    n = int(d * SR)
    out = lp(noise(n), 300) * 0.1
    idx = RNG.integers(0, n, int(d * 30))
    cr = np.zeros(n)
    cr[idx] = RNG.random(len(idx))
    return out + bp(cr, 1500, 6000) * 0.4


def fx_blip(d=0.3):
    n = int(d * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1000 * t) * (t < 0.07) * 0.08


SFX = {
    "sea": (fx_sea, True), "wind": (fx_wind, True), "rain": (fx_rain, True), "crowd": (fx_crowd, True),
    "rotor": (fx_rotor, True), "engine": (fx_engine, True),
    "horn": (lambda d: fx_horn(3.0), False), "gulls": (fx_gulls, True), "jet": (lambda d: fx_jet(2.2), False),
    "missile": (lambda d: bp(noise(int(2.2 * SR)), 1500, 7000) * np.exp(-np.arange(int(2.2 * SR)) / SR / 1.2) * 0.3,
                False),
    "boom": (lambda d: fx_boom(4.0, 900, 0.9), False), "boom_far": (lambda d: fx_boom(3.0, 350, 0.5) * 0.6, False),
    "boom_muffled": (lambda d: lp(fx_boom(3.5, 250, 0.8), 300), False), "splash": (lambda d: fx_splash(2.0), False),
    "gunfire": (lambda d: fx_gunfire(), False), "flare": (lambda d: fx_flare(), False),
    "stick": (lambda d: fx_stick(), False), "ping": (lambda d: fx_ping(), False),
    "launch": (lambda d: fx_launch(), False), "fire": (fx_fire, True), "blip": (lambda d: fx_blip(), False),
}


def build_sfx(total):
    from render import ShotCtx, Timing, build_timeline
    timing = Timing(os.path.join(BUILD, "timing.json"))
    shots = build_timeline(timing)
    out = np.zeros(int(total * SR) + 10 * SR)
    for shot in shots:
        for cue in shot.get("sfx", []):
            when, kind, gain = cue[0], cue[1], cue[2]
            S = ShotCtx(shot, timing, shot["start"], 0)
            t_local = when(S) if callable(when) else when
            end_local = cue[3](S) if len(cue) > 3 else (shot["end"] - shot["start"] + 0.6)
            fn, ambient = SFX[kind]
            d = max(0.5, end_local - t_local)
            v = fn(d)
            if ambient:
                m = len(v)
                f = min(int(0.8 * SR), m // 2)
                v = v.copy()
                v[:f] *= np.linspace(0, 1, f)
                v[-f:] *= np.linspace(1, 0, f)
            i0 = int((shot["start"] + t_local) * SR)
            out[i0:i0 + len(v)] += v[:len(out) - i0] * gain
    return out[:int(total * SR)]


# ------------------------------------------------------------------ mix
def main():
    timing = json.load(open(os.path.join(BUILD, "timing.json")))
    total = timing["total"]
    nar_path = os.path.join(BUILD, "narration48.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(BUILD, "narration.wav"), "-ar",
                    str(SR), "-af", "highpass=f=70,acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,"
                    "equalizer=f=3000:t=q:w=1.2:g=2", nar_path], check=True)
    nar, sr = sf.read(nar_path)
    assert sr == SR
    n = int(total * SR)
    nar = np.pad(nar, (0, max(0, n - len(nar))))[:n]

    print("score...", file=sys.stderr)
    music = build_score(timing, total)
    print("sfx...", file=sys.stderr)
    sfx = build_sfx(total)

    # duck music and effects under the voice
    env = np.abs(nar)
    env = sosfiltfilt(butter(1, 3.0, "low", fs=SR, output="sos"), env)
    duck = 1 - 0.55 * np.clip(env / 0.05, 0, 1)
    music = music / (np.max(np.abs(music)) + 1e-9)
    sfx = sfx / (np.max(np.abs(sfx)) + 1e-9)
    mix = np.zeros((n, 2))
    mix += nar[:, None] * 1.0
    mix += music * 0.26 * duck[:, None]
    mix += sfx[:, None] * 0.30 * (0.55 + 0.45 * duck[:, None])
    # gentle fades
    f = int(1.0 * SR)
    mix[:f] *= np.linspace(0, 1, f)[:, None]
    f2 = int(3.0 * SR)
    mix[-f2:] *= np.linspace(1, 0, f2)[:, None]
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    sf.write(os.path.join(BUILD, "mix.wav"), mix.astype(np.float32), SR, subtype="FLOAT")
    sf.write(os.path.join(BUILD, "music_only.wav"), (music * 0.5).astype(np.float32), SR, subtype="FLOAT")
    print(f"mix.wav written ({total:.1f}s)", file=sys.stderr)


if __name__ == "__main__":
    main()
