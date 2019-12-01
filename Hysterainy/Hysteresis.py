import numpy as np
import matplotlib.pyplot as plt

n = 20 # Dimensions of grid
T = 3 # Temperature
spins = np.random.choice([-1,1], size=[n,n])
fig, ax = plt.subplots(1, 2, figsize=(6, 3))
tmax = n*n*80
tlist = np.arange(tmax)
field = np.zeros((tmax,)) # Internal field
ext = np.sin(6*np.pi*tlist/tmax) # External field

for t in tlist:
    # Pick a random spin
    i = np.random.randint(0,n)
    j = np.random.randint(0,n)

    # How well do they match neighbors?
    energy = 0
    if (i > 0):
        energy += -spins[i,j]*spins[i-1,j]
    if (i < n-1):
        energy += -spins[i,j]*spins[i+1,j]
    if (j > 0):
        energy += -spins[i,j]*spins[i,j-1]
    if (j < n-1):
        energy += -spins[i,j]*spins[i,j+1]
    # Flip in spite of neighbors due to field
    energy += -ext[t]*spins[i,j]

    # Swap state depending on energy
    if (np.random.random() < np.exp(2*energy/T)):
        spins[i,j] = -spins[i,j]

    # Get average internal field
    field[t] = np.mean(spins)
    
    # Grab a picture periodically
    if (t % (n*n) == 0):
        ax[0].matshow(spins, vmin=-1, vmax=1)
        ax[1].clear()
        ax[1].scatter(ext[0:(t+1)], field[0:(t+1)],
                      c=range(t+1), cmap='viridis',
                      vmin=0, vmax=tmax)
        ax[1].set_xlim(-1, 1)
        ax[1].set_ylim(-1, 1)
        plt.tight_layout()
        plt.savefig(str(t)+'.png',bbox_inches='tight')
