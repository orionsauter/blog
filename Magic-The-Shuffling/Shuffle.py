import numpy as np
import numpy.random as rdm
import matplotlib.pyplot as plt
from collections import deque

# Adapted from https://dandrake.livejournal.com/83095.html
def compositions(n, k):
    if n <= 0 or k <= 0:
        return
    elif k == 1:
        yield [n]
        return
    else:
        for i in range(1, n+1):
            for comp in compositions(n-i, k-1):
                yield [i] + comp

# Just want one element of above
def randcomposition(n, k, maxcut=None):
    if maxcut is None:
        maxcut = 2*n//k
    if n <= 0 or k <= 0:
        return
    elif k == 1:
        return([n])
    else:
        i = rdm.randint(1, min(n-k+1, maxcut))
        return([i] + randcomposition(n-i, k-1))

# Count number of runs in deck
def runs(deck):
    d = np.diff(deck)
    # Runs (e.g. 3, 4, 5) have diff 1
    r = np.sum(d == 1) + 1
    return(r)

# Measure distance from original postions
def dist(deck):
    order = np.argsort(deck)
    d = np.abs(order - range(len(deck)))
    return(d)

def riffle(deck):
    cut = rdm.binomial(len(deck), 0.5)
    shuf = np.zeros_like(deck)
    a = deque(deck[:cut])
    b = deque(deck[cut:])
    i = 0
    while len(a) > 0 and len(b) > 0:
        if rdm.random() < 0.5:
            shuf[i] = a.popleft()
        else:
            shuf[i] = b.popleft()
        i += 1
    if len(a) > 0:
        shuf[i:] = list(a)
    elif len(b) > 0:
        shuf[i:] = list(b)
    return(shuf)
    
def overhand(deck, nsplit=5):
    splits = randcomposition(len(deck), nsplit)
    idx = np.concatenate(([0], np.cumsum(splits), [len(deck)]))
    chunks = [deck[idx[i]:idx[i+1]] for i in range(nsplit)]
    shuf = [x for c in chunks[::-1] for x in c]
    return(shuf)

def run(shuffle, ncards, nshuf, nsample):
    if type(shuffle) is not list:
        shuffle = [shuffle]
    decks = np.repeat([np.arange(ncards)], nsample, axis=0)
    stats = np.zeros((nshuf, 8))

    for i in range(nshuf):
        decks = np.apply_along_axis(shuffle[i % len(shuffle)], 1, decks)
        runlist = np.apply_along_axis(runs, 1, decks)
        distlist = np.apply_along_axis(dist, 1, decks)
        stats[i, 0] = np.min(runlist)
        stats[i, 1] = np.mean(runlist)
        stats[i, 2] = np.max(runlist)
        stats[i, 3] = np.std(runlist)
        stats[i, 4] = np.min(distlist)
        stats[i, 5] = np.mean(distlist)
        stats[i, 6] = np.max(distlist)
        stats[i, 7] = np.std(distlist)
    return(stats)

nsample = 5000
ncards = 52
nshuf = 10

stats = run(overhand, ncards, nshuf, nsample)
plt.figure(1)
plt.errorbar(range(nshuf), stats[:, 1], stats[:, 3],
##             np.vstack((stats[:, 1]-stats[:, 0], stats[:, 2]-stats[:, 1])),
             capsize=3, label="overhand")
plt.figure(2)
plt.errorbar(range(nshuf), stats[:, 5], stats[:, 7],
             capsize=3, label="overhand")

stats = run(riffle, ncards, nshuf, nsample)
plt.figure(1)
plt.errorbar(range(nshuf), stats[:, 1], stats[:, 3],
             capsize=3, label="riffle")
plt.figure(2)
plt.errorbar(range(nshuf), stats[:, 5], stats[:, 7],
             capsize=3, label="riffle")

stats = run([riffle, overhand], ncards, nshuf, nsample)
plt.figure(1)
plt.errorbar(range(nshuf), stats[:, 1], stats[:, 3],
             capsize=3, label="alternate")
plt.figure(2)
plt.errorbar(range(nshuf), stats[:, 5], stats[:, 7],
             capsize=3, label="alternate")

plt.figure(1)
plt.xlabel("# of shuffles")
plt.ylabel("# of cards in runs")
plt.legend()
plt.savefig("Runs.png")

plt.figure(2)
plt.xlabel("# of shuffles")
plt.ylabel("distance from orig position")
plt.legend()
plt.savefig("Dist.png")
