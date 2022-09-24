"""unit tests for go game rules and utilties"""
import numpy as np
import unittest

from GoLogic import Board
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
        print(Board.get_territory(board, 1))

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
