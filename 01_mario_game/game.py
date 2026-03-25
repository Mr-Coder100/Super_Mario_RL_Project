# final working model 
import pygame
import sys

# --- Config ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DEBUG_SHOW_HITBOXES = False   # set False to hide hitboxes
TIME_LIMIT = 15              # seconds before truncate (set lower if you want)

# Colors (RGB)w
GROUND_BROWN = (139, 69, 19,0)
HITBOX_COLOR = (255, 0, 0)   # outline color for debug
FINISH_COLOR = (0, 255, 0)

# Player constants
PLAYER_W, PLAYER_H = 40, 55
PLAYER_SPEED = 6
JUMP_VELOCITY = -16
GRAVITY = 0.8
PLATFORM_THICKNESS = 60

# --- Original rectangles (as you provided) ---
ORIGINAL_BOXES = [
    [392, 1087, 564, 919],   # first_pipe
    [1097, 1087, 1264, 918], # second_pipe
    [400, 827, 827, 739],    # second_box
    [32, 824, 120, 739],     # first_box
    [32, 824, 120, 739],     # third_box (Not implemented knowingly
    [562, 469, 650, 381],    # fourth_box
    [1621, 1086, 1706, 907], # invisible_finishing_box (castle gate)
]

# --- Helper: convert original coords -> screen rect ---
def original_to_screen_rect(coords, bg_w, bg_h, screen_w, screen_h):
    x1, y1, x2, y2 = coords
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    scale_x = screen_w / bg_w
    scale_y = screen_h / bg_h

    sx = int(round(left * scale_x))
    sy = int(round(top * scale_y))
    sw = int(round(width * scale_x))
    sh = int(round(height * scale_y))

    return sw, sh, sx, sy, scale_x, scale_y

# --- Sprites ---
class Player(pygame.sprite.Sprite):
    def __init__(self, surf_right, surf_left):
        super().__init__()
        self.image_right = surf_right
        self.image_left = surf_left
        self.image = self.image_right
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = SCREEN_HEIGHT - self.rect.height - PLATFORM_THICKNESS
        self.vx = 0
        self.vy = 0
        self.level = None

    def update(self):
        self.vy = self.vy + GRAVITY if self.vy else 1
        self.rect.x += self.vx
        if self.vx > 0:
            self.image = self.image_right
        elif self.vx < 0:
            self.image = self.image_left

        # Horizontal collisions
        for block in pygame.sprite.spritecollide(self, self.level.platforms, False):
            if self.vx > 0:
                self.rect.right = block.rect.left
            elif self.vx < 0:
                self.rect.left = block.rect.right

        # Vertical movement
        self.rect.y += self.vy
        for block in pygame.sprite.spritecollide(self, self.level.platforms, False):
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

        # Clamp to floor
        if self.rect.y > SCREEN_HEIGHT - self.rect.height:
            self.rect.y = SCREEN_HEIGHT - self.rect.height
            self.vy = 0

    def jump(self):
        self.rect.y += 2
        hits = pygame.sprite.spritecollide(self, self.level.platforms, False)
        self.rect.y -= 2
        if hits:
            self.vy = JUMP_VELOCITY

    def go_left(self):  self.vx = -PLAYER_SPEED
    def go_right(self): self.vx = PLAYER_SPEED
    def stop(self):     self.vx = 0

class Platform(pygame.sprite.Sprite):
    def __init__(self, w, h, x, y, visible=True):
        super().__init__()
        self.image = pygame.Surface((max(1,int(w)), max(1,int(h))), pygame.SRCALPHA)
        if visible:
            self.image.fill(GROUND_BROWN)
        self.rect = self.image.get_rect(topleft=(int(x), int(y)))

class Level:
    def __init__(self, player, background_surf, debug=DEBUG_SHOW_HITBOXES):
        self.player = player
        self.background = background_surf
        self.platforms = pygame.sprite.Group()
        self.debug = debug
        self.finish_box = None

    def draw(self, screen):
        screen.blit(self.background, (0,0))
        self.platforms.draw(screen)
        if self.debug:
            for p in self.platforms:
                pygame.draw.rect(screen, HITBOX_COLOR, p.rect, 2)
            if self.finish_box:
                pygame.draw.rect(screen, FINISH_COLOR, self.finish_box.rect, 2)

