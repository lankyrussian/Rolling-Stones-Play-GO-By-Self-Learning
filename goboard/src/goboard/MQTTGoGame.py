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

    def sendBoardToROS(self, board_diff):
        # send stone positions, move/remove, color to pathfinding algorithm
        for pos, val in np.ndenumerate(board_diff):
            if val != 0:
                idx = pos[0] * self.n + pos[1]
                if self.b.pieces[pos] == 0:
                    msg = struct.pack('H', idx)
                    self.send("board/remove", msg)
                else:
                    color = 1 if self.b.pieces[pos] == 1 else 0
                    msg = struct.pack('H?', idx, color)
                    self.send("board/move", msg)

    def getNextState(self, board, player, action):
        new_board, player = super().getNextState(board, player, action)
        board_diff = new_board - board
        self.sendBoardToROS(board_diff)
        return (self.b.pieces, player)
