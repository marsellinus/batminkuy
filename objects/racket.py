import numpy as np
from renderer import make_box, combine_meshes

HANDLE_COLOR = [0.55, 0.35, 0.15]
HEAD_COLOR   = [0.82, 0.82, 0.82]
STRING_COLOR = [0.96, 0.96, 0.96]

# Racket is built along the +Y axis.
# Y=0  → grip center (where the hand holds it)
# Y=-0.275 → butt of handle
# Y=+0.275 → top of handle / start of shaft
# Y=+0.55  → base of head frame


def build_racket_mesh():
    meshes = []

    # ── Handle (centered at Y=0) ──────────────────────────────────────────────
    v, i = make_box(0.055, 0.55, 0.055, HANDLE_COLOR)
    # already centered at origin — no offset needed
    meshes.append((v, i))

    # ── Shaft ─────────────────────────────────────────────────────────────────
    v, i = make_box(0.035, 0.22, 0.035, HANDLE_COLOR)
    v = v.copy(); v[:, 1] += 0.275 + 0.11   # sits above handle top
    meshes.append((v, i))

    # ── Oval head frame ───────────────────────────────────────────────────────
    segs   = 16
    rx, ry = 0.20, 0.26
    head_y = 0.275 + 0.22 + ry          # center of oval

    for k in range(segs):
        a0 = 2 * np.pi * k / segs
        a1 = 2 * np.pi * (k + 1) / segs
        x0, y0 = np.cos(a0) * rx, np.sin(a0) * ry
        x1, y1 = np.cos(a1) * rx, np.sin(a1) * ry
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        length = np.hypot(x1 - x0, y1 - y0)
        angle  = np.arctan2(y1 - y0, x1 - x0)
        v, i   = make_box(length + 0.01, 0.038, 0.038, HEAD_COLOR)
        c, s   = np.cos(angle), np.sin(angle)
        pos    = v[:, :3].copy()
        pos[:, 0], pos[:, 1] = (
            pos[:, 0] * c - pos[:, 1] * s + cx,
            pos[:, 0] * s + pos[:, 1] * c + cy + head_y,
        )
        v = v.copy(); v[:, :3] = pos
        meshes.append((v, i))

    # ── Strings ───────────────────────────────────────────────────────────────
    for k in range(-3, 4):
        frac = k / 4.0
        sw = rx * 2 * np.sqrt(max(0.0, 1 - frac ** 2))
        v, i = make_box(sw, 0.008, 0.008, STRING_COLOR)
        v = v.copy(); v[:, 1] += head_y + frac * ry
        meshes.append((v, i))

        sh = ry * 2 * np.sqrt(max(0.0, 1 - frac ** 2))
        v, i = make_box(0.008, sh, 0.008, STRING_COLOR)
        v = v.copy(); v[:, 0] += frac * rx; v[:, 1] += head_y
        meshes.append((v, i))

    return combine_meshes(meshes)
