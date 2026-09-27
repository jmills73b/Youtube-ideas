"""Side-profile silhouettes of the ships, aircraft and vehicles of 1982.

Ship parts are given in units of hull length L: u runs stern (0) -> bow (1),
h is height above the waterline (positive up). Shapes are simplified but
follow the real profiles (gun/missile layout, masts, funnels, radomes).
"""
import math

import cairo

from .core import hexc, mix, poly, set_rgba

# ------------------------------------------------------------------ ships
R = "rect"   # (R, u0, u1, h0, h1)
P = "poly"   # (P, [(u, h), ...])
C = "circ"   # (C, u, h, r)
L_ = "line"  # (L_, [(u, h), ...], width)

SHIPS = {
    # Type 42 destroyer -- HMS Sheffield / Coventry
    "type42": [
        (P, [(0.0, 0.038), (0.01, 0.0), (0.95, 0.0), (1.0, 0.064), (0.8, 0.054), (0.6, 0.048), (0.35, 0.042)]),
        (P, [(0.825, 0.052), (0.83, 0.068), (0.85, 0.074), (0.868, 0.068), (0.872, 0.054)]),
        (L_, [(0.86, 0.066), (0.935, 0.071)], 0.0045),
        (R, 0.735, 0.775, 0.048, 0.062),
        (L_, [(0.755, 0.061), (0.8, 0.071)], 0.004),
        (P, [(0.56, 0.046), (0.56, 0.098), (0.6, 0.104), (0.67, 0.1), (0.705, 0.05)]),
        (R, 0.615, 0.635, 0.1, 0.116), (C, 0.625, 0.128, 0.018),
        (P, [(0.528, 0.085), (0.562, 0.085), (0.55, 0.2), (0.542, 0.2)]),
        (L_, [(0.525, 0.172), (0.568, 0.172)], 0.003),
        (R, 0.36, 0.56, 0.042, 0.084),
        (P, [(0.42, 0.08), (0.428, 0.132), (0.497, 0.136), (0.51, 0.08)]),
        (L_, [(0.39, 0.084), (0.39, 0.176)], 0.006),
        (R, 0.362, 0.418, 0.168, 0.2),
        (R, 0.2, 0.36, 0.04, 0.09),
        (R, 0.27, 0.29, 0.09, 0.1), (C, 0.28, 0.112, 0.018),
    ],
    # Type 21 frigate -- HMS Ardent / Antelope
    "type21": [
        (P, [(0.0, 0.036), (0.01, 0.0), (0.95, 0.0), (1.0, 0.07), (0.86, 0.058), (0.6, 0.048), (0.35, 0.044)]),
        (P, [(0.8, 0.055), (0.806, 0.07), (0.826, 0.078), (0.846, 0.072), (0.85, 0.056)]),
        (L_, [(0.835, 0.07), (0.91, 0.076)], 0.0045),
        (P, [(0.57, 0.046), (0.57, 0.1), (0.62, 0.108), (0.66, 0.1), (0.7, 0.052)]),
        (P, [(0.555, 0.09), (0.585, 0.09), (0.574, 0.205), (0.566, 0.205)]),
        (L_, [(0.548, 0.18), (0.592, 0.18)], 0.003),
        (R, 0.36, 0.57, 0.044, 0.086),
        (P, [(0.4, 0.082), (0.415, 0.145), (0.5, 0.135), (0.515, 0.082)]),
        (R, 0.22, 0.36, 0.042, 0.09),
        (R, 0.19, 0.215, 0.042, 0.065),
    ],
    # HMS Hermes -- Centaur-class carrier with 1980 ski-jump
    "hermes": [
        (P, [(0.02, 0.058), (0.035, 0.0), (0.93, 0.0), (0.985, 0.06), (0.9, 0.062), (0.1, 0.06)]),
        (P, [(-0.01, 0.062), (0.0, 0.074), (0.86, 0.074), (0.93, 0.078), (0.975, 0.09), (0.98, 0.083),
             (0.95, 0.064), (0.0, 0.062)]),
        (P, [(0.5, 0.074), (0.505, 0.122), (0.64, 0.122), (0.645, 0.074)]),
        (P, [(0.52, 0.121), (0.525, 0.14), (0.6, 0.14), (0.61, 0.121)]),
        (P, [(0.535, 0.139), (0.54, 0.165), (0.575, 0.165), (0.58, 0.139)]),
        (P, [(0.605, 0.121), (0.612, 0.2), (0.618, 0.2), (0.628, 0.121)]),
        (R, 0.596, 0.634, 0.182, 0.188),
        (C, 0.615, 0.212, 0.012),
    ],
    # HMS Invincible -- light carrier, twin funnels, Sea Dart on the bow
    "invincible": [
        (P, [(0.02, 0.058), (0.035, 0.0), (0.93, 0.0), (0.99, 0.06), (0.9, 0.062), (0.1, 0.06)]),
        (P, [(0.0, 0.062), (0.0, 0.072), (0.84, 0.072), (0.93, 0.08), (0.96, 0.072), (0.95, 0.064),
             (0.0, 0.062)]),
        (R, 0.44, 0.7, 0.072, 0.11),
        (P, [(0.47, 0.11), (0.48, 0.15), (0.53, 0.15), (0.54, 0.11)]),
        (P, [(0.6, 0.11), (0.61, 0.148), (0.655, 0.148), (0.665, 0.11)]),
        (L_, [(0.565, 0.11), (0.565, 0.19)], 0.004),
        (L_, [(0.685, 0.11), (0.685, 0.175)], 0.004),
        (R, 0.66, 0.705, 0.16, 0.168),
        (R, 0.955, 0.975, 0.072, 0.082),
    ],
    # ARA General Belgrano -- ex-USS Phoenix, Brooklyn-class cruiser
    "belgrano": [
        (P, [(0.0, 0.034), (0.01, 0.0), (0.965, 0.0), (1.0, 0.06), (0.82, 0.05), (0.55, 0.043), (0.2, 0.038)]),
        (R, 0.755, 0.8, 0.048, 0.064), (L_, [(0.8, 0.057), (0.87, 0.06)], 0.005),
        (R, 0.69, 0.738, 0.058, 0.076), (L_, [(0.738, 0.067), (0.81, 0.07)], 0.005),
        (R, 0.625, 0.672, 0.07, 0.09), (L_, [(0.672, 0.08), (0.745, 0.083)], 0.005),
        (R, 0.49, 0.61, 0.043, 0.075),
        (P, [(0.53, 0.075), (0.53, 0.125), (0.555, 0.14), (0.595, 0.14), (0.6, 0.075)]),
        (P, [(0.548, 0.14), (0.566, 0.24), (0.572, 0.24), (0.585, 0.14)]),
        (L_, [(0.55, 0.205), (0.59, 0.205)], 0.003),
        (R, 0.34, 0.49, 0.043, 0.08),
        (P, [(0.44, 0.078), (0.445, 0.155), (0.48, 0.155), (0.485, 0.078)]),
        (P, [(0.365, 0.078), (0.37, 0.15), (0.405, 0.15), (0.41, 0.078)]),
        (L_, [(0.325, 0.08), (0.33, 0.2)], 0.005),
        (R, 0.222, 0.27, 0.056, 0.074), (L_, [(0.222, 0.065), (0.155, 0.068)], 0.005),
        (R, 0.15, 0.195, 0.044, 0.06), (L_, [(0.15, 0.052), (0.085, 0.055)], 0.005),
        (L_, [(0.04, 0.036), (0.07, 0.1), (0.1, 0.1)], 0.003),
    ],
    # SS Canberra -- P&O liner requisitioned as a troopship
    "canberra": [
        (P, [(0.0, 0.05), (0.02, 0.0), (0.93, 0.0), (1.0, 0.072), (0.7, 0.058), (0.3, 0.054)]),
        (P, [(0.1, 0.054), (0.12, 0.084), (0.8, 0.084), (0.86, 0.06)]),
        (P, [(0.17, 0.083), (0.19, 0.104), (0.72, 0.104), (0.77, 0.083)]),
        (P, [(0.3, 0.103), (0.31, 0.12), (0.66, 0.12), (0.69, 0.103)]),
        (P, [(0.6, 0.119), (0.61, 0.138), (0.68, 0.138), (0.7, 0.119)]),
        (P, [(0.19, 0.103), (0.205, 0.172), (0.255, 0.172), (0.27, 0.103)]),
        (L_, [(0.655, 0.138), (0.66, 0.2)], 0.004),
    ],
    # RFA Sir Galahad -- Round Table-class landing ship logistic
    "galahad": [
        (P, [(0.0, 0.05), (0.01, 0.0), (0.96, 0.0), (1.0, 0.085), (0.8, 0.072), (0.5, 0.066)]),
        (R, 0.12, 0.43, 0.064, 0.13),
        (P, [(0.14, 0.13), (0.16, 0.155), (0.42, 0.155), (0.44, 0.13)]),
        (P, [(0.19, 0.155), (0.2, 0.2), (0.26, 0.2), (0.27, 0.155)]),
        (L_, [(0.37, 0.155), (0.37, 0.24)], 0.004),
        (L_, [(0.62, 0.07), (0.64, 0.15), (0.72, 0.11)], 0.004),
    ],
    # HMS Endurance -- ice patrol ship (red hull)
    "endurance": [
        (P, [(0.0, 0.055), (0.01, 0.0), (0.95, 0.0), (1.0, 0.09), (0.72, 0.072), (0.4, 0.066)]),
        (R, 0.14, 0.42, 0.066, 0.125),
        (R, 0.44, 0.76, 0.068, 0.13),
        (P, [(0.6, 0.13), (0.61, 0.16), (0.745, 0.16), (0.76, 0.13)]),
        (P, [(0.47, 0.13), (0.48, 0.19), (0.54, 0.19), (0.55, 0.13)]),
        (L_, [(0.71, 0.16), (0.715, 0.28)], 0.005),
        (L_, [(0.82, 0.075), (0.84, 0.17), (0.9, 0.12)], 0.004),
    ],
    # Argentine corvette / generic small warship
    "corvette": [
        (P, [(0.0, 0.05), (0.01, 0.0), (0.95, 0.0), (1.0, 0.08), (0.7, 0.066), (0.4, 0.06)]),
        (R, 0.35, 0.68, 0.06, 0.12), (P, [(0.44, 0.12), (0.46, 0.18), (0.52, 0.18), (0.54, 0.12)]),
        (L_, [(0.62, 0.12), (0.62, 0.24)], 0.006),
        (R, 0.76, 0.81, 0.066, 0.086), (L_, [(0.8, 0.08), (0.88, 0.085)], 0.006),
    ],
}


