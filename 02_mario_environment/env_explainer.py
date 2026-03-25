"""
Mario Environment — Visual Explainer
=====================================
This script walks through HOW the game environment was built, step by step.
Press SPACE (or any key) to move to the next step.

Steps:
  0. Raw background image (original 1920×1080 dimensions shown on screen)
  1. The bounding boxes we manually measured on the original image
  2. The scaling math: how 1920×1080 coords map to 800×600
  3. Final scaled platforms placed on screen — each one labelled
  4. The complete environment as the AI agent sees it
"""

import pygame
import sys

# ── Constants (must match mario_env.py exactly) ────────────────────────────────
SCREEN_W   = 800
SCREEN_H   = 600
BG_ORIG_W  = 1920
BG_ORIG_H  = 1080

PLAYER_W, PLAYER_H     = 40, 55
PLATFORM_THICKNESS     = 60
JUMP_VELOCITY          = -16
PLAYER_SPEED           = 6

# The exact coordinates measured on the 1920×1080 background image
# Format: [x1, y1, x2, y2]
ORIGINAL_BOXES = [
    ([392,  1087, 564,  919],  "First Pipe"),
    ([1097, 1087, 1264, 918],  "Second Pipe"),
    ([400,  827,  827,  739],  "Wide Platform"),
    ([32,   824,  120,  739],  "Left Box"),
    ([32,   824,  120,  739],  "Left Box (duplicate — intentional)"),
    ([562,  469,  650,  381],  "High Box"),
    ([1621, 1086, 1706, 907],  "Finish Box (castle gate)"),
]

# Colours
BLACK       = (  0,   0,   0)
WHITE       = (255, 255, 255)
DARK_GREY   = ( 20,  20,  20)
GREY        = ( 60,  60,  60)
BROWN       = (139,  69,  19)
GREEN       = (  0, 200,   0)
RED         = (220,  50,  50)
YELLOW      = (255, 220,   0)
CYAN        = (  0, 200, 220)
ORANGE      = (255, 140,   0)
PURPLE      = (160,  32, 240)

# One colour per platform
BOX_COLOURS = [RED, ORANGE, YELLOW, CYAN, PURPLE, GREEN, (255, 0, 180)]


# ── Helper ─────────────────────────────────────────────────────────────────────
def scale_rect(coords, src_w, src_h, dst_w, dst_h):
    """Convert [x1,y1,x2,y2] in src space to a pygame.Rect in dst space."""
    x1, y1, x2, y2 = coords
    left   = min(x1, x2)
    top    = min(y1, y2)
    width  = abs(x2 - x1)
    height = abs(y2 - y1)
    sx = int(round(left   * dst_w / src_w))
    sy = int(round(top    * dst_h / src_h))
    sw = max(4, int(round(width  * dst_w / src_w)))
    sh = max(4, int(round(height * dst_h / src_h)))
    return pygame.Rect(sx, sy, sw, sh)


def draw_text(surface, text, x, y, font, colour=WHITE, center=False):
    surf = font.render(text, True, colour)
    rect = surf.get_rect()
    if center:
        rect.centerx = x
        rect.y = y
    else:
        rect.x = x
        rect.y = y
    surface.blit(surf, rect)


def draw_step_indicator(surface, step, total, font_small, screen_w, screen_h):
    txt = f"Step {step + 1} / {total}   |   SPACE or any key to continue   |   ESC to quit"
    draw_text(surface, txt, screen_w // 2, screen_h - 28, font_small,
              colour=(180, 180, 180), center=True)


# ── Steps ──────────────────────────────────────────────────────────────────────

