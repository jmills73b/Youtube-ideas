"""Period post-processing.

film: 16mm news-film / war-art look -- warm grade, clumpy grain, vignette,
      gate weave, dust and the odd scratch.
tv:   1982 broadcast look -- scanlines, chroma bleed, bloom, soft vignette.
paper: printed/document look -- paper grain and uneven light.
"""
import functools

import numpy as np
from PIL import Image, ImageFilter

from .core import H, W, hash01


@functools.lru_cache(maxsize=1)
def _grain_bank():
    r = np.random.default_rng(1982)
    bank = []
    for _ in range(8):
        g = r.standard_normal((H // 2, W // 2)).astype(np.float32)
        img = Image.fromarray(((g * 0.18 + 0.5).clip(0, 1) * 255).astype(np.uint8))
        img = img.resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(0.6))
        bank.append((np.asarray(img, dtype=np.float32) / 255 - 0.5) * 2.2)
    return bank


@functools.lru_cache(maxsize=4)
def _vignette(strength, roundness=1.0):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    nx = (x - W / 2) / (W / 2)
    ny = (y - H / 2) / (H / 2) * roundness
    d = np.sqrt(nx * nx * 0.78 + ny * ny * 0.95)
    v = 1 - strength * np.clip(d - 0.35, 0, None) ** 1.7
    return np.clip(v, 0, 1)[:, :, None].astype(np.float32)


@functools.lru_cache(maxsize=1)
def _scanlines():
    y = np.arange(H, dtype=np.float32)
    s = 0.90 + 0.10 * (0.5 + 0.5 * np.cos(y * 2 * np.pi / 3.0))
    return s[:, None, None]


@functools.lru_cache(maxsize=1)
def _paper():
    from .core import fbm
    n = fbm(W, H, seed=77, octaves=6, base=6)
    fine = np.random.default_rng(5).random((H, W)).astype(np.float32)
    return (0.93 + 0.07 * n + 0.03 * (fine - 0.5))[:, :, None]


def _blur_small(img, factor=8, radius=3):
    h, w = img.shape[:2]
    small = img.reshape(h // factor, factor, w // factor, factor, 3).mean(axis=(1, 3))
    pil = Image.fromarray((np.clip(small, 0, 1) * 255).astype(np.uint8))
    pil = pil.filter(ImageFilter.GaussianBlur(radius)).resize((w, h), Image.BILINEAR)
    return np.asarray(pil, dtype=np.float32) / 255


def _grade(img, lift, gain, sat):
    lum = img @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    img = lum[:, :, None] + (img - lum[:, :, None]) * sat
    img = img * np.asarray(gain, dtype=np.float32) + np.asarray(lift, dtype=np.float32)
    return img


def film(img, frame, strength=1.0, warm=True, dust=True):
    bank = _grain_bank()
    # gate weave: sub-frame jitter of the whole picture
    dx = int(round((hash01(frame, 1) - 0.5) * 2.4 * strength))
    dy = int(round((hash01(frame, 2) - 0.5) * 1.6 * strength))
    if dx or dy:
        img = np.roll(img, (dy, dx), axis=(0, 1))
        if dy > 0:
            img[:dy] = img[dy:dy + 1]
        elif dy < 0:
            img[dy:] = img[dy - 1:dy]
        if dx > 0:
            img[:, :dx] = img[:, dx:dx + 1]
        elif dx < 0:
            img[:, dx:] = img[:, dx - 1:dx]
    if warm:
        img = _grade(img, (0.022, 0.016, 0.010), (1.02, 0.99, 0.92), 0.86)
    else:
        img = _grade(img, (0.012, 0.014, 0.018), (0.98, 1.0, 1.02), 0.9)
    # flicker
    img = img * (1 + (hash01(frame, 3) - 0.5) * 0.035 * strength)
    # bloom on highlights
    hi = np.clip(img - 0.62, 0, None)
    img = img + _blur_small(hi, 8, 4) * 0.55
    g = bank[frame % len(bank)]
    oy, ox = int(hash01(frame, 4) * 40), int(hash01(frame, 5) * 40)
    g = np.roll(g, (oy, ox), axis=(0, 1))
    lum = img.mean(axis=2, keepdims=True)
    amt = 0.055 * strength * (0.6 + 0.8 * (1 - np.abs(lum - 0.5) * 1.6))
    img = img + g[:, :, None] * amt
    img = img * _vignette(0.75)
    if dust:
        img = _dust(img, frame, strength)
    return img


def _dust(img, frame, strength):
    r = np.random.default_rng(frame * 7919 + 13)
    n = r.poisson(2.2 * strength)
    for _ in range(n):
        x, y = int(r.random() * (W - 8)), int(r.random() * (H - 8))
        s = int(1 + r.random() * 3)
        v = 0.55 if r.random() < 0.7 else 1.5
        img[y:y + s, x:x + s + int(r.random() * 3)] *= v
    if r.random() < 0.10 * strength:  # vertical scratch
        x = int(r.random() * W)
        y0 = int(r.random() * H * 0.5)
        img[y0:, x:x + 1] = img[y0:, x:x + 1] * 0.6 + 0.35
    return img


def tv(img, frame, strength=1.0):
    # chroma bleed: shift red right, blue left, soften colour detail
    s = int(round(2 * strength))
    if s:
        img = img.copy()
        img[:, :, 0] = np.roll(img[:, :, 0], s, axis=1)
        img[:, :, 2] = np.roll(img[:, :, 2], -s, axis=1)
    hi = np.clip(img - 0.55, 0, None)
    img = img + _blur_small(hi, 8, 5) * 0.7 * strength
    img = img * (1 - (1 - _scanlines()) * strength)
    bank = _grain_bank()
    g = bank[(frame * 3) % len(bank)]
    img = img + g[:, :, None] * 0.022 * strength
    img = img * _vignette(0.55)
    # occasional faint roll bar
    phase = (frame * 3.1) % (H * 1.6)
    if phase < H:
        yy = np.arange(H, dtype=np.float32)
        bar = 1 + 0.025 * strength * np.exp(-((yy - phase) / 60) ** 2)
        img = img * bar[:, None, None]
    return img


def paper(img, frame, strength=1.0):
    img = img * _paper()
    img = _grade(img, (0.02, 0.015, 0.005), (1.0, 0.97, 0.9), 0.9)
    bank = _grain_bank()
    img = img + bank[frame % len(bank)][:, :, None] * 0.03
    img = img * _vignette(0.8)
    return _dust(img, frame, 0.6 * strength)


def finish(img):
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


@functools.lru_cache(maxsize=1)
def _halftone_grid(cell=9, angle=0.785):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    ca, sa = np.cos(angle), np.sin(angle)
    u = (x * ca + y * sa) / cell
    v = (-x * sa + y * ca) / cell
    du = u - np.round(u)
    dv = v - np.round(v)
    return np.sqrt(du * du + dv * dv)  # 0 at dot centre, ~0.707 at cell corner


def halftone(img, frame, strength=1.0):
    """Newsprint/poster print: luminance rendered as a rotated dot screen."""
    d = _halftone_grid()
    lum = img @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    small = _blur_small(np.repeat(lum[:, :, None], 3, axis=2), 4, 1)[:, :, 0]
    radius = np.sqrt(np.clip(1 - small, 0, 1)) * 0.62
    ink = np.clip((radius - d) * 6 + 0.5, 0, 1)[:, :, None]
    ink_col = np.array([0.1, 0.09, 0.1], dtype=np.float32)
    printed = img * (1 - ink * 0.55 * strength) + ink_col * ink * 0.35 * strength
    return paper(printed, frame, 0.8)
