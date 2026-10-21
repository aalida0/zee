#!/usr/bin/env python3
"""F12: 2026 published Eq(4) LO C7/C8 source-matched screen on ALL 309
original Zee scalar points, with diagnostics vs included cascade proxy.

NO statistical exclusions, no complete Zee Yukawa/LFV/vacuum/HiggsTools.
No claim the historical 309 scalar prior is a representative measure.
Uses independent original A1S LO probe linked to original F6 SHA-checked
SuperIso v5 library, NOT F6 old BR shifts shifted to a new SM baseline.
"""
from __future__ import annotations
import argparse,csv,json,math,subprocess,sys,statistics,traceback
from pathlib import Path

from gateA1r_run_br_pilot import compile_pilot
from gateA1s_run_modern_2026_screen import (
    parse_probe,combine,linearized_2026,MODERN_SM,PDG_EXP,
)
from zee_gateF7_309_2026_bsgamma_tension_sensitivity import (
    ROOT,load_f6,digest,writejson,
)
from zee_gateF8_309_670TypeII_same_legacy_kernel_and_mixing import archive_bin
from zee_paper1_F11_six_real_flavio_LO_NP_rate import (
    close,finite,matching,coeff,
)

STATUS="F12_309_NEW_2026_SOURCE_MATCHED_EQ4_LO_CASCADE_FRONTIER_NOT_EXCLUSION"
FNAME="F12_309_2026_Eq4_LO_Bsgamma_vs_included_cascade_NOT_EXCLUSION.csv"
PARETO="F12_non_dominated_2026_Eq4_LO_CASCADE_PROXY_NOT_ALLOWED.csv"
ERR="F12_FAIL_CLOSED_NO_MODERN_FULL_NNLO_EXCLUSION"
MISSING=(
    "2026 full NNLO two-state rate and full scheme/correlated theory covariance",
    "complete one/two-loop Zee lepton flavor and modern neutrino oscillation fit",
    "rechecked complete scalar vacuum, RGE quark alignment, HiggsTools",
    "full 5-state widths and actual pb hadron rates, representative sampling",
)
def original_source(f6):
    original,meta=load_f6(f6)
    exe,old=archive_bin(f6)
    if len(original)!=309 or len(set(original))!=309:
        raise ValueError("F12 requires complete verified 309-source F6 cohort")
    summ=json.loads((f6/"summary.json").read_text())
    pinned=summ["source_provenance"]["new_C_executable"]
    lib=[Path(x) for x in pinned["command"]
         if str(x).endswith("/src/libsuperiso.a")]
    if len(lib)!=1 or not lib[0].is_file():
        raise ValueError("Historical F6 source library lost")
    if digest(lib[0])!=pinned["vendor_library_sha256"]:
        raise ValueError("F12 vendor library SHA mismatch")
    return original,meta,lib[0].parent.parent.resolve(),old

def build_vendor(vendor,f6,output):
    src=ROOT/"scripts"/"gateA1s_probe_modern_2026_lo.c"
    prog=output/"F12_pinned_A1S_2026_lo"
    info=compile_pilot(vendor,prog,src,False)
    reference=json.loads((f6/"summary.json").read_text())[
        "source_provenance"]["new_C_executable"]["vendor_library_sha256"]
    if info["library_SHA256"]!=reference:
        raise ValueError("F12 compiled with an unexpected SuperIso vendor")
    return prog,{"original_A1S_C_source":digest(src),
                 "A1S_compiled_binary_SHA256":digest(prog),
                 "A1S_original_static_vendor_SHA256":reference}

def source_probe(binary,mass,t,call=subprocess.run):
    cmd=[str(Path(binary).resolve()),f"{mass:.17g}",f"{t:.17g}"]
    z=call(cmd,capture_output=True,text=True,timeout=90,check=False)
    if z.returncode:
        raise RuntimeError("A1S independent source failed: "+
                           z.stderr[-1000:]+z.stdout[-1000:])
    return parse_probe(z.stdout,mass,t)

