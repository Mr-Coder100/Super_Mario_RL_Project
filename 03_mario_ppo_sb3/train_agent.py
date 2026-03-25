"""
Train a PPO agent on Mario using Stable Baselines3.
Saves checkpoints every 10,000 steps and a final model at the end.
Requirements: pip install stable-baselines3 pygame numpy
"""
# train_agent.py

import os
import pygame
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import CheckpointCallback

# Set up a dummy display to avoid a Pygame window
os.environ['SDL_VIDEODRIVER'] = 'dummy'
pygame.init()

# Import the environment
from mario_env import MarioPygameEnv

# Create the environment
env = MarioPygameEnv()
vec_env = make_vec_env(lambda: env, n_envs=1)

# Initialize the PPO agent
model = PPO("MlpPolicy", vec_env, verbose=1)

# Save a checkpoint every 10,000 steps
checkpoint_callback = CheckpointCallback(save_freq=10000, save_path='./models/',
                                         name_prefix='ppo_mario_model')

print("Training started...")
model.learn(total_timesteps=50000, callback=checkpoint_callback)

# Save the final model
model.save("final_ppo_mario_model")
print("Model trained and saved as 'final_ppo_mario_model.zip'")