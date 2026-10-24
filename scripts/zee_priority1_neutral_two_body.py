#!/usr/bin/env python3
"""Neutral h/H/A *included two-body* tree-level widths for the general Zee model.

Physical flavor-off-diagonal and diagonal lepton modes use the EXACT
source-validated A1D Chen-Florentino scalar Yukawa matrices, and D5
exact spin traces/phase space, including both conjugate LFV charges.
Type-II-like quark Yukawas are the *explicit project quark ansatz* used
by Gate E5, NOT an independently UV-complete flavor prescription.
W+W-/ZZ widths include ONLY on-shell tree-level decays; h(125)->VV*
is missing. All quark masses are fixed input proxies (no running or QCD).
All other scalar/gauge/loop/off-shell/3-body modes remain unspecified.
DO NOT use sum of these channels as a physical total width, BR or
HiggsBounds prediction. Source scalar (beta-alpha) convention matches
gateA1d and GateE5. E3 optimized Y fixed by external source verification.
"""
from __future__ import annotations
import math
import numpy as np
from gateA1d_neutral_tree_lfv import scalar_couplings
from zee_gateD5_h125_direct_LFV_27 import (
 exact_flavor_width,exact_diagonal_width,h125_widths,VEV,LEPTON_MASSES)
from gate6_width_inventory import GF,MW,MZ

STATUS="P1_NEUTRAL_H_H_A_2BODY_TREE_PARTIAL_WIDTHS_NO_PHYSICAL_TOTAL"
QUARK_MASS_FIXED_GEV={"bb":4.7,"cc":1.27,"ss":.095,"tt":172.}
QUARK_UP=frozenset({"tt","cc"})
CP_EVEN=frozenset({"h","H"})
NEUTRAL=("h","H","A")
LEPTONS=("e","mu","tau")

def finite(z,label):
 if isinstance(z,bool):
  raise ValueError("Boolean "+label)
 a=float(z)
 if not math.isfinite(a):
  raise ValueError("Nonfinite "+label)
 return a

def quark_two_body(M,m,kappa,cp):
 """LO color-3 scalar or pseudoscalar with fixed pole-like quark masses."""
 M=finite(M,"neutral mass");m=finite(m,"quark mass")
 kappa=finite(kappa,"relative quark Yukawa")
 if M<=0 or m<0 or cp not in ("even","odd"):
  raise ValueError("Neutral quark input invalid")
 if M<=2*m:
  return 0.
 beta=math.sqrt(1.-4.*m*m/(M*M))
 power=3 if cp=="even" else 1
 return 3.*GF*M*m*m/(4.*math.sqrt(2.)*math.pi)*kappa*kappa*beta**power

def on_shell_vector_two_body(M,V,kappa,delta):
 """SM-normalized tree scalar->VV (delta 2 WW, 1 ZZ)."""
 M=finite(M,"neutral mass");V=finite(V,"vector mass")
 kappa=finite(kappa,"neutral vector coupling")
 if M<=0 or V<=0 or delta not in (1,2):
  raise ValueError("Neutral vector channel invalid")
 if M<=2*V:
  return 0.
 x=(V/M)**2
 return delta*GF*M**3/(16.*math.sqrt(2.)*math.pi)*(
  1-4*x+12*x*x)*math.sqrt(1-4*x)*kappa*kappa

def kappas(beta,alpha):
 """Exact Type-II-like quark ansatz and neutral-vector mixing relations."""
 beta=finite(beta,"beta");alpha=finite(alpha,"alpha")
 if not(1.e-8<beta<math.pi/2-1.e-8):
  raise ValueError("beta must be within non-singular physical interval")
 d=beta-alpha
 s,c=math.sin(d),math.cos(d)
 t=math.tan(beta)
 return {
  "h":{"up":c-s/t,"down":c+s*t,"V":c,"CP":"even"},
  "H":{"up":s+c/t,"down":s-c*t,"V":s,"CP":"even"},
  "A":{"up":1/t,"down":t,"V":0.,"CP":"odd"},
 }

