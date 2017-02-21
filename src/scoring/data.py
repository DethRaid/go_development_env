"""Defines the classes which hold the go board data
"""

import binascii
import logging
import os

import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
__log = logging.getLogger('Data Loader')


def get_winner(board_state):
    """Calculates the winner of the game that ended with the given board state

    :param board_state: The state of the board to calcualte the winner from
    :return: 0 if white won, or 1 if black won
    """
    return 0


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
        hash = data_file.read(8)
        data_file.read(2)
        board_state = data_file.read(81)
        has_position_extra_info = binascii.hexlify(data_file.read(1))
        read_bytes += 92

        board_array = convert_to_vector(board_state)

        positions[hash] = board_array

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
        hash = data_file.read(8)
        data_file.read(2)
        score = data_file.read(1)
        confidence = data_file.read(1)
        read_bytes += 12

        scores[hash] = (score, confidence)

        count += 1
        if count % 10000 == 0:
            __log.info('Read in %s scores' % count)

    data_file.close()
    __log.info('Read in %s scores total' % count)

    return scores


def get_data():
    """Reads in the positions database and the scores file. Zips them up into an array with two sub arrays

    :return: Two arrays. One is the positions, the other is the score. These arrays are in the same order
    """

    positions = load_positions('data/input_positions.dat')
    scores = load_scores('data/fuego_chinese.dat')

    positions_list = list()
    scores_list = list()

    for position_id, position in positions.items():
        if position_id in scores.keys():
            positions_list.append(position)
            scores_list.append(scores[position])

    return positions_list, scores_list


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
    positions = load_positions('data/input_positions.dat')
    __log.info('Read in all positions')
    scores = load_scores('data/fuego_chinese.dat')
    __log.info('Read in all scores')

