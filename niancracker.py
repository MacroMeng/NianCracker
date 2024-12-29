import copy
import os.path
import random
import time

import pgzrun

WIDTH = 1600
HEIGHT = 900
TNT_POSES = tuple((410, i) for i in range(300, 600+1, 100))
NIAN_SPAWN_POSES = tuple((1300, i) for _, i in TNT_POSES)
NIAN_SPAWN_PROB = 25
NIAN_SPEED = 2
START_TIME = time.time()
TNT_FLY_SPEED = 10
TNT_CD = 0.2

health = 20
ongoing_time_s = 0
ongoing_time = 0.
tnt_num = 200
score = 0
tnt_cd = 0
last_cd_update = START_TIME


def actor_as_abs_path(path, *args, **kwargs) -> Actor:
    return Actor(os.path.abspath(path), *args, **kwargs)


bg = actor_as_abs_path("./images/bg.png")
posshow = actor_as_abs_path("./images/pos.png")
flint_and_steel = actor_as_abs_path("./images/flintsteel.png")
tnts = [
    actor_as_abs_path("./images/tnt.png", (i, j)) for i, j in TNT_POSES
]
base_heart = actor_as_abs_path("./images/heart.png")
hearts = [base_heart] * health
flying_tnts = []
nians = []
notification = "KILL NIANS!"

music.play("pigsteps.mp3")


def draw() -> None:
    global health, tnt_num, ongoing_time_s, score, notification, tnt_cd
    screen.clear()

    bg.draw()
    for tnt in tnts:
        tnt.draw()
        flint_and_steel.draw()
    for nian in nians:
        nian.draw()
    for tnt in flying_tnts:
        tnt.draw()
    for heart in hearts:
        heart.draw()
    posshow.draw()
    screen.draw.text(
        text=f"Health: {health} | "
             f"Time: {time_fmt(ongoing_time_s)} | "
             f"TNTs: {tnt_num} | "
             f"Score: {score}",
        fontsize=50,
        fontname="mc_ten.otf",
        color="white",
        pos=(150, 50)
    )
    screen.draw.text(
        text=notification,
        fontsize=50,
        fontname="mc_ten.otf",
        color="white",
        pos=(150, 800)
    )
    screen.draw.text(
        text=f"Shoot CD: {tnt_cd:.2f} s",
        fontsize=50,
        fontname="mc_ten.otf",
        color="white",
        pos=(150, 750)
    )


def update() -> None:
    global nians, ongoing_time_s, ongoing_time, health, tnt_num, score, \
           notification, last_cd_update, tnt_cd, hearts

    if random.randint(1, NIAN_SPAWN_PROB) == 1:
        new_nian()
    need_del = []
    for nian in nians:
        nian.x -= NIAN_SPEED
        if nian.x < 450:
            sounds.mehurt.play()
            need_del.append(nians.index(nian))
            notification = f"You've been hit by Nian!"
    for i in need_del:
        nians.pop(i)
        health -= 1

    ongoing_time_s = int(ongoing_time)
    ongoing_time = time.time() - START_TIME

    hearts = [actor_as_abs_path("./images/heart.png") for _ in range(health)]
    for i, heart in enumerate(hearts):
        heart.pos = (165 + i * 30, 50)

    need_del = []
    for tnt in flying_tnts:
        tnt.x += TNT_FLY_SPEED
        for nian in nians:
            if is_near(tnt.pos, nian.pos):
                sounds.mobdeath.play()
                sounds.mobhurt.play()
                nians.pop(nians.index(nian))
                need_del.append(flying_tnts.index(tnt))
                score_add = random.randrange(500, 2500 + 1, 500)
                score += score_add
                notification = f"Killed 1 Nian | Score added {score_add}"
    for i in need_del:
        try:
            flying_tnts.pop(i)
        except IndexError:
            pass

    tnt_cd = TNT_CD - (time.time() - last_cd_update)
    if tnt_cd <= 0:
        tnt_cd = 0


def on_mouse_move(pos: tuple[float, float]) -> None:
    flint_and_steel.pos = pos


def on_mouse_down() -> None:
    global tnt_num, tnt_cd, tnt_num, last_cd_update

    for tnt in tnts:
        if tnt.collidepoint(flint_and_steel.pos) and tnt_num > 0 and tnt_cd == 0:
            last_cd_update = time.time()
            sounds.mefire.play()
            tnt_shoot(tnts.index(tnt))
            tnt_num -= 1


def tnt_shoot(index) -> None:
    tnt = actor_as_abs_path("./images/tnt.png", copy.copy(tnts[index].pos))
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


def is_near(pos1: tuple[float, float],
            pos2: tuple[float, float],
            xdelta: float | None = 50,
            ydelta: float | None = 50) -> bool:
    if xdelta is None:
        xdelta = pos1[0] + pos2[0]
        ydelta = pos1[1] + pos2[1]
    return (
        abs(pos1[0] - pos2[0]) < xdelta and
        abs(pos1[1] - pos2[1]) < ydelta
    )


pgzrun.go()
