import numpy as np
import Arena
from GoGame import GoGame as Game

def init_planner(arena):
    stones = np.zeros((15,15))
    for n in range(24):
        i = n % 15
        j = n // 15
        stones[i,j] = 1
    arena.send("/gomap", stones.astype(np.int32).tobytes())

if __name__ == "__main__":
    game = Game(5)
    arena = Arena.ArenaMQTT(None, None, game, use_mqtt=True)
    # init_planner(arena)
    # test placing the stone
    board_diff = np.zeros((5, 5))
    board_pieces = np.zeros((5, 5))
    board_diff[0, 0] = 1
    board_pieces[0, 0] = 0
    arena.sendBoardToMQTT(board_diff, board_pieces)

    # test removing the stone
    board_diff[0, 0] = -1
    board_pieces[0, 0] = 1
    arena.sendBoardToMQTT(board_diff, board_pieces)