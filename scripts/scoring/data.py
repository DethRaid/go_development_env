"""Defines the classes which hold the go board data
"""

import numpy as np
import binascii

def load_data(data_file_location):
    """Loads Go board data from a file

    The expected file format is documented at http://dcook.org/compgo/9by9_file_format.html

    :param data_file_location: The path to the data file
    :return: A list of tuples. Each tuple has a list of game board states as its first element, then the game result as
     its second element. The game board states are an array of matrices. For each game board state, a 1 denotes a black
     piece, a -1 denotes a white piece, and a 0 denotes no pieces
    """

    data_file = open(data_file_location, 'rb')

    while True:
        hash = data_file.read(8)
        tiebreaker = data_file.read(1)
        next_player = data_file.read(1)
        board_state = data_file.read(81)
        has_position_extra_info = binascii.hexlify(data_file.read(1))

        for i in range(9):
            cur_row = board_state[i * 9:(i + 1) * 9]
            print cur_row

        print ''

        if has_position_extra_info == 1:
            position_extra_info_source = data_file.read(4)
            position_extra_info_variation_number = data_file.read(2)
            position_extra_info_variation_move_numer = data_file.read(2)


if __name__ == '__main__':
    load_data('scoring/input_positions.dat')
