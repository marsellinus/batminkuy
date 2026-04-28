"""
Courtside props: bench, water bottle, sports bag, shuttlecock box,
spectator (animated), stands (tribun bertingkat), umpire, sponsor banner,
line umpire, audience banner, balloon, country flag.
"""
import numpy as np
from renderer import (make_box, make_cylinder, make_cone, make_sphere,
                      combine_meshes, translate, rot_y, rot_x, rot_z, identity)

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
    # Seat plank
    v, i = make_box(1.8, 0.08, 0.45, WOOD)
    v = v.copy(); v[:, 1] += 0.46
    meshes.append((v, i))
    # Backrest
    v, i = make_box(1.8, 0.45, 0.06, WOOD)
    v = v.copy(); v[:, 1] += 0.72; v[:, 2] -= 0.20
    meshes.append((v, i))
    # Legs
    for lx in [-0.75, 0.75]:
        for lz in [-0.16, 0.16]:
            v, i = make_box(0.06, 0.46, 0.06, METAL)
            v = v.copy(); v[:, 0] += lx; v[:, 1] += 0.23; v[:, 2] += lz
            meshes.append((v, i))
    # Cushion (bantal tipis di atas bangku)
    v, i = make_box(1.75, 0.05, 0.40, [0.20, 0.45, 0.80])
    v = v.copy(); v[:, 1] += 0.525
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


# ── Towel ─────────────────────────────────────────────────────────────────────
def _towel_mesh():
    # Handuk terlipat di bangku
    meshes = []
    v, i = make_box(0.28, 0.04, 0.18, [0.95, 0.95, 0.95])
    meshes.append((v, i))
    # Garis warna di tepi handuk
    v, i = make_box(0.28, 0.045, 0.03, [0.15, 0.35, 0.85])
    v = v.copy(); v[:, 2] += 0.075
    meshes.append((v, i))
    return combine_meshes(meshes)


class Towel:
    def __init__(self, ctx, renderer, position, angle=0.0):
        v, i = _towel_mesh()
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
    # Main body
    v, i = make_box(0.65, 0.28, 0.28, color)
    v = v.copy(); v[:, 1] += 0.14
    meshes.append((v, i))
    # Front pocket
    pocket = [min(c * 0.75, 1.0) for c in color]
    v, i = make_box(0.30, 0.20, 0.06, pocket)
    v = v.copy(); v[:, 1] += 0.14; v[:, 2] += 0.17
    meshes.append((v, i))
    # Shoulder strap
    v, i = make_box(0.04, 0.06, 0.50, [0.2, 0.2, 0.2])
    v = v.copy(); v[:, 1] += 0.30
    meshes.append((v, i))
    # Racket handle mencuat dari atas tas
    v, i = make_cylinder(0.018, 0.35, 6, [0.15, 0.15, 0.15])
    v = v.copy(); v[:, 0] += 0.20; v[:, 1] += 0.455; v[:, 2] -= 0.05
    meshes.append((v, i))
    # Grip wrap (warna berbeda di ujung handle)
    v, i = make_cylinder(0.022, 0.10, 6, [0.85, 0.20, 0.10])
    v = v.copy(); v[:, 0] += 0.20; v[:, 1] += 0.58; v[:, 2] -= 0.05
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
    for (dz, sign) in [(D/2, 1), (-D/2, -1)]:
        v, i = make_box(W, H, WALL_T, BOX_COLOR)
        v = v.copy(); v[:, 1] += H/2; v[:, 2] += dz
        meshes.append((v, i))
    for (dx, sign) in [(-W/2, -1), (W/2, 1)]:
        v, i = make_box(WALL_T, H, D, BOX_COLOR)
        v = v.copy(); v[:, 0] += dx; v[:, 1] += H/2
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


# ── Spectator (animated: bobbing + hit reaction + clap) ───────────────────────
def _spectator_mesh(shirt_color):
    meshes = []
    SKIN = [0.85, 0.65, 0.45]
    v, i = make_box(0.30, 0.40, 0.18, shirt_color)
    v = v.copy(); v[:, 1] += 0.80
    meshes.append((v, i))
    v, i = make_sphere(0.16, 5, 7, SKIN)
    v = v.copy(); v[:, 1] += 1.28
    meshes.append((v, i))
    # legs
    for sx in [-0.09, 0.09]:
        v, i = make_box(0.10, 0.38, 0.12, [0.15, 0.15, 0.35])
        v = v.copy(); v[:, 0] += sx; v[:, 1] += 0.38
        meshes.append((v, i))
    return combine_meshes(meshes)


