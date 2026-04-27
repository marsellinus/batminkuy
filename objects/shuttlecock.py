import numpy as np
from renderer import (make_sphere, make_cone, make_circle_flat, combine_meshes,
                      translate, rot_x, rot_y, identity)

CORK_COLOR    = [0.95, 0.85, 0.70]
FEATHER_COLOR = [0.98, 0.98, 0.96]
TRAIL_COLOR   = [0.98, 0.98, 0.96]

P1_Z = -4.0
P2_Z =  4.0
ARC_H = 3.8              # Higher arc for more realistic badminton trajectory
TRAVEL_TIME = 1.2        # Slightly faster for more dynamic rally
TRAIL_LEN   = 12         # More trail segments for better visual


def _ease_inout(t):
    """Smooth start and end of each rally leg - more realistic arc."""
    # Slower at start (server/hitter contact), faster in middle, slow at end
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - (-2 * t * t + 2 * t)


def _build_mesh():
    v1, i1 = make_sphere(0.14, 7, 10, CORK_COLOR)
    v2, i2 = make_cone(0.26, 0.40, 12, FEATHER_COLOR)
    v2 = v2.copy(); v2[:, 1] -= 0.40
    return combine_meshes([(v1, i1), (v2, i2)])


def _build_trail_mesh():
    return make_circle_flat(0.08, 8, TRAIL_COLOR)


class Shuttlecock:
    def __init__(self, ctx, renderer):
        v, i = _build_mesh()
        self.vao, _     = renderer.make_vao(v, i)
        vt, it          = _build_trail_mesh()
        self.trail_vao, _ = renderer.make_vao(vt, it, alpha=True)
        self.renderer   = renderer
        self.position   = np.array([0.0, 1.5, P1_Z], dtype='f4')
        self.velocity   = np.array([0.0, 0.0, 0.0], dtype='f4')
        self._t         = 0.0
        self._dir       = 1
        self._waiting   = False
        self._spin      = 0.0
        self._trail     = []
        self.just_hit   = False
        self._start_x   = 0.0
        self._end_x     = 0.0
        self._prev_pos  = self.position.copy()

    def predict(self, t_ahead=0.25):
        """Predicted position t_ahead seconds from now (linear extrapolation)."""
        return (self.position + self.velocity * t_ahead).astype('f4')

    def set_leg_x(self, start_x, end_x):
        """Called by AnimationController when a new leg begins."""
        self._start_x = float(start_x)
        self._end_x   = float(end_x)

    def landing_z(self):
        return P2_Z if self._dir == 1 else P1_Z

    def update(self, dt):
        self.just_hit = False
        self._prev_pos = self.position.copy()

        if not self._waiting:
            self._t += dt / TRAVEL_TIME
            # Clamp near end — wait for player to hit
            if self._t >= 0.95:
                self._t = 0.95
                self._waiting = True

        t_ease = _ease_inout(self._t)
        z_start = P1_Z if self._dir == 1 else P2_Z
        z_end   = P2_Z if self._dir == 1 else P1_Z
        z = z_start + (z_end - z_start) * t_ease
        x = self._start_x + (self._end_x - self._start_x) * t_ease
        # More realistic parabolic arc (quadratic function for gravity-like drop)
        y = ARC_H * 4 * self._t * (1 - self._t) + 0.55
        self.position = np.array([x, y, z], dtype='f4')
        if dt > 0:
            self.velocity = (self.position - self._prev_pos) / dt
        # Faster spin for more visual interest
        self._spin += dt * 12.0

        self._trail.append(self.position.copy())
        if len(self._trail) > TRAIL_LEN:
            self._trail.pop(0)

    def launch(self, start_x, end_x):
        """Called by AnimationController when a player hits. Starts new leg."""
        self._dir    *= -1
        self._t       = 0.0
        self._waiting = False
        self.just_hit = True
        self.set_leg_x(start_x, end_x)

    def draw(self, vp):
        # Trail: fading spheres behind shuttle - more visible
        for k, pos in enumerate(self._trail):
            alpha = (k / TRAIL_LEN) * 0.5  # Increased opacity
            scale = 0.3 + 0.7 * (k / TRAIL_LEN)  # Smaller to larger
            m = translate(*pos) @ rot_y(self._spin * scale)
            self.renderer.draw_vao(self.trail_vao, m.astype('f4'), vp, alpha=alpha)

        # Main shuttlecock — tilt in direction of travel with more spin
        tilt = np.pi / 5 * self._dir
        model = translate(*self.position) @ rot_y(self._spin) @ rot_x(tilt)
        self.renderer.draw_vao(self.vao, model.astype('f4'), vp)
