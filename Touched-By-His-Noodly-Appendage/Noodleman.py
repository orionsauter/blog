import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as mpa
import scipy.signal as sig

class Noodle:
    def __init__(self, dt, npts, m_wall):
        self.dt = dt
        self.npts = npts
        self.m_wall = m_wall
        self.ang = np.zeros((self.npts-1,))
        self.dang = np.random.normal(0,0.3,size=(self.npts-1,))
        self.P = np.zeros((self.npts,))
        self.v = 0.75
        self.g = 9.8
        self.damp = 0.45

    def step(self, P0):
        self.P[1:] = self.P[:-1]
        self.P[0] = P0
        self.ang += self.dang*self.dt
        T = np.zeros((self.npts-1))
        T += -self.P[1:]*np.sin(self.ang)
        T += -self.damp*self.m_wall*np.sign(self.dang)*self.dang**2
        cumang = np.append([np.pi/2],np.pi/2+np.cumsum(self.ang))
        grav = -self.g*np.cos(cumang[1:])*np.arange(1,self.npts)[::-1]
        self.dang += (T/self.m_wall + grav)*self.dt

    def get_pts(self):
        cumang = np.append([np.pi/2],np.pi/2+np.cumsum(self.ang))
        dx, dy = np.cos(cumang), np.sin(cumang)
        x = np.append([0],np.cumsum(dx))
        y = np.append([0],np.cumsum(dy))
        return x, y

if __name__ == "__main__":
    npts = 20
    steps = 1000
    prd = 35
    duty = 0.1
    Pmax = 35
    noo = Noodle(0.001,npts,1.0e-3)
    P = Pmax*(1+sig.square(np.linspace(0,2*np.pi*(steps-1)/prd,steps),duty))/2
    fig, ax = plt.subplots(figsize=(4,4))
    line, = ax.plot([], [], "-")
    scat = plt.scatter([],[],c=[],cmap=plt.cm.bwr,vmin=0,vmax=Pmax)
    plt.axis("equal")
    plt.xlim((-npts,npts))
    plt.ylim((0,2*npts))
    def animate(i):
        noo.step(P[i])
        x, y = noo.get_pts()
        line.set_data(x,y)
        scat.set_offsets(np.vstack([x[1:],y[1:]]).T)
        scat.set_array(noo.P)
        return line, scat
    
    anim = mpa.FuncAnimation(
        fig, animate, frames = steps, interval = 200, blit = True)
    anim.save("Noodle.gif", fps=10, dpi=100)
