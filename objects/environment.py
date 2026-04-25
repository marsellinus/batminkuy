"""
Stadium environment: outer floor, back walls, ceiling light rigs, scoreboard.
All geometry built from polygons, no external assets.
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
BOARD_TEXT   = [0.95, 0.95, 0.95]   # score digits (simple blocks)

FLOOR_W, FLOOR_L = 22.0, 28.0   # outer floor size
WALL_H           = 8.0
CW, CL           = 6.1, 13.4    # court dims (must match court.py)


def _outer_floor():
    v, i = make_box(FLOOR_W, 0.04, FLOOR_L, FLOOR_OUTER)
    v = v.copy(); v[:, 1] -= 0.02   # sit just below court surface
    return v, i


def _wall(x, y, z, w, h, d, color):
    v, i = make_box(w, h, d, color)
    v = v.copy(); v[:, 0] += x; v[:, 1] += y; v[:, 2] += z
    return v, i


def _walls():
    hw = FLOOR_W / 2;  hl = FLOOR_L / 2;  hy = WALL_H / 2
    meshes = [
        _wall(0,    hy, -hl, FLOOR_W, WALL_H, 0.3, WALL_COLOR),   # back -z
        _wall(0,    hy,  hl, FLOOR_W, WALL_H, 0.3, WALL_COLOR),   # back +z
        _wall(-hw,  hy,  0,  0.3, WALL_H, FLOOR_L, WALL_COLOR),   # side -x
        _wall( hw,  hy,  0,  0.3, WALL_H, FLOOR_L, WALL_COLOR),   # side +x
        # trim strips at base
        _wall(0,    0.15, -hl, FLOOR_W, 0.30, 0.32, WALL_TRIM),
        _wall(0,    0.15,  hl, FLOOR_W, 0.30, 0.32, WALL_TRIM),
        _wall(-hw,  0.15,  0,  0.32, 0.30, FLOOR_L, WALL_TRIM),
        _wall( hw,  0.15,  0,  0.32, 0.30, FLOOR_L, WALL_TRIM),
    ]
    return meshes


def _light_rig(x, z):
    """Single ceiling light: vertical pole + horizontal bar + 2 bulbs."""
    meshes = []
    pole_h = WALL_H - 0.5
    # pole
    v, i = make_cylinder(0.06, pole_h, 6, LIGHT_POLE)
    v = v.copy(); v[:, 0] += x; v[:, 1] += pole_h / 2; v[:, 2] += z
    meshes.append((v, i))
    # horizontal bar
    v, i = make_box(1.6, 0.08, 0.08, LIGHT_POLE)
    v = v.copy(); v[:, 0] += x; v[:, 1] += pole_h; v[:, 2] += z
    meshes.append((v, i))
    # bulbs
    for bx in [-0.65, 0.65]:
        v, i = make_sphere(0.14, 4, 6, LIGHT_BULB)
        v = v.copy(); v[:, 0] += x + bx; v[:, 1] += pole_h - 0.1; v[:, 2] += z
        meshes.append((v, i))
    return meshes


def _scoreboard():
    """Simple scoreboard quad above one end wall."""
    meshes = []
    bx, by, bz = 0.0, 5.5, -(FLOOR_L / 2 - 0.2)
    # background panel
    v, i = make_box(3.2, 1.2, 0.12, BOARD_BG)
    v = v.copy(); v[:, 0] += bx; v[:, 1] += by; v[:, 2] += bz
    meshes.append((v, i))
    # gold trim border
    for (ox, oy, w, h) in [
        (0, 0.55, 3.2, 0.08), (0, -0.55, 3.2, 0.08),
        (-1.55, 0, 0.08, 1.2), (1.55, 0, 0.08, 1.2),
    ]:
        v, i = make_box(w, h, 0.14, BOARD_TRIM)
        v = v.copy(); v[:, 0] += bx+ox; v[:, 1] += by+oy; v[:, 2] += bz
        meshes.append((v, i))
    # score "digits" as white blocks (abstract representation)
    # left score block
    v, i = make_box(0.55, 0.55, 0.14, BOARD_TEXT)
    v = v.copy(); v[:, 0] += bx - 0.9; v[:, 1] += by; v[:, 2] += bz
    meshes.append((v, i))
    # right score block
    v, i = make_box(0.55, 0.55, 0.14, BOARD_TEXT)
    v = v.copy(); v[:, 0] += bx + 0.9; v[:, 1] += by; v[:, 2] += bz
    meshes.append((v, i))
    # dash separator
    v, i = make_box(0.25, 0.08, 0.14, BOARD_TRIM)
    v = v.copy(); v[:, 0] += bx; v[:, 1] += by; v[:, 2] += bz
    meshes.append((v, i))
    return meshes


def build_environment_mesh():
    meshes = [_outer_floor()]
    meshes += _walls()
    # 4 light rigs (corners above court)
    for lx in [-4.5, 4.5]:
        for lz in [-5.5, 5.5]:
            meshes += _light_rig(lx, lz)
    meshes += _scoreboard()
    return combine_meshes(meshes)


class Environment:
    def __init__(self, ctx, renderer):
        v, i = build_environment_mesh()
        self.vao, _ = renderer.make_vao(v, i)
        self.renderer = renderer
        self.model = identity()

    def draw(self, vp):
        self.renderer.draw_vao(self.vao, self.model, vp)
