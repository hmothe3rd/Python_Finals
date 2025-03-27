import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
import cv2

pygame.init()

pygame.display.set_caption("Echoes of Home")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5
window = pygame.display.set_mode((WIDTH, HEIGHT))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100,100,100)

font = pygame.font.Font(None, 36)

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()

def main_game(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    player = Player(100, 100, 50, 50)
    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 2) // block_size)]
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire]

    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"  # Signal to exit main loop

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    return "exit"

def music_settings(window):
    clock = pygame.time.Clock()
    run_music = True

    volume = pygame.mixer.music.get_volume()  # Get current volume
    muted = volume == 0  # Check if muted

    while run_music:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if back_rect.collidepoint((mouse_x, mouse_y)):
                    return  # Go back to main menu

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:  # Increase volume
                    volume = min(1.0, volume + 0.1)
                    pygame.mixer.music.set_volume(volume)
                elif event.key == pygame.K_DOWN:  # Decrease volume
                    volume = max(0.0, volume - 0.1)
                    pygame.mixer.music.set_volume(volume)
                elif event.key == pygame.K_m:  # Mute/unmute
                    muted = not muted
                    pygame.mixer.music.set_volume(0 if muted else volume)

        # Background color (black for now, update if needed)
        window.fill((0, 0, 0))  # BLACK

        # Draw title
        font = pygame.font.Font(None, 40)  # Ensure font is defined
        title_text = font.render("Music Settings", True, (255, 255, 255))  # WHITE
        title_rect = title_text.get_rect(center=(window.get_width() // 2, window.get_height() // 3))
        window.blit(title_text, title_rect)

        instructions_font = pygame.font.Font(None, 30)  # Slightly smaller font for instructions
        music_text = instructions_font.render("Use UP/DOWN to adjust volume, M to mute", True, (200, 200, 200))  # Light gray
        music_rect = music_text.get_rect(center=(window.get_width() // 2, window.get_height() // 2))
        window.blit(music_text, music_rect)

        # Back button
        back_rect = pygame.Rect(window.get_width() // 2 - 50, window.get_height() - 100, 100, 40)
        back_color = (169, 169, 169) if back_rect.collidepoint(pygame.mouse.get_pos()) else (255, 255, 255)
        pygame.draw.rect(window, back_color, back_rect, border_radius=10)
        back_text = font.render("Back", True, (0, 0, 0))
        window.blit(back_text, (back_rect.x + 30, back_rect.y + 10))

        pygame.display.update()
        clock.tick(30)

def credits_screen(window):
    clock = pygame.time.Clock()
    run_credits = True

    while run_credits:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if back_rect.collidepoint((mouse_x, mouse_y)):
                    return  # Go back to main menu

        # Background color
        window.fill(BLACK)

        # Draw title
        title_text = font.render("Credits", True, WHITE)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        window.blit(title_text, title_rect)

        # Example credit text
        credit_text = font.render("Made by: Your Name", True, WHITE)
        credit_rect = credit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        window.blit(credit_text, credit_rect)

        # Back button
        back_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT - 100, 100, 40)
        back_color = GRAY if back_rect.collidepoint(pygame.mouse.get_pos()) else WHITE
        pygame.draw.rect(window, back_color, back_rect, border_radius=10)
        back_text = font.render("Back", True, BLACK)
        window.blit(back_text, (back_rect.x + 30, back_rect.y + 10))

        pygame.display.update()
        clock.tick(30)

def load_video_background(video_path, width, height):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Video file not found -> {video_path}")
        return None, None

    def update_video():
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (width, height))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            video_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
            return video_surface
        else:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return None

    return cap, update_video

def main_menu(window):
    pygame.mixer.init()  # Initialize the mixer
    music_path = join("assets", "Music", "Royalty free forest music for games.mp3")
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play(-1)  # Loop the music

    run_menu = True
    clock = pygame.time.Clock()
    video_path = join("assets", "Background", "Pixel Art Forest - Background.mp4")
    cap, update_video = load_video_background(video_path, WIDTH, HEIGHT)
    frame_rate = cap.get(cv2.CAP_PROP_FPS) if cap else 30

    # Define button rectangles
    start_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 80, 200, 50)
    music_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 20, 200, 50)
    credits_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 40, 200, 50)
    exit_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)

    while run_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if start_rect.collidepoint((mouse_x, mouse_y)):
                    game_result = main_game(window)
                    if game_result == "exit":
                        return "exit"
                elif music_rect.collidepoint((mouse_x, mouse_y)):
                    music_settings(window)  # Call music settings
                elif credits_rect.collidepoint((mouse_x, mouse_y)):
                    credits_screen(window)  # Call credits screen
                elif exit_rect.collidepoint((mouse_x, mouse_y)):
                    return "exit"

        # Update and display video background
        if cap:
            video_surface = update_video()
            if video_surface:
                window.blit(video_surface, (0, 0))

        # Ensure the font is initialized
        font = pygame.font.Font(None, 40)  # Use a default font if not set

        # Draw buttons **AFTER** the background is drawn
        start_color = (169, 169, 169) if start_rect.collidepoint(pygame.mouse.get_pos()) else (255, 255, 255)
        music_color = (169, 169, 169) if music_rect.collidepoint(pygame.mouse.get_pos()) else (255, 255, 255)
        credits_color = (169, 169, 169) if credits_rect.collidepoint(pygame.mouse.get_pos()) else (255, 255, 255)
        exit_color = (169, 169, 169) if exit_rect.collidepoint(pygame.mouse.get_pos()) else (255, 255, 255)

        pygame.draw.rect(window, start_color, start_rect, border_radius=10)
        pygame.draw.rect(window, music_color, music_rect, border_radius=10)
        pygame.draw.rect(window, credits_color, credits_rect, border_radius=10)
        pygame.draw.rect(window, exit_color, exit_rect, border_radius=10)

        start_text = font.render("Start Game", True, (0, 0, 0))
        music_text = font.render("Music", True, (0, 0, 0))
        credits_text = font.render("Credits", True, (0, 0, 0))
        exit_text = font.render("Exit", True, (0, 0, 0))

        window.blit(start_text, (start_rect.x + 50, start_rect.y + 10))
        window.blit(music_text, (music_rect.x + 75, music_rect.y + 10))
        window.blit(credits_text, (credits_rect.x + 65, credits_rect.y + 10))
        window.blit(exit_text, (exit_rect.x + 80, exit_rect.y + 10))

        pygame.display.update()
        clock.tick(frame_rate)

    if cap:
        cap.release()
    return "exit"

def main_loop(window):
    active_screen = "menu"
    run_game = True

    while run_game:
        if active_screen == "menu":
            menu_result = main_menu(window)
            if menu_result == "exit":
                run_game = False
        elif active_screen == "game":
            game_result = main_game(window)
            if game_result == "exit":
                active_screen = "menu"

    pygame.quit()
    quit()

if __name__ == "__main__":
    main_loop(window)