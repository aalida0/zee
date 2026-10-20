#!/usr/bin/env python3
"""E4B: genuine *observable-level* 2026 B->Xs gamma validation harness.

This is NOT an observable implementation. It accepts only an EXTERNAL,
independently authored/reproducible numerical 2026 NNLO inclusive-rate
backend with a documented uncertainty/likelihood definition. It tests
the paper's SM prediction, an independent NUMERIC Type-II control
curve, pure-state exact closure in the ORIGINAL A1M matching basis,
and the published Type-II mass exclusion boundary BEFORE producing
any two-state Zee rate. Without such an external code and its numeric
benchmarks, it FAILS CLOSED (not a pseudo-2026 exclusion).

The 2026 paper (arXiv:2608.29863) gives SM (3.54+-0.14)e-4,
exp (3.49+-0.19)e-4 and a Type-II 95% CL limit of 670 GeV.
Eq.(4) gives a LINEARIZED NP formula, *not* the entire NNLO
rate/variance/likelihood. E4A provides FULL source-pinned matching
input but cannot substitute for the observable.

Backend protocol: one process per JSON request, strict JSON stdin ->
JSON stdout, with actions:
  describe
  predict_sm
  predict_typeii(mass_GeV, tanbeta, Ecut_GeV, mu0_GeV)
  typeii_excluded_95(mass_GeV, tanbeta, Ecut_GeV)
  predict_twocharged_from_raw_superiso(masses, tanbeta, gamma,
          A1M_CW_calculator_raw_3orders_8ops, mu0, Ecut)

The last action MUST convert the saved *raw* A1M matching basis to
the backend operator basis; raw NNLO C3-C6 are known to have unresolved
source-level differences from author/HEPfit conventions. The backend
must keep all SM×NP and NP×NP terms. For an actual public/author
backend, a manifest/independent author holdout table is required.
Self-reported 'validation' without independent numerical Type-II
holdouts is rejected.

One run evaluates 27 Zee physical spectra, two pure-state controls
per spectrum, nine Type-II mass anchors × two tanβ, the published
limit crossing on a fine grid, and all original SHA-locked E4A
matching inputs. Nothing is exported as physically allowed until
all gates succeed.

--audit-only creates a source-readiness blocker report without
pretending to have calculated any NNLO observables.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import traceback
from pathlib import Path

STATUS="GATE_E4B_2026_OBSERVABLE_FULL_TYPEII_VALIDATED_AND_ZEE_EVALUATED"
BLOCKED="GATE_E4B_BLOCKED_MISSING_VALIDATED_2026_OBSERVABLE"
FAILED="GATE_E4B_FAIL_CLOSED_NUMERICAL_OR_SOURCE_INCONSISTENCY"
E4A_STATUS="GATE_E4A_ALL_ORDERS_COHERENT_MATCHING_COMPLETED_2026_PRECISION_OBSERVABLE_BLOCKED"
ECUT=1.6
MU0=160.
SM_REF=3.54e-4
SM_SIGMA=0.14e-4
EXPERIMENT_REF=3.49e-4
EXPERIMENT_SIGMA=0.19e-4
REFERENCE_LIMIT_MASS=670.
PURE_MASSES=(300.,450.,550.,600.,650.,670.,700.,800.,1000.)
PURE_TANB=(5.6,50.)
LIMIT_SCAN=(550.,600.,625.,640.,650.,655.,660.,665.,670.,675.,680.,690.,700.,725.,750.)
OBSERVABLE_OPERATORS=tuple(f"C{i}" for i in range(1,9))
BACKEND_PROTOCOL="zee-bsgamma-2026-nnlo-backend-v1"
RAW_BASIS="A1M_SuperIso_v5_CW_calculator_raw_operators_1to8_orders_0to2"
ALLOWED_BACKEND_ACTIONS={
    "describe","predict_sm","predict_typeii",
    "typeii_excluded_95","predict_twocharged_from_raw_superiso",
}
AUTHOR_CURVE_ABS_TOL=1.0e-6  # absolutely at most 0.01×10^-4; additional source tolerance configurable

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def finite(name,value,positive=False):
    if isinstance(value,bool):
        raise ValueError(f"{name} bool forbidden")
    try:
        f=float(value)
    except (TypeError,ValueError) as e:
        raise ValueError(f"{name} must be finite number") from e
    if not math.isfinite(f) or (positive and f<=0):
        raise ValueError(f"{name} invalid numeric value")
    return f

def read_source_e4a(path):
    p=Path(path)
    data=json.loads(p.read_text())
    if data.get("status")!=E4A_STATUS:
        raise ValueError("E4A source not completed successfully")
    summary=data.get("summary",{})
    if (summary.get("unique_27_Zee_spectra")!=27 or
        summary.get("Zee_original_gamma_coefficients_exported")!=648 or
        summary.get("all_source_matched_vendor_calls")!=216 or
        summary.get("all_8_operator_3_order_coefficients_inspected")!=5184 or
        summary.get("full_2026_TypeII_95CL_reproduced") is not False or
        data.get("2026_TypeII_670GeV_95CL_reproduced") is not False):
        raise ValueError("E4A provenance/precision state differs")
    rows=data.get("model_matching_rows",[])
    if len(rows)!=648:
        raise ValueError("Missing source-pinned 648 matched coefficient entries")
    by={}
    for item in rows:
        key=item["candidate_id"]
        order=int(item["order"])
        op=str(item["operator"])
        if order not in range(3) or op not in OBSERVABLE_OPERATORS:
            raise ValueError("Unsupported matching order/operator")
        by.setdefault(key,{})
        if (order,op) in by[key]:
            raise ValueError("Duplicated E4A coefficient")
        parts=[finite(k,item[k]) for k in
               ("source_SM","light_NP","heavy_NP","coherent_Zee_total")]
        by[key][order,op]=parts
    models=data.get("Zee_27_results",[])
    if len(models)!=27 or set(by)!={x["candidate_id"] for x in models}:
        raise ValueError("Original E4A model identities incorrect")
    for key,matches in by.items():
        if len(matches)!=24 or set(matches)!={
            (order,op) for order in range(3) for op in OBSERVABLE_OPERATORS}:
            raise ValueError("Incomplete source-pinned 24 operator-order entries")
    for row in models:
        ident=row["candidate_id"]
        gamma=finite("gamma",row["gamma"])
        m1=finite("mH1",row["mH1_GeV"],positive=True)
        m2=finite("mH2",row["mH2_GeV"],positive=True)
        t=finite("tanbeta",row["tanbeta"],positive=True)
        if not (0<gamma<math.pi/2 and m1<m2):
            raise ValueError("Original scalar ordering/mixing invalid")
        x=math.cos(gamma)**2
        y=math.sin(gamma)**2
        for coeff in by[ident].values():
            sm,l,h,total=coeff
            if abs(total-(sm+x*l+y*h))>3e-10:
                raise ValueError("E4A two-state source matching not closed")
    return data,models,by

def load_manifest(manifest_path,reference_path):
    manifest=json.loads(Path(manifest_path).read_text())
    reference=json.loads(Path(reference_path).read_text())
    if (manifest.get("protocol")!=BACKEND_PROTOCOL or
        manifest.get("published_source")!="arxiv:2608.29863" or
        manifest.get("full_2026_inclusive_observable") is not True or
        manifest.get("matching_basis_input")!=RAW_BASIS or
        manifest.get("supports_full_np_interference") is not True or
        manifest.get("supports_correlated_theory_likelihood") is not True):
        raise ValueError("External backend precision contract incomplete")
    command=manifest.get("command")
    if (not isinstance(command,list) or not command or
        not all(isinstance(x,str) and x.strip() for x in command)):
        raise ValueError("External backend must provide argv command list")
    if any("sh"==x or x.endswith("/sh") or x in ("bash","-c","python -c")
           for x in command):
        raise ValueError("Refuse shell-based backend code execution")
    source=manifest.get("implementation_source")
    if not isinstance(source,str) or len(source)<15:
        raise ValueError("Document the observable's actual implementation source")
    if not manifest.get("validated_operator_basis_conversion_source"):
        raise ValueError("Missing independent A1M-to-author operator basis conversion")
    if (reference.get("independent_from_tested_backend") is not True or
        reference.get("source_reference")!=manifest.get("published_source")):
        raise ValueError("Independent author benchmark source required")
    points=reference.get("pure_typeII_numerical_reference",[])
    if not isinstance(points,list) or len(points)<6:
        raise ValueError("Need >=6 independently supplied numeric Type-II holdouts")
    seen=set()
    for row in points:
        mass=finite("reference mass",row.get("mass_GeV"),positive=True)
        tanb=finite("reference tanbeta",row.get("tanbeta"),positive=True)
        br=finite("reference physical BR",row.get("BR"),positive=True)
        key=(mass,tanb)
        if key in seen:raise ValueError("Duplicate author reference mass/tanbeta")
        seen.add(key)
        if not (200<=mass<=3000 and .3<=tanb<=100):
            raise ValueError("Reference mass/tanbeta unsupported")
        if not 1e-6<br<1e-3:
            raise ValueError("Author Type-II BR units unexpected")
    if not {550.,650.,670.,700.,800.}.issubset(
        {float(x["mass_GeV"]) for x in points}):
        raise ValueError("Author Type-II reference curve lacks blinded mass anchors")
    return manifest,reference

def call_backend(command,action,payload):
    if action not in ALLOWED_BACKEND_ACTIONS:
        raise ValueError("Invalid external backend operation")
    request={"protocol":BACKEND_PROTOCOL,"action":action,
             "Egamma_cut_GeV":ECUT,"mu0_GeV":MU0,**payload}
    try:
        proc=subprocess.run(command,input=json.dumps(request)+"\n",
                            text=True,capture_output=True,timeout=90,
                            check=False)
    except (OSError,subprocess.TimeoutExpired) as exc:
        raise ValueError("Precision backend not executable") from exc
    if proc.returncode:
        raise ValueError(f"Precision backend failed {action}: "+
                         proc.stderr[-1200:])
    try:
        out=json.loads(proc.stdout)
    except (json.JSONDecodeError,UnicodeDecodeError) as e:
        raise ValueError("Precision backend response is not valid JSON") from e
    if (not isinstance(out,dict) or
        out.get("protocol")!=BACKEND_PROTOCOL or
        out.get("action")!=action or
        out.get("scientific_precision_level")!="FULL_2026_NNLO"):
        raise ValueError("Precision backend returned wrong status/protocol")
    return out

def prediction(out):
    central=finite("BR",out.get("BR"),positive=True)
    sigma=finite("sigma_theory",out.get("sigma_theory"),positive=True)
    if not(1e-8<=central<=1e-3 and 1e-8<=sigma<=1e-3):
        raise ValueError("Unphysical precision BR/sigma")
    if out.get("fully_correlated_with_SM_nuisances") is not True:
        raise ValueError("Uncorrelated or undocumented SM uncertainty")
    return central,sigma

def typeii_calibration(call,reference):
    desc=call("describe",{})
    caps=desc.get("validated_capabilities",[])
    needed={"SM_2026_NNLO","TypeII_2026_NNLO",
            "Zee_two_mixed_charged_from_raw_3order",
            "source_approved_A1M_basis_map","correlated_95CL"}
    if not isinstance(caps,list) or not needed.issubset(caps):
        raise ValueError("Backend does not implement required observable/likelihood")
    sm=call("predict_sm",{})
    c,s=prediction(sm)
    if (abs(c-SM_REF)>4e-7 or abs(s-SM_SIGMA)>4e-7):
        raise ValueError("2026 publication SM reference NOT reproduced")
    author_points=reference["pure_typeII_numerical_reference"]
    holdouts=[]
    for row in author_points:
        m,t=float(row["mass_GeV"]),float(row["tanbeta"])
        pred=call("predict_typeii",{"mass_GeV":m,"tanbeta":t})
        br,sigma=prediction(pred)
        # This tolerance cannot be broadened to fit the source.
        maxerr=min(AUTHOR_CURVE_ABS_TOL,float(row.get(
            "max_abs_deviation_BR",AUTHOR_CURVE_ABS_TOL)))
        if abs(br-float(row["BR"]))>maxerr:
            raise ValueError("Independent blind author Type-II BR curve mismatch")
        holdouts.append({"mass_GeV":m,"tanbeta":t,
                         "author_BR":float(row["BR"]),"reproduced_BR":br,
                         "residual":br-float(row["BR"]),
                         "allowed_reference_error":maxerr})
    # Require source's actual *95% CL statistic* at the Type-II boundary.
    # Do NOT choose an assumed 1-sided/2-sided delta-chi2 threshold.
    threshold=[]
    for mass in LIMIT_SCAN:
        out=call("typeii_excluded_95",{"mass_GeV":mass,"tanbeta":50.})
        if not isinstance(out.get("excluded_95"),bool):
            raise ValueError("Type-II 95% likelihood response is not bool")
        if out.get("confidence_procedure")!=reference.get(
            "confidence_procedure"):
            raise ValueError("95% CL likelihood convention differs from author")
        threshold.append({"mass_GeV":mass,"excluded":out["excluded_95"]})
    last_excluded=max([z["mass_GeV"] for z in threshold
                       if z["excluded"]],default=None)
    first_allowed=min([z["mass_GeV"] for z in threshold
                       if not z["excluded"]],default=None)
    if (last_excluded is None or first_allowed is None or
        not last_excluded<first_allowed or not 645<=last_excluded<=680 or
        not 660<=first_allowed<=695 or
        any(z["excluded"]!= (z["mass_GeV"]<=last_excluded) for z in threshold)):
        raise ValueError("Published 670 GeV Type-II 95% CL boundary NOT reproduced")
    # Author may publish a rounded boundary; independently require an
    # interpolation scan at fixed mass grid instead of forcing 670 exact.
    return {"SM_2026":{"BR":c,"sigma":s},"independent_author_holdouts":holdouts,
            "typeII_95_boundary_scan":threshold,
            "last_excluded_mass_GeV":last_excluded,
            "first_allowed_mass_GeV":first_allowed,
            "SM_author_reference_reproduced":True,
            "TypeII_published_670_limit_independently_reproduced":True}

def ordered_matching(rows):
    return [
        {"order":order,"operator":op,
         "SM":rows[order,op][0],
         "NP_light":rows[order,op][1],
         "NP_heavy":rows[order,op][2]}
        for order in range(3) for op in OBSERVABLE_OPERATORS
    ]

def zee_predictions(call,models,by):
    results=[]
    for i,model in enumerate(models,1):
        id=model["candidate_id"]
        m1,m2,t,g=(float(model[k]) for k in (
           "mH1_GeV","mH2_GeV","tanbeta","gamma"))
        raw=ordered_matching(by[id])
        base={"mH1_GeV":m1,"mH2_GeV":m2,
              "tanbeta":t,"matching_raw_basis":RAW_BASIS,
              "coefficient_rows":raw,
              "SM_subtraction_and_NP_interference_in_backend":True}
        # Pure-state checks must reproduce independent Type-II backend
        # *on the exact same masses and quark normalization*.
        for angle,mass in ((0.,m1),(math.pi/2,m2)):
            m=call("predict_twocharged_from_raw_superiso",
                   {**base,"gamma":angle})
            p=call("predict_typeii",{"mass_GeV":mass,"tanbeta":t})
            left,sl=prediction(m)
            right,sr=prediction(p)
            if abs(left-right)>4e-7 or abs(sl-sr)>4e-7:
                raise ValueError("E4A raw NNLO basis/pure Type-II observable nonclosure")
        val=call("predict_twocharged_from_raw_superiso",
                 {**base,"gamma":g})
        br,sigma=prediction(val)
        # Never apply the Type-II *single-state* 670 mass limit to mixed
        # Zee model. Only record the genuine source-valid model BR here.
        item={"candidate_id":id,"mH1_GeV":m1,"mH2_GeV":m2,
              "gamma":g,"tanbeta":t,
              "2026_NNLO_two_state_BR":br,
              "sigma_theory_correlated":sigma,
              "source_pure_state_consistency_checked":True,
              "Zee_full_global_model_allowed":"UNKNOWN",
              "2026_NNLO_experimental_Zee_exclusion":
                  "NOT_EVALUATED_GLOBAL_LIKELIHOOD"}
        results.append(item)
        print("E4B_FULL_OBSERVABLE",f"{i}/27",id,
              "BR",br,"sigma_theory",sigma,
              "full_Zee_global_model_allowed_UNKNOWN",flush=True)
    return results

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--e4a-summary",type=Path,required=True)
    p.add_argument("--backend-manifest",type=Path)
    p.add_argument("--author-reference",type=Path)
    p.add_argument("--audit-only",action="store_true")
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        p.error("Refuse overwrite existing E4B report")
    args.output_dir.mkdir(parents=True,exist_ok=True)
    status=BLOCKED
    report={
        "status":BLOCKED,"full_2026_Zee_NNLO_prediction":False,
        "TypeII_670GeV_2026_95CL_reproduced":False,
        "global_Zee_allowed":None,"source_paper":"arxiv:2608.29863v1",
        "observable":"BR(B->Xsgamma), Egamma>1.6 GeV",
        "precision_source_unavailable_in_repo":True,
    }
    try:
        data,models,by=read_source_e4a(args.e4a_summary)
        report["e4a_verified_source_SHA256"]=digest(args.e4a_summary)
        if args.audit_only:
            report["blocking_reason"]=(
                "The 2026 paper's Eq(4) and A1M/E4A raw matching do not "
                "provide full NNLO rate tensors, correlated nuisance likelihood "
                "or author Type-II numeric mass curve. Require genuine "
                "backend manifest and independent author holdout reference."
            )
            print("E4B_SOURCE_BLOCKED",report["blocking_reason"],flush=True)
            return 0
        if args.backend_manifest is None or args.author_reference is None:
            raise ValueError(
                "No genuine external 2026 NNLO backend + independent author "
                "Type-II mass curve supplied; NOT computing spurious rate.")
        manifest,source=load_manifest(
            args.backend_manifest,args.author_reference)
        report["backend_SHA256"]=digest(args.backend_manifest)
        report["reference_SHA256"]=digest(args.author_reference)
        command=manifest["command"]
        def call(action,payload):
            return call_backend(command,action,payload)
        pure=typeii_calibration(call,source)
        report["pure_TypeII_validation"]=pure
        report["TypeII_670GeV_2026_95CL_reproduced"]=True
        results=zee_predictions(call,models,by)
        if len(results)!=27:
            raise ValueError("Unexpected Zee two-state observable population")
        report.update(status=STATUS,
            full_2026_Zee_NNLO_prediction=True,
            precision_source_unavailable_in_repo=False,
            implementation_source=manifest["implementation_source"],
            NNLO_2026_Zee_27=results,
            cohort={"spectra":27,
                    "minimum_BR":min(z["2026_NNLO_two_state_BR"] for z in results),
                    "median_BR":statistics.median(
                        z["2026_NNLO_two_state_BR"] for z in results),
                    "maximum_BR":max(z["2026_NNLO_two_state_BR"] for z in results),
                    "Zee_exclusion_from_complete_likelihood":"NOT_COMPUTED",
                    "full_global_Zee_viability":"UNKNOWN"}
        )
        outfile=args.output_dir/"source_validated_2026_NNLO_twocharged_27_NOT_GLOBAL_ALLOWED.csv"
        with outfile.open("w",newline="") as h:
            w=csv.DictWriter(h,fieldnames=list(results[0]))
            w.writeheader();w.writerows(results)
        report["csv"]=str(outfile)
        print("E4B_COHORT",json.dumps(report["cohort"]),flush=True)
        return 0
    except Exception as exc:
        report.update(status=FAILED,error=repr(exc),
                      traceback=traceback.format_exc())
        print("E4B_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
        return 1
    finally:
        location=args.output_dir/"summary.json"
        location.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
        print("E4B_SUMMARY",location,flush=True)

if __name__=="__main__":
    raise SystemExit(main())
