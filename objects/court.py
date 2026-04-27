import numpy as np
from renderer import make_box, combine_meshes, identity

# Konstanta Standar BWF
CL = 13.4               
CW_DOUBLES = 6.1        
CW_SINGLES = 5.18       
SHORT_SERVICE_DIST = 1.98 
LONG_SERVICE_DBL_DIST = 0.76 

HALF_CL = CL / 2        
LINE_W = 0.04           
LINE_H = 0.005          

# Colors
COURT_GREEN = [0.12, 0.45, 0.30]
OUT_GREEN   = [0.10, 0.35, 0.25]
WHITE_LINE  = [0.95, 0.95, 0.95]
POST_COLOR  = [0.15, 0.15, 0.15]
NET_STRAND_COLOR = [0.3, 0.1, 0.1] # Warna benang jaring (cokelat tua)
NET_TAPE_COLOR   = [0.95, 0.95, 0.95] # Pita putih

def _line(x, y, z, w, h, d, color):
    """Helper untuk membuat box dengan posisi offset"""
    v, i = make_box(w, h, d, color)
    v = v.copy()
    v[:, 0] += x; v[:, 1] += y; v[:, 2] += z
    return v, i

def build_court_mesh():
    meshes = []
    
    # 1. LANTAI & GARIS (Sama seperti sebelumnya)
    meshes.append(make_box(CW_DOUBLES + 1.0, 0.02, CL + 1.0, OUT_GREEN))
    v_floor, i_floor = make_box(CW_DOUBLES, 0.025, CL, COURT_GREEN)
    v_floor[:, 1] += 0.005
    meshes.append((v_floor, i_floor))

    y_l = 0.03 
    # Garis-garis lapangan
    meshes.append(_line(0, y_l,  HALF_CL, CW_DOUBLES, LINE_H, LINE_W, WHITE_LINE))
    meshes.append(_line(0, y_l, -HALF_CL, CW_DOUBLES, LINE_H, LINE_W, WHITE_LINE))
    meshes.append(_line(0, y_l,  HALF_CL - LONG_SERVICE_DBL_DIST, CW_DOUBLES, LINE_H, LINE_W, WHITE_LINE))
    meshes.append(_line(0, y_l, -(HALF_CL - LONG_SERVICE_DBL_DIST), CW_DOUBLES, LINE_H, LINE_W, WHITE_LINE))
    meshes.append(_line(0, y_l,  SHORT_SERVICE_DIST, CW_DOUBLES, LINE_H, LINE_W, WHITE_LINE))
    meshes.append(_line(0, y_l, -SHORT_SERVICE_DIST, CW_DOUBLES, LINE_H, LINE_W, WHITE_LINE))
    meshes.append(_line(0, y_l, 0, CW_DOUBLES, LINE_H, LINE_W, WHITE_LINE))
    # Garis samping & tengah
    meshes.append(_line( CW_DOUBLES/2, y_l, 0, LINE_W, LINE_H, CL, WHITE_LINE))
    meshes.append(_line(-CW_DOUBLES/2, y_l, 0, LINE_W, LINE_H, CL, WHITE_LINE))
    meshes.append(_line( CW_SINGLES/2, y_l, 0, LINE_W, LINE_H, CL, WHITE_LINE))
    meshes.append(_line(-CW_SINGLES/2, y_l, 0, LINE_W, LINE_H, CL, WHITE_LINE))
    dz = HALF_CL - SHORT_SERVICE_DIST
    pz = SHORT_SERVICE_DIST + dz/2
    meshes.append(_line(0, y_l,  pz, LINE_W, LINE_H, dz, WHITE_LINE))
    meshes.append(_line(0, y_l, -pz, LINE_W, LINE_H, dz, WHITE_LINE))

    # 2. TIANG
    post_h = 1.55
    for sx in [-CW_DOUBLES/2, CW_DOUBLES/2]:
        meshes.append(_line(sx, post_h/2, 0, 0.04, post_h, 0.04, POST_COLOR))

    # 3. NET (STRUKTUR JARING TRANSPARAN)
    net_w = CW_DOUBLES
    net_h = 0.76
    top_y = 1.55
    bottom_y = top_y - net_h
    
    # A. PITA PUTIH ATAS (Solid)
    tape_h = 0.075
    meshes.append(_line(0, top_y - tape_h/2, 0, net_w, tape_h, 0.02, NET_TAPE_COLOR))
    
    # B. PITA SAMPING (Solid)
    side_w = 0.05
    for sx in [-net_w/2 + side_w/2, net_w/2 - side_w/2]:
        meshes.append(_line(sx, bottom_y + net_h/2, 0, side_w, net_h, 0.015, NET_TAPE_COLOR))

    # C. JARING-JARING (GRID)
    # Membuat jaring dengan garis-garis tipis agar terlihat transparan
    num_cols = 40 # Jumlah lubang horizontal
    num_rows = 12 # Jumlah lubang vertikal
    strand_t = 0.005 # Ketebalan benang jaring
    
    # Benang Horizontal
    row_spacing = net_h / num_rows
    for r in range(num_rows + 1):
        curr_y = bottom_y + r * row_spacing
        # Jangan buat garis jika sudah ada pita putih
        if curr_y < top_y - 0.02:
            meshes.append(_line(0, curr_y, 0, net_w, strand_t, strand_t, NET_STRAND_COLOR))
            
    # Benang Vertikal
    col_spacing = net_w / num_cols
    for c in range(num_cols + 1):
        curr_x = -net_w/2 + c * col_spacing
        meshes.append(_line(curr_x, bottom_y + net_h/2, 0, strand_t, net_h, strand_t, NET_STRAND_COLOR))

    return combine_meshes(meshes)

class Court:
    def __init__(self, ctx, renderer):
        v, i = build_court_mesh()
        self.vao, self.vbo = renderer.make_vao(v, i)
        self.renderer = renderer
        self.model = identity()

    def draw(self, vp):
        self.renderer.draw_vao(self.vao, self.model, vp)