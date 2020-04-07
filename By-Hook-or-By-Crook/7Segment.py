import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import more_itertools as mit

def drawCell(cent, vert, scale=1, **kwargs):
    pts = scale * np.array([
        [-45, 0],
        [-30, 15],
        [30, 15],
        [45, 0],
        [30, -15],
        [-30, -15]])
    if vert:
        pts = pts[:,[1,0]]
    pts = pts + np.tile(np.array(cent).reshape((1,2)), (6, 1))
    pch = mpatches.Polygon(pts, **kwargs)
    return pch

def drawDigit(cent, cellOff, scale=1):
    cellCents = scale * np.array([
        [0, 100],
        [50, 50],
        [50, -50],
        [0, -100],
        [-50, -50],
        [-50, 50],
        [0, 0]])
    vert = [False, True, True, False, True, True, False]
    color = ['red' if off else 'green' for off in cellOff]
    patches = [drawCell(cent + cellCents[i,:],
                        vert[i], scale=scale, color=color[i])
               for i in range(7)]
    return patches

# Cell indexing
#     - 0 -
#     5   1
#     | 6 |
#     4   2
#     - 3 -

# Translation from digit to cell on/off
trans = np.zeros((10,7))
trans[0,:] = [1,1,1,1,1,1,0]
trans[1,:] = [0,1,1,0,0,0,0]
trans[2,:] = [1,1,0,1,1,0,1]
trans[3,:] = [1,1,1,1,0,0,1]
trans[4,:] = [0,1,1,0,0,1,1]
trans[5,:] = [1,0,1,1,0,1,1]
trans[6,:] = [1,0,1,1,1,1,1]
trans[7,:] = [1,1,1,0,0,0,0]
trans[8,:] = [1,1,1,1,1,1,1]
trans[9,:] = [1,1,1,1,0,1,1]
names = list('abcdefg')

# All 2-group paritions of columns
partitions = [part for part in mit.set_partitions(range(7)) if len(part) == 2]
# Include inverses
partitions += [part[::-1] for part in partitions]
distinct = []
for p in partitions:
    # Ignore cells in 2nd group, and check which digits distinguishable
    distinct += [[p[1], [row1 for row1 in range(10)
        if not any([all(trans[row1, p[0]] == trans[row2, p[0]])
                    for row2 in range(10) if row1 != row2])]]]

fig, ax = plt.subplots(figsize=(2,3))
for i in range(len(distinct)):
    plt.cla()
    ax.axis('equal')
    ax.axis('off')
    plt.xlim((-75, 75))
    plt.ylim((-175, 125))
    part = distinct[i][0]
    if len(distinct[i][1]) > 0:
        digits = ', '.join([str(a) for a in distinct[i][1]])
    else:
        digits = 'None'
    cellOff = [(cell in part) for cell in range(7)]
    pchs = drawDigit([0,0], cellOff)
    [ax.add_patch(p) for p in pchs]
    plt.text(0, -160, digits,
             horizontalalignment='center',
             verticalalignment='center')
    name = ''.join([names[k] for k in part])
    plt.savefig('{}{}Digit.png'.format(len(part), name))
