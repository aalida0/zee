#!/usr/bin/env python3
"""309 source-closed complex Zee lepton flavor SLHA *fragments*, not full cards.

For every original E3 optimized f,Y pair generate 4 blocks:
 ZEEFR, ZEEFI (3 antisymmetric f components),
 ZEEYR, ZEEYI (9 charged lepton Y components).
No scalar parameter card is fabricated: Florentino<->YangWu scalar
potential mapping remains unvalidated. The imaginary parts are always
kept, even if numerically tiny; the real-only original Zee UFO cannot
consume these blocks. Consume ONLY with freshly regenerated complex
Type-II Zee FeynRules UFO after parameter basis validation.

Source SHA and optimized E3 per-point association are verified using
the original hard-gated E2/E3 archiving machinery; previous artifacts
stay untouched.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
from zee_priority1_charged_width_export import (
 read_e3,verify_e2_e3_same_source)
from gateB3_general_zee_charged_lepton_widths import (
 read_b1,complex_matrix)
from zee_p1_prepare_complex_flavor_feynrules import F,Y
from zee_priority1_contracts import hashfile

STATUS="P1_309_ORIGINAL_E3_COMPLEX_FLAVOR_SLHA_FRAGMENTS_NOT_FULL_UFO_CARDS"
BLOCKS=("ZEEFR","ZEEFI","ZEEYR","ZEEYI")

def entries(f,Y):
 f=np.asarray(f,complex);Y=np.asarray(Y,complex)
 if f.shape!=(3,3) or Y.shape!=(3,3):
  raise ValueError("Expected three lepton families and full 3x3 Yukawas")
 if not(np.isfinite(f).all() and np.isfinite(Y).all()):
  raise ValueError("Nonfinite E3 flavor input")
 if not np.allclose(f,-f.T,atol=2e-12,rtol=0):
  raise ValueError("E3 charged singlet tensor f must be antisymmetric")
 if np.max(abs(np.diag(f)))>=2e-12:
  raise ValueError("E3 f has nonzero diagonal")
 anti=[f[0,1],f[0,2],f[1,2]]
 yu=[Y[i,j] for i in range(3) for j in range(3)]
 return {
  "ZEEFR":[float(x.real) for x in anti],
  "ZEEFI":[float(x.imag) for x in anti],
  "ZEEYR":[float(x.real) for x in yu],
  "ZEEYI":[float(x.imag) for x in yu],
 }

def fragment(matrix):
 if set(matrix)!=set(BLOCKS):
  raise ValueError("Missing complete real+imag flavor SLHA blocks")
 rows=["# P1 ORIGINAL E3 COMPLEX Zee Yukawas only",
       "# NOT a complete or validated MadGraph parameter card",
       "# Use ONLY with regenerated split-complex Flavor Zee TypeII UFO"]
 for block in BLOCKS:
  vals=matrix[block]
  if len(vals)!=(3 if "F" in block else 9):
   raise ValueError("Invalid original 3 antisymmetric/9 general-Y source")
  rows.append("BLOCK "+block)
  for i,value in enumerate(vals,1):
   if not math.isfinite(value):
    raise ValueError("Nonfinite complex flavor coefficient")
   rows.append(f"  {i:>2d}  {value:+.17e}")
 return "\n".join(rows)+"\n"

def source_arrays(row,expected_id):
 if row.get("candidate_id")!=expected_id or (
   row.get("diagnostic_status")!=
      "MULTIROOT_PARTIAL_LFV_AND_OPTIMIZED_ORIGINAL_RGE_EVALUATED"):
  raise ValueError("Missing original optimized E3 model source "+expected_id)
 sol=row["D2"]["chosen_optimized_source"]["solution"]
 if sol.get("candidate_id")!=expected_id:
  raise ValueError("E3 optimized f/Y source association mismatch")
 return complex_matrix(sol["f"],"f"),complex_matrix(sol["Y"],"Y")

def write_all(e2,e3,out):
 e2=Path(e2).resolve();e3=Path(e3).resolve();out=Path(out).resolve()
 if out.exists():
  raise ValueError("Never overwrite complex E3-Y artifacts")
 verify_e2_e3_same_source(e2,e3)
 sources,summary=read_e3(e3)
 original=read_b1(e2)
 if len(original)!=309 or set(original)!=set(sources):
  raise ValueError("Original E2/E3 full 309 source identity mismatch")
 # Verify all BEFORE any folder creation, so no partial accepted cohort.
 rendered={};maxfi=0.;maxyi=0.
 for ident in sorted(original):
  f,Y=source_arrays(sources[ident],ident)
  z=entries(f,Y)
  rendered[ident]=fragment(z)
  maxfi=max(maxfi,max(z["ZEEFI"],key=abs),key=abs)
  maxyi=max(maxyi,max(z["ZEEYI"],key=abs),key=abs)
 if len(rendered)!=309:
  raise ValueError("All 309 source matrices required")
 out.mkdir(parents=True,exist_ok=False)
 hashes={}
 for id,text in rendered.items():
  f=out/(id+".slha-fragment")
  f.write_text(text)
  hashes[id]=hashfile(f)
 summary_json={
  "status":STATUS,"models":len(rendered),
  "all_source_E3_complex_fY_preserved":True,
  "max_abs_imag_f":abs(maxfi),"max_abs_imag_Y":abs(maxyi),
  "flavor_blocks":list(BLOCKS),
  "not_complete_MadGraph_param_cards":True,
  "Yukawa_field_basis_and_Zee_scalar_potential_matching_validated":False,
  "original_E2_SHA256":hashfile(e2),
  "original_E3_SHA256":hashfile(e3),
  "source_summary_SHA256":summary["E3_summary_SHA256"],
  "script_SHA256":hashfile(Path(__file__)),
  "per_candidate_flavor_SLHA_fragment_SHA256":hashes,
  "full_Zee_allowed_or_excluded":None,
 }
 (out/"summary.json").write_text(json.dumps(
   summary_json,indent=2,sort_keys=True,allow_nan=False)+"\n")
 return summary_json

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument("--e2-csv",required=True,type=Path)
 parser.add_argument("--e3-jsonl",required=True,type=Path)
 parser.add_argument("--out",required=True,type=Path)
 a=parser.parse_args()
 z=write_all(a.e2_csv,a.e3_jsonl,a.out)
 print("P1_E3_COMPLEX_FLAVOR",z["status"],"MODELS",z["models"],
       "MAX_IMAG_F",z["max_abs_imag_f"],"MAX_IMAG_Y",z["max_abs_imag_Y"],
       "FULL_UFO_CARDS",False,"MODEL_ALLOWED",None)
if __name__=="__main__":main()
