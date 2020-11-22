import numpy as np
import matplotlib.pyplot as plt

def adjust(x):
    """ Perform 1 step of process """
    x_old = np.concatenate(([0], x, [1]))
    for i in range(len(x)):
        x[i] = (x_old[i+2] + x_old[i])/2
    return x

def iterate(x, T):
    """ Repeat adjust step T times """
    n = len(x)
    # Divisions should be at i/(n+1) for i=1..n
    exact = np.linspace(0, 1.0, n+2)[1:-1]
    err = np.zeros((T,))
    xlist = [x.tolist()]
    for i in range(T):
        x = adjust(x)
        xlist = xlist + [x.tolist()]
        err[i] = np.sqrt(np.mean((x-exact)**2))
    return err, xlist

T = 60
n = range(2, 9)
err = np.zeros((8, T))
xlists = []
plt.figure(figsize=(4,4))
for i in range(len(n)):
    x = np.round(np.linspace(0, 1, n[i]))
    err[i,:], xlist = iterate(x, T)
    xlists = xlists + [xlist]
    plt.semilogy(range(T), err[i,:], '.-', label=str(n[i]))
plt.legend()
plt.xlabel("iterations")
plt.ylabel("error")
plt.savefig("error.png", bbox_inches="tight")

for t in range(T):
    plt.figure(figsize=(4,4))
    for i in range(len(n)):
        plt.plot([0, 1], [n[i], n[i]], 'k')
        plt.plot(xlists[i][t], [n[i]]*n[i], '.r', markersize=20)
    plt.title("t = {:2.0f}".format(t))
    plt.ylabel("n divisions")
    plt.savefig("frames/divs-{}.png".format(t), bbox_inches="tight")
