#!/usr/bin/env python3
"""Merge four complete CERN F20 production shards into scan plots/CSVs.

Refuse absent/incomplete/error shards, mixed original F18-F19d SHA
cohorts and fake full-model approval. Outputs an exploratory BFB/EWPO +
LO flavor + fixed-NO partial-LFV scan for paper TRIAGE, not CL contours.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,tarfile
from pathlib import Path

EXPECTED_STATUS="F20_AF_INDEPENDENT_LARGE_SCALAR_NEUTRINO_PARTIAL_LFV_LO_FLAVOR_VACUUM_SCAN_NOT_ALLOWED"
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def tarbytes(t,member):
    entry=t.getmember(member)
    if not entry.isfile() or not 0<entry.size<200000000:
        raise ValueError("Invalid F20 tar archive member "+member)
    f=t.extractfile(entry)
    if f is None:raise ValueError("Missing tar stream "+member)
    return f.read()
def read_csv(data):
    r=list(csv.DictReader(io.StringIO(data.decode())))
    if not r:raise ValueError("F20 CSV contains no rows")
    return r
def merged_pareto(rows):
    ordered=sorted(rows,key=lambda r:(
        float(r["LO_Bsgamma_shift_x1e4_NOT_CL"]),
        -float(r["cascade_included_nonleptonic_proxy_NOT_F18_MadWidth"])))
    best=-math.inf;front=[]
    for r in ordered:
        value=float(r["cascade_included_nonleptonic_proxy_NOT_F18_MadWidth"])
        if value>best+1e-15:
            front.append(r);best=value
    return front
def save_csv(path,rows):
    if not rows:raise ValueError("Never write empty global F20 result")
    cols=list(rows[0])
    with Path(path).open("w",newline="") as h:
        w=csv.DictWriter(h,fieldnames=cols,extrasaction="ignore")
        w.writeheader();w.writerows(rows)
def run(eos,out,nshards=4):
    eos=Path(eos).expanduser()
    out=Path(out).expanduser().resolve()
    if out.exists():raise FileExistsError("Never overwrite merged F20 science record")
    if nshards!=4:raise ValueError("Four configured independent F20 shards expected")
    hashes={};source=None;seen=[];allscalar=[];allfits=[];stats=[]
    archive_manifest={}
    for j in range(nshards):
        path=eos/("F20_result_shard_"+str(j)+".tar.gz")
        if not path.is_file():raise FileNotFoundError(path)
        with tarfile.open(path,"r:gz") as t:
            ext=tarbytes(t,"F20_shard_"+str(j)+".exit").decode().strip()
            if ext!="F20_SHARD_"+str(j)+"_EXIT_CODE=0":
                raise ValueError("F20 worker shard "+str(j)+" FAILED: "+ext)
            folder="physics_results/F20_shard_"+str(j)+"/"
            summary=json.loads(tarbytes(t,folder+"F20_shard_complete_summary.json"))
            if (summary.get("status")!=EXPECTED_STATUS
                or summary.get("shard")!=j
                or summary.get("model_fully_allowed_or_excluded") is not None
                or summary.get("theoretical_95pct_Zee_exclusion") is not None):
                raise ValueError("F20 shard source/limitation contract invalid "+str(j))
            cur=summary["original_source_SHA256"]
            if source is not None and source!=cur:
                raise ValueError("F20 shards do not have same original F18-F19d model")
            source=cur
            scalar=read_csv(tarbytes(t,folder+"F20_all_scalar_LO_flavor_NOT_EXCLUSION.csv"))
            fit=read_csv(tarbytes(t,folder+"F20_paper_scan_shortlist_NOT_ALLOWED.csv"))
            if (len(scalar)!=summary["analytic_LO_two_charged_flavor_evaluated_points"]
                or len(fit)!=summary["neutrino_partial_LFV_attempted"]):
                raise ValueError("F20 numerical count/CSV integrity discrepancy "+str(j))
            if any(r["shard"]!=str(j) for r in scalar):
                raise ValueError("F20 shard index in scalar rows was corrupted")
            for r in scalar:r["campaign_unique_key"]=str(j)+"/"+r["candidate_id"]
            for r in fit:r["campaign_unique_key"]=str(j)+"/"+r["candidate_id"]
            allscalar.extend(scalar);allfits.extend(fit);stats.append(summary)
            hashes[str(j)]=sha(path)
            archive_manifest[str(j)]=len(t.getmembers())
            print("F20_MERGE_SHARD",j,"SCALAR",len(scalar),"NEUTRINO_FIT",len(fit),
                  "VACUUM",summary["vacuum_multistart_evaluated"],flush=True)
    count=len(allscalar)
    front=merged_pareto(allscalar)
    allfits.sort(key=lambda r:(
       not r.get("LFV_partial_score_NOT_EXCLUSION"),
       -float(r["cascade_included_LO_proxy_NOT_MadWidth"] or 0)))
    out.mkdir(parents=True,exist_ok=False)
    save_csv(out/"F20_ALL_shards_scalar_LO_flavor_NOT_EXCLUSION.csv",allscalar)
    save_csv(out/"F20_ALL_shards_cascade_flavor_Pareto_NOT_CL.csv",front)
    save_csv(out/"F20_ALL_shards_fixed_NO_partial_LFV_shortlist_NOT_ALLOWED.csv",allfits)
    report={
      "status":"F20_FOUR_SHARDS_MERGED_EXPLORATORY_SCAN_NOT_FULL_ZEE_ALLOWED",
      "four_complete_shards":True,
      "original_exact_three_F18_F19_F19b_F19c_F19d_SHA256":source,
      "HTCondor_output_tar_SHA256":hashes,
      "total_independently_seeded_proposals":sum(q["steps"] for q in stats),
      "screened_scalar_parameter_records_not_unique_allowed_volume":count,
      "frontier_points_not_a_confidence_contour":len(front),
      "complex_fixed_NO_partial_LFV_fits_attempted":sum(
            q["neutrino_partial_LFV_attempted"] for q in stats),
      "complex_fixed_NO_partial_LFV_fits_completed":sum(
            q["neutrino_partial_LFV_completed"] for q in stats),
      "full_tree_vacuum_witness_searches":sum(
            q["vacuum_multistart_evaluated"] for q in stats),
      "MadWidth_or_production_rate_calculated_for_new_scan_points":False,
      "complete_2026_bsgamma_and_complete_LFV_applied":False,
      "calibrated_model_exclusions_or_accepted_points":None,
      "paper_submission_physics_complete":False,
      "limitations":stats[0]["missing_for_publishable_complete_model"],
      "shard_summaries":stats,
      "output_files_SHA256":{f.name:sha(f) for f in out.glob("*.csv")},
    }
    (out/"F20_PRODUCTION_exploratory_summary.json").write_text(
      json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    # Figure panels from the *actual* scan points only. Plotting optional.
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        x=[float(r["LO_Bsgamma_linearized_x1e4_NOT_CL"]) for r in allscalar]
        y=[float(r["cascade_included_nonleptonic_proxy_NOT_F18_MadWidth"]) for r in allscalar]
        fig,ax=plt.subplots(figsize=(6.5,5))
        ax.scatter(x,y,s=7,alpha=.26)
        ax.set_xlabel(r"Linearized LO $10^4\,\\mathrm{BR}(B\\to X_s\\gamma)$ (not CL)")
        ax.set_ylabel(r"Included-channel cascade production-weighted proxy (not pb)")
        ax.set_title("Zee scalar/EWPO-screened exploration: 4 independent seeds")
        fig.tight_layout()
        fig.savefig(out/"F20_cascade_vs_LO_bsgamma_exploratory.png",dpi=180)
        plt.close(fig)
        m1=[float(r["mH1"]) for r in allscalar]
        m2=[float(r["mH2"]) for r in allscalar]
        fig,ax=plt.subplots(figsize=(6.5,5))
        pts=ax.scatter(m1,m2,c=y,s=9,alpha=.5)
        fig.colorbar(pts,ax=ax,label="Included-channel cascade proxy, not pb")
        ax.set_xlabel(r"$m_{H_1^\\pm}$ [GeV]")
        ax.set_ylabel(r"$m_{H_2^\\pm}$ [GeV]")
        ax.set_title("Exploratory scalar/EWPO subset, not an allowed region")
        fig.tight_layout()
        fig.savefig(out/"F20_mass_plane_proxy_exploratory.png",dpi=180)
        plt.close(fig)
    except ImportError:
        print("F20_PLOTS_SKIPPED_NO_MATPLOTLIB",flush=True)
    print("F20_GLOBAL_MERGE_COMPLETED",count,"SCALAR_POINTS",len(front),
         "PARETO_POINTS",report["complex_fixed_NO_partial_LFV_fits_completed"],
         "COMPLEX_SAVED","FULL_MODEL_ALLOWED",None,flush=True)
    print("F20_MERGE_OUTPUT",out)
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--eos-results",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    args=p.parse_args()
    run(args.eos_results,args.output_dir)
if __name__=="__main__":main()
