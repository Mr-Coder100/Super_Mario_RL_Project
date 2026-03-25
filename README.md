# Mario RL — Four Ways

Four progressive implementations of Super Mario, from a playable game to a self-learning AI.

```
mario-rl/
├── 01_mario_game/          ← Play it yourself
├── 02_mario_environment/   ← Visual explainer: how the environment was built
├── 03_mario_ppo_sb3/       ← PPO agent via Stable Baselines3 (gym-based)
└── 04_mario_ppo_custom/    ← REINFORCE agent, pure PyTorch, no gym
```

```
mario_RL_file list
├── 01_mario_game/
│   ├── game.py                        
│   ├── super_mario_background.jpg
│   ├── super_mario_sprite.png
│   └── README.md
|
├── 02_mario_environment/
│   ├── env_explainer.py                        
│   ├── super_mario_background.jpg
│   ├── super_mario_sprite.png
│   └── README.md
|
├── 03_mario_ppo_sb3/                  ← PPO via Stable Baselines3
│   ├── mario_env.py
│   ├── train_agent.py
│   ├── evaluate_agent.py
│   ├── final_ppo_mario_model.zip
│   ├── super_mario_background.jpg
│   ├── super_mario_sprite.png
│   └── README.md
│
└── 04_mario_ppo_custom/               ← Custom PPO, no gymnasium library
    ├── env_without_gym.py
    ├── policy_without_gym.py
    ├── train_agent_without_gym.py
    ├── evaluate_without_gym.py
    ├── custom_actor.pth
    ├── custom_critic.pth
    ├── super_mario_background.jpg
    ├── super_mario_sprite.png
    └── README.md
---

## 01 — Mario Game (Playable)
**Stack:** Python, pygame  
**What it is:** The classic Mario platformer. Arrow keys to move, reach the castle to win.
```bash
cd 01_mario_game && python game.py
```

---

## 02 — Environment Explainer
**Stack:** Python, pygame  
**What it is:** A visual step-by-step walkthrough of how the game environment was built —
how the platforms were manually measured on the background image and scaled to the game window.
Press SPACE to advance through each step.
```bash
cd 02_mario_environment && python env_explainer.py
```

---

## 03 — PPO Agent (Stable Baselines3)
**Stack:** Python, PyTorch, Stable Baselines3, gymnasium  
**What it is:** A PPO agent trained using Stable Baselines3. The environment implements
the Gymnasium API so it's compatible with any SB3 algorithm.
```bash
cd 03_mario_ppo_sb3
python train_agent.py      # train
python evaluate_agent.py   # watch
```

---

## 04 — Custom REINFORCE Agent (No Gym)
**Stack:** Python, PyTorch, pygame  
**What it is:** A REINFORCE policy-gradient agent built from scratch with no gymnasium
or SB3 dependency. Shows what's happening under the hood.
```bash
cd 04_mario_ppo_custom
python train_agent_without_gym.py   # train
python evaluate_without_gym.py      # watch
```

---

## Progression

| | 01 Game | 02 Explainer | 03 PPO SB3 | 04 Custom |
|---|---|---|---|---|
| Who controls Mario? | You | Nobody (visual only) | Trained PPO policy | Trained REINFORCE policy |
| Needs training? | No | No | Yes | Yes |
| External RL library? | No | No | Stable Baselines3 | No |
| Main concept | pygame, platformer | coordinate scaling | PPO, gymnasium API | REINFORCE, policy gradient |

---

## Assets required (all folders)

Both image files must be in the same folder as the script you're running:
- `super_mario_background.jpg`
- `super_mario_sprite.png`

---

## Setup

```bash
# All projects
pip install pygame numpy

# Project 03 only (additional)
pip install stable-baselines3 torch

# Project 04 only (additional)
pip install torch
```
