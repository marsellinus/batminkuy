"""
Player — hierarchical low-poly character.

Right arm aim system (2-axis):
  shoulder_world = root @ translate(SH_X, SH_Y, 0) @ [0,0,0,1]
  dir   = normalize(shuttle - shoulder_world)
  yaw   = atan2(dir.x, dir.z)          → rot_y in shoulder local space
  pitch = atan2(dir.y, |dir.xz|)       → rot_z (down = negative pitch)
  elbow_bend = lerp(0.7, 0.15, dist/2.5)  → more bent when close

All rotations smoothed with per-frame lerp stored in self._smooth_*.
"""
import numpy as np
from renderer import (make_box, make_sphere, make_cylinder, make_circle_flat,
                      translate, rot_x, rot_y, rot_z)
from objects.racket import build_racket_mesh
from animation import lerp

UARM_H  = 0.26
LARM_H  = 0.22
THIGH_H = 0.28
SHIN_H  = 0.26

BODY_Y  = 0.90
HEAD_DY = 0.65
SH_X    = 0.29
SH_Y    = 1.36
HIP_X   = 0.13

SKIN      = [0.95, 0.75, 0.55]
SHOE      = [0.12, 0.12, 0.12]
SHADOW    = [0.0,  0.0,  0.0]
DEBUG_DOT = [1.0,  1.0,  0.0]

KITS = [
    {'shirt': [0.15, 0.35, 0.85], 'shorts': [0.10, 0.10, 0.55], 'sock': [0.88, 0.88, 0.88]},
    {'shirt': [0.85, 0.18, 0.18], 'shorts': [0.55, 0.08, 0.08], 'sock': [0.88, 0.88, 0.88]},
]

SMOOTH = 12.0   # lerp speed (units/sec)


