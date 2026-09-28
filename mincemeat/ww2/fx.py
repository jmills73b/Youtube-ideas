"""The 1943 look.

newsreel(): 35mm black-and-white cinema newsreel - panchromatic tones, fine
            grain, gentle flicker, soft vignette, the odd speck of dust.
noir():     the same stock, harder contrast and deeper blacks, for the night
            and interior scenes of the plot.
"""
import functools

import numpy as np

from engine import fx as F
from engine.core import H, W, hash01


@functools.lru_cache(maxsize=1)
def _vig():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 * 0.75 + ((y - H / 2) / (H / 2)) ** 2)
    return np.clip(1 - 0.75 * np.clip(d - 0.5, 0, None) ** 1.6, 0, 1)[:, :, None]


def _mono(img, contrast, black, tone):
    lum = img @ np.array([0.25, 0.62, 0.13], dtype=np.float32)
    lum = np.clip((lum - black) / (1 - black), 0, 1)
    s = lum * lum * (3 - 2 * lum)
    lum = s * contrast + lum * (1 - contrast)
    return lum[:, :, None] * np.asarray(tone, dtype=np.float32)[None, None, :]


def newsreel(img, frame, strength=1.0, contrast=0.45, black=0.03, tone=(1.0, 0.985, 0.95)):
    img = _mono(img, contrast, black, tone)
    img = img * (1 + (hash01(frame, 31) - 0.5) * 0.05 * strength)
    dx = int(round((hash01(frame, 32) - 0.5) * 2 * strength))
    dy = int(round((hash01(frame, 33) - 0.5) * 2 * strength))
    if dx or dy:
        img = np.roll(img, (dy, dx), axis=(0, 1))
    hi = np.clip(img - 0.7, 0, None)
    img = img + F._blur_small(hi, 8, 4) * 0.4
    g = F._grain_bank()[(frame * 3) % 8]
    img = img + g[:, :, None] * 0.05 * strength
    img = img * _vig()
    return F._dust(img, frame, 0.8 * strength)


def noir(img, frame, strength=1.0):
    return newsreel(img, frame, strength, contrast=0.8, black=0.06, tone=(0.98, 0.98, 1.0))
