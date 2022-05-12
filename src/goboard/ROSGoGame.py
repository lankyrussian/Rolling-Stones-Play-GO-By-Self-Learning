"from sphero_formation commit 0ac14aad3"

from __future__ import print_function

from .Game import Game
from .GoLogic import Board
import numpy as np
import rospy
from std_msgs.msg import Int8MultiArray, Bool, UInt8


class ROSGoGame(Game):
    def __init__(self, n=5, nir=5):
        self.n = n
        self.n_in_row = nir
        self.b = Board(self.n)
        # ROS
        # flag indicating if robot stones are moved to their positions,
        # and the next move can be made
        self.board_ready = False
        # we will publish a flat int array to GoBoard/board on every move
        self.pub = rospy.Publisher('board', Int8MultiArray, queue_size=10)
        rospy.init_node('GoBoard', anonymous=True)
        # the robot controller will report when the robots are in positions
        rospy.Subscriber('board_ready', Bool, self.boardReadyCB)
        # if someone asks for the board info, we will send it after hearing from this topic
        rospy.Subscriber('info', Int8MultiArray, self.boardInfoCB)
        # keep track of consecutive passes
        self.pass_count = 0

    def boardReadyCB(self, data: Bool):
        self.board_ready = data.data

    def boardInfoCB(self, _: Bool):
        info_msg = UInt8()
        info_msg.data = self.n
        self.pub.publish(info_msg)

    def getInitBoard(self):
        # return initial board (numpy board)
        b = Board(self.n)
        return np.array(b.pieces)

    def getBoardSize(self):
        # (a,b) tuple
        return (self.n, self.n)

    def getActionSize(self):
        # return number of actions
        return self.n * self.n + 1

    def sendBoardToROS(self, board):
        # send board to ROS
        board_msg = Int8MultiArray()
        board_msg.data = board.flatten().tolist()
        self.pub.publish(board_msg)

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        if action == self.n * self.n:
            return (board, -player)
        self.b.pieces = np.copy(board)
        old_board = np.copy(self.b.pieces)
        move = (int(action / self.n), action % self.n)
        self.b.execute_move(move, player)
        board_diff = self.b.pieces - old_board
        self.sendBoardToROS(board_diff)
        return (self.b.pieces, -player)

    # modified
    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0] * self.getActionSize()

        self.b.pieces = np.copy(board)
        legalMoves = self.b.get_legal_moves(player)
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
        b = Board(self.n)
        b.pieces = np.copy(board)
        n = self.n_in_row

        # both players passed
        if self.pass_count == 2:
            return 1 if b.countDiff() > 0 else -1 if b.countDiff() < 0 else 0.5

        if b.has_legal_moves():
            return 0
        return 1e-4

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        return player * board

    # modified
    def getSymmetries(self, board, pi):
        # mirror, rotational
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
        # 8x8 numpy array (canonical board)
        return board.tostring()

    @staticmethod
    def display(board):
        n = board.shape[0]

        for y in range(n):
            print(y, "|", end="")
        print("")
        print(" -----------------------")
        for y in range(n):
            print(y, "|", end="")    # print the row #
            for x in range(n):
                piece = board[y][x]    # get the piece to print
                if piece == -1:
                    print("b ", end="")
                elif piece == 1:
                    print("W ", end="")
                else:
                    if x == n:
                        print("-", end="")
                    else:
                        print("- ", end="")
            print("|")
        print("   -----------------------")
