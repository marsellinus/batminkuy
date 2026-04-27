import numpy as np


def lerp(a, b, t):
    t = np.clip(t, 0.0, 1.0)
    return a + (b - a) * t


def smoothstep(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = np.clip(t, 0.0, 1.0)
    return 1 - (1 - t) ** 3


class AnimationController:
    HIT_DIST     = 1.8        # Larger hit zone for more natural arm extension
    HIT_DURATION = 0.45       # Slightly longer swing for more realistic motion

    def __init__(self):
        self._hit_timer = [0.0, 0.0]
        self.cam_shake  = 0.0

    def update(self, dt, shuttlecock, player1, player2):
        players = [player1, player2]

        # ── Hit trigger (only for current receiver) ───────────────────────────
        receiver_idx = 1 if shuttlecock._dir == 1 else 0
        receiver = players[receiver_idx]
        dist = float(np.linalg.norm(shuttlecock.position - receiver.position))

        if shuttlecock._waiting and dist < self.HIT_DIST and self._hit_timer[receiver_idx] <= 0.0:
            self._hit_timer[receiver_idx] = self.HIT_DURATION
            receiver.state = 'hit'
            self.cam_shake = 0.035  # Slightly more shake on hit

            landing_x = float(np.random.uniform(-1.5, 1.5))
            shuttlecock.launch(receiver.position[0], landing_x)

            other = players[1 - receiver_idx]
            other.set_target(landing_x, shuttlecock.landing_z() * 0.80)

        # ── Update blend timers for BOTH players (always) ─────────────────────
        for i, player in enumerate(players):
            if self._hit_timer[i] > 0.0:
                self._hit_timer[i] -= dt
                raw_t = 1.0 - (self._hit_timer[i] / self.HIT_DURATION)
                blend = smoothstep(raw_t / 0.35) if raw_t < 0.35 \
                        else smoothstep(1.0 - (raw_t - 0.35) / 0.65)
                player.set_hit_blend(blend)
                player.state = 'hit'
            else:
                player.set_hit_blend(0.0)
                if player.state == 'hit':
                    player.state = 'idle'

        self.cam_shake = max(0.0, self.cam_shake - dt * 0.8)
