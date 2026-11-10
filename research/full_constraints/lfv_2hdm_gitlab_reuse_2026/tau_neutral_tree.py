#!/usr/bin/env python3
"""Exact three-body phase-space integration of neutral Zee h/H/A tree exchange.

This is a standalone tree *subset*. Interference with photons, boxes,
electroweak penguins and missing Zee two-loop amplitudes is not calculated.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from module2.interface import decode
from module3.core import vertices
from module3.tree import width
from research.full_constraints.lfv_2hdm_transfer_2026.evaluate import read_cards
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_radiative_threebody_diagnostic import evaluate as dipole_evaluate

HBAR_GEV_S = 6.582119569e-25
TAU_LIFETIME_S = 290.3e-15
GAMMA_TAU_GEV = HBAR_GEV_S / TAU_LIFETIME_S
CARD_IDS = ("D7_NO", "D7_IO", "F13_NO", "F13_IO")
CHANNELS = (("tauegamma", "tau_to_3e", 0), ("taumugamma", "tau_to_3mu", 1))


def evaluate_tree(order: int = 14) -> dict:
    """Tree-only h,H,A tau->3e,3mu: exact masses, antisymmetrized spin sums."""
    if type(order) is not int or order < 8 or order > 48:
        raise ValueError("quadrature order must be an integer in [8,48]")
    cards = read_cards()  # Checks original D12 SHA256 and exact low_joint IDs.
    dipole = dipole_evaluate(kappa=0)
    if len(cards) != 4 or len(dipole["cards"]) != 4:
        raise RuntimeError("four frozen source cards required")
    out = {}
    for short, w in zip(CARD_IDS, cards):
        scalar = w["module2_input"]["scalar"]["record"]["physical"]
        ml = w["module2_input"]["lepton_masses_GeV"]
        D = decode(w["yukawas"]["D"])
        vc = vertices(D, scalar, ml)
        channels = {}
        for radiator, final, daughter in CHANNELS:
            exact = width(vc, 2, daughter, daughter, ml, order=order, contact=False)
            contact = width(vc, 2, daughter, daughter, ml, order=order, contact=True)
            if any(not math.isfinite(float(x)) or x < 0 for x in (exact, contact)):
                raise ArithmeticError("invalid tree width")
            if contact > 0 and abs(exact/contact - 1) > 0.01:
                raise ArithmeticError("tree contact approximation unexpectedly disagrees with exact propagators")
            dipole_br = dipole["cards"][short][radiator]["partial_coherent_neutral_BZ_dipole_only_threebody_BR"]
            tree_br = exact / GAMMA_TAU_GEV
            channels[final] = {
                "tree_h_H_A_width_GeV": exact,
                "tree_h_H_A_contact_width_GeV": contact,
                "tree_h_H_A_BR": tree_br,
                "partial_zee_dipole_only_BR": dipole_br,
                "tree_over_partial_dipole_subset_ratio": tree_br / dipole_br,
                "coherent_total_BR": None,
                "physical_threebody_BR": None,
            }
        out[short] = {
            "frozen_benchmark_id": w["id"],
            "scalar_sha256": w["scalar_sha256"],
            "yukawa_sha256": w["yukawa_sha256"],
            "channels": channels,
        }
    return {
        "status": "NEUTRAL_SCALAR_EXACT_TREE_TAU_THREEBODY_SUBSET_ONLY",
        "source": "SHA256-locked validation/module12/d12_benchmarks.json; module3.core.vertices and module3.tree.width",
        "tree_scope": "coherent h,H,A propagators with exact final masses, crossed identical-fermion amplitude, full spin sum and finite three-body integration",
        "dipole_scope": "independently computed leading-log dipole-only virtual photon using native one-loop plus neutral-fermion Barr-Zee partial radiative rate",
        "interference": "NOT CALCULATED; tree, dipole and all other groups must NOT be added as physical total rates",
        "gamma_tau_GeV": GAMMA_TAU_GEV,
        "quadrature_order": order,
        "cards": out,
        "physical_lfv": "UNKNOWN",
        "global_acceptance": None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--order", type=int, default=14)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    result = evaluate_tree(args.order)
    for card, v in result["cards"].items():
        for ch, x in v["channels"].items():
            print(card, ch, "BR_tree", f"{x['tree_h_H_A_BR']:.8e}",
                  "BR_dipole_partial", f"{x['partial_zee_dipole_only_BR']:.8e}",
                  "tree/dipole_partial", f"{x['tree_over_partial_dipole_subset_ratio']:.8e}")
    if args.output:
        if args.output.exists():
            raise FileExistsError(f"Refusing to overwrite {args.output}")
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print("PHYSICAL_LFV UNKNOWN; no coherent tau threebody rate or model exclusion")


if __name__ == "__main__":
    main()
