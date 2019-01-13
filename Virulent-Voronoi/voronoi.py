# Draw Voronoi Diagram for a random set of points
# using a given distance function
import numpy as np
import matplotlib.pyplot as plt

# Euclidean distance
def euclid(a, b):
    return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

# Metropolitan/Taxicab metric
def metro(a, b):
    return np.abs(a[0] - b[0]) + np.abs(a[1] - b[1])

# Time-like Relativistic Interval
def relat(a, b):
    dist2 = (a[0] - b[0])**2 - (a[1] - b[1])**2
    if (dist2 < 0):
        return np.Inf
    else:
        return np.sqrt(dist2)

np.random.seed(0)
gridDim = 200
n = 5
nodes = []
grid = np.zeros([gridDim, gridDim])
dfun = euclid
#dfun = metro
#dfun = relat

for k in range(n):
    i = np.random.randint(0, gridDim)
    j = np.random.randint(0, gridDim)
    nodes += [[i, j]]
    grid[i, j] = k + 1

for i in range(gridDim):
    for j in range(gridDim):
        if (grid[i, j] != 0):
            continue

        dists = [dfun([i, j], node) for node in nodes]
        if (min(dists) == np.Inf):
            grid[i, j] = np.nan
            continue
        pt = nodes[dists.index(min(dists))]
        grid[i, j] = grid[pt[0], pt[1]]

plt.matshow(grid, cmap="viridis")
xy = np.transpose(nodes)
plt.scatter(xy[1] + 0.5, xy[0] + 0.5, c = "black")
ax = plt.gca()
ax.invert_yaxis()
plt.show()
