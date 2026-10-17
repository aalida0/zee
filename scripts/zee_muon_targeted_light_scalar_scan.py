#!/usr/bin/env python3
"""Paper 2: targeted *correlated* Zee scalar/EWPO search at lighter masses.

Reuses Gate6 full scalar-potential BFB/tree unitarity and Gate A1H
two published correlated S,T,U 95%-ellipsoid screens without changing
any physics criteria. Randomly deforms existing B4 accepted scalar
spectra to desired H1/H2 mass pairs and simultaneously adjusts neutral
masses, soft M^2, beta/delta, mixing gamma and singlet quartics.
Does not presume that independently picked physical masses are viable.

Only accepted scalar+EWPO points are recorded. NO calibrated flavor,
HiggsTools, LFV, neutrino solution, global vacuum or physical widths.
Any reported H1 H1 Z -> tb tb Z yield is an included-channel-only
conditional upper-style proxy, never a signal prediction.
This is a seeded conditional search, NOT model allowed-volume statistics
or proof of impossibility when no points pass.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from collections import Counter
import numpy as np

from gateB4_adaptive_zee_scalar_scan import (
    read_seed_csv,encode,decode,scalar_screen,ewpo_screen,
    make_record,OUTPUT_COLS,coarse_bin,
)
from zee_muon_mass_mixing_grid import ALPHA_YW,SW2_YW
from zee_muon_asymmetric_pair_pilot import (
    sigma_both_charges_fb,BR_Z_EE_MUMU,rest_frame_b_momentum,
)

STATUS="PAPER2_LIGHT_ZEE_TARGETED_SCALAR_EWPO_SEARCH_ONLY_NOT_ALLOWED"
DEFAULT_TARGETS="250:500,300:500,250:550,300:550"


def parse_targets(s):
    out=[]
    for item in s.split(","):
        bits=item.split(":")
        if len(bits)!=2:raise ValueError("Use mH1:mH2 comma-separated targets")
        try:m1,m2=map(float,bits)
        except ValueError as exc:raise ValueError("Invalid target masses") from exc
        if not (math.isfinite(m1) and math.isfinite(m2)
                and 200<=m1<m2 and m2>m1+91.1876+1.
                and m1<=720 and m2<=1600):
            raise ValueError("Target violates original Gate B4 mass/decay domain")
        if (m1,m2) in out:raise ValueError("Repeated target")
        out.append((m1,m2))
    if not out:raise ValueError("No targets")
    return out


def deform(source,goal,rng,*,mass_sigma=18.):
    """Correlate neutral/charged scales and soft mass to new physical masses."""
    m1,m2=goal
    old_m2=source["mH2"]
    scale=m2/old_m2
    p=dict(source)
    p.pop("seed_id",None)
    p["mH1"]=float(m1+rng.normal(0,mass_sigma))
    p["mH2"]=float(m2+rng.normal(0,mass_sigma))
    if not 200<=p["mH1"]<p["mH2"]-91.1876-1.:
        return None
    # Neutral masses need not equal the charged masses. Use two
    # physically motivated proposal families to avoid forcing
    # mA/mHheavy to scale in precisely one arbitrary way.
    if rng.random()<.5:
        p["mh2"]=float(source["mh2"]*scale+rng.normal(0,45))
        p["ma"]=float(source["ma"]*scale+rng.normal(0,45))
    else:
        p["mh2"]=float(p["mH2"]+
                       (source["mh2"]-source["mH2"])*rng.uniform(.6,1.4)
                       +rng.normal(0,45))
        p["ma"]=float(p["mH2"]+
                     (source["ma"]-source["mH2"])*rng.uniform(.6,1.4)
                     +rng.normal(0,45))
    p["mh2"]=max(200.,p["mh2"])
    p["ma"]=max(200.,p["ma"])
    p["beta"]=float(source["beta"]+rng.normal(0,.045))
    delta=source["alpha"]-source["beta"]
    p["alpha"]=float(p["beta"]+delta+rng.normal(0,.020))
    # One family tests near-maximal doublet-singlet mixing, the other
    # follows the correlated mixing found in the accepted B4 seeds.
    p["gamma"]=float(
        (math.pi/4 if rng.random()<.6 else source["gamma"])
        +rng.normal(0,.14))
    old_soft=source["m12sq"]/(math.sin(source["beta"])*
                               math.cos(source["beta"]))
    # Shift the soft scale coherently with the charged mass squared.
    # Random breadth avoids silently pinning unrelated quartics.
    soft=old_soft*scale**2*float(np.exp(rng.normal(0,.33)))
    p["m12sq"]=float(soft*math.sin(p["beta"])*math.cos(p["beta"]))
    for k in ("lc","k1","k2"):
        p[k]=float(source[k]*np.exp(rng.normal(0,.35)))
    r=source["k12"]/min(source["k1"],source["k2"])
    r=float(np.clip(r+rng.normal(0,.2),-.90,.90))
    p["k12"]=float(r*min(p["k1"],p["k2"]))
    return p


def choose_sources(seeds,n):
    if n<=0:raise ValueError("Positive number of sources needed")
    ranked=sorted(seeds,key=lambda p:(abs(p["mH2"]-593.)+
                                     abs(p["mH1"]-275.)+
                                     100*abs(p["gamma"]-math.pi/4)))
    # Deduplicate correlated neighbors by mass and charged angle.
    seen=set();out=[]
    for s in ranked:
        cell=(int(s["mH1"]//20),int(s["mH2"]//20),
              int(s["gamma"]/.05))
        if cell in seen:continue
        seen.add(cell);out.append(s)
        if len(out)>=n:break
    if not out:raise ValueError("No usable starting spectra")
    return out


def objective(p,record,E=1500.,L=.5):
    sigma=sigma_both_charges_fb(
        E,p["mH1"],p["mH2"],p["gamma"],
        alpha=ALPHA_YW,sw2=SW2_YW)
    b2=record["BR_H2_H1Z_nonleptonic_included_upper_proxy"]
    b1=record["BR_H1_tb_nonleptonic_included_upper_proxy"]
    n_pair=sigma*1000*L
    return {
        "sigma_Z_both_charges_1500GeV_fb":sigma,
        "n_pairs_0p5ab":n_pair,
        "n_Z_ll_tb_tb_conditional_ceiling_0p5ab":
            n_pair*BR_Z_EE_MUMU*b2*b1*b1,
        "H1_rest_b_momentum_GeV":
            rest_frame_b_momentum(p["mH1"]),
    }


def sample(seeds,targets,trials,rng,quadrature=64,source_count=32,
           report_every=1000):
    if trials<0 or quadrature<40:raise ValueError("Invalid search settings")
    chosen=choose_sources(seeds,source_count)
    rows=[];counts=Counter();best_by_target={}
    bins=set();total=0
    for target_index,goal in enumerate(targets):
        label=f"m{int(goal[0])}_{int(goal[1])}"
        for j in range(trials):
            total+=1
            src=chosen[int(rng.integers(0,len(chosen)))]
            p=deform(src,goal,rng)
            if p is None:
                counts["mass_or_decay_domain"]+=1
                continue
            try:
                # Preserve B4 decode domain including singlet quartics,
                # beta/delta, gamma, and the positive soft term.
                decoded=decode(encode(p))
                if decoded is None:
                    counts["outside_B4_proposal_domain"]+=1
                    continue
                theory=scalar_screen(decoded)
                if theory is None:
                    counts["scalar_BFB_or_tree_unitarity_fail"]+=1
                    continue
                counts["scalar_pass"]+=1
                ew=ewpo_screen(decoded,quadrature)
                if ew is None:
                    counts["correlated_STU_95percent_fail"]+=1
                    continue
                counts["scalar_and_STU_pass"]+=1
                record=make_record(
                    decoded,theory,ew,total,f"P2L_{total:07d}",
                    str(src["seed_id"]))
                # Same output schema as B4; usable by existing B2/B3.
                record["target_mass_pair"]=label
                metrics=objective(decoded,record)
                record.update(metrics)
                cell=coarse_bin(decoded)
                if cell in bins:
                    counts["coarse_duplicate"]+=1
                    continue
                bins.add(cell);rows.append(record)
                best=best_by_target.get(label)
                if best is None or (
                    metrics["n_Z_ll_tb_tb_conditional_ceiling_0p5ab"]>
                    best["n_Z_ll_tb_tb_conditional_ceiling_0p5ab"]):
                    best_by_target[label]={
                        **{k:record[k] for k in ("id","mH1","mH2",
                                                  "mh2","ma","gamma",
                                                  "chi2_Gfitter","chi2_PDG")},
                        **metrics,
                    }
            except (ValueError,ArithmeticError,FloatingPointError,
                    np.linalg.LinAlgError):
                counts["numerical_or_width_failure"]+=1
            if report_every>0 and (j+1)%report_every==0:
                print("TARGET",label,"ATTEMPTS",j+1,
                      "SCALAR_STU_PASSES",
                      counts["scalar_and_STU_pass"],
                      "DISTINCT",len(rows),flush=True)
    return rows,{
        "n_attempts":total,
        "n_sources":len(chosen),
        "n_scalar_STU_passes":counts["scalar_and_STU_pass"],
        "stage_counts":dict(counts),
        "top_by_target_conditional_ceiling":best_by_target,
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--b4-csv",type=Path,required=True)
    ap.add_argument("--targets",default=DEFAULT_TARGETS)
    ap.add_argument("--trials-per-target",type=int,default=3000)
    ap.add_argument("--sources",type=int,default=32)
    ap.add_argument("--quadrature-nodes",type=int,default=64)
    ap.add_argument("--seed",type=int,default=20261017)
    ap.add_argument("--output-dir",type=Path,required=True)
    a=ap.parse_args()
    if not(10<=a.trials_per_target<=100000 and
           1<=a.sources<=1000 and 40<=a.quadrature_nodes<=320):
        ap.error("Invalid trials, sources or quadrature")
    targets=parse_targets(a.targets)
    seeds=read_seed_csv(a.b4_csv)
    rows,stat=sample(seeds,targets,a.trials_per_target,
                     np.random.default_rng(a.seed),
                     quadrature=a.quadrature_nodes,
                     source_count=a.sources)
    out=a.output_dir
    if out.exists() and any(out.iterdir()):
        raise ValueError("Use NEW empty result directory")
    out.mkdir(parents=True,exist_ok=True)
    file=out/"all_screened_candidates_NOT_ALLOWED.csv"
    # Preserve complete original B4 schema for downstream readers;
    # add target and gauge objective with no hidden physics claims.
    columns=tuple(OUTPUT_COLS)+(
        "target_mass_pair","sigma_Z_both_charges_1500GeV_fb",
        "n_pairs_0p5ab",
        "n_Z_ll_tb_tb_conditional_ceiling_0p5ab",
        "H1_rest_b_momentum_GeV")
    with file.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=columns)
        w.writeheader()
        w.writerows(rows)
    stats={
        "status":STATUS,"source_B4_csv":str(a.b4_csv),
        "targets":targets,**stat,
        "n_unique_screened_records":len(rows),
        "not_posterior_or_proof_of_exclusion":True,
        "full_Zee_neutrino_LFV_HiggsTools_Bsgamma_applied":False,
        "full_model_allowed_points":None,
        "conditional_widths_not_physical_BRs":True,
        "EWPO_screens":"both published correlated 95% 3D fits, unchanged",
        "EW_scheme":"YangWu 1/127.9,GF 1.16637e-5,MZ",
        "output_csv":str(file),
    }
    (out/"summary.json").write_text(json.dumps(stats,indent=2)+"\n")
    print("STATUS",STATUS)
    print("TARGETS",targets,"ATTEMPTS",stat["n_attempts"])
    print("SCALAR_STU_PASSES",stat["n_scalar_STU_passes"])
    print("DISTINCT_SCREENED_SPECTRA",len(rows))
    print("STAGE_COUNTS",stat["stage_counts"])
    for t,res in stat["top_by_target_conditional_ceiling"].items():
        print("TARGET_BEST",t,"ID",res["id"],
              "m1",round(res["mH1"],1),"m2",round(res["mH2"],1),
              "gamma",round(res["gamma"],3),
              "sigma_Z_fb",round(res["sigma_Z_both_charges_1500GeV_fb"],5),
              "conditional_Zll_ceiling",round(
                  res["n_Z_ll_tb_tb_conditional_ceiling_0p5ab"],2))
    print("FULL_ZEE_ALLOWED_POINTS unknown")
    print("OUTPUT",file)

if __name__=="__main__":
    main()
