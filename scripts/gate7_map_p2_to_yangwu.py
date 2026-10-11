#!/usr/bin/env python3
"""Map Gate-6 Florentino scalar benchmark to Yang/Wu Zee Higgs-basis UFO.

Tree-level scalar potential mapping only. Source Yang/Wu: ZEE.fr,
Lagrangian.fr, Parameters.fr; Florentino et al. arXiv:2106.08332 Eq(16).
The resulting parameters DO NOT certify a complete Zee neutrino/LFV model.
"""
import argparse
import json
import math
from pathlib import Path

from gate6_benchmark import benchmark

def map_point(beta=1.394,mH1=300.,mH2=700.):
    g=benchmark(beta,mH1,mH2)
    z=g["inputs"]; l=g["quartics"]
    a,b,c,d,e=(l[f"lambda{i}"] for i in range(1,6))
    s=math.sin(beta); co=math.cos(beta)
    t=s*co
    l345=c+d+e
    delta=(a+b-2*l345)*s*s*co*co
    Z1=a*co**4+b*s**4+2*l345*s*s*co*co
    Z2=a*s**4+b*co**4+2*l345*s*s*co*co
    Z3=c+delta
    Z4=d+delta
    Z5=e+delta
    Z6=-t*(a*co*co-b*s*s-l345*(co*co-s*s))
    Z7=-t*(a*s*s-b*co*co+l345*(co*co-s*s))
    k1=z["k1"];k2=z["k2"];k12=z["k12"]
    K1=k1*co*co+k2*s*s-2*k12*t
    K2=k1*s*s+k2*co*co+2*k12*t
    K12=(k2-k1)*t-k12*(co*co-s*s)
    phi=math.pi/2-z["gamma"]
    diff=z["alpha"]-beta

    # Independent paper-vs-Yang/Wu mass-basis identities:
    v=z["v"];v2=v*v
    target_Z1=(z["mh1"]**2*math.cos(diff)**2+z["mh2"]**2*math.sin(diff)**2)/v2
    target_Z5=(-z["ma"]**2+z["mh2"]**2*math.cos(diff)**2+z["mh1"]**2*math.sin(diff)**2)/v2
    Md2=mH2*mH2*math.cos(phi)**2+mH1*mH1*math.sin(phi)**2
    target_Z4=(z["ma"]**2+z["mh2"]**2*math.cos(diff)**2+
               z["mh1"]**2*math.sin(diff)**2-2*Md2)/v2
    target_Z6=(z["mh1"]**2-z["mh2"]**2)*math.sin(diff)*math.cos(diff)/v2
    closure={
        "Z1":Z1-target_Z1,
        "Z4":Z4-target_Z4,
        "Z5":Z5-target_Z5,
        "Z6":Z6-target_Z6,
        "muzee_GeV":(math.sqrt(2)*(mH2*mH2-mH1*mH1)*
                  math.cos(phi)*math.sin(phi)/v)-g["mu4_GeV"],
    }
    if max(abs(value) for value in closure.values()) > 1e-8:
        raise RuntimeError("Scalar mass/potential mapping did not close: "+repr(closure))
    # Higgs-basis full scalar singlet quartics:
    # k1 |Phi1|^2 + k2 |Phi2|^2 - k12(Phi1†Phi2+h.c.)
    #    = K1|Hv|^2+K2|HH|^2+K12(Hv†HH+h.c.)
    out={
        "status":"TREE_LEVEL_YANG_WU_SCALAR_PARAMETER_MAP_NOT_EXPERIMENTAL_VALIDATION",
        "input_Gate6":z,
        "charged_field_mapping":"Yang H+ (PDG 227) = - Florentino H2+; Yang h+ (PDG 228) = Florentino H1+",
        "map":{
          "ZEEINPUTS":{1:beta,2:z["alpha"],3:diff,4:phi},
          "ZEELAMS":{1:Z2,2:Z3,3:Z7,4:K1,5:K2,6:K12,7:z["lambda_c"]},
          "MASS":{25:z["mh1"],225:z["mh2"],226:z["ma"],227:mH2,228:mH1},
        },
        "internal_higgs_basis_quartics":{"lambda1":Z1,"lambda4":Z4,
            "lambda5":Z5,"lambda6":Z6},
        "closure_mass_basis_residuals":closure,
        "explicit_absences":[
           "Gauge/Ward and UFO numerical vertex checks",
           "Flavor and EW precision constraints",
           "Full Zee neutrino/LFV calibration and total charged-Higgs widths",
           "NLO UV and R2 counterterms",
        ],
    }
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--beta",type=float,default=1.394)
    ap.add_argument("--mH1",type=float,default=300.)
    ap.add_argument("--mH2",type=float,default=700.)
    ap.add_argument("--output",type=Path,default=Path("work/gate7_yangwu_p2_mapping.json"))
    a=ap.parse_args()
    result=map_point(a.beta,a.mH1,a.mH2)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    txt=json.dumps(result,indent=2)+"\n"
    a.output.write_text(txt)
    print(txt,end="")
    print("Wrote:",a.output)
    print("NOT an MG5 parameter card; not a complete physical Zee point.")


if __name__=="__main__":
    main()