def _part_path(ctx, part):
    kind = part[0]
    if kind == R:
        _, u0, u1, h0, h1 = part
        ctx.rectangle(u0, -h1, u1 - u0, h1 - h0)
    elif kind == P:
        poly(ctx, [(u, -h) for u, h in part[1]])
    elif kind == C:
        _, u, h, r = part
        ctx.new_sub_path()
        ctx.arc(u, -h, r, 0, 2 * math.pi)


def ship(ctx, kind, x, y, length, facing=1, color=(0.1, 0.11, 0.13), light=None, alpha=1.0,
         hull_color=None, upper_color=None, roll=0.0, list_deg=0.0, sink=0.0, windows=None):
    """Draw a ship with its waterline centred at (x, y), `length` px long.

    light: optional rim/top highlight colour (painterly volume).
    hull_color/upper_color: for coloured ships (Endurance red, Canberra white).
    sink: 0..1 lowers the ship into the sea (clip at waterline).
    """
    parts = SHIPS[kind]
    ctx.save()
    ctx.rectangle(-10, -10, 4000, y + 2 - (-10))  # clip at waterline
    ctx.clip()
    ctx.translate(x, y + sink * length * 0.12)
    ctx.rotate(math.radians(roll + list_deg))
    ctx.scale(facing * length, length)
    ctx.translate(-0.5, 0)
    top = min(-p for part in parts for p in _heights(part))
    for i, part in enumerate(parts):
        ctx.new_path()
        if part[0] == L_:
            ctx.set_line_width(part[2])
            poly(ctx, [(u, -h) for u, h in part[1]], close=False)
            c = upper_color or color
            set_rgba(ctx, c, alpha)
            ctx.stroke()
            continue
        _part_path(ctx, part)
        c = hull_color if (i == 0 and hull_color) else (upper_color or color)
        if light is not None:
            g = cairo.LinearGradient(0, top, 0, 0)
            g.add_color_stop_rgba(0, *mix(c, light, 0.35), alpha)
            g.add_color_stop_rgba(0.55, *c[:3], alpha)
            g.add_color_stop_rgba(1, *mix(c, (0, 0, 0), 0.25), alpha)
            ctx.set_source(g)
        else:
            set_rgba(ctx, c, alpha)
        ctx.fill()
    if windows:
        wc, rows = windows
        for (u0, u1, h, step) in rows:
            u = u0
            while u < u1:
                ctx.rectangle(u, -h, 0.004, 0.005)
                u += step
        set_rgba(ctx, wc, alpha)
        ctx.fill()
    ctx.restore()


