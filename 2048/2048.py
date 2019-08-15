import numpy as np
from random import randrange
from random import choice
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LogNorm
import easyAI

import warnings
warnings.simplefilter('error', UserWarning)

cmap = cm.get_cmap('viridis')
plt.ion()

class GameOf2048( easyAI.TwoPlayersGame ):
    def addBox(self):
        choices = np.array(np.where(self.board == 0))
        if (np.shape(choices)[1] == 0):
            return False
        box = choices[:, randrange(np.shape(choices)[1])]
        self.board[box[0], box[1]] = choice((2, 2, 2, 4))
        return True

    def printBoard(self):
        for i in range(np.shape(self.board)[0]):
            for j in range(np.shape(self.board)[1]):
                print(str(self.board[i, j]) + "\t", end="")
            print("")
        print("\t    2 \n\t  0   1\n\t    3")
        print("Score: {}".format(self.score))

    def drawBoard(self, score, fig):
        (m, n) = np.shape(self.board)
        ax = fig.gca()
        ax.clear()
        for x in range(n + 1):
            ax.plot([x, x], [0, m], 'k')
        for y in range(m + 1):
            ax.plot([0, n], [y, y], 'k')
        for i in range(m):
            for j in range(n):
                x = j + 0.5
                y = i + 0.5
                ax.fill([x - 0.4, x + 0.4, x + 0.4, x - 0.4],
                        [y + 0.4, y + 0.4, y - 0.4, y - 0.4],
                        c = cmap(LogNorm(0.1, 2048)(self.board[i, j] + 0.1)),
                        alpha = 0.6)
                ax.text(x, y, str(self.board[i, j]),
                        horizontalalignment = 'center',
                        verticalalignment = 'center',
                        fontsize = 12)
        plt.axis('off')
        plt.title(str(score))
        plt.pause(1)

    def initBoard(self):
        (m, n) = np.shape(self.board)
        fig = plt.figure(1, figsize = [m, n])
        ax = fig.add_subplot(111)
        drawBoard(self.board, 0, fig)
        return fig

    def moveLeft(self, score):
        board = np.copy(self.board)
        (m, n) = np.shape(board)
        for i in range(m):
            row = board[i, :]
            row = row[row != 0]
            for j in range(len(row) - 1):
                if (row[j] == row[j + 1]):
                    row[j] += row[j + 1]
                    row[j + 1] = 0
                    score += row[j]
            row = row[row != 0]
            row = np.concatenate((row, np.zeros(n - len(row), np.int32)))
            board[i, :] = row
        return (board, score)

    def moveRight(self, score):
        board = np.copy(self.board)
        (m, n) = np.shape(board)
        for i in range(m):
            row = board[i, :]
            row = row[row != 0]
            for j in reversed(range(1, len(row))):
                if (row[j] == row[j - 1]):
                    row[j] += row[j - 1]
                    row[j - 1] = 0
                    score += row[j]
            row = row[row != 0]
            row = np.concatenate((np.zeros(n - len(row), np.int32), row))
            board[i, :] = row
        return (board, score)

    def moveUp(self, score):
        board = np.copy(self.board)
        (m, n) = np.shape(board)
        for j in range(n):
            col = board[:, j]
            col = col[col != 0]
            for i in range(len(col) - 1):
                if (col[i] == col[i + 1]):
                    col[i] += col[i + 1]
                    col[i + 1] = 0
                    score += col[i]
            col = col[col != 0]
            col = np.concatenate((col, np.zeros(m - len(col), np.int32)))
            board[:, j] = col
        return (board, score)

    def moveDown(self, score):
        board = np.copy(self.board)
        (m, n) = np.shape(board)
        for j in range(n):
            col = board[:, j]
            col = col[col != 0]
            for i in reversed(range(1, len(col))):
                if (col[i] == col[i - 1]):
                    col[i] += col[i - 1]
                    col[i - 1] = 0
                    score += col[i]
            col = col[col != 0]
            col = np.concatenate((np.zeros(m - len(col), np.int32), col))
            board[:, j] = col
        return (board, score)

    def noMoves(self):
        if (not np.array_equal(self.board, self.moveLeft(0)[0])):
            return False
        if (not np.array_equal(self.board, self.moveRight(0)[0])):
            return False
        if (not np.array_equal(self.board, self.moveUp(0)[0])):
            return False
        if (not np.array_equal(self.board, self.moveDown(0)[0])):
            return False
        return True

    def bestMove(self, score, method = "random", look = 1):
        if (look == 0 or noMoves(self.board)):
            return (self.board, score)
        moves = np.array((moveLeft(self.board, score),
                          moveRight(self.board, score),
                          moveUp(self.board, score),
                          moveDown(self.board, score)))
        moves[list(map(lambda x: np.array_equal(self.board, x[0]), moves)), 1] = -1
        moves = list(map(lambda x: bestMove(x[0], x[1], method, look - 1), moves))
        scores = np.array(list(map(lambda x: x[1], moves)))
        spaces = np.array(list(map(lambda x: np.sum(x[0].flatten() == 0), moves)))
        if (method is "score"):
            best = np.where(scores == max(scores))[0]
        elif (method is "spaces"):
            best = np.where(spaces == max(spaces))[0]
        elif (method is "random"):
            best = np.where(scores > -1)[0]
        else:
            raise ValueError("Unknown method: "+method)
        if (all(scores < 0)):
            return (self.board, score)
        move = choice(best)
        if (move == 0):
            return moveLeft(self.board, score)
        elif (move == 1):
            return moveRight(self.board, score)
        elif (move == 2):
            return moveUp(self.board, score)
        elif (move == 3):
            return moveDown(self.board, score)
        return (self.board, score)

    def __init__(self, players):
        self.board = np.zeros((4, 4), np.int32)
        self.nMoves = 0
        for i in range(2):
            self.addBox()
        self.score = 0
        self.players = players
        self.nplayer = 1

    def possible_moves(self):
        moves = []
        if (not np.array_equal(self.board, self.moveLeft(0)[0])):
            moves += [0]
        if (not np.array_equal(self.board, self.moveRight(0)[0])):
            moves += [1]
        if (not np.array_equal(self.board, self.moveUp(0)[0])):
            moves += [2]
        if (not np.array_equal(self.board, self.moveDown(0)[0])):
            moves += [3]
        return(moves)

    def make_move(self, move):
        if (move == 0):
            self.board, self.score = self.moveLeft(self.score)
        elif (move == 1):
            self.board, self.score = self.moveRight(self.score)
        elif (move == 2):
            self.board, self.score = self.moveUp(self.score)
        elif (move == 3):
            self.board, self.score = self.moveDown(self.score)
        self.addBox()
        return

    def lose(self):
        return(self.noMoves())

    def is_over(self):
        return(self.lose())

    def show(self):
        self.printBoard()

    def scoring(self):
        return(np.sum(self.board == 0))
        #return(self.score)

if __name__ == "__main__":
    ai9 = easyAI.SSS(5)
    ai0 = easyAI.SSS(5)
    game = GameOf2048([easyAI.AI_Player(ai9), easyAI.AI_Player(ai0)])
    history = game.play()
    
