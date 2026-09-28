"""Render the YouTube thumbnail (1280x720) from the film's own artwork.

  python3 tools/thumbnail.py  ->  build/thumbnail.jpg
"""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

import ww2  # noqa: E402,F401
from PIL import Image  # noqa: E402

from engine import fx  # noqa: E402
from engine.core import H, W, draw_text, new_canvas, set_rgba, surface_to_rgb, vgrad  # noqa: E402
from shots import part1  # noqa: E402
from ww2 import docs as D  # noqa: E402
from ww2 import fx as WFX  # noqa: E402


class FakeS:
    def __init__(self, t, dur):
        self.t, self.dur, self.u, self.frame = t, dur, t / dur, 11

    def at(self, *a):
        return 99.0

    def word(self, *a):
        return 99.0


def main():
    surf, ctx = new_canvas()
    part1.plate = lambda *a, **k: None          # no captions on the thumbnail
    part1.briefcase(ctx, FakeS(2.0, 9.0))
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(vgrad(ctx, 0, 0, 0, H, [(0, (0, 0, 0), 0.8), (0.4, (0, 0, 0), 0.2), (1, (0, 0, 0), 0.1)]))
    ctx.fill()
    draw_text(ctx, "OPERATION", W / 2, 190, "oldstd_b", 120, (0.97, 0.96, 0.92), "cb", 1, 0.2, shadow=(5, 6, 0.9))
    draw_text(ctx, "MINCEMEAT", W / 2, 350, "oldstd_b", 180, (0.97, 0.96, 0.92), "cb", 1, 0.08, shadow=(6, 8, 0.9))
    ctx.rectangle(W / 2 - 760, 880, 1520, 130)
    set_rgba(ctx, (0.02, 0.02, 0.02), 0.85)
    ctx.fill()
    ctx.rectangle(W / 2 - 740, 896, 1480, 98)
    ctx.set_line_width(4)
    set_rgba(ctx, (0.95, 0.95, 0.92))
    ctx.stroke()
    draw_text(ctx, "THE DEAD MAN WHO FOOLED HITLER", W / 2, 972, "stencil", 70, (0.97, 0.96, 0.92), "cb", 1, 0.08)
    img = fx.finish(WFX.noir(surface_to_rgb(surf), 11, 0.6))
    Image.fromarray(img).resize((1280, 720), Image.LANCZOS).save(os.path.join(HERE, "build", "thumbnail.jpg"),
                                                                 quality=92)
    print("build/thumbnail.jpg")


if __name__ == "__main__":
    main()
