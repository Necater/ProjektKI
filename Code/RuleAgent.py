import time
import psutil
import pygame
from flappy import FlappyGame
from cpu_tracker import CPUTracker
from rewards_tracker import RewardTracker

class RuleAgent:
    def act(self, observation):
        bird_y, pipe_x, top_y, bot_y = observation
        gap_center = (top_y + bot_y) / 2
        return 1 if bird_y > gap_center else 0

def play(agent, render, max_steps=100, no_progress_limit=150):
    game = FlappyGame(render=render)
    state = game.reset()
    gesamtReward = 0
    gesamtStep = 0
    done = False

    cpu_tracker = CPUTracker()
    process = psutil.Process()

    reward_tracker = RewardTracker()

    last_reward_step = 0
    step_durations = []
    ram_usages = []

    while not done and gesamtStep < max_steps:
        start = time.perf_counter()

        action = agent.act(state)
        state, reward, done = game.step(action)
        gesamtReward += reward
        gesamtStep += 1

        # Reward-Tracking
        reward_tracker.add_reward(reward)

        # CPU-Tracking
        cpu_tracker.track()

        ram_mb = process.memory_info().rss / (1024 * 1024)
        ram_usages.append(ram_mb)

        if reward > 0:
            last_reward_step = gesamtStep

        step_duration = time.perf_counter() - start
        step_durations.append(step_duration)

        print(f"Reward: {gesamtReward:.2f}, Step: {gesamtStep}, Step-Dauer: {step_duration*1000:.2f} ms, RAM: {ram_mb:.2f} MB")

        if gesamtStep - last_reward_step > no_progress_limit:
            print("Kein Fortschritt, Abbruch.")
            break

        if render:
            time.sleep(0.05)

    pygame.quit()

    avg_cpu = sum(cpu_tracker.usage) / len(cpu_tracker.usage) if cpu_tracker.usage else 0
    avg_step_time = sum(step_durations) / len(step_durations) if step_durations else 0
    max_ram = max(ram_usages) if ram_usages else 0

    print(cpu_tracker.summary())
    print(f"Durchschnittliche Step-Dauer: {avg_step_time*1000:.2f} ms")
    print(f"Max. RAM-Verbrauch: {max_ram:.2f} MB")

    cpu_tracker.plot()

    # Plotten des Rewards
    reward_tracker.plot_rewards()

# Beispiel-Aufruf
if __name__ == "__main__":
    testagent = RuleAgent()

    print("\n=== Benchmark: ohme Rendern ===")
    play(testagent, render=False)


