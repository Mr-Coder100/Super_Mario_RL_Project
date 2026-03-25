# mario_env.py

import pygame
import gymnasium as gym
from gymnasium import spaces
import numpy as np

# --- Config ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DEBUG_SHOW_HITBOXES = True
TIME_LIMIT = 15
GROUND_BROWN = (139, 69, 19)
HITBOX_COLOR = (255, 0, 0)
FINISH_COLOR = (0, 255, 0)
PLAYER_W, PLAYER_H = 40, 55
PLAYER_SPEED = 6
JUMP_VELOCITY = -16
GRAVITY = 0.8
PLATFORM_THICKNESS = 60
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

class MarioPygameEnv(gym.Env):
    metadata = {'render_modes': ['human']}

    def __init__(self, render_mode=None):
        super(MarioPygameEnv, self).__init__()
        
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.TIME_LIMIT = TIME_LIMIT
        self.PLAYER_W, self.PLAYER_H = PLAYER_W, PLAYER_H
        self.PLAYER_SPEED = PLAYER_SPEED
        self.JUMP_VELOCITY = JUMP_VELOCITY
        self.GRAVITY = GRAVITY
        self.PLATFORM_THICKNESS = PLATFORM_THICKNESS
        self.render_mode = render_mode

        self.observation_space = spaces.Box(
    low=np.array([0, 0, -PLAYER_SPEED, JUMP_VELOCITY]),
    high=np.array([SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_SPEED, -JUMP_VELOCITY]),
    dtype=np.float32
)
        self.action_space = spaces.Discrete(4)

        self.platforms = []
        self.player = None
        self.finish_box = None
        self.steps = 0
        self.screen = None

    def _get_obs(self):
        return np.array([self.player.rect.x, self.player.rect.y, self.player.vx, self.player.vy], dtype=np.float32)

    def _get_info(self):
        return {"player_pos": (self.player.rect.x, self.player.rect.y)}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.platforms = []
        
        for i, coords in enumerate(ORIGINAL_BOXES):
            sw, sh, sx, sy, _, _ = original_to_screen_rect(coords, BG_ORIG_SIZE[0], BG_ORIG_SIZE[1], self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
            rect = pygame.Rect(sx, sy, sw, sh)
            if i == len(ORIGINAL_BOXES) - 1:
                self.finish_box = Platform(rect)
            else:
                self.platforms.append(Platform(rect))
        
        floor_rect = pygame.Rect(0, self.SCREEN_HEIGHT - self.PLATFORM_THICKNESS, self.SCREEN_WIDTH, self.PLATFORM_THICKNESS)
        self.platforms.append(Platform(floor_rect))

        player_rect = pygame.Rect(100, self.SCREEN_HEIGHT - self.PLAYER_H - self.PLATFORM_THICKNESS, self.PLAYER_W, self.PLAYER_H)
        self.player = Player(player_rect)
        self.steps = 0
        
        if self.render_mode == "human":
            pygame.init()
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            pygame.display.set_caption("Mario RL Agent")
            self.background = pygame.image.load("super_mario_background.jpg").convert()
            self.background = pygame.transform.scale(self.background, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            self.raw_sprite = pygame.image.load("super_mario_sprite.png").convert_alpha()
            sprite_flipped_at_start = pygame.transform.flip(self.raw_sprite, True, False)
            self.img_right = pygame.transform.scale(sprite_flipped_at_start, (self.PLAYER_W, self.PLAYER_H))
            self.img_left = pygame.transform.flip(self.img_right, True, False)
        
        observation = self._get_obs()
        info = self._get_info()
        return observation, info

    def step(self, action):
        self.steps += 1
        
        if action == 0: self.player.vx = -self.PLAYER_SPEED
        elif action == 1: self.player.vx = self.PLAYER_SPEED
        elif action == 2:
            on_ground = False
            self.player.rect.y += 2
            for platform in self.platforms:
                if self.player.rect.colliderect(platform.rect):
                    on_ground = True
                    break
            self.player.rect.y -= 2
            if on_ground: self.player.vy = self.JUMP_VELOCITY
            else: self.player.vy = self.player.vy + self.GRAVITY if self.player.vy else 1
        elif action == 3: self.player.vx = 0
        
        self.player.vy = self.player.vy + self.GRAVITY if self.player.vy else 1
        self.player.rect.x += self.player.vx
        
        for platform in self.platforms:
            if self.player.rect.colliderect(platform.rect):
                if self.player.vx > 0: self.player.rect.right = platform.rect.left
                elif self.player.vx < 0: self.player.rect.left = platform.rect.right
        
        self.player.rect.y += self.player.vy
        for platform in self.platforms:
            if self.player.rect.colliderect(platform.rect):
                if self.player.vy > 0: self.player.rect.bottom = platform.rect.top; self.player.vy = 0
                elif self.player.vy < 0: self.player.rect.top = platform.rect.bottom; self.player.vy = 0
        
        if self.player.rect.y > self.SCREEN_HEIGHT - self.PLAYER_H:
            self.player.rect.y = self.SCREEN_HEIGHT - self.PLAYER_H
            self.player.vy = 0

        reward = -0.1
        terminated = False
        truncated = False
        
        if self.finish_box and self.player.rect.colliderect(self.finish_box.rect):
            reward = 100; terminated = True
        if self.player.rect.right < 0 or self.player.rect.left > self.SCREEN_WIDTH or self.player.rect.top > self.SCREEN_HEIGHT:
            reward = -100; terminated = True
        if self.steps >= self.TIME_LIMIT * 60:
            truncated = True
        
        observation = self._get_obs()
        info = self._get_info()
        
        if self.render_mode == "human":
            self.render()

        return observation, reward, terminated, truncated, info

    def render(self):
        if self.screen is None: return
        self.screen.blit(self.background, (0, 0))
        for p in self.platforms:
            pygame.draw.rect(self.screen, GROUND_BROWN, p.rect)
        player_image = self.img_right if self.player.vx >= 0 else self.img_left
        self.screen.blit(player_image, self.player.rect)
        pygame.display.flip()

    def close(self):
        if self.screen:
            pygame.quit()