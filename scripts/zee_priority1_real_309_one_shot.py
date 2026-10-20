#!/usr/bin/env python3
"""Priority1 next AF step: 309 source-matched E2/E3 true B3 charged widths.

Auto-discovers E2 and E3 archived source outputs under the existing
/home/aalida/zee/work, only if a UNIQUE correct SHA-matched E2/E3 pair
exists. Never modifies original E2/E3. Calls real GateB3 numerics once
per archive point, then routes outputs through canonical P1 CLI:
the *decays* stage must report incomplete 5-state widths, never physical
HiggsBounds approval/exclusion. Run from checked-out P1 feature branch.
"""
from __future__ import annotations
import argparse,collections,json,sys
from pathlib import Path
from zee_priority1_charged_width_export import (
 execute, verify_e2_e3_same_source, SOURCE_E3)
from zee_priority1_contracts import hashfile,STATUS as P1_STATUS

ROOT=Path(__file__).resolve().parents[1]
E2_FILE="E2_all_original_B4_no_deeper_witness_NOT_ALLOWED.csv"

def locate(work):
 pairs=[]
 e2_sources=sorted(work.rglob(E2_FILE))
 e3_sources=sorted(work.rglob(SOURCE_E3))
 for e3 in e3_sources:
  try:
   e3_report=json.loads((e3.parent/"summary.json").read_text())
   hashes=e3_report.get("E2_provenance",{})
   chosen=[e2 for e2 in e2_sources
      if hashfile(e2)==hashes.get("E2_inputs_sha256",{}).get(E2_FILE)
      and hashfile(e2.parent/"summary.json")==hashes.get("E2_summary_SHA256")]
   for e2 in chosen:
    verify_e2_e3_same_source(e2,e3)
    pairs.append((e2,e3))
  except (KeyError,ValueError,FileNotFoundError,TypeError):
   # Only fully validated E2/E3 outputs can be selected.
   continue
 if len(pairs)!=1:
  raise ValueError("Need precisely one E2/E3 source matched archive pair; "
                   f"found {len(pairs)} among {len(e2_sources)} E2 and "
                   f"{len(e3_sources)} E3 files. Supply --e2-csv/--e3-jsonl "
                   "if there are multiple source-matched copies.")
 return pairs[0]

def run(e2,e3,out):
 from zee_priority1_cli import main as p1main
 if not ROOT.resolve().is_relative_to(Path("/home")):
  raise ValueError("AF runner requires original /home source checkout")
 if out.exists():
  raise ValueError("Never overwrite previous P1 output")
 e2=e2.resolve();e3=e3.resolve()
 verify_e2_e3_same_source(e2,e3)
 out.mkdir(parents=True,exist_ok=False)
 payload=out/"P1_E3_B3_309_charged_LO_included_NOT_COMPLETE.json"
 results=execute(e2,e3,payload)
 joined=out/"joined_five_gate_report"
 rc=p1main(["--points",str(e2),"--decays",str(payload),
            "--out",str(joined)])
 if rc!=0:raise ValueError("Full Priority1 five-gate coverage join failed")
 summary=json.loads((joined/"summary.json").read_text())
 if (summary.get("points")!=309 or
     summary.get("full_Zee_model_allowed_or_excluded") is not None or
     summary.get("per_candidate_higgstools_API_calls")!=0 or
     summary.get("per_component_status_counts",{}).get("decays",{}).get(
       "BLOCKED_DECAY_CHANNEL_COMPLETENESS")!=309):
  raise ValueError("Incomplete B3 widths illegally promoted to HiggsTools")
 data=json.loads(payload.read_text())["records"]
 unique={r["candidate_id"]:r for r in data}
 if len(unique)!=309:
  raise ValueError("P1 B3 output must contain exact original 309 cohort")
 completed=[z for z in data if z.get("status")==
   "P1_E3_SOURCE_CLOSED_B3_GENERAL_ZEE_CHARGED_PARTIAL_WIDTHS_NOT_HIGGSBOUNDS"]
 missing=[z for z in data if z.get("status")=="BLOCKED_NO_OPTIMIZED_E3_FY"]
 if len(completed)+len(missing)!=309:
  raise ValueError("Unknown 309 point B3 status encountered")
 favorites=["B4_0004143","B4_0017640","B4_0003582","B4_0003854",
            "B4_0004380","B4_0002315","B4_0011208","B4_0011188"]
 report={
   "status":"P1_REAL_E3_B3_309_PARTIAL_CHARGED_WIDTHS_NOT_ALLOWED",
   "source_E2_CSV":str(e2),
   "source_E3_JSONL":str(e3),
   "original_source_points":309,
   "B3_neutrino_closed_genuine_charged_included_LO_models":len(completed),
   "B3_without_optimized_source_neutrino_solution_not_excluded":len(missing),
   "actual_HiggsBounds_five_state_evaluated":False,
   "Zee_model_allowed_or_excluded":None,
   "p1_decays_gate":"BLOCKED_DECAY_CHANNEL_COMPLETENESS",
   "E2_SHA256":hashfile(e2),"E3_SHA256":hashfile(e3),
   "charged_export_SHA256":hashfile(payload),
   "priority_cases":{k:unique[k] for k in favorites if k in unique},
   "canonical_P1_join_summary_SHA256":hashfile(joined/"summary.json"),
 }
 (out/"summary.json").write_text(json.dumps(
   report,indent=2,sort_keys=True,allow_nan=False)+"\n")
 print("P1_REAL_309_STATUS",report["status"],"COMPLETED",
       "REAL_B3_WIDTHS",len(completed),"MISSING_E3_SOLUTIONS",len(missing))
 for k,z in report["priority_cases"].items():
  if z.get("status")=="BLOCKED_NO_OPTIMIZED_E3_FY":
   print("P1_REAL_309_PRIORITY",k,"NO_E3_OPTIMIZED_SOLUTION")
  else:
   print("P1_REAL_309_PRIORITY",k,
      "H2_H1Z_INCLUDED_ONLY",
      z["conditional_H2_H1Z_fraction_in_included_channels_ONLY"],
      "H1_TB_INCLUDED_ONLY",
      z["conditional_H1_tb_fraction_in_included_channels_ONLY"],
      "CASCADE_PROXY_NOT_RATE",
      z["conditional_production_weighted_cascade_proxy_NOT_rate"])
 print("P1_REAL_309_HIGGSTOOLS_EXCLUSIONS",None)
 print("P1_REAL_309_REPORT",out/"summary.json")
 return report

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--e2-csv",type=Path)
 p.add_argument("--e3-jsonl",type=Path)
 p.add_argument("--out",type=Path,
   default=ROOT/"work"/"p1_original_309_E3_B3_charged_included_LO_20261020_v1")
 args=p.parse_args()
 if bool(args.e2_csv)!=bool(args.e3_jsonl):
  p.error("Specify both E2 and E3 paths or neither")
 if args.e2_csv:
  e2,e3=args.e2_csv,args.e3_jsonl
 else:
  e2,e3=locate(ROOT/"work")
 run(e2,e3,args.out.resolve())
if __name__=="__main__":main()
