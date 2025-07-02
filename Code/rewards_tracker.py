import matplotlib.pyplot as plt

class RewardTracker:
    def __init__(self):
        self.rewards = []

    def add_reward(self, reward_value):
        self.rewards.append(reward_value)

    def plot_rewards(self):
        plt.plot(self.rewards)
        plt.title("Rewards über die Schritte")
        plt.xlabel("Schritt")
        plt.ylabel("Reward")
        plt.grid(True)
        plt.show()