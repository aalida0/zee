#!/usr/bin/env python3
"""E7: all-309 original Zee neutrino-closed, LEPTON-CORRECTED charged cascades.

Connect completed, SOURCE-FINGERPRINTED E2/E3/E4H/E5/E6 without recomputing
HiggsSignals. Recompute selected neutrino f/Y closure and general Zee
H1/H2->e,mu,tau nu widths, replace the obsolete Type-II lepton contribution,
and rebuild the joint E6-HiggsSignals / corrected-cascade Pareto frontier.

The B3+Gate6 included channels are *not* physical total widths or physical
branching fractions; production proxy sin^2gamma is not a hadronic cross
section. HiggsBounds cannot be meaningfully evaluated for all Zee heavy
states without neutral+charged full widths and production; do not invent
zero rates or declare ALLOWED/EXCLUDED. No calibrated delta-chi2 CL cuts.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys,traceback
from pathlib import Path

STATUS="E7_309_NEUTRINO_CLOSED_GENERAL_ZEE_CHARGED_WIDTH_PARETO_NOT_ALLOWED"
BLOCKED="E7_FAIL_CLOSED_NO_EXCLUSION"
ROOT=Path(__file__).resolve().parents[1]
E6_JSON="E6_309_gamma_Zgamma_loop_corrected_HS_NOT_ALLOWED.jsonl"
E6_CSV="E6_309_gamma_Zgamma_loop_HS_ranked_NOT_ALLOWED.csv"
FAVORITES=("B4_0004143","B4_0003582","B4_0004173","B4_0004380",
           "B4_0002315","B4_0006862","B4_0006962",
           "B4_0017640","B4_0017589")
MISSING={
 "charged_widths":"LO_included_channels_only_no_QCD_offshell_or_complete_cascades",
 "neutral_heavy_widths":"NOT_CALCULATED",
 "heavy_neutral_production_rates":"NOT_CALCULATED",
 "charged_H1_H2_hadronic_production":"NOT_VALIDATED",
 "full_HiggsBounds_Zee":"NOT_EVALUATED_NO_VALID_COMPLETE_INPUT",
 "full_B_to_Xs_gamma_two_charged_order_matched":"NOT_VALIDATED",
 "complete_two_loop_LFV_and_mu_e_conversion":"NOT_VALIDATED",
 "neutrino_experimental_likelihood":"CENTRAL_NORMAL_ORDERING_ONLY",
 "global_vacuum_minimum":"NUMERIC_NO_DEEPER_WITNESS_NOT_PROOF",
 "full_HiggsSignals_STXS_QCD_EW_and_signal_correlations":
      "E6_EFFECTIVE_COUPLING_AND_LO_BSM_LOOP_RATIO_APPROX",
}

def digest(path):
 h=hashlib.sha256()
 with Path(path).open("rb") as f:
  for part in iter(lambda:f.read(1<<20),b""):h.update(part)
 return h.hexdigest()

def load(path):
 return json.loads(Path(path).read_text())

def save(path,x):
 Path(path).write_text(json.dumps(x,sort_keys=True,indent=2,
                             allow_nan=False)+"\n")

def finite(z,name):
 v=float(z)
 if not math.isfinite(v):raise ValueError("Nonfinite "+name)
 return v

def close(a,b,name,rtol=1e-8,atol=1e-11):
 if not math.isclose(finite(a,name),finite(b,name),
                     rel_tol=rtol,abs_tol=atol):
  raise ValueError("Source/physical numerical closure: "+name)

def validate_e6_archive(folder,ids,proof):
 summary=load(folder/"summary.json")
 manifest=load(folder/"manifest.json")
 if (summary.get("status")!=proof["e6_status"] or
     summary.get("original_source_models")!=309 or
     summary.get("updated_HiggsSignals_hgamma_gamma_models")!=309 or
     summary.get("same_HiggsSignals_observables")!=159 or
     summary.get("full_Zee_allowed_or_excluded") is not None or
     not summary.get("full_h_to_Zgamma_one_loop_scalar_subset_with_mixed_mass_completed")
     or not summary.get("full_h_to_Zgamma_higher_order_model_prediction_NOT_completed")
     or manifest.get("status")!=proof["e6_status"] or
     manifest.get("source",{}).get("source")!=proof["e6_source"] or
     manifest.get("summary_SHA256")!=digest(folder/"summary.json")):
  raise ValueError("E6 completion/provenance/status mismatch")
 if summary.get("source")!=proof["e6_source"]:
  raise ValueError("Original E6 physics source files changed since AF run")
 p=folder/E6_JSON
 c=folder/E6_CSV
 for f in (p,c):
  if summary.get("output_hashes",{}).get(f.name)!=digest(f):
   raise ValueError("E6 immutable archived output SHA mismatch: "+f.name)
 out={}
 with p.open() as stream:
  for line in stream:
   row=json.loads(line)
   name=row["candidate_id"]
   if name in out or name not in ids or (
       row.get("full_Zee_allowed_or_excluded") is not None) or (
       row.get("h_Zgamma_full_one_loop_charged_scalar_mixed_mass_completed") is not True):
    raise ValueError("E6 duplicate/nonphysical/missing-source case")
   finite(row["delta_chisq_vs_same_SM"],"E6 chi2")
   finite(row["loop_amplitudes"][
       "new_over_old_h_gamma_gamma_partial_width_LO_amplitude_ratio"],
       "E6 gamma ratio")
   out[name]=row
 if len(out)!=309 or set(out)!=set(ids):
  raise ValueError("E6 source cohort incomplete")
 with c.open(newline="") as f:
  csvrows=list(csv.DictReader(f))
 if len(csvrows)!=309 or {z["candidate_id"] for z in csvrows}!=set(ids):
  raise ValueError("E6 CSV set size/IDs differ")
 if len({z["candidate_id"] for z in csvrows})!=309:
  raise ValueError("E6 CSV duplicated a model")
 for z in csvrows:
  name=z["candidate_id"]
  close(z["gamma_Zgamma_loop_corrected_delta_vs_SM"],
        out[name]["delta_chisq_vs_same_SM"],name+" CSV<->JSONL E6 chi2",
        rtol=1e-11,atol=1e-10)
 return out,{
  "E6_summary_SHA256":digest(folder/"summary.json"),
  "E6_manifest_SHA256":digest(folder/"manifest.json"),
  "E6_JSONL_SHA256":digest(p),"E6_CSV_SHA256":digest(c),
  "original_E6_physics_sources":summary["source"],
 }

def pareto(rows,x="HS_delta_chi2_E6_vs_fixed_SM",
           y="charged_cascade_included_channel_proxy_NOT_physical_rate"):
 """Minimize x, maximize y, requiring a strict improvement in >=one."""
 sortedrows=sorted(rows,key=lambda z:(finite(z[x],"chi"),
                                      -finite(z[y],"cascade"),z["candidate_id"]))
 frontier=[]
 maximum=-math.inf
 for row in sortedrows:
  val=float(row[y])
  if val>maximum:
   frontier.append(row)
   maximum=val
 return frontier

def numerical_channel_closure(source,report):
 """Audit B3 physical included two-body width arithmetic, independently."""
 from gate6_width_inventory import vector_width, MZ
 from gateB3_general_zee_charged_lepton_widths import LEPTONS
 from zee_gateD5_h125_direct_LFV_27 import VEV
 widths=report["partial_widths_included_GeV"]
 fr=report["BR_H2_H1Z_included_general_Zee"]
 br=report["BR_H1_tb_included_general_Zee"]
 for state in ("H1","H2"):
  channels=widths[state]
  if (not isinstance(channels,dict) or "tau_nu_TypeII" in channels or
      not all(f"{ell}_nu_generalZee" in channels for ell in LEPTONS)):
   raise ValueError("Missing general Zee charged-lepton width replacement")
  if not all(finite(val,"charged partial width")>=0 for val in channels.values()):
   raise ValueError("Unphysical included width")
  total=sum(channels.values())
  close(total,report["totals_included_GeV"][state],"H"+state+" width sum")
  if total<=0:raise ValueError("Nonpositive charged included total width")
  fracs={k:val/total for k,val in channels.items()}
  for key,v in fracs.items():
   close(v,report["partial_widths_included_GeV"][state][key]/total,
         "fraction arithmetic")
 if not (0<=fr<=1 and 0<=br<=1):
  raise ValueError("Incorrect included-channel BR range")
 close(widths["H2"]["H1_Z"]/report["totals_included_GeV"]["H2"],
       fr,"H2->H1Z included fraction")
 close(widths["H1"]["tb"]/report["totals_included_GeV"]["H1"],
       br,"H1->tb included fraction")
 g=source["gamma"]
 gauge=(MZ/VEV)*math.sin(g)*math.cos(g)
 expected=vector_width(source["mH2"],source["mH1"],MZ,gauge)
 close(widths["H2"]["H1_Z"],expected,"H2->H1 Z from Z current",
       rtol=4e-10,atol=1e-10)
 p=math.sin(g)**2*fr*br
 close(report["production_weighted_partial_cascade_proxy"],p,
       "B3 lepton corrected cascade proxy",rtol=2e-10,atol=1e-12)
 return p

def evaluate(point,source,e6,targets,b3,complex_matrix):
 """Use optimized ORIGINAL f/Y; no LFV reselection or scalar defaulting."""
 tag=point["id"]
 if source["candidate_id"]!=tag or e6["candidate_id"]!=tag:
  raise ValueError("E3 E6 and original B4 ID mismatch")
 solution=source["D2"]["chosen_optimized_source"]["solution"]
 if solution.get("candidate_id")!=tag:
  raise ValueError("E3 D2 optimized lepton solution ID mismatch")
 f=complex_matrix(solution["f"],"f")
 Y=complex_matrix(solution["Y"],"Y")
 result=b3.evaluate(point,f,Y,targets)
 proxy=numerical_channel_closure(point,result)
 if result.get("candidate_id")!=tag:
  raise ValueError("B3 width output different original model")
 close(result["neutrino_matrix_closure_eV"],
       result["neutrino_matrix_closure_eV"],"neutrino closure")
 if result["neutrino_matrix_closure_eV"]>b3.NUMERIC_ATOL:
  raise ValueError("Neutrino mass reconstruction fails")
 old=finite(point["production_weighted_nonleptonic_cascade_upper_proxy"],
            "original nonleptonic cascade proxy")
 new=finite(proxy,"lepton corrected cascade")
 oldE6=e6["delta_chisq_vs_same_SM"]
 return {
  "candidate_id":tag,
  "mH1_GeV":point["mH1"],"mH2_GeV":point["mH2"],
  "gamma":point["gamma"],"tanbeta":math.tan(point["beta"]),
  "higgs_alignment_beta_minus_alpha":point["beta"]-point["alpha"],
  "HS_delta_chi2_E6_vs_fixed_SM":oldE6,
  "HS_chi2_E6_not_a_calibrated_exclusion":True,
  "original_B4_nonleptonic_proxy":old,
  "charged_cascade_included_channel_proxy_NOT_physical_rate":new,
  "corrected_minus_original_B4_proxy":new-old,
  "included_channel_BR_H2_to_H1Z":result["BR_H2_H1Z_included_general_Zee"],
  "included_channel_BR_H1_to_tb":result["BR_H1_tb_included_general_Zee"],
  "charged_included_total_H1_GeV":result["totals_included_GeV"]["H1"],
  "charged_included_total_H2_GeV":result["totals_included_GeV"]["H2"],
  "charged_lepton_widths_by_flavour_GeV":result["leptonic_widths_GeV"],
  "charged_partial_widths_included_GeV":result["partial_widths_included_GeV"],
  "neutrino_matrix_reconstruction_max_abs_eV":
     result["neutrino_matrix_closure_eV"],
  "partial_LFV_selected_D4_NOT_complete_likelihood":
     source["selected_D4_extended_partial_LFV_score_NOT_EXCLUSION"],
  "source_E6_gamma_ratio":e6["loop_amplitudes"][
     "new_over_old_h_gamma_gamma_partial_width_LO_amplitude_ratio"],
  "source_E6_Zgamma_ratio":e6["Zgamma_full_mixed_mass_PV_amplitudes"][
     "full_charged_scalar_plus_modified_SM_LO_hZgamma_over_SM_LO_width"],
  "claim_full_Zee_approved":None,
  "claim_HiggsBounds_excluded":None,
  "complete_width_or_production_certified":False,
 }

def output_row(z):
 keys=("candidate_id","mH1_GeV","mH2_GeV","gamma","tanbeta",
       "HS_delta_chi2_E6_vs_fixed_SM","original_B4_nonleptonic_proxy",
       "charged_cascade_included_channel_proxy_NOT_physical_rate",
       "corrected_minus_original_B4_proxy",
       "included_channel_BR_H2_to_H1Z","included_channel_BR_H1_to_tb",
       "charged_included_total_H1_GeV","charged_included_total_H2_GeV",
       "neutrino_matrix_reconstruction_max_abs_eV",
       "partial_LFV_selected_D4_NOT_complete_likelihood",
       "claim_full_Zee_approved","claim_HiggsBounds_excluded")
 return {k:z[k] for k in keys}

def write_outputs(folder,rows,provenance,threshold):
 if len(rows)!=309 or len({x["candidate_id"] for x in rows})!=309:
  raise ValueError("Refuse finalize E7 without all 309 unique original cases")
 threshold=finite(threshold,"descriptive cascade threshold")
 if not 0<=threshold<=1:raise ValueError("Threshold outside zero/one")
 if any(row["claim_full_Zee_approved"] is not None or
        row["claim_HiggsBounds_excluded"] is not None for row in rows):
  raise ValueError("False HiggsBounds or allowed classification")
 data=sorted(rows,key=lambda r:(r["HS_delta_chi2_E6_vs_fixed_SM"],
                              -r["charged_cascade_included_channel_proxy_NOT_physical_rate"]))
 frontier=pareto(data)
 details=folder/"E7_309_general_Zee_charged_widths_NOT_ALLOWED.jsonl"
 with details.open("w") as f:
  for row in sorted(data,key=lambda z:z["candidate_id"]):
   f.write(json.dumps(row,sort_keys=True,allow_nan=False)+"\n")
 ranked=folder/"E7_309_HS_vs_lepton_corrected_cascade_NOT_ALLOWED.csv"
 front=folder/"E7_Pareto_HS_vs_general_Zee_cascade_NOT_ALLOWED.csv"
 high=folder/"E7_high_cascade_descriptive_NOT_ALLOWED.csv"
 for file,subset in ((ranked,data),(front,frontier),
                     (high,[r for r in data
                            if r["charged_cascade_included_channel_proxy_NOT_physical_rate"]>=threshold])):
  with file.open("w",newline="") as f:
   writer=csv.DictWriter(f,fieldnames=list(output_row(data[0])))
   writer.writeheader()
   writer.writerows(output_row(row) for row in subset)
 old=[z["original_B4_nonleptonic_proxy"] for z in data]
 new=[z["charged_cascade_included_channel_proxy_NOT_physical_rate"] for z in data]
 shifts=[u-v for u,v in zip(new,old)]
 stats={
  "status":STATUS,"original_models":309,
  "neutrino_closure_full_309_checked":True,
  "general_Zee_lepton_charged_widths_309_calculated":True,
  "higgsSignals_reused_source_locked_E6_not_recomputed":True,
  "HiggsBounds_model_exclusion_not_evaluated":True,
  "full_allowed_and_excluded_Zee_counts":None,
  "original_B4_nonleptonic_proxy_median":float(sorted(old)[154]),
  "new_B3_general_lepton_included_proxy_median":float(sorted(new)[154]),
  "median_change_general_minus_legacy":float(sorted(shifts)[154]),
  "num_proxy_decreased":sum(u<v for u,v in zip(new,old)),
  "num_proxy_increased":sum(u>v for u,v in zip(new,old)),
  "Pareto_frontier_count":len(frontier),
  "Pareto_frontier_ids":[x["candidate_id"] for x in frontier],
  "descriptive_high_cascade_threshold":threshold,
  "descriptive_high_cascade_count":sum(u>=threshold for u in new),
  "prior_E6_key_sources":{
     key:output_row(next(z for z in data if z["candidate_id"]==key))
     for key in FAVORITES if any(z["candidate_id"]==key for z in data)},
  "blocking_missing_physics":MISSING,
  "source_provenance":provenance,
  "sha256_outputs":{p.name:digest(p) for p in (details,ranked,front,high)},
 }
 save(folder/"summary.json",stats)
 return stats

def main(argv=None):
 ap=argparse.ArgumentParser(description=__doc__)
 for field in ("e2-dir","e3-dir","e4h-dir","e5-dir","e6-dir","hs-dataset","output-dir"):
  ap.add_argument("--"+field,type=Path,required=True)
 ap.add_argument("--high-cascade-threshold",type=float,default=.4)
 args=ap.parse_args(argv)
 out=args.output_dir.resolve()
 if not ROOT.resolve().is_relative_to(Path("/home")):
  ap.error("Run only from /home project checkout")
 if not out.is_relative_to(ROOT.resolve()/"work"):
  ap.error("Output must be under /home/aalida/zee/work/")
 if out.exists() and any(out.iterdir()):
  ap.error("Refuse to overwrite a nonempty E7 output directory")
 out.mkdir(parents=True,exist_ok=True)
 try:
  import zee_gateE6_309_charged_gamma_higgssignals as e6
  import gateB3_general_zee_charged_lepton_widths as b3
  from gateA1b_hierarchical_no_seed import target_neutrino_matrix
  from gateB3_general_zee_charged_lepton_widths import complex_matrix
  pts,src,refs,e5orig,e6source=e6.source_inputs(
      args.e2_dir.resolve(),args.e3_dir.resolve(),args.e4h_dir.resolve(),
      args.e5_dir.resolve(),args.hs_dataset.resolve())
  old,prov=validate_e6_archive(args.e6_dir.resolve(),pts,{
      "e6_status":e6.STATUS,"e6_source":e6source})
  target,_=target_neutrino_matrix()
  if getattr(target,"shape",None)!=(3,3):
   raise ValueError("Target neutrino matrix not 3x3")
  provenance={**prov,
   "E7_source_SHA256":digest(Path(__file__)),
   "B3_width_source_SHA256":digest(Path(b3.__file__)),
   "E2_E3_E4H_E5_input_ids_SHA256":hashlib.sha256(
       ("\n".join(sorted(pts))+"\n").encode()).hexdigest()}
  results=[]
  for j,tag in enumerate(sorted(pts),1):
   r=evaluate(pts[tag],src[tag],old[tag],target,b3,complex_matrix)
   results.append(r)
   print("E7_NEUTRINO_WIDTH",j,"/309",tag,
         "HS_E6",round(r["HS_delta_chi2_E6_vs_fixed_SM"],6),
         "OLD_PROXY",round(r["original_B4_nonleptonic_proxy"],6),
         "NEW_INCLUDED_PROXY",round(r[
           "charged_cascade_included_channel_proxy_NOT_physical_rate"],6),
         "HIGGSBOUNDS_NOT_EVALUATED",flush=True)
  summary=write_outputs(out,results,provenance,args.high_cascade_threshold)
  save(out/"manifest.json",{
      "status":STATUS,"source":provenance,
      "summary_SHA256":digest(out/"summary.json")})
  print("E7_STATUS",STATUS,"COMPLETED",309,
        "PARETO",summary["Pareto_frontier_count"],
        "FULL_MODEL_ALLOWED_UNKNOWN",flush=True)
  print("E7_RESULTS",out/"summary.json",flush=True)
  return 0
 except Exception as exc:
  save(out/"error.json",{"status":BLOCKED,"error":repr(exc),
                         "traceback":traceback.format_exc(),
                         "full_Zee_allowed_or_excluded":None})
  print("E7_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
  return 1

if __name__=="__main__":
 raise SystemExit(main())
