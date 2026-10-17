#!/usr/bin/env python3
"""Independent physical-neutrino observables of the fixed family-Z2 IO witness.

Extracts the Dirac phase from BOTH rephasing-invariant sin(delta)
and cos(delta) using the PMNS matrix, and absolute-mass
observables using the Takagi phases of the Majorana mass matrix.

Do not mistake this for a fit against NuFIT v6.1:
- the input scalar spectrum is lepton-texture shape-only at tanbeta=15
  (the original P2 scalar potential is not revalidated there);
- the absolute neutrino scale was set to historical B2 |Delta m32²|,
  not optimized against the latest NuFIT IO mass-splitting likelihood;
- no LFV, cosmology, HiggsTools or flavor exclusions are implemented.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import numpy as np
from zee_section8_IO_first_octant_witness import WITNESS,evaluate_coordinates
from zee_section8_family_z2_neutrino_texture_pilot import (
    forward,mixing_observables,ML
)

STATUS="FAMILY_Z2_FIRST_OCTANT_PHYSICAL_NEUTRINO_OBSERVABLES_NO_LIKELIHOOD"


def calculate():
    w=evaluate_coordinates(WITNESS["coordinates"],
                           tanbeta=WITNESS["tanbeta"])
    pars=w["charged_texture_parameters"]
    point=forward(tanbeta=WITNESS["tanbeta"],**pars)
    obs=mixing_observables(point,"IO")
    order=[1,2,0]  # eigenvalues ascending -> masses (m1,m2,m3) for IO
    U=point["U_sorted_mass_columns"][:,order]
    norm=obs["f_e_mu_to_match_atm_abs"]
    mnu_eV=point["mnu_for_f1_GeV"]*norm*1e9
    masses=np.asarray(obs["masses_eV"],float)
    s12,s13,s23=[obs[key] for key in
                 ("sin2theta12","sin2theta13","sin2theta23")]
    denominator=(math.sqrt(s12*(1-s12)*s23*(1-s23)*s13)*
                 (1-s13))
    if denominator<=0:raise ValueError("Singular mixing phase extraction")
    cos_den=2*math.sqrt(s12*(1-s12)*s23*(1-s23)*s13)
    j=obs["J_CP"]
    sin_delta=j/denominator
    cos_delta=((abs(U[1,0])**2-s12*(1-s23)-
                (1-s12)*s23*s13)/cos_den)
    if not math.isclose(sin_delta**2+cos_delta**2,1,
                        rel_tol=1e-8,abs_tol=1e-8):
        raise ValueError("Jarlskog and modulus give inconsistent delta")
    delta_deg=float(math.degrees(math.atan2(
        sin_delta,cos_delta))%360.)
    # Hermitian eigenvectors have arbitrary phases. Fix these from
    # U.T Mnu U to get Takagi-diagonalized, positive neutrino masses.
    raw_diag=U.T@mnu_eV@U
    phases=np.exp(-.5j*np.angle(np.diag(raw_diag)))
    takagi=U@np.diag(phases)
    reconstructed=takagi.T@mnu_eV@takagi
    closure=float(np.max(abs(reconstructed-np.diag(masses))))
    if closure>1e-9:
        raise ValueError("Majorana Takagi factorization did not close")
    mbeta=float(math.sqrt(sum(abs(U[0,i])**2*masses[i]**2
                              for i in range(3))))
    mbb=float(abs(mnu_eV[0,0]))
    if not math.isclose(
        mbb,abs(sum(np.conj(takagi[0,i])**2*masses[i]
                    for i in range(3))),rel_tol=1e-9,abs_tol=1e-10):
        raise ValueError("Majorana m_bb contraction mismatch")
    f_mass=point["f_mass_basis"]*norm
    yh=point["Y_mass_basis_2022"]
    return {
        "status":STATUS,
        "witness_coordinates":WITNESS["coordinates"],
        "tanbeta":WITNESS["tanbeta"],
        "ordering":"IO",
        "oscillation_values":obs,
        "delta_CP_degrees_mod360":delta_deg,
        "sin_delta_CP":float(sin_delta),
        "cos_delta_CP":float(cos_delta),
        "effective_beta_decay_mass_mbeta_eV":mbeta,
        "light_exchange_0nubb_effective_mass_mbb_eV":mbb,
        "sum_mnu_eV":float(masses.sum()),
        "max_abs_f_mass_basis":float(np.max(abs(f_mass))),
        "max_abs_Y_2022_mass_basis":float(np.max(abs(yh))),
        "charged_lepton_mass_closure_GeV":float(
            point["charged_mass_closure_max_GeV"]),
        "Takagi_diagonalization_max_error_eV":closure,
        "source_2022_first_octant_2sigma_fit_done":False,
        "NuFIT_v6_1_IO_likelihood_done":False,
        "complete_LFV_done":False,
        "full_Zee_allowed":None,
        "convention_note":"Y is the 2022 mass-basis non-VEV Yukawa; Chen B2/B3 conversion and physical LFV couplings need independent checking",
        "neutrino_mass_scale_assumption":"Delta m_atm²=2.534e-3 eV², imported from old A1B diagnostic, not NuFIT6.1 IO",
        "cosmological_likelihood_done":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    row=calculate()
    if a.output.exists():p.error("Refusing to overwrite existing file")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(row,indent=2)+"\n")
    print("STATUS",STATUS)
    print("DELTA_CP_DEGREES",row["delta_CP_degrees_mod360"])
    print("M_BETA_EV",row["effective_beta_decay_mass_mbeta_eV"])
    print("M_BETA_BETA_LIGHT_EXCHANGE_EV",
          row["light_exchange_0nubb_effective_mass_mbb_eV"])
    print("MAX_ABS_F",row["max_abs_f_mass_basis"])
    print("MAX_ABS_Y_2022",row["max_abs_Y_2022_mass_basis"])
    print("TAKAGI_CLOSURE_EV",row["Takagi_diagonalization_max_error_eV"])
    print("NUFIT6P1_LIKELIHOOD_DONE False")
    print("COMPLETE_LFV_DONE False")
    print("FULL_ZEE_ALLOWED False")
    print("OUTPUT",a.output)

if __name__=="__main__":
    main()
