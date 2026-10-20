#!/usr/bin/env python3
"""E4H: direct h(125)->e mu, e tau, mu tau on ALL 309 E3 optimized Zee spectra.

Source reuse: D5 exact tree partial widths, including both conjugate
final states; E3 optimized complex Y and D4 low-energy partial LFV;
E2 original scalar source and numerical vacuum witnesses.

Comparison with published direct BR 95% limits ASSUMES SM-like
production/acceptance; h total width is only leptonic-channel updated.
These are reference screens, NOT physical experimental exclusions.
"""
from __future__ import annotations
import argparse,csv,json,hashlib,math,os,traceback,sys,functools,collections
from pathlib import Path
import numpy as np
from gateB3_general_zee_charged_lepton_widths import complex_matrix
from zee_gateD5_h125_direct_LFV_27 import h125_widths
from zee_gateD4_W_photon_barr_zee_27 import compare_partial
from zee_gateE2_complete_395_original_vacua import STATUS as E2_STATUS
from zee_gateE3_309_multiroot_flavor_optimized_RGE import STATUS as E3_STATUS

ROOT=Path(__file__).resolve().parents[1]
STATUS="E4H_309_H125_DIRECT_LFV_REFERENCE_SCREENS_NOT_ALLOWED"
LIMITS={
 "h_to_e_mu":(4.4e-5,"CMS HIG-22-002","https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-22-002/index.html"),
 "h_to_e_tau":(.0020,"ATLAS JHEP07(2023)166","https://doi.org/10.1007/JHEP07(2023)166"),
 "h_to_mu_tau":(.0015,"CMS HIG-20-009","https://cms-results.web.cern.ch/cms-results/public-results/publications/HIG-20-009/index.html")}
MORE_COMPARISONS={"ATLAS_h_to_mu_tau":.0018,"CMS_h_to_e_tau":.0022}

def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
 return h.hexdigest()

def load(p):return json.loads(Path(p).read_text())
def save(p,obj):Path(p).write_text(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+"\n")

def preflight(e2,e3):
 a,b=load(e2/"summary.json"),load(e3/"summary.json")
 manifest=load(e3/"manifest.json")
 if (a.get("status")!=E2_STATUS or a.get("no_deeper_tree_vacuum_witness_found")!=309
     or a.get("all_RGE_qualified_original_potentials_vacuum_evaluated")!=395
     or b.get("status")!=E3_STATUS
     or b.get("multi_root_D1_D2_D4_evaluated_spectra")!=309
     or b.get("optimized_Yukawa_10TeV_running_screen_pass")!=309
     or manifest.get("status")!=E3_STATUS
     or manifest.get("summary_SHA256")!=sha(e3/"summary.json")
     or b.get("E2_provenance",{}).get("E2_summary_SHA256")!=sha(e2/"summary.json")):
  raise ValueError("E2/E3 309-spectrum source status or SHA mismatch")
 if b.get("NO_complete_experimental_Zee_allowed_or_excluded") is not None:
  raise ValueError("Upstream experimental physical acceptance unexpectedly claimed")
 for k,v in b["E2_provenance"]["E2_inputs_sha256"].items():
  if sha(e2/k)!=v:raise ValueError("E2 source fingerprint mismatch: "+k)
 csvpath=e2/"E2_all_original_B4_no_deeper_witness_NOT_ALLOWED.csv"
 with csvpath.open(newline="") as f: originals=list(csv.DictReader(f))
 pts={}
 keys=("id","mH1","mH2","mh2","ma","alpha","beta","gamma","m12sq",
       "lc","k1","k2","k12","production_weighted_nonleptonic_cascade_upper_proxy")
 for row in originals:
  tag=row["id"]
  if tag in pts or row.get("candidate_status")!="SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED":
   raise ValueError("Invalid E2 original scalar point")
  pts[tag]={k:(v if k=="id" else float(v))
            for k,v in row.items() if k in keys}
 if len(pts)!=309:raise ValueError("E2 has not exactly 309 original scalar points")
 archive=e3/"E3_all_309_multi_neutrino_partial_LFV_diagnostics.jsonl"
 if sha(archive)!=b["evidence_SHA256"]:
  raise ValueError("E3 checkpoint original output changed")
 rows={}
 with archive.open() as f:
  for line in f:
   x=json.loads(line);tag=x["candidate_id"]
   if tag in rows or tag not in pts:raise ValueError("E3 duplicate/mismatched ID")
   if (x["diagnostic_status"]!="MULTIROOT_PARTIAL_LFV_AND_OPTIMIZED_ORIGINAL_RGE_EVALUATED"
       or not x["optimized_original_potential_RGE"]["sampled_BFB_and_55channel_unitarity_pass_to_10TeV"]
       or x["full_Zee_allowed_or_excluded"] is not None):
    raise ValueError("E3 optimizer/RGE incomplete for "+tag)
   rows[tag]=x
 if len(rows)!=309 or set(rows)!=set(pts):raise ValueError("E2/E3 309 IDs disagree")
 provenance={"E2_summary":sha(e2/"summary.json"),
             "E3_summary":sha(e3/"summary.json"),
             "E3_archive":sha(archive),"E3_manifest":sha(e3/"manifest.json"),
             "E2_original_CSV":sha(csvpath)}
 return pts,rows,provenance

