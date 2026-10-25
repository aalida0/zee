#!/usr/bin/env python3
"""F21 WIDE Zee scan: AF-independent 6-shard stratified physics campaign.

Unlike F20's 6-GeV-step local walk around mH2 ~880 GeV, independently
covers charged masses to 2500 GeV, tanbeta 0.7-35, gamma 0.08-1.49,
neutral masses, dimensionful soft term and singlet quartics. A correlated
custodial/decoupling scaffold samples potentially consistent quartics,
rather than rejecting 100% of arbitrary 11D coordinates. Every ACCEPTED
point still passes the existing actual Gate6 scalar and correlated STU
screens. Explore boundaries; do NOT infer allowed volume/prior/posterior.

Uses physically source-verified F18-F19d anchors and the original F20
5075-screened scalar pool + source-verified corrected summary.
Selects Yukawa fit points across independent mH2/tanbeta/gamma
strata, not only maximum unvalidated cascade upper proxies. Evaluates
fixed-NO neutrino, complex f/Y and selected coherent LFV, Yukawa-dependent
charged-lepton widths, and 6D tree-vacuum witnesses for final subset.
NO full-Zee allowed labels, no modern two-Higgs precision Bsgamma,
no full-HiggsTools, no detector/collider cross sections.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from gateB4_adaptive_zee_scalar_scan import (
    scalar_screen,ewpo_screen,make_record)
from zee_paper1_F20_integrated_large_campaign import verify,dump,save_csv
from zee_paper1_F19d_AF_independent_analytic_LO_bsgamma import model,sha
from zee_paper1_florentino_feasibility_scan import (
    scalar_row,optimize_point)
from gateA1b_hierarchical_no_seed import target_neutrino_matrix
from zee_gateD2_neutrino_exact_partial_LFV_optimization import optimize_kernels_cache
from gateB3_general_zee_charged_lepton_widths import complex_matrix
from zee_paper1_F19b_exact_F17f_neutrino_partial_LFV import evaluate_partial_lfv
from zee_gateC1_joined_uv_pilot import scalar_lagrangian
from zee_gateC5_charge_breaking_vacuum_search import candidate_starts,evaluate_multistart

STATUS="F21_STRATIFIED_WIDE_ZEE_SCALAR_FIXED_NO_PARTIAL_LFV_VACUUM_NOT_ALLOWED"
M2_EDGES=(450.,700.,1000.,1400.,1900.,2500.001)
T_EDGES=(.7,1.5,3.,7.,15.,35.001)
G_EDGES=(.08,.4,.8,1.15,1.490001)
M1_EDGES=(200.,400.,650.,900.,1200.001)
REQUIRED_FIELDS=("mH1","mH2","mh2","ma","beta","alpha","gamma",
                 "m12sq","lc","k1","k2","k12")
def index(value,edges):
    for i,(lo,hi) in enumerate(zip(edges[:-1],edges[1:])):
        if lo<=value<hi:return i
    return None
def region(p):
    return (index(p["mH2"],M2_EDGES),
            index(math.tan(p["beta"]),T_EDGES),
            index(p["gamma"],G_EDGES),
            index(p["mH1"],M1_EDGES))
def classify(p):
    k=region(p)
    return ":".join(str(x) if x is not None else "OUT" for x in k)
def candidate(rng,k):
    # Stratum k makes mH2, tanbeta, gamma independently distributed over
    # all axis bins (not conditioned on 2021 P1/P2 benchmark masses).
    bi=(k//(5*4))%5;ti=(k//4)%5;gi=k%4
    m2=float(rng.uniform(M2_EDGES[bi],M2_EDGES[bi+1]))
    m1upper=min(1200.,m2-91.1876-14.)
    if m1upper<200.:return None
    # Log m1 to represent 200-1200 GeV without concentrating at >1 TeV.
    m1=float(np.exp(rng.uniform(math.log(200.),math.log(m1upper))))
    tan=float(np.exp(rng.uniform(math.log(T_EDGES[ti]),math.log(T_EDGES[ti+1]))))
    beta=math.atan(tan)
    gamma=float(rng.uniform(G_EDGES[gi],G_EDGES[gi+1]))
    # Doublet charged diagonal mass: near-degenerate neutral masses
    # and the soft term suppress otherwise huge 2HDM quartics at high m2.
    mD=math.sqrt(m1*m1*math.cos(gamma)**2+m2*m2*math.sin(gamma)**2)
    # Mix broad and narrow custodial/near-alignment proposals, allowing
    # substantial neutral splittings and both signs of lambda5.
    width=float(rng.choice([12.,40.,110.,250.],p=[.25,.40,.25,.10]))
    neutral=float(np.clip(mD+rng.normal(0,width),180.,2600.))
    pseudo=float(np.clip(mD+rng.normal(0,width),180.,2600.))
    delta=float(rng.normal(0,.027))
    delta=float(np.clip(delta,-.13,.13))
    # Soft is dimension^2: produce positive and negative offsets, but
    # fully independent of neutral data within a physically useful scale.
    softmass2=max(2.e4,mD*mD+float(rng.normal(0.,width*max(mD,125.)*.5)))
    # Probe quartic singlet range, including both positive/negative k12.
    lc=float(np.exp(rng.uniform(math.log(.15),math.log(10.))))
    k1=float(np.exp(rng.uniform(math.log(.02),math.log(5.))))
    k2=float(np.exp(rng.uniform(math.log(.02),math.log(5.))))
    k12=float(rng.uniform(-.75,.75)*min(k1,k2))
    return {"mH1":m1,"mH2":m2,"mh2":neutral,"ma":pseudo,
       "beta":beta,"alpha":beta+delta,"gamma":gamma,
       "m12sq":softmass2*math.sin(beta)*math.cos(beta),
       "lc":lc,"k1":k1,"k2":k2,"k12":k12}
def f20_source(csvfile,summaryfile):
    raw=Path(csvfile).read_bytes()
    report=json.loads(Path(summaryfile).read_text())
    # Condor transfer_input_files stages the *same content* under the
    # shorter basename F20scalar.csv. GitHub/CERN source provenance
    # must authenticate BY CONTENT, not by the staging basename.
    source_name="F20_ALL_shards_scalar_LO_flavor_NOT_EXCLUSION.csv"
    expected=report.get("output_files_SHA256",{}).get(source_name)
    actual=hashlib.sha256(raw).hexdigest()
    if (report.get("four_complete_shards") is not True or
        report.get("status")!="F20_FOUR_SHARDS_MERGED_EXPLORATORY_SCAN_NOT_FULL_ZEE_ALLOWED"
        or report.get("calibrated_model_exclusions_or_accepted_points") is not None
        or expected is None or expected!=actual):
        raise ValueError("F21 F20 original merged scalar content SHA/source mismatch"
                         +" expected="+str(expected)+" actual="+actual)
    with Path(csvfile).open(newline="") as f:pool=list(csv.DictReader(f))
    if len(pool)!=report["screened_scalar_parameter_records_not_unique_allowed_volume"]:
        raise ValueError("F21 F20 original scan cohort not complete")
    return pool,report
def perturb(rng,p,wide=False):
    # Local block jump enriches physically accepted wide anchor basins.
    p={k:float(p[k]) for k in REQUIRED_FIELDS}
    masskick=75. if wide else 24.
    old_delta=p["alpha"]-p["beta"]
    p["mH1"]=float(np.clip(p["mH1"]+rng.normal(0,masskick),200.,1200.))
    p["mH2"]=float(np.clip(p["mH2"]+rng.normal(0,masskick*1.8),
            max(450.,p["mH1"]+91.1876+14.),2499.))
    p["gamma"]=float(np.clip(p["gamma"]+rng.normal(0,.10 if wide else .035),.08,1.49))
    t=math.tan(p["beta"])
    t=float(np.clip(t*math.exp(rng.normal(0,.28 if wide else .09)),.7,35.))
    p["beta"]=math.atan(t)
    p["alpha"]=p["beta"]+float(np.clip(old_delta+rng.normal(0,.018),-.13,.13))
    # Reconstruct high-scale custodial scaffold after mass/mixing jumps.
    md=math.sqrt(p["mH1"]**2*math.cos(p["gamma"])**2+
                 p["mH2"]**2*math.sin(p["gamma"])**2)
    p["mh2"]=float(np.clip(md+rng.normal(0.,45.),180.,2600.))
    p["ma"]=float(np.clip(md+rng.normal(0.,45.),180.,2600.))
    soft=max(2.e4,md*md+rng.normal(0.,45*max(md,125.)))
    p["m12sq"]=float(soft*math.sin(p["beta"])*math.cos(p["beta"]))
    return p
def select_stratified(rows,n):
    # Spread downstream expensive complex f/Y fits across mH2 classes,
    # rather than using only the high-proxy region mH2 ~800 GeV.
    buckets=defaultdict(list)
    for r in rows:
        p={k:r[k] for k in REQUIRED_FIELDS}
        key=region(p)
        if None in key:continue
        buckets[key].append(r)
    for key in buckets:
        buckets[key].sort(key=lambda r:(
          -r["production_weighted_nonleptonic_cascade_upper_proxy"],
           r["LO_flavor_shift_x1e4_NOT_CL"]))
    by_m2=defaultdict(list)
    # First diverse cells with one representative each; then next ranks.
    for (ib,it,ig,im),items in buckets.items():
        for ix,record in enumerate(items[:3]):
            by_m2[ib].append((ix,record))
    for k in by_m2:
        by_m2[k].sort(key=lambda p:(p[0],
           -p[1]["production_weighted_nonleptonic_cascade_upper_proxy"]))
    chosen=[];seen=set()
    while len(chosen)<n:
        progress=False
        for k in range(5):
            if by_m2[k]:
                _,r=by_m2[k].pop(0)
                if r["id"] in seen:continue
                chosen.append(r);seen.add(r["id"]);progress=True
                if len(chosen)>=n:break
        if not progress:break
    if len(chosen)<n:
        for r in sorted(rows,key=lambda r:
          -r["production_weighted_nonleptonic_cascade_upper_proxy"]):
            if r["id"] not in seen:
                chosen.append(r);seen.add(r["id"])
                if len(chosen)>=n:break
    return chosen
def execute(a):
    out=Path(a.output).expanduser().resolve()
    if out.exists():raise FileExistsError("Never overwrite F21 wide scan")
    if not(0<=a.shard<24 and 500<=a.global_draws<=30000 and
           0<=a.local_draws<=30000 and 40<=a.quad<=240 and
           4<=a.fits<=200 and 0<=a.vacuum<=a.fits and
           64<=a.vacuum_starts<=512):
        raise ValueError("F21 invalid resource settings")
    _,_,anchor_cohort=verify(a.f18,a.f19,a.f19b,a.f19c,a.f19d)
    pool,prior=f20_source(a.f20_csv,a.f20_summary)
    seed=a.seed+100003*a.shard
    rng=np.random.default_rng(seed)
    # F20 merged all-scalar CSV deliberately omitted the original
    # dimensional soft term and singlet quartics, and is NOT sufficient
    # to reconstruct a legitimate seed. The exact F19 source ledger
    # preserves every physical scalar input and is the safe fallback
    # if a shard initially finds no stratified wide survivor.
    by19=anchor_cohort[1]
    originals=sorted(by19)
    base={k:float(by19[originals[a.shard%len(originals)]][
         "scalar_original_F16_inputs"][k]) for k in REQUIRED_FIELDS}
    out.mkdir(parents=True,exist_ok=False)
    dump(out/"F21_manifest_start.json",{
      "status":"F21_RUNNING_NOT_ALLOWED","shard":a.shard,
      "F20_merged_csv_SHA256":sha(a.f20_csv),
      "F20_merged_summary_SHA256":sha(a.f20_summary),
      "original_F18_through_F19d_sha256":{
        k:sha(getattr(a,k.lower())) for k in ("F18","F19","F19b","F19c","F19d")},
      "requested_independent_stratified_draws":a.global_draws,
      "requested_local_custodial_draws":a.local_draws,
      "full_model_allowed":None})
    rejects=Counter();tries=Counter();passed=Counter()
    records=[]; accepted_pools=defaultdict(list);occupied=set()
    # Keep one *genuine previously screened* F19 scalar seed in the
    # resampling reservoir as a resilience control. It is not counted as
    # a new F21 discovery or one of the independent stratified attempts.
    # If high-mass strata yield real survivors, their bins are selected
    # with equal mass-shell probability during local exploration.
    if scalar_screen(base) is None:
        raise ValueError("F21 original F19 exact scalar anchor no longer passes Gate6")
    accepted_pools[index(base["mH2"],M2_EDGES)].append(base)
    print("F21_START",a.shard,"GLOBAL",a.global_draws,
          "LOCAL",a.local_draws,"M2_MAX",2500.,flush=True)
    total=a.global_draws+a.local_draws
    for i in range(total):
        # 100 strata across mH2(5) x tanb(5) x gamma(4); systematic
        # shuffled index ensures every stratum receives ~same attempts.
        if i<a.global_draws:
            stratum=(i*37+seed)%100
            p=candidate(rng,stratum)
            origin="independent_stratified"
        else:
            nonempty=[k for k,v in accepted_pools.items() if v]
            if nonempty:
                # Equal-chance choice of mass shell (not raw accepted-point
                # abundance). This prevents a good ~800 GeV basin from
                # taking all the local work away from rare >1TeV seeds.
                ib=int(rng.choice(nonempty))
                entries=accepted_pools[ib]
                basepoint=entries[int(rng.integers(len(entries)))]
            else:
                basepoint=base
            p=perturb(rng,basepoint,wide=(i%4==0))
            origin="local_reseeded"
        if p is None:rejects["kinematic_input"]+=1;continue
        ib=index(p["mH2"],M2_EDGES)
        key=(origin,str(ib))
        tries[key]+=1
        try:
            theory=scalar_screen(p)
            if theory is None:
                rejects["BFB_or_unitarity"]+=1;continue
            obs=ewpo_screen(p,a.quad)
            if obs is None:
                rejects["correlated_STU"]+=1;continue
            rec=make_record(p,theory,obs,i+1,
                "F21_s"+str(a.shard)+"_"+str(i).zfill(7),origin)
            f=model(p["mH1"],p["mH2"],p["beta"],p["gamma"],163.)
            rec.update({
               "shard":a.shard,
               "mH2_stratum":ib,
               "tanbeta_stratum":index(math.tan(p["beta"]),T_EDGES),
               "gamma_stratum":index(p["gamma"],G_EDGES),
               "sampling_source":origin,
               "LO_flavor_shift_x1e4_NOT_CL":f["linearized_2026_shift_x1e4"],
               "LO_flavor_BR_x1e4_NOT_CL":f["linearized_2026_central_BR_x1e4"],
               "LO_flavor_C7_NOT_CL":f["delta_C7_LO_analytic"],
               "LO_flavor_C8_NOT_CL":f["delta_C8_LO_analytic"],
               "full_Zee_allowed_or_excluded":None,
            })
            cell=(int(p["mH1"]/12),int(p["mH2"]/20),
                  int(p["gamma"]/.04),int(math.log(math.tan(p["beta"]))/.15),
                  int(p["ma"]/30),int(p["mh2"]/30))
            if cell not in occupied:
                records.append(rec)
                occupied.add(cell)
            passed[key]+=1
            entries=accepted_pools[ib]
            if len(entries)<600:
                entries.append(p)
            else:
                entries[int(rng.integers(len(entries)))]=p
        except (ValueError,ArithmeticError,OverflowError,
                FloatingPointError,np.linalg.LinAlgError) as exc:
            rejects["numeric_"+type(exc).__name__]+=1
        if (i+1)%3000==0:
            print("F21_PROGRESS",a.shard,i+1,"/",total,
                  "SCALAR_ACCEPTED",sum(passed.values()),
                  "DISTINCT",len(records),flush=True)
    if not records:raise ValueError("Wide sampling did not find scalar/EWPO passing records")
    keys=list(records[0].keys())
    save_csv(out/"F21_WIDE_all_scalar_LO_screen_NOT_ALLOWED.csv",records,keys)
    bins=defaultdict(lambda:{"tried":0,"passed":0})
    for (origin,ib),n in tries.items():bins[origin+"/"+str(ib)]["tried"]+=n
    for (origin,ib),n in passed.items():bins[origin+"/"+str(ib)]["passed"]+=n
    selected=select_stratified(records,a.fits)
    summary={
       "status":"F21_WIDE_SCALAR_STAGE_DONE_NOT_ALLOWED",
       "strata_mH2_edges_GeV":M2_EDGES,
       "strata_tanbeta_edges":T_EDGES,
       "strata_gamma_edges_radians":G_EDGES,
       "attempts":total,"distinct_scalar_EWPO_screened":len(records),
       "raw_scalar_EWPO_passes":sum(passed.values()),
       "rejections":dict(rejects),
       "per_origin_mH2_bin":dict(bins),
       "survivors_by_mH2_bin":dict(Counter(r["mH2_stratum"] for r in records)),
       "survivors_by_tanbeta_bin":dict(Counter(r["tanbeta_stratum"] for r in records)),
       "survivors_by_gamma_bin":dict(Counter(r["gamma_stratum"] for r in records)),
       "fully_allowed":None}
    dump(out/"F21_WIDE_stratified_coverage_NOT_ALLOWED.json",summary)
    print("F21_SCALAR_FINISHED",a.shard,len(records),
          "SELECTED",len(selected),
          "M2_BINS",summary["survivors_by_mH2_bin"],flush=True)
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
         "cascade_included_nonleptonic_proxy_NOT_F18_MadWidth":
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
    for name in ("f18","f19","f19b","f19c","f19d",
                 "f20-csv","f20-summary","output"):
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
    a=p.parse_args()
    execute(a)
if __name__=="__main__":main()
