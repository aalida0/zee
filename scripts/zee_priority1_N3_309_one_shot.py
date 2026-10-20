#!/usr/bin/env python3
"""P1 N3: SHA-pinned N2 -> 309 original h/H/A neutral self-pair widths.

Source Gate6 CP-conserving neutral scalar potential generates H->hh,
H->AA and h->AA; cubic couplings are independently checked against
literal invariant scalar-potential polynomial central derivatives for
each model. All previous h/H/A/H1/H2 N2 channels retained bitwise,
new names guaranteed nonoverlapping. The output is still an INCOMPLETE
five-state decay inventory, never a physical total or HiggsBounds input.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
from zee_priority1_contracts import hashfile,validate_decays
from zee_priority1_neutral_bosonic_two_body import (
 STATUS as N2_KERNEL_STATUS)
from zee_priority1_neutral_bosonic_309_one_shot import (
 STATUS as N2_STATUS,PRIOR as PRIOR_N1,PRIOR_CHARGED,ROOT)
from zee_priority1_neutral_309_one_shot import old_sources,PRIORITY
from zee_priority1_neutral_scalar_cubics import (
 STATUS as N3_KERNEL_STATUS,calculate as scalar_cubics)
from gateB3_general_zee_charged_lepton_widths import read_b1
STATUS="P1_N3_309_SOURCE_NEUTRAL_H_HH_AA_WITH_N2_FIVE_STATE_PARTIAL_NOT_COMPLETE"
DEFAULT_N2=ROOT/"work"/"p1_original_309_neutral_bosonic_N2_20261020_v2"
DEFAULT_OUT=ROOT/"work"/"p1_original_309_neutral_scalar_cubics_N3_20261020_v1"
OUTFILE="P1_N3_309_h_H_A_H1_H2_PARTIAL_LO_NOT_COMPLETE.json"

def archived_n2(folder):
 folder=folder.resolve()
 summary=json.loads((folder/"summary.json").read_text())
 file=folder/"P1_N2_309_h_H_A_H1_H2_MORE_PARTIAL_LO_NOT_COMPLETE.json"
 if (summary.get("status")!=N2_STATUS or
     summary.get("original_source_points")!=309 or
     summary.get("real_N2_neutral_bosonic_calculations")!=309 or
     summary.get("N2_Gate6_h_H_charged_cross_cubic_closed")!=309 or
     summary.get("physical_five_state_widths_complete") is not False or
     summary.get("HiggsBounds_95CL_evaluations")!=0 or
     summary.get("experimental_model_allowed_excluded") is not None or
     hashfile(file)!=summary.get("merged_N2_partial_export_SHA256")):
  raise ValueError("N3 archived N2 original 309 completion/status/SHA invalid")
 o=json.loads(file.read_text())
 prov=o.get("provenance",{})
 if (o.get("schema_version")!=1 or o.get("stage")!="decays" or
     o.get("usable_as_complete_HiggsBounds_five_state_input") is not False or
     o.get("full_Zee_allowed_or_excluded") is not None or
     prov.get("N2_bosonic_source_SHA256")!=hashfile(
        ROOT/"scripts"/"zee_priority1_neutral_bosonic_two_body.py") or
     prov.get("N2_runner_SHA256")!=hashfile(
        ROOT/"scripts"/"zee_priority1_neutral_bosonic_309_one_shot.py") or
     prov.get("independent_external_width_validation_completed") is not False or
     any(prov.get(k)!=v for k,v in
         summary.get("source_provenance",{}).items())):
  raise ValueError("N3 original N2 kernel/runner/provenance drift")
 evidence={}
 for q in o.get("records",[]):
  key=q.get("candidate_id")
  if (not isinstance(key,str) or key in evidence or
      q.get("status")!=N2_STATUS or
      q.get("all_physical_decay_channels_enumerated") is not False or
      q.get("complete_Zee_allowed_or_excluded") is not None or
      set(q.get("particles_included_LO_GeV",{}))!=
      {"h","H","A","H1","H2"}):
   raise ValueError("N3 malformed or duplicate real N2 partial decay")
  for state,modes in q["particles_included_LO_GeV"].items():
   if (any(not math.isfinite(float(v)) or float(v)<0
           for v in modes.values()) or
       not math.isclose(sum(modes.values()),float(
         q["included_width_sums_NOT_physical_totals_GeV"][state]),
         rel_tol=1e-10,abs_tol=1e-10)):
    raise ValueError("N3 source N2 per-channel closure invalid")
  evidence[key]=q
 if len(evidence)!=309:
  raise ValueError("N3 must have all 309 N2 original source models")
 return evidence,{
     "archived_N2_summary_SHA256":hashfile(folder/"summary.json"),
     "archived_N2_partial_export_SHA256":hashfile(file),
     "N2_source_provenance":summary["source_provenance"],
 }

def merge_one(point,prior):
 if point["id"]!=prior["candidate_id"]:
  raise ValueError("N3 source scalar and prior N2 decay ID disagreement")
 new=scalar_cubics(point)
 if (new["candidate_id"]!=point["id"] or new["status"]!=N3_KERNEL_STATUS or
     not new["potential_independent_finite_difference_closed"] or
     not new["CP_even_and_CP_odd_masses_source_closed"] or
     new["experimental_Zee_allowed_or_excluded"] is not None):
  raise ValueError("N3 scalar potential independent crosscheck invalid")
 original=prior["particles_included_LO_GeV"]
 combined={k:dict(v) for k,v in original.items()}
 additions=new["neutral_scalar_pair_included_two_body_GeV"]
 for state,more in additions.items():
  if set(more).intersection(combined[state]):
   raise ValueError("N3 duplicate neutral scalar decay mode")
  combined[state].update(more)
 if any(not math.isclose(sum(modes.values()),
         sum(original[state].values())+sum(additions.get(state,{}).values()),
         abs_tol=1e-8,rel_tol=1e-10)
        for state,modes in combined.items()):
  raise ValueError("N3 merged partial width arithmetic inconsistent")
 return {
   "candidate_id":point["id"],"status":STATUS,
   "all_physical_decay_channels_enumerated":False,
   "off_shell_and_QCD_treatment_validated":False,
   "independent_width_validation_reference":None,
   "full_five_state_physical_total_widths_computed":False,
   "particles_included_LO_GeV":combined,
   "included_width_sums_NOT_physical_totals_GeV":{
     s:sum(m.values()) for s,m in combined.items()},
   "N2_original_five_state_LO_GeV":original,
   "N3_new_neutral_scalar_pair_LO_GeV":additions,
   "N3_cubic_couplings_GeV":new["cubic_couplings_GeV"],
   "N3_original_mass_and_independent_potential_derivative_closure":True,
   "cascade_proxy_unchanged_NOT_signal_rate":
     prior["old_cascade_proxy_NOT_signal_rate"],
   "missing_mode_classes":new["missing"],
   "complete_Zee_allowed_or_excluded":None,
 }

def export_payload(rows,source):
 return {
   "schema_version":1,"stage":"decays",
   "provenance":{
     "source":"Archived SHA-matched E2/E3/B3/N1/N2 plus original Gate6 neutral scalar potential and its independent finite-difference numerical check",
     **source,
     "N3_neutral_kernel_SHA256":hashfile(
          ROOT/"scripts"/"zee_priority1_neutral_scalar_cubics.py"),
     "N3_runner_SHA256":hashfile(Path(__file__)),
     "independent_external_UFO_or_MadWidth_validation_completed":False,
    },
   "records":rows,
   "full_Zee_allowed_or_excluded":None,
   "usable_as_HiggsBounds_complete_five_state_input":False,
 }

def execute(n2_dir,charged_dir,out):
 from zee_priority1_cli import main as p1main
 if not ROOT.resolve().is_relative_to(Path("/home")):
  raise ValueError("N3 requires checkout under /home")
 if out.exists():raise ValueError("N3 will not overwrite earlier outputs")
 prev,proof=archived_n2(n2_dir)
 e2,e3,charged,source=old_sources(charged_dir)
 points=read_b1(e2)
 if not(len(points)==len(charged)==len(prev)==309
        and set(points)==set(prev)==set(charged)):
  raise ValueError("N3 previous N2 and scalar model cohorts do not close")
 if any(proof["N2_source_provenance"].get(k)!=v
        for k,v in source.items()):
  raise ValueError("N3 previous N2 original charged E2/E3 source changed")
 records=[merge_one(points[k],prev[k]) for k in sorted(points)]
 if any(validate_decays(q,{})!="BLOCKED_DECAY_CHANNEL_COMPLETENESS"
        for q in records):
  raise ValueError("N3 neutral scalar pairs illegally certified as totals")
 out.mkdir(parents=True,exist_ok=False)
 target=out/OUTFILE
 target.write_text(json.dumps(export_payload(records,{
   **proof,**source}),indent=2,sort_keys=True,allow_nan=False)+"\n")
 joined=out/"joined_five_gate_report"
 if p1main(["--points",str(e2),"--decays",str(target),
            "--out",str(joined)])!=0:
  raise ValueError("N3 canonical P1 five-gate join failed")
 c=json.loads((joined/"summary.json").read_text())
 if (c.get("points")!=309 or
     c.get("per_component_status_counts",{}).get("decays",{}).get(
       "BLOCKED_DECAY_CHANNEL_COMPLETENESS")!=309 or
     c.get("per_candidate_higgstools_API_calls")!=0 or
     c.get("full_Zee_model_allowed_or_excluded") is not None):
  raise ValueError("N3 fail-closed partial HiggsBounds contract invalid")
 byid={q["candidate_id"]:q for q in records}
 focus={}
 for name in PRIORITY:
  entry=byid[name]
  before=prev[name]["included_width_sums_NOT_physical_totals_GeV"]
  after=entry["included_width_sums_NOT_physical_totals_GeV"]
  focus[name]={
   "N2_H_included_not_physical_GeV":before["H"],
   "N3_H_included_not_physical_GeV":after["H"],
   "H_hh_identical_GeV":entry["N3_new_neutral_scalar_pair_LO_GeV"][
     "H"]["h_h_identical"],
   "H_AA_identical_GeV":entry["N3_new_neutral_scalar_pair_LO_GeV"][
     "H"]["A_A_identical"],
   "H_hh_cubic_GeV":entry["N3_cubic_couplings_GeV"]["H_h_h"],
   "H_AA_cubic_GeV":entry["N3_cubic_couplings_GeV"]["H_A_A"],
   "source_cascade_proxy_not_signal_rate":
        entry["cascade_proxy_unchanged_NOT_signal_rate"],
  }
 report={
   "status":STATUS,
   "source_original_309":309,
   "independent_potential_derivative_numerically_checked_309":309,
   "five_state_physical_total_widths_computed":False,
   "HiggsBounds_model_exclusions_computed":False,
   "full_model_allowed_or_excluded":None,
   "prioritized_spectra":focus,
   "source_SHA256":{**proof,**source},
   "export_SHA256":hashfile(target),
   "P1_join_SHA256":hashfile(joined/"summary.json"),
 }
 (out/"summary.json").write_text(json.dumps(
  report,indent=2,sort_keys=True,allow_nan=False)+"\n")
 print("P1_N3_STATUS",STATUS,"COMPLETED 309",
       "INDEPENDENT_NUMERIC_POTENTIAL_CLOSURES 309",
       "HIGGSBOUNDS_EXCLUSIONS 0",flush=True)
 for name,entry in focus.items():
  print("P1_N3_PRIORITY",name,
    "N2_H_INCL",f'{entry["N2_H_included_not_physical_GeV"]:.9g}',
    "N3_H_INCL",f'{entry["N3_H_included_not_physical_GeV"]:.9g}',
    "H_HH",f'{entry["H_hh_identical_GeV"]:.9g}',
    "H_AA",f'{entry["H_AA_identical_GeV"]:.9g}',
    "NO_BR_OR_ALLOWED",flush=True)
 print("P1_N3_REPORT",out/"summary.json",flush=True)
 return report

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument("--prior-n2",type=Path,default=DEFAULT_N2)
 parser.add_argument("--prior-charged",type=Path,default=PRIOR_CHARGED)
 parser.add_argument("--out",type=Path,default=DEFAULT_OUT)
 args=parser.parse_args()
 execute(args.prior_n2.resolve(),args.prior_charged.resolve(),
         args.out.resolve())
if __name__=="__main__":main()