def step_0_raw_background(surface, background, fonts, screen_w, screen_h, total):
    """Show the raw background and explain where it came from."""
    surface.blit(background, (0, 0))

    # Dark overlay so text is readable
    overlay = pygame.Surface((screen_w, 120), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    draw_text(surface, "STEP 1 — The Background Image", screen_w // 2, 10,
              fonts['title'], YELLOW, center=True)
    draw_text(surface, f"Original size: {BG_ORIG_W} × {BG_ORIG_H} px   →   scaled to {screen_w} × {screen_h} for the game window",
              screen_w // 2, 50, fonts['body'], WHITE, center=True)
    draw_text(surface, "This is the raw image. Next we'll mark the platforms on it.",
              screen_w // 2, 80, fonts['body'], (200, 200, 200), center=True)

    draw_step_indicator(surface, 0, total, fonts['small'], screen_w, screen_h)


def step_1_original_boxes(surface, background, fonts, screen_w, screen_h, total):
    """
    Show the bounding boxes as measured on the ORIGINAL 1920×1080 image,
    but visualised on the scaled-down background so the viewer can see
    where they actually are.
    """
    surface.blit(background, (0, 0))

    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    surface.blit(overlay, (0, 0))

    for i, (coords, label) in enumerate(ORIGINAL_BOXES):
        rect = scale_rect(coords, BG_ORIG_W, BG_ORIG_H, screen_w, screen_h)
        colour = BOX_COLOURS[i % len(BOX_COLOURS)]
        pygame.draw.rect(surface, colour, rect, 3)

        # Label above the box
        draw_text(surface, label, rect.x, max(rect.y - 18, 0),
                  fonts['small'], colour)

    # Header
    header = pygame.Surface((screen_w, 60), pygame.SRCALPHA)
    header.fill((0, 0, 0, 200))
    surface.blit(header, (0, 0))
    draw_text(surface, "STEP 2 — Manually Measured Bounding Boxes",
              screen_w // 2, 8, fonts['title'], YELLOW, center=True)
    draw_text(surface, f"Coordinates were measured on the original {BG_ORIG_W}×{BG_ORIG_H} image using an image editor",
              screen_w // 2, 36, fonts['small'], WHITE, center=True)

    draw_step_indicator(surface, 1, total, fonts['small'], screen_w, screen_h)


def step_2_scaling_math(surface, fonts, screen_w, screen_h, total):
    """Explain the coordinate scaling formula with a worked example."""
    surface.fill(DARK_GREY)

    draw_text(surface, "STEP 3 — The Scaling Math", screen_w // 2, 20,
              fonts['title'], YELLOW, center=True)

    lines = [
        ("The Problem:", WHITE, 0),
        ("  Boxes were measured on a 1920×1080 image.", (200,200,200), 0),
        ("  The game window is only 800×600.", (200,200,200), 0),
        ("", WHITE, 0),
        ("The Formula:", WHITE, 0),
        ("  scale_x  =  screen_width  / original_width   =  800 / 1920  =  0.4167", CYAN, 0),
        ("  scale_y  =  screen_height / original_height  =  600 / 1080  =  0.5556", CYAN, 0),
        ("", WHITE, 0),
        ("  screen_x  =  round( original_x * scale_x )", CYAN, 0),
        ("  screen_y  =  round( original_y * scale_y )", CYAN, 0),
        ("", WHITE, 0),
        ("Worked Example — 'First Pipe'  [392, 1087, 564, 919]:", WHITE, 0),
        ("  left   = min(392, 564) = 392   →   screen_x = round(392 × 0.4167) = 163", ORANGE, 0),
        ("  top    = min(919,1087) = 919   →   screen_y = round(919 × 0.5556) = 511", ORANGE, 0),
        ("  width  = |564 - 392|   = 172   →   screen_w = round(172 × 0.4167) =  72", ORANGE, 0),
        ("  height = |1087 - 919|  = 168   →   screen_h = round(168 × 0.5556) =  93", ORANGE, 0),
        ("", WHITE, 0),
        ("  Result: pygame.Rect(163, 511, 72, 93)  ← this is the pipe on screen", GREEN, 0),
    ]

    y = 75
    for text, colour, _ in lines:
        draw_text(surface, text, 40, y, fonts['body'], colour)
        y += 26

    draw_step_indicator(surface, 2, total, fonts['small'], screen_w, screen_h)


def step_3_one_by_one(surface, background, fonts, step_index,
                       screen_w, screen_h, total_steps):
    """Reveal platforms one by one so viewer can see each being placed."""
    # Which sub-step (0 = floor only, 1..N = platforms)
    sub = step_index - 3      # step_index 3 → sub 0 (floor), 4 → sub 1, etc.
    num_to_show = sub          # how many ORIGINAL_BOXES to show (0-based)

    surface.blit(background, (0, 0))

    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surface.blit(overlay, (0, 0))

    # Always draw the floor
    floor = pygame.Rect(0, screen_h - PLATFORM_THICKNESS, screen_w, PLATFORM_THICKNESS)
    pygame.draw.rect(surface, BROWN, floor)
    draw_text(surface, "Floor (always present)", 10,
              screen_h - PLATFORM_THICKNESS + 5, fonts['small'], WHITE)

    # Reveal platforms up to num_to_show
    for i in range(min(num_to_show, len(ORIGINAL_BOXES))):
        coords, label = ORIGINAL_BOXES[i]
        rect = scale_rect(coords, BG_ORIG_W, BG_ORIG_H, screen_w, screen_h)
        colour = BOX_COLOURS[i % len(BOX_COLOURS)]
        is_finish = (i == len(ORIGINAL_BOXES) - 1)

        if is_finish:
            pygame.draw.rect(surface, colour, rect, 3)  # outline only (invisible in-game)
            draw_text(surface, f"[{i+1}] {label}  ← invisible trigger zone",
                      rect.x, max(rect.y - 18, 0), fonts['small'], colour)
        else:
            pygame.draw.rect(surface, colour, rect)
            draw_text(surface, f"[{i+1}] {label}",
                      rect.x, max(rect.y - 18, 0), fonts['small'], colour)

    # Header
    header = pygame.Surface((screen_w, 60), pygame.SRCALPHA)
    header.fill((0, 0, 0, 200))
    surface.blit(header, (0, 0))

    step_label = f"STEP {step_index + 1} — Platform {num_to_show} / {len(ORIGINAL_BOXES)}"
    if num_to_show == 0:
        step_label = "STEP 4 — Building the Environment (floor first)"
    draw_text(surface, step_label, screen_w // 2, 8,
              fonts['title'], YELLOW, center=True)

    if num_to_show < len(ORIGINAL_BOXES):
        if num_to_show < len(ORIGINAL_BOXES):
            next_label = ORIGINAL_BOXES[num_to_show][1] if num_to_show < len(ORIGINAL_BOXES) else ""
            draw_text(surface, f"Next: {next_label}",
                      screen_w // 2, 36, fonts['small'], (180, 180, 180), center=True)
    else:
        draw_text(surface, "All platforms placed!",
                  screen_w // 2, 36, fonts['small'], GREEN, center=True)

    draw_step_indicator(surface, step_index, total_steps, fonts['small'], screen_w, screen_h)


def step_final(surface, background, fonts, screen_w, screen_h, total):
    """Show the complete environment as it appears in the game."""
    surface.blit(background, (0, 0))

    # Floor
    floor = pygame.Rect(0, screen_h - PLATFORM_THICKNESS, screen_w, PLATFORM_THICKNESS)
    pygame.draw.rect(surface, BROWN, floor)

    # Platforms
    for i, (coords, label) in enumerate(ORIGINAL_BOXES):
        rect = scale_rect(coords, BG_ORIG_W, BG_ORIG_H, screen_w, screen_h)
        is_finish = (i == len(ORIGINAL_BOXES) - 1)
        if is_finish:
            pygame.draw.rect(surface, GREEN, rect, 3)
        else:
            pygame.draw.rect(surface, BROWN, rect)

    # Player start position
    player_rect = pygame.Rect(100, screen_h - PLAYER_H - PLATFORM_THICKNESS, PLAYER_W, PLAYER_H)
    pygame.draw.rect(surface, RED, player_rect, border_radius=4)
    draw_text(surface, "START", player_rect.x - 5, player_rect.y - 20,
              fonts['small'], RED)

    # Finish arrow
    finish_coords = ORIGINAL_BOXES[-1][0]
    finish_rect = scale_rect(finish_coords, BG_ORIG_W, BG_ORIG_H, screen_w, screen_h)
    draw_text(surface, "GOAL ↓", finish_rect.x - 10, finish_rect.y - 22,
              fonts['small'], GREEN)

    # Header
    header = pygame.Surface((screen_w, 60), pygame.SRCALPHA)
    header.fill((0, 0, 0, 200))
    surface.blit(header, (0, 0))
    draw_text(surface, "STEP FINAL — Complete Environment (as seen in the game)",
              screen_w // 2, 8, fonts['title'], YELLOW, center=True)
    draw_text(surface, "Red box = player start   |   Green outline = finish/goal trigger",
              screen_w // 2, 36, fonts['small'], WHITE, center=True)

    draw_step_indicator(surface, total - 1, total, fonts['small'], screen_w, screen_h)


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Mario Environment — Visual Explainer")
    clock = pygame.time.Clock()

    fonts = {
        'title': pygame.font.SysFont("monospace", 18, bold=True),
        'body':  pygame.font.SysFont("monospace", 15),
        'small': pygame.font.SysFont("monospace", 13),
    }

    try:
        background = pygame.image.load("super_mario_background.jpg").convert()
        background = pygame.transform.scale(background, (SCREEN_W, SCREEN_H))
    except FileNotFoundError:
        background = pygame.Surface((SCREEN_W, SCREEN_H))
        background.fill((100, 149, 237))   # cornflower blue fallback

    # Total steps:
    # 0: raw bg
    # 1: original boxes
    # 2: scaling math
    # 3..3+N: one-by-one (floor + N platforms)
    # last: final complete view
    one_by_one_steps = len(ORIGINAL_BOXES) + 1   # floor + each platform
    TOTAL_STEPS = 3 + one_by_one_steps + 1
    current_step = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                else:
                    current_step = min(current_step + 1, TOTAL_STEPS - 1)
            if event.type == pygame.MOUSEBUTTONDOWN:
                current_step = min(current_step + 1, TOTAL_STEPS - 1)

        screen.fill(DARK_GREY)

        if current_step == 0:
            step_0_raw_background(screen, background, fonts, SCREEN_W, SCREEN_H, TOTAL_STEPS)
        elif current_step == 1:
            step_1_original_boxes(screen, background, fonts, SCREEN_W, SCREEN_H, TOTAL_STEPS)
        elif current_step == 2:
            step_2_scaling_math(screen, fonts, SCREEN_W, SCREEN_H, TOTAL_STEPS)
        elif current_step == TOTAL_STEPS - 1:
            step_final(screen, background, fonts, SCREEN_W, SCREEN_H, TOTAL_STEPS)
        else:
            step_3_one_by_one(screen, background, fonts, current_step,
                               SCREEN_W, SCREEN_H, TOTAL_STEPS)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
