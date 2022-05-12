import numpy as np

from GoLogic import Board

"""

"""

def testAreaCalculation():
    board = np.array([
        [0, 1, 1, 0, 0],
        [1, 0, 1, -1,0],
        [1, 0, 0, 1, 0],
        [1, 1, 1, 0, 0],
        [-1, 0, 1, 0, 0]
    ])
    print(Board.get_territory(board, 1))


def boardToPlan(board):
    """
    upscale the board to a plan
    """
    # the width of rim of the board where the stones are not counted
    external_fields_width = 2
    planboard = np.zeros((board.shape[0]*2+external_fields_width*2, board.shape[1]*2+external_fields_width*2))
    for x in range(board.shape[0]):
        for y in range(board.shape[0]):
            planboard[y*2+external_fields_width][x*2+external_fields_width] = board[x][y]

    return planboard


if __name__ == "__main__":
    board = np.ones((5,5))

    for x in boardToPlan(board):
        print(x)