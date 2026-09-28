"""1943 visual kit for the Operation Mincemeat film.

Builds on the shared engine in ../falklands/engine and the silent-film helpers
in ../somme/ww1, adding a wartime newsreel look, secret-file documents,
War Office-style maps and wartime artwork.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REPO = os.path.dirname(ROOT)
sys.path.append(os.path.join(REPO, "falklands"))
sys.path.append(os.path.join(REPO, "somme"))

from engine import core  # noqa: E402

_F = os.path.join(ROOT, "assets", "fonts")
core.FONTS.update({
    "oldstd": os.path.join(_F, "OldStandard-Regular.ttf"),
    "oldstd_b": os.path.join(_F, "OldStandard-Bold.ttf"),
    "courier_r": os.path.join(_F, "CourierPrime-Regular.ttf"),
})
