import numpy as np
from renderer import combine_meshes, make_box, identity

# Konstanta Standar BWF
NET_W = 6.1            # Lebar net
POST_H = 1.55          # Tinggi tiang
NET_DEPTH = 0.76       # Tinggi/kedalaman jaring saja (bukan dari tanah)
NET_TOP_Y = 1.55       # Ketinggian pita atas net dari lantai
NET_BOTTOM_Y = NET_TOP_Y - NET_DEPTH # Ketinggian bagian bawah jaring dari lantai (~0.79m)

COLS, ROWS = 40, 10    # Menambah kerapatan agar lebih terlihat seperti jaring
POST_COLOR = [0.2, 0.2, 0.2]     # Tiang biasanya gelap/logam
NET_COLOR  = [0.5, 0.2, 0.2]     # Jaring biasanya berwarna cokelat tua/merah gelap
TAPE_WHITE = [0.95, 0.95, 0.95]  # Pita putih di atas net

def build_net_mesh():
    meshes = []
    
    cw = NET_W / COLS
    rh = NET_DEPTH / ROWS

    # 1. JARING VERTIKAL (Hanya dari NET_BOTTOM_Y ke NET_TOP_Y)
    for c in range(COLS + 1):
        x = -NET_W / 2 + c * cw
        # Tinggi box adalah NET_DEPTH, posisi Y adalah tengah-tengah antara bottom dan top
        v, i = make_box(0.01, NET_DEPTH, 0.01, NET_COLOR)
        v = v.copy()
        v[:, 0] += x
        v[:, 1] += (NET_BOTTOM_Y + NET_TOP_Y) / 2
        meshes.append((v, i))

    # 2. JARING HORIZONTAL (Hanya dari NET_BOTTOM_Y ke NET_TOP_Y)
    for r in range(ROWS + 1):
        y = NET_BOTTOM_Y + r * rh
        v, i = make_box(NET_W, 0.008, 0.008, NET_COLOR)
        v = v.copy()
        v[:, 1] += y
        meshes.append((v, i))

    # 3. PITA PUTIH ATAS (White Tape) - Ciri khas net badminton
    # Pita ini biasanya lebih tebal (75mm)
    v_tape, i_tape = make_box(NET_W, 0.075, 0.02, TAPE_WHITE)
    v_tape = v_tape.copy()
    v_tape[:, 1] += NET_TOP_Y - 0.0375 # Menempel di bagian paling atas
    meshes.append((v_tape, i_tape))

    # 4. TIANG (Dari lantai 0 sampai POST_H)
    for sx in [-NET_W / 2, NET_W / 2]:
        v, i = make_box(0.05, POST_H, 0.05, POST_COLOR)
        v = v.copy()
        v[:, 0] += sx
        v[:, 1] += POST_H / 2 # Berdiri di atas lantai (y=0)
        meshes.append((v, i))

    return combine_meshes(meshes)

class Net:
    def __init__(self, ctx, renderer):
        v, i = build_net_mesh()
        # Menggunakan alpha=True jika renderer mendukung transparansi
        self.vao, self.vbo = renderer.make_vao(v, i)
        self.renderer = renderer
        self.model = identity()

    def draw(self, vp):
        # Menggambar dengan sedikit transparansi agar jaring terlihat tembus pandang
        self.renderer.draw_vao(self.vao, self.model, vp)