def _arm_mesh(color):
    v, i = make_box(0.10, 0.34, 0.10, color)
    return v, i


_CHEER_COLORS = [
    [0.95, 0.20, 0.20],
    [0.20, 0.50, 0.95],
    [0.95, 0.85, 0.10],
    [0.20, 0.85, 0.35],
    [0.85, 0.25, 0.85],
]


class Spectator:
    """
    item_type: None | 'stick' (cheerstick polos) | 'flag' (tongkat+bendera kecil)
    """
    def __init__(self, ctx, renderer, position, shirt_color, angle=0.0,
                 item_type=None, item_color_idx=0):
        v, i = _spectator_mesh(shirt_color)
        self.vao, _ = renderer.make_vao(v, i)
        SKIN = [0.85, 0.65, 0.45]
        va, ia = _arm_mesh(SKIN)
        self.vao_arm, _ = renderer.make_vao(va, ia)
        self.vao_eye,  _ = renderer.make_vao(*make_sphere(0.025, 3, 5, [0.05, 0.05, 0.05]))
        self.vao_mouth,_ = renderer.make_vao(*make_box(0.08, 0.015, 0.015, [0.8, 0.2, 0.2]))

        self.item_type = item_type
        color = _CHEER_COLORS[item_color_idx % len(_CHEER_COLORS)]

        if item_type in ('stick', 'flag'):
            # Tongkat kayu
            vs, is_ = make_cylinder(0.018, 0.55, 6, [0.70, 0.55, 0.30])
            self.vao_stick, _ = renderer.make_vao(vs, is_)

        if item_type == 'flag':
            # Panel bendera kecil di ujung tongkat
            vf, if_ = make_box(0.20, 0.13, 0.02, color)
            self.vao_item, _ = renderer.make_vao(vf, if_)
        elif item_type == 'stick':
            # Cheerstick: silinder warna-warni di ujung
            vc, ic = make_cylinder(0.030, 0.18, 6, color)
            self.vao_item, _ = renderer.make_vao(vc, ic)

        self.renderer   = renderer
        self.base_pos   = np.array(position, dtype='f4')
        self.angle      = angle
        self._phase     = np.random.uniform(0.0, 2 * np.pi)
        self._head_phase= np.random.uniform(0.0, 2 * np.pi)
        self._t         = 0.0
        self._react     = 0.0

    def trigger_hit(self):
        self._react = 0.8

    def update(self, dt):
        self._t += dt
        self._react = max(0.0, self._react - dt)

    def draw(self, vp):
        r   = self.renderer
        t   = self._t
        bob = np.sin(t * 1.8 + self._phase) * 0.02

        if self._react > 0.0:
            frac       = self._react / 0.8
            react_y    = np.sin(np.pi * (1.0 - frac)) * 0.22
            clap_angle = np.sin(t * 14.0) * 0.55
        else:
            react_y    = 0.0
            clap_angle = np.sin(t * 2.2 + self._phase) * 0.18

        head_rot = np.sin(t * 0.5 + self._head_phase) * 0.2

        # pos dengan bob+react untuk badan
        pos = self.base_pos.copy()
        pos[1] += bob + react_y
        base_m = (translate(pos[0], pos[1], pos[2]) @ rot_y(self.angle + head_rot)).astype('f4')
        r.draw_vao(self.vao, base_m, vp)

        # Tangan kiri
        arm_l = (translate(pos[0], pos[1], pos[2])
                 @ rot_y(self.angle)
                 @ translate(-0.22, 0.80, 0)
                 @ rot_z(-clap_angle)).astype('f4')
        r.draw_vao(self.vao_arm, arm_l, vp)

        # Tangan kanan — anchor dari base_pos (tanpa react_y) agar tongkat tidak terbang
        anchor = self.base_pos
        arm_r_base = (translate(anchor[0], anchor[1] + bob, anchor[2])
                      @ rot_y(self.angle)
                      @ translate(0.22, 0.80, 0))
        arm_r = (arm_r_base @ rot_z(clap_angle)).astype('f4')
        r.draw_vao(self.vao_arm, arm_r, vp)

        if self.item_type in ('stick', 'flag'):
            # Ujung bawah lengan = titik pegangan tongkat
            hand = arm_r_base @ rot_z(clap_angle) @ translate(0, -0.17, 0)
            # Tongkat ke atas dari tangan
            stick_m = (hand @ translate(0, 0.275, 0)).astype('f4')
            r.draw_vao(self.vao_stick, stick_m, vp)

            if self.item_type == 'flag':
                # Bendera berkibar di ujung tongkat
                wave = (np.sin(t * 14.0 + self._phase) * 0.45 if self._react > 0.0
                        else np.sin(t * 2.5 + self._phase) * 0.15)
                item_m = (hand @ translate(0.10, 0.60, 0) @ rot_z(wave)).astype('f4')
            else:
                # Cheerstick: silinder warna di ujung, dipukul-pukul
                item_m = (hand @ translate(0, 0.55, 0)).astype('f4')
            r.draw_vao(self.vao_item, item_m, vp)

        # Wajah
        head_m = translate(pos[0], pos[1] + 1.28, pos[2]) @ rot_y(self.angle + head_rot)
        r.draw_vao(self.vao_eye,   (head_m @ translate(-0.055, 0.04, 0.14)).astype('f4'), vp)
        r.draw_vao(self.vao_eye,   (head_m @ translate( 0.055, 0.04, 0.14)).astype('f4'), vp)
        r.draw_vao(self.vao_mouth, (head_m @ translate(0, -0.04, 0.15) @ rot_x(0.25)).astype('f4'), vp)


