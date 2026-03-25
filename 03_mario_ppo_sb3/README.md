# 03 — Mario PPO Agent (Stable Baselines3)

A PPO agent trained to play Mario using Stable Baselines3.
The environment follows the Gymnasium API so it works with any SB3 algorithm out of the box.

## Setup

```bash
pip install pygame stable-baselines3 numpy
```

Place `super_mario_background.jpg` and `super_mario_sprite.png` in the same folder.

## Train

```bash
python train_agent.py
```

Trains for 50,000 timesteps. Saves checkpoints to `checkpoints/` every 10,000 steps
and the final model as `final_ppo_mario_model.zip`.

## Evaluate (watch the agent play)

```bash
python evaluate_agent.py
```

Loads `final_ppo_mario_model.zip` and runs 5 episodes with the pygame window open.

## Environment details

| Property | Value |
|----------|-------|
| Observation space | `Box(4,)` — [x, y, vx, vy] |
| Action space | `Discrete(4)` — left, right, jump, stop |
| Win reward | +100 (reach the castle) |
| Lose reward | −100 (fall off screen) |
| Step penalty | −0.1 per step (encourages speed) |
| Time limit | 15 seconds (~900 steps) |

## File structure

```
03_mario_ppo_sb3/
├── mario_env.py              ← Gymnasium-compatible environment
├── train_agent.py            ← PPO training via SB3
├── evaluate_agent.py         ← Watch the trained agent play
├── final_ppo_mario_model.zip ← Pre-trained weights (included)
├── super_mario_background.jpg
├── super_mario_sprite.png
└── README.md
```
