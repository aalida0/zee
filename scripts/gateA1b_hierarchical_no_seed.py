#!/usr/bin/env python3
"""Gate A1B: general-Zee neutrino seed with hierarchical normal ordering.

CONTRACT: Algebraic one-loop neutrino-mass closure ONLY; not an allowed point.
Uses the Higgs-basis lepton convention in Chen, arXiv:2508.18757, Eq. (5).
An antisymmetric 3x3 f has rank 2; solvability of
    M = kappa*(f Ml Y + (f Ml Y).T)
requires n.T @ M @ n = 0 for the null vector n of f.
For a requested Majorana mass matrix M, choose such a complex n analytically,
then solve the linear system for the minimum Euclidean-norm Yukawa Y.

The user-provided 300/700 GeV charged scalar spectrum with gamma=1.089
is NOT certified to satisfy EWPO, flavour, Higgs, stability, or other bounds.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

ME, MMU, MTAU = 0.00051099895, 0.1056583755, 1.77686  # GeV
ML = np.diag([ME, MMU, MTAU])
M1, M2, GAMMA = 300.0, 700.0, 1.089  # illustrative scalar-sector inputs
MZ = 91.1876
DM21_EV2, DM31_EV2 = 7.49e-5, 2.534e-3
SIN2_T12, SIN2_T13, SIN2_T23 = 0.307, 0.02195, 0.561
DELTA_DEG = 240.0
M_LIGHTEST_EV = 0.001  # deliberately hierarchical (NO)
F_MAX = 0.001
NULL_T = 0.25 + 0.1j  # reproducible design parameter; NOT data

def pmns():
    """PDG convention, zero Majorana phases, charged leptons diagonal."""
    s12, s13, s23 = np.sqrt([SIN2_T12, SIN2_T13, SIN2_T23])
    c12, c13, c23 = np.sqrt(1-np.array([SIN2_T12, SIN2_T13, SIN2_T23]))
    delta = np.deg2rad(DELTA_DEG)
    phase = np.exp(1j*delta)
    return np.array([
        [c12*c13, s12*c13, s13/phase],
        [-s12*c23-c12*s23*s13*phase, c12*c23-s12*s23*s13*phase, s23*c13],
        [s12*s23-c12*c23*s13*phase, -c12*s23-s12*c23*s13*phase, c23*c13]
    ], dtype=complex)

def target_neutrino_matrix():
    """Mnu = U* diag(m_i) U^dagger in eV, with normal ordering."""
    m1 = M_LIGHTEST_EV
    masses = np.array([m1, np.sqrt(m1**2+DM21_EV2),
                       np.sqrt(m1**2+DM31_EV2)])
    U = pmns()
    return U.conj() @ np.diag(masses) @ U.conj().T, masses

def scalar_kappa(m1=M1,m2=M2,gamma=GAMMA):
    """Chen Eq.(6): scalar-dependent Zee one-loop neutrino prefactor.

    The decoupling cases m1=m2 or gamma=0,pi/2 give kappa=0 and
    cannot produce the specified nonzero neutrino-mass target.
    """
    if not (np.isfinite(m1) and np.isfinite(m2) and np.isfinite(gamma) and
            m1>0 and m2>0 and 0<=gamma<=np.pi/2):
        raise ValueError("Invalid Zee neutrino scalar inputs")
    return float(np.sqrt(2)*np.sin(2*gamma) *
                 np.log(m1*m1/(m2*m2))/(16*np.pi**2))

def antisymmetric_f_with_null_condition(M):
    """Choose n=(1,x,t), enforce n.T M n=0 (NOT Hermitian n^dag M n)."""
    t = NULL_T
    coeff = [
        M[1,1],
        2*(M[0,1] + t*M[1,2]),
        M[0,0] + 2*t*M[0,2] + t*t*M[2,2],
    ]
    roots = np.roots(coeff)
    x = min(roots, key=abs)
    n = np.array([1., x, t], dtype=complex)
    f = np.array([
        [0, t, -x],
        [-t, 0, 1],
        [x, -1, 0]
    ], dtype=complex)
    f *= F_MAX/max(1., abs(t), abs(x))
    return f, n

def solve_lepton_yukawa(f, M, *, kappa=None):
    """Solve 6 complex independent symmetric entries for 9 complex Y.

    The minimum 2-norm solution is only a reproducibility choice:
    neutrino observables do not determine the full Yukawa matrix.
    """
    kappa = scalar_kappa() if kappa is None else float(kappa)
    if not np.isfinite(kappa) or abs(kappa)<1e-12:
        raise ValueError("Vanishing Zee loop prefactor forbids the required neutrino masses")
    upper = np.triu_indices(3)
    columns = []
    for i in range(3):
        for j in range(3):
            E = np.zeros((3,3), dtype=complex)
            E[i,j] = 1
            A = f @ ML @ E
            columns.append((kappa*(A+A.T)*1e9)[upper])
    A = np.array(columns).T
    Y_flat, _, rank, singular = np.linalg.lstsq(A, M[upper], rcond=1e-13)
    return Y_flat.reshape(3,3), int(rank), singular

def reconstruct_neutrino(f, Y, *, kappa=None):
    A = f @ ML @ Y
    prefactor=scalar_kappa() if kappa is None else float(kappa)
    return prefactor*(A+A.T)*1e9  # eV

def complex_json(a):
    return {"real": np.asarray(a).real.tolist(),
            "imag": np.asarray(a).imag.tolist()}

def report():
    target, masses = target_neutrino_matrix()
    f, n = antisymmetric_f_with_null_condition(target)
    Y, rank, singular = solve_lepton_yukawa(f, target)
    recovered = reconstruct_neutrino(f, Y)
    U = pmns()
    takagi = U.T @ recovered @ U
    max_err = float(np.max(abs(target-recovered)))
    return {
        "status": "ALGEBRAIC_NEUTRINO_SEED_ONLY_NOT_LFV_OR_GLOBAL_ALLOWED",
        "convention": "Chen 2508.18757 Eq.(5)-(6); Higgs basis, charged lepton diagonal",
        "mass_ordering": "normal",
        "neutrino_inputs": {
            "lightest_eV": M_LIGHTEST_EV,
            "dm21_eV2": DM21_EV2, "dm31_eV2": DM31_EV2,
            "sin2_t12": SIN2_T12, "sin2_t13": SIN2_T13,
            "sin2_t23": SIN2_T23,
            "delta_cp_deg": DELTA_DEG,
            "majorana_phases_rad": [0., 0.]
        },
        "sum_m_eV": float(sum(masses)),
        "masses_eV": masses.tolist(),
        "mass_bb_eV": float(abs(target[0,0])),
        "chosen_null_vector_n": complex_json(n),
        "null_condition_abs_eV": float(abs(n.T @ target @ n)),
        "f_times_n_max_abs": float(np.max(abs(f @ n))),
        "f": complex_json(f),
        "Y_ell": complex_json(Y),
        "max_abs_f": float(np.max(abs(f))),
        "max_abs_Y_ell": float(np.max(abs(Y))),
        "linear_system_rank": rank,
        "singular_values": singular.tolist(),
        "max_matrix_closure_abs_eV": max_err,
        "max_takagi_diagonal_closure_abs_eV":
            float(np.max(abs(takagi-np.diag(masses)))),
        "scalar_inputs": {
            "mH1_GeV": M1, "mH2_GeV": M2,
            "gamma_rad": GAMMA,
            "kappa_chen_convention": scalar_kappa(),
            "cascade_kinematically_open": bool(M2 > M1+MZ)
        },
        "cosmology": {
            "sum_m_below_0p12_eV": bool(sum(masses) < .12),
            "sum_m_below_0p0642_eV": bool(sum(masses) < .0642),
            "interpretation": "threshold-only diagnostic; cosmological bounds are dataset/model/prior dependent"
        },
        "not_checked": [
            "neutrino correlations; Majorana-phase variations and full likelihood",
            "all LFV, dipoles, Barr-Zee, mu-to-e conversion, leptonic universality",
            "scalar-sector constraints and complete widths",
            "quark Type-II flavour protection and RG consistency",
            "two charged Higgs b->s gamma, EWPO, HiggsTools, collider rate"
        ]
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    r = report()
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(r, indent=2)+"\n")
        print("Wrote", a.output)
    print("Neutrino mass sum (eV):", r["sum_m_eV"])
    print("Maximum |f|:", r["max_abs_f"])
    print("Maximum |Y_ell|:", r["max_abs_Y_ell"])
    print("Matrix closure (eV):", r["max_matrix_closure_abs_eV"])
    print("Linear rank:", r["linear_system_rank"])
    print("Cosmology threshold diagnostics:", r["cosmology"])
    assert r["linear_system_rank"] == 5
    assert r["max_matrix_closure_abs_eV"] < 1e-10

if __name__ == "__main__":
    main()
