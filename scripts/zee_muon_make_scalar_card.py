#!/usr/bin/env python3
"""Build a COMPLETE SCALAR-MAPPED Yang/Wu Zee LO UFO diagnostic SLHA card.

Reads one exact B4 screened spectrum (including all singlet quartics)
and maps every scalar potential input with gate7_map_p2_to_yangwu.
Lepton Yukawas are the existing Gate7 Type-II diagnostic f=0 and are
NOT neutrino-compatible. Production s-channel Z-only amplitudes are
independent of them. Raw DECAY entries are STALE, cannot decay events
or claim a physical branching fraction with this card.

For full Yang/Wu Zee flavor production the complex B2 f,Y must be
mapped to a separately validated neutrino-compatible UFO card later.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from gate7_make_diagnostic_param_card import (
    replacements,render_card,validate_card_values
)
from gate7_map_p2_to_yangwu import map_point

REQUIRED=("id","mH1","mH2","mh2","ma","alpha","beta","gamma",
          "m12sq","lc","k1","k2","k12")
MAP_KEYS=("alpha","gamma","m12sq","mh2","ma","lc","k1","k2","k12")
STATUS="ZEE_MUON_B4_SCALAR_MATCHED_DIAGNOSTIC_CARD_NO_NEUTRINO_FIT_OR_DECAYS"


def selected_point(path,candidate_id):
    with Path(path).open(newline="") as f:
        rd=csv.DictReader(f)
        if not rd.fieldnames or any(k not in rd.fieldnames for k in REQUIRED):
            raise ValueError("B4 full screened candidate CSV required")
        rows=[r for r in rd if r["id"]==candidate_id]
    if len(rows)!=1:
        raise ValueError("Expected exactly one B4 scalar candidate ID")
    row=rows[0]
    if row.get("candidate_status") and (
            "NOT_ALLOWED" not in row["candidate_status"]):
        raise ValueError("Input status unexpectedly claims allowed point")
    p={}
    for k in REQUIRED[1:]:
        try:p[k]=float(row[k])
        except (ValueError,TypeError) as exc:
            raise ValueError("Missing scalar parameter "+k) from exc
        if not math.isfinite(p[k]):
            raise ValueError("Nonfinite scalar parameter "+k)
    if not(0<p["mH1"]<p["mH2"]):
        raise ValueError("Invalid charged spectrum")
    p["id"]=candidate_id
    return p


def make_card(point,template):
    scalar_opts={k:point[k] for k in MAP_KEYS}
    kw=dict(beta=point["beta"],mH1=point["mH1"],
            mH2=point["mH2"],**scalar_opts)
    scalar_map=map_point(**kw)
    values=replacements(**kw)
    text=render_card(template,values)
    validate_card_values(text,values)
    for key,mapping_key in ((227,"mH2"),(228,"mH1"),(225,"mh2"),(226,"ma")):
        found=values[("MASS",key)]
        if not math.isclose(found,point[mapping_key],rel_tol=1e-12,
                            abs_tol=1e-9):
            raise ValueError("Mass map mismatch for PDG "+str(key))
    phi=values[("ZEEINPUTS",4)]
    if not math.isclose(phi,math.pi/2-point["gamma"],abs_tol=1e-11):
        raise ValueError("Charged mixing mapping mismatch")
    return text,scalar_map,values


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--b4-csv",type=Path,required=True)
    ap.add_argument("--candidate-id",required=True)
    ap.add_argument("--ufo-template-param-card",type=Path,required=True)
    ap.add_argument("--output-card",type=Path,required=True)
    ap.add_argument("--acknowledge-unfitted-neutrino-sector",
                    action="store_true",required=True)
    a=ap.parse_args()
    if a.output_card.exists() or (
            a.output_card.resolve()==a.ufo_template_param_card.resolve()):
        ap.error("Choose new output, never overwrite original SLHA template")
    p=selected_point(a.b4_csv,a.candidate_id)
    template=a.ufo_template_param_card.read_text()
    card,mp,values=make_card(p,template)
    a.output_card.parent.mkdir(parents=True,exist_ok=True)
    a.output_card.write_text(card)
    report={
        "status":STATUS,"candidate_id":a.candidate_id,
        "input_B4_scalar":p,
        "mapped_UFO_mass_quartic_inputs":mp["map"],
        "map_closure":mp["closure_mass_basis_residuals"],
        "param_card":str(a.output_card),
        "physical_neutrino_masses_calculated":False,
        "model_complete_leptonic_f_Y":False,
        "DECAY_widths_validated":False,
        "Yukawa_model":"TypeII diagonal lepton diagnostics, f=0 only",
        "use_case":"Pure virtual Z gauge pair-production closure ONLY",
    }
    report_path=a.output_card.with_suffix(".scalar_mapping.json")
    report_path.write_text(json.dumps(report,indent=2)+"\n")
    print("STATUS",STATUS)
    print("CANDIDATE",p["id"],"mH1",p["mH1"],"mH2",p["mH2"],
          "gamma",p["gamma"])
    print("YANGWU_phi",values[("ZEEINPUTS",4)])
    print("NEUTRINO_FIT False")
    print("DECAY_WIDTHS_STALE True")
    print("OUTPUT",a.output_card)
    print("MAPPING_REPORT",report_path)


if __name__=="__main__":
    main()
