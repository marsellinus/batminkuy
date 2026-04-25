import numpy as np
from renderer import combine_meshes, make_box, identity

NET_W = 6.1
NET_H = 1.55
COLS, ROWS = 20, 8
POST_COLOR = [0.8, 0.8, 0.8]
NET_COLOR  = [0.9, 0.9, 0.9]


def build_net_mesh():
    meshes = []
    cw = NET_W / COLS
    rh = NET_H / ROWS
    # vertical strands
    for c in range(COLS + 1):
        x = -NET_W / 2 + c * cw
        v, i = make_box(0.02, NET_H, 0.02, NET_COLOR)
        v = v.copy(); v[:, 0] += x; v[:, 1] += NET_H / 2
        meshes.append((v, i))
    # horizontal strands
    for r in range(ROWS + 1):
        y = r * rh
        v, i = make_box(NET_W, 0.02, 0.02, NET_COLOR)
        v = v.copy(); v[:, 1] += y
        meshes.append((v, i))
    # posts
    for sx in [-NET_W / 2, NET_W / 2]:
        v, i = make_box(0.06, NET_H + 0.1, 0.06, POST_COLOR)
        v = v.copy(); v[:, 0] += sx; v[:, 1] += NET_H / 2
        meshes.append((v, i))
    return combine_meshes(meshes)


class Net:
    def __init__(self, ctx, renderer):
        v, i = build_net_mesh()
        self.vao, self.vbo = renderer.make_vao(v, i, alpha=True)
        self.renderer = renderer
        self.model = identity()

    def draw(self, vp):
        self.renderer.draw_vao(self.vao, self.model, vp, alpha=0.75)
