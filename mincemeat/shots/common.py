"""Shared helpers: camera moves and 1940s newsreel-style captions and cards."""
from engine.core import H, W, draw_text, ease_in_out, hash01, lerp, ramp, set_rgba, text_width, vgrad

INK = (0.95, 0.94, 0.9)


def camera(ctx, S, z0=1.0, z1=1.08, p0=(0, 0), p1=(0, 0)):
    k = ease_in_out(S.u)
    z = lerp(z0, z1, k)
    ctx.translate(W / 2 + lerp(p0[0], p1[0], k), H / 2 + lerp(p0[1], p1[1], k))
    ctx.scale(z, z)
    ctx.translate(-W / 2, -H / 2)


def plate(ctx, S, title, sub=None, t_in=0.5, t_out=None, x=100, y=880):
    """Newsreel-style superimposed caption: white capitals over a dark band."""
    t_out = S.dur - 0.4 if t_out is None else t_out
    a = min(ramp(S.t, t_in, t_in + 0.4), 1 - ramp(S.t, t_out - 0.4, t_out))
    if a <= 0:
        return
    ctx.save()
    ctx.identity_matrix()
    w = max(text_width(title, "oldstd_b", 48, 0.12), text_width(sub or "", "courier_r", 32)) + 80
    h = 90 if not sub else 140
    ctx.rectangle(x, y, w, h)
    ctx.set_source(vgrad(ctx, 0, y, 0, y + h, [(0, (0, 0, 0), 0.72 * a), (1, (0, 0, 0), 0.55 * a)]))
    ctx.fill()
    ctx.rectangle(x, y, 6, h)
    set_rgba(ctx, INK, a)
    ctx.fill()
    draw_text(ctx, title, x + 36, y + 64, "oldstd_b", 48, INK, "lb", a, 0.12)
    if sub:
        draw_text(ctx, sub, x + 36, y + 112, "courier_r", 32, (0.85, 0.84, 0.8), "lb", a)
    ctx.restore()


def card(ctx, S, lines, sizes, fonts, t_in=0.2, spacing=1.4, fade_out=True):
    ctx.rectangle(0, 0, W, H)
    ctx.set_source(vgrad(ctx, 0, 0, 0, H, [(0, (0.06, 0.06, 0.065)), (1, (0.02, 0.02, 0.025))]))
    ctx.fill()
    a = ramp(S.t, t_in, t_in + 0.5)
    if fade_out:
        a = min(a, 1 - ramp(S.t, S.dur - 0.4, S.dur))
    total = sum(s * spacing for s in sizes)
    y = H / 2 - total / 2
    for l, s, f in zip(lines, sizes, fonts):
        y += s * spacing
        if l:
            draw_text(ctx, l, W / 2, y - s * 0.3, f, s, INK, "cb", a, 0.06 if f == "oldstd_b" else 0.0)


def quote(ctx, S, lines, who, t_in=0.2):
    card(ctx, S, [], [], [], t_in)
    a = ramp(S.t, t_in, t_in + 0.6)
    y = H / 2 - len(lines) * 45
    draw_text(ctx, "“", 280, y + 30, "oldstd", 170, INK, "lb", a * 0.5)
    for i, l in enumerate(lines):
        draw_text(ctx, l, W / 2, y + i * 90, "oldstd", 64, INK, "cb", a)
    draw_text(ctx, who, W / 2, y + len(lines) * 90 + 50, "courier_r", 36, (0.8, 0.8, 0.76), "cb",
              ramp(S.t, t_in + 0.8, t_in + 1.4))
