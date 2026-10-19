#!/usr/bin/env python3
"""One-command integrated Zee quark-alignment software/physics-input audit.

Runs the relevant Q1/Q2a/Q2b/B2/B3/partial-LFV regression suites, checks
all STORED candidate-B2 neutrino solutions, bridges their Chen Yukawas to
FLS Pi1/Pi2, and evolves their lepton inputs through the existing
TRUNCATED pure-2HDM Yukawa RGEs with a control and convergence check.

This is ONE LARGE NUMERICAL VALIDATION. It is NOT a full Zee RGE, modern
NuFIT likelihood, complete LFV, hadronic FCNC limit, or allowed point.
No new Yukawa random scan. No external code installation. NumPy needed;
optional SciPy-only Barr-Zee suites run when SciPy is available.

Cannot silently skip failed REQUIRED tests. Always produces a JSON
status report for reproducibility. Exit !=0 if a required gate fails.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/"scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0,str(SCRIPTS))

import numpy as np
from gateB3_general_zee_charged_lepton_widths import complex_matrix
from zee_section8_Q2b_chen_FLS_matching_gate import (
    read_scalar_points,validate_B2_solution,bridge_chen_y_to_fls
)
from zee_section8_quark_alignment_one_loop_gate import (
    beta_quarks_2hdm
)
from zee_section8_quark_alignment_truncated_flow import (
    evolve,physical_offdiagonals
)
from zee_section8_Q2c_UV_EFT_scope_audit import (
    charged_matrix_audit,gauge_audit
)
from zee_section8_Q2d_lepton_spurion_scalar_RG_audit import (
    stored_audit as zee_spurion_audit
)
from zee_section8_Q2e_kanemura2001_reduced_f_RGE import (
    run as historical_2001_reduced_f_run
)
from zee_section8_Q3_generic_scalar_bfb_witness import (
    reference_diagnostics as q3_quartic_diagnostics
)

STATUS="Q2_INTEGRATED_NUMERICAL_AUDIT_ONLY_NOT_FULL_ZEE_OR_ALLOWED"
REQUIRED_TEST_FILES=(
    "test_gateA1b_hierarchical_no_seed.py",
    "test_gateA1c_charged_singlet_lfv.py",
    "test_gateA1d_neutral_tree_lfv.py",
    "test_gateA1e_neutral_one_loop_dipoles.py",
    "test_gateA1f_charged_doublet_y_dipoles.py",
    "test_gateB2_zee_neutrino_family_scan.py",
    "test_gateB3_general_zee_charged_lepton_widths.py",
    "test_zee_lfv_backend.py",
    "test_zee_pipeline.py",
    "test_zee_section8_quark_alignment_one_loop_gate.py",
    "test_zee_section8_quark_alignment_truncated_flow.py",
    "test_zee_section8_Q2b_chen_FLS_matching_gate.py",
    "test_zee_section8_run_integrated_Q2_validation.py",
    "test_zee_section8_Q2c_UV_EFT_applicability.py",
    "test_zee_section8_Q2d_lepton_spurion_scalar_RG_audit.py",
    "test_zee_section8_Q2e_kanemura2001_reduced_f_RGE.py",
    "test_zee_section8_Q3_generic_scalar_bfb_witness.py",
)
OPTIONAL_SCIPY_TEST_FILES=(
    "test_zee_barr_zee_kernels.py",
    "test_zee_barr_zee_fermion_dipoles.py",
)
MISSING_PHYSICS=(
    "complete Zee singlet-f coupled RGEs and physical thresholds",
    "modern NuFIT correlated likelihood / current general-Zee neutrino fit",
    "full coherent LFV including all relevant Barr-Zee, conversion, 3-body amplitudes",
    "measured quark CKM and renormalized masses / electroweak gauge running",
    "physical FCNC Wilson coefficients and meson likelihoods",
    "complete two-charged-scalar B -> X_s gamma, vacuum, HiggsTools and rates",
)

def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        while True:
            block=f.read(1024*1024)
            if not block:
                break
            h.update(block)
    return h.hexdigest()

def run_tests(logfile,timeout=240):
    tests=[]
    scipy_present=importlib.util.find_spec("scipy") is not None
    files=list(REQUIRED_TEST_FILES)
    if scipy_present:
        files+=list(OPTIONAL_SCIPY_TEST_FILES)
    logfile.parent.mkdir(parents=True,exist_ok=True)
    with logfile.open("w",encoding="utf-8") as handle:
        for filename in files:
            label=filename.removeprefix("test_").removesuffix(".py")
            cmd=[sys.executable,"-m","unittest","discover",
                 "-s","tests","-p",filename,"-v"]
            start=time.monotonic()
            try:
                proc=subprocess.run(
                    cmd,cwd=ROOT,stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,text=True,
                    timeout=timeout,check=False)
                output=proc.stdout
                ok=(proc.returncode==0 and
                    re.search(r"\bRan\s+(\d+)\s+tests?\b",output) is not None and
                    re.search(r"(?m)^OK(?:\s*\(|\s*$)",output) is not None)
                count_match=re.search(r"\bRan\s+(\d+)\s+tests?\b",output)
                count=int(count_match.group(1)) if count_match else None
                rc=proc.returncode
                error=None
            except subprocess.TimeoutExpired as exc:
                output=(exc.stdout or b"")
                if isinstance(output,bytes):
                    output=output.decode("utf-8","replace")
                output+="\nTIMEOUT: test suite exceeded %ds\n"%timeout
                rc=None
                count=None
                error="TIMEOUT"
                ok=False
            elapsed=time.monotonic()-start
            handle.write("="*76+"\n"+filename+"\n"+"="*76+"\n")
            handle.write(output+"\n")
            handle.flush()
            result={"suite":label,"required":filename in REQUIRED_TEST_FILES,
                    "passed":bool(ok),"tests_run":count,
                    "exit_code":rc,"seconds":round(elapsed,3),
                    "error":error}
            tests.append(result)
            print("TEST_SUITE",label,"PASS" if ok else "FAIL",
                  "N",count,"SECONDS",round(elapsed,2),flush=True)
        if not scipy_present:
            handle.write("SciPy unavailable: TWO Barr-Zee optional suites NOT RUN\n")
            for filename in OPTIONAL_SCIPY_TEST_FILES:
                tests.append({
                    "suite":filename.removeprefix("test_").removesuffix(".py"),
                    "required":False,"passed":None,
                    "tests_run":None,"exit_code":None,"seconds":0.,
                    "error":"SCIPY_UNAVAILABLE_OPTIONAL_NOT_RUN"})
            print("OPTIONAL_SCIPY_BARR_ZEE_SUITES NOT_RUN",flush=True)
    return tests,scipy_present

def quark_boundary(tanbeta,pi1,pi2):
    """Same deliberately TOY CKM/masses as original Q2a experiment."""
    if not 0<tanbeta<1.e5:
        raise ValueError("Invalid matching tanbeta")
    c=1/math.hypot(1.,tanbeta)
    s=tanbeta*c
    a=.225
    b=.041
    R12=np.array([[math.cos(a),math.sin(a),0.],
                  [-math.sin(a),math.cos(a),0.],[0.,0.,1.]])
    R23=np.array([[1.,0.,0.],
                  [0.,math.cos(b),math.sin(b)],
                  [0.,-math.sin(b),math.cos(b)]])
    Vckm=R23@R12
    yd=np.diag([.000027,.00056,.024])
    yu=Vckm.conj().T@np.diag([.000013,.0073,.95])
    zero=np.zeros((3,3),complex)
    return np.asarray((yd/c,zero,zero,yu/s,pi1,pi2),complex)

def offmax(metrics):
    return max(metrics["down_max_abs_rho_offdiag"],
               metrics["up_max_abs_rho_offdiag"])

def check_matched_finite_flow(scalars,solutions,*,top,steps,high,low):
    """Run EXACTLY the stored B2 solutions; no random Yukawa generation."""
    if set(scalars)!=set(solutions):
        raise ValueError("B2 scalar IDs differ: fail closed")
    if not 0<low<high or steps<8:
        raise ValueError("Bad flow interval or integration resolution")
    cases=[]
    for ident,point in scalars.items():
        saved=solutions[ident]
        if not isinstance(saved,list) or len(saved)<top:
            raise ValueError("Fewer saved B2 solutions than required for "+ident)
        for rank,sol in enumerate(saved[:top],1):
            bridge=validate_B2_solution(point,sol)
            if bridge["physical_Zee_allowed"] is not None:
                raise AssertionError("Unexpected physical allowed claim")
            Y=complex_matrix(sol["Y"],"Y")
            tb=bridge["tanbeta"]
            L=bridge_chen_y_to_fls(Y,tb)
            inputs=quark_boundary(tb,L["Pi1"],L["Pi2"])
            initial=physical_offdiagonals(inputs,tb)
            if offmax(initial)>1e-12:
                raise AssertionError("Quark boundary not aligned")
            # Independently compare local beta to bridged Pi trace.
            bg,bd=beta_quarks_2hdm(
                (inputs[0],inputs[1]),(inputs[2],inputs[3]),
                (inputs[4],inputs[5]),g3=1.18,g2=.65,gp=.36)
            T=complex(bridge["T_2HDM_FLS_real"],
                      bridge["T_2HDM_FLS_imag"])
            ng=max(1.,np.linalg.norm(T*inputs[0]))
            nu=max(1.,np.linalg.norm(T*inputs[3]))
            err_g=float(np.linalg.norm(bg[1]-T*inputs[0])/ng)
            err_u=float(np.linalg.norm(bd[0]-T*inputs[3])/nu)
            if max(err_g,err_u)>1e-11:
                raise AssertionError("Finite-flow beta input trace mismatch")
            final=physical_offdiagonals(evolve(
                inputs,high,low,steps),tb)
            if not all(np.isfinite(list(final.values())[i]).all()
                       if isinstance(list(final.values())[i],list)
                       else math.isfinite(list(final.values())[i])
                       for i in range(len(final))):
                raise AssertionError("Nonfinite final Yukawas")
            cases.append({
                "candidate_id":ident,
                "b2_rank":rank,
                "tanbeta":tb,
                "T_real":T.real,"T_imag":T.imag,
                "local_source_over_parent_per_lnmu":abs(T)/(16*math.pi**2),
                "neutrino_algebraic_closure_eV":
                    bridge["neutrino_matrix_closure_eV"],
                "matched_charged_width_subset_GeV":
                    bridge["B3_charged_lepton_widths_LO_subset_GeV"],
                "beta_trace_residual_down":err_g,
                "beta_trace_residual_up":err_u,
                "initial_quark_toy":initial,
                "final_quark_toy_truncated":final,
                "not_experimental_FCNC":True,
            })
            print("MATCHED_FINITE",ident,"RANK",rank,
                  "T_abs_over_16pi2",f"{abs(T)/(16*math.pi**2):.4e}",
                  "rho_d_offdiag",f"{final['down_max_abs_rho_offdiag']:.4e}",
                  "rho_u_offdiag",f"{final['up_max_abs_rho_offdiag']:.4e}",
                  flush=True)
    if not cases:
        raise AssertionError("No matched solutions")
    # One solution RK4 half-step convergence, using same exact saved input.
    first=cases[0]
    p=scalars[first["candidate_id"]]
    sol=solutions[first["candidate_id"]][0]
    L=bridge_chen_y_to_fls(complex_matrix(sol["Y"],"Y"),first["tanbeta"])
    inp=quark_boundary(first["tanbeta"],L["Pi1"],L["Pi2"])
    fine=physical_offdiagonals(evolve(inp,high,low,steps*2),first["tanbeta"])
    coarse=first["final_quark_toy_truncated"]
    convergence={}
    for name in ("down_max_abs_rho_offdiag","up_max_abs_rho_offdiag"):
        delta=abs(coarse[name]-fine[name])
        tolerance=max(1e-12,.02*abs(fine[name]))
        if delta>tolerance:
            raise AssertionError("Failed RK4 convergence in "+name)
        convergence[name]={"steps":steps,"steps_doubled":steps*2,
                           "abs_difference":delta,"allowed_tolerance":tolerance}
    # Type-II lepton control at the SAME quark matching tanbeta/masses.
    K=L["kappa"]
    rho=-first["tanbeta"]*K
    c=1/math.hypot(1.,first["tanbeta"])
    s=first["tanbeta"]*c
    ctrl=quark_boundary(first["tanbeta"],c*K-s*rho,s*K+c*rho)
    ctrl_final=physical_offdiagonals(evolve(ctrl,high,low,steps),
                                      first["tanbeta"])
    if offmax(ctrl_final)>1e-12:
        raise AssertionError("Type-II lepton control failed")
    return {"cases":cases,
            "n_checked":len(cases),
            "control_typeII_leptons_final":ctrl_final,
            "rk4_convergence_first_candidate":convergence,
            "model_rge_complete":False,
            "quark_masses_CKM_are_synthetic":True,
            "lepton_Y_saved_B2_old_NO_fixed_input":True,
            "neutrino_fit_NuFIT61":False,
            "full_LFV":False,
            "physical_FCNC_exclusions":False,
            "physical_Zee_allowed":None}

def git_head():
    try:
        p=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,
                         capture_output=True,text=True,timeout=6)
        return p.stdout.strip() if p.returncode==0 else None
    except (OSError,subprocess.TimeoutExpired):
        return None

def write_json(path,data):
    Path(path).write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--points",type=Path,default=Path(
        "work/gateB1_zee_seed_scan/all_screened_candidates_NOT_ALLOWED.csv"))
    ap.add_argument("--b2-json",type=Path,default=Path(
        "work/gateB2_zee_neutrino_family/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json"))
    ap.add_argument("--output-dir",type=Path,default=Path(
        "work/zee_section8_Q2_integrated_v1"))
    ap.add_argument("--top",type=int,default=10)
    ap.add_argument("--expected-cases",type=int,default=20)
    ap.add_argument("--steps",type=int,default=120)
    ap.add_argument("--high",type=float,default=10000.)
    ap.add_argument("--low",type=float,default=700.)
    ap.add_argument("--suite-timeout",type=int,default=240)
    a=ap.parse_args()
    if not(1<=a.top<=100 and a.expected_cases>0 and
           8<=a.steps<=5000 and 0<a.low<a.high and
           10<=a.suite_timeout<=3600):
        ap.error("Invalid integrated audit settings")
    output=a.output_dir.resolve()
    if output.exists():
        ap.error("Refuse to overwrite integrated output directory")
    for inp in (a.points,a.b2_json):
        if not inp.is_file():
            ap.error("Missing required saved input "+str(inp))
    output.mkdir(parents=True)
    print("STATUS",STATUS,flush=True)
    print("GIT_HEAD",git_head(),flush=True)
    start=time.monotonic()
    summary={
        "status":STATUS,"python":sys.version,"numpy":np.__version__,
        "git_commit":git_head(),"input_files":{
            "scalar_csv":str(a.points.resolve()),
            "scalar_csv_SHA256":digest(a.points),
            "B2_Yukawa_json":str(a.b2_json.resolve()),
            "B2_Yukawa_SHA256":digest(a.b2_json)},
        "parameter_settings":{"top":a.top,
             "expected_cases":a.expected_cases,"steps":a.steps,
             "high_GeV":a.high,"low_GeV":a.low},
        "program_scope":"one-command Q1/Q2a/Q2b/Q2c/Q2d plus published Q2e reduced Zee f-beta reproduction, B2/B3/LFV and matched truncated RG",
        "missing_physics":list(MISSING_PHYSICS),
        "full_Zee_RGE_done":False,
        "full_NuFIT61_fit":False,
        "full_LFV_done":False,
        "experimental_quark_FCNC_likelihood":False,
        "full_Zee_allowed":None,
        "overall_numerical_pass":False,
    }
    try:
        suites,scipy_present=run_tests(
            output/"unittest_suites.log",timeout=a.suite_timeout)
        summary["suites"]=suites
        summary["scipy_available"]=scipy_present
        summary["required_test_count"]=sum(
            x["tests_run"] or 0 for x in suites if x["required"])
        summary["required_suite_failures"]=[
            x["suite"] for x in suites if x["required"] and not x["passed"]]
        summary["optional_suite_failures"]=[
            x["suite"] for x in suites if not x["required"] and x["passed"] is False]
        # Fail closed if ANY executed suite fails; SciPy absence means
        # optional suites NOT_RUN and never counted as PASS.
        if summary["required_suite_failures"] or summary["optional_suite_failures"]:
            raise AssertionError("Software unit suite failures; inspect unittest_suites.log")
        scalar=read_scalar_points(a.points)
        b2=json.loads(a.b2_json.read_text())
        if not isinstance(b2,dict):
            raise ValueError("B2 solution format is not candidate->solutions")
        report=check_matched_finite_flow(scalar,b2,top=a.top,
            steps=a.steps,high=a.high,low=a.low)
        summary["matched_flow"]=report
        if report["n_checked"]!=a.expected_cases:
            raise AssertionError(
                f"Expected {a.expected_cases} matched cases, found {report['n_checked']}")
        charged={k:charged_matrix_audit(
            p["mH1"],p["mH2"],p["gamma"])
            for k,p in scalar.items()}
        hierarchy_inapplicable=all(
            not entry["necessary_heavy_singlet_diagonal_ordering"]
            for entry in charged.values())
        # For these two SOURCE-PINNED scalar points, checking the
        # hierarchy as a *necessary* condition must fail.
        # A future scan may contain other spectra, at which point this
        # strict result must be re-reviewed instead of silently reused.
        if len(charged)!=2 or not hierarchy_inapplicable:
            raise AssertionError(
                "Q2c reference candidates changed; independently reassess EFT hierarchy")
        summary["Q2c_reconstructed_charged_matrices"]=charged
        summary["Q2c_analytical_Zee_gauge_beta"]=gauge_audit()
        summary["Q2c_heavy_singlet_hierarchical_EFT_applicable"]=False
        summary["Q2c_complete_Zee_f_RGEs_available"]=False
        spurions=zee_spurion_audit(
            scalar,b2,top=a.top,expected=a.expected_cases)
        summary["Q2d_Zee_lepton_and_scalar_RGE_spurions"]=spurions
        summary["Q2d_complete_lambda6_lambda7_RGEs_available"]=False
        summary["Q2d_lambda6_lambda7_RG_stability_proven"]=False
        legacy_f=historical_2001_reduced_f_run(
            low=a.low,high=a.high,steps=a.steps)
        summary["Q2e_Kanemura2001_reduced_real_f_RGE"]=legacy_f
        if not (0.9<legacy_f["f_scale_ratio_sqrt_q"]<1. and
                legacy_f["f_beta_matrix_vs_3d_identity_error"]<1e-12 and
                legacy_f["physical_Zee_allowed"] is None):
            raise AssertionError("Q2e source-reduced f running invariant failed")
        summary["Q2e_general_complex_f_beta_validated"]=False
        q3=q3_quartic_diagnostics()
        if (q3["synthetic_stable_example_no_negative_witness"]["negative_witness"] is not None
            or q3["synthetic_unstable_example_has_negative_witness"]["negative_witness"] is None
            or q3["full_UV_Zee_betas_available"] is not False
            or q3["physical_Zee_allowed"] is not None):
            raise AssertionError("Q3 source-limited scalar witness sanity checks failed")
        summary["Q3_generic_quartic_tree_level_source_audit"]=q3
        summary["Q3_complete_UV_Zee_betas_implemented"]=False
        summary["Q3_tree_level_quartic_diagnostics_NOT_global_BFB"]=True
        summary["overall_numerical_pass"]=True
        summary["overall_status"]="NUMERICAL_CONSISTENCY_PASS_ONLY_NO_ALLOWED_BENCHMARK"
        summary["total_seconds"]=round(time.monotonic()-start,3)
        write_json(output/"summary.json",summary)
        print("INTEGRATED_REQUIRED_TESTS_PASS",summary["required_test_count"])
        print("MATCHED_OLD_B2_CASES_PASS",report["n_checked"])
        print("CONTROL_TYPEII_LEPTONS_PASS True")
        print("RK4_STABILITY_PASS True")
        for ident,m in charged.items():
            print("Q2C_CHARGED",ident,
                  "MDD_GeV",f"{m['sqrt_M_DD_squared_GeV']:.5f}",
                  "Mchi_GeV",f"{m['sqrt_M_chichi_squared_GeV']:.5f}",
                  "MU_ZEE_GeV",f"{m['abs_muZee_GeV_from_eq14']:.5f}",
                  "H1_SINGLET_FRACTION",f"{m['H1_singlet_weight']:.6f}")
        print("Q2C_HEAVY_SINGLET_HIERARCHICAL_EFT_APPLICABLE False")
        print("Q2C_FULL_UV_ZEE_LEPTON_RGES_IMPLEMENTED False")
        print("Q2D_MATCHED_B2_SPURIONS",spurions["count"])
        print("Q2D_ALL_T21_NONZERO",spurions["all_T21_nonzero"])
        print("Q2D_ALL_I6_NONZERO",spurions["all_I6_nonzero_at_1e_minus18"])
        print("Q2D_ALL_I7_NONZERO",spurions["all_I7_nonzero_at_1e_minus18"])
        print("Q2D_SCALAR_LAMBDA6_LAMBDA7_ALL_SCALE_PROTECTION_PROVEN False")
        print("Q2D_COMPLETE_LEPTON_AND_QUARTIC_BETAS_IMPLEMENTED False")
        print("Q2E_KANEMURA2001_REDUCED_REAL_F_RGE_PASS True")
        print("Q2E_REAL_F_SCALE_RATIO",
              f"{legacy_f['f_scale_ratio_sqrt_q']:.9f}")
        print("Q2E_GENERAL_COMPLEX_F_AND_YUKAWA_RGES_AVAILABLE False")
        print("Q3_EXACT_SINGLET_QUARTIC_REDUCTION_AND_INSTABILITY_WITNESS_PASS True")
        print("Q3_COMPLETE_ZEE_UV_BETA_FUNCTIONS_IMPLEMENTED False")
        print("COMPLETE_MODEL_AND_EXPERIMENTAL_CONSTRAINTS_PASS False")
        print("FULL_ZEE_ALLOWED UNKNOWN_NOT_EVALUATED")
        print("SUMMARY",output/"summary.json")
        return 0
    except Exception as exc:
        summary["overall_status"]="INTEGRATED_NUMERICAL_FAIL_CLOSED"
        summary["error"]=repr(exc)
        summary["error_traceback"]=traceback.format_exc()
        summary["total_seconds"]=round(time.monotonic()-start,3)
        write_json(output/"summary.json",summary)
        print("INTEGRATED_FAIL",repr(exc),file=sys.stderr)
        print("SUMMARY",output/"summary.json",file=sys.stderr)
        return 1

if __name__=="__main__":
    raise SystemExit(main())
