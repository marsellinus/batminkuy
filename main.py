import pygame
import moderngl
import numpy as np
from camera import Camera
from renderer import Renderer
from animation import AnimationController
from objects.court import Court
from objects.net import Net
from objects.shuttlecock import Shuttlecock
from objects.player import Player
from objects.environment import Environment
from objects.props import (Bench, Bottle, Bag, ShuttlecockBox, Spectator, Stands,
                           Umpire, SponsorBanner, LineUmpire, AudienceBanner, WallFlag,
                           Towel, FloorLight, ScoreBoard)

WIDTH, HEIGHT = 1280, 720
FPS_TARGET    = 60
DEBUG         = False

# Base FOV; camera zoom reduces this temporarily on hit
BASE_FOV = 55.0


def main():
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Badminton 3D")
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    ctx = moderngl.create_context()
    ctx.enable(moderngl.DEPTH_TEST)
    ctx.enable(moderngl.BLEND)
    ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

    renderer    = Renderer(ctx)
    camera      = Camera(WIDTH, HEIGHT)
    anim        = AnimationController()

    # ── Core scene ────────────────────────────────────────────────────────────
    court       = Court(ctx, renderer)
    net         = Net(ctx, renderer)
    shuttlecock = Shuttlecock(ctx, renderer)
    player1     = Player(ctx, renderer, position=np.array([0.0, 0.025, -4.0]), facing=1.0)
    player2     = Player(ctx, renderer, position=np.array([0.0, 0.025,  4.0]), facing=-1.0)
    player2.set_target(0.0, 3.2)

    # ── Environment ───────────────────────────────────────────────────────────
    environment = Environment(ctx, renderer)

    # ── Stands (tribun bertingkat) ────────────────────────────────────────────
    stands = Stands(ctx, renderer)

    # ── Umpire (wasit di net) ─────────────────────────────────────────────────
    umpire = Umpire(ctx, renderer, position=(3.5, 0.0, 0.0))

    # ── Sponsor Banners (Iklan sponsor) ───────────────────────────────────────
    import math
    sponsor_banners = [
        # Left side banners (facing right)
        SponsorBanner(ctx, renderer, "YONEX", position=(-6.5, 2.0, -5.0), angle=math.pi/2),
        SponsorBanner(ctx, renderer, "LING", position=(-6.5, 2.0, 5.0), angle=math.pi/2),
        # Right side banners (facing left)
        SponsorBanner(ctx, renderer, "YONEX", position=(6.5, 2.0, -5.0), angle=-math.pi/2),
        SponsorBanner(ctx, renderer, "LING", position=(6.5, 2.0, 5.0), angle=-math.pi/2),
    ]

    # ── Line Umpires (Hakim garis di titik ujung lapangan) ────────────────────
    line_umpires = [
        # Front line umpires (looking backward at back line)
        LineUmpire(ctx, renderer, position=(-3.8, 0.0, -7.2), angle=0),
        LineUmpire(ctx, renderer, position=(3.8, 0.0, -7.2), angle=0),
        # Back line umpires (looking forward at front line)
        LineUmpire(ctx, renderer, position=(-3.8, 0.0, 7.2), angle=math.pi),
        LineUmpire(ctx, renderer, position=(3.8, 0.0, 7.2), angle=math.pi),
    ]

    # ── Props: benches ────────────────────────────────────────────────────────
    import math
    benches = [
        Bench(ctx, renderer, (-5.5,  0.0, -2.0), angle=math.pi/2),
        Bench(ctx, renderer, (-5.5,  0.0,  2.0), angle=math.pi/2),
        Bench(ctx, renderer, ( 5.5,  0.0, -2.0), angle=-math.pi/2),
        Bench(ctx, renderer, ( 5.5,  0.0,  2.0), angle=-math.pi/2),
    ]

    bottles = [
        Bottle(ctx, renderer, (-5.0, 0.0, -1.2), [0.15, 0.35, 0.85]),
        Bottle(ctx, renderer, (-5.0, 0.0,  1.2), [0.85, 0.18, 0.18]),
        Bottle(ctx, renderer, (-5.2, 0.0, -1.4), [0.15, 0.35, 0.85]),
    ]

    bags = [
        Bag(ctx, renderer, (-5.8, 0.0, -3.0), [0.15, 0.35, 0.85], angle=0.4),
        Bag(ctx, renderer, ( 5.8, 0.0,  3.0), [0.85, 0.18, 0.18], angle=-0.4),
    ]

    shuttle_boxes = [
        ShuttlecockBox(ctx, renderer, (-5.0, 0.0, -3.5)),
        ShuttlecockBox(ctx, renderer, ( 5.0, 0.0,  3.5)),
    ]

    # ── Towels (handuk di bangku pemain) ──────────────────────────────────────
    towels = [
        Towel(ctx, renderer, (-5.5, 0.55, -1.5), angle=math.pi/2),
        Towel(ctx, renderer, (-5.5, 0.55,  0.5), angle=math.pi/2),
        Towel(ctx, renderer, ( 5.5, 0.55, -0.5), angle=-math.pi/2),
        Towel(ctx, renderer, ( 5.5, 0.55,  1.5), angle=-math.pi/2),
    ]

    # ── Floor Lights (lampu sorot di sudut lapangan) ──────────────────────────
    floor_lights = [
        FloorLight(ctx, renderer, (-8.5, 0.0, -7.5), angle= math.pi/4),
        FloorLight(ctx, renderer, ( 8.5, 0.0, -7.5), angle=-math.pi/4 + math.pi),
        FloorLight(ctx, renderer, (-8.5, 0.0,  7.5), angle= math.pi/4 + math.pi),
        FloorLight(ctx, renderer, ( 8.5, 0.0,  7.5), angle=-math.pi/4),
    ]

    # ── Score Boards (papan skor di kedua sisi net) ───────────────────────────
    score_boards = [
        ScoreBoard(ctx, renderer, (-4.5, 1.2, 0.0), angle= math.pi/2),
        ScoreBoard(ctx, renderer, ( 4.5, 1.2, 0.0), angle=-math.pi/2),
    ]

    # ── Spectators on stands (left side X≈-4.5, right side X≈4.5) ────────────
    # Place spectators on each tier of the stands
    SHIRT_COLORS = [
        [0.70, 0.20, 0.20], [0.20, 0.55, 0.20], [0.80, 0.60, 0.10],
        [0.30, 0.30, 0.75], [0.65, 0.20, 0.65], [0.20, 0.60, 0.70],
        [0.85, 0.40, 0.10], [0.10, 0.50, 0.50], [0.60, 0.60, 0.10],
        [0.40, 0.10, 0.60],
    ]
    spectators = []
    # Konstanta harus sinkron dengan _stands_mesh
    S_STEP_H = 0.42
    S_STEP_D = 0.52
    S_SLAB_T = 0.20
    S_SIDE_X = 9.5
    S_ROW_W  = 14.0

    SPACING_Z = 0.85  # lebih longgar (lebar penonton 0.30, gap 0.55)
    N_COLS    = int(S_ROW_W / SPACING_Z)          # ~16 kolom
    Z_START   = -(S_ROW_W / 2) + SPACING_Z / 2

    _ITEMS = [None, None, None, 'stick', 'flag']  # lebih sedikit yang pegang item

    for tier in range(8):   # 8 tier cukup, tidak perlu 10
        # Y: tepat di atas bench slab
        y  = tier * S_STEP_H + S_SLAB_T + 0.03
        # X: slab tier ini (mundur ke luar per tier)
        lx = -(S_SIDE_X + tier * S_STEP_D)
        rx =   S_SIDE_X + tier * S_STEP_D

        for col in range(N_COLS):
            z = Z_START + col * SPACING_Z
            # Offset kecil agar tidak terlalu seragam
            z_off = ((tier * 7 + col * 3) % 5 - 2) * 0.04

            color_idx = (tier * N_COLS + col) % len(SHIRT_COLORS)
            item_l = _ITEMS[(tier * 3 + col * 7) % len(_ITEMS)]
            item_r = _ITEMS[(tier * 5 + col * 3 + 1) % len(_ITEMS)]

            spectators.append(Spectator(
                ctx, renderer, (lx, y, z + z_off),
                SHIRT_COLORS[color_idx], angle=math.pi / 2,
                item_type=item_l, item_color_idx=(tier + col) % 5
            ))
            spectators.append(Spectator(
                ctx, renderer, (rx, y, z + z_off),
                SHIRT_COLORS[(color_idx + 5) % len(SHIRT_COLORS)], angle=-math.pi / 2,
                item_type=item_r, item_color_idx=(tier + col + 2) % 5
            ))

    audience_banners = []

    # ── WallFlag — bendera di dinding belakang arena ─────────────────────────
    # Dinding belakang di Z = ±13.5 (FLOOR_L/2 = 14)
    # Spacing 1.5 unit, 6 bendera per dinding, centered
    _FLAG_COUNTRIES = ['INA', 'MAS', 'CHN', 'JPN', 'KOR', 'INA']
    flags = []
    N_FLAGS   = len(_FLAG_COUNTRIES)
    SPACING_F = 1.8
    START_X   = -(N_FLAGS - 1) * SPACING_F / 2
    FLAG_Y    = 3.5   # ketinggian di dinding
    for k, country in enumerate(_FLAG_COUNTRIES):
        fx = START_X + k * SPACING_F
        # Dinding belakang (Z = -13.5, menghadap ke dalam = +Z)
        flags.append(WallFlag(ctx, renderer, (fx, FLAG_Y, -15.8), country=country, phase=k * 0.6))
        # Dinding depan (Z = +16, menghadap ke dalam = -Z)
        flags.append(WallFlag(ctx, renderer, (fx, FLAG_Y,  15.8), country=country, phase=k * 0.9))


    clock       = pygame.time.Clock()
    slow_motion = False
    dbg_timer   = 0.0
    running     = True
    _prev_shake = 0.0   # detect rising edge of cam_shake to trigger spectators

    print("[Badminton 3D]  WASD=move  Mouse=look  C=cam-mode  SPACE=slowmo  P=cam-info  ESC=quit")

    while running:
        dt_raw = clock.tick(FPS_TARGET) / 1000.0
        dt     = dt_raw * (0.25 if slow_motion else 1.0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                if event.key == pygame.K_c:      camera.cycle_mode()
                if event.key == pygame.K_SPACE:  slow_motion = not slow_motion
                if event.key == pygame.K_p:      camera.debug_print()
                if event.key == pygame.K_l:
                    renderer.unlit_mode = not renderer.unlit_mode
                    print(f"[Lighting] {'OFF (unlit)' if renderer.unlit_mode else 'ON'}")
                if event.key == pygame.K_d:
                    Player.show_debug = not Player.show_debug
                    print(f"[Debug] hand dot {'ON' if Player.show_debug else 'OFF'}")

        keys   = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_rel()

        shuttlecock.update(dt)
        anim.update(dt, shuttlecock, player1, player2)
        player1.set_shuttle(shuttlecock)
        player2.set_shuttle(shuttlecock)
        player1.update(dt)
        player2.update(dt)

        # ── Trigger spectator hit reaction on rising edge of cam_shake ────────
        if anim.cam_shake > 0.01 and _prev_shake <= 0.01:
            for s in spectators:
                s.trigger_hit()
            umpire.trigger_hit()
            for lu in line_umpires:
                lu.trigger_hit()
        _prev_shake = anim.cam_shake

        for s in spectators:
            s.update(dt)
        umpire.update(dt)
        for lu in line_umpires:
            lu.update(dt)

        for b in audience_banners: b.update(dt)
        for f in flags:            f.update(dt)

        # ── Camera zoom: reduce FOV temporarily on hit ────────────────────────
        if anim.cam_zoom > 0.0:
            camera.proj = _perspective(BASE_FOV - anim.cam_zoom, WIDTH / HEIGHT, 0.1, 100.0)
        else:
            camera.proj = _perspective(BASE_FOV, WIDTH / HEIGHT, 0.1, 100.0)

        camera.update(dt, keys, mx, my, shuttlecock.position, shake=anim.cam_shake)

        dbg_timer += dt_raw
        if dbg_timer >= 5.0:
            camera.debug_print(); dbg_timer = 0.0

        ctx.clear(0.08, 0.10, 0.15, 1.0)
        vp = camera.get_view_projection()

        if DEBUG:
            renderer.draw_debug(vp)

        environment.draw(vp)
        stands.draw(vp)
        umpire.draw(vp)
        for lu in line_umpires: lu.draw(vp)
        court.draw(vp)
        net.draw(vp)

        for b in benches:       b.draw(vp)
        for b in bottles:       b.draw(vp)
        for b in bags:          b.draw(vp)
        for b in shuttle_boxes: b.draw(vp)
        for t in towels:        t.draw(vp)
        for f in floor_lights:  f.draw(vp)
        for s in score_boards:  s.draw(vp)
        for s in spectators:    s.draw(vp)

        for b in audience_banners: b.draw(vp)
        for f in flags:            f.draw(vp)

        shuttlecock.draw(vp)
        player1.draw(vp)
        player2.draw(vp)

        pygame.display.set_caption(
            f"Badminton 3D  |  FPS: {clock.get_fps():.0f}"
            f"  |  {camera.mode}  |  {'SLOW-MO' if slow_motion else ''}"
        )
        pygame.display.flip()

    pygame.quit()


def _perspective(fov_deg, aspect, near, far):
    import numpy as np
    f = 1.0 / np.tan(np.radians(fov_deg) / 2.0)
    m = np.zeros((4, 4), dtype='f4')
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2.0 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m


if __name__ == "__main__":
    main()
