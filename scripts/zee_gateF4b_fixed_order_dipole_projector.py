#!/usr/bin/env python3
"""F4b: strict O(alpha_s) low-scale C7eff^2 projector, NOT full NLO BR.

This is deliberately a SOURCE-COEFFICIENT physics audit, not a reproduction
of the EOS NLO inclusive kernel. The latter includes r_i amplitudes,
bremsstrahlung, HQE terms and nontrivial scheme-dependent C3..C6 pieces.
No EOS normalization or experimental likelihood is inferred here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
import traceback
from pathlib import Path

STATUS = "F4B_ORDER_RESOLVED_DIPOLE_PROJECTOR_NOT_FULL_NLO_RATE"
BLOCKED = "F4B_BLOCKED_NOT_FULL_NLO_RATE"
MASSES = (300.0, 580.0, 670.0, 1000.0)
TANBETAS = (5.6, 50.0)
ALPHA_PATTERN = re.compile(
    r"^F4B_SOURCE_INPUT muW=(\S+) mub=(\S+) "
    r"alphas_muW=(\S+) alphas_mub=(\S+) "
    r"mt_running_muW=(\S+) mtmt=(\S+) "
    r"mt_pole=(\S+) mb_pole=(\S+)$")


def checked(value: object, label: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Nonfinite " + label)
    return result


def parse_source_alpha(output: str, muw: float, mub: float) -> dict:
    lines = output.splitlines()
    if lines.count("F4B_NOT_A_BRANCHING_RATIO_OR_EXCLUSION") != 1:
        raise ValueError("Missing source-alpha authenticity marker")
    captures = [ALPHA_PATTERN.fullmatch(s) for s in lines]
    captures = [m for m in captures if m]
    if len(captures) != 1:
        raise ValueError("Expected exactly one complete source input row")
    keys = ("muW", "mub", "alphas_muW", "alphas_mub",
            "mt_running_muW", "mtmt", "mt_pole", "mb_pole")
    d = dict(zip(keys, (checked(x, "source running input")
                        for x in captures[0].groups())))
    if abs(d["muW"] - muw) > 1.e-10 or abs(d["mub"] - mub) > 1.e-10:
        raise ValueError("Source input scales mismatch")
    if not (0.08 < d["alphas_muW"] < .15
            and .15 < d["alphas_mub"] < .35
            and 100. < d["mt_running_muW"] < 250.):
        raise ValueError("Source running input out of accepted diagnostic range")
    return d


def projector(sm0: float, sm1: float, np0: float, np1: float,
              alpha_s_low: float) -> dict:
    """Unnormalised |C7eff|^2 expansion; all inputs are coefficient arrays.

    Full = SM + NP; Ceff = Ceff^(0) + [alpha_s/(4*pi)] Ceff^(1).
    It returns the NP-minus-SM response at LO, O(a), and O(a^2),
    where a = alpha_s/(4*pi). The O(a^2) term is NOT an NNLO rate.
    """
    sm0, sm1, np0, np1, alpha_s_low = (
        checked(v, k) for v, k in zip(
            (sm0, sm1, np0, np1, alpha_s_low),
            ("sm0", "sm1", "np0", "np1", "alpha_s_low")))
    if not 0 < alpha_s_low < 1:
        raise ValueError("Invalid strong coupling")
    a = alpha_s_low / (4. * math.pi)
    total0, total1 = sm0 + np0, sm1 + np1
    leading = total0 * total0 - sm0 * sm0
    nlo = 2. * a * (total0 * total1 - sm0 * sm1)
    partial_nnlo = a*a * (total1*total1 - sm1*sm1)
    exact = (total0 + a*total1)**2 - (sm0 + a*sm1)**2
    if abs(exact - (leading + nlo + partial_nnlo)) > (
        5.e-14 * max(1., abs(exact), abs(leading), abs(nlo))):
        raise ArithmeticError("Order-by-order amplitude closure failed")
    return {
        "C7eff_SM_LO": sm0, "C7eff_SM_NLO_coefficient": sm1,
        "C7eff_NP_LO": np0, "C7eff_NP_NLO_coefficient": np1,
        "a_slow_over_4pi": a,
        "Q7eff_NP_minus_SM_LO": leading,
        "Q7eff_NP_minus_SM_Oalpha_s": nlo,
        "Q7eff_NP_minus_SM_truncated_through_Oalpha_s": leading+nlo,
        "Q7eff_NP_minus_SM_partial_Oalpha_s_squared": partial_nnlo,
        "Q7eff_NP_minus_SM_untruncated_square": exact,
        "Q7eff_not_full_B_to_Xs_gamma_rate": True,
    }


def check_f4_source_summary(path: Path, vendor_source_sha: str) -> dict:
    f4 = json.loads(path.read_text())
    if f4.get("status") != "NOT_YET_VALIDATED":
        raise ValueError("F4 does not report completed conditional pilot")
    if f4.get("a1m_sha256") != vendor_source_sha:
        raise ValueError("F4 A1M SHA does not match current pinned source")
    check = f4.get("source_checks", {})
    if (check.get("six_high_scale_effective_rotations_source_checked") is not True
        or check.get("no_explicit_low_dipole_inverse_in_base1") is not True
        or check.get("three_order_evolution_uses_effective_dipoles") is not True):
        raise ValueError("F4 source low-scale effective basis not verified")
    rows = f4.get("controls")
    if not isinstance(rows, list) or len(rows) != 8:
        raise ValueError("F4 requires original eight Type-II controls")
    mapped = {}
    for row in rows:
        key = (checked(row["mass_GeV"], "F4 mass"),
               checked(row["tanbeta"], "F4 tanbeta"))
        if key in mapped or key not in {(m,t) for t in TANBETAS for m in MASSES}:
            raise ValueError("Unknown/duplicate F4 Type-II control")
        mapped[key] = row
    if len(mapped) != 8:
        raise ValueError("Missing F4 Type-II controls")
    build = f4.get("compiled_F3_source_probe", {})
    if not build.get("library_SHA256") or not build.get("driver_SHA256"):
        raise ValueError("F4 missing source-linked library/probe fingerprints")
    return mapped


def run_projector(exe: Path, source_inputs: dict, f4_rows: dict) -> list[dict]:
    # Import the F3 scientific probe ONLY when running against the AF library.
    from zee_gateF3_fullNLO_source_RG_27 import probe, SCALE_W, SCALE_B
    a = source_inputs["alphas_mub"]
    rows = []
    for t in TANBETAS:
        for mass in MASSES:
            wc = probe(exe, mass, mass, t, 0.)
            sm0 = wc[0, 7]["low_SM_LO"]
            sm1 = wc[0, 7]["low_SM_NLO"]
            v0 = wc[0, 7]["low_LO"]
            for k in (1, 2):
                if (abs(wc[k, 7]["low_LO"] - v0) > 1.e-11
                    or abs(wc[k, 7]["low_SM_LO"] - sm0) > 1.e-11
                    or abs(wc[k, 7]["low_SM_NLO"] - sm1) > 1.e-11):
                    raise ValueError("Low-scale LO/SM dipole changes with high-order input")
            profiles = {
                name: projector(sm0, sm1, v0, wc[mode, 7]["low_NLO"], a)
                for name, mode in (("LO_high_matching_NLO_RGE", 0),
                                   ("NLO_dipoles_matching_NLO_RGE", 1),
                                   ("FULL_NLO_matching_NLO_RGE", 2))
            }
            base, dipo, full = (profiles[k] for k in profiles)
            # At strict first order in a, only interference with C7eff^(0)
            # survives from the matching-induced NLO C7eff shift. It can
            # include operator mixing into C7eff; never label it total BR.
            nlo_matching = full["Q7eff_NP_minus_SM_Oalpha_s"] - (
                base["Q7eff_NP_minus_SM_Oalpha_s"])
            nlo_dip_matching = dipo["Q7eff_NP_minus_SM_Oalpha_s"] - (
                base["Q7eff_NP_minus_SM_Oalpha_s"])
            nlo_fourquark_projection = (
                full["Q7eff_NP_minus_SM_Oalpha_s"]
                - dipo["Q7eff_NP_minus_SM_Oalpha_s"])
            if abs(nlo_matching - (
                2. * a / (4. * math.pi) * (sm0+v0) *
                (wc[2,7]["low_NLO"] - wc[0,7]["low_NLO"]))) > 1.e-12:
                raise ArithmeticError("NLO matching interference closure failed")
            if abs(nlo_fourquark_projection - (
                2. * a / (4. * math.pi) * (sm0+v0) *
                (wc[2,7]["low_NLO"] - wc[1,7]["low_NLO"]))) > 1.e-12:
                raise ArithmeticError("NLO four-quark-induced C7eff closure failed")
            prior = f4_rows[(mass, t)]
            flavio_as = checked(prior["alpha_s_low_from_flavio"],
                                "prior F4 flavio coupling")
            row = {
                "mass_GeV": mass, "tanbeta": t,
                "muW_GeV": SCALE_W, "mub_GeV": SCALE_B,
                "alpha_s_mub_SUPERISO": a,
                "alpha_s_mub_F4_flavio_reference": flavio_as,
                "alpha_s_relative_superiso_minus_flavio": (a-flavio_as)/flavio_as,
                "C7eff_SM_LO": sm0,
                "C7eff_SM_NLO_coefficient": sm1,
                "C7eff_NP_LO": v0,
                "C7eff_NP_NLO_Coeff_LO_matching": wc[0,7]["low_NLO"],
                "C7eff_NP_NLO_Coeff_dipoles_matching": wc[1,7]["low_NLO"],
                "C7eff_NP_NLO_Coeff_full_matching": wc[2,7]["low_NLO"],
                "C8eff_NP_NLO_Coeff_full_matching": wc[2,8]["low_NLO"],
                "Q7eff_NP_LO": full["Q7eff_NP_minus_SM_LO"],
                "Q7eff_NP_NLO_evolution_and_SM_baseline":
                    base["Q7eff_NP_minus_SM_Oalpha_s"],
                "Q7eff_NP_NLO_matching_dipoles_only": nlo_dip_matching,
                "Q7eff_NP_NLO_matching_fourquark_induced": nlo_fourquark_projection,
                "Q7eff_NP_NLO_matching_total": nlo_matching,
                "Q7eff_NP_Oalpha_s_all": full["Q7eff_NP_minus_SM_Oalpha_s"],
                "Q7eff_NP_strictly_truncated_LO_plus_NLO":
                    full["Q7eff_NP_minus_SM_truncated_through_Oalpha_s"],
                "Q7eff_NP_partial_a_squared_from_squared_NLO_dipole":
                    full["Q7eff_NP_minus_SM_partial_Oalpha_s_squared"],
                "Q7eff_NP_untruncated_square":
                    full["Q7eff_NP_minus_SM_untruncated_square"],
                "F4_inverse_EOS_BR_conditional_not_comparable_to_Q7":
                    checked(prior["eos_BR_inverse_effective_CONDITIONAL"],
                            "prior conditional F4 EOS BR"),
                "EOS_NLO_matrix_elements_bremsstrahlung_HQE_included": False,
                "finite_scheme_equivalence_certified": False,
                "physical_full_NLO_BtoXsgamma_rate_calculated": False,
            }
            if not all(isinstance(v, bool) or
                       (math.isfinite(v) if isinstance(v, (int, float)) else True)
                       for v in row.values()):
                raise ValueError("Nonfinite row")
            rows.append(row)
            print("F4B_TYPEII", mass, t,
                  "Q7eff_LO", f"{row['Q7eff_NP_LO']:.8g}",
                  "Q7eff_NLO", f"{row['Q7eff_NP_Oalpha_s_all']:.8g}",
                  "NLO_match", f"{nlo_matching:.8g}",
                  "NOT_BR", flush=True)
    if len(rows) != 8:
        raise ValueError("F4b incomplete Type-II cohort")
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--vendor-root", type=Path, required=True)
    ap.add_argument("--a1m-provenance", type=Path, required=True)
    ap.add_argument("--f4-summary", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    root = Path.cwd().resolve()
    out = args.output_dir.resolve()
    if not root.is_relative_to(Path("/home")):
        ap.error("F4b execution directory must be under /home, never /data")
    if not out.is_relative_to(root / "work"):
        ap.error("F4b outputs must remain under /home repo work/")
    if out.exists() and any(out.iterdir()):
        ap.error("Refuse to overwrite existing F4b result")
    out.mkdir(parents=True, exist_ok=True)
    result = {"status": BLOCKED, "Zee_allowed_or_excluded": None}
    ret = 1
    try:
        from gateA1r_run_br_pilot import check_superiso_source, compile_pilot
        from zee_gateF4_typeii_basis_interface_pilot import audit_low_basis_source
        from zee_gateF3_fullNLO_source_RG_27 import SCALE_W, SCALE_B
        root_si = args.vendor_root.resolve()
        manifest = args.a1m_provenance.resolve()
        provenance = check_superiso_source(root_si, manifest)
        wilson_data = (root_si / "src" / "wilson.c").read_bytes()
        basis = audit_low_basis_source(wilson_data.decode("utf-8"))
        source_hash = hashlib.sha256(wilson_data).hexdigest()
        f4 = check_f4_source_summary(args.f4_summary, source_hash)
        prior = json.loads(args.f4_summary.read_text())
        prior_build = prior["compiled_F3_source_probe"]
        current_library_sha = hashlib.sha256(
            (root_si / "src" / "libsuperiso.a").read_bytes()).hexdigest()
        if current_library_sha != prior_build["library_SHA256"]:
            raise ValueError("A1M library changed since F4")
        prior_driver_sha = hashlib.sha256(
            Path(__file__).with_name("zee_gateF3_fullNLO_rg_probe.c")
            .read_bytes()).hexdigest()
        if prior_driver_sha != prior_build["driver_SHA256"]:
            raise ValueError("F3 C probe changed since F4")
        alpha_exe = out / "f4b_source_running_parameters"
        alpha_build = compile_pilot(
            root_si, alpha_exe,
            Path(__file__).with_name("zee_gateF4b_source_alpha_probe.c"), False)
        env = subprocess.run(
            [str(alpha_exe), f"{SCALE_W:.17g}", f"{SCALE_B:.17g}"],
            check=True, capture_output=True, text=True, timeout=90)
        inputs = parse_source_alpha(env.stdout, SCALE_W, SCALE_B)
        rg_exe = out / "f4b_source_wilson_rg_probe"
        rg_build = compile_pilot(
            root_si, rg_exe,
            Path(__file__).with_name("zee_gateF3_fullNLO_rg_probe.c"), False)
        rows = run_projector(rg_exe, inputs, f4)
        keys = list(rows[0])
        with (out / "F4b_8_TypeII_fixed_order_C7eff_projector.csv").open(
                "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
        result = {
            "status": STATUS,
            "source_wilson_sha256": source_hash,
            "f4_prior_summary_sha256":
                hashlib.sha256(args.f4_summary.read_bytes()).hexdigest(),
            "source_provenance": provenance,
            "source_effective_basis_checks": basis,
            "source_alpha_probe_build": alpha_build,
            "source_rg_probe_build": rg_build,
            "source_rg_probe_executable_sha256":
                hashlib.sha256(rg_exe.read_bytes()).hexdigest(),
            "source_running_parameters": inputs,
            "num_typeII_controls": len(rows),
            "typeII_masses_GeV": list(MASSES),
            "tanbeta_values": list(TANBETAS),
            "typeII_results": rows,
            "strict_C7eff_squared_LO_and_NLO_interference_extracted": True,
            "EOS_source_rate_strictly_expanded": False,
            "independent_NLO_TypeII_rate_validated": False,
            "NLO_operator_scheme_mapping_certified": False,
            "physical_full_NLO_BtoXsgamma_rate_calculated": False,
            "paper_ready_Zee_95CL_exclusions": False,
            "Zee_allowed_or_excluded": None,
        }
        ret = 0
    except Exception as exc:
        result = {"status": BLOCKED, "error": repr(exc),
                  "traceback": traceback.format_exc(),
                  "Zee_allowed_or_excluded": None}
        print("F4B_FAIL_CLOSED", repr(exc), file=sys.stderr, flush=True)
    finally:
        target = out / "summary.json"
        target.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        print("F4B_STATUS", result["status"], "F4B_SUMMARY", target,
              flush=True)
    return ret


if __name__ == "__main__":
    raise SystemExit(main())
