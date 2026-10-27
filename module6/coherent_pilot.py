"""One *coherent* Zee candidate: scalar + neutrino/LFV subset + 2026 flavor.

Not an allowed/excluded decision. Module4 two-loop LFV and full flavor
constraints are NOT evaluated by this pilot. The scalar/neutrino input is
the *same* complete frozen module3 record, never independent toy points.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from module2.interface import strict_loads, scalar_input, canonical_hash
from module3.interface import validate as validate3, evaluate as lfv_evaluate
from module1.scalar_constraints import evaluate as scalar_evaluate
from module5.hyperiso_patch_contract import make_contract
from module5.bsgamma_2026_linear_diagnostic import run_contract

STATUS="COHERENT_ZEE_CANDIDATE_DIAGNOSTIC_ONLY"
LHA_SOURCE_SHA256="984391031656a5f4f86ee71f5b60e7d0cb2b1b80edabd9ff6ba912da3ba39374"
SOURCE_TOP_MS_160=163.96892236746697

def pilot(module3_input, mt_MSbar_160, reference_lha_sha256):
    if not isinstance(module3_input,dict):
        raise ValueError("Module3 record required")
    if not isinstance(mt_MSbar_160,(float,int)) or isinstance(mt_MSbar_160,bool) or not math.isfinite(mt_MSbar_160):
        raise ValueError("Finite explicit reference-MSbar top mass required")
    if reference_lha_sha256!=LHA_SOURCE_SHA256 or abs(mt_MSbar_160-SOURCE_TOP_MS_160)>2e-12:
        raise ValueError("Frozen HyperIso reference-LHA mass and SHA required for pilot")
    validate3(module3_input,"input.schema.json")
    m2=module3_input["module2_input"]
    if m2["benchmark_id"]!=module3_input["benchmark_id"]:
        raise ValueError("Neutrino and LFV benchmark IDs differ")
    wrapper=m2["scalar"]
    if wrapper["kind"]!="module1_input":
        raise ValueError("Pilot accepts a full Module1 input bound by canonical SHA256")
    p,sp=scalar_input(wrapper)  # independently verifies pinned record hash
    scalar=scalar_evaluate(wrapper["record"])
    lfv=lfv_evaluate(module3_input)  # executes frozen neutrino + Module3 LFV
    if scalar["benchmark_id"]!=lfv["benchmark_id"] or scalar["benchmark_id"]!=module3_input["benchmark_id"]:
        raise ValueError("Scalar/LFV benchmark mismatch")
    if scalar["global_zee_acceptance"] is not None or lfv["global_zee_acceptance"] is not None or lfv["COMPLETE_LFV"] is not False:
        raise ValueError("Unexpectedly declared globally accepted or LFV-complete")
    fc={
      "mH1_GeV":p["mH1"],"mH2_GeV":p["mH2"],
      "beta_rad":p["beta"],"gamma_rad":p["gamma"],
      "mt_MSbar_GeV":float(mt_MSbar_160),"matching_scale_GeV":160.}
    flavor=run_contract(make_contract(fc))
    if flavor["external_convention_status"]!="EXTERNAL_CONVENTION_PASS" or flavor["experiment_comparison"]!="NOT_EVALUATED":
        raise ValueError("Unexpected physical flavor classification")
    radiation={}
    for channel in ("mu_to_e_gamma","tau_to_e_gamma","tau_to_mu_gamma"):
        row=lfv["observables"][channel]
        if row["physical_status"]!="SCALAR_ONE_LOOP_APPROXIMATION" or row["experimental_comparison"]!="NOT_EVALUATED":
            raise ValueError("Unexpected LFV scope")
        radiation[channel]={"subset_partial_BR":row["partial_BR"],
                            "physical_status":row["physical_status"],
                            "experimental_comparison":row["experimental_comparison"]}
    return {
      "schema_version":"1.0.0","status":STATUS,"benchmark_id":module3_input["benchmark_id"],
      "ordering":m2["ordering"],
      "scalar":{"status":scalar["status"],
                "gates":{k:{"assessment":v["assessment"],"status":v.get("status")}
                         for k,v in scalar["gates"].items()},
                "global_vacuum_certification":"NOT_ESTABLISHED",
                "output_sha256":canonical_hash(scalar)},
      "neutrino_lfv":{"status":lfv["status"],"gates":lfv["gates"],
                      "radiative_subset_only":radiation,
                      "COMPLETE_LFV":False,
                      "experimental_LFV_comparison":"NOT_EVALUATED",
                      "module4_Barr_Zee_and_W_completion":"NOT_EVALUATED",
                      "output_sha256":canonical_hash(lfv)},
      "bsgamma":{"status":flavor["status"],
                 "operator_scope":flavor["convention_scope"],
                 "delta_C7":flavor["shift_input"]["DeltaC7"],
                 "delta_C8":flavor["shift_input"]["DeltaC8"],
                 "linearized_value_in_1e_minus4":flavor["linearized"]["conditional_B_times_1e4"],
                 "nonlinear_reliability":"UNKNOWN",
                 "experiment_comparison":"NOT_EVALUATED",
                 "flavor_classification":"UNCLASSIFIED"},
      "provenance":{"module3_input_sha256":canonical_hash(module3_input),
                    "bound_scalar_sha256":wrapper["sha256"],
                    "scalar_provenance":sp,
                    "mt_MSbar_160_GeV":float(mt_MSbar_160),
                    "hyperiso_reference_LHA_sha256":reference_lha_sha256},
      "constraints_complete":False,
      "global_zee_acceptance":None,
      "limitations":[
         "Physical scalar stability/vacuum status is never globally certified by stochastic witnesses.",
         "Module3 scalar LFV is a restricted one-loop subset; Module4 is not evaluated.",
         "Oscillation likelihood data provenance is inherited; no new global NuFIT likelihood.",
         "Flavor Eq4 is an exploratory LO-linear diagnostic, not a validated classification.",
         "No experimental exclusions, RG closure, collider likelihood or global viability."
      ]}

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--module3-input",type=Path,required=True)
    a.add_argument("--mt-MSbar-160",type=float,required=True)
    a.add_argument("--reference-lha-sha256",required=True)
    a.add_argument("--output",type=Path,required=True)
    args=a.parse_args()
    raw=args.module3_input.read_bytes()
    rec=strict_loads(raw.decode())
    result=pilot(rec,args.mt_MSbar_160,args.reference_lha_sha256)
    result["input_bytes_sha256"]=hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    tmp=args.output.with_name(args.output.name+".tmp")
    tmp.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    tmp.replace(args.output)
    print(STATUS)

if __name__=="__main__":main()
