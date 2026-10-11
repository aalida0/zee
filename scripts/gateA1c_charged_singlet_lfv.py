#!/usr/bin/env python3
"""Gate A1C: CHARGED-SINGLET f-only lepton radiative-decay screen.

Implements Herrero-Garcia et al. JHEP 04 (2017) 130, arXiv:1701.05345,
Eqs. (3.12), (3.19), for charged-singlet f contributions ONLY.

Do not interpret output as the physical full Zee branching fraction.
Neutral scalar Y effects, other charged-scalar diagrams, two-loop Barr-Zee
amplitudes, and their interferences have NOT been computed.
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

G_F = 1.1663787e-5  # GeV^-2
ALPHA_EM = 1 / 137.035999084
# Belle and Belle II limits, 90% CL; check updated limits before publication.
CHANNELS = {
    "mu_to_e_gamma": dict(parent=1, daughter=0, norm_br=1.0, limit=1.5e-13),
    "tau_to_mu_gamma": dict(parent=2, daughter=1, norm_br=0.1739, limit=4.2e-8),
    "tau_to_e_gamma": dict(parent=2, daughter=0, norm_br=0.1782, limit=3.3e-8),
}

def singlet_propagator_sum(gamma=GAMMA, m1=M1, m2=M2):
    """sum |singlet mixing|²/m² in Florentino et al. convention."""
    return float(np.sin(gamma)**2/m1**2+np.cos(gamma)**2/m2**2)

def dipole_coefficient_f_only(f, parent, daughter, gamma=GAMMA,
                              m1=M1, m2=M2):
    """C_R^(f), GeV^-2.

    Eq. (3.19) of 1701.05345:
      -1/(16*pi²*12) sum_a [g3(a)²/m_a²] sum_k f_(daughter,k)* f_(parent,k)
    with g3=(-2*sin(gamma),-2*cos(gamma)).
    Not the complete C_R. C_L=0 for this contribution.
    """
    assert f.shape == (3, 3)
    ff = np.vdot(f[daughter, :], f[parent, :])
    return -ff*singlet_propagator_sum(gamma, m1, m2)/(48*np.pi**2)

def branching_fraction_f_only(f, parent, daughter, norm_br,
                              gamma=GAMMA, m1=M1, m2=M2):
    """Eq. (3.12); partial |C_R^(f)|² contribution, no interference."""
    C_R = dipole_coefficient_f_only(f, parent, daughter, gamma, m1, m2)
    factor = 48*np.pi**3*ALPHA_EM/G_F**2
    return float(norm_br*factor*abs(C_R)**2)

def report():
    M, _ = target_neutrino_matrix()
    f, _ = antisymmetric_f_with_null_condition(M)
    Y, rank, _ = solve_lepton_yukawa(f, M)
    rows = {}
    for name, ch in CHANNELS.items():
        p, d = ch["parent"], ch["daughter"]
        C = dipole_coefficient_f_only(f, p, d)
        br = branching_fraction_f_only(f, p, d, ch["norm_br"])
        rows[name] = {
            "f_only_C_R_GeV_minus2_real": float(C.real),
            "f_only_C_R_GeV_minus2_imag": float(C.imag),
            "f_only_noninterfering_BR": br,
            "experimental_limit_90CL": ch["limit"],
            "f_only_over_exp_limit": br/ch["limit"],
            "source": "arXiv:1701.05345 Eqs.(3.12),(3.19)"
        }
    return {
        "status": "PARTIAL_F_ONLY_LFV_SCREEN_NOT_FULL_BRANCHING_FRACTIONS",
        "seed": "Gate A1B general Zee NO, M1=300, M2=700, gamma=1.089",
        "masses_GeV": [M1, M2],
        "gamma_rad": GAMMA,
        "singlet_propagator_sum_GeV_minus2": singlet_propagator_sum(),
        "max_abs_f": float(np.max(abs(f))),
        "max_abs_Y_ell": float(np.max(abs(Y))),
        "linear_equation_rank": rank,
        "channels": rows,
        "not_checked": [
            "full one-loop neutral scalar dipoles (H and A, plus h misalignment)",
            "charged doublet Y and mixed Y-f contributions and cancellations",
            "all two-loop Barr-Zee effects including Type-II quark loops",
            "mu->3e and tau->3mu full tree+dipole+box contributions",
            "mu-e conversion, muonium oscillations and universality",
            "other scalar and flavour constraints and complete physical decay widths",
        ]
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    r = report()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(r, indent=2) + "\n")
        print("Wrote", args.output)
    for ch, val in r["channels"].items():
        print(f"{ch}: f-only BR={val['f_only_noninterfering_BR']:.6e} "
              f"(limit={val['experimental_limit_90CL']:.2e}, "
              f"f-only/limit={val['f_only_over_exp_limit']:.4e})")
    print("STATUS:", r["status"])
    assert all(val["f_only_noninterfering_BR"] < val["experimental_limit_90CL"]
               for val in r["channels"].values())
    # The assertion tests only the f-only contribution, not the full model.

if __name__ == "__main__":
    main()
