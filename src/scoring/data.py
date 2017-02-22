"""Defines the classes which hold the go board data
"""

import binascii
import json
import logging
import os

import sys

import struct

from multiprocessing import Pool

import multiprocessing

import time

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
__log = logging.getLogger('Data Loader')


def load_positions(data_file_location):
    """Loads all the positions from the positions file

    :param data_file_location: The location on disk of the file to load positions from
    :return: A dict from position hash to board state
    """

    data_file_size = os.path.getsize(data_file_location)

    data_file = open(data_file_location, 'rb')

    positions = dict()
    count = 0
    read_bytes = 0

    while read_bytes < data_file_size:
        zorbitz = data_file.read(8)
        data_file.read(2)
        board_state = data_file.read(81)
        has_position_extra_info = binascii.hexlify(data_file.read(1))
        read_bytes += 92

        board_array = convert_to_vector(board_state)

        positions[zorbitz] = board_array

        if has_position_extra_info == 1:
            data_file.read(8)
            read_bytes += 8

        count += 1
        if count % 10000 == 0:
            __log.info('Read in %s positions' % count)

    __log.info('Read in %s positions total' % count)

    data_file.close()
    return positions


def load_scores(scores_file_location):
    """Loads the scores from the scores file

    :param scores_file_location: The location on disk of the file to load scores from
    :return: A dict from position hash to score
    """

    data_file_size = os.path.getsize(scores_file_location)

    data_file = open(scores_file_location, 'rb')

    scores = dict()

    count = 0
    read_bytes = 0

    while read_bytes < data_file_size:
        zorbitz = data_file.read(8)
        data_file.read(2)
        score = struct.unpack('<B', data_file.read(1))[0]
        confidence = struct.unpack('<B', data_file.read(1))[0]
        read_bytes += 12

        scores[zorbitz] = (score, confidence)

        count += 1
        if count % 10000 == 0:
            __log.info('Read in %s scores' % count)

    data_file.close()
    __log.info('Read in %s scores total' % count)

    return scores


scores = list()
count = 0
last_time = 0


def thread_func(x):
    global scores
    global count
    if x[0] in scores.keys():
        count += 1
        if count % 50 == 0:
            global last_time
            cur_time = time.clock()
            __log.info('Correlated %s scores and positions in %s seconds' % (count, cur_time - last_time))
            last_time = cur_time
        return x[1], scores[x[0]]


def get_data():
    """Reads in the positions database and the scores file. Zips them up into an array with two sub arrays

    :return: Two arrays. One is the positions, the other is the score. These arrays are in the same order
    """

    positions = load_positions('data/input_positions.dat')
    global scores
    scores = load_scores('data/fuego_chinese.dat')

    global last_time
    last_time = time.clock()

    positions_list = list()
    scores_list = list()

    p = Pool(4)
    data = p.map(thread_func, positions.items())

    return data


def convert_to_vector(board_state):
    """Converts the given board from a string to an array of number so that the numbers can be fed into the RNN

    :param board_state: The board state as a string. Periods mean empty spaces, #s mean black pieces, Os mean white
    pieces
    :return: An array for the board. The array has 0 for empty spaces, 1 for black pieces, and -1 for white pieces
    """
    board_array = list()
    for char in board_state:
        if char == '.':
            board_array.append(0)
        elif char == '#':
            board_array.append(1)
        elif char == 'O':
            board_array.append(-1)
    return board_array


if __name__ == '__main__':
    data = get_data()
    # data = {'positions': position_list, 'scores': score_list}

    with open('training_data.json', 'w') as jsonfile:
        json.dump(data, jsonfile)

