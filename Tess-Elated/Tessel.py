import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pch
import scipy.interpolate as sci

# 4 colors to choose from (per the 4-color map theorem)
colors = ["red", "green", "blue", "orange"]

# Construct rotation matrix
def rot(deg):
    th = np.radians(deg)
    c, s = np.cos(th), np.sin(th)
    R = np.array([[c,-s],[s,c]])
    return R

# Upsample points with a cubic spline curve
def blobify(x, y, upsamp):
    N = x.shape[0]
    newin = np.linspace(0, 1, N*upsamp)
    newout = sci.CubicSpline(x,y)(newin)
    return newin, newout

class TesselTile:
    def __init__(self, N=4, xy=None, smooth=False, upsamp=10, colori=0):
        # N points per side
        self.smooth = smooth
        self.upsamp = upsamp
        if xy is None:
            botx = np.linspace(0, 1, N)
            boty = np.concatenate([[0], 0.5*np.random.random((N-2,)) - 0.25, [0]], axis=0)
            topx = np.linspace(0, 1, N)
            topy = 1 + np.concatenate([[0], 0.5*np.random.random((N-2,)) - 0.25, [0]], axis=0)
            if smooth:
                botx, boty = blobify(botx, boty, upsamp)
                topx, topy = blobify(topx, topy, upsamp)
            self.xy = np.hstack([
                np.vstack([botx,boty]),
                np.vstack([1+(1-topy),topx]),
                np.vstack([topx[::-1],topy[::-1]]),
                np.vstack([-boty[::-1],botx[::-1]])
            ]).T
        else:
            self.xy = xy
        self.N = self.xy.shape[0]//4
        self.colori = colori
        self.pch = pch.Polygon(self.xy, closed=True, color=colors[colori])

    def plot(self, ax):
        ax.add_patch(self.pch)

    def rotate(self, deg, corn, colori):
        # Create a new tile rotated by deg around corner corn
        xy0 = np.tile(self.xy[corn*self.N], (self.xy.shape[0],1))
        xyp = np.dot(self.xy-xy0, rot(deg).T) + xy0
        return TesselTile(xy=xyp, smooth=self.smooth, upsamp=self.upsamp, colori=colori)
    
    def tile(self, parity=True):
        # Make 3 new tiles to fill top right or bottom left corner
        tiles = [self]
        if parity:
            for i in range(3):
                tiles += [tiles[-1].rotate(90, 0, (1+i+self.colori)%4)]
        else:
            for i in range(3):
                tiles += [tiles[-1].rotate(90, 2, (1+i+self.colori)%4)]
        return tiles[1:]

if __name__ == "__main__":
    np.random.seed(42)
    for pts in [4, 6, 10]:
        tess = TesselTile(pts, smooth=False, colori=0)
        tiles = [tess] + tess.tile()
        new_tiles = []
        for tess in tiles:
            new_tiles += tess.tile(False)
        tiles += new_tiles
        new_tiles2 = []
        for tess in new_tiles:
            new_tiles2 += tess.tile(True)
        tiles += new_tiles2
        fig, ax = plt.subplots(figsize=(4,4))
        for tile in tiles:
            tile.plot(ax)
        plt.axis("equal")
        plt.savefig(f"hard_{pts}.png", dpi=100, bbox_inches="tight")
        plt.close()

        tess = TesselTile(pts, smooth=True, colori=0)
        tiles = [tess] + tess.tile()
        new_tiles = []
        for tess in tiles:
            new_tiles += tess.tile(False)
        tiles += new_tiles
        new_tiles2 = []
        for tess in new_tiles:
            new_tiles2 += tess.tile(True)
        tiles += new_tiles2
        fig, ax = plt.subplots(figsize=(4,4))
        for tile in tiles:
            tile.plot(ax)
        plt.axis("equal")
        plt.savefig(f"smooth_{pts}.png", dpi=100, bbox_inches="tight")
        plt.close()
