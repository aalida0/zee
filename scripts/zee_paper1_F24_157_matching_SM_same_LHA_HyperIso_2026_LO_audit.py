#!/usr/bin/env python3
"""F24: one real 157-spectrum baseline-matched HyperIso SM/NP audit.

CRITICAL: F23 original SM R3 reference uses a DIFFERENT SMINPUTS and
MASS file from the actual F23 charged THDM spectra. It is invalid to
subtract 3.2967e-4 to infer the Zee charged new-physics contribution.
For each of 157 original actual LHA inputs, evaluate the unmodified
HyperIso v1.0.3 SM observable with THE SAME LHA and cut/NNLO settings,
then compute the historical scheme matched SM-subtracted NP effect.
This is a rigorous internal observable difference but NOT a
Misiak-2026 NNLO full rate or 95%-CL limit.
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math,re,statistics,subprocess
from pathlib import Path
from collections import Counter
from zee_paper1_F23b_one_pass_157_real_outputs_audit import (
    summary_pins,physical_lha,sha,approximately,number,require,EDGES,
    RESULT,TRACE,REPORT,correlation,math_rank)

STATUS="F24_MATCHED_SAME_THDM_LHA_SM_157_NP_LEGACY_CONDITIONAL_NOT_2026_CL"
SM_CLI_REGEX=re.compile(r"BR_B__Xs_gamma\s*=\s*([0-9.eE+\-]+)")
PHYSICAL_2026_SM=3.54e-4
PHYSICAL_2026_EXP=3.49e-4

def native_sm_baseline(cli,source,timeout=120):
    cmd=[str(cli),"observable","summary",
        "--model","SM","--lha",str(source),
        "--spectrum","true","--observables","BR_B__Xs_gamma",
        "--order","NNLO"]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout)
    if p.returncode:
        raise RuntimeError("F24 native SM with exactly same Type-II source LHA failed "+
                           str(source)+"\n"+p.stderr[-1800:]+"\n"+p.stdout[-2000:])
    vals=SM_CLI_REGEX.findall(p.stdout)
    if len(vals)!=1:
        raise ValueError("F24 native SM observable output missing/ambiguous: "+p.stdout[-1600:])
    v=number(vals[0],"same-LHA HyperIso native SM BR")
    require(0<v<0.1,"impossible matched native SM BR")
    return v,p.stdout[-1300:]

def original_points(f22,f23):
    source_path=f22/"F22_ALL_157_original_complex_fY_sources_NOT_FULL_ALLOWED.jsonl.gz"
    with gzip.open(source_path,"rt") as f:
        originals=[json.loads(line) for line in f if line.strip()]
    original_map={x["campaign_key"]:x for x in originals}
    require(len(original_map)==157,"source full F22 complex points missing")
    pri_path=f22/"F22_mass_stratified_priority_complex_fY_dossier_NOT_ALLOWED.json"
    prior=json.loads(pri_path.read_text())
    priorities={x["campaign_key"] for x in prior["entries"]}
    require(len(priorities)==9,"actual nine priorities absent")
    with (f23/RESULT).open(newline="") as f:
        results=list(csv.DictReader(f))
    traces=[json.loads(line) for line in (f23/TRACE).read_text().splitlines() if line.strip()]
    require(len(results)==157 and len(traces)==193,"F23 real native 157/193 incomplete")
    require({r["key"] for r in results}==set(original_map),"F23/F22 source model ID discrepancy")
    return results,traces,priorities,original_map

def execute(a):
    f22=a.f22.expanduser().resolve()
    f23=a.f23.expanduser().resolve()
    f23b=a.f23b.expanduser().resolve()
    out=a.output.expanduser().resolve()
    require(not out.exists(),"F24 refuses overwrite/partial result collision")
    _,f23report=summary_pins(f22,f23)
    audited=f23b/"F23b_157_native_trace_source_and_physics_audit_NOT_FULL_ALLOWED.json"
    if not audited.is_file():raise FileNotFoundError("F24 needs prior real 193-trace F23b audit "+str(audited))
    prev=json.loads(audited.read_text())
    require(prev.get("status")=="F23b_NATIVE_F23_157_PHYSICS_SOURCE_AND_NUMERICAL_VALIDATED_CONDITIONAL_NOT_2026_CL"
            and prev.get("frozen_models_analysed")==157
            and prev.get("genuine_Cplusplus_matching_calls_checked")==193
            and prev.get("native_THDM_18_absolute_BR_endpoints_compared_independently") is True
            and prev.get("all_frozen_point_source_to_cpp_trace_consistent") is True
            and prev.get("full_model_allowed_or_excluded") is None,
            "F24 genuine prior F23b full real numerical audit was not completed")
    require(prev["source_f22_model_cohort_sha256"]==sha(f22/"F22_freeze_SHA256_manifest.json")
            and prev["source_f23_summary_sha256"]==sha(f23/REPORT),
            "F24 prior F23b audit not from current actual source")
    results,traces,priorities,original_map=original_points(f22,f23)
    cli=[p for p in (f23/"hyperiso-cmake-build").rglob("hyperiso-ui")
         if p.is_file() and p.stat().st_mode & 0o111]
    require(len(cli)==1,"unmodified HyperIso tagged binary missing or ambiguous")
    out.mkdir(parents=True,exist_ok=False)
    outcome=[]
    sm_traces=[]
    by_key={r["key"]:r for r in results}
    source_dir=f23/"F23_THDM_quark_only_surrogate_inputs"
    for i,point in enumerate(results):
        trace=traces[36+i]
        require(point["key"]==trace["campaign_key"],"F24 real BR/native trace ID mismatch")
        lha=source_dir/f"typeII_for_{36+i:05d}.lha"
        require(lha.is_file() and sha(lha)==trace["LHA_SHA256"],
                "F24 actual matched SM LHA not exact prior F23 native source "+point["key"])
        blocks=physical_lha(lha)
        tanbeta=number(point["tanb"],"tanbeta")
        m1=number(point["m1"],"mH1")
        m2=number(point["m2"],"mH2")
        gamma=number(point["gamma"],"gamma")
        require(approximately(blocks["MASS",(37,)],m1,rtol=1e-11)
                and approximately(blocks["MINPAR",(3,)],tanbeta,rtol=1e-11)
                and approximately(blocks["YU",(2,2)],1./tanbeta,rtol=1e-11)
                and approximately(blocks["YD",(2,2)],-tanbeta,rtol=1e-11),
                "F24 physical Type-II inputs not preserved "+point["key"])
        matched,stdout=native_sm_baseline(cli[0],lha)
        full=number(point["legacy_HyperIso_v103_BR_BXs_gamma_conditional"],"mixed BR")
        require(approximately(number(trace["BR_HyperIso_v103_legacy_NNLO_conditional_NOT_CL"],"trace BR"),
                              full,rtol=1e-12),
                "F24 real charged native BR discrepancy "+point["key"])
        delta=full-matched
        lo_2026_probe=(number(point["LO_flavor_x1e4_NOT_CL"],"F19d LO")
                       -3.54)*1e-4
        require(delta!=0.,"F24 two-state BSM correction entirely zero; model SM confusion")
        rec={
          "campaign_key":point["key"],
          "mH1_GeV":m1,"mH2_GeV":m2,"tanbeta":tanbeta,"gamma_rad":gamma,
          "is_frozen_F22_priority":point["key"] in priorities,
          "included_channel_cascade_proxy_NOT_pb":number(point["cascade_included_proxy_NOT_pb"],"cascade"),
          "full_legacy_HyperIso_v103_Zee_BR":full,
          "same_LHA_same_NNLO_HyperIso_SM_BR":matched,
          "matched_SM_subtracted_legacy_BSM_deltaBR_NOT_2026":delta,
          "prior_R3_other_LHA_SM_BR_NOT_MATCHED":number(f23report["R3_SM_BR"],"R3"),
          "difference_between_SM_reference_files":matched-number(f23report["R3_SM_BR"],"R3"),
          "independent_2026_analytic_LO_C7C8_linearized_deltaBR_NOT_CL":lo_2026_probe,
          "ratio_matched_old_NP_deltaBR_to_independent_LO_proxy":
             delta/lo_2026_probe if lo_2026_probe else None,
          "modern_2026_SM_central_BR_for_CONTEXT_NOT_combined":PHYSICAL_2026_SM,
          "modern_2026_experimental_central_BR_for_CONTEXT":PHYSICAL_2026_EXP,
          "full_2026_prediction_or_CL":None,
          "source_original_F23_actual_LHA_SHA256":sha(lha),
          "source_original_F22_LFV_partial_score_NOT_CL":
             number(point["partial_LFV_Wgamma_ratio_NOT_CL"],"LFV"),
        }
        outcome.append(rec)
        sm_traces.append({
           "source_F22_ID":point["key"],"source_original_LHA_SHA256":sha(lha),
           "F23_matching_original_trace":trace["trace"],
           "SM_CLI_model_explicit":"SM","SM_CLI_order":"NNLO",
           "SM_CLI_spectrum_unchanged":True,
           "SM_BR":matched,
           "complete_original_HyperIso_SM_CLI_tail":stdout})
        if i%25==0 or i==156:
            print("F24_NATIVE_SAME_LHA_SM_PROGRESS",i+1,"/157",flush=True)
    same_sm=[r["same_LHA_same_NNLO_HyperIso_SM_BR"] for r in outcome]
    # All 157 surrogate input files share IDENTICAL original SMINPUTS,
    # with only H+ mass/tanbeta/Yukawa differences. A genuine SM
    # observable must therefore be independent of those 157 BSM changes.
    sm_center=statistics.median(same_sm)
    spread=max(same_sm)-min(same_sm)
    require(spread<max(1e-10,abs(sm_center)*2e-7),
            "F24 SM CLI depends significantly on varying THDM mass/tanbeta -- model selection or source bleed!")
    # The matched deltaBR is not a complete modern 2026 NNLO prediction.
    metrics={}
    for lower,upper in zip(EDGES[:-1],EDGES[1:]):
        shell=[r for r in outcome if lower<=r["mH2_GeV"]<upper]
        require(shell,"missing 157 original shell points")
        effects=[r["matched_SM_subtracted_legacy_BSM_deltaBR_NOT_2026"] for r in shell]
        cascade=[r["included_channel_cascade_proxy_NOT_pb"] for r in shell]
        metrics[f"{lower:g}-{upper:g}GeV"]={
          "screened_count":len(shell),
          "matched_legacy_NP_min":min(effects),
          "matched_legacy_NP_median":statistics.median(effects),
          "matched_legacy_NP_max":max(effects),
          "spearman_conditional_NP_vs_cascade_proxy":
              correlation(math_rank(effects),math_rank(cascade)),
        }
    table=out/"F24_157_same_LHA_matched_SM_and_Zee_legacy_NP_NOT_2026_CL.csv"
    with table.open("w",newline="") as f:
        cols=list(outcome[0])
        w=csv.DictWriter(f,fieldnames=cols)
        w.writeheader();w.writerows(outcome)
    priorities_csv=out/"F24_9_priorities_same_LHA_flavor_comparison_NOT_ALLOWED.csv"
    selected=[r for r in outcome if r["is_frozen_F22_priority"]]
    require(len(selected)==9,"nine priority cohort broken")
    with priorities_csv.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(selected[0]))
        w.writeheader();w.writerows(selected)
    tracefile=out/"F24_157_unmodified_SM_CLI_source_trace.jsonl"
    with tracefile.open("w") as f:
        for trace in sm_traces:f.write(json.dumps(trace,sort_keys=True,allow_nan=False)+"\n")
    figfiles=[]
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig,ax=plt.subplots(figsize=(8,5))
        ax.scatter([r["mH2_GeV"] for r in outcome],
                   [1e4*r["matched_SM_subtracted_legacy_BSM_deltaBR_NOT_2026"] for r in outcome],
                   s=19,alpha=.65,label="157 saved F22 Zee spectra")
        ax.scatter([r["mH2_GeV"] for r in selected],
                   [1e4*r["matched_SM_subtracted_legacy_BSM_deltaBR_NOT_2026"] for r in selected],
                   s=95,marker="*",label="9 priority benchmarks")
        ax.set_xlabel(r"$m_{H_2^\pm}$ [GeV]")
        ax.set_ylabel(r"$10^4\,\Delta BR^{\rm legacy}_{\rm NP}$ (same-LHA SM subtraction)")
        ax.set_title("Type-II-quark Zee — HyperIso v1.0.3 (not 2026 CL)")
        ax.legend();fig.tight_layout()
        target=out/"F24_157_mass_vs_matched_legacy_NP_NOT_2026_CL.pdf"
        fig.savefig(target);plt.close(fig);figfiles.append(target)
        fig,ax=plt.subplots(figsize=(8,5))
        xx=[1e4*r["independent_2026_analytic_LO_C7C8_linearized_deltaBR_NOT_CL"] for r in outcome]
        yy=[1e4*r["matched_SM_subtracted_legacy_BSM_deltaBR_NOT_2026"] for r in outcome]
        ax.scatter(xx,yy,s=18,alpha=.7)
        ax.set_xlabel(r"$10^4\,\Delta BR_{2026,\mathrm{Eq.4}}^{LO}$ (diagnostic)")
        ax.set_ylabel(r"$10^4\,\Delta BR_{\rm HyperIso,old}^{SM-matched}$")
        ax.set_title("Cross-scheme NP sensitivity — not an NNLO equivalence")
        fig.tight_layout()
        target=out/"F24_matched_old_vs_independent_2026_LO_NOT_NNLO_EQUIVALENCE.pdf"
        fig.savefig(target);plt.close(fig);figfiles.append(target)
    except ImportError:
        pass
    report={
       "status":STATUS,"real_F22_source_models":157,
       "F23_prior_real_native_Zee_physics_calculations":193,
       "F24_new_unmodified_HyperIso_SM_native_157_input_matched_calculations":157,
       "F23b_18_unmodified_THDM_native_reference_calculations_pass":True,
       "HyperIso_source_PIN":f23report["HyperIso_PIN"],
       "F22_SHA256_manifest":sha(f22/"F22_freeze_SHA256_manifest.json"),
       "F23_SHA256_summary":sha(f23/REPORT),
       "F23b_SHA256_full_audit":sha(audited),
       "tagged_R3_SM_different_input_file_BR":f23report["R3_SM_BR"],
       "matched_THMD_LHA_SM_median_BR":sm_center,
       "all_157_BSM_independent_SM_predictions_max_minus_min":spread,
       "single_unmodified_SM_baseline_invariance_PASSED":True,
       "legitimate_matched_legacy_BSM_shift_is_Zee_BR_minus_own_SMLHA":True,
       "five_original_mass_bins":metrics,
       "nine_priorities":[r for r in selected],
       "2026_original_Misiak_source":"arxiv:2608.29863",
       "2026_SM_BR_CONTEXT_ONLY":PHYSICAL_2026_SM,
       "2026_exp_BR_CONTEXT_ONLY":PHYSICAL_2026_EXP,
       "historical_NP_delta_plus_2026_SM_not_a_valid_physical_prediction":True,
       "experimental_95CL_or_full_2026_NNLO_matching":None,
       "complete_general_Zee_LFV_HiggsTools_LHC_rates":False,
       "full_model_allowed_or_excluded":None,
       "outputs_SHA256":{p.name:sha(p) for p in (table,priorities_csv,tracefile,*figfiles)},
    }
    j=out/"F24_157_source_matched_SM_subtracted_HyperIso_NP_report_NOT_2026_CL.json"
    j.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F24_COMPLETE_NATIVE_SM_MATCHED_157_SOURCE_AND_PHYSICS_PASS",
          "ORIGINAL_F22",157,"EXACT_SHARED_LHA_NATIVE_SM",157,
          "MATCHED_SM_BR",f"{sm_center:.12g}",
          "PRIOR_TAGGED_R3_DIFFERENT_LHA_SM_BR",f"{f23report['R3_SM_BR']:.12g}",
          "FULL_MODEL_ALLOWED",None,flush=True)
    for z in selected:
        print("F24_PRIORITY",z["campaign_key"],
              "M2",z["mH2_GeV"],"CASCADE_PROXY",z["included_channel_cascade_proxy_NOT_pb"],
              "MATCHED_OLD_NP_SHIFT",z["matched_SM_subtracted_legacy_BSM_deltaBR_NOT_2026"],
              "2026_LINEAR_LO_DIAGNOSTIC",z["independent_2026_analytic_LO_C7C8_linearized_deltaBR_NOT_CL"],flush=True)
    print("F24_RESULT",j,flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--f22",required=True,type=Path)
    ap.add_argument("--f23",required=True,type=Path)
    ap.add_argument("--f23b",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    execute(ap.parse_args())
