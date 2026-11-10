#!/usr/bin/env python3
"""Fail-closed import contract for original SARAH ZeeTypeII tau complex dipoles.

This validator DOES NOT run original generated Fortran or prove that a JSON
was produced by the original native code. It checks the original pinned
source SHAs and the complex coefficients' BR normalization; individual
complex phases are unconstrained by BR alone and MUST be independently
replayed against the Fortran source before use as physical inputs.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_radiative_threebody_diagnostic import (
    GATE, EXPECTED_IDS
)

H_BAR = 6.582119569e-25
TAU_LIFETIME = 290.3e-15
M_TAU = 1.77686
CHANNELS=("tauegamma","taumugamma")
SOURCE_KEYS=("generated","couplings","loops")
REQUIRED_ORIGIN="ORIGINAL_COMPILED_SARAH_4_15_4_ZEETYPEII_CALCULATEGAMMA2L"


def finite_complex(pair):
    if not isinstance(pair,list) or len(pair)!=2:
        raise ValueError("Expected complex [real,imag] list")
    if any(type(t) not in (int,float) or not math.isfinite(t) for t in pair):
        raise ValueError("Nonfinite complex source coefficient")
    return complex(pair[0],pair[1])


def validate(payload:dict,rate_tolerance:float=3e-6)->dict:
    if not isinstance(payload,dict) or payload.get("source_origin")!=REQUIRED_ORIGIN:
        raise ValueError("Missing exact original generator origin label")
    gate=json.loads(GATE.read_text())
    expected_hashes=gate["native_original_Fortran_sha256"]
    if payload.get("fortran_sha256")!=expected_hashes:
        raise ValueError("Fortran source hashes do not match the original pinned three-file set")
    if payload.get("compiler_command")!=gate["source_compile"]:
        raise ValueError("Different native Fortran compilation mode")
    if payload.get("lepton_order")!=["e","mu","tau"]:
        raise ValueError("Native lepton flavor order changed")
    if payload.get("native_K2_convention")!="K2L=-OA2L/(2*e*m_parent);K2R=-OA2R/(2*e*m_parent)":
        raise ValueError("Native source dipole convention mismatch")
    rows=payload.get("cards")
    if not isinstance(rows,list) or tuple(r.get("card") for r in rows)!=EXPECTED_IDS:
        raise ValueError("Missing original D7/F13 NO/IO benchmark order")
    orig={c["card"]:c for c in gate["cards"]}
    alpha=gate["alphaEM_for_native"]
    gamma=H_BAR/TAU_LIFETIME
    coefficient=alpha*M_TAU**5/(4*gamma)
    results={}
    for row in rows:
        card=row["card"]
        info=row.get("channels")
        if not isinstance(info,dict) or set(info)!=set(CHANNELS):
            raise ValueError(f"Original complex tau K2 coverage incomplete {card}")
        results[card]={}
        for channel in CHANNELS:
            val=info[channel]
            if not isinstance(val,dict):
                raise ValueError("Invalid channel input")
            L=finite_complex(val.get("K2L"))
            R=finite_complex(val.get("K2R"))
            br=float(val.get("native_source_BR"))
            expected=float(orig[card]["native_one_loop_BR_"+channel])
            if not math.isfinite(br) or br<=0:
                raise ValueError("Invalid source BR")
            reconstruction=coefficient*(abs(L)**2+abs(R)**2)
            if abs(br/expected-1)>rate_tolerance:
                raise ValueError(f"Source BR does not match pinned historical execution: {card} {channel}")
            if abs(reconstruction/br-1)>rate_tolerance:
                raise ValueError(f"Complex K2 norm does not reproduce native source BR: {card} {channel}")
            results[card][channel]={
                "native_source_K2L":[L.real,L.imag],
                "native_source_K2R":[R.real,R.imag],
                "module3_CL_from_native":[(-R).real,(-R).imag],
                "module3_CR_from_native":[(-L).real,(-L).imag],
                "source_BR":br,
                "reconstructed_source_BR":reconstruction,
                "relative_reconstruction_residual":reconstruction/br-1,
                "can_phase_be_verified_from_rate_alone":False
            }
    return {
        "status":"SOURCE_HASH_AND_COMPLEX_K2_NORM_VALIDATION_ONLY_ORIGINAL_FORTRAN_NOT_RERUN",
        "input_origin_claim":REQUIRED_ORIGIN,
        "fortran_sha256":expected_hashes,
        "comparison":"K2L/K2R norm agrees with pinned original massless-final 2body source rate; does not prove complex phase/source execution",
        "input_phases_independently_verified":False,
        "original_fortran_executed_in_this_validation":False,
        "ready_for_physical_full_Zee_rate":False,
        "cards":results,
        "physical_lfv":"UNKNOWN",
        "global_acceptance":None
    }


def run(path:Path)->dict:
    return validate(json.loads(path.read_text()))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("input_json",type=Path)
    p.add_argument("--output",type=Path)
    x=p.parse_args()
    result=run(x.input_json)
    if x.output:
        if x.output.exists():
            raise FileExistsError(f"Refusing overwrite: {x.output}")
        x.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(result["status"],"FOUR_CARDS",len(result["cards"]))
    print("ORIGINAL_FORETRAN_COMPLEX_PHASE_PROOF UNAVAILABLE; PHYSICAL_LFV UNKNOWN")


if __name__=="__main__":
    main()
