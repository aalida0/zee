#!/usr/bin/env python3
"""E5A: explain 309 E5 HiggsSignals tensions WITHOUT inventing exclusions.

Runs the actual pinned 159-observable HiggsSignals input again to verify
each saved E5 chi2, then diagnostic single-sector counterfactuals resetting
bottom, top, diagonal lepton, or gauge effective couplings to SM=1. These
counterfactuals are not physical alternative Zee models and NOT combined.
For the selected best/worst original models and original B4 anchors, use
actual HS Measurement(pred) API to report correlated WITHIN-analysis chi2
differences. Submeasurement.chisqContributions() ignores correlations and is
not used here. Cross-analysis correlations, if any, require caution.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,os,statistics,sys,traceback
from pathlib import Path
import numpy as np
import zee_gateE5_309_h125_higgssignals_effective as e5

BASE=e5.ROOT
STATUS="E5A_309_HS_EFFECTIVE_REPRO_AND_SECTOR_SENSITIVITY_NOT_ALLOWED"
BLOCKED="E5A_BLOCKED_NO_EXCLUSION"
SECTORS={
    "bottom_down_strange_to_SM":("bb","dd","ss"),
    "top_charm_up_to_SM":("tt","cc","uu"),
    "diagonal_charged_leptons_to_SM":("ee","mumu","tautau"),
    "VV_to_SM":("WW","ZZ"),
}
ANCHORS=("B4_0006862","B4_0006962")


def same(a,b,label,*,atol=1e-7,rtol=1e-9):
    if not math.isclose(float(a),float(b),rel_tol=rtol,abs_tol=atol):
        raise ValueError(label+f" original={a} rerun={b}")


def inputs(e2,e3,e4h,e5dir,hs):
    points,source,e4h_rows,prior=e5.validated_sources(e2,e3,e4h)
    e5sum=e5.load(e5dir/"summary.json")
    e5manifest=e5.load(e5dir/"manifest.json")
    dataset=e5.dataset_provenance(hs)
    contract={
       "source":prior,
       "dataset":{
          "dataset_sha256_manifest":dataset["dataset_sha256_manifest"],
          "file_count":dataset["file_count"],"path":dataset["path"]},
       "main_source_script_sha256":e5.sha256(Path(e5.__file__)),
       "Higgs_pred_module_path":None,
       "Higgs_signals_module_path":None,
       "h125_mass_GeV":float(e5.MH),
       "partial_model_flags":e5.VALIDITY,
    }
    if (e5sum.get("status")!=e5.STATUS or
        e5sum.get("HiggsSignals_chi2_evaluated_in_effective_coupling_approx")!=309 or
        e5sum.get("HiggsSignals_number_loaded_observables")!=159 or
        e5sum.get("full_model_allowed_points") is not None or
        e5sum.get("model_125_only") is not True or
        e5manifest.get("status")!=e5.STATUS or
        e5manifest.get("summary_SHA256")!=e5.sha256(e5dir/"summary.json")):
        raise ValueError("E5 completed 309/159 summary/manifest integrity failed")
    e5old=e5manifest.get("provenance")
    if not isinstance(e5old,dict):
        raise ValueError("E5 manifest provenance absent")
    for k,v in contract.items():
        if v is not None and e5old.get(k)!=v:
            raise ValueError("E5 input provenance drift: "+k)
    path=e5dir/"E5_309_h125_conditional_HS_chi2_NOT_ALLOWED.jsonl"
    if e5.sha256(path)!=e5sum.get("output_sha256",{}).get(path.name):
        raise ValueError("E5 309-source chi2 archive SHA mismatch")
    prev={}
    with path.open() as f:
        for line in f:
            row=json.loads(line);name=row["candidate_id"]
            if name in prev or name not in points or (
                row.get("full_Zee_physical_allowed_or_excluded") is not None):
                raise ValueError("Invalid source E5 model evidence")
            prev[name]=row
    if len(prev)!=309 or set(prev)!=set(points):
        raise ValueError("Source E5 309 case mapping incomplete")
    outproof={
       "E5_summary_SHA256":e5.sha256(e5dir/"summary.json"),
       "E5_manifest_SHA256":e5.sha256(e5dir/"manifest.json"),
       "E5_evidence_SHA256":e5.sha256(path),
       "source_E5_provenance":e5old,
       "dataset_sha256_manifest":dataset["dataset_sha256_manifest"],
       "script_SHA256":e5.sha256(Path(__file__)),
       "sectors":SECTORS,
    }
    return points,source,e4h_rows,prev,outproof


def do_sector(package,names):
    altered={**package,"effective_couplings":dict(package["effective_couplings"])}
    for name in names:
        altered["effective_couplings"][name]=1+0j if name not in ("WW","ZZ") else 1.
    return altered


def compute(signals,HP,package,reference,sm):
    _,chi_orig,_=None,None,None
    p,h,base,total=e5.build_predictions(HP,package)
    actual=e5.finite(signals(p),"original 125 HiggsSignals chi2")
    same(actual,reference["h125_effective_HiggsSignals_chi2"],
         "Original E5 full effective model chi2",atol=5e-6)
    same(actual-sm,reference["delta_chi2_vs_SM_same_dataset_NOT_calibrated_CL"],
         "Original E5 SM-delta chi2",atol=5e-6)
    same(total,reference["h125_total_width_with_h_LFV_GeV"],
         "Original E5 total width",atol=1e-9,rtol=5e-8)
    deltas={}
    for label,names in SECTORS.items():
        pred,_,_,_=e5.build_predictions(HP,do_sector(package,names))
        cf=e5.finite(signals(pred),"counterfactual "+label)
        deltas[label]={
            "chisq_if_sole_sector_restored_to_SM_NOT_physical_Zee_point":cf,
            "chisq_shift_relative_to_original":cf-actual,
            "restoration_improves_chisq_descriptively":bool(cf<actual)}
    c=package["effective_couplings"]
    return {
        "candidate_id":package["candidate_id"],
        "chi2_exactly_reproduced":actual,
        "delta_chi2_vs_fixed_SM":actual-sm,
        "kappaV":float(c["WW"]),
        "kappaTop":float(c["tt"].real),
        "kappaBottom":float(c["bb"].real),
        "kappaTauAbs":abs(c["tautau"]),
        "kappaTauReal":float(c["tautau"].real),
        "kappaTauImag":float(c["tautau"].imag),
        "delta_beta_minus_alpha":package["alignment_delta_beta_minus_alpha"],
        "cascade_proxy_NOT_actual_production_rate":
            package["cascade_proxy_not_xsec"],
        "counterfactuals_NOT_physical_Zee_models":deltas,
        "missing_charged_scalar_loop_amplitudes":True,
        "fully_allowed_or_excluded_Zee":None,
    }


def measurements_summary(signals,HP,packages,results,max_each=6):
    # A measurement's __call__ includes within-analysis correlations,
    # unlike chisqContributions() which sums decorrelated subresults.
    selected=(sorted(results,key=lambda k:results[k]["delta_chi2_vs_fixed_SM"])[:max_each]
      +sorted(results,key=lambda k:results[k]["delta_chi2_vs_fixed_SM"],reverse=True)[:max_each]
      +[x for x in ANCHORS if x in results])
    unique=list(dict.fromkeys(selected))
    ref=HP.Predictions()
    hh=ref.addParticle(HP.BsmParticle("h125",charge="neutral",cp="even"))
    hh.setMass(float(e5.MH))
    HP.effectiveCouplingInput(hh,HP.smLikeEffCouplings)
    ref_rows=[]
    for measurement in signals.measurements():
        # Measured per-analysis chisq includes within-measurement covariance.
        # Data derived from actual HS dataset, not invented uncertainty bins.
        chi_sm=e5.finite(measurement(ref),"SM per analysis chisq")
        ref_rows.append((measurement,chi_sm))
    results_out={}
    for name in unique:
        pred,_,_,_=e5.build_predictions(HP,packages[name])
        per=[]
        for measurement,chi_sm in ref_rows:
            delta=e5.finite(measurement(pred),"analysis chi2")-chi_sm
            if not math.isfinite(delta):
                raise ValueError("Nonfinite per-analysis chi2 difference")
            per.append({
                "measurement_id":int(measurement.id()),
                "measurement_reference":str(measurement.reference()),
                "source_json":str(measurement.loadedFrom()),
                "delta_chisq_within_measurement_covariance":delta,
                "note_cross_analysis_covariance_not_allocated":True,
            })
        per.sort(key=lambda q:abs(q[
            "delta_chisq_within_measurement_covariance"]),reverse=True)
        results_out[name]={
           "E5_full_delta_chisq":results[name]["delta_chi2_vs_fixed_SM"],
           "sum_separate_measurement_delta_chisq_NOT_guaranteed_equal_global":
             sum(x["delta_chisq_within_measurement_covariance"] for x in per),
           "leading_12_measurements_by_absolute_delta":per[:12],
           "ranked_by_absolute_not_a_statistical_partition":True,
        }
    return results_out,len(ref_rows)


def checkpoint_read(path,cohort):
    out={}
    if path.is_file():
        with path.open() as f:
            for line in f:
                row=json.loads(line);key=row["candidate_id"]
                if key in out or key not in cohort or (
                    row.get("fully_allowed_or_excluded_Zee") is not None):
                    raise ValueError("E5A checkpoint duplicate/corruption")
                e5.finite(row["chi2_exactly_reproduced"],"checkpoint chi2")
                if set(row["counterfactuals_NOT_physical_Zee_models"])!=set(SECTORS):
                    raise ValueError("E5A incomplete counterfactual checkpoint")
                out[key]=row
    return out


def finalize(out,results,details,manifest,smchi,nb):
    if len(results)!=309 or set(results)!=set(manifest["source_cohort_ids"]):
        raise ValueError("E5A incomplete 309 case set")
    main=out/"E5A_309_HS_sector_sensitivity_NOT_ALLOWED.jsonl"
    with main.open("w") as f:
        for name in sorted(results):
            f.write(json.dumps(results[name],sort_keys=True,allow_nan=False)+"\n")
    ordered=sorted(results.values(),key=lambda row:row["delta_chi2_vs_fixed_SM"])
    table=out/"E5A_309_ranked_drivers_NOT_ALLOWED.csv"
    with table.open("w",newline="") as f:
        labels=["candidate_id","delta_chi2_vs_SM","kappaBottom","kappaTauAbs",
                "kappaTop","kappaV","cascade_proxy","bottom_reset_shift",
                "lepton_reset_shift","top_reset_shift","VV_reset_shift",
                "fully_allowed_Zee"]
        w=csv.DictWriter(f,fieldnames=labels);w.writeheader()
        for row in ordered:
            d=row["counterfactuals_NOT_physical_Zee_models"]
            w.writerow({
                "candidate_id":row["candidate_id"],
                "delta_chi2_vs_SM":row["delta_chi2_vs_fixed_SM"],
                "kappaBottom":row["kappaBottom"],
                "kappaTauAbs":row["kappaTauAbs"],
                "kappaTop":row["kappaTop"],
                "kappaV":row["kappaV"],
                "cascade_proxy":row["cascade_proxy_NOT_actual_production_rate"],
                "bottom_reset_shift":d["bottom_down_strange_to_SM"]["chisq_shift_relative_to_original"],
                "lepton_reset_shift":d["diagonal_charged_leptons_to_SM"]["chisq_shift_relative_to_original"],
                "top_reset_shift":d["top_charm_up_to_SM"]["chisq_shift_relative_to_original"],
                "VV_reset_shift":d["VV_to_SM"]["chisq_shift_relative_to_original"],
                "fully_allowed_Zee":None,
            })
    dlt=np.asarray([r["delta_chi2_vs_fixed_SM"] for r in ordered],float)
    corr=np.asarray([r["kappaBottom"] for r in ordered],float)
    abs_bottom=np.abs(corr-1.)
    if not (np.isfinite(dlt).all() and np.isfinite(abs_bottom).all()):
        raise ValueError("E5A nonfinite delta chi2 or bottom coupling")
    # Pearson is mathematically undefined when one input is constant.
    # Synthetic 309-copy fixture deliberately exercises this limit.
    # Encode undefined as JSON null, never NaN and never a guessed 0.
    def informative_variance(a):
        return bool(np.std(a) > 1e-12*max(1.,float(np.max(np.abs(a)))))
    correlation_defined=(informative_variance(dlt) and
                         informative_variance(abs_bottom))
    pearson=(float(np.corrcoef(dlt,abs_bottom)[0,1])
             if correlation_defined else None)
    stats={
        "status":STATUS,"models":309,
        "HiggsSignals_SM_chi2_same_data":smchi,
        "HiggsSignals_observables":nb,
        "delta_chisq_percentiles":{
            str(q):float(np.quantile(dlt,q))
            for q in (0.,.1,.25,.5,.75,.9,1.)},
        "descriptive_number_delta_chi2_less_than_1":int(np.sum(dlt<1.)),
        "descriptive_number_delta_chi2_less_than_4":int(np.sum(dlt<4.)),
        "descriptive_number_delta_chi2_less_than_10":int(np.sum(dlt<10.)),
        "descriptive_number_delta_chi2_greater_than_100":int(np.sum(dlt>100.)),
        "pearson_approx_chisq_vs_abs_bottom_deviation":pearson,
        "pearson_approx_chisq_vs_abs_bottom_deviation_defined":
            correlation_defined,
        "undefined_correlations_serialized_as_JSON_null":True,
        "counterfactual_effects_are_not_valid_model_points":True,
        "individual_measurement_chisq_include_their_own_correlations":True,
        "cross_analysis_correlations_not_attributed":True,
        "missing_charged_scalar_one_loop_hgamgam_Zgam":True,
        "full_Zee_allowed_or_excluded":None,
        "top_diagnostic_measurements_case_count":len(details),
        "source_manifest":{k:v for k,v in manifest.items() if k!="source_cohort_ids"},
        "sha256_outputs":{p.name:e5.sha256(p) for p in (main,table)},
    }
    save=e5.save
    save(out/"E5A_selected_measurement_drivers_NOT_GLOBAL_CL.json",details)
    stats["sha256_measurement_detail"]=e5.sha256(
      out/"E5A_selected_measurement_drivers_NOT_GLOBAL_CL.json")
    save(out/"summary.json",stats)
    return stats


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ("e2-dir","e3-dir","e4h-dir","e5-dir","hs-dataset","output-dir"):
        ap.add_argument("--"+k,type=Path,required=True)
    ap.add_argument("--resume",action="store_true")
    a=ap.parse_args()
    out=a.output_dir.resolve()
    if not BASE.resolve().is_relative_to(Path("/home")):
        ap.error("Use only /home work checkout")
    if not out.is_relative_to(BASE.resolve()/"work"):
        ap.error("Output must be fresh directory in /home/aalida/zee/work")
    if not a.resume and out.exists() and any(out.iterdir()):
        ap.error("Nonempty output dir; choose a fresh directory or use --resume")
    if a.resume and not (out/"manifest.json").is_file():
        ap.error("Resume requires original manifest")
    out.mkdir(parents=True,exist_ok=True)
    try:
        import Higgs.predictions as HP
        import Higgs.signals as HS
        points,src,e4h,old,provenance=inputs(
            a.e2_dir.resolve(),a.e3_dir.resolve(),a.e4h_dir.resolve(),
            a.e5_dir.resolve(),a.hs_dataset.resolve())
        old_e5=e5.load(a.e5_dir.resolve()/"summary.json")
        dataset=e5.dataset_provenance(a.hs_dataset)
        manifest={
            **provenance,
            "Higgs_pred_module_path":str(Path(HP.__file__).resolve()),
            "Higgs_signals_module_path":str(Path(HS.__file__).resolve()),
            "source_cohort_ids":sorted(points),
        }
        for k in ("Higgs_pred_module_path","Higgs_signals_module_path"):
            if manifest[k]!=old_e5["provenance"][k]:
                raise ValueError("Different compiled HiggsTools module path from E5")
        if a.resume:
            before=e5.load(out/"manifest.json")
            if before.get("provenance")!=manifest or (out/"summary.json").exists():
                raise ValueError("E5A resume changed source or finished")
        else:
            e5.save(out/"manifest.json",{
                "status":"E5A_IN_PROGRESS_NO_EXCLUSION","provenance":manifest})
        signals,smchi,nobs=e5.sm_baseline(HP,HS,dataset["path"])
        same(smchi,old_e5[
            "HiggsSignals_chi2_SM_at_identical_125GeV_and_dataset"],
            "Different HiggsSignals SM chi2",atol=1e-6)
        if nobs!=159:raise ValueError("HiggsSignals observable count changed")
        packages={name:e5.model_couplings(points[name],src[name],e4h[name])
                  for name in sorted(points)}
        cp=out/"E5A_309_checkpoint.jsonl"
        done=checkpoint_read(cp,points)
        with cp.open("a") as stream:
            for i,name in enumerate(sorted(packages),1):
                if name in done:continue
                row=compute(signals,HP,packages[name],old[name],smchi)
                stream.write(json.dumps(row,sort_keys=True,allow_nan=False)+"\n")
                stream.flush();os.fsync(stream.fileno())
                done[name]=row
                print("E5A_SOURCE_REPRO",i,"/309",name,
                      "DELTA_CHI2",row["delta_chi2_vs_fixed_SM"],
                      "RESET_BOTTOM_SHIFT",row["counterfactuals_NOT_physical_Zee_models"][
                          "bottom_down_strange_to_SM"]["chisq_shift_relative_to_original"],
                      "NO_EXCLUSION",flush=True)
        detail,measurements=measurements_summary(signals,HP,packages,done)
        report=finalize(out,done,detail,manifest,smchi,nobs)
        report["loaded_HS_measurement_analyses"]=measurements
        e5.save(out/"summary.json",report)
        e5.save(out/"manifest.json",{"status":STATUS,
             "provenance":manifest,
             "summary_sha256":e5.sha256(out/"summary.json")})
        print("E5A_STATUS",STATUS,"SOURCE_REPRODUCED",309,
              "HS_MEASUREMENTS",measurements,
              "NO_ZEE_ALLOWED_EXCLUDED",flush=True)
        return 0
    except Exception as exc:
        e5.save(out/"error.json",{
            "status":BLOCKED,"error":repr(exc),
            "traceback":traceback.format_exc(),
            "full_Zee_allowed_or_excluded":None})
        print("E5A_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
