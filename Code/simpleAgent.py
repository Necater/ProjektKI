import gym
from FlappyBirdGame import FlappyGame
import random 
import pygame
import time
from pygame.locals import *
game = FlappyGame()  

class simpleAgent():
    def act(self, observation):
        return random.randint(0,1)

testagent = simpleAgent()

def play(agent):
    state = game.reset() 
    gesamtReward = 0
    gesamtStep = 0
    done = False
    while not done:
        action = agent.act(state)
        state, reward, done = game.step(action)
        gesamtReward += reward
        gesamtStep +=1
        print(gesamtReward, gesamtStep)
        continue
    pygame.quit()

       

play(testagent)