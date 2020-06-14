# Based on Jupyter notebooks by Luis Ortega
from pykat import finesse        # import the whole pykat.finesse package
from pykat.commands import *     # import all packages in pykat.commands
import numpy as np               # for basic math/sci/array functions
import matplotlib as mpl
import matplotlib.pyplot as plt  # for plotting
import scipy                     # for analysing the plots
            
# use pykat's plotting style. change dpi to change plot sizes on your screen
pykat.init_pykat_plotting(dpi=90)

basecode = """
l l1 1 0 n1
m m1 0.85 0.15 0 n1 n2
s s1 3000 n2 n3
m m2 0.85 0.15 0 n3 n4
"""

#initialise Finesse with a new empty kat object
basekat = finesse.kat() 
#tell Finesse to talk less
basekat.verbose = False
#parse the Finesse code into PyKat
basekat.parse(basecode)

#create an independent copy of basekat
kat1 = basekat.deepcopy()
#write the code for the PDs and xaxis
PDcode = """
pd Transmitted n4
pd Circulating n2
xaxis m2 phi lin 0 360 60
"""
#parse the code for the new PDs and xaxis to the copied kat object 
kat1.parse(PDcode)
#run the simulation, and store the result in out1
out1 = kat1.run()

out1.plot(filename='Resonance.png',
          show=False,
          xlabel='Position of mirror M2 [deg]',
          ylabel='Power [W]', 
          title = 'Power vs. microscopic cavity length change')

fig, axes = plt.subplots(figsize=(4,2))
tuning = np.linspace(2*np.pi, 4*np.pi, 40)
fontprop = mpl.font_manager.FontProperties()
fontprop.set_size('small')
for i in range(len(tuning)):
    plt.clf()
    reflpt = tuning[i]
    phi = np.linspace(0, reflpt, 60)
    plt.plot(phi, np.sin(phi), '-b', label='Input')
    plt.plot(phi, -np.sin(phi-2*reflpt), '--r', label='Reflected')
    plt.plot(phi, np.sin(phi)-np.sin(phi-2*reflpt), '-g', label='Sum')
    plt.vlines(reflpt, -2, 2)
    plt.xlim((0, 4*np.pi+0.1))
    plt.ylim((-2, 2))
    plt.legend(loc='lower left', prop=fontprop)
    fig.savefig('frames/Reflection-{:02}.png'.format(i))
    fig.savefig('frames/Reflection-{:02}.png'.format(79-i))
