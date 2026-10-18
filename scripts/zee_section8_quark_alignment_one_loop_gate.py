#!/usr/bin/env python3
"""Zee quark-alignment GATE Q1: source-matched ONE-LOOP local tangent.

Source: P.M. Ferreira, L. Lavoura, J.P. Silva, PLB688 (2010) 341,
arXiv:1001.2561, Eqs.(3a-c),(4a-c) in the standard 2HDM.
In its symmetry basis:
  -L_Y = Qbar (Gamma_k Phi_k dR + Delta_k tildePhi_k uR)
       + Lbar (Pi_k Phi_k eR) + h.c.
At the Type-II quark boundary Gamma=(G,0), Delta=(0,D), leptons
Pi=(Pi1,Pi2) generic:
  16pi² dGamma2/dlnmu = T G, 16pi² dDelta1/dlnmu = T D,
  T = Tr(Pi2 Pi1^dagger)=Tr(Pi1^dagger Pi2).

This does NOT claim complete Zee RGEs, RG-invariant alignment, finite
running, quark FCNC compatibility, neutrino/LFV fit, or allowed model.
The singlet f_LLchi terms are not included in this pure-2HDM quark
one-loop expression. This is a local consistency gate only.
Requires numpy, NOT scipy.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np

STATUS="ZEE_QUARK_ALIGNMENT_LOCAL_ONE_LOOP_TANGENT_ONLY_NOT_FCNC_ALLOWED"
SOURCE="https://ar5iv.labs.arxiv.org/html/1001.2561"
V=246.21965

def beta_quarks_2hdm(gammas,deltas,pis,*,g3=0.,g2=0.,gp=0.):
    """D Gamma_k, D Delta_k (D=16pi² d/dlnmu), FLS 2010 Eqs.3,4."""
    if any(len(pair)!=2 for pair in (gammas,deltas,pis)):
        raise ValueError("Each Yukawa pair needs two matrices")
    if any(np.shape(a)!=(3,3) or not np.isfinite(a).all()
           for pair in (gammas,deltas,pis) for a in pair):
        raise ValueError("All Yukawas must be finite 3x3 matrices")
    if any(not math.isfinite(x) or x<0 for x in (g3,g2,gp)):
        raise ValueError("Gauge couplings must be nonnegative finite")
    G=tuple(np.asarray(a,complex) for a in gammas)
    D=tuple(np.asarray(a,complex) for a in deltas)
    P=tuple(np.asarray(a,complex) for a in pis)
    aG=-8*g3**2-9*g2**2/4-5*gp**2/12
    aD=-8*g3**2-9*g2**2/4-17*gp**2/12
    bg=[];bd=[]
    for k in range(2):
        down=aG*G[k].copy()
        up=aD*D[k].copy()
        for l in range(2):
            down+=(3*np.trace(G[k]@G[l].conj().T+
                               D[k].conj().T@D[l])+
                   np.trace(P[k]@P[l].conj().T))*G[l]
            down+=(-2*D[l]@D[k].conj().T@G[l]
                   +G[k]@G[l].conj().T@G[l]
                   +.5*D[l]@D[l].conj().T@G[k]
                   +.5*G[l]@G[l].conj().T@G[k])
            up+=(3*np.trace(D[k]@D[l].conj().T+
                             G[k].conj().T@G[l])+
                 np.trace(P[k].conj().T@P[l]))*D[l]
            up+=(-2*G[l]@G[k].conj().T@D[l]
                 +D[k]@D[l].conj().T@D[l]
                 +.5*G[l]@G[l].conj().T@D[k]
                 +.5*D[l]@D[l].conj().T@D[k])
        bg.append(down);bd.append(up)
    return tuple(bg),tuple(bd)

def higgs_to_symmetry_leptons(kappa_e,rho_e,tanbeta):
    """H_v=c_beta Phi1+s_beta Phi2; H_perp=-s_beta Phi1+c_beta Phi2."""
    if not math.isfinite(tanbeta) or tanbeta<=0:
        raise ValueError("tanbeta must be positive finite")
    k=np.asarray(kappa_e,complex)
    r=np.asarray(rho_e,complex)
    if k.shape!=(3,3) or r.shape!=(3,3) or not (
        np.isfinite(k).all() and np.isfinite(r).all()):
        raise ValueError("Finite 3x3 Higgs-basis Yukawas required")
    c=1/math.hypot(1.,tanbeta)
    s=tanbeta*c
    return c*k-s*r,s*k+c*r

def audit_quark_tangent(gamma1,delta2,pi1,pi2,*,gauge=(1.18,.65,.36)):
    """Evaluate at Type-II quark boundary, generic lepton Yukawas."""
    G=np.asarray(gamma1,complex)
    D=np.asarray(delta2,complex)
    P1=np.asarray(pi1,complex)
    P2=np.asarray(pi2,complex)
    Z=np.zeros((3,3),complex)
    bg,bd=beta_quarks_2hdm((G,Z),(Z,D),(P1,P2),
                            g3=gauge[0],g2=gauge[1],gp=gauge[2])
    T=complex(np.trace(P2@P1.conj().T))
    scale=max(1.,np.linalg.norm(T*G),np.linalg.norm(T*D))
    err_g=float(np.linalg.norm(bg[1]-T*G)/scale)
    err_d=float(np.linalg.norm(bd[0]-T*D)/scale)
    if max(err_g,err_d)>1e-11:
        raise AssertionError("FLS quark-Yukawa beta tangent identity failed")
    return {
        "status":STATUS,"T_real":float(T.real),"T_imag":float(T.imag),
        "normalized_beta_Gamma2_error":err_g,
        "normalized_beta_Delta1_error":err_d,
        "beta_Gamma2_frobenius":float(np.linalg.norm(bg[1])),
        "beta_Delta1_frobenius":float(np.linalg.norm(bd[0])),
        "wrong_doublet_source_nonzero":bool(abs(T)>1e-13),
        "initial_wrong_doublet_source_is_flavor_aligned":True,
        "TypeII_texture_RG_invariant_for_generic_leptons":False,
        "full_Zee_RGE_completed":False,
        "finite_running_completed":False,
        "quark_FCNC_limits_completed":False,
        "neutrino_LFV_fit_completed":False,
        "fully_allowed_Zee":None
    }

def toy_example(tanbeta=5.6):
    """Illustrative matrices ONLY: NOT a fitted Zee point."""
    c=1/math.hypot(1.,tanbeta)
    s=tanbeta*c
    G=np.diag([.0001,.002,.024]).astype(complex)/c
    D=np.diag([.00001,.007,.95]).astype(complex)/s
    k=np.diag(np.sqrt(2)*np.array([.00051099895,.1056583755,1.77686])/V)
    r=np.array([[.002,.005j,.001],
                [.001,.003,.004],
                [.002,-.007j,.020+.002j]],complex)
    pi1,pi2=higgs_to_symmetry_leptons(k,r,tanbeta)
    result=audit_quark_tangent(G,D,pi1,pi2)
    T=complex(result["T_real"],result["T_imag"])
    L=math.log(10000./700.)
    result["illustrative_abs_wrong_doublet_ratio_10TeV_to700GeV"]=(
        abs(T)*L/(16*math.pi**2))
    result["toy_lepton_matrices_NOT_a_flavor_fit"]=True
    result["illustrative_ratio_NOT_an_FCNC_bound"]=True
    result["tanbeta"]=tanbeta
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tanbeta",type=float,default=5.6)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if not math.isfinite(args.tanbeta) or args.tanbeta<=0:
        p.error("Invalid tanbeta")
    if args.output.exists():
        p.error("Refusing to overwrite existing results")
    data=toy_example(args.tanbeta)
    data["literature"]=SOURCE
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2)+"\n")
    print("STATUS",STATUS)
    print("TR_PI2_PI1_DAGGER",complex(data["T_real"],data["T_imag"]))
    print("GAMMA2_TANGENT_IDENTITY_ERROR",data["normalized_beta_Gamma2_error"])
    print("DELTA1_TANGENT_IDENTITY_ERROR",data["normalized_beta_Delta1_error"])
    print("INITIAL_WRONG_DOUBLET_SOURCE_FLAVOR_ALIGNED True")
    print("FINITE_RGE_AND_QUARK_FCNC_LIMITS_DONE False")
    print("PHYSICAL_ZEE_ALLOWED False")
    print("OUTPUT",args.output)

if __name__=="__main__":main()
