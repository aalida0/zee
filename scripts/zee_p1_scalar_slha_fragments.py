#!/usr/bin/env python3
"""Original 309 E2 Zee scalar spectra -> Yang/Wu Higgs-basis SLHA blocks.

Derives the exact *entire* renormalizable scalar quartic basis rotation,
portal couplings, the muzee charged mixing and external mass inputs.
Random complex SU2 doublet/singlet full-potential closure on EACH
original E2 point is required, not only CP-even eigenvalues.

Output fragments contain MASS(25/225/226/227/228), ZEEINPUTS(1..4),
ZEELAMS(1..7), matching upstream Yang/Wu Parameters.fr (Higgs basis).
Do NOT call these full MG5 param cards: SM inputs and complex f/Y
must be added from matching model; source lepton amplitudes and
Ward/decay crosscode tests still required.
"""
from __future__ import annotations
import argparse,json,math
from pathlib import Path
from gateB3_general_zee_charged_lepton_widths import read_b1
from zee_p1_scalar_higgs_basis_map import check_quartic
from zee_priority1_charged_width_export import verify_e2_e3_same_source
from zee_priority1_contracts import hashfile

STATUS="P1_309_YANGWU_P2_SCALAR_FULL_QUARTIC_BASIS_SLHA_FRAGMENTS_NOT_FIVE_STATE_PHYSICS"
NAMES=("lam2","lam3","lam7","lam8","lam9","lam10","lameta")
def fragment(p,source):
 if not source["internal_mass_and_mu4_muzee_closed"]:
  raise ValueError("Scalar source mass/mu mixing not verified")
 x=source["YangWu_input_ZEEINPUTS"]
 q=source["YangWu_external"]
 if set(q)!=set(NAMES):
  raise ValueError("Wrong Higgs-basis source external ZEELAMS")
 masses={25:125.,225:p["mh2"],226:p["ma"],
         227:p["mH2"],228:p["mH1"]}
 rows=["# Original E2 Zee scalar 2VEV -> YangWu Higgs basis; full SU(2) invariant checks",
       "# NOT a full param_card: fermion/complex Yukawas and SM inputs must be supplied",
       "BLOCK MASS"]
 for pdg,mass in sorted(masses.items()):
  if not math.isfinite(mass) or mass<=0:
   raise ValueError("Nonphysical scalar mass in E2 source")
  rows.append(f" {pdg:>4d} {mass:+.17e}")
 rows.append("BLOCK ZEEINPUTS")
 for idx,key in enumerate(("beta","alpha","alphabeta","phi"),1):
  val=x[key]
  if not math.isfinite(val):raise ValueError("Nonfinite Zee source mixing")
  rows.append(f" {idx:>4d} {val:+.17e} # {key}")
 rows.append("BLOCK ZEELAMS")
 for idx,key in enumerate(NAMES,1):
  val=q[key]
  if not math.isfinite(val):raise ValueError("Nonfinite Zee quartic")
  rows.append(f" {idx:>4d} {val:+.17e} # {key}")
 return "\n".join(rows)+"\n"

def produce(e2,e3,out):
 e2=Path(e2).resolve();e3=Path(e3).resolve();out=Path(out).resolve()
 if out.exists():raise ValueError("Refuse to overwrite scalar basis archive")
 proof=verify_e2_e3_same_source(e2,e3)
 points=read_b1(e2)
 if len(points)!=309:raise ValueError("Source scalar cohort not original 309")
 texts={};info={};worst=0.
 for idx,key in enumerate(sorted(points)):
  spec=check_quartic(points[key],trial_count=24,seed=20261020+idx)
  texts[key]=fragment(points[key],spec)
  worst=max(worst,spec["quartic_max_relative_residual"])
  info[key]={"SU2_quartic_max_relative_residual":
             spec["quartic_max_relative_residual"],
             "YangWu_inputs":spec["YangWu_input_ZEEINPUTS"],
             "YangWu_quartics":spec["YangWu_external"]}
 out.mkdir(parents=True,exist_ok=False)
 hashes={}
 for key,t in texts.items():
  f=out/(key+".slha-fragment")
  f.write_text(t)
  hashes[key]=hashfile(f)
 report={
  "status":STATUS,
  "original_models":309,
  "quartic_full_SU2_complex_doublet_and_charged_singlet_tests":309*24,
  "max_relative_quartic_potential_rotation_residual":worst,
  "YangWu_internal_lam1_lam4_lam5_lam6_mass_matching":True,
  "YangWu_internal_muzee_charge_mixing_matching":True,
  "full_FeynRules_generated_vertices_matched":False,
  "full_E3_lepton_f_and_Y_amplitudes_matched":False,
  "physical_five_state_widths_complete":False,
  "full_Zee_allowed_or_excluded":None,
  "original_E2_SHA256":hashfile(e2),
  "original_E3_SHA256":hashfile(e3),
  "original_E2_E3_matching":proof,
  "source_code_SHA256":hashfile(Path(__file__)),
  "per_candidate_checks":info,
  "per_candidate_scalar_SLHA_fragment_SHA256":hashes,
 }
 (out/"summary.json").write_text(json.dumps(
  report,indent=2,sort_keys=True,allow_nan=False)+"\n")
 return report

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--e2-csv",type=Path,required=True)
 p.add_argument("--e3-jsonl",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 report=produce(a.e2_csv,a.e3_jsonl,a.out)
 print("P1_FULL_SCALAR_QUARTIC_BASIS",STATUS,"POINTS",report["original_models"],
       "INDEPENDENT_SU2_TRIALS",
       report["quartic_full_SU2_complex_doublet_and_charged_singlet_tests"],
       "MAX_RESIDUAL",report["max_relative_quartic_potential_rotation_residual"],
       "UFO_FULL_MATCH",False)
if __name__=="__main__":main()
