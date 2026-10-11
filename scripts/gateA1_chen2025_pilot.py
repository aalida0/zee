#!/usr/bin/env python3
"""Gate A1: limited numerical reproduction of Chen (2025), arXiv:2508.18757.

Reference: Eqs. (5), (6), (11) and Table I, normal ordering.
The source Yukawas are rounded. This pilot reconstructs a compatible
neutrino matrix, not the author's unrounded inputs or a full Zee model fit.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

ML = np.diag([0.00051099895, 0.1056583755, 1.77686])  # GeV
KAPPA_REF = 1.0e-5
M1, M2, GAMMA, MZ = 300.0, 700.0, 1.089, 91.1876
PARAM_NAMES = ("f12_1e-4_re", "f12_1e-4_im", "f13_1e-2",
               "f23_1e-4", "Y22", "Y31_1e-4_re", "Y31_1e-4_im",
               "Y32_1e-4", "Y33_1e-5")
PRINTED = np.array([3.20, -0.14, 0.24, 5.96, -0.118,
                    7.69, -1.64, 7.37, 7.98])
HALF_DIGIT = np.array([0.005] * 4 + [0.0005] + [0.005] * 4)

# NuFIT 6.0 NO, IC19 without SK-atm; INDIVIDUAL marginal 3 sigma ranges.
# They are neither a correlated likelihood nor a proof of current viability.
NUFIT = {
    "sin2_t12": (0.307, 0.275, 0.345),
    "sin2_t13": (0.02195, 0.02023, 0.02376),
    "sin2_t23": (0.561, 0.430, 0.596),
    "dm21_eV2": (7.49e-5, 6.92e-5, 8.05e-5),
    "dm31_eV2": (2.534e-3, 2.463e-3, 2.606e-3),
}

def matrices(p):
    a, b, c, d, e, g, h, j, k = np.asarray(p, dtype=float)
    f12, f13, f23 = (a+1j*b)*1e-4, c*1e-2, d*1e-4
    f = np.array([[0, f12, f13], [-f12, 0, f23],
                  [-f13, -f23, 0]], dtype=complex)
    Y = np.zeros((3, 3), dtype=complex)
    Y[1, 1] = e
    Y[2, 0], Y[2, 1], Y[2, 2] = (g+1j*h)*1e-4, j*1e-4, k*1e-5
    return f, Y

def neutrino_matrix(p, kappa=KAPPA_REF):
    """Chen's convention: Mnu = kappa [f Ml Y + (f Ml Y)^T], GeV."""
    f, Y = matrices(p)
    X = f @ ML @ Y
    return kappa * (X + X.T)

def spectrum(M):
    """Takagi singular values and |PMNS| from M.conj().T @ M."""
    eig, U = np.linalg.eigh(M.conj().T @ M)
    m = np.sqrt(np.maximum(eig, 0.)) * 1e9  # eV; normal ordering
    s13 = abs(U[0, 2])**2
    return {
        "masses_eV": m.tolist(),
        "sum_m_eV": float(m.sum()),
        "m_beta_eV": float(np.sqrt(np.sum(abs(U[0, :])**2*m**2))),
        "m_bb_eV": float(abs(M[0, 0])*1e9),
        "sin2_t12": float(abs(U[0, 1])**2/(1-s13)),
        "sin2_t13": float(s13),
        "sin2_t23": float(abs(U[1, 2])**2/(1-s13)),
        "dm21_eV2": float(m[1]**2-m[0]**2),
        "dm31_eV2": float(m[2]**2-m[0]**2),
    }

def rounding_compatible():
    keys = list(NUFIT)
    targets = np.array([NUFIT[k][0] for k in keys])
    # Conditioning weights only, NOT data uncertainties or chi-squared.
    scales = np.array([0.02, 0.0015, 0.045, 0.4e-5, 0.04e-3])
    def residual(p):
        o = spectrum(neutrino_matrix(p))
        return np.array([(o[k]-targets[i])/scales[i]
                         for i, k in enumerate(keys)])
    fit = least_squares(residual, PRINTED.copy(),
                        bounds=(PRINTED-0.999*HALF_DIGIT,
                                PRINTED+0.999*HALF_DIGIT),
                        xtol=1e-13, ftol=1e-13, gtol=1e-13,
                        max_nfev=600)
    return fit.x

