import random

import logging

import sys

import math
from Queue import Queue

from keras.layers import Convolution2D, Dense
from keras.models import Sequential
from keras.optimizers import SGD

import numpy as np


def make_board_state(observation):
    """Builds the board state into a neural-network-friendly format

    :param observation: The observed board state.observations[0] is where my pieces are, observations[1] is where my
    opponent's pieces are, observations[2] is all the valid moves
    :return: A numpy matrix with 1 where my pieces are and -1 where my opponent's pieces are
    """
    return observation[0] - observation[1]


class LstmAi(object):
    """How do I reward this thing? Glad you asked...

    - If the move generated is invalid, a harsh penalty is applied
    - If the move generated results in a loss, a harsh penalty is applied
    - If the move generated results in a captured enemy piece, a reward is applied
    - If the move generates results in a captured piece that we own, a penalty is applied
    - If we win a large reward is applied
    - If we lose, a large penalty is applied

    In this context, "results in" means something that happens on the next turn

    self.model outputs two numbers. The numbers are texture coordinates of where to put the piece on the board - they
    have a range of [0, 1] where point (0, 0) is point A1 on the Go board, and point (1, 1) is poing J9 on the Go
    board. Because the outputs are continuous and the board is discrete, an output which falls within a given board
    square is considered to be a command to put a piece in that board square
    """
    def __init__(self):
        """Builds and initializes this AI"""
        #logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        self.logger = logging.getLogger('LSTM AI')

        self.model = Sequential()
        self.model.add(Dense(100, input_shape=(9, 9), activation='relu'))
        self.model.add(Dense(100, activation='relu'))
        self.model.add(Dense(100, activation='relu'))
        self.model.add(Dense(4))

        # output 0 is board x, output 1 is board y. Output 2 is pass, output 3 is forfeit

        self.model.compile(SGD(lr=.2), 'mse')

        self.reward_estimator = QNetwork()

        self.last_board_state = np.empty([9, 9])
        self.last_action = 82

    def act(self, observation, reward, done):
        """Performs an action

        :param observation: The current state of the board. Observations[0] is where my pieces are, observations[1] is
        where my opponent's pieces are, observations[2] is all the valid moves
        :param reward: The reward amount for the board
        :param done: True if the game is over, False otherwise
        :return: The move to make. this is a number in [0, 82] describing the move to make. 81 is pass, 82 is forfeit.
        Numbers less than 81 refer to a place on the board. A9 is 0, J9 is 8, A8 is 9, J8 is 17, so on and so forth
        """

        board_state = make_board_state(observation)
        rewards = self.reward_estimator.get_rewards(board_state)
        self.reward_estimator.remember([self.last_board_state, self.last_action, rewards, board_state], done)

        move = self.model.predict(np.array([board_state]), batch_size=1)[0][0]
        action = 0
        if move[3] > 0.1:
            self.logger.info('Forfeiting the game')
            action = 82

        elif move[2] > 0.1:
            self.logger.info('Passing this turn')
            action = 81

        else:
            action = math.floor(move[0] * 9 + move[1] * 9 * 9)
            self.logger.info('Placing a piece on %s' % action)

        self.last_board_state = board_state
        self.last_action = action

        return action


class QNetwork(object):
    """A CNN which generates a q-value for each move one can make from a board state in Go

    Because arbitrary board sizes are hard, this network will output Q-values for invalid moves. Hopefully it will
    learn that they are invalid (or I'll figure out how to teach it that)"""

    def __init__(self, max_memory=50, discout=0.9):
        """Builds the CNN model

        The model takes the last four game states and convolves them into a single Q value. This model is based heavily
        on DeepMind's architecture, which is hopefully applicable to this situation
        """

        self.model = Sequential()
        self.model.add(Convolution2D(4, 5, 5, input_shape=(4, 9, 9), activation='relu', dim_ordering='th'))
        self.model.add(Convolution2D(8, 3, 3, activation='relu', dim_ordering='th'))
        self.model.add(Convolution2D(16, 2, 2, activation='relu', dim_ordering='th'))
        self.model.add(Dense(512, activation='relu'))
        self.model.add(Dense(81, activation='linear'))

        self.model.compile(SGD(lr=.2), 'mse')

        self.memory = list()
        self.max_memory = max_memory
        self.discount = discout

    def get_rewards(self, board_state):
        """Calculates the rewards for the moves you might make at this board state

        :param board_state: The board state as a numpy matrix where 1 means you have a piece, -1 means your opponent has
         a piece, and 0 means there's no piece
        :return: The rewards for each move you might make
        """

        inputs = list()
        for i in range(-3, 0):
            if len(self.memory) == 0:
                inputs.append(board_state)
            else:
                input = random.randint(0, len(self.memory) - 1)
                inputs.append(self.memory[input][0][0])

        inputs.append(board_state)

        data_to_predict_on = np.array([inputs])
        return self.model.predict(data_to_predict_on)[0][0]

    def remember(self, state, game_over):
        """Remembers the state of the board

        :param state: The state of the board. [state, action, reward, next_state]
        :param game_over: True if the game ended this turn, false otherwise
        """
        if len(self.memory) > self.max_memory:
            del self.memory[0]

        self.memory.append([state, game_over])
