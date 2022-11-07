"from sphero_formation commit 0ac14aad3"

from __future__ import print_function

from Game import Game
from GoLogic import Board
import numpy as np
from copy import deepcopy


class GoGame(Game):
    def __init__(self, n=5):
        self.n = n

    def getInitBoard(self):
        # return initial board (numpy board)
        return Board(self.n)

    def getBoardSize(self):
        # (a,b) tuple
        return (self.n, self.n)

    def getActionSize(self):
        # return number of actions
        return self.n * self.n + 1

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        newboard = deepcopy(board)
        move = (int(action / self.n), action % self.n)
        if move == board.PASS:
            if newboard.previous_passed:
                newboard.game_ended = True
            else:
                newboard.previous_passed = True
            return (newboard, -player)
        newboard.previous_passed = False
        newboard.execute_move(move, player)
        return (newboard, -player)

    # modified
    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0] * self.getActionSize()
        legalMoves = board.get_legal_moves(player)
        if len(legalMoves) == 0:
            valids[-1] = 1
            return np.array(valids)
        for x, y in legalMoves:
            valids[self.n * x + y] = 1
        return np.array(valids)

    # modified
    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        return board.get_game_ended()

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        new_board = Board(self.n)
        new_board.pieces = board.pieces * player
        new_board.move_number = board.move_number
        new_board.board_history = board.board_history * player
        new_board.previous_passed = board.previous_passed
        new_board.game_ended = board.game_ended
        new_board.captured_stones = {
            1:  board.captured_stones[ player],
            -1: board.captured_stones[-player]}
        return new_board

    # modified
    def getSymmetries(self, board_, pi):
        # mirror, rotational
        board = board_.pieces
        assert(len(pi) == self.n**2 + 1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.n, self.n))
        l = []

        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(board, i)
                newPi = np.rot90(pi_board, i)
                if j:
                    newB = np.fliplr(newB)
                    newPi = np.fliplr(newPi)
                l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        return l

    def stringRepresentation(self, board):
        # the state should include the flag for 2 passes,
        # since the MCTS only checks for the game end on a new state
        return f"{board.pieces.tostring()}{'1' if board.game_ended else '0'}"

    @staticmethod
    def display(board_):
        board = board_.pieces
        n = board.shape[0]

        for y in range(n):
            print(y, "|", end="")
        print(f"")
        print(" -----------------------")
        for y in range(n):
            print(y, "|", end="")    # print the row #
            for x in range(n):
                piece = board[y][x]    # get the piece to print
                if piece == -1:
                    print("w ", end="")
                elif piece == 1:
                    print("b ", end="")
                else:
                    if x == n:
                        print("-", end="")
                    else:
                        print("- ", end="")
            print("|")
        print("   -----------------------")
