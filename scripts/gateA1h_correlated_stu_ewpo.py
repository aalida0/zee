#!/usr/bin/env python3
"""Gate A1H: Zee scalar-sector S,T,U and correlated EWPO likelihood screen.

Grimus et al. arXiv:0802.4353 Eqs.(28),(30),(31), App.B,C.
Florentino et al. arXiv:2106.08332 Eqs.(23),(24): U,V mixing.
The functions G, Ghat are evaluated from finite Feynman-parameter
integrals (Grimus B2, B3, B11, C1-C5) to avoid severe cancellation in
analytic large-mass expressions.

T is imported unchanged from the validated Gate A1G with Grimus -2
charged off-diagonal coefficient. Correlated fits are the *published*
Gfitter 2026 and PDG 2025 STU Gaussian summaries, not new full fits.

NOT an independently validated experimental fit, nor a global Zee pass.
Additional vertex, flavour, Higgs and scalar constraints remain absent.
"""
from __future__ import annotations
import argparse
from functools import lru_cache
import json
from pathlib import Path

import numpy as np
from gateA1g_zee_oblique_T import (
    oblique_T, MW, MZ, ALPHA, BETA, GAMMA,
    MH_SM, MH_HEAVY, MA, MH1_CHARGED, MH2_CHARGED
)

CHI2_95_3DOF = 7.814727903251179
# Source: Gfitter 2026, https://project-gfitter.web.cern.ch/Oblique_Parameters/
# Reference MH=125 GeV and mtop=172.5 GeV.
FITS = {
    "Gfitter_2026_U_floating": {
        "central": [0.03, 0.05, -0.03],
        "sigma": [0.10, 0.12, 0.09],
        "rho": [[1.0, 0.92, -0.67],
                [0.92, 1.0, -0.88],
                [-0.67, -0.88, 1.0]],
        "source": "https://project-gfitter.web.cern.ch/Oblique_Parameters/",
    },
    "PDG_2025_U_floating": {
        "central": [0.021, 0.04, 0.008],
        "sigma": [0.096, 0.12, 0.092],
        "rho": [[1.0, 0.91, -0.62],
                [0.91, 1.0, -0.83],
                [-0.62, -0.83, 1.0]],
        "source": "https://pdg.lbl.gov/2025/reviews/rpp2025-rev-standard-model.pdf Table 10.8",
    },
}

@lru_cache(maxsize=5)
def quadrature(n=160):
    """Gauss-Legendre integral nodes/weights on [0,1]."""
    nodes, weights = np.polynomial.legendre.leggauss(n)
    return (nodes+1.)/2., weights/2.

def _f_log1p_ratio(u):
    """(1-u)log(1-u)+u, stable for u << 1."""
    out=np.empty_like(u)
    small=np.abs(u)<1e-3
    v=u[small]
    out[small]=v*v*(.5+v*(1/6+v*(1/12+v*(1/20+v/30))))
    v=u[~small]
    out[~small]=(1.-v)*np.log1p(-v)+v
    return out

def grimus_G(I,J,Q,n=160):
    """Grimus C2 dimensionless G(I,J,Q) via B3 and C1 integral.

    I,J,Q are strictly-positive masses SQUARED.  At our benchmarks Q
    lies below two-particle thresholds, so log arguments stay positive.
    Div and reference logarithms cancel analytically.
    """
    if min(I,J,Q)<=0:
        raise ValueError("Mass squares must be positive")
    x,w=quadrature(n)
    D=I*(1-x)+J*x
    u=Q*x*(1-x)/D
    if np.any(u>=1):
        raise ValueError("This real Feynman-parameter implementation needs Q below threshold")
    # 12 int x(1-x) log D - log I - log J
    # -12 int [D/Q*((1-u)log(1-u)+u)].
    # The common scale in all logarithms cancels exactly.
    muref=MH_SM**2
    result=(12*np.dot(w,x*(1-x)*np.log(D/muref))
            -np.log(I/muref)-np.log(J/muref)
            -12*np.dot(w,D/Q*_f_log1p_ratio(u)))
    return float(result)

def grimus_Ghat(I,Q,n=160):
    """Grimus C5: Ghat(I,Q)=G(I,Q,Q)+12 Gtilde(I,Q,Q).

    Gtilde = 2 int_0^1 dx log(1-Q*x(1-x)/[I(1-x)+Q*x])
    is derived independently from B11 and C3.
    """
    if min(I,Q)<=0:
        raise ValueError("Mass squares must be positive")
    x,w=quadrature(n)
    D=I*(1-x)+Q*x
    u=Q*x*(1-x)/D
    if np.any(u>=1):
        raise ValueError("Threshold in Ghat")
    return float(grimus_G(I,Q,Q,n=n)+24*np.dot(w,np.log1p(-u)))

