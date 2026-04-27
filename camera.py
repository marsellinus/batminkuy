import numpy as np
import pygame

MODES = ['free', 'follow', 'side']


def perspective(fov_deg, aspect, near, far):
    f = 1.0 / np.tan(np.radians(fov_deg) / 2.0)
    m = np.zeros((4, 4), dtype='f4')
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2.0 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m


def look_at(eye, target, up=None):
    if up is None:
        up = np.array([0.0, 1.0, 0.0], dtype='f4')
    eye    = np.array(eye,    dtype='f4')
    target = np.array(target, dtype='f4')
    f = target - eye;  f /= np.linalg.norm(f)
    r = np.cross(f, up).astype('f4');  r /= np.linalg.norm(r)
    u = np.cross(r, f).astype('f4')
    m = np.eye(4, dtype='f4')
    m[0, :3] = r;  m[1, :3] = u;  m[2, :3] = -f
    m[0, 3] = -np.dot(r, eye)
    m[1, 3] = -np.dot(u, eye)
    m[2, 3] =  np.dot(f, eye)
    return m


class Camera:
    SPEED       = 8.0
    SENSITIVITY = 0.15

    def __init__(self, width, height):
        self.proj      = perspective(45.0, width / height, 0.1, 100.0)
        self.mode_idx  = 0
        # free cam
        self.pos       = np.array([0.0, 3.0, 8.0], dtype='f4')
        self.yaw       = -90.0
        self.pitch     = -15.0
        # smooth pos (lerped)
        self._smooth_pos    = self.pos.copy()
        self._smooth_target = np.array([0.0, 1.0, 0.0], dtype='f4')
        # cinematic orbit
        self._cin_t    = 0.0
        # side-view oscillation
        self._side_t   = 0.0

    @property
    def mode(self):
        return MODES[self.mode_idx]

    def cycle_mode(self):
        self.mode_idx = (self.mode_idx + 1) % len(MODES)
        # Snap immediately to avoid blank frames during transition
        if self.mode == 'follow':
            self._smooth_pos    = self.pos.copy()
            self._smooth_target = np.array([0.0, 1.0, 0.0], dtype='f4')
        elif self.mode == 'side':
            self._smooth_pos    = np.array([10.5, 4.5, 0.0], dtype='f4')
            self._smooth_target = np.array([0.0,  1.5, 0.0], dtype='f4')
        print(f"[Camera] mode → {self.mode}")

    def _forward(self):
        yr, pr = np.radians(self.yaw), np.radians(self.pitch)
        return np.array([np.cos(pr)*np.cos(yr), np.sin(pr), np.cos(pr)*np.sin(yr)], dtype='f4')

    def update(self, dt, keys, mx, my, shuttle_pos, shake=0.0):
        lerp_speed = 6.0 * dt

        if self.mode == 'free':
            self.yaw  += mx * self.SENSITIVITY
            self.pitch = np.clip(self.pitch - my * self.SENSITIVITY, -89.0, 89.0)
            fwd   = self._forward()
            right = np.cross(fwd, [0,1,0]).astype('f4');  right /= np.linalg.norm(right)
            spd   = self.SPEED * dt
            if keys[pygame.K_w]: self.pos += fwd   * spd
            if keys[pygame.K_s]: self.pos -= fwd   * spd
            if keys[pygame.K_a]: self.pos -= right * spd
            if keys[pygame.K_d]: self.pos += right * spd
            if keys[pygame.K_q]: self.pos[1] -= spd
            if keys[pygame.K_e]: self.pos[1] += spd
            self._smooth_pos    = self.pos.copy()
            self._smooth_target = self.pos + self._forward()

        elif self.mode == 'follow':
            # camera trails behind shuttlecock
            want_pos = shuttle_pos + np.array([0.0, 2.0, 4.5], dtype='f4')
            self._smooth_pos    += (want_pos - self._smooth_pos) * lerp_speed
            self._smooth_target += (shuttle_pos - self._smooth_target) * lerp_speed

        elif self.mode == 'side':
            # Stands extend to X≈9.2, wall at X=11 — camera at X=10.5
            self._smooth_pos    = np.array([10.5, 4.5, 0.0], dtype='f4')
            self._smooth_target = np.array([0.0,  1.5, 0.0], dtype='f4')

        # camera shake
        if shake > 0.001:
            self._smooth_pos += np.array([
                np.random.uniform(-shake, shake),
                np.random.uniform(-shake * 0.5, shake * 0.5),
                0.0,
            ], dtype='f4')

    def get_view_projection(self):
        view = look_at(self._smooth_pos, self._smooth_target)
        return self.proj @ view

    def debug_print(self):
        p = self._smooth_pos
        print(f"[Camera] pos=({p[0]:.2f},{p[1]:.2f},{p[2]:.2f})  yaw={self.yaw:.1f}  mode={self.mode}")
