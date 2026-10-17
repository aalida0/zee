#!/usr/bin/env python3
"""Gate 6: tree-level Zee-type scalar-sector mass/BFB/unitarity screen.

Source: arXiv:2106.08332, eqs. (16),(21),(22),(35),(40),(55),(82), App. C.
NOT a full Zee UFO, not a certified physical benchmark.
"""
import argparse
import json
import math
from pathlib import Path
import numpy as np

def benchmark(beta=1.394, mH1=300., mH2=700., *,
              alpha=1.398, gamma=1.089, m12sq=57700.,
              mh1=125., mh2=580.7, ma=633.7,
              lc=4.473, k1=1.082, k2=.00398, k12=-.001266,
              v=246.21965):
    """Reconstruct Zee scalar potential for arbitrary physical inputs.

    Defaults preserve the original Gate 6 published-inspired benchmark.
    BFB is sufficient (not necessary); global minimum is NOT established.
    """
    vals=(beta,mH1,mH2,alpha,gamma,m12sq,mh1,mh2,ma,lc,k1,k2,k12,v)
    if not all(math.isfinite(z) for z in vals):
        raise ValueError("Nonfinite scalar input")
    if not (0.01<beta<math.pi/2-0.01 and
            0.0<gamma<math.pi/2 and
            0.<mh1<=mh2 and 0.<ma and
            0.<mH1<=mH2 and v>0):
        raise ValueError("Invalid scalar spectrum or mixing input")
    sa,ca=math.sin(alpha),math.cos(alpha)
    sb,cb=math.sin(beta),math.cos(beta)
    sg,cg=math.sin(gamma),math.cos(gamma)
    vv=v*v; soft=m12sq/(sb*cb)
    md=mH1*mH1*cg*cg+mH2*mH2*sg*sg
    Mn11=mh1*mh1*ca*ca+mh2*mh2*sa*sa
    Mn22=mh1*mh1*sa*sa+mh2*mh2*ca*ca
    Mn12=(mh1*mh1-mh2*mh2)*sa*ca
    l1=(Mn11-m12sq*sb/cb)/(vv*cb*cb)
    l2=(Mn22-m12sq*cb/sb)/(vv*sb*sb)
    l5=(soft-ma*ma)/vv
    l4=2*(soft-md)/vv-l5
    l3=(Mn12+m12sq)/(vv*sb*cb)-l4-l5
    mu4=-math.sqrt(2)/v*(mH1*mH1-mH2*mH2)*cg*sg
    mc2=(mH1*mH1*sg*sg+mH2*mH2*cg*cg
         -.5*vv*(k1*cb*cb+k2*sb*sb-2*k12*sb*cb))
    neutral=np.array([[m12sq*sb/cb+vv*cb*cb*l1,
                       -m12sq+(l3+l4+l5)*vv*sb*cb],
                      [-m12sq+(l3+l4+l5)*vv*sb*cb,
                       m12sq*cb/sb+vv*sb*sb*l2]])
    charged=np.array([[md,-mu4*v/math.sqrt(2)],
                      [-mu4*v/math.sqrt(2),
                       mc2+.5*vv*(k1*cb*cb+k2*sb*sb-2*k12*sb*cb)]])
    nn=np.linalg.eigvalsh(neutral)
    cc=np.linalg.eigvalsh(charged)
    bfb_neutral=(l1>=0 and l2>=0 and lc>=0 and l3+math.sqrt(max(0,l1*l2))>=0
       and l3+l4-abs(l5)+math.sqrt(max(0,l1*l2))>=0)
    # Proven sufficient global quartic bound for all doublet/singlet configurations:
    # |Phi1†Phi2| <= sqrt(x1 x2),  2 sqrt(x1 x2) <= x1+x2.
    lower=[l3+min(0.,l4-abs(l5)),k1-abs(k12),k2-abs(k12)]
    bfb_sufficient=bfb_neutral and all(z>=0 for z in lower)
    # Appendix C (C1)-(C3): three 6x6 scattering sectors.
    C=l3+l4
    matrices={}
    matrices["Q2Y1"]=[
        [l1,0,0,l5,0,0],[0,C,0,0,0,0],[0,0,k1,0,-k12,0],
        [l5,0,0,l2,0,0],[0,0,-k12,0,k2,0],[0,0,0,0,0,2*lc]]
    matrices["Q1Y1"]=[
        [l1,0,0,l5,0,0],[0,l3,l4,0,0,0],[0,l4,l3,0,0,0],
        [l5,0,0,l2,0,0],[0,0,0,0,k1,-k12],[0,0,0,0,-k12,k2]]
    matrices["Q1Y0"]=[
        [l1,0,0,l4,0,0],[0,l3,l5,0,0,0],[0,l5,l3,0,0,0],
        [l4,0,0,l2,0,0],[0,0,0,0,k1,-k12],[0,0,0,0,-k12,k2]]
    # Appendix C (C5): 13x13 Q0Y0 sector.
    a,b,c,d,e=l1,l2,l3,l4,l5
    h=k12;j=k2;k=k1
    matrices["Q0Y0"]=[
        [2*a,0,0,0,C,0,0,0,k,a,0,0,c],
        [0,2*e,0,C,0,0,0,0,-h,0,e,d,0],
        [0,0,0,0,0,0,k,-h,0,0,0,0,0],
        [0,C,0,2*e,0,0,0,0,-h,0,d,e,0],
        [C,0,0,0,2*b,0,0,0,j,c,0,0,b],
        [0,0,0,0,0,0,-h,j,0,0,0,0,0],
        [0,0,k,0,0,-h,0,0,0,0,0,0,0],
        [0,0,-h,0,0,j,0,0,0,0,0,0,0],
        [k,-h,0,-h,j,0,0,0,4*lc,k,-h,-h,j],
        [a,0,0,0,c,0,0,0,k,2*a,0,0,C],
        [0,e,0,d,0,0,0,0,-h,0,2*e,C,0],
        [0,d,0,e,0,0,0,0,-h,0,C,2*e,0],
        [c,0,0,0,b,0,0,0,j,C,0,0,2*b]]
    spectra={}
    for name,m in matrices.items():
        m=np.asarray(m,float)
        if not np.allclose(m,m.T): raise RuntimeError("Non-symmetric "+name)
        spectra[name]=np.linalg.eigvalsh(m).tolist()
    maxeig=max(abs(w) for E in spectra.values() for w in E)
    return {
        "status":"TREE_SCALAR_SECTOR_SCREEN_NOT_FULL_ZEE_BENCHMARK",
        "inputs":{"mh1":mh1,"mh2":mh2,"ma":ma,"mH1":mH1,"mH2":mH2,
          "alpha":alpha,"beta":beta,"gamma":gamma,"m12sq":m12sq,
          "lambda_c":lc,"k1":k1,"k2":k2,"k12":k12,"v":v},
        "tanbeta":sb/cb,
        "quartics":{"lambda1":l1,"lambda2":l2,"lambda3":l3,
                    "lambda4":l4,"lambda5":l5},
        "mu4_GeV":mu4,"mc2_GeV2":mc2,
        "rebuilt_neutral_masses_GeV":np.sqrt(nn).tolist(),
        "rebuilt_charged_masses_GeV":np.sqrt(cc).tolist(),
        "reconstructed_pseudoscalar_mass_GeV":math.sqrt(soft-l5*vv),
        "necessary_neutral_BFB":bool(bfb_neutral),
        "lower_bound_cross_coefficients":lower,
        "sufficient_global_quartic_BFB":bool(bfb_sufficient),
        "unitarity_eigenvalues":spectra,
        "max_abs_unitarity_eigenvalue":maxeig,
        "max_eigenvalue_allowed_8pi":8*math.pi,
        "tree_unitarity_pass":bool(maxeig<8*math.pi),
        "missing":["charged breaking global vacuum","EW precision S T U",
                   "Higgs searches","B to X_s gamma","neutrinos and LFV",
                   "full gauge-invariant Zee UFO and full widths"]
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--beta",type=float,default=1.394)
    a.add_argument("--mH1",type=float,default=300.)
    a.add_argument("--mH2",type=float,default=700.)
    a.add_argument("--output",type=Path)
    x=a.parse_args()
    data=json.dumps(benchmark(x.beta,x.mH1,x.mH2),indent=2)+"\n"
    print(data,end="")
    if x.output:
        x.output.parent.mkdir(parents=True,exist_ok=True)
        x.output.write_text(data)

if __name__=="__main__":main()
