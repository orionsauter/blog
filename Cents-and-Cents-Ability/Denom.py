import numpy as np
import matplotlib.pyplot as plt

def partition(n, denom, prev=[]):
    if (n == 0):
        yield prev
        return
    if (n == 1):
        yield prev + [1]
        return
    for d in denom:
        if (d <= n):
            for p in partition(n - d, denom[denom <= d], prev + [d]):
                yield p

maxVal = 400
denomUS = np.array([100, 25, 10, 5, 1])
denomEU = np.array([200, 100, 50, 20, 10, 5, 2, 1])
statsUS = np.zeros((maxVal, 3))
statsEU = np.zeros((maxVal, 3))
try:
    for n in range(maxVal):
        print(n)
        combsUS = partition(n, denomUS)
        combsEU = partition(n, denomEU)
        lensUS = [len(coins) for coins in combsUS]
        lensEU = [len(coins) for coins in combsEU]
        statsUS[n,:] = [np.min(lensUS), np.median(lensUS), np.mean(lensUS)]
        statsEU[n,:] = [np.min(lensEU), np.median(lensEU), np.mean(lensEU)]
except:
    pass
np.savetxt("statsUS.txt", statsUS)
np.savetxt("statsEU.txt", statsEU)
##statsUS = np.loadtxt("statsUS.txt")
##statsEU = np.loadtxt("statsEU.txt")

fig, ax = plt.subplots(figsize=(5,3))
plt.tight_layout()
plt.plot(range(maxVal), statsUS[:,0], label="US")
plt.plot(range(maxVal), statsEU[:,0], label="EU")
plt.xlabel("total cents")
plt.ylabel("min # of coins/bills")
plt.legend()
plt.savefig("min.png", bbox_inches = "tight")

fig, ax = plt.subplots(figsize=(5,3))
plt.tight_layout()
plt.plot(range(maxVal), statsUS[:,1], label="US")
plt.plot(range(maxVal), statsEU[:,1], label="EU")
plt.xlabel("total cents")
plt.ylabel("median # of coins/bills")
plt.legend()
plt.savefig("median.png", bbox_inches = "tight")

fig, ax = plt.subplots(figsize=(5,3))
plt.tight_layout()
plt.plot(range(maxVal), statsUS[:,2], label="US")
plt.plot(range(maxVal), statsEU[:,2], label="EU")
plt.xlabel("total cents")
plt.ylabel("mean # of coins/bills")
plt.legend()
plt.savefig("mean.png", bbox_inches = "tight")
