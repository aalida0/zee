#!/usr/bin/env python3
"""F4 eight-point Type-II basis-interface diagnostic, NOT a validated NLO BR.

The A1M SuperIso source fingerprint and the six high-scale effective-dipole
rotations must match exactly. It probes whether the low Cb[7,8] arrays
are already evolved effective dipoles before EOS applies its own rotation.

Outputs two explicitly CONDITIONAL EOS sensitivities: F3's old direct
injection and the inverse-effective-basis input. Neither is a likelihood.
No original 27-spectrum scan and no vendor source modification are made.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
import traceback
from pathlib import Path

from gateA1r_run_br_pilot import check_superiso_source, compile_pilot
from zee_gateF2_eos_flavio_nlo_27_validation import RatePair
from zee_gateF3_fullNLO_source_RG_27 import probe, net_low, SCALE_W, SCALE_B

STATUS = "NOT_YET_VALIDATED"
BLOCKED = "BLOCKED"
MASSES = (300.0, 580.0, 670.0, 1000.0)
TANBETAS = (5.6, 50.0)
Y7 = {3: -1.0 / 3, 4: -4.0 / 9, 5: -20.0 / 3, 6: -80.0 / 9}
Y8 = {3: 1.0, 4: -1.0 / 6, 5: 20.0, 6: -10.0 / 3}


def clean_source(source: str) -> str:
    return re.sub(r"/\*.*?\*/|//[^\n]*", " ", source, flags=re.S)


def normalized(s: str) -> str:
    return re.sub(r"\s+", "", s)


def audit_low_basis_source(source: str) -> dict:
    """Check the AF-pinned source's effective-input, evolved-output path.

    This proves what source path is implemented, not its physical scheme
    equivalence with EOS's NLO c1..c8 / evanescent-operator prescription.
    """
    src = clean_source(source)
    begin = re.search(r"\bvoid\s+C_calculator_base1\s*\(", src)
    end = re.search(r"\bvoid\s+C_calculator_base2\s*\(", src)
    if not begin or not end or end.start() <= begin.start():
        raise ValueError("Cannot uniquely delimit C_calculator_base1 source")
    body = src[begin.start():end.start()]
    for order in (0, 1, 2):
        for op, weights in ((7, Y7), (8, Y8)):
            name = f"C{order}w{op}"
            found = re.findall(
                rf"\bdouble\s+(?:complex\s+)?{name}\s*=\s*([^;]+);",
                body, re.S)
            expected = f"C{order}w[{op}]" + "".join(
                f"{'+' if w >= 0 else '-'}"
                + {3: ("1./3." if op == 7 else "1."),
                   4: ("4./9." if op == 7 else "1./6."),
                   5: ("20./3." if op == 7 else "20."),
                   6: ("80./9." if op == 7 else "10./3.")}[k]
                + f"*C{order}w[{k}]" for k, w in weights.items())
            # Original SuperIso writes +C3 (not +1.*C3) for C8.
            expected = expected.replace(f"+1.*C{order}w[3]",
                                        f"+C{order}w[3]")
            if len(found) != 1 or normalized(found[0]) != expected:
                raise ValueError(f"Unrecognized source effective rotation {name}")
    for op in (7, 8):
        match = re.search(
            rf"if\s*\(\s*je\s*==\s*{op}\s*\)\s*\{{([^}}]+)\}}",
            body, re.S)
        if not match:
            raise ValueError(f"Cannot locate evolved dipole branch je={op}")
        branch = normalized(match[1])
        for lhs, rhs in (
            ("C0b[ie]", f"U0[ie-1][je-1]*C0w{op}"),
            ("C1b[ie]", f"U0[ie-1][je-1]*C1w{op}"),
            ("C2b[ie]", f"U0[ie-1][je-1]*C2w{op}"),
        ):
            if lhs not in branch or rhs not in branch:
                raise ValueError(f"Effective dipole evolution not traced: {lhs}, {rhs}")
    # In the source version under audit, no explicit inverse transform
    # Cb7,8_eff -> Cb7,8_raw occurs after the RG evolution.
    if re.search(r"\bC[012]b\s*\[\s*[78]\s*\]\s*(?:[+\-*/]?=)", body):
        raise ValueError("Source contains direct low-dipole assignments: audit manually")
    return {
        "six_high_scale_effective_rotations_source_checked": True,
        "three_order_evolution_uses_effective_dipoles": True,
        "no_explicit_low_dipole_inverse_in_base1": True,
        "basis_inference": "low_Cb7_Cb8_are_effective_in_this_source_path",
        "finite_renormalization_and_evanescent_scheme_equivalence_certified": False,
    }


def raw_for_eos(eff: dict[int, float]) -> dict[int, float]:
    """Inverse standard effective rotation before EOS's internal rotation."""
    if set(eff) != set(range(1, 9)):
        raise ValueError("Require the complete low-scale C1..C8 NP vector")
    if not all(math.isfinite(float(v)) for v in eff.values()):
        raise ValueError("Nonfinite low-scale coefficient")
    raw = dict(eff)
    raw[7] -= sum(weight * eff[k] for k, weight in Y7.items())
    raw[8] -= sum(weight * eff[k] for k, weight in Y8.items())
    for op, weights in ((7, Y7), (8, Y8)):
        reconstructed = raw[op] + sum(w * raw[k] for k, w in weights.items())
        if abs(reconstructed - eff[op]) > 2e-14 * max(1.0, abs(eff[op])):
            raise ValueError("Dipole inverse rotation closure failed")
    return raw


