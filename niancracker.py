import os.path
import pgzrun


WIDTH = 1600
HEIGHT = 900
TNT_POSES = tuple((410, i) for i in range(300, 600+1, 100))


def actor_as_abs_path(path, *args, **kwargs):
    return Actor(os.path.abspath(path), *args, **kwargs)


bg = actor_as_abs_path("./images/bg.png")
flint_and_steel = actor_as_abs_path("./images/flintsteel.png")
tnts = [
    actor_as_abs_path("./images/tnt.png", (i, j)) for i, j in TNT_POSES
]


def draw():
    screen.clear()
    bg.draw()
    for tnt in tnts:
        tnt.draw()
        flint_and_steel.draw()


def update():
    pass


def on_mouse_move(pos):
    flint_and_steel.pos = pos


def on_mouse_down():
    sounds.mefire.play()


pgzrun.go()
