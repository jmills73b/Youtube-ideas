"""1916 visual kit for the Somme film.

Builds on the shared engine in ../falklands/engine (canvas, text, noise, skies,
smoke, figures) and adds the Great War look: silent-film grade, intertitles,
trench maps, and trench-war artwork.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.append(os.path.join(os.path.dirname(ROOT), "falklands"))

from engine import core  # noqa: E402

_FONTS = os.path.join(ROOT, "assets", "fonts")
core.FONTS.update({
    "fell": os.path.join(_FONTS, "IMFeENrm28P.ttf"),
    "fell_i": os.path.join(_FONTS, "IMFeENit28P.ttf"),
    "fell_sc": os.path.join(_FONTS, "IMFeENsc28P.ttf"),
    "fell_pica": os.path.join(_FONTS, "IMFePIsc28P.ttf"),
    "oldstd": os.path.join(_FONTS, "OldStandard-Regular.ttf"),
    "oldstd_b": os.path.join(_FONTS, "OldStandard-Bold.ttf"),
})
