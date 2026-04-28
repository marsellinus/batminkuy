"""
Player — hierarchical low-poly character.

face_state: "neutral" | "smile" | "angry"
  neutral → normal eyes + flat mouth
  smile   → mouth scale melebar (rot_x lebih besar)
  angry   → alis turun (eye_y offset), mouth sedikit turun

Hit state machine: idle → prepare → hit → recover → idle
  prepare: arm pulled back, body rotates back
  hit:     arm swings fast, racket leads, body leans forward
  recover: arm follows through, body returns
"""
import numpy as np
from renderer import (make_box, make_sphere, make_cylinder, make_circle_flat,
                      translate, rot_x, rot_y, rot_z, scale_mat)
from objects.racket import build_racket_mesh
from animation import lerp, SWING_TYPES

UARM_H  = 0.30
LARM_H  = 0.26
THIGH_H = 0.34
SHIN_H  = 0.32

BODY_Y  = 1.05
HEAD_DY = 0.72
SH_X    = 0.30
SH_Y    = 1.20
HIP_X   = 0.13

SKIN       = [0.95, 0.75, 0.55]
SHOE       = [0.12, 0.12, 0.12]
SHADOW     = [0.0,  0.0,  0.0]
DEBUG_DOT  = [1.0,  1.0,  0.0]
FACE_BLACK = [0.05, 0.05, 0.05]
FACE_RED   = [0.8,  0.2,  0.2]
BROW_COLOR = [0.35, 0.22, 0.10]

KITS = [
    {'shirt': [0.15, 0.35, 0.85], 'shorts': [0.10, 0.10, 0.55], 'sock': [0.88, 0.88, 0.88]},
    {'shirt': [0.85, 0.18, 0.18], 'shorts': [0.55, 0.08, 0.08], 'sock': [0.88, 0.88, 0.88]},
]