# ── Audience Banner (waving rectangle held by spectator) ─────────────────────
class AudienceBanner:
    """A colored banner held up in the stands, with waving animation."""
    COLORS = [
        [0.90, 0.15, 0.15],
        [0.15, 0.35, 0.90],
        [0.90, 0.80, 0.10],
        [0.15, 0.75, 0.25],
        [0.80, 0.30, 0.80],
    ]

    def __init__(self, ctx, renderer, position, color_idx=0, phase=0.0):
        color = self.COLORS[color_idx % len(self.COLORS)]
        trim  = [min(c * 1.3, 1.0) for c in color]
        v, i  = make_box(0.55, 0.30, 0.04, color)
        self.vao, _ = renderer.make_vao(v, i)
        vt, it = make_box(0.55, 0.04, 0.05, trim)
        self.vao_trim, _ = renderer.make_vao(vt, it)
        # stick
        vs, is_ = make_cylinder(0.02, 0.50, 6, [0.6, 0.5, 0.3])
        self.vao_stick, _ = renderer.make_vao(vs, is_)
        self.renderer = renderer
        self.base_pos = np.array(position, dtype='f4')
        self._phase   = phase
        self._t       = 0.0

    def update(self, dt):
        self._t += dt

    def draw(self, vp):
        r   = self.renderer
        t   = self._t
        wave = np.sin(t * 2.5 + self._phase) * 0.30   # waving rotation
        pos  = self.base_pos

        stick_m = translate(pos[0], pos[1], pos[2]).astype('f4')
        r.draw_vao(self.vao_stick, stick_m, vp)

        banner_m = (translate(pos[0], pos[1] + 0.40, pos[2])
                    @ rot_z(wave)).astype('f4')
        r.draw_vao(self.vao, banner_m, vp)

        trim_top = (translate(pos[0], pos[1] + 0.40 + 0.17, pos[2])
                    @ rot_z(wave)).astype('f4')
        trim_bot = (translate(pos[0], pos[1] + 0.40 - 0.17, pos[2])
                    @ rot_z(wave)).astype('f4')
        r.draw_vao(self.vao_trim, trim_top, vp)
        r.draw_vao(self.vao_trim, trim_bot, vp)


