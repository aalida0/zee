#!/usr/bin/env python3
"""Audit the Gate-7D W h(580.7) difference from EW input-scheme choices.

Uses the actual MadWidth INPUT card SMINPUTS (alpha^-1, GF, mZ)
and OUT card DECAY widths. Computes mW/gW exactly as Yang/Wu UFO
parameters.py defines them, then rescaling the independent Gate-6
analytic W hheavy prediction for the changed gW and mW phase space.

Does not validate neutrino/LFV physics, NLO, or gauge cancellations.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

from gate6_width_inventory import (
    inventory, MW as G6_MW, ALPHA_INV as G6_AEWI, SW2 as G6_SW2,
)
from gate7_check_madwidth import read_widths

F_PATTERN = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][+-]?\d+)?$")
BLOCK = re.compile(r"^\s*BLOCK\s+([A-Za-z0-9_]+)", re.I)


def read_ew_inputs(card: str) -> dict:
    block = None
    found = {}
    for raw in card.splitlines():
        match = BLOCK.match(raw)
        if match:
            block = match.group(1).upper()
            continue
        if re.match(r"^\s*(?:DECAY|QNUMBERS)\b", raw, re.I):
            block = None
            continue
        if block != "SMINPUTS":
            continue
        s = raw.split("#",1)[0].split()
        if len(s) < 2 or not s[0].lstrip("+-").isdigit():
            continue
        code=int(s[0])
        if code not in (1,2): continue
        if not F_PATTERN.fullmatch(s[1]):
            raise ValueError(f"Invalid SMINPUTS[{code}]")
        if code in found: raise ValueError(f"Duplicate SMINPUTS[{code}]")
        found[code]=float(s[1].replace("D","E").replace("d","e"))
    for code in (1,2):
        if code not in found or found[code]<=0:
            raise ValueError(f"Missing positive SMINPUTS[{code}]")
    return {"alpha_inv":found[1],"Gf_GeVminus2":found[2]}


def derive_ew(alpha_inv: float, Gf: float, MZ: float):
    rad=MZ**4/4. - math.pi/alpha_inv*MZ*MZ/(Gf*math.sqrt(2))
    if rad<=0: raise ValueError("Unphysical on-shell EW radicand")
    MW=math.sqrt(MZ*MZ/2. + math.sqrt(rad))
    sw2=1.-MW*MW/(MZ*MZ)
    if not (0<sw2<1):raise ValueError("Unphysical weak mixing angle")
    gw=math.sqrt(4*math.pi/(alpha_inv*sw2))
    return {"MW_GeV":MW, "sin2thetaW":sw2,"gW":gw}


def w_width_factor(M:float,m:float,mw:float,gw:float)->float:
    if M<=m+mw:
        return 0.
    k=(M*M-(m+mw)**2)*(M*M-(m-mw)**2)
    return gw*gw*k**1.5/(mw*mw)


def audit(input_card:str,output_card:str,beta=1.394,mH1=300.,mH2=700.):
    params=read_ew_inputs(input_card)
    masses={25:125.,225:580.7,226:633.7,227:mH2,228:mH1}
    # The MZ input is fixed by Gate-6 / Yang-Wu mass convention; read it from
    # the card MASS block to ensure this is not silently changed.
    massblock=None
    for raw in input_card.splitlines():
        m=BLOCK.match(raw)
        if m:
            massblock=m.group(1).upper();continue
        if re.match(r"^\s*(?:DECAY|QNUMBERS)\b",raw,re.I):
            massblock=None;continue
        if massblock=="MASS":
            c=raw.split("#",1)[0].split()
            if len(c)>=2 and c[0].lstrip("+-").isdigit():
                pdg=int(c[0])
                if pdg in masses or pdg==23:
                    val=float(c[1].replace("D","E").replace("d","e"))
                    if pdg in masses and not math.isclose(val,masses[pdg],rel_tol=1e-8):
                        raise ValueError(f"MASS[{pdg}] differs from diagnostic benchmark")
                    masses[pdg]=val
    if 23 not in masses:
        raise ValueError("Diagnostic card lacks MASS[23] needed for EW scheme")
    ew=derive_ew(params["alpha_inv"],params["Gf_GeVminus2"],masses[23])
    g6_gw=math.sqrt(4*math.pi/(G6_AEWI*G6_SW2))
    ref=inventory(beta,mH1,mH2)["partial_widths_GeV"]["H2"]["W_hheavy"]
    adjustment=w_width_factor(mH2,masses[225],ew["MW_GeV"],ew["gW"])/w_width_factor(
         mH2,masses[225],G6_MW,g6_gw
    )
    computed=read_widths(output_card)
    if 227 not in computed or (24,225) not in computed[227]["channels"]:
        raise ValueError("MadWidth table missing heavy->W heavy-neutral channel")
    observed=computed[227]["width_GeV"]*computed[227]["channels"][(24,225)]
    predicted=ref*adjustment
    relative=(observed-predicted)/predicted
    return {
        "status":"GATE7D_EW_SCHEME_DIAGNOSTIC_NOT_PHYSICAL_BR",
        "input_ew":params,
        "ufo_on_shell_scheme":ew,
        "Gate6_hardcoded_scheme":{"MW_GeV":G6_MW,"sin2thetaW":G6_SW2,"gW":g6_gw},
        "channel":"H2 -> W hheavy (700 -> W 580.7)",
        "Gate6_original_width_GeV":ref,
        "expected_EW_scheme_ratio":adjustment,
        "predicted_on_shell_width_GeV":predicted,
        "MadWidth_width_GeV":observed,
        "relative_residual_after_EW_match":relative,
        "EW_scheme_explains_width_at_0p1pct":abs(relative)<0.001,
        "warning":"Diagnostic f_ab=0 Zee lepton limit; not physical BR, excludes NLO and global constraints."
    }


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input-card",required=True,type=Path)
    ap.add_argument("--width-card",required=True,type=Path)
    ap.add_argument("--output",type=Path)
    a=ap.parse_args()
    x=audit(a.input_card.read_text(),a.width_card.read_text())
    blob=json.dumps(x,indent=2)+"\n"
    print(blob,end="")
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(blob)
    if not x["EW_scheme_explains_width_at_0p1pct"]:
        raise SystemExit("EW scheme audit did not close to 0.1%: investigate")
if __name__=="__main__":main()
