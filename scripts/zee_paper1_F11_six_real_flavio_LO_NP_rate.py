#!/usr/bin/env python3
"""F11: six NEW Zee benchmarks, source-validated LO NP C7/C8 -> real flavio inclusive rate.

Unlike the F10 historical SuperIso full BR, this re-injects the correct
coherent two-charged-scalar LO NP matching coefficients (not an average
of two BRs) into flavio/wilson inclusive BR(B->Xsgamma).

IMPORTANT: this is an *older published-era flavio-rate / LO Zee NP matching
hybrid*, not full 2026 NNLO NP matching, Type-II 670-GeV exclusion, full
uncertainty likelihood, or model-allowed classification. DO NOT replace
the flavio SM baseline with the 2026 SM value. No ad hoc scale variations
claim to be a perturbative error estimate.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import os
import subprocess
from pathlib import Path
import statistics
import sys
import traceback

from gateA1r_run_br_pilot import compile_pilot
from gateA1s_run_modern_2026_screen import (
    linearized_2026,parse_probe as parse_a1s_probe,MODERN_SM,PDG_EXP,K7,K8,
)
from zee_gateE4a_integrated_precision_matching_calibration import (
    run_matching as e4a_run_matching,
)
from zee_gateF1_peerreviewed_flavio_27_observable import (
    FlavioEngine,no_np_test,basis_derivative_test,
    SM_2015_SIGMA,EXP,EXP_SIGMA,STATUS as F1_STATUS,
)
from zee_gateF7_309_2026_bsgamma_tension_sensitivity import (
    ROOT,load_f6,digest,load,writejson,
)
from zee_gateF8_309_670TypeII_same_legacy_kernel_and_mixing import archive_bin
from zee_paper1_F10_six_new_two_charged_legacy_bsgamma import (
    read_scan,SCALAR,RANKED,
    STATUS as F10_STATUS,
)

STATUS="F11_REAL_FLAVIO_LO_ZEE_NP_2015_RATE_SIX_NOT_MODERN_NNLO_EXCLUSION"
BLOCKED="F11_SOURCE_OR_NUMERIC_BACKEND_FAILED_NOT_EXCLUSION"
MISSING=(
    "full 2026 matched inclusive NNLO BSM C1-C8, matrix elements and "
    "nonperturbative terms (Misiak et al. 2608.29863)",
    "2026 complete Type-II 670 GeV calibrated independent rate and 95% CL",
    "correlated SM, BSM perturbative and experimental likelihood uncertainties",
    "complete Zee lepton LFV / quark alignment / neutrino likelihood / "
    "HiggsTools / vacuum and physical hadron collider signal rate",
)
F10CSV="F10_six_full_legacy_Bsgamma_same_kernel_NOT_EXCLUSION.csv"
F11CSV="F11_six_Zee_real_flavio_LO_C7C8_2015rate_NOT_EXCLUSION.csv"
MU0=160.
PURE_MASSES=(300.,450.,550.,600.,650.,670.,700.,800.,1000.)
PURE_TANB=(5.6,50.)
RTOL=6e-12

def finite(x,label):
    if isinstance(x,bool):raise ValueError(label+" boolean")
    value=float(x)
    if not math.isfinite(value):raise ValueError(label+" nonfinite")
    return value

def close(a,b,label,rtol=2e-9,atol=2e-12):
    if not math.isclose(finite(a,label),finite(b,label),
                        rel_tol=rtol,abs_tol=atol):
        raise ValueError("F11 source/physical mismatched "+label)

def load_f10(folder,six):
    folder=Path(folder).resolve()
    summ=load(folder/"summary.json")
    man=load(folder/"manifest.json")
    if (summ.get("status")!=F10_STATUS or
        summ.get("evaluated_new_P1_scalar_points")!=6 or
        summ.get("full_Zee_model_allowed_or_excluded") is not None or
        summ.get("modern_2026_Zee_BtoXsGamma_likelihood_completed") is not False or
        man.get("summary_SHA256")!=digest(folder/"summary.json") or
        man.get("status")!=summ.get("status") or
        summ.get("CSV_SHA256")!=digest(folder/F10CSV)):
        raise ValueError("F10 original same-kernel SuperIso source corrupted")
    with (folder/F10CSV).open(newline="") as stream:
        rows=list(csv.DictReader(stream))
    if len(rows)!=6 or {x["candidate_id"] for x in rows}!={x["id"] for x in six}:
        raise ValueError("F10 and paper-1 six-point cohort identity disagrees")
    joined={x["candidate_id"]:x for x in rows}
    for row in six:
        q=joined[row["id"]]
        for a,b in (("mH1","mH1_GeV"),("mH2","mH2_GeV"),
                    ("gamma","gamma"),("tanbeta","tanbeta")):
            close(row[a],q[b],row["id"]+" "+a)
        if q.get("physical_full_Zee_allowed_or_excluded","") not in ("","None","null"):
            raise ValueError("F10 incorrectly asserts full model allowance")
    return joined,summ

def verify_f6(f6,summ_f10):
    original,prov=load_f6(f6)
    executable,pin=archive_bin(f6)
    if len(original)!=309:
        raise ValueError("F6 legacy validation did not certify 309 input models")
    if (summ_f10.get("source",{}).get("F6_summary_SHA256")!=digest(f6/"summary.json") or
        summ_f10.get("source",{}).get("F6_manifest_SHA256")!=digest(f6/"manifest.json") or
        summ_f10.get("source",{}).get("executable_SHA256")!=pin["executable_SHA256"]):
        raise ValueError("F10 run used DIFFERENT pinned F6 library/executable")
    f6sum=load(f6/"summary.json")
    args=f6sum["source_provenance"]["new_C_executable"]["command"]
    libs=[Path(x) for x in args if str(x).endswith("/src/libsuperiso.a")]
    if len(libs)!=1 or not libs[0].is_file():
        raise ValueError("Original F6 vendor static library path ambiguous")
    vendor=libs[0].parent.parent.resolve()
    if digest(libs[0])!=f6sum["source_provenance"][
          "new_C_executable"]["vendor_library_sha256"]:
        raise ValueError("F6 pinned static SuperIso library CHANGED")
    return vendor,prov,pin

def compile_source(f6,summ_f10,output):
    vendor,source,pin=verify_f6(f6,summ_f10)
    driver=ROOT/"scripts"/"zee_gateE4a_full_order_matching_probe.c"
    path=output/"f11_same_source_E4A_matching"
    build=compile_pilot(vendor,path,driver,False)
    cross_driver=ROOT/"scripts"/"gateA1s_probe_modern_2026_lo.c"
    cross_path=output/"f11_independent_A1S_2026_EQ4_LO_matching"
    cross_build=compile_pilot(vendor,cross_path,cross_driver,False)
    if cross_build["library_SHA256"]!=build["library_SHA256"]:
        raise ValueError("F11 A1S/E4A independent sources linked different libraries")
    if (build["library_SHA256"]!=load(f6/"summary.json")[
         "source_provenance"]["new_C_executable"]["vendor_library_sha256"]):
        raise ValueError("E4A matching static library differs from original F6")
    return path,cross_path,{"vendor_static_library_SHA256":build["library_SHA256"],
                 "independent_A1S_driver_SHA256":cross_build["driver_SHA256"],
                 "independent_A1S_binary_SHA256":digest(cross_path),
                 "matching_driver_SHA256":build["driver_SHA256"],
                 "matching_executable_SHA256":digest(path),
                 "historical_F6_executable_SHA256":pin["executable_SHA256"],
                 "F6_original_source_hashes":source,
                 "compilation_command":build["compiler_command"]}

def matching(probe,m1,m2,t,g,runner=e4a_run_matching):
    obj=runner(probe,m1,m2,t,g)
    x=obj["input"]
    for name,want in (("mH1",m1),("mH2",m2),
                      ("tanbeta",t),("gamma",g),("mu0",MU0)):
        close(x[name],want,"E4A "+name,rtol=2e-11,atol=1e-9)
    if abs(x["w1"]+x["w2"]-1.)>1e-12:
        raise ValueError("E4A charged-doublet weights do not sum to one")
    rows=obj["coefficient_rows"]
    if len(rows)!=24:raise ValueError("Missing all E4A source C1-C8 x LO/NLO/NNLO")
    if obj["max_coherent_Wilson_residual"]>4e-12:
        raise ValueError("E4A raw Wilson superposition mismatch")
    for op in (7,8):
        for q in (0,1,2):
            a,b,c,m=[finite(v,f"C{op} order{q}")
                       for v in rows[q,op]]
            close(m,a+x["w1"]*b+x["w2"]*c,
                  f"C{op} order{q} coherence",atol=4e-12)
    return obj

def independent_a1s_coefficients(cross_probe,mass,tanbeta):
    if cross_probe is None:
        return None
    call=[str(Path(cross_probe).resolve()),f"{mass:.17g}",f"{tanbeta:.17g}"]
    result=subprocess.run(call,capture_output=True,text=True,timeout=90,check=False)
    if result.returncode:
        raise ValueError("A1S independently compiled 2026 source failed "
                         +result.stderr[-1400:]+result.stdout[-1400:])
    got=parse_a1s_probe(result.stdout,mass,tanbeta)
    return got["delta_C7_LO"],got["delta_C8_LO"]

def cross_check_a1s_vs_e4a(cross_probe,mass,tanbeta,c7,c8):
    if cross_probe is None:return False
    observed=independent_a1s_coefficients(cross_probe,mass,tanbeta)
    close(observed[0],c7,"2026 Eq4 independently sourced C7",rtol=2e-9,atol=3e-12)
    close(observed[1],c8,"2026 Eq4 independently sourced C8",rtol=2e-9,atol=3e-12)
    return True

def coeff(obj,op):
    a,b,c,m=obj["coefficient_rows"][0,op]
    x=obj["input"]
    d=x["w1"]*b+x["w2"]*c
    close(m-a,d,f"C{op} LO combined source")
    return float(b),float(c),float(d)

def controls(engine,probe,runner=e4a_run_matching,cross_probe=None):
    """Independent TypeII source + proper flavio response (not a 2026 CL)."""
    sm=no_np_test(engine)
    engine._sm=sm["flavio_SM"]
    derivative=basis_derivative_test(engine,engine._sm)
    if (not sm["flavio_matches_2015_SM_within_0p20e_4"] or
        not derivative["both_operator_derivative_sign_and_scale_consistent"]):
        raise ValueError("flavio SM/2015 derivative C7 C8 basis closure failed")
    # A second, intentionally non-identical 2026 published Eq.(4)
    # normalization check. 15% is a *cross-era* plausibility gate,
    # not proof that 2015 NLO and 2026 NNLO matrix elements coincide.
    modern={7:K7*1e-4,8:K8*1e-4}
    eq4_dev={}
    for i in (7,8):
        slope=derivative[f"C{i}"]["observed_dBR_dC"]
        eq4_dev[f"C{i}"]=abs(slope-modern[i])/abs(modern[i])
        if not slope<0 or eq4_dev[f"C{i}"]>0.15:
            raise ValueError("flavio WET operator normalization/sign incompatible "
                             "with 2026 Eq4 at 15% exploratory tolerance")
    engine._slopes={7:derivative["C7"]["observed_dBR_dC"],
                    8:derivative["C8"]["observed_dBR_dC"]}
    pure=[]
    for t in PURE_TANB:
        ordered=[]
        for mass in PURE_MASSES:
            src=matching(probe,mass,mass,t,.39,runner=runner)
            a7,b7,d7=coeff(src,7)
            a8,b8,d8=coeff(src,8)
            close(a7,b7,"equal-mass C7 independent pure TypeII",rtol=2e-9)
            close(a8,b8,"equal-mass C8 independent pure TypeII",rtol=2e-9)
            cross_check_a1s_vs_e4a(cross_probe,mass,t,d7,d8)
            q=engine.prediction(d7,d8)
            # Pure Type-II at LO must have a positive and decoupling NP contribution.
            if q<=engine._sm:raise ValueError("Pure TypeII LO coefficient has wrong sign")
            ordered.append(q)
            pure.append({"mass_GeV":mass,"tanbeta":t,
                         "LO_dC7":d7,"LO_dC8":d8,"BR_hybrid":q,
                         "published_2026_670_limit_reproduced":False})
        for a,b in zip(ordered[:-1],ordered[1:]):
            if a+3e-9 < b:raise ValueError("Pure TypeII mass decoupling broken")
    return {"SM_2015_rate":sm,"2015_C7_C8_derivative":derivative,
            "crosscheck_2026_Eq4_slope_fractions":eq4_dev,
            "A1S_independent_crosscheck_on_18_TypeII":cross_probe is not None,
            "pure_TypeII_18":pure,"all_pass":True,
            "does_not_reproduce_2026_TypeII_670GeV_CL":True}

def six_rates(engine,probe,six,f10,runner=e4a_run_matching,cross_probe=None):
    out=[]
    for i,src in enumerate(six,1):
        key=src["id"]
        m1,m2,g,t=[finite(src[k],k) for k in
                   ("mH1","mH2","gamma","tanbeta")]
        obj=matching(probe,m1,m2,t,g,runner=runner)
        l7,h7,d7=coeff(obj,7)
        l8,h8,d8=coeff(obj,8)
        c=math.cos(g)**2;s=math.sin(g)**2
        close(d7,c*l7+s*h7,"C7 exact weighted NP")
        close(d8,c*l8+s*h8,"C8 exact weighted NP")
        cross_check_a1s_vs_e4a(cross_probe,m1,t,l7,l8)
        cross_check_a1s_vs_e4a(cross_probe,m2,t,h7,h8)
        pure_l=engine.prediction(l7,l8)
        pure_h=engine.prediction(h7,h8)
        actual=engine.prediction(d7,d8)
        # Independent endpoints must match physical pure-state rates.
        if not min(pure_l,pure_h)-5e-9 <= actual <= max(pure_l,pure_h)+5e-9:
            raise ValueError("Flavio quadratic result outside pure states")
        if not all(1e-7<val<1e-3 for val in (pure_l,pure_h,actual)):
            raise ValueError("flavio hybrid outside physical screen")
        # A physically interpretable same-engine *diagnostic reference* at
        # each original benchmark tanbeta, never a 2026 95%-CL bound.
        ref=matching(probe,670.,670.,t,.39,runner=runner)
        rl7,rh7,rd7=coeff(ref,7)
        rl8,rh8,rd8=coeff(ref,8)
        close(rl7,rh7,"same-mass TypeII670 C7")
        close(rl8,rh8,"same-mass TypeII670 C8")
        cross_check_a1s_vs_e4a(cross_probe,670.,t,rd7,rd8)
        br670=engine.prediction(rd7,rd8)
        ref_shift=br670-engine._sm
        mix_shift=actual-engine._sm
        if ref_shift<=0:
            raise ValueError("TypeII670 same-flavio matching shift must be constructive")
        hybrid_ratio=mix_shift/ref_shift
        modern_z=linearized_2026(d7,d8)
        modern_ref=linearized_2026(rd7,rd8)
        modern_br=modern_z["linearized_predicted_central_times_1e4"]*1e-4
        modern_ref_br=modern_ref["linearized_predicted_central_times_1e4"]*1e-4
        modern_ratio=modern_z["linearized_shift_times_1e4"]/modern_ref[
            "linearized_shift_times_1e4"] if abs(modern_ref[
            "linearized_shift_times_1e4"])>1e-15 else None
        gaussian_z=(modern_br-PDG_EXP["central_times_1e4"]*1e-4) / (
             math.hypot(MODERN_SM["sigma_times_1e4"],
                        PDG_EXP["sigma_times_1e4"])*1e-4)
        slopes=getattr(engine,"_slopes",None)
        if slopes is None:
            # Test doubles only; actual run must always validate slopes.
            quadr_fraction=None
        else:
            linear_2015=slopes[7]*d7+slopes[8]*d8
            quadratic_residual=mix_shift-linear_2015
            quadr_fraction=(abs(quadratic_residual)/abs(linear_2015)
                            if abs(linear_2015)>1e-16 else None)
        historical=f10[key]
        row={
          "candidate_id":key,"mH1_GeV":m1,"mH2_GeV":m2,
          "gamma":g,"tanbeta":t,
          "C7_LO_light":l7,"C7_LO_heavy":h7,"C7_LO_mixed":d7,
          "C8_LO_light":l8,"C8_LO_heavy":h8,"C8_LO_mixed":d8,
          "BR_flavio_2015_SM_reference":engine._sm,
          "BR_flavio_LO_NP_hybrid":actual,
          "BR_flavio_LO_NP_pure_light":pure_l,
          "BR_flavio_LO_NP_pure_heavy":pure_h,
          "BSM_rate_shift_flavio_hybrid_minus_same_flavio_SM":mix_shift,
          "BR_flavio_TypeII670_same_tanbeta_hybrid":br670,
          "LO_C7_TypeII670":rd7,
          "LO_C8_TypeII670":rd8,
          "Zee_to_TypeII670_same_flavio_NP_rate_shift_NOT_CL":hybrid_ratio,
          "BR_2026_published_Eq4_LINEARIZED":modern_br,
          "BR_2026_Eq4_TypeII670_same_tanbeta_LINEARIZED":modern_ref_br,
          "Zee_to_TypeII670_2026_Eq4_LINEAR_NP_SHIFT_NOT_CL":modern_ratio,
          "Z_2026_Eq4_linearized_vs_experiment_uncalibrated_NOT_CL":gaussian_z,
          "flavio_quadratic_fraction_from_2015_response_DIAGNOSTIC":
              quadr_fraction,
          "2026_150GeV_source_crosschecked_A1S_vs_E4A":cross_probe is not None,
          "BR_SuperIso_historical_separate_scheme":float(historical[
              "legacy_SuperIso_full_Zee_BR_Egamma1p6_NOT_2026"]),
          "ratio_to_670_TypeII_legacy_reference_NOT_95CL":float(historical[
              "Zee_to_TypeII670_legacy_NP_shift_ratio_NOT_CL"]),
          "included_cascade_proxy_NOT_physical_pb":float(historical[
              "P1_general_lepton_included_cascade_proxy_NOT_pb"]),
          "LFV_subset_max_ratio_NOT_physical":float(historical[
              "partial_LFV_max_ratio_NOT_PHYSICAL_CL"]),
          "exp_2026_central_BR_comparison_DIAGNOSTIC_ONLY":EXP,
          "z_exp_plus_2015_SM_sigma_DIAGNOSTIC_ONLY":
              (actual-EXP)/math.hypot(EXP_SIGMA,SM_2015_SIGMA),
          "modern_NNLO_Zee_2026_95CL":None,
          "fully_Zee_allowed_or_excluded":None,
          "physical_Zee_hadronic_R_tbZ_pb":None,
          "status":STATUS,
        }
        out.append(row)
        print("F11_SIX",i,"/6",key,"2015_era_flavio_LO_BSM_BR",
              format(actual,".11g"),"C7",format(d7,".7g"),
              "C8",format(d8,".7g"),
              "R_flavio_670",format(hybrid_ratio,".7g"),
              "BR_2026_Eq4",format(modern_br,".10g"),
              "Z_Eq4_DIAGNOSTIC",format(gaussian_z,".5g"),
              "NO_2026_EXCLUSION",flush=True)
    return out

def run(args,engine=None):
    if args.output_dir.exists():
        raise FileExistsError("Refuse to overwrite existing F11 run")
    six,flavor,pr=read_scan(args.scan_dir)
    f10,f10report=load_f10(args.f10_dir,six)
    f6=Path(f10report["source"]["original_F6_dir"]).resolve()
    if args.f6_dir is not None and args.f6_dir.resolve()!=f6:
        raise ValueError("Override F6 differs from source recorded in F10")
    output=args.output_dir.resolve()
    if not ROOT.resolve().is_relative_to(Path("/home")):
        raise ValueError("F11 scientific runner only from /home source checkout")
    if not output.is_relative_to(ROOT/"work"):
        raise ValueError("F11 output must stay in source /home/work tree")
    output.mkdir(parents=True,exist_ok=False)
    summary={"status":BLOCKED,"full_Zee_allowed_or_excluded":None,
             "genuine_2026_NNLO_matching_and_likelihood":False}
    try:
        probe,cross_probe,prov=compile_source(f6,f10report,output)
        if engine is None:engine=FlavioEngine()
        calibration=controls(engine,probe,cross_probe=cross_probe)
        rows=six_rates(engine,probe,six,f10,cross_probe=cross_probe)
        if len(rows)!=6 or len({r["candidate_id"] for r in rows})!=6:
            raise ValueError("F11 source six identity mismatch")
        with (output/F11CSV).open("w",newline="") as f:
            csv_writer=csv.DictWriter(f,fieldnames=list(rows[0]))
            csv_writer.writeheader();csv_writer.writerows(rows)
        vals=sorted(q["BR_flavio_LO_NP_hybrid"] for q in rows)
        modern_vals=sorted(q["BR_2026_published_Eq4_LINEARIZED"]
                            for q in rows)
        summary={
            "status":STATUS,
            "six_new_zee_matched_LO_BSM_2015_era_flavio_inclusive_rates":len(rows),
            "flavio_version":getattr(engine,"flavio_version","unknown"),
            "wilson_version":getattr(engine,"wilson_version","unknown"),
            "flavio_calls":engine.calls,
            "SM_2015_and_full_18_TypeII_reference_controls":calibration,
            "SM_2015_zero_NP_BR":engine._sm,
            "Zee_hybrid_BR_min_median_max":[vals[0],statistics.median(vals),vals[-1]],
            "2026_published_Eq4_linearized_BR_min_median_max":
                [modern_vals[0],statistics.median(modern_vals),modern_vals[-1]],
            "2026_Eq4_is_linearized_LO_approx_not_NNLO_2HDM_rate":True,
            "A1S_vs_E4A_independent_matching_source_crosscheck":True,
            "source":{"paper1":pr,
                      "F10_summary_SHA256":digest(args.f10_dir/"summary.json"),
                      "F10_csv_SHA256":digest(args.f10_dir/F10CSV),
                      "F6_summary_SHA256":digest(f6/"summary.json"),
                      "compiled_E4A":prov,
                      "current_F11_SHA256":digest(Path(__file__))},
            "accuracy":"LO_NP_dC7_dC8_160GeV_2015era_flavio_selected_NNLO_rate",
            "genuine_2026_NNLO_matching_and_likelihood":False,
            "model_specific_theory_uncertainty_calibrated":False,
            "modern_2026_Zee_exclusions":None,
            "full_Zee_allowed_or_excluded":None,
            "paper1_GO_or_NOGO":None,
            "missing_full_physics":MISSING,
            "output_csv_SHA256":digest(output/F11CSV),
        }
        writejson(output/"summary.json",summary)
        writejson(output/"manifest.json",{
            "status":STATUS,"summary_SHA256":digest(output/"summary.json"),
            "source":summary["source"]})
        print("F11_STATUS",STATUS,"SIX",len(rows),"2026_CL",None,flush=True)
        print("F11_SUMMARY",output/"summary.json",flush=True)
        return 0
    except Exception as exc:
        summary["error"]=repr(exc)
        summary["traceback"]=traceback.format_exc()
        writejson(output/"error.json",summary)
        print("F11_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
        traceback.print_exc()
        return 1

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scan-dir",type=Path,
     default=ROOT/"work"/"zee_paper1_florentino_pilot_20261021T111413Z")
    p.add_argument("--f10-dir",type=Path,required=True)
    p.add_argument("--f6-dir",type=Path)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(argv)
    return run(a)
if __name__=="__main__":
    raise SystemExit(main())
