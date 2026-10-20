#!/usr/bin/env python3
"""Write MadGraph generation decks for Zee asymmetric-pair 2->2 pilot.

Uses existing locally exported complete scalar/quark Zee LO UFO.
Model particles: Yang/Wu H+ = heavy H2+; h+ = light H1+.
Creates two separate processes:
  Z-only: mu+ mu- > z > H+ h- AND charge conjugate.
  Full tree: mu+ mu- > H+ h- AND conjugate.
The FIRST is a diagram-restricted analytic normalization check,
not a gauge-complete NP model. FULL tree includes possible neutrino
t-channel / Higgs contributions for the *diagnostic* Type-II lepton
Yukawas and f=0. Neither is a neutrino-fit Zee model.

Only creates process-generation scripts; does not invent run cross
sections. Input SLHA card must be scalar-matched and its DECAY widths
are STALE; do not use to simulate the physical H2 cascade.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

STATUS="ZEE_MUON_MG5_PAIR_PROCESS_DECKS_ONLY_NOT_VALIDATED_CROSS_SECTION"
PROCESS={
    "Z_only":{
        "first":"mu+ mu- > z > H+ h- QCD=0",
        "second":"mu+ mu- > z > H- h+ QCD=0"},
    "full_tree":{
        "first":"mu+ mu- > H+ h- QCD=0",
        "second":"mu+ mu- > H- h+ QCD=0"},
}


def decks(ufo,output_dir):
    ufo=Path(ufo).resolve()
    out=Path(output_dir).resolve()
    if not (ufo/"particles.py").is_file() or not (
            ufo/"vertices.py").is_file():
        raise ValueError("Missing local Yang/Wu modified Zee LO UFO")
    if out.exists() and any(out.iterdir()):
        raise ValueError("Choose a new empty directory; no overwrite")
    out.mkdir(parents=True,exist_ok=True)
    result={}
    for name,pair in PROCESS.items():
        process_dir=out/("MG5_"+name)
        card=out/(name+".mg5")
        card.write_text(
            "set automatic_html_opening False\n"
            "import model "+str(ufo)+"\n"
            "generate "+pair["first"]+"\n"
            "add process "+pair["second"]+"\n"
            "output "+str(process_dir)+"\n")
        result[name]={
            "process_dir":str(process_dir),
            "MG5_input_deck":str(card),
            "first_process":pair["first"],
            "second_process":pair["second"],
            "both_charge_conjugates":True}
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ufo",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    a=ap.parse_args()
    info=decks(a.ufo,a.output_dir)
    report={
        "status":STATUS,
        "local_model":str(a.ufo.resolve()),
        "processes":info,
        "note":"Run the provided MG5 decks; MG5 may need automatic "
               "UFO conversion. Compare Z-only matrix element with "
               "analytic scalar rate. Never use old SLHA DECAY widths.",
        "MG5_event_generation_completed":False,
        "s_channel_Z_analytic_validation_completed":False,
        "full_Zee_muon_Yukawa_neutrino_fits_loaded":False,
    }
    (a.output_dir/"plan.json").write_text(
        json.dumps(report,indent=2)+"\n")
    print("STATUS",STATUS)
    for name,row in info.items():
        print("MG5_DECK",name,row["MG5_input_deck"])
    print("MG5_RATES_CALCULATED False")


if __name__=="__main__":
    main()
