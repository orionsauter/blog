import numpy as np
import matplotlib.pyplot as plt

nsamples = 10000
nang = 300
w = np.random.uniform(3, 10, nsamples)
l = np.random.uniform(w, 20, nsamples)
door = 0.9
r = np.zeros((nsamples,))

for i in range(nsamples):
    tanth = np.tan(np.linspace(0, np.pi, nang))
    m, n = np.meshgrid(range(20), range(20))
    valid = np.array([(np.abs(2*m*l[i]/tt - n*w[i]) < door/2)
                      for tt in tanth])
    m2 = np.tile(m, (nang,1,1))[valid]
    n2 = np.tile(n, (nang,1,1))[valid]
    r[i] = np.min(np.mean(np.sqrt(4*m2*m2*l[i]*l[i] + \
                   n2*n2*w[i]*w[i]), axis=0))

area = l * w
lin = l + w
fig, ax = plt.subplots(figsize=(4,3))
plt.scatter(area, r, c=l, s=1)
cbar = plt.colorbar()
cbar.set_label('length (m)')
plt.xlabel('area (m^2)')
plt.ylabel('distance (m)')
plt.savefig('area-r.png', bbox_inches='tight')

fig, ax = plt.subplots(figsize=(4,3))
bins = np.linspace(np.min(area), np.max(area), 20)
cents = bins[:-1] + np.diff(bins)
dig = np.digitize(area, bins)
means = [r[dig == i].mean() for i in range(1, 20)]
plt.plot(cents, means, '-')
plt.xlabel('area (m^2)')
plt.ylabel('mean distance (m)')
plt.savefig('area-meanr.png', bbox_inches='tight')

fig, ax = plt.subplots(figsize=(4,3))
bins = np.linspace(np.min(lin), np.max(lin), 20)
cents = bins[:-1] + np.diff(bins)
dig = np.digitize(lin, bins)
means = [r[dig == i].mean() for i in range(1, 20)]
plt.plot(cents, means, '-')
plt.xlabel('linear size (m)')
plt.ylabel('mean distance (m)')
plt.savefig('linear-meanr.png', bbox_inches='tight')