# ── Country Flag — hiasan digantung di langit-langit GOR ─────────────────────
class CountryFlag:
    """
    Bendera negara digantung dari langit-langit sebagai hiasan GOR.
    Kawat + rod horizontal + panel stripe menjuntai ke bawah, berkibar.
    """
    FLAG_PRESETS = {
        'INA': [[0.85, 0.10, 0.10], [0.95, 0.95, 0.95]],
        'MAS': [[0.85, 0.10, 0.10], [0.95, 0.95, 0.95],
                [0.85, 0.10, 0.10], [0.95, 0.95, 0.95]],
        'CHN': [[0.85, 0.10, 0.10]],
        'JPN': [[0.95, 0.95, 0.95]],
    }

    def __init__(self, ctx, renderer, position, country='INA', phase=0.0):
        stripes = self.FLAG_PRESETS.get(country, [[0.85, 0.10, 0.10], [0.95, 0.95, 0.95]])
        n = len(stripes)
        stripe_h = 0.38 / n
        self._stripe_h = stripe_h
        self.stripe_vaos = []
        for idx, color in enumerate(stripes):
            v, i = make_box(0.38, stripe_h, 0.03, color)
            vao, _ = renderer.make_vao(v, i)
            self.stripe_vaos.append((vao, idx))
        # Rod horizontal
        vr, ir = make_cylinder(0.015, 0.42, 6, [0.65, 0.65, 0.65])
        self.vao_rod, _ = renderer.make_vao(vr, ir)
        # Kawat penggantung
        vw, iw = make_cylinder(0.008, 0.55, 4, [0.50, 0.50, 0.50])
        self.vao_wire, _ = renderer.make_vao(vw, iw)
        self.renderer = renderer
        self.base_pos = np.array(position, dtype='f4')
        self._phase   = phase
        self._t       = 0.0

    def update(self, dt):
        self._t += dt

    def draw(self, vp):
        r    = self.renderer
        pos  = self.base_pos
        wave = np.sin(self._t * 1.8 + self._phase) * 0.12
        # Kawat
        r.draw_vao(self.vao_wire, translate(pos[0], pos[1] - 0.275, pos[2]).astype('f4'), vp)
        # Rod horizontal
        r.draw_vao(self.vao_rod,
                   (translate(pos[0], pos[1], pos[2]) @ rot_x(np.pi / 2)).astype('f4'), vp)
        # Panel bendera menjuntai ke bawah
        for vao, idx in self.stripe_vaos:
            stripe_y = pos[1] - 0.05 - idx * self._stripe_h - self._stripe_h / 2
            m = (translate(pos[0] + 0.19, stripe_y, pos[2]) @ rot_y(wave)).astype('f4')
            r.draw_vao(vao, m, vp)


# ── WallFlag — bendera ditempel di dinding arena ─────────────────────────────
class WallFlag:
    """
    Bendera negara ditempel di dinding arena.
    Ukuran 0.8 × 0.5. Stripe horizontal sesuai negara.
    JPN: background putih + lingkaran merah di tengah.
    Wave effect: rot_y(sin(t)).
    """
    # (stripe_colors_top_to_bottom, has_circle)
    FLAG_PRESETS = {
        'INA': ([[0.85, 0.10, 0.10], [0.95, 0.95, 0.95]], False),
        'MAS': ([[0.85, 0.10, 0.10], [0.95, 0.95, 0.95],
                 [0.85, 0.10, 0.10], [0.95, 0.95, 0.95]], False),
        'CHN': ([[0.85, 0.10, 0.10]], False),
        'JPN': ([[0.95, 0.95, 0.95]], True),
        'KOR': ([[0.95, 0.95, 0.95]], False),
    }
    FLAG_W = 0.80
    FLAG_H = 0.50

    def __init__(self, ctx, renderer, position, country='INA', phase=0.0):
        stripes, has_circle = self.FLAG_PRESETS.get(
            country, ([[0.85, 0.10, 0.10], [0.95, 0.95, 0.95]], False))
        n = len(stripes)
        sh = self.FLAG_H / n
        self._stripe_h = sh
        self._n = n

        self.stripe_vaos = []
        for color in stripes:
            v, i = make_box(self.FLAG_W, sh, 0.05, color)
            vao, _ = renderer.make_vao(v, i)
            self.stripe_vaos.append(vao)

        # Lingkaran merah untuk JPN
        self.vao_circle = None
        if has_circle:
            v, i = make_sphere(0.10, 5, 10, [0.85, 0.10, 0.10])
            # Pipihkan di Z jadi lingkaran flat
            v = v.copy(); v[:, 2] *= 0.15
            self.vao_circle, _ = renderer.make_vao(v, i)

        self.renderer = renderer
        self.base_pos = np.array(position, dtype='f4')
        self._phase   = phase
        self._t       = 0.0

    def update(self, dt):
        self._t += dt

    def draw(self, vp):
        r    = self.renderer
        pos  = self.base_pos
        wave = np.sin(self._t * 2.0 + self._phase) * 0.08

        # Stripe dari atas ke bawah
        for idx, vao in enumerate(self.stripe_vaos):
            y = pos[1] + (self._n - 1 - idx) * self._stripe_h + self._stripe_h / 2
            m = (translate(pos[0], y, pos[2]) @ rot_y(wave)).astype('f4')
            r.draw_vao(vao, m, vp)

        # Lingkaran merah di tengah (JPN)
        if self.vao_circle is not None:
            cy = pos[1] + self.FLAG_H / 2
            m  = (translate(pos[0], cy, pos[2] + 0.03) @ rot_y(wave)).astype('f4')
            r.draw_vao(self.vao_circle, m, vp)