def evaluate(original,binary,probe=source_probe):
    memo={}
    def at(m,t):
        key=(m,t)
        if key not in memo:memo[key]=probe(binary,m,t)
        return memo[key]
    rows=[]
    sigma=math.hypot(PDG_EXP["sigma_times_1e4"],
                     MODERN_SM["sigma_times_1e4"])
    for index,(name,v) in enumerate(sorted(original.items()),1):
        m1,m2,g,t=[finite(v[k],k) for k in
                    ("mH1_GeV","mH2_GeV","gamma","tanbeta")]
        if not(200<=m1<m2<=10000 and 0<=g<=math.pi/2 and 0.25<=t<=100):
            raise ValueError("F12 input F6 original unphysical: "+name)
        pred=combine(at(m1,t),at(m2,t),g)
        ref=linearized_2026(at(670.,t)["delta_C7_LO"],
                            at(670.,t)["delta_C8_LO"])
        shift=pred["linearized_shift_times_1e4"]
        denominator=ref["linearized_shift_times_1e4"]
        if not(shift>0 and denominator>0):
            raise ValueError("Unexpected nonconstructive Type-II charged loop")
        b=pred["linearized_predicted_central_times_1e4"]
        pull=(b-PDG_EXP["central_times_1e4"])/sigma
        proxy=finite(v["E7_included_cascade_proxy_NOT_physical_rate"],
                     "E7 included channel proxy")
        if not 0<=proxy<=1.1:
            raise ValueError("F12 malformed E7 proxy")
        rows.append({
            "candidate_id":name,
            "mH1_GeV":m1,"mH2_GeV":m2,"gamma":g,"tanbeta":t,
            "DeltaC7_LO_coherent":pred["LO_delta_C7_mu0_160"],
            "DeltaC8_LO_coherent":pred["LO_delta_C8_mu0_160"],
            "2026_published_Eq4_LO_linear_BRx1e4":b,
            "2026_LO_Eq4_BSM_shift_x1e4":shift,
            "2026_same_tanbeta_TypeII670_Eq4_shift_x1e4":denominator,
            "Zee_to_TypeII670_Eq4_LO_shift_ratio_NOT_CL":shift/denominator,
            "2026_exp_plus_SM_sigma_diagnostic_z_NOT_CL":pull,
            "diagnostic_abs_z_below_1p96_NOT_a_validity_classification":
                abs(pull)<1.96,
            "E7_included_cascade_proxy_NOT_physical_pb":proxy,
            "E6_HiggsSignals_delta_chi2_NOT_CL":v[
                "HiggsSignals_E6_delta_chi2_NOT_CL"],
            "F6_full_legacy_SuperIso_BR_separate_scheme":v[
                "BR_BtoXsgamma_legacy_SuperIso_two_state"],
            "F12_full_Zee_allowed_or_excluded":None,
            "F12_modern_2026_full_NNLO_Zee_BR":None,
            "model_theory_covariance_calibrated":False,
        })
        if index%60==0 or index==len(original):
            print("F12_309",index,"/",len(original),
                  "DIAGNOSTIC_BELOW_1p96",
                  sum(q["diagnostic_abs_z_below_1p96_NOT_a_validity_classification"]
                      for q in rows),flush=True)
    return rows,{"unique_source_probes":len(memo)}

def frontier(rows):
    """Non-dominated in (max proxy, min Eq4 excess z), all not allowed."""
    best=[]
    for r in sorted(rows,key=lambda q:
       (-q["E7_included_cascade_proxy_NOT_physical_pb"],
         q["2026_exp_plus_SM_sigma_diagnostic_z_NOT_CL"])):
        if not best or (r["2026_exp_plus_SM_sigma_diagnostic_z_NOT_CL"] <
                        min(b["2026_exp_plus_SM_sigma_diagnostic_z_NOT_CL"]
                            for b in best)-1e-13):
            best.append(r)
    return best

def write_csv(path,rows):
    if not rows:raise ValueError("No valid F12 rows")
    with path.open("w",newline="") as out:
        writer=csv.DictWriter(out,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)