def scalar_kappa(m1=M1, m2=M2, gamma=GAMMA):
    """Chen Eq. (6), including its sqrt(2) convention and signed log."""
    return np.sqrt(2)*np.sin(2*gamma)*np.log(m1**2/m2**2)/(16*np.pi**2)

def report():
    fit = rounding_compatible()
    source = spectrum(neutrino_matrix(PRINTED))
    reconstructed = spectrum(neutrino_matrix(fit))
    marginals = {
        k: bool(NUFIT[k][1] <= reconstructed[k] <= NUFIT[k][2])
        for k in NUFIT
    }
    kp = float(scalar_kappa())
    f, Y = matrices(fit)
    new_f = f*KAPPA_REF/kp
    X = new_f @ ML @ Y
    max_error_eV = float(np.max(abs(kp*(X+X.T)-neutrino_matrix(fit)))*1e9)
    return {
        "source": "Chen arXiv:2508.18757 Eq.(5),(6),(11) Table I NO",
        "status": "NEUTRINO_AND_ROUNDING_DIAGNOSTIC_ONLY_NOT_FULL_ZEE_FIT",
        "printed_parameters": dict(zip(PARAM_NAMES, PRINTED.tolist())),
        "rounding_compatible_parameters": dict(zip(PARAM_NAMES, fit.tolist())),
        "source_rounded_observables": source,
        "reconstructed_observables": reconstructed,
        "individual_nufit60_3sigma": marginals,
        "all_five_individual_ranges_pass": all(marginals.values()),
        "scalar_candidate": {
            "mH1_GeV": M1, "mH2_GeV": M2, "gamma_rad": GAMMA,
            "kinematically_open": M2 > M1+MZ,
            "sin_2gamma": float(np.sin(2*GAMMA)),
            "chen_kappa_at_300_700_gamma": kp,
            "abs_kappa_ratio_to_reference": abs(kp/KAPPA_REF),
            "rescale_f_keep_Y_fixed": KAPPA_REF/kp,
            "matrix_closure_max_abs_eV": max_error_eV,
            "Y22_only_mu_nu_width_H1_GeV": float(M1*abs(fit[4])**2*np.cos(GAMMA)**2/(8*np.pi)),
            "Y22_only_mu_nu_width_H2_GeV": float(M2*abs(fit[4])**2*np.sin(GAMMA)**2/(8*np.pi)),
        },
        "not_checked": [
            "full LFV including Barr-Zee contributions",
            "Type-II quark sector and flavour-protection mechanism",
            "S,T,U; Higgs and direct searches; B to Xs gamma",
            "full charged scalar widths and cascade collider rate",
            "cosmology and correlated neutrino likelihood",
            "published unrounded Chen Yukawa inputs"
        ],
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = report()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2)+"\n")
    print("Rounded source sum(mnu):", result["source_rounded_observables"]["sum_m_eV"], "eV")
    print("Reconstructed sum(mnu):", result["reconstructed_observables"]["sum_m_eV"], "eV")
    print("Individual marginal NuFIT checks:", result["individual_nufit60_3sigma"])
    print("Cascade kinematically open:", result["scalar_candidate"]["kinematically_open"])
    print("Required f rescaling:", result["scalar_candidate"]["rescale_f_keep_Y_fixed"])
    print("Matrix rescaling closure (eV):", result["scalar_candidate"]["matrix_closure_max_abs_eV"])
    assert result["all_five_individual_ranges_pass"]
    assert result["scalar_candidate"]["matrix_closure_max_abs_eV"] < 1e-11

if __name__ == "__main__":
    main()