# ── Stands (tribun bertingkat, lebih tinggi & jauh) ───────────────────────────
def _stands_mesh(side_x, facing_sign, rows=10):
    meshes = []
    ROW_W  = 14.0
    STEP_H = 0.42
    STEP_D = 0.52
    SLAB_T = 0.20

    for i in range(rows):
        y        = i * STEP_H
        x_offset = i * STEP_D * facing_sign
        x        = side_x + x_offset

        # Concrete slab
        v, i_ = make_box(SLAB_T, SLAB_T, ROW_W, CONCRETE)
        v = v.copy(); v[:, 0] += x; v[:, 1] += y + SLAB_T / 2
        meshes.append((v, i_))

        # Bench on slab
        v, i_ = make_box(SLAB_T * 0.8, 0.06, ROW_W * 0.95, BENCH_C)
        v = v.copy(); v[:, 0] += x; v[:, 1] += y + SLAB_T + 0.03
        meshes.append((v, i_))

    # Back support wall
    total_h = rows * STEP_H
    back_x  = side_x + rows * STEP_D * facing_sign
    v, i_ = make_box(0.22, total_h, ROW_W, CONCRETE)
    v = v.copy(); v[:, 0] += back_x; v[:, 1] += total_h / 2
    meshes.append((v, i_))

    return combine_meshes(meshes)


class Stands:
    def __init__(self, ctx, renderer):
        self.renderer = renderer
        vl, il = _stands_mesh(side_x=-9.5, facing_sign=-1, rows=10)
        self.vao_left, _ = renderer.make_vao(vl, il)
        vr, ir = _stands_mesh(side_x=9.5, facing_sign=1, rows=10)
        self.vao_right, _ = renderer.make_vao(vr, ir)
        self.model = identity()

    def draw(self, vp):
        self.renderer.draw_vao(self.vao_left,  self.model, vp)
        self.renderer.draw_vao(self.vao_right, self.model, vp)


# ── Umpire ────────────────────────────────────────────────────────────────────
def _umpire_chair_mesh():
    meshes = []
    v, i = make_box(0.50, 0.08, 0.50, METAL)
    v = v.copy(); v[:, 1] += 1.60
    meshes.append((v, i))
    v, i = make_box(0.50, 0.50, 0.06, METAL)
    v = v.copy(); v[:, 1] += 1.95; v[:, 2] -= 0.20
    meshes.append((v, i))
    for lx in [-0.18, 0.18]:
        for lz in [-0.18, 0.18]:
            v, i = make_cylinder(0.03, 1.60, 6, METAL)
            v = v.copy(); v[:, 0] += lx; v[:, 1] += 0.80; v[:, 2] += lz
            meshes.append((v, i))
    return combine_meshes(meshes)


def _umpire_mesh():
    meshes = []
    SKIN    = [0.85, 0.65, 0.45]
    UNIFORM = [0.15, 0.15, 0.35]
    v, i = make_box(0.28, 0.35, 0.16, UNIFORM)
    v = v.copy(); v[:, 1] += 1.75
    meshes.append((v, i))
    v, i = make_sphere(0.15, 5, 7, SKIN)
    v = v.copy(); v[:, 1] += 2.15
    meshes.append((v, i))
    for sx in [-0.20, 0.20]:
        v, i = make_box(0.08, 0.32, 0.08, SKIN)
        v = v.copy(); v[:, 0] += sx; v[:, 1] += 1.68
        meshes.append((v, i))
    for sx in [-0.08, 0.08]:
        v, i = make_box(0.08, 0.40, 0.10, UNIFORM)
        v = v.copy(); v[:, 0] += sx; v[:, 1] += 1.20
        meshes.append((v, i))
    return combine_meshes(meshes)


