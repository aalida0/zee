#!/usr/bin/env python3
"""Gate A1E: isolated neutral-scalar ONE-LOOP dipoles, not full Zee LFV.

Compute h125/H/A + internal e/mu/tau with exact scalar-mass-ratio loop
functions in the expansion of vanishing external invariants.

Conventions:
- Chen arXiv:2508.18757 Eq.(4) for Y^ell (NOT an extra sqrt(2)).
- Florentino arXiv:2106.08332 Eqs.(21),(27)-(28) for alpha,beta.
- Lavoura hep-ph/0302221 Eqs.(26)-(30),(38)-(43), QF=-1, QB=0.
- Herrero-Garcia arXiv:1701.05345 Eqs.(3.12),(3.16)-(3.17) for
  C chirality and independent leading-log cross-check.

Not a complete one-loop Zee amplitude: physical charged-scalar Y parts
and neutral+charged interference remain outside this gate. All two-loop
Barr-Zee terms are also absent. Do NOT label as full LFV pass.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np
from gateA1b_hierarchical_no_seed import (
    ME, MMU, MTAU, target_neutrino_matrix,
    antisymmetric_f_with_null_condition, solve_lepton_yukawa,
)
from gateA1d_neutral_tree_lfv import scalar_couplings
from gateA1c_charged_singlet_lfv import CHANNELS, G_F, ALPHA_EM

LEPTON_MASSES = np.array([ME, MMU, MTAU], dtype=float)

def loop_A(t):
    """Lavoura 2003 Eq.(40), (c+3/2*d) for neutral loop, t=mF²/mS²."""
    t = float(t)
    if t <= 0 or abs(t-1) < 1e-5:
        raise ValueError("Require positive t away from t=1 (unstable direct form)")
    return ((t*t-5*t-2)/(12*(t-1)**3)
            + t*np.log(t)/(2*(t-1)**4))

def loop_B(t):
    """Lavoura 2003 Eq.(42), 2c for neutral loop, t=mF²/mS²."""
    t = float(t)
    if t <= 0 or abs(t-1) < 1e-5:
        raise ValueError("Require positive t away from t=1 (unstable direct form)")
    return ((t-3)/(2*(t-1)**2)
            + np.log(t)/(t-1)**3)

def neutral_dipole_for_scalar(C, scalar_mass, *, parent, daughter):
    """Return neutral-scalar CL,CR [GeV^-2] in Herrero Eq.(3.12).

    Lavoura B bar(F)[L_i PL + R_i PR] ell_i convention:
      L_i = C[F,i], R_i = C[i,F]^*
    (minus signs from Yukawa Lagrangian cancel between vertices).

    QF=-1,QB=0. Keep external lepton mass chirality flip prefactors,
    neglect external 4-momenta in scalar loop denominators.
    """
    C = np.asarray(C, complex)
    if C.shape != (3,3):
        raise ValueError("Expected 3x3 scalar Yukawa coupling matrix")
    if parent not in (1,2) or daughter not in (0,1) or parent<=daughter:
        raise ValueError("Allowed channels: mu->e, tau->e, tau->mu")
    mb = float(scalar_mass)
    if mb <= 0:
        raise ValueError("Scalar mass must be positive")
    mi,mj=LEPTON_MASSES[parent],LEPTON_MASSES[daughter]
    CL=0j
    CR=0j
    for k,mF in enumerate(LEPTON_MASSES):
        Li = C[k,parent]
        Ri = np.conj(C[parent,k])
        Lj = C[k,daughter]
        Rj = np.conj(C[daughter,k])
        lam = np.conj(Lj)*Li
        rho = np.conj(Rj)*Ri
        zeta = np.conj(Lj)*Ri
        upsilon = np.conj(Rj)*Li
        A=loop_A((mF/mb)**2)
        B=loop_B((mF/mb)**2)
        common=-1/(16*np.pi**2 * mb**2 * mi)
        CL+=common*(rho*mi*A+lam*mj*A+upsilon*mF*B)
        CR+=common*(lam*mi*A+rho*mj*A+zeta*mF*B)
    return CL,CR

def total_neutral_dipoles(Y, *, parent, daughter):
    """Coherently sum h125,H,A ONE-LOOP neutral-scalar contributions."""
    CL=0j
    CR=0j
    by_scalar={}
    for name,(C,mb) in zip(("h125","Hheavy","A"),scalar_couplings(Y)):
        cL,cR=neutral_dipole_for_scalar(C,mb,parent=parent,daughter=daughter)
        CL+=cL
        CR+=cR
        by_scalar[name]={"mass_GeV":mb,
                         "CL_GeV_minus2":[float(cL.real),float(cL.imag)],
                         "CR_GeV_minus2":[float(cR.real),float(cR.imag)]}
    return CL,CR,by_scalar

def partial_radiative_br(CL,CR,*,norm_br):
    """Herrero Eq.(3.12), isolated (CL,CR) only."""
    return float(norm_br * 48*np.pi**3*ALPHA_EM/G_F**2
                 * (abs(CL)**2+abs(CR)**2))

def leading_log_herrero_mu_to_e(Y,mS):
    """Dominant internal tau one-loop CL for sparse Y only.

    Herrero Eqs.(3.16)-(3.17), up to a common convention sign:
        Y[e,tau] * Y[tau,mu] * (m_tau/m_mu)
        * (log(mS²/m_tau²)-3/2)/(16*pi²*mS²)
    Used as an INDEPENDENT asymptotic comparison, not an observable.
    """
    return (Y[0,2]*Y[2,1]*(MTAU/MMU)
            * (np.log(mS*mS/(MTAU*MTAU))-1.5)/(16*np.pi**2*mS*mS))

def report():
    M,_=target_neutrino_matrix()
    f,_=antisymmetric_f_with_null_condition(M)
    Y,rank,_=solve_lepton_yukawa(f,M)
    res={}
    for ch,info in CHANNELS.items():
        CL,CR,components=total_neutral_dipoles(
            Y,parent=info["parent"],daughter=info["daughter"])
        br=partial_radiative_br(CL,CR,norm_br=info["norm_br"])
        res[ch]={
            "neutral_one_loop_only_BR_NOT_total":br,
            "90CL_experimental_limit":info["limit"],
            "neutral_one_loop_only_over_limit_NOT_a_full_pass":br/info["limit"],
            "CL_GeV_minus2":[float(CL.real),float(CL.imag)],
            "CR_GeV_minus2":[float(CR.real),float(CR.imag)],
            "individual_neutral_scalar_amplitudes":components,
        }
    return {
        "status":"NEUTRAL_ONE_LOOP_ONLY_NO_CHARGED_INTERFERENCE_NO_BARR_ZEE_NOT_FULL_LFV",
        "sources":[
            "Lavoura hep-ph/0302221 Eqs.(26)-(30),(38)-(43)",
            "Herrero-Garcia arXiv:1701.05345 Eqs.(3.12),(3.16)-(3.17)",
            "Chen arXiv:2508.18757 Eq.(4)",
            "Florentino arXiv:2106.08332 Eqs.(21),(27)-(28)",
        ],
        "seed":"Gate A1B hierarchical NO minimum-norm general Zee seed",
        "lepton_max_Y":float(np.max(abs(Y))),
        "neutrino_linear_rank":rank,
        "channels":res,
        "not_checked":[
            "charged scalar Y-dependent one-loop amplitudes and neutral interference",
            "complete one-loop mixed charged scalar chirality and neutrino effects",
            "two-loop Barr-Zee amplitudes (including quark and W loops)",
            "mu-to-e conversion, muonium, tree+dipole+box three-body decays",
            "all scalar and quark-flavour constraints, complete widths and collider rate",
        ],
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    r=report()
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(r,indent=2)+"\n")
        print("Wrote",a.output)
    for k,v in r["channels"].items():
        print(f"{k}: neutral-one-loop-only BR="
              f"{v['neutral_one_loop_only_BR_NOT_total']:.6e} "
              f"(limit={v['90CL_experimental_limit']:.2e})")
    print("STATUS:",r["status"])
    assert all(np.isfinite(x["neutral_one_loop_only_BR_NOT_total"])
               for x in r["channels"].values())
    assert "NOT_FULL" in r["status"]

if __name__=="__main__":
    main()
