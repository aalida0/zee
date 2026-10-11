#!/usr/bin/env python3
"""Gate A1D: neutral-scalar tree-level tau->3mu and tau->e mu mu ONLY.

References: Chen arXiv:2508.18757 Eq.(4), Table I;
Herrero-Garcia et al arXiv:1701.05345 Eqs.(3.8)-(3.9);
Florentino et al arXiv:2106.08332 Eqs.(21),(27)-(28).
No dipole, box, QED corrections or full Zee LFV/global fitness claim.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from gateA1b_hierarchical_no_seed import (
    ML, target_neutrino_matrix, antisymmetric_f_with_null_condition,
    solve_lepton_yukawa
)

GF=1.1663787e-5
VEV=246.21965
MH=125.0
MHEAVY=580.7
MA=633.7
ALPHA=1.398
BETA=1.394
BR_MUNUNU=0.1739
BR_ENUNU=0.1782

def scalar_couplings(Y, *, mh=MH, mH=MHEAVY, mA=MA,
                     alpha=ALPHA, beta=BETA):
    """Matrices C in L=-S bar(ell)_i [C_ij P_L+C_ji* P_R] ell_j.

    Chen's Y^ell already absorbs sqrt(2); DO NOT insert another factor.
    Florentino: h125=cos(delta) H1 - sin(delta) H2,
    Hheavy=sin(delta) H1 + cos(delta) H2, delta=beta-alpha.
    """
    Y=np.asarray(Y,complex)
    if Y.shape!=(3,3):
        raise ValueError("Y must be 3x3")
    d=beta-alpha
    sm=ML/VEV
    return (
        (np.cos(d)*sm-np.sin(d)*Y, float(mh)),
        (np.sin(d)*sm+np.cos(d)*Y, float(mH)),
        (1j*Y, float(mA)),
    )

def wilson(Y, *, daughter, mh=MH, mH=MHEAVY, mA=MA,
           alpha=ALPHA, beta=BETA):
    """Coherent neutral-scalar Wilson coefficients of Herrero Eq.(3.8).

    daughter: 1 (mu) for tau->3mu; 0 (e) for tau->e mu mu.
    spectator lepton pair is always mu+mu-; tau index is 2.
    """
    if daughter not in (0,1):
        raise ValueError("daughter must be e=0 or mu=1")
    D={x:0j for x in ("LL","RR","LR","RL")}
    for C,m in scalar_couplings(Y,mh=mh,mH=mH,mA=mA,
                                 alpha=alpha,beta=beta):
        left=C[daughter,2]
        right=np.conj(C[2,daughter])
        muL=C[1,1]
        muR=np.conj(muL)
        fac=-0.5/m**2
        D["LL"]+=fac*left*muL
        D["RR"]+=fac*right*muR
        D["LR"]+=fac*left*muR
        D["RL"]+=fac*right*muL
    return D

def tau_tree_br(Y, *, daughter, mh=MH, mH=MHEAVY, mA=MA,
                alpha=ALPHA, beta=BETA):
    """Neutral-tree scalar-exchange contribution, massless final leptons.

    Eq.(3.8): BR/BR(tau->daughter nu nu)=
        [xi(|DLL|²+|DRR|²)+|DLR|²+|DRL|²]/(32 GF²)
    xi=1/2 for tau->3mu (two identical mu-), else xi=1.
    """
    if daughter not in (0,1):
        raise ValueError("daughter must be e=0 or mu=1")
    D=wilson(Y,daughter=daughter,mh=mh,mH=mH,mA=mA,
             alpha=alpha,beta=beta)
    xi=.5 if daughter==1 else 1.
    norm=BR_MUNUNU if daughter==1 else BR_ENUNU
    return float(norm/(32*GF**2)*(
        xi*(abs(D["LL"])**2+abs(D["RR"])**2)
        +abs(D["LR"])**2+abs(D["RL"])**2
    )),D

def chen_tableI_NO():
    """Only the tree-relevant Table I printed entries (NO) from Chen 2025."""
    Y=np.zeros((3,3),complex)
    Y[1,1]=-.118
    Y[2,0]=(7.69-1.64j)*1e-4
    Y[2,1]=7.37e-4
    Y[2,2]=7.98e-5
    return Y

def complex_json(x):
    return {"re":float(np.real(x)),"im":float(np.imag(x))}

def report():
    # Table I uses mH=150, mA=200 GeV, aligned h; these scalar masses
    # are NOT the project's 580.7/633.7 GeV candidate.
    ref=chen_tableI_NO()
    reproduced={}
    for label,daughter,target in (
        ("tau_to_3mu",1,3.9e-10),
        ("tau_to_e_mumu",0,4.7e-10),
    ):
        br,_=tau_tree_br(ref,daughter=daughter,mH=150,mA=200,alpha=0,beta=0)
        reproduced[label]={
            "chen_2025_tableI_published_BR":target,
            "computed_from_printed_inputs":br,
            "relative_difference":(br-target)/target,
            "printed_precision_reproduction_within_5pct":abs(br-target)<.05*target,
        }
    M,_=target_neutrino_matrix()
    f,_=antisymmetric_f_with_null_condition(M)
    Y,rank,_=solve_lepton_yukawa(f,M)
    candidate={}
    for label,daughter,exp in (
        ("tau_to_3mu",1,1.9e-8),
        ("tau_to_e_mumu",0,2.7e-8),
    ):
        br,D=tau_tree_br(Y,daughter=daughter)
        candidate[label]={
            "neutral_tree_only_BR_NOT_total":br,
            "90pct_CL_experimental_limit":exp,
            "neutral_tree_component_over_limit_NOT_a_full_pass":br/exp,
            "chiral_coefficients_GeV_minus2":{k:complex_json(v) for k,v in D.items()},
        }
    return {
        "status":"NEUTRAL_TREE_ONLY_NOT_FULL_LFV_RATE_OR_GLOBAL_ZEE_FIT",
        "sources":[
            "Chen arXiv:2508.18757 Eqs.(4),(5) Table I",
            "Herrero et al arXiv:1701.05345 Eqs.(3.8)-(3.9)",
            "Florentino et al arXiv:2106.08332 Eqs.(21),(27)-(28)",
        ],
        "published_benchmark":reproduced,
        "candidate_neutral_tree_only":candidate,
        "candidate_scalar_masses_GeV":{"h":MH,"H":MHEAVY,"A":MA},
        "alpha_rad":ALPHA,"beta_rad":BETA,
        "kappa_hVV_florentino":float(np.cos(BETA-ALPHA)),
        "max_abs_Y_ell":float(np.max(abs(Y))),
        "neutrino_linear_rank":int(rank),
        "not_checked":[
            "complete neutral + charged one-loop dipoles and their interference",
            "two-loop Barr-Zee diagrams with Type-II quark Yukawas",
            "dipole/box contributions and QED corrections to 3-body decays",
            "mu->3e, mu-e conversion, muonium oscillation, lepton universality",
            "full scalar EW/Higgs/B->Xs gamma/physical-width global fit",
        ],
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
    for k,x in r["published_benchmark"].items():
        print(f"Chen {k}: source={x['chen_2025_tableI_published_BR']:.4e}; "
              f"reproduced={x['computed_from_printed_inputs']:.4e}")
    for k,x in r["candidate_neutral_tree_only"].items():
        print(f"Candidate {k}: neutral-tree-only BR={x['neutral_tree_only_BR_NOT_total']:.6e}; "
              f"experimental limit={x['90pct_CL_experimental_limit']:.2e}")
    print("STATUS:",r["status"])
    assert all(x["printed_precision_reproduction_within_5pct"]
               for x in r["published_benchmark"].values())

if __name__=="__main__":
    main()
