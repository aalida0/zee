#!/usr/bin/env python3
"""Finite-mass, full three-body photon-DIPOLE phase-space kernels.

This integrates a constant on-shell photon dipole operator at off-shell q^2,
including the crossed photon diagram for identical final leptons.
It does NOT compute the genuine q^2-dependent Zee photon monopole,
the physical two-loop K2(q^2), the relative phase with neutral-scalar
tree operators, or any other LFV amplitude.

For exact identical-lepton integration, exploit the exchange symmetry:
(1/2) int |A_direct - A_cross|^2
  = int (|A_direct|^2 - Re[A_direct A_cross*]).
This prevents missed collinear logarithms in a low-order Dalitz grid.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from module3 import tree
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_neutral_tree import (
    CARD_IDS, GAMMA_TAU_GEV, evaluate_tree
)
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_mixed_flavour_tree import (
    evaluate as evaluate_mixed_tree
)
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_radiative_threebody_diagnostic import (
    evaluate as read_radiative
)
from research.full_constraints.lfv_2hdm_transfer_2026.evaluate import read_cards

METRIC = np.array([1., -1., -1., -1.])
ALPHA_PAIR = 1/137.035999084
ALPHA_SOURCE = 1/127.95
SIGMA = np.array([
    [0.5j*(tree.G[mu]@tree.G[nu]-tree.G[nu]@tree.G[mu]) for nu in range(4)]
    for mu in range(4)
])
CHANNELS = (
    ("tau_to_3e", "tauegamma", 0, 0, "same"),
    ("tau_to_3mu", "taumugamma", 1, 1, "same"),
    ("tau_to_e_minus_mu_minus_mu_plus", "tauegamma", 0, 1, "mixed"),
    ("tau_to_mu_minus_e_minus_e_plus", "taumugamma", 1, 0, "mixed"),
)


def spin_inner(a: np.ndarray, b: np.ndarray, ps, mass: float, masses) -> complex:
    """Independent bilinear extension of the existing module3.tree.spin_sum."""
    ds = [(tree.slash(p)+m*np.eye(4))@tree.G0
          for p,m in zip(ps,[mass,*masses[:2],-masses[2]])]
    u = np.einsum('ea,abcd->ebcd',ds[1],a)
    u = np.einsum('bf,ebcd->efcd',ds[0],u)
    u = np.einsum('gc,efcd->efgd',ds[2],u)
    u = np.einsum('dh,efgd->efgh',ds[3],u)
    return np.sum(u*b.conjugate())/2


def photon_tensors(ps, parent_mass, cl, cr, *, identical: bool,
                   alpha_pair=ALPHA_PAIR, alpha_source=ALPHA_SOURCE):
    """Ordered 4-spinor tensors in module3.tree basis.

    L_dipole=(e m_tau/2) bar(l) sigma^{mu nu}(CL PL+CR PR)tau F_mu nu.
    The overall common complex phase is immaterial here: only the dipole
    squared and its relative CL/CR phase are computed, not scalar interference.
    """
    chirality = cl*tree.PL+cr*tree.PR
    factor = 4*math.pi*math.sqrt(alpha_pair*alpha_source)*parent_mass
    def sigma_current(q):
        qcov = q*METRIC
        sigma_q = np.einsum('mnab,n->mab',SIGMA,qcov)
        return [tree.G0@sigma_q[mu]@chirality for mu in range(4)]
    def current(mu):
        return METRIC[mu]*tree.G0@tree.G[mu]
    q=ps[2]+ps[3]
    q2=q[0]*q[0]-np.dot(q[1:],q[1:])
    if q2<=0:
        raise ArithmeticError("non-timelike photon propagator")
    d=np.zeros((4,4,4,4),dtype=complex)
    for mu, op in enumerate(sigma_current(q)):
        d+=np.einsum('ab,cd->abcd',op,current(mu))
    d *= factor/q2
    if not identical:
        return d, None
    qx=ps[1]+ps[3]
    qx2=qx[0]*qx[0]-np.dot(qx[1:],qx[1:])
    if qx2<=0:
        raise ArithmeticError("non-timelike crossed photon")
    c=np.zeros_like(d)
    for mu,op in enumerate(sigma_current(qx)):
        c-=np.einsum('cb,ad->abcd',op,current(mu))
    c *= factor/qx2
    return d,c


def photon_width(mass:float,ma:float,mb:float,cl:complex=1.,cr:complex=0.,
                 ns:int=64,nz:int=24)->float:
    """Full-mass constant-dipole tree-level tau->l_a l_b l_b width [GeV].

    Logarithmic s=(p2+p3)^2 mapping resolves near-collinear e+e-.
    The identical-particle crossing identity is integrated analytically
    in the direct-square term but NOT an approximation to the exchange term.
    """
    if (type(ns) is not int or type(nz) is not int or
            ns<12 or ns>160 or nz<8 or nz>128):
        raise ValueError("ns in [12,160] and nz in [8,128] must be integers")
    vals=(mass,ma,mb)
    if any(not math.isfinite(x) or x<=0 for x in vals) or mass<=ma+2*mb:
        raise ValueError("invalid three-body masses or closed decay")
    if not (math.isfinite(complex(cl).real) and math.isfinite(complex(cl).imag)
            and math.isfinite(complex(cr).real) and math.isfinite(complex(cr).imag)):
        raise ValueError("nonfinite dipole coefficient")
    s0,s1=(2*mb)**2,(mass-ma)**2
    logrange=math.log(s1/s0)
    sn,sw=np.polynomial.legendre.leggauss(ns)
    zn,zw=np.polynomial.legendre.leggauss(nz)
    masses=(ma,mb,mb)
    identical=(ma==mb)
    total=0.
    for t,wt in zip(sn,sw):
        s=s0*math.exp(logrange*(t+1)/2)
        jac=s*logrange/2
        phase=math.sqrt(max(0.,tree.kallen(mass*mass,ma*ma,s) *
                             tree.kallen(s,mb*mb,mb*mb)))
        phase/=512*math.pi**3*mass**3*s
        for z,wz in zip(zn,zw):
            ps=tree.momenta(mass,masses,s,z)
            direct,cross=photon_tensors(ps,mass,cl,cr,identical=identical)
            # Exact exchange identity after full phase-space integration:
            # 1/2 int (|d|²+|c|² +2Re d*c) = int (|d|²+Re d*c).
            # Crucially: no further factor 1/2 for identical pair.
            val=tree.spin_sum(direct,ps,mass,masses)
            if identical:
                val+=spin_inner(direct,cross,ps,mass,masses).real
            total+=wt*wz*jac*phase*val
    if total<=0 or not math.isfinite(total):
        raise ArithmeticError("nonpositive or nonfinite dipole width")
    return total


def radiative_width_unit(mass:float,ma:float)->float:
    """Source normalization used by original module3.core.radiative_width."""
    return ALPHA_SOURCE*mass**5*(1-(ma/mass)**2)**3/4


def kernel_range(mass:float,ma:float,mb:float,ns:int=64,nz:int=24)->dict:
    """Eigenvalue interval for ANY complex CL,CR at fixed radiative BR.

    The 2x2 positive semidefinite Hermitian quadratic form is evaluated by
    four explicit spin-summed phase-space calculations. For an unknown
    complex dipole vector, min/max eigenvalues are phase-independent.
    """
    ref=radiative_width_unit(mass,ma)
    rl=photon_width(mass,ma,mb,1,0,ns,nz)/ref
    rr=photon_width(mass,ma,mb,0,1,ns,nz)/ref
    rp=photon_width(mass,ma,mb,1,1,ns,nz)/(2*ref)
    ri=photon_width(mass,ma,mb,1,1j,ns,nz)/(2*ref)
    mean=(rl+rr)/2
    re=rp-mean
    im=ri-mean
    difference=math.sqrt(((rl-rr)/2)**2+re**2+im**2)
    if mean-difference<=0:
        raise ArithmeticError("nonpositive dipole rate eigenvalue")
    return {
        "pure_CL_conversion": rl, "pure_CR_conversion":rr,
        "equal_real_CL_CR_conversion": rp,
        "relative_imaginary_CL_CR_conversion": ri,
        "conversion_eigen_min":mean-difference,
        "conversion_eigen_max":mean+difference,
        "chirality_independent_spectral_deviation":difference,
        "kernel_Hermitian_spectrum_positive":True,
    }


def phase_independent_tree_dipole_envelope(dmin:float,dmax:float,tree_rate:float)->dict:
    """Sharp norm-only Cauchy bounds for the two INCLUDED amplitudes.

    This is conditional on the dipole rate interval and tree rate being
    computed in a common phase-space/normalization scheme. It cannot bound
    absent photon monopole, boxes, Zee-specific 2loop or any other diagram.
    """
    if any(not math.isfinite(x) or x<0 for x in (dmin,dmax,tree_rate)) or dmin>dmax:
        raise ValueError("nonnegative ordered rate interval required")
    rt=math.sqrt(tree_rate)
    rlo,rhi=math.sqrt(dmin),math.sqrt(dmax)
    if rlo<=rt<=rhi:
        lower=0.
    else:
        lower=min((rlo-rt)**2,(rhi-rt)**2)
    return {"subset_norm_lower":lower,
            "subset_norm_upper":(rhi+rt)**2,
            "dipole_norm_rate_range":[dmin,dmax],
            "tree_rate":tree_rate,
            "missing_other_amplitudes_norm_bound":None,
            "physical_full_threebody_BR":None}


def evaluate(ns:int=64,nz:int=24,tree_order:int=14)->dict:
    frozen=read_cards()  # SHA256-lock and four exact original cards
    if len(frozen)!=4:
        raise ValueError("four source cards required")
    sources=read_radiative(kappa=0)
    same=evaluate_tree(tree_order)
    mixed=evaluate_mixed_tree(tree_order)
    ml=frozen[0]["module2_input"]["lepton_masses_GeV"]
    if any(tuple(w["module2_input"]["lepton_masses_GeV"])!=tuple(ml) for w in frozen):
        raise ValueError("unexpected benchmark-dependent lepton masses")
    kernels={}
    for name,rad,a,b,group in CHANNELS:
        kernels[name]=kernel_range(ml[2],ml[a],ml[b],ns,nz)
    result={}
    for short,w in zip(CARD_IDS,frozen):
        rows={}
        for name,rad,a,b,group in CHANNELS:
            radsource=sources["cards"][short][rad]
            br=radsource["Zee_one_loop_plus_neutral_fermion_BZ_partial_radiative_BR"]
            eig=kernels[name]
            dmin=br*eig["conversion_eigen_min"]
            dmax=br*eig["conversion_eigen_max"]
            if group=="same":
                tree_rate=same["cards"][short]["channels"][name]["tree_h_H_A_BR"]
            else:
                tree_rate=mixed["cards"][short]["channels"][name]["neutral_h_H_A_exact_tree_BR"]
            rows[name]={
                "partial_source_radiative_BR":br,
                "dipole_only_exact_constant_K2_BR_min":dmin,
                "dipole_only_exact_constant_K2_BR_max":dmax,
                "neutral_h_H_A_tree_BR":tree_rate,
                "norm_only_conditional_tree_dipole_envelope":
                    phase_independent_tree_dipole_envelope(dmin,dmax,tree_rate),
                "physical_total_BR":None,
            }
        result[short]={"frozen_card":w["id"],
                       "scalar_sha256":w["scalar_sha256"],
                       "yukawa_sha256":w["yukawa_sha256"],
                       "channels":rows}
    return {
        "status":"EXACT_FINITE_MASS_CONSTANT_DIPOLE_AND_TREE_NORM_ENVELOPE_NOT_FULL_ZEE",
        "kernel":kernels,
        "approximation":"Constant on-shell K2 chirality coefficients analytically continued off shell, alpha(0) photon conversion; exact finite masses and direct/crossed photon amplitude squared. No off-shell K1, K2(q2), box or gauge-complete Zee two-loop.",
        "source_provenance":"Four SHA256-locked D12 input cards; native one-loop plus corrected neutral-fermion BZ radiative BR source gate; exact neutral h/H/A tree widths.",
        "phases":"Source-locked radiative BR only; complex combined native+BZ K2 not provided, so NO physical tree/dipole relative phase. Spectral bounds cover any complex dipole chirality decomposition and Cauchy covers tree/dipole interference only.",
        "all_other_full_model_amplitudes_unbounded":True,
        "quadrature":{"ns":ns,"nz":nz,"tree_order":tree_order},
        "cards":result,
        "physical_lfv":"UNKNOWN",
        "global_acceptance":None,
    }


def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--ns",type=int,default=64)
    p.add_argument("--nz",type=int,default=24)
    p.add_argument("--tree-order",type=int,default=14)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    data=evaluate(args.ns,args.nz,args.tree_order)
    for ch,kernel in data["kernel"].items():
        print("EXACT_DIPOLE_KERNEL",ch,
              f"{kernel['conversion_eigen_min']:.10e}",
              f"{kernel['conversion_eigen_max']:.10e}")
    for card,row in data["cards"].items():
        for ch,info in row["channels"].items():
            envelope=info["norm_only_conditional_tree_dipole_envelope"]
            print("PHASE_FREE_RESTRICTED_SCOPE",card,ch,
                  f"{envelope['subset_norm_lower']:.8e}",
                  f"{envelope['subset_norm_upper']:.8e}")
    if args.output:
        if args.output.exists():raise FileExistsError("Refusing to overwrite result")
        args.output.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("PHYSICAL_LFV UNKNOWN; NO COMPLETE TREE+PHOTON+Z+BOX+2LOOP AMPLITUDE")


if __name__=="__main__":
    main()
