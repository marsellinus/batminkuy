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
PREPARE_END = 0.28   # lebih lama agar prepare terasa penuh
HIT_END     = 0.42
RECOVER_END = 0.88

# 3 swing types with distinct body and arm parameters
SWING_TYPES = {
    'forehand': dict(
        pitch_prepare=-0.70, pitch_hit=+0.80, pitch_recover=-0.15,
        yaw_offset=+0.30,   body_prepare=-0.35, body_hit=+0.35,
        lean_prepare=-0.05, lean_hit=+0.15,
        elbow_prepare=0.45, elbow_hit=0.05,
        jump_prepare=0.0,   jump_hit=0.0,
    ),
    'smash': dict(
        # Smash pulls far back and swings fully downward.
        pitch_prepare=-1.40, pitch_hit=+1.30, pitch_recover=-0.40,
        yaw_offset=+0.15,   body_prepare=-0.50, body_hit=+0.60,
        lean_prepare=-0.25, lean_hit=+0.45,
        elbow_prepare=0.70, elbow_hit=0.00,
        jump_prepare=0.4,   jump_hit=0.6,
    ),
    'backhand': dict(
        # Backhand turns the body backwards (positive body rot), arm crosses body.
        pitch_prepare=+0.80, pitch_hit=-0.80, pitch_recover=+0.30,
        yaw_offset=-0.90,   body_prepare=+0.75, body_hit=-0.30,
        lean_prepare=+0.05, lean_hit=+0.15,
        elbow_prepare=0.85, elbow_hit=0.05,
        jump_prepare=0.0,   jump_hit=0.0,
    ),
}


class AnimationController:
    HIT_DIST     = 2.2
    HIT_DURATION = 0.70

    def __init__(self):
        self._hit_timer  = [0.0, 0.0]
        self._swing_type = ['forehand', 'forehand']
        self.cam_shake   = 0.0
        self.cam_zoom    = 0.0
        self.hit_event   = False

    def update(self, dt, shuttlecock, player1, player2):
        players = [player1, player2]

        receiver_idx = 1 if shuttlecock._dir == 1 else 0
        receiver = players[receiver_idx]
        diff_xz = shuttlecock.position[[0, 2]] - receiver.position[[0, 2]]
        dist = float(np.linalg.norm(diff_xz))

        if (shuttlecock._t > 0.60) and dist < self.HIT_DIST and self._hit_timer[receiver_idx] <= 0.0:
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
            other.set_target(landing_x, shuttlecock.landing_z())

        for i, player in enumerate(players):
            if self._hit_timer[i] > 0.0:
                self._hit_timer[i] -= dt
                raw_t = 1.0 - (self._hit_timer[i] / self.HIT_DURATION)

                if raw_t < PREPARE_END:
                    player.hit_state = 'prepare'
                    phase_t = raw_t / PREPARE_END
                    blend = smoothstep(phase_t)
                elif raw_t < HIT_END:
                    player.hit_state = 'hit'
                    phase_t = (raw_t - PREPARE_END) / (HIT_END - PREPARE_END)
                    blend = smoothstep(phase_t)
                    if phase_t < dt / (HIT_END - PREPARE_END) + 0.05:
                        self.cam_shake = 0.04
                        self.cam_zoom  = 3.0
                        self.hit_event = True
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

