import moderngl
import numpy as np

# Row-major matrices; transposed (.T) before GPU upload.

VERT_SHADER = """
#version 330
in vec3 in_position;
in vec3 in_normal;
in vec3 in_color;

uniform mat4 model;
uniform mat4 vp;
uniform vec3 light_dir;
uniform vec3 light_dir2;
uniform vec3 light_dir3;
uniform float ambient;

out vec3 v_color;

void main() {
    vec4 world_pos = model * vec4(in_position, 1.0);
    gl_Position = vp * world_pos;

    mat3 norm_mat = mat3(transpose(inverse(model)));
    vec3 N = normalize(norm_mat * in_normal);

    float diff1 = max(dot(N, normalize(light_dir)),  0.0);        // key: top-front
    float diff2 = max(dot(N, normalize(light_dir2)), 0.0) * 0.30; // fill: back-cool
    float diff3 = max(dot(N, normalize(light_dir3)), 0.0) * 0.45; // side: from +X

    float light = ambient + diff1 * (1.0 - ambient) + diff2 + diff3;
    v_color = in_color * clamp(light, 0.0, 1.0);
}
"""

FRAG_SHADER = """
#version 330
in vec3 v_color;
out vec4 fragColor;
void main() { fragColor = vec4(v_color, 1.0); }
"""

FRAG_ALPHA_SHADER = """
#version 330
in vec3 v_color;
uniform float alpha;
out vec4 fragColor;
void main() { fragColor = vec4(v_color, alpha); }
"""

VERT_UNLIT = """
#version 330
in vec3 in_position;
in vec3 in_color;
uniform mat4 vp;
out vec3 v_color;
void main() {
    gl_Position = vp * vec4(in_position, 1.0);
    v_color = in_color;
}
"""
FRAG_UNLIT = """
#version 330
in vec3 v_color;
out vec4 fragColor;
void main() { fragColor = vec4(v_color, 1.0); }
"""


def _upload(prog, name, mat):
    prog[name].write(mat.T.astype('f4').tobytes())


class Renderer:
    LIGHT_DIR  = np.array([0.6,  1.0,  0.4],  dtype='f4')   # key: top-front
    LIGHT_DIR2 = np.array([-0.4, 0.3, -0.6],  dtype='f4')   # fill: back-cool
    LIGHT_DIR3 = np.array([1.0,  0.5,  0.0],  dtype='f4')   # side: from +X
    AMBIENT    = 0.30

    def __init__(self, ctx: moderngl.Context):
        self.ctx        = ctx
        self.unlit_mode = False   # toggle with L key
        self.prog       = ctx.program(vertex_shader=VERT_SHADER, fragment_shader=FRAG_SHADER)
        self.prog_alpha = ctx.program(vertex_shader=VERT_SHADER, fragment_shader=FRAG_ALPHA_SHADER)
        self.prog_unlit = ctx.program(vertex_shader=VERT_UNLIT,  fragment_shader=FRAG_UNLIT)
        self._build_debug(ctx)

    def make_vao(self, vertices: np.ndarray, indices: np.ndarray, alpha=False):
        prog = self.prog_alpha if alpha else self.prog
        vbo  = self.ctx.buffer(vertices.astype('f4').tobytes())
        ibo  = self.ctx.buffer(indices.astype('i4').tobytes())
        vao  = self.ctx.vertex_array(
            prog,
            [(vbo, '3f 3f 3f', 'in_position', 'in_normal', 'in_color')],
            ibo,
        )
        return vao, vbo

    def draw_vao(self, vao, model_mat: np.ndarray, vp_mat: np.ndarray, alpha=None, unlit=False):
        prog = self.prog_alpha if alpha is not None else self.prog
        _upload(prog, 'vp',    vp_mat)
        _upload(prog, 'model', model_mat)
        prog['light_dir'].write(self.LIGHT_DIR.tobytes())
        prog['light_dir2'].write(self.LIGHT_DIR2.tobytes())
        prog['light_dir3'].write(self.LIGHT_DIR3.tobytes())
        prog['ambient'].value = 1.0 if (unlit or self.unlit_mode) else self.AMBIENT
        if alpha is not None:
            prog['alpha'].value = alpha
        vao.render()

    def _build_debug(self, ctx):
        lines = [
            0,0,0, 1,0,0,  3,0,0, 1,0,0,
            0,0,0, 0,1,0,  0,3,0, 0,1,0,
            0,0,0, 0,0,1,  0,0,3, 0,0,1,
        ]
        g = [0.25, 0.25, 0.25]
        for i in range(-8, 9):
            lines += [i,0,-8]+g+[i,0,8]+g
            lines += [-8,0,i]+g+[8,0,i]+g
        vbo = ctx.buffer(np.array(lines, dtype='f4').tobytes())
        self._debug_vao = ctx.vertex_array(
            self.prog_unlit,
            [(vbo, '3f 3f', 'in_position', 'in_color')],
        )

    def draw_debug(self, vp_mat: np.ndarray):
        _upload(self.prog_unlit, 'vp', vp_mat)
        self._debug_vao.render(moderngl.LINES)


