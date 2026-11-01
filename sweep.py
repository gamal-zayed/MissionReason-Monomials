"""Discretization sensitivity sweep: how much of the policy is captured by pure cells,
and how many minimal generators does each action need, as bins get finer?"""
import sys, time, json
import numpy as np
import region_analysis as ra
import mr_algebra as alg

CONFIGS = {
 "coarse":  {"battery_level":[0,15,30,40,101], "memory_usage":[0,50,101],
             "cloud_probability":[0,50,80,101], "ground_contact":[0,1,15,31]},
 "default": ra.DEFAULT_EDGES,
 "fine":    {"battery_level":[0,15,30,40,101],
             "memory_usage":list(range(0,101,10))+[101],
             "cloud_probability":[0,10,20,30,40,50,60,70,80,90,101],
             "ground_contact":[0,1,4,8,12,15,23,31]},
}
repo = sys.argv[1]
from pathlib import Path
policy = ra.load_policy(Path(repo))
rows = {}
for name, edges in CONFIGS.items():
    t=time.time()
    bins = ra.build_bins(edges)
    labels, ids, mixed = ra.label_cells(policy, bins)
    inv = {v:k for k,v in ids.items()}
    W = ra.weight_array(bins)
    mm = float(W[labels<0].sum())
    gens = {}
    for aid, act in inv.items():
        m = ra.minimal_patterns(labels==aid)
        gens[act] = int(m.sum())
    rows[name] = dict(cells=int(labels.size), mixed_mass=round(mm,4), generators=gens, secs=round(time.time()-t,1))
    print(name, rows[name], flush=True)
json.dump(rows, open("results/sweep.json","w"), indent=2)
