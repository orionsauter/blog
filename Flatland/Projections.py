#import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Set up colormap
from matplotlib.colors import LinearSegmentedColormap as cmapper
cmapLigo = cmapper.from_list("ligo", ["linen", "red"], 256)
cmapLigo._init()

def greatprob(xy1, xy2):
    d = np.arccos(np.sin(xy1[1])*np.sin(xy2[1]) +
                  np.cos(xy1[1])*np.cos(xy2[1])*np.cos(xy1[0]-xy2[0]))
    return(d)

def gaussian(x, xhat, sigma):
    return(1/(sigma * np.sqrt(2*np.pi)) * np.exp(-0.5*((x-xhat)/sigma)**2))

n = 200
ra, dec = np.meshgrid(np.linspace(-np.pi, np.pi, 2*n + 1),
                      np.linspace(-np.pi/2, np.pi/2, n + 1),
                      indexing = "ij")
prob = np.zeros_like(ra)
circ = np.zeros_like(ra)
cent = [np.pi/6, np.pi/3]
dist = np.zeros_like(ra)
for i in range(2*n + 1):
    for j in range(n + 1):
        dist[i][j] = greatprob([ra[i][j], dec[i][j]], cent)
radius = np.pi/3
width = 0.075
prob += gaussian(dist, radius, width)
circ[np.abs(dist - radius) < width] += 1

cent = [np.pi/3, np.pi/3]
dist = np.zeros_like(ra)
for i in range(2*n + 1):
    for j in range(n + 1):
        dist[i][j] = greatprob([ra[i][j], dec[i][j]], cent)
radius = np.pi/4
width = 0.1
prob *= gaussian(dist, radius, width)
circ[np.abs(dist - radius) < width] += 1

fig = plt.figure(frameon=False)
ax = plt.axes(projection='aitoff')
plt.title("Aitoff")
plt.pcolormesh(ra, dec, circ, cmap=cmapLigo)
ax.grid()
plt.savefig("aitoff-circ.png")

fig = plt.figure(frameon=False)
ax = plt.axes(projection='aitoff')
plt.title("Aitoff")
plt.pcolormesh(ra, dec, prob, cmap=cmapLigo)
ax.grid()
plt.savefig("aitoff-prob.png")

fig = plt.figure(frameon=False)
ax = plt.axes(projection='hammer')
plt.title("Hammer")
plt.pcolormesh(ra, dec, circ, cmap=cmapLigo)
ax.grid()
plt.savefig("hammer-circ.png")

fig = plt.figure(frameon=False)
ax = plt.axes(projection='hammer')
plt.title("Hammer")
plt.pcolormesh(ra, dec, prob, cmap=cmapLigo)
ax.grid()
plt.savefig("hammer-prob.png")

fig = plt.figure(frameon=False)
ax = plt.axes(projection='lambert', center_longitude = 0, center_latitude = np.pi/2)
plt.title("Lambert")
plt.pcolormesh(ra, dec, circ, cmap=cmapLigo)
ax.grid()
plt.savefig("lambert-circ.png")

fig = plt.figure(frameon=False)
ax = plt.axes(projection='lambert', center_longitude = 0, center_latitude = np.pi/2)
plt.title("Lambert")
plt.pcolormesh(ra, dec, prob, cmap=cmapLigo)
ax.grid()
plt.savefig("lambert-prob.png")

fig = plt.figure(frameon=False)
ax = plt.axes(projection='mollweide')
plt.title("Mollweide")
plt.pcolormesh(ra, dec, circ, cmap=cmapLigo)
ax.grid()
plt.savefig("mollweide-circ.png")

fig = plt.figure(frameon=False)
ax = plt.axes(projection='mollweide')
plt.title("Mollweide")
plt.pcolormesh(ra, dec, prob, cmap=cmapLigo)
ax.grid()
plt.savefig("mollweide-prob.png")
