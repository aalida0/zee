#!/usr/bin/env python3
"""F10: re-evaluate actual Paper1 scan six scalar points in the pinned
historical full inclusive SuperIso source and SAME kernel TypeII(670).

This is a NEW physically reconstructed B4 scalar point for each row, not
an unphysical gamma deformation, but the flavor observable is LEGACY.
No modern 2026 NNLO Zee branching ratio/CL/allowed conclusion. No pb.
All inputs/provenance are independently checked against original F6 SHA.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys,traceback
from pathlib import Path
from zee_gateF7_309_2026_bsgamma_tension_sensitivity import (
    ROOT,load_f6,digest,load,writejson,
)
from zee_gateF8_309_670TypeII_same_legacy_kernel_and_mixing import (
    archive_bin,call_source,near,REFERENCE_MASS
)
from zee_gateF6_309_full_legacy_bsgamma import STATUS as F6_STATUS

STATUS="F10_SIX_NEW_B4_ZEE_P1_TWO_STATE_SUPERISO_LEGACY_COMPARATOR_NOT_EXCLUSION"
SCALAR="selected_scalar_spectra_NOT_ALLOWED.csv"
RANKED="ranked_florentino_injection_NOT_ALLOWED.csv"
MISSING=(
    "modern 2026 scheme-matched complete two-charged NNLO B->Xs gamma rate",
    "correlated theory/systematic uncertainties and experimental CL",
    "complete neutrino + LFV likelihood, scalar running and global vacuum",
    "complete HiggsTools exclusion, full decay widths, pp production and R_tbZ",
)
def discover_f6(work):
    candidates=[]
    for f in sorted(work.glob("**/F6_309_legacy_two_state_BtoXsgamma_NOT_2026_EXCLUSION.jsonl")):
        try:
            src=f.parent
            # independent strict F7 original 309 provenance closure
            original,proof=load_f6(src)
            exe,pin=archive_bin(src)
            candidates.append((src,original,proof,exe,pin))
        except (KeyError,ValueError,FileNotFoundError,OSError):
            continue
    if not candidates:
        raise FileNotFoundError("No source-verified original F6 archive and pinned binary in work. "
          "F6 binary cannot be substituted with reconstructed source or a new vendor.")
    sha={digest(x[3]) for x in candidates}
    if len(sha)!=1:
        raise ValueError("Multiple different F6 binaries; specify --f6-dir")
    return candidates[0]
def read_scan(folder):
    folder=Path(folder).resolve()
    source=load(folder/"summary.json")
    if (source.get("status")!=
         "PAPER1_ACTUAL_SCALAR_NEUTRINO_PARTIAL_LFV_CASCADE_PILOT_NOT_ALLOWED"
       or source.get("fully_Zee_allowed_or_excluded") is not None
       if "fully_Zee_allowed_or_excluded" in source else False):
        # Source summary has nullable 'modern_model_complete_constraints_passed'
        raise ValueError("Original Paper1 numerical scan status unexpected")
    if source.get("modern_model_complete_constraints_passed") is not None:
        raise ValueError("Cannot reinterpret full-model acceptance")
    man=load(folder/"manifest.json")
    if (man.get("status")!=source["status"] or
        man.get("summary_SHA256")!=digest(folder/"summary.json")):
        raise ValueError("Source Paper1 summary/manifest mismatch")
    for fn in (SCALAR,RANKED):
        if (source.get("candidate_file_SHA256",{}).get(fn)!=digest(folder/fn)):
            raise ValueError("Original Paper1 SHA/CSV mismatch: "+fn)
    with (folder/SCALAR).open(newline="") as f:
        s=list(csv.DictReader(f))
    with (folder/RANKED).open(newline="") as f:
        r=list(csv.DictReader(f))
    if (len(s)!=6 or len(r)!=6 or
        {x["id"] for x in s}!={x["candidate_id"] for x in r} or
        len({x["id"] for x in s})!=6):
        raise ValueError("Expected exact original six joined scalar points")
    for x in s:
        if x.get("candidate_status")!="SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED":
            raise ValueError("Untrusted B4 scalar status")
    joined={x["candidate_id"]:x for x in r}
    for x in s:
        d=joined[x["id"]]
        for l,k in (("mH1","mH1_GeV"),("mH2","mH2_GeV"),("gamma","gamma")):
            near(x[l],d[k],x["id"]+" "+l,rtol=5e-11,atol=1e-8)
        if d.get("fully_allowed","") not in ("","None","null"):
            raise ValueError("Existing data asserts unvalidated full-model allowed status")
        p=folder/("point_"+str(s.index(x)+1).zfill(2)+"_NOT_ALLOWED.json")
        record=load(p)
        if (record["scalar"]["id"]!=x["id"] or
            record.get("full_Zee_allowed_or_excluded") is not None or
            record["flavor"].get("model_allowed_or_excluded") is not None):
            raise ValueError("Paper1 checkpoint pairing/fail-closed violated")
    return s,joined,{
        "scan_summary_SHA256":digest(folder/"summary.json"),
        "scan_manifest_SHA256":digest(folder/"manifest.json"),
        "selected_scalar_SHA256":digest(folder/SCALAR),
        "ranked_flavor_SHA256":digest(folder/RANKED),
    }

def evaluate(scalars,joined,exe,sm,source_br=call_source):
    result=[]
    for p in scalars:
        name=p["id"]
        m1,m2,g,t=(float(p[k]) for k in ("mH1","mH2","gamma","tanbeta"))
        if not (200<=m1<m2<=10000 and 0<g<math.pi/2 and 0.25<=t<=100):
            raise ValueError("Invalid full physical B4 scalar for "+name)
        old=source_br(exe,m1,m2,g,t)
        ref=source_br(exe,REFERENCE_MASS,REFERENCE_MASS,0.,t)
        if not (sm<ref<.01 and sm<old<.01):
            raise ValueError("Invalid F6 historical full legacy BR ordering")
        den=ref-sm
        ratio=(old-sm)/den
        r=joined[name]
        result.append({
          "candidate_id":name,"mH1_GeV":m1,"mH2_GeV":m2,
          "gamma":g,"tanbeta":t,
          "legacy_SuperIso_full_Zee_BR_Egamma1p6_NOT_2026":old,
          "legacy_same_kernel_SM_BR":sm,
          "legacy_TypeII_mH670_same_tanbeta_BR":ref,
          "Zee_to_TypeII670_legacy_NP_shift_ratio_NOT_CL":ratio,
          "B4_original_nonleptonic_proxy_NOT_pb":float(r[
             "nonleptonic_cascade_proxy_NOT_pb"]),
          "P1_general_lepton_included_cascade_proxy_NOT_pb":float(r[
             "flavor_corrected_included_cascade_proxy_NOT_pb"]),
          "cascade_width_retention":float(r[
             "flavor_corrected_included_cascade_proxy_NOT_pb"])/float(r[
             "nonleptonic_cascade_proxy_NOT_pb"]),
          "partial_LFV_max_ratio_NOT_PHYSICAL_CL":float(r[
             "partial_LFV_max_ratio_NOT_CL"]),
          "physical_full_Zee_allowed_or_excluded":None,
          "modern_matched_2026_two_state_Bsgamma_available":False,
          "hadronic_signal_rate_pb":None,
          "status":STATUS,
        })
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scan-dir",type=Path,required=True)
    p.add_argument("--f6-dir",type=Path)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(argv)
    out=a.output_dir.resolve()
    if not ROOT.resolve().is_relative_to(Path("/home")) or not out.is_relative_to(ROOT/"work"):
        p.error("Run original source in /home, store new outputs under work only")
    if out.exists():p.error("Refuse overwrite")
    try:
        six,flavor,pr=read_scan(a.scan_dir)
        if a.f6_dir is None:
            f6,orig,source,exe,pin=discover_f6(ROOT/"work")
        else:
            f6=a.f6_dir.resolve()
            orig,source=load_f6(f6)
            exe,pin=archive_bin(f6)
        if len(orig)!=309:raise ValueError("F6 source 309 cohort not validated")
        f6sum=load(f6/"summary.json")
        if f6sum["status"]!=F6_STATUS:
            raise ValueError("F6 status corrupted")
        sm=float(f6sum["legacy_SM_BR"])
        # Equal-mass charged doublet sum rule in source engine.
        z0=call_source(exe,REFERENCE_MASS,REFERENCE_MASS,0.,float(six[0]["tanbeta"]))
        zg=call_source(exe,REFERENCE_MASS,REFERENCE_MASS,.8,float(six[0]["tanbeta"]))
        near(z0,zg,"TypeII equal-mass gamma control",rtol=2e-8,atol=2e-12)
        rows=evaluate(six,flavor,exe,sm)
        out.mkdir(parents=True,exist_ok=False)
        f=out/"F10_six_full_legacy_Bsgamma_same_kernel_NOT_EXCLUSION.csv"
        with f.open("w",newline="") as stream:
            w=csv.DictWriter(stream,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
        prov={
            **pr,**pin,
            "F6_summary_SHA256":digest(f6/"summary.json"),
            "F6_manifest_SHA256":digest(f6/"manifest.json"),
            "F10_script_SHA256":digest(Path(__file__)),
            "original_F6_dir":str(f6),
        }
        ratios=sorted(x["Zee_to_TypeII670_legacy_NP_shift_ratio_NOT_CL"]
                    for x in rows)
        summary={
            "status":STATUS,"evaluated_new_P1_scalar_points":len(rows),
            "legacy_ratio_min_median_max":[ratios[0],sum(ratios[2:4])/2,ratios[-1]],
            "legacy_ratio_above_TypeII670_comparator_NOT_excluded":sum(v>1 for v in ratios),
            "same_vendor_equal_mass_control_pass":True,
            "modern_2026_Zee_BtoXsGamma_likelihood_completed":False,
            "all_constraints_completed":False,
            "full_Zee_model_allowed_or_excluded":None,
            "paper1_GO_or_NOGO":None,
            "missing_critical_physics":MISSING,
            "source":prov,
            "CSV_SHA256":digest(f),
        }
        writejson(out/"summary.json",summary)
        writejson(out/"manifest.json",{
            "status":STATUS,"summary_SHA256":digest(out/"summary.json"),
            "source":prov})
        for x in rows:
            print("F10_SIX",x["candidate_id"],
                "R_legacy_670",format(x[
                   "Zee_to_TypeII670_legacy_NP_shift_ratio_NOT_CL"],".8g"),
                "proxy",format(x[
                   "P1_general_lepton_included_cascade_proxy_NOT_pb"],".7g"),
                "NOT_EXCLUSION",flush=True)
        print("F10_STATUS",STATUS,"N",len(rows),
              "MODERN_CL",None,flush=True)
        print("F10_SUMMARY",out/"summary.json",flush=True)
        return 0
    except Exception as e:
        print("F10_FAIL_CLOSED",repr(e),file=sys.stderr,flush=True)
        traceback.print_exc()
        return 1

if __name__=="__main__":raise SystemExit(main())
