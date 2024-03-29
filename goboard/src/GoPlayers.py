"from sphero_formation commit 0ac14aad3"
import numpy as np


class GoPlayer:
    def __init__(self):
        self.passed_last_turn = False


class RandomPlayer(GoPlayer):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def play(self, board):
        a = np.random.randint(self.game.getActionSize())
        valids = self.game.getValidMoves(board, 1)
        while valids[a]!=1:
            a = np.random.randint(self.game.getActionSize())
        return a


class HumanGoPlayer(GoPlayer):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def play(self, board):
        # display(board)
        valid = self.game.getValidMoves(board, 1)
        for i in range(len(valid)):
            if valid[i]:
                print(int(i/self.game.n), int(i%self.game.n), end=" ")
        print("")
        while True:
            try:
                a = input()
                if a == 'pass':
                    a = self.game.PASS
                    break
                x,y = [int(x) for x in a.split(' ')]
                a = self.game.n * x + y if x!= -1 else self.game.n ** 2
                if valid[a]:
                    break
                else:
                    raise Exception('Invalid ')
            except Exception as e:
                print(f'{e}')

        return a


class GreedyGobangPlayer(GoPlayer):
    def __init__(self, game):
        super().__init__()
        self.game = game

    def play(self, board):
        valids = self.game.getValidMoves(board, 1)
        candidates = []
        for a in range(self.game.getActionSize()):
            if valids[a]==0:
                continue
            nextBoard, _ = self.game.getNextState(board, 1, a)
            score = self.game.getScore(nextBoard, 1)
            candidates += [(-score, a)]
        candidates.sort()
        return candidates[0][1]
