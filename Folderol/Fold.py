import numpy as np
import matplotlib.pyplot as plt

def Neighbors(arr, i, j):
    nbrs = []
    if (i > 0):
        nbrs += [(0, i-1, j)]
    if (j > 0):
        nbrs += [(0, i, j-1)]
    if (i < arr.shape[0]-1):
        nbrs += [(0, i+1, j)]
    if (j < arr.shape[1]-1):
        nbrs += [(0, i, j+1)]
    return(nbrs)

def PadToShape(arr, shape):
    # Find where zeros are needed
    fit = np.array(shape) - np.array(arr.shape)
    height = arr.shape[0]
    # Pad array at top left only
    out = np.pad(arr, (np.max(fit[1:]), 0), mode='constant', constant_values=0)
    # Trim to the correct size
    return(out[(out.shape[0]-height):, fit[2]:, fit[1]:])

def Fold(arr, pos, axis):
    # Break array at [pos] in direction [axis]
    a, b = np.split(arr, [pos], axis=axis)
    if (a.shape[axis] < b.shape[axis]):
        a = PadToShape(a, b.shape)
    else:
        b = PadToShape(b, a.shape)
    # Flip along [axis] and also front to back
    # Use negative to indicate downward-facing sides
    out = np.concatenate((np.flip(-b, axis=[0,axis]), a), axis=0)
    return(out)

def ShowFolds(arr, stk):
    # 90 deg rotation matrix
    R = np.array([[0,-1],[1,0]])
    plt.figure(figsize=(3,3))
    plt.plot([0, 0], [0, arr.shape[1]], 'k-')
    plt.plot([0, arr.shape[1]], [arr.shape[2], arr.shape[1]], 'k-')
    plt.plot([arr.shape[2], arr.shape[1]], [arr.shape[2], 0], 'k-')
    plt.plot([arr.shape[2], 0], [0, 0], 'k-')
    for i in range(arr.shape[1]):
        for j in range(arr.shape[2]):
            for nbr in Neighbors(arr, i, j):
                i1 = np.where(np.abs(stk) == arr[0, i, j])[0][0]
                i2 = np.where(np.abs(stk) == arr[nbr])[0][0]
                val1 = stk[i1]
                val2 = stk[i2]
                # Get line connecting boxes, then rotate to make edge
                center = 0.5 * np.array([[i+nbr[1]], [j+nbr[2]]])
                pt1 = (R.dot(np.array([[i],[j]]) - center) + center + 0.5)
                pt2 = (R.dot(np.array([[nbr[1]],[nbr[2]]]) - center) + center + 0.5)
                # Need [x1, x2], [y1, y2]
                mat = np.concatenate((pt1, pt2), axis=1)
                if ((i1 < i2 and val1 > 0) or (i1 > i2 and val2 > 0)):
                    # Valley fold
                    plt.plot(mat[0,:], mat[1,:], 'r-')
                else:
                    # Mountain fold
                    plt.plot(mat[0,:], mat[1,:], 'b-')
    plt.gca().set_aspect('equal', 'box')
    plt.gca().invert_yaxis()

if __name__ == "__main__":
    n = 3
    arr = np.array(np.arange(n*n)+1).reshape((1,n,n))
    # Alternate dir
    stk = Fold(Fold(Fold(Fold(arr, 1, 1), 1, 2), 1, 1), 1, 2).flatten()
    ShowFolds(arr, stk)
    plt.show()

    # Same dir    
    stk = Fold(Fold(Fold(Fold(arr, 2, 2), 1, 2), 1, 1), 1, 1).flatten()
    ShowFolds(arr, stk)
    plt.show()
