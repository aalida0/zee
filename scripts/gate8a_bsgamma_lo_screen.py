#!/usr/bin/env python3
"""Gate 8A: two-charged-scalar LO b->s gamma Wilson matching screen.

Uses standard Type-II charged-Higgs LO loop functions F7/F8^(1,2),
and Florentino, Romao, Silva EPJC 81 (2021) 1148, Eq (B.9), (C.12):
the contributions of two charged states add with doublet fractions
cos^2(gamma) (light) and sin^2(gamma) (heavy).

THIS IS NOT BR(B->Xs gamma). It excludes NLO/NNLO matching, QCD RG
running, the full SM+BSM interference, theoretical uncertainties,
experimental covariance and valid exclusion/allowed status.
See https://doi.org/10.1140/epjc/s10052-021-09956-2, Appendix C.
Charged Higgs LO F7,F8 formulas also in hep-ph/0009337, Eqs 5-8.
"""
import argparse
import json
import math
from pathlib import Path

from gate6_benchmark import benchmark


def loop_functions(y:float):
    if not math.isfinite(y) or y<=0:
        raise ValueError("Require finite y=m_t^2/m_H^2 > 0")
    if abs(y-1.)<1e-4:
        raise ValueError("Near y=1: numerical cancellation. Implement Taylor limit before using.")
    log=math.log(y)
    u=y-1.
    f7a=(y*(7.-5.*y-8.*y*y)/(24.*u**3)
         +y*y*(3.*y-2.)*log/(4.*u**4))
    f7b=(y*(3.-5.*y)/(12.*u*u)
         +y*(3.*y-2.)*log/(6.*u**3))
    f8a=(y*(2.+5.*y-y*y)/(8.*u**3)
         -3.*y*y*log/(4.*u**4))
    f8b=(y*(3.-y)/(4.*u*u)
         -y*log/(2.*u**3))
    return {"F7_1":f7a,"F7_2":f7b,"F8_1":f8a,"F8_2":f8b}


def typeii_charged_lo(mass:float,tanbeta:float,mt:float):
    if mass<=0 or tanbeta<=0 or mt<=0:
        raise ValueError("Masses and tanbeta must be positive")
    y=(mt/mass)**2
    f=loop_functions(y)
    cot2=tanbeta**-2
    return {"C7":cot2/3.*f["F7_1"]+f["F7_2"],
            "C8":cot2/3.*f["F8_1"]+f["F8_2"],
            "y":y,**f}


def screen(beta=1.394,gamma=1.089,mH1=300.,mH2=700.,mt=172.,
           reference_mass=580.):
    if mH1>=mH2:
        raise ValueError("Convention requires mH1 < mH2")
    tanbeta=math.tan(beta)
    if tanbeta<=0:
        raise ValueError("Require beta in first quadrant for Type-II")
    w1=math.cos(gamma)**2
    w2=math.sin(gamma)**2
    light=typeii_charged_lo(mH1,tanbeta,mt)
    heavy=typeii_charged_lo(mH2,tanbeta,mt)
    ref=typeii_charged_lo(reference_mass,tanbeta,mt)
    combined={k:w1*light[k]+w2*heavy[k] for k in ("C7","C8")}
    ratios={k:combined[k]/ref[k] if abs(ref[k])>1e-15 else None
            for k in combined}
    effective_inverse_square=(w1/mH1**2+w2/mH2**2)**(-.5)
    return {
        "status":"LO_B_TO_S_GAMMA_MATCHING_SCREEN_NOT_BR_OR_EXCLUSION",
        "inputs":{"beta":beta,"tanbeta":tanbeta,"gamma":gamma,
                  "mH1_GeV":mH1,"mH2_GeV":mH2,"mt_input_GeV":mt,
                  "reference_TypeII_single_Hmass_GeV":reference_mass},
        "mixing_weight_light_cos2gamma":w1,
        "mixing_weight_heavy_sin2gamma":w2,
        "mixing_unitarity_sum":w1+w2,
        "individual_TypeII_LO_matching":{"light":light,"heavy":heavy},
        "combined_LO_charged_scalar":{"DeltaC7":combined["C7"],
                                      "DeltaC8":combined["C8"]},
        "reference_single_charged_scalar_TypeII":{
           "DeltaC7":ref["C7"],"DeltaC8":ref["C8"]},
        "combined_over_reference_LO":{
           "DeltaC7":ratios["C7"],"DeltaC8":ratios["C8"]},
        "inverse_mass_squared_proxy_GeV":effective_inverse_square,
        "warnings":[
           "LO Wilson coefficients at electroweak matching only; NOT an observable BR.",
           "Using fixed mt input, not a fully run MS-bar m_t(muW); perturbative-scheme choices affect results.",
           "The historical 580 GeV single-state Type-II bound is NOT an exclusion test for a mixed Zee pair.",
           "A physical bound requires NLO/NNLO, RG evolution, SM+BSM interference and up-to-date HFLAV inputs.",
           "No neutrino/LFV fit or oblique/Higgs search checks have been done."
        ]
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--beta",type=float,default=1.394)
    p.add_argument("--gamma",type=float,default=1.089)
    p.add_argument("--mH1",type=float,default=300.)
    p.add_argument("--mH2",type=float,default=700.)
    p.add_argument("--mt",type=float,default=172.)
    p.add_argument("--reference-mass",type=float,default=580.)
    p.add_argument("--output",type=Path,default=Path("work/gate8a_bsgamma_lo_screen.json"))
    a=p.parse_args()
    x=screen(a.beta,a.gamma,a.mH1,a.mH2,a.mt,a.reference_mass)
    blob=json.dumps(x,indent=2)+"\n"
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(blob)
    print(blob,end="")
    print("OUTPUT:",a.output)
    print("NO PASS/FAIL of B->Xs gamma: this is only LO matching.")


if __name__=="__main__":
    main()
