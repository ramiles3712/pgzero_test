import math
import random

import pgzrun
from pgzero.builtins import Actor, keyboard, sounds, music
from pygame import Rect

TITLE = "Jungle Adventure"
WIDTH = 1000
HEIGHT = 700
TILE_SIZE = 64

START_X = 100
START_Y = 300

GRAVITY = 0.8
JUMP_FORCE = -20
PLAYER_SPEED = 9
ENEMY_SPEED = 1

STATE_MENU = 0
STATE_INTRO = 1
STATE_GAME = 2
STATE_WIN = 3
STATE_DEAD = 4
STATE_GOODBYE = 5

current_state = STATE_MENU
sound_enabled = True

platforms = []
LEVEL_WIDTH = WIDTH
GROUND_TOP = HEIGHT - TILE_SIZE
camera_x = 0


def load_level(filename: str) -> None:
    global LEVEL_WIDTH, GROUND_TOP
    platforms.clear()
    max_cols = 0

    try:
        with open(filename, "r") as f:
            lines = f.read().splitlines()

        num_rows = len(lines)
        map_height = num_rows * TILE_SIZE

        vertical_offset = max(0, map_height - HEIGHT)

        for row_index, line in enumerate(lines):
            values = line.split(",")
            max_cols = max(max_cols, len(values))

            for col_index, val in enumerate(values):
                val = val.strip()
                if val == "" or val == "-1":
                    continue

                tile_id = int(val)
                image_name = f"tile_{tile_id:04d}"

                block = Actor(f"tiles/{image_name}")
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE - vertical_offset
                block.topleft = (x, y)
                platforms.append(block)

        LEVEL_WIDTH = max_cols * TILE_SIZE

        ground_top = 0
        for p in platforms:
            if p.top > ground_top:
                ground_top = p.top
        GROUND_TOP = ground_top

        print("Level width:", LEVEL_WIDTH)
        print("Map height:", map_height, "offset:", vertical_offset)
    except Exception as exc:
        print(f"Error loading map: {exc}")
        LEVEL_WIDTH = WIDTH
        GROUND_TOP = HEIGHT - TILE_SIZE


load_level("mapa_plataformas.csv")


def get_actor_rect(actor: Actor) -> Rect:
    return Rect(actor.left, actor.top, actor.width, actor.height)


class Character:
    def __init__(self, image_name: str, x: float, y: float) -> None:
        self.actor = Actor(image_name)
        self.actor.topleft = (x, y)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.frame = 0
        self.anim_timer = 0

    def move_physics(self) -> None:
        self.actor.x += self.vx

        hit_box = get_actor_rect(self.actor)
        plat_rects = [get_actor_rect(p) for p in platforms]
        index = hit_box.collidelist(plat_rects)
        if index != -1:
            block = plat_rects[index]
            if self.vx > 0:
                self.actor.right = block.left
            elif self.vx < 0:
                self.actor.left = block.right

        self.vy += GRAVITY
        self.actor.y += self.vy
        self.on_ground = False

        hit_box = get_actor_rect(self.actor)
        index = hit_box.collidelist(plat_rects)
        if index != -1:
            block = plat_rects[index]
            if self.vy > 0:
                self.actor.bottom = block.top
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0:
                self.actor.top = block.bottom
                self.vy = 0

    def draw(self) -> None:
        self.actor.draw()

    def respawn(self) -> None:
        self.actor.pos = (START_X, START_Y)
        self.vx = 0
        self.vy = 0


class Player(Character):
    def __init__(self, x: float, y: float) -> None:
        super().__init__("hero_idle_0", x, y)
        self.idle_imgs = [f"hero_idle_{i}" for i in range(10)]
        self.walk_imgs = ["hero_walk_right_0", "hero_walk_right_1"]

    def handle_input(self) -> None:
        if keyboard.left:
            self.vx = -PLAYER_SPEED
        elif keyboard.right:
            self.vx = PLAYER_SPEED
        else:
            self.vx = 0

        if keyboard.space and self.on_ground:
            self.vy = JUMP_FORCE
            if sound_enabled:
                try:
                    sounds.jump.play()
                except Exception:
                    pass

    def animate(self) -> None:
        self.anim_timer += 1

        if self.vx != 0:
            img_list = self.walk_imgs
            speed = 6
        else:
            img_list = self.idle_imgs
            speed = 8

        if self.anim_timer % speed == 0:
            self.frame = (self.frame + 1) % len(img_list)
            self.actor.image = img_list[self.frame]

    def clamp_to_world(self) -> None:
        if self.actor.left < 0:
            self.actor.left = 0
        if self.actor.right > LEVEL_WIDTH:
            self.actor.right = LEVEL_WIDTH

    def update(self) -> None:
        self.handle_input()
        self.move_physics()
        self.clamp_to_world()
        self.animate()


