"""
Courtside props: bench, water bottle, sports bag, shuttlecock box,
spectator (animated), stands (tribun bertingkat).
"""
import numpy as np
from renderer import (make_box, make_cylinder, make_cone, make_sphere,
                      combine_meshes, translate, rot_y, rot_x, identity)

# ── Shared colors ─────────────────────────────────────────────────────────────
WOOD    = [0.55, 0.38, 0.20]
METAL   = [0.45, 0.45, 0.50]
WHITE   = [0.92, 0.92, 0.92]
CORK    = [0.95, 0.85, 0.70]
FEATHER = [0.98, 0.98, 0.96]
CONCRETE= [0.52, 0.52, 0.55]
BENCH_C = [0.48, 0.32, 0.18]


# ── Bench ─────────────────────────────────────────────────────────────────────
def _bench_mesh():
    meshes = []
    v, i = make_box(1.8, 0.08, 0.45, WOOD)
    v = v.copy(); v[:, 1] += 0.46
    meshes.append((v, i))
    v, i = make_box(1.8, 0.45, 0.06, WOOD)
    v = v.copy(); v[:, 1] += 0.72; v[:, 2] -= 0.20
    meshes.append((v, i))
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
    v, i = make_cylinder(0.055, 0.22, 8, color)
    v = v.copy(); v[:, 1] += 0.11
    meshes.append((v, i))
    cap = [min(c + 0.15, 1.0) for c in color]
    v, i = make_cylinder(0.04, 0.06, 8, cap)
    v = v.copy(); v[:, 1] += 0.25
    meshes.append((v, i))
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
    v, i = make_box(0.65, 0.28, 0.28, color)
    v = v.copy(); v[:, 1] += 0.14
    meshes.append((v, i))
    pocket = [min(c * 0.75, 1.0) for c in color]
    v, i = make_box(0.30, 0.20, 0.06, pocket)
    v = v.copy(); v[:, 1] += 0.14; v[:, 2] += 0.17
    meshes.append((v, i))
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
    v1, i1 = make_sphere(0.04, 4, 6, CORK)
    v2, i2 = make_cone(0.07, 0.10, 8, FEATHER)
    v2 = v2.copy(); v2[:, 1] -= 0.10
    return combine_meshes([(v1, i1), (v2, i2)])


def _box_mesh():
    BOX_COLOR = [0.60, 0.42, 0.22]
    WALL_T    = 0.04
    W, H, D   = 0.30, 0.22, 0.30
    meshes = []
    v, i = make_box(W, WALL_T, D, BOX_COLOR)
    meshes.append((v, i))
    v, i = make_box(W, H, WALL_T, BOX_COLOR)
    v = v.copy(); v[:, 1] += H/2; v[:, 2] += D/2
    meshes.append((v, i))
    v, i = make_box(W, H, WALL_T, BOX_COLOR)
    v = v.copy(); v[:, 1] += H/2; v[:, 2] -= D/2
    meshes.append((v, i))
    v, i = make_box(WALL_T, H, D, BOX_COLOR)
    v = v.copy(); v[:, 0] -= W/2; v[:, 1] += H/2
    meshes.append((v, i))
    v, i = make_box(WALL_T, H, D, BOX_COLOR)
    v = v.copy(); v[:, 0] += W/2; v[:, 1] += H/2
    meshes.append((v, i))
    return combine_meshes(meshes)


class ShuttlecockBox:
    def __init__(self, ctx, renderer, position):
        v, i = _box_mesh()
        self.box_vao, _ = renderer.make_vao(v, i)
        vs, is_ = _mini_shuttle()
        self.shuttle_vao, _ = renderer.make_vao(vs, is_)
        self.renderer = renderer
        self.pos = np.array(position, dtype='f4')
        self.model = translate(*position).astype('f4')
        self._offsets = [(-0.08, 0.18, 0.0), (0.0, 0.18, 0.0), (0.08, 0.18, 0.0)]

    def draw(self, vp):
        self.renderer.draw_vao(self.box_vao, self.model, vp)
        for ox, oy, oz in self._offsets:
            m = translate(self.pos[0]+ox, self.pos[1]+oy, self.pos[2]+oz)
            self.renderer.draw_vao(self.shuttle_vao, m.astype('f4'), vp)


