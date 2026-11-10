#!/usr/bin/env python3
"""Exact neutral-scalar tree subsets for mixed-flavour tau three-lepton decays.

All four D7/F13 original witness inputs are SHA256-locked through
lfv_2hdm_transfer_2026.evaluate.read_cards(). This is a tree-only
calculation (including crossed scalar contractions); it does not include
a physical one-loop or full-model LFV prediction.
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
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_neutral_tree import (
    CARD_IDS, GAMMA_TAU_GEV
)

CHANNELS = (
    ("tau_to_e_minus_mu_minus_mu_plus", 0, 1),
    ("tau_to_mu_minus_e_minus_e_plus", 1, 0),
)


def evaluate(order: int = 14) -> dict:
    if type(order) is not int or order < 8 or order > 48:
        raise ValueError("quadrature order must be an integer in [8, 48]")
    cards = read_cards()
    if len(cards) != 4:
        raise ValueError("expected exactly four frozen input cards")
    output = {}
    for card_id, witness in zip(CARD_IDS, cards):
        p = witness["module2_input"]["scalar"]["record"]["physical"]
        ml = witness["module2_input"]["lepton_masses_GeV"]
        D = decode(witness["yukawas"]["D"])
        scalar_vertices = vertices(D, p, ml)
        channels = {}
        for channel, a, b in CHANNELS:
            exact_width = width(scalar_vertices, i=2, a=a, b=b, ml=ml,
                                order=order, contact=False)
            contact_width = width(scalar_vertices, i=2, a=a, b=b, ml=ml,
                                  order=order, contact=True)
            if not (math.isfinite(exact_width) and exact_width >= 0
                    and math.isfinite(contact_width) and contact_width >= 0):
                raise ArithmeticError("invalid mixed flavour tree width")
            if contact_width > 0 and abs(exact_width/contact_width - 1) >= 0.01:
                raise ArithmeticError("contact approximation not within one percent")
            channels[channel] = {
                "neutral_h_H_A_exact_tree_width_GeV": exact_width,
                "neutral_h_H_A_contact_width_GeV": contact_width,
                "neutral_h_H_A_exact_tree_BR": exact_width / GAMMA_TAU_GEV,
                "physical_threebody_BR": None,
                "coherent_full_LFV_amplitude": None,
            }
        output[card_id] = {
            "frozen_input_id": witness["id"],
            "scalar_sha256": witness["scalar_sha256"],
            "yukawa_sha256": witness["yukawa_sha256"],
            "channels": channels,
        }
    return {
        "status": "TAU_MIXED_FLAVOUR_NEUTRAL_TREE_SUBSET_ONLY",
        "parent": "tau_minus",
        "channels": [c[0] for c in CHANNELS],
        "scalar_source": "module3/core.py and module3/tree.py exact propagators, full 4-spin traces, crossed contractions",
        "scope_warning": "Tree-only h/H/A; no photon, Z, box, full-model two-loop LFV or full interference calculated.",
        "quadrature_order": order,
        "gamma_tau_GeV": GAMMA_TAU_GEV,
        "cards": output,
        "physical_lfv": "UNKNOWN",
        "global_acceptance": None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--order", type=int, default=14)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    result = evaluate(args.order)
    for card_id, card in result["cards"].items():
        for channel, x in card["channels"].items():
            print(card_id, channel, "TREE_ONLY_BR",
                  f"{x['neutral_h_H_A_exact_tree_BR']:.10e}")
    if args.output:
        if args.output.exists():
            raise FileExistsError("Refusing output overwrite")
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print("PHYSICAL_LFV UNKNOWN; NO FULL THREE-LEPTON AMPLITUDE")


if __name__ == "__main__":
    main()
