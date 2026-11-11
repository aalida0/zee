#!/usr/bin/env python3
"""Source-pinned HEPfit NNLO Type-II charged Higgs *matching* probe.

All 16 Zee fixed scalar cards, both charged eigenstates, shared running
top mass at 160 GeV; independent source HEPfit GPL matching evaluated
as ephemeral compiled C++ oracle. Does NOT convert NNLO Wilson output
into a fully updated 2026 B->Xs gamma rate or exclusion.
"""
from __future__ import annotations
import argparse,json,math,subprocess,hashlib
from pathlib import Path

from scripts.zee_module5_bmu_nlo import matching as bmu
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points
MATCHING_CARD=Path(__file__).resolve().parents[3]/"module14/conditional_scan/matching_card.json"

def oracle(exe:Path,tanb:float,mt:float,mass:float,mu:float):
    p=subprocess.run([str(exe.resolve()),f"{tanb:.17g}",f"{mt:.17g}",
                      f"{mass:.17g}",f"{mu:.17g}"],
                      capture_output=True,text=True,timeout=60,check=True)
    rows={}
    for line in p.stdout.splitlines():
        vals=line.split()
        if len(vals)!=3:raise ValueError("Source HEPfit C++ non-machine-readable output")
        order,i=int(vals[0]),int(vals[1]);v=float(vals[2])
        if not math.isfinite(v):raise ArithmeticError("Nonfinite upstream WC")
        if (order,i) in rows:raise ArithmeticError("Duplicate Wilson")
        rows[(order,i)]=v
    if set(rows)!={(a,b) for a in range(3) for b in range(8)}:
        raise ArithmeticError("Full 3-order 8-operator HEPfit source output missing")
    return {str(order):{f"C{n+1}":rows[(order,n)] for n in range(8)}
            for order in range(3)}

def run(binary:Path,output:Path):
    if output.exists():raise FileExistsError("Refuse overwriting source output")
    card=json.loads(MATCHING_CARD.read_text())
    mu=float(card["matching_scale_GeV"])
    mt=float(card["mt_MSbar_GeV"])
    if mu!=160:raise ValueError("Matching scale changed")
    out=[]
    for p in sorted(source_points(),key=lambda x:x["id"]):
        ph=p["input_card"]["physical"]
        masses=(ph["mH1"],ph["mH2"])
        tanb=math.tan(ph["beta"]);gamma=ph["gamma"]
        weights=(math.cos(gamma)**2,math.sin(gamma)**2)
        sources=[]
        for mass in masses:
            from_hepfit=oracle(binary,tanb,mt,mass,mu)
            native=bmu(mass,tanb,mt,mu)
            lo=from_hepfit["0"];nlo=from_hepfit["1"];nnlo=from_hepfit["2"]
            compare={
                "LO_C7_upstream":lo["C7"],"LO_C8_upstream":lo["C8"],
                "LO_C7_BMU":native["C7_LO"],"LO_C8_BMU":native["C8_LO"],
                "NLO_C4_upstream":nlo["C4"],"NLO_C4_BMU":native["C4_NLO_raw"],
                "NLO_C7_upstream_effective":nlo["C7"],
                "NLO_C8_upstream_effective":nlo["C8"],
                "NLO_C7_upstream_ordinary_candidate":nlo["C7"]+4/9*nlo["C4"],
                "NLO_C8_upstream_ordinary_candidate":nlo["C8"]+1/6*nlo["C4"],
                "NLO_C7_BMU":native["C7_NLO_raw"],
                "NLO_C8_BMU":native["C8_NLO_raw"],
                "NNLO_matching_C3_to_C8_source":{k:v for k,v in nnlo.items() if k in ("C3","C4","C5","C6","C7","C8")},
            }
            sources.append({"charged_mass_GeV":mass,"matched_Hepfit":from_hepfit,"matched_BMU":native,"comparisons":compare})
        mixed={}
        for ord in ("0","1","2"):
            mixed[ord]={k:math.fsum(w*e["matched_Hepfit"][ord][k]
                                    for w,e in zip(weights,sources))
                        for k in sources[0]["matched_Hepfit"][ord]}
        id=p["id"]
        val={
            "scalar_id":id,"scalar_sha256":p["scalar_sha256"],
            "tanbeta":tanb,"gamma":gamma,"weights":weights,
            "source_charged_mass_GeV":masses,
            "source_Hepfit_per_charged_state":sources,
            "mixed_three_orders":mixed,
            "matching_only_includes_no_low_scale_NNLO_evolution":True,
            "physical_B":"UNKNOWN","global_acceptance":None
        }
        out.append(val)
        print("HEPFIT_UPSTREAM_NNLO_MATCHING",id,
              "MASS",masses,"LO7",mixed["0"]["C7"],
              "NLO7",mixed["1"]["C7"],"NNLO7",mixed["2"]["C7"],
              "NNLO8",mixed["2"]["C8"],
              "STATE1_LO7_DIFF",sources[0]["comparisons"]["LO_C7_upstream"]-sources[0]["comparisons"]["LO_C7_BMU"],
              "STATE1_NLO7_EFF_DIFF",sources[0]["comparisons"]["NLO_C7_upstream_ordinary_candidate"]-sources[0]["comparisons"]["NLO_C7_BMU"],flush=True)
    payload={
        "schema":"zee-16-source-certified-two-charged-hepfit-independent-three-loop-B-match-v1",
        "HEPfit_source_commit":"add26f5ac16cec688021d95226ece6397de29e5e",
        "HEPfit_source_blob":"8029be52c3e2f83490dfe3199f80e5db484dd23b",
        "NLO_BMU_source":"hep-ph/9904413 independent mpmath",
        "upstream_license":"HEPfit is GPL-3.0-or-later; isolated downloaded source compiled only in CI",
        "matching_scale_GeV":mu,"matching_top_mass_GeV":mt,
        "source_wilson_basis":"HEPfit GeneralTHDMMatching/THDMMatching Misiak Q1-Q8, note effective C7,C8 vs ordinary BMU require validation",
        "n_fixed_scalar_spectra":len(out),
        "cases":out,
        "NNLO_full_rate_computed":False,
        "physical_B":"UNKNOWN","global_acceptance":None,
    }
    output.write_text(json.dumps(payload,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("HEPFIT_UPSTREAM_NNLO_MATCHING_ALL_DONE",len(out),"FULL_RATE_NOT_DONE",flush=True)
    return payload

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--binary",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    run(a.binary,a.output)

if __name__=="__main__":main()
