# Based on https://physics.weber.edu/schroeder/fluids/LatticeBoltzmannDemo.py.txt
# Copyright 2013, Daniel V. Schroeder (Weber State University) 2013

# Permission is hereby granted, free of charge, to any person obtaining a copy of 
# this software and associated data and documentation (the "Software"), to deal in 
# the Software without restriction, including without limitation the rights to 
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
# of the Software, and to permit persons to whom the Software is furnished to do 
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR 
# ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR 
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR 
# OTHER DEALINGS IN THE SOFTWARE.

# Except as contained in this notice, the name of the author shall not be used in 
# advertising or otherwise to promote the sale, use or other dealings in this 
# Software without prior written authorization.

# Credits:
# The "wind tunnel" entry/exit conditions are inspired by Graham Pullan's code
# (http://www.many-core.group.cam.ac.uk/projects/LBdemo.shtml).  Additional inspiration from 
# Thomas Pohl's applet (http://thomas-pohl.info/work/lba.html).  Other portions of code are based 
# on Wagner (http://www.ndsu.edu/physics/people/faculty/wagner/lattice_boltzmann_codes/) and
# Gonsalves (http://www.physics.buffalo.edu/phy411-506-2004/index.html; code adapted from Succi,
# http://global.oup.com/academic/product/the-lattice-boltzmann-equation-9780199679249).

# For related materials see http://physics.weber.edu/schroeder/fluids

import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib.animation
import scipy.signal as sg

four9ths = 4.0/9.0                    # abbreviations for lattice-Boltzmann weight factors
one9th   = 1.0/9.0
one36th  = 1.0/36.0

