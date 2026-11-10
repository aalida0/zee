#!/usr/bin/env python3
"""Leading-log dipole tau->3l diagnostics from frozen Zee source gates.

These are *dipole-only* terms. They are not physical total three-body
branching fractions and do not establish a bound on Zee two-loop remainders.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = HERE.parent / "lfv_lo_closure_2026" / "NATIVE_ZEE_TAU_RADIATIVE_LFV_GATE_2026-11-10.json"
ALPHA_ZERO = 1 / 137.035999084
M_TAU_GEV = 1.77686
M_E_GEV = 0.00051099895
M_MU_GEV = 0.1056583755
LIMIT_90CL = {"tauegamma": 5.6e-8, "taumugamma": 4.2e-8}
EXPECTED_IDS = ("D7_NO", "D7_IO", "F13_NO", "F13_IO")
CORRECTED_AUTHOR_SHA256 = "9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193"


def dipole_threebody_ratio(parent_mass: float, daughter_mass: float, alpha: float = ALPHA_ZERO) -> float:
    """LO leading-log BR(li->3lj)_dipole/BR(li->lj gamma).

    Formula alpha/(3 pi) [log(m_i^2/m_j^2) - 11/4]; neglects O(m_j/m_i)
    terms, other off-shell photon operators, and non-photonic amplitudes.
    Appropriate only when the parent is much heavier than the daughter.
    """
    if any(not math.isfinite(x) or x <= 0 for x in (parent_mass, daughter_mass, alpha)):
        raise ValueError("masses and alpha must be finite and positive")
    if daughter_mass >= parent_mass / 10:
        raise ValueError("leading-log approximation requires m_daughter < m_parent/10")
    return alpha / (3 * math.pi) * (2 * math.log(parent_mass / daughter_mass) - 11 / 4)


def evaluate(kappa: float = 40.0, input_gate: Path = GATE) -> dict:
    """Kappa is an assumed (never derived) amplitude-norm remainder ratio."""
    if not math.isfinite(kappa) or kappa < 0:
        raise ValueError("kappa must be finite and nonnegative")
    gate = json.loads(Path(input_gate).read_text(encoding="utf-8"))
    if (gate.get("physical_lfv") != "UNKNOWN"
            or gate.get("global_acceptance") is not None
            or gate.get("authors_uploaded_thdm_sha256") != CORRECTED_AUTHOR_SHA256):
        raise ValueError("Unexpected source gate provenance or physical status")
    rows = gate.get("cards")
    if not isinstance(rows, list) or tuple(r.get("card") for r in rows) != EXPECTED_IDS:
        raise ValueError("Expected exactly four frozen D7/F13 NO/IO cards")
    r_3e = dipole_threebody_ratio(M_TAU_GEV, M_E_GEV)
    r_3mu = dipole_threebody_ratio(M_TAU_GEV, M_MU_GEV)
    results = {}
    for row in rows:
        if row.get("full_Zee_two_loop_qualified") is not False or row.get("physical_tau_LFV_acceptance") != "UNKNOWN":
            raise ValueError("Unexpected completeness assertion in frozen gate")
        card = row["card"]
        result = {}
        for label, daughter, ratio in (("tauegamma", "3e", r_3e), ("taumugamma", "3mu", r_3mu)):
            suffix = "tauegamma" if label == "tauegamma" else "taumugamma"
            one = row["native_one_loop_BR_" + suffix]
            partial = row["partial_Zee_one_loop_plus_corrected_neutral_fermion_BZ_BR_" + suffix]
            limit = LIMIT_90CL[label]
            if any(not isinstance(x, (int, float)) or not math.isfinite(x) or x <= 0
                   for x in (one, partial, limit)):
                raise ValueError("Nonpositive or nonfinite rate/limit")
            kappa_max = math.sqrt(limit / partial) - 1
            result[label] = {
                "native_Zee_one_loop_radiative_BR": one,
                "Zee_one_loop_plus_neutral_fermion_BZ_partial_radiative_BR": partial,
                "dipole_only_threebody_final_state": "tau_to_" + daughter,
                "dipole_only_threebody_over_radiative_factor": ratio,
                "native_one_loop_dipole_only_threebody_BR": one * ratio,
                "partial_coherent_neutral_BZ_dipole_only_threebody_BR": partial * ratio,
                "radiative_experimental_90CL_limit": limit,
                "max_assumed_missing_amplitude_norm_over_partial_norm": kappa_max,
                "radiative_worst_case_given_assumption": (1 + kappa) ** 2 * partial,
                "conditional_radiative_sufficient_pass": (1 + kappa) ** 2 * partial < limit,
                "physical_radiative_BR": None,
                "physical_threebody_BR": None,
            }
        results[card] = result
    return {
        "status": "TAU_DIPOLE_THREEBODY_LEADING_LOG_ONLY_PHYSICAL_LFV_UNKNOWN",
        "source": "NATIVE_ZEE_TAU_RADIATIVE_LFV_GATE_2026-11-10.json (corrected author source-locked)",
        "threebody_approximation": "Dipole only, alpha(0) leading log; O(m_l/m_tau), off-shell K1, Z, tree and box omitted",
        "remainder_assumption": "For each radiative channel ||A_missing|| <= kappa ||A_partial|| in a common normalized amplitude basis; this has NOT been derived.",
        "assumed_kappa": kappa,
        "ratios": {"tau3e_over_tauegamma_dipole": r_3e, "tau3mu_over_taumugamma_dipole": r_3mu},
        "all_conditional_radiative_sufficient_pass": all(
            v["conditional_radiative_sufficient_pass"] for x in results.values() for v in x.values()
        ),
        "cards": results,
        "physical_lfv": "UNKNOWN",
        "global_acceptance": None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kappa", type=float, default=40.0)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    result = evaluate(args.kappa)
    if args.output:
        if args.output.exists():
            raise FileExistsError(f"Refusing to overwrite {args.output}")
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for card, channels in result["cards"].items():
        print(card, "BR(tau->3e)_dipole_partial", f"{channels['tauegamma']['partial_coherent_neutral_BZ_dipole_only_threebody_BR']:.5e}",
              "BR(tau->3mu)_dipole_partial", f"{channels['taumugamma']['partial_coherent_neutral_BZ_dipole_only_threebody_BR']:.5e}",
              "kappa_max_tau_mu_gamma", f"{channels['taumugamma']['max_assumed_missing_amplitude_norm_over_partial_norm']:.3f}")
    print("PHYSICAL_LFV UNKNOWN: neither full tau->3l nor full Zee two-loop calculated")


if __name__ == "__main__":
    main()