def analyze(point,source,check_d4=True):
 tag=point["id"]
 if source["candidate_id"]!=tag:raise ValueError("Wrong E3 source point")
 opt=source["D2"]["chosen_optimized_source"]
 sol=opt["solution"]
 if sol["candidate_id"]!=tag:raise ValueError("Wrong optimized f/Y point")
 Y=complex_matrix(sol["Y"],"Y")
 f=complex_matrix(sol["f"],"f")
 if not(np.isfinite(Y).all() and np.isfinite(f).all()):
  raise ValueError("Nonfinite optimized Zee f/Y")
 if check_d4:
  d4=compare_partial(point,f,Y,opt)
  got=d4["new_W_gamma_extended_max_partial_ratio_NOT_EXCLUSION"]
  expected=source["selected_D4_extended_partial_LFV_score_NOT_EXCLUSION"]
  if not math.isclose(got,expected,rel_tol=2e-8,abs_tol=1e-12):
   raise ValueError("E3/D4 coherent LFV did not reproduce: "+tag)
 widths=h125_widths(point,Y)
 br=widths["leptonic_updated_BR_proxy"]
 nominal=widths["nominal_SM_reference_BR"]
 scores={k:float(br[k])/v[0] for k,v in LIMITS.items()}
 nom={k:float(nominal[k])/v[0] for k,v in LIMITS.items()}
 if not all(math.isfinite(x) and x>=0 for x in
            list(scores.values())+list(nom.values())):
  raise ValueError("Invalid h125 LFV BR reference ratios")
 channel=max(scores,key=scores.get)
 kappas={k:float(widths[k]) for k in
  ("kappa_V_tree","kappa_top_TypeII_ansatz","kappa_bottom_TypeII_ansatz")}
 return {
  "candidate_id":tag,"mH1_GeV":point["mH1"],"mH2_GeV":point["mH2"],
  "cascade_proxy_NOT_cross_section":
     point["production_weighted_nonleptonic_cascade_upper_proxy"],
  "D4_incomplete_LFV_score":source[
     "selected_D4_extended_partial_LFV_score_NOT_EXCLUSION"],
  "h125_tree_LFV_partial_widths_GeV":widths["h125_LFV_partial_widths_GeV"],
  "h125_SM_width_assumed_BR":nominal,
  "h125_leptonic_only_width_updated_BR_proxy":br,
  "h125_leptonic_only_width_updated_total_GeV":
     widths["h125_leptonic_only_width_updated_GeV"],
  "h125_nominal_reference_limit_ratios":nom,
  "h125_leptonic_updated_reference_limit_ratios":scores,
  "worst_h125_direct_reference_ratio":max(scores.values()),
  "worst_h125_direct_reference_channel":channel,
  "all_three_SM_production_direct_reference_screens_below_one_NOT_PASS":
     max(scores.values())<1,
  "other_direct_reference_ratios_NOT_combined":{
     "ATLAS_h_to_mu_tau":br["h_to_mu_tau"]/.0018,
     "CMS_h_to_e_tau":br["h_to_e_tau"]/.0022},
  "h125_coupling_modifiers":kappas,
  "SM_production_assumed_NO_acceptance_recast":True,
  "nonleptonic_h125_widths_left_SM_like":True,
  "global_vacuum_proof":False,
  "physical_Zee_allowed_or_excluded":None}