class Umpire:
    def __init__(self, ctx, renderer, position=(3.5, 0.0, 0.0), angle=-np.pi/2):
        v_chair, i_chair = _umpire_chair_mesh()
        self.chair_vao, _ = renderer.make_vao(v_chair, i_chair)
        v_ump, i_ump = _umpire_mesh()
        self.umpire_vao, _ = renderer.make_vao(v_ump, i_ump)

        # Wajah
        self.vao_eye,  _ = renderer.make_vao(*make_sphere(0.025, 3, 5, [0.05, 0.05, 0.05]))
        self.vao_brow, _ = renderer.make_vao(*make_box(0.07, 0.015, 0.015, [0.30, 0.18, 0.08]))
        self.vao_mouth,_ = renderer.make_vao(*make_box(0.08, 0.015, 0.015, [0.75, 0.20, 0.20]))

        self.renderer = renderer
        self.pos   = np.array(position, dtype='f4')
        self.angle = angle
        self.model = (translate(*position) @ rot_y(angle)).astype('f4')
        self._t      = 0.0
        self._react  = 0.0   # hit reaction timer

    def trigger_hit(self):
        self._react = 1.2   # wasit fokus lebih lama

    def update(self, dt):
        self._t += dt
        self._react = max(0.0, self._react - dt)

    def draw(self, vp):
        r = self.renderer
        r.draw_vao(self.chair_vao,  self.model, vp)
        r.draw_vao(self.umpire_vao, self.model, vp)

        # Kepala wasit ada di (pos + rot_y(angle)) @ (0, 2.15, 0)
        # Hitung posisi kepala di world space
        head_base = translate(*self.pos) @ rot_y(self.angle) @ translate(0, 2.15, 0)

        # Idle: kepala sedikit menoleh kiri-kanan mengikuti rally
        head_turn = np.sin(self._t * 0.4) * 0.25
        # Saat hit: kepala sedikit menunduk (fokus)
        head_nod  = -0.15 if self._react > 0.0 else 0.0

        head_m = head_base @ rot_y(head_turn) @ rot_x(head_nod)

        # Mata
        r.draw_vao(self.vao_eye, (head_m @ translate(-0.055, 0.03, 0.13)).astype('f4'), vp)
        r.draw_vao(self.vao_eye, (head_m @ translate( 0.055, 0.03, 0.13)).astype('f4'), vp)

        # Alis — turun saat fokus (hit), normal saat idle
        brow_y = 0.08 if self._react > 0.0 else 0.10
        brow_rx = 0.2 if self._react > 0.0 else 0.0
        r.draw_vao(self.vao_brow, (head_m @ translate(-0.055, brow_y, 0.13) @ rot_z(-brow_rx)).astype('f4'), vp)
        r.draw_vao(self.vao_brow, (head_m @ translate( 0.055, brow_y, 0.13) @ rot_z( brow_rx)).astype('f4'), vp)

        # Mulut — garis lurus saat fokus, sedikit senyum saat idle
        mouth_rx = 0.0 if self._react > 0.0 else 0.2
        r.draw_vao(self.vao_mouth, (head_m @ translate(0, -0.04, 0.14) @ rot_x(mouth_rx)).astype('f4'), vp)


# ── Sponsor Banner ────────────────────────────────────────────────────────────
def _sponsor_banner_mesh(sponsor_name):
    meshes = []
    if sponsor_name == "YONEX":
        bg = [0.95, 0.20, 0.10]
    else:
        bg = [0.10, 0.40, 0.85]

    v, i = make_box(1.2, 0.60, 0.08, bg)
    meshes.append((v, i))

    text_color = [0.95, 0.95, 0.95]
    n_letters = len(sponsor_name)
    spacing   = 0.22
    start_x   = -(n_letters - 1) * spacing / 2
    for k in range(n_letters):
        v, i = make_box(0.08, 0.32, 0.10, text_color)
        v = v.copy(); v[:, 0] += start_x + k * spacing
        meshes.append((v, i))

    border = [0.85, 0.85, 0.10]
    for dy in [0.32, -0.32]:
        v, i = make_box(1.2, 0.07, 0.10, border)
        v = v.copy(); v[:, 1] += dy
        meshes.append((v, i))

    return combine_meshes(meshes)