def _heights(part):
    if part[0] == R:
        return [part[3], part[4]]
    if part[0] == P or part[0] == L_:
        return [h for _, h in part[1]]
    if part[0] == C:
        return [part[2] + part[3]]
    return [0]


def wake(ctx, x, y, length, facing, t, alpha=0.5, spread=0.35):
    """V-shaped wake and bow wave behind a ship moving in `facing` direction."""
    bow = x + facing * length * 0.5
    stern = x - facing * length * 0.5
    ctx.set_line_width(3)
    for k in range(6):
        d = k / 6
        yy = y + 2 + k * 3
        ctx.move_to(bow, y + 1)
        ctx.curve_to(bow - facing * length * 0.3, yy, stern - facing * length * (0.3 + d),
                     yy + length * spread * d * 0.1, stern - facing * length * (0.8 + d * 1.2),
                     yy + length * spread * d * 0.12)
        ctx.set_source_rgba(1, 1, 1, alpha * (1 - d) * (0.8 + 0.2 * math.sin(t * 4 + k)))
        ctx.stroke()
    ctx.rectangle(min(stern, stern - facing * length * 0.6), y, length * 0.6, 4)
    ctx.set_source_rgba(1, 1, 1, alpha * 0.6)
    ctx.fill()


# ------------------------------------------------------------------ aircraft (side views)
JETS = {
    # McDonnell Douglas A-4 Skyhawk (A-4B/C/P/Q of the Argentine Air Force/Navy)
    "skyhawk": {
        "body": [(1.0, 0.0), (0.93, -0.028), (0.8, -0.05), (0.72, -0.07), (0.64, -0.1), (0.56, -0.1),
                 (0.5, -0.088), (0.32, -0.078), (0.14, -0.062), (0.02, -0.05), (0.0, -0.02), (0.02, 0.02),
                 (0.3, 0.045), (0.7, 0.04), (0.9, 0.02)],
        "fin": [(0.2, -0.07), (0.075, -0.3), (0.0, -0.3), (0.035, -0.05)],
        "wing": [(0.66, 0.02), (0.4, 0.075), (0.3, 0.078), (0.44, 0.02)],
        "tail": [(0.14, -0.035), (0.0, -0.005), (0.03, 0.005), (0.2, -0.02)],
        "canopy": [(0.72, -0.07), (0.66, -0.105), (0.58, -0.106), (0.56, -0.09), (0.7, -0.068)],
        "probe": [(0.8, -0.005), (1.08, -0.02)],
        "tank": (0.5, 0.075, 0.14, 0.02),
    },
    # Dassault Super Etendard (Argentine Navy, Exocet carrier)
    "etendard": {
        "body": [(1.0, 0.0), (0.9, -0.03), (0.78, -0.05), (0.7, -0.075), (0.6, -0.082), (0.5, -0.07),
                 (0.25, -0.06), (0.05, -0.05), (0.0, -0.035), (0.0, 0.02), (0.3, 0.04), (0.8, 0.03)],
        "fin": [(0.24, -0.06), (0.1, -0.27), (0.02, -0.27), (0.05, -0.05)],
        "wing": [(0.6, 0.0), (0.36, 0.06), (0.28, 0.062), (0.42, 0.0)],
        "tail": [(0.12, -0.04), (-0.02, -0.02), (0.02, -0.01), (0.2, -0.03)],
        "canopy": [(0.74, -0.068), (0.66, -0.098), (0.58, -0.096), (0.57, -0.078), (0.72, -0.065)],
        "probe": [(0.78, -0.07), (1.02, -0.09)],
        "tank": (0.42, 0.06, 0.12, 0.018),
    },
    # BAe Sea Harrier FRS.1
    "harrier": {
        "body": [(1.0, 0.0), (0.9, -0.03), (0.78, -0.07), (0.72, -0.1), (0.62, -0.1), (0.5, -0.07),
                 (0.2, -0.05), (0.05, -0.04), (0.0, -0.02), (0.02, 0.02), (0.3, 0.05), (0.7, 0.05),
                 (0.9, 0.02)],
        "fin": [(0.22, -0.05), (0.1, -0.22), (0.03, -0.22), (0.06, -0.04)],
        "wing": [(0.6, -0.06), (0.36, -0.02), (0.3, -0.02), (0.42, -0.06)],
        "tail": [(0.13, -0.03), (-0.02, 0.01), (0.02, 0.015), (0.2, -0.015)],
        "canopy": [(0.78, -0.07), (0.72, -0.12), (0.64, -0.12), (0.62, -0.1), (0.76, -0.068)],
        "probe": None,
        "tank": None,
    },
}


