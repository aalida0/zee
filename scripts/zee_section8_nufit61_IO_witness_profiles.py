#!/usr/bin/env python3
"""Source-pinned NuFIT6.1 IO 2D-profile diagnostic of the family-Z2 witness.

NuFIT tables contain OVERLAPPING marginalized profiles. Never add their
Delta-chi2 values or claim an accepted complete joint oscillation fit.
Do not distribute source tables, for which redistribution terms are unclear.
"""
from __future__ import annotations
import argparse
import bisect
import hashlib
import json
import lzma
import math
from pathlib import Path
import re

from zee_section8_IO_witness_neutrino_physical_observables import calculate

STATUS="FAMILY_Z2_NUFIT61_IO_2D_PROFILES_NOT_JOINT_LIKELIHOOD_OR_ALLOWED"
SOURCE="https://www.nu-fit.org/?q=node/309"
THRESHOLD_3SIGMA_2DOF=11.829158081900795
TABLES={
 "TBoff-IO":{
  "url":"https://www.nu-fit.org/sites/default/files/v61.release-TBoff-IO.txt.xz",
  "bytes":4083980,
  "sha256":"6e14ce52503d053ce4d8d0171ffecae24c2dd3dc41be99c3c5c952f321331f16",
  "variant":"IC23 without tabulated SK-atmospheric data"},
 "TByes-IO":{
  "url":"https://www.nu-fit.org/sites/default/files/v61.release-TByes-IO.txt.xz",
  "bytes":4087336,
  "sha256":"d92fbd1886a85738080a394a6af513ec1ac49d5e474a6517cada0c2c6f3b96b2",
  "variant":"IC24 with tabulated SK-atmospheric data"},
}
# Hash/size manifest from public external audit,
# FloatingPragma/observer-patch-holography (retrieved July 2026).
# Hashes not directly independently checked by this code's authors.
WANTED=("T13/T12","T23/DCP","DMS/DMA")
SECTION=re.compile(r"^# ([A-Z0-9/]+) projection:")

def verify(path,key):
    if key not in TABLES:raise ValueError("Unknown source variant")
    p=Path(path)
    if not p.is_file():raise FileNotFoundError(p)
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):h.update(chunk)
    if h.hexdigest()!=TABLES[key]["sha256"] or p.stat().st_size!=TABLES[key]["bytes"]:
        raise ValueError("Official-source SHA256/size mismatch; do not interpret this table")
    return {"url":TABLES[key]["url"],"sha256":h.hexdigest(),
            "bytes":p.stat().st_size,"variant":TABLES[key]["variant"]}

class Grid:
    def __init__(self,rows,name):
        if not rows:raise ValueError("Missing section "+name)
        self.x=sorted({p[0] for p in rows})
        self.y=sorted({p[1] for p in rows})
        self.z={}
        for x,y,value in rows:
            if (x,y) in self.z and self.z[x,y]!=value:
                raise ValueError("Conflicting duplicated source coordinates")
            self.z[x,y]=value
        if len(self.x)<2 or len(self.y)<2 or len(self.z)!=len(self.x)*len(self.y):
            raise ValueError("Nonrectangular 2D NuFIT section "+name)

    @staticmethod
    def bracket(axis,value):
        if not math.isfinite(value) or value<axis[0] or value>axis[-1]:
            raise ValueError(f"Outside official table support: {value} not [{axis[0]},{axis[-1]}]")
        j=max(0,min(len(axis)-2,bisect.bisect_right(axis,value)-1))
        a,b=axis[j:j+2]
        return a,b,(value-a)/(b-a)

    def interpolate(self,x,y):
        a,b,t=self.bracket(self.x,x)
        c,d,u=self.bracket(self.y,y)
        z=self.z
        return float((1-t)*(1-u)*z[a,c]+t*(1-u)*z[b,c]+
                     (1-t)*u*z[a,d]+t*u*z[b,d])

def read_tables(path):
    rows={name:[] for name in WANTED}
    active=None
    opener=lzma.open if str(path).endswith(".xz") else open
    with opener(path,"rt",encoding="utf-8") as f:
        for line in f:
            if line.startswith("# "):
                m=SECTION.match(line)
                active=m.group(1) if m and m.group(1) in rows else None
                continue
            if active is None or not line.strip() or line.lstrip().startswith("#"):
                continue
            fields=line.split()
            if len(fields)!=3:raise ValueError("Expected 3-column NuFIT 2D table")
            v=tuple(map(float,fields))
            if any(not math.isfinite(a) for a in v):raise ValueError("Nonfinite source row")
            rows[active].append(v)
    return {key:Grid(value,key) for key,value in rows.items()}