SMOOTH = 12.0


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
        self.hit_state    = 'idle'   # 'idle' | 'prepare' | 'hit' | 'recover'
        self.face_state   = 'neutral'  # 'neutral' | 'smile' | 'angry'
        self._face_timer  = 0.0      # how long current face_state lasts

        kit = KITS[Player._kit_index % len(KITS)]
        Player._kit_index += 1

        def vao(fn, *a, alpha=False):
            v, i = fn(*a)
            return renderer.make_vao(v, i, alpha=alpha)[0]

        self.vao_head   = vao(make_sphere,      0.21, 7, 10, SKIN)
        self.vao_eye    = vao(make_sphere,      0.035, 4, 6, FACE_BLACK)
        self.vao_mouth  = vao(make_box,         0.10, 0.02, 0.02, FACE_RED)
        self.vao_brow   = vao(make_box,         0.08, 0.015, 0.015, BROW_COLOR)
        self.vao_body   = vao(make_box,         0.42, 0.56, 0.22, kit['shirt'])
        self.vao_uarm   = vao(make_cylinder,    0.075, UARM_H,  8, SKIN)
        self.vao_larm   = vao(make_cylinder,    0.065, LARM_H,  8, SKIN)
        self.vao_thigh  = vao(make_cylinder,    0.095, THIGH_H, 8, kit['shorts'])
        self.vao_shin   = vao(make_cylinder,    0.075, SHIN_H,  8, kit['sock'])
        self.vao_shoe   = vao(make_box,         0.14, 0.09, 0.24, SHOE)
        self.vao_shadow = vao(make_circle_flat, 0.36, 14, SHADOW, alpha=True)
        self.vao_racket = vao(build_racket_mesh)
        self.vao_dot    = vao(make_sphere,      0.04, 3, 6, DEBUG_DOT)

        self._s_ra_yaw      = 0.0
        self._s_ra_pitch    = -0.20
        self._s_elbow       = 0.25
        self._s_head_yaw    = 0.0
        self._s_head_pit    = 0.0
        self._s_body_rot    = 0.0
        self._s_body_lean   = 0.0   # forward lean saat hit
        self._s_racket_lag  = 0.0

        self.state       = 'idle'
        self.swing_type  = 'forehand'
        self._target_pos = self.position.copy()
        self.SPEED       = 3.5
        self._shuttle    = None

    def set_face_state(self, state, duration=1.2):
        """Set face expression with auto-reset after duration seconds."""
        self.face_state  = state
        self._face_timer = duration

    def set_target(self, x, z):
        if self.facing > 0:
            z_min, z_max = -6.7, -0.8
        else:
            z_min, z_max = 0.8, 6.7
        self._target_pos = np.array([
            np.clip(x, -2.8, 2.8),
            self.position[1],
            np.clip(z, z_min, z_max),
        ], dtype='f4')
        if self.state != 'hit':
            self.state = 'move'

    def set_hit_blend(self, t):  self._hit_blend = t
    def trigger_hit(self):       pass
    def set_shuttle(self, shuttle):
        self._shuttle = shuttle
        self._shuttle_pos = shuttle.position.copy()

    def update(self, dt):
        self._t += dt
        k = min(SMOOTH * dt, 1.0)

        # Auto-reset face_state ke neutral
        if self._face_timer > 0.0:
            self._face_timer -= dt
            if self._face_timer <= 0.0:
                self.face_state = 'neutral'

        if self.state == 'move':
            to_target = self._target_pos - self.position
            to_target[1] = 0
            dist_to_target = np.linalg.norm(to_target)
            if dist_to_target > 0.08:
                self.position += (to_target / dist_to_target) * self.SPEED * dt
            else:
                self.position[:] = self._target_pos
                self.state = 'idle'
            self.position[1] = 0.025

        hb = self._hit_blend
        fa = 0.0 if self.facing > 0 else np.pi

        sw = SWING_TYPES.get(self.swing_type, SWING_TYPES['forehand'])
        if self.hit_state == 'prepare':
            state_pitch_offset = sw['pitch_prepare']
            target_body_rot    = sw['body_prepare'] * self.facing
            target_body_lean   = -0.08   # sedikit condong ke belakang saat prepare
            target_racket_lag  = +0.30   # racket tertinggal saat prepare
        elif self.hit_state == 'hit':
            state_pitch_offset = sw['pitch_hit']
            target_body_rot    = sw['body_hit'] * self.facing
            target_body_lean   = +0.18   # condong ke depan saat hit
            target_racket_lag  = -0.20   # racket memimpin saat hit
        elif self.hit_state == 'recover':
            state_pitch_offset = sw['pitch_recover']
            target_body_rot    = sw['body_prepare'] * self.facing * 0.5
            target_body_lean   = +0.06   # masih sedikit condong
            target_racket_lag  = +0.12   # follow-through: racket masih di depan
        else:
            state_pitch_offset = 0.0
            target_body_rot    = 0.0
            target_body_lean   = 0.0
            target_racket_lag  = 0.0

        self._s_body_rot  += (target_body_rot  - self._s_body_rot)  * k * 1.5
        self._s_body_lean += (target_body_lean - self._s_body_lean) * k * 1.8
        # Racket lag: slower to follow = more natural delay
        self._s_racket_lag += (target_racket_lag - self._s_racket_lag) * k * 1.2

        p = self.position
        root_approx = (translate(p[0], p[1], p[2])
                       @ rot_y(fa + self._s_body_rot))
        sh_world = (root_approx @ np.array([SH_X, SH_Y, 0, 1], dtype='f4'))[:3]

        aim_pos = self._shuttle.predict(0.20) if self._shuttle is not None \
                  else self._shuttle_pos
        to_sh = aim_pos - sh_world
        dist  = float(np.linalg.norm(to_sh)) + 1e-6
        d     = to_sh / dist

        target_yaw   = float(np.arctan2(d[0], d[2]))
        target_pitch = float(-np.arctan2(d[1], np.linalg.norm(d[[0,2]]) + 1e-6))
        target_yaw   = np.clip(target_yaw,   -0.6,  0.6)
        target_pitch = np.clip(target_pitch, -1.3,  0.3)

        target_pitch += state_pitch_offset * hb
        target_yaw   += sw['yaw_offset'] * hb

        target_elbow = lerp(0.70, 0.15, np.clip(dist / 2.5, 0.0, 1.0))
        target_elbow = lerp(target_elbow, 0.05, hb)

        head_origin = p + np.array([0, 1.85, 0], dtype='f4')
        dh = aim_pos - head_origin
        target_hy = float(np.arctan2(dh[0], dh[2])) * 0.35
        target_hp = float(np.arctan2(dh[1], np.linalg.norm(dh[[0,2]]) + 1e-6)) * 0.30

        idle_pitch = -np.sin(self._t * 2.4) * 0.12 - 0.20
        self._s_ra_yaw   += (lerp(0.0,        target_yaw,   hb) - self._s_ra_yaw)   * k * 1.5
        self._s_ra_pitch += (lerp(idle_pitch, target_pitch, hb) - self._s_ra_pitch) * k * 1.5
        self._s_elbow    += (lerp(0.25,       target_elbow, hb) - self._s_elbow)    * k * 2.0
        self._s_head_yaw += (target_hy - self._s_head_yaw) * k * 1.3
        self._s_head_pit += (target_hp - self._s_head_pit) * k * 1.3

    @staticmethod
    def _arm(root, sh_x, sh_y, yaw, pitch, elbow_z):
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

    def _draw_face(self, head_mat, vp):
        """Draw eyes, eyebrows, and mouth based on face_state."""
        r = self.renderer
        fs = self.face_state

        # ── Eyebrows ──
        # neutral: flat; angry: rotated down toward center
        brow_rot_l = -0.3 if fs == 'angry' else 0.0
        brow_rot_r =  0.3 if fs == 'angry' else 0.0
        brow_y_offset = -0.02 if fs == 'angry' else 0.0

        brow_l = head_mat @ translate(-0.07, 0.12 + brow_y_offset, 0.18) @ rot_z(brow_rot_l)
        brow_r = head_mat @ translate( 0.07, 0.12 + brow_y_offset, 0.18) @ rot_z(brow_rot_r)
        r.draw_vao(self.vao_brow, brow_l.astype('f4'), vp)
        r.draw_vao(self.vao_brow, brow_r.astype('f4'), vp)

        # ── Eyes ──
        # angry: squint (scale y kecil)
        eye_sy = 0.6 if fs == 'angry' else 1.0
        eye_l_mat = head_mat @ translate(-0.07, 0.05, 0.18) @ scale_mat(1.0, eye_sy, 1.0)
        eye_r_mat = head_mat @ translate( 0.07, 0.05, 0.18) @ scale_mat(1.0, eye_sy, 1.0)
        r.draw_vao(self.vao_eye, eye_l_mat.astype('f4'), vp)
        r.draw_vao(self.vao_eye, eye_r_mat.astype('f4'), vp)

        # ── Mouth ──
        # neutral: flat; smile: melebar + rot_x; angry: sedikit turun
        if fs == 'smile':
            mouth_sx   = 1.6   # melebar
            mouth_rx   = 0.45  # curve ke atas
            mouth_y    = -0.05
        elif fs == 'angry':
            mouth_sx   = 1.0
            mouth_rx   = -0.2  # curve ke bawah
            mouth_y    = -0.07
        else:
            mouth_sx   = 1.0
            mouth_rx   = 0.15
            mouth_y    = -0.05

        mouth = (head_mat
                 @ translate(0, mouth_y, 0.19)
                 @ scale_mat(mouth_sx, 1.0, 1.0)
                 @ rot_x(mouth_rx))
        r.draw_vao(self.vao_mouth, mouth.astype('f4'), vp)

    def draw(self, vp):
        r  = self.renderer
        p  = self.position
        t  = self._t
        hb = self._hit_blend
        fa = 0.0 if self.facing > 0 else np.pi

        bob   = np.sin(t * 2.4) * 0.04
        sway  = np.sin(t * 1.2) * 0.025
        la_z  = np.sin(t * 2.4) * 0.12 + 0.20
        leg_speed = 5.0 if self.state == 'move' else 2.4
        leg_amp   = 0.35 if self.state == 'move' else 0.18
        leg   = np.sin(t * leg_speed) * leg_amp

        root = (translate(p[0], p[1] + bob, p[2])
                @ rot_y(fa + self._s_body_rot)
                @ rot_x(-0.07 + sway + self._s_body_lean))

        # Shadow
        r.draw_vao(self.vao_shadow, translate(p[0], 0.02, p[2]).astype('f4'), vp, alpha=0.28)

        # Body
        body = root @ translate(0, BODY_Y, 0)
        r.draw_vao(self.vao_body, body.astype('f4'), vp)

        # Head — tracks shuttlecock
        head = body @ translate(0, HEAD_DY, 0) @ rot_y(self._s_head_yaw) @ rot_x(self._s_head_pit)
        r.draw_vao(self.vao_head, head.astype('f4'), vp)

        # Face expressions
        self._draw_face(head, vp)

        # Left arm (idle)
        sh_l    = root @ translate(-SH_X, SH_Y, 0)
        uarm_l  = sh_l @ rot_z(la_z)
        elbow_l = uarm_l @ translate(0, -UARM_H/2, 0)
        larm_l  = elbow_l @ rot_z(-0.30) @ translate(0, -LARM_H/2, 0)
        r.draw_vao(self.vao_uarm, uarm_l.astype('f4'), vp)
        r.draw_vao(self.vao_larm, larm_l.astype('f4'), vp)

        # Right arm + racket (2-axis aim + hit-state)
        uarm_r, larm_r, hand = self._arm(
            root, SH_X, SH_Y,
            self._s_ra_yaw, self._s_ra_pitch, self._s_elbow
        )
        r.draw_vao(self.vao_uarm, uarm_r.astype('f4'), vp)
        r.draw_vao(self.vao_larm, larm_r.astype('f4'), vp)

        # Racket with lag (natural delay: racket trails on prepare, leads on hit)
        racket = hand @ rot_x(np.pi) @ rot_z(-0.12 + self._s_racket_lag)
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
