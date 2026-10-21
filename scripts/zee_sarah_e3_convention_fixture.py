#!/usr/bin/env python3
"""ONE integrated E3/SARAH convention fixture (not a fitted E3 309 sample).

Source A1b provides Chen 2508.18757 Higgs-basis complex f,Y and M_nu.
A1b/Chen use 2 f and sqrt(2) Y in the charged scalar vertices; SARAH's
actual extracted couplings instead use fSARAH and
YD = -sin(beta)*Ye + cos(beta)*Ye2, so the test supplies
fSARAH = 2 fE3 and YD = sqrt(2) YE3 in a diagonal lepton basis.

The signed neutrino self-energy orientation is NOT independently obtained
from SARAH's self-energy loop generator; the Mathematica partner checks
a convention-chosen one-loop contraction and finite B0 kernel only.
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path
import numpy as np

from gateA1b_hierarchical_no_seed import (
    ME, MMU, MTAU, target_neutrino_matrix,
    antisymmetric_f_with_null_condition, solve_lepton_yukawa,
    reconstruct_neutrino, scalar_kappa,
)
from gateB2_zee_neutrino_family_scan import f_from_null_parameter
from gateB3_general_zee_charged_lepton_widths import charged_lepton_widths
from gate6_benchmark import benchmark

MASS_LEPTON = np.array([ME, MMU, MTAU],float)
STATUS = "CHEN_E3_CONVENTION_FIXTURE_NO_REAL_309_SOURCE_OR_SELFENERGY_CERTIFICATE"

def wlreal(v):
    v=float(v)
    if not math.isfinite(v):
        raise ValueError("non-finite Wolfram fixture")
    return f"{v:.17e}".replace("e","*^")

def wlc(v):
    v=complex(v)
    return "(" + wlreal(v.real) + " + I*(" + wlreal(v.imag) + "))"

def wlm(x):
    a=np.asarray(x)
    if a.shape!=(3,3):
        raise ValueError("expected 3x3 matrix")
    return "{" + ",".join(
        "{" + ",".join(map(wlc,row)) + "}" for row in a
    ) + "}"

def wlrule(name,value):
    if isinstance(value,str):
        return '"' + value + '"'
    if np.asarray(value).shape == (3,3):
        return wlm(value)
    return wlreal(value)

def lepton_log_kernel(m1,m2,ml):
    """Independent finite Feynman parameter integral of scalar B0 difference.

    Integral_0^1 dx log[(x*ml²+(1-x)*m1²)/(x*ml²+(1-x)*m2²)].
    In ml -> 0, equals log(m1²/m2²); explicit charged lepton mass
    dependence tests the approximation used in Chen's kappa.
    """
    x,w=np.polynomial.legendre.leggauss(120)
    x=(x+1)/2
    w=w/2
    a=x*ml**2+(1-x)*m1**2
    b=x*ml**2+(1-x)*m2**2
    return float(np.dot(w,np.log(a/b)))

def case(name,m1,m2,gamma,f,Y,target,beta,v):
    kap=scalar_kappa(m1,m2,gamma)
    y=np.asarray(Y,complex)
    f=np.asarray(f,complex)
    if f.shape!=(3,3) or y.shape!=(3,3):
        raise ValueError("bad source Yukawa matrices")
    if np.max(abs(f+f.T))>1e-12:
        raise ValueError("f source not antisymmetric")
    reconstructed=reconstruct_neutrino(f,y,kappa=kap)
    if np.max(abs(reconstructed-target))>1e-9:
        raise ValueError("Chen E3 neutrino closure failed")

    c,s=math.cos(beta),math.sin(beta)
    sCoupling=np.diag(np.sqrt(2.)*MASS_LEPTON/v)
    dCoupling=np.sqrt(2.)*y
    ye=c*sCoupling-s*dCoupling
    ye2=s*sCoupling+c*dCoupling
    fs=2.*f
    if np.max(abs(c*ye+s*ye2-sCoupling))>5e-15:
        raise ValueError("lepton mass Yukawa inverse rotation failed")
    if np.max(abs(-s*ye+c*ye2-dCoupling))>5e-15:
        raise ValueError("Higgs basis Yukawa inverse rotation failed")

    bw=charged_lepton_widths(m1,m2,gamma,f,y)
    widths=np.array([[bw["H1"][ell],bw["H2"][ell]]
                     for ell in ("e","mu","tau")],float)
    logs=np.array([lepton_log_kernel(m1,m2,m) for m in MASS_LEPTON])
    exact=np.zeros((3,3),complex)
    for ell in range(3):
        part=np.outer(f[:,ell],y[ell,:])
        exact+=(math.sqrt(2.)*math.sin(2*gamma)/(16*math.pi**2)) * (
            MASS_LEPTON[ell]*logs[ell]) * (part+part.T)
    exact*=1e9 # to eV
    rel=float(np.max(abs(exact-reconstructed))/
              max(1e-15,np.max(abs(target))))
    if not rel<3e-3:
        raise ValueError("finite-mass integral too far from Chen limit")
    if not np.allclose([lepton_log_kernel(m1,m2,0)],
                       [math.log(m1*m1/(m2*m2))],rtol=1e-11):
        raise ValueError("finite-integral zero-mass limit failed")

    entries={
      "Label":name, "M1":m1, "M2":m2, "Gamma":gamma, "Beta":beta, "V":v,
      "FChen":f,"YChen":y,"FSARAH":fs,"YeSARAH":ye,"Ye2SARAH":ye2,
      "TargetNuEV":target, "ChenMnuEV":reconstructed,
      "FiniteMnuEV":exact, "KappaChen":kap,
      "ExpectedWidths":widths,
      "LeptonMasses":MASS_LEPTON.astype(complex),
      "FiniteLogs":logs.astype(complex),
    }
    # ExpectedWidths is 3x2, and LeptonMasses/FiniteLogs are 3 vectors.
    raw=[]
    for key,value in entries.items():
        if key=="ExpectedWidths":
            encoded="{"+",".join("{"+",".join(wlreal(z) for z in row)+"}"
                                for row in widths)+"}"
        elif key in ("LeptonMasses","FiniteLogs"):
            encoded="{"+",".join(wlreal(z.real) for z in value)+"}"
        else:
            encoded=wlrule(key,value)
        raw.append('"'+key+'" -> '+encoded)
    return "<|" + ",".join(raw) + "|>",rel,np.max(abs(reconstructed-target))

def main():
    pa=argparse.ArgumentParser(description=__doc__)
    pa.add_argument("--out",type=Path,
       default=Path("work/sarah_zee/e3_charged_loop_fixture.m"))
    args=pa.parse_args()
    target,_=target_neutrino_matrix()
    f0,_=antisymmetric_f_with_null_condition(target)
    f1=f_from_null_parameter(target,t=0.37-0.29j,norm=0.002,root=1)
    gate=benchmark()
    b=gate["inputs"]["beta"];v=gate["inputs"]["v"]
    configs=[
      ("A1b_original",300.,700.,1.089,f0),
      ("B2_second_null_root",375.,925.,0.71,f1)
    ]
    cases=[]
    for name,m1,m2,gamma,f in configs:
        kap=scalar_kappa(m1,m2,gamma)
        y,rank,_=solve_lepton_yukawa(f,target,kappa=kap)
        if rank!=5:
            raise ValueError("neutrino source operator rank != 5")
        row,finiteRel,closure=case(name,m1,m2,gamma,f,y,target,b,v)
        cases.append(row)
        print("ZEE_E3_CASE",name,"kappa",kap,
              "source_closure_eV",closure,"finite_mass_relative_correction",finiteRel)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(
      "(* Generated from A1b + B2 + B3 + Gate6, not from SARAH vertices. *)\n"+
      "zeeE3Cases = {" + ",\n".join(cases) + "};\n"+
      "zeeE3FixtureStatus = \""+STATUS+"\";\n")
    print("ZEE_E3_FIXTURE_WRITTEN",args.out)
    print("ZEE_E3_FIXTURE_STATUS",STATUS)
    print("ZEE_E3_REAL_309_SOURCE_INCLUDED False")
    print("ZEE_E3_SARAH_SELFENERGY_GENERATED False")

if __name__=="__main__":
    main()
