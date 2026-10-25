#!/usr/bin/env python3
"""P1 Stage N1: actual 309 E3 neutrino-closed h/H/A neutral tree subset.

Reads the COMPLETE prior P1 E3->B3 charged artifact, validates SHA
against its summary, original E2 and E3 archive fingerprint, and matches
the same optimized Yukawa Y to new A1D/D5 source-consistent neutral
partial widths. Merges h,H,A and H1,H2 INCLUDED channels into an
honest *partial* five-state decay export. No total widths, HiggsBounds
predictions, or approved Zee model are manufactured.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
from zee_priority1_contracts import hashfile,validate_decays
from zee_priority1_charged_width_export import (
 verify_e2_e3_same_source,read_e3)
from zee_priority1_neutral_two_body import calculate as neutral_widths
from gateB3_general_zee_charged_lepton_widths import read_b1,complex_matrix

ROOT=Path(__file__).resolve().parents[1]
STATUS="P1_309_NEUTRAL_H_H_A_AND_CHARGED_H1_H2_INCLUDED_TREE_WIDTHS_NOT_COMPLETE"
PRIORITY=("B4_0004143","B4_0017640","B4_0003582","B4_0003854",
          "B4_0004380","B4_0002315","B4_0011208","B4_0011188")
def old_sources(prior):
 prior=prior.resolve()
 summary=json.loads((prior/"summary.json").read_text())
 if (summary.get("status")!=
   "P1_REAL_E3_B3_309_PARTIAL_CHARGED_WIDTHS_NOT_ALLOWED"
     or summary.get("original_source_points")!=309
     or summary.get("B3_neutrino_closed_genuine_charged_included_LO_models")!=309
     or summary.get("Zee_model_allowed_or_excluded") is not None
     or summary.get("actual_HiggsBounds_five_state_evaluated") is not False):
  raise ValueError("Incomplete previous charged 309 P1 source")
 e2=Path(summary["source_E2_CSV"]).resolve()
 e3=Path(summary["source_E3_JSONL"]).resolve()
 if (not e2.is_file() or not e3.is_file() or
     hashfile(e2)!=summary["E2_SHA256"] or
     hashfile(e3)!=summary["E3_SHA256"]):
  raise ValueError("Previous E2/E3 scalar-lepton source SHA changed")
 verify_e2_e3_same_source(e2,e3)
 archive=prior/"P1_E3_B3_309_charged_LO_included_NOT_COMPLETE.json"
 if not archive.is_file() or hashfile(archive)!=summary[
     "charged_export_SHA256"]:
  raise ValueError("Previous P1 genuine charged partial source altered")
 raw=json.loads(archive.read_text())
 if (raw.get("schema_version")!=1 or raw.get("stage")!="decays" or
     raw.get("full_Zee_allowed_or_excluded") is not None):
  raise ValueError("Previous charged export is not incomplete decays schema")
 byid={}
 for row in raw.get("records",[]):
  k=row["candidate_id"]
  if k in byid or row.get("status")!=(
    "P1_E3_SOURCE_CLOSED_B3_GENERAL_ZEE_CHARGED_PARTIAL_WIDTHS_NOT_HIGGSBOUNDS"
  ) or row.get("complete_five_state_physical_widths_computed") is not False:
   raise ValueError("Incomplete charged model/duplication/tampering")
  byid[k]=row
 if len(byid)!=309:
  raise ValueError("Prior charged widths did not finish all 309")
 return e2,e3,byid,{
    "previous_309_P1_summary_SHA256":hashfile(prior/"summary.json"),
    "previous_309_P1_charged_export_SHA256":hashfile(archive),
    "E2_original_309_SHA256":hashfile(e2),
    "E3_optimized_original_309_SHA256":hashfile(e3),
 }

def join_one(point,optimized,charged):
 """Re-use archived verified charged channel predictions, compute neutrals."""
 if not(point["id"]==optimized["candidate_id"]==
        charged["candidate_id"]):
  raise ValueError("Source IDs for neutral and charged widths disagree")
 if optimized.get("diagnostic_status")!=(
      "MULTIROOT_PARTIAL_LFV_AND_OPTIMIZED_ORIGINAL_RGE_EVALUATED"):
  raise ValueError("Missing original exact-neutrino E3 optimization")
 sol=optimized["D2"]["chosen_optimized_source"]["solution"]
 if sol.get("candidate_id")!=point["id"]:
  raise ValueError("Yukawa flavor model mismatch")
 Y=complex_matrix(sol["Y"],"Y")
 neutral=neutral_widths(point,Y)
 if neutral["candidate_id"]!=point["id"]:
  raise ValueError("Neutral width source mismatch")
 for pid in ("H1","H2"):
  val=charged["charged_included_LO_GeV"][pid]
  if not math.isclose(sum(val.values()),
      charged["charged_included_totals_NOT_physical_total_GeV"][pid],
      rel_tol=1e-10,abs_tol=1e-10):
   raise ValueError("Archived B3 charged sum drift")
 return {
  "candidate_id":point["id"],
  "status":STATUS,
  "all_physical_decay_channels_enumerated":False,
  "off_shell_and_QCD_treatment_validated":False,
  "independent_width_validation_reference":None,
  "full_five_state_physical_total_widths_computed":False,
  "particles_included_LO_GeV":{
    **neutral["tree_level_included_modes_GeV"],
    **charged["charged_included_LO_GeV"]},
  "included_width_sums_NOT_physical_totals_GeV":{
    **neutral["included_width_sums_NOT_physical_total_GeV"],
    **charged["charged_included_totals_NOT_physical_total_GeV"]},
  "h125_LFV_exact_source_D5_reproduced":
      neutral["h125_three_LFV_rates_exact_D5_reference_closure"],
  "conditional_H2_H1Z_included_only":
      charged["conditional_H2_H1Z_fraction_in_included_channels_ONLY"],
  "conditional_H1_tb_included_only":
      charged["conditional_H1_tb_fraction_in_included_channels_ONLY"],
  "cascade_proxy_NOT_signal_rate":
      charged["conditional_production_weighted_cascade_proxy_NOT_rate"],
  "neutral_missing_channels":neutral["unimplemented_modes"],
  "complete_Zee_allowed_or_excluded":None,
 }

def execute(prior,out):
 from zee_priority1_cli import main as p1main
 if out.exists():
  raise ValueError("Never overwrite earlier physical-source diagnostics")
 if not ROOT.resolve().is_relative_to(Path("/home")):
  raise ValueError("Run original Zee checkout from /home")
 e2,e3,charged,prior_proof=old_sources(prior)
 sources,_=read_e3(e3)
 scalar=read_b1(e2)
 if not(set(scalar)==set(sources)==set(charged)) or len(scalar)!=309:
  raise ValueError("E2 E3 and old B3 309 cohort mismatch")
 out.mkdir(parents=True,exist_ok=False)
 records=[join_one(scalar[k],sources[k],charged[k]) for k in sorted(scalar)]
 if any(validate_decays(row,{})!="BLOCKED_DECAY_CHANNEL_COMPLETENESS"
        for row in records):
  raise ValueError("Incomplete physical channels promoted to full model")
 payload=out/"P1_309_h_H_A_H1_H2_partial_LO_NOT_COMPLETE.json"
 payload.write_text(json.dumps({
    "schema_version":1,"stage":"decays",
    "provenance":{
      "source":"Original E2 E3 optimized f/Y, B3 charged and A1D/D5 neutral partial widths",
      **prior_proof,
      "neutral_kernel_SHA256":hashfile(
        ROOT/"scripts/zee_priority1_neutral_two_body.py"),
      "neutral_join_SHA256":hashfile(Path(__file__))},
    "records":records,"full_Zee_allowed_or_excluded":None,
    "usable_as_HiggsBounds_complete_five_state_input":False
  },indent=2,sort_keys=True,allow_nan=False)+"\n")
 join=out/"joined_five_stage_report"
 if p1main(["--points",str(e2),"--decays",str(payload),
             "--out",str(join)])!=0:
  raise ValueError("Five-stage P1 incomplete neutral decay join failed")
 canonical=json.loads((join/"summary.json").read_text())
 if (canonical.get("points")!=309 or
     canonical.get("per_component_status_counts",{}).get("decays",{}).get(
      "BLOCKED_DECAY_CHANNEL_COMPLETENESS")!=309 or
     canonical.get("per_candidate_higgstools_API_calls")!=0 or
     canonical.get("full_Zee_model_allowed_or_excluded") is not None):
  raise ValueError("Partial neutral widths incorrectly passed HiggsTools")
 byid={r["candidate_id"]:r for r in records}
 report={
  "status":STATUS,
  "original_source_points":309,
  "source_matched_neutral_h_H_A_models":309,
  "source_matched_charged_H1_H2_models":309,
  "all_three_h125_direct_LFV_rates_reproduced":309,
  "full_model_allowed_or_excluded":None,
  "HiggsBounds_model_evaluations":0,
  "full_five_state_decay_totals_computed":False,
  "priority_partial_width_summaries":{
    k:{
      "neutral_included_LO_not_total":byid[k][
        "included_width_sums_NOT_physical_totals_GeV"],
      "cascade_proxy_not_signal_rate":byid[k][
        "cascade_proxy_NOT_signal_rate"],
      "neutral_H_higher_than_A_included_width_NOT_total":
        byid[k]["included_width_sums_NOT_physical_totals_GeV"]["H"]>
        byid[k]["included_width_sums_NOT_physical_totals_GeV"]["A"]}
    for k in PRIORITY},
  "source_SHA256":prior_proof,
  "combined_partial_decay_export_SHA256":hashfile(payload),
  "canonical_P1_join_SHA256":hashfile(join/"summary.json"),
 }
 (out/"summary.json").write_text(json.dumps(
     report,indent=2,sort_keys=True,allow_nan=False)+"\n")
 print("P1_NEUTRAL_309_STATUS",STATUS,"COMPLETED",309,
       "H125_LFV_SOURCE_CLOSED",309,
       "FULL_HIGGSBOUNDS_EVALUATIONS",0,flush=True)
 for k,entry in report["priority_partial_width_summaries"].items():
  n=entry["neutral_included_LO_not_total"]
  print("P1_NEUTRAL_PRIORITY",k,"h_INCL_GeV",f'{n["h"]:.7g}',
        "H_INCL_GeV",f'{n["H"]:.7g}',
        "A_INCL_GeV",f'{n["A"]:.7g}',
        "NOT_PHYSICAL_TOTAL",flush=True)
 print("P1_NEUTRAL_309_REPORT",out/"summary.json")
 return report

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--prior",type=Path,
    default=ROOT/"work"/"p1_original_309_E3_B3_charged_included_LO_20261020_v1")
 ap.add_argument("--out",type=Path,
    default=ROOT/"work"/"p1_original_309_neutral_h_H_A_plus_charged_LO_20261020_v1")
 a=ap.parse_args()
 execute(a.prior.resolve(),a.out.resolve())
if __name__=="__main__":main()
