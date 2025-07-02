import gym
from gym import spaces
import numpy as np
import pygame

from flappy import FlappyGame

class FlappyBirdEnv(gym.Env):
    def __init__(self, render=False):
        super(FlappyBirdEnv, self).__init__() #so muss nicht ständig gym.Env.__init__() geschrieben werden  
        self.game = FlappyGame(render=render) #Initialisierung des Spiels

        #Observation Space: [bird_y, pipe_x, top_pipe_y, bottom_pipe_y]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0], dtype=np.float32),
            high=np.array([600, 400, 600, 600], dtype=np.float32),
            dtype=np.float32
        )
        self.action_space = spaces.Discrete(2) #Action Space: 0: nichts tun, 1: flippen

    def reset(self):
        state = self.game.reset()
        return np.array(state, dtype=np.float32)

    def step(self, action):
        state, reward, done = self.game.step(action)
        return np.array(state, dtype=np.float32), reward, done, {}

    def render(self):
        # Wird automatisch im Spiel gerendert, wenn render=True beim Init war
        pass

    def close(self):
        pygame.quit()



env = FlappyBirdEnv(render=False)