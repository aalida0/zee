#!/usr/bin/env python3
"""F2: real EOS NLO / flavio quadratic B->Xs gamma response cross-check.

No 2026 preprint inputs. E4A source is source-pinned SuperIso CW matching.
The EOS NLO rate has an independent matrix-element calculation, but uses
the SAME E4A matching and wilson RG as the flavio path. Therefore this is
NOT independent Wilson matching and NOT 2017 full-NNLO TypeII reproduction.

Two expansion modes: LO NP C7,C8 only (F1-identical high-scale input);
NLO source CW C3-C8 added as alpha_s(mu0)/(4*pi)*C^(1), including
possible C4 source terms. NLO matched input in EOS/ fl avio higher-order
inclusive models is DIAGNOSTIC, NOT complete NLO/NNLO BSM calculation.
No custom 95% CL likelihood or physical Zee viability inference.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import math
import statistics
import sys
import traceback
from pathlib import Path

from zee_gateE4b_2026_observable_validation import read_source_e4a
from zee_gateE4a_integrated_precision_matching_calibration import (
    run_matching, TYPEII_MASSES, TANBETA_VALUES)
from zee_gateF1_peerreviewed_flavio_27_observable import (
    MU0, OBS, FlavioEngine, validate_e4a_typeii, sha)

SUCCESS="F2_INDEPENDENT_EOS_NLO_RESPONSE_LO_AND_NLO_SOURCE_AUDIT_NOT_EXCLUSION"
BLOCKED="F2_EOS_OR_MATCHING_OR_BASIS_VALIDATION_BLOCKED_NO_EXCLUSION"
E0=1.6
EOS_SCALE=4.2
# EOS and flavio retain different SM normalizations and fixed-order terms.
# Evaluate absolute NP ENHANCEMENTS and do not force agreement of SM rates.
# This rough tolerance only flags O(1) basis errors, NOT precision.
MAX_RESPONSE_FRACTIONAL_MISMATCH=0.60
CHECK_MASS=(300.,450.,550.,600.,650.,670.,700.,800.,1000.)
DENSE_MASS=tuple(sorted(set(float(x) for x in range(300,1001,25))|
                             {570.,580.,670.}))
WC_NLO_OPERATORS=tuple(range(3,9))
EOS_WC_NAMES={
    1:"b->s::c1",2:"b->s::c2",3:"b->s::c3",
    4:"b->s::c4",5:"b->s::c5",6:"b->s::c6",
    7:"b->s::Re{c7}",8:"b->s::c8",
}

def finite(v,label):
    z=float(v)
    if not math.isfinite(z):
        raise ValueError(f"nonfinite {label}")
    return z

class RatePair:
    """Both real libraries; EOS default SM parameters are retained."""
    def __init__(self):
        self.flavio=importlib.import_module("flavio")
        self.eos=importlib.import_module("eos")
        self.wilson=importlib.import_module("wilson")
        self.par=self.flavio.default_parameters.get_central_all()
        self.alpha160=self.flavio.physics.running.running.get_alpha(
            self.par,MU0,nf_out=5)["alpha_s"]
        if not 0.09<self.alpha160<0.14:
            raise ValueError("Unexpected alpha_s(160) or nf5 convention")
        self.as4pi=self.alpha160/(4*math.pi)
        self.calls=0
        self.flavio_version=getattr(self.flavio,"__version__","unknown")
        self.wilson_version=getattr(self.wilson,"__version__","unknown")
        self.eos_version=getattr(self.eos,"__version__","unknown")

    def prepare(self):
        p=self.eos.Parameters.Defaults()
        p["sb::mu"].set(EOS_SCALE)
        obs=self.eos.Observable.make(
            "B->X_sgamma::BR(E_min)@NLO",p,
            self.eos.Kinematics(E_min=E0),
            self.eos.Options(model="WET"))
        if obs is None:
            raise RuntimeError("EOS NLO inclusive observable not available")
        self.eos_p=p
        self.eos_obs=obs
        self.eos_defaults={n:finite(p[key].evaluate(),key)
                           for n,key in EOS_WC_NAMES.items()}
        self.eos_sm=self.eos_rate({k:0. for k in range(1,9)})
        self.flavio_sm=self.flavio_rate({})
        if not 1.e-4<self.eos_sm<7.e-4:
            raise ValueError("EOS SM is implausible for selected E_min")
        if abs(self.flavio_sm-3.36e-4)>0.20e-4:
            raise ValueError("flavio SM not near published 2015 reference")
        return {"eos_SM_NLO":self.eos_sm,"flavio_SM_2015_era":self.flavio_sm,
                "alpha_s_160GeV_nf5":self.alpha160,
                "EOS_scale_GeV":EOS_SCALE,
                "SM_norms_differ_not_cross_normalized":True}

    def eos_rate(self,low_wc):
        for n,key in EOS_WC_NAMES.items():
            v=finite(self.eos_defaults[n]+low_wc.get(n,0.),key)
            self.eos_p[key].set(v)
        val=finite(self.eos_obs.evaluate(),"EOS NLO BR")
        if not 1.e-7<val<1.e-3:
            raise ValueError("Bad EOS branching ratio")
        return val

    def wc(self,high):
        wc=self.flavio.WilsonCoefficients()
        # The E4A matching is NOT an EOS WET coefficient set; 'wilson'
        # converts each NP perturbation from mu0 to low WET/flavio.
        coeffs={f"C{n}_bs":complex(v) for n,v in high.items()
                if abs(v)>1.e-19}
        wc.set_initial(coeffs or {"C7_bs":0.},
                       MU0,eft="WET",basis="flavio")
        low=wc.get_wc("bsee",EOS_SCALE,self.par,nf_out=5)
        result={}
        for n in range(1,9):
            value=complex(low.get(f"C{n}_bs",0.))
            if abs(value.imag)>1e-10:
                raise ValueError(f"Unexpected imaginary WET C{n}")
            result[n]=finite(value.real,f"delta C{n} at EOS scale")
        other=[(k,v) for k,v in low.items() if k.startswith("C") and
               k.endswith("_bs") and k not in {f"C{n}_bs" for n in range(1,9)}
               and abs(v)>1e-9]
        if other:
            raise ValueError("Unsupported nontrivial NP WET operators: "+repr(other[:5]))
        return wc,result

    def flavio_rate(self,high):
        wc=self.flavio.WilsonCoefficients()
        coeffs={f"C{n}_bs":complex(v) for n,v in high.items()
                if abs(v)>1.e-19}
        wc.set_initial(coeffs or {"C7_bs":0.},
                       MU0,eft="WET",basis="flavio")
        val=finite(self.flavio.np_prediction(OBS,wc),"flavio BR")
        if not 1.e-7<val<1.e-3:
            raise ValueError("Bad flavio branching ratio")
        return val

    def evaluate(self,high):
        _,low=self.wc(high)
        eos_br=self.eos_rate(low)
        fl_br=self.flavio_rate(high)
        self.calls+=1
        return {
            "flavio_BR":fl_br,"eos_NLO_BR":eos_br,
            "flavio_delta_BR":fl_br-self.flavio_sm,
            "eos_NLO_delta_BR":eos_br-self.eos_sm,
            "EOS_low_scale_delta_C7":low[7],
            "EOS_low_scale_delta_C8":low[8],
            "EOS_low_scale_delta_C4":low[4],
        }

def from_e4a_source(coeffs, weight1, order, alpha):
    if order not in ("LO","NLO_matching"):
        raise ValueError("Invalid perturbative order")
    if not 0<=weight1<=1:
        raise ValueError("Invalid charged doublet mixing fraction")
    out={}
    for n in range(1,9):
        lo=coeffs[0,n]
        shift=weight1*lo[0]+(1-weight1)*lo[1]
        if order=="NLO_matching":
            nlo=coeffs[1,n]
            shift+=alpha*(weight1*nlo[0]+(1-weight1)*nlo[1])
        if n not in (7,8) and order=="LO" and abs(shift)>1e-11:
            raise ValueError("unexpected LO NP beyond dipoles; F1 mismatch")
        if order=="NLO_matching" and n in (1,2) and abs(shift)>1e-11:
            raise ValueError("unexpected NLO C1,2 source in F2 matching")
        if abs(shift)>1e-18:out[n]=shift
    return out

def model_coeffs(rows,ident):
    return {(order,n):
            (finite(rows[ident][order,f"C{n}"][1],"light"),
             finite(rows[ident][order,f"C{n}"][2],"heavy"))
            for order in (0,1,2) for n in range(1,9)}

def typeii_controls(e4a,binpath):
    """Use source-pinned equal-mass probe for 29+ mass controls.

    Verify every stored E4A 18-anchor LO+NLO dipole coefficient before
    accepting any *new* mass point from the existing compiled binary.
    """
    anchors=validate_e4a_typeii(e4a)
    result={}
    if not binpath.is_file():
        raise FileNotFoundError(f"E4A compiled probe is missing: {binpath}")
    for t in TANBETA_VALUES:
        for m in DENSE_MASS:
            x=run_matching(binpath,m,m,t,0.)["coefficient_rows"]
            keys={(o,n):(x[o,n][1],x[o,n][1])
                  for o in (0,1,2) for n in range(1,9)}
            if (m,t) in anchors:
                a=anchors[m,t]
                for op in (7,8):
                    if abs(keys[0,op][0]-a[f"LO_C{op}"])>3e-10 or abs(
                            keys[1,op][0]-a[f"NLO_C{op}_vendor"])>3e-10:
                        raise ValueError(f"E4A probe not same pinned source at mass {m}")
            result[m,t]=keys
        # E4A anchor 450/550/650 are off 25-GeV lattice? 450 yes,
        # 550 yes, 650 yes; add 670 explicit above.
        if set(m for m,tt in result if tt==t)!={*DENSE_MASS}:
            raise ValueError("TypeII dense curve missing masses")
    if len(result)!=2*len(DENSE_MASS):
        raise ValueError("Full Type-II curve count incorrect")
    return result

def run(pair,e4a,f1,path_probe,e1=None):
    data,models,rows=read_source_e4a(e4a)
    f1r=json.loads(Path(f1).read_text())
    if (f1r.get("source_e4a_summary_sha256")!=sha(e4a) or
        f1r.get("summary",{}).get("Zee_models")!=27 or
        f1r.get("summary",{}).get("TypeII_controls")!=18 or
        f1r.get("Zee_allowed_or_excluded") is not None):
        raise ValueError("F1 provenancing incomplete/not source identical")
    old={r["candidate_id"]:r for r in f1r["Zee_27_results"]}
    if len(old)!=27 or set(old)!={m["candidate_id"] for m in models}:
        raise ValueError("F1/F2 cohort identities disagree")
    old_legacy=None
    if e1 is not None:
        if data.get("fingerprints_sha256",{}).get("E1")!=sha(e1):
            raise ValueError("E1 original SuperIso SHA does not match E4A ancestry")
        e1data=json.loads(Path(e1).read_text())
        old_legacy={r["candidate_id"]:r for r in e1data.get("rows",[])}
        if (e1data.get("tested")!=27 or len(old_legacy)!=27 or
            set(old_legacy)!=set(old)):
            raise ValueError("Original legacy E1 27-spectrum source mismatched")
    pair.prepare()
    controls=typeii_controls(data,path_probe)
    typeii=[];zee=[]
    # Check the actual old F1 observable by recomputing all original 27.
    for k,model in enumerate(models,1):
        name=model["candidate_id"]
        coeff=model_coeffs(rows,name)
        w=math.cos(float(model["gamma"]))**2
        v_lo=pair.evaluate(from_e4a_source(coeff,w,"LO",pair.as4pi))
        v_nlo=pair.evaluate(from_e4a_source(coeff,w,"NLO_matching",pair.as4pi))
        if abs(v_lo["flavio_BR"]-old[name]["flavio_hybrid_BR"])>3e-10:
            raise ValueError(f"F2 nonreproduction of REAL F1 for {name}")
        for mode,z in (("LO",v_lo),("NLO_matching",v_nlo)):
            rec={"candidate_id":name,"input_matching_order":mode,
                 "mH1_GeV":model["mH1_GeV"],
                 "mH2_GeV":model["mH2_GeV"],
                 "tanbeta":model["tanbeta"],"gamma":model["gamma"],
                 **z,"F1_LO_flavio_control_BR":old[name]["flavio_hybrid_BR"],
                 "Zee_allowed_or_excluded":None,
                 "legacy_SuperIso_BR_separate_scheme":(
                     None if old_legacy is None else
                     finite(old_legacy[name][
                         "B_to_Xs_gamma_legacy_Zee_BR"],"E1 legacy BR")),
                 "legacy_E1_vs_f2_absolute_difference_DIAGNOSTIC":(
                     None if old_legacy is None else
                     z["flavio_BR"]-finite(old_legacy[name][
                         "B_to_Xs_gamma_legacy_Zee_BR"],"E1 legacy BR"))}
            zee.append(rec)
        print("F2_ZEE",f"{k}/27",name,
              "F1_reproduced",f"{v_lo['flavio_BR']:.11g}",
              "EOS_NLO_LOmatch_BR",f"{v_lo['eos_NLO_BR']:.11g}",
              "flavio_NLOmatch_BR",f"{v_nlo['flavio_BR']:.11g}",
              "EOS_NLO_NLOmatch_BR",f"{v_nlo['eos_NLO_BR']:.11g}",
              "EXCLUSION_UNKNOWN",flush=True)
    for t in TANBETA_VALUES:
        for m in DENSE_MASS:
            coeff=controls[m,t]
            for order in ("LO","NLO_matching"):
                z=pair.evaluate(from_e4a_source(
                    coeff,1.,order,pair.as4pi))
                typeii.append({"mass_GeV":m,"tanbeta":t,
                               "input_matching_order":order,**z,
                               "published_TypeII_580GeV_bound_reproduced":False})
    ref=pair.evaluate({})
    if abs(ref["flavio_delta_BR"])>1e-12 or abs(ref["eos_NLO_delta_BR"])>1e-12:
        raise ValueError("Zero NP EOS or flavio baseline not closed")
    checks={}
    for order in ("LO","NLO_matching"):
        samples=[x for x in typeii if x["input_matching_order"]==order]
        # Pure TypeII should constructively increase the rate and decouple.
        positive=all(x["flavio_delta_BR"]>0 and
                     x["eos_NLO_delta_BR"]>0 for x in samples)
        monotone=True
        for t in TANBETA_VALUES:
            arr=sorted((x for x in samples if x["tanbeta"]==t),
                       key=lambda x:x["mass_GeV"])
            for a,b in zip(arr,arr[1:]):
                if (a["flavio_delta_BR"]+3e-9<b["flavio_delta_BR"] or
                    a["eos_NLO_delta_BR"]+3e-9<b["eos_NLO_delta_BR"]):
                    monotone=False
        # EOS 1990s NLO formula has different scale and normalization;
        # only compare NP *response* on large enough shifts.
        ratios=[]
        for x in samples:
            if abs(x["flavio_delta_BR"])>1e-6:
                ratios.append(abs(x["eos_NLO_delta_BR"]-
                                  x["flavio_delta_BR"])/
                              abs(x["flavio_delta_BR"]))
        checks[order]={
            "constructive_both":positive,"decoupling_both":monotone,
            "median_fractional_deltaBR_discrepancy":statistics.median(ratios),
            "max_fractional_deltaBR_discrepancy":max(ratios),
            "exploratory_max_under_60pct":max(ratios)<
                MAX_RESPONSE_FRACTIONAL_MISMATCH,
        }
    reasons=[]
    for order,c in checks.items():
        if not c["constructive_both"]:reasons.append(order+": constructive sign failed")
        if not c["decoupling_both"]:reasons.append(order+": monotonicity failed")
        if not c["exploratory_max_under_60pct"]:
            reasons.append(order+": EOS and flavio NP rate shifts differ >60%")
    summary={
        "real_Zee_spectra":27,"real_Zee_rows_LO_plus_NLO_matching":len(zee),
        "typeii_mass_points_each_tanbeta":len(DENSE_MASS),
        "typeii_rows_LO_plus_NLO_matching":len(typeii),
        "F1_27_real_flavio_predictions_reproduced":True,
        "EOS_NLO_SM":pair.eos_sm,"flavio_SM":pair.flavio_sm,
        "alpha_s_160_nf5":pair.alpha160,"EOS_scale_GeV":EOS_SCALE,
        "EOS_and_flavio_compare_deltas_not_absolute_SM":True,
        "typeii_checks":checks,"errors":reasons,
        "EOS_independent_NLO_rate_but_shared_E4A_matching_and_wilson_running":True,
        "NLO_BSM_complete":False,
        "separate_legacy_E1_27_comparison_included":old_legacy is not None,
        "2017_TypeII_580GeV_95CL_reproduced":False,
        "publishable_Zee_95CL_exclusions":False}
    return {
        "status":SUCCESS if not reasons else BLOCKED,
        "source_F1_sha256":sha(f1),"source_E4A_sha256":sha(e4a),
        "source_E1_legacy_sha256":sha(e1) if e1 is not None else None,
        "flavio_version":pair.flavio_version,
        "EOS_version":pair.eos_version,"wilson_version":pair.wilson_version,
        "matching_raw_source":"E4A CW_calculator at mu0=160GeV",
        "C3_to_C8_NLO_terms_added_with_alpha_s_over_4pi":True,
        "raw_NNLO_C3_to_C6_discrepancies_unresolved":True,
        "SM":{"EOS_NLO":pair.eos_sm,"flavio":pair.flavio_sm},
        "Zee_27_by_matching_order":zee,
        "TypeII_dense_by_matching_order":typeii,
        "summary":summary,
        "Zee_physical_allowed_or_excluded":None}

def write_csv(path,rows):
    if not rows:return
    with Path(path).open("w",newline="") as f:
        out=csv.DictWriter(f,fieldnames=list(rows[0]))
        out.writeheader();out.writerows(rows)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--e4a-summary",type=Path,required=True)
    p.add_argument("--f1-summary",type=Path,required=True)
    p.add_argument("--e1-summary",type=Path)
    p.add_argument("--e4a-probe",type=Path)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    if a.output_dir.exists() and any(a.output_dir.iterdir()):
        p.error("Never overwrite a previous F2 report")
    a.output_dir.mkdir(parents=True,exist_ok=True)
    report={"status":BLOCKED,"Zee_physical_allowed_or_excluded":None}
    exitcode=1
    try:
        binpath=a.e4a_probe or (
            a.e4a_summary.parent/"gateE4A_source_pinned_multiorder_matching")
        for label,path in (
            ("E4A",a.e4a_summary),("F1 real run",a.f1_summary),
            ("compiled pinned E4A matching probe",binpath)):
            if not path.is_file():
                raise FileNotFoundError(f"{label} missing: {path.resolve()}")
        if a.e1_summary is not None and not a.e1_summary.is_file():
            raise FileNotFoundError("Optional E1 summary missing: "
                                    +str(a.e1_summary.resolve()))
        pair=RatePair()
        report=run(pair,a.e4a_summary,a.f1_summary,binpath,a.e1_summary)
        write_csv(a.output_dir/"F2_54_Zee_LO_NLOmatching_real_EOS_flavio.csv",
                  report["Zee_27_by_matching_order"])
        write_csv(a.output_dir/"F2_TypeII_dense_EOS_flavio_LO_NLOmatching.csv",
                  report["TypeII_dense_by_matching_order"])
        print("F2_COHORT",json.dumps(report["summary"]),flush=True)
        print("F2_EXCLUSIONS UNKNOWN",flush=True)
        exitcode=0 if report["status"]==SUCCESS else 1
    except Exception as exc:
        report={"status":BLOCKED,"error":repr(exc),
                "traceback":traceback.format_exc(),
                "Zee_physical_allowed_or_excluded":None}
        print("F2_FAIL_CLOSED",repr(exc),file=sys.stderr,flush=True)
        exitcode=1
    finally:
        dest=a.output_dir/"summary.json"
        dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
        print("F2_SUMMARY",dest,flush=True)
    return exitcode

if __name__=="__main__":
    raise SystemExit(main())
