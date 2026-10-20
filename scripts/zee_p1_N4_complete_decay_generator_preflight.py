#!/usr/bin/env python3
"""Actual 309 E3-> complex FeynRules/MadWidth readiness preflight.

One command creates all 309 real+imag flavor SLHA BLOCK fragments from
the original completed E2/E3 archive, builds the complex Type-II
FeynRules source *if the original modified source is present*, and
audits existing LO UFO without inventing scalar basis parameters.
This intentionally does not call MadWidth until a valid FeynRules
UFO/point-specific parameter card and exact source-consistency checks
exist. Preflight status explicitly enumerates outstanding blockers.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from zee_priority1_charged_width_export import (
 verify_e2_e3_same_source)
from zee_priority1_neutral_309_one_shot import old_sources
from zee_p1_e3_complex_flavor_fragments import write_all
from zee_p1_prepare_complex_flavor_feynrules import prepare
from zee_p1_ufo_model_audit import audit
from zee_priority1_contracts import hashfile

ROOT=Path(__file__).resolve().parents[1]
PRIOR_CHARGED=ROOT/"work"/"p1_original_309_E3_B3_charged_included_LO_20261020_v1"
DEFAULT_OUTPUT=ROOT/"work"/"p1_auto_decay_full_ufo_N4_20261020_v1"
STATUS="P1_EXTERNAL_DECAY_AUTOMATION_E3_PREPARED_UFO_MAPPING_AND_PRECISION_NOT_COMPLETE"

def execute(prior,out,typeii_source,ufo):
 prior=prior.resolve();out=out.resolve()
 if not ROOT.resolve().is_relative_to(Path("/home")):
  raise ValueError("Only run source/build from /home")
 if out.exists():raise ValueError("Never overwrite original output")
 e2,e3,charged,sourceproof=old_sources(prior)
 if len(charged)!=309:raise ValueError("Missing original E3/B3 309 source")
 verify_e2_e3_same_source(e2,e3)
 out.mkdir(parents=True,exist_ok=False)
 flavor=write_all(e2,e3,out/"E3_complex_flavor_309")
 fr_info={"status":"MISSING_TYPEII_FEYNRULES_SOURCE_ON_AF",
          "out_path":None}
 if typeii_source is not None and typeii_source.is_dir():
  dest=out/"Zee_TypeII_Complex_FR_SOURCE_ONLY"
  fr=prepare(typeii_source,dest)
  fr_info={"status":fr["status"],"out_path":str(dest),
           "source_parameters_SHA256":fr["source_SHA256"],
           "generated_parameters_SHA256":fr["result_SHA256"],
           "FeynRules_UFO_export_executed":False}
 ufo_info={"status":"NO_VALIDATED_FRESH_COMPLEX_ZEE_UFO_PRESENT",
           "full_Zee_E3_MadWidth_ready":False}
 if ufo is not None:
  z=audit(ufo)
  ufo_info={"status":z["status"],"audit":z,
            "full_Zee_E3_MadWidth_ready":False}
 report={
   "status":STATUS,
   "source_original_309":309,
   "source_E2_SHA256":hashfile(e2),
   "source_E3_SHA256":hashfile(e3),
   "original_charged_E3_source_provenance":sourceproof,
   "real_309_complex_lepton_Y_f_exported":True,
   "flavor_export_summary_SHA256":hashfile(
     out/"E3_complex_flavor_309"/"summary.json"),
   "max_abs_E3_Y_imaginary":flavor["max_abs_imag_Y_UFO_convention"],
   "max_abs_E3_f_imaginary":flavor["max_abs_imag_f"],
   "feynrules_complex_typeII_source":fr_info,
   "ufo_audit":ufo_info,
   "full_scalar_potential_Higgs_basis_mapping_validated":False,
   "independent_exact_tree_width_MadWidth_crosscode_validation":False,
   "modern_NNLO_bsgamma_complete":False,
   "complete_LFV_and_muon_conversion":False,
   "five_state_full_HiggsTools_production_and_widths_complete":False,
   "full_Zee_allowed_or_excluded":None,
   "blocking_next":["FeynRules export of full complex TypeII Zee UFO",
     "numerical Florentino physical-to-Higgs-basis scalar/trilinear mapping",
     "source-wise point E3 Yukawa amplitude normalization matching",
     "MG5 MadWidth two/three-body widths with matched full parameter card",
     "physical SM-loop/QCD corrections and independent amplitude validation",
     "actual production amplitudes and HiggsTools",
     "modern B->Xs gamma, complete LFV, neutrino full likelihood"],
 }
 (out/"summary.json").write_text(
    json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
 print("P1_N4_STATUS",STATUS,"E3_COMPLEX_FLAVOR_EXPORTED 309",
       "MAX_IMAG_Y",report["max_abs_E3_Y_imaginary"],
       "FR_SOURCE",fr_info["status"],
       "UFO",ufo_info["status"],
       "COMPLETE_HIGGSBOUNDS",False,flush=True)
 print("P1_N4_REPORT",out/"summary.json",flush=True)
 return report

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--prior-charged",type=Path,default=PRIOR_CHARGED)
 p.add_argument("--out",type=Path,default=DEFAULT_OUTPUT)
 p.add_argument("--typeii-source",type=Path,default=ROOT/"models"/"Zee_TypeII_FR")
 p.add_argument("--ufo",type=Path,default=None)
 args=p.parse_args()
 execute(args.prior_charged,args.out,args.typeii_source,args.ufo)
if __name__=="__main__":main()
