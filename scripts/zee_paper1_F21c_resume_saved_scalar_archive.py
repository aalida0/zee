#!/usr/bin/env python3
"""F21c production RESUME: reuse actual 24 successful scalar-screen CSVs.

F21b's 24 physics jobs calculated and saved the scalar/EWPO point table,
then all failed because shortlist ranking referenced a nonexistent
B4 field. DO NOT rerun 240,000 initial proposals. Strictly verify
original 24 EOS tarball scalar files against SHA-locked F18-F20 anchors,
then continue from complex f/Y neutrino/LFV and C5 vacuum calculations.

This driver reuses the original F21 physics-stage code (no new formulas).
The 10k original proposals/shard are counted as source-attributed work.
Attempt-by-bin/raw pass totals were not serialized at F21b failure;
do NOT fabricate them in this recovery report.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,tarfile
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
from zee_paper1_F21_stratified_wide_mass_mix_scan import (
    verify,f20_source,sha,REQUIRED_FIELDS,region,index,
    M2_EDGES,T_EDGES,G_EDGES,STATUS,select_stratified,dump,save_csv,
    scalar_screen,ewpo_screen,scalar_row,optimize_point,
    target_neutrino_matrix,optimize_kernels_cache,complex_matrix,
    evaluate_partial_lfv,scalar_lagrangian,candidate_starts,evaluate_multistart)

CANONICAL_CSV="F21_WIDE_all_scalar_LO_screen_NOT_ALLOWED.csv"
REQUIRED_NUMERIC=REQUIRED_FIELDS+(
    "tanbeta","max_unitarity","chi2_Gfitter","chi2_PDG",
    "production_weighted_nonleptonic_cascade_upper_proxy",
    "LO_flavor_shift_x1e4_NOT_CL","LO_flavor_BR_x1e4_NOT_CL",
    "LO_flavor_C7_NOT_CL","LO_flavor_C8_NOT_CL")

def original_scalar_archive(a,check_actual=True):
    tar=Path(a.original_scalar_archive).resolve()
    with tarfile.open(tar,"r:gz") as tf:
        stem=f"results/F21_shard_{a.shard}/"
        def get(name):
            member=tf.getmember(stem+name)
            if not member.isfile() or member.size<4 or member.size>200000000:
                raise ValueError("F21c corrupt or too large original archive entry "+name)
            h=tf.extractfile(member)
            if h is None:raise ValueError("F21c original archive stream missing "+name)
            return h.read()
        manifest=json.loads(get("F21_manifest_start.json"))
        csvbytes=get(CANONICAL_CSV)
        # The F21b error was in selector *after this CSV was flushed*.
        # Do not silently accept data from an unverified other shard.
        if (manifest.get("status")!="F21_RUNNING_NOT_ALLOWED"
            or manifest.get("shard")!=a.shard
            or manifest.get("requested_independent_stratified_draws")!=a.global_draws
            or manifest.get("requested_local_custodial_draws")!=a.local_draws):
            raise ValueError("F21c archived original scalar/shard identity mismatch")
        # The genuine F21b start manifest uses F18/F19/F19b/F19c/F19d
        # as dictionary keys (although argparse Namespace uses lowercase).
        expected={
            k[0].upper()+k[1:]:sha(getattr(a,k))
            for k in ("f18","f19","f19b","f19c","f19d")}
        if manifest.get("original_F18_through_F19d_sha256")!=expected:
            raise ValueError("F21c original physical F18-F19d input SHA mismatch")
        if (manifest.get("F20_merged_csv_SHA256")!=sha(a.f20_csv)
            or manifest.get("F20_merged_summary_SHA256")!=sha(a.f20_summary)
            or manifest.get("full_model_allowed") is not None):
            raise ValueError("F21c archived F20 provenance or allowance corrupted")
        data=list(csv.DictReader(io.StringIO(csvbytes.decode("utf-8"))))
        if not data:raise ValueError("F21c archive has no scalar-screened records")
        ids=set()
        for entry in data:
            pid=entry.get("id")
            if not pid or pid in ids or not pid.startswith("F21_s"+str(a.shard)+"_"):
                raise ValueError("F21c duplicate/wrong-shard scalar result ID")
            ids.add(pid)
            if (entry.get("candidate_status")!="SCALAR_EWPO_SCREEN_ONLY_NOT_ALLOWED"
                or entry.get("flavor_and_HiggsTools_applied") not in ("False","false","0")
                or entry.get("full_Zee_allowed_or_excluded") not in ("","None",None)):
                raise ValueError("F21c a source scalar row spuriously claims full physics")
            for field in REQUIRED_NUMERIC:
                try:
                    value=float(entry[field])
                except (ValueError,TypeError,KeyError) as exc:
                    raise ValueError("F21c incomplete numeric scalar source "+field) from exc
                if not math.isfinite(value):
                    raise ValueError("F21c nonfinite scalar source "+field)
                entry[field]=value
            if not (200<=entry["mH1"]<=1200
                and 450<=entry["mH2"]<=2500
                and entry["mH2"]>entry["mH1"]+91.1876
                and .7<=entry["tanbeta"]<=35.001
                and .08<=entry["gamma"]<=1.49
                and 0<=entry["production_weighted_nonleptonic_cascade_upper_proxy"]<=1
                and entry["max_unitarity"]<8*math.pi+1e-8):
                raise ValueError("F21c impossible source scalar bounds or partial cascade")
        if check_actual:
            # Independent physics reconstruction on first/middle/last
            # SAVED accepted spectra; no 240k-proposal rerun.
            samples=[data[0],data[len(data)//2],data[-1]]
            for row in samples:
                p={key:row[key] for key in REQUIRED_FIELDS}
                if scalar_screen(p) is None or ewpo_screen(p,a.quad) is None:
                    raise ValueError("F21c original archived scalar/EWPO screen no longer reproducible")
        return data,manifest,csvbytes,sha(tar)

def execute(a):
    if not(0<=a.shard<24 and a.global_draws==6000 and
        a.local_draws==4000 and 40<=a.quad<=240 and
        1<=a.fits<=200 and 0<=a.vacuum<=a.fits and
        64<=a.vacuum_starts<=512):
        raise ValueError("F21c original production physics configuration mismatch")
    _,_,_ = verify(a.f18,a.f19,a.f19b,a.f19c,a.f19d)
    f20pool,_=f20_source(a.f20_csv,a.f20_summary)
    records,original_manifest,rawscalar,archive_hash=original_scalar_archive(a)
    print("F21C_SCALAR_ARCHIVE_SOURCE_PASS",a.shard,"ROWS",len(records),
          "ORIGINAL_CERN_TARBALL_SHA256",archive_hash,flush=True)
    if a.verify_only:return {
        "shard":a.shard,"scalar_screened_source_rows":len(records),
        "original_archive_sha256":archive_hash}
    out=Path(a.output).expanduser().resolve()
    if out.exists():raise FileExistsError("F21c cannot overwrite recovery output")
    out.mkdir(parents=True,exist_ok=False)
    (out/CANONICAL_CSV).write_bytes(rawscalar)
    original={"status":"F21C_SOURCE_ARCHIVE_RECOVERY_FIXED_SCALAR_STAGE",
              "shard":a.shard,
              "original_scalar_csv_SHA256":hashlib.sha256(rawscalar).hexdigest(),
              "original_failed_EOS_archive_SHA256":archive_hash,
              "original_manifest":original_manifest,
              "reconstructed_screened_points_are_original":True,
              "original_240k_initial_proposals_are_NOT_recomputed":True,
              "full_model_allowed":None}
    dump(out/"F21c_original_saved_scalar_source_provenance.json",original)
    seed=a.seed+100003*a.shard
    rng=np.random.default_rng(seed)
    # IMPORTANT the RNG starts from the published fixed shard seed but
    # cannot reconstruct its advanced state after 10k proposals. This
    # yields NEW reproducible complex f/Y seeds, not the originally
    # intended downstream RNG state. Do not claim exact resumed random
    # stream; scalar inputs and scalar result bytes remain untouched.
    selected=select_stratified(records,a.fits)
    if not selected:raise ValueError("F21c original scalar archive produced no fit shortlist")
    coverage_m2=Counter(region(r)[0] for r in records)
    coverage_tb=Counter(region(r)[1] for r in records)
    coverage_g=Counter(region(r)[2] for r in records)
    summary={
       "status":"F21C_ORIGINAL_SCALAR_CSV_RECOVERED_NOT_ALLOWED",
       "shard":a.shard,
       "strata_mH2_edges_GeV":M2_EDGES,
       "strata_tanbeta_edges":T_EDGES,
       "strata_gamma_edges_radians":G_EDGES,
       "attempts":a.global_draws+a.local_draws,
       "original_scalar_proposals_were_calculated_in_failed_F21b_job":True,
       "original_raw_scalar_EWPO_pass_count_unavailable":True,
       "raw_scalar_EWPO_passes":None,
       "distinct_scalar_EWPO_screened":len(records),
       "rejections":{},
       "per_origin_mH2_bin":{},
       "survivors_by_mH2_bin":dict(coverage_m2),
       "survivors_by_tanbeta_bin":dict(coverage_tb),
       "survivors_by_gamma_bin":dict(coverage_g),
       "original_scalar_csv_SHA256":hashlib.sha256(rawscalar).hexdigest(),
       "original_failed_scalar_archive_SHA256":archive_hash,
       "fully_allowed":None}
    dump(out/"F21_WIDE_stratified_coverage_NOT_ALLOWED.json",summary)
    print("F21C_RESCUED_STAGE",a.shard,"SURVIVORS",len(records),
          "FITS_SELECTED",len(selected),
          "M2_BIN_SURVIVORS",dict(coverage_m2),flush=True)
    target,_=target_neutrino_matrix()
    optimize_kernels_cache()
    physics=[];failures=Counter()
    for j,record in enumerate(selected,1):
        p=scalar_row(record)
        try:
            sol=optimize_point(p,target,rng,trials=a.trials,
                local_seeds=a.optimize_seeds,max_evals=a.opt_evals)
            if sol["status"]!="NEUTRINO_EXACT_WITH_PARTIAL_LFV_AND_INCLUDED_CASCADE_ONLY":
                failures["no_complex_solution"]+=1
            extension=None
            if sol.get("best"):
                f=complex_matrix(sol["best"]["optimized_f"],"f")
                Y=complex_matrix(sol["best"]["optimized_Y"],"Y")
                extension=evaluate_partial_lfv(p,f,Y)
            item={"candidate_id":record["id"],"shard":a.shard,
                  "scalar":p,"scalar_screen":record,
                  "fixed_NO_neutrino_and_LFV_subset":sol,
                  "coherent_partial_LFV_with_W_gamma":extension,
                  "full_Zee_model_allowed":None}
        except (ValueError,OverflowError,FloatingPointError,ArithmeticError,
                np.linalg.LinAlgError) as exc:
            failures["failed_"+type(exc).__name__]+=1
            item={"candidate_id":record["id"],"shard":a.shard,
                  "error":repr(exc),"full_Zee_model_allowed":None}
        physics.append(item)
        dump(out/("F21_fit_"+str(j).zfill(3)+"_NOT_ALLOWED.json"),item)
        if j%8==0:print("F21_FITS",a.shard,j,"/",len(selected),flush=True)
    valid=[i for i in physics if i.get("coherent_partial_LFV_with_W_gamma")]
    # Explicitly use *corrected* General Zee lepton-width charged BR proxy
    # from the optimized exact complex f/Y, not scalar-only upper proxy.
    valid.sort(key=lambda i:-i["fixed_NO_neutrino_and_LFV_subset"]["best"][
         "charged_included_LO_cascade_proxy_NOT_pb"])
    vacuums=[];vacfail=Counter()
    # Span mass shells, not only proxy leaders near 800 GeV.
    vac_selection=select_stratified([
        {**i["scalar"],"id":i["candidate_id"],
         "production_weighted_nonleptonic_cascade_upper_proxy":
          i["fixed_NO_neutrino_and_LFV_subset"]["best"][
            "charged_included_LO_cascade_proxy_NOT_pb"],
         "LO_flavor_shift_x1e4_NOT_CL":
          i["scalar_screen"]["LO_flavor_shift_x1e4_NOT_CL"]}
        for i in valid],a.vacuum)
    byid={i["candidate_id"]:i for i in valid}
    for k,r in enumerate(vac_selection,1):
        i=byid[r["id"]]
        p=i["scalar"]
        try:
            state,_=scalar_lagrangian(p)
            ss=seed+int.from_bytes(hashlib.sha256(
               i["candidate_id"].encode()).digest()[:4],"big")
            starters=candidate_starts(a.vacuum_starts,ss%(2**32))
            result=evaluate_multistart(p,state,starters,maxiter=a.vacuum_iters)
            if result["search_is_not_a_global_minimization_certificate"] is not True:
                raise ValueError("C5 no-global-proof convention changed")
            item={"candidate_id":i["candidate_id"],
                  "vacuum_no_global_proof":result,
                  "deeper_tree_witness":result["most_negative_witness"] is not None,
                  "model_allowed":None}
        except (ValueError,ArithmeticError,FloatingPointError,
                OverflowError,np.linalg.LinAlgError) as exc:
            vacfail[type(exc).__name__]+=1
            item={"candidate_id":i["candidate_id"],"error":repr(exc),
                  "model_allowed":None}
        vacuums.append(item)
        dump(out/("F21_vacuum_"+str(k).zfill(3)+"_NOT_GLOBAL.json"),item)
    bv={x["candidate_id"]:x for x in vacuums}
    shortlist=[]
    for item in physics:
        name=item["candidate_id"]
        s=item.get("scalar_screen",{})
        sol=item.get("fixed_NO_neutrino_and_LFV_subset",{})
        best=sol.get("best",{})
        w=item.get("coherent_partial_LFV_with_W_gamma") or {}
        vac=bv.get(name,{})
        widths=best.get("charged_included_channel_widths_GeV",{})
        # Gamma/m narrow-width warning is a LOWER-bound estimate here:
        # these are only the model's included tree channels. For very
        # heavy H2 a broad charged resonance may invalidate NWA rates.
        gamma1=sum(float(x) for x in widths.get("H1",{}).values()) if widths else None
        gamma2=sum(float(x) for x in widths.get("H2",{}).values()) if widths else None
        shortlist.append({
           "candidate_id":name,"shard":a.shard,
           "Gamma_H1_included_over_mass_NOT_full_width":(
              gamma1/float(s["mH1"]) if gamma1 is not None else None),
           "Gamma_H2_included_over_mass_NOT_full_width":(
              gamma2/float(s["mH2"]) if gamma2 is not None else None),
           "H2_included_width_warn_NWA_if_over_10pct":(
              gamma2/float(s["mH2"])>=.10 if gamma2 is not None else None),
           "mH1_GeV":s.get("mH1"),"mH2_GeV":s.get("mH2"),
           "tanbeta":s.get("tanbeta"),"gamma_rad":s.get("gamma"),
           "neutral_H_GeV":s.get("mh2"),"neutral_A_GeV":s.get("ma"),
           "scalar_nonleptonic_cascade_proxy_NOT_MadWidth":s.get(
             "production_weighted_nonleptonic_cascade_upper_proxy"),
           "complex_Yukawa_included_cascade_proxy_NOT_MadWidth":best.get(
             "charged_included_LO_cascade_proxy_NOT_pb"),
           "BR_H2_H1Z_included":best.get("BR_H2_H1Z_included_channels_ONLY"),
           "BR_H1_tb_included":best.get("BR_H1_tb_included_channels_ONLY"),
           "analytic_LO_Bsgamma_BR_x1e4_NOT_CL":s.get("LO_flavor_BR_x1e4_NOT_CL"),
           "fixed_NO_neutrino_closure_eV":best.get("neutrino_matrix_closure_eV"),
           "partial_LFV_Wgamma_max_ratio_NOT_CL":w.get(
              "max_extended_partial_ratio_to_reference_NOT_EXCLUSION"),
           "numerical_no_deeper_tree_witness_NOT_CERTIFICATE":
             vac.get("vacuum_no_global_proof",{}).get("status")==
               "NO_DEEPER_WITNESS_FOUND_NOT_GLOBAL_CERTIFICATE"
               if vac and "vacuum_no_global_proof" in vac else None,
           "fully_allowed_or_excluded":"UNKNOWN_NOT_EVALUATED"})
    save_csv(out/"F21_WIDE_complex_fY_LFV_vacuum_shortlist_NOT_ALLOWED.csv",
       shortlist,list(shortlist[0]))
    summary.update({
       "status":STATUS,
       "source_F20_original_SHA256":sha(a.f20_csv),
       "original_F18_F19d_sources":{
         k:sha(getattr(a,k)) for k in ("f18","f19","f19b","f19c","f19d")},
       "shard":a.shard,"complex_LFV_fits_attempted":len(physics),
       "complex_LFV_fits_completed":len(valid),
       "vacuum_witness_searches_attempted":len(vacuums),
       "LFV_errors":dict(failures),"vacuum_errors":dict(vacfail),
       "complete_two_state_Bsgamma":False,
       "full_LFV_oscillation_NO_IO":False,"full_HiggsTools_or_real_production":False,
       "model_allowed_or_excluded":None,
       "all_major_uncertainties_still_missing":True,
       "result_csv_SHA256":{x.name:sha(x) for x in out.glob("*.csv")},
    })
    dump(out/"F21_SHARD_COMPLETED_summary.json",summary)
    print("F21_SHARD_COMPLETED",a.shard,"SCALAR",len(records),
          "FITTED",len(valid),"VACUUM",len(vacuums),
          "FULL_MODEL_ALLOWED",None,flush=True)
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("f18","f19","f19b","f19c","f19d","f20-csv",
                 "f20-summary","original-scalar-archive","output"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--shard",type=int,required=True)
    p.add_argument("--seed",type=int,default=20261025)
    p.add_argument("--global-draws",type=int,default=6000)
    p.add_argument("--local-draws",type=int,default=4000)
    p.add_argument("--quad",type=int,default=64)
    p.add_argument("--fits",type=int,default=40)
    p.add_argument("--trials",type=int,default=90)
    p.add_argument("--optimize-seeds",type=int,default=2)
    p.add_argument("--opt-evals",type=int,default=180)
    p.add_argument("--vacuum",type=int,default=12)
    p.add_argument("--vacuum-starts",type=int,default=64)
    p.add_argument("--vacuum-iters",type=int,default=350)
    p.add_argument("--verify-only",action="store_true")
    a=p.parse_args()
    execute(a)

if __name__=="__main__":main()
