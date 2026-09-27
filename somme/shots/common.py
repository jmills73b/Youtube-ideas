"""Small helpers shared by the Somme shots."""
from engine.core import H, W, ease_in_out, hash01, lerp


def camera(ctx, S, z0=1.0, z1=1.08, p0=(0, 0), p1=(0, 0), ease=ease_in_out):
    k = ease(S.u)
    z = lerp(z0, z1, k)
    ctx.translate(W / 2 + lerp(p0[0], p1[0], k), H / 2 + lerp(p0[1], p1[1], k))
    ctx.scale(z, z)
    ctx.translate(-W / 2, -H / 2)


def shake(ctx, S, t0, amp=10, dur=0.8):
    a = S.t - t0
    if 0 <= a < dur:
        k = (1 - a / dur) ** 2 * amp
        ctx.translate((hash01(S.frame, 11) - 0.5) * 2 * k, (hash01(S.frame, 12) - 0.5) * 2 * k)
