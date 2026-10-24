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
            # Important: the original F20 shortlist contains B4's
            # NONLEPTONIC upper proxy even though each optimization
            # actually recomputed f/Y-dependent charged-lepton widths
            # with B3. Recover the already-evaluated physical-subset
            # cascade from the archived 30 point_*.json files, without
            # rerunning the scan or relabeling as full MadWidth.
            prefix=folder+"point_"
            pt_members=sorted(m.name for m in t.getmembers()
                if m.isfile() and m.name.startswith(prefix)
                and m.name.endswith("_NOT_ALLOWED.json"))
            if len(pt_members)!=len(fit):
                raise ValueError("F20 individual complex-fit archive count mismatch "+str(j))
            point_by_id={}
            for member in pt_members:
                point=json.loads(tarbytes(t,member))
                pid=point["candidate_id"]
                if pid in point_by_id or point.get("F20_all_model_allowed") is not None:
                    raise ValueError("F20 duplicate or falsely allowed individual point "+pid)
                point_by_id[pid]=point
            if set(point_by_id)!={r["candidate_id"] for r in fit}:
                raise ValueError("F20 ranked shortlist does not match individual complex solutions")
            vacuum_members=sorted(m.name for m in t.getmembers()
                if m.isfile() and m.name.startswith(folder+"vacuum_")
                and m.name.endswith("_NOT_GLOBAL.json"))
            if len(vacuum_members)!=summary["vacuum_multistart_evaluated"]:
                raise ValueError("F20 vacuum JSON population mismatch "+str(j))
            vacuum_by_id={}
            for member in vacuum_members:
                v=json.loads(tarbytes(t,member))
                vid=v["candidate_id"]
                if vid in vacuum_by_id or v.get("full_model_allowed") is not None:
                    raise ValueError("F20 repeated vacuum case or false model acceptance "+vid)
                vacuum_by_id[vid]=v
            for row in fit:
                p=point_by_id[row["candidate_id"]]
                f=p.get("fixed_NO_complex_neutrino_and_partial_LFV",{})
                best=f.get("best")
                if best is None:
                    if row.get("LFV_partial_score_NOT_EXCLUSION") not in ("",None):
                        raise ValueError("F20 fitted CSV reports missing completed f/Y "+row["candidate_id"])
                    row.update({
                        "cascade_generalZee_lepton_included_LO_proxy_NOT_MadWidth":"",
                        "BR_H2_H1Z_generalZee_included_only":"",
                        "BR_H1_tb_generalZee_included_only":"",
                        "generalZee_included_proxy_over_nonleptonic_upper":"",
                        "verified_F19b_coherent_W_gamma_LFV_ratio_NOT_CL":"",
                        "vacuum_deeper_tree_witness":""})
                    continue
                two=float(best["BR_H2_H1Z_included_channels_ONLY"])
                one=float(best["BR_H1_tb_included_channels_ONLY"])
                corrected=float(best["charged_included_LO_cascade_proxy_NOT_pb"])
                original=float(row["cascade_included_LO_proxy_NOT_MadWidth"])
                gamma=float(p["scalar"]["gamma"])
                if (not all(math.isfinite(z) for z in (two,one,corrected,original,gamma))
                    or not 0<=two<=1 or not 0<=one<=1
                    or original<=0 or not 0<=corrected<=original+1e-8
                    or not math.isclose(corrected,math.sin(gamma)**2*two*one,
                        rel_tol=2e-9,abs_tol=1e-12)):
                    raise ValueError("F20 source B3 cascade f/Y physics identity mismatch "+row["candidate_id"])
                w=p.get("coherent_F19b_W_fermion_BZ_one_loop_partial_LFV")
                if not isinstance(w,dict):
                    raise ValueError("F20 extended coherent partial LFV missing "+row["candidate_id"])
                wscore=float(w["max_extended_partial_ratio_to_reference_NOT_EXCLUSION"])
                oldscore=float(row["LFV_partial_plus_Wgamma_score_NOT_EXCLUSION"])
                if (not math.isfinite(wscore) or wscore<0 or not math.isclose(
                    wscore,oldscore,rel_tol=2e-9,abs_tol=1e-14)):
                    raise ValueError("F20 partial LFV CSV/amplitude archive mismatch "+row["candidate_id"])
                v=vacuum_by_id.get(row["candidate_id"])
                if v is not None:
                    if ("error" in v or
                       v.get("C5_tree_vacuum_witness") not in (
                        "NO_DEEPER_WITNESS_FOUND_NOT_GLOBAL_CERTIFICATE",
                        "EXPLICIT_DEEPER_TREE_POTENTIAL_WITNESS")):
                        raise ValueError("F20 incomplete archived six-field vacuum search "+row["candidate_id"])
                    no_witness=v["C5_tree_vacuum_witness"]==(
                       "NO_DEEPER_WITNESS_FOUND_NOT_GLOBAL_CERTIFICATE")
                    if row["vacuum_no_deeper_witness_found_NOT_PROOF"]!=str(no_witness):
                        raise ValueError("F20 merged vacuum status mismatch "+row["candidate_id"])
                row.update({
                    "cascade_generalZee_lepton_included_LO_proxy_NOT_MadWidth":corrected,
                    "BR_H2_H1Z_generalZee_included_only":two,
                    "BR_H1_tb_generalZee_included_only":one,
                    "generalZee_included_proxy_over_nonleptonic_upper":corrected/original,
                    "verified_F19b_coherent_W_gamma_LFV_ratio_NOT_CL":wscore,
                    "vacuum_deeper_tree_witness":str(
                        v.get("deeper_witness_found")) if v is not None else ""})
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
       not r.get("cascade_generalZee_lepton_included_LO_proxy_NOT_MadWidth"),
       -float(r["cascade_generalZee_lepton_included_LO_proxy_NOT_MadWidth"] or 0)))
    # A scientific triage *among the 120 actually fitted f/Y cases*.
    # This is still no full-model acceptance: every row has missing
    # LO-QCD, complete LFV, flavor and HiggsTools constraints.
    candidate_triage=[r for r in allfits
        if (r["vacuum_no_deeper_witness_found_NOT_PROOF"]=="True"
            and r["vacuum_deeper_tree_witness"]=="False"
            and r.get("cascade_generalZee_lepton_included_LO_proxy_NOT_MadWidth")
            and float(r["verified_F19b_coherent_W_gamma_LFV_ratio_NOT_CL"])<1)]
    by_leptonic=sorted(candidate_triage,key=lambda r:
        -float(r["cascade_generalZee_lepton_included_LO_proxy_NOT_MadWidth"]))
    by_analytic_flavor=sorted(candidate_triage,key=lambda r:(
        float(r["LO_flavor_BR_x1e4_NOT_CL"]),
        -float(r["cascade_generalZee_lepton_included_LO_proxy_NOT_MadWidth"])))
    out.mkdir(parents=True,exist_ok=False)
    save_csv(out/"F20_ALL_shards_scalar_LO_flavor_NOT_EXCLUSION.csv",allscalar)
    save_csv(out/"F20_ALL_shards_cascade_flavor_Pareto_NOT_CL.csv",front)
    save_csv(out/"F20_ALL_shards_fixed_NO_partial_LFV_shortlist_NOT_ALLOWED.csv",allfits)
    # This is the correct f/Y-dependent B3 included-channel ranking,
    # NOT an actual MadWidth total or physical production rate in pb.
    if by_leptonic:
        save_csv(out/"F20_LFV_and_tree_vacuum_triage_ranked_by_leptonic_cascade_NOT_ALLOWED.csv",by_leptonic)
        save_csv(out/"F20_LFV_and_tree_vacuum_triage_ranked_by_LO_flavor_NOT_ALLOWED.csv",by_analytic_flavor)
    report={
      "status":"F20_FOUR_SHARDS_MERGED_EXPLORATORY_SCAN_NOT_FULL_ZEE_ALLOWED",
      "four_complete_shards":True,
      "original_exact_three_F18_F19_F19b_F19c_F19d_SHA256":source,
      "HTCondor_output_tar_SHA256":hashes,
      "total_independently_seeded_proposals":sum(q["steps"] for q in stats),
      "screened_scalar_parameter_records_not_unique_allowed_volume":count,
      "frontier_points_not_a_confidence_contour":len(front),
      "extended_120_solution_B3_lepton_width_source_recovered":True,
      "fitted_no_deeper_witness_and_partial_LFV_lt_reference_NOT_ALLOWED":len(by_leptonic),
      "fitted_best_leptonic_cascade_source_NOT_MadWidth":(
          by_leptonic[0]["campaign_unique_key"] if by_leptonic else None),
      "fitted_best_analytic_LO_flavor_source_NOT_95CL":(
          by_analytic_flavor[0]["campaign_unique_key"] if by_analytic_flavor else None),
      "ranked_leptonic_cascade_still_included_channel_proxy_NOT_QCD_or_pb":True,
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
        ax.set_xlabel(r"Linearized LO $10^4\,\mathrm{BR}(B\to X_s\gamma)$ (not CL)")
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
        ax.set_xlabel(r"$m_{H_1^\pm}$ [GeV]")
        ax.set_ylabel(r"$m_{H_2^\pm}$ [GeV]")
        ax.set_title("Exploratory scalar/EWPO subset, not an allowed region")
        fig.tight_layout()
        fig.savefig(out/"F20_mass_plane_proxy_exploratory.png",dpi=180)
        plt.close(fig)
    except ImportError:
        print("F20_PLOTS_SKIPPED_NO_MATPLOTLIB",flush=True)
    print("F20_ACTUAL_B3_LEPTON_WIDTH_ADJUSTED_TRIAGE",len(by_leptonic),
          "PAIRED_LOWEST_LO_FLAVOR",len(by_analytic_flavor),
          "FULLY_ALLOWED",None,flush=True)
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