# ── Matrix helpers (ROW-MAJOR) ────────────────────────────────────────────────

def identity():
    return np.eye(4, dtype='f4')

def translate(x, y, z):
    m = np.eye(4, dtype='f4')
    m[0,3]=x; m[1,3]=y; m[2,3]=z
    return m

def scale_mat(sx, sy, sz):
    m = np.eye(4, dtype='f4')
    m[0,0]=sx; m[1,1]=sy; m[2,2]=sz
    return m

def rot_x(a):
    c,s = float(np.cos(a)), float(np.sin(a))
    m = np.eye(4, dtype='f4')
    m[1,1]=c; m[1,2]=-s; m[2,1]=s; m[2,2]=c
    return m

def rot_y(a):
    c,s = float(np.cos(a)), float(np.sin(a))
    m = np.eye(4, dtype='f4')
    m[0,0]=c; m[0,2]=s; m[2,0]=-s; m[2,2]=c
    return m

def rot_z(a):
    c,s = float(np.cos(a)), float(np.sin(a))
    m = np.eye(4, dtype='f4')
    m[0,0]=c; m[0,1]=-s; m[1,0]=s; m[1,1]=c
    return m


# ── Geometry helpers ──────────────────────────────────────────────────────────

def make_box(w, h, d, color):
    hw,hh,hd = w/2,h/2,d/2
    faces = [
        ([ hw,-hh,-hd],[ hw, hh,-hd],[ hw, hh, hd],[ hw,-hh, hd],[1,0,0]),
        ([-hw,-hh, hd],[-hw, hh, hd],[-hw, hh,-hd],[-hw,-hh,-hd],[-1,0,0]),
        ([-hw, hh,-hd],[-hw, hh, hd],[ hw, hh, hd],[ hw, hh,-hd],[0,1,0]),
        ([-hw,-hh, hd],[-hw,-hh,-hd],[ hw,-hh,-hd],[ hw,-hh, hd],[0,-1,0]),
        ([-hw,-hh, hd],[ hw,-hh, hd],[ hw, hh, hd],[-hw, hh, hd],[0,0,1]),
        ([ hw,-hh,-hd],[-hw,-hh,-hd],[-hw, hh,-hd],[ hw, hh,-hd],[0,0,-1]),
    ]
    verts,idxs,base = [],[],0
    for v0,v1,v2,v3,n in faces:
        for v in [v0,v1,v2,v3]: verts += v+n+list(color)
        idxs += [base,base+1,base+2,base,base+2,base+3]; base+=4
    return np.array(verts,'f4').reshape(-1,9), np.array(idxs,'i4')

