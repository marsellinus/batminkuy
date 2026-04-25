import numpy as np
from renderer import make_box, combine_meshes, translate, identity

# Court: 13.4m long, 6.1m wide (halved for simplicity → scale 1u=1m)
CW, CL = 6.1, 13.4
LINE_W = 0.05
LINE_H = 0.01

GREEN  = [0.18, 0.55, 0.22]
WHITE  = [0.95, 0.95, 0.95]


def _floor():
    v, i = make_box(CW, 0.05, CL, GREEN)
    return v, i


def _line(x, y, z, w, d):
    v, i = make_box(w, LINE_H, d, WHITE)
    # offset verts
    v = v.copy(); v[:, 0] += x; v[:, 1] += y; v[:, 2] += z
    return v, i


def build_court_mesh():
    meshes = [_floor()]
    y = 0.03
    # boundary lines
    meshes.append(_line(0, y, 0, CW, LINE_W))           # center line z
    meshes.append(_line(0, y, CL/2, CW, LINE_W))        # back line +z
    meshes.append(_line(0, y, -CL/2, CW, LINE_W))       # back line -z
    meshes.append(_line(-CW/2, y, 0, LINE_W, CL))       # side line -x
    meshes.append(_line( CW/2, y, 0, LINE_W, CL))       # side line +x
    # service lines (1.98m from net)
    meshes.append(_line(0, y,  1.98, CW, LINE_W))
    meshes.append(_line(0, y, -1.98, CW, LINE_W))
    # center service line
    meshes.append(_line(0, y, 0, LINE_W, CL * 0.5))
    return combine_meshes(meshes)


class Court:
    def __init__(self, ctx, renderer):
        v, i = build_court_mesh()
        self.vao, self.vbo = renderer.make_vao(v, i)
        self.renderer = renderer
        self.model = identity()

    def draw(self, vp):
        self.renderer.draw_vao(self.vao, self.model, vp)
