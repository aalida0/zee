#!/usr/bin/env python3
"""REAL pre-existing B3 charged-scalar LO widths -> P1 decay *partial* export.

Consumes the original scalar B4/E2 CSV and *actual optimized* E3 f,Y
solutions, checks exact neutrino closure in the B3 model, replaces
the obsolete Type-II tau-nu term, and recomputes H1/H2 INCLUDED modes.
Never populates neutral heavy widths, never assumes unknown channels
are zero, never calls this a full HiggsTools input or a model exclusion.

Input E3 JSONL is source-pinned to its completed summary when supplied
from the original E3 directory. No changes to E2/E3/E7 source outputs.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys,traceback
from pathlib import Path
from zee_priority1_contracts import hashfile,validate_decays

STATUS="P1_E3_SOURCE_CLOSED_B3_GENERAL_ZEE_CHARGED_PARTIAL_WIDTHS_NOT_HIGGSBOUNDS"
SOURCE_E3="E3_all_309_multi_neutrino_partial_LFV_diagnostics.jsonl"
def read_e3(path):
 from zee_gateE3_309_multiroot_flavor_optimized_RGE import STATUS as E3_STATUS
 directory=path.parent
 summary=json.loads((directory/"summary.json").read_text())
 if (summary.get("status")!=E3_STATUS or
     summary.get("evidence_SHA256")!=hashfile(path) or
     summary.get("E2_original_no_deeper_witness_cohort")!=309 or
     summary.get("NO_complete_experimental_Zee_allowed_or_excluded") is not None):
  raise ValueError("Incomplete E3 archive or source SHA mismatch")
 result={}
 with path.open() as f:
  for line in f:
   row=json.loads(line);key=row["candidate_id"]
   if (key in result or row.get("full_Zee_allowed_or_excluded") is not None):
    raise ValueError("E3 duplicate or incorrectly labeled model")
   result[key]=row
 if len(result)!=309:
  raise ValueError("Required complete 309 original E3 source lines")
 return result,{"E3_summary_SHA256":hashfile(directory/"summary.json"),
                "E3_rows_SHA256":hashfile(path),"E3_status":E3_STATUS}

def calculate(point,original,*,backend=None):
 """No independent model reoptimization or fabricated total widths."""
 name=point["id"]
 if original.get("candidate_id")!=name or original.get(
    "full_Zee_allowed_or_excluded") is not None:
  raise ValueError("Selected scalar and E3 Yukawas are different models")
 if original.get("diagnostic_status")!=(
     "MULTIROOT_PARTIAL_LFV_AND_OPTIMIZED_ORIGINAL_RGE_EVALUATED"):
  return {"candidate_id":name,
          "all_physical_decay_channels_enumerated":False,
          "status":"BLOCKED_NO_OPTIMIZED_E3_FY",
          "experimentally_allowed_or_excluded":None}
 src=original["D2"]["chosen_optimized_source"]["solution"]
 if src.get("candidate_id")!=name:
  raise ValueError("E3 optimized f,Y source ID mismatch")
 if backend is None:
  from gateB3_general_zee_charged_lepton_widths import (
       evaluate,complex_matrix)
  from gateA1b_hierarchical_no_seed import target_neutrino_matrix
  target,_=target_neutrino_matrix()
  report=evaluate(point,complex_matrix(src["f"],"f"),
                      complex_matrix(src["Y"],"Y"),target)
 else:
  report=backend(point,src)
 if report.get("candidate_id")!=name or report.get("status")!=(
   "GENERAL_ZEE_LEPTON_WIDTHS_LO_INCLUDED_ONLY_NOT_ALLOWED"):
  raise ValueError("B3 source returned wrong identity or completion status")
 if not(0<=report["neutrino_matrix_closure_eV"]<1e-9):
  raise ValueError("Neutrino target closure invalid")
 widths=report["partial_widths_included_GeV"]
 for state in ("H1","H2"):
  modes=widths[state]
  if "tau_nu_TypeII" in modes or not all(
      q in modes for q in ("e_nu_generalZee","mu_nu_generalZee",
                          "tau_nu_generalZee")):
   raise ValueError("Incorrect B3 general leptonic inventory")
  if not all(math.isfinite(float(v)) and float(v)>=0
             for v in modes.values()):
   raise ValueError("Invalid charged decay partial widths")
  tot=sum(modes.values())
  if not math.isclose(tot,report["totals_included_GeV"][state],
                      rel_tol=1e-10,abs_tol=1e-10):
   raise ValueError("B3 included total width not closed")
 if not math.isclose(
       report["production_weighted_partial_cascade_proxy"],
       math.sin(point["gamma"])**2*
         report["BR_H2_H1Z_included_general_Zee"]*
         report["BR_H1_tb_included_general_Zee"],
       rel_tol=1e-9,abs_tol=1e-12):
  raise ValueError("B3 included-cascade arithmetic inconsistent")
 return {
  "candidate_id":name,
  "status":STATUS,
  "all_physical_decay_channels_enumerated":False,
  "off_shell_and_QCD_treatment_validated":False,
  "independent_width_validation_reference":None,
  "neutral_H_and_A_widths_computed":False,
  "complete_five_state_physical_widths_computed":False,
  "charged_included_LO_GeV":widths,
  "charged_included_totals_NOT_physical_total_GeV":
      report["totals_included_GeV"],
  "B3_selected_neutrino_closure_eV":
      report["neutrino_matrix_closure_eV"],
  "conditional_H2_H1Z_fraction_in_included_channels_ONLY":
      report["BR_H2_H1Z_included_general_Zee"],
  "conditional_H1_tb_fraction_in_included_channels_ONLY":
      report["BR_H1_tb_included_general_Zee"],
  "conditional_production_weighted_cascade_proxy_NOT_rate":
      report["production_weighted_partial_cascade_proxy"],
  "experimentally_allowed_or_excluded":None,
 }

def execute(points,e3_file,out):
 from gateB3_general_zee_charged_lepton_widths import read_b1
 inputs=read_b1(points)
 source,proof=read_e3(e3_file)
 if set(inputs)!=set(source) or len(inputs)!=309:
  raise ValueError("Original scalar points must be precisely the source E3 309 cohort")
 rec=[calculate(inputs[k],source[k]) for k in sorted(source)]
 if any(validate_decays(x,{"h":125.,"H":1.,"A":1.,
                            "H1":inputs[x["candidate_id"]]["mH1"],
                            "H2":inputs[x["candidate_id"]]["mH2"]})
        != "BLOCKED_DECAY_CHANNEL_COMPLETENESS" for x in rec):
  raise ValueError("Partial charged widths were incorrectly promoted to complete HiggsTools")
 payload={
  "schema_version":1,"stage":"decays",
  "provenance":{"source":"original E3 optimized f/Y + B3 full general-Zee leptons and Gate6 boson/quark included LO",
                **proof,"B3_script_SHA256":hashfile(Path(__file__).with_name(
                  "gateB3_general_zee_charged_lepton_widths.py")),
                "Gate6_script_SHA256":hashfile(Path(__file__).with_name("gate6_width_inventory.py")),
                "original_scalar_input_SHA256":hashfile(points),
                "produced_by_script_SHA256":hashfile(Path(__file__))},
  "records":rec,"full_Zee_allowed_or_excluded":None,
  "usable_as_complete_five_state_HiggsBounds_input":False,
 }
 if out.exists():raise ValueError("Never overwrite prior widths export")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(payload,indent=2,allow_nan=False,sort_keys=True)+"\n")
 return {"status":STATUS,"input_original_E3_models":len(rec),
         "actual_B3_charged_models":sum(x["status"]==STATUS for x in rec),
         "missing_complete_five_state_widths":True,
         "HiggsBounds_run_with_partial_widths":False,
         "export_SHA256":hashfile(out),"export":str(out)}

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--points",required=True,type=Path,
                 help="E2 original 309 no-deeper-witness CSV")
 ap.add_argument("--e3",required=True,type=Path,
                 help="Original E3 completed 309 evidence JSONL")
 ap.add_argument("--out",required=True,type=Path)
 a=ap.parse_args()
 result=execute(a.points.resolve(),a.e3.resolve(),a.out.resolve())
 print("P1_CHARGED_WIDTHS",json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":main()
