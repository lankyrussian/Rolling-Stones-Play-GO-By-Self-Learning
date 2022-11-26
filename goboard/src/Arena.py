"from sphero_formation commit 0ac14aad3"

import logging
import struct

import numpy as np
import paho.mqtt.client as mqtt

from tqdm import tqdm

log = logging.getLogger(__name__)


class ArenaMQTT():
    """
    An Arena class where any 2 agents can be pit against each other.
    """

    def __init__(self, player1, player2, game, display=None, use_mqtt=False, broker='localhost', port=1883):
        """
        Input:
            player 1,2: two functions that takes board as input, return action
            game: Game object
            display: a function that takes board as input and prints it (e.g.
                     display in othello/OthelloGame). Is necessary for verbose
                     mode.

        see othello/OthelloPlayers.py for an example. See pit.py for pitting
        human players/other baselines with each other.
        """
        self.player1 = player1
        self.player2 = player2
        self.game = game
        self.display = display
        self.broker = broker
        self.port = port
        self.use_mqtt = use_mqtt
        self.client = mqtt.Client() if use_mqtt else None

    def send(self, topic, msg):
        self.client.connect(self.broker, self.port)
        self.client.publish(topic, msg)
        self.client.disconnect()

    def sendBoardToMQTT(self, board_diff, board_pieces):
        # send stone positions, move/remove, color to pathfinding algorithm
        n = board_diff.shape[0]
        for pos, val in np.ndenumerate(board_diff):
            if val != 0:
                idx = pos[0] * n + pos[1]
                print(f'sending {idx}')
                if board_pieces[pos] == 0:
                    msg = struct.pack('ii', idx, 0)
                    self.send("/gomove", msg)
                else:
                    color = 1 if board_pieces[pos] == 1 else -1
                    msg = struct.pack('ii', idx, color)
                    self.send("/gomove", msg)

    def playGame(self, verbose=False):
        """
        Executes one episode of a game.

        Returns:
            either
                winner: player who won the game (1 if player1, -1 if player2)
            or
                draw result returned from the game that is neither 1, -1, nor 0.
        """
        players = [self.player2, None, self.player1]
        curPlayer = 1
        board = self.game.getInitBoard()
        it = 0
        while self.game.getGameEnded(board, curPlayer) == 0:
            it += 1
            if verbose:
                assert self.display
                print("Turn ", str(it), "Player ", str(curPlayer))
                self.display(board)
            action = players[curPlayer + 1](self.game.getCanonicalForm(board, curPlayer))

            valids = self.game.getValidMoves(board, curPlayer)

            if valids[action] == 0:
                log.error(f'Action {action} is not valid! Ending the game prematurely.')
                log.debug(f'valids = {valids}')
                board.game_ended = True
                break
            new_board, curPlayer = self.game.getNextState(board, curPlayer, action)
            # send board difference to mqtt
            if self.use_mqtt:
                board_diff = new_board.pieces - board.pieces
                self.sendBoardToMQTT(board_diff, board)
            board = new_board
        if verbose:
            assert self.display
            print("Game over: Turn ", str(it), "Result ", str(self.game.getGameEnded(board, 1)))
            self.display(board)
        return curPlayer * self.game.getGameEnded(board, curPlayer)

    def playGames(self, num, verbose=False):
        """
        Plays num games in which player1 starts num/2 games and player2 starts
        num/2 games.

        Returns:
            oneWon: games won by player1
            twoWon: games won by player2
            draws:  games won by nobody
        """

        num = int(num / 2)
        oneWon = 0
        twoWon = 0
        draws = 0
        for _ in tqdm(range(num), desc="Arena.playGames (1)"):
            gameResult = self.playGame(verbose=verbose)
            if gameResult == 1:
                oneWon += 1
            elif gameResult == -1:
                twoWon += 1
            else:
                draws += 1

        self.player1, self.player2 = self.player2, self.player1

        for _ in tqdm(range(num), desc="Arena.playGames (2)"):
            gameResult = self.playGame(verbose=verbose)
            if gameResult == -1:
                oneWon += 1
            elif gameResult == 1:
                twoWon += 1
            else:
                draws += 1

        return oneWon, twoWon, draws
