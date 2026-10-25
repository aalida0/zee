#!/usr/bin/env python3
"""N2: exact source-convention *on-shell two-body* neutral bosonic subsets.

Two separate LO source-anchored sectors:
  1) gauge-kinetic h/H/A -> Z A/h/H and H_i^\u00b1 W^\u2213,
     with both charge conjugate W modes counted explicitly;
  2) h/H -> H_i^+ H_j^- through the *original Gate6 charged
     Hessian VEV derivatives* projected into charged physical states,
     including a factor two for i != j conjugate final states.

Use Florentino/Romao/Silva EPJC 81 (2021) 1148 scalar rotations and
the EXACT previous gate6_width_inventory vector_width/trilinears
conventions. This is NOT the full neutral model: neutral H->hh/AA,
neutral off-shell, h125 VV*, loops, QCD etc still missing. No full BR.

This independently reconstructed charged Hessian projection must close
the old Gate6 H2-H1-h/H trilinears on EVERY source point. Failure is hard.
"""
from __future__ import annotations
import math
import numpy as np
from gate6_benchmark import benchmark
from gate6_width_inventory import (
 ALPHA_INV,SW2,MW,MZ,vector_width,scalar_width,trilinears)
from zee_priority1_neutral_two_body import finite

STATUS="P1_N2_REAL_NEUTRAL_Z_W_AND_CHARGED_PAIR_LO_NOT_COMPLETE"

def charged_hessian_cubic_matrices(p):
 """Original Gate6 quadratic charged Hessian derivatives in weak basis."""
 z=p["inputs"];q=p["quartics"]
 v=z["v"];v1=v*math.cos(z["beta"]);v2=v*math.sin(z["beta"])
 a,b,c,d,e=[q["lambda"+str(i)] for i in range(1,6)]
 mu=p["mu4_GeV"]
 d1=np.array([
  [a*v1,(d+e)*v2/2,0],
  [(d+e)*v2/2,c*v1,-mu/math.sqrt(2)],
  [0,-mu/math.sqrt(2),z["k1"]*v1-z["k12"]*v2]])
 d2=np.array([
  [c*v2,(d+e)*v1/2,mu/math.sqrt(2)],
  [(d+e)*v1/2,b*v2,0],
  [mu/math.sqrt(2),0,z["k2"]*v2-z["k12"]*v1]])
 angle=z["alpha"]
 dh=math.cos(angle)*d1+math.sin(angle)*d2
 dH=-math.sin(angle)*d1+math.cos(angle)*d2
 beta=z["beta"];gamma=z["gamma"]
 sb,cb=math.sin(beta),math.cos(beta)
 sg,cg=math.sin(gamma),math.cos(gamma)
 gold=np.array([cb,sb,0.])
 u1=np.array([-sb*cg,cb*cg,sg])
 u2=np.array([sb*sg,-cb*sg,cg])
 U=np.column_stack([u1,u2])
 if not np.allclose(U.T@U,np.eye(2),rtol=0,atol=1e-13):
  raise ValueError("N2 source charged rotation nonunitary")
 if not np.allclose(gold@U,0.,rtol=0,atol=1e-13):
  raise ValueError("N2 Goldstone leaked into charged scalar basis")
 result={}
 for key,dM in (("h",dh),("H",dH)):
  result[key]=U.T@dM@U
  if not np.allclose(result[key],result[key].T,rtol=2e-13,atol=1e-9):
   raise ValueError("N2 projected charged trilinears nonsymmetric")
 reference=trilinears(p)
 for key,ref in (("h",reference["h125"]),("H",reference["hheavy"])):
  if not math.isclose(float(result[key][0,1]),ref,
           rel_tol=1e-11,abs_tol=5e-10):
   raise ValueError("Gate6 N2 h/H H1 H2 cubic derivative not source closed")
 return result

