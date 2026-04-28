# 🏸 Badminton 3D — Visualisasi Interaktif Berbasis ModernGL
> Simulasi visual pertandingan bulu tangkis 3D menggunakan teknik *real-time rendering*, *hierarchical animation*, dan *procedural geometry* dengan Python dan ModernGL.

---

## 📖 Deskripsi

Project ini merupakan simulasi visual pertandingan bulu tangkis dalam ruang tiga dimensi yang dibangun sepenuhnya menggunakan Python. Tujuan utamanya adalah mengeksplorasi konsep grafika komputer modern, mulai dari pembuatan geometri prosedural, sistem animasi hierarkis, hingga pencahayaan berbasis shader.

Sistem ini menampilkan dua karakter pemain *low-poly* yang saling beradu dalam sebuah arena lengkap dengan tribun bertingkat, penonton animasi, papan sponsor, bendera negara, dan berbagai props lapangan — semuanya dirender secara *real-time*. Project ini adalah **simulasi visual**, bukan game penuh; tidak ada sistem input pemain maupun logika skor yang kompleks.

---

## ✨ Fitur Utama

### 🧍 Karakter & Animasi
- **Karakter pemain low-poly** dengan animasi tubuh hierarkis (kepala, bahu, lengan, kaki)
- **Sistem ekspresi wajah** — `neutral`, `smile`, `angry` berubah dinamis sesuai fase pukulan
- **Animasi tangan berbasis aiming** — lengan kanan mengarah ke shuttlecock via kalkulasi *yaw* & *pitch* real-time
- **Tiga jenis pukulan** — *forehand*, *smash*, *backhand* dengan offset animasi berbeda
- **Follow-through raket** — delay alami (tertinggal saat prepare, memimpin saat hit)
- **Body lean** — badan condong sesuai fase pukulan

### 🏸 Gameplay & Fisika
- **Shuttlecock dengan lintasan parabola** — gerakan realistis dengan gravitasi dan prediksi posisi
- **Rally otomatis** — state machine mengatur giliran pukulan dan pergerakan pemain

### 🏟️ Arena & Environment
- **Lapangan badminton** dengan garis lengkap dan net
- **Tribun 8 tingkat** di kedua sisi lapangan, bertingkat dengan slab beton dan bench
- **Arena luas** — lantai `36×32`, dinding tinggi, lampu sorot di sudut lapangan
- **Scoreboard digital** di kedua sisi net
- **Papan sponsor** YONEX & LING di pinggir lapangan

### 👥 Penonton & Aksesoris
- **Penonton animasi** — tepuk tangan, lompat saat hit, kepala bergerak acak
- **Ekspresi wajah penonton** — mata, mulut, senyum
- **Item random** — sebagian penonton pegang tongkat bendera atau cheerstick
- **Tongkat bendera** berkibar saat hit; cheerstick dipukul-pukul saat hit

### 🏳️ Dekorasi
- **Bendera negara** (INA, MAS, CHN, JPN, KOR) ditempel di dinding belakang arena dengan wave effect
- **Wasit** di kursi tinggi dengan ekspresi wajah dan animasi kepala
- **4 Hakim garis** dengan ekspresi fokus saat hit

### 🎥 Kamera
- **4 mode kamera** — *free* (WASD+mouse), *follow* (mengikuti shuttlecock), *side view*, *broadcast* (sudut TV)
- **Camera shake & zoom** saat terjadi pukulan
- **Broadcast mode** — kamera bergerak mengikuti Z shuttlecock seperti siaran langsung

### 💡 Pencahayaan
- **3 sumber cahaya** — *key light*, *fill light*, *side light* + ambient
- **Toggle unlit mode** untuk debug

---

## 🛠️ Teknologi yang Digunakan

| Teknologi | Fungsi |
|-----------|--------|
| **ModernGL** | Antarmuka OpenGL modern untuk rendering 3D, manajemen shader GLSL, VAO/VBO |
| **Pygame** | Pembuatan window, event loop, input keyboard & mouse, kontrol waktu (clock) |
| **NumPy** | Operasi matriks transformasi (translate, rotate, scale), kalkulasi geometri dan fisika |

---

## 💡 Konsep dan Teknik yang Digunakan

- **Procedural Geometry** — seluruh objek dibangun dari vertex dan index secara programatik tanpa aset eksternal
- **Hierarchical Transformation** — `root → body → shoulder → upper arm → lower arm → racket`
- **GLSL Vertex Shader** — pencahayaan *diffuse multi-light* + ambient di vertex shader
- **Smooth Interpolation** — semua parameter animasi diperhalus dengan *lerp* berbasis delta time
- **State Machine Animasi** — `idle → prepare → hit → recover → idle`
- **Parabolic Projectile** — shuttlecock menggunakan persamaan gerak parabola dengan prediksi posisi
- **Sinusoidal Animation** — gerakan idle, tepuk tangan, waving flag menggunakan `sin(t)`
- **Camera Shake** — offset posisi acak yang meluruh terhadap waktu
- **Alpha Blending** — bayangan pemain dengan transparansi OpenGL

