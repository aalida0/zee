#!/usr/bin/env python3
"""Q2b-1: bridge existing Chen/Higgs-basis Zee leptons to FLS quark RGEs.

CONVENTIONS:
Chen 2508.18757 Eq.(4): -L ⊃ sqrt(2) bar(ell_R) Y nu_L H_perp^-
FLS 1001.2561 Eq.(1): -L ⊃ bar(L_L) Pi_k Phi_k ell_R + h.c.
Thus in charged-lepton mass basis:
    rho_e := Pi_perp = sqrt(2) Y.conj().T, NOT sqrt(2) Y.
    kappa_e := Pi_v = sqrt(2) diag(m_e,m_mu,m_tau)/v.
    Pi1 = c_beta kappa_e - s_beta rho_e,
    Pi2 = s_beta kappa_e + c_beta rho_e.
With Type-II quarks at their declared boundary the local 2HDM Yukawa
source is D Gamma2=T Gamma1, D Delta1=T Delta2,
T=Tr(Pi2 Pi1^dagger), D=16 pi^2 d/dlnmu.

This bridges the STORED B2 solutions, but B2 neutrino target is
an older fixed NO oscillation *algebraic* target and LFV is PARTIAL.
No full Zee singlet-f RGEs, lepton fitting, flavor experimental bounds,
or physically allowed benchmarks are calculated. SciPy is not needed.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from gateA1b_hierarchical_no_seed import (
    ME,MMU,MTAU,target_neutrino_matrix
)
from gateB3_general_zee_charged_lepton_widths import (
    complex_matrix,ensure_neutrino_closure,charged_lepton_widths
)
from zee_section8_quark_alignment_one_loop_gate import V,higgs_to_symmetry_leptons

STATUS="Q2B_CHEN_TO_FLS_LEPTON_BRIDGE_ALGEBRA_ONLY_NOT_LFV_FCNC_OR_ALLOWED"
SOURCES=(
    "https://arxiv.org/html/2508.18757",
    "https://ar5iv.labs.arxiv.org/html/1001.2561",
)
LEPTON_MASSES=np.asarray((ME,MMU,MTAU),dtype=float)

def bridge_chen_y_to_fls(Y,tanbeta):
    """Chen Y rows (ell_R), columns (nu_L); FLS Pi rows L, columns R."""
    Y=np.asarray(Y,dtype=complex)
    if Y.shape!=(3,3) or not np.isfinite(Y).all():
        raise ValueError("Expected finite Chen 3x3 Y")
    if not math.isfinite(tanbeta) or tanbeta<=0:
        raise ValueError("Require tanbeta>0")
    K=np.diag(np.sqrt(2.)*LEPTON_MASSES/V).astype(complex)
    rho=np.sqrt(2.)*Y.conj().T
    p1,p2=higgs_to_symmetry_leptons(K,rho,tanbeta)
    c=1/math.hypot(1.,tanbeta)
    s=tanbeta*c
    np.testing.assert_allclose(c*p1+s*p2,K,rtol=2e-14,atol=1e-16)
    np.testing.assert_allclose(-s*p1+c*p2,rho,rtol=2e-14,atol=1e-16)
    np.testing.assert_allclose(rho.conj().T/math.sqrt(2.),Y,
                               rtol=2e-14,atol=1e-16)
    return {"kappa":K,"rho":rho,"Pi1":p1,"Pi2":p2}

def local_alignment_source(Y,tanbeta):
    b=bridge_chen_y_to_fls(Y,tanbeta)
    K,rho,p1,p2=(b[k] for k in ("kappa","rho","Pi1","Pi2"))
    T=np.trace(p2@p1.conj().T)
    c=1/math.hypot(1.,tanbeta)
    s=tanbeta*c
    X=np.trace(rho@K.conj().T)
    T_analytic=(c*s*(np.linalg.norm(K)**2-np.linalg.norm(rho)**2)
                +c*c*X-s*s*np.conj(X))
    if not np.allclose(T,T_analytic,rtol=1e-12,atol=1e-14):
        raise ValueError("Trace mismatch in Higgs-basis/symmetry-basis conversion")
    if not np.allclose(T,np.trace(p1.conj().T@p2),
                       rtol=1e-12,atol=1e-14):
        raise ValueError("Wrong-doublet up/down trace mismatch")
    # Imag(T) = Imag Tr(rho kappa†), independent of chosen real tanbeta.
    if not np.isclose(T.imag,X.imag,rtol=1e-12,atol=1e-14):
        raise ValueError("CP-odd trace identity failed")
    return {
        "T_complex":complex(T),
        "Higgs_basis_trace_X":complex(X),
        "norm_kappa_e":float(np.linalg.norm(K)),
        "norm_rho_e":float(np.linalg.norm(rho)),
        "per_log_scale_wrong_doublet_amplitude_over_parent":
            float(abs(T)/(16*math.pi**2)),
        "trace_identity_error":float(abs(T-T_analytic)),
        "chen_y_reconstruction_error":float(
            np.max(abs(rho.conj().T/math.sqrt(2.)-Y))),
    }

def validate_B2_solution(point,solution,*,target=None):
    """Fail closed on scalar ID, scalar spectrum, f/Y, neutrino closure."""
    if target is None:
        target,_=target_neutrino_matrix()
    required=("id","mH1","mH2","gamma","beta")
    if any(k not in point for k in required):
        raise ValueError("Missing scalar point keys")
    if str(solution.get("candidate_id"))!=str(point["id"]):
        raise ValueError("B2 candidate ID differs from scalar ID")
    for name in ("mH1","mH2","gamma"):
        if name not in solution or not math.isclose(
             float(solution[name]),float(point[name]),
             rel_tol=1e-11,abs_tol=1e-10):
            raise ValueError("B2 scalar spectrum mismatch: "+name)
    f=complex_matrix(solution["f"],"f")
    Y=complex_matrix(solution["Y"],"Y")
    if np.max(abs(f+f.T))>1e-10:
        raise ValueError("Not an antisymmetric Zee f")
    if max(np.max(abs(f)),np.max(abs(Y)))>math.sqrt(4*math.pi):
        raise ValueError("Nonperturbative B2 f/Y magnitudes")
    err=ensure_neutrino_closure(point,f,Y,target)
    if err>1e-9:
        raise ValueError("B2 neutrino closure mismatch")
    tanbeta=math.tan(float(point["beta"]))
    q=local_alignment_source(Y,tanbeta)
    # Independent charged-scalar doublet-only total coupling norm:
    # sum_l Gamma(H_i->l nu)[Y only] = m_i/(16pi)*w_i*||rho||_F².
    widths=charged_lepton_widths(
        float(point["mH1"]),float(point["mH2"]),
        float(point["gamma"]),f,Y)
    sg=math.sin(float(point["gamma"]))**2
    cg=math.cos(float(point["gamma"]))**2
    f_norm_sq=np.linalg.norm(f)**2
    rho_norm_sq=q["norm_rho_e"]**2
    for state,mass,dweight,sweight in (
        ("H1",float(point["mH1"]),cg,sg),
        ("H2",float(point["mH2"]),sg,cg)):
        if not mass>0:
            raise ValueError("Invalid charged Higgs mass")
        # B3 has exact phase-space factors per flavor. For the equality,
        # use its massless-lepton coupling limit; all original widths
        # retain the physical (1 - m_l²/m_H²)² factors.
        expected_massless=(mass/(16*math.pi)*
             (dweight*rho_norm_sq+4*sweight*f_norm_sq))
        total_physical=sum(widths[state].values())
        if total_physical<0 or not np.isfinite(total_physical):
            raise ValueError("Invalid charged lepton widths")
        # Small positive difference is due exclusively to lepton masses.
        if total_physical>expected_massless*(1+1e-12):
            raise ValueError("B3 width exceeds massless-nu+lepton norm")
        if (expected_massless-total_physical) > (
                expected_massless*1e-3+1e-14):
            raise ValueError("B3 widths incompatible with Higgs-basis Yukawa norm")
    return {
        "status":STATUS,
        "candidate_id":str(point["id"]),
        "mH1_GeV":float(point["mH1"]),
        "mH2_GeV":float(point["mH2"]),
        "charged_mixing_gamma_rad":float(point["gamma"]),
        "tanbeta":tanbeta,
        "neutrino_matrix_closure_eV":float(err),
        "max_abs_f":float(np.max(abs(f))),
        "max_abs_Chen_Y":float(np.max(abs(Y))),
        "T_2HDM_FLS_real":q["T_complex"].real,
        "T_2HDM_FLS_imag":q["T_complex"].imag,
        "Tr_rho_kappa_dag_real":q["Higgs_basis_trace_X"].real,
        "Tr_rho_kappa_dag_imag":q["Higgs_basis_trace_X"].imag,
        "norm_kappa_e":q["norm_kappa_e"],
        "norm_rho_e":q["norm_rho_e"],
        "per_log_scale_wrong_doublet_amplitude_over_parent_LOCAL":
            q["per_log_scale_wrong_doublet_amplitude_over_parent"],
        "trace_identity_error":q["trace_identity_error"],
        "chen_y_reconstruction_error":q["chen_y_reconstruction_error"],
        "B3_charged_lepton_widths_LO_subset_GeV":widths,
        "full_NuFIT61_likelihood":False,
        "B2_neutrino_target_is_old_NO_fixed":True,
        "full_Zee_f_coupled_RGE":False,
        "experimental_quark_FCNC_likelihood":False,
        "complete_LFV":False,
        "physical_Zee_allowed":None,
    }

def read_scalar_points(path):
    with Path(path).open(newline="") as fh:
        rd=csv.DictReader(fh)
        if not rd.fieldnames or not set(("id","mH1","mH2","gamma","beta")).issubset(rd.fieldnames):
            raise ValueError("Expected B1/B4 candidate CSV with id masses angles")
        result={}
        for line in rd:
            name=str(line["id"])
            if name in result:
                raise ValueError("Duplicate scalar ID")
            p={"id":name}
            for k in ("mH1","mH2","gamma","beta"):
                p[k]=float(line[k])
                if not math.isfinite(p[k]):
                    raise ValueError("Nonfinite scalar parameter")
            if not(p["mH2"]>p["mH1"]>0 and
                   0<p["gamma"]<math.pi/2 and 0<p["beta"]<math.pi/2):
                raise ValueError("Invalid scalar spectrum")
            result[name]=p
    if not result:
        raise ValueError("Empty scalar points")
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--points",type=Path,required=True)
    ap.add_argument("--b2-json",type=Path,required=True)
    ap.add_argument("--top",type=int,default=10)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    if not 1<=a.top<=1000:
        ap.error("top must be in 1..1000")
    if a.output.exists():
        ap.error("Refuse to overwrite existing report")
    scalars=read_scalar_points(a.points)
    solutions=json.loads(a.b2_json.read_text())
    if not isinstance(solutions,dict) or set(scalars)!=set(solutions):
        raise ValueError("B2 and scalar candidate IDs must match exactly")
    rows=[]
    for name,p in scalars.items():
        family=solutions[name]
        if not isinstance(family,list) or not family:
            raise ValueError("Empty B2 Yukawa family")
        for rank,item in enumerate(family[:a.top],1):
            row=validate_B2_solution(p,item)
            row["b2_rank"]=rank
            rows.append(row)
    r={
        "status":STATUS,"sources":SOURCES,
        "n_scalar_candidates":len(scalars),
        "n_B2_Yukawa_solutions":len(rows),
        "neutrino_input_type":"OLD_FIXED_NO_TARGET_NOT_MODERN_NUFIT",
        "correct_Chen_Y_to_FLS_Pi_perp":"Pi_perp = sqrt(2) Y_Chen_dagger",
        "source":"FLS local 2HDM quark RGE; incomplete full Zee RGE",
        "no_scale_extrapolation_performed":True,
        "physical_Zee_allowed":None,
        "cases":rows,
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2)+"\n")
    print("STATUS",STATUS)
    print("CASES",len(rows))
    for row in rows:
        print("MATCHED_B2",row["candidate_id"],"rank",row["b2_rank"],
              "T",complex(row["T_2HDM_FLS_real"],row["T_2HDM_FLS_imag"]),
              "local_per_ln_mu",row[
                  "per_log_scale_wrong_doublet_amplitude_over_parent_LOCAL"],
              "nu_closure_eV",row["neutrino_matrix_closure_eV"])
    print("COMPLETE_ZEE_RGE_OR_LFV_OR_FCNC_CONSTRAINTS False")
    print("PHYSICAL_ZEE_ALLOWED False")
    print("OUTPUT",a.output)

if __name__=="__main__":
    main()