# ── Spectator (animated: bobbing + hit reaction) ──────────────────────────────
def _spectator_mesh(shirt_color):
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
    # arms
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
        self.base_pos = np.array(position, dtype='f4')
        self.angle    = angle
        # randomize phase so spectators don't all bob in sync
        self._phase   = np.random.uniform(0.0, 2 * np.pi)
        self._head_phase = np.random.uniform(0.0, 2 * np.pi)
        self._t       = 0.0
        self._react   = 0.0   # hit reaction timer (0..1 → jump height)

    def trigger_hit(self):
        """Call when a hit occurs — spectator jumps."""
        self._react = 0.6   # seconds of reaction

    def update(self, dt):
        self._t += dt
        self._react = max(0.0, self._react - dt)

    def draw(self, vp):
        # idle bobbing
        bob = np.sin(self._t * 1.8 + self._phase) * 0.02
        # hit reaction: quick upward jump that decays
        react_y = np.sin(np.pi * (1.0 - self._react / 0.6)) * 0.12 \
                  if self._react > 0.0 else 0.0
        # random head turn
        head_rot = np.sin(self._t * 0.5 + self._head_phase) * 0.2

        pos = self.base_pos.copy()
        pos[1] += bob + react_y
        m = (translate(pos[0], pos[1], pos[2])
             @ rot_y(self.angle + head_rot)).astype('f4')
        self.renderer.draw_vao(self.vao, m, vp)


# ── Stands (tribun bertingkat) ────────────────────────────────────────────────
def _stands_mesh(side_x, facing_sign, rows=5):
    """
    Build a multi-tier stand on one side of the court.
    side_x: X position of the stand (positive or negative)
    facing_sign: +1 or -1 (which way the stand faces)
    rows: number of tiers
    """
    meshes = []
    ROW_W   = 12.0   # length along Z axis
    STEP_H  = 0.40   # height per tier
    STEP_D  = 0.55   # depth per tier
    SLAB_T  = 0.18   # slab thickness

    for i in range(rows):
        y = i * STEP_H
        z_offset = i * STEP_D * facing_sign
        x = side_x + z_offset   # tiers step outward

        # Concrete slab (seat platform)
        v, i_ = make_box(SLAB_T, SLAB_T, ROW_W, CONCRETE)
        v = v.copy()
        v[:, 0] += x
        v[:, 1] += y + SLAB_T / 2
        meshes.append((v, i_))

        # Wooden bench on top of slab
        v, i_ = make_box(SLAB_T * 0.8, 0.06, ROW_W * 0.95, BENCH_C)
        v = v.copy()
        v[:, 0] += x
        v[:, 1] += y + SLAB_T + 0.03
        meshes.append((v, i_))

    # Vertical back wall (structural support)
    total_h = rows * STEP_H
    back_x  = side_x + rows * STEP_D * facing_sign
    v, i_ = make_box(0.20, total_h, ROW_W, CONCRETE)
    v = v.copy()
    v[:, 0] += back_x
    v[:, 1] += total_h / 2
    meshes.append((v, i_))

    return combine_meshes(meshes)


class Stands:
    """Two-sided stands (left and right of court)."""
    def __init__(self, ctx, renderer):
        self.renderer = renderer
        # Left stand (negative X side, faces +X)
        vl, il = _stands_mesh(side_x=-7.0, facing_sign=-1)
        self.vao_left, _ = renderer.make_vao(vl, il)
        # Right stand (positive X side, faces -X)
        vr, ir = _stands_mesh(side_x=7.0, facing_sign=1)
        self.vao_right, _ = renderer.make_vao(vr, ir)
        self.model = identity()

    def draw(self, vp):
        self.renderer.draw_vao(self.vao_left,  self.model, vp)
        self.renderer.draw_vao(self.vao_right, self.model, vp)


# ── Umpire (Wasit) at the net ────────────────────────────────────────────────
def _umpire_chair_mesh():
    """Create a high chair for the umpire to sit on."""
    meshes = []
    
    # Chair seat (platform)
    v, i = make_box(0.50, 0.08, 0.50, METAL)
    v = v.copy(); v[:, 1] += 1.60
    meshes.append((v, i))
    
    # Backrest
    v, i = make_box(0.50, 0.50, 0.06, METAL)
    v = v.copy(); v[:, 1] += 1.95; v[:, 2] -= 0.20
    meshes.append((v, i))
    
    # 4 chair legs
    for lx in [-0.18, 0.18]:
        for lz in [-0.18, 0.18]:
            v, i = make_cylinder(0.03, 1.60, 6, METAL)
            v = v.copy(); v[:, 0] += lx; v[:, 1] += 0.80; v[:, 2] += lz
            meshes.append((v, i))
    
    return combine_meshes(meshes)


