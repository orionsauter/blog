import requests
import json
import logging
from collections import defaultdict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mc

url = "https://app.birdweather.com/graphql"
taxon = "https://www.ebi.ac.uk/ena/taxonomy/rest/scientific-name/"
tree = lambda: defaultdict(tree)

def RecurseTree(d, value, keys):
    if len(keys) == 1:
        d[keys[0]] = value
        return
    RecurseTree(d[keys[0]], value, keys[1:])

def PrintTree(d):
    if type(d) is not defaultdict:
        print(d)
        return
    for key in d.keys():
        print(key)
        PrintTree(d[key])

def GetData(station):
    body = """
    {
        station(id: [station]) {
            detections[detarg] {
                nodes {
                    timestamp
                    species {
                        scientificName
                        commonName
                    }
                    probability
                    certainty
                    confidence
                    score
                    coords {
                        lat
                        lon
                    }
                }
                pageInfo {
                    endCursor
                    hasNextPage
                }
            }
        }
    }"""
    body = body.replace("[station]",str(station))
    page = 1
    logging.info(f"Fetching page {page}.")
    response = requests.post(url=url, json={"query": body.replace("[detarg]","")})
    jres = json.loads(response.content)["data"]["station"]["detections"]
    dets = pd.DataFrame(jres["nodes"])
    page += 1
    while jres["pageInfo"]["hasNextPage"]:
        try:
            logging.info(f"Fetching page {page}.")
            response = requests.post(url=url, json={"query": body.replace("[detarg]",f'(after: "{jres["pageInfo"]["endCursor"]}")')})
            jres = json.loads(response.content)["data"]["station"]["detections"]
            dets = pd.concat([dets, pd.DataFrame(jres["nodes"])], ignore_index=True)
            page += 1
        except json.JSONDecodeError:
            print(response.content)
    dets["name"] = dets["species"].apply(lambda x: x["commonName"])
    dets["species"] = dets["species"].apply(lambda x: x["scientificName"])
    dets["lat"] = dets["coords"].apply(lambda x: x["lat"])
    dets["lon"] = dets["coords"].apply(lambda x: x["lon"])
    dets["station"] = station
    return dets

def GetTaxon(species, lineage):
    response = requests.get(url=taxon+species.replace(" ","%20"))
    jres = json.loads(response.content)
    RecurseTree(lineage, species, jres[0]['lineage'].split("; ")[:-1])
    return lineage

def PlotHours(name):
    dets = pd.read_hdf("records.h5",name)
    dets["timestamp"] = pd.to_datetime(dets["timestamp"])
    dets["hour"] = [ts.hour for ts in dets["timestamp"]]
    good = dets[dets["certainty"].isin(["almost_certain","very_likely"])]

    spgrp = good.groupby("name")
    ndet = 200
    counts = [grp.shape[0] for _, grp in spgrp if grp.shape[0] > ndet]
    hours = [grp["hour"] for _, grp in spgrp if grp.shape[0] > ndet]
    specs = [spec for spec, grp in spgrp if grp.shape[0] > ndet]
    hours = [x for _, x in sorted(zip(counts,hours))]
    specs = [x for _, x in sorted(zip(counts,specs))]
    fig, ax = plt.subplots(figsize=(4,8))
    plt.violinplot(hours, points=80, vert=False, widths=0.7,
                    showmeans=True, showextrema=True, showmedians=False)
    plt.xticks([0,6,12,18])
    plt.yticks(range(1,len(specs)+1), specs, rotation=45)
    plt.xlabel("hour")
    plt.grid(True,"major","x")
    plt.tight_layout()
    plt.savefig("hours.png")

def DailyCounts(dets):
    dets["timestamp"] = pd.to_datetime(dets["timestamp"])
    dets["date"] = dets["timestamp"].dt.date
    return dets.groupby("date").count()["name"]

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    
    stations = {"Nate": 1985, "Orion": 2707, "Steve": 2122}
    # Load & store data
    for name, station in stations.items():
        print(name)
        dets = GetData(station)
        dets.to_hdf("records.h5",name)

    # Plot folded detection data
    PlotHours("Orion")

    # Plot obs dates for carolina wren
    fig, ax = plt.subplots(figsize=(4,4))
    for name, station in stations.items():
        dets = pd.read_hdf("records.h5",name)
        dets = dets[dets["name"]=="Carolina Wren"]
        good = dets[dets["certainty"].isin(["almost_certain","very_likely"])]
        daily = DailyCounts(good)
        plt.plot(daily.index, daily, "-", label=name)
    plt.legend()
    plt.xlabel("date")
    plt.ylabel("counts")
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig("Wren.png")

    # Plot non-bird detections
    weird = ["Engine", "Siren", "Gun", "Gray Wolf", "Coyote", "Green Frog", "Dog", "Greenhouse Frog"]
    wdata = []
    for name, station in stations.items():
        print(name)
        dets = pd.read_hdf("records.h5",name)
        dets = dets[dets["name"].isin(weird)]
        wdata += [dets]
    wdata = pd.concat(wdata, ignore_index=True)
    fig, axs = plt.subplots(figsize=(4,8), nrows=len(weird))
    for i, name in enumerate(weird):
        print(name)
        sub = wdata[wdata["name"]==name].groupby("certainty").count().reindex(index = ["unlikely","uncertain","very_likely","almost_certain"])
        axs[i].barh(range(1,sub.shape[0]+1),sub["name"])
        axs[i].set_yticks(range(1,sub.shape[0]+2),sub.index.to_list()+[""])
        axs[i].set_ylabel(name)
    plt.tight_layout()
    plt.savefig("Nonbird.png")

    # Attempt at using taxonomy to categorize birds
    # lineage = tree()
    # lineage = GetTaxon("Cyanocitta cristata", lineage)
    # lineage = GetTaxon("Cardinalis cardinalis", lineage)
    # lineage = GetTaxon("Strix varia", lineage)
    # print(json.dumps(lineage))
    # PrintTree(lineage)
