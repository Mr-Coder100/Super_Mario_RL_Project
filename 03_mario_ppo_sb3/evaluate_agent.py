"""
Watch a trained PPO agent play Mario.
Requirements: pip install stable-baselines3 pygame numpy
"""
# evaluate_agent.py

import os
import pygame
import time
from stable_baselines3 import PPO

# Import the environment
from mario_env import MarioPygameEnv

# Path to the trained model file
MODEL_PATH = "final_ppo_mario_model.zip"

try:
    # Load the trained model
    model = PPO.load(MODEL_PATH, render_mode='human')
    print(f"Model loaded from {MODEL_PATH}")

    # Create the environment in human rendering mode
    env = MarioPygameEnv(render_mode="human")
    
    obs, info = env.reset()
    done = False
    
    while not done:
        # Check for user input to close the window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                
        # Use the model to predict the next action
        action, _states = model.predict(obs, deterministic=True)
        
        # Take the action in the environment
        obs, reward, terminated, truncated, info = env.step(action)
        
        done = terminated or truncated

        # Control the speed of the animation
        time.sleep(0.01)

    print("Episode finished.")
    env.close()
    
except FileNotFoundError:
    print(f"Error: Model file '{MODEL_PATH}' not found. Please train the model first.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    if 'env' in locals():
        env.close()