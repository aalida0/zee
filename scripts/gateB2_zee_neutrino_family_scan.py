#!/usr/bin/env python3
"""Gate B2: scan neutrino-compatible complex Zee Yukawas and partial LFV.

This is NOT a full experimental fit or a set of physically allowed points:
Barr-Zee, other LFV diagrams, universality, complete widths, HiggsTools,
and calibrated b->s gamma likelihood remain missing.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import math
import numpy as np

from gateA1b_hierarchical_no_seed import (
    ML,target_neutrino_matrix,antisymmetric_f_with_null_condition,
    solve_lepton_yukawa,reconstruct_neutrino,scalar_kappa,
)
from gateA1c_charged_singlet_lfv import CHANNELS,dipole_coefficient_f_only
from gateA1d_neutral_tree_lfv import tau_tree_br
from gateA1e_neutral_one_loop_dipoles import (
    total_neutral_dipoles,partial_radiative_br,
)
from gateA1f_charged_doublet_y_dipoles import charged_doublet_y_dipole

STATUS="GATE_B2_NEUTRINO_ALGEBRA_AND_PARTIAL_LFV_ONLY_NOT_ALLOWED"
COLS=("id","mH1","mH2","mh2","ma","alpha","beta","gamma")
TAU3MU_LIMIT_REFERENCE=1.9e-8

def read_candidates(path):
    with Path(path).open(newline="") as f:
        rd=csv.DictReader(f)
        if not rd.fieldnames or any(c not in rd.fieldnames for c in COLS):
            raise ValueError("Require Gate B1 full candidate CSV")
        rows=[]
        for row in rd:
            p={"id":str(row["id"])}
            for k in COLS[1:]:
                p[k]=float(row[k])
            if not all(math.isfinite(p[k]) for k in COLS[1:]) or not (
                200<=p["mH1"]<p["mH2"]<=10000 and
                0<p["gamma"]<math.pi/2 and
                0<p["beta"]<math.pi/2 and
                p["mh2"]>0 and p["ma"]>0):
                raise ValueError("Invalid Gate B1 point")
            rows.append(p)
    if not rows or len(set(x["id"] for x in rows))!=len(rows):
        raise ValueError("Empty or duplicate B1 candidate rows")
    return rows

def f_from_null_parameter(M,t,norm,root=0):
    """Find n=(1,x,t) satisfying n.T M n=0, build antisymmetric f n=0."""
    if not (math.isfinite(norm) and norm>0 and root in (0,1)):
        raise ValueError("Invalid f nullspace settings")
    coeff=[M[1,1],2*(M[0,1]+t*M[1,2]),
           M[0,0]+2*t*M[0,2]+t*t*M[2,2]]
    roots=np.roots(coeff)
    if len(roots)!=2:
        raise ValueError("Degenerate Zee null-direction quadratic")
    x=roots[root]
    n=np.array([1.,x,t],complex)
    f=np.array([[0,t,-x],[-t,0,1],[x,-1,0]],complex)
    f*=norm/np.max(abs(f))
    if abs(n.T@M@n)>5e-12 or np.max(abs(f@n))>1e-12:
        raise ValueError("Antisymmetric f identity failed")
    return f

def linear_neutrino_operator(f,kappa):
    upper=np.triu_indices(3)
    cols=[]
    for i in range(3):
        for j in range(3):
            E=np.zeros((3,3),complex);E[i,j]=1.
            a=f@ML@E
            cols.append((kappa*(a+a.T)*1e9)[upper])
    return np.asarray(cols).T

def family_yukawa(f,M,kappa,rng,strength=0.):
    """One particular Y plus all 4 complex homogeneous directions."""
    Y0,rank,_=solve_lepton_yukawa(f,M,kappa=kappa)
    if rank!=5: raise ValueError("Zee neutrino rank != 5")
    op=linear_neutrino_operator(f,kappa)
    _,sing,vh=np.linalg.svd(op,full_matrices=True)
    if np.sum(sing>sing[0]*1e-13)!=5:
        raise ValueError("Unstable linear-system rank")
    null=vh[5:,:].conj().T
    if null.shape!=(9,4) or np.max(abs(op@null))>max(
        1e-9,np.max(abs(op))*2e-12):
        raise ValueError("Complex nullspace closure failed")
    z=(rng.normal(size=4)+1j*rng.normal(size=4))/np.sqrt(8.)
    Y=Y0+(null@(z*strength*np.linalg.norm(Y0))).reshape(3,3)
    err=float(np.max(abs(reconstruct_neutrino(f,Y,kappa=kappa)-M)))
    if not np.isfinite(err) or err>=1e-9:
        raise ValueError("Neutrino matrix closure failure")
    return Y,err

def subset_lfv(p,f,Y):
    """Coherent implemented 1-loop scalar components; NOT full LFV."""
    rates={}
    ratios={}
    for name,info in CHANNELS.items():
        parent,daughter=info["parent"],info["daughter"]
        nl,nr,_=total_neutral_dipoles(
            Y,parent=parent,daughter=daughter,
            mH=p["mh2"],mA=p["ma"],
            alpha=p["alpha"],beta=p["beta"])
        dl,dr=charged_doublet_y_dipole(
            Y,parent=parent,daughter=daughter,m1=p["mH1"],
            m2=p["mH2"],gamma=p["gamma"])
        sr=dipole_coefficient_f_only(
            f,parent,daughter,m1=p["mH1"],m2=p["mH2"],
            gamma=p["gamma"])
        br=partial_radiative_br(nl+dl,nr+dr+sr,
                               norm_br=info["norm_br"])
        rates[name]=br
        ratios[name]=br/info["limit"]
    t3,_=tau_tree_br(Y,daughter=1,mH=p["mh2"],mA=p["ma"],
                     alpha=p["alpha"],beta=p["beta"])
    te,_=tau_tree_br(Y,daughter=0,mH=p["mh2"],mA=p["ma"],
                     alpha=p["alpha"],beta=p["beta"])
    rates["tau_to_3mu_tree_subset"]=t3
    rates["tau_to_e_mumu_tree_subset"]=te
    ratios["tau_to_3mu_tree_subset"]=t3/TAU3MU_LIMIT_REFERENCE
    return rates,ratios

def encode(x):
    return {"real":np.asarray(x).real.tolist(),
            "imag":np.asarray(x).imag.tolist()}

def solve_point(p,M,f,rng,strength):
    kap=scalar_kappa(p["mH1"],p["mH2"],p["gamma"])
    Y,err=family_yukawa(f,M,kap,rng,strength)
    maxf=float(np.max(abs(f)));maxY=float(np.max(abs(Y)))
    if not np.isfinite(maxY) or max(maxY,maxf)>np.sqrt(4*np.pi):
        return None
    rates,ratios=subset_lfv(p,f,Y)
    score=max(ratios.values())
    if not math.isfinite(score):raise ValueError("Nonfinite LFV subset")
    return {
        "candidate_id":p["id"],"mH1":p["mH1"],"mH2":p["mH2"],
        "gamma":p["gamma"],"max_abs_f":maxf,"max_abs_Y":maxY,
        "neutrino_matrix_closure_eV":err,
        "partial_LFV_score_NOT_EXCLUSION":score,
        "partial_LFV_rates_NOT_FULL":rates,
        "partial_LFV_ratios_NOT_EXCLUSION":ratios,
        "nullspace_strength":strength,
        "f":encode(f),"Y":encode(Y),
        "status":"NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED",
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--b1-csv",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,
                    default=Path("work/gateB2_zee_neutrino_family"))
    ap.add_argument("--trials-per-candidate",type=int,default=300)
    ap.add_argument("--top",type=int,default=10)
    ap.add_argument("--seed",type=int,default=20261014)
    a=ap.parse_args()
    if not 1<=a.trials_per_candidate<=50000 or not 1<=a.top<=1000:
        ap.error("Invalid scan settings")
    rows=read_candidates(a.b1_csv)
    M,masses=target_neutrino_matrix()
    fseed,_=antisymmetric_f_with_null_condition(M)
    rng=np.random.default_rng(a.seed)
    successes={};stats={}
    for p in rows:
        output=[];fail=0
        for j in range(a.trials_per_candidate):
            try:
                if j==0:
                    f=fseed
                    strength=0.
                else:
                    t=complex(rng.uniform(-1.5,1.5),
                              rng.uniform(-1.5,1.5))
                    f=f_from_null_parameter(M,t,10**rng.uniform(-5,-2),
                                            int(rng.integers(0,2)))
                    strength=float(10**rng.uniform(-1.5,1.))
                result=solve_point(p,M,f,rng,strength)
                if result is None:fail+=1
                else:output.append(result)
            except (ValueError,ArithmeticError,np.linalg.LinAlgError):
                fail+=1
        output.sort(key=lambda x:x["partial_LFV_score_NOT_EXCLUSION"])
        successes[p["id"]]=output
        stats[p["id"]]={
            "attempted":a.trials_per_candidate,
            "neutrino_closed_perturbative":len(output),
            "rejected_numeric_or_nonperturbative":fail,
            "best_partial_LFV_score": (
                output[0]["partial_LFV_score_NOT_EXCLUSION"] if output else None),
        }
    a.output_dir.mkdir(parents=True,exist_ok=True)
    ranked=a.output_dir/"ranked_partial_LFV_NOT_ALLOWED.csv"
    cols=("candidate_id","rank","mH1","mH2","gamma","max_abs_f",
          "max_abs_Y","neutrino_matrix_closure_eV",
          "partial_LFV_score_NOT_EXCLUSION","nullspace_strength","status")
    with ranked.open("w",newline="") as h:
        w=csv.DictWriter(h,fieldnames=cols);w.writeheader()
        for id_,data in successes.items():
            for rank,x in enumerate(data[:a.top],1):
                w.writerow({**{k:x[k] for k in cols if k!="rank"},"rank":rank})
    matrices=a.output_dir/"top_neutrino_Yukawa_matrices_NOT_ALLOWED.json"
    matrices.write_text(json.dumps(
        {k:v[:a.top] for k,v in successes.items()},indent=2)+"\n")
    info={
        "status":STATUS,"neutrino_target":"fixed A1B normal ordering central inputs",
        "neutrino_masses_eV":masses.tolist(),
        "family":"complex f null-direction; overall f scale; 4 complex Y-null modes",
        "statistics":stats,"top_Yukawas_json":str(matrices),
        "ranked_csv":str(ranked),
        "physical_Zee_allowed_points":None,
        "meaning_of_small_partial_LFV_score":
            "NOT a physical pass because Barr-Zee and other LFV amplitudes missing",
        "outstanding":[
            "full two-loop LFV, mu to 3e and mu-e conversion",
            "neutrino oscillation ranges, ordering and Majorana phases",
            "full charged-scalar lepton widths and HiggsTools",
            "precision b to s gamma likelihood and global vacuum"],
    }
    (a.output_dir/"summary.json").write_text(json.dumps(info,indent=2)+"\n")
    print("STATUS",STATUS)
    for k,x in stats.items():
        print("CANDIDATE",k,"NEUTRINO_CLOSED",x["neutrino_closed_perturbative"],
              "BEST_PARTIAL_LFV_RATIO",x["best_partial_LFV_score"])
    print("COMPLETE_LFV_CALCULATED False")
    print("FULL_ZEE_ALLOWED_POINTS unknown")
    print("Wrote",ranked)

if __name__=="__main__":
    main()
