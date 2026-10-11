#!/usr/bin/env python3
"""Gate A1G: Zee scalar-sector oblique T and literature coefficient audit.

MAIN REFERENCE: Grimus, Lavoura, Ogreid and Osland, arXiv:0802.4353
Eq.(28) (or arXiv:0711.4022 Eq.(48)), based on gauge boson
self-energies for arbitrary scalar doublets and charged singlets.
The off-diagonal charged-scalar contribution is -2 |(Udag U)_12|² F.

ALTERNATIVE DOCUMENTED: Herrero-Garcia et al., arXiv:1701.05345,
Appendix A Eq.(A.1), has -1/2 and explicitly notes -2 in Ref.[129].
The script reports both; physically preferred is the general result.

This IS NOT a full correlated S,T,U fit. No S or U implemented.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

MH_SM=125.0
MH_HEAVY=580.7
MA=633.7
MH1_CHARGED=300.0
MH2_CHARGED=700.0
ALPHA=1.398
BETA=1.394
GAMMA=1.089
MW=80.379
MZ=91.1876

def F_squared(x,y):
    """Symmetric F(x,y) in GeV², where x,y are MASS-SQUARED in GeV².

    F=(x+y)/2 - xy/(x-y)*log(x/y). Small-splitting series prevents
    catastrophic cancellation in decoupling and custodial-limit tests.
    """
    x=float(x); y=float(y)
    if x<=0 or y<=0:
        raise ValueError("Mass squared values must be strictly positive")
    if x==y:
        return 0.
    if x<y:
        x,y=y,x
    u=(x-y)/y
    if u<1e-3:
        # log1p expansion to O(u^7), enough for u<.001.
        return float(y*(u**2/6-u**3/12+u**4/20-u**5/30
                        +u**6/42-u**7/56))
    return float((x+y)/2-(x*y/(x-y))*np.log(x/y))

def F(m1,m2):
    """Physical mass wrapper for F_squared."""
    return F_squared(float(m1)**2,float(m2)**2)

def charged_doublet_overlap(beta=BETA,gamma=GAMMA):
    """Florentino arXiv:2106.08332 Eq.(24), physical charged UdagU.

    Columns: Goldstone, charged H1, charged H2; rows: two doublets.
    U is 2x3, so U^dag U contains the charge-changing Z coupling.
    """
    cb,sb=np.cos(beta),np.sin(beta)
    cg,sg=np.cos(gamma),np.sin(gamma)
    U=np.array([[cb,-sb*cg,sb*sg],
                [sb,cb*cg,-cb*sg]],float)
    return U.T@U

def T_terms(*,mh=MH_SM,mH=MH_HEAVY,mA=MA,
            m1=MH1_CHARGED,m2=MH2_CHARGED,
            alpha=ALPHA,beta=BETA,gamma=GAMMA,
            mW=MW,mZ=MZ,charged_pair_coefficient=2.):
    """Contributions to numerator of alpha_em*T in GeV².

    Florentino convention h125 gauge strength = cos(beta-alpha).
    Herrero-Garcia conventional notation uses sin(beta-alpha) for
    the SM-like Higgs, so the angle complements are exchanged.

    Grimus off-diagonal term: -2*sin²gamma*cos²gamma*F(m1,m2).
    Herrero alternative: -0.5*sin²gamma*cos²gamma*F(m1,m2).
    """
    c2g=np.cos(gamma)**2
    s2g=np.sin(gamma)**2
    aligned_h=np.cos(beta-alpha)**2
    misaligned_h=np.sin(beta-alpha)**2
    return {
        "charged1_neutral":float(c2g*(
            misaligned_h*F(m1,mh)+aligned_h*F(m1,mH)+F(m1,mA))),
        "charged2_neutral":float(s2g*(
            misaligned_h*F(m2,mh)+aligned_h*F(m2,mH)+F(m2,mA))),
        "offdiagonal_charged_pair":float(
            -charged_pair_coefficient*c2g*s2g*F(m1,m2)),
        "neutral_pair":float(-misaligned_h*F(mh,mA)
                             -aligned_h*F(mH,mA)),
        "SM_reference_subtraction":float(3*misaligned_h*(
            F(mZ,mH)-F(mW,mH)-F(mZ,mh)+F(mW,mh))),
    }

def oblique_T(*,coefficient=2.,mW=MW,mZ=MZ,**kwargs):
    """T using on-shell sW² = 1-MW²/MZ² for consistent normalization.

    Same denominator as Grimus g²/(64*pi²*alpha*MW²)
    = 1/(16*pi*sW²*MW²). Inputs are screening-level EW values.
    """
    sw2=1-(mW/mZ)**2
    if not 0<sw2<1:
        raise ValueError("Invalid electroweak input values")
    terms=T_terms(mW=mW,mZ=mZ,charged_pair_coefficient=coefficient,
                  **kwargs)
    total=sum(terms.values())
    return float(total/(16*np.pi*sw2*mW*mW)),terms

def report():
    T_general,parts=oblique_T(coefficient=2.)
    T_herrero,altparts=oblique_T(coefficient=.5)
    matrix=charged_doublet_overlap()
    offdiag=matrix[1,2]
    sw2=1-(MW/MZ)**2
    return {
        "status":"GRIMUS_T_CONVENTION_RESOLVED_SCREEN_NOT_CORRELATED_STU_PASS",
        "scalar_benchmark":{
            "mh125_GeV":MH_SM,"mH_GeV":MH_HEAVY,"mA_GeV":MA,
            "mH1_charged_GeV":MH1_CHARGED,"mH2_charged_GeV":MH2_CHARGED,
            "alpha_rad":ALPHA,"beta_rad":BETA,"gamma_rad":GAMMA,
        },
        "EW_inputs":{"MW_GeV":MW,"MZ_GeV":MZ,
                     "sin2_thetaW_onshell":sw2},
        "overlap_UdagU":matrix.tolist(),
        "charged_pair_overlap_squared":float(abs(offdiag)**2),
        "preferred_general_Grimus_T":T_general,
        "preferred_Grimus_numerator_components_GeV2":parts,
        "alternative_Herrero2017_T_not_recommended":T_herrero,
        "alternative_Herrero_numerator_components_GeV2":altparts,
        "T_convention_difference":T_herrero-T_general,
        "literature":[
            "arXiv:0802.4353 Eq.(28) or 0711.4022 Eq.(48): -2 mixing-overlap squared",
            "arXiv:1701.05345 App.A Eq.(A.1): -1/2, footnote 13 notes -2 in Grimus",
            "arXiv:2106.08332 Eqs.(21),(24),(27)-(28): Zee mixing conventions",
        ],
        "uncomputed":[
            "S and U at q²=mZ²/mW² and their scheme-aligned definitions",
            "correlated experimental S,T,U fit and likelihood",
            "B->Xs gamma with two mixed charged Higgs bosons",
            "HiggsBounds/HiggsSignals, scalar vacuum global minimum",
            "global LFV including Barr-Zee and full physical collider rate",
        ],
        "interpretation":(
            "T alone is not a global EWPO pass; do not exclude or accept "
            "this benchmark until S/U and correlated fit are evaluated."
        ),
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    r=report()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(r,indent=2)+"\n")
        print("Wrote",args.output)
    print(f"Grimus Eq.(28) T = {r['preferred_general_Grimus_T']:.9f}")
    print(f"Herrero Appendix A T (disputed) = "
          f"{r['alternative_Herrero2017_T_not_recommended']:.9f}")
    print(f"Difference = {r['T_convention_difference']:.9f}")
    print("STATUS:",r["status"])
    assert abs(r["preferred_general_Grimus_T"])<.01
    assert r["T_convention_difference"]>.3

if __name__=="__main__":
    main()
