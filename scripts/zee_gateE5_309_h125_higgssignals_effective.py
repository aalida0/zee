#!/usr/bin/env python3
"""E5: 309 source-pinned Zee h(125) HiggsSignals effective-coupling fit.

This is a REAL HiggsSignals correlated chi^2 (if HiggsTools and a nonempty
HiggsSignals dataset are installed), using a limited 125-GeV effective
coupling approximation. Not a full Zee model HiggsSignals/HiggsBounds result:

* missing two-charged hH_i+H_i- one-loop amplitudes in h->gamgam,Zgam;
* HiggsTools' internal effective top/bottom/W loops are approximations;
* only h125 is input, not other heavy neutral scalars/charged states;
* general lepton Yukawa is retained in h->ee,mumu,tautau and h LFV;
* Type-II-like QUARK Yukawas are a model ansatz, not a proven UV Z2;
* HiggsTools dataset coverage/stats must be documented separately.
No arbitrary kappab cuts, no inferred p-values, no 'allowed Zee points'.

Refuses missing/empty HS datasets, inconsistent E2-E4H provenance,
incomplete 309-cohort, unvalidated source hashes and malformed outputs.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,os,sys,traceback,collections
from pathlib import Path
import numpy as np
from gateA1b_hierarchical_no_seed import ML
from gateB3_general_zee_charged_lepton_widths import complex_matrix
from zee_gateD5_h125_direct_LFV_27 import h125_widths,VEV,MH
from zee_gateE4h_309_direct_h125_lfv_screen import (
    preflight as e4h_preflight, STATUS as E4H_STATUS,sha as sha256)
ROOT=Path(__file__).resolve().parents[1]
STATUS="E5_309_HIGGSSIGNALS_EFFECTIVE_125_ONLY_APPROX_NOT_ALLOWED"
BLOCKED="E5_HIGGSSIGNALS_BLOCKED_NOT_ALLOWED"
HDECAYS={"h_to_e_mu":"emu","h_to_e_tau":"etau","h_to_mu_tau":"mutau"}
SM_MODES=("bb","WW","ZZ","tautau","mumu","gamgam","Zgam","gg","cc")
VALIDITY={
    "125_only_other_Zee_neutral_or_charged_searches":"NOT_INCLUDED",
    "charged_H1_H2_loop_amplitudes_h_gamgam_h_Zgam":"NOT_COMPUTED",
    "new_loop_contributions_h_gg":"NO_COLORED_NEW_PARTICLES_ASSUMED",
    "quark_TypeII_ansatz_RGE_well_defined":"NOT_ESTABLISHED",
    "full_production_STXS_acceptance":"EFFECTIVE_COUPLING_APPROX",
    "complete_Zee_HiggsBounds_exclusions":"NOT_EVALUATED",
    "statistically_calibrated_global_model_CL":"NOT_EVALUATED",
    "full_CLFV_and_2026_B_to_Xs_gamma":"NOT_VALIDATED",
    "numerical_vacuum_no_witness_global_minimum":"NOT_PROVEN",
}


def load(path):
    return json.loads(Path(path).read_text())


def save(path,data):
    Path(path).write_text(json.dumps(data,sort_keys=True,indent=2,
                               allow_nan=False)+"\n")


def dataset_provenance(folder):
    folder=Path(folder).resolve()
    files=sorted(p for p in folder.rglob("*.json") if p.is_file())
    if not files:raise ValueError("No HiggsSignals measurement .json files in dataset")
    if len(files)!=len({str(p.resolve()) for p in files}):
        raise ValueError("Duplicate dataset filenames")
    records=[]
    for p in files:
        if not p.resolve().is_relative_to(folder):
            raise ValueError("Dataset symlink outside selected tree: "+str(p))
        records.append((str(p.relative_to(folder)),sha256(p)))
    h=hashlib.sha256()
    for p,s in records:
        h.update((p+" "+s+"\n").encode("utf8"))
    return {"path":str(folder),"file_count":len(files),
            "dataset_sha256_manifest":h.hexdigest(),
            "files":records}


def validated_sources(e2,e3,e4h):
    points,sources,e2e3_source=e4h_preflight(e2,e3)
    summary=load(e4h/"summary.json")
    manifest=load(e4h/"manifest.json")
    details=e4h/"E4H_309_complete_h125_direct_LFV_NOT_ALLOWED.jsonl"
    if (summary.get("status")!=E4H_STATUS or
        summary.get("E3_optimized_original_models_tested")!=309 or
        summary.get("direct_Higgs_reference_screens_below_one_NOT_physical_allowed")!=309 or
        summary.get("full_Zee_allowed_or_excluded") is not None or
        manifest.get("status")!=E4H_STATUS or
        manifest.get("summary_SHA256")!=sha256(e4h/"summary.json") or
        summary.get("per_candidate_JSONL_SHA256")!=sha256(details) or
        summary.get("source_provenance_SHA256")!=e2e3_source):
        raise ValueError("E4H 309-point source SHA/status mismatch")
    reference={}
    with details.open() as stream:
        for line in stream:
            z=json.loads(line);tag=z["candidate_id"]
            if tag in reference or tag not in points or (
                  z["physical_Zee_allowed_or_excluded"] is not None):
                raise ValueError("Invalid E4H 309 per-spectrum record")
            reference[tag]=z
    if set(reference)!=set(points) or set(points)!=set(sources) or len(points)!=309:
        raise ValueError("E2/E3/E4H unique source model identifiers differ")
    return points,sources,reference,{
      "E2_E3_E4H_primary_provenance":e2e3_source,
      "E4H_summary_SHA256":sha256(e4h/"summary.json"),
      "E4H_manifest_SHA256":sha256(e4h/"manifest.json"),
      "E4H_full_JSONL_SHA256":sha256(details),
    }


def finite(x,label):
    val=float(x)
    if not math.isfinite(val):raise ValueError("Nonfinite "+label)
    return val


def model_couplings(p,src,reference):
    tag=p["id"]
    if src["candidate_id"]!=tag or reference["candidate_id"]!=tag:
        raise ValueError("Inconsistent original Zee source ID")
    opt=src["D2"]["chosen_optimized_source"]["solution"]
    if opt["candidate_id"]!=tag:raise ValueError("E3 optimized Yukawa ID mismatch")
    Y=complex_matrix(opt["Y"],"Y")
    if Y.shape!=(3,3) or not np.isfinite(Y).all():
        raise ValueError("Nonfinite E3 optimized lepton Yukawa")
    h=h125_widths(p,Y)
    for channel in HDECAYS:
        old=finite(reference["h125_tree_LFV_partial_widths_GeV"][channel],
                   "E4H h LFV width")
        new=finite(h["h125_LFV_partial_widths_GeV"][channel],
                   "E5 h LFV width")
        if not math.isclose(old,new,rel_tol=2e-9,abs_tol=1e-15):
            raise ValueError("E4H/H125 same-Yukawa source recalculation mismatch")
    # h125 physical matrix C: SM diagonal mass/v modified by general Zee Y.
    # HiggsTools normalizes diagonal couplings to m_l/v.
    data=h["h125_physical_Yukawa_C"]
    C=np.asarray(data["real"],float)+1j*np.asarray(data["imag"],float)
    if C.shape!=(3,3) or not np.isfinite(C).all():
        raise ValueError("Wrong h125 complex coupling matrix")
    sm=np.asarray(np.diag(ML),float)/VEV
    if np.any(sm<=0):raise ValueError("Charged lepton SM masses invalid")
    ratios=np.diag(C)/sm
    kV=finite(h["kappa_V_tree"],"kappaV")
    kt=finite(h["kappa_top_TypeII_ansatz"],"kappaTop")
    kb=finite(h["kappa_bottom_TypeII_ansatz"],"kappaBottom")
    delta=float(p["beta"])-float(p["alpha"])
    if not math.isclose(kV,math.cos(delta),rel_tol=1e-11,abs_tol=1e-13):
        raise ValueError("Alignment convention corrupted")
    result={
      "uu":complex(kt),"dd":complex(kb),
      "cc":complex(kt),"ss":complex(kb),
      "tt":complex(kt),"bb":complex(kb),
      "ee":complex(ratios[0]),
      "mumu":complex(ratios[1]),"tautau":complex(ratios[2]),
      "WW":float(kV),"ZZ":float(kV),
      # The effective input calculates ggH from t/b and h->gamgam
      # from SM W/fermions using HiggsTools (defaults calc... True).
      # The stand-in Zgamma=1 MUST remain explicitly provisional.
      "Zgam":1.,"gg":1.,"gamgam":1.,"lam":1.,
    }
    for k,v in result.items():
        if not(math.isfinite(complex(v).real) and math.isfinite(complex(v).imag)):
            raise ValueError("Nonfinite effective coupling "+k)
    return {
      "candidate_id":tag,
      "effective_couplings":result,
      "h125_exact_LFV_GeV":{
         channel:float(h["h125_LFV_partial_widths_GeV"][channel])
         for channel in HDECAYS},
      "scalar":{k:float(p[k]) for k in ("mH1","mH2","mh2","ma",
                                     "alpha","beta","gamma")},
      "cascade_proxy_not_xsec":float(p[
          "production_weighted_nonleptonic_cascade_upper_proxy"]),
      "D4_partial_LFV_score_NOT_a_complete_rate":float(src[
          "selected_D4_extended_partial_LFV_score_NOT_EXCLUSION"]),
      "E4H_reference_ratio_NOT_a_fit":float(reference[
          "worst_h125_direct_reference_ratio"]),
      "alignment_delta_beta_minus_alpha":delta,
      "h125_mass_used_GeV":float(MH),
    }


def build_predictions(HP,package):
    pred=HP.Predictions()
    h=pred.addParticle(HP.BsmParticle("h125",charge="neutral",cp="even"))
    h.setMass(float(MH))
    ec=HP.NeutralEffectiveCouplings()
    for k,v in package["effective_couplings"].items():
        setattr(ec,k,v)
    HP.effectiveCouplingInput(h,ec)
    original=finite(h.totalWidth(),"E5 baseline total width")
    for ch,d in HDECAYS.items():
        h.setDecayWidth(d,package["h125_exact_LFV_GeV"][ch])
    total=finite(h.totalWidth(),"E5 LFV-updated total width")
    if original<=0 or total<=0 or total<original*(1-1e-9):
        raise ValueError("HiggsTools total-width negative/decreased after adding LFV")
    summed=sum(package["h125_exact_LFV_GeV"].values())
    if not math.isclose(total,original+summed,rel_tol=2e-8,abs_tol=1e-10):
        raise ValueError("HiggsTools LFV widths not added exactly once")
    return pred,h,original,total


def sm_baseline(HP,HS,dataset):
    reference=HP.Predictions()
    h=reference.addParticle(HP.BsmParticle("h125",charge="neutral",cp="even"))
    h.setMass(float(MH))
    HP.effectiveCouplingInput(h,HP.smLikeEffCouplings)
    signals=HS.Signals(str(dataset))
    if signals.observableCount()<=0:
        raise ValueError("HiggsSignals dataset contains no loaded observables")
    chi2=finite(signals(reference),"HiggsSignals exact SM chi2")
    return signals,chi2,int(signals.observableCount())


def analyze_one(signals,HP,pack,sm_chisq):
    pred,h,prior,total=build_predictions(HP,pack)
    chi2=finite(signals(pred),"HiggsSignals E5 chi2")
    kappas=pack["effective_couplings"]
    return {
      "candidate_id":pack["candidate_id"],
      "h125_effective_HiggsSignals_chi2":chi2,
      "delta_chi2_vs_SM_same_dataset_NOT_calibrated_CL":chi2-sm_chisq,
      "h125_total_width_before_offdiagonal_LFV_GeV":prior,
      "h125_total_width_with_h_LFV_GeV":total,
      "h125_Zee_LFV_partial_width_sum_GeV":
          sum(pack["h125_exact_LFV_GeV"].values()),
      "h125_BRs_effective_approx":{key:finite(h.br(key),"BR "+key)
                                    for key in SM_MODES},
      "h125_effective_kappaV":kappas["WW"],
      "h125_effective_kappa_top":float(kappas["tt"].real),
      "h125_effective_kappa_bottom":float(kappas["bb"].real),
      "h125_effective_tau_ratio_real":float(kappas["tautau"].real),
      "h125_effective_tau_ratio_imag":float(kappas["tautau"].imag),
      "h125_leptonic_source_match":True,
      "h125_standalone_only":True,
      "h125_gamgam_missing_charged_Zee_scalar_loops":True,
      "HiggsSignals_is_real_fit_of_CONDITIONAL_effective_coupling_model":True,
      "full_Zee_physical_allowed_or_excluded":None,
    }


def checkpoint(path,valid):
    rows={}
    if path.is_file():
        with path.open() as f:
            for line in f:
                row=json.loads(line);tag=row["candidate_id"]
                if tag in rows or tag not in valid or (
                     row.get("full_Zee_physical_allowed_or_excluded") is not None):
                    raise ValueError("Corrupted E5 checkpoint")
                finite(row["h125_effective_HiggsSignals_chi2"],"checkpoint HS chi2")
                rows[tag]=row
    return rows


def finish(output,packages,results,manifest,sm_chisq,nobs):
    if set(results)!=set(packages) or len(results)!=309:
        raise ValueError("Cannot finalize incomplete 309 E5 HiggsSignals evaluations")
    record=output/"E5_309_h125_conditional_HS_chi2_NOT_ALLOWED.jsonl"
    with record.open("w") as f:
        for key in sorted(results):
            f.write(json.dumps(results[key],sort_keys=True,allow_nan=False)+"\n")
    data=[]
    for key,row in results.items():
        pack=packages[key]
        data.append({
          "candidate_id":key,
          "mH1_GeV":pack["scalar"]["mH1"],
          "mH2_GeV":pack["scalar"]["mH2"],
          "beta_minus_alpha":pack["alignment_delta_beta_minus_alpha"],
          "kappaV":row["h125_effective_kappaV"],
          "kappa_top":row["h125_effective_kappa_top"],
          "kappa_bottom":row["h125_effective_kappa_bottom"],
          "kappa_tau_abs":abs(pack["effective_couplings"]["tautau"]),
          "h125_total_width_effective_GeV":
              row["h125_total_width_with_h_LFV_GeV"],
          "chi2_conditional_125_only":row["h125_effective_HiggsSignals_chi2"],
          "delta_chi2_vs_SM_same_dataset":
              row["delta_chi2_vs_SM_same_dataset_NOT_calibrated_CL"],
          "cascade_proxy_NOT_cross_section":pack["cascade_proxy_not_xsec"],
          "full_Zee_allowed":None,
        })
    data.sort(key=lambda r:(r["delta_chi2_vs_SM_same_dataset"],
                            -r["cascade_proxy_NOT_cross_section"]))
    dst=output/"E5_309_ranked_conditional_h125_HiggsSignals_NOT_ALLOWED.csv"
    with dst.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(data[0]))
        writer.writeheader();writer.writerows(data)
    chi=[r["delta_chi2_vs_SM_same_dataset"] for r in data]
    summary={
      "status":STATUS,
      "number_E2_E3_E4H_source_optimized_models":309,
      "HiggsSignals_chi2_evaluated_in_effective_coupling_approx":309,
      "HiggsSignals_number_loaded_observables":nobs,
      "HiggsSignals_chi2_SM_at_identical_125GeV_and_dataset":sm_chisq,
      "delta_chi2_vs_SM_min":min(chi),
      "delta_chi2_vs_SM_median":float(np.median(chi)),
      "delta_chi2_vs_SM_max":max(chi),
      "naive_delta_chi2_NOT_a_model_CL":True,
      "full_model_allowed_points":None,
      "charged_Zee_scalar_loop_amplitudes_missing":True,
      "complete_HiggsBounds_not_run":True,
      "model_125_only":True,
      "scientific_validity":VALIDITY,
      "provenance":manifest,
      "output_sha256":{p.name:sha256(p) for p in (record,dst)},
    }
    save(output/"summary.json",summary)
    return summary


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--e2-dir",type=Path,required=True)
    ap.add_argument("--e3-dir",type=Path,required=True)
    ap.add_argument("--e4h-dir",type=Path,required=True)
    ap.add_argument("--hs-dataset",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    ap.add_argument("--resume",action="store_true")
    a=ap.parse_args()
    if not ROOT.resolve().is_relative_to(Path("/home")):
        ap.error("Run source only under /home project checkout")
    out=a.output_dir.resolve()
    if not out.is_relative_to(ROOT.resolve()/"work"):
        ap.error("Output must be in /home project work/")
    if not a.resume and out.exists() and any(out.iterdir()):
        ap.error("Refuse overwriting an existing E5 output")
    if a.resume and not (out/"manifest.json").is_file():
        ap.error("Cannot resume without old E5 manifest")
    out.mkdir(parents=True,exist_ok=True)
    try:
        import Higgs.predictions as HP
        import Higgs.signals as HS
        import Higgs
        pts,src,e4h,provenance=validated_sources(
            a.e2_dir.resolve(),a.e3_dir.resolve(),a.e4h_dir.resolve())
        dataset=dataset_provenance(a.hs_dataset)
        manifest={
           "source":provenance,
           "dataset":{
             "dataset_sha256_manifest":dataset["dataset_sha256_manifest"],
             "file_count":dataset["file_count"],
             "path":dataset["path"]},
           "main_source_script_sha256":sha256(Path(__file__)),
           "Higgs_pred_module_path":str(Path(HP.__file__).resolve()),
           "Higgs_signals_module_path":str(Path(HS.__file__).resolve()),
           "h125_mass_GeV":float(MH),
           "partial_model_flags":VALIDITY,
        }
        if a.resume:
            old=load(out/"manifest.json")
            if old["provenance"]!=manifest or (out/"summary.json").is_file():
                raise ValueError("E5 resume fingerprint mismatch or already complete")
        else:
            save(out/"manifest.json",{"status":"E5_HS_IN_PROGRESS_NOT_ALLOWED",
                                       "provenance":manifest})
        packages={key:model_couplings(pts[key],src[key],e4h[key])
                  for key in sorted(pts)}
        # This is REAL HiggsSignals evaluated on the original installed
        # measurement dataset; no invented experimental errors/cutoffs.
        signals,smchi,nobs=sm_baseline(HP,HS,dataset["path"])
        print("E5_SM_HIGGSSIGNALS_CHI2",smchi,
              "N_OBSERVABLES",nobs,flush=True)
        checkpoint_file=out/"E5_309_checkpoint.jsonl"
        completed=checkpoint(checkpoint_file,packages)
        with checkpoint_file.open("a") as stream:
            for idx,key in enumerate(sorted(packages),1):
                if key in completed:continue
                row=analyze_one(signals,HP,packages[key],smchi)
                stream.write(json.dumps(row,sort_keys=True,allow_nan=False)+"\n")
                stream.flush();os.fsync(stream.fileno())
                completed[key]=row
                print("E5_HIGGSSIGNALS_125_ONLY",idx,"/309",key,
                      "CHI2",row["h125_effective_HiggsSignals_chi2"],
                      "DELTA_CHI2_VS_SM",
                      row["delta_chi2_vs_SM_same_dataset_NOT_calibrated_CL"],
                      "APPROX_NO_ZEE_EXCLUSION",flush=True)
        summary=finish(out,packages,completed,manifest,smchi,nobs)
        save(out/"manifest.json",{"status":STATUS,"provenance":manifest,
                                "summary_SHA256":sha256(out/"summary.json")})
        print("E5_STATUS",STATUS,"HIGGSSIGNALS_POINTS",309,
              "SM_CHI2",smchi,"FULL_ZEE_ALLOWED_UNKNOWN",flush=True)
        print("E5_SUMMARY",out/"summary.json",flush=True)
        return 0
    except Exception as exc:
        save(out/"error.json",{"status":BLOCKED,"error":repr(exc),
                              "traceback":traceback.format_exc(),
                              "full_Zee_allowed":None})
        print("E5_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
        return 1


if __name__=="__main__":
    raise SystemExit(main())
