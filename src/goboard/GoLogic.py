'''
from sphero_formation commit 0ac14aad3
Author: Vlad
'''
import numpy as np


class Board():
    def __init__(self, n):
        "Set up initial board configuration."
        self.n = n
        # Create the empty board array.
        self.pieces = [None]*self.n
        for i in range(self.n):
            self.pieces[i] = [0]*self.n

    # add [][] indexer syntax to the Board
    def __getitem__(self, index): 
        return self.pieces[index]

    def get_legal_moves(self, color):
        """Returns all the legal moves for the given color.
        (1 for white, -1 for black
        """
        moves = set()  # stores the legal moves.

        # Get all empty locations.
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y] == 0:
                    moves.add((x, y))
        return list(moves)

    def has_legal_moves(self):
        """Returns True if has legal move else False
        """
        # Get all empty locations.
        for y in range(self.n):
            for x in range(self.n):
                if self[x][y] == 0:
                    return True
        return False

    @staticmethod
    def mark_enclosed_recurse(board, color, x, y, vc):
        """Recursively check if the given location is enclosed.
        color gives the color pf the piece to play (1=white,-1=black)
        the passed board will be modified to enclosed territory with -3
        """
        if x<0 or y<0 or x>=board.shape[0] or y>=board.shape[1] or board[x][y] == color or board[x][y] == vc:
            return True
        elif board[x][y] == -color:
            return False
        elif board[x][y] == 0:
            # mark as visited
            board[x][y] = vc
            return Board.mark_enclosed_recurse(board, color, x + 1, y, vc) and \
                   Board.mark_enclosed_recurse(board, color, x - 1, y, vc) and \
                   Board.mark_enclosed_recurse(board, color, x, y + 1, vc) and \
                   Board.mark_enclosed_recurse(board, color, x, y - 1, vc)

    @staticmethod
    def territory(board, color):
        territory = 0
        assert color == 1 or color == -1
        # copy of the board to avlid recalculating the counted territories
        board_copy = np.copy(board)
        visited_code = -2
        # Get all enclosed empty locations.
        for y in range(board.shape[0]):
            for x in range(board.shape[1]):
                if board_copy[x][y] == 0:
                    if Board.mark_enclosed_recurse(board_copy, color, x, y, visited_code):
                        territory += np.sum(board_copy[board_copy == visited_code]/visited_code)
                    visited_code -= 1
        print(board_copy)
        return territory

    def execute_move(self, move, color):
        """Perform the given move on the board; flips pieces as necessary.
        color gives the color pf the piece to play (1=white,-1=black)
        """
        (x,y) = move
        assert self[x][y] == 0
        self[x][y] = color