---

## 📐 Rumus dan Persamaan yang Digunakan

### 1. Gerak Parabola Shuttlecock
```
y(t) = H × 4t(1 - t) + y_min      (H = 3.8, y_min = 0.55)
x(t) = x_start + (x_end - x_start) × ease(t)
```

### 2. Ease In-Out
```
ease(t) = 2t²              , t < 0.5
ease(t) = 1 - (-2t² + 2t)  , t ≥ 0.5
```

### 3. Smooth Interpolasi (Lerp)
```
value += (target - value) × k
k = min(SMOOTH × dt, 1.0)     (SMOOTH = 12.0)
```

### 4. Smoothstep
```
smoothstep(t) = t² × (3 - 2t)
```

### 5. Aiming Tangan — Yaw & Pitch
```
d = normalize(shuttle_pos - shoulder_world)
yaw   = atan2(d.x, d.z)
pitch = -atan2(d.y, |d.xz|)
```

### 6. Elbow Bend
```
elbow = lerp(0.70, 0.15, clamp(dist / 2.5, 0, 1))
elbow = lerp(elbow, 0.05, hit_blend)
```

### 7. Prediksi Posisi Shuttlecock
```
predicted_pos = current_pos + velocity × 0.20
```

### 8. Animasi Sinusoidal
```
bob(t)       = sin(t × 2.4) × 0.04
banner(t)    = sin(t × 2.5 + φ) × 0.30
flag_wave(t) = sin(t × 2.0 + φ) × 0.10
```

### 9. Camera Shake
```
shake_offset = random(-s, s)
cam_shake   -= dt × 1.2
cam_zoom    -= dt × 8.0
```

### 10. Transformasi Hierarkis
```
M_racket = M_root × M_body × M_shoulder × M_upper_arm × M_lower_arm × M_racket_local
```

---

## 📁 Struktur Folder

```
kiroki/
├── main.py              # Entry point: inisialisasi scene, game loop
├── renderer.py          # Renderer OpenGL: shader, VAO, helper geometri & matriks
├── camera.py            # Sistem kamera (free, follow, side, broadcast) + shake
├── animation.py         # AnimationController: state machine rally & fase pukulan
└── objects/
    ├── __init__.py
    ├── player.py        # Karakter pemain: animasi hierarkis, ekspresi wajah, aiming
    ├── shuttlecock.py   # Shuttlecock: fisika parabola, prediksi posisi
    ├── racket.py        # Mesh raket
    ├── net.py           # Net lapangan
    ├── court.py         # Lapangan badminton dengan garis
    ├── environment.py   # Lingkungan arena: lantai, dinding, lampu, scoreboard
    └── props.py         # Props: tribun, penonton, wasit, sponsor, bendera,
                         #        bangku, tas, handuk, lampu sorot, papan skor
```

---

## 🚀 Cara Menjalankan

**1. Install dependensi**
```bash
pip install moderngl pygame numpy
```

**2. Jalankan program**
```bash
python main.py
```

**Kontrol:**

| Tombol | Fungsi |
|--------|--------|
| `W A S D` | Gerak kamera (mode free) |
| `Q / E` | Turun / naik kamera |
| `Mouse` | Arah pandang kamera |
| `C` | Ganti mode kamera (free → follow → side → broadcast) |
| `Space` | Aktifkan slow motion |
| `L` | Toggle pencahayaan (lit/unlit) |
| `D` | Toggle debug dot tangan |
| `ESC` | Keluar |

---

## 📸 Screenshot / Preview

> *Tambahkan screenshot di sini*

---

## 🔮 Pengembangan Selanjutnya

- [ ] AI pemain dengan strategi pukulan adaptif
- [ ] Sistem scoring dan set pertandingan
- [ ] Tambahan jenis pukulan: *lob*, *drop shot*, *net kill*
- [ ] Fisika shuttlecock lebih realistis (drag udara, spin)
- [ ] Tekstur dan normal map pada objek
- [ ] Efek partikel saat shuttlecock mendarat
- [ ] Suara efek (pukulan, sorak penonton)

---

## 📝 Penutup

Project ini dikembangkan sebagai media pembelajaran grafika komputer dan simulasi interaktif berbasis OpenGL. Seluruh geometri, animasi, dan sistem rendering dibangun dari nol tanpa engine eksternal, sehingga cocok sebagai referensi untuk memahami konsep dasar *real-time 3D rendering* menggunakan Python.
