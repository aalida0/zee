#!/usr/bin/env python3
"""Published *restricted* neutral-tau photon monopole in Zee/Type-II.

Source: Herrero-Garcia, Ohlsson, Riad, Wiren, JHEP04 (2017) 130,
Eq.(3.25), neutral tau-loop and q^2->0 limit only.
This is NOT the complete 2HDM/charged-Zee off-shell photon K1.

The published gLV and gRV are in the Eq.(3.24)-(3.25) source vector
normalization [GeV^-2]. Their conversion to a standalone native K1
in the common photon/Z/boxes 4-fermion operator basis is NOT certified.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from module2.interface import decode
from module3.core import vertices

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
ARCHIVE=ROOT/"validation/module12/d12_benchmarks.json"
SHA="f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8"
ALPHA=1/137.035999084

def cp(z):
    z=complex(z)
    assert math.isfinite(z.real) and math.isfinite(z.imag)
    return [z.real,z.imag]

def card_inputs():
    raw=ARCHIVE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==SHA
    cards=[g["witnesses"]["low_joint"] for g in json.loads(raw)["groups"]]
    assert [w["id"] for w in cards]==[
        "d7_NO_neutral_near_heavy_07/NO/texture_0.0001",
        "d7_NO_neutral_near_heavy_07/IO/texture_0.0001",
        "F13_heavy_0001330/NO/texture_0.001",
        "F13_heavy_0001330/IO/texture_0.001"]
    return cards

def paper_prefactor(mtau,mphi,alpha=ALPHA):
    """Eq(3.25): (alpha/(2*pi))*(-1/(9*mphi^2))*(4+3*ln(mtau^2/mphi^2))"""
    assert mtau>0 and mphi>0 and 0<alpha<1
    return -alpha/(18*math.pi*mphi**2)*(4+3*math.log((mtau/mphi)**2))

def source_tau_monopole(w,alpha=ALPHA):
    """Real neutral scalar h/H/A only; internal charged tau only.

    Source gLV: sum prefactor * C_(tau,mu) C_(tau,e)^*
    Source gRV: sum prefactor * C_(mu,tau)^* C_(e,tau)

    Native D is RH row / LH column and rho_l=D/sqrt2.
    This preserves tau-row and tau-column oriented phases separately.
    """
    p=w["module2_input"]["scalar"]["record"]["physical"]
    ml=w["module2_input"]["lepton_masses_GeV"]
    cs=vertices(decode(w["yukawas"]["D"]),p,ml)
    left=right=0j
    details={}
    for name,(C,mass) in cs.items():
        fac=paper_prefactor(ml[2],mass,alpha)
        lv=fac*C[2,1]*C[2,0].conjugate()
        rv=fac*C[1,2].conjugate()*C[0,2]
        left+=lv;right+=rv
        details[name]={"mass_GeV":mass,"gLV_GeV_minus2":cp(lv),
                       "gRV_GeV_minus2":cp(rv),
                       "prefactor_GeV_minus2":fac}
    return dict(gLV=left,gRV=right,by_scalar=details)

def source_y2_independent(w,alpha=ALPHA):
    """Independent paper Eq(2.18)-(2.20) implementation using Ye2 itself.

    For native h/H mixing, g2 factors are [-sin(delta),cos(delta),-i] /
    (sqrt(2)*cos(beta)) instead of copying the source authors' alpha
    parameter; the latter is a different angle convention.
    Off-diagonal Ye2 = cos(beta)*D exactly in mass basis.
    """
    p=w["module2_input"]["scalar"]["record"]["physical"]
    y2=decode(w["yukawas"]["Ye2"])
    mtau=w["module2_input"]["lepton_masses_GeV"][2]
    delta=p["beta"]-p["alpha"]
    g={
        "h":-math.sin(delta)/(math.sqrt(2)*math.cos(p["beta"])),
        "H": math.cos(delta)/(math.sqrt(2)*math.cos(p["beta"])),
        "A":-1j/(math.sqrt(2)*math.cos(p["beta"])),
    }
    masses={"h":p["mh1"],"H":p["mh2"],"A":p["ma"]}
    return {
        "gLV":sum(paper_prefactor(mtau,masses[k],alpha)*abs(g[k])**2*
                 y2[2,1]*y2[2,0].conjugate() for k in g),
        "gRV":sum(paper_prefactor(mtau,masses[k],alpha)*abs(g[k])**2*
                 y2[1,2].conjugate()*y2[0,2] for k in g),
    }

def run(write=True):
    data=[]
    for w in card_inputs():
        p=w["module2_input"]["scalar"]["record"]["physical"]
        src=source_tau_monopole(w)
        independent=source_y2_independent(w)
        residual=max(abs(src[k]-independent[k])/
                 max(abs(src[k]),abs(independent[k]),1e-100)
                 for k in ("gLV","gRV"))
        if residual>1e-10: raise ArithmeticError((w["id"],residual))
        data.append(dict(id=w["id"],source_eq="JHEP04(2017)130 Eq(3.25)",
             gLV_source_tau_neutral_GeV_minus2=cp(src["gLV"]),
             gRV_source_tau_neutral_GeV_minus2=cp(src["gRV"]),
             by_scalar=src["by_scalar"],
             direct_vertices_vs_paper_Ye2_relative_residual=residual,
             full_common_K1L=None,full_common_K1R=None,
             full_mu3e_rate=None,physical_muAl_conversion=None,
             physics_status="RESTRICTED_TAU_NEUTRAL_SOURCE_SUBSET"))
    result=dict(
        status="RESTRICTED_2HDM_TAU_NEUTRAL_OFFSHELL_PHOTON",
        equation="g_X^V = -alpha/(18*pi)*sum_phi [(4+3*ln(mtau^2/mphi^2))/mphi^2] * (complex ordered Yukawa product)_X",
        source="https://doi.org/10.1007/JHEP04(2017)130 Eq.(3.25) + Eq.(2.18)-(2.20)",
        approximation="neutral h/H/A internal tau only; published q2->0 photon monopole formula",
        alpha_em=ALPHA,
        field_convention="native D RH-row/LH-col; source angle mapped via physical h/H",
        checks="native vertices compared to independent source Ye2 formula in all four complex cards",
        cards=data,
        missing=["neutral e/mu internal flavor (and external-mass effects)",
                 "charged doublet D photon monopole",
                 "charged singlet F photon monopole",
                 "source->common K1 sign/normalization and offshell Ward match",
                 "Z penguin and complete boxes and signed interference"],
        missing_common_K1=[None,None],
        physical_lfv="UNKNOWN",global_acceptance=None)
    if write: (HERE/"RESULT.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    return result

if __name__=="__main__":
    r=run()
    print("Four source tau-only neutral-photon monopole controls passed; no complete K1:")
    for c in r["cards"]:
        print(c["id"],"gLV=",c["gLV_source_tau_neutral_GeV_minus2"],
              "gRV=",c["gRV_source_tau_neutral_GeV_minus2"],
              "relative residual",c["direct_vertices_vs_paper_Ye2_relative_residual"])
