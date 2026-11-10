#!/usr/bin/env python3
"""QED diagonal-dipole leading-log Zee subset below mW; NOT full Zee 2loop.

Literature source: EPJC 84 (2024) article DOI 10.1140/epjc/s10052-024-12782-x,
Eq. (4.4), C_D(m_l)/C_D(M)=1-16*alpha/(4pi)*log(M/m_l).
The source operates in a normalized low-energy LFV dipole EFT; input scheme,
running alpha, threshold matching, and mixing from other operators are NOT
included. Applying to original Zee one-loop native K2 is only a diagnostic.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_native_monopole_source import (
    EXPECTED, SHA, complex_pair, BZ_SOURCE_SHA, K2_JSON, MTAU
)

ALPHA_ZERO=1/137.035999084
MW=80.379


def diagonal_qed_factor(upper=MW,lower=MTAU,alpha=ALPHA_ZERO):
    if any(not math.isfinite(x) or x<=0 for x in (upper,lower,alpha)) or upper<lower:
        raise ValueError("positive ordered QED scales required")
    return 1-16*alpha/(4*math.pi)*math.log(upper/lower)


def compute(bz_json:Path,native_k2:Path=K2_JSON,upper=MW):
    native=json.loads(Path(native_k2).read_text())
    bz=json.loads(Path(bz_json).read_text())
    if (native.get("fortran_sha256")!=SHA
            or tuple(x["card"] for x in native["cards"])!=EXPECTED):
        raise ValueError("Unverified original Zee source")
    if (bz.get("gitlab_thdm_sha256")!=BZ_SOURCE_SHA
            or bz.get("full_Zee_gauge_completed_BZ") is not None
            or set(bz.get("cards",{}))!=set(EXPECTED)):
        raise ValueError("Unverified restricted corrected author source")
    factor=diagonal_qed_factor(upper)
    out={}
    for card in native["cards"]:
        name=card["card"]
        channels={}
        for flavor in ("tauegamma","taumugamma"):
            v=card["channels"][flavor]
            # Native K2L=-Module3 CR, native K2R=-Module3 CL.
            lo=[-complex_pair(v["K2R"]),-complex_pair(v["K2L"])]
            bz2=[complex_pair(x) for x in bz["cards"][name]["channels"][flavor]["author_neutral_BZ_in_module3_CL_CR_GeV_minus2"]]
            current=[x+y for x,y in zip(lo,bz2)]
            shifted=[factor*x+y for x,y in zip(lo,bz2)]
            norm=lambda a:sum(abs(x)**2 for x in a)
            ratio=norm(shifted)/norm(current)
            channels[flavor]={
                "native_Zee_one_loop_CL_CR":[[z.real,z.imag] for z in lo],
                "corrected_2HDM_neutral_fermion_BZ_CL_CR":[[z.real,z.imag] for z in bz2],
                "low_energy_diagonal_QED_amplitude_factor":factor,
                "one_loop_plus_restricted_BZ_BR_ratio_after_diagonal_QED_LL":ratio,
                "fractional_shift_in_restricted_partial_rate":ratio-1,
                "physical_radiative_BR":None,
                "missing_mixed_Zee_electroweak_2loop":True
            }
        out[name]=channels
    return {
        "status":"UNIVERSAL_QED_DIAGONAL_DIPOLE_LEADING_LOG_DIAGNOSTIC_NOT_FULL_ZEE",
        "source_D0_EFTrunning":"EPJC2024 12782-x Eq(4.4), gamma_D=16",
        "upper_QED_scale_GeV":upper,
        "lower_QED_scale_GeV":MTAU,
        "alpha_fixed":ALPHA_ZERO,
        "diagonal_factor":factor,
        "pure_one_loop_rate_scaling":factor**2,
        "operator_mixing_omitted":True,
        "EW_matching_omitted":True,
        "alpha_running_omitted":True,
        "all_Zee_2loop":False,
        "physical_lfv":"UNKNOWN",
        "global_acceptance":None,
        "cards":out
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--corrected-neutral-bz",type=Path,required=True)
    p.add_argument("--native-k2",type=Path,default=K2_JSON)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=compute(a.corrected_neutral_bz,a.native_k2)
    for card,chans in result["cards"].items():
        for ch,row in chans.items():
            print("QED_LL_RESTRICTED",card,ch,
                  f"{row['fractional_shift_in_restricted_partial_rate']:.9e}")
    if a.output:
        if a.output.exists():raise FileExistsError("Refusing overwrite")
        a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("PHYSICAL_LFV UNKNOWN; gauge-complete Zee mixed electroweak two-loop not computed")


if __name__=="__main__":
    main()
