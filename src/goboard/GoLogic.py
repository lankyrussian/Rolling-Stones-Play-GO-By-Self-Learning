'''
from sphero_formation commit 0ac14aad3
Author: Vlad
'''
import queue

import numpy as np
from copy import deepcopy


class Board():
    def __init__(self, n):
        "Set up initial board configuration."
        self.n = n
        # Create the empty board array.
        self.pieces = np.zeros((n, n), dtype=int)
        self.board_history = np.zeros((n*2, n, n), dtype=int)
        self.move_number = 0
        self.previous_passed = False
        self.captured_stones = {-1: 0, 1: 0}

    # add [][] indexer syntax to the Board
    def __getitem__(self, index): 
        return self.pieces[index]

    def is_legal_move(self, color, move):
        """Returns True if the move is legal.
        """
        # not occupied
        if self.pieces[move] != 0:
            return False
        # doesn't result in a repeated position
        new_board = deepcopy(self.pieces)
        new_board[move] = color
        idxs = Board.get_captured(new_board, move, color)
        for i in idxs:
            new_board[i] = 0
        for board in self.board_history[:self.move_number, :, :]:
            if np.array_equal(new_board, board):
                return False
        return True

    def get_legal_moves(self, color):
        """Returns all the legal moves for the given color.
        (1 for white, -1 for black
        """
        moves = set()  # stores the legal moves.

        # Get all empty locations.
        for y in range(self.n):
            for x in range(self.n):
                if self.is_legal_move(color, (x, y)):
                    moves.add((x, y))
        return list(moves)

    def has_legal_moves(self):
        """Returns True if has legal move else False
        """
        # Get all empty locations.
        for y in range(self.n):
            for x in range(self.n):
                if self.is_legal_move(1, (x, y)) or self.is_legal_move(-1, (x, y)):
                    return True
        return False

    @staticmethod
    def mark_enclosed_recurse(board, true_color, false_color, x, y, vc, enclosed_color=0):
        """Recursively check if the given location is enclosed.
        color gives the color pf the piece to play (1=white,-1=black)
        the passed board will be modified to enclosed territory with a visited code vc
        """
        if x<0 or y<0 or x>=board.shape[0] or y>=board.shape[1] or board[x][y] == true_color or board[x][y] == vc:
            return True
        elif board[x][y] == false_color:
            return False
        elif board[x][y] == enclosed_color:
            # mark as visited
            board[x][y] = vc
            return Board.mark_enclosed_recurse(board, true_color, false_color, x + 1, y, vc, enclosed_color) and \
                   Board.mark_enclosed_recurse(board, true_color, false_color, x - 1, y, vc, enclosed_color) and \
                   Board.mark_enclosed_recurse(board, true_color, false_color, x, y + 1, vc, enclosed_color) and \
                   Board.mark_enclosed_recurse(board, true_color, false_color, x, y - 1, vc, enclosed_color)

    @staticmethod
    def get_territory(board, color):
        territory = 0
        assert color in [-1, 1]
        # copy of the board to avlid recalculating the counted territories
        board_copy = deepcopy(board)
        visited_code = -2
        # Get all enclosed empty locations.
        for y in range(board.shape[0]):
            for x in range(board.shape[1]):
                if board_copy[x][y] == 0:
                    if Board.mark_enclosed_recurse(board_copy, color, -color, x, y, visited_code):
                        territory += np.sum(board_copy[board_copy == visited_code]/visited_code)
                    visited_code -= 1
        return territory

    @staticmethod
    def get_seki(board, color):
        """"group is in seki if playing in it will result in its loss (like having one eye)"""
        seki = 0
        assert color in [-1, 1]

    @staticmethod
    def count_liberties(board, piece):
        """Returns the number of liberties of the group that piece belongs to.
        """
        (x,y) = piece
        assert board[x][y] != 0, "Tried to count liberties of empty space"
        liberties = 0
        visited = set()
        to_visit = queue.Queue()
        to_visit.put((x,y))
        while not to_visit.empty():
            (x,y) = to_visit.get()
            if (x,y) not in visited and x >= 0 and y >= 0 and x < board.shape[0] and y < board.shape[1]:
                # mark as visited
                visited.add((x,y))
                if board[x][y] == 0:
                    liberties += 1
                else:
                    to_visit.put((x+1,y))
                    to_visit.put((x-1,y))
                    to_visit.put((x,y+1))
                    to_visit.put((x,y-1))

        return liberties

    @staticmethod
    def get_captured(board, move, color):
        """Returns np indexes captured pieces after the move
        """
        (x,y) = move
        # board_copy = deepcopy(board)
        idxs = []
        # check for captures in all directions
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            board_copy = deepcopy(board)
            # capturing enemy group
            if Board.mark_enclosed_recurse(board_copy, color, 0, x + dx, y + dy, -2, -color):
                idxs.append(np.where(board_copy == -2))

        if len(idxs) > 0:
            return idxs

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (0,0)]:
            board_copy = deepcopy(board)
            # capturing own group
            if Board.mark_enclosed_recurse(board_copy, -color, 0, x + dx, y + dy, -2, color):
                idx = np.where(board_copy == -2)
                board_copy[idx] = 0
            else:
                board_copy[x,y] = color
        # remove captured pieces
        idx = np.where(board_copy == -2)

        return idx

    def calculate_score(self, color):
        """Returns the score of the board for the given color.
        score = territory - (seki stones + captured stones) (+ komi if you are white)
        in this version we don't count seki
        """
        board = deepcopy(self.pieces)
        return Board.get_territory(board, color) - self.captured_stones[color]

    def execute_move(self, move, color):
        """Perform the given move on the board; flips pieces as necessary.
        color gives the color pf the piece to play (1=white,-1=black)
        """
        (x,y) = move
        assert self[x][y] == 0
        self.pieces[x][y] = color
        idx = Board.get_captured(self.pieces, move, color)
        for i in idx:
            self.pieces[i] = 0
        self.move_number += 1
        self.board_history[self.move_number] = deepcopy(self.pieces)
