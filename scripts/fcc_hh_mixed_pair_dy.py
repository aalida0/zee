#!/usr/bin/env python3
"""LO Drell-Yan rate screen for pp -> H1+ H2- + H1- H2+ at 80/100 TeV.

Only the off-diagonal Z H1 H2 vertex is included. NOT a Zee UFO,
a full constrained Zee model, or a detector-level production prediction.

Lagrangian: i*g12*Z_mu*(H1- <->d^mu H2+ + h.c.).
For a fixed final-state charge, massless initial q, 3 colors:
 sigmahat = gZ^2*g12^2*(gL^2+gR^2)*lambda^(3/2)
          / (288*pi*shat^2*((shat-MZ^2)^2+(MZ*GammaZ)^2)).
gZ=e/(sW*cW), gL=T3-Q*sW^2, gR=-Q*sW^2.
Other final-state charge assignment gives factor 2.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

GEV2_TO_FB = 3.89379338e11
MZ = 91.1876
GAMMA_Z = 2.4952
SW2 = 0.23122
ALPHA_MZ = 1/127.95
G12_P2_PILOT = 0.1520746183402528
FLAVORS = (1, 2, 3, 4, 5)


def zee_g12(gamma: float, *, alpha: float = ALPHA_MZ,
            sw2: float = SW2) -> float:
    ee = math.sqrt(4*math.pi*alpha)
    return ee*math.sin(gamma)*math.cos(gamma)/(2*math.sqrt(sw2*(1-sw2)))


def lambda_kallen(shat: float, m1: float, m2: float) -> float:
    return max(0., (shat-(m1+m2)**2)*(shat-(m1-m2)**2))


def sigmahat_qqbar_to_h1h2(
        shat: float, m1: float, m2: float, pid: int,
        *, g12: float = G12_P2_PILOT, alpha: float = ALPHA_MZ,
        sw2: float = SW2, mz: float = MZ, gamma_z: float = GAMMA_Z,
        color_factor: int = 3) -> float:
    """Partonic σ in GeV^-2 for ONE H1+H2- assignment."""
    if min(m1, m2) <= 0 or color_factor < 1 or pid not in FLAVORS:
        raise ValueError("Bad mass, initial flavor or color")
    if not 0 < sw2 < 1 or alpha <= 0 or gamma_z < 0:
        raise ValueError("Bad EW inputs")
    if shat <= (m1+m2)**2:
        return 0.
    up = pid in (2, 4)
    charge = 2/3 if up else -1/3
    t3 = .5 if up else -.5
    gl = t3-charge*sw2
    gr = -charge*sw2
    gz2 = 4*math.pi*alpha/(sw2*(1-sw2))
    prop = (shat-mz*mz)**2+(mz*gamma_z)**2
    return (gz2*g12*g12*(gl*gl+gr*gr)*
            lambda_kallen(shat,m1,m2)**1.5 /
            (96*color_factor*math.pi*shat**2*prop))


def rate_pp_mixed_pair(
    pdf, *, sqrt_s_tev: float = 100., m1: float = 300.,
    m2: float = 700., g12: float = G12_P2_PILOT,
    nodes_tau: int = 60, nodes_y: int = 40,
    q_gev: float | None = None,
    flavors: tuple[int, ...] = FLAVORS,
) -> dict:
    """Integrate five-flavor LO pp Drell-Yan with lhapdf-like xfxQ(pid,x,Q).

    x1*x2=tau, y=log(x1/sqrt(tau)); d x1 d x2=d tau d y.
    PDFs use x*f(x,Q), hence product contributes 1/tau.
    With tau=tau0*exp(t*log(1/tau0)), d tau/tau=log(1/tau0)dt.
    pp luminosity is even under y -> -y after qqbar+qbarq sum.
    """
    if sqrt_s_tev <= 0 or min(m1,m2) <= 0 or nodes_tau<3 or nodes_y<3:
        raise ValueError("Invalid collider inputs")
    ss = (sqrt_s_tev*1000)**2
    tau0 = (m1+m2)**2/ss
    if tau0 >= 1:
        return {"sqrt_s_tev":sqrt_s_tev,"sigma_per_charge_fb":0.,
                "sigma_both_charges_fb":0.,"tau_min":tau0}
    Q = q_gev if q_gev is not None else m1+m2
    if Q <= 0:
        raise ValueError("PDF scale must be positive")
    tx,tw = np.polynomial.legendre.leggauss(nodes_tau)
    yx,yw = np.polynomial.legendre.leggauss(nodes_y)
    tx,tw=(tx+1)/2,tw/2
    yx,yw=(yx+1)/2,yw/2
    L=math.log(1/tau0)
    contributions={str(pid):0. for pid in flavors}
    for t,wt in zip(tx,tw):
        tau=tau0*math.exp(t*L)
        shat=tau*ss
        Y=-.5*math.log(tau)
        part={pid:sigmahat_qqbar_to_h1h2(shat,m1,m2,pid,g12=g12)
              *GEV2_TO_FB for pid in flavors}
        for z,wz in zip(yx,yw):
            y=Y*z
            x1=math.sqrt(tau)*math.exp(y)
            x2=math.sqrt(tau)*math.exp(-y)
            if not (0<x1<1 and 0<x2<1):
                raise AssertionError(f"Invalid x1/x2: {x1}/{x2}")
            for pid in flavors:
                lum=(pdf.xfxQ(pid,x1,Q)*pdf.xfxQ(-pid,x2,Q)+
                     pdf.xfxQ(-pid,x1,Q)*pdf.xfxQ(pid,x2,Q))
                contributions[str(pid)] += (wt*wz*2*Y*L*
                                            lum*part[pid])
    one=sum(contributions.values())
    return {
        "status":"LO_Z_OFFDIAGONAL_ONLY_NOT_A_ZEE_UFO",
        "sqrt_s_tev":sqrt_s_tev,
        "mH1_GeV":m1,"mH2_GeV":m2,"g_ZH1H2":g12,
        "pdf_Q_GeV":Q,"tau_min":tau0,
        "nodes_tau":nodes_tau,"nodes_y":nodes_y,
        "sigma_per_charge_fb":one,
        "sigma_both_charges_fb":2*one,
        "per_charge_quark_flavor_fb":contributions,
        "uncertainties":"PDF, scale, scheme, EW-input NOT quantified",
        "branching_fractions_acceptance_backgrounds":"NOT INCLUDED",
    }


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--energy-tev",type=float,nargs="+",default=[80,100])
    p.add_argument("--m1",type=float,default=300.)
    p.add_argument("--m2",type=float,default=700.)
    p.add_argument("--gamma",type=float,default=1.089)
    p.add_argument("--g12",type=float,default=G12_P2_PILOT)
    p.add_argument("--pdf-set",default="NNPDF31_lo_as_0130")
    p.add_argument("--pdf-member",type=int,default=0)
    p.add_argument("--pdf-q-gev",type=float)
    p.add_argument("--nodes-tau",type=int,default=60)
    p.add_argument("--nodes-y",type=int,default=40)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    try:
        import lhapdf
        pdf=lhapdf.mkPDF(args.pdf_set,args.pdf_member)
    except (ImportError,RuntimeError,OSError) as e:
        raise SystemExit(
            "LHAPDF or PDF set not available. With Key4hep active run "
            "python3 -c 'import lhapdf; print(lhapdf.availablePDFSets())'. "
            f"Details: {e}"
        ) from e
    summary={
        "model":"off-diagonal Z-only Drell-Yan screening; NOT full Zee UFO",
        "pdf_set":args.pdf_set,"pdf_member":args.pdf_member,
        "gamma_rad":args.gamma,
        "g12_from_alpha_mz_convention":zee_g12(args.gamma),
        "rates":[]
    }
    for energy in args.energy_tev:
        summary["rates"].append(rate_pp_mixed_pair(
            pdf,sqrt_s_tev=energy,m1=args.m1,m2=args.m2,g12=args.g12,
            q_gev=args.pdf_q_gev,nodes_tau=args.nodes_tau,
            nodes_y=args.nodes_y))
    data=json.dumps(summary,indent=2)+"\n"
    print(data,end="")
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(data)


if __name__=="__main__":
    main()
