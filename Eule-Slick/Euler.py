import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.transform import Rotation as R
from scipy.integrate import solve_ivp
from scipy.linalg import inv

def BoxDemo(a, b, c):
    box = np.array([
        [-a, -b, -c],
        [a, -b, -c],
        [a, -b, c],
        [a, -b, -c],
        [a, b, -c],
        [a, b, c],
        [a, b, -c],
        [-a, b, -c],
        [-a, b, c],
        [-a, b, -c],
        [-a, -b, -c],
        [-a, -b, c],
        [a, -b, c],
        [a, b, c],
        [-a, b, c],
        [-a, -b, c]])

    dth = 0.05
    rx = R.from_rotvec(np.array([dth,0,0]))
    ry = R.from_rotvec(np.array([0,dth,0]))
    box1 = box.copy()
    box2 = box.copy()
    fig = plt.figure(figsize=(3,6))
    ax1 = fig.add_subplot(211, projection='3d')
    ax2 = fig.add_subplot(212, projection='3d')
    frame = 0
    for th in np.arange(0, np.pi/2, dth):
        ax1.clear()
        ax1.plot(xs=box1[:,0],ys=box1[:,1],zs=box1[:,2])
        ax1.set_xlim3d([-1,1])
        ax1.set_ylim3d([-1,1])
        ax1.set_zlim3d([-1,1])
        box1 = rx.apply(box1)
        ax2.clear()
        ax2.plot(xs=box2[:,0],ys=box2[:,1],zs=box2[:,2])
        ax2.set_xlim3d([-1,1])
        ax2.set_ylim3d([-1,1])
        ax2.set_zlim3d([-1,1])
        box2 = ry.apply(box2)
        plt.savefig("rigid/rigid-{}.png".format(frame))
        frame += 1
        
    for th in np.arange(0, np.pi/2, dth):
        ax1.clear()
        ax1.plot(xs=box1[:,0],ys=box1[:,1],zs=box1[:,2])
        ax1.set_xlim3d([-1,1])
        ax1.set_ylim3d([-1,1])
        ax1.set_zlim3d([-1,1])
        box1 = ry.apply(box1)
        ax2.clear()
        ax2.plot(xs=box2[:,0],ys=box2[:,1],zs=box2[:,2])
        ax2.set_xlim3d([-1,1])
        ax2.set_ylim3d([-1,1])
        ax2.set_zlim3d([-1,1])
        box2 = rx.apply(box2)
        plt.savefig("rigid/rigid-{}.png".format(frame))
        frame += 1

def Thandle(a, m, w0, e0, name):
    # Each branch of handle has mass m/3
    I_rod = m*a*a/9 # kg m^2
    I = np.array([
        [2*I_rod, 0, 0],
        [0, I_rod, 0],
        [0, 0, 3*I_rod]])
    def dwdt(t, we):
        # Split into ang. vel. and euler angles
        w = we[:3]
        e = we[3:]
        # From https://rotations.berkeley.edu/the-euler-angle-parameterization/
        ew = np.array([
            [np.sin(e[2])/np.sin(e[1]), np.cos(e[2])/np.sin(e[1]), 0],
            [np.cos(e[2]), -np.sin(e[2]), 0],
            [-np.sin(e[2])/np.tan(e[1]), -np.cos(e[2])/np.tan(e[1]), 1]])
        # Change in omega
        wdot = -np.dot(inv(I), np.cross(w, np.dot(I, w)))
        # Change in orientation
        edot = np.dot(ew, w)
        return np.hstack((wdot, edot))
    sol = solve_ivp(dwdt, [0, 20], np.hstack((w0, e0)),
                    t_eval=np.arange(0, 20, 0.1))

    thand = np.array([
        [0, 0, 0],
        [a, 0, 0],
        [0, 0, 0],
        [0, a, 0],
        [0, -a, 0]])
    fig = plt.figure(figsize=(3,3))
    ax = fig.add_subplot(111, projection='3d')
    for i in range(sol.y.shape[1]):
        e = sol.y[3:,i]
        r = R.from_euler("zxz", e)
        thand_rot = r.apply(thand)
        ax.clear()
        ax.plot(xs=thand_rot[:,0],ys=thand_rot[:,1],zs=thand_rot[:,2])
        ax.set_xlim3d([-a,a])
        ax.set_ylim3d([-a,a])
        ax.set_zlim3d([-a,a])
        plt.savefig("handle/{}-{}.png".format(name, i))

a = 1
b = 0.5
c = 0.25
BoxDemo(a,b,c)

a = 0.05 # m
m = 0.1 # kg
# Perfectly aligned velocity
w0 = [1, 0, 0]
e0 = [0, np.pi/2, 0]
Thandle(a, m, w0, e0, "perfect")
# 2% offset
off = 0.02
w0 = [np.sqrt(1-off**2), off, 0]
e0 = [0, np.pi/2, 0]
Thandle(a, m, w0, e0, "real")
