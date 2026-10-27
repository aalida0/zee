"""Exploratory Zee B->Xs gamma *linear* scan triage (not an exclusion).

Uses C1's source-locked Misiak 2026 Eq.(4), and distinguishes the
published SM and experimental errors from completely assumed NP model
uncertainty/correlation scenarios. No automatic accept/reject decisions,
no hard charged-scalar bounds, no '95% CL' significance claim.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from module5.hyperiso_patch_contract import make_contract, INPUT_FIELDS, unique_pairs
from module5.bsgamma_2026_linear_diagnostic import (
    run_contract, SM_CENTRAL, SM_SIGMA, EXPERIMENT_CENTRAL,
    EXPERIMENT_SIGMA, MATCHING_GEV, STATUS as C1_STATUS, SOURCE_URL
)

STATUS = "EXPLORATORY_LINEAR_SCAN_TRIAGE_NOT_A_FLAVOR_CONSTRAINT"


def real(x, name):
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise ValueError(f"{name}: finite real required")
    try:
        value = float(x)
    except OverflowError as exc:
        raise ValueError(f"{name}: finite real required") from exc
    if not math.isfinite(value):
        raise ValueError(f"{name}: finite real required")
    return value


def scenario_variance(rho, np_sigma):
    """Hypothetical variance of theory-exp difference under stated assumptions."""
    rho = real(rho, "rho_SM_exp")
    np_sigma = real(np_sigma, "assumed_NP_sigma_in_1e_minus4")
    if not -1 <= rho <= 1 or np_sigma < 0:
        raise ValueError("Correlation must be in [-1,1], NP sigma nonnegative")
    v = SM_SIGMA**2 + EXPERIMENT_SIGMA**2 - 2*rho*SM_SIGMA*EXPERIMENT_SIGMA + np_sigma*np_sigma
    if not math.isfinite(v) or v <= 0:
        raise ValueError("Nonpositive/nonfinite scenario variance")
    return v


def evaluate(batch):
    if not isinstance(batch, dict) or set(batch) != {"schema_version", "points", "assumed_uncertainty_scenarios"} or batch["schema_version"] != "1.0.0":
        raise ValueError("Unexpected scan-triage schema")
    points = batch["points"]
    scenarios = batch["assumed_uncertainty_scenarios"]
    if not isinstance(points, list) or not points or len(points)>1000:
        raise ValueError("Require 1..1000 points")
    if not isinstance(scenarios, list) or not scenarios or len(scenarios)>16:
        raise ValueError("Require 1..16 explicitly assumed scenarios")
    scenarios_out = []
    names = set()
    for s in scenarios:
        if not isinstance(s, dict) or set(s) != {"name","rho_SM_exp","assumed_NP_sigma_in_1e_minus4"}:
            raise ValueError("Unexpected scenario keys")
        n = s["name"]
        if not isinstance(n, str) or not (1<=len(n)<=80) or n in names:
            raise ValueError("Invalid/duplicate scenario name")
        names.add(n)
        rho = real(s["rho_SM_exp"], "rho_SM_exp")
        np_sigma = real(s["assumed_NP_sigma_in_1e_minus4"], "assumed_NP_sigma_in_1e_minus4")
        var = scenario_variance(rho, np_sigma)
        scenarios_out.append({"name":n,"assumed_rho_SM_exp":rho,
            "assumed_NP_sigma_in_1e_minus4":np_sigma,
            "hypothetical_sigma_in_1e_minus4":math.sqrt(var),
            "assumptions":"SM/experiment bivariate Gaussian with stated rho; NP-model error independent Gaussian with stated sigma, NOT experimentally/theoretically calibrated"})
    output = []
    point_ids=set()
    physics_points=set()
    for p in points:
        if not isinstance(p, dict) or set(p) != INPUT_FIELDS | {"point_id"}:
            raise ValueError("Require point_id and exactly six explicit physics inputs")
        label=p["point_id"]
        if not isinstance(label, str) or not (1<=len(label)<=80) or label in point_ids:
            raise ValueError("Missing/duplicate point_id")
        point_ids.add(label)
        inputs={k:real(p[k], k) for k in INPUT_FIELDS}
        point_key=tuple(inputs[k] for k in sorted(INPUT_FIELDS))
        if point_key in physics_points:
            raise ValueError("Duplicate physics point")
        physics_points.add(point_key)
        if inputs["matching_scale_GeV"]!=MATCHING_GEV:
            raise ValueError("Misiak Eq4 requires qmatch=160 GeV")
        try:
            c=make_contract(inputs)
            e=run_contract(c)
        except (OverflowError, ZeroDivisionError) as exc:
            raise ValueError("Physics inputs exceed numerical diagnostic domain") from exc
        if e["status"]!=C1_STATUS or e["external_convention_status"]!="EXTERNAL_CONVENTION_PASS":
            raise ValueError("C1 external operator convention gate not established")
        value=real(e["linearized"]["conditional_B_times_1e4"],"linearized BR diagnostic")
        difference=value-EXPERIMENT_CENTRAL
        data=[]
        for scenario in scenarios_out:
            sigma=scenario["hypothetical_sigma_in_1e_minus4"]
            pull=difference/sigma
            if not math.isfinite(pull):
                raise ValueError("Nonfinite pull")
            data.append({"scenario":scenario["name"],"hypothetical_signed_pull":pull,
                         "hypothetical_abs_pull":abs(pull),
                         "not_an_exclusion":True})
        output.append({
            "point_id":label,
            "C1_status":e["status"],
            "external_convention_status":e["external_convention_status"],
            "matching_input":c["input"],
            "delta_C7":e["shift_input"]["DeltaC7"],
            "delta_C8":e["shift_input"]["DeltaC8"],
            "linearized_value_in_1e_minus4":value,
            "linearized_minus_experiment_in_1e_minus4":difference,
            "np_shift_in_1e_minus4":e["linearized"]["delta_B_times_1e4"],
            "hypothetical_scenario_comparisons":data,
            "nonlinear_error":"UNKNOWN",
            "NP_NLO_rate_and_theory_error":"UNKNOWN",
            "physical_BR":None,
            "flavor_classification":"UNCLASSIFIED",
            "global_zee_acceptance":None
        })
    return {
        "schema_version":"1.0.0","status":STATUS,
        "linear_formula_source":"Misiak et al. arXiv:2608.29863v1 Eq.(4), mu0=160 GeV, Egamma>1.6 GeV",
        "linear_formula_source_url":SOURCE_URL,
        "C1_status":C1_STATUS,
        "implementation_sha256":{
            name:hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ("bsgamma_2026_linear_diagnostic.py", "bsgamma_lo.py",
                         "hyperiso_patch_contract.py", "BSGAMMA_2026_CONVENTION.md")},
        "operator_convention_scope":"C1 real top-only LO, ms=0, BMU source bridge",
        "SM_reference_in_1e_minus4":{"central":SM_CENTRAL,"reported_sigma":SM_SIGMA},
        "experiment_in_1e_minus4":{"central":EXPERIMENT_CENTRAL,"reported_sigma":EXPERIMENT_SIGMA},
        "assumed_scenarios":scenarios_out,"points":output,
        "filter_ready":False,"physical_exclusions":None,
        "2026_LINEARIZED_FLAVOR_FILTER_READY":False,
        "FULL_ZEE_ALLOWED":"NOT_EVALUATED",
        "limitations":[
            "All pulls are hypothetical sensitivity scenarios, NOT exclusion confidence levels.",
            "Uncertainty/covariance assumptions are user-defined, not a validated Zee NP error budget.",
            "No quadratic NP response, C4 NLO rate term, NP NLO/NNLO uncertainties or validated applicability domain.",
            "No complete Zee flavor/combined viability is inferred.",
            "The one-charged-Higgs Type-II 670 GeV exclusion is not applied to individual Zee masses."
        ]
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",required=True,type=Path)
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    raw=args.input.read_bytes()
    inp=json.loads(raw,object_pairs_hook=unique_pairs,
                   parse_constant=lambda x: (_ for _ in ()).throw(ValueError("Nonfinite JSON constant "+x)))
    result=evaluate(inp)
    result["source_batch_sha256"]=hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    target=args.output.with_name(args.output.name+".tmp")
    target.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    target.replace(args.output)
    print(STATUS)

if __name__=="__main__":main()
