#!/usr/bin/env python3
"""F14: 13-TeV production-normalized *included-channel* Zee cascade estimate.

Reads the actual, unchanged LHCHXSWG YR4 2016 Santander-matched
13-TeV Type-II mH+/tanbeta grid; interpolates positive cross sections
and relative uncertainty magnitudes in (mH, ln tanbeta). Conservatively
fails closed on missing/duplicate grid corners, out-of-domain points,
mismatched F13 IDs, or corrupt source hashes.

Production hypothesis:
  sigma(pp -> tbH2) ~ sin^2(gamma) sigma_TypeII(pp -> tbH; mH2,tanbeta).
The source F13 proxy ALREADY includes sin^2(gamma), so multiplying its
lepton-width-corrected proxy by *unrescaled* Type-II sigma gives the
included-channel cascade-rate estimate in pb. This is not an observed
fiducial rate or a fully complete 5-state branching-fraction prediction.
The original grid charge combination and matched-process convention
must be checked before labeling the physical +/- inclusive signal rate.
The 13-TeV reference must never be relabelled as 13.6/14 TeV.

Production grid: LHCHXSWG Heavy charged Higgs, 2016-02-05 (YR4).
Cite Degrande et al arXiv:1507.02549; Flechl et al arXiv:1409.5615;
LHCHXSWG Handbook YR4 arXiv:1610.07922 and other papers listed on
the original Twiki citation guide if publishing the results.
"""
from __future__ import annotations
import argparse,bisect,csv,hashlib,json,math
from pathlib import Path
from datetime import datetime,timezone
from zee_gateF7_309_2026_bsgamma_tension_sensitivity import ROOT,digest,writejson

STATUS="F14_OFFICIAL_LHCHXSWG_13TEV_NLO_MATCHED_TYPEII_GRID_ZEE_PARTIAL_CASCADE_ESTIMATE_NOT_FULL_RATE_OR_ALLOWED"
SOURCE_FILE="mflechl_xsec_13TeV_tHp_2016_2_5.txt"
ORIGINAL=ROOT/"work"/"zee_paper1_F13_heavy_final_20261021T125623Z"
SELECT="F13_selected_priority_scalar_2026LO_NOT_ALLOWED.csv"
RANKED="F13_ranked_heavy_neutrino_LFV_2026Eq4_NOT_ALLOWED.csv"
ALL="F13_all_heavy_scalar_2026LO_flavor_screen_NOT_ALLOWED.csv"
OUTNAME="F14_8_F13_13TeV_TypeII_XS_times_generalZee_included_cascade_NOT_FULL_SIGMA.csv"
NONFITTED="F14_minimum_Bsgamma_Z_control_without_lepton_fit_NOT_FULL_SIGMA.json"
GRID_REFERENCE="LHCHXSWG YR4 Santander matched Type-II, 2016-02-05"
VERIFIED_ORIGINAL_GRID_SHA256="45f9aa7e0f0a117894daaf9364f7e6b2c81e5273de9c50b8f7f593e5261681da"
GRID_URL=("https://twiki.cern.ch/twiki/pub/LHCPhysics/"
          "LHCHWGMSSMCharged/mflechl_xsec_13TeV_tHp_2016_2_5.txt")
ZEE_ZLL_E_MU_APPROX=.0673  # Z->ee + Z->mumu approximately; not analysis acceptance
SCHEMA=("mhp","tb","xsec","unc-","unc+")
MISSING=(
 "Published grid rate charge-summation convention not independently established",
 "2016 13-TeV Type-II matched production grid: no 13.6/14-TeV recalculation",
 "Singlet-mixing rescaling assumes no wrong-doublet quark Yukawas or FCNC",
 "Production rate uncertainty alone: no branching fractions or rescaling theory errors",
 "Charged/neutral total widths and all off-shell/loop/QCD modes incomplete",
 "Modern two-state B->Xs gamma 2026 full NNLO and NP theory covariance",
 "Full neutrino oscillation/LFV/LEP/LHC HiggsTools, RGE, vacuum stability",
 "Detector efficiency, background, fiducial acceptance and luminosity projections",
)

def positive(x,name,zero=False):
    value=float(x)
    if not math.isfinite(value) or (value<0 if zero else value<=0):
        raise ValueError(f"Invalid {name}: {x!r}")
    return value

