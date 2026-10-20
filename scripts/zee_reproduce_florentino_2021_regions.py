#!/usr/bin/env python3
"""Source-faithful first-stage Florentino et al 2021 Table 2 scalar pilot.

Reads P1-P4 **benchmark REGIONS** from data/florentino2021_table2_regions.json.
Does not imply any particular region midpoint appeared in the paper or
passed its historical Higgs/CB/B->Xs gamma selections.

Our existing scalar backend accepts only 0<gamma<pi/2.
Signed-angle cases P3/P4 deliberately FAIL CLOSED until the source and
code mass/mixing conventions are independently reconciled.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

from gate6_benchmark import benchmark as scalar_benchmark
from gate6_width_inventory import inventory as scalar_width_inventory

BASE=Path(__file__).resolve().parents[1]
REGIONS=BASE/"data/florentino2021_table2_regions.json"
STATUS="FLORENTINO_TABLE2_ILLUSTRATIVE_REGION_MEMBER_NOT_PUBLISHED_POINT_OR_ALLOWED"

def load_regions(path=REGIONS):
    x=json.loads(Path(path).read_text())
    if x["schema_version"]!=1 or set(x["benchmarks"])!={
            "P1","P2","P3","P4"}:
        raise ValueError("Unexpected Florentino 2021 benchmark source")
    for key,p in x["benchmarks"].items():
        for k in ("lambda_c","k1","k2","k12","alpha_rad",
                  "gamma_rad","mh2_GeV","ma_GeV","m12sq_GeV2"):
            if not math.isfinite(float(p[k])):
                raise ValueError(f"Nonfinite {key} {k}")
        for field in ("mH1_interval_GeV","mH2_interval_GeV"):
            a,b=p[field]
            if not (0<a<b):raise ValueError("Invalid source mass interval")
    return x

def build_inputs(region, *,mH1=None,mH2=None,beta=None,k12=None):
    m1lo,m1hi=region["mH1_interval_GeV"]
    m2lo,m2hi=region["mH2_interval_GeV"]
    m1=(m1lo+m1hi)/2 if mH1 is None else float(mH1)
    m2=(m2lo+m2hi)/2 if mH2 is None else float(mH2)
    gamma=float(region["gamma_rad"])
    alpha=float(region["alpha_rad"])
    if not(0<gamma<math.pi/2):
        raise ValueError(
            "Signed gamma in Table 2 requires explicit charged-basis/"
            "mu4 convention audit; cannot take abs(gamma) silently")
    if beta is None:
        if not (0<alpha<math.pi/2):
            raise ValueError("Negative alpha: beta cannot be inferred "
                             "from ambiguous source ~alpha statement")
        beta=alpha # representative chosen by us, not author-provided exact beta
    beta=float(beta)
    if not(m1lo<=m1<=m1hi and m2lo<=m2<=m2hi and
           0<beta<math.pi/2 and m2>m1):
        raise ValueError("Requested representative outside source region/domain")
    if k12 is not None and not math.isfinite(float(k12)):
        raise ValueError("Invalid k12 override")
    return dict(
        beta=beta,mH1=m1,mH2=m2,alpha=alpha,
        gamma=gamma,m12sq=float(region["m12sq_GeV2"]),
        mh1=float(region["mh125_GeV"]),mh2=float(region["mh2_GeV"]),
        ma=float(region["ma_GeV"]),lc=float(region["lambda_c"]),
        k1=float(region["k1"]),k2=float(region["k2"]),
        k12=float(region["k12"] if k12 is None else k12)
    )


def less_conservative_analytic_bfb(scalar):
    """Another SUFFICIENT (not necessary) global *quartic* BFB certificate.

    Write x1=|phi1|², x2=|phi2|², xc=|chi|². Since
    |Re(phi1^dag phi2)| <= sqrt(x1*x2), the singlet cross term obeys
    xc*(k1*x1+k2*x2-2*k12*Re(phi1^dag phi2))
    >= xc*(k1*x1+k2*x2-2*abs(k12)*sqrt(x1*x2)).
    The RHS is nonnegative if the symmetric 2x2 k matrix
    [[k1,-|k12|],[-|k12|,k2]] is positive semidefinite.
    Combine this with ordinary CP-conserving 2HDM BFB and lc>=0.
    A negative lambda1 is a NECESSARY BFB failure, irrespective of
    any weakness in the original Gate 6 *sufficient* condition.
    """
    q=scalar["quartics"]
    p=scalar["inputs"]
    l1,l2,l3,l4,l5=[float(q["lambda"+str(j)]) for j in range(1,6)]
    k1,k2,k12,lc=[float(p[k]) for k in ("k1","k2","k12","lambda_c")]
    neutral=(l1>=0 and l2>=0 and
             l3+math.sqrt(max(0.,l1*l2))>=0 and
             l3+l4-abs(l5)+math.sqrt(max(0.,l1*l2))>=0)
    margin=k1*k2-k12*k12
    singlet_cross_psd=(k1>=0 and k2>=0 and margin>=0 and lc>=0)
    return {
        "lambda1":l1,"lambda2":l2,
        "neutral_2HDM_BFB":bool(neutral),
        "singlet_cross_PSD_sufficient":bool(singlet_cross_psd),
        "singlet_cross_PSD_determinant":margin,
        "alternative_global_quartic_BFB_sufficient":
            bool(neutral and singlet_cross_psd),
        "negative_lambda1_proves_unbounded_quartic":bool(l1<0),
        "this_is_not_global_vev_vacuum_or_charge_breaking_test":True,
    }


def evaluate(source,point,*,mH1=None,mH2=None,beta=None,k12=None):
    region=source["benchmarks"][point]
    inputs=build_inputs(region,mH1=mH1,mH2=mH2,beta=beta,k12=k12)
    s=scalar_benchmark(**inputs)
    w=scalar_width_inventory(**inputs)
    masses=s["rebuilt_charged_masses_GeV"]
    if not all(math.isclose(a,b,rel_tol=5e-10,abs_tol=1e-5)
               for a,b in zip(masses,[inputs["mH1"],inputs["mH2"]])):
        raise AssertionError("Scalar mass reconstruction failed")
    neutral=s["rebuilt_neutral_masses_GeV"]
    if not all(math.isclose(a,b,rel_tol=5e-10,abs_tol=1e-5)
               for a,b in zip(neutral,sorted([inputs["mh1"],inputs["mh2"]]))):
        raise AssertionError("Neutral scalar mass closure failed")
    sf=w["conditional_fractions_included_channels_only"]
    alternative=less_conservative_analytic_bfb(s)
    return {
        "status":STATUS,
        "source_paper":source["source"],
        "source_benchmark_region":point,
        "input_choice":"USER_SELECTED" if any(z is not None for z in
                       (mH1,mH2,beta,k12)) else "MASS_MIDPOINTS_BETA_EQUALS_ALPHA_ASSUMED",
        "source_k12_value":float(region["k12"]),
        "k12_source_overridden_for_softly_broken_Z2":bool(k12 is not None),
        "source_Table2_exact_scalar_parameters_used":bool(k12 is None),
        "family_Z2_exact_quartics_operator_audit":bool(inputs["k12"]==0),
        "family_Z2_neutrino_LFV_fitted":False,
        "inputs":inputs,
        "mass_eigenvalue_closure":"PASS",
        "scalar_sufficient_BFB":s["sufficient_global_quartic_BFB"],
        "alternative_analytic_quartic_BFB":alternative,
        "scalar_tree_unitarity":s["tree_unitarity_pass"],
        "scalar_max_unitarity_eigenvalue":s["max_abs_unitarity_eigenvalue"],
        "physical_Zee_allowed":None,
        "paper_exact_benchmark_reproduced":False,
        "full_constraints_NOT_COMPUTED":[
            "charge-breaking global vacuum","HiggsTools 2026",
            "modern two-state b->s gamma","full general Zee lepton fit",
            "complete widths","HL-LHC signal/background analysis"],
        "scalar_diagnostics":s,
        "conditional_included_channel_BR_H2_H1Z":sf["H2"]["H1_Z"],
        "conditional_included_channel_BR_H1_tb":sf["H1"]["tb"],
        "width_diagnostics":w,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--benchmark",choices=("P1","P2","P3","P4"),
                    default="P2")
    ap.add_argument("--mH1",type=float)
    ap.add_argument("--mH2",type=float)
    ap.add_argument("--beta",type=float)
    ap.add_argument("--k12",type=float,help="Override the published singlet hard Z2-breaking quartic. --k12 0 defines a NEW symmetry-compatible scalar POINT, not the published Table 2 P2.")
    ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args()
    source=load_regions()
    result=evaluate(source,a.benchmark,mH1=a.mH1,mH2=a.mH2,
                    beta=a.beta,k12=a.k12)
    if a.output.exists():
        raise FileExistsError("Use new output file to preserve provenance")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("STATUS",STATUS)
    print("SOURCE",a.benchmark)
    print("CHOSEN_INPUTS",json.dumps(result["inputs"],sort_keys=True))
    print("K12_SOURCE_OVERRIDDEN",result["k12_source_overridden_for_softly_broken_Z2"])
    print("MASS_RECONSTRUCTION",result["mass_eigenvalue_closure"])
    print("OLD_STRONGER_SUFFICIENT_BFB",result["scalar_sufficient_BFB"])
    print("ALTERNATIVE_ANALYTIC_BFB_SUFFICIENT",
          result["alternative_analytic_quartic_BFB"][
              "alternative_global_quartic_BFB_sufficient"])
    print("LAMBDA1",result["alternative_analytic_quartic_BFB"]["lambda1"])
    print("TREE_UNITARITY",result["scalar_tree_unitarity"])
    print("MAX_UNITARITY_EIGENVALUE",
          result["scalar_max_unitarity_eigenvalue"])
    print("BR_H2_H1Z_INCLUDED_ONLY",
          result["conditional_included_channel_BR_H2_H1Z"])
    print("BR_H1_tb_INCLUDED_ONLY",
          result["conditional_included_channel_BR_H1_tb"])
    print("HISTORICAL_ALLOWED_REPRODUCED False")
    print("OUTPUT",a.output)

if __name__=="__main__":main()