def _umpire_mesh():
    """Create an umpire figure sitting on chair."""
    meshes = []
    SKIN = [0.85, 0.65, 0.45]
    UNIFORM = [0.15, 0.15, 0.35]  # Dark blue uniform
    
    # Torso (sitting position)
    v, i = make_box(0.28, 0.35, 0.16, UNIFORM)
    v = v.copy(); v[:, 1] += 1.75
    meshes.append((v, i))
    
    # Head
    v, i = make_sphere(0.15, 5, 7, SKIN)
    v = v.copy(); v[:, 1] += 2.15
    meshes.append((v, i))
    
    # Arms (resting on armrests/body)
    for sx in [-0.20, 0.20]:
        v, i = make_box(0.08, 0.32, 0.08, SKIN)
        v = v.copy(); v[:, 0] += sx; v[:, 1] += 1.68
        meshes.append((v, i))
    
    # Legs (dangling)
    for sx in [-0.08, 0.08]:
        v, i = make_box(0.08, 0.40, 0.10, [0.15, 0.15, 0.35])
        v = v.copy(); v[:, 0] += sx; v[:, 1] += 1.20
        meshes.append((v, i))
    
    return combine_meshes(meshes)


class Umpire:
    """Umpire sitting on a high chair at the side of the net."""
    def __init__(self, ctx, renderer, position=(20.5, 0.0, 0.0), angle=-np.pi/2):
        # Chair mesh
        v_chair, i_chair = _umpire_chair_mesh()
        self.chair_vao, _ = renderer.make_vao(v_chair, i_chair)

        # Umpire figure mesh
        v_umpire, i_umpire = _umpire_mesh()
        self.umpire_vao, _ = renderer.make_vao(v_umpire, i_umpire)

        self.renderer = renderer
        self.pos = np.array(position, dtype='f4')

        # Rotate supaya menghadap lapangan
        self.model = (translate(*position) @ rot_y(angle)).astype('f4')

    def draw(self, vp):
        self.renderer.draw_vao(self.chair_vao, self.model, vp)
        self.renderer.draw_vao(self.umpire_vao, self.model, vp)


# ── Sponsor Banner (Iklan sponsor) ────────────────────────────────────────────
def _sponsor_banner_mesh(sponsor_name, bg_color):
    """Create a sponsor banner with text/logo."""
    meshes = []
    
    # Background panel
    v, i = make_box(1.2, 0.60, 0.08, bg_color)
    meshes.append((v, i))
    
    # Border frame (gold/silver)
    border_color = [0.85, 0.85, 0.10]
    # Top border
    v, i = make_box(1.2, 0.08, 0.10, border_color)
    v = v.copy(); v[:, 1] += 0.32
    meshes.append((v, i))
    # Bottom border
    v, i = make_box(1.2, 0.08, 0.10, border_color)
    v = v.copy(); v[:, 1] -= 0.32
    meshes.append((v, i))
    
    # Logo/text representation (simple colored rectangles)
    text_color = [0.95, 0.95, 0.95]
    
    if sponsor_name == "YONEX":
        # Yonex: red brand color
        bg_color = [0.95, 0.20, 0.10]
        # Re-create background with Yonex red
        v, i = make_box(1.2, 0.60, 0.08, bg_color)
        meshes = [(v, i)]
        
        # Text "YONEX" as blocks
        # Y
        v, i = make_box(0.08, 0.35, 0.10, text_color)
        v = v.copy(); v[:, 0] -= 0.35
        meshes.append((v, i))
        # O
        v, i = make_box(0.08, 0.35, 0.10, text_color)
        v = v.copy(); v[:, 0] -= 0.10
        meshes.append((v, i))
        # N
        v, i = make_box(0.08, 0.35, 0.10, text_color)
        v = v.copy(); v[:, 0] += 0.15
        meshes.append((v, i))
        # E
        v, i = make_box(0.08, 0.35, 0.10, text_color)
        v = v.copy(); v[:, 0] += 0.40
        meshes.append((v, i))
        # X
        v, i = make_box(0.08, 0.35, 0.10, text_color)
        v = v.copy(); v[:, 0] += 0.65
        meshes.append((v, i))
        
    elif sponsor_name == "LING":
        # Ling: blue brand color
        bg_color = [0.10, 0.40, 0.85]
        v, i = make_box(1.2, 0.60, 0.08, bg_color)
        meshes = [(v, i)]
        
        # Text "LING" as blocks
        # L
        v, i = make_box(0.08, 0.35, 0.10, text_color)
        v = v.copy(); v[:, 0] -= 0.25
        meshes.append((v, i))
        # I
        v, i = make_box(0.08, 0.35, 0.10, text_color)
        v = v.copy(); v[:, 0] -= 0.05
        meshes.append((v, i))
        # N
        v, i = make_box(0.08, 0.35, 0.10, text_color)
        v = v.copy(); v[:, 0] += 0.15
        meshes.append((v, i))
        # G
        v, i = make_box(0.08, 0.35, 0.10, text_color)
        v = v.copy(); v[:, 0] += 0.35
        meshes.append((v, i))
    
    # Add borders
    border_color = [0.85, 0.85, 0.10]
    v, i = make_box(1.2, 0.08, 0.10, border_color)
    v = v.copy(); v[:, 1] += 0.32
    meshes.append((v, i))
    v, i = make_box(1.2, 0.08, 0.10, border_color)
    v = v.copy(); v[:, 1] -= 0.32
    meshes.append((v, i))
    
    return combine_meshes(meshes)


