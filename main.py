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
from objects.props import Bench, Bottle, Bag, ShuttlecockBox, Spectator, Stands

WIDTH, HEIGHT = 1280, 720
FPS_TARGET    = 60
DEBUG         = False

# Base FOV; camera zoom reduces this temporarily on hit
BASE_FOV = 45.0


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

    # ── Spectators on stands (left side X≈-4.5, right side X≈4.5) ────────────
    # Place spectators on each tier of the stands
    SHIRT_COLORS = [
        [0.70, 0.20, 0.20], [0.20, 0.55, 0.20], [0.80, 0.60, 0.10],
        [0.30, 0.30, 0.75], [0.65, 0.20, 0.65], [0.20, 0.60, 0.70],
        [0.85, 0.40, 0.10], [0.10, 0.50, 0.50], [0.60, 0.60, 0.10],
        [0.40, 0.10, 0.60],
    ]
    spectators = []
    STEP_H = 0.40
    STEP_D = 0.55
    Z_POSITIONS = [-4.5, -1.5, 1.5, 4.5]   # 4 spectators per tier per side

    for tier in range(5):
        y = tier * STEP_H + 0.55   # sit on top of bench
        for zi, z in enumerate(Z_POSITIONS):
            color_idx = (tier * 4 + zi) % len(SHIRT_COLORS)
            # Left stand: X = -7.0 - tier*STEP_D, faces +X (angle=+π/2)
            lx = -7.0 - tier * STEP_D
            spectators.append(Spectator(
                ctx, renderer, (lx, y, z),
                SHIRT_COLORS[color_idx], angle=math.pi / 2
            ))
            # Right stand: X = +7.0 + tier*STEP_D, faces -X (angle=-π/2)
            rx = 7.0 + tier * STEP_D
            spectators.append(Spectator(
                ctx, renderer, (rx, y, z),
                SHIRT_COLORS[(color_idx + 5) % len(SHIRT_COLORS)], angle=-math.pi / 2
            ))

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
        _prev_shake = anim.cam_shake

        for s in spectators:
            s.update(dt)

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
        court.draw(vp)
        net.draw(vp)

        for b in benches:       b.draw(vp)
        for b in bottles:       b.draw(vp)
        for b in bags:          b.draw(vp)
        for b in shuttle_boxes: b.draw(vp)
        for s in spectators:    s.draw(vp)

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
