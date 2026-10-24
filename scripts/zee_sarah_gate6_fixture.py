#!/usr/bin/env python3
"""Gate6 benchmark -> independent Wolfram-language mass-matrix fixture.

Run before Mathematica SARAH audit. No acceptance/exclusion decisions.
"""
from __future__ import annotations
import argparse
import math
from pathlib import Path
import numpy as np
from gate6_benchmark import benchmark

def wl(x):
    x = float(x)
    if not math.isfinite(x):
        raise ValueError("non-finite fixture")
    return f"{x:.17e}".replace("e", "*^")

def wlmatrix(rows):
    return "{" + ", ".join("{" + ", ".join(map(wl,row)) + "}" for row in rows) + "}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,default=Path("work/sarah_zee/gate6_fixture.m"))
    dest=ap.parse_args().out
    z=benchmark()
    p=z["inputs"]; q=z["quartics"]
    v=p["v"]; b=p["beta"]; alpha=p["alpha"]; ga=p["gamma"]
    c=math.cos(b); s=math.sin(b)
    v1=v*c; v2=v*s
    l345=sum(q["lambda"+str(i)] for i in (3,4,5))
    m112=p["m12sq"]*v2/v1-.5*q["lambda1"]*v1*v1-.5*l345*v2*v2
    m222=p["m12sq"]*v1/v2-.5*q["lambda2"]*v2*v2-.5*l345*v1*v1
    vals={"v1":v1,"v2":v2,"M112":m112,"M222":m222,
          "M12Sq":p["m12sq"],"MCS2":z["mc2_GeV2"],
          "Mu4":z["mu4_GeV"],"LambdaC":p["lambda_c"],
          "K1":p["k1"],"K2":p["k2"],"K12":p["k12"]}
    vals.update({"Lambda"+str(i):q["lambda"+str(i)] for i in range(1,6)})
    mh=p["mh1"]; mH=p["mh2"]; ma=p["ma"]
    mhh=np.array([[mh*mh*math.cos(alpha)**2+mH*mH*math.sin(alpha)**2,
                   (mh*mh-mH*mH)*math.sin(alpha)*math.cos(alpha)],
                  [(mh*mh-mH*mH)*math.sin(alpha)*math.cos(alpha),
                   mh*mh*math.sin(alpha)**2+mH*mH*math.cos(alpha)**2]])
    d=np.array([-s,c])
    maa=ma*ma*np.outer(d,d)
    gd=np.array([c,s,0.])
    hd=np.array([-s,c,0.])
    se=np.array([0.,0.,1.])
    md=p["mH1"]**2*math.cos(ga)**2+p["mH2"]**2*math.sin(ga)**2
    ms=p["mH1"]**2*math.sin(ga)**2+p["mH2"]**2*math.cos(ga)**2
    off=-z["mu4_GeV"]*v/math.sqrt(2)
    mcharged=(md*np.outer(hd,hd)+ms*np.outer(se,se)
              +off*(np.outer(hd,se)+np.outer(se,hd)))
    assert np.allclose(np.linalg.eigvalsh(mcharged),
                       [0,p["mH1"]**2,p["mH2"]**2],rtol=1e-10,atol=1e-6)
    assert np.linalg.norm(mcharged@gd,ord=np.inf)<1e-7
    rules="{" + ", ".join(key+" -> "+wl(value) for key,value in vals.items())+"}"
    lines=[
      "(* Generated from existing Gate6 formulas, not from SARAH. *)",
      "zeeGate6Rules = "+rules+";",
      "zeeGate6Beta = "+wl(b)+";",
      "zeeGate6Gamma = "+wl(p["gamma"])+";",
      "zeeGate6Alpha = "+wl(alpha)+";",
      "zeeGate6ExpectedHH = "+wlmatrix(mhh)+";",
      "zeeGate6ExpectedAh = "+wlmatrix(maa)+";",
      "zeeGate6ExpectedHm = "+wlmatrix(mcharged)+";",
      "zeeGate6GoldstoneNeutral = {"+wl(c)+","+wl(s)+"};",
      "zeeGate6GoldstoneCharged = {"+wl(c)+","+wl(s)+",0};",
    ]
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text("\n".join(lines)+"\n")
    print("ZEE_GATE6_FIXTURE_WRITTEN",dest)
    print("ZEE_GATE6_BENCHMARK_GEV",mh,mH,ma,p["mH1"],p["mH2"])
    print("SOURCE_GATE6_REFERENCE_ONLY_NOT_FULL_MODEL_VALIDATED")

if __name__=="__main__":
    main()
