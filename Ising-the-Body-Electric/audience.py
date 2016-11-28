import numpy as np
import matplotlib.pyplot as plt

n = 20 # Dimensions of grid
qual = 0.5 # Quality of Performance
T = 2 # How willing to change sit/stand?
# Audience begins all sitting (-1), can change to standing (+1)
audi = -np.ones([n,n])

for t in range(n*n*20):
    # Pick a random person
    i = np.random.randint(0,n)
    j = np.random.randint(0,n)

    # How well do they match neighbors?
    enthus = 0
    if (i > 0):
        enthus += audi[i,j]*audi[i-1,j]
    if (i < n-1):
        enthus += audi[i,j]*audi[i+1,j]
    if (j > 0):
        enthus += audi[i,j]*audi[i,j-1]
    if (j < n-1):
        enthus += audi[i,j]*audi[i,j+1]
    # Stand in spite of neighbors for a good performance
    enthus += qual*audi[i,j]

    # Swap state depending on enthusiasm
    if (np.random.random() < np.exp(-2*enthus/T)):
        audi[i,j] = -audi[i,j]
    # Grab a picture periodically
    if (t % (n*n/2) == 0):
        plt.matshow(audi)
        plt.title("t = "+str(t))
        plt.savefig(str(t)+'.png',bbox_inches='tight')
