#!/usr/bin/env python3
"""F3: real source-locked NLO C3...C8 low-Wilson audit, 27 Zee + 64 TypeII.

This actually calls SuperIso C_calculator_base1, not WCxf C4_bs, and
reports independent EOS NLO rate response as DIAGNOSTIC. It does NOT
claim a validated physical Zee BR, paper-level NLO matching, or a 95%CL.
Before any rate interpretation compare the low coefficients against
the independent wilson RG and EOS low-SM conventions. Fail CLOSED on
source, matching or primary-rate provenance disagreement. Record all
residuals, including the previously omitted C3-C6 contribution.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import re
import statistics
import subprocess
import sys
import traceback
from pathlib import Path

from gateA1r_run_br_pilot import check_superiso_source,compile_pilot
from zee_gateE4b_2026_observable_validation import read_source_e4a
from zee_gateF1_peerreviewed_flavio_27_observable import sha, validate_e4a_typeii
from zee_gateF2_eos_flavio_nlo_27_validation import (
    RatePair,model_coeffs,from_e4a_source, DENSE_MASS,
    TANBETA_VALUES,WC_NLO_OPERATORS, SUCCESS as F2_PASS)

STATUS="F3_FULL_SOURCE_NLO_LOW_RG_AND_EOS_RESPONSE_DIAGNOSTIC_NO_EXCLUSION"
BLOCK="F3_SOURCE_OR_BASIS_VALIDATION_BLOCKED_NO_EXCLUSION"
SCALE_W=160.
SCALE_B=4.2
MODES={"LO_RG":0,"NLO_DIPOLES_RG":1,"FULL_NLO_RG":2}
TOL_HIGH=5.e-9
# This is a deliberately loose detection of an O(1) cross-code basis
# error, not perturbative accuracy. Differences are reported explicitly.
RG_DIAGNOSTIC_MAX_FRACTION=0.35
OBS_DIAGNOSTIC_MAX_FRACTION=0.35
INPUT_RE=re.compile(
    r"^INPUT mass1=(\S+) mass2=(\S+) tanbeta=(\S+) gamma=(\S+) "
    r"muW=(\S+) mub=(\S+) w1=(\S+) w2=(\S+)$")
WILSON_RE=re.compile(
    r"^WC mode=(\d+) op=(\d+) hiLO=(\S+) hiNLO=(\S+) "
    r"loLO=(\S+) loNLO=(\S+) SMloLO=(\S+) SMloNLO=(\S+)$")

def finite(v,what):
    z=float(v)
    if not math.isfinite(z):raise ValueError("nonfinite "+what)
    return z

def probe(exe,m1,m2,t,g):
    cmd=[str(Path(exe).resolve()),*[f"{v:.17g}" for v in
          (m1,m2,t,g,SCALE_W,SCALE_B)]]
    z=subprocess.run(cmd,check=False,capture_output=True,text=True,timeout=90)
    if z.returncode:
        raise RuntimeError(f"F3 source RG returned {z.returncode}: "+
                           z.stderr[-1800:]+z.stdout[-700:])
    lines=z.stdout.splitlines()
    if lines.count("STATUS F3_SOURCE_PINNED_NLO_RG_DIAGNOSTIC_NOT_BR_OR_EXCLUSION")!=1 or \
        lines.count("F3_WC_XF_FOURQUARK_TRANSLATION_ASSUMED false")!=1 or \
        lines.count("F3_EXCLUSION UNKNOWN")!=1:
        raise ValueError("F3 source-driver authenticity markers absent")
    found=[INPUT_RE.fullmatch(s) for s in lines]
    found=[m for m in found if m]
    if len(found)!=1:raise ValueError("F3 probe inputs missing/duplicate")
    raw=[finite(x,"F3 input") for x in found[0].groups()]
    given=(m1,m2,t,g,SCALE_W,SCALE_B)
    if any(abs(a-b)>2.e-9 for a,b in zip(raw[:6],given)) or \
       abs(raw[6]+raw[7]-1.)>1.e-11:
        raise ValueError("F3 source driver input mismatch")
    data={}
    for row in lines:
        match=WILSON_RE.fullmatch(row)
        if match:
            mode,op=map(int,match.groups()[:2])
            key=(mode,op)
            if mode not in range(3) or op not in range(1,9) or key in data:
                raise ValueError("F3 invalid duplicate/source operator")
            vals=[finite(x,"F3 low coefficient") for x in match.groups()[2:]]
            data[key]={"high_LO":vals[0],"high_NLO":vals[1],
                       "low_LO":vals[2],"low_NLO":vals[3],
                       "low_SM_LO":vals[4],"low_SM_NLO":vals[5]}
    if set(data)!={(k,n) for k in range(3) for n in range(1,9)}:
        raise ValueError("F3 incomplete low WCs; expected 24")
    for n in range(1,9):
        sm=[data[i,n]["low_SM_LO"] for i in range(3)]
        sn=[data[i,n]["low_SM_NLO"] for i in range(3)]
        if max(sm)-min(sm)>1.e-11 or max(sn)-min(sn)>1.e-11:
            raise ValueError("F3 SM RG changes when NP high order toggled")
    return data

def check_high(reference,data,w):
    for n in range(1,9):
        a=reference[0,n]
        elo=w*a[0]+(1-w)*a[1]
        if abs(elo-data[0,n]["high_LO"])>TOL_HIGH:
            raise ValueError(f"F3 E4A LO source mismatch op={n}")
        for mode in range(3):
            v=data[mode,n]
            if abs(v["high_LO"]-elo)>TOL_HIGH:
                raise ValueError("F3 source LO changes across modes")
            en=(w*reference[1,n][0]+(1-w)*reference[1,n][1]) \
                if (mode==2 or (mode==1 and n in (7,8))) else 0.
            if abs(v["high_NLO"]-en)>TOL_HIGH:
                raise ValueError(f"F3 high NLO source mismatch mode={mode} op={n}")

def net_low(data,mode,aslow):
    return {n:data[mode,n]["low_LO"]+aslow*data[mode,n]["low_NLO"]
            for n in range(1,9)}

def rg_validation(pair,data,reference,w,aslow):
    # All LO source deltas are included. Cross-check two loop paths
    # WITHOUT assigning unsupported C4_bs in WCxf.
    high=from_e4a_source(reference,w,"LO",pair.as4pi)
    _,independent=pair.wc(high)
    actual=net_low(data,0,aslow)
    source_lo_only={n:data[0,n]["low_LO"] for n in range(1,9)}
    errors={}
    for n in (7,8):
        x=actual[n]
        xlo=source_lo_only[n]
        y=independent[n]
        # Non-effective and effective low C7,8 might differ by penguin
        # rotations. Compare both instead of choosing by assumption.
        y_peng=({3:-1/3,4:-4/9,5:-20/3,6:-80/9} if n==7 else
                {3:1,4:-1/6,5:20,6:-10/3})
        effective=x+sum(y_peng[i]*actual[i] for i in (3,4,5,6))
        scale=max(1.e-9,abs(y))
        errors[f"C{n}"]={
            "superiso_low_raw_LOplusNLO_RGE":x,
            "superiso_low_raw_LO_RG_only":xlo,
            "source_NLO_RG_delta_at_fixed_LO_high":x-xlo,
            "independent_wilson_low_raw_NP":y,
            "relative_LO_only_residual":abs(xlo-y)/scale,
            "relative_LOplusNLO_residual":abs(x-y)/scale,
            "superiso_low_effective_candidate":effective,
            "relative_raw_residual":abs(x-y)/scale,
            "relative_effective_candidate_residual":abs(effective-y)/scale,
            "basis_translation_not_certified":True}
    # Compare raw to raw because EOS and flavio expect non-effective WCs
    # at their model parameter boundary.
    maximum=max(errors[f"C{n}"]["relative_raw_residual"] for n in (7,8))
    maximum_lo=max(errors[f"C{n}"]["relative_LO_only_residual"]
                   for n in (7,8))
    return {"dipole_low_cross_code":errors,
            "max_raw_fractional_residual":maximum,
            "max_LO_only_fractional_residual":maximum_lo,
            "within_gross_35percent_screen":maximum<RG_DIAGNOSTIC_MAX_FRACTION}

def eos_observable(pair,data,aslow):
    # EOS parameters b->s::c1..c8 are low-scale non-effective coefficients.
    # Source-to-EOS precise scheme correspondence is not yet independently
    # certified: report conditional numerical sensitivity, NOT exclusion.
    lo_only={n:data[0,n]["low_LO"] for n in range(1,9)}
    lo_br=pair.eos_rate(lo_only)
    outcome={"LO_QCD_RG_ONLY": {
        "EOS_NLO_BR_conditional_basis":lo_br,
        "EOS_deltaBR_conditional_basis":lo_br-pair.eos_sm,
        "low_coeffs":lo_only}}
    for label,mode in MODES.items():
        d=net_low(data,mode,aslow)
        br=pair.eos_rate(d)
        outcome[label]={
            "EOS_NLO_BR_conditional_basis":br,
            "EOS_deltaBR_conditional_basis":br-pair.eos_sm,
            "low_coeffs":d,
        }
    return outcome

def validate_provenance(e4a,f1,f2):
    d,models,rows=read_source_e4a(e4a)
    f=json.loads(Path(f1).read_text())
    s=json.loads(Path(f2).read_text())
    if (f.get("source_e4a_summary_sha256")!=sha(e4a) or
        f.get("summary",{}).get("Zee_models")!=27 or
        f.get("summary",{}).get("errors") or
        f.get("summary",{}).get("underlying_2015_basis_validation_provisional") is not True):
        raise ValueError("F3 original F1 source validation missing")
    if (s.get("status")!=F2_PASS or
        s.get("source_F1_sha256")!=sha(f1) or
        s.get("source_E4A_sha256")!=sha(e4a) or
        s.get("summary",{}).get("real_Zee_spectra")!=27 or
        s.get("summary",{}).get("errors") or
        s.get("summary",{}).get("NLO_BSM_complete") is not False):
        raise ValueError("F3 cannot recover source-validated real F2 result")
    zid={m["candidate_id"] for m in models}
    fz={r["candidate_id"] for r in f["Zee_27_results"]}
    z2={r["candidate_id"] for r in s["Zee_27_by_matching_order"]}
    if zid!=fz or zid!=z2:
        raise ValueError("F3 cohort changed from F1/F2")
    return d,models,rows,f,s

def calc(pair,exe,models,rows,f2,e4a_data=None):
    pair.prepare()
    alpha_b=pair.flavio.physics.running.running.get_alpha(
        pair.par,SCALE_B,nf_out=5)["alpha_s"]
    if not .17<alpha_b<.28:
        raise ValueError("Unexpected alpha_s(4.2GeV)")
    aslow=alpha_b/(4*math.pi)
    old={(r["candidate_id"],r["input_matching_order"]):r
         for r in f2["Zee_27_by_matching_order"]}
    outZ=[]
    max_wilson=0.;max_f2_rate=0.
    max_wilson_lo_only=0.;max_f2_rate_lo_only=0.
    nlo_running_rate_shifts=[];lo_only_raw_c7_residuals=[]
    for index,m in enumerate(models,1):
        name=m["candidate_id"];g=float(m["gamma"])
        coeff=model_coeffs(rows,name)
        d=probe(exe,float(m["mH1_GeV"]),float(m["mH2_GeV"]),
                float(m["tanbeta"]),g)
        w=math.cos(g)**2
        check_high(coeff,d,w)
        rg=rg_validation(pair,d,coeff,w,aslow)
        eos=eos_observable(pair,d,aslow)
        max_wilson=max(max_wilson,rg["max_raw_fractional_residual"])
        max_wilson_lo_only=max(max_wilson_lo_only,
            rg["max_LO_only_fractional_residual"])
        f2_ref=old[name,"LO"]
        original=eos["LO_RG"]["EOS_NLO_BR_conditional_basis"]
        ref=f2_ref["eos_NLO_BR"]
        response=original-pair.eos_sm
        f2_response=ref-pair.eos_sm
        rate_relative=abs(response-f2_response)/max(abs(f2_response),1.e-8)
        lo_only_br=eos["LO_QCD_RG_ONLY"]["EOS_NLO_BR_conditional_basis"]
        lo_only_rate_relative=abs((lo_only_br-pair.eos_sm)-f2_response)/max(
            abs(f2_response),1.e-8)
        nlo_running_rate_shift=original-lo_only_br
        nlo_running_rate_shifts.append(nlo_running_rate_shift)
        max_f2_rate=max(max_f2_rate,rate_relative)
        max_f2_rate_lo_only=max(max_f2_rate_lo_only,lo_only_rate_relative)
        a=eos["NLO_DIPOLES_RG"]["EOS_NLO_BR_conditional_basis"]
        b=eos["FULL_NLO_RG"]["EOS_NLO_BR_conditional_basis"]
        row={
            "candidate_id":name,
            "mH1_GeV":m["mH1_GeV"],
            "mH2_GeV":m["mH2_GeV"],
            "gamma":g,"tanbeta":m["tanbeta"],
            "EOS_source_LO_RG_BR_conditional":original,
            "EOS_source_LO_QCD_RG_ONLY_BR_conditional":lo_only_br,
            "EOS_source_NLO_running_shift_at_LO_matching_conditional":
                nlo_running_rate_shift,
            "EOS_source_LO_QCD_RG_ONLY_vs_F2_delta_rate_relative":
                lo_only_rate_relative,
            "LO_source_QCD_RG_ONLY_vs_wilson_max_C7C8_relative":
                rg["max_LO_only_fractional_residual"],
            "EOS_source_NLO_dipoles_RG_BR_conditional":a,
            "EOS_source_full_NLO_matching_RG_BR_conditional":b,
            "fourquark_NLO_matching_deltaBR_conditional":b-a,
            "all_NLO_matching_deltaBR_vs_LO_conditional":b-original,
            "LO_source_RG_vs_wilson_F2_rate_relative":rate_relative,
            "LO_source_RG_vs_wilson_max_C7C8_relative":
                rg["max_raw_fractional_residual"],
            "raw_vs_effective_C7":rg["dipole_low_cross_code"]["C7"],
            "raw_vs_effective_C8":rg["dipole_low_cross_code"]["C8"],
            "source_NLO_low_C3_C6_full":{
                f"C{n}":eos["FULL_NLO_RG"]["low_coeffs"][n]
                for n in (3,4,5,6)},
            "Zee_physical_allowed_or_excluded":None,
        }
        outZ.append(row)
        print("F3_ZEE",f"{index}/27",name,
              "EOS_FULL_SOURCE_NLO_CONDITIONAL",f"{b:.12g}",
              "FOURQUARK_RATE_SHIFT_CONDITIONAL",f"{b-a:.8g}",
              "LO_CROSSCODE_WC_RESIDUAL_LOONLY",f"{rg['max_LO_only_fractional_residual']:.4g}",
              "LO_CROSSCODE_WC_RESIDUAL_LOPLUSNLO",f"{rg['max_raw_fractional_residual']:.4g}",
              "LO_ONLY_EOS_DELTA_RATE_RESIDUAL",f"{lo_only_rate_relative:.4g}",
              "LO_PLUS_NLO_EOS_DELTA_RATE_RESIDUAL",f"{rate_relative:.4g}",
              "EXCLUSION_UNKNOWN",flush=True)
    typeII=[]
    anchors=validate_e4a_typeii(e4a_data) if e4a_data is not None else {}
    if e4a_data is not None and len(anchors)!=18:
        raise ValueError("F3 original 18 E4A TypeII reference controls absent")
    seen_anchors=set()
    for t in TANBETA_VALUES:
        for mass in DENSE_MASS:
            # Regenerate full source-matched single charged spectrum;
            # same angles and masses at both eigenvalues.
            d=probe(exe,mass,mass,t,0.)
            if (mass,t) in anchors:
                a=anchors[mass,t]
                for op in (7,8):
                    if abs(d[0,op]["high_LO"]-float(a[f"LO_C{op}"]))>TOL_HIGH or abs(
                        d[2,op]["high_NLO"]-float(a[f"NLO_C{op}_vendor"]))>TOL_HIGH:
                        raise ValueError("F3 TypeII probe not original E4A source")
                seen_anchors.add((mass,t))
            rates=eos_observable(pair,d,aslow)
            z={
                "mass_GeV":mass,"tanbeta":t,
                "LO_BR_conditional":rates["LO_RG"]["EOS_NLO_BR_conditional_basis"],
                "NLO_dipoles_BR_conditional":
                    rates["NLO_DIPOLES_RG"]["EOS_NLO_BR_conditional_basis"],
                "full_NLO_matched_BR_conditional":
                    rates["FULL_NLO_RG"]["EOS_NLO_BR_conditional_basis"],
                "full_minus_dipole_NLO_conditional":(
                    rates["FULL_NLO_RG"]["EOS_NLO_BR_conditional_basis"]-
                    rates["NLO_DIPOLES_RG"]["EOS_NLO_BR_conditional_basis"]),
                "2017_580GeV_bound_reproduced":False,
            }
            typeII.append(z)
    if e4a_data is not None and seen_anchors!=set(anchors):
        raise ValueError("F3 dense scan omitted source-locked TypeII E4A anchors")
    errors=[]
    if max_wilson>RG_DIAGNOSTIC_MAX_FRACTION:
        errors.append("SuperIso low-scale raw dipole and wilson-eft LO evolution differ beyond 35%")
    if max_f2_rate>OBS_DIAGNOSTIC_MAX_FRACTION:
        errors.append("SuperIso-source LO RG and F2 wilson-RG EOS rate shifts differ beyond 35%")
    if any(x["fourquark_NLO_matching_deltaBR_conditional"]!=
           x["fourquark_NLO_matching_deltaBR_conditional"] for x in outZ):
        errors.append("nonfinite fourquark-induced shift")
    # A source-pinned RG implementation, even on PASS, is not yet a
    # perturbatively matched EOS observable in a certified common basis.
    summary={
        "Zee_spectra":len(outZ),"typeII_dense_benchmarks":len(typeII),
        "source_locked_TypeII_18_anchor_coefficients_checked":len(seen_anchors),
        "RG_evaluations":len(outZ)+len(typeII),
        "muW_GeV":SCALE_W,"mub_GeV":SCALE_B,
        "max_relative_LO_raw_C7_C8_source_vs_wilson":max_wilson,
        "max_relative_QCD_LO_only_C7_C8_source_vs_wilson":max_wilson_lo_only,
        "max_relative_LO_source_RG_vs_F2_EOS_deltaBR":max_f2_rate,
        "max_relative_QCD_LO_only_RG_vs_F2_EOS_deltaBR":max_f2_rate_lo_only,
        "median_extra_NLO_running_rate_shift_with_LO_matching_conditional":
            statistics.median(nlo_running_rate_shifts),
        "NLO_ADM_order_not_equated_to_wilson_default_LO_QCD":True,
        "median_fourquark_rate_shift_conditional":statistics.median(
            x["fourquark_NLO_matching_deltaBR_conditional"] for x in outZ),
        "max_abs_fourquark_rate_shift_conditional":max(
            abs(x["fourquark_NLO_matching_deltaBR_conditional"])
            for x in outZ),
        "NLO_C3_C6_matching_included_by_original_SuperIso_RG":True,
        "EOS_and_SuperIso_operator_basis_fully_certified":False,
        "full_NLO_exclusion_accuracy_calibrated":False,
        "2017_TypeII_580GeV_95CL_reproduced":False,
        "paper_ready_Zee_95CL_exclusions":False,
        "errors":errors}
    return {"status":STATUS if not errors else BLOCK,
            "summary":summary,"Zee_27_results":outZ,
            "TypeII_dense_results":typeII,
            "uninterpreted_nonperturbative_status":"NO_PHYSICAL_EXCLUSIONS",
            "Zee_allowed_or_excluded":None}

def csv_rows(path,rows):
    if not rows:return
    # Nested diagnostics are encoded deterministically as JSON columns.
    keys=list(rows[0])
    with Path(path).open("w",newline="") as h:
        f=csv.DictWriter(h,fieldnames=keys);f.writeheader()
        for r in rows:
            f.writerow({k:json.dumps(v,sort_keys=True) if isinstance(v,dict) else v
                       for k,v in r.items()})

def main():
    a=argparse.ArgumentParser(description=__doc__)
    for key in ("e4a-summary","f1-summary","f2-summary",
                "vendor-root","a1m-provenance","output-dir"):
        a.add_argument("--"+key,required=True,type=Path)
    args=a.parse_args()
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        a.error("Refuse to overwrite previous F3 output")
    args.output_dir.mkdir(parents=True,exist_ok=True)
    report={"status":BLOCK,"Zee_allowed_or_excluded":None}
    code=1
    try:
        for key in ("e4a_summary","f1_summary","f2_summary","a1m_provenance"):
            if not getattr(args,key).is_file():
                raise FileNotFoundError(key+" missing: "+str(getattr(args,key).resolve()))
        data,models,rows,f1,f2=validate_provenance(
            args.e4a_summary,args.f1_summary,args.f2_summary)
        source=check_superiso_source(args.vendor_root,args.a1m_provenance)
        compiler=compile_pilot(args.vendor_root,
                               args.output_dir/"f3_source_pinned_RG_probe",
                               Path(__file__).with_name("zee_gateF3_fullNLO_rg_probe.c"),
                               False)
        pair=RatePair()
        report=calc(pair,args.output_dir/"f3_source_pinned_RG_probe",
                    models,rows,f2,data)
        report.update({
            "hash_E4A":sha(args.e4a_summary),
            "hash_F1":sha(args.f1_summary),
            "hash_F2":sha(args.f2_summary),
            "hash_A1M":sha(args.a1m_provenance),
            "flavio_version":pair.flavio_version,
            "eos_version":pair.eos_version,"wilson_version":pair.wilson_version,
            "source_verification":source,"compiled_probe":compiler})
        csv_rows(args.output_dir/"F3_27_Zee_full_source_NLO_eos_conditional.csv",
                 report["Zee_27_results"])
        csv_rows(args.output_dir/"F3_64_TypeII_full_source_NLO_eos_conditional.csv",
                 report["TypeII_dense_results"])
        print("F3_COHORT",json.dumps(report["summary"]),flush=True)
        print("F3_PAPER_READY_EXCLUSIONS False",flush=True)
        code=0 if report["status"]==STATUS else 1
    except Exception as exc:
        report={"status":BLOCK,"error":repr(exc),
                "traceback":traceback.format_exc(),
                "Zee_allowed_or_excluded":None}
        print("F3_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
        code=1
    finally:
        dest=args.output_dir/"summary.json"
        dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
        print("F3_SUMMARY",dest,flush=True)
    return code

if __name__=="__main__":
    raise SystemExit(main())
