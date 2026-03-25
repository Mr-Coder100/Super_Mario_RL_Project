# mario_env_custom.py

import pygame
import numpy as np

# --- Config ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TIME_LIMIT = 15
PLAYER_W, PLAYER_H = 40, 55
PLAYER_SPEED = 6
JUMP_VELOCITY = -16
GRAVITY = 0.8
PLATFORM_THICKNESS = 60
GROUND_BROWN = (139, 69, 19)
ORIGINAL_BOXES = [
    [392, 1087, 564, 919],
    [1097, 1087, 1264, 918],
    [400, 827, 827, 739],
    [32, 824, 120, 739],
    [32, 824, 120, 739],
    [562, 469, 650, 381],
    [1621, 1086, 1706, 907],
]
BG_ORIG_SIZE = (1920, 1080)

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

class Player:
    def __init__(self, rect, vx=0, vy=0):
        self.rect = rect
        self.vx = vx
        self.vy = vy

class Platform:
    def __init__(self, rect):
        self.rect = rect

class MarioPygameEnvironment:
    def __init__(self, render_mode=False):
        self.render_mode = render_mode
        self.player = None
        self.platforms = []
        self.finish_box = None
        self.steps = 0
        self.screen = None
        self.background = None
        self.img_right = None
        self.img_left = None

        if self.render_mode:
            pygame.init()
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("Mario RL Agent")
            self.background = pygame.image.load("super_mario_background.jpg").convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            raw = pygame.image.load("super_mario_sprite.png").convert_alpha()
            self.img_right = pygame.transform.scale(
                pygame.transform.flip(raw, True, False), (PLAYER_W, PLAYER_H))
            self.img_left = pygame.transform.flip(self.img_right, True, False)

        self.reset()

    def reset(self):
        self.platforms = []
        for i, coords in enumerate(ORIGINAL_BOXES):
            sw, sh, sx, sy, _, _ = original_to_screen_rect(
                coords, BG_ORIG_SIZE[0], BG_ORIG_SIZE[1], SCREEN_WIDTH, SCREEN_HEIGHT)
            rect = pygame.Rect(sx, sy, sw, sh)
            if i == len(ORIGINAL_BOXES) - 1:
                self.finish_box = Platform(rect)
            else:
                self.platforms.append(Platform(rect))
        floor_rect = pygame.Rect(0, SCREEN_HEIGHT - PLATFORM_THICKNESS, SCREEN_WIDTH, PLATFORM_THICKNESS)
        self.platforms.append(Platform(floor_rect))
        player_rect = pygame.Rect(100, SCREEN_HEIGHT - PLAYER_H - PLATFORM_THICKNESS, PLAYER_W, PLAYER_H)
        self.player = Player(player_rect)
        self.steps = 0
        return self.get_state()

    def get_state(self):
        return np.array(
            [self.player.rect.x, self.player.rect.y, self.player.vx, self.player.vy],
            dtype=np.float32)

    def step(self, action):
        self.steps += 1

        # Action mapping
        if action == 0:
            self.player.vx = -PLAYER_SPEED
        elif action == 1:
            self.player.vx = PLAYER_SPEED
        elif action == 2:
            on_ground = False
            self.player.rect.y += 2
            for p in self.platforms:
                if self.player.rect.colliderect(p.rect):
                    on_ground = True
                    break
            self.player.rect.y -= 2
            if on_ground:
                self.player.vy = JUMP_VELOCITY
            else:
                self.player.vy = self.player.vy + GRAVITY if self.player.vy else 1
        elif action == 3:
            self.player.vx = 0

        # Apply gravity
        self.player.vy = self.player.vy + GRAVITY if self.player.vy else 1

        # Horizontal movement + collision
        self.player.rect.x += self.player.vx
        for p in self.platforms:
            if self.player.rect.colliderect(p.rect):
                if self.player.vx > 0:
                    self.player.rect.right = p.rect.left
                elif self.player.vx < 0:
                    self.player.rect.left = p.rect.right

        # Vertical movement + collision
        self.player.rect.y += self.player.vy
        for p in self.platforms:
            if self.player.rect.colliderect(p.rect):
                if self.player.vy > 0:
                    self.player.rect.bottom = p.rect.top
                    self.player.vy = 0
                elif self.player.vy < 0:
                    self.player.rect.top = p.rect.bottom
                    self.player.vy = 0

        # Floor clamp
        if self.player.rect.y > SCREEN_HEIGHT - PLAYER_H:
            self.player.rect.y = SCREEN_HEIGHT - PLAYER_H
            self.player.vy = 0

        # Reward and termination
        reward = -0.1
        terminated = False

        if self.finish_box and self.player.rect.colliderect(self.finish_box.rect):
            reward = 100
            terminated = True

        if (self.player.rect.right < 0 or
                self.player.rect.left > SCREEN_WIDTH or
                self.player.rect.top > SCREEN_HEIGHT):
            reward = -100
            terminated = True

        if self.render_mode:
            self._render()

        return self.get_state(), reward, terminated

    def _render(self):
        if self.screen is None:
            return
        self.screen.blit(self.background, (0, 0))
        for p in self.platforms:
            pygame.draw.rect(self.screen, GROUND_BROWN, p.rect)
        if self.finish_box:
            pygame.draw.rect(self.screen, (0, 200, 0), self.finish_box.rect, 3)
        img = self.img_right if self.player.vx >= 0 else self.img_left
        self.screen.blit(img, self.player.rect)
        pygame.display.flip()

    def close(self):
        if self.render_mode and self.screen:
            pygame.quit()
            self.screen = None