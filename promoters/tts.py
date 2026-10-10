"""Voice the beats (generic synthetic voices) and build the timeline.

Outputs build/dialogue.wav, build/timeline.json, build/env.npy (per-frame mouth
openness for every beat) and build/captions.srt.
"""
import json
import os
import sys

import numpy as np
import soundfile as sf

from script import BEATS, VOICES

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
MODELS = os.path.join(os.path.dirname(HERE), "falklands", "models")
FPS = 30
SR = 24000


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    from kokoro_onnx import Kokoro
    kok = Kokoro(os.path.join(MODELS, "kokoro-v1.0.onnx"), os.path.join(MODELS, "voices-v1.0.bin"))
    os.makedirs(BUILD, exist_ok=True)
    chunks, beats, t = [], [], 0.0
    for shot, who, text, pause in BEATS:
        if who:
            voice, speed = VOICES[who]
            a, _ = kok.create(text, voice=voice, speed=speed, lang="en-us" if voice.startswith("a") else "en-gb")
            a = np.asarray(a, dtype=np.float32)
            idx = np.where(np.abs(a) > 0.004)[0]
            a = a[max(0, idx[0] - 600): idx[-1] + 600]
            d = len(a) / SR
            beats.append({"shot": shot, "who": who, "text": text, "start": t, "end": t + d})
            chunks.append(a)
            t += d
        else:
            beats.append({"shot": shot, "who": None, "text": None, "start": t, "end": t})
        n = int(pause * SR)
        chunks.append(np.zeros(n, dtype=np.float32))
        beats[-1]["end_pause"] = t + pause
        t += pause
        print(f"{shot:18s} {who or '-':6s} {t:6.2f}", file=sys.stderr)
    audio = np.concatenate(chunks)
    audio = audio / np.max(np.abs(audio)) * 0.89
    sf.write(os.path.join(BUILD, "dialogue.wav"), audio, SR)
    # per-frame mouth openness (smoothed RMS)
    hop = SR // FPS
    nfr = len(audio) // hop + 1
    rms = np.array([np.sqrt(np.mean(audio[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(nfr)])
    env = np.clip((rms - 0.01) / 0.12, 0, 1)
    np.save(os.path.join(BUILD, "env.npy"), env.astype(np.float32))
    json.dump({"beats": beats, "total": t}, open(os.path.join(BUILD, "timeline.json"), "w"), indent=1)
    lines = []
    for i, b in enumerate([b for b in beats if b["who"]]):
        name = {"DANA": "DANA", "EDDIE": "EDDIE", "INT": "(INTERVIEWER)", "GARY": "GARY"}[b["who"]]
        lines.append(f"{i + 1}\n{srt_time(b['start'])} --> {srt_time(b['end'] + 0.3)}\n{name}: {b['text']}\n")
    open(os.path.join(BUILD, "captions.srt"), "w").write("\n".join(lines))
    print(f"total {t:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
