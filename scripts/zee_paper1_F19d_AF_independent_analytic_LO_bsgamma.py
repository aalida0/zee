#!/usr/bin/env python3
"""F19d: AF-independent, analytical LO Type-II two-charged C7/C8 diagnostic.

Uses exact F18/F19/F19b/F19c source-hash-joined three cases; no SuperIso
binary, F13 AF CSV, or AF server required. Mahmoudi & Stal,
PRD81 035016 (2010), arXiv:0907.1791 Eqs.(17),(18), at matching scale
mu0 = 160 GeV, and Misiak et al. 2026 arXiv:2608.29863 Eq.(4).
Physical running m_t(mu0) treated as a specified INPUT. The default 163
GeV is a transparent illustrative value, not the validated original
SuperIso A1S running-mass prescription. 160, 163, 166 GeV are compared.

All ratios/shifts are LO and linearized; NEITHER full 2026 B->Xs gamma
prediction nor 95% CL classification. Original AF F13 flavor data are
NOT reconstructed or claimed source-equivalent. Call A1S/E4A crosscode
only after restoring exact vendor and matching scheme.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path

CASES=("F13_heavy_0001330","F13_heavy_0000981","F13_heavy_0001003")
STATUS="F19D_AF_INDEPENDENT_ANALYTIC_2CH_LO_C7C8_LINEARIZED_NOT_CALIBRATED"
MISSING=[
 "full NNLO matched two-charged 2026 B->Xs gamma and correlated uncertainties",
 "source-matched A1S/E4A original vendor running top scheme and independent code validation",
 "NNLO/LO scheme and scale variation calibrated to 2026 Type-II reference",
 "complete flavor/neutral-Higgs and quark-alignment contributions",
 "no full general Zee model allowance or exclusion from LO response",
]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def positive(x,name):
    if isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) or x<=0:
        raise ValueError("Invalid "+name)
    return float(x)

def kernels(y):
    """Eqs.(18) of Mahmoudi & Stal 0907.1791, standard WET Q7/Q8."""
    y=positive(y,"y=m_t(mu0)^2/mH^2")
    if abs(y-1)<0.01:
        raise ValueError("F19d LO kernels not numerically stable near y=1; use series expansion")
    l=math.log(y); t=y-1
    return {
        "F7_1":y*(7-5*y-8*y*y)/(24*t**3)+y*y*(3*y-2)*l/(4*t**4),
        "F8_1":y*(2+5*y-y*y)/(8*t**3)-3*y*y*l/(4*t**4),
        "F7_2":y*(3-5*y)/(12*t**2)+y*(3*y-2)*l/(6*t**3),
        "F8_2":y*(3-y)/(4*t**2)-y*l/(2*t**3),
    }

def single(m,t,mt):
    """Type-II lambda_tt=cot(beta),lambda_bb=-tan(beta), Eq.(17)."""
    m=positive(m,"charged mass")
    t=positive(t,"tanbeta")
    mt=positive(mt,"MSbar running mt specified at mu0=160GeV")
    k=kernels((mt/m)**2)
    # Eq.17: C_i^H=(lambda_tt^2/3) F_i^(1)
    #            -lambda_tt*lambda_bb F_i^(2);
    # TypeII λtt λbb=-1, so constructive F_i^(2).
    d7=k["F7_1"]/(3*t*t)+k["F7_2"]
    d8=k["F8_1"]/(3*t*t)+k["F8_2"]
    return d7,d8

def model(m1,m2,beta,gamma,mt):
    m1=positive(m1,"mH1")
    m2=positive(m2,"mH2")
    if not m1<m2:raise ValueError("Ordered charged masses required")
    if not 0<beta<math.pi/2 or not 0<gamma<math.pi/2:
        raise ValueError("Invalid mixing")
    t=math.tan(beta)
    light=single(m1,t,mt)
    heavy=single(m2,t,mt)
    w1=math.cos(gamma)**2
    w2=math.sin(gamma)**2
    d7=w1*light[0]+w2*heavy[0]
    d8=w1*light[1]+w2*heavy[1]
    shift=-8.51*d7-2.16*d8
    ref=single(670.,t,mt)
    reference_shift=-8.51*ref[0]-2.16*ref[1]
    if not all(math.isfinite(x) for x in (d7,d8,shift,reference_shift)):
        raise ValueError("Nonfinite analytic LO")
    if shift<=0 or reference_shift<=0:
        raise ValueError("Unexpected sign or operator basis: positive Type-II LO rate shift required")
    return dict(
        mH1_GeV=m1,mH2_GeV=m2,tanbeta=t,gamma_rad=gamma,
        running_top_at_mu0_input_GeV=mt,mu0_GeV=160.,
        weight_H1_cos2gamma=w1,weight_H2_sin2gamma=w2,
        delta_C7_LO_analytic=d7,delta_C8_LO_analytic=d8,
        single_light_delta_C7=light[0],single_heavy_delta_C7=heavy[0],
        single_light_delta_C8=light[1],single_heavy_delta_C8=heavy[1],
        linearized_2026_shift_x1e4=shift,
        linearized_2026_central_BR_x1e4=3.54+shift,
        pure_TypeII_670_shift_x1e4_same_input=reference_shift,
        Zee_shift_over_TypeII670_shift_LO_NOT_CL=shift/reference_shift,
        TypeII_2026_670_bound_not_applied_to_Zee=True,
        A1S_SuperIso_source_reproduced=False,
        full_NNLO_flavor_likelihood=None,physical_Zee_allowed_or_excluded=None,
    )

def checked_cohort(f18,f19,f19b,f19c):
    files=[Path(p).expanduser().resolve() for p in (f18,f19,f19b,f19c)]
    objects=[json.loads(f.read_text()) for f in files]
    a,b,c,d=objects
    if (a.get("status")!="F18_THREE_CASES_CONDOR_OR_LOCAL_MERGED_TREE_LO_NOT_ALLOWED"
        or a.get("three_original_benchmarks_LO_MadWidth_completed") is not True
        or a.get("physical_Zee_model_allowed_or_excluded") is not None):
        raise ValueError("F19d original F18 source not a completed tree cohort")
    if (b.get("status")!="F19_REAL_F18_THREE_SCALAR_BFB_UNITARITY_STU_SCREENS_NOT_FULL_ZEE_ALLOWED"
        or b.get("F18_merged_JSON_SHA256")!=sha(files[0])
        or b.get("observational_allowance_or_exclusion") is not None):
        raise ValueError("F19d exact F18-F19 SHA source mismatch")
    if (c.get("status")!="F19B_EXACT_F17F_COMPLEX_NEUTRINO_PARTIAL_LFV_NOT_FULL_EXCLUSION"
        or c.get("F18_exact_merged_sha256")!=sha(files[0])
        or c.get("F19_real_scalar_EWPO_ledger_sha256")!=sha(files[1])
        or c.get("FULL_MODEL_EXPERIMENTALLY_ALLOWED_OR_EXCLUDED") is not None):
        raise ValueError("F19d exact F19b SHA source mismatch")
    if (d.get("status")!="F19C_EXACT_F18_F19B_TREE_CHARGE_BREAKING_VACUUM_WITNESS_SCREEN_NOT_GLOBAL"
        or d.get("original_F18_SHA256")!=sha(files[0])
        or d.get("original_F19_SHA256")!=sha(files[1])
        or d.get("original_F19b_SHA256")!=sha(files[2])
        or d.get("full_Zee_theory_and_experimental_allowed") is not None):
        raise ValueError("F19d F19c real 3-case vacuum source mismatch")
    if b.get("F16_original_source_bundle_SHA256")!=c.get("F16_F17f_source_bundle_sha256"):
        raise ValueError("F19b original full-complex source bundle mismatch")
    cohort=[]
    for obj,key in ((a,"benchmarks"),(b,"benchmarks"),(c,"results"),(d,"cases")):
        rows=obj.get(key)
        if not isinstance(rows,list) or len(rows)!=3 or (
            set(r.get("candidate_id") for r in rows)!=set(CASES)):
            raise ValueError("F19d mandatory original cohort "+key+" not exact")
        cohort.append({r["candidate_id"]:r for r in rows})
    original,scalar,flavor,vacuum=cohort
    for name in CASES:
        if not math.isclose(
             float(original[name]["cascade_BR_product_model_LO_2plus3"]),
             float(scalar[name]["BR_cascade_tree_MadWidth"]),
             rel_tol=1e-12,abs_tol=1e-14):
            raise ValueError("F19d original F18/F19 cascade mismatch")
        if not math.isclose(
             float(original[name]["cascade_BR_product_model_LO_2plus3"]),
             float(flavor[name]["F18_actual_model_tree_cascade_BR"]),
             rel_tol=1e-12,abs_tol=1e-14):
            raise ValueError("F19d exact F17f flavor source mismatch")
        if not math.isclose(
             float(original[name]["cascade_BR_product_model_LO_2plus3"]),
             float(vacuum[name]["BR_cascade_tree_MadWidth"]),
             rel_tol=1e-12,abs_tol=1e-14):
            raise ValueError("F19d exact F19c vacuum source mismatch")
    return files,objects,cohort

def run(f18,f19,f19b,f19c,out,*,mt_cases=(160.,163.,166.)):
    out=Path(out).expanduser().resolve()
    if out.exists():raise FileExistsError("F19d refuses overwrite of old source-checked run")
    mt_cases=tuple(positive(x,"mt input") for x in mt_cases)
    if len(mt_cases)!=3 or not(145<=min(mt_cases)<max(mt_cases)<=180):
        raise ValueError("Exactly three different sensible running mt inputs required")
    files,objects,cohort=checked_cohort(f18,f19,f19b,f19c)
    by18,by19,_,_=cohort
    allrows=[]
    for name in CASES:
        p=by19[name]["scalar_original_F16_inputs"]
        for mt in mt_cases:
            row=model(p["mH1"],p["mH2"],p["beta"],p["gamma"],mt)
            row["candidate_id"]=name
            row["F18_tree_cascade_BR"]=float(by18[name][
                "cascade_BR_product_model_LO_2plus3"])
            row["running_top_scheme_uncertainty_NOT_calibrated"]=True
            allrows.append(row)
    result={
        "status":STATUS,"actual_CERN_F18_F19_F19b_F19c_source_SHA256":{
            name:sha(f) for name,f in zip(("F18","F19","F19b","F19c"),files)},
        "original_three_cases_matched":True,
        "AF_original_F13_csv_unavailable_not_required":True,
        "analytic_LO_reference":"Mahmoudi and Stal PRD81 035016 (2010) Eqs17-18, arXiv:0907.1791",
        "linearized_2026_reference":"Misiak et al. arXiv:2608.29863 Eq4 (not quadratic or full likelihood)",
        "mu0_GeV":160,
        "mt_running_mu0_scenario_inputs_GeV":list(mt_cases),
        "original_SuperIso_A1S_running_mt_and_vendor_revalidated":False,
        "full_B_to_Xs_gamma_95CL":None,
        "full_Zee_model_experimentally_allowed_or_excluded":None,
        "missing_constraints":MISSING,
        "rows":allrows
    }
    out.mkdir(parents=True,exist_ok=False)
    (out/"F19d_analytic_LO_three_source_matched_NOT_PRECISION.json").write_text(
      json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n")
    with (out/"F19d_analytic_two_charged_2026_linearized_LO_NOT_CL.csv").open("w",newline="") as h:
        cols=("candidate_id","mH1_GeV","mH2_GeV","tanbeta","gamma_rad",
           "running_top_at_mu0_input_GeV","weight_H1_cos2gamma","weight_H2_sin2gamma",
           "delta_C7_LO_analytic","delta_C8_LO_analytic","linearized_2026_shift_x1e4",
           "linearized_2026_central_BR_x1e4","pure_TypeII_670_shift_x1e4_same_input",
           "Zee_shift_over_TypeII670_shift_LO_NOT_CL","F18_tree_cascade_BR")
        w=csv.DictWriter(h,fieldnames=cols);w.writeheader()
        w.writerows({k:r[k] for k in cols} for r in allrows)
    for row in allrows:
        print("F19D_CASE",row["candidate_id"],"MT_INPUT",row["running_top_at_mu0_input_GeV"],
          "C7_LO",format(row["delta_C7_LO_analytic"],".10g"),
          "C8_LO",format(row["delta_C8_LO_analytic"],".10g"),
          "BR_x1e4_LO_LINEARIZED",format(row["linearized_2026_central_BR_x1e4"],".10g"),
          "ZEE_TO_670_RATIO_NOT_CL",
          format(row["Zee_shift_over_TypeII670_shift_LO_NOT_CL"],".10g"),
          "FULL_ALLOWED","UNKNOWN",flush=True)
    print("F19D_DONE",len(allrows),"ROWS",len(CASES),"CASES",
         "SOURCE_VENDOR_MATCHED",False,"PHYSICAL_EXCLUSION",False)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--f18",type=Path,required=True)
    p.add_argument("--f19",type=Path,required=True)
    p.add_argument("--f19b",type=Path,required=True)
    p.add_argument("--f19c",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--mt-cases",type=float,nargs=3,default=(160.,163.,166.))
    args=p.parse_args()
    run(args.f18,args.f19,args.f19b,args.f19c,args.output_dir,
        mt_cases=args.mt_cases)
if __name__=="__main__":main()
