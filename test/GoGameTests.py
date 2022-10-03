"""unit tests for go game rules and utilties"""
import sys

import numpy as np
import unittest

sys.path.append('goboard')
from goboard.GoLogic import Board
from src.goboard import GoLogic


class TestGoLogic(unittest.TestCase):
    """unit tests for go game rules and utilties"""

    def test_count_territories(self):
        board = np.array([
            [1, 1, 1, 0, 0],
            [1, 0, 1, 0, 0],
            [1, 1, 1, 0, 0],
            [1, 1, 1, 0,-1],
            [0, 0, 0, 0, 0]
        ])

        self.assertEqual(Board.get_territory(board, 1), 1)

    def test_count_territories_2(self):
        board = np.array([
            [0, 1, 1, 0, 0],
            [1, 0, 1, -1, 0],
            [1, 0, 0, 1, 0],
            [1, 1, 1, 0, 0],
            [-1, 0, 1, 0, 0]
        ])

    def test_count_liberties(self):
        board = np.array([
            [1, 1, 1, 0, 0],
            [1, 0, 1, 0, 0],
            [1, 1, 1, 0, 0],
            [0, 0, 0, 0,-1],
            [0, 0, 0, 0, 0]
        ])

        self.assertEqual(Board.count_liberties(board, (0, 0)), 7)
        self.assertEqual(Board.count_liberties(board, (2, 0)), 7)
        self.assertEqual(Board.count_liberties(board, (2, 2)), 7)

    def test_repetition(self):
        board = Board(5)
        board.execute_move((0, 1), 1)
        board.execute_move((1, 0), 1)
        board.execute_move((1, 2), 1)
        board.execute_move((2, 1), 1)
        board.execute_move((0, 2), -1)
        board.execute_move((2, 2), -1)
        board.execute_move((1, 3), -1)
        board.execute_move((1, 1), -1)  # capture
        # board.execute_move((1, 2), 1) # would be a ko
        valid_moves = board.get_legal_moves(1)
        self.assertNotIn((1, 2), valid_moves)
        self.assertIn((3, 3), valid_moves)

    def test_capture(self):
        board = Board(5)
        board.pieces = np.array([
            [0, 1, 0, 0, 0],
            [1,-1, 1, 0, 0],
            [1,-1, 1, 0, 0],
            [1,-1, 1, 0,-1],
            [0, 0, 0, 0, 0]
        ])
        board.execute_move((4, 1), 1)
        new_board = np.array([
            [0, 1, 0, 0, 0],
            [1, 0, 1, 0, 0],
            [1, 0, 1, 0, 0],
            [1, 0, 1, 0,-1],
            [0, 1, 0, 0, 0]
        ])
        board_diff = np.sum(board.pieces - new_board)
        self.assertEqual(0, board_diff, "position after capture is wrong: {}".format(board.pieces))

    def test_game(self):
        board = Board(5)
        board.execute_move((2, 3), -1)
        board.execute_move((2, 2), 1)
        board.execute_move((1, 2), -1)
        board.execute_move((3, 3), 1)
        board.execute_move((2, 1), -1)
        board.execute_move((2, 4), 1)
        board.execute_move((4, 2), -1)
        board.execute_move((3, 2), 1)
        board.execute_move((3, 4), -1)
        board.execute_move((1, 3), 1)
        # black stone at 2,3 captured
        board.execute_move((3, 1), -1)
        board.execute_move((1, 1), 1)
        board.execute_move((0, 2), -1)
        board.execute_move((0, 1), 1)
        board.execute_move((0, 0), -1)
        board.execute_move((0, 3), 1)
        # two black stones captured at 1,2 and 0,2
        board.execute_move((1, 0), -1)
        board.execute_move((4, 1), 1)
        board.execute_move((4, 0), -1)
        # white stones at 4,1 captured
        board.execute_move((4, 3), 1)
        board.execute_move((1, 2), -1)
        board.execute_move((2, 0), 1)
        # black stones at 0,0 and 0,1 captured
        board.execute_move((4, 4), -1)
        # black stones at 4,4 3,4 captured
        board.execute_move((3, 0), 1)
        board.execute_move((2, 3), -1)
        # white stones at 2,2 3,2 3,3 and 3,4 captured
        board.execute_move((4, 1), 1)
        # black stone 4,0 captured
        # black and white pass
        # final score:
        # black: 1 stone - 10 captured + 0 territory = -9
        # white: 12 stones - 1 captured + 11 territory = 22
        self.assertEqual(Board.get_territory(board.pieces, -1), 0)
        self.assertEqual(Board.get_territory(board.pieces, 1), 11)
        self.assertEqual(board.captured_stones[-1], 10)
        self.assertEqual(board.captured_stones[1], 1)
        self.assertEqual(board.calculate_score(-1), -9)
        self.assertEqual(board.calculate_score(1), 22)
