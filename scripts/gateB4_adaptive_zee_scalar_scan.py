#!/usr/bin/env python3
"""B4: adaptive Zee scalar/EWPO screening, NOT a global physics fit.

Correlated random-walk proposals seeded by B1 candidates explore the
full tree-level Zee scalar reconstruction including singlet quartics.
Accepted points satisfy implemented sufficient BFB, tree unitarity and
correlated S,T,U Gaussian ellipsoids, NOT complete experimental bounds.

Acceptance efficiency is NOT a posterior probability or physical
allowed-volume estimate. No full LFV, HiggsTools, modern two-state
b->s gamma, global vacuum proof or physical production rates.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
import numpy as np

from gate6_benchmark import benchmark
from gate6_width_inventory import inventory, MZ
from gateA1h_correlated_stu_ewpo import report as stu_report

STATUS="GATE_B4_ADAPTIVE_ZEE_SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED"
COORDS=("mH1","mH2","mh2","ma","beta","delta","gamma","soft",
        "log_lc","log_k1","log_k2","r12")
STEP=np.array([6.,6.,5.,5.,.00045,.0035,.024,1200.,.07,.08,.14,.04])
SINGLET_DEFAULTS={"lc":4.473,"k1":1.082,"k2":.00398,"k12":-.001266}
OUTPUT_COLS=(
    "id","seed_id","iteration","mH1","mH2","mh2","ma",
    "alpha","beta","gamma","m12sq","lc","k1","k2","k12",
    "tanbeta","lambda1","lambda2","lambda3","lambda4","lambda5",
    "max_unitarity","S","T","U","chi2_Gfitter","chi2_PDG",
    "BR_H2_H1Z_nonleptonic_included_upper_proxy",
    "BR_H1_tb_nonleptonic_included_upper_proxy",
    "production_weighted_nonleptonic_cascade_upper_proxy",
    "flavor_and_HiggsTools_applied","candidate_status")


def read_seed_csv(path):
    out=[]
    with Path(path).open(newline="") as stream:
        reader=csv.DictReader(stream)
        required=("id","mH1","mH2","mh2","ma","alpha","beta",
                  "gamma","m12sq")
        if not reader.fieldnames or any(k not in reader.fieldnames
                                       for k in required):
            raise ValueError("Require B1/B4 screened-candidate CSV")
        for row in reader:
            p={k:float(row[k]) for k in required if k!="id"}
            p.update({k:(float(row[k]) if row.get(k) not in (None,"")
                         else default)
                      for k,default in SINGLET_DEFAULTS.items()})
            p["seed_id"]=str(row["id"])
            if not all(math.isfinite(v) for k,v in p.items() if k!="seed_id"):
                raise ValueError("Nonfinite seed input")
            out.append(p)
    if not out:raise ValueError("Empty seed CSV")
    return out


def encode(p):
    """Use soft M^2=m12^2/(sin beta cos beta) and log-positive quartics."""
    beta=p["beta"]
    sc=math.sin(beta)*math.cos(beta)
    if sc<=0 or p["m12sq"]<=0 or min(p[k] for k in
                                      ("lc","k1","k2"))<=0:
        raise ValueError("Invalid scalar seed")
    ratio=p["k12"]/min(p["k1"],p["k2"])
    if not abs(ratio)<1.:
        raise ValueError("Seed fails singlet BFB cross bound")
    return np.asarray([
        p["mH1"],p["mH2"],p["mh2"],p["ma"],beta,
        p["alpha"]-beta,p["gamma"],p["m12sq"]/sc,
        math.log(p["lc"]),math.log(p["k1"]),math.log(p["k2"]),
        ratio],float)


def decode(x):
    if x.shape!=(len(COORDS),) or not np.all(np.isfinite(x)):
        return None
    m1,m2,mh,ma,beta,delta,gamma,soft,llc,lk1,lk2,r=x
    if not (200<=m1<=720 and m1+MZ+1.<m2<=1600
            and 200<=mh<=1550 and 200<=ma<=1550
            and .45<beta<1.54 and -.20<delta<.20
            and .08<gamma<1.50 and 1.e4<soft<2.e6
            and math.log(1.e-5)<llc<math.log(15.)
            and math.log(1.e-5)<lk1<math.log(15.)
            and math.log(1.e-6)<lk2<math.log(15.)
            and abs(r)<.98):
        return None
    k1,k2=math.exp(lk1),math.exp(lk2)
    return {
        "mH1":float(m1),"mH2":float(m2),
        "mh2":float(mh),"ma":float(ma),
        "beta":float(beta),"alpha":float(beta+delta),
        "gamma":float(gamma),
        "m12sq":float(soft*math.sin(beta)*math.cos(beta)),
        "lc":float(math.exp(llc)),"k1":float(k1),"k2":float(k2),
        "k12":float(r*min(k1,k2))}


def propose(base,rng,scale):
    x=base.copy()
    mode=rng.random()
    if mode<.61:
        dims=rng.choice(len(COORDS),size=1,replace=False)
    elif mode<.91:
        dims=rng.choice(len(COORDS),
                        size=int(rng.integers(2,5)),replace=False)
    else:
        dims=np.arange(len(COORDS))
    kick=scale*(3. if rng.random()<.055 else 1.)
    x[dims]+=rng.normal(size=len(dims))*STEP[dims]*kick
    return x


def scalar_screen(p):
    theory=benchmark(
        beta=p["beta"],mH1=p["mH1"],mH2=p["mH2"],
        alpha=p["alpha"],gamma=p["gamma"],m12sq=p["m12sq"],
        mh2=p["mh2"],ma=p["ma"],lc=p["lc"],k1=p["k1"],
        k2=p["k2"],k12=p["k12"])
    if not (theory["sufficient_global_quartic_BFB"] and
            theory["tree_unitarity_pass"]):
        return None
    return theory


def ewpo_screen(p,quad):
    report=stu_report(
        m1=p["mH1"],m2=p["mH2"],mh=125.,
        mH=p["mh2"],mA=p["ma"],alpha=p["alpha"],
        beta=p["beta"],gamma=p["gamma"],n=quad)
    if not all(x["inside_95percent_3D_gaussian_ellipsoid"]
               for x in report["correlated_fit_screens"].values()):
        return None
    return report


def nonleptonic_proxy(p):
    """Upper-bound proxy; omit the obsolete Type-II lepton width."""
    r=inventory(
        beta=p["beta"],mH1=p["mH1"],mH2=p["mH2"],
        alpha=p["alpha"],gamma=p["gamma"],m12sq=p["m12sq"],
        mh2=p["mh2"],ma=p["ma"],lc=p["lc"],k1=p["k1"],
        k2=p["k2"],k12=p["k12"])
    widths=r["partial_widths_GeV"]
    had={s:{name:v for name,v in widths[s].items()
            if name!="tau_nu_TypeII"} for s in ("H1","H2")}
    sums={s:sum(had[s].values()) for s in had}
    if min(sums.values())<=0:
        raise ValueError("Invalid nonleptonic inventory")
    b2=had["H2"]["H1_Z"]/sums["H2"]
    b1=had["H1"]["tb"]/sums["H1"]
    return b2,b1,math.sin(p["gamma"])**2*b2*b1


def make_record(p,theory,ew,it,uid,seed_id):
    st=ew["scalar_STU"]
    fits=ew["correlated_fit_screens"]
    b2,b1,proxy=nonleptonic_proxy(p)
    return {
        "id":uid,"seed_id":seed_id,"iteration":it,
        **p,"tanbeta":theory["tanbeta"],**theory["quartics"],
        "max_unitarity":theory["max_abs_unitarity_eigenvalue"],
        **st,
        "chi2_Gfitter":fits["Gfitter_2026_U_floating"]
                            ["chi2_relative_to_fit_minimum"],
        "chi2_PDG":fits["PDG_2025_U_floating"]
                        ["chi2_relative_to_fit_minimum"],
        "BR_H2_H1Z_nonleptonic_included_upper_proxy":b2,
        "BR_H1_tb_nonleptonic_included_upper_proxy":b1,
        "production_weighted_nonleptonic_cascade_upper_proxy":proxy,
        "flavor_and_HiggsTools_applied":False,
        "candidate_status":"SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED"}


def coarse_bin(p):
    return (
        int(p["mH1"]//12),int(p["mH2"]//18),
        int(p["mh2"]//25),int(p["ma"]//25),
        int(p["gamma"]/.065),int(p["beta"]/.012),
        int(p["k1"]/.2),int(math.log10(p["k2"])/.35))


def shortlist(rows,n):
    s=sorted(rows,key=lambda r:r[
        "production_weighted_nonleptonic_cascade_upper_proxy"],reverse=True)
    chosen=[];bins=set()
    for row in s:
        cell=(int(row["mH1"]//25),int(row["mH2"]//40),
              int(row["gamma"]/.12))
        if cell in bins:continue
        bins.add(cell);chosen.append(row)
        if len(chosen)>=n:break
    return chosen


def write_csv(path,rows,headers=OUTPUT_COLS):
    with Path(path).open("w",newline="") as stream:
        w=csv.DictWriter(stream,fieldnames=headers,extrasaction="ignore")
        w.writeheader();w.writerows(rows)


def scan(seeds,*,steps,chains,quad,adaptive_block,rng,
         report_every=500):
    if steps<0 or chains<=0 or quad<40 or adaptive_block<20:
        raise ValueError("Invalid scanner settings")
    records=[];states=[];provenance=[];seen=set()
    reject={"invalid_input":0,"scalar_theory":0,
            "oblique_gaussian":0,"numerical":0}
    for seed in seeds:
        p={k:v for k,v in seed.items() if k!="seed_id"}
        try:
            x=encode(p)
            decoded=decode(x)
            if decoded is None:raise ValueError("Outside B4 domain")
            th=scalar_screen(decoded)
            ew=ewpo_screen(decoded,quad) if th is not None else None
            if th is None or ew is None:
                raise ValueError("Input did not pass scalar and S,T,U screens")
            row=make_record(decoded,th,ew,0,"B4_seed_"+seed["seed_id"],
                            seed["seed_id"])
        except (ValueError,ArithmeticError,FloatingPointError,
                np.linalg.LinAlgError) as exc:
            raise ValueError("Invalid initial seed "+seed["seed_id"]+
                             ": "+str(exc)) from exc
        cell=coarse_bin(decoded)
        if cell not in seen:records.append(row);seen.add(cell)
        states.append(x);provenance.append(seed["seed_id"])
    initial=list(states);sources=list(provenance)
    while len(states)<chains:
        k=len(states)%len(initial)
        states.append(initial[k].copy());provenance.append(sources[k])
    states=states[:chains];provenance=provenance[:chains]
    accepted=0;theory_ok=0;per_block=0;scale=1.
    history=[]
    for it in range(1,steps+1):
        k=int(rng.integers(0,len(states)))
        x=propose(states[k],rng,scale)
        p=decode(x)
        success=False
        if p is None:
            reject["invalid_input"]+=1
        else:
            try:
                th=scalar_screen(p)
                if th is None:
                    reject["scalar_theory"]+=1
                else:
                    theory_ok+=1
                    ew=ewpo_screen(p,quad)
                    if ew is None:
                        reject["oblique_gaussian"]+=1
                    else:
                        success=True
            except (ValueError,ArithmeticError,FloatingPointError,
                    np.linalg.LinAlgError):
                reject["numerical"]+=1
        if success:
            cell=coarse_bin(p)
            new_record=None
            if cell not in seen:
                try:
                    new_record=make_record(
                        p,th,ew,it,"B4_"+str(it).zfill(7),provenance[k])
                except (ValueError,ArithmeticError,FloatingPointError,
                        np.linalg.LinAlgError):
                    # A proposal is accepted only when its required
                    # recorded observables can also be calculated.
                    reject["numerical"]+=1
                    success=False
            if success:
                accepted+=1;per_block+=1
                states[k]=x
                if new_record is not None:
                    records.append(new_record);seen.add(cell)
        if it%adaptive_block==0:
            rate=per_block/adaptive_block
            if rate>.43:scale=min(6.,scale*1.22)
            elif rate<.09:scale=max(.15,scale*.82)
            history.append({"iteration":it,"block_acceptance":rate,
                            "proposal_scale":scale})
            per_block=0
        if report_every>0 and it%report_every==0:
            print("ITER",it,"EWPO_ACCEPTED",accepted,
                  "DISTINCT_BINS",len(records),
                  "SCALE",round(scale,3),flush=True)
    summary={
        "attempted_new_proposals":steps,"initial_seeds":len(seeds),
        "chains":len(states),"theory_screen_pass_proposals":theory_ok,
        "EWPO_screen_pass_proposals":accepted,
        "distinct_screened_parameter_bins":len(records),
        "stage_rejection_counts":reject,
        "proposal_acceptance_NOT_allowed_volume":accepted/steps if steps else None,
        "proposal_scale_adaptation":history,
        "n_physically_allowed_points":None,
        "note":"Seeded correlated proposals, not unbiased sampling or a posterior. "
               "No allowed-volume or confidence-level inference is permitted.",
        "HiggsTools_applied":False,
        "full_neutrino_LFV_applied":False,
        "calibrated_b_to_s_gamma_applied":False}
    return records,summary


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed-csv",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,
                    default=Path("work/gateB4_zee_adaptive_scalar"))
    ap.add_argument("--steps",type=int,default=5000)
    ap.add_argument("--chains",type=int,default=12)
    ap.add_argument("--top",type=int,default=40)
    ap.add_argument("--quadrature-nodes",type=int,default=96)
    ap.add_argument("--adapt-every",type=int,default=200)
    ap.add_argument("--random-seed",type=int,default=20261013)
    a=ap.parse_args()
    if not (1<=a.steps<=200000 and 2<=a.chains<=128 and
            1<=a.top<=1000 and 40<=a.quadrature_nodes<=320 and
            20<=a.adapt_every<=5000):
        ap.error("Invalid scan settings")
    seeds=read_seed_csv(a.seed_csv)
    rows,summary=scan(
        seeds,steps=a.steps,chains=a.chains,quad=a.quadrature_nodes,
        adaptive_block=a.adapt_every,
        rng=np.random.default_rng(a.random_seed))
    a.output_dir.mkdir(parents=True,exist_ok=True)
    full=a.output_dir/"all_screened_candidates_NOT_ALLOWED.csv"
    write_csv(full,rows)
    key="production_weighted_nonleptonic_cascade_upper_proxy"
    by_proxy=sorted(rows,key=lambda r:r[key],reverse=True)
    by_br=sorted(rows,key=lambda r:r[
        "BR_H2_H1Z_nonleptonic_included_upper_proxy"],reverse=True)
    proxy_path=a.output_dir/"ranked_by_cascade_proxy_NOT_ALLOWED.csv"
    write_csv(proxy_path,by_proxy[:a.top])
    write_csv(a.output_dir/"ranked_by_cascade_BR_NOT_ALLOWED.csv",
              by_br[:a.top])
    selected=shortlist(rows,a.top)
    b2csv=a.output_dir/"diverse_candidates_for_B2_NOT_ALLOWED.csv"
    write_csv(b2csv,selected)
    flav=a.output_dir/"flavour_inputs_selected.csv"
    write_csv(flav,selected,("mH1","mH2","gamma","tanbeta"))
    summary.update({
        "status":STATUS,"random_seed":a.random_seed,
        "singlet_quartics_varied":True,
        "BFB_test":"Sufficient, not necessary, Zee quartic condition",
        "EWPO_test":"Scalar S,T,U correlated Gfitter+PDG Gaussian",
        "ranking":"Nonleptonic LO included-channel UPPER-BOUND proxies; "
                  "requires B2+B3 leptonic widths at each selected point",
        "input_seed_csv":str(a.seed_csv),
        "diverse_shortlist_size":len(selected),
        "paths":{"all_screened_candidates":str(full),
                 "ranked_by_proxy":str(proxy_path),
                 "diverse_candidates_for_B2":str(b2csv),
                 "selected_A1V_flavour_inputs":str(flav)},
        "remaining_constraints":[
            "full neutrino likelihood and LFV including Barr-Zee",
            "HiggsTools and full model spectra/decay inputs",
            "modern matched two-charged B->Xs gamma likelihood",
            "global vacuum including charge-breaking minima",
            "complete widths and hadronic cross sections"]})
    (a.output_dir/"summary.json").write_text(
        json.dumps(summary,indent=2)+"\n")
    print("STATUS",STATUS)
    print("THEORY_PASS_PROPOSALS",summary["theory_screen_pass_proposals"])
    print("EWPO_PASS_PROPOSALS",summary["EWPO_screen_pass_proposals"])
    print("DISTINCT_SCREENED_BINS",len(rows))
    print("DIVERSE_B2_CANDIDATES",len(selected))
    print("FULL_EXPERIMENTAL_ACCEPTANCE_CALCULATED False")
    print("PHYSICALLY_ALLOWED_POINTS unknown")
    print("OUTPUT",b2csv)


if __name__=="__main__":
    main()
