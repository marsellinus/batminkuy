import numpy as np
import random


def lerp(a, b, t):
    t = np.clip(t, 0.0, 1.0)
    return a + (b - a) * t


def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = np.clip(t, 0.0, 1.0)
    return 1 - (1 - t) ** 3


# Hit phase timing — longer recover for natural follow-through
PREPARE_END = 0.20
HIT_END     = 0.35
RECOVER_END = 0.85   # extended: arm follows through longer

# 3 swing types: (pitch_prepare, pitch_hit, pitch_recover, yaw_offset, body_rot_hit)
SWING_TYPES = {
    'forehand': dict(
        pitch_prepare=-0.35, pitch_hit=+0.65, pitch_recover=-0.20,
        yaw_offset=+0.15,  body_prepare=-0.20, body_hit=+0.35,
    ),
    'smash': dict(
        pitch_prepare=-0.70, pitch_hit=+0.90, pitch_recover=-0.30,
        yaw_offset=+0.05,  body_prepare=-0.15, body_hit=+0.25,
    ),
    'backhand': dict(
        pitch_prepare=+0.20, pitch_hit=-0.55, pitch_recover=+0.15,
        yaw_offset=-0.40,  body_prepare=+0.15, body_hit=-0.30,
    ),
}


class AnimationController:
    HIT_DIST     = 1.8
    HIT_DURATION = 0.70

    def __init__(self):
        self._hit_timer  = [0.0, 0.0]
        self._swing_type = ['forehand', 'forehand']
        self.cam_shake   = 0.0
        self.cam_zoom    = 0.0

    def update(self, dt, shuttlecock, player1, player2):
        players = [player1, player2]

        receiver_idx = 1 if shuttlecock._dir == 1 else 0
        receiver = players[receiver_idx]
        dist = float(np.linalg.norm(shuttlecock.position - receiver.position))

        if shuttlecock._waiting and dist < self.HIT_DIST and self._hit_timer[receiver_idx] <= 0.0:
            self._hit_timer[receiver_idx] = self.HIT_DURATION
            self._swing_type[receiver_idx] = random.choice(list(SWING_TYPES.keys()))
            receiver.hit_state  = 'prepare'
            receiver.swing_type = self._swing_type[receiver_idx]
            # face: angry/serious during hit sequence
            receiver.set_face_state('angry', duration=self.HIT_DURATION)
            self.cam_shake = 0.0

            landing_x = float(np.random.uniform(-1.5, 1.5))
            shuttlecock.launch(receiver.position[0], landing_x)

            other = players[1 - receiver_idx]
            other.set_target(landing_x, shuttlecock.landing_z() * 0.80)

        for i, player in enumerate(players):
            if self._hit_timer[i] > 0.0:
                self._hit_timer[i] -= dt
                raw_t = 1.0 - (self._hit_timer[i] / self.HIT_DURATION)

                if raw_t < PREPARE_END:
                    player.hit_state = 'prepare'
                    phase_t = raw_t / PREPARE_END
                    blend = smoothstep(phase_t) * 0.5
                elif raw_t < HIT_END:
                    player.hit_state = 'hit'
                    phase_t = (raw_t - PREPARE_END) / (HIT_END - PREPARE_END)
                    blend = 0.5 + smoothstep(phase_t) * 0.5
                    if phase_t < dt / (HIT_END - PREPARE_END) + 0.05:
                        self.cam_shake = 0.04
                        self.cam_zoom  = 3.0
                else:
                    player.hit_state = 'recover'
                    phase_t = (raw_t - HIT_END) / (RECOVER_END - HIT_END)
                    blend = smoothstep(1.0 - phase_t)

                player.set_hit_blend(blend)
            else:
                # just finished hit sequence → smile briefly
                if self._hit_timer[i] > -0.05:
                    player.set_face_state('smile', duration=1.5)
                player.set_hit_blend(0.0)
                player.hit_state  = 'idle'
                player.swing_type = 'forehand'
                if player.state == 'hit':
                    player.state = 'idle'

        self.cam_shake = max(0.0, self.cam_shake - dt * 1.2)
        self.cam_zoom  = max(0.0, self.cam_zoom  - dt * 8.0)

