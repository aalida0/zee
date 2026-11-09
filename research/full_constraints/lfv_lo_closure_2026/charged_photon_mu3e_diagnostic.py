#!/usr/bin/env python3
"""Charged H1/H2 photon-only diagnostic for mu -> 3e (NOT a full LFV rate).

Toma & Vicente, JHEP01(2014)160 Eq.(22): retain only A_ND and A_D.
Charged-scalar coefficients are imported from CHARGED_RESULT.json, using
the massless-active-neutrino Hundi EPJC85(2025)805 Eq.(23) transfer.
The relative sign to neutral/Z/box contributions is NOT established.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "research/full_constraints/lfv_2hdm_photon_2026/CHARGED_RESULT.json"
GF_GEV_NEG2 = 1.1663787e-5
ALPHA_ZERO = 1 / 137.035999084
MUON_MASS_GEV = 0.1056583755
ELECTRON_MASS_GEV = 0.00051099895000


def as_complex(pair):
    if not isinstance(pair, list) or len(pair) != 2:
        raise ValueError("expected real/imaginary pair")
    z = complex(float(pair[0]), float(pair[1]))
    if not math.isfinite(z.real) or not math.isfinite(z.imag):
        raise ValueError("nonfinite input Wilson")
    return z


def photon_only_rate(a_nd, a_d, *, alpha=ALPHA_ZERO, gf=GF_GEV_NEG2,
                     m_mu=MUON_MASS_GEV, m_e=ELECTRON_MASS_GEV):
    """Published Eq.(22) with B=F_Z=0, single external chirality.

    [A_ND]=[A_D]=GeV^-2. Br(mu -> e nu nu) approximated as unity.
    The final electron mass is retained only in the collinear log.
    """
    if not (0 < m_e < m_mu and 0 < alpha < 1 and gf > 0):
        raise ValueError("unphysical rate inputs")
    log_factor = 16 / 3 * math.log(m_mu / m_e) - 22 / 3
    # Eq.(22) interference: (-2 A_ND A_D* + h.c.)
    bracket = abs(a_nd)**2 + log_factor * abs(a_d)**2 - 4 * (a_nd * a_d.conjugate()).real
    invariant = abs(a_nd - 2 * a_d)**2 + (log_factor - 4) * abs(a_d)**2
    if not math.isclose(bracket, invariant, rel_tol=1e-12, abs_tol=1e-60):
        raise ArithmeticError("photon-only rate algebra failed")
    return 3 * (4 * math.pi)**2 * alpha**2 / (8 * gf**2) * bracket


EXPECTED_IDS = [
    "d7_NO_neutral_near_heavy_07/NO/texture_0.0001",
    "d7_NO_neutral_near_heavy_07/IO/texture_0.0001",
    "F13_heavy_0001330/NO/texture_0.001",
    "F13_heavy_0001330/IO/texture_0.001",
]


def calculate(source_file=SOURCE):
    source_file = Path(source_file)
    data_bytes = source_file.read_bytes()
    data = json.loads(data_bytes)
    if data.get("status") != "CHARGED_MASSLESS_NEUTRINO_PHOTON_SOURCE_TRANSFER":
        raise ValueError("wrong charged source input")
    if data.get("physical_lfv") != "UNKNOWN" or data.get("full_common_K1") is not None:
        raise ValueError("invalid upstream incompleteness contract")
    cards = data.get("cards", [])
    if [x["id"] for x in cards] != EXPECTED_IDS:
        raise ValueError("four-card witness selection mismatch")
    outputs = []
    for card in cards:
        # A simultaneous sign flip of A_ND and A_D has no effect on this
        # photon-only quadratic diagnostic; no cross-source signed bridge
        # to the other Zee amplitudes is claimed.
        f_nd, f_d = -as_complex(card["A1L_F"]), -as_complex(card["A2R_F"])
        d_nd, d_d = -as_complex(card["A1R_D"]), -as_complex(card["A2L_D"])
        for nd, dip in ((f_nd, f_d), (d_nd, d_d)):
            if abs(nd - 2 / 3 * dip) > 1e-10 * max(abs(nd), abs(dip), 1e-90):
                raise ValueError("unexpected source A_ND/A_D relation")
        f_br, d_br = photon_only_rate(f_nd, f_d), photon_only_rate(d_nd, d_d)
        outputs.append({
            "id": card["id"],
            "charged_F_photon_only_BR": f_br,
            "charged_D_photon_only_BR": d_br,
            "charged_total_photon_only_BR": f_br + d_br,
            "F_D_cross_chirality_interference": "neglected O(m_e/m_mu)",
            "status": "PARTIAL_DIAGNOSTIC_NOT_PHYSICAL_RATE",
            "physical_mu3e_BR": None,
            "LFV_pass_fail": "UNKNOWN",
        })
    return {
        "status": "PARTIAL_DIAGNOSTIC_NOT_PHYSICAL_RATE",
        "physical_lfv": "UNKNOWN",
        "global_acceptance": None,
        "physical_mu3e_BR": None,
        "source_charged_sha256": hashlib.sha256(data_bytes).hexdigest(),
        "source_eq": "Toma-Vicente JHEP01(2014)160 Eq.(22), photon-only A_ND+A_D",
        "topology_source": "Hundi EPJC85(2025)805 Eq.(23), charged massless nu",
        "m_mu_GeV": MUON_MASS_GEV,
        "m_e_GeV": ELECTRON_MASS_GEV,
        "alpha_em_q2_0": ALPHA_ZERO,
        "gf_GeV_minus2": GF_GEV_NEG2,
        "approximation": "m_nu=0; m_e neglected except log; F/D external chiralities summed incoherently",
        "not_included": [
            "full neutral photon form factors",
            "Z penguins, scalar/tree and all D/F boxes",
            "interference with other Zee amplitudes",
            "complete off-shell signed basis and uncertainties",
        ],
        "cards": outputs,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=HERE / "CHARGED_PHOTON_MU3E_PARTIAL.json")
    args = parser.parse_args()
    result = calculate(args.source)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    for card in result["cards"]:
        print(card["id"], f"charged photon-only BR(mu->3e) = {card['charged_total_photon_only_BR']:.8e}")
    print("PHYSICAL_LFV=UNKNOWN (NOT a complete rate)")


if __name__ == "__main__":
    main()
