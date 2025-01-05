import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class Branch:
    def __init__(self, L, parent=None):
        self.L = L
        self.parent = parent
        self.children = []
        self.weight = 1
        if parent is None:
            self.ang = 0
            self.base = np.array([0,0])
        else:
            self.ang = parent.ang
            self.base = self.parent.base + self.parent.L*np.array([np.sin(self.parent.ang),np.cos(self.parent.ang)])
        while parent is not None:
            parent.weight += 1
            parent = parent.parent

    def update(self):
        if not self.parent:
            return
        self.base = self.parent.base + self.parent.L*np.array([np.sin(self.parent.ang),np.cos(self.parent.ang)])

class Plant:
    def __init__(self, L, pgrow, psprt, stiff):
        self.L = L
        self.root = Branch(L)
        self.size = 1
        self.pgrow = pgrow
        self.psprt = psprt
        self.stiff = stiff

    def __iter__(self):
        self.queue = [self.root]
        return self
    
    def __next__(self):
        if len(self.queue) == 0:
            raise StopIteration
        brch = self.queue.pop()
        self.queue += brch.children
        return brch
    
    def step(self, sun):
        for brch in self:
            if ((len(brch.children) == 0) and (np.random.rand() < self.pgrow/self.size)) or \
               ((len(brch.children) > 0) and (np.random.rand() < self.psprt/self.size)):
                brch.children += [Branch(self.L, brch)]
                self.size += 1
                continue
            tilt = np.sin(sun-brch.ang)
            brch.ang += tilt/self.stiff/brch.weight**2
        for brch in self:
            brch.update()

    def plot(self, ax):
        for brch in self:
            ax.plot([brch.base[0],brch.base[0]+brch.L*np.sin(brch.ang)],
                    [brch.base[1],brch.base[1]+brch.L*np.cos(brch.ang)],"-g")
        return

if __name__ == "__main__":
    # plant = Plant(1.0, 1.0, 0.01, 15.0)
    # fig, ax = plt.subplots()
    # def animate(i):
    #     plt.cla()
    #     plant.step(np.pi/3*np.sin(2*np.pi*i/100))
    #     plant.plot(ax)
    #     plt.axis("equal")
    # ani = FuncAnimation(fig, animate, range(100), interval=500)
    # plt.show()

    psprt = [0.01, 0.02, 0.05]
    stiff = [10.0, 15.0, 20.0]
    plants = np.array([[Plant(1.0, 1.0, p, s) for s in stiff] for p in psprt])
    m, n = plants.shape
    fig, axs = plt.subplots(figsize=(8,8),nrows=m,ncols=n,sharey=True)
    def animate(i):
        for a in range(m):
            for b in range(n):
                axs[a,b].clear()
                for j in range(5):
                    plants[a,b].step(np.pi/3*np.sin(2*np.pi*(i*5+j)/250))
                plants[a,b].plot(axs[a,b])
                axs[a,b].axis("equal")
        for ax, col in zip(axs[0], stiff):
            ax.set_title(col)
        for ax, row in zip(axs[:,0], psprt):
            ax.set_ylabel(row, rotation=90, size='large')
        plt.tight_layout()
        ax.figure = fig
    ani = FuncAnimation(fig, animate, range(150), interval=200)
    ani.save("vary.gif", "ffmpeg", fps=10)
    