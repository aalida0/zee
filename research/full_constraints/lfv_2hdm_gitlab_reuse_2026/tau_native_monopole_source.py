#!/usr/bin/env python3
"""Source-matched restricted Zee tau photon K1/K2 -> three-lepton rates.

Based on original SARAH 4.15.4 Gamma2l AO1/2 source fragments, the
public original SARAH Photon_wrapper.m, and the original FlavorKit
Calculate_Lto3Lp/LtoL1L2L2 rate formula. Fully signed *photonic only*:
no neutral tree, Z, boxes, finite-q2 or gauge-complete mixed Zee two-loop.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
K1_JSON=ROOT/"ORIGINAL_NATIVE_TAU_K1_REPLAY_2026-11-10.json"
K2_JSON=ROOT/"ORIGINAL_NATIVE_TAU_K2_REPLAY_2026-11-10.json"
EXPECTED=("D7_NO","D7_IO","F13_NO","F13_IO")
SHA={
 "generated":"2d30006d8d4759b2b7bfe76e2e4795bd2cf2f19ef5cb5772390ed3155b1bc41d",
 "couplings":"a0de851498f3e68e7421538098b3979381a3ecf5245021fce9d1c2df46a42e8c",
 "loops":"8142a813fcc00283d1de2865266be04ff1de25c09422b24b04d57523a6595a24",
}
ALPHA=1/127.95
MTAU=1.77686
GAMMA_TAU=6.582119569e-25/(290.3e-15)
ME=0.00051099895
MMU=0.1056583755
BZ_SOURCE_SHA="9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193"


def complex_pair(x):
    if not isinstance(x,list) or len(x)!=2 or any(type(y) not in (int,float) or not math.isfinite(y) for y in x):
        raise ValueError("Complex Wilson requires finite [real,imag]")
    return complex(x[0],x[1])


def photon_rate(K1L,K1R,K2L,K2R,mfinal,mpair,alpha=ALPHA):
    """Exact source leading-log photon-only observable, *not* full physical BR.

    For same flavor: D=(16 log(M/m)-22)/3; V=|K1L|²+|K1R|²;
    I=-4 Re(K2L K1R* + K2R K1L*).
    For mixed negative daughter and pair: D=16/3 log(M/mpair)-8,
    V=(2/3)|K1|²; I=-(8/3) Re(...).
    """
    if any(not math.isfinite(x) or x<=0 for x in (mfinal,mpair,alpha)) or mfinal+2*mpair>=MTAU:
        raise ValueError("Unphysical channel")
    ks=[complex(K1L),complex(K1R),complex(K2L),complex(K2R)]
    if any(not math.isfinite(z.real) or not math.isfinite(z.imag) for z in ks):
        raise ValueError("Nonfinite source Wilson")
    same=mfinal==mpair
    if same:
        dip=(16*math.log(MTAU/mpair)-22)/3
        vec=1.
        mix=-4.
    else:
        dip=(16/3)*math.log(MTAU/mpair)-8
        vec=2/3
        mix=-8/3
    norm=(4*math.pi*alpha)**2*MTAU**5/(512*math.pi**3*GAMMA_TAU)
    D=norm*dip*(abs(K2L)**2+abs(K2R)**2)
    V=norm*vec*(abs(K1L)**2+abs(K1R)**2)
    I=norm*mix*(K2L*K1R.conjugate()+K2R*K1L.conjugate()).real
    if D+V+I< -1e-14*max(abs(D),abs(V),abs(I),1e-100):
        raise ArithmeticError("Negative photonic squared source amplitude")
    return {
        "dipole_leading_log_BR":D,
        "K1_squared_BR":V,
        "signed_K1_K2_cross_BR":I,
        "photon_only_source_BR":max(0.,D+V+I),
        "K1_fractional_correction_to_dipole":(V+I)/D if D else None,
        "identical_final_leptons":same,
        "physical_total_BR":None,
    }


def evaluate(k1_path=K1_JSON,k2_path=K2_JSON,corrected_bz_path=None):
    k1=json.loads(Path(k1_path).read_text())
    k2=json.loads(Path(k2_path).read_text())
    if k1["source_sha256"]!=SHA or k2["fortran_sha256"]!=SHA:
        raise ValueError("Original generated source SHA contract mismatch")
    if (k1["benchmark_cards_sha256"]!="1472e0741671bd8e832e256ddafc371562ea446c3d7bba3ec0c"
            or set(k1["cards"])!=set(EXPECTED)
            or tuple(c["card"] for c in k2["cards"])!=EXPECTED):
        raise ValueError("Four-card benchmark provenance mismatch")
    checks=k1["complex_source_controls"]
    if (checks["max_full_minus_F_D_relative"]>1e-12
            or checks["max_F_K1L_plus_two_thirds_K2L_relative"]>1e-12
            or checks["zero_mode_absolute"]!=0):
        raise ValueError("Original F+D/zero/F-only source controls failed")
    bz=None
    if corrected_bz_path is not None:
        bz=json.loads(Path(corrected_bz_path).read_text())
        if (bz.get("gitlab_thdm_sha256")!=BZ_SOURCE_SHA
                or bz.get("full_Zee_gauge_completed_BZ") is not None
                or set(bz.get("cards",{}))!=set(EXPECTED)):
            raise ValueError("Corrected authors' source lock failed")
    result={}
    e=math.sqrt(4*math.pi*ALPHA)
    for card,row in zip(EXPECTED,k2["cards"]):
        if row["card"]!=card:
            raise ValueError("Source channel order mismatch")
        channels={}
        for name,flavor,ma,mb in (
            ("tau_to_3e","tauegamma",ME,ME),
            ("tau_to_3mu","taumugamma",MMU,MMU),
            ("tau_to_e_minus_mu_minus_mu_plus","tauegamma",ME,MMU),
            ("tau_to_mu_minus_e_minus_e_plus","taumugamma",MMU,ME),
        ):
            k1part=k1["cards"][card][flavor]
            k2part=row["channels"][flavor]
            k1L=complex_pair(k1part["OA1L"])/e
            k1R=complex_pair(k1part["OA1R"])/e
            k2L=complex_pair(k2part["K2L"])
            k2R=complex_pair(k2part["K2R"])
            if bz:
                orig=bz["cards"][card]["channels"][flavor]["author_neutral_BZ_in_module3_CL_CR_GeV_minus2"]
                # Original native K2L=-Module3 CR, native K2R=-Module3 CL.
                k2L-=complex_pair(orig[1])
                k2R-=complex_pair(orig[0])
            channels[name]=photon_rate(k1L,k1R,k2L,k2R,ma,mb)
        result[card]=channels
    return {
        "status":"SIGNED_NATIVE_K1_K2_AND_CORRECTED_NEUTRAL_FERMION_BZ_PHOTON_SUBSET_ONLY",
        "source_original_sarah_sha256":SHA,
        "source_wrapper":"SARAH FlavorKit Photon_wrapper.m, Zee-Toolbox blob 8fd5c9cd",
        "source_observable":"FlavorKit_Observables_Zee.f90 blob 0ad7d169",
        "alpha_matching":ALPHA,
        "neutral_fermion_bz_included":bz is not None,
        "approximation":"Source leading-log photons, constant K1,K2 evaluated at q2=0. No finite-q2, scalar/Z/box or complete Zee 2loop",
        "full_Zee_two_loop_included":False,
        "physical_lfv":"UNKNOWN",
        "global_acceptance":None,
        "cards":result,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--k1-json",type=Path,default=K1_JSON)
    p.add_argument("--k2-json",type=Path,default=K2_JSON)
    p.add_argument("--corrected-neutral-bz",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    data=evaluate(a.k1_json,a.k2_json,a.corrected_neutral_bz)
    for card,chans in data["cards"].items():
        for ch,x in chans.items():
            print("SOURCE_PHOTON_ONLY",card,ch,
                  f"{x['photon_only_source_BR']:.11e}",
                  "K1_delta_ratio",f"{x['K1_fractional_correction_to_dipole']:.7g}")
    if a.output:
        if a.output.exists():raise FileExistsError("Refusing to overwrite")
        a.output.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("PHYSICAL_LFV UNKNOWN: photons only, not full Zee two-loop")


if __name__=="__main__":
    main()