class SponsorBanner:
    """Sponsor advertising banner placed at courtside."""
    def __init__(self, ctx, renderer, sponsor_name, position, angle=0.0):
        v, i = _sponsor_banner_mesh(sponsor_name, [0.90, 0.90, 0.90])
        self.vao, _ = renderer.make_vao(v, i)
        self.renderer = renderer
        self.model = (translate(*position) @ rot_y(angle)).astype('f4')
    
    def draw(self, vp):
        self.renderer.draw_vao(self.vao, self.model, vp)


# ── Line Umpire (Hakim Garis) ────────────────────────────────────────────────
def _line_umpire_mesh():
    """Line umpire sitting position."""
    meshes = []
    SKIN = [0.85, 0.65, 0.45]
    UNIFORM = [0.15, 0.15, 0.35]

    # ── Kursi kecil ──
    v, i = make_box(0.40, 0.08, 0.40, [0.3, 0.3, 0.3])
    v = v.copy(); v[:, 1] += 0.25
    meshes.append((v, i))

    # kaki kursi
    for lx in [-0.15, 0.15]:
        for lz in [-0.15, 0.15]:
            v, i = make_box(0.05, 0.25, 0.05, [0.2, 0.2, 0.2])
            v = v.copy(); v[:, 0] += lx; v[:, 1] += 0.125; v[:, 2] += lz
            meshes.append((v, i))

    # ── Badan (lebih rendah karena duduk) ──
    v, i = make_box(0.26, 0.32, 0.16, UNIFORM)
    v = v.copy(); v[:, 1] += 0.55
    meshes.append((v, i))

    # ── Kepala ──
    v, i = make_sphere(0.14, 5, 7, SKIN)
    v = v.copy(); v[:, 1] += 0.95
    meshes.append((v, i))

    # ── Lengan (lebih santai) ──
    # kanan (pegang bendera sedikit naik)
    v, i = make_box(0.08, 0.30, 0.08, SKIN)
    v = v.copy(); v[:, 0] += 0.18; v[:, 1] += 0.65
    meshes.append((v, i))

    # kiri (turun santai)
    v, i = make_box(0.08, 0.28, 0.08, SKIN)
    v = v.copy(); v[:, 0] -= 0.18; v[:, 1] += 0.60
    meshes.append((v, i))

    # ── Kaki (ditekuk ke depan = posisi duduk) ──
    for sx in [-0.08, 0.08]:
        v, i = make_box(0.08, 0.20, 0.12, UNIFORM)
        v = v.copy()
        v[:, 0] += sx
        v[:, 1] += 0.35
        v[:, 2] += 0.18   # maju ke depan (ini kunci biar terlihat duduk)
        meshes.append((v, i))

    # ── Bendera ──
    v, i = make_box(0.20, 0.15, 0.06, [0.95, 0.20, 0.20])
    v = v.copy(); v[:, 0] += 0.22; v[:, 1] += 0.85; v[:, 2] -= 0.05
    meshes.append((v, i))

    return combine_meshes(meshes)


class LineUmpire:
    """Line umpire sitting at court boundary to monitor lines."""
    def __init__(self, ctx, renderer, position=(0.0, 0.0, 0.0), angle=0.0):
        v, i = _line_umpire_mesh()
        self.vao, _ = renderer.make_vao(v, i)
        self.renderer = renderer
        self.model = (translate(*position) @ rot_y(angle)).astype('f4')

    def draw(self, vp):
        self.renderer.draw_vao(self.vao, self.model, vp)