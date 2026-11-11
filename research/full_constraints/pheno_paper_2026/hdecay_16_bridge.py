#!/usr/bin/env python3
"""All-16 original Zee scalar cards: portable AnyHdecay/HDECAY R2HDM *control*.

Reuse HDECAY's validated transferable quark-QCD, gluonic, neutral-vector and
neutral-doublet scalar partial widths only. The ordinary 2HDM charged scalar
is an auxiliary curvature parameter, never a Zee physical eigenstate.
Never transfer HDECAY lepton, charged-Higgs, photon, or *total* widths to Zee.
"""
from __future__ import annotations
import argparse,hashlib,json,math,subprocess
from pathlib import Path
from module7.d4_inputs import SM
from module7.d4_tree_kernels import scalar_vector,scalar_scalar
from research.full_constraints.higgs.decays_bridge import neutral_hhh
from research.full_constraints.higgs.decays_bridge import read_output
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points

def finite(v,label):
    val=float(v)
    if not math.isfinite(val) or val<0:raise ValueError("Invalid "+label)
    return val

def auxiliary_doublet_charged_mass(p):
    g=float(p["gamma"])
    h1=float(p["mH1"]);h2=float(p["mH2"])
    m2=math.cos(g)**2*h1**2+math.sin(g)**2*h2**2
    if not math.isfinite(m2) or m2<=0:raise ValueError("Bad Zee charged doublet curvature")
    return math.sqrt(m2)

def driver_arguments(p):
    if p["mh1"]!=125.0:raise ValueError("Frozen source scalar h125 mass mismatch")
    return [math.tan(p["beta"]),p["m12sq"],p["ma"],
            auxiliary_doublet_charged_mass(p),p["mh2"],p["mh1"],
            p["alpha"]+math.pi/2,1]

def extract(raw,p):
    """Reject any attempt to promote R2HDM total or charged/leptonic BRs."""
    result={}
    for state,key,mass in (("H","Hh",p["mh2"]),("A","A",p["ma"])):
        total=finite(raw["w_"+key],key+" reference total")
        if total<=0:raise ValueError("Empty HDECAY R2HDM reference width")
        brsum=math.fsum(finite(v,key+" BR") for k,v in raw.items() if k.startswith("b_"+key+"_"))
        if not math.isclose(brsum,1.,abs_tol=5e-9):
            raise ValueError("HDECAY reference BR bookkeeping invalid")
        names=["bb","ss","cc","tt","gg"]+(["WW","ZZ","HlHl","ZA","AA"] if state=="H" else ["ZHl","ZHh"])
        channels={name:finite(total*raw["b_"+key+"_"+name],name) for name in names}
        if state=="H":
            reference_hhh=channels["HlHl"]
            independent_hhh=scalar_scalar(mass,p["mh1"],p["mh1"],neutral_hhh(p))/2
            if not math.isclose(reference_hhh,independent_hhh,rel_tol=5e-7,abs_tol=1e-9):
                raise ValueError("HDECAY H->hh does not match Zee neutral potential")
            for vector in ("WW","ZZ"):
                smwidth=finite(raw["SM_w_H"]*raw["SM_b_H_"+vector],vector+" SM")
                source=channels[vector]
                target=math.sin(p["beta"]-p["alpha"])**2
                if smwidth>0 and not math.isclose(source/smwidth,target,rel_tol=1e-6,abs_tol=1e-9):
                    raise ValueError("HDECAY H->"+vector+" source coupling mismatch")
        else:
            reference_hz=channels["ZHl"]
            independent_hz=scalar_vector(mass,p["mh1"],SM["EW"]["mZ"],
                    SM["EW"]["mZ"]/p["v"]*math.sin(p["beta"]-p["alpha"]))
            if not math.isclose(reference_hz,independent_hz,rel_tol=5e-7,abs_tol=1e-9):
                raise ValueError("HDECAY A->hZ does not match Zee neutral gauge current")
        result[state]={
            "mass_GeV":mass,
            "transferable_partial_widths_GeV":channels,
            "source_R2HDM_total_width_GeV_REJECTED_ZEE":total,
            "source_R2HDM_BRs_sum":brsum,
            "nontransferable_groups":["charged_scalar_loop_gammaZgamma",
                "single_R2HDM_Hcharged_or_W_cascades","TypeII_lepton_widths",
                "source_total_width_and_all_R2HDM_branching_fractions"],
            "completes_Zee_total_width":False,
        }
    return result

def run(driver:Path,out:Path):
    if out.exists():raise FileExistsError("No overwrites of source partial-width evidence")
    if not driver.is_file():raise FileNotFoundError("Built AnyHdecay reference driver is missing")
    root=out.parent
    points=source_points()
    if len(points)!=16 or len({p["id"] for p in points})!=16:
        raise ValueError("Source-specified 16 scalar cards not complete or unique")
    rows=[]
    for point in points:
        p=point["input_card"]["physical"]
        rid=int(point["id"])
        args=[format(float(x),".17g") for x in driver_arguments(p)]
        res=subprocess.run([str(driver),*args],text=True,capture_output=True,check=True,timeout=150)
        outfile=root/("hdecay_control_"+str(rid)+".txt")
        if outfile.exists():raise FileExistsError(outfile)
        outfile.write_text(res.stdout)
        values=read_output(outfile)
        source=extract(values,p)
        rows.append({
            "scalar_id":rid,
            "scalar_sha256":point.get("scalar_sha256"),
            "HDECAY_R2HDM_argv":args,
            "raw_hdecay_stdout_sha256":hashlib.sha256(res.stdout.encode()).hexdigest(),
            "heavy_states":source,
            "H_A_Zee_physical_widths_complete":False,
            "HiggsBounds_observed_limits_applied":False,
        })
        print("HDECAY_ZEE_16_SCALAR_REFERENCE",rid,
              "H_qqgg_partial_GeV",sum(source["H"]["transferable_partial_widths_GeV"][k] for k in ("tt","bb","cc","ss","gg")),
              "A_qqgg_partial_GeV",sum(source["A"]["transferable_partial_widths_GeV"][k] for k in ("tt","bb","cc","ss","gg")),
              "PHYSICAL_HIGGS_UNKNOWN",flush=True)
    output={
        "schema":"zee-2026-hdecay-6.60-16-scalar-quark-QCD-neutral-transfer-only",
        "source":"AnyHdecay 1.1.0 HDECAY 6.60 pinned source; auxiliary R2HDM curvature charged mass",
        "source_n_scalar":16,
        "driver_sha256":hashlib.sha256(driver.read_bytes()).hexdigest(),
        "partial_widths_only":True,
        "H_A_full_total_width_GeV":None,
        "HiggsBounds_exclusion":None,
        "global_acceptance":None,
        "cards":rows,
    }
    out.write_text(json.dumps(output,sort_keys=True,indent=2,allow_nan=False)+"\n")
    return output

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--driver",type=Path,required=True)
    a.add_argument("--output",type=Path,required=True)
    x=a.parse_args()
    run(x.driver,x.output)

if __name__=="__main__":main()