def read_grid(filename):
    path=Path(filename).resolve()
    if not path.is_file():raise FileNotFoundError(path)
    text=path.read_text(encoding="utf-8",errors="strict")
    header="\n".join(s for s in text.splitlines() if s.lstrip().startswith("#"))
    required=("#Contacts: Martin Flechl", "#Date: 2016/2/5",
              "#Santander-matched cross sections", "#mhp tb xsec unc- unc+")
    for needle in required:
        if needle not in header:
            raise ValueError(f"Wrong LHCHXSWG grid/header, missing {needle}")
    if "sqrt(s)=13 TeV" not in header or "200-2000 GeV" not in header:
        raise ValueError("Grid is not the documented 13 TeV mass interval")
    data={};masses=set();tbs=set()
    for index,line in enumerate(text.splitlines(),1):
        s=line.strip()
        if not s or s.startswith("#"):continue
        items=s.split()
        if len(items)!=5:raise ValueError(f"Bad 5-column LHCHXSWG row {index}")
        mass,tanbeta,sigma,uncminus,uncplus=(
            positive(v,SCHEMA[i],zero=i>=3) for i,v in enumerate(items))
        if not 200<=mass<=2000 or not .1<=tanbeta<=60:
            raise ValueError(f"Outside stated 13-TeV domain in line {index}")
        if uncminus>sigma or uncplus>sigma:
            raise ValueError("Grid total uncertainty exceeds central production rate")
        key=(mass,tanbeta)
        if key in data:raise ValueError(f"Duplicated grid point {key}")
        data[key]=(sigma,uncminus,uncplus)
        masses.add(mass);tbs.add(tanbeta)
    if not data:raise ValueError("No valid grid data")
    # Header independently supplied in user chat: known numerical anchor.
    # Use an unusually tight tolerance because this tests wrong file version.
    ref=data.get((200.,.1))
    if ref is None or any(not math.isclose(v,target,rel_tol=1e-8,abs_tol=1e-9)
       for v,target in zip(ref,(336.33,42.293,41.074))):
        raise ValueError("YR4 2016 13-TeV grid known published first row differs")
    masses=sorted(masses);tbs=sorted(tbs)
    if masses[0]!=200 or masses[-1]!=2000 or tbs[0]!=.1 or tbs[-1]!=60:
        raise ValueError("Wrong mass/tanbeta full grid domain")
    # Reject incomplete grid rather than interpolating across data holes.
    missing=[(m,t) for m in masses for t in tbs if (m,t) not in data]
    if missing:
        raise ValueError(f"Nonrectangular or incomplete LHCHXSWG grid: first {missing[:3]}; "+
                         f"number_missing={len(missing)}")
    return {
       "data":data,"masses":masses,"tanbetas":tbs,
       "points":len(data),"min_mass":masses[0],"max_mass":masses[-1],
       "min_tanbeta":tbs[0],"max_tanbeta":tbs[-1],
       "raw_SHA256":digest(path),"raw_path":str(path),
       "header":"\n".join(header.splitlines()[:18]),
       "provenance":GRID_REFERENCE,
    }

def brackets(axis,x):
    if not(math.isfinite(x) and axis[0]<=x<=axis[-1]):
        raise ValueError(f"No extrapolation: {x} outside [{axis[0]},{axis[-1]}]")
    i=bisect.bisect_left(axis,x)
    if i<len(axis) and math.isclose(axis[i],x,rel_tol=1e-13,abs_tol=1e-12):
        return (axis[i],axis[i],0.)
    if i==0 or i==len(axis):
        raise ValueError("Outside actual grid")
    a,b=axis[i-1],axis[i]
    return (a,b,(x-a)/(b-a))

