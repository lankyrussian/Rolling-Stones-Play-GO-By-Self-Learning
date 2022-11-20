from __future__ import print_function

import struct

import numpy as np
import paho.mqtt.client as mqtt
from GoGame import GoGame


class MQTTGoGame(GoGame):
    def __init__(self, n=5, broker="localhost", port=1883):
        GoGame.__init__(self, n)
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()

    def send(self, topic, msg):
        self.client.connect(self.broker, self.port)
        self.client.publish(topic, msg)
        self.client.disconnect()

    def sendBoardToMQTT(self, board_diff, board):
        # send stone positions, move/remove, color to pathfinding algorithm
        for pos, val in np.ndenumerate(board_diff):
            if val != 0:
                idx = pos[0] * self.n + pos[1]
                if board.pieces[pos] == 0:
                    msg = struct.pack('ii', idx, 0)
                    self.send("goboard", msg)
                else:
                    color = 1 if board.pieces[pos] == 1 else -1
                    msg = struct.pack('ii', idx, color)
                    self.send("goboard", msg)

    def getNextState(self, board, player, action):
        new_board, player = super().getNextState(board, player, action)
        board_diff = new_board.pieces - board.pieces
        self.sendBoardToMQTT(board_diff, board)
        return (new_board, player)
