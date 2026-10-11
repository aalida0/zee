#!/usr/bin/env python3
"""Convert a Type-II 2HDM charged-Higgs LO production proxy into Zee HL-LHC yields.

This does not establish a viable Zee-model benchmark, full charged-Higgs
branching fractions, backgrounds, discovery significance, or a precision QCD rate.
"""
from __future__ import annotations
import argparse
import json
import math
import re
from pathlib import Path


def calculate(sigma_pb: float, error_pb: float, gamma: float,
              luminosity_fb: float, br_h2_to_h1z: float, br_h1_tb: float,
              br_z_ee_mumu: float = 0.0673, br_w_e_mu: float = 0.216,
              br_w_had: float = 0.674) -> dict:
    if sigma_pb < 0 or error_pb < 0 or luminosity_fb < 0:
        raise ValueError("Cross sections, errors and luminosity must be nonnegative")
    for label, val in [("br_h2_to_h1z", br_h2_to_h1z),
                       ("br_h1_tb", br_h1_tb), ("br_z_ee_mumu", br_z_ee_mumu),
                       ("br_w_e_mu", br_w_e_mu), ("br_w_had", br_w_had)]:
        if not 0 <= val <= 1:
            raise ValueError(f"{label} is outside [0,1]")
    if br_w_e_mu + br_w_had > 1 + 1e-9:
        raise ValueError("e/mu and hadronic W decays overlap")
    factor = math.sin(gamma) ** 2
    rate_fb = sigma_pb * 1000 * factor
    stat_fb = error_pb * 1000 * factor
    produced = luminosity_fb * rate_fb
    cascades = produced * br_h2_to_h1z * br_h1_tb
    zll = cascades * br_z_ee_mumu
    trilepton = zll * 2 * br_w_e_mu * br_w_had
    dilepton = zll * br_w_had ** 2
    return {
        "status": "LO_2HDM_PRODUCTION_PROXY_UNVALIDATED_ZEE_BR_AND_ACCEPTANCE",
        "sigma_2hdm_LO_fb": 1000 * sigma_pb,
        "sigma_2hdm_LO_integration_error_fb": 1000 * error_pb,
        "sin_gamma_squared": factor,
        "sigma_zee_proxy_LO_fb": rate_fb,
        "sigma_zee_proxy_integration_error_fb": stat_fb,
        "theory_pdf_scale_and_4fs_5fs_uncertainty": "NOT_EVALUATED",
        "luminosity_fb_inverse": luminosity_fb,
        "assumed_BR_H2_H1Z": br_h2_to_h1z,
        "assumed_BR_H1_tb": br_h1_tb,
        "produced_events": produced,
        "cascade_events": cascades,
        "Z_to_e_mu_dilepton_events": zll,
        "one_direct_W_to_e_mu_and_other_hadronic_probability": 2 * br_w_e_mu * br_w_had,
        "3l_before_detector": trilepton,
        "3l_selected_if_efficiency_2pct": trilepton * .02,
        "3l_selected_if_efficiency_5pct": trilepton * .05,
        "3l_selected_if_efficiency_10pct": trilepton * .10,
        "Zll_and_both_W_had_before_detector": dilepton,
    }


def cross_section_from_log(path: Path) -> tuple[float, float]:
    """Read last final MG5 Cross-section row in pb; never match survey estimates."""
    content = path.read_text()
    matches = re.findall(
        r"Cross-section\s*:\s*([0-9]+(?:\.[0-9]*)?(?:[eE][+-]?\d+)?)"
        r"\s*(?:\+-|\+/-|±)\s*"
        r"([0-9]+(?:\.[0-9]*)?(?:[eE][+-]?\d+)?)\s*pb\b",
        content,
        flags=re.I,
    )
    if not matches:
        raise ValueError(f"No final Cross-section : value +- error pb in {path}")
    return float(matches[-1][0]), float(matches[-1][1])


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--mg5-log", type=Path, help="MG5 run log ending in Cross-section : ... pb")
    source.add_argument("--sigma-2hdm-pb", type=float, help="MG5 production proxy total in pb")
    p.add_argument("--integration-error-pb", type=float, default=0,
                   help="Required only with --sigma-2hdm-pb; integration uncertainty, not theory")
    p.add_argument("--gamma", type=float, default=1.089)
    p.add_argument("--luminosity-fb", type=float, default=3000)
    p.add_argument("--br-h2-h1z", type=float, default=.70)
    p.add_argument("--br-h1-tb", type=float, default=.95)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    sigma, error = (cross_section_from_log(args.mg5_log) if args.mg5_log
                    else (args.sigma_2hdm_pb, args.integration_error_pb))
    result = calculate(sigma, error, args.gamma, args.luminosity_fb,
                       args.br_h2_h1z, args.br_h1_tb)
    data = json.dumps(result, indent=2) + "\n"
    print(data, end="")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data)


if __name__ == "__main__":
    main()
