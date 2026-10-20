#!/usr/bin/env python3
"""F5: 309 original-Zee-source two-charged B->Xs gamma C7eff projector audit.

Reuses *actual* pinned F4b SuperIso 3-mode C1..C8 RG executable and its
previously validated 8 Type-II single-Higgs controls, not a fitted analytic
function of charged mass. Pairs every E7 original optimized model with
its charged masses, gamma and tanbeta; computes LO and strictly truncated
O(alpha_s) NP-minus-SM |C7eff|^2 PROJECTION, including genuine 4-quark
NLO high matching. This is NOT an inclusive B->Xs gamma branching ratio,
and cannot label any point allowed/excluded. Charged-quark Yukawa Z2
assumption itself needs independent model/RGE validation.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys,traceback
from pathlib import Path
from zee_gateF4b_fixed_order_dipole_projector import projector
from zee_gateF3_fullNLO_source_RG_27 import probe
STATUS="F5_309_TWO_CHARGED_C7EFF_PROJECTOR_NLO_MATCHING_NOT_BRGAMMA_OR_EXCLUSION"
BLOCK="F5_BLOCKED_NO_BRGAMMA_OR_EXCLUSION"
ROOT=Path(__file__).resolve().parents[1]
E7_FILE="E7_309_general_Zee_charged_widths_NOT_ALLOWED.jsonl"
F4B_CONTROL_KEYS=("Q7eff_NP_LO","Q7eff_NP_Oalpha_s_all",
 "Q7eff_NP_strictly_truncated_LO_plus_NLO",
 "Q7eff_NP_NLO_matching_dipoles_only",
 "Q7eff_NP_NLO_matching_fourquark_induced",
 "Q7eff_NP_NLO_matching_total")

def sha(p):
 h=hashlib.sha256()
 with Path(p).open("rb") as f:
  for block in iter(lambda:f.read(1<<20),b""):h.update(block)
 return h.hexdigest()

def load(p):return json.loads(Path(p).read_text())
def save(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,indent=2,
                                    allow_nan=False)+"\n")
def finite(v,label):
 x=float(v)
 if not math.isfinite(x):raise ValueError("Nonfinite "+label)
 return x
def near(a,b,label,*,rtol=2e-8,atol=1e-11):
 if not math.isclose(finite(a,label),finite(b,label),rel_tol=rtol,abs_tol=atol):
  raise ValueError("F5 source/control closure mismatch "+label)

def source_e7(dir):
 s=load(dir/"summary.json");m=load(dir/"manifest.json")
 if (s.get("status")!="E7_309_NEUTRINO_CLOSED_GENERAL_ZEE_CHARGED_WIDTH_PARETO_NOT_ALLOWED"
     or s.get("original_models")!=309 or
     s.get("neutrino_closure_full_309_checked") is not True or
     s.get("HiggsBounds_model_exclusion_not_evaluated") is not True or
     s.get("full_allowed_and_excluded_Zee_counts") is not None or
     m.get("status")!=s["status"] or
     m.get("summary_SHA256")!=sha(dir/"summary.json") or
     m.get("source")!=s.get("source_provenance")):
  raise ValueError("E7 source summary/manifest status and SHA mismatch")
 for filename,expected in s["sha256_outputs"].items():
  if sha(dir/filename)!=expected:raise ValueError("E7 archived evidence SHA mismatch")
 from zee_gateE7_309_general_lepton_width_pareto import (
  STATUS as E7_STATUS, ROOT as E7_ROOT)
 if s["status"]!=E7_STATUS or E7_ROOT!=ROOT:
  raise ValueError("E7 original code/environment changed")
 if s["source_provenance"].get("E7_source_SHA256")!=sha(
  ROOT/"scripts/zee_gateE7_309_general_lepton_width_pareto.py"):
  raise ValueError("E7 original source code SHA changed")
 rows={}
 with (dir/E7_FILE).open() as f:
  for line in f:
   row=json.loads(line);name=row["candidate_id"]
   if (name in rows or row["claim_full_Zee_approved"] is not None or
       row["claim_HiggsBounds_excluded"] is not None):
    raise ValueError("E7 invalid duplicate or physical exclusion")
   if not 0<=finite(row[
    "charged_cascade_included_channel_proxy_NOT_physical_rate"],"cascade")<=1:
    raise ValueError("E7 unphysical cascade proxy")
   rows[name]=row
 if len(rows)!=309:raise ValueError("E7 requires exactly 309 unique original points")
 return rows,{"E7_summary_SHA256":sha(dir/"summary.json"),
              "E7_manifest_SHA256":sha(dir/"manifest.json"),
              "E7_evidence_SHA256":sha(dir/E7_FILE),
              "E7_original_E6_source_fingerprint":
                  s["source_provenance"].get("original_E6_physics_sources")}

def source_f4b(p):
 old=load(p)
 if (old.get("status")!="F4B_ORDER_RESOLVED_DIPOLE_PROJECTOR_NOT_FULL_NLO_RATE"
     or old.get("num_typeII_controls")!=8 or
     old.get("strict_C7eff_squared_LO_and_NLO_interference_extracted") is not True
     or old.get("physical_full_NLO_BtoXsgamma_rate_calculated") is not False
     or old.get("Zee_allowed_or_excluded") is not None):
  raise ValueError("F4b reference is not successful source-matched 8 control")
 cc=old.get("typeII_results")
 if not isinstance(cc,list) or len(cc)!=8:raise ValueError("F4b controls incomplete")
 controls={}
 for rec in cc:
  key=(finite(rec["mass_GeV"],"F4b mass"),
       finite(rec["tanbeta"],"F4b beta"))
  if key in controls:raise ValueError("Duplicate F4b Type-II control")
  controls[key]=rec
 if set(controls)!={(mass,t) for mass in (300.,580.,670.,1000.)
                             for t in (5.6,50.)}:
  raise ValueError("F4b TypeII 8-control identifiers changed")
 ex=Path(old["source_rg_probe_build"]["compiler_command"][-1]).resolve()
 if (not ex.is_file() or not ex.is_relative_to(ROOT/"work") or
     ex.is_relative_to(Path("/data")) or
     sha(ex)!=old["source_rg_probe_executable_sha256"]):
  raise ValueError("F4b compiled SuperIso RG binary missing/changed")
 inp=old["source_running_parameters"]
 alpha=finite(inp["alphas_mub"],"source alpha_s(mub)")
 if (not .15<alpha<.35 or
     not math.isclose(float(inp["muW"]),160.,abs_tol=1e-9) or
     not math.isclose(float(inp["mub"]),4.2,abs_tol=1e-9)):
  raise ValueError("F4b source scale or alpha mismatch")
 return ex,alpha,controls,{
  "F4b_prior_summary_SHA256":sha(p),
  "SuperIso_RG_probe_binary_SHA256":sha(ex),
  "SuperIso_wilson_c_source_SHA256":old["source_wilson_sha256"],
  "SuperIso_alpha_s_low":alpha,
  "F4b_8_TypeII_input_control_count":8,
 }

def response(wc,alpha):
 """All three source modes required: LO RG, dipole NLO, full C3..C8 NLO."""
 sm0=finite(wc[0,7]["low_SM_LO"],"SM LO C7eff")
 sm1=finite(wc[0,7]["low_SM_NLO"],"SM NLO C7eff")
 np0=finite(wc[0,7]["low_LO"],"NP LO C7eff")
 for mode in (1,2):
  near(wc[mode,7]["low_SM_LO"],sm0,"SM LO source-mode closure",atol=1e-10)
  near(wc[mode,7]["low_SM_NLO"],sm1,"SM NLO source-mode closure",atol=1e-10)
  near(wc[mode,7]["low_LO"],np0,"NP LO source-mode closure",atol=1e-10)
 profiles={i:projector(sm0,sm1,np0,finite(wc[i,7]["low_NLO"],
                                          "NP low NLO C7eff"),alpha)
           for i in (0,1,2)}
 a,b,c=(profiles[i] for i in (0,1,2))
 terms={
  "Q7eff_NP_LO":c["Q7eff_NP_minus_SM_LO"],
  "Q7eff_NP_NLO_evolution_and_SM_baseline":a["Q7eff_NP_minus_SM_Oalpha_s"],
  "Q7eff_NP_NLO_matching_dipoles_only":
    b["Q7eff_NP_minus_SM_Oalpha_s"]-a["Q7eff_NP_minus_SM_Oalpha_s"],
  "Q7eff_NP_NLO_matching_fourquark_induced":
    c["Q7eff_NP_minus_SM_Oalpha_s"]-b["Q7eff_NP_minus_SM_Oalpha_s"],
  "Q7eff_NP_Oalpha_s_all":c["Q7eff_NP_minus_SM_Oalpha_s"],
  "Q7eff_NP_strictly_truncated_LO_plus_NLO":
    c["Q7eff_NP_minus_SM_truncated_through_Oalpha_s"],
  "Q7eff_NP_partial_Oalpha_s_squared":
    c["Q7eff_NP_minus_SM_partial_Oalpha_s_squared"],
  "Q7eff_NP_untruncated_square":
    c["Q7eff_NP_minus_SM_untruncated_square"],
  "C7eff_SM_LO":sm0,"C7eff_SM_NLO":sm1,
  "C7eff_NP_LO":np0,
  "C7eff_NP_NLO_full":wc[2,7]["low_NLO"],
  "C8eff_NP_NLO_full":wc[2,8]["low_NLO"],
  "source_high_scale_NLO_C4":wc[2,4]["high_NLO"],
 }
 terms["Q7eff_NP_NLO_matching_total"]=(
  terms["Q7eff_NP_NLO_matching_dipoles_only"]+
  terms["Q7eff_NP_NLO_matching_fourquark_induced"])
 near(terms["Q7eff_NP_LO"]+
      terms["Q7eff_NP_NLO_evolution_and_SM_baseline"]+
      terms["Q7eff_NP_NLO_matching_total"],
      terms["Q7eff_NP_strictly_truncated_LO_plus_NLO"],
      "strict order-by-order Q7 closure",atol=2e-13)
 scale=sm0*sm0
 if scale<=1e-7:raise ValueError("Vanishing SM C7 LO norm")
 terms["LO_Q7eff_NP_minus_SM_over_SM_LO_square"]=terms["Q7eff_NP_LO"]/scale
 terms["NLO_truncated_Q7eff_NP_minus_SM_over_SM_LO_square"]=(
     terms["Q7eff_NP_strictly_truncated_LO_plus_NLO"]/scale)
 terms["NOT_inclusive_B_to_Xs_gamma_BR"]=True
 terms["model_excluded_allowed"]=None
 return terms

def check_f4b_controls(probe_func,exe,alpha,controls):
 matched=0
 for (mass,tanb),old in sorted(controls.items()):
  wc=probe_func(exe,mass,mass,tanb,0.)
  cur=response(wc,alpha)
  for key in F4B_CONTROL_KEYS:
   near(cur[key],old[key],f"F4b TypeII_{mass}_{tanb}_{key}",
        rtol=2e-8,atol=2e-11)
  matched+=1
 return matched

def apply(rows,exe,alpha,probe_func=probe):
 out=[]
 for index,name in enumerate(sorted(rows),1):
  z=rows[name]
  mass1=finite(z["mH1_GeV"],"original H1 mass")
  mass2=finite(z["mH2_GeV"],"original H2 mass")
  gam=finite(z["gamma"],"original gamma")
  t=finite(z["tanbeta"],"original tanbeta")
  if not(150<mass1<mass2<2000 and 0<gam<math.pi/2 and t>0):
   raise ValueError("Original Zee two-state scalar point invalid")
  wc=probe_func(exe,mass1,mass2,t,gam)
  result=response(wc,alpha)
  result.update({
    "candidate_id":name,"mH1_GeV":mass1,"mH2_GeV":mass2,
    "gamma":gam,"tanbeta":t,
    "charged_typeII_quark_weight_H1_cos2gamma":math.cos(gam)**2,
    "charged_typeII_quark_weight_H2_sin2gamma":math.sin(gam)**2,
    "E6_HiggsSignals_delta_chi2_NOT_CL":
        finite(z["HS_delta_chi2_E6_vs_fixed_SM"],"HS chi2"),
    "E7_included_channel_cascade_proxy_NOT_signal":
        finite(z["charged_cascade_included_channel_proxy_NOT_physical_rate"],
               "charged cascade"),
  })
  out.append(result)
  print("F5_C7EFF",index,"/309",name,
        "Q7_LO",f"{result['Q7eff_NP_LO']:.8g}",
        "Q7_NLO_TRUNC",f"{result['Q7eff_NP_strictly_truncated_LO_plus_NLO']:.8g}",
        "NLO_C4_MATCHING",f"{result['source_high_scale_NLO_C4']:.8g}",
        "NO_BR_OR_EXCLUSION",flush=True)
 return out

def pareto(data,xx="E6_HiggsSignals_delta_chi2_NOT_CL",
           yy="E7_included_channel_cascade_proxy_NOT_signal"):
 result=[];highest=-math.inf
 for row in sorted(data,key=lambda z:(z[xx],-z[yy],z["candidate_id"])):
  if row[yy]>highest:
   result.append(row)
   highest=row[yy]
 return result

def finish(folder,rows,controls_count,source):
 if len(rows)!=309 or len({r["candidate_id"] for r in rows})!=309:
  raise ValueError("Cannot publish incomplete F5 source result")
 if controls_count!=8:raise ValueError("Independent F4b 8 controls missing")
 rows.sort(key=lambda q:(q["E6_HiggsSignals_delta_chi2_NOT_CL"],
                         -q["E7_included_channel_cascade_proxy_NOT_signal"]))
 main=folder/"F5_309_Zee_strict_dipole_projector_NO_BR.jsonl"
 with main.open("w") as f:
  for q in rows:f.write(json.dumps(q,allow_nan=False,sort_keys=True)+"\n")
 keys=("candidate_id","mH1_GeV","mH2_GeV","gamma","tanbeta",
       "E6_HiggsSignals_delta_chi2_NOT_CL",
       "E7_included_channel_cascade_proxy_NOT_signal",
       "charged_typeII_quark_weight_H1_cos2gamma",
       "charged_typeII_quark_weight_H2_sin2gamma",
       "Q7eff_NP_LO","Q7eff_NP_NLO_matching_dipoles_only",
       "Q7eff_NP_NLO_matching_fourquark_induced",
       "Q7eff_NP_strictly_truncated_LO_plus_NLO",
       "NLO_truncated_Q7eff_NP_minus_SM_over_SM_LO_square",
       "source_high_scale_NLO_C4","model_excluded_allowed")
 c=folder/"F5_309_HS_cascade_C7_dipole_NO_EXCLUSION.csv"
 with c.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
  w.writerows({k:q[k] for k in keys} for q in rows)
 front=pareto(rows)
 fpath=folder/"F5_E7_Pareto_C7_source_audit_NO_EXCLUSION.csv"
 with fpath.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
  w.writerows({k:q[k] for k in keys} for q in front)
 allq=[q["Q7eff_NP_strictly_truncated_LO_plus_NLO"] for q in rows]
 ranked=sorted(allq)
 summary={
   "status":STATUS,"source_models":309,"F4b_source_matched_controls":8,
   "strict_source_C7eff_squared_projector_only":True,
   "complete_EOS_NLO_matrix_elements_and_B_to_Xs_gamma_BR":False,
   "complete_NLO_EW_matching_scheme_and_operator_equivalence":False,
   "full_model_allowed_or_excluded":None,
   "C7_strict_projector_min_median_max":[ranked[0],ranked[154],ranked[-1]],
   "E7_Pareto_source_cases":len(front),
   "E7_Pareto_source_diagnostic":{
     z["candidate_id"]:{
       "Q7eff_NP_LO":z["Q7eff_NP_LO"],
       "Q7eff_NP_truncated_LO_NLO":
         z["Q7eff_NP_strictly_truncated_LO_plus_NLO"],
       "HighScale_NLO_C4":z["source_high_scale_NLO_C4"],
       "E6_HS":z["E6_HiggsSignals_delta_chi2_NOT_CL"],
       "E7_partial_cascade":
           z["E7_included_channel_cascade_proxy_NOT_signal"]}
     for z in front},
   "source_provenance":source,
   "output_sha256":{p.name:sha(p) for p in (main,c,fpath)},
 }
 save(folder/"summary.json",summary)
 return summary

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--e7-dir",type=Path,required=True)
 ap.add_argument("--f4b-summary",type=Path,required=True)
 ap.add_argument("--output-dir",type=Path,required=True)
 args=ap.parse_args()
 out=args.output_dir.resolve()
 if not ROOT.resolve().is_relative_to(Path("/home")) or not out.is_relative_to(ROOT/"work"):
  ap.error("Run under /home/aalida/zee and store only in /home/.../work")
 if out.exists() and any(out.iterdir()):
  ap.error("Never overwrite prior F5 results")
 out.mkdir(parents=True,exist_ok=True)
 try:
  rows,provenance=source_e7(args.e7_dir.resolve())
  exe,alpha,controls,ref=source_f4b(args.f4b_summary.resolve())
  n=check_f4b_controls(probe,exe,alpha,controls)
  complete=apply(rows,exe,alpha)
  source={**provenance,**ref,"F5_driver_SHA256":sha(Path(__file__)),
          "F3_probe_wrapper_SHA256":sha(
              ROOT/"scripts/zee_gateF3_fullNLO_source_RG_27.py"),
          "F4b_projector_SHA256":sha(
              ROOT/"scripts/zee_gateF4b_fixed_order_dipole_projector.py")}
  final=finish(out,complete,n,source)
  save(out/"manifest.json",{"status":STATUS,"source":source,
                            "summary_SHA256":sha(out/"summary.json")})
  print("F5_STATUS",STATUS,"MODELS",309,"F4B_ANCHOR_CLOSED",8,
        "FULL_ZEE_ALLOWED_UNKNOWN",flush=True)
  print("F5_RESULTS",out/"summary.json",flush=True)
  return 0
 except Exception as e:
  save(out/"error.json",{"status":BLOCK,"error":repr(e),
                        "traceback":traceback.format_exc(),
                        "physical_allowed_or_excluded":None})
  print("F5_FAIL_CLOSED",repr(e),file=sys.stderr,flush=True)
  return 1

if __name__=="__main__":raise SystemExit(main())
