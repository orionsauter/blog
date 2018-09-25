import numpy as np
from random import randrange
from random import choice
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LogNorm

import warnings
warnings.simplefilter('error', UserWarning)

cmap = cm.get_cmap('viridis')
plt.ion()

def addBox(board):
    choices = np.array(np.where(board == 0))
    if (np.shape(choices)[1] == 0):
        return False
    box = choices[:, randrange(np.shape(choices)[1])]
    board[box[0], box[1]] = choice((2, 2, 2, 4))
    return True

def printBoard(board):
    for i in range(np.shape(board)[0]):
        for j in range(np.shape(board)[1]):
            print(str(board[i, j]) + "\t")
        print("\n")

def drawBoard(board, score, fig):
    (m, n) = np.shape(board)
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
                    c = cmap(LogNorm(0.1, 2048)(board[i, j] + 0.1)),
                    alpha = 0.6)
            ax.text(x, y, str(board[i, j]),
                    horizontalalignment = 'center',
                    verticalalignment = 'center',
                    fontsize = 12)
    plt.axis('off')
    plt.title(str(score))
    plt.pause(1)

def initBoard(board):
    (m, n) = np.shape(board)
    fig = plt.figure(1, figsize = [m, n])
    ax = fig.add_subplot(111)
    drawBoard(board, 0, fig)
    return fig

def moveLeft(board, score):
    board = np.copy(board)
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

def moveRight(board, score):
    board = np.copy(board)
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

def moveDown(board, score):
    board = np.copy(board)
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

def moveUp(board, score):
    board = np.copy(board)
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

def noMoves(board):
    if (not np.array_equal(board, moveLeft(board, 0)[0])):
        return False
    if (not np.array_equal(board, moveRight(board, 0)[0])):
        return False
    if (not np.array_equal(board, moveUp(board, 0)[0])):
        return False
    if (not np.array_equal(board, moveDown(board, 0)[0])):
        return False
    return True

def bestMove(board, score, method = "random", look = 1):
    if (look == 0 or noMoves(board)):
        return (board, score)
    moves = np.array((moveLeft(board, score),
                      moveRight(board, score),
                      moveUp(board, score),
                      moveDown(board, score)))
    moves[list(map(lambda x: np.array_equal(board, x[0]), moves)), 1] = -1
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
        return (board, score)
    move = choice(best)
    if (move == 0):
        return moveLeft(board, score)
    elif (move == 1):
        return moveRight(board, score)
    elif (move == 2):
        return moveUp(board, score)
    elif (move == 3):
        return moveDown(board, score)
    return (board, score)

def runGame(method = "score", look = 1, plot = False):
    board = np.zeros((4, 4), np.int32)
    nMoves = 0
    for i in range(2):
        addBox(board)
    score = 0
    if (plot):
        fig = initBoard(board)
        drawBoard(board, score, fig)
    while (not noMoves(board) and max(board.flatten()) < 2048):
        (board, score) = bestMove(board, score, method, look)
        nMoves += 1
        addBox(board)
        if (plot):
            drawBoard(board, score, fig)
    return (score, max(board.flatten()), nMoves)

##runGame(1, True)
games = np.array(list(map(lambda x: runGame("spaces", 2, False), range(1000))))
print(np.mean(games[:,0]))
print(np.mean(games[:,1] >= 2048))
print(np.mean(games[:,2]))
