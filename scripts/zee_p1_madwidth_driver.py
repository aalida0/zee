#!/usr/bin/env python3
"""MadWidth on an actual complete Zee UFO + actual parameter card.

Uses MG5 documented syntax:
 compute_widths 25 225 226 227 228 --path=INPUT --output=OUTPUT
   --body_decay=3
No fake event generation or widths. Requires entire model already
compiled by FeynRules, with 24 E3 complex-flavor inputs and both
charged tb + offdiagonal Z interactions. This script DOES NOT map
a Florentino scalar spectrum onto the Higgs-basis UFO: an external
point-specific param card must already be independently validated.

MadWidth computes automatic on-shell tree and selected multi-body
decays of the Lagrangian model represented by THAT card; it cannot
create unknown loop/QCD/NNLO amplitudes. Outputs never accepted as
full physical model exclusions automatically.
"""
from __future__ import annotations
import argparse,hashlib,json,math,subprocess
from pathlib import Path
from zee_p1_ufo_model_audit import audit
from zee_priority1_contracts import hashfile

STATUS="P1_MADWIDTH_AUTOMATED_SOURCE_MODEL_DECAY_2_AND_3BODY_DIAGNOSTIC_NOT_PRECISION_EXCLUSION"
PDGS=(25,225,226,227,228)
OUT_CARD="Zee_MadWidth_2and3body.slha"

def make_deck(ufo,source,out):
 ufo=Path(ufo).resolve();source=Path(source).resolve()
 out=Path(out).resolve()
 if not source.is_file():
  raise ValueError("Need independently matched input parameter card")
 if out.exists():raise ValueError("Never overwrite existing MadWidth job output")
 if not(str(ufo).startswith("/home/") and
        str(source).startswith("/home/") and
        str(out).startswith("/home/")):
  raise ValueError("CERN AF MadWidth run/source/output must be under /home")
 result=audit(ufo)
 if not result["static_necessary_conditions_pass"]:
  raise ValueError("Cannot run E3 Zee model with incomplete vertices or real-only flavor UFO")
 deck=(f"set automatic_html_opening False\n"
       f"import model {ufo}\n"
       f"compute_widths {' '.join(str(p) for p in PDGS)} "
       f"--path={source} --output={out/OUT_CARD} --body_decay=3\n")
 return deck,result

def parse_widths(card):
 """Parse genuine SLHA DECAY output; preserve reported channels exactly."""
 blocks={};curr=None
 for original in Path(card).read_text().splitlines():
  row=original.split("#",1)[0].strip().split()
  if not row:continue
  if row[0].upper()=="DECAY":
   if len(row)<3:raise ValueError("Malformed SLHA DECAY")
   key=int(row[1]);width=float(row[2].replace("D","E"))
   if key in blocks or not math.isfinite(width) or width<0:
    raise ValueError("Duplicate or invalid SLHA decay total")
   curr=key;blocks[key]={"total_width_GeV":width,"modes":[]}
   continue
  if row[0].upper() in {"BLOCK","QNUMBERS"}:
   curr=None
   continue
  if curr is not None:
   try:
    br=float(row[0].replace("D","E"))
    daughters=int(row[1])
   except (ValueError,IndexError):
    raise ValueError("Malformed MadWidth SLHA decay channel")
   if daughters<=0 or len(row)!=2+daughters:
    raise ValueError("Wrong daughter count in MadWidth channel")
   pdgs=tuple(int(v) for v in row[2:])
   if not math.isfinite(br) or not 0<=br<=1+1e-9:
    raise ValueError("Invalid MadWidth branching fraction")
   blocks[curr]["modes"].append({"daughters":pdgs,
       "BR_in_MadWidth_model_only":br,
       "partial_width_GeV":br*blocks[curr]["total_width_GeV"]})
 for pid in PDGS:
  if pid not in blocks:
   raise ValueError("MadWidth did not compute scalar PDG "+str(pid))
  record=blocks[pid]
  if record["total_width_GeV"]>0:
   ratios=sum(v["BR_in_MadWidth_model_only"] for v in record["modes"])
   if not record["modes"] or not math.isclose(ratios,1.,rel_tol=2e-3,abs_tol=2e-3):
    raise ValueError("Incomplete MadWidth table vs its own reported model total")
 return blocks

def run(ufo,source,out,mg5=None):
 out=Path(out).resolve()
 deck,model=make_deck(ufo,source,out)
 if mg5 is not None:
  mg5=Path(mg5).resolve()
  if not mg5.is_file():
   raise ValueError("Actual MG5 executable not found")
 out.mkdir(parents=True,exist_ok=False)
 (out/"compute_widths.mg5").write_text(deck)
 initial={
  "status":STATUS,"source_UFO_audit":model,
  "source_param_card_SHA256":hashfile(source),
  "MG5_command_source_SHA256":hashfile(out/"compute_widths.mg5"),
  "source_scalar_basis_and_flavor_normalization_matched":False,
  "physics_five_state_complete":False,
  "model_allowed_or_excluded":None,
 }
 if mg5 is None:
  (out/"manifest.json").write_text(
     json.dumps({**initial,"MadWidth_executed":False},
                indent=2,sort_keys=True)+"\n")
  return {"status":STATUS,"MadWidth_executed":False,"out":str(out)}
 with (out/"mg5_madwidth.log").open("w") as log:
  proc=subprocess.run([str(mg5),str(out/"compute_widths.mg5")],
    cwd=out,stdout=log,stderr=subprocess.STDOUT,check=False)
 if proc.returncode!=0 or not(out/OUT_CARD).is_file():
  (out/"failed.json").write_text(json.dumps({
    **initial,"MadWidth_return_code":proc.returncode,
    "model_allowed_or_excluded":None},indent=2,sort_keys=True)+"\n")
  raise RuntimeError("MadWidth failed; inspect source-pinned log, no physical prediction")
 rates=parse_widths(out/OUT_CARD)
 (out/"manifest.json").write_text(json.dumps({
   **initial,"MadWidth_executed":True,
   "MG5_binary_SHA256":hashfile(mg5),
   "MadWidth_output_card_SHA256":hashfile(out/OUT_CARD),
   "source_model_only_decay_tables":rates,
   "physical_Zee_E3_consistency_validated":False,
   "source_model_total_widths_are_not_matched_Zee_physical_totals":True
 },indent=2,sort_keys=True)+"\n")
 return {"status":STATUS,"MadWidth_executed":True,
         "decay_tables":len(rates),"out":str(out)}

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--ufo",required=True,type=Path)
 ap.add_argument("--param-card",required=True,type=Path)
 ap.add_argument("--out",required=True,type=Path)
 ap.add_argument("--mg5-bin",type=Path,
   help="Optional: actually execute MG5/MadWidth; otherwise write validated deck")
 a=ap.parse_args()
 result=run(a.ufo,a.param_card,a.out,a.mg5_bin)
 print("P1_MADWIDTH",json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
