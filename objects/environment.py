"""
Stadium environment: outer floor, walls, lighting, scoreboard.
All geometry built from polygons (no external assets).
"""

import numpy as np
from renderer import make_box, make_cylinder, make_sphere, combine_meshes, translate, rot_y, identity

# ── Colors ────────────────────────────────────────────────────────────────────
FLOOR_OUTER  = [0.12, 0.12, 0.14]
WALL_COLOR   = [0.18, 0.18, 0.22]
WALL_TRIM    = [0.28, 0.28, 0.35]
LIGHT_POLE   = [0.35, 0.35, 0.38]
LIGHT_BULB   = [1.00, 0.97, 0.80]
BOARD_BG     = [0.08, 0.08, 0.10]
BOARD_TRIM   = [0.85, 0.65, 0.10]
BOARD_TEXT   = [0.95, 0.95, 0.95]

FLOOR_W, FLOOR_L = 22.0, 28.0
WALL_H = 8.0


# ── FLOOR ─────────────────────────────────────────────────────────────────────
def _outer_floor():
    v, i = make_box(FLOOR_W, 0.04, FLOOR_L, FLOOR_OUTER)
    v = v.copy()
    v[:, 1] -= 0.02
    return v, i


# ── WALLS ─────────────────────────────────────────────────────────────────────
def _wall(x, y, z, w, h, d, color):
    v, i = make_box(w, h, d, color)
    v = v.copy()
    v[:, 0] += x
    v[:, 1] += y
    v[:, 2] += z
    return v, i


def _walls():
    hw = FLOOR_W / 2
    hl = FLOOR_L / 2
    hy = WALL_H / 2

    return [
        _wall(0, hy, -hl, FLOOR_W, WALL_H, 0.3, WALL_COLOR),
        _wall(0, hy, hl, FLOOR_W, WALL_H, 0.3, WALL_COLOR),
        _wall(-hw, hy, 0, 0.3, WALL_H, FLOOR_L, WALL_COLOR),
        _wall(hw, hy, 0, 0.3, WALL_H, FLOOR_L, WALL_COLOR),

        _wall(0, 0.15, -hl, FLOOR_W, 0.3, 0.32, WALL_TRIM),
        _wall(0, 0.15, hl, FLOOR_W, 0.3, 0.32, WALL_TRIM),
        _wall(-hw, 0.15, 0, 0.32, 0.3, FLOOR_L, WALL_TRIM),
        _wall(hw, 0.15, 0, 0.32, 0.3, FLOOR_L, WALL_TRIM),
    ]


# ── LIGHTING ──────────────────────────────────────────────────────────────────
def _light_rig(x, z):
    meshes = []
    pole_h = WALL_H - 0.5

    # pole
    v, i = make_cylinder(0.06, pole_h, 6, LIGHT_POLE)
    v = v.copy()
    v[:, 0] += x
    v[:, 1] += pole_h / 2
    v[:, 2] += z
    meshes.append((v, i))

    # bar
    v, i = make_box(1.6, 0.08, 0.08, LIGHT_POLE)
    v = v.copy()
    v[:, 0] += x
    v[:, 1] += pole_h
    v[:, 2] += z
    meshes.append((v, i))

    # bulbs
    for bx in [-0.65, 0.65]:
        v, i = make_sphere(0.14, 4, 6, LIGHT_BULB)
        v = v.copy()
        v[:, 0] += x + bx
        v[:, 1] += pole_h - 0.1
        v[:, 2] += z
        meshes.append((v, i))

    return meshes


# ── 7-SEGMENT DIGIT ───────────────────────────────────────────────────────────
def _draw_digit(digit, base_x, base_y, base_z, scale=1.0, color=None):
    if color is None:
        color = BOARD_TEXT

    segments = {
        0: [1,1,1,1,1,1,0],
        1: [0,1,1,0,0,0,0],
        2: [1,1,0,1,1,0,1],
        3: [1,1,1,1,0,0,1],
        4: [0,1,1,0,0,1,1],
        5: [1,0,1,1,0,1,1],
        6: [1,0,1,1,1,1,1],
        7: [1,1,1,0,0,0,0],
        8: [1,1,1,1,1,1,1],
        9: [1,1,1,1,0,1,1],
    }

    w = 0.25 * scale
    h = 0.05 * scale
    d = 0.14

    positions = [
        (0, 0.3),     # top
        (0.15, 0.15),
        (0.15, -0.15),
        (0, -0.3),    # bottom
        (-0.15, -0.15),
        (-0.15, 0.15),
        (0, 0),       # middle
    ]

    meshes = []

    for idx, on in enumerate(segments[digit]):
        if not on:
            continue

        px, py = positions[idx]

        if idx in [0, 3, 6]:
            v, i = make_box(w, h, d, color)
        else:
            v, i = make_box(h, w, d, color)

        v = v.copy()
        v[:, 0] += base_x + px
        v[:, 1] += base_y + py
        v[:, 2] += base_z

        meshes.append((v, i))

    return meshes


# ── SCOREBOARD ────────────────────────────────────────────────────────────────
def _scoreboard():
    meshes = []
    bx, by, bz = 0.0, 5.5, -(FLOOR_L / 2 - 0.2)

    # background
    v, i = make_box(4.2, 1.4, 0.12, BOARD_BG)
    v = v.copy()
    v[:, 0] += bx
    v[:, 1] += by
    v[:, 2] += bz
    meshes.append((v, i))

    # border
    for (ox, oy, w, h) in [
        (0, 0.65, 4.2, 0.08),
        (0, -0.65, 4.2, 0.08),
        (-2.05, 0, 0.08, 1.4),
        (2.05, 0, 0.08, 1.4),
    ]:
        v, i = make_box(w, h, 0.14, BOARD_TRIM)
        v = v.copy()
        v[:, 0] += bx + ox
        v[:, 1] += by + oy
        v[:, 2] += bz
        meshes.append((v, i))

    scale = 1.2

    # LEFT SCORE (21)
    meshes += _draw_digit(2, bx - 1.2, by, bz, scale, [1.0, 0.9, 0.2])
    meshes += _draw_digit(1, bx - 0.6, by, bz, scale, [1.0, 1.0, 1.0])

    # COLON
    for dy in [0.2, -0.2]:
        v, i = make_box(0.08, 0.12, 0.14, BOARD_TEXT)
        v = v.copy()
        v[:, 0] += bx
        v[:, 1] += by + dy
        v[:, 2] += bz
        meshes.append((v, i))

    # RIGHT SCORE (20)
    meshes += _draw_digit(2, bx + 0.6, by, bz, scale, [0.2, 1.0, 1.0])
    meshes += _draw_digit(0, bx + 1.2, by, bz, scale, [0.2, 1.0, 1.0])

    return meshes


# ── BUILD ALL ─────────────────────────────────────────────────────────────────
def build_environment_mesh():
    meshes = [_outer_floor()]
    meshes += _walls()

    for lx in [-4.5, 4.5]:
        for lz in [-5.5, 5.5]:
            meshes += _light_rig(lx, lz)

    meshes += _scoreboard()

    return combine_meshes(meshes)


# ── CLASS ─────────────────────────────────────────────────────────────────────
class Environment:
    def __init__(self, ctx, renderer):
        v, i = build_environment_mesh()
        self.vao, _ = renderer.make_vao(v, i)
        self.renderer = renderer
        self.model = identity()

    def draw(self, vp):
        self.renderer.draw_vao(self.vao, self.model, vp)