class SponsorBanner:
    def __init__(self, ctx, renderer, sponsor_name, position, angle=0.0):
        v, i = _sponsor_banner_mesh(sponsor_name)
        self.vao, _ = renderer.make_vao(v, i)
        self.renderer = renderer
        self.model = (translate(*position) @ rot_y(angle)).astype('f4')

    def draw(self, vp):
        self.renderer.draw_vao(self.vao, self.model, vp)


# ── Line Umpire ───────────────────────────────────────────────────────────────
def _line_umpire_mesh():
    meshes = []
    SKIN    = [0.85, 0.65, 0.45]
    UNIFORM = [0.15, 0.15, 0.35]

    v, i = make_box(0.40, 0.08, 0.40, [0.3, 0.3, 0.3])
    v = v.copy(); v[:, 1] += 0.25
    meshes.append((v, i))
    for lx in [-0.15, 0.15]:
        for lz in [-0.15, 0.15]:
            v, i = make_box(0.05, 0.25, 0.05, [0.2, 0.2, 0.2])
            v = v.copy(); v[:, 0] += lx; v[:, 1] += 0.125; v[:, 2] += lz
            meshes.append((v, i))
    v, i = make_box(0.26, 0.32, 0.16, UNIFORM)
    v = v.copy(); v[:, 1] += 0.55
    meshes.append((v, i))
    v, i = make_sphere(0.14, 5, 7, SKIN)
    v = v.copy(); v[:, 1] += 0.95
    meshes.append((v, i))
    for sx, dy in [( 0.18, 0.65), (-0.18, 0.60)]:
        v, i = make_box(0.08, 0.30, 0.08, SKIN)
        v = v.copy(); v[:, 0] += sx; v[:, 1] += dy
        meshes.append((v, i))
    for sx in [-0.08, 0.08]:
        v, i = make_box(0.08, 0.20, 0.12, UNIFORM)
        v = v.copy(); v[:, 0] += sx; v[:, 1] += 0.35; v[:, 2] += 0.18
        meshes.append((v, i))
    v, i = make_box(0.20, 0.15, 0.06, [0.95, 0.20, 0.20])
    v = v.copy(); v[:, 0] += 0.22; v[:, 1] += 0.85; v[:, 2] -= 0.05
    meshes.append((v, i))
    return combine_meshes(meshes)


class LineUmpire:
    def __init__(self, ctx, renderer, position=(0.0, 0.0, 0.0), angle=0.0):
        v, i = _line_umpire_mesh()
        self.vao, _ = renderer.make_vao(v, i)

        # Wajah
        self.vao_eye,  _ = renderer.make_vao(*make_sphere(0.022, 3, 5, [0.05, 0.05, 0.05]))
        self.vao_brow, _ = renderer.make_vao(*make_box(0.06, 0.013, 0.013, [0.30, 0.18, 0.08]))
        self.vao_mouth,_ = renderer.make_vao(*make_box(0.07, 0.013, 0.013, [0.75, 0.20, 0.20]))

        self.renderer = renderer
        self.pos   = np.array(position, dtype='f4')
        self.angle = angle
        self.model = (translate(*position) @ rot_y(angle)).astype('f4')
        self._t     = np.random.uniform(0.0, 6.28)
        self._react = 0.0

    def trigger_hit(self):
        self._react = 0.9

    def update(self, dt):
        self._t += dt
        self._react = max(0.0, self._react - dt)

    def draw(self, vp):
        r = self.renderer
        r.draw_vao(self.vao, self.model, vp)

        # Kepala line umpire di Y=0.95 (dari _line_umpire_mesh)
        head_base = translate(*self.pos) @ rot_y(self.angle) @ translate(0, 0.95, 0)

        # Idle: kepala sedikit goyang; saat hit: menoleh ke lapangan
        head_turn = np.sin(self._t * 0.35) * 0.15
        head_nod  = -0.20 if self._react > 0.0 else 0.0
        head_m = head_base @ rot_y(head_turn) @ rot_x(head_nod)

        r.draw_vao(self.vao_eye, (head_m @ translate(-0.048, 0.03, 0.12)).astype('f4'), vp)
        r.draw_vao(self.vao_eye, (head_m @ translate( 0.048, 0.03, 0.12)).astype('f4'), vp)

        brow_rx = 0.25 if self._react > 0.0 else 0.0
        r.draw_vao(self.vao_brow, (head_m @ translate(-0.048, 0.07, 0.12) @ rot_z(-brow_rx)).astype('f4'), vp)
        r.draw_vao(self.vao_brow, (head_m @ translate( 0.048, 0.07, 0.12) @ rot_z( brow_rx)).astype('f4'), vp)

        mouth_rx = 0.0 if self._react > 0.0 else 0.15
        r.draw_vao(self.vao_mouth, (head_m @ translate(0, -0.03, 0.13) @ rot_x(mouth_rx)).astype('f4'), vp)