def jet(ctx, kind, x, y, length, facing=1, color=(0.12, 0.12, 0.13), light=(0.6, 0.6, 0.6), bank=0.0,
        pitch=0.0, alpha=1.0, burner=0.0):
    spec = JETS[kind]
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.radians(pitch * -facing))
    ctx.scale(facing * length, length * (1 - 0.35 * abs(bank)))
    ctx.translate(-0.5, 0)
    if burner > 0:
        g = cairo.RadialGradient(-0.02, -0.01, 0, -0.02, -0.01, 0.25)
        g.add_color_stop_rgba(0, 1, 0.8, 0.5, 0.5 * burner)
        g.add_color_stop_rgba(1, 1, 0.5, 0.2, 0)
        ctx.set_source(g)
        ctx.arc(-0.02, -0.01, 0.25, 0, 6.283)
        ctx.fill()
    for key in ("tail", "wing", "fin", "body"):
        poly(ctx, spec[key])
        g = cairo.LinearGradient(0, -0.12, 0, 0.06)
        g.add_color_stop_rgba(0, *mix(color, light, 0.45), alpha)
        g.add_color_stop_rgba(0.6, *color[:3], alpha)
        g.add_color_stop_rgba(1, *mix(color, (0, 0, 0), 0.4), alpha)
        ctx.set_source(g)
        ctx.fill()
    if spec.get("tank"):
        u, h, l, r = spec["tank"]
        ctx.save()
        ctx.translate(u, h)
        ctx.scale(l, r)
        ctx.arc(0, 0, 1, 0, 6.283)
        ctx.restore()
        set_rgba(ctx, mix(color, (0, 0, 0), 0.2), alpha)
        ctx.fill()
    poly(ctx, spec["canopy"])
    set_rgba(ctx, mix(light, (0.3, 0.4, 0.5), 0.5), alpha * 0.9)
    ctx.fill()
    if spec.get("probe"):
        ctx.set_line_width(0.012)
        poly(ctx, spec["probe"], close=False)
        set_rgba(ctx, color, alpha)
        ctx.stroke()
    ctx.restore()