class BoltzFlute:
    def __init__(self, height=80, width=120, viscosity=0.05, u0=0.08):
        # Define constants:
        self.height = height                            # lattice dimensions
        self.width = width
        self.viscosity = viscosity                    # fluid viscosity
        self.omega = 1 / (3*viscosity + 0.5)        # "relaxation" parameter
        self.u0 = u0                            # initial and in-flow speed
        self.un = 1e-6                          # noise in speed
        self.performanceData = True                # set to True if performance data is desired

        # Initialize all the arrays to steady rightward flow:
        self.n0 = four9ths * (np.ones((self.height,self.width)) - 1.5*self.u0**2)    # particle densities along 9 directions
        self.nN = one9th * (np.ones((self.height,self.width)) - 1.5*self.u0**2)
        self.nS = one9th * (np.ones((self.height,self.width)) - 1.5*self.u0**2)
        self.nE = one9th * (np.ones((self.height,self.width)) + 3*self.u0 + 4.5*self.u0**2 - 1.5*self.u0**2)
        self.nW = one9th * (np.ones((self.height,self.width)) - 3*self.u0 + 4.5*self.u0**2 - 1.5*self.u0**2)
        self.nNE = one36th * (np.ones((self.height,self.width)) + 3*self.u0 + 4.5*self.u0**2 - 1.5*self.u0**2)
        self.nSE = one36th * (np.ones((self.height,self.width)) + 3*self.u0 + 4.5*self.u0**2 - 1.5*self.u0**2)
        self.nNW = one36th * (np.ones((self.height,self.width)) - 3*self.u0 + 4.5*self.u0**2 - 1.5*self.u0**2)
        self.nSW = one36th * (np.ones((self.height,self.width)) - 3*self.u0 + 4.5*self.u0**2 - 1.5*self.u0**2)
        self.rho = self.n0 + self.nN + self.nS + self.nE + self.nW + self.nNE + self.nSE + self.nNW + self.nSW        # macroscopic density
        self.ux = (self.nE + self.nNE + self.nSE - self.nW - self.nNW - self.nSW) / self.rho                # macroscopic x velocity
        self.uy = (self.nN + self.nNE + self.nNW - self.nS - self.nSE - self.nSW) / self.rho                # macroscopic y velocity

        # Initialize barriers:
        self.thick = 4
        self.barrier = np.zeros((self.height,self.width), bool)                    # True wherever there's a barrier
        self.barrier[(self.height//2)-self.thick:(self.height//2)+self.thick, self.height//2] = True
        self.barrier[(self.height//2)+self.thick, self.height//2+10:3*self.height//2] = True
        self.barrier[(self.height//2)-self.thick, self.height//2:3*self.height//2] = True
        self.barrierN = np.roll(self.barrier,  1, axis=0)                    # sites just north of barriers
        self.barrierS = np.roll(self.barrier, -1, axis=0)                    # sites just south of barriers
        self.barrierE = np.roll(self.barrier,  1, axis=1)                    # etc.
        self.barrierW = np.roll(self.barrier, -1, axis=1)
        self.barrierNE = np.roll(self.barrierN,  1, axis=1)
        self.barrierNW = np.roll(self.barrierN, -1, axis=1)
        self.barrierSE = np.roll(self.barrierS,  1, axis=1)
        self.barrierSW = np.roll(self.barrierS, -1, axis=1)

    # Move all particles by one step along their directions of motion (pbc):
    def stream(self):
        self.nN  = np.roll(self.nN,   1, axis=0)    # axis 0 is north-south; + direction is north
        self.nNE = np.roll(self.nNE,  1, axis=0)
        self.nNW = np.roll(self.nNW,  1, axis=0)
        self.nS  = np.roll(self.nS,  -1, axis=0)
        self.nSE = np.roll(self.nSE, -1, axis=0)
        self.nSW = np.roll(self.nSW, -1, axis=0)
        self.nE  = np.roll(self.nE,   1, axis=1)    # axis 1 is east-west; + direction is east
        self.nNE = np.roll(self.nNE,  1, axis=1)
        self.nSE = np.roll(self.nSE,  1, axis=1)
        self.nW  = np.roll(self.nW,  -1, axis=1)
        self.nNW = np.roll(self.nNW, -1, axis=1)
        self.nSW = np.roll(self.nSW, -1, axis=1)
        # Use tricky boolean arrays to handle barrier collisions (bounce-back):
        self.nN[self.barrierN] = self.nS[self.barrier]
        self.nS[self.barrierS] = self.nN[self.barrier]
        self.nE[self.barrierE] = self.nW[self.barrier]
        self.nW[self.barrierW] = self.nE[self.barrier]
        self.nNE[self.barrierNE] = self.nSW[self.barrier]
        self.nNW[self.barrierNW] = self.nSE[self.barrier]
        self.nSE[self.barrierSE] = self.nNW[self.barrier]
        self.nSW[self.barrierSW] = self.nNE[self.barrier]
            
    # Collide particles within each cell to redistribute velocities (could be optimized a little more):
    def collide(self):
        self.rho = self.n0 + self.nN + self.nS + self.nE + self.nW + self.nNE + self.nSE + self.nNW + self.nSW
        self.ux = (self.nE + self.nNE + self.nSE - self.nW - self.nNW - self.nSW) / self.rho
        self.uy = (self.nN + self.nNE + self.nNW - self.nS - self.nSE - self.nSW) / self.rho
        ux2 = self.ux * self.ux                # pre-compute terms used repeatedly...
        uy2 = self.uy * self.uy
        u2 = ux2 + uy2
        omu215 = 1 - 1.5*u2            # "one minus u2 times 1.5"
        uxuy = self.ux * self.uy
        self.n0 = (1-self.omega)*self.n0 + self.omega * four9ths * self.rho * omu215
        self.nN = (1-self.omega)*self.nN + self.omega * one9th * self.rho * (omu215 + 3*self.uy + 4.5*uy2)
        self.nS = (1-self.omega)*self.nS + self.omega * one9th * self.rho * (omu215 - 3*self.uy + 4.5*uy2)
        self.nE = (1-self.omega)*self.nE + self.omega * one9th * self.rho * (omu215 + 3*self.ux + 4.5*ux2)
        self.nW = (1-self.omega)*self.nW + self.omega * one9th * self.rho * (omu215 - 3*self.ux + 4.5*ux2)
        self.nNE = (1-self.omega)*self.nNE + self.omega * one36th * self.rho * (omu215 + 3*(self.ux+self.uy) + 4.5*(u2+2*uxuy))
        self.nNW = (1-self.omega)*self.nNW + self.omega * one36th * self.rho * (omu215 + 3*(-self.ux+self.uy) + 4.5*(u2-2*uxuy))
        self.nSE = (1-self.omega)*self.nSE + self.omega * one36th * self.rho * (omu215 + 3*(self.ux-self.uy) + 4.5*(u2-2*uxuy))
        self.nSW = (1-self.omega)*self.nSW + self.omega * one36th * self.rho * (omu215 + 3*(-self.ux-self.uy) + 4.5*(u2+2*uxuy))
        # Force steady rightward flow at ends (no need to set 0, N, and S components):
        u0 = self.u0 + np.random.normal(0, self.un)
        self.nE[:,0] = one9th * (1 + 3*u0 + 4.5*u0**2 - 1.5*u0**2)
        self.nW[:,0] = one9th * (1 - 3*u0 + 4.5*u0**2 - 1.5*u0**2)
        self.nNE[:,0] = one36th * (1 + 3*u0 + 4.5*u0**2 - 1.5*u0**2)
        self.nSE[:,0] = one36th * (1 + 3*u0 + 4.5*u0**2 - 1.5*u0**2)
        self.nNW[:,0] = one36th * (1 - 3*u0 + 4.5*u0**2 - 1.5*u0**2)
        self.nSW[:,0] = one36th * (1 - 3*u0 + 4.5*u0**2 - 1.5*u0**2)

# Compute curl of the macroscopic velocity field:
def curl(ux, uy):
    return np.roll(uy,-1,axis=1) - np.roll(uy,1,axis=1) - np.roll(ux,-1,axis=0) + np.roll(ux,1,axis=0)

def simulate(u0, save_anim=False):
    boltz = BoltzFlute(u0=u0)
    # Here comes the graphics and animation...
    # theFig = plt.figure(figsize=(8,3))
    theFig = plt.figure(figsize=(4,2))
    # fluidImage = plt.imshow(curl(boltz.ux, boltz.uy), origin='lower', norm=plt.Normalize(-.1,.1), 
    #                                     cmap=plt.get_cmap('jet'), interpolation='none')
    # fluidImage = plt.imshow((boltz.rho-np.mean(boltz.rho)), origin='lower', norm=plt.Normalize(-0.02,-0.01), 
    #                                     cmap=plt.get_cmap('jet'), interpolation='none')
    fluidImage = plt.imshow(np.log10(boltz.rho), origin='lower', norm=plt.Normalize(-0.005,0.005), 
                                        cmap=plt.get_cmap('jet'), interpolation='none')
            # See http://www.loria.fr/~rougier/teaching/matplotlib/#colormaps for other cmap options
    bImageArray = np.zeros((boltz.height, boltz.width, 4), np.uint8)    # an RGBA image
    bImageArray[boltz.barrier,3] = 255                                # set alpha=255 only at barrier sites
    barrierImage = plt.imshow(bImageArray, origin='lower', interpolation='none')

    # Function called for each successive animation frame:
    startTime = time.time()
    #frameList = open('frameList.txt','w')        # file containing list of images (to make movie)
    def nextFrame(arg, stepsize=20):                            # (arg is the frame number, which we don't need)
        nonlocal startTime
        if boltz.performanceData and (arg%100 == 0) and (arg > 0):
            endTime = time.time()
            print(f"{100/(endTime-startTime):1.1f} frames per second")
            startTime = endTime
        for step in range(stepsize):                    # adjust number of steps for smooth animation
            boltz.stream()
            boltz.collide()
        return boltz.ux, boltz.uy, boltz.rho

    def plotFrame(arg):
        ux, uy, rho = nextFrame(arg)
        fluidImage.set_array(np.log10(rho))
        return (fluidImage, barrierImage)        # return the figure elements to redraw

    if save_anim:
        animate = matplotlib.animation.FuncAnimation(theFig, plotFrame, frames=400, interval=1, blit=True)
        animate.save("Rho.gif", writer="ffmpeg", fps=100)
    plt.close()
    if not save_anim:
        frames = range(2000)
        vels = [nextFrame(i) for i in frames]
        # Coordinates of opening
        io, jo = (boltz.height//2)+boltz.thick, boltz.height//2+5
        mouth = np.array([[v[2][io,jo]] for v in vels])
        return mouth

if __name__ == "__main__":
    us = [0.005, 0.08, 0.22]
    simulate(0.08, save_anim=True)
    sim_data = [simulate(u0, save_anim=False) for u0 in us]

    fig, ax = plt.subplots(figsize=(4,3))
    plt.plot(range(75,sim_data[1].shape[0]),sim_data[1][75:,0],"-",label=us[1])
    plt.xlim((75,200))
    plt.xlabel("step")
    plt.ylabel("density")
    plt.legend(title="wind speed")
    plt.savefig("Time.png",bbox_inches="tight")

    fig, ax = plt.subplots(figsize=(4,3))
    for i, u0 in enumerate(us):
        freq, psd = sg.welch(sim_data[i][75:,0])
        plt.loglog(freq,np.sqrt(psd),"-",label=u0)
    plt.xlabel("freq.")
    plt.ylabel("density ASD")
    plt.legend(title="wind speed")
    plt.savefig("Spect.png",bbox_inches="tight")
