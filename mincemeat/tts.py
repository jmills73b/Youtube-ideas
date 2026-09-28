"""Voice the Mincemeat narration with Kokoro (offline neural TTS) and write timing data.

Outputs (in build/):
  narration.wav   mono 24 kHz narration with pauses
  timing.json     start/end of every sentence and segment
  captions.srt    YouTube-ready subtitles
"""
import json
import os
import re
import sys

import numpy as np
import soundfile as sf

from script import SEGMENTS

HERE = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(HERE, "build")
MODELS = os.path.join(os.path.dirname(HERE), "falklands", "models")   # shared with the Falklands film
MODEL = os.environ.get("KOKORO_MODEL", os.path.join(MODELS, "kokoro-v1.0.onnx"))
VOICES = os.environ.get("KOKORO_VOICES", os.path.join(MODELS, "voices-v1.0.bin"))
VOICE = os.environ.get("KOKORO_VOICE", "bm_george")
SPEED = float(os.environ.get("KOKORO_SPEED", "1.0"))

LEAD_IN = 3.2          # seconds of picture/music before the first word
SENTENCE_GAP = 0.38
SEGMENT_GAP = 1.05
TAIL = 6.0             # end card after the last word

# Written form -> spoken form (captions keep the written form).
SPOKEN = [
    (r"\b1943\b", "nineteen forty-three"),
    (r"\b1939\b", "nineteen thirty-nine"),
    (r"\b1998\b", "nineteen ninety-eight"),
    (r"Glyndwr", "Glin-door"),
    (r"Cholmondeley", "Chumly"),
    (r"Huelva", "Well-va"),
    (r"Abwehr", "Ab-vair"),
    (r"Clauss", "Clowss"),
    (r"HMS", "H M S"),
    (r"MI5", "M I 5"),
    (r"Mountbatten", "Mount-batten"),
]


def spoken(text):
    for pat, rep in SPOKEN:
        text = re.sub(pat, rep, text)
    return text


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def trim(samples, sr, thresh=0.004):
    """Trim leading/trailing near-silence, keeping a few ms of padding."""
    idx = np.where(np.abs(samples) > thresh)[0]
    if len(idx) == 0:
        return samples
    pad = int(0.03 * sr)
    return samples[max(0, idx[0] - pad): idx[-1] + pad]


def main():
    from kokoro_onnx import Kokoro

    os.makedirs(BUILD, exist_ok=True)
    kok = Kokoro(MODEL, VOICES)
    sr = 24000
    chunks = [np.zeros(int(LEAD_IN * sr), dtype=np.float32)]
    t = LEAD_IN
    timing = {"segments": [], "sr": sr}
    for si, seg in enumerate(SEGMENTS):
        seg_info = {"id": seg["id"], "chapter": seg["chapter"], "start": t, "sentences": []}
        for ji, sent in enumerate(seg["sentences"]):
            audio, sr_ = kok.create(spoken(sent), voice=VOICE, speed=SPEED, lang="en-gb")
            assert sr_ == sr
            audio = trim(np.asarray(audio, dtype=np.float32), sr)
            dur = len(audio) / sr
            seg_info["sentences"].append({"text": sent, "start": t, "end": t + dur})
            chunks.append(audio)
            t += dur
            last = ji == len(seg["sentences"]) - 1
            gap = SEGMENT_GAP if last else SENTENCE_GAP
            chunks.append(np.zeros(int(gap * sr), dtype=np.float32))
            t += gap
            print(f"  [{seg['id']}] {dur:5.2f}s  {sent[:60]}", file=sys.stderr)
        seg_info["end"] = t
        timing["segments"].append(seg_info)
    chunks.append(np.zeros(int(TAIL * sr), dtype=np.float32))
    t += TAIL
    timing["total"] = t
    audio = np.concatenate(chunks)
    peak = np.max(np.abs(audio))
    audio = audio / peak * 0.89
    sf.write(os.path.join(BUILD, "narration.wav"), audio, sr)
    with open(os.path.join(BUILD, "timing.json"), "w") as f:
        json.dump(timing, f, indent=1, ensure_ascii=False)

    # Captions: split long sentences into two-line-friendly chunks.
    lines = []
    n = 1
    for seg in timing["segments"]:
        for s in seg["sentences"]:
            words = s["text"].split()
            parts = []
            cur = []
            for w in words:
                cur.append(w)
                if len(" ".join(cur)) > 70 and w[-1] in ",.;":
                    parts.append(" ".join(cur))
                    cur = []
            if cur:
                parts.append(" ".join(cur))
            total_chars = sum(len(p) for p in parts)
            st = s["start"]
            for p in parts:
                d = (s["end"] - s["start"]) * len(p) / total_chars
                lines.append(f"{n}\n{srt_time(st)} --> {srt_time(st + d)}\n{p}\n")
                n += 1
                st += d
    with open(os.path.join(BUILD, "captions.srt"), "w") as f:
        f.write("\n".join(lines))
    print(f"total {t:.1f}s ({t/60:.2f} min)", file=sys.stderr)


if __name__ == "__main__":
    main()
