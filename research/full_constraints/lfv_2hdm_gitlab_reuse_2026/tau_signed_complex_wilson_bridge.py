#!/usr/bin/env python3
"""Retrieve corrected author neutral-BZ *complex* tau Wilsons and compare to Zee.

Diagnostic only. The original private SARAH 4.15.4 complex native tau K2
source outputs are not in the public repository; module3 analytic one-loop
is an independently checked approximation, not a replacement for the
original source's full complex coefficient payload.

Uses exact external corrected GitLab source at pinned commit and SHA.
No source file rewriting, no complete Zee gauge-bosonic 2-loop inclusion.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import pathlib
import sys

import numpy as np
from module2.interface import decode
from module3.core import dipole_ledger,combine,radiative_width
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.official_gitlab_control import (
    make_input,source_decomposition, SOURCE_SHA, DATA, EXPECTED_COMMIT
)
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_radiative_threebody_diagnostic import (
    GATE, EXPECTED_IDS, CORRECTED_AUTHOR_SHA256
)
from research.full_constraints.lfv_lo_closure_2026 import __init__  # package existence audit

HBAR_GEV_S=6.582119569e-25
GAMMA_TAU_GEV=HBAR_GEV_S/(290.3e-15)
ALPHA_NATIVE=1/127.95
FLAVORS=(("tauegamma",3,1,0),("taumugamma",3,2,1))


def c2(z):
    c=complex(z)
    return [float(c.real),float(c.imag)]


def rate(coefs,ml,j):
    return radiative_width(np.array(coefs,dtype=complex),ml[2],ml[j],ALPHA_NATIVE)/GAMMA_TAU_GEV


def run(source_dir:pathlib.Path, revision:str)->dict:
    if not revision.startswith(EXPECTED_COMMIT):raise ValueError("Unreviewed GitLab source revision")
    if hashlib.sha256(DATA.read_bytes()).hexdigest()!=SOURCE_SHA:
        raise ValueError("Frozen D12 card source SHA mismatch")
    source=pathlib.Path(source_dir).resolve()/"thdm.py"
    if hashlib.sha256(source.read_bytes()).hexdigest()!=CORRECTED_AUTHOR_SHA256:
        raise ValueError("Corrected GitLab thdm.py SHA mismatch")
    gate=json.loads(GATE.read_text())
    if (gate.get("physical_lfv")!="UNKNOWN" or gate.get("global_acceptance") is not None
            or gate.get("authors_uploaded_thdm_sha256")!=CORRECTED_AUTHOR_SHA256):
        raise ValueError("Native tau source receipt changed")
    rows=[g["witnesses"]["low_joint"] for g in json.loads(DATA.read_text())["groups"]]
    if len(rows)!=4 or tuple(x.get("card") for x in gate["cards"])!=EXPECTED_IDS:
        raise ValueError("Unexpected exact four cards")

    spec=importlib.util.spec_from_file_location("pinned_2hdm_tau_source",source)
    module=importlib.util.module_from_spec(spec)
    sys.path.insert(0,str(source.parent))
    try:spec.loader.exec_module(module)
    finally:sys.path.remove(str(source.parent))
    out={}
    for card,w,saved in zip(EXPECTED_IDS,rows,gate["cards"]):
        p=w["module2_input"]["scalar"]["record"]["physical"]
        ml=w["module2_input"]["lepton_masses_GeV"]
        F=decode(w["yukawas"]["F"])
        D=decode(w["yukawas"]["D"])
        inp,_=make_input(w,"bare")
        model=module.thdm(inp)
        channels={}
        for name,src_i,src_j,native_j in FLAVORS:
            native_approx=combine(dipole_ledger(F,D,p,ml,2,native_j))
            # Authors' corrected complex neutral-fermion 2HDM BZ coefficients.
            r=source_decomposition(model,"cR_llpg",src_i,src_j)["neutral_fermion"]
            l=source_decomposition(model,"cL_llpg",src_i,src_j)["neutral_fermion"]
            # Native K2L=+cR/(8pi²v²); K2R=+cL/(8pi²v²).
            # Module3 CL=-native K2R; CR=-native K2L in verified convention.
            bz_module3=-np.array([l,r],dtype=complex)/(8*math.pi**2*inp["vev"]**2)
            plus=native_approx+bz_module3
            minus=native_approx-bz_module3
            src_one=saved["native_one_loop_BR_"+name]
            src_partial=saved["partial_Zee_one_loop_plus_corrected_neutral_fermion_BZ_BR_"+name]
            calc_one=rate(native_approx,ml,native_j)
            calc_plus=rate(plus,ml,native_j)
            calc_minus=rate(minus,ml,native_j)
            if min(calc_one,calc_plus,calc_minus)<=0:
                raise ArithmeticError("Nonpositive source-comparison radiative BR")
            channels[name]={
                "module3_independent_one_loop_CL_CR_GeV_minus2":list(map(c2,native_approx)),
                "corrected_author_neutral_BZ_cL_cR": [c2(l),c2(r)],
                "author_neutral_BZ_in_module3_CL_CR_GeV_minus2":list(map(c2,bz_module3)),
                "partial_signed_plus_CL_CR_GeV_minus2":list(map(c2,plus)),
                "partial_signed_minus_control_CL_CR_GeV_minus2":list(map(c2,minus)),
                "original_native_source_one_loop_BR":src_one,
                "original_native_plus_neutral_BZ_partial_BR":src_partial,
                "module3_one_loop_approx_BR":calc_one,
                "module3_plus_signed_BZ_approx_BR":calc_plus,
                "module3_minus_sign_control_BR":calc_minus,
                "relative_deviation_one_loop":calc_one/src_one-1,
                "relative_deviation_partial_plus":calc_plus/src_partial-1,
                "relative_deviation_partial_minus":calc_minus/src_partial-1,
                "source_exact_complex_native_K2_confirmed":False,
                "full_Zee_two_loop":None,
            }
            print("TAU_COMPLEX_REUSE",card,name,
                  "module3_1L_over_native",f"{calc_one/src_one:.8g}",
                  "signed_plus_over_saved_partial",f"{calc_plus/src_partial:.8g}",
                  "opposite_minus_over_saved_partial",f"{calc_minus/src_partial:.8g}",
                  "signed_BZ_CLCR",list(map(c2,bz_module3)),flush=True)
        out[card]={"frozen_benchmark_id":w["id"],"channels":channels}
    return {
        "status":"PINNED_CORRECTED_AUTHOR_COMPLEX_NEUTRAL_BZ_REUSED_WITH_MODULE3_APPROX_ONELOOP_ONLY",
        "gitlab_revision":revision,
        "gitlab_thdm_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
        "frozen_card_sha256":SOURCE_SHA,
        "source_sign_mapping":"Native K2L=+cR/(8pi²v²), K2R=+cL/(8pi²v²); Module3 CL=-K2R, CR=-K2L",
        "precision_warning":"Module3 analytic one-loop not the exact persisted complex native source. Model3 on-shell external-invariant approximation and authors' scheme differ; compare rate residuals, do not promote to source-matched physical amplitude.",
        "future_complex_source_input_needed":True,
        "full_Zee_gauge_completed_BZ":None,
        "cards":out,"physical_lfv":"UNKNOWN","global_acceptance":None,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=pathlib.Path,required=True)
    ap.add_argument("--commit",default=EXPECTED_COMMIT)
    ap.add_argument("--output",type=pathlib.Path)
    args=ap.parse_args()
    x=run(args.source,args.commit)
    if args.output:
        if args.output.exists():raise FileExistsError("Refusing output overwrite")
        args.output.write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("PHYSICAL_LFV UNKNOWN; exact original complex SARAH source not in public repo.")


if __name__=="__main__":
    main()
