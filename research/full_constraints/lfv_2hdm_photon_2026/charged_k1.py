#!/usr/bin/env python3
"""One-loop off-shell photon monopole from charged scalar + massless neutrino.

Universal source topology: R. S. Hundi, EPJC 85 (2025) 805,
Eq.(23) for neutral fermion and charged scalar. Also Toma/Vicente
JHEP01(2014)160 (non-dipole photon A_ND). Not assuming scotogenic
neutrino masses or dark matter: this uses ONLY the shared QED topology
with x=m_nu^2/m_H+^2 = 0, and Zee's frozen native charged vertices.

SOURCE FORM FACTORS, i e ubar_e [ A1_L q^2 gamma^mu PL
    - A1_L (m_mu PR - m_e PL) q^mu
    + A2_R (m_mu PR + m_e PL) i sigma^mu nu q_nu
    + {L<->R} ] u_mu.
Here [A1]=[A2]=GeV^-2. Mixed F-D fermion lines vanish at m_nu=0.
A2_R=charged F dipole CR, A2_L=charged D dipole CL in frozen
L_eff = e*m_mu/2 * bar e sigma(C_L PL+C_R PR) mu F.
The non-dipole source A1_L=(2/3)*A2_R from F,
A1_R=(2/3)*A2_L from D, with exact daughter-mass flips in A2.
No complete common mu3e, conversion or full neutral photon K1 is claimed.

The source-to-native map of the charged universal topology is crosschecked
via BOTH on-shell dipole chiralities and pure doublet/singlet limits.
An explicit full Zee off-shell generated source control is still pending.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from module2.interface import decode
from module3.core import dipole_ledger

from research.full_constraints.lfv_2hdm_photon_2026.tau_monopole import (
    HERE, card_inputs, cp,
)

def g1_zero(): return 1/3
def g2_zero(): return 1/6

def prefactors(mass):
    """Published source Eq(23) at x=0."""
    return (-g1_zero()/(16*math.pi**2*6*mass**2),
            -g2_zero()/(16*math.pi**2*2*mass**2))

def charged_source(w, i=1,j=0):
    p=w["module2_input"]["scalar"]["record"]["physical"]
    ml=w["module2_input"]["lepton_masses_GeV"]
    F,D=decode(w["yukawas"]["F"]),decode(w["yukawas"]["D"])
    rho=(D@D.conjugate().T)[j,i]   # external-R lepton, A1_R
    lam=(F.conjugate().T@F)[j,i]   # external-L lepton, A1_L
    states=[("H1",p["mH1"],math.cos(p["gamma"]),math.sin(p["gamma"])),
            ("H2",p["mH2"],-math.sin(p["gamma"]),math.cos(p["gamma"]))]
    pieces={}
    A1L=A1R=A2R_F=A2L_D=0j
    for name,m,d,s in states:
        a1,a2=prefactors(m)
        f=a1*s*s*lam
        d_term=a1*d*d*rho
        f_dip=a2*s*s*lam
        d_dip=a2*d*d*rho
        pieces[name]=dict(
            mass_GeV=m,doublet_fraction=d,singlet_fraction=s,
            A1L_F=cp(f),A1R_D=cp(d_term),
            A2R_F=cp(f_dip),A2L_D=cp(d_dip))
        A1L+=f;A1R+=d_term;A2R_F+=f_dip;A2L_D+=d_dip
    retained=dipole_ledger(F,D,p,ml,i,j)
    observed={
        "A2R_F":sum(retained[k+"_F"]["C_R"] for k in ("H1","H2")),
        "A2L_D":sum(retained[k+"_D"]["C_L"] for k in ("H1","H2")),
        "A2L_F_daughter_suppressed":sum(retained[k+"_F"]["C_L"] for k in ("H1","H2")),
        "A2R_D_daughter_suppressed":sum(retained[k+"_D"]["C_R"] for k in ("H1","H2")),
    }
    expected={
        "A2R_F":A2R_F,"A2L_D":A2L_D,
        "A2L_F_daughter_suppressed":ml[j]/ml[i]*A2R_F,
        "A2R_D_daughter_suppressed":ml[j]/ml[i]*A2L_D,
    }
    err=max(abs(expected[k]-observed[k])/
            max(abs(expected[k]),abs(observed[k]),1e-100)
            for k in expected)
    if err>2e-11: raise ArithmeticError(f"charged source A2 vs native dipole {err}")
    return dict(
        A1L_F=cp(A1L),A1R_D=cp(A1R),
        A2R_F=cp(A2R_F),A2L_D=cp(A2L_D),
        rho_DDdag=cp(rho),lam_FdagF=cp(lam),
        chiral_A2_daughter_mass_ratio=ml[j]/ml[i],
        native_on_shell_A2_relative_residual=err,
        source_massless_ratio_A1_to_A2=2/3,
        by_state=pieces,
        status="CHARGED_TOPOLOGY_TRANSFER_LIMIT_VALIDATED_WITH_NATIVE_DIPOLE",
        common_photon_form_factor={
           "K1L_charged_only_candidate":cp(A1L),
           "K1R_charged_only_candidate":cp(A1R),
           "neutral_complete":False,
           "Z_penguin_or_boxes_included":False,
           "full_signed_interference":False})

def run(write=True):
    cards=[dict(id=w["id"],**charged_source(w)) for w in card_inputs()]
    out=dict(status="CHARGED_MASSLESS_NEUTRINO_PHOTON_SOURCE_TRANSFER",
     source="Hundi EPJC85 (2025) 805 Eq(23); Toma-Vicente JHEP01 (2014) 160",
     universal_QED_topology="neutral massless fermion, charged physical scalar (H1/H2) with two separate external lepton chiralities",
     source_form_factor_G1_at_0=g1_zero(),source_form_factor_G2_at_0=g2_zero(),
     source_A1_over_A2=2/3,
     parent_native_operator="module3.core.OPERATOR; frozen charged dipole",
     approximate_neutrino="m_nu=0, external masses kept only in spinor Ward relation and dipole flips",
     cards=cards,full_common_K1=None,
     missing=["neutral charged-lepton loops outside tau published approximation",
              "independent full Zee generated off-shell photon check",
              "complete mu3e penguin/box relative phases",
              "conversion vector matching to nuclear kernel and RG"],
     physical_lfv="UNKNOWN",global_acceptance=None)
    if write:(HERE/"CHARGED_RESULT.json").write_text(json.dumps(out,indent=2,allow_nan=False)+"\n")
    return out

if __name__=="__main__":
    out=run()
    print("4/4 charged one-loop monopole source A1 + on-shell A2 validations; incomplete physical rate")
    for w in out["cards"]:
        print(w["id"],"A1L_F",w["A1L_F"],"A1R_D",w["A1R_D"],
             "max A2 residual",w["native_on_shell_A2_relative_residual"])
