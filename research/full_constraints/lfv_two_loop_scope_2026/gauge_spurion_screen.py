#!/usr/bin/env python3
"""Exact Zee charged-current mixing identities and source-locked sensitivity.

NOT a gauge-complete two-loop amplitude. This screens a hypothetical
F†F dressing deltaC = [g²/(16pi²)] K C_F only; K is unknown.
"""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
from module2.interface import decode
from research.full_constraints.lfv_2hdm_transfer_2026.evaluate import read_cards

ROOT=Path(__file__).resolve().parents[3]
SCOPE=ROOT/"research/full_constraints/lfv_precision_scope_2026/SCOPE_DIAGNOSTICS.json"
NATIVE=ROOT/"research/full_constraints/lfv_lo_closure_2026/NATIVE_COMPLETE_ONELOOP_LFV_FOUR_CARD_GATE_2026-11-10.json"
IDS=("D7_NO","D7_IO","F13_NO","F13_IO")
ALPHA=1/127.95
SW2=0.23129
V=246.22
MMU=0.1056583755
ME=0.00051099895
GAMMA_MU=6.582119569e-25/2.1969811e-6
MEGII=1.5e-13

def currents(gamma:float)->dict:
    if not math.isfinite(gamma):raise ValueError("invalid mixing")
    c,s=math.cos(gamma),math.sin(gamma)
    u=np.array([c,-s]);v=np.array([s,c])
    p=np.outer(u,u);q=np.eye(2)
    return {"u":u,"v":v,"P":p,"Q":q,"Z_over_g_cW":.5*p-SW2*q}

def lepton_conserving_spurion_allowed(nmu:int,nconj:int)->bool:
    """Necessary L=0 condition with L(chi+)=-2, L(mu4)=-2."""
    if type(nmu)!=int or type(nconj)!=int or min(nmu,nconj)<0:
        raise ValueError("nonnegative integer spurion multiplicities")
    return nmu==nconj

def evaluate():
    cards=read_cards()
    s=json.loads(SCOPE.read_text())
    n=json.loads(NATIVE.read_text())
    if (len(cards)!=4 or len(s["cards"])!=4 or len(n["cards"])!=4
        or s["original_D12_sha256"]!="f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8"
        or n["physical_lfv"]!="UNKNOWN" or n["global_acceptance"] is not None):
        raise ValueError("source provenance/physical status mismatch")
    g2=4*math.pi*ALPHA/SW2
    eps=g2/(16*math.pi**2)
    norm=ALPHA*MMU**5/(4*GAMMA_MU)
    clim=math.sqrt(MEGII/norm)
    result={}
    for name,w,scope,native in zip(IDS,cards,s["cards"],n["cards"]):
        if w["id"]!=scope["id"] or name!=native["id"]:
            raise ValueError("four original benchmark IDs changed")
        p=w["module2_input"]["scalar"]["record"]["physical"]
        F=decode(w["yukawas"]["F"])
        D=decode(w["yukawas"]["D"])
        g=p["gamma"];m1=p["mH1"];m2=p["mH2"]
        if m1<=0 or m2<=0:raise ValueError("invalid charged masses")
        c,sin=math.cos(g),math.sin(g)
        J=currents(g);u,v=J["u"],J["v"]
        inv=np.diag([m1**-2,m2**-2])
        mix=float(u@inv@v)
        mix_expected=c*sin*(m1**-2-m2**-2)
        if abs(mix-mix_expected)>1e-18:
            raise ArithmeticError("charged mixing propagator identity failed")
        fprod=(F.conj().T@F)[0,1]
        weight=sin**2/m1**2+c**2/m2**2
        cf=abs(fprod)*weight/(192*math.pi**2)
        if (abs(abs(fprod)/scope["FdagF_e_mu_abs"]-1)>1e-12
             or abs(cf/scope["CR_F_only_abs_GeV_minus2"]-1)>1e-12):
            raise ArithmeticError("frozen F sector no longer matches published source gate")
        cF_vector=cf*math.sqrt(1+(ME/MMU)**2)
        lone=math.sqrt(native["one_loop_muegamma_BR"]/norm)
        if lone>=clim:raise ArithmeticError("source one-loop baseline above experimental limit")
        crit=(clim-lone)/(eps*cF_vector)
        mu4=-math.sqrt(2)/V*(m1*m1-m2*m2)*sin*c
        if abs(mu4+math.sqrt(2)/V*float(u@np.diag([m1*m1,m2*m2])@v))>1e-10:
            raise ArithmeticError("charged mass mixing/µ4 identity failed")
        result[name]={
            "card":w["id"],"FdagF_e_mu_abs":abs(fprod),
            "max_D_abs":float(np.max(np.abs(D))),
            "direct_D_e_mu_max":max(abs(D[0,1]),abs(D[1,0])),
            "doublet_singlet_mixed_weight_GeVminus2":mix,
            "Z12_over_g_cW":float(J["Z_over_g_cW"][0,1]),
            "mu4_GeV":mu4,
            "source_F_one_loop_dominant_chirality_C_abs_GeVminus2":cf,
            "source_F_one_loop_full_chirality_norm_GeVminus2":cF_vector,
            "native_source_one_loop_BR":native["one_loop_muegamma_BR"],
            "MEGII_90CL_BR":MEGII,
            "source_matched_coefficient_headroom_GeVminus2":clim-lone,
            "EW_loop_factor_g2_over_16pi2":eps,
            "conditional_missing_F_dressing_K_threshold":crit,
            "physical_missing_K_bound":None,
            "complete_Zee_two_loop_K":None,
            "physical_lfv":"UNKNOWN",
        }
    return {
        "status":"EXACT_CHARGED_CURRENT_IDENTITIES_AND_CONDITIONAL_F_DRESSING_SCREEN",
        "scope":"LO F†F gauge-dressing sensitivity ONLY; not complete two-loop calculation",
        "source":"Four SHA256-locked original D12 cards, earlier source-matched F-only one-loop gate and original native one-loop BRs",
        "photon_charge_operator":"Identity in both mass bases: no offdiagonal photon vertex",
        "Z_charge_operator":"(1/2)P_doublet - sin²thetaW I, physical Z12=-cos(gamma)sin(gamma)/2 (units g/cW)",
        "charged_mixed_loop_identity":"u^T diag(f(m1²),f(m2²)) v = cos(gamma)sin(gamma)[f(m1²)-f(m2²)]",
        "lepton_number_spurion":"L(chi+)=-2 and L(mu4)=-2; L-conserving dipole with one unpaired mu4 spurion forbidden; this does not remove F†F gauge dressing or multi-insertion loops",
        "K_interpretation":"K threshold only conditional on deltaC_vector=eps*K*C_F_vector including the mass-suppressed mirror chirality; not estimate/bound of missing Zee gauge loop or any new invariant",
        "complete_all_two_loop_Zee":False,
        "physical_lfv":"UNKNOWN","global_acceptance":None,"cards":result,
    }

if __name__=="__main__":
    import argparse
    a=argparse.ArgumentParser()
    a.add_argument("--output",type=Path)
    v=a.parse_args()
    out=evaluate()
    for k,r in out["cards"].items():
        print(k,"Kthreshold",f'{r["conditional_missing_F_dressing_K_threshold"]:.9g}',
              "Z12",f'{r["Z12_over_g_cW"]:.9g}',"mu4_GeV",f'{r["mu4_GeV"]:.6g}')
    print("COMPLETE_ZEE_TWOLOOP_UNKNOWN; PHYSICAL_LFV_UNKNOWN")
    if v.output:
        if v.output.exists():raise FileExistsError("no overwrite")
        v.output.write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
