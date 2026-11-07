#!/usr/bin/env python3
"""Read-only Zee D12 LFV-texture materiality assessment.

Uses *existing* D12 witnesses; never evaluates a new neutrino point or a
new loop. All numbers concern the frozen retained dipole subset, not the full
physical LFV amplitude. "budget" is a sufficient *conditional* bound, not an
estimate of the missing diagrams.

Run from repo root:
    python3 research/full_constraints/lfv/texture_materiality_gate.py
    python3 research/full_constraints/lfv/texture_materiality_gate.py --output /tmp/texture_gate.json
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
D12 = ROOT / "validation/module12/d12_benchmarks.json"
SNAP = ROOT / "research/full_constraints/lfv/PRACTICAL_SENSITIVITY.json"
LIMITS = ROOT / "research/full_constraints/lfv/experiments.json"


def read(path):
    with path.open() as stream:
        return json.load(stream)


def norm(coeff):
    return math.sqrt(sum(comp[key] ** 2
                         for comp in coeff.values() for key in ("real", "imag")))


def geometry(central_br, reference_norm, new_br, limit):
    """Coherent amplitudes obey sqrt(BR) proportional to their Euclidean norm.

    Triangle inequality: if ||Delta|| <= limit_norm - new_norm, the
    *total* rate remains below the stated experimental limit.
    A physical bound on Delta must be provided independently.
    """
    if not all(math.isfinite(v) and v > 0
               for v in (central_br, reference_norm, new_br, limit)):
        raise ValueError("Finite positive rates and reference norm required")
    limit_norm = reference_norm * math.sqrt(limit / central_br)
    new_norm = limit_norm * math.sqrt(new_br / limit)
    return {
        "retained_norm_GeV_minus2": new_norm,
        "limit_norm_GeV_minus2": limit_norm,
        "max_missing_norm_sufficient_for_pass_GeV_minus2":
            max(0.0, limit_norm - new_norm),
        "requires_cancellation_for_existing_retained_amplitude":
            new_norm > limit_norm,
        "minimum_cancellation_fraction_if_above_bound":
            max(0.0, 1.0 - limit_norm / new_norm),
        "note": "Sufficient conditional norm budget, NOT an estimated or measured omitted amplitude.",
    }


def evaluate():
    data = read(D12)
    partial = read(SNAP)
    limits = read(LIMITS)
    limit = limits["limits"]["mu_to_e_gamma"]["upper_limit"]
    assert data["COMPLETE_LFV"] is False
    assert data["global_zee_acceptance"] is None
    assert data["production"]["status"] == "NOT_EXECUTED"
    cards = {card["id"]: card for card in partial["cards"]}
    out = []
    for group in data["groups"]:
        reference = group["witnesses"]["central"]
        selected = group["witnesses"]["low_joint"]
        key = reference["id"]
        locked = cards[key]
        central_br = locked["results"]["mu_to_e_gamma"]["partial_BR"]
        if not math.isclose(central_br,
                            reference["radiative"]["mu_to_e_gamma"],
                            rel_tol=1e-11):
            raise ValueError("Central D12 and independent sensitivity receipts disagree: " + key)
        c_norm = norm(locked["mu_dipole_coefficients_GeV_minus2"])
        low_br = selected["radiative"]["mu_to_e_gamma"]
        central_gate = geometry(central_br, c_norm, central_br, limit)
        low_gate = geometry(central_br, c_norm, low_br, limit)
        c_prod = reference["cascade_product"]
        l_prod = selected["cascade_product"]
        assert c_prod > 0 and l_prod > 0
        variations = [row for row in group["texture_sensitivity"]
                      if row["base_design"] == "texture_0.001"]
        if len(variations) != 2:
            raise ValueError("Expected two pre-existing +/-1% texture_0.001 variations")
        variant = sorted([{
            "homogeneous_coefficient_factor": row["coefficient_factor"],
            "partial_mu_e_gamma_BR": row["radiative"]["mu_to_e_gamma"],
            "partial_BR_over_experimental_limit":
                row["radiative"]["mu_to_e_gamma"] / limit,
            "cascade_product": row["cascade_product"],
        } for row in variations], key=lambda v: v["homogeneous_coefficient_factor"])
        out.append({
            "spectrum": group["scalar"],
            "ordering": group["ordering"],
            "central_witness_id": key,
            "central_partial_mu_e_gamma_BR": central_br,
            "low_texture_witness_id": selected["id"],
            "low_texture_design": selected["design"],
            "low_partial_mu_e_gamma_BR": low_br,
            "source_locked_neutrino_closure_relative":
                selected["metrics"]["closure_relative"],
            "partial_BR_suppression_factor": central_br / low_br,
            "central": central_gate,
            "low_texture": low_gate,
            "central_cascade_times_tb_BR": c_prod,
            "low_cascade_times_tb_BR": l_prod,
            "cascade_product_relative_shift": l_prod / c_prod - 1,
            "texture_0p001_one_percent_variations": variant,
            "partial_mu3e_tree_low": selected["mu_to_3e_tree"],
            "physical_lfv": "UNKNOWN",
            "physical_exclusion": None,
            "note": "Neutrino closure and tree scalar vacuum are source-level; no full LFV or global model pass.",
        })
    return {
        "description": "D12 saved NO/IO textures, coherent missing-amplitude norm geometry; no new points",
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (D12, SNAP, LIMITS)},
        "mu_to_e_gamma_observed_limit_90CL": limit,
        "cards": out,
        "new_parameter_points": 0,
        "new_loop_amplitudes": 0,
        "experimental_exclusions": None,
        "global_acceptance": None,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, help="Optional scratch output; no input files are changed")
    args = p.parse_args()
    text = json.dumps(evaluate(), indent=2, allow_nan=False) + "\n"
    if args.output:
        if args.output.exists():
            p.error("Refusing to overwrite an existing output")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
