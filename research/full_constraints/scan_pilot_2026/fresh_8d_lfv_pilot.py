#!/usr/bin/env python3
"""Fresh-source, eight-real-dimensional Zee neutrino-preserving LFV pilot.

IMPORTANT: A newly generated neutrino-family card is deliberately *not* the
original historical family: its source input is fully serialized and pinned
within this output. The original certified scalar is reused unchanged.
Optimizes only the retained Module4 dipole, never claims physical LFV pass.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

from module14.scan import digest, neutrino_input, perturbativity
from module14.lfv import evaluate_family as evaluate_partial_lfv
from module2.interface import evaluate as neutrino_evaluate
from module14.decays import DecayCalculation
from research.full_constraints.scan_pilot_2026.historical_certified_texture import source_points

SEED = 20261111
COEFFICIENT_UNIT = 1e-4
MEGII_BOUND = 1.5e-13
START_ETAS = (0.0, 0.0003254613882564927)
TRUST_BOX = 0.5
RADII = (0.001, 0.01, 0.03)


def fresh_family():
    p = next(x for x in source_points() if x["id"] == 2264)
    if p["gates"]["vacuum"]["assessment"] != "PASS":
        raise ArithmeticError("Original complete scalar has no vacuum certificate")
    if p["bsg_nominal_classification"] != "APPROX_COMPATIBLE":
        raise ArithmeticError("Original B reference changed")
    row = {"id": p["id"], "scalar": p["input_card"], "scalar_sha256": p["scalar_sha256"]}
    seed, spec, inp = neutrino_input(row, SEED, "IO", 1)
    if seed != digest(["d14-neutrino-v1", SEED, p["id"], "IO", 1]):
        raise ArithmeticError("New deterministic family seed mismatch")
    # This input is a new physics card, not a recreation of the original
    # historical D14 neutrino family. Save all of it verbatim.
    return p, seed, spec, inp


def starting_vector(inp, eta):
    coef = inp["homogeneous_coefficients"]
    return np.asarray(
        [eta * v / COEFFICIENT_UNIT for v in coef["real"]]
        + [eta * v / COEFFICIENT_UNIT for v in coef["imag"]], dtype=float
    )


def input_at(base, x):
    x = np.asarray(x, dtype=float)
    if x.shape != (8,) or not np.all(np.isfinite(x)) or np.max(abs(x)) > TRUST_BOX + 1e-12:
        raise ValueError("Out of declared finite eight-real-dimensional trust box")
    inp = copy.deepcopy(base)
    inp["homogeneous_coefficients"] = {
        "real": (x[:4] * COEFFICIENT_UNIT).tolist(),
        "imag": (x[4:] * COEFFICIENT_UNIT).tolist(),
    }
    return inp


def evaluate(base, x, with_d4=False):
    inp = input_at(base, x)
    nu = neutrino_evaluate(inp)
    closure = float(nu["inverse"]["family_relative_residual"])
    if not math.isfinite(closure) or closure >= 2e-9:
        raise ArithmeticError("Broken neutrino target closure")
    m = perturbativity(nu)
    if not math.isfinite(m["overall_max"]) or m["overall_max"] >= math.sqrt(4 * math.pi):
        raise ArithmeticError("Nonperturbative Yukawa family")
    fam = {k: nu[k] for k in ("F", "D", "Ye", "Ye2", "Mnu")}
    fam.update(input=inp, input_sha256=digest(inp))
    l = evaluate_partial_lfv(fam, with_d4)
    if l["status"] != "PARTIAL" or l["complete_lfv"]:
        raise ArithmeticError("Invalid promotion of incomplete Zee LFV")
    c = l["channels"]["mu_to_e_gamma"]
    br = float(c["partial_BR"])
    if br < 0 or not math.isfinite(br):
        raise ArithmeticError("Invalid partial mu-e branching ratio")
    left, right = complex(**c["C_L"]), complex(**c["C_R"])
    values = np.asarray((left.real, left.imag, right.real, right.imag), float)
    result = {
        "input": inp, "input_sha256": digest(inp), "target_sha256": digest(inp["target_eV"]),
        "partial_BR": br, "dipole_CL": c["C_L"], "dipole_CR": c["C_R"],
        "amp_components": values, "neutrino_relative_closure": closure,
        "max_abs_yukawa": m["overall_max"], "physical_LFV": "UNKNOWN",
        "global_acceptance": None,
    }
    if with_d4:
        decay = DecayCalculation(inp["scalar"]["record"], fam).evaluate(fam)
        if decay["status"] != "PASS":
            raise ArithmeticError("Full D4 two-body charged decay table missing")
        result.update({
            "cascade_tree_BR_product": decay["cascade_product"],
            "H2_to_H1Z_tree_BR": decay["mothers"]["H2"]["br_H1_Z"],
            "H1_to_tb_tree_BR": decay["mothers"]["H1"]["br_tb"],
            "partial_mu3e_tree_BR": l["mu_to_3e"]["tree_subset_BR"],
            "other_partial_radiative_BR": {
                k: v["partial_BR"] for k, v in l["channels"].items()
                if k != "mu_to_e_gamma"
            },
        })
    return result


def optimize_family(base, max_nfev=32):
    cache = {}
    def get(x):
        key = tuple(float(v) for v in x)
        if key not in cache:
            cache[key] = evaluate(base, x)
        return cache[key]
    starts = [starting_vector(base, eta) for eta in START_ETAS]
    for v in starts:
        if np.max(abs(v)) >= TRUST_BOX:
            raise ArithmeticError("Declared start does not fit trust box")
    reference = get(starts[0])
    amplitude = np.linalg.norm(reference["amp_components"])
    if amplitude <= 0 or reference["partial_BR"] <= 0:
        raise ArithmeticError("Reference dipole normalization unavailable")
    amp_limit = amplitude * math.sqrt(MEGII_BOUND / reference["partial_BR"])
    best = None
    diagnostics = []
    for start_eta, x0 in zip(START_ETAS, starts):
        def residual(x):
            out = get(x)
            return np.r_[out["amp_components"] / amp_limit, 0.05 * (x - x0)]
        # Fixed absolute steps avoid scipy's tiny relative step close to x=0.
        def jac(x):
            rows = []
            h = 0.001
            for j in range(8):
                delta = np.zeros(8)
                delta[j] = h
                a = get(np.clip(x + delta, -TRUST_BOX, TRUST_BOX))["amp_components"]
                b = get(np.clip(x - delta, -TRUST_BOX, TRUST_BOX))["amp_components"]
                rows.append((a - b) / (
                    amp_limit * (np.clip(x[j] + h, -TRUST_BOX, TRUST_BOX)
                                 - np.clip(x[j] - h, -TRUST_BOX, TRUST_BOX))
                ))
            return np.vstack([np.array(rows).T, 0.05 * np.eye(8)])
        result = least_squares(
            residual, x0, jac=jac, bounds=(-TRUST_BOX, TRUST_BOX),
            max_nfev=max_nfev, xtol=1e-9, ftol=1e-9, gtol=1e-9
        )
        check = get(result.x)
        if best is None or check["partial_BR"] < best[1]["partial_BR"]:
            best = (np.asarray(result.x), check)
        diagnostics.append({
            "start_eta": start_eta, "initial_partial_BR": get(x0)["partial_BR"],
            "final_partial_BR": check["partial_BR"], "nfev": result.nfev,
            "status": result.status, "success": bool(result.success),
            "message": result.message,
            "trust_box": TRUST_BOX,
        })
    return best, diagnostics, len(cache), amp_limit


def neighborhood(base, x, radius, n_random=24):
    rng = np.random.default_rng(2264 + round(radius * 1e6))
    directions = list(np.eye(8)) + list(-np.eye(8))
    directions += [
        z / np.linalg.norm(z) for z in rng.normal(size=(n_random, 8))
    ]
    trials = []
    for d in directions:
        y = x + radius * np.asarray(d)
        if np.max(abs(y)) >= TRUST_BOX:
            continue
        out = evaluate(base, y)
        trials.append(out["partial_BR"])
    return {
        "coefficient_coordinate_radius": radius,
        "absolute_coefficient_step_GeV_dimensionless": radius * COEFFICIENT_UNIT,
        "sample_design": "16 Cartesian signed directions and 24 seeded unit-sphere directions",
        "n_trials": len(trials),
        "n_retained_partial_below_limit": sum(z < MEGII_BOUND for z in trials),
        "min_partial_BR": min(trials) if trials else None,
        "median_partial_BR": float(np.median(trials)) if trials else None,
        "max_partial_BR": max(trials) if trials else None,
        "not_eight_dimensional_volume_fraction": True,
    }


def run(path: Path, max_nfev=32):
    if path.exists():
        raise FileExistsError("Refuse overwriting numerical evidence")
    if not (4 <= max_nfev <= 120):
        raise ValueError("Bounded evaluation cap required")
    scalar, seed, spec, source = fresh_family()
    optimum, searches, n_calls, amp_limit = optimize_family(source, max_nfev)
    x, chk = optimum
    full = evaluate(source, x, with_d4=True)
    if not math.isclose(full["partial_BR"], chk["partial_BR"], rel_tol=1e-12):
        raise ArithmeticError("Independent selected dipole replay failed")
    tests = [neighborhood(source, x, radius) for radius in RADII]
    out = {
        "schema": "zee-2264-new-input-8d-partial-LFV-optimization-pilot-v1",
        "status": "INDEPENDENT_FRESH_FAMILY_EIGHT_REAL_FLAVOR_PILOT_NOT_FULL_LFV",
        "original_20k_scalar_id": 2264,
        "original_scalar_sha256": scalar["scalar_sha256"],
        "vacuum_sufficient_certificate": "PASS",
        "nominal_B_reference": "APPROX_COMPATIBLE",
        "physical_B": "UNKNOWN", "physical_Higgs": "UNKNOWN",
        "historical_neutrino_family_identity_claimed": False,
        "new_seed": SEED, "ordering": "IO", "new_family_id": 1,
        "new_family_seed_hash": seed, "new_target_spec": spec,
        "new_full_neutrino_input": source, "new_input_sha256": digest(source),
        "coefficient_unit": COEFFICIENT_UNIT,
        "optimized_8D_coefficients_in_units": x.tolist(),
        "optimized_input": full["input"],
        "optimized_input_sha256": full["input_sha256"],
        "optimized_target_sha256": full["target_sha256"],
        "retained_mu_to_e_gamma_BR": full["partial_BR"],
        "retained_ratio_to_MEGII_limit": full["partial_BR"] / MEGII_BOUND,
        "retained_partial_below_limit": full["partial_BR"] < MEGII_BOUND,
        "limit_90CL": MEGII_BOUND,
        "dipole_CL": full["dipole_CL"], "dipole_CR": full["dipole_CR"],
        "neutrino_relative_closure": full["neutrino_relative_closure"],
        "max_abs_yukawa": full["max_abs_yukawa"],
        "tree_mu_to_3e_partial_BR": full["partial_mu3e_tree_BR"],
        "retained_other_radiative_BR": full["other_partial_radiative_BR"],
        "D4_cascade_product": full["cascade_tree_BR_product"],
        "D4_br_H2_H1Z": full["H2_to_H1Z_tree_BR"],
        "D4_br_H1_tb": full["H1_to_tb_tree_BR"],
        "optimization_runs": searches, "distinct_source_evaluations": n_calls,
        "coherent_amp_limit_in_module4_units": amp_limit,
        "local_perturbation_checks": tests,
        "source_git_commit": os.environ.get("GITHUB_SHA", "UNSPECIFIED"),
        "full_Zee_LFV": False, "physical_LFV": "UNKNOWN",
        "global_acceptance": None, "production_new_point": None,
        "13TeV_cross_section_pb": None, "14TeV_cross_section_pb": None,
        "interpretation": (
            "Fresh target and neutrino family on original scalar, unlike original "
            "20k historical IO family. Optimized ONLY the validated partial "
            "mu->e gamma dipole, with full actual Module2 neutrino closure and "
            "D4 tree re-evaluation. Tests are directional not 8D allowed volumes. "
            "No full LFV, physical B/Higgs exclusion, or collider viability claim."
        ),
    }
    path.write_text(json.dumps(out, sort_keys=True, indent=2, allow_nan=False) + "\n")
    print(
        "NEW_2264_8D_OPTIMIZATION", "BR", full["partial_BR"],
        "RATIO", out["retained_ratio_to_MEGII_limit"],
        "CASCADE", full["cascade_tree_BR_product"],
        "CLOSURE", full["neutrino_relative_closure"],
        "EVALS", n_calls, flush=True,
    )
    for t in tests:
        print("LOCAL_8D_TEST", t["coefficient_coordinate_radius"],
              t["n_retained_partial_below_limit"], "/", t["n_trials"],
              "MAX_BR", t["max_partial_BR"], flush=True)
    print("GLOBAL_ACCEPTANCE UNKNOWN / PHYSICAL_LFV UNKNOWN", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--max-nfev", type=int, default=32)
    args = ap.parse_args()
    run(args.output, args.max_nfev)


if __name__ == "__main__":
    main()
