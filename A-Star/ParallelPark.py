import numpy as np
import matplotlib.pyplot as plt
from matplotlib import collections  as mc
from matplotlib import transforms  as mt
from matplotlib import animation  as ani
import heapq

class Car:
    def __init__(self, pos=np.array([0.0,0.0])):
        self.pos = pos
        self.ang = 0.0
        self.cm = np.array([0.0,0.0])
        # https://www.researchgate.net/figure/Samples-of-passenger-car-dimensions-a-Audi-A6-and-b-Audi-A4-Source_fig1_351440904
        self.width = 1847.0
        self.length = 4762.0
        self.wheel_pos = np.array([
            [[ 2820./2, 1572./2], [ 2820./2, -1572./2]],
            [[-2820./2, 1572./2], [-2820./2, -1572./2]]
        ])
        self.radii = np.array([
            [self.wheel_pos[i,j,:]-self.cm for j in range(2)] for i in range(2)
        ])
        self.wheel_ang = np.array([
            [0.0, 0.0], [0.0, 0.0]
        ])
        # https://tireconverter.com/215-70r16-in-inches
        self.wheel_rad = 708./2
        # https://hypertextbook.com/facts/2000/YanaZorina.shtml
        self.mass = 1500
        self.I = self.mass*(self.width+self.length)**2*1e-6/4
        self.history = [self]
        self.steps = []

    def copy(self):
        ccar = Car()
        ccar.pos = self.pos.copy()
        ccar.ang = self.ang
        ccar.cm = self.cm
        ccar.width = self.width
        ccar.length = self.length
        ccar.wheel_pos = self.wheel_pos
        ccar.radii = self.radii
        ccar.wheel_ang = self.wheel_ang.copy()
        ccar.wheel_rad = self.wheel_rad
        ccar.mass = self.mass
        ccar.I = self.I
        ccar.history = self.history[:]
        ccar.steps = self.steps[:]
        return ccar
    
    def box(self):
        return np.array([
            self.pos+[self.length/2,self.width/2],
            self.pos+[self.length/2,-self.width/2],
            self.pos+[-self.length/2,self.width/2],
            self.pos+[-self.length/2,-self.width/2]
        ])

    def steer(self, ang):
        self.wheel_ang = np.array([
            [ang, ang], [0.0, 0.0]
        ])

    def drive(self, d):
        angs = np.mean(self.wheel_ang, axis=1)
        pos = np.mean(self.wheel_pos, axis=1)
        L = np.sqrt((pos[0,0]-pos[1,0])**2 + (pos[0,1]-pos[1,1])**2)
        if angs[0] != 0:
            r = L/np.sin(angs[0])
        else:
            r = np.inf
        dpos = d*np.array([np.cos(self.ang),np.sin(self.ang)])
        dang = d/r
        self.pos += dpos
        self.ang += dang

    def plot(self, fig, color="blue"):
        ax = fig.axes[0]
        # plt.cla()
        wheel_lines = np.array([[(self.pos[0]+self.wheel_pos[i,j,0]-
            self.wheel_rad*np.cos(self.wheel_ang[i,j]),
            self.pos[1]+self.wheel_pos[i,j,1]-
            self.wheel_rad*np.sin(self.wheel_ang[i,j])),
            (self.pos[0]+self.wheel_pos[i,j,0]+
            self.wheel_rad*np.cos(self.wheel_ang[i,j]),
            self.pos[1]+self.wheel_pos[i,j,1]+
            self.wheel_rad*np.sin(self.wheel_ang[i,j]))]
            for i in range(2) for j in range(2)])
        xform = mt.Affine2D().rotate_around(*(self.pos+np.mean(self.wheel_pos, axis=1)[1,:]), self.ang)
        wheel_lines = np.apply_along_axis(xform.transform, 2, wheel_lines)
        lc = mc.LineCollection(wheel_lines, colors=color)
        ax.add_collection(lc)
        plt.axis("equal")
        ax.set(xlim=(-5000, 5000), ylim=(-10000, 10000))
        return lc

    def step(self, ang, d, fig=None):
        self.steer(ang)
        self.drive(d)
        self.history += [self.copy()]
        self.steps += [(ang,d)]
        if fig is not None:
            return self.plot(fig)

    def dist(self, other):
        xformA = mt.Affine2D().rotate_around(*(self.pos+np.mean(self.wheel_pos, axis=1)[1,:]), self.ang)
        cornsA = np.apply_along_axis(xformA.transform, 1, self.box())
        xformB = mt.Affine2D().rotate_around(*(other.pos+np.mean(other.wheel_pos, axis=1)[1,:]), other.ang)
        cornsB = np.apply_along_axis(xformB.transform, 1, other.box())
        d = np.sum((cornsA-cornsB)**2)
        return d
    
    def __eq__(self, other):
        return self.g+self.h == other.g+other.h
    
    def __lt__(self, other):
        return self.g+self.h < other.g+other.h
    
    def __gt__(self, other):
        return self.g+self.h > other.g+other.h
    
    def __le__(self, other):
        return self.g+self.h <= other.g+other.h
    
    def __ge__(self, other):
        return self.g+self.h >= other.g+other.h