# ── FloorLight — lampu sorot di sudut lapangan ────────────────────────────────
class FloorLight:
    """Lampu sorot berdiri di sudut lapangan, mengarah ke tengah."""
    def __init__(self, ctx, renderer, position, angle=0.0):
        meshes = []
        # Base (tripod kaki)
        for a in [0, 2.09, 4.19]:  # 120° apart
            dx = np.cos(a) * 0.25
            dz = np.sin(a) * 0.25
            v, i = make_cylinder(0.03, 0.40, 6, [0.25, 0.25, 0.25])
            v = v.copy()
            v[:, 0] += dx; v[:, 1] += 0.20; v[:, 2] += dz
            meshes.append((v, i))
        # Pole
        v, i = make_cylinder(0.04, 1.80, 8, [0.30, 0.30, 0.32])
        v = v.copy(); v[:, 1] += 0.90
        meshes.append((v, i))
        # Light head (box)
        v, i = make_box(0.30, 0.20, 0.25, [0.15, 0.15, 0.15])
        v = v.copy(); v[:, 1] += 1.85
        meshes.append((v, i))
        # Bulb (bright yellow)
        v, i = make_box(0.25, 0.15, 0.20, [1.00, 0.95, 0.70])
        v = v.copy(); v[:, 1] += 1.85; v[:, 2] += 0.05
        meshes.append((v, i))

        v, i = combine_meshes(meshes)
        self.vao, _ = renderer.make_vao(v, i)
        self.renderer = renderer
        self.model = (translate(*position) @ rot_y(angle)).astype('f4')

    def draw(self, vp):
        self.renderer.draw_vao(self.vao, self.model, vp)


# ── ScoreBoard — papan skor digital di pinggir net ────────────────────────────
class ScoreBoard:
    """Papan skor digital kecil di pinggir net, menampilkan skor 21-20."""
    def __init__(self, ctx, renderer, position, angle=0.0):
        meshes = []
        # Frame (hitam)
        v, i = make_box(0.80, 0.45, 0.08, [0.08, 0.08, 0.10])
        meshes.append((v, i))
        # Screen (hijau gelap)
        v, i = make_box(0.72, 0.38, 0.06, [0.10, 0.25, 0.12])
        v = v.copy(); v[:, 2] += 0.01
        meshes.append((v, i))
        # Digit "21" kiri (merah terang)
        v, i = make_box(0.12, 0.22, 0.07, [0.95, 0.20, 0.10])
        v = v.copy(); v[:, 0] -= 0.18; v[:, 2] += 0.02
        meshes.append((v, i))
        v, i = make_box(0.08, 0.22, 0.07, [0.95, 0.20, 0.10])
        v = v.copy(); v[:, 0] -= 0.05; v[:, 2] += 0.02
        meshes.append((v, i))
        # Colon tengah
        for dy in [0.08, -0.08]:
            v, i = make_box(0.04, 0.04, 0.07, [0.90, 0.90, 0.10])
            v = v.copy(); v[:, 1] += dy; v[:, 2] += 0.02
            meshes.append((v, i))
        # Digit "20" kanan (biru terang)
        v, i = make_box(0.12, 0.22, 0.07, [0.10, 0.60, 0.95])
        v = v.copy(); v[:, 0] += 0.05; v[:, 2] += 0.02
        meshes.append((v, i))
        v, i = make_box(0.12, 0.22, 0.07, [0.10, 0.60, 0.95])
        v = v.copy(); v[:, 0] += 0.18; v[:, 2] += 0.02
        meshes.append((v, i))
        # Stand pole
        v, i = make_cylinder(0.03, 1.20, 6, [0.35, 0.35, 0.35])
        v = v.copy(); v[:, 1] -= 0.60
        meshes.append((v, i))

        v, i = combine_meshes(meshes)
        self.vao, _ = renderer.make_vao(v, i)
        self.renderer = renderer
        self.model = (translate(*position) @ rot_y(angle)).astype('f4')

    def draw(self, vp):
        self.renderer.draw_vao(self.vao, self.model, vp)
