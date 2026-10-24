#!/usr/bin/env python3
"""Exact P2->Yang/Wu Higgs-basis *scalar quartic* mapping for Zee TypeII.

P2 Phi1=cβ H1 -sβ H2; Phi2=sβ H1 +cβ H2.
Source Gate6 quartic λ1...λ5, singlet lc, portals k1,k2,k12.
Yang/Wu Higgs-basis Z1...Z7, singlet lameta, portals lam8..10.

Each point validates via two INDEPENDENT representations of the
gauge-invariant quartic polynomial evaluated at arbitrary COMPLEX
SU(2) doublets and charged singlet, not just neutral VEVs; checks
Yang/Wu internal lam1,lam4,lam5,lam6 and muzee masses exactly.
This mapping is a *necessary step*, not a complete UFO mass/vertex/
complex lepton-sector parameter-card certification.

Original Yang/Wu model basis: source Lagrangian.fr/Parameters.fr,
https://github.com/YangPhy/Zee-Model.
"""
from __future__ import annotations
import math
import numpy as np
from gate6_benchmark import benchmark

STATUS="P1_ZEE_SCALAR_QUARTIC_HIGGS_BASIS_ROTATION_SOURCE_NUMERIC_CHECKED"

def map_point(point):
 p=benchmark(beta=float(point["beta"]),mH1=float(point["mH1"]),
  mH2=float(point["mH2"]),mh2=float(point["mh2"]),
  ma=float(point["ma"]),alpha=float(point["alpha"]),
  gamma=float(point["gamma"]),m12sq=float(point["m12sq"]),
  lc=float(point["lc"]),k1=float(point["k1"]),
  k2=float(point["k2"]),k12=float(point["k12"]))
 b=p["inputs"]["beta"];s=math.sin(b);c=math.cos(b)
 sq=s*s*c*c
 l=p["quartics"]
 a,b2,l3,l4,l5=(l["lambda"+str(i)] for i in range(1,6))
 l345=l3+l4+l5
 q=(a+b2-2*l345)*sq
 Z={
  "lam1":a*c**4+b2*s**4+2*l345*sq,
  "lam2":a*s**4+b2*c**4+2*l345*sq,
  "lam3":l3+q,
  "lam4":l4+q,
  "lam5":l5+q,
  "lam6":-s*c*(a*c*c-b2*s*s-l345*(c*c-s*s)),
  "lam7":-s*c*(a*s*s-b2*c*c+l345*(c*c-s*s)),
 }
 inputs=p["inputs"];k1,k2,k12=(inputs[k] for k in ("k1","k2","k12"))
 Z.update({
  "lam8":k1*c*c+k2*s*s-2*k12*s*c,
  "lam9":k1*s*s+k2*c*c+2*k12*s*c,
  "lam10":(k2-k1)*s*c-k12*(c*c-s*s),
  "lameta":inputs["lambda_c"],
 })
 gamma=inputs["gamma"]
 phi=math.pi/2-gamma
 ab=inputs["alpha"]-inputs["beta"]
 mm=inputs["mh1"]**2
 heavy=inputs["mh2"]**2
 ps=inputs["ma"]**2
 dbl=(inputs["mH1"]**2*math.cos(gamma)**2+
      inputs["mH2"]**2*math.sin(gamma)**2)
 cab,sab=math.cos(ab),math.sin(ab)
 v=inputs["v"]
 reference={
  "lam1":(mm*cab*cab+heavy*sab*sab)/v**2,
  "lam4":(ps+heavy*cab*cab+mm*sab*sab-2*dbl)/v**2,
  "lam5":(-ps+heavy*cab*cab+mm*sab*sab)/v**2,
  "lam6":cab*(mm-heavy)*sab/v**2,
 }
 for key,val in reference.items():
  if not math.isclose(Z[key],val,rel_tol=1e-9,abs_tol=1e-9):
   raise ValueError(f"Yang/Wu internal mass-derived {key} disagrees with rotated P2 quartic {Z[key]} vs {val}")
 mu_model=math.sqrt(2)*math.cos(phi)*(
      inputs["mH2"]**2-inputs["mH1"]**2)*math.sin(phi)/v
 if not math.isclose(mu_model,p["mu4_GeV"],rel_tol=1e-10,abs_tol=1e-8):
  raise ValueError("Yang/Wu muzee and P2 mu4 charged mixing disagree")
 return {"status":STATUS,"scalar":p,"higgs_basis":Z,
   "YangWu_external_lam2_lam3_lam7_lam8_lam9_lam10_lameta":{
       n:Z[n] for n in ("lam2","lam3","lam7","lam8","lam9","lam10","lameta")},
   "YangWu_input_ZEEINPUTS":{
      "beta":inputs["beta"],"alpha":inputs["alpha"],
      "alphabeta":ab,"phi":phi},
   "YangWu_internal_mass_mixing_closed":True,
   "charged_mu4_muzee_source_closed":True,
   "full_flavor_Y_f_amplitudes_matched":False,
   "all_source_FeynRules_vertices_matched":False,
 }

