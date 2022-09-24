import numpy as np

from GoLogic import Board
from unittest import TestCase


def boardToPlan(board):
    """
    upscale the board to a plan
    """
    # the width of rim of the board where the stones are not counted
    external_fields_width = 2
    planboard = np.zeros(
        (board.shape[0] * 2 + external_fields_width * 2, board.shape[1] * 2 + external_fields_width * 2))
    for x in range(board.shape[0]):
        for y in range(board.shape[0]):
            planboard[y * 2 + external_fields_width][x * 2 + external_fields_width] = board[x][y]

    return planboard


class TestBoard(TestCase):
    def setUp(self):
        self.board = Board(5)

    def testCapture(self):
        board = self.board
        # capture one stone
        board.execute_move((1, 1), -1)
        board.execute_move((1, 2), 1)
        board.execute_move((2, 1), 1)
        board.execute_move((0, 1), 1)
        board.execute_move((1, 0), 1)
        board.execute_move((2, 2), -1)  # so the rest of the board is not counted as white territory
        self.assertEqual(0, board.pieces[1][1])
        self.assertEqual(1, board.calculate_score(1))


# if __name__ == "__main__":
#     board = np.ones((5,5))
#
#     for x in boardToPlan(board):
#         print(x)