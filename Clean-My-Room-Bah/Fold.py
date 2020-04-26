import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from scipy.spatial.transform import Rotation as R

# Dimensions (m)
door = 0.9
l = 5.0
w = 3.0
n = 5
nsteps = 20

def room(enter, direc):
    x_corners = [enter[0] - w/2,
                 enter[0] + w/2,
                 enter[0] + w/2,
                 enter[0] - w/2]
    y_corners = [enter[1],
                 enter[1],
                 enter[1] + direc*l,
                 enter[1] + direc*l]
    x_frame = [enter[0] - door/2,
               enter[0] + door/2]
    y_frame = [enter[1], enter[1]]
    segs = [np.array([[x_corners[i] + j*(x_corners[(i+1)%4]-x_corners[i])/n,
                       y_corners[i] + j*(y_corners[(i+1)%4]-y_corners[i])/n]
                      for j in range(n+1)])
            for i in range(4)]
    segs += [np.array([[enter[0]-door/2+j*door/n, enter[1]]
                       for j in range(n+1)])]
    return segs

def wallCollect(segs):
    return LineCollection(segs,
        colors=((0,0,0,1), (0,0,0,1), (0,0,0,1),
                (0,0,0,1), (1,0,0,1), (0,0,1,1)))

def fold(axis, wall, shift=[0,0,0]):
    if wall.shape[1] < 3:
        wall = np.hstack((wall, np.zeros((wall.shape[0],1))))
    else:
        wall[:,2] = 0
    r = R.from_rotvec(axis)
    rwall = np.dot(r.as_matrix(),
                   (wall-np.tile(shift,(wall.shape[0],1))).T).T +\
                   np.tile(shift,(wall.shape[0],1))
    return rwall[:,0:2]

def clearTraces(ax):
    for artist in ax.lines + ax.collections:
        artist.remove()

rooms = [room([-w,-l],1),
         room([-w,l],-1),
         room([0,l],-1),
         room([0,-l],1),
         room([w,l],-1),
         room([w,-l],1)]
slope = l/w
path = np.array([[x, slope*(x+w)-l] for x in np.linspace(-w, w, n)])
for i in range(len(rooms)):
    r = np.array(rooms[i])
    xrange = [np.min(r[:,:,0]), np.max(r[:,:,0])]
    yrange = [np.min(r[:,:,1]), np.max(r[:,:,1])]
    inx = np.logical_and(path[:,0] >= xrange[0],
                         path[:,0] <= xrange[1])
    iny = np.logical_and(path[:,1] >= yrange[0],
                         path[:,1] <= yrange[1])
    rooms[i] += [path[np.logical_and(inx,iny),:]]

fig, ax = plt.subplots(figsize=(4,3))
plt.xlim((-2*w, 2*w))
plt.ylim((-l-0.1, l+0.1))
plt.axis('off')
for th in np.linspace(0, np.pi, nsteps):
    clearTraces(ax)
    foldrooms = []
    for r in rooms:
        rwalls = [fold([th,0,0], wall)
                  if any(wall[:,1] > 0.1) else wall for wall in r]
        foldrooms += [rwalls]
        ax.add_collection(wallCollect(rwalls))
    plt.savefig('frames/1-{:.3}-fold.png'.format(th), bbox_inches='tight')
for th in np.linspace(0, np.pi, nsteps):
    clearTraces(ax)
    foldrooms2 = []
    for r in foldrooms:
        rwalls = [fold([0,th,0], wall, [w/2,0,0])
                  if any(wall[:,0] > w/2) else wall for wall in r]
        foldrooms2 += [rwalls]
        ax.add_collection(wallCollect(rwalls))
    plt.savefig('frames/2-{:.3}-fold.png'.format(th), bbox_inches='tight')
for th in np.linspace(0, np.pi, nsteps):
    clearTraces(ax)
    for r in foldrooms2:
        rwalls = [fold([0,th,0], wall, [-w/2,0,0])
                  if any(wall[:,0] < -w/2) else wall for wall in r]
        ax.add_collection(wallCollect(rwalls))
    plt.savefig('frames/3-{:.3}-fold.png'.format(th), bbox_inches='tight')
