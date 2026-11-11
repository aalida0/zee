#!/usr/bin/env python3
"""Merge source-matched 16-card AnyHdecay partial channels into 64 native Zee H/A cards.

The transfer is a *mixed-order positive, disjoint channel inventory*, not a
physical width. Do NOT feed derived totals/BRs to HiggsBounds. This is
intentionally useful for estimating which missing contributions may matter
and preparing a later complete-width/observed-search adapter.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path

# Native source channel names versus the frozen AnyHdecay R2HDM reference.
QCD_REPLACE={"bb":"b bbar","cc":"c cbar","ss":"s sbar","tt":"t tbar"}
NEUTRAL_REPLACE={"H":{"WW":"WW","ZZ":"ZZ","HlHl":"h h"},
                 "A":{"ZHl":"h Z"}}
ADDITIONAL={"H":{"gg":"gg","ZA":"A Z (HDECAY reference only)","AA":"A A (HDECAY reference only)"},
            "A":{"gg":"gg","ZHh":"H Z (HDECAY reference only)"}}

def positive(v,label):
    if not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:
        raise ValueError("Invalid native/HDECAY source width "+label)
    return float(v)

def merge_one(tree,reference,state):
    if state not in ("H","A") or tree["state"]!=state:
        raise ValueError("Native H/A state identity mismatch")
    if reference.get("completes_Zee_total_width") is not False:
        raise ValueError("R2HDM reference wrongly declared a full Zee total width")
    if not math.isclose(tree["mass_GeV"],reference["mass_GeV"],rel_tol=1e-12):
        raise ValueError("Matched source H/A mass mismatch")
    channels={k:positive(v,k) for k,v in tree["channels_tree_GeV"].items()}
    if not math.isclose(sum(channels.values()),tree["known_tree_disjoint_sum_GeV"],rel_tol=1e-9,abs_tol=1e-8):
        raise ValueError("Native disjoint tree sum changed")
    h=reference["transferable_partial_widths_GeV"]
    expected=set(QCD_REPLACE)|set(NEUTRAL_REPLACE[state])|set(ADDITIONAL[state])
    if set(h)!=expected:
        raise ValueError("Incomplete or extra AnyHdecay channel keys")
    ratios={}
    replaced={}
    for source,target in {**QCD_REPLACE,**NEUTRAL_REPLACE[state]}.items():
        new=positive(h[source],source)
        old=channels[target]
        replaced[source]={"native_tree_GeV":old,"public_hdecay_GeV":new,
                          "ratio_new_to_tree":new/old if old>0 else None}
        channels[target]=new
    for source,target in ADDITIONAL[state].items():
        new=positive(h[source],source)
        if target in channels:
            raise ValueError("Duplicate source transferred channel "+target)
        channels[target]=new
    # A reference HDECAY neutral transition may be on/off-shell; it is
    # added separately from the tree-native two-body ledger, never silently
    # mixed with any native H/A->other-neutral entry.
    total=math.fsum(channels.values())
    if total<=0 or total<0.1*tree["known_tree_disjoint_sum_GeV"]:
        raise ArithmeticError("Unphysical merged partial sum")
    return {
        "state":state,
        "mass_GeV":tree["mass_GeV"],
        "source_tree_sum_GeV":tree["known_tree_disjoint_sum_GeV"],
        "mixed_order_known_channel_sum_GeV":total,
        "mixed_order_known_Gamma_over_M":total/tree["mass_GeV"],
        "channel_widths_GeV":channels,
        "replaced_channel_audit":replaced,
        "reference_hdecay_R2HDM_total_rejected":reference["source_R2HDM_total_width_GeV_REJECTED_ZEE"],
        "source_uncomputed_on_shell":tree["on_shell_missing"],
        "source_uncomputed_channel_groups":tree["uncomputed_positive_width_channels"],
        "additional_missing_groups":["Complete H/A photon and Zgamma loop widths (including mixed charged state Z current)",
            "Finite-width and genuine three-/four-body scalar cascades",
            "QCD/EW corrections to native charged-W and other tree modes and their uncertainties",
            "Experimental signal acceptance/width-shape validation and complete production"],
        "full_physical_total_width_GeV":None,
        "normalized_physical_branching_fractions":None,
        "HiggsBounds_observed_limit_status":"NOT_EVALUATED",
        "full_Higgs":"UNKNOWN",
    }

def execute(native_path:Path,hdecay_path:Path,out:Path):
    if out.exists():raise FileExistsError("Never overwrite source model bridge")
    n=json.loads(native_path.read_text())
    d=json.loads(hdecay_path.read_text())
    if n.get("n_evaluated")!=64 or n.get("global_acceptance") is not None:
        raise ValueError("Expected unqualified complete 64-native source")
    if d.get("source_n_scalar")!=16 or not d.get("partial_widths_only") or d.get("global_acceptance") is not None:
        raise ValueError("Invalid 16-HDECAY transfer provenance")
    look={int(x["scalar_id"]):x for x in d["cards"]}
    if len(look)!=16:
        raise ValueError("Duplicate scalar in HDECAY reference")
    joined=[]
    for row in n["families"]:
        id=int(row["scalar_id"])
        if id not in look or row["scalar_sha256"]!=look[id]["scalar_sha256"]:
            raise ValueError("Native flavor is not matched to its exact original scalar reference")
        states={s:merge_one(row["heavy_neutral"][s],look[id]["heavy_states"][s],s)
                for s in ("H","A")}
        joined.append({"scalar_id":id,"ordering":row["ordering"],"seed":row["seed"],
                       "scalar_sha256":row["scalar_sha256"],"states":states,
                       "full_physical_Higgs":"UNKNOWN","global_acceptance":None})
    if len(joined)!=64 or len({(x["scalar_id"],x["ordering"],x["seed"]) for x in joined})!=64:
        raise ValueError("Missing or duplicated 64 neutral Zee cases")
    outdata={
        "schema":"zee-16x4-new-H-A-HDECAY-plus-native-width-partial-source-v1",
        "native_sha256":hashlib.sha256(native_path.read_bytes()).hexdigest(),
        "anyhdecay_control_sha256":hashlib.sha256(hdecay_path.read_bytes()).hexdigest(),
        "count":64,"partial_widths_only":True,"full_physical_Higgs":"UNKNOWN",
        "observed_HiggsBounds_run":False,
        "global_acceptance":None,"cases":joined,
    }
    out.write_text(json.dumps(outdata,allow_nan=False,indent=2,sort_keys=True)+"\n")
    for id in (15673,15591,2264):
        x=next((k for k in joined if k["scalar_id"]==id and k["ordering"]=="NO" and k["seed"]==20261111),None)
        if x is not None:
            print("ZEE_HDECAY_MIXED_SCOPE",id,"H_SUM",x["states"]["H"]["mixed_order_known_channel_sum_GeV"],
                  "A_SUM",x["states"]["A"]["mixed_order_known_channel_sum_GeV"],
                  "PHYSICAL_HIGGS_UNKNOWN",flush=True)
    print("ZEE_HDECAY_SOURCE_JOIN_64_PARTIAL",len(joined),"NO_HIGGS_EXCLUSION",flush=True)
    return outdata

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--native",type=Path,required=True)
    a.add_argument("--hdecay",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    x=a.parse_args()
    execute(x.native,x.hdecay,x.output)

if __name__=="__main__":
    main()
