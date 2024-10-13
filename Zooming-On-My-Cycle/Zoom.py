import numpy as np
import matplotlib.pyplot as plt
import scipy.spatial as ssp
import networkx as nx

maxn = 25
rt2 = np.sqrt(2)

def EquivCycle(list1, list2):
    # Check if two cycles are the same
    # https://www.geeksforgeeks.org/python-check-whether-two-lists-circularly-identical/
    return (" ".join(map(str, list2)) in " ".join(map(str, list1 * 2))) or (" ".join(map(str, list2[::-1])) in " ".join(map(str, list1 * 2)))

def MakeLayout(n):
    # Arrange n nodes to fit in a window with the most space
    nc = np.ceil(np.sqrt(n))
    nr = n//nc
    pts = [[c,nr-r] for c in np.arange(nc) for r in np.arange(nr)]
    left = n - len(pts)
    pts += [[c+(nc-left)/2,0] for c in np.arange(left)]
    return np.array(pts)

def GetCycles(G):
    # Generate all paths from each node to its neighbors, and check if Hamiltonian
    cyc = []
    for start in G.nodes:
        for stop in G.adj[start].keys():
            for path in nx.all_simple_paths(G, source=start, target=stop):
                if len(path) == len(G.nodes) and not any([EquivCycle(path, expath) for expath in cyc]):
                    cyc += [path]
    return cyc

if __name__ == "__main__":
    for n in range(4,maxn+1):
        pts = MakeLayout(n)
        dist = ssp.distance_matrix(pts,pts)
        adj = np.argwhere((dist<rt2)&(dist>0))
        G = nx.Graph()
        G.add_edges_from(adj)
        cyc = GetCycles(G)
        print(f"{n}: {len(cyc)}")
        fig, ax = plt.subplots(figsize=(4,4))
        nx.draw(G, pos={idx:pts[idx,:] for idx in range(pts.shape[0])}, ax=ax)
        plt.title(f"Cycles: {len(cyc):.0f}")
        plt.savefig(f"Figures/n={n}.png")
        plt.close()