def vulcan_plan(ctx, x, y, size, angle=0.0, color=(0.1, 0.1, 0.12), light=(0.5, 0.5, 0.55), alpha=1.0):
    """Avro Vulcan B.2 seen from below: the classic delta."""
    half = [(1.0, 0.0), (0.95, 0.035), (0.84, 0.06), (0.72, 0.085), (0.6, 0.2), (0.46, 0.34), (0.3, 0.5),
            (0.2, 0.56), (0.13, 0.555), (0.12, 0.42), (0.1, 0.2), (0.06, 0.08), (0.0, 0.035)]
    pts = half + [(u, -v) for u, v in reversed(half)]
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.scale(size, size)
    ctx.translate(-0.5, 0)
    poly(ctx, pts)
    g = cairo.LinearGradient(0, -0.5, 0, 0.5)
    g.add_color_stop_rgba(0, *mix(color, light, 0.3), alpha)
    g.add_color_stop_rgba(0.5, *mix(color, light, 0.12), alpha)
    g.add_color_stop_rgba(1, *color[:3], alpha)
    ctx.set_source(g)
    ctx.fill()
    for s in (1, -1):  # engine intakes
        ctx.move_to(0.66, 0.06 * s)
        ctx.line_to(0.6, 0.15 * s)
        ctx.set_line_width(0.012)
        set_rgba(ctx, mix(color, (0, 0, 0), 0.5), alpha)
        ctx.stroke()
    # refuelling probe
    ctx.move_to(1.0, 0)
    ctx.line_to(1.08, 0)
    ctx.set_line_width(0.012)
    set_rgba(ctx, color, alpha)
    ctx.stroke()
    ctx.restore()


