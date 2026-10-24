#!/usr/bin/env python3
"""N2 AF 309 source-pinned neutral bosonic LO inventory augmentation.

Read completed immutable N1 and original E2/E3, compute real N2
gauge-kinetic neutral -> charged W / AZ and charged-pair modes, retain
every original N1 h/H/A H1/H2 partial record, strictly reject overlaps.
No width sum is a physical total, HiggsBounds still BLOCKED 309/309.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
from zee_priority1_contracts import hashfile,validate_decays
from zee_priority1_neutral_309_one_shot import (
 old_sources,PRIORITY as FAVORITES, ROOT as ROOT_N1)
from zee_priority1_neutral_bosonic_two_body import (
 calculate as bosonic,STATUS as BOSONIC_STATUS)
from gateB3_general_zee_charged_lepton_widths import read_b1
ROOT=Path(__file__).resolve().parents[1]
STATUS="P1_N2_309_SOURCE_H_H_A_CHARGED_Z_W_AND_CHARGED_PAIRS_NOT_COMPLETE"
PRIOR=ROOT/"work"/"p1_original_309_neutral_h_H_A_plus_charged_LO_20261020_v1"
PRIOR_CHARGED=ROOT/"work"/"p1_original_309_E3_B3_charged_included_LO_20261020_v1"

def archived_n1(n1_dir):
 n1_dir=n1_dir.resolve()
 summary=json.loads((n1_dir/"summary.json").read_text())
 file=n1_dir/"P1_309_h_H_A_H1_H2_partial_LO_NOT_COMPLETE.json"
 if (summary.get("status")!=
    "P1_309_NEUTRAL_H_H_A_AND_CHARGED_H1_H2_INCLUDED_TREE_WIDTHS_NOT_COMPLETE"
     or summary.get("original_source_points")!=309
     or summary.get("source_matched_neutral_h_H_A_models")!=309
     or summary.get("source_matched_charged_H1_H2_models")!=309
     or summary.get("HiggsBounds_model_evaluations")!=0
     or summary.get("full_model_allowed_or_excluded") is not None
     or summary.get("full_five_state_decay_totals_computed") is not False
     or hashfile(file)!=summary.get("combined_partial_decay_export_SHA256")):
  raise ValueError("N2 previous real N1 309 archive status/hash mismatch")
 raw=json.loads(file.read_text())
 proof=raw.get("provenance",{})
 if (raw.get("schema_version")!=1 or raw.get("stage")!="decays"
     or raw.get("full_Zee_allowed_or_excluded") is not None
     or raw.get("usable_as_HiggsBounds_complete_five_state_input") is not False
     or proof.get("neutral_kernel_SHA256")!=hashfile(
      ROOT/"scripts"/"zee_priority1_neutral_two_body.py")
     or proof.get("neutral_join_SHA256")!=hashfile(
      ROOT/"scripts"/"zee_priority1_neutral_309_one_shot.py")):
  raise ValueError("N2 previous N1 code provenance changed")
 rows={}
 for row in raw.get("records",[]):
  key=row["candidate_id"]
  if (key in rows or row.get("status")!=summary["status"]
      or row.get("all_physical_decay_channels_enumerated") is not False
      or row.get("complete_Zee_allowed_or_excluded") is not None
      or set(row["particles_included_LO_GeV"])!=
       {"h","H","A","H1","H2"}):
   raise ValueError("N2 previous N1 309 incomplete per-model evidence invalid")
  rows[key]=row
 if len(rows)!=309:
  raise ValueError("N2 previous N1 archive does not have 309 unique source records")
 return rows,{
   "N1_summary_SHA256":hashfile(n1_dir/"summary.json"),
   "N1_archive_SHA256":hashfile(file),
   "N1_existing_kernel_SHA256":proof["neutral_kernel_SHA256"],
   "N1_existing_runner_SHA256":proof["neutral_join_SHA256"],
 }

def merge_one(point,old):
 key=point["id"]
 if key!=old["candidate_id"]:
  raise ValueError("N2 wrong E2 point linked to N1 neutral/charged rates")
 source=old["particles_included_LO_GeV"]
 if set(source)!={"h","H","A","H1","H2"}:
  raise ValueError("N2 previous five-state channel inventory malformed")
 addition=bosonic(point)
 if addition["candidate_id"]!=key or addition["status"]!=BOSONIC_STATUS:
  raise ValueError("N2 bosonic source kernel returned invalid result")
 full={k:dict(v) for k,v in source.items()}
 for k,extras in addition["additional_gauge_and_charged_pair_LO_GeV"].items():
  if set(extras)&set(full[k]):
   raise ValueError("N2 duplicate decay mode between N1 and N2 "+k)
  full[k].update(extras)
 for k,values in full.items():
  if not all(math.isfinite(float(v)) and float(v)>=0 for v in values.values()):
   raise ValueError("N2 illegal partial width")
  if sum(values.values())+1e-12<float(
    old["included_width_sums_NOT_physical_totals_GeV"][k]):
   raise ValueError("N2 source partial width sum unexpectedly decreased")
 return {
  "candidate_id":key,"status":STATUS,
  "all_physical_decay_channels_enumerated":False,
  "off_shell_and_QCD_treatment_validated":False,
  "independent_width_validation_reference":None,
  "full_five_state_physical_total_widths_computed":False,
  "particles_included_LO_GeV":full,
  "included_width_sums_NOT_physical_totals_GeV":{
     k:sum(v.values()) for k,v in full.items()},
  "original_N1_included_sums_NOT_physical_totals_GeV":
     old["included_width_sums_NOT_physical_totals_GeV"],
  "N2_new_neutral_bosonic_GeV":
     addition["additional_gauge_and_charged_pair_LO_GeV"],
  "N2_Gate6_H1_H2_h_H_trilinear_source_closed":True,
  "old_cascade_proxy_NOT_signal_rate":old["cascade_proxy_NOT_signal_rate"],
  "missing_mode_classes":[
    *addition["missing"], "missing all physics from previous N1 inventory",
    "fully calibrated HiggsBounds mapping/production"],
  "complete_Zee_allowed_or_excluded":None,
 }

def decay_export_payload(records,archive_proof,charged_proof):
 """One audited N2 schema-v1 artifact for the canonical P1 validator.

 The source key is required by load_export(), but explicitly DOES NOT
 claim independent external cross-code physics verification.
 """
 return {
  "schema_version":1,"stage":"decays",
  "provenance":{
    "source":"Original SHA-verified E2/E3/charged/N1 archives; Gate6 scalar Hessian and gauge-kinetic N2 source implementation (same repository, not independent cross-code validation)",
    **archive_proof,**charged_proof,
    "N2_bosonic_source_SHA256":hashfile(
        ROOT/"scripts"/"zee_priority1_neutral_bosonic_two_body.py"),
    "N2_runner_SHA256":hashfile(Path(__file__)),
    "independent_external_width_validation_completed":False},
  "records":records,
  "full_Zee_allowed_or_excluded":None,
  "usable_as_complete_HiggsBounds_five_state_input":False,
 }

def execute(n1,charged,out):
 from zee_priority1_cli import main as p1main
 if not ROOT.resolve().is_relative_to(Path("/home")):
  raise ValueError("N2 original Zee work checkout must be in /home")
 if out.exists():raise ValueError("N2 refuses to overwrite existing output")
 original,archive_proof=archived_n1(n1)
 e2,e3,oldcharged,charged_proof=old_sources(charged)
 data=read_b1(e2)
 if not (len(data)==len(oldcharged)==len(original)==309
        and set(data)==set(oldcharged)==set(original)):
  raise ValueError("N2 original E2/E3/N1 309 cohort mismatch")
 n1summary=json.loads((n1/"summary.json").read_text())
 if n1summary["source_SHA256"]!=charged_proof:
  raise ValueError("N2 original N1 linked charged E2/E3 source drift")
 result=[merge_one(data[k],original[k]) for k in sorted(data)]
 if any(validate_decays(r,{})!="BLOCKED_DECAY_CHANNEL_COMPLETENESS"
        for r in result):
  raise ValueError("N2 partial decay values incorrectly accepted by P1")
 out.mkdir(parents=True,exist_ok=False)
 target=out/"P1_N2_309_h_H_A_H1_H2_MORE_PARTIAL_LO_NOT_COMPLETE.json"
 target.write_text(json.dumps(
   decay_export_payload(result,archive_proof,charged_proof),
   sort_keys=True,indent=2,allow_nan=False)+"\n")
 joined=out/"joined_five_gate_report"
 if p1main(["--points",str(e2),"--decays",str(target),
            "--out",str(joined)])!=0:
  raise ValueError("N2 canonical Priority1 contract failed")
 summary=json.loads((joined/"summary.json").read_text())
 if (summary.get("points")!=309 or
     summary.get("per_component_status_counts",{}).get("decays",{}).get(
        "BLOCKED_DECAY_CHANNEL_COMPLETENESS")!=309
     or summary.get("per_candidate_higgstools_API_calls")!=0
     or summary.get("full_Zee_model_allowed_or_excluded") is not None):
  raise ValueError("N2 HiggsBounds exclusion fabricated from partial rates")
 priority={}
 byid={r["candidate_id"]:r for r in result}
 for k in FAVORITES:
  z=byid[k]
  priority[k]={
   "old_N1_h_H_A_included_sums_NOT_totals_GeV":{
    t:z["original_N1_included_sums_NOT_physical_totals_GeV"][t]
       for t in ("h","H","A")},
   "new_N2_h_H_A_included_sums_NOT_totals_GeV":{
    t:z["included_width_sums_NOT_physical_totals_GeV"][t]
       for t in ("h","H","A")},
   "N2_H_to_H1plus_H1minus_GeV":
     z["N2_new_neutral_bosonic_GeV"]["H"]["H1plus_H1minus"],
   "N2_A_to_H1_W_both_charge_modes_GeV":
     z["N2_new_neutral_bosonic_GeV"]["A"]["H1_W_both_charge_modes"],
   "N2_A_to_h_Z_GeV":z["N2_new_neutral_bosonic_GeV"]["A"]["h_Z"],
   "H1H2_cascade_proxy_unchanged_NOT_physical_rate":
        z["old_cascade_proxy_NOT_signal_rate"],
  }
 report={
  "status":STATUS,"original_source_points":309,
  "real_N2_neutral_bosonic_calculations":309,
  "N2_Gate6_h_H_charged_cross_cubic_closed":309,
  "physical_five_state_widths_complete":False,
  "HiggsBounds_95CL_evaluations":0,
  "experimental_model_allowed_excluded":None,
  "N2_priority_modes_and_N1_comparison":priority,
  "source_provenance":{**archive_proof,**charged_proof},
  "merged_N2_partial_export_SHA256":hashfile(target),
  "joined_P1_canonical_SHA256":hashfile(joined/"summary.json"),
 }
 (out/"summary.json").write_text(json.dumps(
  report,sort_keys=True,indent=2,allow_nan=False)+"\n")
 print("P1_N2_STATUS",STATUS,"COMPLETED 309",
   "HIGGSBOUNDS",0,"NO_PHYSICAL_TOTAL",flush=True)
 for key in FAVORITES:
  z=priority[key]
  print("P1_N2_PRIORITY",key,
    "N1_H_INCL",round(z["old_N1_h_H_A_included_sums_NOT_totals_GeV"]["H"],7),
    "N2_H_INCL",round(z["new_N2_h_H_A_included_sums_NOT_totals_GeV"]["H"],7),
    "H_H1plusH1minus",round(z["N2_H_to_H1plus_H1minus_GeV"],7),
    "A_H1W_BOTH",round(z["N2_A_to_H1_W_both_charge_modes_GeV"],7),
    "NOT_TOTAL_OR_ALLOWED",flush=True)
 print("P1_N2_REPORT",out/"summary.json",flush=True)
 return report

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--prior-n1",type=Path,default=PRIOR)
 p.add_argument("--prior-charged",type=Path,default=PRIOR_CHARGED)
 p.add_argument("--out",type=Path,default=ROOT/"work"/
  "p1_original_309_neutral_bosonic_N2_20261020_v2")
 a=p.parse_args()
 execute(a.prior_n1.resolve(),a.prior_charged.resolve(),a.out.resolve())
if __name__=="__main__":main()
