#!/usr/bin/env python3
"""Source-referenced generator reported pp cross section ingestion (LHE <init>).

This is a *real* upstream MG5/other LHE cross-section reader. It does
NOT generate Zee rates, validate the chosen UFO/model/process, check
mass consistency, establish mode completeness or turn LO cross sections
into NLO/NNLO. Those must be independently implemented and checked.
No zero channels are fabricated. An actual LHE initial subprocess XSECUP
in pb is used; NEVER derive rates from a number of events or from the
H2 doublet-fraction proxy.

Manifest JSON: {"runs":[{"candidate_id":"B4_...", "state":"H2",
  "mode":"pp_to_H2_tb", "lhe":"/home/.../unweighted_events.lhe",
  "process_card":"/home/.../proc_card_mg5.dat",
  "parameter_card":"/home/.../param_card.dat",
  "generator":"MG5_aMC", "model":"YOUR_ACTUAL_VALIDATED_UFO"}]}
All paths must be files. Output is a P1 'production' schema 1 export,
explicitly blocked from complete five-state HiggsTools interpretation.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
from zee_priority1_contracts import IDS,hashfile,validate_production
STATUS="P1_ACTUAL_LHE_INIT_LO_CROSS_SECTIONS_PARTIAL_CHANNELS_NOT_VALIDATED_HIGGSTOOLS"
ENERGIES={13000.0:"LHC13",13600.0:"LHC13p6",14000.0:"LHC14"}
def number(text):
 x=float(text.replace("D","E").replace("d","e"))
 if not math.isfinite(x):
  raise ValueError("Nonfinite LHE initialization number")
 return x
def parse_lhe_init(path):
 """Strict LHE init parser, not an event-weight-normalization guess."""
 with Path(path).open(errors="replace") as f:
  for line in f:
   if line.strip().lower().startswith("<init>"):
    break
  else:
   raise ValueError("No Les Houches <init> block")
  line=f.readline().split()
  if len(line)<10:
   raise ValueError("Malformed LHE beam initialization")
  if (int(line[0])!=2212 or int(line[1])!=2212):
   raise ValueError("Only proton-proton generator inputs supported")
  energy=number(line[2])+number(line[3])
  matched=next((name for value,name in ENERGIES.items()
     if abs(value-energy)<=1.),None)
  if matched is None:
   raise ValueError("Unsupported pp center-of-mass energy")
  count=int(line[9])
  if not(1<=count<=100000):
   raise ValueError("Invalid subprocess count in LHE init")
  subprocesses=[]
  for _ in range(count):
   row=f.readline().split()
   if len(row)<4:raise ValueError("Missing LHE subprocess")
   x,err,xmax=map(number,row[:3]);pid=int(row[3])
   if x<0 or err<0 or xmax<0:
    raise ValueError("Negative LHE cross section, error or max weight")
   subprocesses.append({"sigma_pb":x,
                        "reported_error_pb":err,
                        "max_weight_in_LHE":xmax,"LPRUP":pid})
  if f.readline().strip().lower()!="</init>":
   raise ValueError("Unclosed LHE <init> block")
  return {"collider":matched,
          "partonic_subprocesses_LHE_init":subprocesses,
          "LHE_total_generator_reported_sigma_pb":
             sum(x["sigma_pb"] for x in subprocesses),
          "LHE_subprocess_uncertainties_not_independently_combined":True,
          "LHE_beam_energy_sum_GeV":energy}
def build(manifest,out):
 source=json.loads(Path(manifest).read_text())
 entries=source.get("runs")
 if not isinstance(entries,list) or not entries:
  raise ValueError("Nonempty runs array required")
 by_id={};seen=set()
 for run in entries:
  if not isinstance(run,dict):raise ValueError("Nonobject generator record")
  key=run["candidate_id"];pid=run["state"];mode=run["mode"]
  if (not isinstance(key,str) or not key or pid not in IDS or
      not isinstance(mode,str) or not mode or
      (key,pid,mode) in seen):
   raise ValueError("Invalid or duplicate generator input identity")
  seen.add((key,pid,mode))
  if not run.get("generator") or not run.get("model"):
   raise ValueError("Generator and UFO/model must be named")
  paths={k:Path(run[k]).resolve() for k in
         ("lhe","process_card","parameter_card")}
  if not all(p.is_file() for p in paths.values()):
   raise ValueError("Original generator files missing")
  result=parse_lhe_init(paths["lhe"])
  record=by_id.setdefault(key,{"candidate_id":key,
    "status":STATUS,"particles":{},
    "all_relevant_hadronic_channels_enumerated":False,
    "interference_K_factors_PDF_uncertainties_validated":False,
    "generator_tune_and_validation_reference":None,
    "model_production_amplitude_validation_completed":False,
    "physical_Zee_allowed_or_excluded":None})
  record["particles"].setdefault(pid,{})[mode]={
   "sigma_pb":result["LHE_total_generator_reported_sigma_pb"],
   "collider":result["collider"],"generator_reported_subprocesses":
      result["partonic_subprocesses_LHE_init"],
   "uncertainty_pb":None,
   "generator":run["generator"],"UFO_model_name_UNVERIFIED":run["model"],
   "LHE_input_SHA256":hashfile(paths["lhe"]),
   "process_card_SHA256":hashfile(paths["process_card"]),
   "parameter_card_SHA256":hashfile(paths["parameter_card"]),
   "mass_parameter_and_UFO_gauge_implementation_validated":False,
  }
  if validate_production(record,{})!= "BLOCKED_HADRONIC_CHANNEL_COVERAGE":
   raise ValueError("Partial generator source improperly promoted to complete HiggsTools")
 result={"schema_version":1,"stage":"production",
         "status":STATUS,
         "provenance":{"source":"actual LHE <init> subprocess cross sections",
                       "input_manifest_SHA256":hashfile(manifest),
                       "script_SHA256":hashfile(Path(__file__))},
         "records":[by_id[k] for k in sorted(by_id)],
         "all_five_state_production_channels_covered":False,
         "full_Zee_allowed_or_excluded":None}
 out=Path(out)
 if out.exists():raise ValueError("Refuse overwrite of previous production export")
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(result,allow_nan=False,sort_keys=True,indent=2)+"\n")
 return {"status":STATUS,"input_runs":len(entries),
         "models_with_some_real_generator_LHE_rates":len(by_id),
         "validated_complete_Zee_production":False,
         "output_sha256":hashfile(out)}
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--runs",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 args=p.parse_args()
 print("P1_PRODUCTION_LHE",json.dumps(
   build(args.runs.resolve(),args.out.resolve()),
   sort_keys=True),flush=True)
if __name__=="__main__":main()
