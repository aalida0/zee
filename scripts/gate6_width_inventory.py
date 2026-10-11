#!/usr/bin/env python3
"""Gate 6 partial LO two-body Zee charged-scalar widths.

These fractions are conditional on included channels; NOT physical Zee BRs
because the independent charged-singlet neutrino/LFV Yukawas are unspecified.
"""
import argparse
import json
import math
import numpy as np
from pathlib import Path
from gate6_benchmark import benchmark

GF=1.1663787e-5
MT=172.;MB=4.7;MTAU=1.77686;MW=80.379;MZ=91.1876
G12=0.1520746183402528
ALPHA_INV=127.95
SW2=.23122

def kallen(M,m,V):
    return max(0.,(M*M-(m+V)**2)*(M*M-(m-V)**2))

def vector_width(M,m,mv,coupling):
    if M<=m+mv:return 0.
    return coupling**2*kallen(M,m,mv)**1.5/(16*math.pi*M**3*mv**2)

def scalar_width(M,m,ms,coupling):
    if M<=m+ms:return 0.
    return coupling**2*math.sqrt(kallen(M,m,ms))/(16*math.pi*M**3)

def tb_width(M,tanb,doublet2):
    if M<=MT+MB:return 0.
    t,b=(MT/M)**2,(MB/M)**2
    kin=math.sqrt(max(0.,(1-t-b)**2-4*t*b))
    piece=(MT**2/tanb**2+MB**2*tanb**2)*(1-t-b)-4*MT**2*MB**2/M**2
    return max(0.,3*GF*M/(4*math.sqrt(2)*math.pi)*doublet2*kin*piece)

def tau_width(M,tanb,doublet2):
    if M<=MTAU:return 0.
    return GF*M/(4*math.sqrt(2)*math.pi)*MTAU**2*tanb**2*doublet2*(1-(MTAU/M)**2)**2

def trilinears(p):
    """Differentiate the charged 3x3 mass Hessian wrt CP-even neutral VEVs."""
    q=p["quartics"];z=p["inputs"]
    beta,alpha,gamma=z["beta"],z["alpha"],z["gamma"]
    v=z["v"];v1=v*math.cos(beta);v2=v*math.sin(beta)
    sb,cb=math.sin(beta),math.cos(beta)
    sg,cg=math.sin(gamma),math.cos(gamma)
    l1,l2,l3,l4,l5=[q["lambda"+str(i)] for i in range(1,6)]
    mu=p["mu4_GeV"]
    d1=np.array([
      [l1*v1,(l4+l5)*v2/2,0],
      [(l4+l5)*v2/2,l3*v1,-mu/math.sqrt(2)],
      [0,-mu/math.sqrt(2),z["k1"]*v1-z["k12"]*v2]])
    d2=np.array([
      [l3*v2,(l4+l5)*v1/2,mu/math.sqrt(2)],
      [(l4+l5)*v1/2,l2*v2,0],
      [mu/math.sqrt(2),0,z["k2"]*v2-z["k12"]*v1]])
    u1=np.array([-sb*cg,cb*cg,sg])
    u2=np.array([sb*sg,-cb*sg,cg])
    return {"h125":float(u1@(math.cos(alpha)*d1+math.sin(alpha)*d2)@u2),
            "hheavy":float(u1@(-math.sin(alpha)*d1+math.cos(alpha)*d2)@u2)}

def inventory(beta=1.394,mH1=300.,mH2=700.):
    p=benchmark(beta,mH1,mH2)
    x=p["inputs"]
    angle=x["beta"]-x["alpha"]
    sg,cg=math.sin(x["gamma"]),math.cos(x["gamma"])
    gw=math.sqrt(4*math.pi/(ALPHA_INV*SW2))
    tb=p["tanbeta"]
    g=trilinears(p)
    h1={
      "tb":tb_width(mH1,tb,cg*cg),
      "tau_nu_TypeII":tau_width(mH1,tb,cg*cg),
      "W_h125":vector_width(mH1,x["mh1"],MW,gw/2*cg*math.sin(angle)),
      "W_hheavy":vector_width(mH1,x["mh2"],MW,gw/2*cg*math.cos(angle)),
      "W_A":vector_width(mH1,x["ma"],MW,gw/2*cg),
    }
    h2={
      "H1_Z":vector_width(mH2,mH1,MZ,G12),
      "H1_h125":scalar_width(mH2,mH1,x["mh1"],g["h125"]),
      "H1_hheavy":scalar_width(mH2,mH1,x["mh2"],g["hheavy"]),
      "tb":tb_width(mH2,tb,sg*sg),
      "tau_nu_TypeII":tau_width(mH2,tb,sg*sg),
      "W_h125":vector_width(mH2,x["mh1"],MW,gw/2*sg*math.sin(angle)),
      "W_hheavy":vector_width(mH2,x["mh2"],MW,gw/2*sg*math.cos(angle)),
      "W_A":vector_width(mH2,x["ma"],MW,gw/2*sg),
    }
    widths={"H1":h1,"H2":h2}
    totals={k:sum(w.values()) for k,w in widths.items()}
    conditional={k:{name:value/totals[k] for name,value in w.items()}
                 for k,w in widths.items()}
    return {
      "status":"PARTIAL_LO_WIDTH_INVENTORY_NOT_PHYSICAL_ZEE_BRANCHING_RATIOS",
      "input":{"beta":beta,"mH1":mH1,"mH2":mH2,"gamma":x["gamma"]},
      "trilinear_H2_H1_h125_GeV":g["h125"],
      "g12_used":G12,
      "partial_widths_GeV":widths,
      "sum_of_included_widths_GeV":totals,
      "conditional_fractions_included_channels_only":conditional,
      "missing":["independent Zee singlet charged-lepton interactions",
                 "full neutrino/LFV-sector fit","QCD corrections to tb",
                 "additional fermionic/off-shell channels","physical total widths"],
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--beta",type=float,default=1.394)
    p.add_argument("--mH1",type=float,default=300.)
    p.add_argument("--mH2",type=float,default=700.)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    blob=json.dumps(inventory(a.beta,a.mH1,a.mH2),indent=2)+"\n"
    print(blob,end="")
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(blob)

if __name__=="__main__":main()
