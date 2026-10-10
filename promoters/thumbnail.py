"""1280x720 thumbnail: the two promoters, split screen, one line of text."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.append(os.path.join(os.path.dirname(HERE), "falklands"))

from PIL import Image  # noqa: E402

from engine.core import W, H, draw_text, new_canvas, set_rgba, surface_to_rgb  # noqa: E402
import film  # noqa: E402
import toons as T  # noqa: E402

surf, ctx = new_canvas()
ctx.set_source_surface(film.blurred_bg(0), 0, 0)
ctx.paint()
ctx.rectangle(W / 2, 0, W / 2, H)
ctx.save()
ctx.clip()
ctx.set_source_surface(film.blurred_bg(1), 0, 0)
ctx.paint()
ctx.restore()
T.character(ctx, "DANA", 500, 600, 360, mouth=0.7, look=0.5, pose="gesture", t=0.3, talk=1)
T.character(ctx, "EDDIE", 1420, 600, 360, mouth=0.2, look=-0.5, pose="binder", t=0.3, talk=1)
ctx.save()
ctx.translate(1420, 960)
ctx.rotate(-0.05)
ctx.rectangle(-270, -170, 540, 300)
set_rgba(ctx, (0.95, 0.95, 0.93))
ctx.fill()
draw_text(ctx, "CONTRACT", 0, -80, "oswald", 70, (0.15, 0.15, 0.2), "cb", 1, 0.12)
ctx.restore()
ctx.rectangle(W / 2 - 6, 0, 12, H)
set_rgba(ctx, (1, 1, 1))
ctx.fill()
draw_text(ctx, "\"I'M PROMOTING IT\"", 480, 190, "oswald", 96, (1, 1, 1), "cb", 1, 0.02, stroke=10)
draw_text(ctx, "\"HE CAN'T.\"", 1440, 190, "oswald", 110, (1, 0.9, 0.2), "cb", 1, 0.02, stroke=10)
img = Image.fromarray((surface_to_rgb(surf) * 255).astype("uint8")).resize((1280, 720), Image.LANCZOS)
img.save(os.path.join(HERE, "output", "thumbnail.jpg"), quality=92)
