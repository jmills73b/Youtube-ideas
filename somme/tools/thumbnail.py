"""Render the YouTube thumbnail (1280x720) from the film's own artwork.

  python3 tools/thumbnail.py  ->  build/thumbnail.jpg
"""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

import ww1  # noqa: E402,F401
from PIL import Image  # noqa: E402

from engine import fx  # noqa: E402
from engine.core import H, W, draw_text, new_canvas, set_rgba, surface_to_rgb, vgrad  # noqa: E402
from shots import part2  # noqa: E402
from ww1 import cards as C  # noqa: E402
from ww1 import fx as WFX  # noqa: E402


class FakeS:
    def __init__(self, t, dur):
        self.t, self.dur, self.u, self.frame = t, dur, t / dur, 11

    def at(self, *a):
        return 99.0

    def word(self, *a):
        return 99.0


def main():
    surf, ctx = new_canvas()
    C.clock_text = lambda *a, **k: None       # no clock on the thumbnail
    part2.C.clock_text = C.clock_text
    part2.over_the_top(ctx, FakeS(3.2, 9.0))
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(vgrad(ctx, 0, 0, 0, H, [(0, (0, 0, 0), 0.75), (0.45, (0, 0, 0), 0.15), (1, (0, 0, 0), 0.0)]))
    ctx.fill()
    draw_text(ctx, "THE SOMME", W / 2, 250, "fell_sc", 230, (0.97, 0.94, 0.86), "cb", 1, 0.04, shadow=(6, 8, 0.9))
    draw_text(ctx, "1st July 1916", W / 2, 360, "fell_i", 96, (0.97, 0.94, 0.86), "cb", 1, shadow=(4, 5, 0.9))
    ctx.rectangle(W / 2 - 440, 410, 880, 110)
    set_rgba(ctx, (0.55, 0.08, 0.06))
    ctx.fill()
    draw_text(ctx, "57,470 CASUALTIES", W / 2, 492, "oldstd_b", 70, (1, 0.96, 0.9), "cb", 1, 0.03)
    img = fx.finish(WFX.silent(surface_to_rgb(surf), 11, "sepia", 0.6))
    Image.fromarray(img).resize((1280, 720), Image.LANCZOS).save(os.path.join(HERE, "build", "thumbnail.jpg"),
                                                                 quality=92)
    print("build/thumbnail.jpg")


if __name__ == "__main__":
    main()
