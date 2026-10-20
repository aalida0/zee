#!/usr/bin/env python3
"""Q2d: source-controlled Zee flavor-spurion audit, NOT full RGEs.

Evaluate exact invariants of Pi1,Pi2 for all saved B2 solutions:
  T21 = Tr(Pi2 Pi1_dagger)
  I6 = Tr(Pi1 Pi1_dagger Pi1 Pi2_dagger)
  I7 = Tr(Pi2 Pi2_dagger Pi2 Pi1_dagger).
These are symmetry-allowed one-loop mixed-doublet
fermion-box *structures*, not complete beta_lambda6/beta_lambda7.
Also record f_dagger f invariants and validate complex linear
variation delta(D T21)=Tr(delta(D Pi2) Pi1_dagger+
                         Pi2 delta(D Pi1)_dagger).
D=16pi^2*d/dln(mu). D Pi corrections are deliberately UNKNOWN;
we never assign an unverified full-Zee coefficient.

Sources: Schmidt-Vandeleur JHEP06(2026)006 Sec.2/3/Appendix B;
FLS PLB688(2010) 341; Machacek-Vaughn NPB236(1984) 221;
Ferreira et al EPJC84(2024), 2HDM lambda6/7 beta scalar/fermion split.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import traceback
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from zee_section8_Q2b_chen_FLS_matching_gate import (
    bridge_chen_y_to_fls,read_scalar_points,validate_B2_solution)
from gateB3_general_zee_charged_lepton_widths import complex_matrix

STATUS="Q2D_ZEE_UNPROTECTED_YUKAWA_SPURIONS_NOT_COMPLETE_QUARTIC_RGES"
TEST_FILE="test_zee_section8_Q2d_lepton_spurion_scalar_RG_audit.py"
SOURCES=[
    "https://arxiv.org/html/2512.17235v2",
    "https://arxiv.org/abs/1001.2561",
    "https://doi.org/10.1016/0550-3213(84)90533-9",
    "https://link.springer.com/article/10.1140/epjc/s10052-024-12561-8",
]

def structures(pi1,pi2,f=None):
    p=np.asarray(pi1,complex);q=np.asarray(pi2,complex)
    if any(m.shape!=(3,3) or not np.isfinite(m).all() for m in (p,q)):
        raise ValueError("Expected finite Pi1,Pi2 3x3 lepton Yukawas")
    t=np.trace(q@p.conj().T)
    i6=np.trace(p@p.conj().T@p@q.conj().T)
    i7=np.trace(q@q.conj().T@q@p.conj().T)
    out={"T21":complex(t),"I6":complex(i6),"I7":complex(i7),
         "T21_abs":float(abs(t)),"I6_abs":float(abs(i6)),
         "I7_abs":float(abs(i7)),
         "one_loop_quartic_beta_coefficient_calculated":False,
         "lambda6_lambda7_RG_stability_proven":False}
    if f is not None:
        ff=np.asarray(f,complex)
        if ff.shape!=(3,3) or not np.isfinite(ff).all():
            raise ValueError("Expected finite Zee f matrix")
        if np.max(abs(ff+ff.T))>1e-10:
            raise ValueError("f must be antisymmetric")
        H=ff.conj().T@ff
        out.update({"f_frobenius_squared":float(np.trace(H).real),
                    "f_quartic_invariant":float(np.trace(H@H).real),
                    "f_numerical_rank":int(np.linalg.matrix_rank(ff,tol=1e-12)),
                    "complete_Zee_f_beta_calculated":False})
    return out

def delta_trace(pi1,pi2,deltaDpi1,deltaDpi2):
    p,q,x,y=[np.asarray(a,complex)
             for a in (pi1,pi2,deltaDpi1,deltaDpi2)]
    if any(z.shape!=(3,3) or not np.isfinite(z).all()
           for z in (p,q,x,y)):
        raise ValueError("All Pi and delta(D Pi) must be finite 3x3")
    return complex(np.trace(y@p.conj().T+q@x.conj().T))

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def stored_audit(points,saved,top=10,expected=20):
    if not isinstance(saved,dict) or set(points)!=set(saved):
        raise ValueError("Scalar and B2 candidate sets differ")
    if not (1<=top<=1000):
        raise ValueError("Invalid B2 top count")
    rows=[]
    for ident,p in points.items():
        sols=saved[ident]
        if not isinstance(sols,list) or len(sols)<top:
            raise ValueError("Insufficient stored B2 Yukawa solutions")
        for rank,sol in enumerate(sols[:top],1):
            validation=validate_B2_solution(p,sol)
            f=complex_matrix(sol["f"],"f")
            Y=complex_matrix(sol["Y"],"Y")
            x=bridge_chen_y_to_fls(Y,validation["tanbeta"])
            a=structures(x["Pi1"],x["Pi2"],f)
            refT=complex(validation["T_2HDM_FLS_real"],
                         validation["T_2HDM_FLS_imag"])
            if not np.isclose(a["T21"],refT,rtol=1e-11,atol=1e-13):
                raise AssertionError("Q2b/Q2d trace mismatch")
            if a["f_numerical_rank"]!=2:
                raise AssertionError("Expected rank-two antisymmetric f")
            rows.append({
                "candidate_id":ident,"rank":rank,
                "T21_real":a["T21"].real,"T21_imag":a["T21"].imag,
                "I6_real":a["I6"].real,"I6_imag":a["I6"].imag,
                "I7_real":a["I7"].real,"I7_imag":a["I7"].imag,
                "I6_abs":a["I6_abs"],"I7_abs":a["I7_abs"],
                "f_frobenius_squared":a["f_frobenius_squared"],
                "f_quartic_invariant":a["f_quartic_invariant"],
                "nu_matrix_closure_eV":validation["neutrino_matrix_closure_eV"],
                "complete_Zee_quartic_betas":False,
                "physically_allowed":None,
            })
    if len(rows)!=expected:
        raise ValueError("Expected %d cases; found %d"%(expected,len(rows)))
    return {
        "count":len(rows),"rows":rows,
        "all_T21_nonzero":all(abs(complex(
            r["T21_real"],r["T21_imag"]))>1e-14 for r in rows),
        "all_I6_nonzero_at_1e_minus18":all(r["I6_abs"]>1e-18 for r in rows),
        "all_I7_nonzero_at_1e_minus18":all(r["I7_abs"]>1e-18 for r in rows),
        "zero_lambda6_lambda7_at_all_scales_proven":False,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--points",type=Path,default=Path(
       "work/gateB1_zee_seed_scan/all_screened_candidates_NOT_ALLOWED.csv"))
    ap.add_argument("--b2-json",type=Path,default=Path(
       "work/gateB2_zee_neutrino_family/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json"))
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--top",type=int,default=10)
    ap.add_argument("--expected-cases",type=int,default=20)
    a=ap.parse_args()
    if a.output_dir.exists():
        ap.error("Refusing to overwrite")
    for f in (a.points,a.b2_json):
        if not f.is_file():ap.error("Missing input "+str(f))
    output=a.output_dir.resolve()
    output.mkdir(parents=True)
    report={
        "status":STATUS,"sources":SOURCES,
        "input_sha256":{str(x):sha256(x) for x in (a.points,a.b2_json)},
        "complete_Zee_f_Yukawa_betas":False,
        "complete_Zee_lambda6_lambda7_betas":False,
        "all_scale_scalar_restrictions_proven":False,
        "full_neutrino_likelihood":False,
        "complete_LFV":False,
        "experimental_quark_FCNC_likelihood":False,
        "physical_Zee_allowed":None,
        "numerical_success":False}
    try:
        u=subprocess.run(
            [sys.executable,"-m","unittest","discover","-s","tests",
             "-p",TEST_FILE,"-v"],cwd=ROOT,capture_output=True,
            text=True,timeout=120,check=False)
        log=u.stdout+u.stderr
        (output/"unit_tests.log").write_text(log)
        if u.returncode or "Ran " not in log or "OK" not in log:
            raise RuntimeError("Q2d source structure tests failed")
        points=read_scalar_points(a.points)
        solutions=json.loads(a.b2_json.read_text())
        report["matched_B2"]=stored_audit(points,solutions,a.top,a.expected_cases)
        report["numerical_success"]=True
        report["scientific_decision"]=(
            "NO_EXACT_Z2_IS_DEMONSTRATED_FOR_THE_GENERAL_LEPTON_SECTOR;"
            " FULL_BETA_LAMBDA6_LAMBDA7_AND_F_BETAS_REQUIRED")
        (output/"summary.json").write_text(json.dumps(report,indent=2)+"\n")
        print("Q2D_UNIT_TESTS PASS")
        print("Q2D_MATCHED_B2",report["matched_B2"]["count"])
        for key in ("all_T21_nonzero","all_I6_nonzero_at_1e_minus18",
                    "all_I7_nonzero_at_1e_minus18"):
            print("Q2D_"+key.upper(),report["matched_B2"][key])
        print("FULL_ZEE_LEPTON_QUARTIC_BETAS_IMPLEMENTED False")
        print("PHYSICAL_ZEE_ALLOWED False")
        print("SUMMARY",output/"summary.json")
        return 0
    except Exception as exc:
        report["error"]=repr(exc)
        report["traceback"]=traceback.format_exc()
        (output/"summary.json").write_text(json.dumps(report,indent=2)+"\n")
        print("Q2D_FAILED",repr(exc),file=sys.stderr)
        return 1

if __name__=="__main__":
    raise SystemExit(main())
