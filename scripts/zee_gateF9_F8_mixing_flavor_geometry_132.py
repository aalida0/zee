#!/usr/bin/env python3
"""F9: source-audited SIX-CASE mixing/flavor geometry of F8 counterfactuals.

Reopens completed F8 309-source and 132 gamma-counterfactual CSVs, hashes
every original output, recomputes legacy Type-II 670 ratios and analytic
offdiagonal ZH1H2 coupling geometry, then ranks gamma slices for diagnostic
flavor-vs-geometry tradeoffs. No code executes the old SuperIso vendor
again. No counterfactual is a physical Zee point; its scalar potential,
neutrino solutions, LFV/RGE/vacuum, widths and hadronic rates are NOT
reoptimized. A legacy ratio <= 1 is NOT a TypeII-670-model exclusion test
nor a modern 2026 CL. Gauge/production geometry is NOT a cross section,
physical branching fraction or cascade signal.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics,sys,traceback
from pathlib import Path
from zee_gateF8_309_670TypeII_same_legacy_kernel_and_mixing import (
 STATUS as F8_STATUS, PRIORITY, ROOT, gauge_geometry)
STATUS="F9_SIX_ORIGINAL_ZEE_F8_GAMMA_FLAVOR_GEOMETRY_COUNTERFACTUAL_DIAGNOSTIC_NOT_ALLOWED"
FAIL="F9_FAIL_CLOSED_NOT_ZEE_EXCLUSION"
F8_ORIGINAL="F8_309_Zee_legacy_vs_670TypeII_NOT_EXCLUSION.jsonl"
F8_ACTUAL="F8_309_legacy_typeII_670_same_kernel_DIAGNOSTIC.csv"
F8_GAMMA="F8_six_fixed_mass_gamma_counterfactual_NOT_MODEL_POINTS.csv"
RATIO_EDGE=1.0 # legacy same-vendor Type-II, NEVER a modern CL boundary
RETENTION_THRESHOLDS=(0.5,0.8,0.95)

def digest(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for bit in iter(lambda:f.read(1<<20),b""):h.update(bit)
 return h.hexdigest()

def readjson(path):return json.loads(Path(path).read_text())
def dumpjson(path,v):Path(path).write_text(
 json.dumps(v,sort_keys=True,indent=2,allow_nan=False)+"\n")

def finite(x,name):
 val=float(x)
 if not math.isfinite(val):raise ValueError("F9 nonfinite "+name)
 return val

def check(a,b,label,rtol=5e-10,atol=5e-12):
 av=finite(a,label);bv=finite(b,label)
 if not math.isclose(av,bv,rel_tol=rtol,abs_tol=atol):
  raise ValueError("F9 F8 archived physical closure: "+label)

def records_from_csv(file):
 with file.open(newline="") as f:
  return list(csv.DictReader(f))

def read_f8(folder):
 """Verify immutable completed source hashes, 309 original and 132 scan."""
 s=readjson(folder/"summary.json")
 m=readjson(folder/"manifest.json")
 want={F8_ORIGINAL,F8_ACTUAL,F8_GAMMA}
 if (s.get("status")!=F8_STATUS or m.get("status")!=F8_STATUS or
     s.get("original_F6_Zee_models")!=309 or
     s.get("same_source_legacy_TypeII_670_reference_run_per_model")!=309 or
     s.get("number_fixed_mass_gamma_counterfactual_rows")!=132 or
     s.get("num_actual_original_gamma_points_in_counterfactual_slices")!=6 or
     s.get("published_2026_TypeII_mass_bound_imposed_on_Zee") is not False or
     s.get("F8_2026_modern_model_likelihood_completed") is not False or
     s.get("fully_model_allowed_or_excluded") is not None or
     s.get("all_counterfactual_points_are_unoptimized_unvalidated") is not True or
     s.get("source")!=m.get("source") or
     m.get("summary_SHA256")!=digest(folder/"summary.json") or
     set(s.get("sha256_outputs",{}))!=want or
     s.get("source",{}).get("F8_script_SHA256")!=digest(
      ROOT/"scripts/zee_gateF8_309_670TypeII_same_legacy_kernel_and_mixing.py")):
  raise ValueError("F9 F8 source/status/manifest/code-hash invalid")
 for file in want:
  if digest(folder/file)!=s["sha256_outputs"][file]:
   raise ValueError("F9 F8 archived SHA mismatch: "+file)
 actual={}
 with (folder/F8_ORIGINAL).open() as f:
  for line in f:
   r=json.loads(line);key=r["candidate_id"]
   if (key in actual or r.get("model_allowed_or_excluded") is not None
       or r.get("published_TypeII_670_bound_transferred_to_Zee") is not False):
    raise ValueError("F9 F8 illegal original Zee labeling/duplicates")
   if not(0<=finite(r["gamma"],"gamma")<=math.pi/2):
    raise ValueError("F9 original gamma outside interval")
   sm=finite(r["common_legacy_SM_BR"],"SM")
   ref=finite(r["reference_TypeII_670_legacy_BR_same_tanbeta"],"TypeII")
   old=finite(r["F6_original_legacy_inclusive_BR"],"F6")
   if not(0<sm<ref<.01 and 0<sm<old<.01):
    raise ValueError("F9 original TypeII/BSM/SM ordering invalid")
   check((old-sm)/(ref-sm),
         r["NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"],
         key+" original ratio")
   check(old-ref,r["Zee_minus_TypeII670_legacy_BR_NOT_EXCLUSION"],
         key+" rate difference")
   geom=gauge_geometry(float(r["gamma"]))
   for field in ("H1_quark_doublet_weight_cos2gamma",
                 "H2_quark_doublet_weight_sin2gamma",
                 "offdiagonal_ZH1H2_squared_normalized_to_max"):
    check(geom[field],r[field],key+" "+field)
   actual[key]=r
 if len(actual)!=309:
  raise ValueError("F9 F8 original cohort must have 309 entries")
 csv_actual=records_from_csv(folder/F8_ACTUAL)
 if len(csv_actual)!=309 or {v["candidate_id"] for v in csv_actual}!=set(actual):
  raise ValueError("F9 F8 actual CSV cohort differs")
 for r in csv_actual:
  check(r["NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"],
        actual[r["candidate_id"]][
         "NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"],
        r["candidate_id"]+" original CSV")
 if set(s.get("six_priority_actual_source",{}))!=set(PRIORITY):
  raise ValueError("F9 F8 actual Pareto benchmarks changed")
 for key,v in s["six_priority_actual_source"].items():
  check(v["NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"],
        actual[key]["NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"],
        key+" priority summary")
 calc=sorted(float(v["NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"])
             for v in actual.values())
 for v,x in zip(s["source_legacy_NP_over_TypeII670_ratio_min_median_max"],
                (calc[0],calc[154],calc[-1])):
  check(v,x,"F8 original ratio min/median/max")
 if s["num_Zee_higher_than_TypeII670_in_same_legacy_kernel"]!=sum(
    float(v["NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"])>1
    for v in actual.values()):
  raise ValueError("F9 F8 population >670 count changed")
 raws=records_from_csv(folder/F8_GAMMA)
 if len(raws)!=132:raise ValueError("F9 expected all 132 gamma lines")
 by_key={k:[] for k in PRIORITY}
 for row in raws:
  key=row["source_candidate_id"]
  if key not in by_key:
   raise ValueError("F9 six original source IDs differ")
  origin=actual[key]
  for left,right,label in (
      ("fixed_original_mH1_GeV","mH1_GeV","mH1"),
      ("fixed_original_mH2_GeV","mH2_GeV","mH2"),
      ("fixed_original_tanbeta","tanbeta","tanbeta"),
      ("original_gamma","gamma","original gamma")):
   check(row[left],origin[right],key+" "+label)
  gamma=finite(row["gamma_counterfactual"],key+" gamma")
  geom=gauge_geometry(gamma)
  for k in ("H1_quark_doublet_weight_cos2gamma",
            "H2_quark_doublet_weight_sin2gamma",
            "offdiagonal_ZH1H2_squared_normalized_to_max",
            "gZH1H2_over_doublet_Z_scale"):
   check(row[k],geom[k],key+" geometric "+k)
  legacy=finite(row["legacy_full_inclusive_BR_at_counterfactual_gamma"],
                key+" legacy counterfactual BR")
  ref=finite(row["legacy_TypeII670_comparator_same_tanbeta"],
             key+" counterfactual comparator")
  check(ref,origin["reference_TypeII_670_legacy_BR_same_tanbeta"],
        key+" comparator identical")
  check(legacy-ref,row["counterfactual_BR_minus_TypeII670_NOT_EXCLUSION"],
        key+" gamma rate difference")
  if not(0<legacy<.01):
   raise ValueError("F9 counterfactual BR outside physical numeric range")
  eq=legacy<ref
  if str(row["below_same_legacy_TypeII670_reference_NOT_ALLOWED"]).lower()!=str(eq).lower():
   raise ValueError("F9 F8 counterfactual 670 threshold flag inconsistent")
  is_orig=str(row["is_original_gamma_source_model"]).lower()=="true"
  if is_orig:
   check(gamma,origin["gamma"],key+" source exact gamma",rtol=0.,atol=1e-13)
   check(legacy,origin["F6_original_legacy_inclusive_BR"],
         key+" original gamma legacy BR",rtol=2e-8,atol=2e-12)
  elif math.isclose(gamma,float(origin["gamma"]),rel_tol=0,abs_tol=1e-13):
   raise ValueError("F9 duplicate near-original gamma mislabeled")
  if not(all(str(row[c]).lower()=="true" for c in (
      "counterfactual_scalar_potential_neutrinos_LFV_RGE_unverified",
      "complete_cascade_BRs_not_recomputed")) and
      str(row["experimental_Zee_allowed_or_excluded"]).strip() in ("","None","null")):
   raise ValueError("F9 counterfactual incorrectly declared physical")
  by_key[key].append((row,legacy,ref,gamma,is_orig))
 for key,rows in by_key.items():
  if len(rows)!=22 or sum(x[4] for x in rows)!=1:
   raise ValueError("F9 missing original and 21-grid gamma for "+key)
  gg=sorted(x[3] for x in rows)
  check(gg[0],0.,key+" gamma=0",rtol=0,atol=1e-13)
  check(gg[-1],math.pi/2,key+" gamma=pi/2",rtol=0,atol=1e-13)
  if len(set(gg))!=22:raise ValueError("F9 duplicate gamma values")
  for j in range(21):
   expected=math.pi/2*j/20
   if not any(math.isclose(g,expected,rel_tol=0.,abs_tol=5e-13)
              for g in gg):
    raise ValueError("F9 incomplete 21 grid "+key)
 proof={"F8_summary_SHA256":digest(folder/"summary.json"),
        "F8_manifest_SHA256":digest(folder/"manifest.json"),
        "F8_outputs_SHA256":dict(s["sha256_outputs"]),
        "F8_original_physics_source_SHA256":s["source"]["F8_script_SHA256"],
        "source_typeII_670_comparator_is_not_a_Zee_CL":True}
 return actual,by_key,proof

def pareto(rows,x="legacy_NP_shift_ratio_relative_to_TypeII670_NOT_CL",
           y="offdiag_Z_gauge_squared_relative_to_original"):
 """Minimize legacy rate ratio and maximize retained squared gauge coupling."""
 best=-math.inf;front=[]
 for q in sorted(rows,key=lambda row:(row[x],-row[y],row["gamma_counterfactual_rad"])):
  yv=finite(q[y],"Pareto gauge")
  if yv>best+1e-13:
   front.append(q);best=yv
 return front

def evaluate(actual,scans):
 """Recompute geometric trade-offs; do NOT manufacture physical models."""
 summaries={}
 full=[]
 selected=[]
 for name in PRIORITY:
  origin=actual[name];ori_gamma=float(origin["gamma"])
  ori_g=math.sin(2*ori_gamma)**2
  ori_p=math.sin(ori_gamma)**2 * ori_g
  if not(ori_g>1e-6 and ori_p>1e-6):
   raise ValueError("F9 original gauge coupling vanishes: "+name)
  sm=float(origin["common_legacy_SM_BR"])
  denom=float(origin["reference_TypeII_670_legacy_BR_same_tanbeta"])-sm
  if denom<=0:raise ValueError("F9 TypeII 670 denominator <=0")
  enriched=[]
  for src,br,ref,gamma,is_orig in scans[name]:
   g2=math.sin(2*gamma)**2
   p=math.sin(gamma)**2*g2
   legacy_ratio=(br-sm)/denom
   data={
    "source_candidate_id":name,
    "gamma_counterfactual_rad":gamma,
    "gamma_counterfactual_deg":math.degrees(gamma),
    "is_original_physically_reconstructed_Zee_point":bool(is_orig),
    "legacy_counterfactual_inclusive_BR_NOT_2026_model_rate":br,
    "legacy_TypeII670_inclusive_BR_same_tanbeta":ref,
    "legacy_NP_shift_ratio_relative_to_TypeII670_NOT_CL":legacy_ratio,
    "less_than_same_legacy_670_REFERENCE_NOT_experimental_acceptance":
        legacy_ratio<1,
    "quark_doublet_light_cos2gamma":math.cos(gamma)**2,
    "quark_doublet_heavy_sin2gamma":math.sin(gamma)**2,
    "offdiag_Z_gauge_squared_sin2_2gamma":g2,
    "offdiag_Z_gauge_squared_relative_to_original":g2/ori_g,
    "heavy_doublet_weight_times_offdiag_Z_squared_GEOMETRY_ONLY":p,
    "prodweighted_gauge_geometry_relative_to_original_NOT_signal_rate":p/ori_p,
    "complete_Zee_scalar_flavor_reoptimized_for_counterfactual":False,
    "actual_included_cascade_fraction_for_gamma_recalculated":False,
    "modern_2026_matching_or_exclusion_provided":False,
    "experimental_allowed_or_excluded":None,
   }
   if is_orig:
    check(data["legacy_NP_shift_ratio_relative_to_TypeII670_NOT_CL"],
          origin["NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"],
          name+" original NP ratio")
    check(data["offdiag_Z_gauge_squared_relative_to_original"],1.,
          name+" original gauge geometry ratio")
    check(data["prodweighted_gauge_geometry_relative_to_original_NOT_signal_rate"],
          1.,name+" original production-gauge geometry")
   enriched.append(data)
  f=pareto(enriched)
  selected.extend(f)
  def best_at(metric,t):
   candidates=[v for v in enriched if v[metric]>=t]
   return min(candidates,key=lambda z:(z[
     "legacy_NP_shift_ratio_relative_to_TypeII670_NOT_CL"],
     -z[metric])) if candidates else None
  min_any=min(enriched,key=lambda v:v[
        "legacy_NP_shift_ratio_relative_to_TypeII670_NOT_CL"])
  def bestrecord(v):
   if v is None:return None
   return {"gamma_deg":v["gamma_counterfactual_deg"],
           "original_source_gamma":v[
              "is_original_physically_reconstructed_Zee_point"],
           "legacy_NP_vs_TypeII670_ratio_NOT_CL":v[
              "legacy_NP_shift_ratio_relative_to_TypeII670_NOT_CL"],
           "gauge_retention":v["offdiag_Z_gauge_squared_relative_to_original"],
           "prodweighted_gauge_geometry_retention":v[
              "prodweighted_gauge_geometry_relative_to_original_NOT_signal_rate"]}
  out={
   "original_gamma_deg":math.degrees(ori_gamma),
   "original_HiggsSignals_E6_delta_NOT_CL":float(origin["E6_HS_delta_chi2_NOT_CL"]),
   "original_E7_included_cascade_proxy_NOT_signal":float(origin[
       "E7_cascade_included_channels_proxy_NOT_rate"]),
   "original_legacy_Zee_over_TypeII670_NP_shift_ratio":float(origin[
       "NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"]),
   "original_offdiag_Z_sin2_2gamma":ori_g,
   "original_sin2gamma_times_offdiag_Z_gauge_squared_geometry":ori_p,
   "all_22_gamma_slices_are_counterfactual_except_exact_original":True,
   "minimum_legacy_ratio_without_geometric_requirement":bestrecord(min_any),
   "num_any_counterfactual_below_same_legacy_TypeII670_reference":
        sum(v["legacy_NP_shift_ratio_relative_to_TypeII670_NOT_CL"]<1
            for v in enriched),
   "Pareto_gamma_slice_count":len(f),
  }
  for threshold in RETENTION_THRESHOLDS:
   val=best_at("offdiag_Z_gauge_squared_relative_to_original",threshold)
   key=f"gauge_retention_ge_{int(threshold*100)}pct"
   out[key]=bestrecord(val)
   val2=best_at("prodweighted_gauge_geometry_relative_to_original_NOT_signal_rate",
                threshold)
   key2=f"prodweighted_geometry_retention_ge_{int(threshold*100)}pct"
   out[key2]=bestrecord(val2)
   for label,which in (("gauge",val),("prodweighted_geometry",val2)):
    if which is not None:
     out[f"below_legacy_670_with_{label}_retention_ge_{int(threshold*100)}pct_NOT_ALLOWED"]=(
         which["legacy_NP_shift_ratio_relative_to_TypeII670_NOT_CL"]<1)
    else:
     out[f"below_legacy_670_with_{label}_retention_ge_{int(threshold*100)}pct_NOT_ALLOWED"]=False
  summaries[name]=out
  full.extend(enriched)
 if len(full)!=132 or sum(z["is_original_physically_reconstructed_Zee_point"]
                         for z in full)!=6:
  raise ValueError("F9 132/6 original source invariant failed")
 return full,selected,summaries

def output(out,actual,grid,pareto_rows,summaries,source):
 if not(len(actual)==309 and len(grid)==132 and len(summaries)==6 and
        set(summaries)==set(PRIORITY)):
  raise ValueError("F9 incomplete source census")
 if any(v["experimental_allowed_or_excluded"] is not None or
        v["modern_2026_matching_or_exclusion_provided"] or
        v["actual_included_cascade_fraction_for_gamma_recalculated"]
        for v in grid):
  raise ValueError("F9 may not claim physical gamma counterfactuals")
 files={
  "all":out/"F9_132_gamma_legacy_flavor_gauge_geometry_NOT_PHYSICAL.csv",
  "pareto":out/"F9_six_gamma_Pareto_geometries_NOT_PHYSICAL.csv",
  "summary":out/"F9_six_priority_gamma_tradeoff_NOT_ALLOWED.json",
 }
 for file,subset in ((files["all"],grid),(files["pareto"],pareto_rows)):
  with file.open("w",newline="") as f:
   w=csv.DictWriter(f,fieldnames=list(grid[0]))
   w.writeheader()
   w.writerows(sorted(subset,key=lambda v:(
       v["source_candidate_id"],v["gamma_counterfactual_rad"])))
 dumpjson(files["summary"],summaries)
 counts={k:sum(v.get(k) is True for v in summaries.values())
     for k in summaries[PRIORITY[0]] if k.startswith("below_legacy_670_with_")}
 minratio=sorted(z["legacy_NP_shift_ratio_relative_to_TypeII670_NOT_CL"]
                 for z in grid)
 report={
  "status":STATUS,"archived_original_Zee_points":309,
  "archived_gamma_counterfactual_rows":132,
  "one_real_original_gamma_source_per_priority_case":6,
  "num_original_source_models_vs_same_legacy_TypeII670_above":sum(
    float(x["NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"])>1
    for x in actual.values()),
  "num_original_source_models_vs_same_legacy_TypeII670_below":sum(
    float(x["NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"])<1
    for x in actual.values()),
  "six_priority_gamma_counts_below_reference_with_retention":counts,
  "all_132_gamma_ratio_min_median_max":[minratio[0],statistics.median(minratio),minratio[-1]],
  "counterfactual_gauge_vs_flavor_Pareto_records":len(pareto_rows),
  "six_priority_summaries":summaries,
  "modern_2026_Zee_B_to_Xs_gamma_complete_model_likelihood_evaluated":False,
  "physically_consistent_new_Zee_scalar_neutrino_Yukawa_reoptimization_evaluated":False,
  "full_Zee_allowed_excluded":None,
  "source":source,
  "outputs_SHA256":{p.name:digest(p) for p in files.values()},
 }
 dumpjson(out/"summary.json",report)
 dumpjson(out/"manifest.json",{
    "status":STATUS,"source":source,
    "summary_SHA256":digest(out/"summary.json")})
 return report

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument("--f8-dir",type=Path,required=True)
 parser.add_argument("--output-dir",type=Path,required=True)
 args=parser.parse_args()
 out=args.output_dir.resolve()
 if not ROOT.resolve().is_relative_to(Path("/home")) or not out.is_relative_to(ROOT.resolve()/"work"):
  parser.error("Only original Zee work tree in /home accepted")
 if out.exists() and any(out.iterdir()):
  parser.error("Cannot overwrite existing F9 outputs")
 out.mkdir(parents=True,exist_ok=True)
 try:
  actual,scans,proof=read_f8(args.f8_dir.resolve())
  grid,front,detail=evaluate(actual,scans)
  report=output(out,actual,grid,front,detail,{
     **proof,"F9_source_code_SHA256":digest(Path(__file__))})
  print("F9_STATUS",STATUS,"COMPLETED",len(actual),
        "GAMMA_POINTS",len(grid),"COUNTERFACTUAL_PARETO",len(front),
        "NO_PHYSICAL_ZEE_EXCLUSIONS",flush=True)
  for k in PRIORITY:
   x=report["six_priority_summaries"][k]
   print("F9_PRIORITY",k,
         "ORIGINAL_GAMMA_DEG",round(x["original_gamma_deg"],4),
         "ORIGINAL_LEGACY_RATIO",round(x[
           "original_legacy_Zee_over_TypeII670_NP_shift_ratio"],6),
         "MIN_RATIO_ANY",round(x[
           "minimum_legacy_ratio_without_geometric_requirement"][
             "legacy_NP_vs_TypeII670_ratio_NOT_CL"],6),
         "G80_BEST",x["gauge_retention_ge_80pct"],
         "P80_BEST",x["prodweighted_geometry_retention_ge_80pct"],
         "NOT_REOPTIMIZED",flush=True)
  for metric,n in report["six_priority_gamma_counts_below_reference_with_retention"].items():
   print("F9_UNPHYSICAL_GAMMA_DIAGNOSTIC",metric,n,"OF_6",flush=True)
  print("F9_SUMMARY",out/"summary.json",flush=True)
  return 0
 except Exception as exc:
  dumpjson(out/"error.json",{"status":FAIL,"error":repr(exc),
                             "traceback":traceback.format_exc(),
                             "full_Zee_allowed_excluded":None})
  print("F9_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
  return 1
if __name__=="__main__":raise SystemExit(main())
