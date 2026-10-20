#!/usr/bin/env python3
"""F8: SAME-LEGACY-kernel Type-II 670-GeV anchor and Zee mixing tradeoff.

All 309 F6 ORIGINAL Zee spectra vs their own tanbeta-dependent 670-GeV
SINGLE physical Type-II charged-doublet reference, computed through the
SAME pinned F6/A1U full legacy SuperIso source executable. 670 is taken
from Misiak et al (2026) as a REFERENCE MASS ONLY; the source calculation
is historical and does NOT transfer the modern 95% CL exclusion.

Six priority cases: counterfactual gamma scans AT FIXED CHARGED MASSES
and tanbeta, with real source BR recomputation and independent geometric
ZH1H2 gauge-coupling factor sin²(2gamma). These deformed gamma slices
do NOT reconstruct a consistent scalar potential, RGE, LFV, vacuum,
full charged BRs or collider production. No deformed point is called
physical or allowed/excluded, and the gauge factor is not a cascade rate.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys,traceback
from pathlib import Path
from zee_gateF7_309_2026_bsgamma_tension_sensitivity import (
 ROOT,load_f6,PRIORITY,REFERENCE,digest,load,writejson)
from zee_gateF6_309_full_legacy_bsgamma import (
 run_pinned,STATUS as F6_STATUS)
STATUS="F8_309_SAME_LEGACY_KERNEL_TYPEII_670_REFERENCE_AND_FIXED_MASS_MIXING_COUNTERFACTUAL_NOT_EXCLUSION"
BLOCK="F8_BLOCKED_REFERENCE_NOT_EXCLUSION"
REFERENCE_MASS=670.0
NGRID=21
EXEC="f6_pinned_A1U_inclusive_br"
FILE_PREFIX="F8"

def near(a,b,label,rtol=2e-8,atol=2e-12):
 try: a=float(a);b=float(b)
 except (TypeError,ValueError):raise ValueError("Invalid numeric "+label)
 if not(math.isfinite(a) and math.isfinite(b) and
        math.isclose(a,b,rel_tol=rtol,abs_tol=atol)):
  raise ValueError("F8 source closure "+label)

def archive_bin(folder):
 """Only reopen original F6 compiled A1U; never link unpinned vendor."""
 summ=load(folder/"summary.json");manifest=load(folder/"manifest.json")
 if (summ.get("status")!=F6_STATUS or
     manifest.get("summary_SHA256")!=digest(folder/"summary.json")):
  raise ValueError("F6 successful archive missing")
 bound=summ["source_provenance"]["new_C_executable"]
 exe=Path(bound["command"][-1]).resolve()
 if (exe.name!=EXEC or
     not exe.is_relative_to(folder.resolve()) or
     exe!=folder.resolve()/EXEC or
     not exe.is_file() or not exe.stat().st_size or
     digest(exe)!=bound["binary_sha256"]):
  raise ValueError("F8 historical binary does not match F6 SHA")
 from zee_gateF6_309_full_legacy_bsgamma import ROOT as R
 if R.resolve()!=ROOT.resolve():
  raise ValueError("F8 current source root mismatch")
 return exe,{"executable_SHA256":digest(exe),
             "F6_original_C_source_SHA256":bound["source_sha256"],
             "F6_original_static_vendor_SHA256":bound["vendor_library_sha256"]}

def gauge_geometry(gamma):
 """Normalized H1-H2-Z gauge coupling magnitude squared."""
 if not math.isfinite(gamma) or not(0<=gamma<=math.pi/2):
  raise ValueError("F8 gamma outside physical mixing interval")
 c,s=math.cos(gamma),math.sin(gamma)
 return {"gamma":gamma,
         "H1_quark_doublet_weight_cos2gamma":c*c,
         "H2_quark_doublet_weight_sin2gamma":s*s,
         "offdiagonal_ZH1H2_squared_normalized_to_max":math.sin(2*gamma)**2,
         "gZH1H2_over_doublet_Z_scale":c*s}

def call_source(exe,m1,m2,gamma,t,call=run_pinned):
 rec,_=call(exe,m1,m2,gamma,t,"helper_reload")
 value=float(rec["full_legacy_Zee_BR"])
 if not(0<value<.01 and math.isfinite(value)):
  raise ValueError("F8 nonphysical legacy rate source")
 # run_pinned checks coefficient/context closures and authentic markers.
 return value

def check_anchor(exe,six,call=call_source):
 """First close 6 actual F6 originals and Type-II degenerate endpoints."""
 for key in PRIORITY:
  row=six[key]
  obs=call(exe,row["mH1_GeV"],row["mH2_GeV"],
           row["gamma"],row["tanbeta"])
  near(obs,row["BR_BtoXsgamma_legacy_SuperIso_two_state"],
       "previous F6 source reproducibility "+key)
 t=six[PRIORITY[0]]["tanbeta"]
 ref=call(exe,REFERENCE_MASS,REFERENCE_MASS,0.,t)
 other=call(exe,REFERENCE_MASS,REFERENCE_MASS,math.pi/2,t)
 center=call(exe,REFERENCE_MASS,REFERENCE_MASS,.8,t)
 near(other,ref,"pure TypeII 670 equal-mass gamma endpoint")
 near(center,ref,"pure TypeII 670 equal-mass arbitrary gamma")
 return {"reproduced_F6_original_priority":len(PRIORITY),
         "TypeII670_degenerate_H1_H2_gamma_independence_verified":True,
         "reference_tanbeta":t,"reference_BR_legacy":ref}

def sweep_actual(rows,exe,call=call_source):
 out=[]
 for n,key in enumerate(sorted(rows),1):
  r=rows[key]
  mb=float(r["mH1_GeV"]);mB=float(r["mH2_GeV"])
  g=float(r["gamma"]);t=float(r["tanbeta"])
  actual=float(r["BR_BtoXsgamma_legacy_SuperIso_two_state"])
  ref=call(exe,REFERENCE_MASS,REFERENCE_MASS,0.,t)
  ownSM=float(r["BR_BtoXsgamma_legacy_SuperIso_SM_reference"])
  if not(ownSM<actual<.01 and ownSM<ref<.01):
   raise ValueError("F8 sample nonmonotonic NP relative to own legacy SM")
  ratio=(actual-ownSM)/(ref-ownSM)
  geo=gauge_geometry(g)
  line={
   "candidate_id":key,"mH1_GeV":mb,"mH2_GeV":mB,
   "gamma":g,"tanbeta":t,
   "E6_HS_delta_chi2_NOT_CL":r["HiggsSignals_E6_delta_chi2_NOT_CL"],
   "E7_cascade_included_channels_proxy_NOT_rate":
       r["E7_included_cascade_proxy_NOT_physical_rate"],
   "F6_original_legacy_inclusive_BR":actual,
   "reference_TypeII_670_legacy_BR_same_tanbeta":ref,
   "common_legacy_SM_BR":ownSM,
   "NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL":ratio,
   "Zee_minus_TypeII670_legacy_BR_NOT_EXCLUSION":actual-ref,
   "Zee_higher_than_TypeII670_in_same_legacy_kernel":actual>ref,
   **geo,"model_allowed_or_excluded":None,
   "published_TypeII_670_bound_transferred_to_Zee":False,
  }
  if not math.isclose(geo["H1_quark_doublet_weight_cos2gamma"]+
                      geo["H2_quark_doublet_weight_sin2gamma"],1.,
                      rel_tol=0.,abs_tol=1e-13):
   raise ValueError("F8 charged quark mixing weights not unitary")
  out.append(line)
  print("F8_TYPEII670",n,"/309",key,
        "ACTUAL_LEGACY",f"{actual:.10g}",
        "TYPEII670_LEGACY",f"{ref:.10g}",
        "NP_RATIO_NOT_LIMIT",f"{ratio:.7g}",
        "MODEL_ALLOWED_UNKNOWN",flush=True)
 return out

def counterfactual_grid(rows,exe,call=call_source,ngrid=NGRID):
 if ngrid<5:raise ValueError("At least five gamma counterfactual points")
 out=[]
 for key in PRIORITY:
  row=rows[key]
  m1=float(row["mH1_GeV"]);m2=float(row["mH2_GeV"])
  t=float(row["tanbeta"]);g=float(row["gamma"])
  old=float(row["BR_BtoXsgamma_legacy_SuperIso_two_state"])
  reference=call(exe,REFERENCE_MASS,REFERENCE_MASS,0.,t)
  # include historical exact original point as separate center;
  # never replace it with a nearby discrete gamma-grid point.
  gammas=sorted(set([g]+[math.pi/2*j/(ngrid-1)
                             for j in range(ngrid)]))
  if len(gammas)!=ngrid+1:
   # Could coincide exactly with one grid point, valid.
   if len(gammas)!=ngrid:raise ValueError("F8 gamma grid duplicates")
  original_matches=0
  for ga in gammas:
   BR=call(exe,m1,m2,ga,t)
   if ga==g:
    near(BR,old,key+" original gamma full legacy inclusive BR")
    original_matches+=1
   geo=gauge_geometry(ga)
   out.append({
    "source_candidate_id":key,"fixed_original_mH1_GeV":m1,
    "fixed_original_mH2_GeV":m2,"fixed_original_tanbeta":t,
    "gamma_counterfactual":ga,
    "original_gamma":g,
    "is_original_gamma_source_model":ga==g,
    "legacy_full_inclusive_BR_at_counterfactual_gamma":BR,
    "legacy_TypeII670_comparator_same_tanbeta":reference,
    "counterfactual_BR_minus_TypeII670_NOT_EXCLUSION":BR-reference,
    "below_same_legacy_TypeII670_reference_NOT_ALLOWED":BR<reference,
    **{k:v for k,v in geo.items() if k!="gamma"},
    "counterfactual_scalar_potential_neutrinos_LFV_RGE_unverified":True,
    "complete_cascade_BRs_not_recomputed":True,
    "experimental_Zee_allowed_or_excluded":None,
   })
  if original_matches!=1:raise ValueError("F8 original gamma never closed")
 return out

def save_report(out,records,scans,proof):
 if len(records)!=309 or len({x["candidate_id"] for x in records})!=309:
  raise ValueError("F8 invalid 309 actual source set")
 if (len({r["source_candidate_id"] for r in scans})!=6 or
     any(r["experimental_Zee_allowed_or_excluded"] is not None for r in scans) or
     any(r["model_allowed_or_excluded"] is not None for r in records)):
  raise ValueError("F8 cannot produce misleading model exclusion")
 j=out/"F8_309_Zee_legacy_vs_670TypeII_NOT_EXCLUSION.jsonl"
 with j.open("w") as f:
  for row in sorted(records,key=lambda r:r["candidate_id"]):
   f.write(json.dumps(row,sort_keys=True,allow_nan=False)+"\n")
 csvpath=out/"F8_309_legacy_typeII_670_same_kernel_DIAGNOSTIC.csv"
 with csvpath.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader()
  w.writerows(sorted(records,key=lambda r:r[
      "NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"]))
 scanpath=out/"F8_six_fixed_mass_gamma_counterfactual_NOT_MODEL_POINTS.csv"
 with scanpath.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(scans[0]));w.writeheader()
  w.writerows(sorted(scans,key=lambda r:(r["source_candidate_id"],
                                         r["gamma_counterfactual"])))
 items=sorted(r["NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"]
              for r in records)
 d=sorted(r["Zee_minus_TypeII670_legacy_BR_NOT_EXCLUSION"]
          for r in records)
 summ={
  "status":STATUS,"original_F6_Zee_models":309,
  "same_source_legacy_TypeII_670_reference_run_per_model":309,
  "published_2026_TypeII_95CL_limit_GeV":REFERENCE_MASS,
  "published_2026_TypeII_mass_bound_imposed_on_Zee":False,
  "F8_2026_modern_model_likelihood_completed":False,
  "fully_model_allowed_or_excluded":None,
  "source_legacy_NP_over_TypeII670_ratio_min_median_max":[
       items[0],items[154],items[-1]],
  "same_legacy_Zee_minus_TypeII670_BR_min_median_max":[
       d[0],d[154],d[-1]],
  "num_Zee_higher_than_TypeII670_in_same_legacy_kernel":
       sum(z["Zee_higher_than_TypeII670_in_same_legacy_kernel"]
           for z in records),
  "six_priority_actual_source":{
       k:next(r for r in records if r["candidate_id"]==k)
       for k in PRIORITY},
  "number_fixed_mass_gamma_counterfactual_rows":len(scans),
  "num_counterfactual_slice_points_below_legacy_TypeII670_reference":
    sum(z["below_same_legacy_TypeII670_reference_NOT_ALLOWED"]
        for z in scans),
  "num_actual_original_gamma_points_in_counterfactual_slices":
    sum(z["is_original_gamma_source_model"] for z in scans),
  "all_counterfactual_points_are_unoptimized_unvalidated":True,
  "source":proof,
  "missing_for_physical_conclusions":[
       "2026 modern NLO/NNLO matched two-state BSM matrix elements and theory covariance",
       "heavy scalar total widths, production, HiggsBounds",
       "full LFV including Barr-Zee and mu->e conversion",
       "neutrino likelihood global vacuum and reoptimization for any gamma deformation",
       "real signal production times BR and detector acceptance"],
  "sha256_outputs":{p.name:digest(p) for p in (j,csvpath,scanpath)},
 }
 writejson(out/"summary.json",summ)
 return summ

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--f6-dir",type=Path,required=True)
 p.add_argument("--output-dir",type=Path,required=True)
 a=p.parse_args()
 out=a.output_dir.resolve()
 if not ROOT.resolve().is_relative_to(Path("/home")) or not out.is_relative_to(ROOT.resolve()/"work"):
  p.error("F8 only runs original Zee checkout under /home")
 if out.exists() and any(out.iterdir()):
  p.error("F8 refuses to overwrite previous results")
 out.mkdir(parents=True,exist_ok=True)
 try:
  orig,proof=load_f6(a.f6_dir.resolve())
  binary,pin=archive_bin(a.f6_dir.resolve())
  anchor=check_anchor(binary,orig)
  fixed=sweep_actual(orig,binary)
  scan=counterfactual_grid(orig,binary)
  full=save_report(out,fixed,scan,{
     **proof,**pin,"historical_controls":anchor,
     "F8_script_SHA256":digest(Path(__file__)),
     "modern_paper_reference":{
       "source":"arxiv:2608.29863 v1 (2026-08-30), TypeII-only bound",
       "TypeII_95CL_reference_mass_GeV":670.,
       "not_a_Zee_95CL_bound":True},
  })
  writejson(out/"manifest.json",{
      "status":STATUS,"summary_SHA256":digest(out/"summary.json"),
      "source":full["source"]})
  print("F8_STATUS",STATUS,"COMPLETED",309,
        "TYPEII670_REFERENCES",309,
        "GAMMA_COUNTERFACTUALS",len(scan),
        "MODERN_ZEE_EXCLUSION_NOT_COMPUTED",flush=True)
  print("F8_RATIO_MIN_MEDIAN_MAX",
        *full["source_legacy_NP_over_TypeII670_ratio_min_median_max"])
  print("F8_SAME_KERNEL_ZEE_ABOVE_TYPEII670_NOT_EXCLUSIONS",
        full["num_Zee_higher_than_TypeII670_in_same_legacy_kernel"])
  for k in PRIORITY:
   z=full["six_priority_actual_source"][k]
   print("F8_PRIORITY",k,
         "E6_HS",round(z["E6_HS_delta_chi2_NOT_CL"],4),
         "E7_INCLUDED_CASCADE",round(z[
              "E7_cascade_included_channels_proxy_NOT_rate"],6),
         "ZEE_OVER_TYPEII670_NP_RATIO",round(z[
              "NP_shift_Zee_over_TypeII670_legacy_ratio_NOT_CL"],5),
         "NO_ZEE_EXCLUSION",flush=True)
  print("F8_SUMMARY",out/"summary.json",flush=True)
  return 0
 except Exception as exc:
  writejson(out/"error.json",{"status":BLOCK,
        "error":repr(exc),"traceback":traceback.format_exc(),
        "full_model_allowed_or_excluded":None})
  print("F8_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
  return 1
if __name__=="__main__":raise SystemExit(main())
