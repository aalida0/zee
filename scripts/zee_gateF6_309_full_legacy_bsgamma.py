#!/usr/bin/env python3
"""F6: 309-source original Zee full LEGACY SuperIso v5 inclusive b->s gamma.

Uses source-pinned A1U helper-reload-interposed original SuperIso C kernel:
mixed two charged Wilson arrays LO/NLO/NNLO and primed, RGE, full inclusive
bsgamma observable. Anchors to previously SUCCESSFUL A1U benchmark and A1R
SM/single TypeII reference and crossjoins every F5 source row.

This is *legacy vendor physics*, not validated 2026 updated NNLO theory,
not calibrated B->Xs gamma 95% likelihood and NEVER physical exclusion.
Original E2-E7/F5 work dirs treated as READ ONLY. Fatal on any mismatch.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,os,shutil,subprocess,sys,traceback
from pathlib import Path
from gateA1u_run_legacy_two_state_br import (
 audit_affine_internal_matching,parse_driver)
from gateA1r_run_br_pilot import check_superiso_source
from zee_gateF5_309_source_pinned_C7_dipole_pareto import (
 source_e7, sha, finite,near, STATUS as F5_IMPORT_STATUS)
ROOT=Path(__file__).resolve().parents[1]
STATUS="F6_309_TWO_CHARGED_LEGACY_SUPERISO_FULL_INCLUSIVE_BR_NOT_MODERN_CL"
BLOCK="F6_FAIL_CLOSED_NO_PHYSICAL_EXCLUSION"
F5_NAME="F5_309_Zee_strict_dipole_projector_NO_BR.jsonl"
PRIORITY=("B4_0004143","B4_0003582","B4_0003854",
          "B4_0004380","B4_0002315","B4_0017640")
FIXED_A1U=(300.,700.,1.089,5.597170833164245)
def load(p):return json.loads(Path(p).read_text())
def save(p,record):Path(p).write_text(
 json.dumps(record,sort_keys=True,indent=2,allow_nan=False)+"\n")

def input_f5(folder,e7):
 s=load(folder/"summary.json");m=load(folder/"manifest.json")
 if (s.get("status")!=F5_IMPORT_STATUS or s.get("source_models")!=309 or
     s.get("F4b_source_matched_controls")!=8 or
     s.get("complete_EOS_NLO_matrix_elements_and_B_to_Xs_gamma_BR") is not False
     or s.get("full_model_allowed_or_excluded") is not None or
     m.get("status")!=s["status"] or m.get("source")!=s["source_provenance"] or
     m.get("summary_SHA256")!=sha(folder/"summary.json") or
     s.get("source_provenance",{}).get("F5_driver_SHA256")!=sha(
      ROOT/"scripts/zee_gateF5_309_source_pinned_C7_dipole_pareto.py")):
  raise ValueError("F5 archived source/version/model completeness contract failed")
 for name,expected in s["output_sha256"].items():
  if sha(folder/name)!=expected:raise ValueError("F5 SHA evidence changed "+name)
 rows={}
 with (folder/F5_NAME).open() as h:
  for ln in h:
   row=json.loads(ln);k=row["candidate_id"]
   if k in rows or k not in e7 or row.get("model_excluded_allowed") is not None:
    raise ValueError("F5 source duplicates/missing/false allowed")
   for a,b,label in (
      (row["mH1_GeV"],e7[k]["mH1_GeV"],"light mass"),
      (row["mH2_GeV"],e7[k]["mH2_GeV"],"heavy mass"),
      (row["tanbeta"],e7[k]["tanbeta"],"tanbeta"),
      (row["gamma"],e7[k]["gamma"],"charged mixing"),
      (row["E7_included_channel_cascade_proxy_NOT_signal"],
       e7[k]["charged_cascade_included_channel_proxy_NOT_physical_rate"],
       "corrected cascade"),
      (row["E6_HiggsSignals_delta_chi2_NOT_CL"],
       e7[k]["HS_delta_chi2_E6_vs_fixed_SM"],"HiggsSignals chi2")):
    near(a,b,k+" "+label,atol=1e-11,rtol=1e-11)
   rows[k]=row
 if len(rows)!=309 or set(rows)!=set(e7):
  raise ValueError("F5 and E7 original model cohort differs")
 return rows,{"F5_summary_SHA256":sha(folder/"summary.json"),
              "F5_manifest_SHA256":sha(folder/"manifest.json"),
              "F5_rows_SHA256":sha(folder/F5_NAME)}

def validate_a1u(a1u_path,a1r_path,vendor,manifest):
 a=load(a1u_path)
 if (a.get("status")!="GATE_A1U_FULL_LEGACY_SUPERISO_TWO_STATE_BR_ENDPOINT_CLOSED_NOT_2026_EXCLUSION"
     or a.get("all_A1R_physical_endpoint_checks_pass") is not True or
     a.get("full_legacy_two_state_BR_calculated") is not True or
     a.get("MODERN_2026_full_NNLO_two_state_BR_validated") is not False or
     a.get("flavour_error_budget_validated") is not False or
     a.get("Zee_model_allowed") is not None or a.get("Zee_model_excluded") is not None):
  raise ValueError("A1U real AF original control not successfully source validated")
 af=a["affine_internal_CW_source_contract"]
 actual_a1m=check_superiso_source(vendor,manifest)
 actual=audit_affine_internal_matching(vendor)
 if (actual!=af or actual.get("internal_CW_mode")!="helper_reload" or
     actual_a1m!=a["compiled_static_vendor"]["source_pinned_vendor"]):
  raise ValueError("A1U pinned SuperIso internal matching source changed")
 dr=ROOT/"scripts/gateA1u_legacy_two_state_br.c"
 lib=vendor/"src/libsuperiso.a"
 if (not lib.is_file() or lib.stat().st_mtime_ns<max(
        (vendor/"src/wilson.c").stat().st_mtime_ns,
        (vendor/"src/bsgamma.c").stat().st_mtime_ns) or
     sha(dr)!=a["compiled_static_vendor"]["build"]["driver_SHA256"] or
     sha(lib)!=a["compiled_static_vendor"]["build"]["library_SHA256"]):
  raise ValueError("A1U original C driver/library SHA or mtime changed")
 p=a["benchmark"]
 for x,y,label in zip((p["mH1_GeV"],p["mH2_GeV"],p["gamma_rad"],p["tanbeta"]),
                      FIXED_A1U,("mH1","mH2","gamma","tanbeta")):
  near(x,y,"historical A1U control "+label,atol=1e-10,rtol=1e-12)
 old=load(a1r_path)
 if (old.get("status")!="GATE_A1R_SINGLE_TYPEII_OBSERVABLE_BR_PILOT_AWAITING_INDEPENDENT_ERROR_BUDGET"
     or a["SM_BR_legacy"]<=0 or
     a["SM_BR_legacy"]!=old["SM_model_BR"]):
  raise ValueError("A1U historical SM/A1R closure changed")
 return a,{"historical_A1U_SHA256":sha(a1u_path),
           "historical_A1R_SHA256":sha(a1r_path),
           "A1U_C_source_SHA256":sha(dr),
           "A1M_libsuperiso_static_SHA256":sha(lib),
           "A1M_wilson_source_SHA256":actual_a1m["A1M_patched_wilson_SHA256"],
           "A1U_internal_matching_mode":actual["internal_CW_mode"]}

def build(vendor,out):
 dr=ROOT/"scripts/gateA1u_legacy_two_state_br.c"
 lib=vendor/"src/libsuperiso.a"
 cc=shutil.which("gcc")
 if not cc:raise ValueError("gcc missing")
 exe=out/"f6_pinned_A1U_inclusive_br"
 args=[cc,"-O2","-std=gnu99","-Wall","-Wextra",
       "-I"+str(vendor/"src"),str(dr),"-Wl,--wrap=CW_calculator",
       str(lib),"-lm","-o",str(exe)]
 run=subprocess.run(args,capture_output=True,text=True,timeout=90)
 if run.returncode:
  raise ValueError("A1U F6 compile fails: "+run.stderr[-3000:])
 return exe,{"command":args,"binary_sha256":sha(exe),
             "source_sha256":sha(dr),"vendor_library_sha256":sha(lib),
             "compiler_warning_excerpt":run.stderr[-1500:]}

def run_pinned(exe,m1,m2,g,t,mode,call=subprocess.run):
 vals=(finite(m1,"light mass"),finite(m2,"heavy mass"),
       finite(g,"gamma"),finite(t,"tanbeta"))
 if not (200<=m1<=m2<=10000 and 0<=g<=math.pi/2 and .25<=t<=100):
  raise ValueError("F6 physical original point outside validated A1U inputs")
 command=[str(exe.resolve()),*[f"{a:.17g}" for a in vals],mode]
 res=call(command,capture_output=True,text=True,timeout=90)
 if res.returncode:raise RuntimeError(
   "F6 failed original SuperIso source at "+str(vals)+" "+
   res.stderr[-1600:]+res.stdout[-1600:])
 obj=parse_driver(res.stdout,m1,m2,g,t,expected_mode=mode)
 if (obj["high_scale_fixed_RG_context_max_abs_delta_H1"]>1e-10 or
     obj["high_scale_fixed_RG_context_max_abs_delta_H2"]>1e-10):
  raise ValueError("A1U high RG context did not close")
 for k in ("SM_minus_H1","SM_minus_H2"):
  if abs(obj["fixed_low_context_numeric_separation"][k])>2e-12:
   raise ValueError("A1U internal model context not invariant")
 return obj,res.stdout

def benchmark_closure(exe,old,mode):
 sample,raw=run_pinned(exe,*FIXED_A1U,mode)
 near(sample["full_legacy_Zee_BR"],old["benchmark"]["full_legacy_Zee_BR"],
      "historical A1U full inclusive benchmark",rtol=2e-8,atol=2e-12)
 for key in ("H1","H2","SM"):
  near(sample["full_single_state_BR"][key],
       old["benchmark"]["full_single_state_BR"][key],
       "historical A1U single control "+key,rtol=2e-8,atol=2e-12)
 for m1,m2,g,k in ((300.,700.,0.,"gamma_0_endpoint"),
                   (300.,700.,math.pi/2,"gamma_pi2_endpoint"),
                   (700.,700.,1.089,"equal_mass_gamma_endpoint")):
  row,_=run_pinned(exe,m1,m2,g,FIXED_A1U[3],mode)
  near(row["full_legacy_Zee_BR"],old[k]["full_legacy_Zee_BR"],
       "A1U published/AF "+k,atol=2e-12,rtol=2e-8)
 return {"fixed_A1U":sample["full_legacy_Zee_BR"],
         "historical_A1U":old["benchmark"]["full_legacy_Zee_BR"],
         "legacy_SM_reference":sample["full_single_state_BR"]["SM"],
         "all_four_historical_A1U_controls_closed":True}

def apply(f5,exe,mode,SM):
 result=[]
 for idx,key in enumerate(sorted(f5),1):
  src=f5[key]
  br,raw=run_pinned(exe,src["mH1_GeV"],src["mH2_GeV"],
                    src["gamma"],src["tanbeta"],mode)
  near(br["full_single_state_BR"]["SM"],SM,"fixed SM baseline",
       atol=3e-11,rtol=1e-9)
  row={
    "candidate_id":key,
    "mH1_GeV":src["mH1_GeV"],"mH2_GeV":src["mH2_GeV"],
    "gamma":src["gamma"],"tanbeta":src["tanbeta"],
    "HiggsSignals_E6_delta_chi2_NOT_CL":
         src["E6_HiggsSignals_delta_chi2_NOT_CL"],
    "E7_included_cascade_proxy_NOT_physical_rate":
         src["E7_included_channel_cascade_proxy_NOT_signal"],
    "F5_strict_C7eff_projector_not_rate":
         src["Q7eff_NP_strictly_truncated_LO_plus_NLO"],
    "BR_BtoXsgamma_legacy_SuperIso_two_state":
         br["full_legacy_Zee_BR"],
    "BR_BtoXsgamma_legacy_SuperIso_SM_reference":SM,
    "legacy_BR_NP_minus_SM":br["full_legacy_Zee_BR"]-SM,
    "legacy_BR_ratio_to_same_legacy_SM":br["full_legacy_Zee_BR"]/SM,
    "A1U_source_diagnostics":br,
    "modern_2026_NNLO_and_likelihood_validated":False,
    "full_Zee_allowed_excluded":None,
  }
  result.append(row)
  print("F6_LEGACY_FULL_BR",idx,"/309",key,
        "BR_LEGACY",f"{row['BR_BtoXsgamma_legacy_SuperIso_two_state']:.12g}",
        "NP_MINUS_SM_LEGACY",f"{row['legacy_BR_NP_minus_SM']:.12g}",
        "F5_DIP_ONLY",f"{row['F5_strict_C7eff_projector_not_rate']:.7g}",
        "NOT_2026_EXCLUSION",flush=True)
 return result

def final(out,rows,source,reference,control):
 if len(rows)!=309 or len({r["candidate_id"] for r in rows})!=309:
  raise ValueError("F6 cannot finalize fewer than 309 unique spectra")
 if any(z["modern_2026_NNLO_and_likelihood_validated"] or
        z["full_Zee_allowed_excluded"] is not None for z in rows):
  raise ValueError("F6 cannot manufacture model exclusions")
 name=out/"F6_309_legacy_two_state_BtoXsgamma_NOT_2026_EXCLUSION.jsonl"
 with name.open("w") as f:
  for z in sorted(rows,key=lambda v:v["candidate_id"]):
   f.write(json.dumps(z,sort_keys=True,allow_nan=False)+"\n")
 keys=("candidate_id","mH1_GeV","mH2_GeV","gamma","tanbeta",
       "HiggsSignals_E6_delta_chi2_NOT_CL",
       "E7_included_cascade_proxy_NOT_physical_rate",
       "F5_strict_C7eff_projector_not_rate",
       "BR_BtoXsgamma_legacy_SuperIso_two_state",
       "BR_BtoXsgamma_legacy_SuperIso_SM_reference",
       "legacy_BR_NP_minus_SM","legacy_BR_ratio_to_same_legacy_SM",
       "modern_2026_NNLO_and_likelihood_validated","full_Zee_allowed_excluded")
 table=out/"F6_309_legacy_BR_HS_cascade_NO_CL.csv"
 front=out/"F6_E7_Pareto_legacy_BR_NO_CL.csv"
 high=sorted(rows,key=lambda v:(v["HiggsSignals_E6_delta_chi2_NOT_CL"],
                      -v["E7_included_cascade_proxy_NOT_physical_rate"]))
 with table.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
  w.writerows({k:q[k] for k in keys} for q in high)
 priority=[q for q in high if q["candidate_id"] in PRIORITY]
 if len(priority)!=len(PRIORITY):raise ValueError("F6 missing an E7 Pareto candidate")
 with front.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
  w.writerows({k:q[k] for k in keys} for q in priority)
 ss=sorted(q["BR_BtoXsgamma_legacy_SuperIso_two_state"] for q in rows)
 ds=sorted(q["legacy_BR_NP_minus_SM"] for q in rows)
 summary={
  "status":STATUS,"original_source_points":309,
  "A1U_historical_full_inclusive_kernel_reproduced":True,
  "A1U_SM_TypeII_endpoints_and_equal_masses_validated":True,
  "A1U_source_context_matching_interposition_checked_every_point":True,
  "full_legacy_SuperIso_inclusive_BR_309_computed":True,
  "modern_2026_matching_and_theory_uncertainties_calibrated":False,
  "experimental_95CL_likelihood_validated":False,
  "Zee_allowed_or_excluded":None,
  "legacy_SM_BR":reference,
  "legacy_BR_min_median_max":[ss[0],ss[154],ss[-1]],
  "legacy_NP_minus_SM_min_median_max":[ds[0],ds[154],ds[-1]],
  "legacy_BtoXsGamma_above_same_legacy_SM":sum(q["legacy_BR_NP_minus_SM"]>0 for q in rows),
  "priority_six":{
    q["candidate_id"]:{
     "legacy_BR":q["BR_BtoXsgamma_legacy_SuperIso_two_state"],
     "legacy_BR_NP_minus_SM":q["legacy_BR_NP_minus_SM"],
     "F5_C7eff_dipole":q["F5_strict_C7eff_projector_not_rate"],
     "E6_HiggsSignals_delta":q["HiggsSignals_E6_delta_chi2_NOT_CL"],
     "E7_cascade":q["E7_included_cascade_proxy_NOT_physical_rate"]}
    for q in priority},
  "validated_original_A1U_controls":control,
  "source_provenance":source,
  "output_hashes":{p.name:sha(p) for p in (name,table,front)},
 }
 save(out/"summary.json",summary)
 return summary

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for name in ("e7-dir","f5-dir","a1u-result","a1r-result",
              "vendor-root","a1m-provenance","output-dir"):
  ap.add_argument("--"+name,type=Path,required=True)
 args=ap.parse_args()
 out=args.output_dir.resolve()
 if not ROOT.resolve().is_relative_to(Path("/home")) or not out.is_relative_to(ROOT/"work"):
  ap.error("F6 only in /home project work tree")
 if out.exists() and any(out.iterdir()):
  ap.error("F6 refuses overwrite of any previous work")
 out.mkdir(parents=True,exist_ok=True)
 try:
  e7,eprov=source_e7(args.e7_dir.resolve())
  f5,fprov=input_f5(args.f5_dir.resolve(),e7)
  old,apro=validate_a1u(args.a1u_result.resolve(),args.a1r_result.resolve(),
                        args.vendor_root.resolve(),args.a1m_provenance.resolve())
  exe,buildinfo=build(args.vendor_root.resolve(),out)
  control=benchmark_closure(exe,old,"helper_reload")
  previousSM=finite(old["SM_BR_legacy"],"previous A1U SM")
  near(control["legacy_SM_reference"],previousSM,"SM source normalization",
       atol=2e-12,rtol=1e-9)
  rows=apply(f5,exe,"helper_reload",previousSM)
  src={**eprov,**fprov,**apro,"new_F6_script_SHA256":sha(Path(__file__)),
       "new_C_executable":buildinfo,
       "original_F5_source_version":F5_IMPORT_STATUS}
  summary=final(out,rows,src,previousSM,control)
  save(out/"manifest.json",{"status":STATUS,"source":src,
                            "summary_SHA256":sha(out/"summary.json")})
  print("F6_STATUS",STATUS,"COMPLETED",309,
        "MODERN_2026_FLAVOR_EXCLUSION_NOT_CALCULATED",flush=True)
  print("F6_SUMMARY",out/"summary.json",flush=True)
  return 0
 except Exception as e:
  save(out/"error.json",{"status":BLOCK,"error":repr(e),
                         "traceback":traceback.format_exc(),
                         "model_allowed_excluded":None})
  print("F6_FAIL_CLOSED",repr(e),file=sys.stderr,flush=True)
  return 1
if __name__=="__main__":raise SystemExit(main())