class Astar:
    def __init__(self, init, tgt, upsample=1, tol=1, bounds=np.array([[-np.inf,-np.inf],[np.inf,np.inf]])):
        self.target = tgt
        self.openNodes = [self.calcDist(init)]
        self.closedNodes = []
        self.angs = [-np.pi/4, 0, np.pi/4]
        self.stepsize = 1500
        self.upsample = upsample
        self.tol = tol
        self.bounds = bounds
        self.done = False
        self.succ = False

    def calcDist(self, node):
        node.g = len(node.history)
        node.h = node.dist(self.target)
        return node
    
    def genNeighs(self, node):
        for ang in self.angs:
            for dir in [1,-1]:
                skip = False
                ncar = node.copy()
                for i in range(self.upsample):
                    ncar.step(ang, dir*self.stepsize/self.upsample)
                if np.any(ncar.pos<self.bounds[0,:]) or np.any(ncar.pos>self.bounds[1,:]):
                    continue
                self.calcDist(ncar)
                for i, other in enumerate(self.closedNodes):
                    if ncar.dist(other) < self.tol:
                        skip = True
                        break
                if skip:
                    continue
                for i, other in enumerate(self.openNodes):
                    if ncar.dist(other) < self.tol:
                        if ncar.g < other.g:
                            skip = True
                            self.openNodes[i] = ncar
                            heapq.heapify(self.openNodes)
                        break
                if skip:
                    continue
                heapq.heappush(self.openNodes, ncar)
        return

    def iter(self, fig=None):
        if len(self.openNodes) == 0:
            self.done = True
            return None
        curNode = heapq.heappop(self.openNodes)
        err = curNode.dist(self.target)
        if fig is not None:
            plt.cla()
            curNode.plot(fig)
            self.target.plot(fig, "red")
            plt.draw()
            plt.pause(0.001)
        if err < self.tol:
            self.done = True
            self.succ = True
        print(f"{err:.0f}, {len(self.openNodes)}, {len(self.closedNodes)}")
        self.genNeighs(curNode)
        self.closedNodes += [curNode]
        return curNode, err

if __name__ == "__main__":
    N = 500
    d = 50.0*np.ones((N,))
    ang = np.pi/4*np.ones((N,))
    car = Car()
    fig, ax = plt.subplots()
    def k_anim(i):
        plt.cla()
        plot = car.step(ang[i],d[i],fig)
        plt.xlim((-7500, 7500))
        plt.ylim((-8000, 16000))
        return plot,
    anim = ani.FuncAnimation(fig, k_anim, N, blit=True)
    anim.save("Circle.gif", writer = 'ffmpeg', fps = 20)

    upsample = 5
    start = Car()
    park = Car(start.pos+np.array([0.0,start.width]))
    err = start.dist(park)
    astar = Astar(start, park, upsample, 4e5, bounds=np.array([[-2*start.length,-2*start.width],[2*start.length,2*start.width]]))
    # fig, ax = plt.subplots()
    # plt.ion()
    # plt.show()
    ehist = [err]
    bhist = [start]
    while not astar.done:
        bestNode, err = astar.iter()
        ehist += [err]
        bhist += [bestNode]
    print(len(bestNode.history))
    fig, ax = plt.subplots(figsize=(4,4))
    def search_anim(i):
        plt.cla()
        cplot = bhist[i].plot(fig)
        tplot = astar.target.plot(fig, "red")
        ax.set_title(f"Step {i}: {ehist[i]:.0f}")
        return cplot, tplot,
    anim = ani.FuncAnimation(fig, search_anim, len(bhist), blit=True)
    anim.save("Search.gif", writer = 'ffmpeg', fps = 2)

    car = Car()
    fig, ax = plt.subplots(figsize=(4,4))
    def park_anim(i):
        plt.cla()
        j = i//upsample
        if j < len(bestNode.steps):
            ang, d = bestNode.steps[j]
            car.steer(ang)
            car.drive(d/upsample)
        cplot = car.plot(fig)
        tplot = astar.target.plot(fig, "red")
        return cplot, tplot,
    anim = ani.FuncAnimation(fig, park_anim, upsample*len(bestNode.steps)+5, blit=True)
    anim.save("Park.gif", writer = 'ffmpeg', fps = 15)

    fig, ax = plt.subplots(figsize=(4,4))
    plt.plot(range(len(ehist)), ehist, "-")
    plt.xlabel("step")
    plt.ylabel("error")
    plt.savefig("error.png", bbox_inches="tight")
