# 02 — Mario Environment Explainer

A visual, step-by-step walkthrough of how the Mario game environment was built.
Run this before looking at the AI code — it explains the foundation everything else is built on.

## Setup

```bash
pip install pygame
```

Place `super_mario_background.jpg` in the same folder, then:

```bash
python env_explainer.py
```

Press **SPACE** (or any key) to move through the steps. **ESC** to quit.

## What it shows

| Step | What you see |
|------|-------------|
| 1 | The raw background image scaled to the 800×600 game window |
| 2 | The bounding boxes manually measured on the original 1920×1080 image, overlaid on the background — each platform colour-coded and labelled |
| 3 | The scaling formula explained with a worked example (First Pipe walkthrough) |
| 4–10 | Platforms placed one by one — floor first, then each box/pipe/platform in order |
| Final | The complete environment as it appears in the game, with player start and goal marked |

## Why this matters

The environment has no physics engine or tilemap — every solid surface is a manually
measured rectangle converted from the original image coordinates to screen coordinates
using simple scale factors:

```
scale_x = screen_width  / original_width   # 800 / 1920 = 0.4167
scale_y = screen_height / original_height  # 600 / 1080 = 0.5556

screen_x = round(original_x * scale_x)
screen_y = round(original_y * scale_y)
```

The finish zone (castle gate) is an invisible trigger box — the same math, but drawn
as an outline only and not filled, so the player can walk through it to trigger a win.