def invariant_potential(Q1,Q2,charged,values,basis):
 """Gauge-invariant quartic in arbitrary complex two-doublet fields."""
 Q1=np.asarray(Q1,complex);Q2=np.asarray(Q2,complex)
 if Q1.shape!=(2,) or Q2.shape!=(2,):
  raise ValueError("SU2 doublet fields must be 2 complex components")
 x1=float(np.vdot(Q1,Q1).real)
 x2=float(np.vdot(Q2,Q2).real)
 z=np.vdot(Q1,Q2)
 y=abs(complex(charged))**2
 if basis=="two_vev":
  q=values
  l1,l2,l3,l4,l5=(q["lambda"+str(i)] for i in range(1,6))
  return (.5*l1*x1*x1+.5*l2*x2*x2+l3*x1*x2+
      l4*abs(z)**2+l5*(z*z).real+
      y*(q["k1"]*x1+q["k2"]*x2-2*q["k12"]*z.real)+
      q["lc"]*y*y)
 if basis=="Higgs":
  q=values
  return (.5*q["lam1"]*x1*x1+.5*q["lam2"]*x2*x2+
      q["lam3"]*x1*x2+q["lam4"]*abs(z)**2+
      q["lam5"]*(z*z).real+
      2*q["lam6"]*x1*z.real+2*q["lam7"]*x2*z.real+
      y*(q["lam8"]*x1+q["lam9"]*x2+2*q["lam10"]*z.real)+
      q["lameta"]*y*y)
 raise ValueError("Unknown scalar basis")

def check_quartic(point,trial_count=20,seed=20261020):
 report=map_point(point)
 original=report["scalar"]["quartics"]
 src=report["scalar"]["inputs"]
 p={**original,"k1":src["k1"],"k2":src["k2"],
    "k12":src["k12"],"lc":src["lambda_c"]}
 z=report["higgs_basis"]
 beta=src["beta"];c,s=math.cos(beta),math.sin(beta)
 rng=np.random.default_rng(seed)
 worst=0.
 for _ in range(trial_count):
  H1=rng.normal(size=2)+1j*rng.normal(size=2)
  H2=rng.normal(size=2)+1j*rng.normal(size=2)
  chi=complex(*rng.normal(size=2))
  phi1=c*H1-s*H2
  phi2=s*H1+c*H2
  left=invariant_potential(phi1,phi2,chi,p,"two_vev")
  right=invariant_potential(H1,H2,chi,z,"Higgs")
  scale=max(1.,abs(left),abs(right))
  relative=abs(left-right)/scale
  worst=max(worst,relative)
  if relative>4e-11:
   raise ValueError("P2 Zee potential not gauge-invariantly closed under Higgs-basis rotation")
 return {
   "status":STATUS,"original_scalar_id":point.get("id"),
   "quartic_full_SU2_arbitrary_complex_field_trials":trial_count,
   "quartic_max_relative_residual":worst,
   "YangWu_external":report["YangWu_external_lam2_lam3_lam7_lam8_lam9_lam10_lameta"],
   "YangWu_input_ZEEINPUTS":report["YangWu_input_ZEEINPUTS"],
   "internal_mass_and_mu4_muzee_closed":True,
   "complete_UFO_lepton_Y_fermion_boson_amplitude_matching":False,
   "complete_Gauge_and_HiggsTools_model_allowed":None,
 }
