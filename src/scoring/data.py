"""Defines the classes which hold the go board data
"""

import binascii
import json
import logging
import os

import sys

import struct

from multiprocessing import Pool

import numpy as np

import time

import cPickle as pickle


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
        data_file.read(1)
        who_plays_next = data_file.read(1)
        board_state = data_file.read(81)
        has_position_extra_info = binascii.hexlify(data_file.read(1))
        read_bytes += 92

        board_array = convert_to_vector(board_state, who_plays_next == 'W')

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

        scores[zorbitz] = [score, confidence]

        count += 1
        if count % 10000 == 0:
            __log.info('Read in %s scores' % count)

    data_file.close()
    __log.info('Read in %s scores total' % count)

    return scores


scores = list()


def thread_func(x):
    global scores
    try:
        return x[1], scores[x[0]]
    except Exception:
        # Yes, empty catch block. Failures aren't important to me here.
        pass


def convert_to_matrix(to_convert):
    """Converts a 81-element array into a 9x9 numpy matrix

    :param to_convert: The 81-element array to convert
    :return: a 9x9 numpy matrix for the array
    """
    mat = np.empty([9, 9])
    for y in range(9):
        for x in range(9):
            mat[y][x] = to_convert[x + y * 9]

    return mat


def get_data():
    """Reads in the positions database and the scores file. Zips them up into an array with two sub arrays

    :return: Two arrays. One is the positions, the other is the score. These arrays are in the same order
    """

    positions = load_positions('data/input_positions.dat')
    global scores
    scores = load_scores('data/fuego_chinese.dat')

    # 49.2999 seconds with 2 threads in run mode
    # 42.6354 seconds with 4 threads in run mode
    # 44.4638 seconds with 6 threads in run mode
    # 45.0285 seconds with 8 threads in run mode
    num_threads = 3

    start_time = time.clock()
    p = Pool(num_threads)
    data = np.array(p.map(thread_func, positions.items()))
    end_time = time.clock()

    __log.info('Correlated the scores in %s seconds with %s threads' % (end_time - start_time, num_threads))

    data_no_null = np.array([x for x in data if x is not None])
    data_lists = np.array(map(list, zip(*data_no_null)))
    data_lists[0] = map(convert_to_matrix, data_lists[0])

    return {'positions': data_lists[0], 'scores': data_lists[1]}


def convert_to_vector(board_state, white_plays_next):
    """Converts the given board from a string to an array of number so that the numbers can be fed into the RNN

    :param board_state: The board state as a string. Periods mean empty spaces, #s mean black pieces, Os mean white
    pieces
    :return: An array for the board. The array has 0 for empty spaces, 1 for black pieces, and -1 for white pieces
    """

    if white_plays_next:
        conversion = {'.': 0, '#': 1, 'O': -1}
    else:
        conversion = {'.': 0, '#': -1, 'O': 1}

    board_array = list()
    for char in board_state:
        try:
            board_array.append(conversion[char])
        except:
            __log.error('Could not convert char %s' % char)
            board_array.append(0)

    return board_array


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    __log = logging.getLogger('Data Loader')

    start_time = time.clock()
    data = get_data()
    end_time = time.clock()
    __log.info('Loaded data from disk in %s seconds' % (end_time - start_time))

    with open('data/training_data.p', 'wb') as datafile:
        start_time = time.clock()
        pickle.dump(data, datafile, pickle.HIGHEST_PROTOCOL)
        end_time = time.clock()

        __log.info('Saved data in %s seconds' % (end_time - start_time))