def florentino_mixing(alpha=ALPHA,beta=BETA,gamma=GAMMA):
    """U(2x3),V(2x4) per Florentino 2106.08332 Eqs.(23),(24).

    Physical charged: columns U=G+,H1+,H2+.
    Neutral: V=G0,h125,Hheavy,A.
    """
    cb,sb=np.cos(beta),np.sin(beta)
    ca,sa=np.cos(alpha),np.sin(alpha)
    cg,sg=np.cos(gamma),np.sin(gamma)
    U=np.array([
        [cb,-sb*cg,sb*sg],
        [sb,cb*cg,-cb*sg]
    ],complex)
    V=np.array([
        [1j*cb,ca,-sa,-1j*sb],
        [1j*sb,sa,ca,1j*cb]
    ],complex)
    return U,V

def stu_S_U(*,m1=MH1_CHARGED,m2=MH2_CHARGED,
            mh=MH_SM,mH=MH_HEAVY,mA=MA,
            alpha=ALPHA,beta=BETA,gamma=GAMMA,
            mW=MW,mZ=MZ,n=160):
    """Evaluate Grimus 0802.4353 Eq.(30),(31): S,U=braces/(24*pi).

    Builds full U,V rather than hand-assigning mixing weights.
    Excludes Goldstone columns from physical-state sums and subtracts
    the 125 GeV reference SM Higgs contribution.
    """
    U,V=florentino_mixing(alpha,beta,gamma)
    UU=U.conj().T@U
    UV=U.conj().T@V
    VV=V.conj().T@V
    charged=np.asarray([m1,m2],float)**2
    neutral=np.asarray([mh,mH,mA],float)**2
    QZ=float(mZ*mZ)
    QW=float(mW*mW)
    sw2=1-QW/QZ
    if not 0<sw2<1:
        raise ValueError("invalid electroweak input")
    gc=lambda I,J,Q:grimus_G(I,J,Q,n=n)
    gh=lambda I,Q:grimus_Ghat(I,Q,n=n)
    S_terms={
        "charged_diagonal":sum((2*sw2-UU[a,a].real)**2*
                               gc(charged[a-1],charged[a-1],QZ)
                               for a in (1,2)),
        "charged_offdiagonal":2*abs(UU[1,2])**2*
                              gc(charged[0],charged[1],QZ),
        "neutral_pairs":sum(VV[b,bp].imag**2*
                            gc(neutral[b-1],neutral[bp-1],QZ)
                            for b in (1,2,3) for bp in range(b+1,4)),
        "mass_logs":(
            -2*sum(UU[a,a].real*np.log(charged[a-1]/mh**2)
                   for a in (1,2))
            +sum(VV[b,b].real*np.log(neutral[b-1]/mh**2)
                 for b in (1,2,3))),
        "SM_reference_mixed":(
            sum(VV[0,b].imag**2*gh(neutral[b-1],QZ)
                for b in (1,2,3))-gh(mh*mh,QZ)),
    }
    U_terms={
        "W_charged_neutral":sum(abs(UV[a,b])**2*
                                gc(charged[a-1],neutral[b-1],QW)
                                for a in (1,2) for b in (1,2,3)),
        "minus_charged_diagonal":-S_terms["charged_diagonal"],
        "minus_charged_offdiagonal":-S_terms["charged_offdiagonal"],
        "minus_neutral_pairs":-S_terms["neutral_pairs"],
        "SM_reference_mixed_WZ_diff":(
            sum(VV[0,b].imag**2*
                (gh(neutral[b-1],QW)-gh(neutral[b-1],QZ))
                for b in (1,2,3))
            -(gh(mh*mh,QW)-gh(mh*mh,QZ))),
    }
    # sum(log weights) = -2 trace UU_phys + trace VV_phys - 1 = 0
    log_weight_identity=(-2*sum(UU[a,a].real for a in (1,2))
                         +sum(VV[b,b].real for b in (1,2,3))-1.)
    return {
        "S":float(sum(S_terms.values())/(24*np.pi)),
        "U":float(sum(U_terms.values())/(24*np.pi)),
        "S_numerator_terms":{k:float(v) for k,v in S_terms.items()},
        "U_numerator_terms":{k:float(v) for k,v in U_terms.items()},
        "UV_mixing_closure_log_weight":float(log_weight_identity),
        "charged_overlap_squared":float(abs(UU[1,2])**2),
        "h125_reduced_WW_ZZ":float(abs(VV[0,1].imag)),
    }

