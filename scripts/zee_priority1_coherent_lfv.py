#!/usr/bin/env python3
"""Coherent Zee l_i -> l_j gamma amplitude assembly, exact interference.

Unlike a sum of separate branching fractions, all contributions must
be added as COMPLEX Wilson amplitudes in one common operator convention.
This only calculates a full rate if the physics backend really supplies
ALL independently validated contributions, including fermion/W/scalar
Barr-Zee terms. It does NOT compute missing two-loop integrals or mu-e
conversion by itself; never call an incomplete sum 'complete'.
"""
from __future__ import annotations
import math
ALPHA=1/137.035999084
GF=1.1663787e-5
PARTS=("one_loop_neutral","one_loop_charged_Y",
       "one_loop_charged_f","two_loop_Barr_Zee_fermion",
       "two_loop_Barr_Zee_W","two_loop_Barr_Zee_scalar")
CHANNELS=("mu_to_e_gamma","tau_to_mu_gamma","tau_to_e_gamma")

def as_complex(pair,label):
    if not isinstance(pair,(tuple,list)) or len(pair)!=2:
        raise ValueError("Complex "+label+" requires [Re,Im]")
    if any(isinstance(v,bool) for v in pair):
        raise ValueError("Boolean coefficient")
    z=complex(float(pair[0]),float(pair[1]))
    if not(math.isfinite(z.real) and math.isfinite(z.imag)):
        raise ValueError("Nonfinite dipole "+label)
    return z

def coherent_dipole(components,norm_br,*,all_diagrams_verified=False,
                    common_operator_convention=False):
    if not isinstance(components,dict):
        raise ValueError("Components must be named amplitudes")
    if not set(components).issubset(PARTS) or not components:
        raise ValueError("Unknown dipole amplitude topology")
    if isinstance(norm_br,bool) or not 0<float(norm_br)<=1:
        raise ValueError("Invalid leptonic normalization BR")
    CL=0j;CR=0j;parts={}
    for term,pair in components.items():
        if not isinstance(pair,dict):raise ValueError("Nonobject amplitude")
        l=as_complex(pair.get("CL_GeV_minus2"),term+" CL")
        r=as_complex(pair.get("CR_GeV_minus2"),term+" CR")
        CL+=l;CR+=r
        parts[term]=float(norm_br*48*math.pi**3*ALPHA/GF**2*
                          (abs(l)**2+abs(r)**2))
    value=float(norm_br*48*math.pi**3*ALPHA/GF**2*
                (abs(CL)**2+abs(CR)**2))
    complete=(set(components)==set(PARTS) and
              all_diagrams_verified is True and
              common_operator_convention is True)
    return {
      "BR_coherent_amplitude_sum":value,
      "CL_total_GeV_minus2":[CL.real,CL.imag],
      "CR_total_GeV_minus2":[CR.real,CR.imag],
      "individual_BR_if_alone_NOT_ADDITIVE":parts,
      "interference_term_BR":value-sum(parts.values()),
      "all_six_amplitude_classes_present":set(components)==set(PARTS),
      "all_amplitudes_common_convention_and_independently_verified":
          bool(complete),
      "full_radiative_LFV_rate_certified":bool(complete),
      "full_Zee_LFV_likelihood_evaluated":False,
      "Zee_allowed_or_excluded":None,
    }

def evaluate_all(channels):
    """Assemble all three radiative channels; 3-body and mu-e remain separate."""
    if set(channels)!=set(CHANNELS):raise ValueError("Three channels required")
    out={}
    for name,entry in channels.items():
        if not isinstance(entry,dict):raise ValueError("Invalid LFV channel")
        out[name]=coherent_dipole(
            entry["components"],entry["norm_br"],
            all_diagrams_verified=entry.get("all_diagrams_verified") is True,
            common_operator_convention=entry.get("common_operator_convention") is True)
    return {"status":"COHERENT_LFV_RADIATIVE_DIPOLES_NO_CONVERSION_OR_3BODY",
            "radiative":out,"full_lfv_constraints_computed":False,
            "all_Zee_allowed_or_excluded":None}
