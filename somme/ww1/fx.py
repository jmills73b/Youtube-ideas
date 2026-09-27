"""The 1916 look: orthochromatic silent film, printed onto tinted stock.

silent(): monochrome with a sepia (or blue night) tint, crushed blacks and
          blooming highlights, heavy flicker and uneven exposure, big gate
          weave, dust, hairs and running scratches.
print_(): lithograph / map paper for posters, maps and documents.
"""
import functools

import numpy as np
from PIL import Image, ImageFilter

from engine import fx as F
from engine.core import H, W, hash01

TINTS = {
    "sepia": np.array([1.0, 0.86, 0.66], dtype=np.float32),
    "amber": np.array([1.0, 0.8, 0.5], dtype=np.float32),
    "night": np.array([0.62, 0.78, 1.0], dtype=np.float32),   # blue tint = night, as in 1916 prints
    "grey": np.array([0.97, 0.96, 0.93], dtype=np.float32),
}


@functools.lru_cache(maxsize=1)
def _soft_vignette():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    nx, ny = (x - W / 2) / (W / 2), (y - H / 2) / (H / 2)
    d = np.sqrt(nx ** 2 * 0.7 + ny ** 2)
    return np.clip(1 - 0.9 * np.clip(d - 0.45, 0, None) ** 1.5, 0, 1)[:, :, None]


def _soften(img, amount=0.6):
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    blur = np.asarray(pil.filter(ImageFilter.GaussianBlur(1.2)), dtype=np.float32) / 255
    return img * (1 - amount) + blur * amount


def _hairs(img, frame, strength):
    r = np.random.default_rng(frame * 131 + 7)
    if r.random() < 0.06 * strength:          # a hair caught in the gate
        x0, y0 = r.random() * W, r.random() * H
        ang = r.random() * 6.28
        for k in range(120):
            ang += (r.random() - 0.5) * 0.3
            x0 += np.cos(ang) * 2
            y0 += np.sin(ang) * 2
            xi, yi = int(x0), int(y0)
            if 0 <= xi < W - 2 and 0 <= yi < H - 2:
                img[yi:yi + 2, xi:xi + 2] *= 0.25
    # running scratches that persist for a few frames
    seg = frame // 9
    rr = np.random.default_rng(seg * 17 + 3)
    for k in range(rr.integers(0, 3)):
        x = int((rr.random() * W + (frame % 9) * (rr.random() - 0.5) * 2) % W)
        y0 = int(rr.random() * H * 0.3)
        y1 = int(H - rr.random() * H * 0.3)
        img[y0:y1, x:x + 1] = img[y0:y1, x:x + 1] * 0.5 + 0.45 * strength
    return img


def silent(img, frame, tint="sepia", strength=1.0):
    lum = img @ np.array([0.30, 0.59, 0.11], dtype=np.float32)
    lum = _soften(lum[:, :, None].repeat(3, axis=2), 0.5)[:, :, 0]
    # orthochromatic response and contrasty print: s-curve with crushed blacks
    lum = np.clip((lum - 0.04) / 0.94, 0, 1)
    lum = lum * lum * (3 - 2 * lum) * 0.8 + lum * 0.2
    # flicker + uneven exposure across the frame
    fl = 1 + (hash01(frame, 21) - 0.5) * 0.12 * strength
    grad = 1 + (hash01(frame // 3, 22) - 0.5) * 0.10 * strength * np.linspace(-1, 1, W, dtype=np.float32)[None, :]
    lum = lum * fl * grad
    img = lum[:, :, None] * TINTS[tint][None, None, :]
    # gate weave (larger than 16mm news film)
    dx = int(round((hash01(frame, 23) - 0.5) * 5 * strength))
    dy = int(round((hash01(frame, 24) - 0.5) * 4 * strength))
    if dx or dy:
        img = np.roll(img, (dy, dx), axis=(0, 1))
        if dy > 0:
            img[:dy] = 0
        elif dy < 0:
            img[dy:] = 0
        if dx > 0:
            img[:, :dx] = 0
        elif dx < 0:
            img[:, dx:] = 0
    bank = F._grain_bank()
    g = bank[(frame * 5) % len(bank)]
    img = img + g[:, :, None] * 0.085 * strength
    img = img * _soft_vignette()
    img = F._dust(img, frame, 2.2 * strength)
    img = _hairs(img, frame, strength)
    return img


def print_(img, frame, strength=1.0):
    """Printed paper: maps, posters, documents (steady, fine grain, slight vignette)."""
    img = F.paper(img, frame, strength)
    return img
