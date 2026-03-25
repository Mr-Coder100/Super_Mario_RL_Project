# evaluate_from_scratch.py

import pygame
import torch
import time
from env_without_gym import MarioPygameEnvironment
from policy_without_gym import Actor, Critic

# --- Config ---
STATE_DIM = 4
ACTION_DIM = 4

# Paths to the saved model weights
ACTOR_MODEL_PATH = "custom_actor.pth"
CRITIC_MODEL_PATH = "custom_critic.pth"

def evaluate(num_episodes=5):
    try:
        # Load the models
        actor = Actor(STATE_DIM, ACTION_DIM)
        actor.load_state_dict(torch.load(ACTOR_MODEL_PATH))
        actor.eval()

        # The critic is not needed for just taking actions
        print(f"Models loaded successfully from '{ACTOR_MODEL_PATH}'")

        env = MarioPygameEnvironment(render_mode=True)
        clock = pygame.time.Clock()

        for episode in range(num_episodes):
            print(f"--- Running Episode {episode + 1} ---")
            state = env.reset()
            done = False
            total_reward = 0

            while not done:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        done = True

                state_tensor = torch.FloatTensor(state).unsqueeze(0)
                
                with torch.no_grad():
                    action_probs = actor(state_tensor)
                    action = torch.argmax(action_probs, dim=1).item()

                state, reward, done = env.step(action)
                total_reward += reward

                clock.tick(60)

            print(f"Episode {episode + 1} finished with total reward: {total_reward:.2f}")

        env.close()

    except FileNotFoundError:
        print("Error: Model files not found. Please train the agent first.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        if 'env' in locals():
            env.close()

if __name__ == "__main__":
    evaluate()