def gauge_subset(point):
 """Gauge-kinetic channels with explicit charges and kinematic thresholds."""
 beta=finite(point["beta"],"beta")
 alpha=finite(point["alpha"],"alpha")
 gamma=finite(point["gamma"],"gamma")
 if not(0<gamma<math.pi/2):
  raise ValueError("N2 charged mixing outside 0<gamma<pi/2")
 mh=125.;mH=finite(point["mh2"],"mH");mA=finite(point["ma"],"mA")
 m1=finite(point["mH1"],"mH1");m2=finite(point["mH2"],"mH2")
 if not all(x>0 for x in (mH,mA,m1,m2)):
  raise ValueError("N2 physical masses invalid")
 delta=beta-alpha
 sn,cs=math.sin(delta),math.cos(delta)
 gw=math.sqrt(4*math.pi/(ALPHA_INV*SW2))
 gz=gw/(2*math.sqrt(1.-SW2))
 mc={"h":mh,"H":mH,"A":mA}
 amps={"h":abs(sn),"H":abs(cs),"A":1.}
 doublet={"H1":math.cos(gamma),"H2":math.sin(gamma)}
 charged={"H1":m1,"H2":m2}
 out={}
 for state,M in mc.items():
  row={}
  for cname,Cmass in charged.items():
   # Final W charge conjugates of neutral initial state, each
   # individually has the same on-shell tree-level partial width.
   one=vector_width(M,Cmass,MW,gw/2*doublet[cname]*amps[state])
   row[cname+"_W_both_charge_modes"]=2*one
  if state=="h":
   row["A_Z"]=vector_width(M,mA,MZ,gz*sn)
  elif state=="H":
   row["A_Z"]=vector_width(M,mA,MZ,gz*cs)
  else:
   row["h_Z"]=vector_width(M,mh,MZ,gz*sn)
   row["H_Z"]=vector_width(M,mH,MZ,gz*cs)
  out[state]=row
 return out

def charged_pair_subset(point):
 """h/H->H_i+H_j- from old complete charged Hessian derivative."""
 inputs=dict(point)
 p=benchmark(beta=float(inputs["beta"]),
             mH1=float(inputs["mH1"]),mH2=float(inputs["mH2"]),
             mh2=float(inputs["mh2"]),ma=float(inputs["ma"]),
             alpha=float(inputs["alpha"]),gamma=float(inputs["gamma"]),
             m12sq=float(inputs["m12sq"]),lc=float(inputs["lc"]),
             k1=float(inputs["k1"]),k2=float(inputs["k2"]),
             k12=float(inputs["k12"]))
 mats=charged_hessian_cubic_matrices(p)
 result={}
 for name,M in (("h",p["inputs"]["mh1"]),("H",p["inputs"]["mh2"])):
  g=mats[name]
  low,high=p["inputs"]["mH1"],p["inputs"]["mH2"]
  # Charge combinations H1+H1-, H2+H2- (single charge arrangement
  # each) and H1+H2-/H1-H2+ (TWO distinct final states).
  result[name]={
   "H1plus_H1minus":scalar_width(M,low,low,float(g[0,0])),
   "H1plus_H2minus_and_conjugate":2*scalar_width(
       M,low,high,float(g[0,1])),
   "H2plus_H2minus":scalar_width(M,high,high,float(g[1,1])),
  }
 return result,mats,p

def calculate(point):
 if "id" not in point:
  raise ValueError("N2 source missing candidate ID")
 kinetic=gauge_subset(point)
 pairs,matrices,reconstructed=charged_pair_subset(point)
 enriched={s:{**kinetic[s],**pairs.get(s,{})}
           for s in ("h","H","A")}
 if any(not math.isfinite(x) or x<0
        for m in enriched.values() for x in m.values()):
  raise ValueError("N2 negative/nonfinite bosonic widths")
 if any(set(pairs.get(k,{})).intersection(kinetic[k])
        for k in enriched):
  raise ValueError("N2 duplicate channel appeared")
 return {
  "candidate_id":point["id"],"status":STATUS,
  "additional_gauge_and_charged_pair_LO_GeV":enriched,
  "additional_included_subtotals_NOT_physical_totals_GeV":{
     k:sum(v.values()) for k,v in enriched.items()},
  "gauge_vector_decay_both_W_charge_modes_counted":True,
  "charged_mixed_pair_both_charge_modes_counted":True,
  "old_Gate6_H2_H1_h_H_trilinear_source_closed":True,
  "scalar_physical_input_reconstructed_with_Gate6":True,
  "missing":["H to hh/AA (neutral scalar triple couplings)",
             "A to charged mixed scalar pairs potentially CP allowed",
             "all off-shell WWstar ZZstar three-body modes",
             "neutral loop-induced gg/gamma gamma/Zgamma",
             "QCD correction, running quark masses, higher-order gauges",
             "independent gauge-invariant UFO/MadWidth crosscode validation",
             "complete heavy neutral physical total widths"],
  "neutral_physical_total_widths":None,
  "full_model_allowed_or_excluded":None,
 }
