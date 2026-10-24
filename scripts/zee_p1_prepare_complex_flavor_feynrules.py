#!/usr/bin/env python3
"""Complexify the existing *Type-II modified* Yang/Wu Zee FeynRules flavor.

The public real-only f_ij and Y_ij external FeynRules parameters cannot
represent the general complex lepton Yukawas saved in original E3.
Create twelve complex *internal* parameters whose real and imaginary
parts are independent real external SLHA entries. This changes the
LAGRANGIAN-generated vertices, rather than altering isolated UFO couplings.

The new FeynRules source MUST be freshly re-exported via Mathematica;
a modified Parameters.fr is not itself a UFO. No assertion of exact
Florentino<->Yang/Wu scalar-basis or lepton Y-convention matching.
No reuse of any old UV/R2 NLO counterterms.
"""
from __future__ import annotations
import argparse,hashlib,json,re,shutil
from pathlib import Path
from gate7_prepare_typeii_feynrules import SOURCE_FILES

F=("fem","fet","fmt")
Y=("ylzee","ylzem","ylzet","ylzme","ylzmm",
   "ylzmt","ylzte","ylztm","ylztt")
REQUIRED=F+Y
STATUS="P1_COMPLEX_FLAVOR_FEYNRULES_SOURCE_ONLY_EXPORT_NOT_VALIDATED"

def sha(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def balanced_definition(text,name):
 hits=list(re.finditer(r"(?<![a-zA-Z0-9_])"+re.escape(name)+
     r"\s*==\s*\{",text))
 if len(hits)!=1:
  raise ValueError("Expected exactly one original definition "+name)
 m=hits[0];first=text.index("{",m.start())
 depth=0
 for j in range(first,len(text)):
  if text[j]=="{":depth+=1
  elif text[j]=="}":
   depth-=1
   if not depth:
    return m.start(),j+1,text[first+1:j]
 raise ValueError("Unbalanced FeynRules parameter block "+name)

def patch(text):
 original=text
 rows=[]
 for ix,name in enumerate(REQUIRED):
  start,end,block=balanced_definition(original,name)
  if not re.search(r"\bParameterType\s*->\s*External\b",block):
   raise ValueError(name+" not a source real external")
  group="ZEEYUKAWAF" if name in F else "ZEEYUKAWAY"
  m=re.search(r"\bBlockName\s*->\s*"+group+r"\b",block)
  if m is None:raise ValueError("Source flavor block mismatch "+name)
  c=re.search(r"\bOrderBlock\s*->\s*(\d+)\b",block)
  default=re.search(r"\bValue\s*->\s*([+\-]?(?:\d+\.\d*|\.\d+|\d+)(?:\*\^[+\-]?\d+)?)\s*(?:,|$)",block)
  if not c or not default:
   raise ValueError("No source index/real default for "+name)
  index=int(c.group(1))
  expected=(ix+1 if name in F else ix+1-len(F))
  if index!=expected:raise ValueError("Different source parameter ordering "+name)
  real_block="ZEEFR" if name in F else "ZEEYR"
  imag_block="ZEEFI" if name in F else "ZEEYI"
  interaction="InteractionOrder -> {ZEE,1}," if name in F else ""
  repl=f"""{name} == {{
    ParameterType -> Internal,
    ComplexParameter -> True,
    Value -> (R{name} + I*I{name}),
    {interaction}
    Description -> "Complex E3-compatible {name}: independent real imaginary source"
  }},
  R{name} == {{
    ParameterType -> External, BlockName -> {real_block},
    OrderBlock -> {index}, Value -> {default.group(1)},
    Description -> "real component of {name}"
  }},
  I{name} == {{
    ParameterType -> External, BlockName -> {imag_block},
    OrderBlock -> {index}, Value -> 0,
    Description -> "imaginary component of {name}"
  }}"""
  rows.append((start,end,name,repl))
 # Original definition for each of 12 symbols must be disjoint.
 for (a,z,_,_),(b,e,_,_) in zip(sorted(rows),sorted(rows)[1:]):
  if z>b:raise ValueError("Overlapping Zee parameter definitions")
 for start,end,name,repl in sorted(rows,reverse=True):
  text=text[:start]+repl+text[end:]
 for name in REQUIRED:
  if not re.search(rf"\b{name}\s*==\s*\{{\s*ParameterType\s*->\s*Internal\b",text):
   raise ValueError("Complex internal model patch missing "+name)
  for prefix in ("R","I"):
   if text.count(prefix+name+" == {")!=1:
    raise ValueError("Real/imag split source insertion failed "+name)
 if original==text:raise ValueError("No actual model change")
 return text

def prepare(source,target):
 source=Path(source).resolve();target=Path(target).resolve()
 if not source.is_dir() or source==target or target.exists():
  raise ValueError("Input must be a valid existing derived source; output must be fresh")
 if source in target.parents or str(target).startswith("/data/"):
  raise ValueError("No source nesting or builds in /data")
 for name in SOURCE_FILES:
  if not (source/name).is_file():
   raise ValueError("Original FeynRules source missing "+name)
 # The TypeII step must have really taken place. No raw Yang/Wu source.
 lag=(source/"Lagrangian.fr").read_text()
 if ("Tan[beta]*H2[ii]" not in lag or
     "Cot[beta]*H2bar[jj]" not in lag):
  raise ValueError("Must use our Type-II Higgs-basis modified Zee source")
 src=source/"Parameters.fr"
 changed=patch(src.read_text())
 target.mkdir(parents=True,exist_ok=False)
 for n in SOURCE_FILES:
  shutil.copy2(source/n,target/n)
 (target/"Parameters.fr").write_text(changed)
 report={
  "status":STATUS,
  "parent_model":str(source),
  "real_flavor_parameters":list(REQUIRED),
  "complex_flavor_parameters":list(REQUIRED),
  "new_LHA_blocks":{"f_real":"ZEEFR","f_imag":"ZEEFI",
                    "Y_real":"ZEEYR","Y_imag":"ZEEYI"},
  "parameter_order":{"f":list(F),"Y":list(Y)},
  "no_scalar_basis_parameter_mapping_certified":True,
  "no_UFO_or_MadWidth_generated":True,
  "source_SHA256":{n:sha(source/n) for n in SOURCE_FILES},
  "result_SHA256":{n:sha(target/n) for n in SOURCE_FILES},
  "required_next":["fresh FeynRules UFO export",
                   "complex f and Y numerical source closure",
                   "full neutral and charged scalar trilinear matching",
                   "on-shell MadWidth vs analytic numerical amplitudes",
                   "Ward tests, full SLHA mode inventory and precision corrections"],
 }
 (target/"COMPLEX_FLAVOR_PATCH.json").write_text(
   json.dumps(report,indent=2,sort_keys=True)+"\n")
 return report

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--source",type=Path,default=Path("models/Zee_TypeII_FR"))
 p.add_argument("--out",type=Path,default=Path("models/Zee_TypeII_Complex_FR"))
 args=p.parse_args()
 report=prepare(args.source,args.out)
 print("P1_COMPLEX_FR",report["status"],"N_COMPLEX",len(REQUIRED),
       "SCALAR_MAPPING", "UNVALIDATED")
 print("OUTPUT",args.out.resolve())
if __name__=="__main__":main()
