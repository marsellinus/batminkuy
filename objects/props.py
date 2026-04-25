"""
Courtside props: bench, water bottle, sports bag, shuttlecock box.
Each is a standalone class with a single combined VAO.
"""
import numpy as np
from renderer import (make_box, make_cylinder, make_cone, make_sphere,
                      combine_meshes, translate, rot_y, rot_x, identity)

# ── Shared colors ─────────────────────────────────────────────────────────────
WOOD   = [0.55, 0.38, 0.20]
METAL  = [0.45, 0.45, 0.50]
WHITE  = [0.92, 0.92, 0.92]
CORK   = [0.95, 0.85, 0.70]
FEATHER= [0.98, 0.98, 0.96]


# ── Bench ─────────────────────────────────────────────────────────────────────
def _bench_mesh():
    meshes = []
    # seat
    v, i = make_box(1.8, 0.08, 0.45, WOOD)
    v = v.copy(); v[:, 1] += 0.46
    meshes.append((v, i))
    # backrest
    v, i = make_box(1.8, 0.45, 0.06, WOOD)
    v = v.copy(); v[:, 1] += 0.72; v[:, 2] -= 0.20
    meshes.append((v, i))
    # 4 legs
    for lx in [-0.75, 0.75]:
        for lz in [-0.16, 0.16]:
            v, i = make_box(0.06, 0.46, 0.06, METAL)
            v = v.copy(); v[:, 0] += lx; v[:, 1] += 0.23; v[:, 2] += lz
            meshes.append((v, i))
    return combine_meshes(meshes)


class Bench:
    def __init__(self, ctx, renderer, position, angle=0.0):
        v, i = _bench_mesh()
        self.vao, _ = renderer.make_vao(v, i)
        self.renderer = renderer
        self.model = (translate(*position) @ rot_y(angle)).astype('f4')

    def draw(self, vp):
        self.renderer.draw_vao(self.vao, self.model, vp)


# ── Water Bottle ──────────────────────────────────────────────────────────────
def _bottle_mesh(color):
    meshes = []
    # body cylinder
    v, i = make_cylinder(0.055, 0.22, 8, color)
    v = v.copy(); v[:, 1] += 0.11
    meshes.append((v, i))
    # cap (small cylinder)
    cap = [min(c + 0.15, 1.0) for c in color]
    v, i = make_cylinder(0.04, 0.06, 8, cap)
    v = v.copy(); v[:, 1] += 0.25
    meshes.append((v, i))
    # label stripe (slightly wider, different shade)
    label = [min(c * 1.2, 1.0) for c in color]
    v, i = make_cylinder(0.057, 0.08, 8, label)
    v = v.copy(); v[:, 1] += 0.11
    meshes.append((v, i))
    return combine_meshes(meshes)


class Bottle:
    def __init__(self, ctx, renderer, position, color):
        v, i = _bottle_mesh(color)
        self.vao, _ = renderer.make_vao(v, i)
        self.renderer = renderer
        self.model = translate(*position).astype('f4')

    def draw(self, vp):
        self.renderer.draw_vao(self.vao, self.model, vp)


# ── Sports Bag ────────────────────────────────────────────────────────────────
def _bag_mesh(color):
    meshes = []
    # main body
    v, i = make_box(0.65, 0.28, 0.28, color)
    v = v.copy(); v[:, 1] += 0.14
    meshes.append((v, i))
    # front pocket
    pocket = [min(c * 0.75, 1.0) for c in color]
    v, i = make_box(0.30, 0.20, 0.06, pocket)
    v = v.copy(); v[:, 1] += 0.14; v[:, 2] += 0.17
    meshes.append((v, i))
    # strap
    v, i = make_box(0.04, 0.06, 0.50, [0.2, 0.2, 0.2])
    v = v.copy(); v[:, 1] += 0.30
    meshes.append((v, i))
    return combine_meshes(meshes)


class Bag:
    def __init__(self, ctx, renderer, position, color, angle=0.0):
        v, i = _bag_mesh(color)
        self.vao, _ = renderer.make_vao(v, i)
        self.renderer = renderer
        self.model = (translate(*position) @ rot_y(angle)).astype('f4')

    def draw(self, vp):
        self.renderer.draw_vao(self.vao, self.model, vp)


