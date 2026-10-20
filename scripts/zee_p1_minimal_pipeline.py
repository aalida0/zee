#!/usr/bin/env python3
"""Small, conservative Priority-1 Zee scan interface.

This module deliberately does not pretend to implement missing NNLO Zee
matching, complete LFV, full heavy-scalar widths or hadronic production.
It verifies and normalizes externally computed provider records, implements
the exact-neutrino algebra option through the existing B2 backend, and
produces an auditable per-point constraint *coverage* ledger.

Provider JSON input can hold four independent records:
  bsgamma: {"status":"validated","BR":...,"sigma_theory":...,
            "scheme":...,"sm_control":...,"typeii_control":...}
  lfv:     {"status":"validated","observables":{...},
            "complete_amplitudes":true,"interference_validated":true}
  higgs:   {"status":"validated","higgstools":{...},
            "full_five_state_input":true}
  rates:   {"status":"validated","charged_widths":{...},
            "neutral_widths":{...},"production":{...}}
Even status='validated' is not trusted unless backed by an external
machine-readable source of validation, hashes and explicit test coverage.
This is a coverage evaluator, NOT a scientific likelihood or exclusion.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path
from typing import Any

REQUIRED=("bsgamma","lfv","higgs","rates","neutrino")
STATUS="P1_SCANNING_BACKEND_COVERAGE_NOT_EXPERIMENTAL_EXCLUSION"
# This list is a conservative source-supported statement about the repo,
# not a substitute for dedicated physics validation by an independent code.
KNOWN={
 "bsgamma":{"level":"legacy_inclusive_only",
             "source":"scripts/zee_gateF6_309_full_legacy_bsgamma.py",
             "missing":["modern_two_state_order_matched_inclusive_NNLO",
                        "BSM_uncertainty_covariance","matched_modern_controls"]},
 "lfv":{"level":"partial_one_loop_and_Barr_Zee",
        "source":"scripts/zee_lfv_backend.py",
        "missing":["all_diagrams_and_coherent_interference",
                   "mu_e_conversion_nuclear_inputs",
                   "independent_full_coverage_validation"]},
 "higgs":{"level":"h125_effective_HiggsSignals",
          "source":"scripts/zee_gateE6_309_charged_gamma_higgssignals.py",
          "missing":["five_state_HiggsBounds_input",
                     "all_heavy_Higgs_decay_channels",
                     "full_production_rate_validation"]},
 "rates":{"level":"partial_LO_charged_width_inventory",
          "source":"scripts/gate6_width_inventory.py",
          "missing":["all_charged_and_neutral_decay_modes",
                     "offshell_and_higher_order",
                     "validated_hadronic_production_rates"]},
 "neutrino":{"level":"exact_one_target_neutrino_mass_matrix",
             "source":"scripts/gateB2_zee_neutrino_family_scan.py",
             "missing":["oscillation_likelihood",
                        "mass_orderings_and_oscillation_nuisances",
                        "reoptimization_after_scalar_deformations"]},
}
def hashfile(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()
def clean_number(n):
 if isinstance(n,bool) or not isinstance(n,(int,float)) or not math.isfinite(n):
  raise ValueError("Invalid numerical prediction")
 return float(n)
def validated_provider(obj):
 # Provider status cannot turn into a physical exclusion without a
 # machine-readable input-evidence contract and a signed-off test matrix.
 if not isinstance(obj,dict):
  return False
 if obj.get("status")!="validated":
  return False
 evidence=obj.get("validation")
 if not isinstance(evidence,dict):
  return False
 return bool(evidence.get("independent_comparison_passed") is True and
             evidence.get("complete_model_basis") is True and
             isinstance(evidence.get("reference"),str) and
             evidence["reference"].strip() and
             isinstance(evidence.get("source_sha256"),str) and
             len(evidence["source_sha256"])==64 and
             all(c in "0123456789abcdef" for c in evidence["source_sha256"]))
def evaluate(point,providers=None):
 if not isinstance(point,dict) or not str(point.get("id","")).strip():
  raise ValueError("Point must contain a nonempty id")
 providers=providers or {}
 if not isinstance(providers,dict):
  raise ValueError("Expected providers object")
 extra=set(providers)-set(REQUIRED)
 if extra:raise ValueError("Unknown provider keys "+repr(sorted(extra)))
 record={"id":str(point["id"]),"status":STATUS,"components":{},
         "all_required_implemented_and_validated":False,
         "experimental_allowed_or_excluded":None}
 for key in REQUIRED:
  provider=providers.get(key)
  status="NOT_IMPLEMENTED_COMPLETE" if provider is None else "SUPPLIED_NOT_CERTIFIED"
  reason=list(KNOWN[key]["missing"])
  if provider is not None and not isinstance(provider,dict):
   raise ValueError(f"Provider {key} must be JSON object")
  # Even external 'validated' sources are NOT automatically scientifically
  # endorsed or allowed. They require manual independent per-model audit.
  if provider and validated_provider(provider):
   status="EXTERNAL_VALIDATION_CLAIM_REQUIRES_INDEPENDENT_REVIEW"
  record["components"][key]={
   "status":status,
   "existing_repo_level":KNOWN[key]["level"],
   "existing_repo_source":KNOWN[key]["source"],
   "unresolved_physics":reason,
   "provider_claim":provider.get("status") if provider else None,
  }
 return record
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--points",type=Path,required=True,
                 help="JSONL with one {id,...} per candidate")
 ap.add_argument("--providers",type=Path,help="JSON keyed by point id")
 ap.add_argument("--output",type=Path,required=True)
 args=ap.parse_args()
 store=json.loads(args.providers.read_text()) if args.providers else {}
 if not isinstance(store,dict):ap.error("Providers must be JSON object")
 if args.points.resolve()==args.output.resolve() or (
   args.providers is not None and args.providers.resolve()==args.output.resolve()):
  ap.error("Do not overwrite original input evidence")
 args.output.parent.mkdir(parents=True,exist_ok=True)
 ids=set();count=0
 # Streaming, temporary file + atomic replacement supports millions of rows.
 tmp=args.output.with_suffix(args.output.suffix+".partial")
 if tmp.exists():ap.error("Prior partial output exists; check prior run")
 try:
  with args.points.open() as inp,tmp.open("x") as out:
   for line in inp:
    if not line.strip():continue
    row=json.loads(line);name=str(row["id"])
    if name in ids:raise ValueError("Duplicate candidate "+name)
    ids.add(name)
    result=evaluate(row,store.get(name))
    out.write(json.dumps(result,allow_nan=False,sort_keys=True)+"\n")
    count+=1
  if count==0:raise ValueError("No candidates")
  if args.output.exists():ap.error("Output exists; refuse overwrite")
  tmp.replace(args.output)
 finally:
  if tmp.exists():tmp.unlink()
 print("STATUS",STATUS,"N",count,"MODEL_EXCLUSIONS",0)
 print("OUTPUT_SHA256",hashfile(args.output))
if __name__=="__main__":main()
