"""Defines the classes which hold the go board data
"""

import numpy as np
import binascii


def get_winner(board_state):
    """Calculates the winner of the game that ended with the given board state

    :param board_state: The state of the board to calcualte the winner from
    :return: 0 if white won, or 1 if black won
    """
    return 0


def load_data(data_file_location):
    """Loads Go board data from a file

    The expected file format is documented at http://dcook.org/compgo/9by9_file_format.html

    :param data_file_location: The path to the data file
    :return: A list of tuples. Each tuple has a list of game board states as its first element, then the game result as
     its second element. The game board states are an array of matrices. For each game board state, a 1 denotes a black
     piece, a -1 denotes a white piece, and a 0 denotes no pieces
    """

    data_file = open(data_file_location, 'rb')

    # A list of tuples. The first element of each tuple is a list of all the moves in a game. The second element is 1
    # if black won and 0 if white won
    games = list()

    # A list of all the moves in the game being loaded from the data file
    cur_game = list()

    num_moves_processed = 0
    num_games = 0
    last_board_state = '.'

    while True:
        hash = data_file.read(8)
        tiebreaker = data_file.read(1)
        next_player = data_file.read(1)
        board_state = data_file.read(81)
        has_position_extra_info = binascii.hexlify(data_file.read(1))

        board_array = convert_to_vector(board_state)

        if board_state.count('.') == 80 and len(cur_game) > 0:
            # All but one piece is an empty space. This means that a new game has just started
            # Now we need to figure out the winner of the game
            black_win_chance = get_winner(cur_game[-1])
            games.append((cur_game, black_win_chance))
            cur_game = list()
            num_games += 1
            print 'Processed ' + str(num_moves_processed) + ' moves, which has given us ' + str(num_games) + ' games'

        else:
            cur_game.append(board_array)

        if has_position_extra_info == 1:
            data_file.read(8)

        num_moves_processed += 1
        last_board_state = board_state

    return games


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
    load_data('scoring/input_positions.dat')