def run(args):
    if args.output_dir.exists():
        raise FileExistsError("F12 refuses overwrite")
    if not ROOT.resolve().is_relative_to(Path("/home")):
        raise ValueError("Run only original Zee checkout on /home")
    output=args.output_dir.resolve()
    if not output.is_relative_to(ROOT/"work"):
        raise ValueError("F12 output must be under /home project work")
    original,meta,vendor,f6pin=original_source(args.f6_dir.resolve())
    output.mkdir(parents=True,exist_ok=False)
    try:
        source,compiled=build_vendor(vendor,args.f6_dir.resolve(),output)
        cohort,calls=evaluate(original,source)
        if len(cohort)!=309 or len({x["candidate_id"] for x in cohort})!=309:
            raise ValueError("F12 original cohort incomplete")
        front=frontier(cohort)
        write_csv(output/FNAME,cohort)
        write_csv(output/PARETO,front)
        z=sorted(q["2026_exp_plus_SM_sigma_diagnostic_z_NOT_CL"]
                 for q in cohort)
        bands={
          "z_lt_1p96_diagnostic_only":sum(x<1.96 for x in z),
          "z_1p96_to_3_diagnostic_only":sum(1.96<=x<3 for x in z),
          "z_ge_3_diagnostic_only":sum(x>=3 for x in z),
        }
        summary={
          "status":STATUS,"number_original_source_spectra":309,
          "unique_source_probes":calls["unique_source_probes"],
          "modern_published_Eq4_LO_linearized_applied_to_each":True,
          "LO_Eq4_2026_BR_x1e4_min_median_max":[z[0],statistics.median(z),z[-1]],
          "Bsgamma_gaussian_z_not_a_CL_min_median_max":
              [z[0],statistics.median(z),z[-1]],
          "diagnostic_threshold_counts_NOT_model_allowed_or_excluded":bands,
          "diagnostic_Pareto_points":len(front),
          "best_proxy_among_z_lt_1p96_DIAGNOSTIC_ONLY":
               max((v for v in cohort if v[
                "2026_exp_plus_SM_sigma_diagnostic_z_NOT_CL"]<1.96),
                   key=lambda v:v[
                    "E7_included_cascade_proxy_NOT_physical_pb"],
                   default=None),
          "physical_rate_in_pb_computed":False,
          "modern_2026_full_Zee_NNLO_precision_and_CL_computed":False,
          "fully_Zee_allowed_or_excluded":None,
          "paper1_GO_or_NOGO":None,
          "missing":MISSING,
          "source":{"F6_309":meta,**compiled,
                    "F12_script_SHA256":digest(Path(__file__)),
                    "F6_summary_SHA256":digest(args.f6_dir/"summary.json")},
          "output_files_SHA256":{
              FNAME:digest(output/FNAME),PARETO:digest(output/PARETO)},
        }
        writejson(output/"summary.json",summary)
        writejson(output/"manifest.json",{
            "status":STATUS,
            "summary_SHA256":digest(output/"summary.json"),
            "source":summary["source"]})
        print("F12_STATUS",STATUS,flush=True)
        print("F12_BANDS",bands,"PARETO",len(front),flush=True)
        top=sorted(front,key=lambda v:-v[
            "E7_included_cascade_proxy_NOT_physical_pb"])[:8]
        for v in top:
            print("F12_FRONTIER",v["candidate_id"],
                  "MASS",v["mH1_GeV"],v["mH2_GeV"],
                  "Z_DIAGNOSTIC",round(v[
                    "2026_exp_plus_SM_sigma_diagnostic_z_NOT_CL"],4),
                  "PROXY_NOT_PB",round(v[
                    "E7_included_cascade_proxy_NOT_physical_pb"],6),
                  "NOT_EXCLUSION",flush=True)
        print("F12_SUMMARY",output/"summary.json",flush=True)
        return 0
    except Exception as exc:
        writejson(output/"error.json",{
            "status":ERR,"reason":repr(exc),
            "traceback":traceback.format_exc(),
            "full_Zee_model_allowed_or_excluded":None})
        print("F12_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
        traceback.print_exc()
        return 1

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--f6-dir",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    return run(p.parse_args(argv))

if __name__=="__main__":raise SystemExit(main())
