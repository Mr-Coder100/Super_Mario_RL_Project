# 01 — Super Mario (Playable Game)

A playable Super Mario-style platformer built with pygame.

## Setup

```bash
pip install pygame
```

Make sure `super_mario_background.jpg` and `super_mario_sprite.png` are in the same folder.

## Run

```bash
python game.py
```

## Controls

| Key | Action |
|-----|--------|
| ← → Arrow keys | Move left / right |
| ↑ or SPACE | Jump |
| R | Restart after game over |
| Q | Quit |

## How it works

- Platforms are rectangles measured manually on the original 1920×1080 background image and scaled down to the 800×600 game window
- The finish trigger is an invisible box at the castle gate on the right side
- Falling off screen or running out of time counts as a loss
- See `02_mario_environment` for a visual walkthrough of how the platforms were built