def victor_plan(ctx, x, y, size, angle=0.0, color=(0.13, 0.13, 0.15), light=(0.5, 0.5, 0.55), alpha=1.0,
                hose=0.0):
    """Handley Page Victor K.2 tanker from below: crescent wing, T-tail."""
    half_wing = [(0.64, 0.05), (0.52, 0.18), (0.4, 0.3), (0.3, 0.42), (0.26, 0.47), (0.22, 0.47),
                 (0.3, 0.3), (0.4, 0.16), (0.44, 0.05)]
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(angle)
    ctx.scale(size, size)
    ctx.translate(-0.5, 0)
    g = cairo.LinearGradient(0, -0.5, 0, 0.5)
    g.add_color_stop_rgba(0, *mix(color, light, 0.3), alpha)
    g.add_color_stop_rgba(1, *color[:3], alpha)
    for s in (1, -1):
        poly(ctx, [(u, v * s) for u, v in half_wing])
        ctx.set_source(g)
        ctx.fill()
        poly(ctx, [(0.1, 0.03 * s), (0.02, 0.19 * s), (-0.02, 0.19 * s), (0.02, 0.03 * s)])
        ctx.set_source(g)
        ctx.fill()
    ctx.save()
    ctx.translate(0.5, 0)
    ctx.scale(0.52, 0.045)
    ctx.arc(0, 0, 1, 0, 6.283)
    ctx.restore()
    ctx.set_source(g)
    ctx.fill()
    if hose > 0:  # centre-line hose and drogue
        ctx.set_line_width(0.006)
        ctx.move_to(0.1, 0)
        ctx.curve_to(-0.2 * hose, 0.01, -0.4 * hose, 0.03, -0.6 * hose, 0.04)
        set_rgba(ctx, (0.2, 0.2, 0.2), alpha)
        ctx.stroke()
        ctx.arc(-0.6 * hose, 0.04, 0.025, 0, 6.283)
        set_rgba(ctx, (0.3, 0.3, 0.3), alpha)
        ctx.fill()
    ctx.restore()


def exocet(ctx, x, y, length, facing=1, t=0.0, alpha=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(facing, 1)
    # exhaust plume
    for k in range(10):
        d = k / 10
        ctx.arc(-length * (0.55 + d * 2.2), (math.sin(t * 30 + k) * 2), length * (0.05 + d * 0.12), 0, 6.283)
        ctx.set_source_rgba(0.85, 0.85, 0.85, alpha * 0.35 * (1 - d))
        ctx.fill()
    radial_glow(ctx, -length * 0.55, 0, length * 0.35, (1, 0.8, 0.4), alpha)
    ctx.move_to(length * 0.5, 0)
    ctx.line_to(length * 0.35, -length * 0.04)
    ctx.line_to(-length * 0.5, -length * 0.04)
    ctx.line_to(-length * 0.5, length * 0.04)
    ctx.line_to(length * 0.35, length * 0.04)
    ctx.close_path()
    ctx.move_to(0.05 * length, 0)
    ctx.line_to(-0.2 * length, -length * 0.14)
    ctx.line_to(-0.28 * length, -length * 0.14)
    ctx.line_to(-0.18 * length, 0)
    ctx.close_path()
    ctx.set_source_rgba(0.75, 0.75, 0.72, alpha)
    ctx.fill()
    ctx.restore()


def radial_glow(ctx, x, y, r, color, alpha):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *color[:3], alpha)
    g.add_color_stop_rgba(1, *color[:3], 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 6.283)
    ctx.fill()


