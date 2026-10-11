#!/usr/bin/env python3
"""Gate 6 beta scan: analytic scalar BFB and perturbative unitarity only.

This is NOT a phenomenological allowed region; experimental, CB/global
vacuum and full Zee lepton-sector constraints have NOT been applied.
"""
import argparse
import csv
from pathlib import Path
import numpy as np
from gate6_benchmark import benchmark

def scan(beta_min=1.385,beta_max=1.399,points=141,mH1=300,mH2=700):
    for beta in np.linspace(beta_min,beta_max,points):
        r=benchmark(float(beta),mH1,mH2)
        yield {
           "beta_rad":float(beta),
           "tanbeta":r["tanbeta"],
           "lambda1":r["quartics"]["lambda1"],
           "BFB_proved":int(r["sufficient_global_quartic_BFB"]),
           "max_abs_unitarity_eigenvalue":r["max_abs_unitarity_eigenvalue"],
           "unitarity_pass":int(r["tree_unitarity_pass"]),
           "SCALAR_SCREEN_pass":int(
               r["sufficient_global_quartic_BFB"] and r["tree_unitarity_pass"]),
        }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--beta-min",type=float,default=1.385)
    p.add_argument("--beta-max",type=float,default=1.399)
    p.add_argument("--points",type=int,default=141)
    p.add_argument("--output",type=Path,default=Path("work/gate6_beta_scan.csv"))
    args=p.parse_args()
    rows=list(scan(args.beta_min,args.beta_max,args.points))
    passes=[r for r in rows if r["SCALAR_SCREEN_pass"]]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print("Wrote",args.output)
    print("THEORY-ONLY SCALAR passes:",len(passes),"/",len(rows))
    if passes:
        print("beta range [rad] over grid:",passes[0]["beta_rad"],
              passes[-1]["beta_rad"])
    print("NOT an experimentally viable range.")

if __name__=="__main__":main()