def interpolate(grid,mass,tanbeta):
    """Log cross section, positive relative asymmetric uncertainties.

    Mass is interpolated linearly, log(tanbeta) linearly; both the
    central xs log and relative uncertainties via corner interpolation.
    This is a documented numerical choice, NOT an uncertainty on
    interpolation or an official LHCHXSWG interpolation prescription.
    """
    mass=positive(mass,"mH2");tanbeta=positive(tanbeta,"tanbeta")
    ma,mb,u=brackets(grid["masses"],mass)
    ta,tb,_=brackets(grid["tanbetas"],tanbeta)
    v=(math.log(tanbeta)-math.log(ta))/(math.log(tb)-math.log(ta)) if ta!=tb else 0.
    def corners(i):
        a,b=grid["data"][(i,ta)],grid["data"][(i,tb)]
        def prep(val):
            sigma,lo,hi=val
            return (math.log(sigma),lo/sigma,hi/sigma)
        x,y=prep(a),prep(b)
        return [x[k]*(1-v)+y[k]*v for k in range(3)]
    lo,hi=corners(ma),corners(mb)
    lm,down_rel,up_rel=[(1-u)*lo[k]+u*hi[k] for k in range(3)]
    sigma=math.exp(lm)
    if not all(math.isfinite(x) and x>=0 for x in
               (sigma,down_rel,up_rel)) or sigma<=0:
        raise ValueError("Invalid interpolated xsec / uncertainty")
    return {
       "TypeII_Santander_NLO13TeV_sigma_pb":sigma,
       "TypeII_total_uncminus_pb":sigma*down_rel,
       "TypeII_total_uncplus_pb":sigma*up_rel,
       "TypeII_total_uncminus_fraction":down_rel,
       "TypeII_total_uncplus_fraction":up_rel,
       "mass_grid_nodes_GeV":[ma,mb],
       "tanbeta_grid_nodes":[ta,tb],
       "mass_linear_fraction":u,
       "ln_tanbeta_linear_fraction":v,
       "interpolation":"bilinear log(sigma), linear frac(unc) in (mass,ln tanbeta)",
       "interpolation_uncertainty_assessed":False,
    }

def read_f13(folder):
    folder=Path(folder).resolve()
    summary_path=folder/"summary.json";manifest_path=folder/"manifest.json"
    summ=json.loads(summary_path.read_text())
    man=json.loads(manifest_path.read_text())
    status="F13_HEAVY_P1_2026_EQ4_FLAVOR_GUIDED_NEUTRINO_LFV_FEASIBILITY_NOT_ALLOWED"
    if (summ.get("status")!=status or man.get("status")!=status or
        man.get("summary_SHA256")!=digest(summary_path) or
        summ.get("full_physical_model_allowed_or_excluded") is not None or
        summ.get("physical_hadronic_cascade_rate_pb") is not None or
        summ.get("selected_for_exact_neutrino_and_partial_lfv")!=8):
        raise ValueError("F13 real source cohort status/provenance wrong")
    original_hashes=summ.get("outputs_SHA256",{})
    for name in (SELECT,RANKED,ALL):
        if original_hashes.get(name)!=digest(folder/name):
            raise ValueError(f"F13 input file SHA mismatch {name}")
    def csvrows(name):
        with (folder/name).open(newline="") as stream:
            return list(csv.DictReader(stream))
    selected=csvrows(SELECT);ranked=csvrows(RANKED);allrows=csvrows(ALL)
    if (len(selected)!=8 or len(ranked)!=8 or
        len({r["id"] for r in selected})!=8 or
        {r["id"] for r in selected}!={r["candidate_id"] for r in ranked} or
        not allrows):
        raise ValueError("Wrong or incomplete source F13 selected cohort")
    by_id={r["id"]:r for r in selected}
    for row in ranked:
        name=row["candidate_id"];scalar=by_id[name]
        for x,y in (("mH1","mH1"),("mH2","mH2"),
                    ("gamma","gamma"),("tanbeta","tanbeta")):
            if not math.isclose(float(scalar[x]),float(row[y]),
                 rel_tol=3e-11,abs_tol=3e-9):
                raise ValueError(f"F13 mismatched scalar and lepton solution {name}")
        if (row.get("full_Zee_model_allowed_or_excluded","") not in ("","None","null")
            or row.get("2026_NNLO_excluded_or_allowed","") not in ("","None","null")
            or row["neutrino_closed_fixed_old_NO"].lower()!="true"):
            raise ValueError("F13 selected original claims unavailable full Zee validation")
    return summ,selected,ranked,allrows,{
      "F13_summary_SHA256":digest(summary_path),
      "F13_manifest_SHA256":digest(manifest_path),
      "F13_SELECTED_SHA256":digest(folder/SELECT),
      "F13_RANKED_SHA256":digest(folder/RANKED),
      "F13_ALL_SHA256":digest(folder/ALL),
    }

