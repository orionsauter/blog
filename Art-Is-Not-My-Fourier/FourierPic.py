import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
sys.path += ["linedraw/"]
import linedraw as ld

writergif = PillowWriter(fps=30)

def GetPath(img, pad=10):
    ld.draw_hatch = False
    lines = [np.vstack(pts) for pts in ld.sketch(img)]
    dim = np.max(np.vstack(lines), axis=0)
    path = np.vstack(lines)
    path = path[np.logical_and(path[:,0]>pad, path[:,0]<dim[0]-pad)]
    path = path[np.logical_and(path[:,1]>pad, path[:,1]<dim[1]-pad)]
    path[:,0] -= dim[0]//2
    path[:,1] -= dim[1]//2
    path[:,1] *= -1
    return path

def FourierCoeff(s, n):
    P = len(s)
    c = np.sum(s*np.exp(-2.0j*np.pi*n*np.arange(P)/P))/P
    return np.array([[n, c]])

def FourierTerms(cn, P):
    N = cn.shape[0]
    x = np.tile(np.arange(P).reshape(-1,1),(1,N))
    n = np.tile(cn[:,0].reshape(1,-1),(P,1))
    c = np.tile(cn[:,1].reshape(1,-1),(P,1))
    sn = c*np.exp(2.0j*np.pi*n*x/P)
    return sn

def Anim(t, sn, four):
    sc = np.insert(np.cumsum(sn[t,:]), 0, 0)
    four.set_data(sc.real, sc.imag)
    return four,

def AnimAll(t, sns, fours):
    for i in range(len(sns)):
        fours[i].set_data(sns[i][t,:].real, sns[i][t,:].imag)
    return fours

def PlotFourier(cns, P, Ns, name, nrows=1, ncols=1):
    fig, axs = plt.subplots(figsize=(4,4),
        nrows=nrows, ncols=ncols, sharex=True, sharey=True)
    axs = axs.flatten()
    fours = []
    scs = []
    for i in range(len(cns)):
        sn = FourierTerms(cns[i], P)
        sn = np.insert(sn, 0, 0, axis=1)
        s = np.sum(sn, axis=1)
        plt.sca(axs[i])
        axs[i].axis("off")
        axs[i].set_title(f"N = {Ns[i]}")
        line = plt.plot(s.real, s.imag, "-")
        sc = np.cumsum(sn, axis=1)
        scs += [sc]
        four, = plt.plot(sc[0,:].real, sc[0,:].imag, "-")
        fours += [four]
    animate = FuncAnimation(fig, AnimAll, fargs=(scs, fours),
        frames=range(P), interval=30, blit=True, repeat=True)
    # plt.show()
    animate.save(f"{name}.gif", writer=writergif)

if __name__ == "__main__":
    name = "austen"
    # path = GetPath("einstein.jpeg")
    path = GetPath("austen.png")
    s = path[:,0] + 1.0j*path[:,1]
    Ns = [3, 15, 30, 60]
    cns = [np.vstack([FourierCoeff(s, n) for n in range(-N,N)]) for N in Ns]
    P = len(s)
    PlotFourier(cns, P, Ns, name, nrows=2, ncols=2)