def finish(out,pts,rows,provenance):
 if set(rows)!=set(pts) or len(rows)!=309:raise ValueError("E4H incomplete 309")
 full=out/"E4H_309_complete_h125_direct_LFV_NOT_ALLOWED.jsonl"
 with full.open("w") as f:
  for tag in sorted(rows):
   if rows[tag].get("physical_Zee_allowed_or_excluded") is not None:
    raise ValueError("E4H falsely classified physical Zee point")
   f.write(json.dumps(rows[tag],sort_keys=True,allow_nan=False)+"\n")
 dataset=[]
 for z in rows.values():
  mods=z["h125_coupling_modifiers"]
  data={
   "candidate_id":z["candidate_id"],
   "mH1_GeV":z["mH1_GeV"],"mH2_GeV":z["mH2_GeV"],
   "cascade_proxy":z["cascade_proxy_NOT_cross_section"],
   "D4_partial_low_energy_score":z["D4_incomplete_LFV_score"],
   "worst_H125_reference_ratio":z["worst_h125_direct_reference_ratio"],
   "dominant_h125_reference":z["worst_h125_direct_reference_channel"],
   "three_direct_reference_screens_below_one_NOT_ALLOWED":
       z["all_three_SM_production_direct_reference_screens_below_one_NOT_PASS"],
   "kappaV":mods["kappa_V_tree"],"kappaTop":mods["kappa_top_TypeII_ansatz"],
   "kappaBottom":mods["kappa_bottom_TypeII_ansatz"],
   "physical_Zee_allowed":None}
  for k in LIMITS:
   data["BR_"+k+"_leptonic_proxy"]=z[
       "h125_leptonic_only_width_updated_BR_proxy"][k]
   data["ratio_"+k]=z["h125_leptonic_updated_reference_limit_ratios"][k]
  dataset.append(data)
 dataset.sort(key=lambda d:(
     not d["three_direct_reference_screens_below_one_NOT_ALLOWED"],
     d["worst_H125_reference_ratio"],-d["cascade_proxy"],d["candidate_id"]))
 target=out/"E4H_309_ranked_direct_h125_LFV_NOT_ALLOWED.csv"
 with target.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(dataset[0]));w.writeheader();w.writerows(dataset)
 successes=sum(x["three_direct_reference_screens_below_one_NOT_ALLOWED"]
               for x in dataset)
 summary={
   "status":STATUS,"E3_optimized_original_models_tested":309,
   "direct_Higgs_reference_screens_below_one_NOT_physical_allowed":successes,
   "direct_Higgs_reference_tensions_NOT_physical_excluded":309-successes,
   "reference_score_min":min(x["worst_H125_reference_ratio"] for x in dataset),
   "reference_score_median":float(np.median(
      [x["worst_H125_reference_ratio"] for x in dataset])),
   "reference_score_max":max(x["worst_H125_reference_ratio"] for x in dataset),
   "dominant_reference_channels":dict(collections.Counter(
       x["dominant_h125_reference"] for x in dataset)),
   "observed_95CL_SM_production_BR_reference_limits":LIMITS,
   "other_limits_not_combined":MORE_COMPARISONS,
   "source_provenance_SHA256":provenance,
   "complete_HiggsTools_likelihood":"NOT_COMPUTED",
   "full_h125_total_width_and_production":"NOT_COMPUTED",
   "complete_CLFV_and_bsgamma":"NOT_COMPUTED",
   "full_Zee_allowed_or_excluded":None,
   "ranked_CSV_SHA256":sha(target),"per_candidate_JSONL_SHA256":sha(full)}
 save(out/"summary.json",summary)
 return summary

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ("e2-dir","e3-dir","output-dir"):
  p.add_argument("--"+key,type=Path,required=True)
 p.add_argument("--resume",action="store_true")
 a=p.parse_args()
 if not ROOT.resolve().is_relative_to(Path("/home")):
  p.error("Run only inside /home checkout")
 out=a.output_dir.resolve()
 if not out.is_relative_to(ROOT.resolve()/"work"):
  p.error("Use a fresh /home project work directory")
 if a.resume and not (out/"manifest.json").is_file():
  p.error("--resume requires prior E4H manifest")
 if not a.resume and out.exists() and any(out.iterdir()):
  p.error("Existing nonempty output. Use a new path or --resume")
 out.mkdir(parents=True,exist_ok=True)
 try:
  pts,source,provenance=preflight(a.e2_dir.resolve(),a.e3_dir.resolve())
  fingerprint={"source_SHA256":provenance,"script_SHA256":sha(Path(__file__))}
  if a.resume:
   old=load(out/"manifest.json")
   if old.get("fingerprint")!=fingerprint or (out/"summary.json").exists():
    raise ValueError("E4H resume source drift or completed campaign")
  else:save(out/"manifest.json",{"status":"E4H_IN_PROGRESS_NOT_ALLOWED",
                                 "fingerprint":fingerprint})
  import zee_gateD4_W_photon_barr_zee_27 as d4
  if not hasattr(d4.photon_W_kernel,"cache_info"):
   d4.photon_W_kernel=functools.lru_cache(maxsize=4096)(d4.photon_W_kernel)
  checkpoint=out/"E4H_309_checkpoint.jsonl"
  done={}
  if checkpoint.is_file():
   for line in checkpoint.read_text().splitlines():
    row=json.loads(line);key=row["candidate_id"]
    if key in done or key not in pts or row["physical_Zee_allowed_or_excluded"] is not None:
     raise ValueError("E4H checkpoint integrity failed")
    done[key]=row
  with checkpoint.open("a") as f:
   for idx,key in enumerate(sorted(pts),1):
    if key in done:continue
    row=analyze(pts[key],source[key])
    f.write(json.dumps(row,sort_keys=True,allow_nan=False)+"\n")
    f.flush();os.fsync(f.fileno())
    done[key]=row
    print("E4H_H125_DIRECT",idx,"/309",key,
          "REFERENCE_RATIO",row["worst_h125_direct_reference_ratio"],
          "NOT_PHYSICAL_EXCLUSION",flush=True)
  report=finish(out,pts,done,provenance)
  save(out/"manifest.json",{"status":STATUS,"fingerprint":fingerprint,
                             "summary_SHA256":sha(out/"summary.json")})
  print("E4H_STATUS",STATUS,
        "BELOW_REFERENCE_NOT_ALLOWED",
        report["direct_Higgs_reference_screens_below_one_NOT_physical_allowed"],
        "ABOVE_REFERENCE_NOT_EXCLUSION",
        report["direct_Higgs_reference_tensions_NOT_physical_excluded"],
        "FULL_ZEE_ALLOWED_UNKNOWN",flush=True)
  return 0
 except Exception as exc:
  save(out/"error.json",{"status":"E4H_BLOCKED_NOT_ALLOWED",
                         "error":repr(exc),"traceback":traceback.format_exc(),
                         "full_Zee_allowed_or_excluded":None})
  print("E4H_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
  return 1

if __name__=="__main__":
 raise SystemExit(main())
