import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import itertools as it
import scipy.signal as sig
from tqdm import trange

class Metronome:
    def __init__(self, r, m, k, zeta, pos, ang):
        self.r = r
        self.m = m
        self.k = k
        self.zeta = zeta
        self.g = 0.1
        self.t = 0
        self.I = m*r*r
        self.pos = pos
        self.ang = ang
        self.dang = 0.0
        self.Tint = 0.0

    def step(self, dt, Fext):
        self.t += dt
        self.ang += self.dang*dt
        self.Tint = -self.k*self.ang - self.zeta*self.dang - self.r*self.m*self.g*np.sin(self.ang)
        T = self.Tint - self.r*Fext*np.cos(self.ang)
        self.dang += T/self.I*dt

    def plot(self, x0):
        line, = plt.plot([x0+self.pos,x0+self.pos+self.r*np.sin(self.ang)],[0,self.r*np.cos(self.ang)], ".-")
        return line

class Table:
    def __init__(self, x0, v0, L, m):
        self.x = x0
        self.v = v0
        self.L = L
        self.m = m
        self.F = 0.0

    def step(self, dt, F):
        self.x += self.v*dt
        self.v += F/self.m
        self.F = F

    def plot(self):
        bar, = plt.plot([self.x,self.x+self.L],[0,0],"-")
        return bar

def step(ms, tab, dt):
    for m in ms:
        m.step(dt, tab.F)
        Fext = -m.Tint/m.r
    tab.step(dt, Fext)

def trace_peak(ts, fs):
    f, t, spec = sig.spectrogram(ts,fs,nperseg=3000)
    inds = np.int32(t*fs)
    amps = [np.max(np.abs(p)) for p in np.split(ts,inds[:-1])]
    peaks = f[np.argmax(spec,axis=0)]/amps
    return t, peaks

if __name__ == "__main__":
    dt = 0.02
    fs = 1/dt
    L = 10.0
    mB = 25.0
    nm = 5
    np.random.seed(42)
    ms = [Metronome(r=np.random.normal(1.0,0.4), m=np.random.normal(1.2,0.2),
                    k=2.0, zeta=2e-2, pos=i*L/(nm-1),
                    ang=np.random.normal(0.0,np.pi/8)) for i in range(nm)]
    tab = Table(0,0,L,mB)

    nsteps = 150000
    amp = np.zeros((nsteps,len(ms)))
    for i in range(nsteps):
        step(ms, tab, dt)
        for j, m in enumerate(ms):
            amp[i,j] = m.ang

    nsplit = 20
    sidx = np.array_split(np.arange(nsteps),nsplit)
    phase = np.zeros((nsteps,len(ms)))
    for i in range(nsplit):
        phase[sidx[i]] = np.arcsin(amp[sidx[i],:]/np.max(np.abs(amp[sidx[i],:]),axis=0))

    fig, ax = plt.subplots(figsize=(4,3))
    plt.plot(np.arange(nsteps)/1000,phase-np.mean(phase,axis=1,keepdims=True),"-")
    plt.xlabel("step/1000")
    plt.ylabel("phase error")
    plt.savefig("phase.png", bbox_inches="tight", dpi=100)

    # for j in range(nm):
    #     t, f = trace_peak(phase[:,j], fs)
    #     plt.plot(t, f, "-")
    # plt.show()

    np.random.seed(42)
    ms = [Metronome(r=np.random.normal(1.0,0.4), m=np.random.normal(1.2,0.2),
                    k=2.0, zeta=2e-2, pos=i*L/(nm-1),
                    ang=np.random.normal(0.0,np.pi/8)) for i in range(nm)]
    tab = Table(0,0,L,mB)
    fig, ax = plt.subplots(figsize=(4,2))
    plt.axis("equal")
    def animate(i):
        plt.cla()
        for _ in range(5):
            step(ms, tab, dt)
        bar = tab.plot()
        for m in ms:
            line = m.plot(tab.x)
        plt.xlim([-0.2*L,1.2*L])
        ylim = plt.ylim()
        plt.ylim([-(ylim[1]-ylim[0])/4,(ylim[1]-ylim[0])*3/4])
        cnt = ax.set_title(i)
        plt.tight_layout()
        return bar, line, cnt

    ani = FuncAnimation(fig, animate, range(1200), interval=10)
    ani.save("metronome.gif", writer="ffmpeg", fps=50, dpi=100)
