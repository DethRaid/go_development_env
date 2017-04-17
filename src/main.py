"""Main file to run my Go AI
"""

import gym
import sys

from keras.layers import Convolution2D, Flatten, Dense
from keras.models import Sequential
from keras.optimizers import SGD
from qlearning4k import Agent
from qlearning4k.games.game import Game

from ai import LstmAi
import logging

class Go(Game):
    def __init__(self, render=False):
        self.env = gym.make('Go9x9-v0')

        self.render = render

        if self.render:
            self.env.render()

    def reset(self):
        self.env.close()
        self.env = gym.make('Go9x9-v0')

    @property
    def name(self):
        return 'Go 9x9'

    @property
    def nb_actions(self):
        return 83

    def play(self, action):
        state, _, done, _ = self.env.step(action)

        self.state = state[0] - state[1]
        self.done = done

    def is_over(self):
        return self.done

    def is_won(self):
        if not self.done:
            return False

        return True


if __name__ == '__main__':
    gym.undo_logger_setup()
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logger = logging.getLogger('main')

    env = gym.make('Go9x9-v0')
    ob = env.reset()
    env.render()

    q_network = Sequential()

    q_network.add(Convolution2D(32, 5, 5, input_shape=(1, 9, 9), activation='relu', dim_ordering='th'))
    q_network.add(Convolution2D(64, 3, 3, activation='relu', dim_ordering='th'))
    q_network.add(Convolution2D(64, 2, 2, activation='relu', dim_ordering='th'))
    q_network.add(Flatten())
    q_network.add(Dense(256, activation='relu'))
    q_network.add(Dense(83, activation='linear'))

    q_network.compile(optimizer=SGD(lr=.2), loss='mse', metrics=['accuracy'])

    ai = Agent(model=q_network)

    reward = 0
    done = False

    while True:
        action = ai.act(ob, reward, done)
        ob, reward, done, _ = env.step(action)
        env.render()
        if done:
            break

    env.close()
    logger.info('Game done')