def correlated_fit(S,T,U,name):
    fit=FITS[name]
    mean=np.asarray(fit["central"],float)
    sd=np.asarray(fit["sigma"],float)
    rho=np.asarray(fit["rho"],float)
    cov=sd[:,None]*rho*sd[None,:]
    if np.min(np.linalg.eigvalsh(cov))<=0:
        raise RuntimeError("Fit covariance is not positive definite")
    delta=np.asarray([S,T,U])-mean
    chi2=float(delta@np.linalg.solve(cov,delta))
    from scipy.stats import chi2 as chi2dist
    return {
        "source":fit["source"],
        "central_STU":mean.tolist(),
        "sigma_STU":sd.tolist(),
        "correlation_STU":rho.tolist(),
        "covariance_STU":cov.tolist(),
        "chi2_relative_to_fit_minimum":chi2,
        "p_value_3d_Gaussian_fit_region":float(chi2dist.sf(chi2,df=3)),
        "chi2_95percent_3DOF":CHI2_95_3DOF,
        "inside_95percent_3D_gaussian_ellipsoid":bool(chi2<CHI2_95_3DOF),
        "interpretation":"published correlated Gaussian approximation; not a re-fit to EW observables",
    }

def report(**kwargs):
    values=stu_S_U(**kwargs)
    T,_=oblique_T(m1=kwargs.get("m1",MH1_CHARGED),
                  m2=kwargs.get("m2",MH2_CHARGED),
                  mh=kwargs.get("mh",MH_SM),
                  mH=kwargs.get("mH",MH_HEAVY),
                  mA=kwargs.get("mA",MA),
                  alpha=kwargs.get("alpha",ALPHA),
                  beta=kwargs.get("beta",BETA),
                  gamma=kwargs.get("gamma",GAMMA),
                  mW=kwargs.get("mW",MW),
                  mZ=kwargs.get("mZ",MZ),
                  coefficient=2.)
    S,U=values["S"],values["U"]
    return {
        "status":"SCALAR_STU_GAUSSIAN_EWPO_SCREEN_NOT_GLOBAL_ZEE_BENCHMARK",
        "scalar_STU":{"S":S,"T":T,"U":U},
        "scalar_inputs":{
            "mH1_charged_GeV":kwargs.get("m1",MH1_CHARGED),
            "mH2_charged_GeV":kwargs.get("m2",MH2_CHARGED),
            "mh125_GeV":kwargs.get("mh",MH_SM),
            "mHheavy_GeV":kwargs.get("mH",MH_HEAVY),
            "mA_GeV":kwargs.get("mA",MA),
            "alpha_rad":kwargs.get("alpha",ALPHA),
            "beta_rad":kwargs.get("beta",BETA),
            "gamma_rad":kwargs.get("gamma",GAMMA),
            "mW_GeV":kwargs.get("mW",MW),
            "mZ_GeV":kwargs.get("mZ",MZ),
        },
        "loop_diagnostics":values,
        "correlated_fit_screens":{
            k:correlated_fit(S,T,U,k) for k in FITS
        },
        "sources":[
            "Grimus arXiv:0802.4353 Eqs.(28),(30),(31), App.B,C",
            "Florentino arXiv:2106.08332 Eqs.(23),(24)",
            "Gfitter 2026 oblique three-parameter full covariance",
            "PDG 2025 review Eq/Table 10.8, three-parameter case",
        ],
        "not_checked":[
            "EW observables beyond oblique approximation including nonuniversal vertices",
            "uncertainty from higher-loop BSM EW self-energies",
            "Higgs constraints, B->Xs gamma, flavour, global scalar vacuum",
            "full Barr-Zee LFV and complete benchmark signal widths/rates",
        ],
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path)
    p.add_argument("--mH1",type=float,default=MH1_CHARGED)
    p.add_argument("--mH2",type=float,default=MH2_CHARGED)
    p.add_argument("--mH",type=float,default=MH_HEAVY)
    p.add_argument("--mA",type=float,default=MA)
    p.add_argument("--alpha",type=float,default=ALPHA)
    p.add_argument("--beta",type=float,default=BETA)
    p.add_argument("--gamma",type=float,default=GAMMA)
    p.add_argument("--quad-nodes",type=int,default=160)
    a=p.parse_args()
    r=report(m1=a.mH1,m2=a.mH2,mH=a.mH,mA=a.mA,alpha=a.alpha,
             beta=a.beta,gamma=a.gamma,n=a.quad_nodes)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(r,indent=2)+"\n")
        print("Wrote",a.output)
    v=r["scalar_STU"]
    print(f"S = {v['S']:.9f}; T = {v['T']:.9f}; U = {v['U']:.9f}")
    for name,d in r["correlated_fit_screens"].items():
        print(f"{name}: chi2={d['chi2_relative_to_fit_minimum']:.6f}, "
              f"p3d={d['p_value_3d_Gaussian_fit_region']:.6f}, "
              f"within_95percent={d['inside_95percent_3D_gaussian_ellipsoid']}")
    print("STATUS:",r["status"])
    assert abs(r["loop_diagnostics"]["UV_mixing_closure_log_weight"])<1e-12
    assert all(x["inside_95percent_3D_gaussian_ellipsoid"]
               for x in r["correlated_fit_screens"].values())

if __name__=="__main__":
    main()
