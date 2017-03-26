"""Uses a Keras recurrent neural network to estimate the chance that each player will win, given a sequence of moves in
a GO board
"""
import json

import sys

import time
from keras.layers import Convolution2D, Dense, MaxPooling2D, Flatten
from keras.models import Sequential, load_model
from keras.optimizers import SGD

import numpy as np

import cPickle as pickle

import logging


class GoScorer(object):
    """Contains a model which can score a Go board

    TODO: Make the AI in the AI Gym play itself to get game data
    Train the Q-network on the data from the gym
    Party
    """

    def __init__(self, model_path=None, learning_rate=0.9):
        """Initializes this model

        :param model_path: The path to where the model is stored on disk. If this parameter is not provided, or is set
         to None, then this model is initialized with default weights. This is suitable if you want to train it on some
         data
        """
        self.log = logging.getLogger('GoScorer')
        self.learning_rate = learning_rate

        self.previous_board = np.empty([9, 9])

        if model_path is None:
            self.log.info('Creating default model')
            self.q_network = Sequential()

            self.q_network.add(Convolution2D(32, 5, 5, input_shape=(1, 9, 9), activation='relu', dim_ordering='th'))
            self.q_network.add(Convolution2D(64, 3, 3, activation='relu', dim_ordering='th'))
            self.q_network.add(Convolution2D(64, 2, 2, activation='relu', dim_ordering='th'))
            self.q_network.add(Flatten())
            self.q_network.add(Dense(256, activation='relu'))
            self.q_network.add(Dense(83, activation='linear'))

            self.q_network.compile(optimizer=SGD(lr=.2), loss='mse', metrics=['accuracy'])

        else:
            self.log.info('Loading model from %s' % model_path)
            self.q_network = load_model(model_path)

    def train(self, positions, scores):
        """Trains this model on the provided boards and scores

        :param positions: A list of 9x9 numpy matrices representing the board. This code assumes that a value of 1 in
        the matrix means that a space has one of your pieces, a -1 means that a space has one of our opponent's pieces,
        and a 0 means that there's no pieces
        :param scores: The list of the scores for the provided boards. The list of scores and list of positions should
        be in the same order
        """

        self.log.info('Beginning model training')
        start_time = time.clock()
        try:
            # positions = [x for x in positions]
            positions_np = np.array(positions)
            scores_np = np.array(scores)

            self.log.info('First board: \n%s' % str(positions_np[0]))
            self.log.info('First score: \n%s' % str(scores_np[0]))

            self.q_network.fit(positions_np, scores_np, nb_epoch=100, batch_size=300)
            end_time = time.clock()
            self.log.info('Model training complete in %s seconds' % (end_time - start_time))
            self.q_network.save('go_scoring.h5')
            self.log.info('Model saved')
        except Exception as e:
            end_time = time.clock()
            self.log.error('Failed in %s seconds' % (end_time - start_time))
            if end_time - start_time > 300:
                self.log.error('(%s minutes)' % ((end_time - start_time) / 60))
            if end_time - start_time > 3600:
                self.log.error('(%s hours)' % ((end_time - start_time) / 3600))
            self.log.error('Reason: %s' % e)

    def process_turn(self, board):
        """Retrieves the score for a particular board

        :param board: The board to get the score for
        :return: The score of the board
        """

        board_np = np.array(board)

        # This is kinda weird. We update the network here for what happened last turn because we need two consecuive
        # board states in order to properly Q-learn. We have the last board state, and we ahve this board state, so we
        # can party

        rewards = self.q_network.predict(self.previous_board)

        max_r = 0
        for i in range(len(rewards)):
            if rewards[i] > rewards[max_r]:
                max_r = i

        rewards_next = self.q_network.predict(board_np)
        max_rn = 0
        for i in range(len(rewards_next)):
            if rewards_next[i] > rewards_next[max_rn]:
                max_rn = i

        rewards[max_r] += self.learning_rate * rewards_next[max_rn]

        self.previous_board = board_np

        action_rewards = self.q_network.predict(board_np)

        max = 0
        for i in range(len(action_rewards)):
            if action_rewards[i] > action_rewards[max]:
                max = i

        return max


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    __log = logging.getLogger('scoring_main')
    scorer = GoScorer()

    with open('data/training_data.p', 'rb') as datafile:
        __log.info('Beginning loading data')
        start_time = time.clock()
        data = pickle.load(datafile)
        end_time = time.clock()
        __log.info('Read in training data in %s seconds' % (end_time - start_time))

        positions_data = [[x] for x in data['positions']]
        scores_data = [np.array([x[0] / 8]) for x in data['scores']]

        __log.info('Training on %s examples with %s labels' % (len(positions_data), len(scores_data)))

        scorer.train(positions_data, scores_data)
