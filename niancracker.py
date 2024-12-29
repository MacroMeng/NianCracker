import copy
import os.path
import random
import time

import pgzrun
from pygame.sprite import collide_rect

WIDTH = 1600
HEIGHT = 900
TNT_POSES = tuple((410, i) for i in range(300, 600+1, 100))
NIAN_SPAWN_POSES = tuple((1700, i) for _, i in TNT_POSES)
NIAN_SPAWN_PROB = 100
NIAN_SPEED = 1.5
START_TIME = time.time()
TNT_FLY_SPEED = 15

health = 20
ongoing_time_s = 0
ongoing_time = 0.
tnt_num = 200


def actor_as_abs_path(path, *args, **kwargs) -> Actor:
    return Actor(os.path.abspath(path), *args, **kwargs)


bg = actor_as_abs_path("./images/bg.png")
posshow = actor_as_abs_path("./images/pos.png")
flint_and_steel = actor_as_abs_path("./images/flintsteel.png")
tnts = [
    actor_as_abs_path("./images/tnt.png", (i, j)) for i, j in TNT_POSES
]
flying_tnts = []
nians = []


def draw() -> None:
    global health, tnt_num
    screen.clear()

    bg.draw()
    for tnt in tnts:
        tnt.draw()
        flint_and_steel.draw()
    for nian in nians:
        nian.draw()
    for tnt in flying_tnts:
        tnt.draw()
    posshow.draw()
    screen.draw.text(
        text=f"Health: {health} | "
             f"Time: {time_fmt(ongoing_time_s)} | "
             f"TNTs: {tnt_num}",
        fontsize=50,
        fontname="mc_ten.otf",
        color="white",
        pos=(150, 50)
    )


def update() -> None:
    global nians, ongoing_time_s, ongoing_time, health, tnt_num

    if random.randint(1, NIAN_SPAWN_PROB) == 1:
        new_nian()
    need_del = []
    for nian in nians:
        nian.x -= NIAN_SPEED
        if nian.x < 450:
            sounds.mehurt.play()
            need_del.append(nians.index(nian))
    for i in need_del:
        nians.pop(i)
        health -= 1

    ongoing_time_s = int(ongoing_time)
    ongoing_time = time.time() - START_TIME

    need_del = []
    for tnt in flying_tnts:
        if not tnt.fly_up_done:
            tnt.y -= TNT_FLY_SPEED
            draw()
        if tnt.y < -100:
            tnt.fly_up_done = True
        tnt.nearest_nian = find_nearest_nian(tnt) if not tnt.looked_for_nian else tnt.nearest_nian
        tnt.has_target = tnt.nearest_nian is not None
        if tnt.has_target and not tnt.fly_down_done and tnt.fly_up_done:
            print(f"{f"YEP and {tnt}":=^100}")
            tnt.y += TNT_FLY_SPEED
            tnt.x = tnt.nearest_nian.x
            draw()
        if tnt.has_target and is_near(tnt.pos, tnt.nearest_nian.pos, 100):
            tnt.fly_down_done = True
        if tnt.has_target and tnt.fly_up_done and tnt.fly_down_done:
            nians.pop(nians.index(tnt.nearest_nian))
            sounds.mobhurt.play()
            need_del.append(flying_tnts.index(tnt))
        if not tnt.has_target and tnt.fly_up_done:
            need_del.append(flying_tnts.index(tnt))
        print(tnt.pos, tnt.fly_up_done, tnt.fly_down_done, tnt.has_target, tnt.nearest_nian)
    for i in need_del:
        flying_tnts.pop(i)


def on_mouse_move(pos: tuple[float, float]) -> None:
    flint_and_steel.pos = pos


def on_mouse_down() -> None:
    global tnt_num

    for tnt in tnts:
        if tnt.collidepoint(flint_and_steel.pos):
            sounds.mefire.play()
            tnt_shoot(tnts.index(tnt))
            tnt_num -= 1


def tnt_shoot(index) -> None:
    tnt = actor_as_abs_path("./images/tnt.png", copy.copy(tnts[index].pos))
    tnt.fly_up_done = False
    tnt.fly_down_done = False
    tnt.looked_for_nian = False
    flying_tnts.append(tnt)


def find_nearest_nian(tnt: Actor) -> Actor:
    possibly_nians = []
    for nian in nians:
        if abs(nian.y - tnt.y) < 10:
            print(f"found 1 <{nian}, {tnt}>")
            possibly_nians.append(nian)
    nearest_nian = min(possibly_nians, key=lambda n: abs(n.x - tnt.x), default=None)
    print(nearest_nian)
    return nearest_nian


def new_nian() -> None:
    new = actor_as_abs_path("./images/nian_s.png")
    new.pos = random.choice(NIAN_SPAWN_POSES)
    nians.append(new)


def time_fmt(time_s: int) -> str:
    min_ = time_s // 60
    sec = time_s % 60
    return f"{min_:0>2}:{sec:0>2}"


def is_near(pos1: tuple[float, float], pos2: tuple[float, float], delta: int = 50) -> bool:
    return (
        abs(pos1[0] - pos2[0]) < delta and
        abs(pos1[1] - pos2[1]) < delta
    )


pgzrun.go()
