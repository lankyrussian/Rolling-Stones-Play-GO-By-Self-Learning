import argparse
import numpy as np

from Arena import Arena
from MCTS import MCTS
from NNet import NNetWrapper as nn
from GoPlayers import RandomPlayer, HumanGoPlayer, GreedyGobangPlayer
from GoGame import GoGame
from utils import dotdict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name',       type=str, default='goboard')
    parser.add_argument('--log',        type=str, default='log.txt')
    parser.add_argument('--board_size', type=int, default=5)
    parser.add_argument('--num_games',  type=int, default=10)
    parser.add_argument('--com_type', type=str, default="mqtt")
    parser.add_argument('--player1',    type=str, default='a')
    parser.add_argument('--player2',    type=str, default='a')
    parser.add_argument('--mqtt_broker', type=str, default='localhost')
    parser.add_argument('--mqtt_port', type=int, default=1883)

    args = parser.parse_args()
    board_size = args.board_size
    num_games = args.num_games
    player1 = args.player1
    player2 = args.player2

    if args.com_type == "mqtt":
        from MQTTGoGame import MQTTGoGame
        g = MQTTGoGame(board_size, args.mqtt_broker, args.mqtt_port)
    elif args.com_type == "ros":
        from ROSGoGame import ROSGoGame
        g = ROSGoGame(board_size)
    else:
        raise ValueError("Invalid communication type, should be either mqtt or ros")

    # all players
    players = {
        "r": RandomPlayer(g).play,
        "g": GreedyGobangPlayer(g).play,
        "h": HumanGoPlayer(g).play,
        "a": True
    }

    # player1
    if player1[0] == 'a':
        # nnet players
        n1 = nn(g)
        n1.load_checkpoint('./pretrained/', 'checkpoint_3.pth.tar')
        args1 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
        mcts1 = MCTS(g, n1, args1)
        player1 = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))
    else:
        player1 = players[player1[0]]

    if player2[0] == 'a':
        n2 = nn(g)
        n2.load_checkpoint('/home/vlad/PycharmProjects/Rolling-Stones-Play-GO-By-Self-Learning/goboard/src/pretrained', 'checkpoint_3.pth.tar')
        args2 = dotdict({'numMCTSSims': 50, 'cpuct': 1.0})
        mcts2 = MCTS(g, n2, args2)
        n2p = lambda x: np.argmax(mcts2.getActionProb(x, temp=0))
        player2 = n2p  # Player 2 is neural network if it's cpu vs cpu.
    else:
        player2 = players[player2[0]]

    arena = Arena(player1, player2, g, display=GoGame.display)

    print(arena.playGames(num_games, verbose=True))


if __name__ == "__main__":
    main()