class Player:
    _kit_index = 0
    show_debug = False

    def __init__(self, ctx, renderer, position, facing=1.0):
        self.position     = np.array(position, dtype='f4')
        self.facing       = facing
        self.renderer     = renderer
        self._t           = 0.0
        self._hit_blend   = 0.0
        self._shuttle_pos = np.array([0.0, 1.5, 0.0], dtype='f4')

        kit = KITS[Player._kit_index % len(KITS)]
        Player._kit_index += 1

        def vao(fn, *a, alpha=False):
            v, i = fn(*a)
            return renderer.make_vao(v, i, alpha=alpha)[0]

        self.vao_head   = vao(make_sphere,      0.21, 7, 10, SKIN)
        self.vao_body   = vao(make_box,         0.42, 0.56, 0.22, kit['shirt'])
        self.vao_uarm   = vao(make_cylinder,    0.075, UARM_H,  8, SKIN)
        self.vao_larm   = vao(make_cylinder,    0.065, LARM_H,  8, SKIN)
        self.vao_thigh  = vao(make_cylinder,    0.095, THIGH_H, 8, kit['shorts'])
        self.vao_shin   = vao(make_cylinder,    0.075, SHIN_H,  8, kit['sock'])
        self.vao_shoe   = vao(make_box,         0.14, 0.09, 0.24, SHOE)
        self.vao_shadow = vao(make_circle_flat, 0.36, 14, SHADOW, alpha=True)
        self.vao_racket = vao(build_racket_mesh)
        self.vao_dot    = vao(make_sphere,      0.04, 3, 6, DEBUG_DOT)

        # Smoothed state (updated each frame via lerp)
        self._s_ra_yaw   = 0.0    # right shoulder yaw  (Y rotation)
        self._s_ra_pitch = -0.20  # right shoulder pitch (Z rotation)
        self._s_elbow    = 0.25   # elbow bend
        self._s_head_yaw = 0.0
        self._s_head_pit = 0.0

        # Movement / rally state
        self.state       = 'idle'   # 'idle' | 'move' | 'hit'
        self._target_pos = self.position.copy()
        self.SPEED       = 3.5      # m/s
        self._shuttle    = None     # set via set_shuttle()

    def set_target(self, x, z):
        """Move toward (x, z), clamped to this player's half of court."""
        # Court: Z = -6.7 to +6.7, net at Z=0
        # player facing=+1 is on -Z side, facing=-1 is on +Z side
        if self.facing > 0:   # player1: Z in [-6.7, -0.8]
            z_min, z_max = -6.7, -0.8
        else:                  # player2: Z in [+0.8, +6.7]
            z_min, z_max = 0.8, 6.7
        self._target_pos = np.array([
            np.clip(x, -2.8, 2.8),
            self.position[1],
            np.clip(z, z_min, z_max),
        ], dtype='f4')
        if self.state != 'hit':
            self.state = 'move'

    def set_hit_blend(self, t):     self._hit_blend = t
    def trigger_hit(self):          pass
    def set_shuttle(self, shuttle):
        """Pass shuttlecock object so player can use predict()."""
        self._shuttle = shuttle
        self._shuttle_pos = shuttle.position.copy()

    def update(self, dt):
        self._t += dt
        k = min(SMOOTH * dt, 1.0)

        # ── Movement ─────────────────────────────────────────────────────────
        if self.state == 'move':
            to_target = self._target_pos - self.position
            to_target[1] = 0
            dist_to_target = np.linalg.norm(to_target)
            if dist_to_target > 0.08:
                self.position += (to_target / dist_to_target) * self.SPEED * dt
            else:
                self.position[:] = self._target_pos
                self.state = 'idle'
            self.position[1] = 0.025   # always stand on court surface

        hb = self._hit_blend
        fa = 0.0 if self.facing > 0 else np.pi

        # ── Shoulder world position (via full root transform) ─────────────────
        p = self.position
        b_rot = lerp(0.0, 0.25 * self.facing, hb)  # More body rotation on hit
        root_approx = (translate(p[0], p[1], p[2])
                       @ rot_y(fa + b_rot))
        sh_world = (root_approx @ np.array([SH_X, SH_Y, 0, 1], dtype='f4'))[:3]

        # ── Direction to shuttlecock (use predicted intercept, not current pos) ─
        aim_pos = self._shuttle.predict(0.20) if self._shuttle is not None \
                  else self._shuttle_pos
        to_sh = aim_pos - sh_world
        dist  = float(np.linalg.norm(to_sh)) + 1e-6
        d     = to_sh / dist

        # 2-axis aim angles (in shoulder local space)
        target_yaw   = float(np.arctan2(d[0], d[2]))          # left/right
        target_pitch = float(-np.arctan2(d[1], np.linalg.norm(d[[0,2]]) + 1e-6))  # up/down

        # Clamp to natural arm range
        target_yaw   = np.clip(target_yaw,   -0.6,  0.6)
        target_pitch = np.clip(target_pitch, -1.3,  0.3)

        # Elbow: more bent when shuttle is close, MUCH more during hit
        target_elbow = lerp(0.70, 0.15, np.clip(dist / 2.5, 0.0, 1.0))
        target_elbow = lerp(target_elbow, 0.05, hb)  # Compress arm significantly on hit

        # Head tracking (use predicted pos for more natural look)
        head_origin = p + np.array([0, 1.58, 0], dtype='f4')
        dh = aim_pos - head_origin
        target_hy = float(np.arctan2(dh[0], dh[2])) * 0.35  # More head turn
        target_hp = float(np.arctan2(dh[1], np.linalg.norm(dh[[0,2]]) + 1e-6)) * 0.30  # More head up/down

        # Blend aim influence by hit_blend
        idle_pitch = -np.sin(self._t * 2.4) * 0.12 - 0.20
        self._s_ra_yaw   += (lerp(0.0,          target_yaw,   hb) - self._s_ra_yaw)   * k * 1.5  # Faster blend
        self._s_ra_pitch += (lerp(idle_pitch,   target_pitch, hb) - self._s_ra_pitch) * k * 1.5  # Faster blend
        self._s_elbow    += (lerp(0.25,         target_elbow, hb) - self._s_elbow)    * k * 2.0  # Much faster elbow
        self._s_head_yaw += (target_hy - self._s_head_yaw) * k * 1.3
        self._s_head_pit += (target_hp - self._s_head_pit) * k * 1.3

    @staticmethod
    def _arm(root, sh_x, sh_y, yaw, pitch, elbow_z):
        """
        2-axis shoulder: rot_y(yaw) then rot_z(pitch).
        Pivot chain: shoulder → uarm → elbow → larm → hand_tip
        """
        shoulder = root @ translate(sh_x, sh_y, 0)
        uarm_m   = shoulder @ rot_y(yaw) @ rot_z(pitch)
        elbow    = uarm_m   @ translate(0, -UARM_H / 2, 0)
        larm_m   = elbow    @ rot_z(elbow_z) @ translate(0, -LARM_H / 2, 0)
        hand_tip = larm_m   @ translate(0, -LARM_H / 2, 0)
        return uarm_m, larm_m, hand_tip

    @staticmethod
    def _leg(root, hip_x, leg_x):
        hip    = root  @ translate(hip_x, 0.36, 0)
        thigh  = hip   @ rot_x(leg_x)
        knee   = thigh @ translate(0, -THIGH_H / 2, 0)
        shin   = knee  @ rot_x(-abs(leg_x) * 0.45) @ translate(0, -SHIN_H / 2, 0)
        foot   = shin  @ translate(0, -SHIN_H / 2, 0.03)
        return thigh, shin, foot

    def draw(self, vp):
        r  = self.renderer
        p  = self.position
        t  = self._t
        hb = self._hit_blend
        fa = 0.0 if self.facing > 0 else np.pi

        bob   = np.sin(t * 2.4) * 0.04
        sway  = np.sin(t * 1.2) * 0.025
        la_z  = np.sin(t * 2.4) * 0.12 + 0.20
        # faster leg swing when moving
        leg_speed = 5.0 if self.state == 'move' else 2.4
        leg_amp   = 0.35 if self.state == 'move' else 0.18
        leg   = np.sin(t * leg_speed) * leg_amp
        b_rot = lerp(0.0, 0.25 * self.facing, hb)  # More body rotation on hit

        root = (translate(p[0], p[1] + bob, p[2])
                @ rot_y(fa + b_rot)
                @ rot_x(-0.07 + sway))

        # Shadow
        r.draw_vao(self.vao_shadow, translate(p[0], 0.02, p[2]).astype('f4'), vp, alpha=0.28)

        # Body
        body = root @ translate(0, BODY_Y, 0)
        r.draw_vao(self.vao_body, body.astype('f4'), vp)

        # Head
        head = body @ translate(0, HEAD_DY, 0) @ rot_y(self._s_head_yaw) @ rot_x(self._s_head_pit)
        r.draw_vao(self.vao_head, head.astype('f4'), vp)

        # Left arm (1-axis, idle only)
        sh_l   = root @ translate(-SH_X, SH_Y, 0)
        uarm_l = sh_l @ rot_z(la_z)
        elbow_l = uarm_l @ translate(0, -UARM_H/2, 0)
        larm_l  = elbow_l @ rot_z(-0.30) @ translate(0, -LARM_H/2, 0)
        r.draw_vao(self.vao_uarm, uarm_l.astype('f4'), vp)
        r.draw_vao(self.vao_larm, larm_l.astype('f4'), vp)

        # Right arm + racket (2-axis aim)
        uarm_r, larm_r, hand = self._arm(
            root, SH_X, SH_Y,
            self._s_ra_yaw, self._s_ra_pitch, self._s_elbow
        )
        r.draw_vao(self.vao_uarm, uarm_r.astype('f4'), vp)
        r.draw_vao(self.vao_larm, larm_r.astype('f4'), vp)

        # Racket — strict child of hand_tip
        racket = hand @ rot_x(np.pi) @ rot_z(-0.12)
        r.draw_vao(self.vao_racket, racket.astype('f4'), vp)

        if Player.show_debug:
            r.draw_vao(self.vao_dot, hand.astype('f4'), vp)

        # Legs
        thigh_l, shin_l, foot_l = self._leg(root, -HIP_X,  leg)
        r.draw_vao(self.vao_thigh, thigh_l.astype('f4'), vp)
        r.draw_vao(self.vao_shin,  shin_l.astype('f4'),  vp)
        r.draw_vao(self.vao_shoe,  foot_l.astype('f4'),  vp)

        thigh_r, shin_r, foot_r = self._leg(root,  HIP_X, -leg)
        r.draw_vao(self.vao_thigh, thigh_r.astype('f4'), vp)
        r.draw_vao(self.vao_shin,  shin_r.astype('f4'),  vp)
        r.draw_vao(self.vao_shoe,  foot_r.astype('f4'),  vp)
