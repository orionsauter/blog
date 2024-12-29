import datetime
import requests
import getpass
import json
import logging
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# References
# https://github.com/geudrik/peloton-client-library/blob/master/API_DOCS.md
# https://app.swaggerhub.com/apis/DovOps/peloton-unofficial-api/0.3.0#/

class Peloton:
    def __init__(self, user, db_file="peloton.db"):
        self.user = user
        pwd = getpass.getpass("Password: ")
        s = requests.Session()
        s.post("https://api.onepeloton.com/auth/login", json={"username_or_email": user, "password": pwd})
        self.session = s
        self.info = self.get_info()
        self.id = self.info["id"]
        self.db = sqlite3.connect(db_file)

    def get_info(self):
        res = self.session.get(f"https://api.onepeloton.com/api/user/{self.user}")
        info = json.loads(res.text)
        if "id" not in info.keys():
            raise Exception("Login failed.")
        return info
    
    def get_workouts(self):
        self.workouts = []
        res = self.session.get(f"https://api.onepeloton.com/api/user/{self.id}/workouts")
        rides = json.loads(res.text)
        self.workouts += rides["data"]
        for page in range(1, rides["page_count"]):
            res = self.session.get(f"https://api.onepeloton.com/api/user/{self.id}/workouts?page={page}")
            rides = json.loads(res.text)
            self.workouts += rides["data"]

    def __del__(self):
        self.session.close()
        if hasattr(self,"db"):
            self.db.close()

    def load_workout(self, id):
        try:
            df = pd.read_sql(f"SELECT * FROM '{id}';", self.db)
            if "index" in df.columns:
                df = df.set_index("index")
            logging.info(f"Loaded workout {id} from cache.")
            return df
        except pd.errors.DatabaseError:
            pass
        res = self.session.get(f"https://api.onepeloton.com/api/workout/{id}/performance_graph?every_n=5")
        perf = json.loads(res.text)
        df = pd.DataFrame({p["display_name"]:p["values"] for p in perf["metrics"]}, index=perf["seconds_since_pedaling_start"])
        df = df.reset_index(names="Time")
        df["duration"] = perf["duration"]
        df["id"] = id
        df[["cadence_min","cadence_max","resistance_min","resistance_max"]] = np.nan
        for tgt in perf["target_metrics_performance_data"]["target_metrics"]:
            if tgt["segment_type"] != "cycling":
                logging.error("Non-cycling workouts are not yet supported.")
            idx = df.index[(df["Time"]>=tgt["offsets"]["start"]) & (df["Time"]<=tgt["offsets"]["end"])]
            for mdict in tgt["metrics"]:
                df.loc[idx,f"{mdict['name']}_min"] = mdict["lower"]
                df.loc[idx,f"{mdict['name']}_max"] = mdict["upper"]
        logging.info(f"Loaded workout {id} from server.")
        df.to_sql(id, self.db)
        return df

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    user = input("Username: ")
    pelo = Peloton(user)
    pelo.get_workouts()
    nworks = len(pelo.workouts)
    # with open("workout_ex.json","w") as fp:
    #     json.dump(pelo.workouts[0], fp, indent=4)
    
    works = []
    for i in range(nworks):
        df = pelo.load_workout(pelo.workouts[i]["id"])
        df["date"] = pelo.workouts[i]["created_at"]
        df["total_work"] = pelo.workouts[i]["total_work"]
        works += [df]
    df = pd.concat(works,axis=0,ignore_index=True)
    df.loc[df["Heart Rate"]==0,"Heart Rate"] = np.nan
    df["days"] = (df["date"] - df["date"].min())/(3600*24)

    daily = df.groupby("days").apply(lambda grp: grp.dropna().max())
    fig, ax = plt.subplots(figsize=(4,3))
    plt.scatter(daily["total_work"]/1e3,daily["Heart Rate"],c=daily.index)
    plt.xlabel("Total Work [kJ]")
    plt.ylabel("Max Heart Rate [bpm]")
    plt.colorbar(label="Days")
    plt.tight_layout()
    plt.savefig("MaxHeart.png",dpi=100)
    plt.close()

    fig, ax = plt.subplots(figsize=(4,3))
    plt.scatter(df["Cadence"],df["Output"],c=df["Resistance"])
    plt.xlabel("Cadence [rpm]")
    plt.ylabel("Output [W]")
    plt.colorbar(label="Resistance [%]")
    plt.tight_layout()
    plt.savefig("OutputCurve.png",dpi=100)
    plt.close()

    grp = df[["days","Cadence","Resistance","Output"]].groupby("days")
    mins = grp.quantile(0.25)
    meds = grp.median()
    maxs = grp.quantile(0.75)
    fig, ax = plt.subplots(figsize=(4,3))
    plt.errorbar(mins.index, meds["Output"], yerr=np.vstack([meds["Output"]-mins["Output"],maxs["Output"]-meds["Output"]]),
                 linestyle="none", marker=".")
    plt.xlabel("Day")
    plt.ylabel("Output [W]")
    plt.tight_layout()
    plt.savefig("Output.png",dpi=100)
    plt.close()
    
    cuts = np.argwhere((np.diff(df["cadence_max"])!=0) | (np.diff(df["cadence_min"])!=0) | 
                       (np.diff(df["resistance_max"])!=0) | (np.diff(df["resistance_min"])!=0))[:,0]
    cuts = np.append([0], np.append(cuts, [df.shape[0]]))
    df["section"] = np.nan
    for i in range(len(cuts)-1):
        df.loc[df.index[cuts[i]:cuts[i+1]],"section"] = i
    stable = df.groupby("section").agg({"Cadence": "std", "Resistance": "mean"})
    fig, ax = plt.subplots(figsize=(4,3))
    plt.plot(stable["Resistance"], stable["Cadence"], ".")
    plt.xlabel("Resistence [%]")
    plt.ylabel("Cadence Std. Dev. [rpm]")
    plt.tight_layout()
    plt.savefig("Stability.png",dpi=100)
    plt.close()

    # df = df.dropna()
    # for i, df in enumerate(works):
    #     date = datetime.datetime(1970, 1, 1)+datetime.timedelta(seconds=pelo.workouts[i]["created_at"])
    #     # plt.plot(df.index,df["Cadence"],"-",label=date.date())
    #     plt.plot(df["Resistance"],df["Cadence"],".",label=date.date())
    # plt.legend()
    # plt.scatter(df["Resistance"],df["Output"]/df["Cadence"]*60,c=df["Cadence"])
    # plt.scatter(df["Resistance"],df["Output"],c=df["Cadence"])
    # plt.scatter(df["Cadence"],df["Output"],c=df["Resistance"])

    # for cad, grp in df.groupby("Resistance"):
    #     plt.plot(grp["Cadence"],grp["Output"],"-")
    # plt.xlabel("Cadence [rpm]")
    # plt.ylabel("Output [W]")
    # plt.colorbar(label="Resistance [%]")
    # plt.xscale("log")
    # plt.yscale("log")
    # plt.scatter(df["Output"],df["Heart Rate"],c=df["date"])
    # for dt, grp in df.groupby("date"):
    #     coef, _, _, _ = np.linalg.lstsq(np.vstack([grp["Output"].to_numpy(), np.ones((grp.shape[0],))]).T,grp["Heart Rate"].to_numpy())
    #     plt.plot(grp["Output"], coef[0]*grp["Output"]+coef[1],"-")
    # plt.xlabel("Output [W]")
    # plt.ylabel("Heart Rate [bpm]")
    # plt.legend()
    # plt.colorbar(label="Datetime")
    # slopes = df.groupby("date").apply(lambda grp: np.linalg.lstsq(np.vstack([grp["Output"].to_numpy(), np.ones((grp.shape[0],))]).T,
    #                                                               grp["Heart Rate"].to_numpy())[0][0])
    # plt.plot(slopes.index,slopes,".")
    # plt.show()
