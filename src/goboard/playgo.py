import argparse
import numpy as np

from .Arena import Arena
from .MCTS import MCTS
from .kerasclasses.NNet import NNetWrapper as NNet

from .ROSGoGame import ROSGoGame
from .GoPlayers import RandomPlayer, HumanGoPlayer, GreedyGobangPlayer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('__name',       type=str, default='goboard')
    parser.add_argument('__log',        type=str, default='log.txt')
    parser.add_argument('--board_size', type=int, default=5)
    parser.add_argument('--num_games',  type=int, default=2)
    parser.add_argument('--player1',    type=str, default='human')
    parser.add_argument('--player2',    type=str, default='random')

    args = parser.parse_args()
    board_size = args.board_size
    num_games = args.num_games
    player1 = args.player1
    player2 = args.player2

    g = ROSGoGame(board_size)
    # g = GobangGame(board_size)

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
        n1 = NNet(g)
        # todo provide a model file
        # n1.load_checkpoint('./pretrained_models/othello/pytorch/', '6x100x25_best.pth.tar')
        args1 = {'numMCTSSims': 50, 'cpuct': 1.0}
        mcts1 = MCTS(g, n1, args1)
        player1 = lambda x: np.argmax(mcts1.getActionProb(x, temp=0))
    else:
        player1 = players[player1[0]]

    if player2[0] == 'a':
        n2 = NNet(g)
        # n2.load_checkpoint('./pretrained_models/othello/pytorch/', '8x8_100checkpoints_best.pth.tar')
        args2 = {'numMCTSSims': 50, 'cpuct': 1.0}
        mcts2 = MCTS(g, n2, args2)
        n2p = lambda x: np.argmax(mcts2.getActionProb(x, temp=0))
        player2 = n2p  # Player 2 is neural network if it's cpu vs cpu.
    else:
        player2 = players[player2[0]]

    arena = Arena(player1, player2, g, display=ROSGoGame.display)

    print(arena.playGames(num_games, verbose=True))