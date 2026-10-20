#!/usr/bin/env python3
"""Zee Q2c: one large *source-controlled* UV/EFT applicability audit.

Source: Schmidt & Vandeleur, JHEP 06 (2026) 006,
https://arxiv.org/html/2512.17235v2 :
  Eq. (14) physical charged-singlet/doublet mixing and mu_Zee;
  Sec. 3 (in particular the paragraph at Sec.3 start) and App.B:
  the main matching sequence assumes singlet h heavy, then the other
  doublet, and does NOT compute full UV Zee coupled beta-functions.

Our convention (as checked in B3):
  H1+ = cos(gamma) HD+ + sin(gamma) chi+
  H2+ = -sin(gamma) HD+ + cos(gamma) chi+.
This reconstructs physical broken-phase charged M², NOT the
unbroken-theory bare mass parameters used for threshold matching.

Also check the MODEL's one-loop gauge coupling b_i via SM+one extra
complex SU2 doublet (Y=1/2)+charged SU2 singlet (Y=1).
With SM-normalized g1=g' (NOT GUT-normalized):
  b_2HDM=(7,-3,-7), b_Zee=(22/3,-3,-7).
These gauge group coefficients do NOT supply full Zee Yukawa RGEs.

No guessed f-dependent beta-functions; no thresholds, matched
experimental inputs, model exclusion, or physical allowed point.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time
import traceback
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from zee_section8_Q2b_chen_FLS_matching_gate import (
    read_scalar_points,validate_B2_solution
)

STATUS="ZEE_Q2C_SOURCE_CONTROLLED_HIERARCHY_GAUGE_AND_B2_AUDIT_NO_FULL_UV_RGE_OR_ALLOWED"
SOURCE="https://arxiv.org/html/2512.17235v2"
V=246.21965
B_2HDM={"g1_SM_hypercharge":7.0,"g2_SU2":-3.0,"g3_SU3":-7.0}
B_ZEE={"g1_SM_hypercharge":22./3.,"g2_SU2":-3.0,"g3_SU3":-7.0}
GAUGE_BETA_DERIVATION={
 "SM_one_Higgs_doublet_hypercharge_b":41./6.,
 "extra_SU2_complex_doublet_Y_half":1./6.,
 "charged_SU2_complex_singlet_Y_one":1./3.,
 "singlet_SU2_and_SU3_contributions":0.,
 "hypercharge_g1_convention":"SM gprime, not sqrt(5/3) gprime",
}
REQUIRED_NEW_TEST="test_zee_section8_Q2c_UV_EFT_applicability.py"

def file_hash(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for buf in iter(lambda:f.read(1024*1024),b""):
            h.update(buf)
    return h.hexdigest()

def charged_matrix_audit(m1,m2,gamma):
    """Invert physical H1/H2 masses and the charged-mixing rotation."""
    if not all(math.isfinite(v) for v in (m1,m2,gamma)):
        raise ValueError("Nonfinite charged spectrum")
    if not(0<m1<m2 and 0<=gamma<=math.pi/2):
        raise ValueError("Invalid physical charged-scalar inputs")
    c=math.cos(gamma);s=math.sin(gamma)
    R=np.asarray([[c,s],[-s,c]],float)
    D=np.diag([m1*m1,m2*m2])
    M=R.T@D@R
    md2=float(M[0,0]);ms2=float(M[1,1]);mix=float(M[0,1])
    delta=m2*m2-m1*m1
    # Schmidt-Vandeleur Eq.14, up to a rephasable trilinear sign.
    mu_abs=float(abs(math.sin(2*gamma)*delta)/(math.sqrt(2)*V))
    offdiag_from_mu=mu_abs*V/math.sqrt(2)
    scale=max(md2,ms2)
    eigen=np.linalg.eigvalsh(M)
    err=float(max(abs(eigen[0]-m1*m1),abs(eigen[1]-m2*m2))/scale)
    mu_identity_err=float(abs(abs(mix)-offdiag_from_mu)/scale)
    if err>1e-12 or mu_identity_err>1e-12:
        raise AssertionError("Charged mass/trilinear reconstruction failure")
    if min(md2,ms2)<=0:
        raise AssertionError("Unphysical diagonal masses")
    return {
      "mH1_GeV":m1,"mH2_GeV":m2,
      "gamma_rad":gamma,
      "sin2gamma":float(math.sin(2*gamma)),
      "H1_singlet_weight":float(s*s),
      "H2_singlet_weight":float(c*c),
      "M_DD_squared_GeV2":md2,
      "M_chichi_squared_GeV2":ms2,
      "M_D_chi_squared_GeV2":mix,
      "sqrt_M_DD_squared_GeV":float(math.sqrt(md2)),
      "sqrt_M_chichi_squared_GeV":float(math.sqrt(ms2)),
      "singlet_over_doublet_diagonal_mass":float(math.sqrt(ms2/md2)),
      "abs_muZee_GeV_from_eq14":mu_abs,
      "offdiag_over_geometric_diagonal":
          float(abs(mix)/math.sqrt(md2*ms2)),
      "offdiag_over_diagonal_splitting":
          float(abs(mix)/(abs(md2-ms2))) if abs(md2-ms2)>1e-15 else None,
      "broken_phase_mass_matrix_eigenvalue_relative_residual":err,
      "mu_trilinear_identity_relative_residual":mu_identity_err,
      "necessary_heavy_singlet_diagonal_ordering":bool(ms2>md2),
      "light_charged_H1_singlet_dominated":bool(s*s>.5),
      "hierarchical_heavy_singlet_EFT_validated":False,
      "complete_Zee_UV_RGE_validated":False,
      "physical_Zee_allowed":None,
    }

def run_gauge(g0,b,lo,hi):
    """Analytic fixed-field-content one-loop RG solution.

    1/g_i²(hi) = 1/g_i²(lo) - b_i/(8pi²) ln(hi/lo).
    No decoupling or threshold matching, therefore an illustrative
    fixed-field-content comparison, NOT a gauge precision prediction.
    """
    if not all(math.isfinite(v) and v>0 for v in (g0,lo,hi)):
        raise ValueError("Positive finite gauge input and scales required")
    if hi<lo or not math.isfinite(b):
        raise ValueError("Invalid gauge running parameters")
    inverse=1/g0**2-b/(8*math.pi**2)*math.log(hi/lo)
    if inverse<=0 or not math.isfinite(inverse):
        raise ValueError("Gauge coupling Landau pole")
    return float(1/math.sqrt(inverse))

def gauge_audit(lo=700.,hi=10000.,g1=.36,g2=.65,g3=1.18):
    out={"low_GeV":lo,"high_GeV":hi,
         "gauge_boundary":"illustrative fixed (gprime,g2,g3)="+str((g1,g2,g3)),
         "thresholds_or_measured_coupling_inputs":False,
         "coefficients_2HDM":B_2HDM,
         "coefficients_Zee":B_ZEE,
         "hypercharge_derivation":GAUGE_BETA_DERIVATION}
    after={}
    for label,key,g in (
         ("g1_SM_hypercharge","g1_SM_hypercharge",g1),
         ("g2_SU2","g2_SU2",g2),
         ("g3_SU3","g3_SU3",g3)):
        a=run_gauge(g,B_2HDM[key],lo,hi)
        z=run_gauge(g,B_ZEE[key],lo,hi)
        after[label]={"2HDM":a,"Zee":z,
                      "fractional_Zee_minus_2HDM_over_2HDM":z/a-1}
    if not(math.isclose(
        B_ZEE["g1_SM_hypercharge"]-B_2HDM["g1_SM_hypercharge"],
        1/3,rel_tol=0,abs_tol=1e-15)):
        raise AssertionError("Hypercharge singlet beta difference")
    if not all(abs(after[n]["fractional_Zee_minus_2HDM_over_2HDM"])<1e-13
           for n in ("g2_SU2","g3_SU3")):
        raise AssertionError("Incorrect Zee nonabelian singlet gauge effect")
    out["couplings_at_high"]=after
    return out

def unit_tests():
    cmd=[sys.executable,"-m","unittest","discover","-s","tests",
         "-p",REQUIRED_NEW_TEST,"-v"]
    proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,
                        text=True,timeout=120,check=False)
    output=proc.stdout+proc.stderr
    good=proc.returncode==0 and "Ran " in output and "OK" in output
    return good,output,proc.returncode

def all_cases(points,solutions,expected):
    if not isinstance(solutions,dict) or set(points)!=set(solutions):
        raise ValueError("Mismatched candidate sets: fail closed")
    rows=[]
    unique={}
    for ident,point in points.items():
        charged=charged_matrix_audit(
            point["mH1"],point["mH2"],point["gamma"])
        unique[ident]=charged
        saved=solutions[ident]
        if not isinstance(saved,list) or len(saved)!=10:
            raise ValueError("Expected exactly 10 saved B2 candidates per scalar ID")
        for rank,solution in enumerate(saved,1):
            old=validate_B2_solution(point,solution)
            if old["physical_Zee_allowed"] is not None:
                raise AssertionError("Unexpected allowed benchmark assertion")
            rows.append({
                "candidate_id":ident,"B2_rank":rank,
                "T_real":old["T_2HDM_FLS_real"],
                "T_imag":old["T_2HDM_FLS_imag"],
                "local_rge_source_per_lnmu":old[
                    "per_log_scale_wrong_doublet_amplitude_over_parent_LOCAL"],
                "neutrino_algebra_closure_eV":old["neutrino_matrix_closure_eV"],
                "charged_hierarchy":charged,
                "full_LFV":False,
                "modern_neutrino_likelihood":False,
                "allowed_Zee":None,
            })
    if len(rows)!=expected:
        raise ValueError(f"Expected {expected} matched B2 solutions, got {len(rows)}")
    return unique,rows

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--points",type=Path,default=Path(
        "work/gateB1_zee_seed_scan/all_screened_candidates_NOT_ALLOWED.csv"))
    p.add_argument("--b2-json",type=Path,default=Path(
        "work/gateB2_zee_neutrino_family/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json"))
    p.add_argument("--output-dir",type=Path,default=Path(
        "work/zee_section8_Q2c_fullZee_EFT_scope_v1"))
    p.add_argument("--expected-cases",type=int,default=20)
    a=p.parse_args()
    if a.output_dir.exists():
        p.error("Refusing overwrite; choose new output directory")
    for path in (a.points,a.b2_json):
        if not path.is_file():p.error("Missing input "+str(path))
    out=a.output_dir.resolve()
    out.mkdir(parents=True)
    report={
      "status":STATUS,"literature":SOURCE,
      "source_scope":"arxiv:2512.17235v2 eq14 sec3 appB; 2HDM EFT after heavy singlet, no full Zee UV RG",
      "input_sha256":{str(a.points):file_hash(a.points),
                      str(a.b2_json):file_hash(a.b2_json)},
      "full_Zee_f_coupled_one_loop_RGE":False,
      "complete_EFT_threshold_matching":False,
      "neutrino_NuFIT61_likelihood":False,
      "full_LFV":False,
      "experimental_FCNC":False,
      "physical_Zee_allowed":None,
      "numerical_pass":False
    }
    try:
        good,testlog,rc=unit_tests()
        (out/"unit_tests.log").write_text(testlog)
        report["unit_suite_pass"]=good
        report["unit_exit_code"]=rc
        if not good:raise AssertionError("Q2c unit tests failed")
        points=read_scalar_points(a.points)
        data=json.loads(a.b2_json.read_text())
        unique,rows=all_cases(points,data,a.expected_cases)
        gauge=gauge_audit()
        report["candidate_mass_matrix_audit"]=unique
        report["matched_B2_solutions"]=rows
        report["matched_B2_count"]=len(rows)
        report["gauge_beta_audit"]=gauge
        report["all_candidates_fail_necessary_heavy_singlet_ordering"]=all(
            not v["necessary_heavy_singlet_diagonal_ordering"]
            for v in unique.values())
        report["source_hierarchical_EFT_applicable_to_present_candidates"]=False
        if not report["all_candidates_fail_necessary_heavy_singlet_ordering"]:
            raise AssertionError("New scalar points need individual hierarchy reassessment")
        report["numerical_pass"]=True
        report["scientific_status"]=( 
            "SOURCE_HIERARCHICAL_HEAVY_SINGLET_EFT_INAPPLICABLE_TO_CURRENT_B1"
            "_POINTS; FULL_UV_ZEE_RGE_AND_MODERN_FLAVOR_STILL_REQUIRED")
        (out/"summary.json").write_text(json.dumps(report,indent=2)+"\n")
        print("Q2C_UNIT_SUITE PASS")
        for ident,v in unique.items():
            print("CANDIDATE",ident,"MDD_GeV",
                  f"{v['sqrt_M_DD_squared_GeV']:.5f}",
                  "Mchi_GeV",f"{v['sqrt_M_chichi_squared_GeV']:.5f}",
                  "muZee_abs_GeV",f"{v['abs_muZee_GeV_from_eq14']:.5f}",
                  "light_H1_singlet_fraction",f"{v['H1_singlet_weight']:.6f}",
                  "heavy_singlet_ordering",
                  v["necessary_heavy_singlet_diagonal_ordering"])
        print("B2_MATCHED_SOLUTIONS",len(rows))
        print("GAUGE_U1_ZEE_MINUS_2HDM_BETA_COEFF",
              B_ZEE["g1_SM_hypercharge"]-B_2HDM["g1_SM_hypercharge"])
        print("HEAVY_SINGLET_HIERARCHICAL_EFT_APPLICABLE False")
        print("FULL_ZEE_UV_YUKAWA_BETAS_AVAILABLE False")
        print("FULL_NUFIT_LFV_FCNC_COMPLETED False")
        print("FULL_ZEE_ALLOWED False")
        print("SUMMARY",out/"summary.json")
        return 0
    except Exception as exc:
        report["scientific_status"]="INTEGRATED_Q2C_FAIL_CLOSED"
        report["error"]=repr(exc)
        report["error_traceback"]=traceback.format_exc()
        (out/"summary.json").write_text(json.dumps(report,indent=2)+"\n")
        print("Q2C_FAIL",repr(exc),file=sys.stderr)
        print("SUMMARY",out/"summary.json",file=sys.stderr)
        return 1

if __name__=="__main__":
    raise SystemExit(main())
