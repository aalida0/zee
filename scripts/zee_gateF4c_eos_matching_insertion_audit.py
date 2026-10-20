#!/usr/bin/env python3
"""F4c conditional EOS quadratic-in-NLO-matching-insertion audit.

A fixed EOS NLO *kernel*, evaluated as a function of the high-scale-NLO
matching shift propagated to low-energy Wilson coefficients, is quadratic
in that shift. This is NOT the expansion of the inclusive rate in alpha_s.
All source-level/physical NLO and all Zee exclusion gates remain blocked.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import traceback

STATUS = "F4C_EOS_QUADRATIC_MATCHING_INSERTION_CHECK_NOT_STRICT_NLO"
BLOCKED = "F4C_BLOCKED_NOT_STRICT_NLO"
MASSES = (300., 580., 670., 1000.)
TANBETAS = (5.6, 50.)
COHORT = {(m, t) for m in MASSES for t in TANBETAS}


def finite(v, label):
    z = float(v)
    if not math.isfinite(z):
        raise ValueError("Nonfinite " + label)
    return z


def checked_vector(vec, name):
    if set(vec) != set(range(1, 9)):
        raise ValueError(name + " requires coefficients 1..8")
    return {n: finite(vec[n], f"{name} C{n}") for n in range(1, 9)}


def add(v, dv, t):
    v = checked_vector(v, "base")
    dv = checked_vector(dv, "direction")
    t = finite(t, "insertion parameter")
    return {n: v[n] + t * dv[n] for n in range(1, 9)}


def quadratic_path(rate, baseline, shift):
    """Exact conditional polynomial in the Wilson *insertion* parameter.

    Pass requires EOS response R(C+t*h) to be exactly quadratic in t
    within numerical error; tests +-1, +-0.5 and +2. Not strict in alpha_s.
    """
    baseline = checked_vector(baseline, "baseline")
    shift = checked_vector(shift, "shift")
    rs = {k: finite(rate(add(baseline, shift, k)), f"rate t={k}")
          for k in (0., 1., -1., .5, -.5, 2.)}
    central = rs[0.]
    lin = (rs[1.] - rs[-1.]) / 2.
    quad = (rs[1.] + rs[-1.]) / 2. - central
    residuals = {k: rs[k] - (central + lin*k + quad*k*k)
                 for k in (.5, -.5, 2.)}
    # Rates are ~1e-4 and numerical error is well below this absolute
    # diagnostic threshold. A false PASS cannot certify a QCD order.
    tolerance = 5e-13
    if any(abs(v) > tolerance for v in residuals.values()):
        raise ValueError("EOS response not quadratic in inserted WCs: " +
                         repr(residuals))
    return {
        "rate_at_baseline": central,
        "rate_at_plus_full_matching_shift": rs[1.],
        "rate_at_minus_matching_shift": rs[-1.],
        "matching_shift_linear_response": lin,
        "matching_shift_quadratic_response": quad,
        "max_abs_polynomial_closure": max(abs(x) for x in residuals.values()),
        "full_shift_total_response": rs[1.] - central,
        "quadratic_only_in_matching_insertion_NOT_alpha_s_order": True,
    }


def validate_prior(f4_path, f4b_path, hepfit_path):
    f4 = json.loads(f4_path.read_text())
    fb = json.loads(f4b_path.read_text())
    hp = json.loads(hepfit_path.read_text())
    if (f4.get("status") != "NOT_YET_VALIDATED" or
        fb.get("status") != "F4B_ORDER_RESOLVED_DIPOLE_PROJECTOR_NOT_FULL_NLO_RATE" or
        hp.get("status") !=
        "F4B_INDEPENDENT_MATCHING_LO_NLO_8_NUMERICALLY_CONSISTENT_NOT_RATE"):
        raise ValueError("F4/F4b chain does not have required diagnostic status")
    if hp.get("prior_F4b_summary_sha256") != hashlib.sha256(
            f4b_path.read_bytes()).hexdigest():
        raise ValueError("Independent HEPfit does not refer to this F4b report")
    if fb.get("f4_prior_summary_sha256") != hashlib.sha256(
            f4_path.read_bytes()).hexdigest():
        raise ValueError("F4b does not refer to this F4 report")
    if hp.get("tested_rows") != 40 or hp.get("matching_disagreements") != 0:
        raise ValueError("F4b independent HEPfit 40-row matching audit incomplete")
    if (f4.get("a1m_sha256") != fb.get("source_wilson_sha256")
        or fb.get("num_typeII_controls") != 8
        or fb.get("EOS_source_rate_strictly_expanded") is not False):
        raise ValueError("F4/F4b source identity or status changed")
    def cohort(rows):
        if not isinstance(rows, list) or len(rows) != 8:
            raise ValueError("Incorrect F4/F4b cohort length")
        keys = [(finite(x["mass_GeV"], "mass"),
                 finite(x["tanbeta"], "tanbeta")) for x in rows]
        if set(keys) != COHORT or len(keys) != len(set(keys)):
            raise ValueError("Unexpected/duplicate Type-II control")
        return {key:row for key,row in zip(keys,rows)}
    old = cohort(f4["controls"])
    new = cohort(fb["typeII_results"])
    return f4, fb, hp, old, new


def run_checks(pair, rg_exe, alpha_source, f4rows, f4brows):
    from zee_gateF3_fullNLO_source_RG_27 import probe, net_low
    from zee_gateF4_typeii_basis_interface_pilot import raw_for_eos
    if not .15 < alpha_source < .35:
        raise ValueError("Unphysical source alpha_s low")
    a = alpha_source / (4. * math.pi)
    results = []
    pair.prepare()
    for tanb in TANBETAS:
        for mass in MASSES:
            probe_rows = probe(rg_exe, mass, mass, tanb, 0.)
            lo = checked_vector(net_low(probe_rows, 0, a), "LO matching")
            dip = checked_vector(net_low(probe_rows, 1, a), "dipole NLO matching")
            full = checked_vector(net_low(probe_rows, 2, a), "full NLO matching")
            hd = {n: dip[n] - lo[n] for n in lo}
            hq = {n: full[n] - dip[n] for n in lo}
            ht = {n: full[n] - lo[n] for n in lo}
            def rate(effective):
                return pair.eos_rate(raw_for_eos(effective))
            total = quadratic_path(rate, lo, ht)
            part_d = quadratic_path(rate, lo, hd)
            part_q = quadratic_path(rate, lo, hq)
            linear_sum = (part_d["matching_shift_linear_response"] +
                          part_q["matching_shift_linear_response"])
            if abs(total["matching_shift_linear_response"]-linear_sum) > 5e-13:
                raise ArithmeticError("Linear NLO matching sensitivity non-additive")
            mixed = (total["matching_shift_quadratic_response"] -
                     part_d["matching_shift_quadratic_response"] -
                     part_q["matching_shift_quadratic_response"])
            match = f4brows[mass,tanb]
            if (abs(match["C7eff_NP_NLO_Coeff_full_matching"]
                    - probe_rows[2,7]["low_NLO"]) > 5e-11
                or abs(match["C7eff_NP_LO"] - probe_rows[0,7]["low_LO"]) > 5e-11):
                raise ValueError("F4b projector C7 output drifted")
            f4prev = f4rows[mass,tanb]
            expected = finite(
                f4prev["eos_BR_full_source_NLO_matching_CONDITIONAL"],
                "F4 conditional EOS rate")
            # Source-alpha matching vector differs from the F4 flavio-alpha
            # vector, so report the rate difference, NOT require equality.
            results.append({
                "mass_GeV": mass, "tanbeta":tanb,
                "source_alpha_s_mub":alpha_source,
                "source_low_scale_a":a,
                "EOS_alpha_s_from_its_own_WET_model_not_synchronized":True,
                "EOS_rate_LO_high_matching_NLO_RGE_conditional":
                    total["rate_at_baseline"],
                "EOS_rate_full_source_NLO_matching_conditional":
                    total["rate_at_plus_full_matching_shift"],
                "EOS_rate_NLO_matching_linear_insertion":
                    total["matching_shift_linear_response"],
                "EOS_rate_NLO_matching_quadratic_insertion":
                    total["matching_shift_quadratic_response"],
                "EOS_rate_NLO_matching_linear_dipoles":
                    part_d["matching_shift_linear_response"],
                "EOS_rate_NLO_matching_linear_fourquark":
                    part_q["matching_shift_linear_response"],
                "EOS_rate_NLO_matching_quadratic_dipoles":
                    part_d["matching_shift_quadratic_response"],
                "EOS_rate_NLO_matching_quadratic_fourquark":
                    part_q["matching_shift_quadratic_response"],
                "EOS_rate_NLO_matching_quadratic_cross":
                    mixed,
                "EOS_rate_matching_insertion_polynomial_max_residual":
                    max(total["max_abs_polynomial_closure"],
                        part_d["max_abs_polynomial_closure"],
                        part_q["max_abs_polynomial_closure"]),
                "F4_conditional_full_rate_flavio_alpha_s_reference":expected,
                "rate_shift_vs_F4_due_in_part_to_different_alpha_s":
                    total["rate_at_plus_full_matching_shift"]-expected,
                "Q7eff_dipole_only_NLO_matching_projector_NOT_rate":
                    match["Q7eff_NP_NLO_matching_total"],
                "source_scheme_certified":False,
                "strict_full_NLO_alpha_s_expansion_complete":False,
                "B_to_Xsgamma_exclusion_validated":False,
            })
            print("F4C_TYPEII",mass,tanb,
                  "EOS_BR_conditional",
                  f"{total['rate_at_plus_full_matching_shift']:.12g}",
                  "linear",f"{total['matching_shift_linear_response']:.8g}",
                  "quadratic",f"{total['matching_shift_quadratic_response']:.8g}",
                  "NOT_STRICT_NLO",flush=True)
    if len(results) != 8:
        raise ValueError("Incomplete F4c Type-II controls")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("f4-summary", "f4b-summary", "f4b-hepfit-summary",
                "output-dir"):
        parser.add_argument("--"+arg, required=True, type=Path)
    a=parser.parse_args()
    cwd=Path.cwd().resolve()
    out=a.output_dir.resolve()
    if not cwd.is_relative_to(Path("/home")) or not out.is_relative_to(cwd/"work"):
        parser.error("F4c runs/writes only in the /home repo work tree")
    if out.exists() and any(out.iterdir()):
        parser.error("Refuse overwriting F4c result")
    out.mkdir(parents=True,exist_ok=True)
    report={"status":BLOCKED,"Zee_allowed_or_excluded":None}
    exitcode=1
    try:
        from zee_gateF2_eos_flavio_nlo_27_validation import RatePair
        f4, fb, hp, f4rows, f4brows = validate_prior(
            a.f4_summary,a.f4b_summary,a.f4b_hepfit_summary)
        path = Path(fb["source_rg_probe_build"]["compiler_command"][-1]).resolve()
        if not path.is_file() or not path.is_relative_to(cwd/"work"):
            raise ValueError("Cannot locate source-pinned F4b RG executable")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != fb.get("source_rg_probe_executable_sha256"):
            raise ValueError("F4b RG binary sha256 has changed")
        sourcealpha = finite(fb["source_running_parameters"]["alphas_mub"],
                             "SuperIso source alpha_s(mub)")
        pair=RatePair()
        rows=run_checks(pair,path,sourcealpha,f4rows,f4brows)
        with (out/"F4c_8_TypeII_quadratic_EOS_matching_insertion.csv").open(
                "w",newline="") as handle:
            writer=csv.DictWriter(handle,fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        report={
            "status":STATUS,
            "num_typeII_controls":len(rows),
            "f4b_summary_sha256":hashlib.sha256(a.f4b_summary.read_bytes()).hexdigest(),
            "hepfit_summary_sha256":hashlib.sha256(
                a.f4b_hepfit_summary.read_bytes()).hexdigest(),
            "RG_probe_binary_sha256":actual,
            "eos_version":pair.eos_version,
            "flavio_version":pair.flavio_version,
            "EOS_v1_1_source_git_blob_checked_in_prior_audit":
                "3bbb034b920709503b767fb372f35338ae427877",
            "EOS_installed_binary_link_to_upstream_source_certified":False,
            "quadratic_response_at_fixed_EOS_kernel_verified":True,
            "full_rate_strict_Oalpha_s_expansion_done":False,
            "NLO_operator_scheme_certified":False,
            "independent_NLO_inclusive_rate_certified":False,
            "Zee_allowed_or_excluded":None,
            "rows":rows,
        }
        exitcode=0
    except Exception as exc:
        report={"status":BLOCKED,"error":repr(exc),
                "traceback":traceback.format_exc(),
                "Zee_allowed_or_excluded":None}
        print("F4C_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
    finally:
        dest=out/"summary.json"
        dest.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
        print("F4C_STATUS",report["status"],"F4C_SUMMARY",dest,flush=True)
    return exitcode


if __name__=="__main__":
    raise SystemExit(main())
