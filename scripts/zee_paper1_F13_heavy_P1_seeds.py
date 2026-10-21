#!/usr/bin/env python3
"""F13: genuine heavy Zee scalar seeds from Florentino P1, not gamma-only edits.

These seed candidates fully reconstruct the CP-conserving scalar potential,
and are passed through the existing B4 sufficient BFB, tree unitarity, full
correlated S,T,U screen. They are not globally full Zee allowed points.
The P1 Table2 source specifies intervals, NOT one physical benchmark.
"""
from __future__ import annotations
import math
from pathlib import Path
import numpy as np
from gateB4_adaptive_zee_scalar_scan import (
    encode,decode,scalar_screen,ewpo_screen,make_record,coarse_bin
)
from zee_reproduce_florentino_2021_regions import load_regions,build_inputs

STATUS="F13_P1_INSPIRED_HEAVY_GENUINE_SCALAR_EWPO_SEEDS_NOT_ALLOWED"
HEAVY_MIN=550.
HEAVY_MAX=720.
H2_MAX=1600.
MZ=91.1876

def p1_candidate(*,m1,m2,gamma,beta,k12=None,
                 mh2=None,ma=None):
    region=load_regions()["benchmarks"]["P1"]
    # Build a fresh actual scalar point, source P1 inspired and extended.
    p={
        "mH1":float(m1),"mH2":float(m2),
        "mh2":float(region["mh2_GeV"] if mh2 is None else mh2),
        "ma":float(region["ma_GeV"] if ma is None else ma),
        "beta":float(beta),"alpha":float(region["alpha_rad"]),
        "gamma":float(gamma),"m12sq":float(region["m12sq_GeV2"]),
        "lc":float(region["lambda_c"]),"k1":float(region["k1"]),
        "k2":float(region["k2"]),
        "k12":float(region["k12"] if k12 is None else k12),
    }
    # B4's physical coordinate codec is necessary but not sufficient.
    if not (HEAVY_MIN<=p["mH1"]<=HEAVY_MAX and
            p["mH2"]>p["mH1"]+MZ+1 and p["mH2"]<=H2_MAX):
        raise ValueError("Heavy P1 source point outside search domain")
    code=encode(p)
    p=decode(code)
    if p is None:raise ValueError("P1 scalar reconstruction outside B4 domain")
    return p

def candidate_grid(n,seed=20261021):
    """Wide physical input proposal grid, reproducible and bounded.

    First deterministic P1 midpoints and endpoints; then seeded jitter in
    continuous masses and neutral/charged quartic correlations. No prior
    flavor or allowed-volume inference.
    """
    if n<1:raise ValueError("At least one heavy seed attempt required")
    rng=np.random.default_rng(seed)
    anchor=[
        (625.,825.,.894,1.391,.0543,715.,767.4),
        (575.,810.,.894,1.391,.0543,715.,767.4),
        (670.,870.,.894,1.391,.0543,715.,767.4),
        (700.,900.,.894,1.391,.0543,715.,767.4),
        (550.,750.,.894,1.391,.0543,715.,767.4),
        (650.,900.,.894,1.391,0.,715.,767.4),
        (700.,1000.,.894,1.391,0.,715.,767.4),
        (600.,850.,1.05,1.391,0.,715.,767.4),
        (690.,850.,.65,1.391,.0543,715.,767.4),
        (675.,780.,.894,1.391,.0543,715.,767.4),
    ]
    for i in range(n):
        if i<len(anchor):
            m1,m2,g,b,k,h,a=anchor[i]
        else:
            m1=float(rng.uniform(550.,715.))
            m2=float(rng.uniform(max(m1+MZ+10.,745.),1050.))
            g=float(rng.uniform(.35,1.35))
            b=float(rng.uniform(1.382,1.407))
            k=float(rng.choice([0.,.0543,.03,-.03]))
            h=float(rng.normal(715.,42.))
            a=float(rng.normal(767.4,45.))
        try:
            p=p1_candidate(m1=m1,m2=m2,gamma=g,beta=b,
                           k12=k,mh2=h,ma=a)
        except (ValueError,FloatingPointError):
            continue
        yield i,p

def validated_p1_seeds(n,quad,seed,max_seeds=4):
    if quad<40 or max_seeds<1:raise ValueError("Bad seed search settings")
    found=[];bins=set();reason={"input":0,"theory":0,"EWPO":0,"numeric":0}
    attempted=0
    for index,p in candidate_grid(n,seed):
        attempted+=1
        try:
            th=scalar_screen(p)
            if th is None:
                reason["theory"]+=1;continue
            ew=ewpo_screen(p,quad)
            if ew is None:
                reason["EWPO"]+=1;continue
            cell=coarse_bin(p)
            if cell in bins:continue
            row=make_record(p,th,ew,0,
                        f"F13_heavy_P1_seed_{index:04d}",
                        f"P1_INSP_{index:04d}")
            found.append((p,row));bins.add(cell)
            if len(found)>=max_seeds:break
        except (ValueError,ArithmeticError,FloatingPointError,
                np.linalg.LinAlgError):
            reason["numeric"]+=1
    stats={"status":STATUS,"attempts_iterated":attempted,
           "accepted_seed_points":len(found),
           "failure_counts":reason,
           "all_are_genuine_rebuilt_theory_EWPO_not_allowed":True,
           "published_P1_not_an_exact_benchmark":True}
    return found,stats
