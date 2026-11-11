#!/usr/bin/env python3
"""Independent *runtime* replay of a fully serialized Zee 2264 flavor card.

This is independent of the random target generator and 8D optimizer, but
uses the same Module2/Module4/D4 physical implementation. Numerical
portability is not an independent amplitude-level physics validation.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from module2.interface import evaluate as neutrino_evaluate
from module14.scan import digest, perturbativity
from module14.lfv import evaluate_family as partial_lfv
from module14.decays import DecayCalculation
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points

REFERENCE = Path(__file__).with_name("2264_fresh_8d_reference.json")
LIMIT = 1.5e-13


def run(output):
    if output.exists():
        raise FileExistsError("No overwrite of replay evidence")
    ref = json.loads(REFERENCE.read_text())
    inp = ref["optimized_input"]
    sha = digest(inp)
    if sha != ref["optimized_input_sha256"]:
        raise ValueError("Frozen optimized complete neutrino input SHA mismatch")
    point = next(p for p in source_points() if p["id"] == 2264)
    if inp["scalar"]["sha256"] != point["scalar_sha256"]:
        raise ValueError("Frozen original scalar identity mismatch")
    if point["gates"]["vacuum"]["assessment"] != "PASS":
        raise ValueError("Original vacuum certificate not verified")
    nu = neutrino_evaluate(inp)
    closure = float(nu["inverse"]["family_relative_residual"])
    y = perturbativity(nu)
    if closure >= 2e-9 or y["overall_max"] >= math.sqrt(4 * math.pi):
        raise ArithmeticError("Neutrino closure or perturbativity failed")
    family = {k: nu[k] for k in ("F", "D", "Ye", "Ye2", "Mnu")}
    family.update(input=inp, input_sha256=sha)
    l = partial_lfv(family, True)
    if l["status"] != "PARTIAL" or l["complete_lfv"]:
        raise ArithmeticError("Partial LFV status changed")
    widths = DecayCalculation(inp["scalar"]["record"], family).evaluate(family)
    if widths["status"] != "PASS":
        raise ArithmeticError("Charged-scalar D4 widths failed")
    values = {k: float(l["channels"][k]["partial_BR"])
              for k in ("mu_to_e_gamma", "tau_to_e_gamma", "tau_to_mu_gamma")}
    values["mu_to_3e_tree"] = float(l["mu_to_3e"]["tree_subset_BR"])
    values["cascade_product"] = float(widths["cascade_product"])
    old = ref["retained_reference"]
    # The optimized dipole is exceptionally small. Use an absolute tolerance,
    # not a fragile relative tolerance for its cancellation residual.
    if not (values["mu_to_e_gamma"] < 1e-17
            and values["mu_to_e_gamma"] < LIMIT):
        raise ArithmeticError("Retained mu-e amplitude no longer suppressed")
    for measured, reference in (
        ("tau_to_e_gamma", "tau_to_e_gamma_BR"),
        ("tau_to_mu_gamma", "tau_to_mu_gamma_BR"),
        ("cascade_product", "D4_cascade_BR_product"),
    ):
        if not math.isclose(values[measured], old[reference], rel_tol=1e-5, abs_tol=1e-28):
            raise ArithmeticError("Fresh input replay changed: " + measured)
    if values["mu_to_3e_tree"] > 1e-28:
        raise ArithmeticError("Tree mu3e unexpectedly increased")
    out = {
        "schema": "zee-2264-cross-runtime-serialized-optimized-family-replay-v1",
        "status": "SERIALIZED_CARD_REPLAY_NUMERICAL_PASS_NOT_PHYSICAL",
        "optimized_input_sha256": sha,
        "scalar_sha256": point["scalar_sha256"],
        "neutrino_relative_residual": closure,
        "max_abs_yukawa": y["overall_max"],
        "partial_rates": values,
        "mu_to_e_gamma_retained_Br_bound": LIMIT,
        "source_module4_output_sha256": l["module4_output_sha256"],
        "scope": "Same Module2+Module4+D4 code, independent from generator and optimization",
        "missing_contributions": l["missing_contributions"],
        "physical_LFV": "UNKNOWN", "physical_B": "UNKNOWN",
        "physical_Higgs": "UNKNOWN", "global_acceptance": None,
    }
    output.write_text(json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print("FROZEN_NEW_2264_INPUT_REPLAY_PASS", sha, "PARTIAL_BR",
          values["mu_to_e_gamma"], "CASCADE", values["cascade_product"],
          "CLOSURE", closure, "PHYSICAL_LFV UNKNOWN", flush=True)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    run(args.output)


if __name__ == "__main__":
    main()
