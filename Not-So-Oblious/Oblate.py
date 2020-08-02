import numpy as np
from scipy.integrate import dblquad
import matplotlib.pyplot as plt

def norm3(x, y):
    return np.power(np.linalg.norm([x, y]), 3)

def force(x, y, a, b):
    # Integrate [x-x0, y-y0]/|x-x0, y-y0|^3
    fx = dblquad(lambda x0, y0: -(x-x0)/norm3(x-x0, y-y0),
                 -a, a, lambda x0: -b*np.sqrt(1 - x0*x0/(a*a)),
                 lambda x0: b*np.sqrt(1 - x0*x0/(a*a)))[0]
    fy = dblquad(lambda x0, y0: -(y-y0)/norm3(x-x0, y-y0),
                 -a, a, lambda x0: -b*np.sqrt(1 - x0*x0/(a*a)),
                 lambda x0: b*np.sqrt(1 - x0*x0/(a*a)))[0]
    return np.array([fx, fy])

def radialTest(n, A):
    e = np.linspace(0.05, 0.99, n)
    th = np.pi/4
    ellth = np.linspace(np.pi/n, 2*np.pi+np.pi/n, n)
    err = np.zeros((n,))
    fig, ax = plt.subplots(figsize=(4,4))
    for ei in range(n):
        a = np.power(A*A/(np.pi*np.pi*(1-e[ei]*e[ei])), 0.25)
        b = A/(a*np.pi)
        x = a*np.cos(th)
        y = b*np.sin(th)
        f = force(x, y, a, b)
        fmag = np.linalg.norm(f)
        pmag = np.linalg.norm([x, y])
        err[ei] = np.arccos(-(f[0]*x + f[1]*y)/(fmag*pmag))*180/np.pi
        if ei % 2 == 0:
            ellx = a*np.cos(ellth)
            elly = b*np.sin(ellth)
            plt.cla()
            plt.plot([ellx,ellx[::-1]], [elly,-elly[::-1]], '-b')
            plt.plot([0,x], [0,y], '--r')
            plt.quiver(x,y,f[0],f[1])
            plt.title('e = {:.2g}'.format(e[ei]))
            plt.xlabel('x')
            plt.ylabel('y')
            ax.axis('equal')
            plt.xlim((-1.6,1.6))
            plt.ylim((-1.6,1.6))
            plt.savefig('frames/radial-{}.png'.format(ei), bbox_inches='tight')
    plt.figure(figsize=(4,3))
    plt.plot(e, err, '-')
    plt.xlabel('eccentricity')
    plt.ylabel('angle from radius (deg)')
    plt.savefig('AngleErr.png', bbox_inches='tight')

if __name__ == '__main__':
    n = 40
    A = 1.0
    e = np.linspace(0.05, 0.99, n)
##    radialTest(n, A)
    th = np.linspace(np.pi/n, 2*np.pi+np.pi/n, n)
    fig, axs = plt.subplots(nrows=2, figsize=(4,8))
    for ei in range(n):
        print('{}/{}'.format(ei,n))
        a = np.power(A*A/(np.pi*np.pi*(1-e[ei]*e[ei])), 0.25)
        b = A/(a*np.pi)
        x = a*np.cos(th)
        y = b*np.sin(th)
        subi = range(0, n, 2)
        f = np.vstack([np.array([-x[i], -y[i]]) for i in subi])
##        subi = range(0, n, 5)
##        f = np.vstack([force(x[i], y[i], a, b) for i in subi])
        f = f/np.max(np.linalg.norm(f, axis=1))
        plt.sca(axs[0])
        plt.cla()
        plt.plot(x, y, '-b')
        plt.quiver(x[subi], y[subi], f[:,0], f[:,1])
        plt.title('e = {:.2g}'.format(e[ei]))
        plt.xlabel('x')
        plt.ylabel('y')
        axs[0].axis('equal')
        plt.xlim((-1.6,1.6))
        plt.ylim((-1.6,1.6))
        plt.sca(axs[1])
        plt.cla()
        surf = np.array([np.diff(x)[subi], np.diff(y)[subi]]).T
        dot = np.sum(f*surf, axis=1)
        plt.plot(th[subi], np.abs(dot), '-b')
        plt.xlabel('theta')
        plt.ylabel('horiz. gravity')
        plt.ylim((0,0.25))
        plt.savefig('frames/ellip-{}.png'.format(ei), bbox_inches='tight')
        if ei > 0 and ei < n-1:
            plt.savefig('frames/ellip-{}.png'.format(2*(n-1)-ei), bbox_inches='tight')
