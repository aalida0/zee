#!/usr/bin/env python3
"""Gate A1F: charged-doublet Y^ell one-loop dipole and coherent scalar 1-loop screen.

Charged H+ Yukawa normalization:
  Chen arXiv:2508.18757 Eq.(4): L contains sqrt(2) * bar(ell_R) Y nu_L H-.
  Lavoura hep-ph/0302221 Eqs.(26)-(30),(38)-(43): internal neutrino
  Q_F=0, charged H+ Q_B=+1, t=m_nu^2/m_H+^2 -> 0.
  Eq.(41): barred external-mass loop function -> 1/12.

Charged-doublet component:
  C_L^(Y,charged) = (Y Y^dagger)[daughter,parent] / (96*pi^2)
                   * (cos(gamma)^2/mH1^2+sin(gamma)^2/mH2^2);
  C_R^(Y,charged) = 0 up to tiny neutrino-mass terms.
  Two charged-scalar signs square in pure-Y dipoles.
  Same convention as Gate A1E dipole C_{L,R} (GeV^-2).

Additionally, add neutral one-loop (A1E), charged singlet f-only (A1C),
and charged Y-only amplitudes coherently. This is ONE-LOOP-ONLY,
massless-internal-neutrino, scalar-sector dipole, not the total physical
BR: 2-loop Barr-Zee, possible UV/model-dependent matching and other
LFV channels are uncomputed. Quark Type-II and general lepton texture
require a consistent Lagrangian and full global constraints.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from gateA1b_hierarchical_no_seed import (
    M1, M2, GAMMA, target_neutrino_matrix,
    antisymmetric_f_with_null_condition, solve_lepton_yukawa
)
from gateA1c_charged_singlet_lfv import (
    CHANNELS, dipole_coefficient_f_only, branching_fraction_f_only
)
from gateA1e_neutral_one_loop_dipoles import (
    total_neutral_dipoles, partial_radiative_br
)

def charged_doublet_mass_weight(gamma=GAMMA,m1=M1,m2=M2):
    """Sum of squared charged-doublet fractions divided by mass squared."""
    if m1<=0 or m2<=0:
        raise ValueError("Charged scalar masses must be positive")
    return float(np.cos(gamma)**2/m1**2+np.sin(gamma)**2/m2**2)

def charged_doublet_y_dipole(Y,*,parent,daughter,
                              gamma=GAMMA,m1=M1,m2=M2):
    """Charged Y-only (CL,CR) in Herrero/Lavoura normalization, GeV^-2.

    Vertex H+ bar(nu_k) R_(ki) P_R ell_i with
    R_(ki) = sqrt(2)*doublet_fraction*(Y^ell)_(i,k)^*.
    rho=sum_k R_(kj)^* R_(ki)=2*(Y Ydag)_(j,i)*doublet_fraction².
    Lavoura eq.(41) tends to 1/12 at massless internal neutrino.
    Thus CL=rho/(192*pi²*mH+²); sum both H+ states.
    """
    Y=np.asarray(Y,complex)
    if Y.shape!=(3,3):
        raise ValueError("Y must be 3x3 charged-lepton x neutrino Yukawas")
    if (parent,daughter) not in ((1,0),(2,0),(2,1)):
        raise ValueError("Allowed parent/daughter: mu->e, tau->e, tau->mu")
    gram=Y@Y.conj().T
    CL=(gram[daughter,parent]/(96*np.pi**2)
        *charged_doublet_mass_weight(gamma,m1,m2))
    return complex(CL),0j

def complex_pair(z):
    return [float(z.real),float(z.imag)]

def report():
    M,_=target_neutrino_matrix()
    f,_=antisymmetric_f_with_null_condition(M)
    Y,rank,_=solve_lepton_yukawa(f,M)
    results={}
    for name,settings in CHANNELS.items():
        parent,daughter=settings["parent"],settings["daughter"]
        norm_br=settings["norm_br"]
        CLneutral,CRneutral,by_scalar=total_neutral_dipoles(
            Y,parent=parent,daughter=daughter)
        CLY,CRY=charged_doublet_y_dipole(
            Y,parent=parent,daughter=daughter)
        CRf=dipole_coefficient_f_only(f,parent,daughter)
        CLfull=CLneutral+CLY
        CRfull=CRneutral+CRY+CRf
        br_Y=partial_radiative_br(CLY,CRY,norm_br=norm_br)
        br_neutral=partial_radiative_br(
            CLneutral,CRneutral,norm_br=norm_br)
        br_f=branching_fraction_f_only(
            f,parent,daughter,norm_br=norm_br)
        br_1loop=partial_radiative_br(CLfull,CRfull,norm_br=norm_br)
        results[name]={
            "charged_doublet_Y_ONLY_squared_BR":br_Y,
            "neutral_ONELOOP_ONLY_squared_BR":br_neutral,
            "charged_singlet_f_ONLY_squared_BR":br_f,
            "coherent_scalar_ONELOOP_ONLY_BR_NOT_FULL_PHYSICAL":br_1loop,
            "exp_limit_90CL":settings["limit"],
            "coherent_one_loop_only_over_limit_NOT_FINAL_PASS":
                br_1loop/settings["limit"],
            "amplitudes_GeV_minus2":{
                "neutral_CL":complex_pair(CLneutral),
                "neutral_CR":complex_pair(CRneutral),
                "charged_doublet_Y_CL":complex_pair(CLY),
                "charged_singlet_f_CR":complex_pair(CRf),
                "coherent_one_loop_CL":complex_pair(CLfull),
                "coherent_one_loop_CR":complex_pair(CRfull),
            },
        }
    return {
        "status":"COHERENT_SCALAR_ONELOOP_SCREEN_NOT_FULL_LFV_NO_BARR_ZEE",
        "seed":"A1B hierarchical NO minimum-norm Yukawas",
        "masses_GeV":{"H1_charged":M1,"H2_charged":M2},
        "gamma_rad":GAMMA,
        "doublet_mass_weight_GeV_minus2":charged_doublet_mass_weight(),
        "linear_neutrino_rank":rank,
        "max_abs_Y":float(np.max(abs(Y))),
        "channels":results,
        "source_conventions":[
            "Chen arXiv:2508.18757 Eq.(4), sqrt2 charged Y convention",
            "Lavoura hep-ph/0302221 Eqs.(26)-(30),(38)-(43), charged Q_B=+1",
            "Herrero-Garcia arXiv:1701.05345 Eqs.(3.12),(3.19), singlet f part",
            "Florentino arXiv:2106.08332 Eqs.(22),(38), mixing fractions",
        ],
        "missing":[
            "two-loop Barr-Zee incl Type-II top and bottom loops",
            "independent validation of all coherent 1-loop chirality/phase conventions",
            "full LFV including mu->3e, mu-e conversion, muonium and universality",
            "full EW precision, b->s gamma, Higgs, vacuum and global constraints",
            "complete physical widths and collider signal rate",
        ],
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    r=report()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(r,indent=2)+"\n")
        print("Wrote",args.output)
    for name,vals in r["channels"].items():
        print(f"{name}: charged-Y-only BR="
              f"{vals['charged_doublet_Y_ONLY_squared_BR']:.6e}; "
              f"coherent-scalar-1loop-only BR="
              f"{vals['coherent_scalar_ONELOOP_ONLY_BR_NOT_FULL_PHYSICAL']:.6e} "
              f"(90CL limit={vals['exp_limit_90CL']:.2e})")
    print("STATUS:",r["status"])
    assert all(np.isfinite(v["coherent_scalar_ONELOOP_ONLY_BR_NOT_FULL_PHYSICAL"])
               for v in r["channels"].values())
    assert "NOT_FULL" in r["status"]

if __name__=="__main__":
    main()
