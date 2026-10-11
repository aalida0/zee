#!/usr/bin/env python3
"""Gate A1I: SuperIso v5 two-charged-state matching and tooling preflight.

NOT a physical B->Xs gamma rate or an exclusion. Reuses Gate8a's LO
Type-II Wilson coefficients, weighted by Zee charged-doublet fractions.
Native 2HDM predictions have one charged mass, not two mixed states.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from scipy.optimize import brentq
from gate8a_bsgamma_lo_screen import screen, typeii_charged_lo

NAMES = ("scan_coeffs.c","predict.c","thdm.c","2hdm.c",
         "bsgamma.c","wilson.c","bsgamma.h","leshouches.c")

def effective_mass(key, coefficient, tanbeta, mt=172.):
    """A single-mass matching NO-GO diagnostic; not an NNLO proxy."""
    if key not in ("C7","C8"):
        raise ValueError("key must be C7/C8")
    fn=lambda m:typeii_charged_lo(m,tanbeta,mt)[key]-coefficient
    if fn(225.)*fn(3000.)>0:
        raise ValueError("no root")
    return float(brentq(fn,225.,3000.,xtol=1e-9))

def checksum(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for part in iter(lambda:f.read(1024*1024),b""):
            h.update(part)
    return h.hexdigest()

def source_inventory(path):
    """Inventory existing source only. Does not execute any binaries."""
    base=Path(path).expanduser().resolve()
    if not base.is_dir():
        return {"status":"NOT_FOUND","path":str(base),
                "zee_two_state_matching_certified":False}
    manifest=[]
    for name in NAMES:
        for p in (base/name,base/"src"/name):
            if p.is_file():
                manifest.append({"path":str(p.relative_to(base)),
                                 "sha256":checksum(p)})
    binaries=[x for x in ("sm.x","thdm.x","2hdm.x","scan_coeffs.x","predict.x")
              if (base/x).is_file()]
    return {"status":"SOURCE_INVENTORY_ONLY","path":str(base),
            "manifest":manifest,"detected_executables":binaries,
            "scan_coeffs_source_detected":any(
                x["path"].endswith("scan_coeffs.c") for x in manifest),
            "zee_two_state_matching_certified":False,
            "warning":"File presence does not prove external C7/C8 "
                      "injection or mixed charged-state NNLO support."}

def report(superiso_dir=None):
    lo=screen(beta=1.394,gamma=1.089,mH1=300,mH2=700,
              mt=172,reference_mass=580)
    c7=lo["combined_LO_charged_scalar"]["DeltaC7"]
    c8=lo["combined_LO_charged_scalar"]["DeltaC8"]
    tb=lo["inputs"]["tanbeta"]
    e7=effective_mass("C7",c7,tb)
    e8=effective_mass("C8",c8,tb)
    return {
        "status":"MIXED_ZEE_SUPERISO_PREFLIGHT_NOT_A_PHYSICAL_BR_OR_EXCLUSION",
        "lo_matching":{
            "DeltaC7":c7,"DeltaC8":c8,"tanbeta":tb,
            "light_doublet_fraction_squared":lo["mixing_weight_light_cos2gamma"],
            "heavy_doublet_fraction_squared":lo["mixing_weight_heavy_sin2gamma"],
            "scheme":"Gate8a LO fixed mt=172; not consistently NLO/NNLO"},
        "single_mass_mapping_NOT_PHYSICAL":{
            "m_matching_C7_GeV":e7,"m_matching_C8_GeV":e8,
            "difference_GeV":e8-e7,
            "valid_as_full_NNLO_Zee_prediction":False},
        "superiso":source_inventory(superiso_dir) if superiso_dir else {
            "status":"NOT_CHECKED_NO_SOURCE_PATH",
            "zee_two_state_matching_certified":False},
        "remaining":[
            "locate SuperIso 5.0 source and record revision",
            "run SM and genuine single-H+ Type-II controls",
            "verify supported C7/C8 input, matching-scale and operator schemes",
            "add both charged scalar masses at amplitude level at every order",
            "validate gamma=0 and pi/2 limits after RG running",
            "evaluate physical BR with latest HFLAV and theory uncertainties"],
        "prohibited":["average two SuperIso BR predictions",
                      "replace Zee by one matching effective mass",
                      "treat LO coefficients as an exclusion"],
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--superiso-dir",type=Path)
    p.add_argument("--output",type=Path,
                   default=Path("work/gateA1i_superiso_preflight.json"))
    a=p.parse_args()
    r=report(a.superiso_dir)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2)+"\n")
    print("Wrote",a.output)
    q=r["lo_matching"]; e=r["single_mass_mapping_NOT_PHYSICAL"]
    print(f"LO mixed DeltaC7={q['DeltaC7']:.9f}; DeltaC8={q['DeltaC8']:.9f}")
    print(f"Single-2HDM matching masses: C7={e['m_matching_C7_GeV']:.3f}, "
          f"C8={e['m_matching_C8_GeV']:.3f} GeV (NOT NNLO proxy)")
    print("SuperIso inventory:",r["superiso"]["status"])
    print("STATUS:",r["status"])
    assert abs(q["DeltaC7"]+.06296082441633362)<1e-10
    assert abs(q["DeltaC8"]+.06612190677250937)<1e-10
    assert not r["superiso"]["zee_two_state_matching_certified"]

if __name__=="__main__":
    main()