class Enemy(Character):
    def __init__(self, x: float, y: float, patrol_distance: int) -> None:
        super().__init__("bee_walkright_0", x, y)
        self.start_x = x
        self.spawn_x = x
        self.spawn_y = y
        self.max_dist = patrol_distance
        self.vx = ENEMY_SPEED

        self.walk_right_imgs = ["bee_walkright_0", "bee_walkright_1"]
        self.walk_left_imgs = ["bee_walkleft_0", "bee_walkleft_1"]
        self.current_imgs = self.walk_right_imgs

    def animate(self) -> None:
        self.anim_timer += 1
        if self.anim_timer % 10 == 0:
            self.frame = (self.frame + 1) % len(self.current_imgs)
            self.actor.image = self.current_imgs[self.frame]

    def update(self) -> None:
        self.actor.x += self.vx

        if self.actor.x > self.start_x + self.max_dist:
            self.vx = -ENEMY_SPEED
        elif self.actor.x < self.start_x:
            self.vx = ENEMY_SPEED

        if self.vx > 0:
            self.current_imgs = self.walk_right_imgs
        else:
            self.current_imgs = self.walk_left_imgs

        self.animate()

    def reset(self) -> None:
        self.actor.topleft = (self.spawn_x, self.spawn_y)
        self.vx = ENEMY_SPEED


hero = Player(START_X, START_Y)

enemies = [
    Enemy(600, 400, 140),
    Enemy(1200, 340, 140),
    Enemy(900, 500, 140),
]

goal_actor = Actor("ramiles")
goal_actor.y = 260
goal_actor.x = LEVEL_WIDTH - 240


def play_bg_music() -> None:
    if not sound_enabled:
        return
    try:
        music.play("musicthe")
        music.set_volume(0.4)
    except Exception:
        pass


def stop_bg_music() -> None:
    try:
        music.stop()
    except Exception:
        pass


def play_click() -> None:
    if not sound_enabled:
        return
    try:
        sounds.mouseclick.play()
    except Exception:
        try:
            sounds.click.play()
        except Exception:
            pass


def play_hit() -> None:
    if sound_enabled:
        try:
            sounds.hit.play()
        except Exception:
            pass


play_bg_music()

