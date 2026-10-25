#!/usr/bin/env python3
"""Merge 24 F21b broad Zee scalar+partial LFV+vacuum shards.

WIDE explored parameter window, not a 95%-CL allowed contour. Refuse
missing / failed / mismatched original CERN/F20 input sources.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,tarfile
from collections import Counter,defaultdict
from pathlib import Path
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def tarbytes(t,member):
    entry=t.getmember(member)
    if not entry.isfile() or not 0<entry.size<200000000:
        raise ValueError("Invalid archived F21 member "+member)
    f=t.extractfile(entry)
    if f is None:raise ValueError("F21 archive could not read "+member)
    return f.read()
def save_csv(path,rows):
    if not rows:raise ValueError("Cannot write empty F21 result CSV")
    with Path(path).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),extrasaction="ignore")
        w.writeheader();w.writerows(rows)

STATUS="F21_STRATIFIED_WIDE_ZEE_SCALAR_FIXED_NO_PARTIAL_LFV_VACUUM_NOT_ALLOWED"
def read(data):
    x=list(csv.DictReader(io.StringIO(data.decode())))
    if not x:raise ValueError("Missing wide-scan physics CSV rows")
    return x
def numerical(row,key):
    try:
        x=float(row[key])
    except (TypeError,ValueError,KeyError) as e:
        raise ValueError("Missing/nonfinite "+key) from e
    if not math.isfinite(x):raise ValueError("Nonfinite "+key)
    return x
def run(eos,out):
    eos=Path(eos).expanduser()
    out=Path(out).expanduser().resolve()
    if out.exists():raise FileExistsError("Never overwrite F21 original merged result")
    summaries=[];anchors=None;allscalar=[];allfit=[];archives={}
    mergedattempts=Counter();mergedpasses=Counter();mergedreject=Counter()
    for j in range(24):
        archive=eos/f"F21_result_shard_{j}.tar.gz"
        if not archive.is_file():raise FileNotFoundError(archive)
        with tarfile.open(archive,"r:gz") as t:
            code=tarbytes(t,f"F21_shard_{j}.exit").decode().strip()
            if code!=f"F21_SHARD_{j}_EXIT_CODE=0":
                raise ValueError("F21 wide-scan HTCondor worker failed "+code)
            pre=f"results/F21_shard_{j}/"
            summ=json.loads(tarbytes(t,pre+"F21_SHARD_COMPLETED_summary.json"))
            if (summ.get("status")!=STATUS or summ.get("shard")!=j or
                summ.get("model_allowed_or_excluded") is not None or
                summ.get("complete_two_state_Bsgamma") is not False or
                summ.get("full_LFV_oscillation_NO_IO") is not False or
                summ.get("full_HiggsTools_or_real_production") is not False):
                raise ValueError("F21 shard model eligibility is mislabeled "+str(j))
            this={**summ.get("original_F18_F19d_sources",{}),
                  "F20csv":summ["source_F20_original_SHA256"]}
            if anchors is not None and this!=anchors:
                raise ValueError("F21b 24 shards used inconsistent original model datasets")
            anchors=this
            sr=read(tarbytes(t,pre+"F21_WIDE_all_scalar_LO_screen_NOT_ALLOWED.csv"))
            fr=read(tarbytes(t,pre+"F21_WIDE_complex_fY_LFV_vacuum_shortlist_NOT_ALLOWED.csv"))
            if (len(sr)!=summ["distinct_scalar_EWPO_screened"] or
                len(fr)!=summ["complex_LFV_fits_attempted"]):
                raise ValueError("F21 mismatch actual per-shard source files/count")
            if any(int(float(r["shard"]))!=j for r in sr+fr):
                raise ValueError("F21 mixed up per-shard candidate IDs")
            for k in ("model_allowed_or_excluded",):
                if any(r.get(k) not in (None,"","UNKNOWN_NOT_EVALUATED") for r in sr):
                    raise ValueError("F21 illegitimate model allowance")
            if any(r.get("fully_allowed_or_excluded")!="UNKNOWN_NOT_EVALUATED"
                   for r in fr):
                raise ValueError("F21 LFV table falsely labels viability")
            for r in sr:r["campaign_key"]=f"{j}/"+r["id"]
            for r in fr:r["campaign_key"]=f"{j}/"+r["candidate_id"]
            allscalar.extend(sr);allfit.extend(fr)
            summaries.append(summ);archives[str(j)]=sha(archive)
            for name,data in summ["per_origin_mH2_bin"].items():
                mergedattempts[name]+=int(data["tried"])
                mergedpasses[name]+=int(data["passed"])
            mergedreject.update(summ["rejections"])
            print("F21_MERGE_SHARD",j,"SCALAR",len(sr),"FITTED",summ["complex_LFV_fits_completed"],
                 "VACUUM",summ["vacuum_witness_searches_attempted"],flush=True)
    # This is not an inferred posterior or a physical allowed population.
    accepted=[r for r in allfit
              if (r.get("numerical_no_deeper_tree_witness_NOT_CERTIFICATE")=="True"
                  and r.get("partial_LFV_Wgamma_max_ratio_NOT_CL") not in ("",None)
                  and numerical(r,"partial_LFV_Wgamma_max_ratio_NOT_CL")<1
                  and r.get("complex_Yukawa_included_cascade_proxy_NOT_MadWidth") not in ("",None))]
    accepted.sort(key=lambda r:-numerical(r,
        "complex_Yukawa_included_cascade_proxy_NOT_MadWidth"))
    coverage=Counter()
    for r in allscalar:
        b=str(int(float(r["mH2_stratum"])))
        coverage["mH2_"+b]+=1
        coverage["tanb_"+str(int(float(r["tanbeta_stratum"])))]+=1
        coverage["gamma_"+str(int(float(r["gamma_stratum"])))]+=1
    out.mkdir(parents=True,exist_ok=False)
    save_csv(out/"F21_ALL_wide_scalar_LO_flavor_NOT_ALLOWED.csv",allscalar)
    save_csv(out/"F21_ALL_wide_neutrino_partial_LFV_NOT_ALLOWED.csv",allfit)
    if accepted:
        save_csv(out/"F21_WIDE_vacuum_LFV_triaged_cascade_NOT_FULL_ALLOWED.csv",accepted)
        save_csv(out/"F21_WIDE_vacuum_LFV_triaged_analytic_LO_flavor_NOT_CL.csv",
                 sorted(accepted,key=lambda r:numerical(r,
                   "analytic_LO_Bsgamma_BR_x1e4_NOT_CL")))
    report={
       "status":"F21B_24_SHARDS_WIDE_EXPLORATORY_MODEL_NOT_ALLOWED",
       "source_Sha256_F18_through_F20":anchors,
       "CERN_24_result_tar_SHA256":archives,
       "strata_mH2_GeV":(450,700,1000,1400,1900,2500),
       "strata_tanbeta":(.7,1.5,3,7,15,35),
       "strata_gamma_rad":(.08,.4,.8,1.15,1.49),
       "shards_complete":24,
       "total_independent_stratified_and_local_proposals":sum(
          x["attempts"] for x in summaries),
       "total_scalar_EWPO_screened_distinct_per_shard_not_physical_allowed":len(allscalar),
       "raw_scalar_EWPO_pass_count_not_allowed_volume":sum(
          x["raw_scalar_EWPO_passes"] for x in summaries),
       "accepted_strata_record_count_not_allowed_volume":dict(coverage),
       "attempted_by_generator_and_mH2_bin":dict(mergedattempts),
       "passes_by_generator_and_mH2_bin":dict(mergedpasses),
       "rejections":dict(mergedreject),
       "complex_neutrino_fixed_NO_partial_LFV_fits_attempted":sum(
          x["complex_LFV_fits_attempted"] for x in summaries),
       "complex_neutrino_fixed_NO_partial_LFV_fits_completed":sum(
          x["complex_LFV_fits_completed"] for x in summaries),
       "vacuum_multistart_searches_attempted":sum(
          x["vacuum_witness_searches_attempted"] for x in summaries),
       "vacuum_no_deeper_witness_AND_LFV_partial_score_lt1_subset_NOT_ALLOWED":len(accepted),
       "complete_modern_bsgamma_LFV_HiggsTools_real_LHC_prediction":False,
       "paper_fully_allowed_or_excluded_points":None,
       "shard_summaries":summaries,
       "CSV_SHA256":{x.name:sha(x) for x in out.glob("*.csv")}}
    (out/"F21_WIDE_PRODUCTION_summary_NOT_ALLOWED.json").write_text(
       json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        # Three independent physical parameter projections, scatter not CL.
        panels=[
            ("mH2","tanbeta","F21_MH2_vs_tanbeta_exploratory.png",
             r"$m_{H_2^\pm}$ [GeV]",r"$\tan\beta$"),
            ("mH2","gamma","F21_MH2_vs_gamma_exploratory.png",
             r"$m_{H_2^\pm}$ [GeV]",r"$\gamma$ [rad]"),
            ("mH1","mH2","F21_charged_mass_plane_exploratory.png",
             r"$m_{H_1^\pm}$ [GeV]",r"$m_{H_2^\pm}$ [GeV]")]
        for xx,yy,name,xlab,ylab in panels:
            fig,ax=plt.subplots(figsize=(7,5))
            xs=[numerical(z,xx) for z in allscalar]
            ys=[numerical(z,yy) for z in allscalar]
            col=[numerical(z,"LO_flavor_BR_x1e4_NOT_CL") for z in allscalar]
            pts=ax.scatter(xs,ys,c=col,s=5,alpha=.5)
            fig.colorbar(pts,ax=ax,label="LO linearized $10^4$ BR (not CL)")
            ax.set_xlabel(xlab);ax.set_ylabel(ylab)
            ax.set_title("Stratified scalar/EWPO Zee screens (not full allowed)")
            fig.tight_layout();fig.savefig(out/name,dpi=170);plt.close(fig)
    except ImportError:
        print("F21_PLOTS_SKIPPED_MATPLOTLIB_UNAVAILABLE",flush=True)
    print("F21_WIDE_MERGED_SUCCESS","SCALAR",len(allscalar),
         "COMPLEX_FY",report["complex_neutrino_fixed_NO_partial_LFV_fits_completed"],
         "VACUUM",report["vacuum_multistart_searches_attempted"],
         "SCOPED_TRIAGE",len(accepted),"FULL_ALLOWED",None,flush=True)
    print("F21_WIDE_SUMMARY",out/"F21_WIDE_PRODUCTION_summary_NOT_ALLOWED.json")
    return report
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--eos",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.eos,a.out)
if __name__=="__main__":main()