def selected_records(grid,ranked):
    results=[]
    for r in ranked:
        name=r["candidate_id"]
        gam=positive(r["gamma"],"gamma")
        t=positive(r["tanbeta"],"tanbeta")
        mass=positive(r["mH2"],"mH2")
        if not 0<gam<math.pi/2 or mass<200:
            raise ValueError("Invalid original charged scalar inputs")
        proxy=positive(r["lepton_included_cascade_proxy_NOT_pb"],"lepton proxy",
                       zero=True)
        previous=positive(r[
          "scalar_nonleptonic_included_cascade_proxy_NOT_pb"],"nonlepton proxy")
        if proxy>previous+1e-8 or previous>1+1e-8:
            raise ValueError("F13 included-channel proxy normalization invalid")
        shape=interpolate(grid,mass,t)
        sig=shape["TypeII_Santander_NLO13TeV_sigma_pb"]
        down,up=shape["TypeII_total_uncminus_pb"],shape["TypeII_total_uncplus_pb"]
        mix=math.sin(gam)**2
        conditional=proxy/mix
        if not 0<=conditional<=1+1e-8:
            raise ValueError("Unphysical inferred included-channel BR product")
        result={
          "candidate_id":name,"mH1_GeV":positive(r["mH1"],"mH1"),
          "mH2_GeV":mass,"tanbeta":t,"gamma_rad":gam,
          "mixing_sin2_gamma_doublet_production_weight":mix,
          **shape,
          "Zee_assuming_TypeII_aligned_quarks_sigma_H2_pb":sig*mix,
          "Zee_prod_total_uncminus_pb":down*mix,
          "Zee_prod_total_uncplus_pb":up*mix,
          "general_Zee_conditional_included_BR_H2_H1Z_times_BR_H1_tb":conditional,
          "general_Zee_included_channel_cascade_proxy_NOT_pb":proxy,
          "13TeV_TypeII_sigma_times_included_cascade_proxy_pb":sig*proxy,
          "13TeV_cascade_estimate_prod_uncminus_ONLY_pb":down*proxy,
          "13TeV_cascade_estimate_prod_uncplus_ONLY_pb":up*proxy,
          "13TeV_cascade_Z_to_ee_mumu_estimate_pb":sig*proxy*ZEE_ZLL_E_MU_APPROX,
          "Z_to_ee_mumu_assumed_BR":ZEE_ZLL_E_MU_APPROX,
          "2026_Eq4_Bsgamma_z_diagnostic_NOT_CL":float(r["z_UNCALIBRATED_NOT_CL"]),
          "2026_Eq4_pass_1p96_diagnostic_ONLY":r[
              "z_below_1p96_diagnostic_ONLY"].lower()=="true",
          "fixed_old_NO_neutrino_closed":r["neutrino_closed_fixed_old_NO"].lower()=="true",
          "partial_LFV_subset_ratio_NOT_full_CL":float(r["partial_LFV_score_NOT_full_CL"]),
          "fully_Zee_allowed_or_excluded":None,
          "physical_complete_13TeV_R_tbZ_pb":None,
          "complete_model_decay_BRs_calculated":False,
          "experimental_limit_or_sensitivity_calculated":False,
          "LHCHXSWG_13TeV_charge_convention_checked":False,
          "model_dependent_production_uncertainty_completed":False,
        }
        results.append(result)
    return sorted(results,key=lambda x:-
        x["13TeV_TypeII_sigma_times_included_cascade_proxy_pb"])

def minimum_flavor_control(grid,allrows):
    """Source-backed scalar-only control; NO f/Y solution or lepton proxy."""
    best=min(allrows,key=lambda r:float(r["abs_z_illustrative_NOT_CL"]))
    row=interpolate(grid,positive(best["mH2"],"min-z H2"),
                        positive(best["tanbeta"],"min-z tanbeta"))
    gam=positive(best["gamma"],"min-z gamma")
    nonlep=positive(best[
        "production_weighted_nonleptonic_cascade_upper_proxy"],
        "min-z nonlepton proxy",zero=True)
    return {
      "candidate_id":best["id"],
      "mH1_GeV":float(best["mH1"]),"mH2_GeV":float(best["mH2"]),
      "tanbeta":float(best["tanbeta"]),"gamma":gam,
      "min_screened_2026_Bsgamma_abs_z_NOT_CL":float(best[
           "abs_z_illustrative_NOT_CL"]),
      "TypeII_grid_production_sigma13_pb":row[
           "TypeII_Santander_NLO13TeV_sigma_pb"],
      "nonleptonic_cascade_proxy_NOT_a_BR":nonlep,
      "13TeV_nonleptonic_cascade_included_ESTIMATE_pb":nonlep*row[
           "TypeII_Santander_NLO13TeV_sigma_pb"],
      "complex_neutrino_Yukawa_optimized":False,
      "real_general_Zee_lepton_widths_applied":False,
      "full_Zee_allowed_or_excluded":None,
    }