# ------------------------------------------------------------------ helicopters
def helicopter(ctx, kind, x, y, length, facing=1, t=0.0, color=(0.12, 0.13, 0.12), alpha=1.0):
    """Sea King / Wessex (single rotor) or Chinook (tandem)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(facing * length, length)
    ctx.translate(-0.5, 0)
    if kind == "chinook":
        body = [(0.05, -0.02), (0.08, -0.14), (0.9, -0.14), (0.98, -0.1), (1.0, -0.04), (0.95, 0.03),
                (0.1, 0.03)]
        poly(ctx, body)
        poly(ctx, [(0.02, -0.1), (0.05, -0.24), (0.2, -0.24), (0.22, -0.13)])
        poly(ctx, [(0.8, -0.13), (0.82, -0.2), (0.9, -0.2), (0.9, -0.13)])
        set_rgba(ctx, color, alpha)
        ctx.fill()
        for cx, cy in ((0.12, -0.25), (0.86, -0.21)):
            ctx.save()
            ctx.translate(cx, cy)
            ctx.scale(0.5, 0.025)
            ctx.arc(0, 0, 1, 0, 6.283)
            ctx.restore()
            ctx.set_source_rgba(*color[:3], alpha * 0.35)
            ctx.fill()
    else:
        # Westland Sea King: boat hull, engines on top, tapering tail boom and pylon
        ctx.move_to(1.0, -0.07)
        ctx.curve_to(1.0, -0.13, 0.95, -0.17, 0.86, -0.18)
        ctx.line_to(0.4, -0.19)
        ctx.line_to(0.3, -0.16)
        ctx.line_to(0.06, -0.13)
        ctx.line_to(0.02, -0.3)
        ctx.line_to(-0.02, -0.3)
        ctx.line_to(-0.01, -0.1)
        ctx.line_to(0.1, -0.07)
        ctx.line_to(0.34, -0.03)
        ctx.curve_to(0.4, 0.0, 0.8, 0.01, 0.92, 0.0)
        ctx.curve_to(0.97, -0.01, 1.0, -0.03, 1.0, -0.07)
        ctx.close_path()
        poly(ctx, [(0.45, -0.19), (0.5, -0.24), (0.78, -0.24), (0.82, -0.19)])
        set_rgba(ctx, color, alpha)
        ctx.fill()
        # sponson and wheel
        ctx.rectangle(0.55, -0.04, 0.12, 0.05)
        ctx.fill()
        ctx.arc(0.6, 0.03, 0.022, 0, 6.283)
        ctx.fill()
        # cockpit glazing
        poly(ctx, [(0.9, -0.17), (0.98, -0.12), (0.99, -0.08), (0.9, -0.1)])
        ctx.set_source_rgba(0.55, 0.6, 0.65, alpha * 0.6)
        ctx.fill()
        # rotor mast and blurred disc
        ctx.rectangle(0.62, -0.28, 0.025, 0.05)
        set_rgba(ctx, color, alpha)
        ctx.fill()
        ctx.save()
        ctx.translate(0.63, -0.285)
        ctx.scale(0.62, 0.028)
        ctx.arc(0, 0, 1, 0, 6.283)
        ctx.restore()
        ctx.set_source_rgba(*color[:3], alpha * 0.28)
        ctx.fill()
        ang = t * 40
        ctx.set_line_width(0.014)
        ctx.move_to(0.63 + math.cos(ang) * 0.62, -0.285)
        ctx.line_to(0.63 - math.cos(ang) * 0.62, -0.285)
        ctx.set_source_rgba(*color[:3], alpha * 0.7)
        ctx.stroke()
        # tail rotor blur
        ctx.arc(0.0, -0.27, 0.08, 0, 6.283)
        ctx.set_source_rgba(*color[:3], alpha * 0.22)
        ctx.fill()
    ctx.restore()


# ------------------------------------------------------------------ vehicles
def amtrac(ctx, x, y, length, facing=1, color=(0.1, 0.11, 0.1), alpha=1.0, t=0.0):
    """LVTP-7 amphibious tractor, as used by the Argentine marines on 2 April."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(facing * length, length)
    ctx.translate(-0.5, 0)
    poly(ctx, [(0.0, -0.3), (0.06, -0.02), (0.84, -0.02), (1.0, -0.26), (0.96, -0.46), (0.02, -0.46)])
    poly(ctx, [(0.62, -0.46), (0.64, -0.56), (0.76, -0.56), (0.78, -0.46)])
    set_rgba(ctx, color, alpha)
    ctx.fill()
    ctx.set_line_width(0.012)
    ctx.move_to(0.72, -0.56)
    ctx.line_to(0.95, -0.58)
    ctx.stroke()
    for k in range(6):
        ctx.arc(0.12 + k * 0.13, -0.08, 0.05, 0, 6.283)
        ctx.set_source_rgba(0.05, 0.05, 0.05, alpha)
        ctx.fill()
    ctx.restore()
