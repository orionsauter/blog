import copy
import uuid
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as ani
import networkx as nx
from tqdm import tqdm

class Person:
    def __init__(self, pinfect=0, pvacc=0, sucep=0.5, T_sick=22, T_contag=[10,18]):
        self.id = uuid.uuid1()
        self.infect = bool(np.random.rand() < pinfect)
        self.vacc = bool(np.random.rand() < pvacc)
        if self.vacc:
            self.sucep = 0.005
        else:
            self.sucep = sucep
        self.T_sick = T_sick
        self.T_contag = T_contag
        self.course = 0
        self.history = [[self.infect, self.vacc]]

    def step(self):
        if self.infect:
            self.course += 1
            if self.course > self.T_sick:
                self.infect = False
                self.course = 0
                self.vacc = True
                self.sucep = 0.005
        self.history += [[self.infect, self.vacc]]

class Population:
    def __init__(self, n=100, k=5, pwire=0.05, pinfect=0.1, pvacc=0.5, sucep=0.5):
        self.n = n
        self.sucep = sucep
        # https://www.cdc.gov/measles/hcp/communication-resources/clinical-diagnosis-fact-sheet.html
        T_sick = 22
        T_contag = [10,18]

        self.G = nx.watts_strogatz_graph(n, k, pwire)
        nx.relabel_nodes(self.G, {i: Person(pinfect, pvacc, sucep, T_sick, T_contag) for i in range(n)}, copy=False)

    def step(self):
        for nd in nx.dfs_preorder_nodes(self.G):
            nd.step()
        newG = copy.deepcopy(self.G)
        for nnode in nx.dfs_preorder_nodes(newG):
            onode = [nd for nd in self.G if nd.id==nnode.id][0]
            if onode.infect and (onode.course >= onode.T_contag[0]) and (onode.course <= onode.T_contag[1]):
                for neig in newG.neighbors(nnode):
                    neig.infect = neig.infect | (np.random.rand() < neig.sucep)
        self.G = newG

    def history(self):
        return np.array([nd.history for nd in nx.dfs_preorder_nodes(self.G)])

    def set_state(self, state):
        for i, nd in enumerate(nx.dfs_preorder_nodes(self.G)):
            nd.infect = state[i]
    
    def plot(self, ax=None):
        colors = []
        for nd in self.G:
            if nd.infect:
                colors += ["red"]
            elif nd.vacc:
                colors += ["green"]
            else:
                colors += ["blue"]
        nx.draw(self.G, pos=nx.kamada_kawai_layout(self.G), node_size=50, node_color=colors, ax=ax)

def stats(pop):
    grid = pop.history()[:,:,0]
    nsick = np.mean(np.any(grid,axis=1))
    fsick = np.mean(grid)
    cure = np.argwhere(np.logical_not(np.any(grid,axis=0)))
    if len(cure) > 0:
        tsick = np.min(cure)
    else:
        tsick = grid.shape[1]
    return pd.Series([nsick, fsick, tsick], index=["nsick","fsick","tsick"])

def course(pop, name):
    hist = pop.history()
    grid = hist[:,:,0]
    immu = hist[:,:,1]
    cure = np.argwhere(np.logical_not(np.any(grid,axis=0)))
    if len(cure) > 0:
        tsick = np.min(cure) + 5
    else:
        tsick = grid.shape[1]
    fig, ax = plt.subplots(figsize=(4,4))
    def animate(j):
        for i, nd in enumerate(nx.dfs_preorder_nodes(pop.G)):
            nd.infect = grid[i,j]
            nd.vacc = immu[i,j]
        ax.clear()
        pop.plot(ax)
        ax.set_title(j)
        return
    anim = ani.FuncAnimation(fig, animate, frames=tsick, blit=False, interval=200)
    anim.save(name, writer="ffmpeg", fps=5, dpi=100)

if __name__ == "__main__":
    np.random.seed(42)
    nstep = 300
    nrun = 10
    npop = 200

    run, ks, ws, vacs = np.meshgrid(np.arange(nrun), [5, 10, 30], [0.01, 0.05, 0.1], [0.0, 0.2, 0.5, 0.8])
    df = pd.DataFrame({"run": run.flatten(), "k": ks.flatten(), "pwire": ws.flatten(), "pvacc": vacs.flatten()})
    hists = []
    for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
        pop = Population(n=npop, k=int(row["k"]), pwire=row["pwire"], pvacc=row["pvacc"])
        for i in range(nstep-1):
            pop.step()
        hists += [pop]
    df["history"] = hists
    df.to_hdf("data.h5", "samples")

    df = pd.read_hdf("data.h5", "samples")
    df[["nsick","fsick","tsick"]] = df.apply(lambda row: stats(row["history"]), axis=1)
    df = df[df["tsick"]>0]
    avg = df[["k","pwire","pvacc","nsick","fsick","tsick"]].groupby(["k","pwire","pvacc"]).mean().reset_index()
    fig, ax = plt.subplots(figsize=(4,3))
    scatter = plt.scatter(avg["k"],avg["fsick"],c=avg["pwire"],s=avg["pvacc"]*100)
    legend = ax.legend(*scatter.legend_elements(prop="sizes"),
        loc="upper left", title=r"% vacc.")
    plt.xscale("log")
    plt.colorbar(label=r"$p_\mathrm{wire}$")
    plt.xlabel("community size")
    plt.ylabel("frac. sick days/person")
    plt.tight_layout()
    plt.savefig("frac.png")

    fig, ax = plt.subplots(figsize=(4,3))
    scatter = plt.scatter(avg["k"],avg["nsick"],c=avg["pwire"],s=avg["pvacc"]*100)
    legend = ax.legend(*scatter.legend_elements(prop="sizes"),
        loc="lower right", title=r"% vacc.")
    plt.xscale("log")
    plt.colorbar(label=r"$p_\mathrm{wire}$")
    plt.xlabel("community size")
    plt.ylabel("frac. people infected")
    plt.tight_layout()
    plt.savefig("nsick.png")

    fig, ax = plt.subplots(figsize=(4,3))
    scatter = plt.scatter(avg["k"],avg["tsick"],c=avg["pwire"],s=avg["pvacc"]*100)
    legend = ax.legend(*scatter.legend_elements(prop="sizes"),
        loc="lower right", title=r"% vacc.")
    plt.xscale("log")
    plt.colorbar(label=r"$p_\mathrm{wire}$")
    plt.xlabel("community size")
    plt.ylabel("days to erad.")
    plt.tight_layout()
    plt.savefig("tsick.png")


    maxdur = df[df["tsick"]==300]
    minvac = df[df["pvacc"]==df["pvacc"].min()]
    print(minvac)
    # course(maxdur["history"].iloc[4], "maxdur.gif")
    course(minvac["history"].iloc[np.argmax(minvac["fsick"])], "maxsick.gif")
    course(minvac["history"].iloc[np.argmin(minvac["fsick"])], "minsick.gif")