def make_cylinder(radius, height, segments, color):
    verts,idxs = [],[]
    hh = height/2
    for i in range(segments):
        a0=2*np.pi*i/segments; a1=2*np.pi*(i+1)/segments
        x0,z0=np.cos(a0)*radius,np.sin(a0)*radius
        x1,z1=np.cos(a1)*radius,np.sin(a1)*radius
        n0=[np.cos(a0),0,np.sin(a0)]; n1=[np.cos(a1),0,np.sin(a1)]
        b=len(verts)//9
        for (x,z,n,y) in [(x0,z0,n0,-hh),(x1,z1,n1,-hh),(x1,z1,n1,hh),(x0,z0,n0,hh)]:
            verts+=[x,y,z]+n+list(color)
        idxs+=[b,b+1,b+2,b,b+2,b+3]
        b2=len(verts)//9
        verts+=[0,hh,0,0,1,0]+list(color)+[x0,hh,z0,0,1,0]+list(color)+[x1,hh,z1,0,1,0]+list(color)
        idxs+=[b2,b2+1,b2+2]
        b3=len(verts)//9
        verts+=[0,-hh,0,0,-1,0]+list(color)+[x1,-hh,z1,0,-1,0]+list(color)+[x0,-hh,z0,0,-1,0]+list(color)
        idxs+=[b3,b3+1,b3+2]
    return np.array(verts,'f4').reshape(-1,9), np.array(idxs,'i4')

def make_sphere(radius, stacks, slices, color):
    verts,idxs = [],[]
    for i in range(stacks):
        phi0=np.pi*i/stacks-np.pi/2; phi1=np.pi*(i+1)/stacks-np.pi/2
        for j in range(slices):
            th0=2*np.pi*j/slices; th1=2*np.pi*(j+1)/slices
            pts=[]
            for phi,th in [(phi0,th0),(phi0,th1),(phi1,th1),(phi1,th0)]:
                x=np.cos(phi)*np.cos(th); y=np.sin(phi); z=np.cos(phi)*np.sin(th)
                pts.append([x*radius,y*radius,z*radius,x,y,z]+list(color))
            b=len(verts)//9
            for p in pts: verts+=p
            idxs+=[b,b+1,b+2,b,b+2,b+3]
    return np.array(verts,'f4').reshape(-1,9), np.array(idxs,'i4')

def make_cone(radius, height, segments, color):
    verts,idxs = [],[]
    for i in range(segments):
        a0=2*np.pi*i/segments; a1=2*np.pi*(i+1)/segments
        x0,z0=np.cos(a0)*radius,np.sin(a0)*radius
        x1,z1=np.cos(a1)*radius,np.sin(a1)*radius
        n=[np.cos((a0+a1)/2),radius/height,np.sin((a0+a1)/2)]
        b=len(verts)//9
        verts+=[0,height,0]+n+list(color)+[x0,0,z0]+n+list(color)+[x1,0,z1]+n+list(color)
        idxs+=[b,b+1,b+2]
        b2=len(verts)//9
        verts+=[0,0,0,0,-1,0]+list(color)+[x1,0,z1,0,-1,0]+list(color)+[x0,0,z0,0,-1,0]+list(color)
        idxs+=[b2,b2+1,b2+2]
    return np.array(verts,'f4').reshape(-1,9), np.array(idxs,'i4')

def make_circle_flat(radius, segments, color):
    verts,idxs = [],[]
    for i in range(segments):
        a0=2*np.pi*i/segments; a1=2*np.pi*(i+1)/segments
        b=len(verts)//9
        verts+=[0,0,0,0,1,0]+list(color)
        verts+=[np.cos(a0)*radius,0,np.sin(a0)*radius,0,1,0]+list(color)
        verts+=[np.cos(a1)*radius,0,np.sin(a1)*radius,0,1,0]+list(color)
        idxs+=[b,b+1,b+2]
    return np.array(verts,'f4').reshape(-1,9), np.array(idxs,'i4')

def combine_meshes(meshes):
    all_v,all_i,offset = [],[],0
    for v,i in meshes:
        all_v.append(v); all_i.append(i+offset); offset+=len(v)
    return np.concatenate(all_v), np.concatenate(all_i)
