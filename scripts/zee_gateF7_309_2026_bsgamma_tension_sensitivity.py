#!/usr/bin/env python3
"""F7: source-locked 309-point LEGACY-to-modern B->Xs gamma tension sensitivity.

Original F6 data: physically computed *legacy* full inclusive two-charged
SuperIso v5 BR. External 2026 reference: Misiak et al arXiv:2608.29863,
SM (3.54 +/- 0.14)e-4, experiment (3.49 +/- 0.19)e-4 (Egamma>1.6GeV).

IMPORTANT: adding the legacy NP-minus-legacy-SM shift to 2026 SM is NOT
a perturbatively matched modern prediction. The Gaussian significance
below is a transparent WHAT-IF sensitivity diagnostic, NOT a real
likelihood, model exclusion, or an approximation certified for publication
as a physical B->Xs gamma prediction. The unknown model-dependent NP
theory covariance may be substantial. No cut labels ALLOWED/EXCLUDED.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics,sys,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
STATUS="F7_309_LEGACY_NP_TO_2026_SM_GAUSSIAN_SENSITIVITY_ONLY_NOT_EXCLUSION"
ERROR_STATUS="F7_FAIL_CLOSED_NO_MODERN_BSGAMMA_RATE_OR_EXCLUSION"
F6_FILE="F6_309_legacy_two_state_BtoXsgamma_NOT_2026_EXCLUSION.jsonl"
REFERENCE={
 "source":"Misiak et al arXiv:2608.29863 (30 Aug 2026), first-preprint reference",
 "Egamma_min_GeV":1.6,
 "modern_SM_central":3.54e-4,
 "modern_SM_sigma":.14e-4,
 "experimental_central":3.49e-4,
 "experimental_sigma":.19e-4,
 "assumptions":"Illustrative independent Gaussian combination for fixed NP shifts; not a modern BSM likelihood.",
 "Gaussian_two_sided_reference_z":1.96,
}
# Not fitted, not confidence-level nuisance profiling. Two independent
# perturbative mismatch axes which must NEVER be labeled physical.
NP_SCALE_SCENARIOS=(0.,.5,.75,.8,.85,.9,1.,1.1,1.2)
SM_SIGMA_FACTORS=(1.,1.25,1.5,2.)
PRIORITY=("B4_0004143","B4_0003582","B4_0003854",
          "B4_0004380","B4_0002315","B4_0017640")

def digest(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()

def load(path):return json.loads(Path(path).read_text())
def writejson(path,value):
 Path(path).write_text(json.dumps(value,sort_keys=True,indent=2,
                             allow_nan=False)+"\n")

def finite(v,label):
 z=float(v)
 if not math.isfinite(z):raise ValueError("F7 nonfinite "+label)
 return z

def near(a,b,label,rtol=2e-10,atol=5e-13):
 if not math.isclose(finite(a,label),finite(b,label),
                     rel_tol=rtol,abs_tol=atol):
  raise ValueError("F7 crosscheck failed: "+label)

def load_f6(path):
 """Fail-closed full provenance and 309-entry previous-AF-result closure."""
 summary=load(path/"summary.json")
 manifest=load(path/"manifest.json")
 from zee_gateF6_309_full_legacy_bsgamma import STATUS as PREV
 if (summary.get("status")!=PREV or manifest.get("status")!=PREV or
     summary.get("original_source_points")!=309 or
     summary.get("A1U_historical_full_inclusive_kernel_reproduced") is not True or
     summary.get("A1U_SM_TypeII_endpoints_and_equal_masses_validated") is not True or
     summary.get("A1U_source_context_matching_interposition_checked_every_point") is not True or
     summary.get("full_legacy_SuperIso_inclusive_BR_309_computed") is not True or
     summary.get("modern_2026_matching_and_theory_uncertainties_calibrated") is not False or
     summary.get("experimental_95CL_likelihood_validated") is not False or
     summary.get("Zee_allowed_or_excluded") is not None or
     manifest.get("source")!=summary.get("source_provenance") or
     manifest.get("summary_SHA256")!=digest(path/"summary.json") or
     summary.get("source_provenance",{}).get("new_F6_script_SHA256")!=
       digest(ROOT/"scripts/zee_gateF6_309_full_legacy_bsgamma.py")):
  raise ValueError("F7 F6 source-status/manifest/physics hash contract failed")
 for name,expected in summary.get("output_hashes",{}).items():
  if digest(path/name)!=expected:
   raise ValueError("F7 F6 immutable output SHA mismatch "+name)
 if set(summary.get("output_hashes",{}))!={
    F6_FILE,"F6_309_legacy_BR_HS_cascade_NO_CL.csv",
    "F6_E7_Pareto_legacy_BR_NO_CL.csv"}:
  raise ValueError("F7 F6 output SHA inventory incomplete")
 sm=finite(summary["legacy_SM_BR"],"legacy SM")
 if not (.0003 < sm < .0004):
  raise ValueError("F7 unexpected prior-vendor SM normalization")
 allrows={}
 with (path/F6_FILE).open() as f:
  for ln in f:
   o=json.loads(ln);name=o["candidate_id"]
   if (name in allrows or o.get("full_Zee_allowed_excluded") is not None or
       o.get("modern_2026_NNLO_and_likelihood_validated") is not False):
    raise ValueError("F7 false physical-CL assertion or duplicate case")
   b=finite(o["BR_BtoXsgamma_legacy_SuperIso_two_state"],"legacy full BR")
   d=finite(o["legacy_BR_NP_minus_SM"],"legacy NP shift")
   near(o["BR_BtoXsgamma_legacy_SuperIso_SM_reference"],sm,
        name+" immutable SM")
   near(b-sm,d,name+" full BR-minus-SM closure",atol=1e-12)
   near(b/sm,o["legacy_BR_ratio_to_same_legacy_SM"],
        name+" BSM/SM ratio closure")
   near(o["A1U_source_diagnostics"]["full_legacy_Zee_BR"],b,
        name+" original A1U driver")
   if not(0<b<.01):
    raise ValueError("F7 invalid physical legacy branching-ratio range")
   allrows[name]=o
 if len(allrows)!=309:raise ValueError("F7 complete original 309 source cohort required")
 br=sorted(z["BR_BtoXsgamma_legacy_SuperIso_two_state"] for z in allrows.values())
 ds=sorted(z["legacy_BR_NP_minus_SM"] for z in allrows.values())
 for group,rep,label in (
     (br,summary["legacy_BR_min_median_max"],"legacy BR"),
     (ds,summary["legacy_NP_minus_SM_min_median_max"],"NP shift")):
  for v,expected in zip((group[0],group[154],group[-1]),rep):
   near(v,expected,"F6 "+label+" min median max")
 if sum(d>0 for d in ds)!=summary["legacy_BtoXsGamma_above_same_legacy_SM"]:
  raise ValueError("F6 positive NP population statistic invalid")
 with (path/"F6_309_legacy_BR_HS_cascade_NO_CL.csv").open(newline="") as f:
  csvrows=list(csv.DictReader(f))
 if len(csvrows)!=309 or {z["candidate_id"] for z in csvrows}!=set(allrows):
  raise ValueError("F6 legacy CSV fails independent cohort check")
 for z in csvrows:
  near(z["BR_BtoXsgamma_legacy_SuperIso_two_state"],
       allrows[z["candidate_id"]]["BR_BtoXsgamma_legacy_SuperIso_two_state"],
       z["candidate_id"]+" CSV/JSONL BR")
 if set(summary.get("priority_six",{}))!=set(PRIORITY):
  raise ValueError("F7 did not find exactly six E7 Pareto candidates")
 return allrows,{
  "F6_summary_SHA256":digest(path/"summary.json"),
  "F6_manifest_SHA256":digest(path/"manifest.json"),
  "F6_rows_SHA256":digest(path/F6_FILE),
  "F6_unmodified_physics_script_SHA256":
    digest(ROOT/"scripts/zee_gateF6_309_full_legacy_bsgamma.py"),
  "F6_captured_source_provenance":summary["source_provenance"],
 }

def gaussian_what_if(delta,k=1.,s=1.,reference=REFERENCE):
 """Only normalized sensitivity: NEVER model-dependent 2026 rate."""
 k=finite(k,"NP hypothetical scale")
 s=finite(s,"SM sigma inflation")
 if k<0 or s<=0:raise ValueError("F7 invalid hypothetical sensitivity factor")
 pred=reference["modern_SM_central"]+k*finite(delta,"legacy NP shift")
 sigma=math.hypot(reference["experimental_sigma"],
                   s*reference["modern_SM_sigma"])
 pull=(pred-reference["experimental_central"])/sigma
 if sigma<=0:raise ValueError("F7 Gaussian diagnostic uncertainty vanishes")
 return {
   "HYPOTHETICAL_2026SM_PLUS_scaled_legacy_delta_NOT_a_model_BR":pred,
   "Gaussian_what_if_pull_NOT_model_likelihood":pull,
   "absolute_Gaussian_what_if_pull":abs(pull),
   "experimental_plus_SM_uncertainty_illustrative":sigma,
   "hypothetical_NP_scale":k,
   "hypothetical_SM_error_scale":s,
   "within_illustrative_two_sided_1p96_band_NOT_allowed_or_excluded":
       abs(pull)<=reference["Gaussian_two_sided_reference_z"],
 }

def model_row(src,reference=REFERENCE):
 d=finite(src["legacy_BR_NP_minus_SM"],"NP shift")
 nominal=gaussian_what_if(d,reference=reference)
 z=reference["Gaussian_two_sided_reference_z"]
 sigma=nominal["experimental_plus_SM_uncertainty_illustrative"]
 # Upper allowed *positive* NP shift under the Gaussian *diagnostic*
 # (one-sided high-branch only); not an exclusion bound.
 dmax=reference["experimental_central"]+z*sigma-reference["modern_SM_central"]
 kmax=dmax/d if d>0 else None
 # Shift required in legacy NP matching to fall at upper 1.96 band edge
 suppress_fraction=max(0.,1.-kmax) if kmax is not None else None
 target=reference["modern_SM_central"]+d-reference["experimental_central"]
 req_sm_unc=math.sqrt(max(0.,(target/z)**2-
                                    reference["experimental_sigma"]**2))
 extra_sigma=math.sqrt(max(0.,req_sm_unc**2-
                                reference["modern_SM_sigma"]**2))
 return {
  "candidate_id":src["candidate_id"],
  "E6_HiggsSignals_delta_chi2_NOT_CL":
     finite(src["HiggsSignals_E6_delta_chi2_NOT_CL"],"E6"),
  "E7_included_cascade_proxy_NOT_physical_rate":
     finite(src["E7_included_cascade_proxy_NOT_physical_rate"],"E7"),
  "mH1_GeV":finite(src["mH1_GeV"],"mH1"),
  "mH2_GeV":finite(src["mH2_GeV"],"mH2"),
  "F5_C7eff_squared_dipole_NOT_rate":
     finite(src["F5_strict_C7eff_projector_not_rate"],"F5"),
  "F6_legacy_superiso_full_inclusive_BR":finite(
     src["BR_BtoXsgamma_legacy_SuperIso_two_state"],"F6"),
  "F6_legacy_NP_shift":d,
  "illustrative_2026SM_plus_legacy_shift_NOT_modern_prediction":
      nominal["HYPOTHETICAL_2026SM_PLUS_scaled_legacy_delta_NOT_a_model_BR"],
  "illustrative_Gaussian_pull_NOT_an_exclusion":
      nominal["Gaussian_what_if_pull_NOT_model_likelihood"],
  "illustrative_scale_to_1p96_upper_edge":
      kmax,
  "illustrative_NP_shift_suppression_fraction_to_1p96":
      suppress_fraction,
  "illustrative_extra_SM_uncertainty_quadrature_for_1p96":
      extra_sigma,
  "no_validated_model_BtoXsgamma_2026_rate":True,
  "experimentally_allowed_or_excluded":None,
 }

def scenario_counts(models,reference=REFERENCE,
                    scales=NP_SCALE_SCENARIOS,
                    sigmas=SM_SIGMA_FACTORS):
 allscenarios=[]
 for factor in scales:
  for infl in sigmas:
   values=[gaussian_what_if(m["F6_legacy_NP_shift"],
                            factor,infl,reference=reference)
           for m in models]
   pulls=sorted(v["Gaussian_what_if_pull_NOT_model_likelihood"]
                for v in values)
   allscenarios.append({
    "hypothetical_NP_shift_scale":factor,
    "hypothetical_SM_sigma_inflation":infl,
    "number_illustratively_beyond_positive_1p96_NOT_exclusion":
      sum(x>reference["Gaussian_two_sided_reference_z"] for x in pulls),
    "number_illustratively_beyond_abs_1p96_NOT_exclusion":
      sum(abs(x)>reference["Gaussian_two_sided_reference_z"] for x in pulls),
    "diagnostic_Gaussian_pull_min_median_max":
      [pulls[0],pulls[len(pulls)//2],pulls[-1]],
    "modern_BSM_likelihood_evaluated":False,
   })
 return allscenarios

def write_outputs(folder,models,origin,reference=REFERENCE):
 if len(models)!=309 or len({m["candidate_id"] for m in models})!=309:
  raise ValueError("F7 cannot finalize incomplete 309")
 if any(m["experimentally_allowed_or_excluded"] is not None or
        not m["no_validated_model_BtoXsgamma_2026_rate"] for m in models):
  raise ValueError("F7 refuses to fabricate exclusion labels")
 actual=sorted(models,key=lambda v:v["candidate_id"])
 full=folder/"F7_309_legacy_BtoXsgamma_2026_sensitivity_NOT_EXCLUSION.jsonl"
 with full.open("w") as f:
  for row in actual:f.write(json.dumps(row,sort_keys=True,allow_nan=False)+"\n")
 keys=tuple(models[0].keys())
 ranked=folder/"F7_309_HS_cascade_legacy_vs_modern_Gaussian_DIAGNOSTIC.csv"
 with ranked.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
  w.writerows(sorted(models,key=lambda m:(
     m["illustrative_Gaussian_pull_NOT_an_exclusion"],
     -m["E7_included_cascade_proxy_NOT_physical_rate"])))
 prior=[m for m in models if m["candidate_id"] in PRIORITY]
 if len(prior)!=len(PRIORITY):
  raise ValueError("F7 missing six corrected E7 Pareto controls")
 target=folder/"F7_six_priority_HS_cascade_flavor_tension_DIAGNOSTIC.csv"
 with target.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
  w.writerows(sorted(prior,key=lambda m:m[
      "illustrative_Gaussian_pull_NOT_an_exclusion"]))
 scenarios=scenario_counts(models,reference)
 scen=folder/"F7_36_hypothetical_NP_and_SM_uncertainty_scenarios.csv"
 with scen.open("w",newline="") as f:
  fields=("hypothetical_NP_shift_scale","hypothetical_SM_sigma_inflation",
          "number_illustratively_beyond_positive_1p96_NOT_exclusion",
          "number_illustratively_beyond_abs_1p96_NOT_exclusion",
          "diagnostic_Gaussian_pull_min_median_max",
          "modern_BSM_likelihood_evaluated")
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for row in scenarios:
   w.writerow({**row,"diagnostic_Gaussian_pull_min_median_max":
                      json.dumps(row["diagnostic_Gaussian_pull_min_median_max"])})
 pulls=sorted(v["illustrative_Gaussian_pull_NOT_an_exclusion"] for v in models)
 d=sorted(v["F6_legacy_NP_shift"] for v in models)
 nominal=next(x for x in scenarios if x[
     "hypothetical_NP_shift_scale"]==1. and x[
     "hypothetical_SM_sigma_inflation"]==1.)
 report={
  "status":STATUS,
  "total_source_models":309,
  "legacy_full_inclusive_F6_bsgamma_successfully_reused":True,
  "modern_2026_SM_and_exp_reference_used":reference,
  "2026_model_BSM_matching_derived":False,
  "full_experimental_likelihood_evaluated":False,
  "all_309_Zee_allowed_or_excluded":None,
  "SM_legacy_to_modern_central_shift_not_a_matched_BSM_correction":True,
  "legacy_BSM_NP_shift_min_median_max": [d[0],d[154],d[-1]],
  "purely_illustrative_Gaussian_pull_min_median_max":
      [pulls[0],pulls[154],pulls[-1]],
  "purely_illustrative_above_positive_1p96_count":
      nominal["number_illustratively_beyond_positive_1p96_NOT_exclusion"],
  "purely_illustrative_95pct_gaussian_NOT_an_exclusion":True,
  "num_sensitivity_scenarios":len(scenarios),
  "sensitivity_scenarios":scenarios,
  "priority_six":{m["candidate_id"]:m for m in prior},
  "required_next_physics":[
    "independently modern two-charged NLO/NNLO matching consistent with 2026 EFT operator basis",
    "model-aware perturbative/nonperturbative correlation and uncertainty likelihood",
    "independent SM and Type-II-670-GeV calibrated control in SAME 2026 rate engine",
    "combined LFV HiggsBounds heavy production, global vacuum validation"],
  "original_source_provenance":origin,
  "output_sha256":{p.name:digest(p) for p in (full,ranked,target,scen)},
 }
 writejson(folder/"summary.json",report)
 writejson(folder/"manifest.json",{
    "status":STATUS,
    "summary_SHA256":digest(folder/"summary.json"),
    "source":origin})
 return report

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--f6-dir",required=True,type=Path)
 p.add_argument("--output-dir",required=True,type=Path)
 a=p.parse_args()
 out=a.output_dir.resolve()
 if not ROOT.resolve().is_relative_to(Path("/home")) or not out.is_relative_to(ROOT/"work"):
  p.error("Only run under original /home Zee work checkout")
 if out.exists() and any(out.iterdir()):
  p.error("F7 refuses to overwrite any existing work output")
 out.mkdir(parents=True,exist_ok=True)
 try:
  orig,prov=load_f6(a.f6_dir.resolve())
  results=[model_row(z) for z in orig.values()]
  data=write_outputs(out,results,{**prov,
       "F7_analysis_source_SHA256":digest(Path(__file__))})
  print("F7_STATUS",STATUS,"COMPLETED",len(results),flush=True)
  print("F7_ILLUSTRATIVE_GAUSSIAN_PULL_MIN_MED_MAX",
        *data["purely_illustrative_Gaussian_pull_min_median_max"],flush=True)
  print("F7_ILLUSTRATIVE_ABOVE_1P96_NOT_MODEL_EXCLUSIONS",
        data["purely_illustrative_above_positive_1p96_count"],flush=True)
  for k in PRIORITY:
   m=data["priority_six"][k]
   print("F7_PRIORITY",k,"HS_E6",
         round(m["E6_HiggsSignals_delta_chi2_NOT_CL"],4),
         "E7_CASCADE",round(m["E7_included_cascade_proxy_NOT_physical_rate"],6),
         "F6_LEGACY_BR",f'{m["F6_legacy_superiso_full_inclusive_BR"]:.12g}',
         "LEGACY_NP_SHIFT",f'{m["F6_legacy_NP_shift"]:.9g}',
         "GAUSSIAN_WHAT_IF_PULL",round(m["illustrative_Gaussian_pull_NOT_an_exclusion"],4),
         "NP_SCALE_TO_REACH_1P96",round(m["illustrative_scale_to_1p96_upper_edge"],5),
         "NO_MODERN_MODEL_BR_OR_EXCLUSION",flush=True)
  print("F7_REPORT",out/"summary.json",flush=True)
  return 0
 except Exception as ex:
  writejson(out/"error.json",{
    "status":ERROR_STATUS,"error":repr(ex),"traceback":traceback.format_exc(),
    "Zee_model_allowed_or_excluded":None})
  print("F7_FAIL_CLOSED",repr(ex),file=sys.stderr,flush=True)
  return 1
if __name__=="__main__":raise SystemExit(main())
