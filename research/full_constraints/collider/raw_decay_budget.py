#!/usr/bin/env python3
"""Source-bound pre-detector 14 TeV Zee cascade yields (NOT limits).

Read ONLY existing D14D 14 TeV LO five-flavour charge-summed
production and actual family decay records. No new integration or scan.

Examples:
  python3 research/full_constraints/collider/raw_decay_budget.py
  python3 research/full_constraints/collider/raw_decay_budget.py --output /tmp/zee-collider-raw.json
"""
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT / "module14/conditional_scan/production_map_14TeV_families.csv"

# Source: PDG 2026 particle listings / pdgLive W and Z decay modes.
PDG_SOURCE = {
    "Z": "https://pdgprod.lbl.gov/pdgprod/pdgLive/Particle.action?node=S044",
    "W": "https://pdgprod.lbl.gov/pdgprod/pdgLive/Particle.action?home=&node=S043",
}
B = {
    "Z_to_ee": 0.033632,
    "Z_to_mumu": 0.033662,
    "W_to_enu": 0.1071,
    "W_to_munu": 0.1063,
    "W_to_hadrons": 0.6741,
}
LUMINOSITY_FB = 3000.0
EXPECTED_IDS = {"15591", "2264", "15673"}


def numeric(obj, name):
    try:
        value = float(obj[name])
    except (TypeError, ValueError, KeyError) as error:
        raise ValueError("Invalid missing/non-numeric " + name) from error
    if not math.isfinite(value):
        raise ValueError("Non-finite " + name)
    return value