def run_pilot(pair, exe: Path) -> list[dict]:
    pair.prepare()
    alpha_b = pair.flavio.physics.running.running.get_alpha(
        pair.par, SCALE_B, nf_out=5)["alpha_s"]
    if not 0.17 < alpha_b < 0.28:
        raise ValueError("Unexpected flavio alpha_s(4.2), no NLO scaling accepted")
    aslow = alpha_b / (4.0 * math.pi)
    rows = []
    for tanb in TANBETAS:
        for mass in MASSES:
            data = probe(exe, mass, mass, tanb, 0.0)
            lo = net_low(data, 0, aslow)
            dip = net_low(data, 1, aslow)
            full = net_low(data, 2, aslow)
            input_old = pair.eos_rate(full)
            input_inverse = pair.eos_rate(raw_for_eos(full))
            f0 = pair.eos_rate(raw_for_eos(lo))
            f_dip = pair.eos_rate(raw_for_eos(dip))
            h = {n: full[n] - lo[n] for n in range(1, 9)}
            minus = {n: lo[n] - h[n] for n in range(1, 9)}
            fminus = pair.eos_rate(raw_for_eos(minus))
            linear_odd = 0.5 * (input_inverse - fminus)
            quadratic_even = 0.5 * (input_inverse + fminus) - f0
            if not all(math.isfinite(v) for v in
                       (input_old, input_inverse, f0, f_dip, fminus,
                        linear_odd, quadratic_even)):
                raise ValueError("Nonfinite EOS response")
            rows.append({
                "mass_GeV": mass, "tanbeta": tanb,
                "alpha_s_low_from_flavio": alpha_b,
                "eos_BR_F3_direct_injection_CONDITIONAL": input_old,
                "eos_BR_inverse_effective_CONDITIONAL": input_inverse,
                "basis_interface_rate_difference_CONDITIONAL":
                    input_inverse - input_old,
                "eos_BR_LO_matching_NLO_RG_CONDITIONAL": f0,
                "eos_BR_NLO_dipoles_matching_CONDITIONAL": f_dip,
                "eos_BR_full_source_NLO_matching_CONDITIONAL": input_inverse,
                "fourquark_matching_BR_shift_CONDITIONAL":
                    input_inverse - f_dip,
                "nlo_matching_insertion_odd_rate_part": linear_odd,
                "nlo_matching_insertion_even_rate_part": quadratic_even,
                "even_is_formally_higher_order_not_complete_NNLO": True,
                "odd_includes_unseparated_NLO_kernel_times_NLO_WC": True,
                "source_high_NLO_C4": data[2, 4]["high_NLO"],
                "low_effective_C7": full[7],
                "low_effective_C8": full[8],
                "low_fourquark_C3": full[3],
                "low_fourquark_C4": full[4],
                "low_fourquark_C5": full[5],
                "low_fourquark_C6": full[6],
                "full_nlo_rate_and_exclusion_validated": False,
            })
    if len(rows) != 8 or len({(x["mass_GeV"], x["tanbeta"])
                             for x in rows}) != 8:
        raise ValueError("Expected eight distinct Type-II controls")
    if not any(abs(x["source_high_NLO_C4"]) > 1e-10 for x in rows):
        raise ValueError("Source did not provide a nonzero NLO C4 canary")
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--vendor-root", type=Path, required=True)
    p.add_argument("--a1m-provenance", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    root = Path.cwd().resolve()
    out = a.output_dir.resolve()
    if not out.is_relative_to(root / "work"):
        p.error("F4 output must be below the current repository's work/ (not /data)")
    if out.exists() and any(out.iterdir()):
        p.error("Refusing to overwrite nonempty audit output directory")
    out.mkdir(parents=True, exist_ok=True)
    status = {"status": BLOCKED, "Zee_flavor_allowed_or_excluded": None}
    exit_code = 1
    try:
        si = check_superiso_source(a.vendor_root, a.a1m_provenance)
        source_file = a.vendor_root / "src" / "wilson.c"
        content = source_file.read_bytes()
        source_basis = audit_low_basis_source(content.decode("utf-8"))
        binary_path = out / "f4_A1M_source_RG_probe"
        build = compile_pilot(
            a.vendor_root, binary_path,
            Path(__file__).with_name("zee_gateF3_fullNLO_rg_probe.c"), False)
        pair = RatePair()
        rows = run_pilot(pair, binary_path)
        write_csv(out / "F4_8_TypeII_basis_interface_CONDITIONAL.csv", rows)
        status = {
            "status": STATUS,
            "a1m_sha256": hashlib.sha256(content).hexdigest(),
            "source_checks": source_basis, "other_source_provenance": si,
            "compiled_F3_source_probe": build,
            "eos_version": pair.eos_version,
            "flavio_version": pair.flavio_version,
            "masses_GeV": list(MASSES), "tanbeta": list(TANBETAS),
            "num_controls": len(rows), "controls": rows,
            "EOS_source_commit_audited_separately":
                "3eb16b5b7265df7023363e615179fd44a1a02d00",
            "EOS_installed_package_source_SHA_certified": False,
            "NLO_operator_scheme_mapping_certified": False,
            "fixed_order_NLO_EOS_extracted": False,
            "independent_NLO_TypeII_reference_validated": False,
            "paper_ready_Zee_95CL_exclusions": False,
            "Zee_flavor_allowed_or_excluded": None,
        }
        exit_code = 0
    except Exception as exc:
        status = {"status": BLOCKED, "error": repr(exc),
                  "traceback": traceback.format_exc(),
                  "Zee_flavor_allowed_or_excluded": None}
        print("F4_FAIL_CLOSED", repr(exc), file=sys.stderr, flush=True)
    finally:
        (out / "summary.json").write_text(
            json.dumps(status, sort_keys=True, indent=2) + "\n")
        print("F4_STATUS", status["status"],
              "F4_SUMMARY", out / "summary.json", flush=True)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
