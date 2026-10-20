#!/usr/bin/env python3
"""Q2a exploratory finite pure-2HDM Yukawa running in the Zee flavor project.

Reference: Ferreira-Lavoura-Silva 2010 Eqs (3),(4),(5).
OMITS Zee charged-singlet f_LLchi beta terms, all scalar/gauge running,
VEV-angle running and matching thresholds. Do not treat its numerical
off-diagonal couplings as physical Zee FCNC predictions or bounds.
Only numpy. No SciPy.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np
from zee_section8_quark_alignment_one_loop_gate import (
    beta_quarks_2hdm,higgs_to_symmetry_leptons,V
)
STATUS="ZEE_TRUNCATED_PURE_2HDM_YUKAWA_FLOW_NOT_PHYSICAL_FCNC_BOUND"

def beta_leptons(G,D,P,*,g2,gp):
    """D Pi_k, FLS 2010 Eq. 5, D=16pi² d/dln(mu)."""
    a=-9*g2*g2/4-15*gp*gp/4
    out=[]
    for k in range(2):
        value=a*P[k].copy()
        for l in range(2):
            value+=(3*np.trace(G[k]@G[l].conj().T+
                                D[k].conj().T@D[l])+
                    np.trace(P[k]@P[l].conj().T))*P[l]
            value+=P[k]@P[l].conj().T@P[l]+.5*P[l]@P[l].conj().T@P[k]
        out.append(value)
    return out

def beta_all(Y,gauge=(1.18,.65,.36)):
    G,D,P=Y[:2],Y[2:4],Y[4:6]
    g,d=beta_quarks_2hdm(G,D,P,g3=gauge[0],
                         g2=gauge[1],gp=gauge[2])
    l=beta_leptons(G,D,P,g2=gauge[1],gp=gauge[2])
    return np.asarray([*g,*d,*l],complex)/(16*math.pi**2)

def evolve(Y,high,low,steps=120,gauge=(1.18,.65,.36)):
    if np.shape(Y)!=(6,3,3) or not np.isfinite(Y).all():
        raise ValueError("Expected 6 finite 3x3 Yukawa matrices")
    if not(0<low<high) or type(steps)!=int or steps<4:
        raise ValueError("Require high>low>0 and steps>=4")
    dt=math.log(low/high)/steps
    a=np.asarray(Y,complex).copy()
    for _ in range(steps):
        k1=beta_all(a,gauge)
        k2=beta_all(a+dt*k1/2,gauge)
        k3=beta_all(a+dt*k2/2,gauge)
        k4=beta_all(a+dt*k3,gauge)
        a+=dt*(k1+2*k2+2*k3+k4)/6
        if not np.isfinite(a).all():
            raise ValueError("Nonperturbative or invalid flow encountered")
    return a

def physical_offdiagonals(Y,tanbeta):
    """Diagonalize each quark mass matrix, inspect orthogonal Higgs rho."""
    if not(math.isfinite(tanbeta) and tanbeta>0):
        raise ValueError("Invalid tanbeta")
    c=1/math.hypot(1,tanbeta);s=tanbeta*c
    results={}
    for name,kappa,rho in (
        ("down",c*Y[0]+s*Y[1],-s*Y[0]+c*Y[1]),
        ("up",c*Y[2]+s*Y[3],-s*Y[2]+c*Y[3])):
        U,m,Vh=np.linalg.svd(kappa)
        mass_basis=U.conj().T@rho@Vh.conj().T
        off=mass_basis-np.diag(np.diag(mass_basis))
        results[name+"_max_abs_rho_offdiag"]=float(np.max(abs(off)))
        results[name+"_norm_rho_offdiag"]=float(np.linalg.norm(off))
        results[name+"_mass_yukawa_singular_values"]=sorted(
            map(float,m))
    return results

def example(tanbeta=5.6,high=10000.,low=700.,steps=120,
            rho_scale=1.,typeii_leptons=False):
    """Toy CKM-like quarks and lepton rho only: NOT a fitted Zee point."""
    c=1/math.hypot(1,tanbeta);s=tanbeta*c
    a=.225;b=.041
    R12=np.array([[math.cos(a),math.sin(a),0],
                  [-math.sin(a),math.cos(a),0],[0,0,1.]])
    R23=np.array([[1.,0,0],
                  [0,math.cos(b),math.sin(b)],
                  [0,-math.sin(b),math.cos(b)]])
    CKM=R23@R12
    yd=np.diag([.000027,.00056,.024])
    yu=CKM.conj().T@np.diag([.000013,.0073,.95])
    Z=np.zeros((3,3),complex)
    ke=np.diag(np.sqrt(2)*np.array([
        .00051099895,.1056583755,1.77686])/V)
    rho=( -tanbeta*ke if typeii_leptons else
         rho_scale*np.array([[.002,.005j,.001],
                             [.001,.003,.004],
                             [.002,-.007j,.020+.002j]],complex))
    p1,p2=higgs_to_symmetry_leptons(ke,rho,tanbeta)
    Y=np.asarray([yd/c,Z,Z,yu/s,p1,p2],complex)
    before=physical_offdiagonals(Y,tanbeta)
    after=physical_offdiagonals(evolve(Y,high,low,steps),tanbeta)
    return {"status":STATUS,"tanbeta":tanbeta,
            "high_GeV":high,"low_GeV":low,"steps":steps,
            "typeII_leptons_control":bool(typeii_leptons),
            "rho_scale":rho_scale,"initial":before,"final":after,
            "truncated_pure_2HDM_only":True,
            "full_Zee_f_coupled_RGE":False,
            "run_gauge_and_scalar_thresholds":False,
            "neutrino_LFV_fit":False,
            "quark_FCNC_flavor_likelihood":False,
            "allowed_Zee_point":None}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tanbeta",type=float,default=5.6)
    p.add_argument("--high",type=float,default=10000.)
    p.add_argument("--low",type=float,default=700.)
    p.add_argument("--steps",type=int,default=120)
    p.add_argument("--typeii-leptons-control",action="store_true")
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():p.error("Refusing overwrite")
    report=example(a.tanbeta,a.high,a.low,a.steps,
                   typeii_leptons=a.typeii_leptons_control)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2)+"\n")
    print("STATUS",STATUS)
    print("INITIAL",json.dumps(report["initial"],sort_keys=True))
    print("FINAL",json.dumps(report["final"],sort_keys=True))
    print("FULL_ZEE_RGE_OR_FCNC_LIKELIHOOD False")
    print("PHYSICAL_ZEE_ALLOWED False")
    print("OUTPUT",a.output)

if __name__=="__main__":main()
