"""Main file to run my Go AI
"""

import gym
import sys

from ai import LstmAi
import logging

if __name__ == '__main__':
    gym.undo_logger_setup()
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logger = logging.getLogger('main')

    env = gym.make('Go9x9-v0')
    ob = env.reset()
    env.render()

    ai = LstmAi()

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
