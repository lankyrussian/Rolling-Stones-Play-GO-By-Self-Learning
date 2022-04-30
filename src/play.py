import argparse
import sys
import numpy as np
sys.path.append('../alpha-zero-general/')

import Arena, MCTS
from gobang.keras.NNet import NNetWrapper as NNet

import Go.GoGame as GoGame
from Go.GoPlayers import RandomPlayer, HumanGoPlayer, GreedyGobangPlayer


if __name__ =="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--board_size', type=int, default=9)
    parser.add_argument('--num_games', type=int, default=1)
    parser.add_argument('--player1', type=str, default='human')
    parser.add_argument('--player2', type=str, default='random')

    args = parser.parse_args()
    board_size = args.board_size
    num_games = args.num_games
    player1 = args.player1
    player2 = args.player2

    g = GoGame.ROSGoGame()

    # all players

    players = {
        "r": RandomPlayer(g).play,
        "g": GreedyGobangPlayer(g).play,
        "h": HumanGoPlayer(g).play,
        "a": True
    }

    # player1
    if player1[0] != 'h':
        # nnet players
        n1 = NNet(g)
        n1.load_checkpoint('./pretrained_models/othello/pytorch/','6x100x25_best.pth.tar')
        args1 = {'numMCTSSims': 50, 'cpuct':1.0}
        mcts1 = MCTS(g, n1, args1)
        player1 = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))

    if player2[0] != 'h':
        n2 = NNet(g)
        n2.load_checkpoint('./pretrained_models/othello/pytorch/', '8x8_100checkpoints_best.pth.tar')
        args2 = {'numMCTSSims': 50, 'cpuct': 1.0}
        mcts2 = MCTS(g, n2, args2)
        n2p = lambda x: np.argmax(mcts2.getActionProb(x, temp=0))
        player2 = n2p  # Player 2 is neural network if it's cpu vs cpu.

    arena = Arena.Arena(player1, player2, g, display=GoGame.ROSGoGame.display)

    print(arena.playGames(2, verbose=True))