class LevelFromOriginal(Level):
    def __init__(self, player, background_surf, bg_original_size, debug=DEBUG_SHOW_HITBOXES):
        super().__init__(player, background_surf, debug)
        bg_w, bg_h = bg_original_size

        for i, coords in enumerate(ORIGINAL_BOXES):
            sw, sh, sx, sy, _, _ = original_to_screen_rect(coords, bg_w, bg_h, SCREEN_WIDTH, SCREEN_HEIGHT)
            if i == len(ORIGINAL_BOXES) - 1:  # last box = finish
                self.finish_box = Platform(sw, sh, sx, sy, visible=False)
            else:
                block = Platform(sw, sh, sx, sy, visible=True)
                self.platforms.add(block)

        floor = Platform(SCREEN_WIDTH, PLATFORM_THICKNESS, 0, SCREEN_HEIGHT - PLATFORM_THICKNESS, visible=True)
        self.platforms.add(floor)

# --- Main ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mario — Win/Lose/Truncate")
    clock = pygame.time.Clock()

    raw_sprite = pygame.image.load("super_mario_sprite.png").convert_alpha()
    background = pygame.image.load("super_mario_background.jpg").convert()
    bg_orig_w, bg_orig_h = background.get_width(), background.get_height()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    sprite_flipped_at_start = pygame.transform.flip(raw_sprite, True, False)
    img_right = pygame.transform.scale(sprite_flipped_at_start, (PLAYER_W, PLAYER_H))
    img_left = pygame.transform.flip(img_right, True, False)

    player = Player(img_right, img_left)
    level = LevelFromOriginal(player, background, (bg_orig_w, bg_orig_h), debug=DEBUG_SHOW_HITBOXES)
    player.level = level

    all_sprites = pygame.sprite.Group(player)

    start_ticks = pygame.time.get_ticks()
    game_over = False
    result = None

    font_big = pygame.font.SysFont("Arial", 42, bold=True)
    font_small = pygame.font.SysFont("Arial", 20)

    while True:
        elapsed = (pygame.time.get_ticks() - start_ticks) / 1000.0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_q:   # Q to quit
                    pygame.quit()
                    sys.exit()
                if ev.key == pygame.K_r and game_over:
                    main()
                    return
                if not game_over:
                    if ev.key == pygame.K_LEFT:  player.go_left()
                    elif ev.key == pygame.K_RIGHT: player.go_right()
                    elif ev.key in (pygame.K_UP, pygame.K_SPACE): player.jump()
            if ev.type == pygame.KEYUP and not game_over:
                if ev.key in (pygame.K_LEFT, pygame.K_RIGHT): player.stop()

        if not game_over and elapsed >= TIME_LIMIT:
            result = "truncate"
            print("TIME OVER (Truncate)")
            game_over = True

        if not game_over:
            all_sprites.update()
            if player.rect.right < 0 or player.rect.left > SCREEN_WIDTH or player.rect.top > SCREEN_HEIGHT:
                result = "lose"
                print("YOU LOSE! (Out of bounds)")
                game_over = True
            if level.finish_box and player.rect.colliderect(level.finish_box.rect):
                result = "win"
                print("YOU WIN! (Castle gate reached)")
                game_over = True

        level.draw(screen)
        all_sprites.draw(screen)

        time_text = f"Time: {int(elapsed)}s / {TIME_LIMIT}s"
        text_surf = font_small.render(time_text, True, (255,255,255))
        screen.blit(text_surf, (10, 10))

        if game_over:
            if result == "win":
                msg = "🎉 YOU WIN! — Press R to Restart | Q to Quit"
                color = (0, 200, 0)
            elif result == "lose":
                msg = "💀 YOU LOSE! — Press R to Restart | Q to Quit"
                color = (200, 0, 0)
            else:
                msg = "⌛ TIME OVER! — Press R to Restart | Q to Quit"
                color = (200, 200, 0)

            msg_surf = font_big.render(msg, True, color)
            screen.blit(msg_surf, ((SCREEN_WIDTH - msg_surf.get_width()) // 2,
                                   (SCREEN_HEIGHT - msg_surf.get_height()) // 2))

        if DEBUG_SHOW_HITBOXES:
            for p in level.platforms:
                pygame.draw.rect(screen, HITBOX_COLOR, p.rect, 2)
            if level.finish_box:
                pygame.draw.rect(screen, FINISH_COLOR, level.finish_box.rect, 2)

        pygame.display.flip()
        clock.tick(60) ##Its the FPS in simple words

if __name__ == "__main__":
    main()
