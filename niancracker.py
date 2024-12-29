import copy
import os.path
import random
import time

import pgzrun

WIDTH = 1600
HEIGHT = 900
FRAME_RATE = 60
TNT_POSES = tuple((410, i) for i in range(300, 600+1, 100))
NIAN_SPAWN_POSES = tuple((1300, i) for _, i in TNT_POSES)
NIAN_SPAWN_PROB = 20
NIAN_SPEED = 2.5
START_TIME = time.time()
TNT_FLY_SPEED = 15
TNT_CD = 0.1
TOTAL_TIME = 3 * 60

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
notification = "点击TNT，射击年！"
ending_helper = type("EndingHelper", (), {"ending_l": False, "ending_time": None, "ending_w": False})()

music.play("pigsteps.mp3")


def draw() -> None:
    global health, tnt_num, ongoing_time_s, score, notification, tnt_cd
    screen.clear()

    bg.draw()
    for tnt in tnts:
        tnt.draw()
    if tnt_cd == 0:
        flint_and_steel.draw()
    for nian in nians:
        nian.draw()
    for tnt in flying_tnts:
        tnt.draw()
    for heart in hearts:
        heart.draw()
    screen.draw.text(
        text=f"血量: {health} | "
             f"时间: {time_fmt(ongoing_time_s)} | "
             f"剩余时间: {time_fmt(TOTAL_TIME - ongoing_time_s)} | "
             f"剩余TNT: {tnt_num} | "
             f"分数: {score}",
        fontsize=40,
        fontname="unifont.otf",
        color="white",
        pos=(150, 50)
    )
    screen.draw.text(
        text=notification,
        fontsize=50,
        fontname="unifont.otf",
        color="white",
        pos=(150, 800)
    )
    screen.draw.text(
        text=f"TNT冷却: {tnt_cd:.2f} s",
        fontsize=50,
        fontname="unifont.otf",
        color="white",
        pos=(150, 750)
    )
    if health <= 0:
        screen.draw.text(
            text="YOU DIED",
            fontsize=200,
            fontname="mc_ten.otf",
            color="white",
            pos=(150, 550)
        )


def update() -> None:
    global nians, ongoing_time_s, ongoing_time, health, tnt_num, score, \
           notification, last_cd_update, tnt_cd, hearts, ending_helper

    if health <= 0:
        notification = f"你没了qwq"
        ending_helper.ending_l = True
        ending_helper.ending_time = time.time() if ending_helper.ending_time is None else ending_helper.ending_time
        if (time.time() - ending_helper.ending_time) > 1.:
            music.play_once("medead.mp3")
            time.sleep(2)
            quit(-114514)
    if ongoing_time_s >= TOTAL_TIME:
        notification = f"时间到了！"
        ending_helper.ending_w = True
        ending_helper.ending_time = time.time() if ending_helper.ending_time is None else ending_helper.ending_time
        if (time.time() - ending_helper.ending_time) > 1.:
            music.play_once("mewin.mp3")
            time.sleep(2)
            quit(114514)

    if ending_helper.ending_l or ending_helper.ending_w:
        return

    if random.randint(1, NIAN_SPAWN_PROB) == 1:
        new_nian()
    need_del = []
    for nian in nians:
        nian.x -= NIAN_SPEED
        if nian.x < 450:
            sounds.mehurt.play()
            need_del.append(nians.index(nian))
            notification = f"你被年击打了！（哦那看起来很接近"
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
                notification = f"1个年被炸掉了！| 加分！ {score_add}（把老子的意大利炮拿出来"
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
    global notification
    tnt = actor_as_abs_path("./images/tnt.png", copy.copy(tnts[index].pos))
    flying_tnts.append(tnt)
    notification = "发射了一个TNT！（把老子的意大利炮拿出来"


def new_nian() -> None:
    global notification
    new = actor_as_abs_path("./images/nian_s.png")
    new.pos = random.choice(NIAN_SPAWN_POSES)
    nians.append(new)
    notification = "又有一个年出来了！（子子孙孙无穷尽也"


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