def execute(args):
    out=Path(args.output).resolve()
    if out.exists():raise FileExistsError("Refuse overwrite existing F14 results")
    folder=Path(args.f13_dir).resolve()
    _,_,ranked,allrows,proof=read_f13(folder)
    grid=read_grid(args.grid)
    if (grid["raw_SHA256"]!=VERIFIED_ORIGINAL_GRID_SHA256 or
        grid["points"]!=2484 or len(grid["masses"])!=36 or
        len(grid["tanbetas"])!=69):
        raise ValueError("F14 original 2016 YR4 CERN grid SHA/size mismatch: do not substitute a different table")
    result=selected_records(grid,ranked)
    control=minimum_flavor_control(grid,allrows)
    out.mkdir(parents=True,exist_ok=False)
    with (out/OUTNAME).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(result[0]))
        w.writeheader();w.writerows(result)
    writejson(out/NONFITTED,control)
    report={
      "status":STATUS,"source":GRID_REFERENCE,
      "grid_header":grid["header"],
      "grid_url":GRID_URL,"grid_sha256":grid["raw_SHA256"],
      "grid_unique_masses":len(grid["masses"]),
      "grid_unique_tanbetas":len(grid["tanbetas"]),
      "grid_point_count":grid["points"],
      "source_F13":proof,
      "eight_same_scalar_neutrino_lepton_widths_evaluated":len(result),
      "rates_energy_GeV":13000,
      "cross_sections_in_pb":True,
      "uncertainties":"LHCHXSWG quoted TOTAL production uncertainties only",
      "method":"2D log sigma + linear relative uncertainty interpolation in (m,ln tanbeta)",
      "14TeV_or_13p6TeV_cross_section_derived":False,
      "production_rescale_consistent_with_proxy":True,
      "charged_cross_section_sum_convention_source_confirmed":False,
      "min_z_control_not_neutrino_fitted":control,
      "best_13TeV_included_cascade_estimate":result[0],
      "none_are_complete_physical_Zee_rates_or_allowed":True,
      "modern_full_NNLO_Zee_Bsgamma":None,
      "real_Zee_hadronic_signal_complete":None,
      "paper1_publication_GO_or_NOGO":None,
      "missing":MISSING,
      "script_SHA256":digest(Path(__file__)),
      "outputs_SHA256":{OUTNAME:digest(out/OUTNAME),NONFITTED:digest(out/NONFITTED)},
    }
    writejson(out/"summary.json",report)
    writejson(out/"manifest.json",{
      "status":STATUS,"summary_SHA256":digest(out/"summary.json"),
      "grid_SHA256":grid["raw_SHA256"],
      "F13_summary_SHA256":proof["F13_summary_SHA256"],
    })
    for r in result:
        print("F14_SIGNAL",r["candidate_id"],
          "M_H2",format(r["mH2_GeV"],".1f"),
          "TYPEII_13TeV_PB",format(r["TypeII_Santander_NLO13TeV_sigma_pb"],".9g"),
          "ZEE_H2_13TeV_PB",format(r["Zee_assuming_TypeII_aligned_quarks_sigma_H2_pb"],".9g"),
          "INCLUDED_TBZ_13TeV_PB",format(r[
            "13TeV_TypeII_sigma_times_included_cascade_proxy_pb"],".9g"),
          "PROD_DOWN_UP_PB",format(r[
            "13TeV_cascade_estimate_prod_uncminus_ONLY_pb"],".4g"),
          format(r["13TeV_cascade_estimate_prod_uncplus_ONLY_pb"],".4g"),
          "INCOMPLETE_WIDTHS_NOT_ALLOWED",flush=True)
    print("F14_MIN_FLAVOR_CONTROL",control["candidate_id"],
          "z",control["min_screened_2026_Bsgamma_abs_z_NOT_CL"],
          "NONFITTED_ESTIMATE_PB",control[
            "13TeV_nonleptonic_cascade_included_ESTIMATE_pb"],flush=True)
    print("F14_STATUS",STATUS,"N",len(result),"COMPLETE_ZEE_RATE",False,flush=True)
    print("F14_SUMMARY",out/"summary.json",flush=True)
    return report

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--grid",type=Path,
        default=ROOT/"data"/"lhchxswg"/SOURCE_FILE)
    ap.add_argument("--f13-dir",type=Path,default=ORIGINAL)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args(argv)
    execute(args)
if __name__=="__main__":
    main()
