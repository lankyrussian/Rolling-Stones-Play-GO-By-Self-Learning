from __future__ import print_function

import rospy
from std_msgs.msg import Int8MultiArray, Bool, UInt8
from GoGame import GoGame


class ROSGoGame(GoGame):
    def __init__(self, n=5):
        GoGame.__init__(self, n)
        # we will publish a flat int array to GoBoard/board on every move
        self.pub = rospy.Publisher('board', Int8MultiArray, queue_size=10)
        rospy.init_node('GoBoard', anonymous=True)
        # the robot controller will report when the robots are in positions
        rospy.Subscriber('board_ready', Bool, self.boardReadyCB)
        # if someone asks for the board info, we will send it after hearing from this topic
        rospy.Subscriber('info', Int8MultiArray, self.boardInfoCB)
        # ROS
        # flag indicating if robot stones are moved to their positions,
        # and the next move can be made
        self.board_ready = False

    def boardReadyCB(self, data: Bool):
        self.board_ready = data.data

    def boardInfoCB(self, _: Bool):
        info_msg = UInt8()
        info_msg.data = self.n
        self.pub.publish(info_msg)

    def sendBoardToROS(self, board):
        # send board to ROS
        board_msg = Int8MultiArray()
        board_msg.data = board.flatten().tolist()
        self.pub.publish(board_msg)

    def getNextState(self, board, player, action):
        new_board, player = super().getNextState(board, player, action)
        board_diff = new_board - board
        self.sendBoardToROS(board_diff)
        return (self.b.pieces, player)