def witness():
    p=calculate()
    obs=p["oscillation_values"]
    m=obs["masses_eV"]
    d21=m[1]**2-m[0]**2
    d32=m[2]**2-m[1]**2
    if not(d21>0>d32):raise ValueError("Not inverted ordering")
    r=d21/(-d32)
    if not math.isclose(r,obs["mass_ratio"],rel_tol=1e-9):
        raise ValueError("Witness splitting ratio mismatch")
    delta=(p["delta_CP_degrees_mod360"]+180)%360-180
    return {"sin2theta12":obs["sin2theta12"],
            "sin2theta13":obs["sin2theta13"],
            "sin2theta23":obs["sin2theta23"],
            "deltaCP_deg_signed":delta,
            "dm21_sq_eV2":d21,"dm32_sq_eV2":d32,
            "solar_over_abs_atm":r,
            "sum_mnu_eV":p["sum_mnu_eV"]}

def profile_ratio(grid,ratio,steps=4001):
    """Diagnostic finite-grid sample: no certified continuous minimum."""
    if ratio<=0 or steps<1001:raise ValueError("Bad solar/atmospheric ratio or sampling")
    best=None
    for i in range(steps):
        y=grid.y[0]+(grid.y[-1]-grid.y[0])*i/(steps-1)
        if y>=0:continue # IO: dm32 < 0, units 1e-3 eV^2
        x=math.log10(ratio*(-y)*1e-3)
        if not(grid.x[0]<=x<=grid.x[-1]):continue
        score=grid.interpolate(x,y)
        if best is None or score<best["delta_chi2"]:
            best={"delta_chi2":score,"dm21_eV2":ratio*(-y)*1e-3,
                  "dm32_eV2":y*1e-3,
                  "method":"finite scan along fixed ratio; NOT mathematically certified continuous profile"}
    if best is None:raise ValueError("Ratio curve has no NuFIT grid support")
    return best

def analyze(path,key,coords=None,check_hash=True):
    provenance=verify(path,key) if check_hash else {
        "SYNTHETIC_TEST_ONLY":"unverified bytes; no physics claim"}
    grids=read_tables(path)
    c=witness() if coords is None else coords
    values={
       "T13/T12":grids["T13/T12"].interpolate(c["sin2theta13"],c["sin2theta12"]),
       "T23/DCP":grids["T23/DCP"].interpolate(c["sin2theta23"],c["deltaCP_deg_signed"]),
       "DMS/DMA_fixed_old_atm_scale":grids["DMS/DMA"].interpolate(
           math.log10(c["dm21_sq_eV2"]),c["dm32_sq_eV2"]/1e-3),
    }
    minimum=profile_ratio(grids["DMS/DMA"],c["solar_over_abs_atm"])
    output={name:{
      "interpolated_Delta_chi2":v,
      "outside_3sigma_for_this_2D_projection":v>THRESHOLD_3SIGMA_2DOF}
      for name,v in values.items()}
    output["DMS/DMA_profile_common_scale"]={
      "interpolated_Delta_chi2":minimum["delta_chi2"],
      "outside_3sigma_for_this_2D_projection":minimum["delta_chi2"]>THRESHOLD_3SIGMA_2DOF,
      "profile_details":minimum}
    return {"status":STATUS,"variant":key,"provenance":provenance,
            "individual_marginal_2D_profiles_DO_NOT_SUM":output,
            "critical_Delta_chi2_3sigma_2dof":THRESHOLD_3SIGMA_2DOF,
            "at_least_one_profile_incompatible_3sigma":any(
                row["outside_3sigma_for_this_2D_projection"] for row in output.values()),
            "full_NuFIT_joint_likelihood":None,"physical_Zee_allowed":None}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tb-off-io",type=Path,required=True)
    ap.add_argument("--tb-yes-io",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args()
    if a.output.exists():ap.error("Refusing overwrite")
    result={"status":STATUS,"official_source":SOURCE,"witness":witness(),
            "TBoff-IO":analyze(a.tb_off_io,"TBoff-IO"),
            "TByes-IO":analyze(a.tb_yes_io,"TByes-IO"),
            "joint_likelihood_available":False,"physical_Zee_allowed":None}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print("STATUS",STATUS)
    print("WITNESS_SPLITTINGS",json.dumps(result["witness"],sort_keys=True))
    for key in TABLES:
        print("VARIANT",key)
        for name,entry in result[key]["individual_marginal_2D_profiles_DO_NOT_SUM"].items():
            print("PROFILE",name,"DELTA_CHI2",entry["interpolated_Delta_chi2"],
                  "OUTSIDE_3SIGMA_2DOF",entry["outside_3sigma_for_this_2D_projection"])
    print("FULL_NUFIT_JOINT_LIKELIHOOD False")
    print("FULL_ZEE_ALLOWED False")
    print("OUTPUT",a.output)

if __name__=="__main__":main()