def calculate(point,Y):
 """Return partial widths, not physical totals, for neutral h,H,A."""
 matrix=np.asarray(Y,dtype=complex)
 if matrix.shape!=(3,3) or not np.isfinite(matrix).all():
  raise ValueError("Require complex finite 3x3 E3 lepton Y")
 need=("mh2","ma","alpha","beta","mH1","mH2","gamma")
 if any(k not in point for k in need):
  raise ValueError("Missing source spectrum for neutral Zee widths")
 beta=finite(point["beta"],"beta");alpha=finite(point["alpha"],"alpha")
 specs={"h":125.,"H":finite(point["mh2"],"mh2"),
        "A":finite(point["ma"],"ma")}
 if any(v<=0 for v in specs.values()):
  raise ValueError("Invalid neutral scalar mass")
 couplings=scalar_couplings(matrix,mh=specs["h"],mH=specs["H"],
                           mA=specs["A"],alpha=alpha,beta=beta)
 mix=kappas(beta,alpha)
 names=(("e","mu",0,1),("e","tau",0,2),("mu","tau",1,2))
 partial={}
 for (pid,(C,original_mass)) in zip(NEUTRAL,couplings):
  M=specs[pid]
  if not math.isclose(M,original_mass,rel_tol=0,abs_tol=1e-12):
   raise ValueError("Source neutral scalar masses mismatched")
  out={}
  for i,label in enumerate(LEPTONS):
   out[label+"_"+label]=exact_diagonal_width(C,mh=M,i=i)
  for first,last,i,j in names:
   out[first+"_"+last+"_both_charges"]=exact_flavor_width(
    C,mh=M,i=i,j=j)
  opts=mix[pid]
  for channel,mass in QUARK_MASS_FIXED_GEV.items():
   k=opts["up"] if channel in QUARK_UP else opts["down"]
   out[channel+"_TypeII_fixed_quark_mass_LO"]=quark_two_body(
      M,mass,k,opts["CP"])
  out["W_W_onshell_tree"]=on_shell_vector_two_body(
      M,MW,opts["V"],2) if pid in CP_EVEN else 0.
  out["Z_Z_onshell_tree"]=on_shell_vector_two_body(
      M,MZ,opts["V"],1) if pid in CP_EVEN else 0.
  if any(not math.isfinite(v) or v<0 for v in out.values()):
   raise ValueError("Negative/nonfinite neutral partial width")
  partial[pid]=out
 # The source D5 h(125) LFV calculation must agree *exactly* for all 3
 # source physical Yukawas, masses and scalar mixing angles.
 d5=h125_widths(point,matrix)
 for old,key in (("h_to_e_mu","e_mu_both_charges"),
                 ("h_to_e_tau","e_tau_both_charges"),
                 ("h_to_mu_tau","mu_tau_both_charges")):
  if not math.isclose(partial["h"][key],
                      d5["h125_LFV_partial_widths_GeV"][old],
                      rel_tol=5e-10,abs_tol=1e-16):
   raise ValueError("Gate D5 and new neutral width h125 LFV mismatch")
 return {
   "status":STATUS,"candidate_id":str(point["id"]),
   "neutral_state_masses_GeV":specs,
   "tree_level_included_modes_GeV":partial,
   "included_width_sums_NOT_physical_total_GeV":{
      k:sum(v.values()) for k,v in partial.items()},
   "coupling_factors_TypeII_quark_ansatz":mix,
   "h125_three_LFV_rates_exact_D5_reference_closure":True,
   "unimplemented_modes":[
       "h125 WWstar ZZstar gg gamgam Zgam",
       "H/A scalar-to-scalar decays and Z h/H associated final states",
       "general Zee neutral additional loop/offshell/three_body",
       "running_quark_masses and QCD or electroweak corrections",
       "complete gauge/inert scalar widths and production",
       "independent scalar-potential trilinear validation",
       "physical total widths and five-state HiggsBounds input"],
   "complete_physical_neutral_totals_computed":False,
   "experimental_Zee_allowed_or_excluded":None,
 }