def evaluate(source=INPUT, luminosity_fb=LUMINOSITY_FB):
    if not math.isfinite(luminosity_fb) or luminosity_fb <= 0:
        raise ValueError("Positive finite luminosity required")
    if not math.isclose(B["Z_to_ee"] + B["Z_to_mumu"] + 0.033696, .101, abs_tol=.001):
        raise ValueError("Unexpected PDG Z leptonic input")
    z_ll = B["Z_to_ee"] + B["Z_to_mumu"]
    w_l = B["W_to_enu"] + B["W_to_munu"]
    w_h = B["W_to_hadrons"]
    factors = {
        "Zll_both_top_hadronic": z_ll * w_h**2,
        "Zll_exactly_one_direct_top_e_mu": z_ll * 2 * w_l * w_h,
        "Zll_both_tops_direct_e_mu": z_ll * w_l**2,
    }
    by_id = defaultdict(list)
    with source.open(newline="") as f:
        for i, row in enumerate(csv.DictReader(f), 1):
            ident = str(row["id"])
            if ident not in EXPECTED_IDS or numeric(row, "energy_TeV") != 14:
                raise ValueError("Unexpected spectrum or energy at CSV row " + str(i))
            if row["vacuum"] != "PASS" or row["physical_bsgamma"] != "UNKNOWN":
                raise ValueError("Unexpected constraint interpretation")
            if row["global_acceptance"] not in ("null", "", "None"):
                raise ValueError("Not a conditional benchmark: global acceptance is asserted")
            if row["production_status"] != "D14D_NATIVE_RUN_PASS":
                raise ValueError("Production is not a native validated integration")
            h1 = json.loads(row["H1_decay_BR_separate"])
            h1_tb = numeric(h1, "t anti-b")
            cascade = numeric(row, "BR_H2_H1Z")
            sigma_pb = numeric(row, "sigma_pb")
            rate_pb = numeric(row, "sigma_times_BR_pb")
            if not (0 < h1_tb <= 1 and 0 < cascade <= 1 and sigma_pb > 0 and rate_pb > 0):
                raise ValueError("Unphysical branching or cross-section input")
            if not math.isclose(rate_pb, sigma_pb * cascade, rel_tol=3e-12):
                raise ValueError("Generator and decay product inconsistent")
            # The associated top and the top from H1 are both retained;
            # BR(top->Wb) treated as 1, not independently measured here.
            n = rate_pb * 1000.0 * luminosity_fb * h1_tb
            by_id[ident].append({
                "family": row["family"], "ordering": row["ordering"],
                "binding_sha256": row["binding_sha256"],
                "mH1_GeV": numeric(row, "mH1_GeV"),
                "mH2_GeV": numeric(row, "mH2_GeV"),
                "H2_total_width_GeV": numeric(row, "H2_total_width_GeV"),
                "BR_H2_to_H1Z": cascade,
                "BR_H1_to_tb": h1_tb,
                "sigma_associated_charge_summed_LO_pb": sigma_pb,
                "sigma_times_BR_H2_H1Z_fb": rate_pb * 1000.0,
                "raw_H1tb_Z_any": n,
                "Z_to_ee_mumu": n * z_ll,
                "channels": {key: n * factor for key, factor in factors.items()},
            })

    if set(by_id) != EXPECTED_IDS:
        raise ValueError("Incomplete benchmark ID inventory")
    benchmark_summary = []
    for ident, items in sorted(by_id.items()):
        if len(items) != 4 or len({(x["ordering"], x["family"]) for x in items}) != 4:
            raise ValueError("Expected exactly four distinct neutrino families per ID")
        for key in ("mH1_GeV", "mH2_GeV", "sigma_associated_charge_summed_LO_pb"):
            if max(x[key] for x in items) - min(x[key] for x in items) > 1e-9:
                raise ValueError("Same-scalar data inconsistent for "+key)
        fields = ("sigma_times_BR_H2_H1Z_fb", "BR_H2_to_H1Z",
                  "BR_H1_to_tb", "raw_H1tb_Z_any", "Z_to_ee_mumu")
        ranges = {key: {"min": min(x[key] for x in items), "max": max(x[key] for x in items)}
                  for key in fields}
        for name in factors:
            ranges[name] = {"min": min(x["channels"][name] for x in items),
                            "max": max(x["channels"][name] for x in items)}
        benchmark_summary.append({
            "id": ident, "mH1_GeV": items[0]["mH1_GeV"],
            "mH2_GeV": items[0]["mH2_GeV"], "family_count": 4,
            "H2_width_over_mass_range": {
                "min": min(x["H2_total_width_GeV"]/x["mH2_GeV"] for x in items),
                "max": max(x["H2_total_width_GeV"]/x["mH2_GeV"] for x in items),
            },
            "ranges": ranges,
        })
    return {
        "status": "PRE_DETECTOR_TRUTH_DECAY_BUDGET_ONLY",
        "energy_TeV": 14,
        "luminosity_fb_inverse": luminosity_fb,
        "source_csv_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "production": "LO 5FS bg->tH2 charge summed, exactly once; no 4FS or NLO matching",
        "BR_inputs": B,
        "BR_sources": PDG_SOURCE,
        "channel_factors_excluding_H1tb": factors,
        "top_to_Wb": "Assumed 1.0; no tau feeddown; no detector acceptance",
        "benchmarks": benchmark_summary,
        "source_family_rows": sum(map(len, by_id.values())),
        "background_yields": None,
        "detector_acceptance_efficiency": None,
        "signal_selected_events": None,
        "cross_section_theory_uncertainty": None,
        "expected_CLs": None,
        "global_acceptance": None,
        "limitations": [
            "BR(Z->ee/mumu) and W direct e/mu/hadronic modes only.",
            "Predicted 3l yields include either top assigning its W to e/mu, not necessarily the H1 daughter top.",
            "W->tau->e/mu and tau->hadronic backgrounds not included.",
            "13 TeV native rates cannot be relabelled 13.6 TeV; 14 TeV backgrounds are not available from these records.",
            "No shower, b tagging, reconstruction, luminosity/systematic uncertainties or calibrated HL-LHC reach.",
            "Original charged Higgs physical B, complete LFV and Higgs exclusions remain UNKNOWN.",
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    p.add_argument("--luminosity-fb", type=float, default=LUMINOSITY_FB)
    args = p.parse_args()
    result = evaluate(luminosity_fb=args.luminosity_fb)
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        if args.output.exists():
            p.error("Refuse to overwrite existing output")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized)
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
