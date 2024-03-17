import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

class DipoleGrid:
    def __init__(self, m, n, init=None):
        if init is None:
            init = np.random.random((m,n))*2*np.pi
        self.m = m
        self.n = n
        self.grid = init
        self.x, self.y = np.meshgrid(range(m),range(n),indexing="xy")
        self.b_field()

    def b_field(self):
        A = np.zeros((self.m,self.n))
        for i in range(self.m):
            for j in range(self.n):
                r = np.stack([self.x[i,j]-self.x,self.y[i,j]-self.y],axis=-1)
                rmag = np.sqrt(r[:,:,0]**2+r[:,:,1]**2)
                rmag[rmag==0] = 1.0
                # th = np.arctan2(self.y[i,j]-self.y,self.x[i,j]-self.x)
                A[i,j] = np.sum((np.cos(self.grid)*r[:,:,1] - np.sin(self.grid)*r[:,:,0])/rmag**3)
        dy, dx = np.gradient(A)
        self.B = np.stack([-dx, dy],axis=-1)
        self.Bmag = np.sqrt(dx*dx+dy*dy)

    def torque(self, Bext):
        B = self.B + np.tile(Bext,(self.m,self.n,1))
        T = np.cos(self.grid)*B[:,:,1] - np.sin(self.grid)*B[:,:,0]
        return T

    def energy(self, test_grid, Bext):
        B = self.B + np.tile(Bext,(self.m,self.n,1))
        E = np.cos(test_grid)*B[:,:,0] + np.sin(test_grid)*B[:,:,1]
        return E
    
    def step(self, Bext, dt, noise):
        # new_grid = self.grid.copy()
        # mask = np.random.choice([0, 1], size=new_grid.shape, p=((1 - rfrac), rfrac)).astype(bool)
        # new_grid[mask] = np.random.random((np.sum(mask)))*2*np.pi
        # old_E = self.energy(self.grid, Bext)
        # new_E = self.energy(new_grid, Bext)
        # self.grid = np.where(np.exp(-(new_E-old_E)/temp)<np.random.random(new_grid.shape), new_E, old_E)
        self.grid += self.torque(Bext)*dt + (2*np.random.random((self.m,self.n))-1)*noise
        self.b_field()

    def plot_arrows(self, Bext):
        B = self.B + np.tile(Bext,(self.m,self.n,1))
        u, v = np.cos(self.grid), np.sin(self.grid)
        # plt.contourf(self.x+0.5, self.y+0.5, self.Bmag)
        # plt.pcolormesh(self.x+0.5, self.y+0.5, self.Bmag)
        # plt.streamplot(self.x+0.5, self.y+0.5, self.B[:,:,0], self.B[:,:,1], density=[0.5, 1])
        Bavg = np.tile(np.mean(B, axis=(0,1)),(self.m,self.n,1))
        AvgAr = plt.quiver(self.x+0.5, self.y+0.5, Bavg[:,:,0], Bavg[:,:,1], color="red")
        IndAr = plt.quiver(self.x+0.5, self.y+0.5, u, v)
        if Bext[0] > 0:
            plt.hlines([0,self.m],0,self.n,colors=["blue","red"],alpha=np.abs(Bext[0]))
        else:
            plt.hlines([self.m,0],0,self.n,colors=["blue","red"],alpha=np.abs(Bext[0]))
        if Bext[1] > 0:
            plt.vlines([0,self.n],0,self.m,colors=["blue","red"],alpha=np.abs(Bext[1]))
        else:
            plt.vlines([self.n,0],0,self.n,colors=["blue","red"],alpha=np.abs(Bext[1]))
        plt.xticks(range(self.n+1))
        plt.yticks(range(self.m+1))
        plt.grid("major","both")
        return AvgAr, IndAr,

if __name__ == "__main__":
    np.random.seed(42)
    n = 10
    steps = 200
    Bext = 2*np.exp(-np.linspace(0,2,steps)).reshape(-1,1)*np.vstack([np.cos(np.linspace(0,6*np.pi,steps)),np.sin(np.linspace(0,6*np.pi,steps))]).T
    # Bext = np.linspace(0,2,steps).reshape(-1,1)[::-1]*np.vstack([np.cos(np.linspace(0,6*np.pi,steps)),np.sin(np.linspace(0,6*np.pi,steps))]).T
    Bmag = np.ones((steps,))*np.nan
    norm = np.zeros((n,n,2))
    norm[0,:,1] = -1
    norm[-1,:,1] = 1
    norm[:,0,0] = -1
    norm[:,-1,0] = 1
    grid = DipoleGrid(n, n, np.random.random((n,n))*np.pi/4-np.pi/8)
    # Bstart = np.mean(np.abs(grid.B*norm))
    Bstart = np.sqrt(np.sum(np.mean(grid.B,axis=(0,1))**2))
    fig = plt.figure(figsize=(4,6))
    spec = fig.add_gridspec(nrows=2, height_ratios=[2,1])
    axs = [fig.add_subplot(spec[0]),fig.add_subplot(spec[1])]
    def animate(i):
        grid.step(Bext[i,:], 0.1, np.pi/24)
        plt.sca(axs[1])
        plt.cla()
        # Bmag[i] = np.mean(np.abs(grid.B*norm))
        Bmag[i] = np.sqrt(np.sum(np.mean(grid.B,axis=(0,1))**2))
        line, = axs[1].plot(range(steps), Bmag)
        start = plt.hlines(Bstart,0,steps,colors="red",linestyles="dashed")
        axs[1].set_xlim((0,steps))
        plt.sca(axs[0])
        plt.cla()
        axs[0].set_title(i)
        return grid.plot_arrows(Bext[i,:]/np.max(Bext)), line, start
    for i in range(steps):
        animate(i)
        plt.savefig(f"frames/{i:03d}.png",bbox_inches="tight")
    # ani = FuncAnimation(fig, animate, range(steps), blit=False)
    # plt.show()
    # ani.save("Gauss.gif", writer="ffmpeg", fps=3)
