#!/usr/bin/env python3
"""Source-audited Section 8 exact family-dependent Z2 operator check.

One concrete Z2 texture from Primulando/Julio/Uttayarat,
EPJC 82 (2022) 253, with additional consistent TYPE-II quark
charges; not the fully general original Zee lepton texture.
All charges are +1/-1 and all conjugate fields have the same
Z2 charge.

A symmetry-invariant dimension-4 Yukawa coupling is permitted.
Soft m12sq term is explicitly odd, allowed only as SOFT breaking.
Nonzero k12 is dimension-4 HARD breaking and cannot coexist with
an exact protective Z2 in the same scalar potential.
"""
from __future__ import annotations
import json

STATUS="ZEE_FAMILY_Z2_OPERATOR_AUDIT_NO_NEUTRINO_FIT"
CHARGE={
    "Phi1":+1,"Phi2":-1,"chi":-1,
    "QL":+1,"uR":-1,"dR":+1,
    "Le":-1,"Lmu":+1,"Ltau":+1,
    "eR":+1,"muR":+1,"tauR":+1,
}

OPERATORS={
    "up_to_Phi2":("QL","Phi2","uR"),
    "up_wrong_Phi1":("QL","Phi1","uR"),
    "down_to_Phi1":("QL","Phi1","dR"),
    "down_wrong_Phi2":("QL","Phi2","dR"),
    "lepton_e_to_Phi2":("Le","Phi2","eR"),
    "lepton_e_wrong_Phi1":("Le","Phi1","eR"),
    "lepton_mu_to_Phi1":("Lmu","Phi1","muR"),
    "lepton_mu_wrong_Phi2":("Lmu","Phi2","muR"),
    "lepton_tau_to_Phi1":("Ltau","Phi1","tauR"),
    "f_e_mu_chi":("Le","Lmu","chi"),
    "f_e_tau_chi":("Le","Ltau","chi"),
    "f_mu_tau_chi":("Lmu","Ltau","chi"),
    "mu4_Phi1_Phi2_chi":("Phi1","Phi2","chi"),
    "m12sq_Phi1dag_Phi2_SOFT":("Phi1","Phi2"),
    "k12_Phi1dag_Phi2_chichi_HARD":("Phi1","Phi2","chi","chi"),
    "lambda5_Phi1dagPhi2_squared":("Phi1","Phi2","Phi1","Phi2"),
}

def sign(fields,charges=CHARGE):
    ans=1
    for f in fields:ans*=charges[f]
    return ans

def report():
    signs={k:sign(fields) for k,fields in OPERATORS.items()}
    required={
        "up_to_Phi2":1,"up_wrong_Phi1":-1,
        "down_to_Phi1":1,"down_wrong_Phi2":-1,
        "lepton_e_to_Phi2":1,"lepton_e_wrong_Phi1":-1,
        "lepton_mu_to_Phi1":1,"lepton_mu_wrong_Phi2":-1,
        "lepton_tau_to_Phi1":1,
        "f_e_mu_chi":1,"f_e_tau_chi":1,"f_mu_tau_chi":-1,
        "mu4_Phi1_Phi2_chi":1,
        "m12sq_Phi1dag_Phi2_SOFT":-1,
        "k12_Phi1dag_Phi2_chichi_HARD":-1,
        "lambda5_Phi1dagPhi2_squared":1,
    }
    if signs!=required:
        raise AssertionError("Charge assignment does not enforce advertised operators")
    return {
        "status":STATUS,
        "scalar_potential_choice":"Florentino restricted lambda6=lambda7=0; exact Z2 quartics require k12=0",
        "z2_charge_assignments":CHARGE,
        "operator_invariant_signs":signs,
        "quark_tree_FCNC_forbidden_by_Yukawa_texture":True,
        "full_complex_mass_basis_B2_Yukawa_families_checked":False,
        "published_P2_nonzero_k12_is_exact_Z2_consistent":False,
        "m12sq_is_soft_spurion_not_Z2_invariant":True,
        "physical_neutrino_and_LFV_fit_done":False,
    }

if __name__=="__main__":
    result=report()
    print(json.dumps(result,indent=2))
