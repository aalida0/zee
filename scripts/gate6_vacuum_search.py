#!/usr/bin/env python3
"""Gate 6 finite multistart charged-breaking vacuum check.

Uses a gauge-fixed 7-real-field slice of the full CP-conserving two-doublet
plus singly charged singlet potential, with complex Phi2 and chi components.
Finite random restarts CANNOT certify the global minimum.
"""
import argparse
import json
import math
import numpy as np
from pathlib import Path
from scipy.optimize import minimize
from gate6_benchmark import benchmark

def potential(y,p):
    q=p["quartics"];x=p["inputs"]
    a,b,c,d,e,f,g=y
    x1=a*a
    x2=b*b+c*c+d*d+e*e
    xc=f*f+g*g
    rey=a*d
    absy2=a*a*(d*d+e*e)
    rey2=a*a*(d*d-e*e)
    v=x["v"]
    cb,sb=math.cos(x["beta"]),math.sin(x["beta"])
    l1,l2,l3,l4,l5=[q["lambda"+str(i)] for i in range(1,6)]
    soft1=x["m12sq"]*sb/cb-.5*v*v*(l1*cb*cb+(l3+l4+l5)*sb*sb)
    soft2=x["m12sq"]*cb/sb-.5*v*v*(l2*sb*sb+(l3+l4+l5)*cb*cb)
    return (
        soft1*x1+soft2*x2-2*x["m12sq"]*rey+p["mc2_GeV2"]*xc
        +.5*l1*x1*x1+.5*l2*x2*x2+l3*x1*x2
        +l4*absy2+l5*rey2+x["lambda_c"]*xc*xc
        +(x["k1"]*x1+x["k2"]*x2-2*x["k12"]*rey)*xc
        -2*p["mu4_GeV"]*a*(b*f+c*g)
    )

def search(beta=1.394,nstarts=30,seed=123):
    p=benchmark(beta=beta)
    x=p["inputs"];v=x["v"]
    neutral=np.array([v*math.cos(beta)/math.sqrt(2),0,0,
                      v*math.sin(beta)/math.sqrt(2),0,0,0],float)
    vnormal=potential(neutral,p)
    rng=np.random.default_rng(seed)
    choices=[neutral,np.zeros(7)]
    choices.extend(rng.uniform(-600,600,size=7) for _ in range(nstarts))
    best=float("inf")
    deepest=None
    for starting in choices:
        res=minimize(lambda z:potential(z*v,p)/(v**4),
                     starting/v,method="BFGS",
                     options={"maxiter":2000,"gtol":1e-8})
        value=res.fun*v**4
        if np.isfinite(value) and value<best:
            best=float(value)
            deepest=(res.x*v).tolist()
    if deepest is None:raise RuntimeError("No finite minimization")
    delta=best-vnormal
    return {
       "status":"NUMERICAL_VACUUM_SEARCH_NOT_A_GLOBAL_CERTIFICATE",
       "beta":beta,"n_trials":len(choices),"seed":seed,
       "neutral_vacuum_GeV4":vnormal,
       "best_vacuum_GeV4":best,
       "best_minus_neutral_GeV4":delta,
       "deeper_point_found":bool(delta < -1e-6*max(1,abs(vnormal))),
       "best_gauge_fixed_real_fields_GeV":deepest,
       "warning":"Finite multistart BFGS does not prove a global minimum, even with complex fields."
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--beta",type=float,default=1.394)
    ap.add_argument("--nstarts",type=int,default=30)
    ap.add_argument("--seed",type=int,default=123)
    ap.add_argument("--output",type=Path)
    a=ap.parse_args()
    data=json.dumps(search(a.beta,a.nstarts,a.seed),indent=2)+"\n"
    print(data,end="")
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(data)

if __name__=="__main__":
    main()
