#!/usr/bin/env python3
"""64 Zee family threshold, width floor and NWA/shape materiality registry.

Finite-width flags are computed from the original *exact* source masses,
native two-body charged D4 totals and public HDECAY + Zee neutral known
disjoint positive widths. A small **lower-width** ratio is not a proof of
the physical narrow-width approximation, so the report never sets NWA_PASS.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
from module14.scan import digest
from module14.decays import DecayCalculation
from module2.interface import evaluate as neutrino_evaluate
from module7.d4_inputs import SM
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points

PINNED_HDECAY_SHA="c02622cb7d9eb6bbe74a8e435b5e9f0e85513cd2160cee48376003f5db83b32d"

def finite(v,name):
    x=float(v)
    if not math.isfinite(x) or x<0:raise ValueError("Invalid "+name)
    return x

def diagnostics(p,charge,H,A):
    masses={k:finite(v,k) for k,v in (("H1",p["mH1"]),("H2",p["mH2"]),
                                          ("H",p["mh2"]),("A",p["ma"]))}
    widths={"H1":finite(charge["H1"]["total"]["total_width_GeV"],"H1"),
            "H2":finite(charge["H2"]["total"]["total_width_GeV"],"H2"),
            "H":finite(H["mixed_order_known_channel_sum_GeV"],"H"),
            "A":finite(A["mixed_order_known_channel_sum_GeV"],"A")}
    if min(widths.values())<=0 or min(masses.values())<=0:raise ValueError("No zero widths/masses allowed")
    width_ratios={k:widths[k]/masses[k] for k in widths}
    q={"source_widths_GeV":widths,"source_width_floor_over_mass":width_ratios,
       "charged_full_on_shell_D4_but_offshell_loop_unknown":True,
       "heavy_H_A_full_total_widths_unknown":True,
       "inferred_narrow_width_allowed":None,
       "ttpair_resonance_interference_status":"MISSING_CALCULATION"}
    # distances to known two-body cascade thresholds: negative denotes closed.
    vW=SM["EW"]["mW"];vZ=SM["EW"]["mZ"]
    cases=[]
    cases.append(("H2 -> H1 Z",masses["H2"]-masses["H1"]-vZ,
                  max(widths["H1"],widths["H2"],2.4952)))
    for parent in ("H","A"):
        for daughter in ("H1","H2"):
            cases.append((f"{parent} -> {daughter} W",masses[parent]-masses[daughter]-vW,
                          max(widths[parent],widths[daughter],2.085)))
    q["thresholds"]={s:{
        "gap_GeV":gap,
        "gap_over_max_parent_daughter_width":gap/w,
        "classification":("CLOSED" if gap<=0 else
           "OPEN_FAR_ABOVE_THRESHOLD_5WIDTHS" if gap>=5*w else
           "OPEN_NEAR_THRESHOLD_NEEDS_OFFSHELL_CHECK")
       } for s,gap,w in cases}
    q["known_width_floor_exceeds_10pct"]={k:width_ratios[k]>0.10 for k in ("H","A")}
    q["charged_D4_width_over_10pct"]={k:width_ratios[k]>0.10 for k in ("H1","H2")}
    q["all_open_H1W_and_H2H1Z_far_five_widths"]=all(
          x["classification"]!="OPEN_NEAR_THRESHOLD_NEEDS_OFFSHELL_CHECK"
          for x in q["thresholds"].values())
    return q

def run(source:Path,widths:Path,out:Path):
    if out.exists():raise FileExistsError("Refuse overwrite source model NWA receipts")
    if hashlib.sha256(widths.read_bytes()).hexdigest()!=PINNED_HDECAY_SHA:
        raise ValueError("Original 64 HDECAY Zee partial-width source not pinned")
    s=json.loads(source.read_text());w=json.loads(widths.read_text())
    if (s.get("new_neutrino_family_count")!=64 or w.get("count")!=64
        or s.get("global_acceptance") is not None or w.get("global_acceptance") is not None):
        raise ValueError("Requires full 64 but never accepted Zee parameter points")
    original={r["id"]:r for r in source_points()}
    smap={r["scalar_id"]:r for r in s["scalars"]}
    zmap={(r["scalar_id"],r["ordering"],r["seed"]):r for r in w["cases"]}
    if len(zmap)!=64 or set(smap)!=set(original):
        raise ValueError("Source scalar identity not complete")
    records=[]
    for f in s["families"]:
        sid=f["id"];key=(sid,f["ordering"],f["seed"])
        if (f["scalar_sha256"]!=original[sid]["scalar_sha256"] or
            zmap[key]["scalar_sha256"]!=f["scalar_sha256"]):
            raise ValueError("Native scalar source hash mismatch")
        scalar=smap[sid]["scalar_input"]
        if digest(scalar)!=f["scalar_sha256"]:
            raise ValueError("Mismatched original physical source")
        n=neutrino_evaluate(f["algebraic_texture_input"])
        if n["inverse"]["family_relative_residual"]>=2e-9:
            raise ValueError("Neutrino inverse lost")
        family={k:n[k] for k in ("F","D","Ye","Ye2","Mnu")}
        family.update(input=f["algebraic_texture_input"],input_sha256=f["algebraic_texture_input_sha256"])
        charged=DecayCalculation(scalar,family).evaluate(family)
        if charged["status"]!="PASS":raise ValueError("Charged D4 total width was not completed")
        states=zmap[key]["states"]
        q=diagnostics(scalar["physical"],charged["mothers"],states["H"],states["A"])
        records.append({"scalar_id":sid,"ordering":key[1],"seed":key[2],
                        "metrics":q,"actual_resonance_shape_validation":None,
                        "full_Higgs":"UNKNOWN","global_acceptance":None})
        if sid in (15673,15591,2264) and key[1]=="NO" and key[2]==20261111:
            print("ZEE_WIDTH_THRESHOLD",sid,
              "RATIOS",q["source_width_floor_over_mass"],
              "CASCADE_GAP_OVER_WIDTH",q["thresholds"]["H2 -> H1 Z"]["gap_over_max_parent_daughter_width"],
              "FAR_5_WIDTHS",q["all_open_H1W_and_H2H1Z_far_five_widths"],
              "FULL_SHAPE_UNKNOWN",flush=True)
    if len(records)!=64:raise ValueError("Incomplete 64-case threshold inventory")
    report={"schema":"zee-64-source-width-ratio-threshold-materiality-not-NWA-certification-v1",
            "n_case":len(records),
            "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
            "hdecay_source_sha256":PINNED_HDECAY_SHA,
            "n_charged_known_over_10pct":sum(any(q["metrics"]["charged_D4_width_over_10pct"].values()) for q in records),
            "n_heavy_known_floor_over_10pct":sum(any(q["metrics"]["known_width_floor_exceeds_10pct"].values()) for q in records),
            "n_near_two_body_threshold":sum(not q["metrics"]["all_open_H1W_and_H2H1Z_far_five_widths"] for q in records),
            "no_certified_NWA_pass":True,
            "global_acceptance":None,
            "cases":records}
    out.write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+"\n")
    print("ZEE_WIDTH_MATERIALITY_64_FINISHED",len(records),
       "N_NEAR_THRESH",report["n_near_two_body_threshold"],"PHYSICAL_MODEL_UNKNOWN",flush=True)
    return report

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source",type=Path,required=True)
    a.add_argument("--widths",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    x=a.parse_args()
    run(x.source,x.widths,x.output)

if __name__=="__main__":main()
