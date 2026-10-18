#!/usr/bin/env python3
"""Q2e SOURCE-REPRODUCTION of a REDUCED historical Zee one-loop RGE.

Kanemura, Kasai, Lin, Okada, Tseng & Yuan, Phys Rev D64 053007
(2001), arXiv:hep-ph/0011357v2, Appendix A Eqs (A1)-(A3),
(A12)-(A13), and Sec.III. Original authors keep top Yukawa
only (neglect other ordinary fermion Yukawas) and use f products
without complex conjugation. THIS REPRODUCTION IS RESTRICTED
TO REAL antisymmetric f. It is NOT a general complex Zee f beta,
NOT a calculation of Pi1,Pi2 beta, lambda6,lambda7 beta, LFV,
quark FCNC or physically allowed point.

D=16*pi*pi d/dln(mu), g1=SM hypercharge g', NOT GUT g1.
Dg=(22/3*g1^3,-3*g2^3,-7*g3^3).
Dyt=yt[-17/12*g1^2-9/4*g2^2-8*g3^2+9/2*yt^2].
D f_ij=-(3/2*g1^2+9/2*g2^2)*f_ij
       +4*sum_kl(f_kl^2)*f_ij
       -4*sum_kl(f_ik*f_kl*f_lj).
For any *real 3x3 antisymmetric f* and
q=sum(i<j) f_ij^2, f^3=-q f and sum_ij f_ij^2=2q.
Therefore Df=[-3/2*g1^2-9/2*g2^2+12*q]*f.

No threshold matching. This is an exact check of the source's
reduced beta functions, not a full Zee model computation.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import numpy as np

STATUS="Q2E_PUBLISHED_2001_REDUCED_REAL_F_RGES_REPRODUCED_NOT_GENERAL_ZEE_OR_ALLOWED"
SOURCE="https://arxiv.org/abs/hep-ph/0011357"
LOOP=16*math.pi**2
GAUGE_B=(22./3.,-3.,-7.)

def check_f(f):
    a=np.asarray(f)
    if a.shape!=(3,3) or np.iscomplexobj(a):
        raise ValueError("Historical A13 implementation ONLY accepts real 3x3 f")
    a=np.asarray(a,dtype=float)
    if not np.isfinite(a).all() or np.max(abs(a+a.T))>1e-12:
        raise ValueError("Historical f must be finite and antisymmetric")
    return a

def f_invariant(f):
    a=check_f(f)
    return float(np.sum(np.triu(a,1)**2))

def beta_f_matrix(f,g1,g2):
    a=check_f(f)
    if not all(math.isfinite(x) for x in (g1,g2)):
        raise ValueError("Finite gauge couplings required")
    q=f_invariant(a)
    return (-(1.5*g1*g1+4.5*g2*g2)*a
            +4.*(2*q)*a-4.*(a@a@a))

def beta_f_reduced(f,g1,g2):
    a=check_f(f)
    q=f_invariant(a)
    return (-(1.5*g1*g1+4.5*g2*g2)+12*q)*a

def beta_reduced(g,y,f):
    gauge=np.asarray(g,dtype=float)
    if gauge.shape!=(3,) or not np.isfinite(gauge).all() or (
            gauge<=0).any() or not math.isfinite(y) or y<0:
        raise ValueError("Require positive real gauge and nonnegative top Yukawa")
    a=check_f(f)
    g1,g2,g3=gauge
    dg=np.asarray(GAUGE_B)*gauge**3
    dy=y*(-17/12*g1*g1-9/4*g2*g2-8*g3*g3+4.5*y*y)
    return dg, float(dy),beta_f_matrix(a,g1,g2)

def initial():
    a=np.zeros((3,3),float)
    a[0,1]=.001
    a[0,2]=-.002
    a[1,2]=.003
    a=a-a.T
    return np.array([.36,.65,1.18]),.95,a

def run(high=10000.,low=700.,steps=120,*,gauge=None,yt=None,f=None):
    """Fixed full-field-content one-loop RK4. No thresholds or matching."""
    if not all(math.isfinite(x) and x>0 for x in (high,low)) or steps<8:
        raise ValueError("Invalid scales/steps")
    if gauge is None or yt is None or f is None:
        g0,y0,f0=initial()
        if gauge is None:gauge=g0
        if yt is None:yt=y0
        if f is None:f=f0
    g=np.asarray(gauge,dtype=float).copy()
    y=float(yt)
    a=check_f(f).copy()
    if high<low:
        raise ValueError("Use high>low and specify initial input at low")
    log_step=math.log(high/low)/steps

    def add(state,derivative,coef):
        g,y,a=state
        dg,dy,da=derivative
        return g+coef*dg/LOOP,y+coef*dy/LOOP,a+coef*da/LOOP

    def function(state):
        return beta_reduced(*state)
    init=[g.copy(),y,a.copy()]
    for _ in range(steps):
        st=(g,y,a)
        k1=function(st)
        k2=function(add(st,k1,log_step/2))
        k3=function(add(st,k2,log_step/2))
        k4=function(add(st,k3,log_step))
        step=(log_step/6)
        g,y,a=add(st,(
            k1[0]+2*k2[0]+2*k3[0]+k4[0],
            k1[1]+2*k2[1]+2*k3[1]+k4[1],
            k1[2]+2*k2[2]+2*k3[2]+k4[2]),step)
        if not np.isfinite(g).all() or not np.isfinite(a).all() or (
                 not math.isfinite(y)):
            raise ValueError("RG flow nonfinite")
        if np.max(abs(a+a.T))>1e-11:
            raise ValueError("Antisymmetry not preserved")
    initial_q=f_invariant(init[2])
    final_q=f_invariant(a)
    return {
        "status":STATUS,
        "source":SOURCE,
        "scale_low_GeV":low,
        "scale_high_GeV":high,
        "RK4_steps":steps,
        "gauge_initial":init[0].tolist(),
        "gauge_final":g.tolist(),
        "top_yukawa_initial":init[1],
        "top_yukawa_final":y,
        "f_initial":init[2].tolist(),
        "f_final":a.tolist(),
        "q_initial":initial_q,
        "q_final":final_q,
        "f_scale_ratio_sqrt_q":math.sqrt(final_q/initial_q) if initial_q else None,
        "f_beta_matrix_vs_3d_identity_error":float(np.max(abs(
           beta_f_matrix(a,g[0],g[1])-beta_f_reduced(a,g[0],g[1]))),
        "general_complex_f_supported":False,
        "ordinary_lepton_Pi_beta_included":False,
        "quartic_lambda6_lambda7_beta_included":False,
        "quark_FCNC_likelihood":False,
        "physical_Zee_allowed":None,
    }

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path)
    p.add_argument("--steps",type=int,default=120)
    x=p.parse_args()
    result=run(steps=x.steps)
    if x.output:
        x.output.parent.mkdir(parents=True,exist_ok=True)
        x.output.write_text(json.dumps(result,indent=2)+"\n")
    print("STATUS",result["status"])
    print("f_scale_ratio_sqrt_q",result["f_scale_ratio_sqrt_q"])
    print("f_beta_matrix_3d_identity_residual",result[
        "f_beta_matrix_vs_3d_identity_error"])
    print("FULL_ZEE_COMPLEX_LEPTON_YUKAWA_RGES False")
