#!/usr/bin/env python3
"""F22: freeze ALL actual F21c source-matched Zee shortlist f/Y solutions.

No new scan, no Bsmixing flavor exclusion, no claimed physics completion.
Joins 157 actual *numerically screened only* F21c shortlist rows with
their immutable original per-shard CERN archives containing optimized
complex f and Y, coherent partial LFV, scalar potential and C5 vacuum
witness. Exact sha256 provenance and values cross-checked.
Outputs one compact gzipped 157-record real-model intake plus a
mass-stratified ten-case full benchmark dossier (two per H2 mass shell).
"""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math,tarfile
from collections import defaultdict
from pathlib import Path

STATUS="F22_F21C_FULL_COMPLEX_YUKAWA_157_BENCHMARK_FREEZE_NOT_ALLOWED"
SHARDS=24
EDGES=(450.,700.,1000.,1400.,1900.,2500.001)

def hash_file(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as stream:
        for chunk in iter(lambda:stream.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()

def exact_json(tf,name):
    info=tf.getmember(name)
    if not info.isfile() or not 2<=info.size<=20_000_000:
        raise ValueError("F22 unexpected science archive member "+name)
    h=tf.extractfile(info)
    if h is None:raise ValueError("F22 missing stream "+name)
    return json.load(h)

def close(actual,expected,label):
    if not(math.isfinite(actual) and math.isfinite(expected)
           and math.isclose(actual,expected,rel_tol=1e-8,abs_tol=1e-12)):
        raise ValueError("F22 same physical point mismatch "+label+
                         " "+str(actual)+" vs "+str(expected))

def execute(a):
    output=Path(a.output).expanduser().resolve()
    if output.exists():raise FileExistsError("Do not overwrite frozen science dossier")
    home=Path(a.merged).expanduser().resolve()
    source=Path(a.eos).expanduser().resolve()
    report_path=home/"F21_WIDE_PRODUCTION_summary_NOT_ALLOWED.json"
    summary=json.loads(report_path.read_text())
    if (summary.get("status")!="F21C_24_SHARDS_SAVED_SCALAR_RESCUE_COMPLETED_NOT_FULL_ALLOWED"
       or summary.get("shards_complete")!=SHARDS
       or summary.get("all_original_mass_stratified_scalar_screens_rescued") is not True
       or summary.get("complete_modern_bsgamma_LFV_HiggsTools_real_LHC_prediction") is not False
       or summary.get("paper_fully_allowed_or_excluded_points") is not None):
        raise ValueError("F22 original merged F21c scientific status invalid")
    field="F21_WIDE_vacuum_LFV_triaged_cascade_NOT_FULL_ALLOWED.csv"
    with (home/field).open(newline="") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=summary["vacuum_no_deeper_witness_AND_LFV_partial_score_lt1_subset_NOT_ALLOWED"]:
        raise ValueError("F22 original F21c physics shortlist population/count mismatched")
    if not rows:raise ValueError("F22 empty original shortlist")
    if hash_file(home/field)!=summary.get("CSV_SHA256",{}).get(field):
        raise ValueError("F22 original source F21c shortlisted CSV SHA mismatch")
    targets=defaultdict(set)
    rowdict={}
    for row in rows:
        key=row["campaign_key"]
        shard,sep,name=key.partition("/")
        if not sep or not shard.isdigit() or int(shard) not in range(SHARDS):
            raise ValueError("F22 invalid original shard/candidate ID "+key)
        if key in rowdict:raise ValueError("F22 duplicate physics solution "+key)
        if not name.startswith("F21_s"+shard+"_"):
            raise ValueError("F22 wrong original candidate ID "+name)
        if row["fully_allowed_or_excluded"]!="UNKNOWN_NOT_EVALUATED":
            raise ValueError("F22 model wrongly marked accepted")
        if row["numerical_no_deeper_tree_witness_NOT_CERTIFICATE"]!="True":
            raise ValueError("F22 only archived C5 numerical no-deeper-witness subset")
        l=float(row["partial_LFV_Wgamma_max_ratio_NOT_CL"])
        if not(math.isfinite(l) and 0<=l<1):
            raise ValueError("F22 partial LFV score invalid")
        targetkey=(int(shard),name)
        targets[int(shard)].add(name);rowdict[targetkey]=row
    bundles={}
    stored_hashes={}
    for n in range(SHARDS):
        if n not in targets:continue
        arch=source/f"F21c_resumed_shard_{n}.tar.gz"
        if not arch.is_file():raise FileNotFoundError(arch)
        expectedsha=summary["CERN_24_result_tar_SHA256"].get(str(n))
        foundsha=hash_file(arch)
        if foundsha!=expectedsha:raise ValueError("F22 tampered original EOS source "+str(n))
        stored_hashes[str(n)]=foundsha
        with tarfile.open(arch,"r:gz") as tf:
            prefix=f"results/F21_shard_{n}/"
            status=tf.extractfile(tf.getmember(f"F21c_shard_{n}.exit"))
            if status is None or status.read().decode().strip()!=f"F21C_SHARD_{n}_EXIT_CODE=0":
                raise ValueError("F22 original HTCondor physics exit code invalid")
            fits={};vac={}
            for info in tf:
                p=info.name
                if not info.isfile() or not p.startswith(prefix):continue
                if (p.startswith(prefix+"F21_fit_")
                     and p.endswith("_NOT_ALLOWED.json")):
                    point=exact_json(tf,p)
                    name=point.get("candidate_id")
                    if name in targets[n]:
                        if name in fits:raise ValueError("F22 duplicate true f/Y JSON "+name)
                        fits[name]=point
                if (p.startswith(prefix+"F21_vacuum_")
                     and p.endswith("_NOT_GLOBAL.json")):
                    point=exact_json(tf,p)
                    name=point.get("candidate_id")
                    if name in targets[n]:
                        if name in vac:raise ValueError("F22 duplicate true vacuum JSON "+name)
                        vac[name]=point
            if set(fits)!=targets[n] or set(vac)!=targets[n]:
                raise ValueError("F22 original f/Y or C5 vacuum archive missing some selected points for shard "+str(n))
            for name in targets[n]:
                key=(n,name)
                fit=fits[name];v=vac[name];row=rowdict[key]
                sol=fit.get("fixed_NO_neutrino_and_LFV_subset",{})
                best=sol.get("best")
                if not isinstance(best,dict) or "optimized_f" not in best or "optimized_Y" not in best:
                    raise ValueError("F22 complex general Zee f/Y optimization missing "+name)
                if fit.get("full_Zee_model_allowed") is not None or v.get("model_allowed") is not None:
                    raise ValueError("F22 original numerical stage falsely reports allowed point")
                if (v.get("deeper_tree_witness") is not False or
                    v.get("vacuum_no_global_proof",{}).get("status")
                      !="NO_DEEPER_WITNESS_FOUND_NOT_GLOBAL_CERTIFICATE"):
                    raise ValueError("F22 original numerical C5 tree-vacuum screen mismatch "+name)
                exact=fit.get("coherent_partial_LFV_with_W_gamma")
                if not isinstance(exact,dict):
                    raise ValueError("F22 original computed LFV Wgamma term missing "+name)
                close(float(exact["max_extended_partial_ratio_to_reference_NOT_EXCLUSION"]),
                    float(row["partial_LFV_Wgamma_max_ratio_NOT_CL"]),
                    name+":coherent_partial_LFV")
                for inp,csvcol in (("mH1","mH1_GeV"),("mH2","mH2_GeV"),
                         ("gamma","gamma_rad")):
                    close(float(fit["scalar"][inp]),float(row[csvcol]),name+":"+inp)
                close(float(best["charged_included_LO_cascade_proxy_NOT_pb"]),
                    float(row["complex_Yukawa_included_cascade_proxy_NOT_MadWidth"]),
                    name+":GeneralZee_B3_proxy")
                bundles[key]={
                    "campaign_key":row["campaign_key"],
                    "F21c_ranked_source_csv":row,
                    "exact_scalar_and_complex_fY_partial_LFV":fit,
                    "C5_six_field_tree_vacuum_non_global_witness":v,
                    "source_F21c_24job_EOS_SHA256":foundsha,
                    "fully_Zee_allowed_or_excluded":None,
                    "quark_flavor_only_analytic_LO":True,
                    "full_MadWidth_new_spectrum":False,
                    "full_HiggsTools_applied":False,
                    "physical_LHC_cross_section_pb_evaluated":False,
                }
    if set(bundles)!=set(rowdict):
        raise ValueError("F22 full cohort source join mismatch")
    # Select two independent scientific motivations per heavy-mass class:
    # highest Yukawa-adjusted cascade and lowest linearized LO Bsgamma.
    # Duplicates count once; all other candidates kept in the FULL archive.
    chosen=[];slices={}
    for i,(lo,hi) in enumerate(zip(EDGES[:-1],EDGES[1:])):
        sample=[k for k,b in bundles.items()
                if lo<=float(b["F21c_ranked_source_csv"]["mH2_GeV"])<hi]
        if not sample:
            slices[str(i)]={"n_triaged":0,"priority":[]}
            continue
        c=max(sample,key=lambda k:float(
            bundles[k]["F21c_ranked_source_csv"]["complex_Yukawa_included_cascade_proxy_NOT_MadWidth"]))
        f=min(sample,key=lambda k:float(
            bundles[k]["F21c_ranked_source_csv"]["analytic_LO_Bsgamma_BR_x1e4_NOT_CL"]))
        for k in (c,f):
            if k not in chosen:chosen.append(k)
        slices[str(i)]={"n_triaged":len(sample),
                        "priority":[bundles[k]["campaign_key"] for k in dict.fromkeys((c,f))]}
    output.mkdir(parents=True,exist_ok=False)
    full=output/"F22_ALL_157_original_complex_fY_sources_NOT_FULL_ALLOWED.jsonl.gz"
    with gzip.open(full,"wt",encoding="utf-8") as dest:
        for key in sorted(bundles):
            dest.write(json.dumps(bundles[key],sort_keys=True,allow_nan=False)+"\n")
    priority=output/"F22_mass_stratified_priority_complex_fY_dossier_NOT_ALLOWED.json"
    priority.write_text(json.dumps({
       "status":STATUS,
       "source_merged_F21c_summary_SHA256":hash_file(report_path),
       "total_actual_triaged_solutions":len(bundles),
       "selection_policy":"highest corrected cascade and lowest analytic LO flavor in each heavy-mass shell",
       "source_mass_shells":slices,
       "FULL_ALLOWED":None,
       "entries":[bundles[k] for k in chosen]},indent=2,sort_keys=True,allow_nan=False)+"\n")
    manifest={
        "status":STATUS,"model_fully_allowed_or_excluded":None,
        "source_F21c_merge_summary_SHA256":hash_file(report_path),
        "source_F21c_shortlist_CSV_SHA256":hash_file(home/field),
        "source_real_24_CERN_job_archives_SHA256":stored_hashes,
        "mass_stratified_source_slices":slices,
        "preserved_real_complex_neutrino_and_partial_LFV_cases":len(bundles),
        "priority_benchmarks":len(chosen),
        "source_original_wide_proposals_not_rerun":240000,
        "complete_2026_Bsgamma_or_complete_general_Zee_LFV":False,
        "physical_production_normalized_collider_rates_evaluated":False,
        "output_SHA256":{p.name:hash_file(p) for p in (full,priority)},
    }
    (output/"F22_freeze_SHA256_manifest.json").write_text(json.dumps(
        manifest,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F22_REAL_FULL_FY_FREEZE","SAVED",len(bundles),"PRIORITY",len(chosen),
          "MASS_BINS",json.dumps({k:v["n_triaged"] for k,v in slices.items()}),
          "FULL_ALLOWED",None,flush=True)
    print("F22_GZIPPED_FULL",full,flush=True)
    print("F22_FROZEN_PRIORITY",priority,flush=True)
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--merged",type=Path,required=True)
    ap.add_argument("--eos",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    execute(ap.parse_args())
if __name__=="__main__":main()
