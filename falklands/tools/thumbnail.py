"""Render the YouTube thumbnail (1280x720 JPEG) from the film's own artwork.

  python3 tools/thumbnail.py  ->  build/thumbnail.jpg
"""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from PIL import Image  # noqa: E402

from engine import fx  # noqa: E402
from engine import maps as M  # noqa: E402
from engine.core import H, W, draw_text, new_canvas, set_rgba, surface_to_rgb, vgrad  # noqa: E402
from scenes import part2  # noqa: E402


class FakeS:
    def __init__(self, t, dur):
        self.t, self.dur, self.u, self.frame = t, dur, t / dur, 7

    def at(self, *a):
        return 99.0

    def word(self, *a):
        return 99.0


def main():
    surf, ctx = new_canvas()
    S = FakeS(9.5, 10.0)
    part2.lower_third = lambda *a, **k: None   # no captions on the thumbnail
    part2.sheffield(ctx, S)          # burning destroyer after the Exocet strike
    # darken the left for the title
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(vgrad(ctx, 0, 0, W, 0, [(0, (0, 0, 0), 0.85), (0.55, (0, 0, 0), 0.35), (1, (0, 0, 0), 0.0)]))
    ctx.fill()
    draw_text(ctx, "THE", 90, 250, "stencil", 110, (0.95, 0.93, 0.88), "lb", 1, 0.08, shadow=(5, 6, 0.8))
    draw_text(ctx, "FALKLANDS", 90, 420, "stencil", 190, (0.98, 0.96, 0.9), "lb", 1, 0.04, shadow=(6, 8, 0.8))
    draw_text(ctx, "WAR", 90, 590, "stencil", 190, (0.98, 0.96, 0.9), "lb", 1, 0.06, shadow=(6, 8, 0.8))
    ctx.rectangle(90, 640, 560, 110)
    set_rgba(ctx, M.BRIT)
    ctx.fill()
    draw_text(ctx, "74 DAYS · 1982", 120, 725, "oswald", 76, (1, 1, 1), "lb", 1, 0.04)
    draw_text(ctx, "INVASION • TASK FORCE • SURRENDER", 92, 830, "cond", 44, (0.95, 0.85, 0.35), "lb", 1,
              0.08, shadow=(3, 3, 0.8))
    img = fx.finish(fx.film(surface_to_rgb(surf), 7, 0.7, warm=False, dust=False))
    Image.fromarray(img).resize((1280, 720), Image.LANCZOS).save(os.path.join(HERE, "build", "thumbnail.jpg"),
                                                                 quality=92)
    print("build/thumbnail.jpg")


if __name__ == "__main__":
    main()