# ── Shuttlecock Box ───────────────────────────────────────────────────────────
def _mini_shuttle():
    """Tiny shuttlecock for inside the box."""
    v1, i1 = make_sphere(0.04, 4, 6, CORK)
    v2, i2 = make_cone(0.07, 0.10, 8, FEATHER)
    v2 = v2.copy(); v2[:, 1] -= 0.10
    return combine_meshes([(v1, i1), (v2, i2)])


def _box_mesh():
    BOX_COLOR = [0.60, 0.42, 0.22]
    WALL_T    = 0.04
    W, H, D   = 0.30, 0.22, 0.30
    meshes = []
    # bottom
    v, i = make_box(W, WALL_T, D, BOX_COLOR)
    meshes.append((v, i))
    # 4 sides (open top)
    for (ox, oy, ow, od) in [
        (0,       H/2, W,     WALL_T),   # front
        (0,       H/2, W,     WALL_T),   # back (offset below)
        (-W/2,    H/2, WALL_T, D),
        ( W/2,    H/2, WALL_T, D),
    ]:
        pass   # built individually below
    # front wall
    v, i = make_box(W, H, WALL_T, BOX_COLOR)
    v = v.copy(); v[:, 1] += H/2; v[:, 2] += D/2
    meshes.append((v, i))
    # back wall
    v, i = make_box(W, H, WALL_T, BOX_COLOR)
    v = v.copy(); v[:, 1] += H/2; v[:, 2] -= D/2
    meshes.append((v, i))
    # left wall
    v, i = make_box(WALL_T, H, D, BOX_COLOR)
    v = v.copy(); v[:, 0] -= W/2; v[:, 1] += H/2
    meshes.append((v, i))
    # right wall
    v, i = make_box(WALL_T, H, D, BOX_COLOR)
    v = v.copy(); v[:, 0] += W/2; v[:, 1] += H/2
    meshes.append((v, i))
    return combine_meshes(meshes)


class ShuttlecockBox:
    def __init__(self, ctx, renderer, position):
        v, i = _box_mesh()
        self.box_vao, _ = renderer.make_vao(v, i)
        # 3 mini shuttlecocks inside
        vs, is_ = _mini_shuttle()
        self.shuttle_vao, _ = renderer.make_vao(vs, is_)
        self.renderer = renderer
        self.pos = np.array(position, dtype='f4')
        self.model = translate(*position).astype('f4')
        # offsets for 3 shuttles inside box
        self._offsets = [(-0.08, 0.18, 0.0), (0.0, 0.18, 0.0), (0.08, 0.18, 0.0)]

    def draw(self, vp):
        self.renderer.draw_vao(self.box_vao, self.model, vp)
        for ox, oy, oz in self._offsets:
            m = translate(self.pos[0]+ox, self.pos[1]+oy, self.pos[2]+oz)
            self.renderer.draw_vao(self.shuttle_vao, m.astype('f4'), vp)


# ── Spectator (simple idle NPC) ───────────────────────────────────────────────
def _spectator_mesh(shirt_color):
    from renderer import make_cylinder
    meshes = []
    SKIN = [0.85, 0.65, 0.45]
    # torso
    v, i = make_box(0.30, 0.40, 0.18, shirt_color)
    v = v.copy(); v[:, 1] += 0.80
    meshes.append((v, i))
    # head
    v, i = make_sphere(0.16, 5, 7, SKIN)
    v = v.copy(); v[:, 1] += 1.28
    meshes.append((v, i))
    # arms (simple boxes)
    for sx in [-0.22, 0.22]:
        v, i = make_box(0.10, 0.34, 0.10, SKIN)
        v = v.copy(); v[:, 0] += sx; v[:, 1] += 0.80
        meshes.append((v, i))
    # legs
    for sx in [-0.09, 0.09]:
        v, i = make_box(0.10, 0.38, 0.12, [0.15, 0.15, 0.35])
        v = v.copy(); v[:, 0] += sx; v[:, 1] += 0.38
        meshes.append((v, i))
    return combine_meshes(meshes)


class Spectator:
    def __init__(self, ctx, renderer, position, shirt_color, angle=0.0):
        v, i = _spectator_mesh(shirt_color)
        self.vao, _ = renderer.make_vao(v, i)
        self.renderer = renderer
        self.model = (translate(*position) @ rot_y(angle)).astype('f4')

    def draw(self, vp):
        self.renderer.draw_vao(self.vao, self.model, vp)
