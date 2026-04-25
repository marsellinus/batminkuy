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
from objects.props import Bench, Bottle, Bag, ShuttlecockBox, Spectator

WIDTH, HEIGHT = 1280, 720
FPS_TARGET    = 60
DEBUG         = False


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

    # First leg: shuttle goes toward player2 (dir=+1), send player2 to intercept
    player2.set_target(0.0, 3.2)

    # ── Environment ───────────────────────────────────────────────────────────
    environment = Environment(ctx, renderer)

    # ── Props: benches (both sides) ───────────────────────────────────────────
    import math
    benches = [
        Bench(ctx, renderer, (-5.5,  0.0, -2.0), angle=math.pi/2),
        Bench(ctx, renderer, (-5.5,  0.0,  2.0), angle=math.pi/2),
        Bench(ctx, renderer, ( 5.5,  0.0, -2.0), angle=-math.pi/2),
        Bench(ctx, renderer, ( 5.5,  0.0,  2.0), angle=-math.pi/2),
    ]

    # ── Props: bottles near benches ───────────────────────────────────────────
    bottles = [
        Bottle(ctx, renderer, (-5.0, 0.0, -1.2), [0.15, 0.35, 0.85]),
        Bottle(ctx, renderer, (-5.0, 0.0,  1.2), [0.85, 0.18, 0.18]),
        Bottle(ctx, renderer, (-5.2, 0.0, -1.4), [0.15, 0.35, 0.85]),
    ]

    # ── Props: sports bags ────────────────────────────────────────────────────
    bags = [
        Bag(ctx, renderer, (-5.8, 0.0, -3.0), [0.15, 0.35, 0.85], angle=0.4),
        Bag(ctx, renderer, ( 5.8, 0.0,  3.0), [0.85, 0.18, 0.18], angle=-0.4),
    ]

    # ── Props: shuttlecock boxes ──────────────────────────────────────────────
    shuttle_boxes = [
        ShuttlecockBox(ctx, renderer, (-5.0, 0.0, -3.5)),
        ShuttlecockBox(ctx, renderer, ( 5.0, 0.0,  3.5)),
    ]

    # ── Props: spectators ─────────────────────────────────────────────────────
    spectators = [
        Spectator(ctx, renderer, (-7.5, 0.0, -3.0), [0.70, 0.20, 0.20], angle= math.pi/2),
        Spectator(ctx, renderer, (-7.5, 0.0,  0.0), [0.20, 0.55, 0.20], angle= math.pi/2),
        Spectator(ctx, renderer, (-7.5, 0.0,  3.0), [0.80, 0.60, 0.10], angle= math.pi/2),
        Spectator(ctx, renderer, ( 7.5, 0.0, -3.0), [0.30, 0.30, 0.75], angle=-math.pi/2),
        Spectator(ctx, renderer, ( 7.5, 0.0,  0.0), [0.65, 0.20, 0.65], angle=-math.pi/2),
        Spectator(ctx, renderer, ( 7.5, 0.0,  3.0), [0.20, 0.60, 0.70], angle=-math.pi/2),
    ]

    clock       = pygame.time.Clock()
    slow_motion = False
    dbg_timer   = 0.0
    running     = True

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
        camera.update(dt, keys, mx, my, shuttlecock.position, shake=anim.cam_shake)

        dbg_timer += dt_raw
        if dbg_timer >= 5.0:
            camera.debug_print(); dbg_timer = 0.0

        ctx.clear(0.08, 0.10, 0.15, 1.0)
        vp = camera.get_view_projection()

        if DEBUG:
            renderer.draw_debug(vp)

        # Draw order: environment first (back), then court, then props, then players
        environment.draw(vp)
        court.draw(vp)
        net.draw(vp)

        for b in benches:      b.draw(vp)
        for b in bottles:      b.draw(vp)
        for b in bags:         b.draw(vp)
        for b in shuttle_boxes: b.draw(vp)
        for s in spectators:   s.draw(vp)

        shuttlecock.draw(vp)
        player1.draw(vp)
        player2.draw(vp)

        pygame.display.set_caption(
            f"Badminton 3D  |  FPS: {clock.get_fps():.0f}"
            f"  |  {camera.mode}  |  {'SLOW-MO' if slow_motion else ''}"
        )
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
