# 04 — Mario Custom Agent (No Gymnasium)

A REINFORCE policy-gradient agent trained from scratch with pure PyTorch.
No Stable Baselines3, no gymnasium — just the environment, the network, and the training loop.

## Setup

```bash
pip install torch pygame numpy
```

Place `super_mario_background.jpg`, `super_mario_sprite.png` in the same folder.

## Train

```bash
python train_agent_without_gym.py
```

Trains for 1,000 episodes using REINFORCE (Monte Carlo policy gradient).
Prints reward every 10 episodes and saves a checkpoint every 100.
Final weights saved as `custom_actor.pth`.

## Evaluate (watch the agent play)

```bash
python evaluate_without_gym.py
```

Loads `custom_actor.pth` and runs 5 episodes with the pygame window open.

## How it works

**Algorithm:** REINFORCE (vanilla policy gradient)
- Actor network outputs a probability distribution over 4 actions
- At each step, sample an action from the distribution
- At episode end, compute discounted returns and update the policy:
  `loss = -sum(log_prob(action) * return)`
- Returns are normalised for stability, gradients are clipped to ±0.5
- Small reward shaping bonus for moving right (+0.01 × delta_x)

**Why no Critic?**
REINFORCE doesn't require a value baseline to work. A critic (Actor-Critic / PPO)
would reduce gradient variance and learn faster — that's what `03_mario_ppo_sb3` does
using Stable Baselines3.

## File structure

```
04_mario_ppo_custom/
├── env_without_gym.py          ← standalone Mario environment
├── policy_without_gym.py       ← Actor + Critic network definitions
├── train_agent_without_gym.py  ← REINFORCE training loop
├── evaluate_without_gym.py     ← watch the trained agent play
├── custom_actor.pth            ← pre-trained weights (included)
├── custom_critic.pth           ← critic weights (included)
├── super_mario_background.jpg
├── super_mario_sprite.png
└── README.md
```
