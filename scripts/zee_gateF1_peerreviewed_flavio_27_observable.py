#!/usr/bin/env python3
"""F1: one real flavio/wilson 2015-era inclusive B->Xsγ run for 27 Zee points.

This IS an executable observable-level study, unlike E4B's source intake.
It uses actual flavio BR(B->Xsgamma), which has a quadratic Wilson response
and NLO+selected NNLO coefficient matrices based on arXiv:1503.01789.
The BSM matching fed to the RG is strictly LO C7/C8 from authenticated E4A,
at μ0=160GeV, with Type-II doublet fractions. We DO NOT silently insert
incompatible SuperIso NNLO C3-C6 or claim full NNLO Type-II prediction.

Validation: match E4A's actual 648 coefficient entries/27 identities,
pure 18 TypeII source-mass/tanbeta controls, 2015 SM envelope, published
2015 Eq(10) LO derivatives (basis/sign crosscheck), monotonic constructive
mass trend at tanbeta>=5.6, pure γ=0,π/2 endpoint closure for all 27,
common Wilson-level superposition, selected quadratic NP curvature.
Optional source-pinned old SuperIso E1 27-rate comparison. Any substantial
SM/basis/endpoint failure changes classification to BLOCKED. Always mark
2017 complete TypeII 580GeV 95% CL reproduction FALSE: unlike the 2017
paper this mixed-order calculation is not full NNLO TypeII.

A rough exp/theory Gaussian comparison is reported as DIAGNOSTIC_ONLY,
never as a paper-ready exclusion because the theory error in a mixed-
order NP calculation is not calibrated; current HFLAV EXP=3.49±0.19
and peer-reviewed 2015 SM theory=3.36±0.23 (all BR in 1e-4).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import math
import platform
import statistics
import sys
import traceback
from pathlib import Path

from zee_gateE4b_2026_observable_validation import read_source_e4a

MU0=160.0
EXP=3.49e-4
EXP_SIGMA=0.19e-4
SM_2015=3.36e-4
SM_2015_SIGMA=0.23e-4
OBS="BR(B->Xsgamma)"
STATUS="F1_FLAVIO_2015_OBSERVABLE_LO_ZEE_NP_SCREEN_NOT_EXCLUSION"
BLOCKED="F1_OBSERVABLE_OR_BASIS_VALIDATION_FAILED_NO_EXCLUSION"
NOENGINE="F1_MISSING_FLAVIO_OR_WILSON_INSTALL_DEPENDENCIES"
NO_FULL_NNLO="LO_NP_MATCHING_SELECTED_NNLO_OBSERVABLE_NOT_FULL_TYPEII_NNLO"
DERIVATIVES_2015={7:-8.22e-4,8:-1.99e-4}
# 2015 Eq(10) is not the flavio exact Kij response. ~25% headroom for
# scale/scheme/nuisance choices, recorded explicitly for scrutiny.
MAX_BASIS_RELATIVE_DEVIATION=0.25
SM_ENVELOPE_ABS=0.20e-4

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def numeric(value,name):
    if isinstance(value,bool):raise ValueError("boolean used as number "+name)
    v=float(value)
    if not math.isfinite(v):raise ValueError("nonfinite "+name)
    return v

class FlavioEngine:
    def __init__(self):
        # Import lazily; audit tests can inject deterministic response
        # without pretending to have run the external library.
        self.flavio=importlib.import_module("flavio")
        self.wilson=importlib.import_module("wilson")
        self.calls=0
        self.flavio_version=getattr(self.flavio,"__version__","unknown")
        self.wilson_version=getattr(self.wilson,"__version__","unknown")
    def prediction(self,d7,d8):
        d7=numeric(d7,"delta C7");d8=numeric(d8,"delta C8")
        wc=self.flavio.WilsonCoefficients()
        wc.set_initial({"C7_bs":d7,"C8_bs":d8},MU0,eft="WET",basis="flavio")
        value=numeric(self.flavio.np_prediction(OBS,wc),"flavio inclusive BR")
        self.calls+=1
        if not 1e-7<value<1e-3:raise ValueError("implausible B->Xs gamma value")
        return value

def no_np_test(engine):
    zero=engine.prediction(0.,0.)
    return {
        "flavio_SM":zero,"peer_reviewed_2015_SM":SM_2015,
        "SM_difference":zero-SM_2015,
        "flavio_matches_2015_SM_within_0p20e_4":abs(zero-SM_2015)<=SM_ENVELOPE_ABS
    }

def basis_derivative_test(engine,sm):
    epsilon=2.e-4
    out={}
    passed=True
    for op in (7,8):
        plus=engine.prediction(epsilon if op==7 else 0.,
                               epsilon if op==8 else 0.)
        minus=engine.prediction(-epsilon if op==7 else 0.,
                                -epsilon if op==8 else 0.)
        slope=(plus-minus)/(2*epsilon)
        expected=DERIVATIVES_2015[op]
        diff=abs(slope-expected)/abs(expected)
        # Test quadratic component is finite/nontrivial and the input
        # sign response matches the published Eq.(10) convention.
        curvature=(plus+minus-2*sm)/(epsilon*epsilon)
        close=diff<=MAX_BASIS_RELATIVE_DEVIATION and slope<0.
        out[f"C{op}"]={"observed_dBR_dC":slope,
                       "2015_linear_reference_dBR_dC":expected,
                       "fractional_residual":diff,
                       "quadratic_response_second_difference":curvature,
                       "pass":close}
        passed=passed and close
    out["both_operator_derivative_sign_and_scale_consistent"]=passed
    return out

def validate_e4a_typeii(data):
    source=data.get("pure_TypeII_18_results",[])
    actual={(numeric(x["mH_GeV"],"mass"),
             numeric(x["tanbeta"],"tanbeta")):x for x in source}
    required={(m,t) for m in (300.,450.,550.,600.,650.,670.,
                                700.,800.,1000.) for t in (5.6,50.)}
    if len(source)!=18 or set(actual)!=required:
        raise ValueError("Missing original E4A pure TypeII mass/tanbeta controls")
    for key,x in actual.items():
        for op in (7,8):
            numeric(x[f"LO_C{op}"],"matching LO C"+str(op))
        if not x.get("three_gamma_endpoints_checked",False):
            raise ValueError("E4A TypeII equal-mass controls not complete")
    return actual

def evaluate_typeii(engine,by):
    values=[]
    for tanb in (5.6,50.):
        group=[]
        for mass in (300.,450.,550.,600.,650.,670.,700.,800.,1000.):
            source=by[mass,tanb]
            d7=numeric(source["LO_C7"],"pure C7")
            d8=numeric(source["LO_C8"],"pure C8")
            br=engine.prediction(d7,d8)
            row={"mass_GeV":mass,"tanbeta":tanb,
                 "LO_delta_C7":d7,"LO_delta_C8":d8,
                 "flavio_hybrid_BR":br,
                 "published_2017_full_580GeV_95CL_reproduced":False}
            values.append(row);group.append(row)
        # Physically expected Type II constructive contribution over the
        # SM, decoupling with increasing charged-scalar mass.
        for x in group:
            if x["flavio_hybrid_BR"]<=engine._sm:
                raise ValueError("Type-II model has wrong constructive NP sign")
        for a,b in zip(group[:-1],group[1:]):
            if a["flavio_hybrid_BR"]+3.e-9<b["flavio_hybrid_BR"]:
                raise ValueError("Type-II charged scalar fails decoupling trend")
    return values

def evaluate_zee(engine,models,rows,legacy=None):
    legacy_by={}
    if legacy is not None:
        if legacy.get("tested")!=27 or len(legacy.get("rows",[]))!=27:
            raise ValueError("E1 legacy file has no complete 27 spectra")
        legacy_by={x["candidate_id"]:x for x in legacy["rows"]}
        if len(legacy_by)!=27:raise ValueError("Duplicated legacy E1 rows")
    results=[]
    for i,model in enumerate(models,1):
        name=model["candidate_id"]
        if legacy is not None and name not in legacy_by:
            raise ValueError("E1 candidate labels differ")
        q=rows[name]
        gamma=numeric(model["gamma"],"gamma")
        c=math.cos(gamma)**2;s=math.sin(gamma)**2
        d7l,d7h=q[0,"C7"][1:3]
        d8l,d8h=q[0,"C8"][1:3]
        d7=c*d7l+s*d7h;d8=c*d8l+s*d8h
        original=q[0,"C7"][3]-q[0,"C7"][0]
        if abs(d7-original)>2.e-11:
            raise ValueError("LO C7 original gamma vector mismatch")
        if abs(d8-(q[0,"C8"][3]-q[0,"C8"][0]))>2.e-11:
            raise ValueError("LO C8 original gamma vector mismatch")
        purelight=engine.prediction(d7l,d8l)
        pureheavy=engine.prediction(d7h,d8h)
        mixed=engine.prediction(d7,d8)
        # For a quadratic observable, mixed output need not be equal to
        # c*BR(light)+s*BR(heavy). Check the correct NP amplitude combination.
        if not min(purelight,pureheavy)-5.e-9<=mixed<=max(purelight,pureheavy)+5.e-9:
            raise ValueError("Two-state observable outside endpoint rates")
        zerolimit=engine.prediction(
            c*d7l+s*d7l,c*d8l+s*d8l)
        if abs(zerolimit-purelight)>2.e-13:
            raise ValueError("Degenerate mass/invariant doublet sum failure")
        old=None if legacy is None else numeric(
            legacy_by[name]["B_to_Xs_gamma_legacy_Zee_BR"],"old SuperIso BR")
        # gaussian diagnostic explicitly NOT an exclusion confidence
        # level (mixed-order NP theory uncertainty not calibrated).
        z_exp_only=(mixed-EXP)/EXP_SIGMA
        z_broad=(mixed-EXP)/math.hypot(EXP_SIGMA,SM_2015_SIGMA)
        record={"candidate_id":name,
                "mH1_GeV":numeric(model["mH1_GeV"],"mH1"),
                "mH2_GeV":numeric(model["mH2_GeV"],"mH2"),
                "tanbeta":numeric(model["tanbeta"],"tanbeta"),
                "gamma":gamma,
                "LO_delta_C7_coherent":d7,"LO_delta_C8_coherent":d8,
                "flavio_hybrid_BR":mixed,
                "flavio_pure_light_BR":purelight,
                "flavio_pure_heavy_BR":pureheavy,
                "old_SuperIso_BR_separate_scheme":old,
                "experimental_central_BR":EXP,
                "Z_exp_only_DIAGNOSTIC":z_exp_only,
                "Z_exp_plus_2015_SM_theory_DIAGNOSTIC":z_broad,
                "2017_TypeII_full_NNLO_bound_applied":False,
                "Zee_physically_allowed":None}
        results.append(record)
        print("F1_ZEE",f"{i}/27",name,"flavio_LO_NP_BR",
              f"{mixed:.10g}","legacy_separate",old,
              "Z_exp_plus_old_SM_sigma_diagnostic",f"{z_broad:.3f}",
              "EXCLUSION_UNKNOWN",flush=True)
    return results

def real_run(engine,e4a,e1=None):
    data,models,rows=read_source_e4a(e4a)
    typeii=validate_e4a_typeii(data)
    old=None
    if e1:
        if data.get("fingerprints_sha256",{}).get("E1")!=sha(e1):
            raise ValueError("E1 legacy and E4A SHA ancestry inconsistent")
        old=json.loads(Path(e1).read_text())
    zero=no_np_test(engine)
    engine._sm=zero["flavio_SM"]
    derivative=basis_derivative_test(engine,engine._sm)
    pure=evaluate_typeii(engine,typeii)
    zee=evaluate_zee(engine,models,rows,old)
    errors=[]
    if not zero["flavio_matches_2015_SM_within_0p20e_4"]:
        errors.append("flavio default SM too far from published 2015 prediction")
    if not derivative["both_operator_derivative_sign_and_scale_consistent"]:
        errors.append("flavio↔2015 Eq10 C7/C8 normalization/sign discrepancy")
    summary={
        "Zee_models":len(zee),"TypeII_controls":len(pure),
        "flavio_evaluations":engine.calls,
        "SM_BR_flavio":engine._sm,
        "Zee_median_hybrid_BR":statistics.median(
            x["flavio_hybrid_BR"] for x in zee),
        "Zee_min_hybrid_BR":min(x["flavio_hybrid_BR"] for x in zee),
        "Zee_max_hybrid_BR":max(x["flavio_hybrid_BR"] for x in zee),
        "Zee_median_signed_Z_exp_plus_2015_theory_DIAGNOSTIC":
            statistics.median(x["Z_exp_plus_2015_SM_theory_DIAGNOSTIC"]
                              for x in zee),
        "published_2017_580GeV_TypeII_95CL_reproduced":False,
        "publishable_95CL_Zee_exclusions_calculated":False,
        "underlying_2015_basis_validation_provisional":not errors,
        "errors":errors}
    return {"status":STATUS if not errors else BLOCKED,
            "source_e4a_summary_sha256":sha(e4a),
            "source_e1_sha256":sha(e1) if e1 else None,
            "flavio_version":engine.flavio_version,
            "wilson_version":engine.wilson_version,
            "python_version":platform.python_version(),
            "accuracy":NO_FULL_NNLO,
            "comparison_2015_peer_reviewed":zero,
            "C7_C8_2015_derivative_validation":derivative,
            "TypeII_18_results":pure,"Zee_27_results":zee,
            "summary":summary,"Zee_allowed_or_excluded":None,
            "full_2017_TypeII_reproduction":False}

def write_rows(path,rows):
    if not rows:return
    with Path(path).open("w",newline="") as f:
        keys=list(rows[0]);csv_writer=csv.DictWriter(f,fieldnames=keys)
        csv_writer.writeheader();csv_writer.writerows(rows)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--e4a-summary",required=True,type=Path)
    p.add_argument("--e1-summary",type=Path)
    p.add_argument("--output-dir",required=True,type=Path)
    args=p.parse_args()
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        p.error("Refuse to overwrite previous source-backed F1 report")
    args.output_dir.mkdir(parents=True,exist_ok=True)
    result={"status":BLOCKED,"Zee_allowed_or_excluded":None,
            "published_2017_580GeV_bound_reproduced":False}
    code=1
    try:
        # Validate the actual source before importing physics dependencies
        # to avoid silently running on absent or partial 27 model inputs.
        read_source_e4a(args.e4a_summary)
        try:
            engine=FlavioEngine()
        except (ModuleNotFoundError,ImportError) as exc:
            result.update(status=NOENGINE,reason=repr(exc))
            print("F1_DEPENDENCY_MISSING",repr(exc),file=sys.stderr,flush=True)
            return 2
        result=real_run(engine,args.e4a_summary,args.e1_summary)
        write_rows(args.output_dir/"F1_27_Zee_flavio_hybrid_LO_NP.csv",
                   result["Zee_27_results"])
        write_rows(args.output_dir/"F1_18_TypeII_flavio_hybrid_LO_NP.csv",
                   result["TypeII_18_results"])
        print("F1_COHORT",json.dumps(result["summary"]),flush=True)
        print("F1_ZEE_ALLOWED_OR_EXCLUDED UNKNOWN",flush=True)
        print("F1_FULL_2017_TYPEII_NNLO_REPRODUCED False",flush=True)
        code=0 if result["status"]==STATUS else 1
    except Exception as exc:
        result={"status":BLOCKED,"reason":repr(exc),
                "traceback":traceback.format_exc(),
                "Zee_allowed_or_excluded":None}
        print("F1_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
        code=1
    finally:
        dest=args.output_dir/"summary.json"
        dest.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
        print("F1_SUMMARY",dest,flush=True)
    return code

if __name__=="__main__":
    raise SystemExit(main())
