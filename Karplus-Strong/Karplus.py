import os
import numpy as np
import numpy.random as rdm
from collections import deque
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt

# Constants
fs = 16000.0 # Sampling freq (Hz)
dur = 3.0 # Duration (s)
ns = int(fs * dur) # N samples

def step(queue, filt):
    # Filter, sum, and move to end
    queue.append(np.sum(np.array(queue)*filt))
    return(queue.popleft())

def generate(name, init, filt, fs, ns):
    try:
        os.mkdir(name)
    except OSError:
        # Dir exists, ignore
        pass
    queue = deque(init)
    L = len(init)

    output = []
    for i in range(ns):
        if i % 100 == 0 and i < fs/2:
            plt.figure()
            plt.plot(range(L), queue)
            plt.ylim((-1,1))
            plt.savefig("{}/{}.png".format(name, i))
            plt.close()
        output.append(step(queue, filt))

    wav.write("{}/string.wav".format(name), int(fs), np.array(output))

f0 = 440.0 # A4
L = int(fs/f0) # Length of buffer
strike = int(L/3.0) # Length of initial strike
scale = 1.0 # Scaling factor to fade

# Original Karplus-Strong method
init = np.zeros((L,), dtype=np.float32)
init[:strike] = 2.0 * rdm.rand(strike) - 1.0
filt = np.zeros((L,), dtype=np.float32)
filt[0] = filt[1] = 1
filt = scale*filt/np.sum(filt)
generate("orig", init, filt, fs, ns)

# 5-bin filter
init = np.zeros((L,), dtype=np.float32)
init[:strike] = 2.0 * rdm.rand(strike) - 1.0
filt = np.zeros((L,), dtype=np.float32)
filt[0:5] = 1
filt = scale*filt/np.sum(filt)
generate("wide", init, filt, fs, ns)

# Sinusoid filter
init = np.zeros((L,), dtype=np.float32)
init[:strike] = 2.0 * rdm.rand(strike) - 1.0
filt = np.cos(np.arange(L, dtype=np.float32)*np.pi/L)
filt = scale*filt/np.sum(filt)
generate("sin", init, filt, fs, ns)
plt.figure()
plt.plot(range(L), filt, '-')
plt.savefig("cosfilt.png")
plt.close()

# Simple sine wave
puresin = 0.9*np.sin(2*np.pi/L*np.arange(0, ns))
wav.write("puresine.wav", int(fs), np.array(puresin, dtype=np.float32))
plt.figure()
plt.plot(range(3*L), puresin[:(3*L)], '-')
plt.savefig("puresin.png")
plt.close()
