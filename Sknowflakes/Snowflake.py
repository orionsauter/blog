import numpy as np
import random as rdm
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

debug = False
# Number of cells/steps
nx = 75
ny = 61
nt = 30
# Distance between cells
dx = 1.0
dy = np.sqrt(3)/2.0
# Distance from center to corners
r = 1.0/np.sqrt(3)
# Neighbor directions for even and odd rows
edirs = np.array([
    [1, 0],
    [0, -1],
    [-1, -1],
    [-1, 1],
    [0, 1],
    [-1, 0]])
odirs = np.array([
    [1, 0],
    [1, -1],
    [0, -1],
    [-1, 0],
    [0, 1],
    [1, 1]])

def hexagon(x, y, c='black'):
    if (y % 2 == 0):
        pts = np.array([[x*dx + r*np.cos(phi+np.pi/6.),
                         y*dy + r*np.sin(phi+np.pi/6.)]
                        for phi in np.arange(0, 2*np.pi, np.pi/3)])
    else:
        pts = np.array([[(x+0.5)*dx + r*np.cos(phi+np.pi/6.),
                         y*dy + r*np.sin(phi+np.pi/6.)]
                        for phi in np.arange(0, 2*np.pi, np.pi/3)])
    return(Polygon(pts, color=c))

def neighbors(x, y):
    if (y % 2 == 0):
        neigh = np.array([[x+edirs[i,0], y+edirs[i,1]]
                          for i in range(edirs.shape[0])
                          if (x+edirs[i,0] >= 0 and y+edirs[i,1] >= 0
                              and x+edirs[i,0] < nx and y+edirs[i,1] < ny)])
    else:
        neigh = np.array([[x+odirs[i,0], y+odirs[i,1]]
                          for i in range(odirs.shape[0])
                          if (x+odirs[i,0] >= 0 and y+odirs[i,1] >= 0
                              and x+odirs[i,0] < nx and y+odirs[i,1] < ny)])
    return neigh

def display(grid, name="snowflake.png"):
    # Find filled cells
    cells = np.transpose(np.where(grid))
    hexes = [hexagon(cells[i,0], cells[i,1])
             for i in range(cells.shape[0])]
    fig = plt.figure(figsize=(4,4))
    ax = fig.add_axes([0,0,1,1])
    [ax.add_patch(p) for p in hexes]
    ax.axis('off')
    ax.axis('equal')
    plt.xlim((-1,nx))
    plt.ylim((-1,ny))
    if debug:
        for i in range(nx):
            for j in range(ny):
                neigh = neighbors(i, j)
                tot = np.sum([grid[neigh[k,0], neigh[k,1]]
                              for k in range(neigh.shape[0])])
                if j % 2 == 0:
                    plt.text(i*dx, j*dy, "{},{}".format(i,j),
                             bbox=dict(facecolor='white'),
                             fontsize=8,
                             horizontalalignment='center',
                             verticalalignment='center')
                else:
                    plt.text((i+0.5)*dx, j*dy, "{},{}".format(i,j),
                             bbox=dict(facecolor='white'),
                             fontsize=8,
                             horizontalalignment='center',
                             verticalalignment='center')
    plt.savefig(name)
    plt.close(fig)

grid = np.zeros((nt+1, nx, ny))
grid[0,37,30] = 1
display(grid[0,:,:], "imgs/snowflake-{:02d}.png".format(0))

for t in range(1, nt):
    grid[t,:,:] = grid[t-1,:,:]
    totals = np.zeros((nx,ny))
    for i in range(nx):
        for j in range(ny):
            neigh = neighbors(i, j)
            tot = np.sum([grid[t-1, neigh[k,0], neigh[k,1]]
                          for k in range(neigh.shape[0])])
            totals[i,j] = tot
            if (tot == 1):
                grid[t,i,j] = 1
    display(grid[t,:,:], "imgs/snowflake-{:02d}.png".format(t))
    # Stop if we hit the edge
    if (any(grid[t,0,:]) or
        any(grid[t,nx-1,:]) or
        any(grid[t,:,0]) or
        any(grid[t,:,ny-1])):
        break