btn_start = Rect(WIDTH // 2 - 120, 260, 240, 50)
btn_sound = Rect(WIDTH // 2 - 120, 330, 240, 50)
btn_exit = Rect(WIDTH // 2 - 120, 400, 240, 50)

btn_game_exit = Rect(WIDTH - 150, 20, 130, 40)


def draw_button(rect: Rect, label: str, color) -> None:
    screen.draw.filled_rect(rect, color)
    screen.draw.text(label, center=rect.center, fontsize=30, color="white")


def draw_menu():
    screen.fill((15, 20, 40))
    screen.draw.text(
        "Ramiles Platformer Test",
        center=(WIDTH // 2, 120),
        fontsize=52,
        color="white",
    )
    screen.draw.text(
        "Um pequeno desafio feito especialmente para voce, recrutador.",
        center=(WIDTH // 2, 170),
        fontsize=26,
        color="lightgray",
    )

    draw_button(btn_start, "START TEST", "green")
    sound_text = "SOUND: ON" if sound_enabled else "SOUND: OFF"
    draw_button(btn_sound, sound_text, "orange")
    draw_button(btn_exit, "EXIT", "red")

    screen.draw.text(
        "Setas para mover  |  ESPACO para pular",
        center=(WIDTH // 2, 480),
        fontsize=22,
        color="lightgray",
    )


def draw_intro():
    screen.fill((10, 20, 40))
    screen.draw.text(
        "Ola, recrutador!",
        center=(WIDTH // 2, 140),
        fontsize=48,
        color="white",
    )
    screen.draw.text(
        "Se voce chegou ate aqui, e porque leva programacao a serio.",
        center=(WIDTH // 2, 200),
        fontsize=26,
        color="white",
    )
    screen.draw.text(
        "Agora e minha vez de te desafiar: atravesse a fase,",
        center=(WIDTH // 2, 240),
        fontsize=26,
        color="white",
    )
    screen.draw.text(
        "desvie das abelhas e encontre o Ramiles no final do mapa.",
        center=(WIDTH // 2, 275),
        fontsize=26,
        color="white",
    )
    screen.draw.text(
        "Setas: mover  |  ESPACO: pular",
        center=(WIDTH // 2, 325),
        fontsize=24,
        color="lightgray",
    )
    screen.draw.text(
        "Clique em qualquer lugar para comecar o desafio!",
        center=(WIDTH // 2, 380),
        fontsize=28,
        color="yellow",
    )


def draw_game():
    try:
        screen.blit("background", (0, 0))
    except Exception:
        screen.fill((100, 200, 255))

    for platform in platforms:
        if platform.right < camera_x - 64 or platform.left > camera_x + WIDTH + 64:
            continue
        old_x = platform.x
        platform.x = old_x - camera_x
        platform.draw()
        platform.x = old_x

    old_px = hero.actor.x
    hero.actor.x = old_px - camera_x
    hero.actor.draw()
    hero.actor.x = old_px

    for enemy in enemies:
        old_ex = enemy.actor.x
        enemy.actor.x = old_ex - camera_x
        enemy.actor.draw()
        enemy.actor.x = old_ex

    old_gx = goal_actor.x
    goal_actor.x = old_gx - camera_x
    goal_actor.draw()
    goal_actor.x = old_gx

    draw_button(btn_game_exit, "EXIT", "darkred")


def draw_win():
    screen.fill((5, 10, 25))

    old_pos = goal_actor.pos
    goal_actor.pos = (WIDTH // 2, HEIGHT // 2 - 60)
    goal_actor.draw()
    goal_actor.pos = old_pos

    screen.draw.text(
        "Parabens, recrutador!",
        center=(WIDTH // 2, HEIGHT // 2 + 40),
        fontsize=42,
        color="white",
    )
    screen.draw.text(
        "Voce chegou ate o Ramiles no final da fase.",
        center=(WIDTH // 2, HEIGHT // 2 + 85),
        fontsize=30,
        color="white",
    )
    screen.draw.text(
        "Clique para voltar ao menu.",
        center=(WIDTH // 2, HEIGHT // 2 + 130),
        fontsize=26,
        color="yellow",
    )


def draw_dead():
    screen.fill((10, 0, 20))
    screen.draw.text(
        "Voce caiu da plataforma!",
        center=(WIDTH // 2, HEIGHT // 2 - 20),
        fontsize=42,
        color="white",
    )
    screen.draw.text(
        "Nem todo recrutador sobrevive a primeira tentativa...",
        center=(WIDTH // 2, HEIGHT // 2 + 20),
        fontsize=28,
        color="lightgray",
    )
    screen.draw.text(
        "Clique para tentar de novo.",
        center=(WIDTH // 2, HEIGHT // 2 + 70),
        fontsize=28,
        color="yellow",
    )


def draw_goodbye():
    screen.fill((0, 5, 15))
    screen.draw.text(
        "Obrigado por jogar, recrutador!",
        center=(WIDTH // 2, HEIGHT // 2 - 20),
        fontsize=40,
        color="white",
    )
    screen.draw.text(
        "Foi um prazer te mostrar um pouco do meu codigo.",
        center=(WIDTH // 2, HEIGHT // 2 + 20),
        fontsize=28,
        color="lightgray",
    )
    screen.draw.text(
        "Clique em qualquer lugar para fechar o jogo.",
        center=(WIDTH // 2, HEIGHT // 2 + 70),
        fontsize=26,
        color="yellow",
    )


def draw():
    screen.clear()

    if current_state == STATE_MENU:
        draw_menu()
    elif current_state == STATE_INTRO:
        draw_intro()
    elif current_state == STATE_GAME:
        draw_game()
    elif current_state == STATE_WIN:
        draw_win()
    elif current_state == STATE_DEAD:
        draw_dead()
    elif current_state == STATE_GOODBYE:
        draw_goodbye()


def reset_game() -> None:
    global camera_x
    hero.respawn()
    for enemy in enemies:
        enemy.reset()
    camera_x = 0


def player_die() -> None:
    global current_state
    play_hit()
    current_state = STATE_DEAD
    stop_bg_music()


def update():
    global camera_x, current_state

    if current_state == STATE_GAME:
        hero.update()

        if hero.actor.top > HEIGHT + 100:
            player_die()
            return

        for enemy in enemies:
            enemy.update()
            if hero.actor.colliderect(enemy.actor):
                play_hit()
                hero.respawn()
                camera_x = 0

        if hero.actor.colliderect(goal_actor):
            current_state = STATE_WIN
            stop_bg_music()

        target_x = hero.actor.centerx - WIDTH // 2
        camera_x = max(0, min(target_x, LEVEL_WIDTH - WIDTH))


def on_mouse_down(pos):
    global current_state, sound_enabled, camera_x

    if current_state == STATE_MENU:
        if btn_start.collidepoint(pos):
            play_click()
            current_state = STATE_INTRO
        elif btn_sound.collidepoint(pos):
            play_click()
            sound_enabled = not sound_enabled
            if sound_enabled:
                play_bg_music()
            else:
                stop_bg_music()
        elif btn_exit.collidepoint(pos):
            play_click()
            stop_bg_music()
            raise SystemExit

    elif current_state == STATE_INTRO:
        play_click()
        current_state = STATE_GAME
        camera_x = 0

    elif current_state == STATE_GAME:
        if btn_game_exit.collidepoint(pos):
            play_click()
            stop_bg_music()
            current_state = STATE_GOODBYE

    elif current_state == STATE_WIN:
        play_click()
        current_state = STATE_MENU
        reset_game()
        play_bg_music()

    elif current_state == STATE_DEAD:
        play_click()
        reset_game()
        current_state = STATE_GAME
        play_bg_music()

    elif current_state == STATE_GOODBYE:
        play_click()
        raise SystemExit


pgzrun.go()
