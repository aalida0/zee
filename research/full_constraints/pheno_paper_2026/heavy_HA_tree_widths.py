#!/usr/bin/env python3
"""Source-matched 64-family heavy Zee H/A *tree-level lower-width* ledger.

Actual new per-family D is reconstructed by the native Module2 neutrino
inverse and the saved source input SHA. The complete *non-overlapping*
on-shell tree channels computed are:
- 6 diagonal quark flavors with source D4 running Yukawa masses at parent
  scale and independent physical threshold kinematic masses;
- 6 neutral charged-lepton combinations including LFV charge-conjugate
  pairs, native Module3 exact complex neutral-width kernels;
- H→WW,ZZ at ordinary on-shell tree level, with native H kappaV;
- H→hh via the independently source-validated trilinear;
- H/A→H1±W∓ and H2±W∓, both charge configurations;
- H/A→H_i+ H_j- open two-body pairs, including correct charge multiplicity;
- A→hZ at tree level.
If another on-shell heavy-neutral transition opens, it is explicitly
flagged MISSING_ON_SHELL, never implicitly zero. Loop gg, gamma gamma,
Zgamma, QCD/EW radiative corrections, 3/4 body virtual tails are not
included. Thus the *sum* is a positive lower bound only at the declared
tree-level channel decomposition, not a physical measured total width.

Never feed BR(ττ)=Γττ/known_sum as a physical HiggsTools model prediction.
The ratio is an **upper bound** assuming remaining omitted decay channels
give positive widths, at the chosen tree order, only.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np

from module14.scan import digest
from module2.interface import evaluate as neutrino_evaluate, decode
from module1.scalar_constraints import reconstruct
from module3.core import vertices,neutral_width
from module4.couplings import quarks,trilinears
from module7.d4_inputs import SM,yukawa_masses
from module7.d4_tree_kernels import scalar_scalar,scalar_vector
from research.full_constraints.higgs.decays_bridge import neutral_hhh

SOURCE_TAU_FRACTION_KEY="tau tau"
ROOT=Path(__file__).resolve().parents[3]

def positive_channel(width,label):
    if not isinstance(width,(int,float,np.floating)) or not math.isfinite(float(width)) or width<0:
        raise ArithmeticError(f"Invalid tree partial width {label}: {width}")
    return float(width)

def vv_width(M,mv,v,kv,identical):
    if M<2*mv:return 0.0
    z=(mv/M)**2
    return positive_channel(
        kv**2*M**3/(16*math.pi*v*v)*
        math.sqrt(1-4*z)*(1-4*z+12*z*z)*
        (0.5 if identical else 1.0),"H_to_VV"
    )

def heavy_tree_channels(p,D,state):
    if state not in ("H","A"):raise ValueError("Only heavy neutral H or A")
    M=p["mh2" if state=="H" else "ma"]
    if M<=2*SM["EW"]["mW"]:raise ValueError("Benchmarks must have on-shell W pairs")
    ml=np.asarray(SM["lepton_masses"],dtype=float)
    vertex=vertices(D,p,ml)[state]
    C=vertex[0]
    if abs(vertex[1]-M)>1e-9:raise ArithmeticError("Native neutral scalar mass mismatch")
    masses_yuk=yukawa_masses(M)
    masses_kin=SM["kinematic_masses"]
    channels={}
    for f,my,mk in zip(SM["quark_order"],masses_yuk,masses_kin):
        species="top" if f in ("u","c","t") else "bottom"
        q=quarks(my,species,p)[state]
        beta=math.sqrt(max(0,1-4*mk*mk/(M*M)))
        width=3*M/(8*math.pi)*(float(q.real*q.real)*beta**3+float(q.imag*q.imag)*beta)
        channels[f+" "+f+"bar"]=positive_channel(width,f)
    for i,lepi in enumerate(("e","mu","tau")):
        for j,lepj in enumerate(("e","mu","tau")):
            if j<i:continue
            name=lepi+" "+lepj if i!=j else lepi+" "+lepi
            channels[name]=positive_channel((2 if i!=j else 1)*neutral_width(C,M,i,j,ml),name)
    if state=="H":
        kv=math.sin(p["beta"]-p["alpha"])
        channels["WW"]=vv_width(M,SM["EW"]["mW"],p["v"],kv,False)
        channels["ZZ"]=vv_width(M,SM["EW"]["mZ"],p["v"],kv,True)
        channels["h h"]=positive_channel(scalar_scalar(M,p["mh1"],p["mh1"],neutral_hhh(p))/2,"Hhh")
    else:
        channels["h Z"]=positive_channel(
            scalar_vector(M,p["mh1"],SM["EW"]["mZ"],
                          SM["EW"]["mZ"]/p["v"]*math.sin(p["beta"]-p["alpha"])),
            "AhZ")
    cg=math.cos(p["gamma"])
    sg=math.sin(p["gamma"])
    for k,weight in ((1,cg),(2,-sg)):
        c=SM["EW"]["mW"]/p["v"]*weight
        if state=="H":c*=math.cos(p["beta"]-p["alpha"])
        channels[f"H{k} W both charges"]=positive_channel(
            2*scalar_vector(M,p[f"mH{k}"],SM["EW"]["mW"],c),
            f"{state}H{k}W")
    lagrangian=reconstruct(p)[0]
    g=trilinears(p,lagrangian)[state]
    for i in (1,2):
        for j in (i,2):
            if j<i:continue
            factor=2 if j!=i else 1
            channels[f"H{i}+ H{j}-"+(" and c.c." if i!=j else "")]=positive_channel(
                factor*scalar_scalar(M,p[f"mH{i}"],p[f"mH{j}"],g[i,j]),
                f"{state}H{i}H{j}"
            )
    missing=[]
    if state=="H" and M>p["ma"]+SM["EW"]["mZ"]:
        missing.append("H -> A Z on-shell, model-matched tree transition NOT included")
    if state=="A" and M>p["mh2"]+SM["EW"]["mZ"]:
        missing.append("A -> H Z on-shell, model-matched tree transition NOT included")
    if state=="H" and M>2*p["ma"]:
        missing.append("H -> A A on-shell, neutral quartic-derived trilinear NOT included")
    base=sum(channels.values())
    if base<=0:raise ArithmeticError("Zero heavy-neutral known partial width")
    bounds={name:width/base for name,width in channels.items()}
    # Positive omitted widths mean every physical BR is <= to this bound,
    # at the declared tree-order and with no significant loop interference
    # in the computed channels. Total positive width is unknown.
    for k in bounds:
        if not 0<=bounds[k]<=1:raise ArithmeticError("Tree partial BR upper bound invalid")
    return {
        "state":state,"mass_GeV":M,
        "channels_tree_GeV":channels,
        "known_tree_disjoint_sum_GeV":base,
        "tree_partial_BR_upper_bound":bounds,
        "tree_mode_largest":max(channels,key=channels.get),
        "on_shell_missing":missing,
        "uncomputed_positive_width_channels":[
            "gg, gamma gamma, Zgamma leading one-loop and higher-order corrections",
            "QCD corrections to quark partial widths and running/scheme uncertainties",
            "off-shell finite daughter / multi-body cascades",
            "model-matched heavy-neutral exotic and interference corrections",
        ],
        "physical_total_width_GeV":None,
        "HiggsTools_observed_exclusion":None,
        "full_Higgs":"UNKNOWN",
    }

def run(source:Path,out:Path):
    if out.exists():raise FileExistsError("Do not overwrite Higgs source receipts")
    data=json.loads(source.read_text())
    if data.get("new_neutrino_family_count")!=64 or len(data.get("families",[]))!=64:
        raise ValueError("Requires all 64 complete source Yukawa cards")
    if data.get("global_acceptance") is not None:
        raise ValueError("Source wrongly promotes model acceptance")
    original={p["scalar_id"]:p for p in data["scalars"]}
    cases=[]
    for f in data["families"]:
        id=f["id"];scalar=original[id]
        inp=f["algebraic_texture_input"]
        if digest(inp)!=f["algebraic_texture_input_sha256"]:
            raise ValueError("Source flavor input SHA mismatch")
        if digest(scalar["scalar_input"])!=f["scalar_sha256"]:
            raise ValueError("Source original scalar SHA mismatch")
        if inp["scalar"]["sha256"]!=f["scalar_sha256"]:
            raise ValueError("New family not bound to scalar")
        n=neutrino_evaluate(inp)
        if n["inverse"]["family_relative_residual"]>2e-9:
            raise ArithmeticError("Neutrino inverse closure broken")
        D=decode(n["D"])
        p=scalar["scalar_input"]["physical"]
        heavy={state:heavy_tree_channels(p,D,state) for state in ("H","A")}
        result={
            "scalar_id":id,"ordering":f["ordering"],"seed":f["seed"],
            "input_sha256":f["algebraic_texture_input_sha256"],
            "heavy_states":heavy,"physical_Higgs":"UNKNOWN",
            "full_neutral_widths":None,"globally_allowed":None,
        }
        cases.append(result)
        if id in (15591,15673,14074) and f["ordering"]=="NO" and f["seed"]==20261111:
            for state in ("H","A"):
                h=heavy[state]
                print("SOURCE_HEAVY_TREE",id,state,
                      "M",h["mass_GeV"],
                      "KNOWN_SUM",h["known_tree_disjoint_sum_GeV"],
                      "TAUTAU_BR_UPPER",h["tree_partial_BR_upper_bound"]["tau tau"],
                      "TOP_BR_UPPER",h["tree_partial_BR_upper_bound"]["t tbar"],
                      "H1W_BR_UPPER",h["tree_partial_BR_upper_bound"]["H1 W both charges"],
                      "MISSING_ONSHELL",len(h["on_shell_missing"]),
                      "FULL_HIGGS_UNKNOWN",flush=True)
    assert len(cases)==64
    summary={}
    for id in sorted(original):
        rows=[z for z in cases if z["scalar_id"]==id]
        summary[str(id)]={
            "number_new_flavor_families":len(rows),
            "H_known_tree_sum_GeV_range":[min(z["heavy_states"]["H"]["known_tree_disjoint_sum_GeV"] for z in rows),
                                            max(z["heavy_states"]["H"]["known_tree_disjoint_sum_GeV"] for z in rows)],
            "A_known_tree_sum_GeV_range":[min(z["heavy_states"]["A"]["known_tree_disjoint_sum_GeV"] for z in rows),
                                            max(z["heavy_states"]["A"]["known_tree_disjoint_sum_GeV"] for z in rows)],
            "H_tautau_tree_BR_upper_max":max(z["heavy_states"]["H"]["tree_partial_BR_upper_bound"]["tau tau"] for z in rows),
            "A_tautau_tree_BR_upper_max":max(z["heavy_states"]["A"]["tree_partial_BR_upper_bound"]["tau tau"] for z in rows),
            "H1W_heavy_tree_BR_upper_max":max(z["heavy_states"]["H"]["tree_partial_BR_upper_bound"]["H1 W both charges"] for z in rows),
            "A1W_heavy_tree_BR_upper_max":max(z["heavy_states"]["A"]["tree_partial_BR_upper_bound"]["H1 W both charges"] for z in rows),
            "at_least_one_open_missing_tree_channel":any(h["on_shell_missing"] for z in rows for h in z["heavy_states"].values()),
            "physical_Higgs":"UNKNOWN",
        }
    output={
        "schema":"zee-64-new-neutrino-family-heavy-H-A-tree-level-partial-width-positive-lower-bound-v1",
        "source_file":source.name,
        "n_families":len(cases),
        "n_source_scalar_spectra":len(original),
        "channel_scope":"Known disjoint on-shell tree two-body with exact native scalar/Yukawa coupling conventions, no full HDECAY/QCD or loop widths",
        "all_theory_errors_uncalibrated":True,
        "HiggsTools_observed_limits_applied":False,
        "full_H_A_widths_established":False,
        "physical_Higgs":"UNKNOWN",
        "global_acceptance":None,
        "scalar_summaries":summary,"cases":cases
    }
    out.write_text(json.dumps(output,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("SOURCE_HEAVY_TREE_ALL_64_DONE",len(cases),"NO_FULL_HIGGS_PASS",flush=True)
    return output

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fresh-json",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    run(a.fresh_json,a.output)

if __name__=="__main__":
    main()
