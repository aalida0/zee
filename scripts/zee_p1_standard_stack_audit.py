#!/usr/bin/env python3
"""Audit EXISTING HEP packages and model readiness before BSMArt scans.

This does not pretend installing an external code or deriving the Zee
Lagrangian from a JSON flag. The deployment dependency graph is:
 SARAH model -> generated SPheno and FlexibleSUSY/FlexibleDecay
 independent FeynRules Zee model -> MG5/MadWidth
  -> BSMArt orchestrates + HiggsTools + Vevacious++.
Using two calculation programs does NOT make their common SARAH model
definition independent; demand separate FeynRules source amplitude tests.
No physical Zee point is marked allowed/excluded by this utility.
"""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,os,shutil,subprocess
from pathlib import Path

STATUS="P1_EXTERNAL_STANDARD_TOOLS_PROBE_NOT_A_COMPLETED_MODEL_OR_EXCLUSION"
SARAH_FILES=("Model.m","parameters.m","particles.m","SPheno.m")
COMMANDS={
 "wolfram_kernel":("math","wolframscript"),
 "BSMArt_scan":("BSMArt",),
 "BSMArt_prepare_model":("BSMArt-PrepareModel",),
 "BSMArt_package_check":("BSMArt-CheckPackages",),
 "MG5":("mg5_aMC",),
 "gfortran":("gfortran",),
 "cmake":("cmake",),
}
MODULES={"bsmart":"bsmart","HiggsTools":"Higgs","flavio":"flavio"}
STAGES={
 "model_definition":"requires tested SARAH non-SUSY Zee model with complete f, Y and two charged states",
 "spectra_and_flavor":"generated SPheno+FlavorKit; two-loop LFV and modern b->s gamma beyond default modules separately",
 "second_spectrum_decay":"FlexibleSUSY/FlexibleDecay generated from SAME SARAH model (correlated source)",
 "independent_vertices":"FeynRules LO UFO from SEPARATE Zee Lagrangian; source-mapped vertices",
 "collider":"MG5/MadWidth and actual hadronic cross sections from mapped UFO",
 "Higgs_direct":"HiggsTools and real production+complete decay tables",
 "vacuum":"Vevacious++ or VacStab used on correct scalar potential",
 "scan":"BSMArt with explicit dependency gates and staged sampling",
}
def digest(path):
 return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def command_info(names,override=None):
 if override:
  path=Path(override).expanduser().resolve()
  found=str(path) if path.is_file() else None
 else:
  found=next((shutil.which(s) for s in names if shutil.which(s)),None)
 return {"detected":found is not None,"path":found,
         "executable":(os.access(found,os.X_OK) if found else False),
         "sha256":digest(found) if found and Path(found).is_file()
                    and Path(found).stat().st_size<100_000_000 else None}

def sarah_model_info(root):
 if root is None:
  return {"detected":False,"source_files_present":[],"model_validated":False}
 root=Path(root).expanduser().resolve()
 found=[name for name in SARAH_FILES if (root/name).is_file()]
 return {"detected":root.is_dir(),
         "path":str(root),
         "source_files_present":found,
         "all_four_source_files_present":len(found)==4,
         "source_sha256":{name:digest(root/name) for name in found},
         "model_validated":False,
         "reason":"File presence is not a SARAH mass, gauge, Yukawa, FlavorKit or Ward audit"}

def tool_status(args):
 sources={"SARAH_model":sarah_model_info(args.sarah_model_dir)}
 if args.sarah_package_dir:
  f=Path(args.sarah_package_dir).expanduser().resolve()/"SARAH.m"
  sources["SARAH_package"]={"present":f.is_file(),
                "sha256":digest(f) if f.is_file() else None,
                "path":str(f)}
 binaries={k:command_info(v) for k,v in COMMANDS.items()}
 overrides={
  "BSMArt_scan":args.bsmart_bin,
  "MG5":args.mg5_bin,
 }
 for k,path in overrides.items():
  if path is not None:
   binaries[k]=command_info(COMMANDS[k],path)
 for name,path in (
   ("SPheno_Zee",args.spheno_model_executable),
   ("FlexibleSUSY_Zee",args.flexible_model_executable),
   ("Vevacious",args.vevacious_bin)):
  binaries[name]=command_info((),path) if path else command_info(())
 modules={}
 for name,module in MODULES.items():
  try:
   spec=importlib.util.find_spec(module)
   has=spec is not None
  except (ImportError,ValueError,AttributeError):
   has=False
  modules[name]={"import_spec_found":has}
 prereq={
   "SARAH_model_full_source_files":sources["SARAH_model"].get(
       "all_four_source_files_present",False),
   "SPheno_model_binary":binaries["SPheno_Zee"]["executable"],
   "FlexibleSUSY_model_binary":binaries["FlexibleSUSY_Zee"]["executable"],
   "BSMArt_binary":binaries["BSMArt_scan"]["executable"],
   "MG5_binary":binaries["MG5"]["executable"],
 }
 return {
  "status":STATUS,
  "commands":binaries,"python_modules":modules,
  "sources":sources,"stage_dependencies":STAGES,
  "model_compile_and_physical_checks_passed":False,
  "all_independent_external_physics_backends_connected":False,
  "source_model_usable_for_Zee_exclusions":False,
  "scan_of_millions_of_Zee_models_launched":False,
  "full_Zee_allowed_or_excluded":None,
  "prerequisites_detected_NOT_validated":prereq,
  "required_validation":{
     "SARAH":"CheckModel and exact h/H/A,H1/H2 spectra, potential, neutrino f/Y",
     "SPheno":"compile model; exact flavor structures; test masses/decays/RGEs",
     "FlavorKit":"check each dipole/conversion operator; missing Barr-Zee and matched modern bsgamma",
     "FlexibleDecay":"compare same-parameter spectra and LO partial modes to SPheno, not independent SARAH Lagrangian",
     "FeynRules_MG5":"compare complex Yukawa and charged/neutral vertices using independently authored Yang/Wu source",
     "HiggsTools":"complete modes and real production inputs",
     "Vevacious":"charge-breaking fields and tunneling lifetime",
     "BSMArt":"launch after a validated model, maintain error-code and provenance screens",
  },
 }

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--sarah-model-dir",type=Path)
 p.add_argument("--sarah-package-dir",type=Path)
 p.add_argument("--spheno-model-executable",type=Path)
 p.add_argument("--flexible-model-executable",type=Path)
 p.add_argument("--bsmart-bin",type=Path)
 p.add_argument("--mg5-bin",type=Path)
 p.add_argument("--vevacious-bin",type=Path)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 if a.out.exists():p.error("Output exists; no overwrite")
 res=tool_status(a)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
 print("P1_STANDARD_TOOLCHAIN",res["status"])
 for name,item in res["commands"].items():
  print("P1_TOOL",name,"FOUND" if item["detected"] else "NOT_FOUND",
        "EXEC" if item["executable"] else "NOT_EXEC")
 print("P1_SARAH_MODEL_SOURCE_FOUND",res["sources"]["SARAH_model"].get(
       "all_four_source_files_present",False))
 print("P1_FULL_ZEE_ALLOWED_OR_EXCLUDED",None)
 print("P1_STANDARD_TOOLCHAIN_REPORT",a.out)
if __name__=="__main__":main()
