#!/usr/bin/env python3
"""General Zee H/A -> gamma gamma at exact leading one loop on all 64 families.

Reuses *unchanged* signed source-validated analytic spin-0,1/2,1 kernels,
native SARAH-matched trilinears, Zee charged 2x2 mixing and general complex
lepton Yukawas; explicitly rejects incorrect A diagonal charged couplings.
Adding these positive partial widths still does not certify a full H/A total.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np

from module14.scan import digest
from module2.interface import evaluate as neutrino_evaluate,decode
from module3.core import vertices
from module1.scalar_constraints import reconstruct
from module4.couplings import quarks,trilinears
from module7.d4_inputs import SM
from research.full_constraints.higgs.diphoton import amplitude,ALPHA_TREE
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points

ORIGINAL_HDECAY_64_SHA="c02622cb7d9eb6bbe74a8e435b5e9f0e85513cd2160cee48376003f5db83b32d"

def heavy_photons(p,D,state):
    if state not in ("H","A"):raise ValueError("Only heavy CP-even or CP-odd neutral")
    mass=float(p["mh2" if state=="H" else "ma"])
    lepton_masses=np.asarray(SM["lepton_masses"],dtype=float)
    c=vertices(D,p,lepton_masses)[state][0]
    coeff={f:quarks(p["v"],"top" if f in ("u","c","t") else "bottom",p)[state]
           for f in ("u","c","t","d","s","b")}
    coeff.update(zip(("e","mu","tau"),np.diag(c)*p["v"]/lepton_masses))
    potential=reconstruct(p)[0]
    g=trilinears(p,potential)[state][1:,1:]
    if np.max(np.abs(g-g.conj().T))>1e-10:
        raise ValueError("Charged trilinear source not Hermitian")
    if state=="A" and np.max(np.abs(np.diag(g)))>1e-10:
        raise ValueError("CP-odd physical charged diagonal trilinear source violated")
    charged=([(p[f"mH{i+1}"],g[i,i].real,1) for i in range(2)] if state=="H" else [])
    kv=math.sin(p["beta"]-p["alpha"]) if state=="H" else 0.0
    val=amplitude(mass,kv,coeff,charged=charged,v=p["v"],alpha=ALPHA_TREE)
    result=float(val["width_GeV"])
    if not math.isfinite(result) or result<0:
        raise ValueError("Invalid heavy neutral photon partial width")
    return {"state":state,"mass_GeV":mass,"width_gamma_gamma_GeV":result,
            "even_amplitude":{"real":float(val["even"].real),"imag":float(val["even"].imag)},
            "odd_amplitude":{"real":float(val["odd"].real),"imag":float(val["odd"].imag)},
            "g_charged_diagonal_GeV":[float(g[i,i].real) for i in (0,1)],
            "charged_two_state_loop_included":state=="H",
            "general_complex_lepton_Yukawa_included":True,
            "Zgamma_model_specific_incomplete":True,
            "same_tree_input_alpha_em":ALPHA_TREE}

def execute(source:Path,old_widths:Path,out:Path):
    if out.exists():raise FileExistsError("Do not overwrite native model source")
    if hashlib.sha256(old_widths.read_bytes()).hexdigest()!=ORIGINAL_HDECAY_64_SHA:
        raise ValueError("Expected source-locked original 64 HDECAY/native width cards")
    s=json.loads(source.read_text())
    w=json.loads(old_widths.read_text())
    if (s.get("new_neutrino_family_count")!=64 or len(s.get("families",[]))!=64
        or w.get("count")!=64 or s.get("global_acceptance") is not None
        or w.get("global_acceptance") is not None):
        raise ValueError("Require exact frozen 64 source families")
    original={x["id"]:x for x in source_points()}
    smap={x["scalar_id"]:x for x in s["scalars"]}
    previous={(x["scalar_id"],x["ordering"],x["seed"]):x for x in w["cases"]}
    if len(previous)!=64 or set(smap)!=set(original):
        raise ValueError("Original scalar dataset/width join incomplete")
    cases=[]
    for family in s["families"]:
        sid=family["id"];key=(sid,family["ordering"],family["seed"])
        if family["scalar_sha256"]!=original[sid]["scalar_sha256"] or previous[key]["scalar_sha256"]!=family["scalar_sha256"]:
            raise ValueError("Native scalar card changes or HDECAY inconsistent")
        if digest(smap[sid]["scalar_input"])!=family["scalar_sha256"]:
            raise ValueError("Source scalar hash changed")
        n=neutrino_evaluate(family["algebraic_texture_input"])
        if n["inverse"]["family_relative_residual"]>=2e-9:
            raise ValueError("Native source neutrino inverse lost")
        D=decode(n["D"])
        p=smap[sid]["scalar_input"]["physical"]
        states={}
        for name in ("H","A"):
            actual=heavy_photons(p,D,name)
            floor=previous[key]["states"][name]["mixed_order_known_channel_sum_GeV"]
            ratio=actual["width_gamma_gamma_GeV"]/floor
            actual["known_HDECAY_tree_channel_sum_GeV"]=floor
            actual["Gamma_gammagamma_over_known_sum"]=ratio
            actual["total_physical_width_GeV"]=None
            actual["full_Higgs_exclusion"]=None
            states[name]=actual
        cases.append({"scalar_id":sid,"ordering":key[1],"seed":key[2],
                      "states":states,"full_Higgs":"UNKNOWN","global_acceptance":None})
        if sid in (15673,15591,2264) and key[1]=="NO" and key[2]==20261111:
            print("HEAVY_ZEE_GAMMA_GAMMA",sid,
                  "H_Gamma",states["H"]["width_gamma_gamma_GeV"],
                  "A_Gamma",states["A"]["width_gamma_gamma_GeV"],
                  "H_fraction",states["H"]["Gamma_gammagamma_over_known_sum"],
                  "A_fraction",states["A"]["Gamma_gammagamma_over_known_sum"],
                  "FULL_MODEL_UNKNOWN",flush=True)
    if len(cases)!=64:raise ValueError("Missing heavy photons for source families")
    ratios=[a["Gamma_gammagamma_over_known_sum"] for x in cases for a in x["states"].values()]
    report={
        "schema":"zee-64-heavy-H-A-source-exact-leading-one-loop-gamma-gamma-v1",
        "number_families":len(cases),
        "source_64_neutrino_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "source_64_HDECAY_sha256":ORIGINAL_HDECAY_64_SHA,
        "max_Gamma_gammagamma_over_known_sum":max(ratios),
        "loops":"native 2 state charged-scalar plus W plus exact complex lepton and quark one-loop amplitudes",
        "complete_Zee_H_A_total_widths":False,"full_Higgs":"UNKNOWN",
        "global_acceptance":None,"cases":cases}
    out.write_text(json.dumps(report,allow_nan=False,indent=2,sort_keys=True)+"\n")
    print("HEAVY_ZEE_GAMMA64_COMPLETE",len(cases),
          "MAX_RELATIVE_SOURCE_GAMMA",max(ratios),
          "NOT_FULL_MODEL",flush=True)
    return report

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source",type=Path,required=True)
    a.add_argument("--widths",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    x=a.parse_args()
    execute(x.source,x.widths,x.output)

if __name__=="__main__":main()
