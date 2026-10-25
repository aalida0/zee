#!/usr/bin/env python3
"""P1 N3: neutral Zee h/H -> hh/AA tree two-body widths, *not totals*.

Reconstructs exactly the neutral CP-conserving 2HDM part of original
Gate6 Zee potential. Charged singlet has NO neutral VEV so does not
contribute to the neutral cubic couplings at tree level.

Unmodified scalar conventions: neutral weak fields rho1,rho2; physical
h=(cos alpha,sin alpha), H=(-sin alpha,cos alpha);
A=(-sin beta,cos beta) along eta1,eta2.

Cubic h/H -> aa couplings are directional third derivatives of V,
not guessed mass-dependent formulae. A second, independently coded
polynomial potential numerical central-difference evaluator verifies
Hhh and HAA cubics and CP-even and CP-odd mass Hessians. Identical
neutral boson factor 1/2 relative to Gate6.scalar_width.

Only open, on-shell tree-level 2-body channels. Neutral 3-body,
loops, full EW/QCD, HiggsBounds and total widths are NOT computed.
"""
from __future__ import annotations
import math
import numpy as np
from gate6_benchmark import benchmark
from gate6_width_inventory import scalar_width
STATUS="P1_N3_NEUTRAL_H_HH_AA_SOURCE_POTENTIAL_TWO_BODY_LO_NOT_COMPLETE"

def finite(x,label):
 z=float(x)
 if not math.isfinite(z):raise ValueError("N3 nonfinite "+label)
 return z

def reconstruct(point):
 required=("mH1","mH2","mh2","ma","alpha","beta","gamma",
           "m12sq","lc","k1","k2","k12")
 if any(k not in point for k in required):
  raise ValueError("N3 missing original scalar reconstruction input")
 p=benchmark(beta=finite(point["beta"],"beta"),
  mH1=finite(point["mH1"],"mH1"),mH2=finite(point["mH2"],"mH2"),
  mh2=finite(point["mh2"],"mh2"),ma=finite(point["ma"],"ma"),
  alpha=finite(point["alpha"],"alpha"),
  gamma=finite(point["gamma"],"gamma"),
  m12sq=finite(point["m12sq"],"m12sq"),
  lc=finite(point["lc"],"lc"),k1=finite(point["k1"],"k1"),
  k2=finite(point["k2"],"k2"),k12=finite(point["k12"],"k12"))
 return p

def neutral_tensor(p):
 """Analytic V''' in weak rho1,rho2 and rho-eta-eta subspaces."""
 z=p["inputs"];q=p["quartics"]
 beta=z["beta"];v=z["v"]
 v1=v*math.cos(beta);v2=v*math.sin(beta)
 l1,l2,l3,l4,l5=(q["lambda"+str(i)] for i in range(1,6))
 l345=l3+l4+l5
 # CP even rho_i rho_j rho_k full symmetric third derivative.
 e=np.zeros((2,2,2))
 e[0,0,0]=3*l1*v1
 e[1,1,1]=3*l2*v2
 for i,j,k in ((0,0,1),(0,1,0),(1,0,0)):
  e[i,j,k]=l345*v2
 for i,j,k in ((0,1,1),(1,0,1),(1,1,0)):
  e[i,j,k]=l345*v1
 # rho_i eta_j eta_k third derivative; eta index symmetric.
 a=np.zeros((2,2,2))
 a[0,0,0]=l1*v1
 a[1,1,1]=l2*v2
 a[0,1,1]=(l3+l4-l5)*v1
 a[1,0,0]=(l3+l4-l5)*v2
 a[0,0,1]=a[0,1,0]=l5*v2
 a[1,0,1]=a[1,1,0]=l5*v1
 # physical normalized rotations exactly as original Gate6/A1D.
 alpha=z["alpha"]
 h=np.array([math.cos(alpha),math.sin(alpha)])
 H=np.array([-math.sin(alpha),math.cos(alpha)])
 A=np.array([-math.sin(beta),math.cos(beta)])
 ghh=float(np.einsum("ijk,i,j,k",e,H,h,h))
 gAA=float(np.einsum("ijk,i,j,k",a,H,A,A))
 hAA=float(np.einsum("ijk,i,j,k",a,h,A,A))
 return {"H_h_h":ghh,"H_A_A":gAA,"h_A_A":hAA,
         "full_CP_even_tensor":e,"rho_eta_eta_tensor":a,
         "h_rotation":h,"H_rotation":H,"A_rotation":A}

def potential(p,rho,eta):
 """Independent literal neutral 2HDM gauge-invariant polynomial V."""
 rho=np.asarray(rho,float);eta=np.asarray(eta,float)
 if rho.shape!=(2,) or eta.shape!=(2,):
  raise ValueError("N3 rho/eta must be two physical weak neutral fields")
 z=p["inputs"];q=p["quartics"]
 beta=z["beta"];v=z["v"]
 v1=v*math.cos(beta);v2=v*math.sin(beta)
 l1,l2,l3,l4,l5=(q["lambda"+str(i)] for i in range(1,6))
 l345=l3+l4+l5
 m12=z["m12sq"]
 m11=m12*math.tan(beta)-.5*(l1*v1*v1+l345*v2*v2)
 m22=m12/math.tan(beta)-.5*(l2*v2*v2+l345*v1*v1)
 a1=v1+rho[0];a2=v2+rho[1]
 x1=(a1*a1+eta[0]*eta[0])/2
 x2=(a2*a2+eta[1]*eta[1])/2
 rr=(a1*a2+eta[0]*eta[1])/2
 im=(a1*eta[1]-a2*eta[0])/2
 return (m11*x1+m22*x2-2*m12*rr+
         .5*l1*x1*x1+.5*l2*x2*x2+l3*x1*x2+
         (l4+l5)*rr*rr+(l4-l5)*im*im)

def third_numeric(p,left,twice,sector,step=2.):
 """Independent symmetric finite difference V'''[left,twice,twice]."""
 if sector not in ("rho","eta"):
  raise ValueError("N3 unknown third-derivative sector")
 left=np.asarray(left,float);twice=np.asarray(twice,float)
 h=finite(step,"finite difference step")
 if h<=0:raise ValueError("N3 finite difference must be positive")
 def eval_at(u,w):
  rho=u*left if sector=="eta" else u*left+w*twice
  eta=w*twice if sector=="eta" else np.zeros(2)
  return potential(p,rho,eta)
 return (eval_at(h,h)+eval_at(h,-h)-2*eval_at(h,0)-
         eval_at(-h,h)-eval_at(-h,-h)+2*eval_at(-h,0))/(2*h**3)

def hessian_checks(p):
 """CP-even/odd weak Hessians from the independent polynomial."""
 z=p["inputs"];q=p["quartics"]
 v=z["v"];beta=z["beta"]
 v1,v2=v*math.cos(beta),v*math.sin(beta)
 l1,l2,l3,l4,l5=(q["lambda"+str(i)] for i in range(1,6))
 soft=z["m12sq"]
 ce=np.array([[soft*math.tan(beta)+l1*v1**2,
         -soft+(l3+l4+l5)*v1*v2],
        [-soft+(l3+l4+l5)*v1*v2,
         soft/math.tan(beta)+l2*v2**2]])
 co=np.array([[soft*math.tan(beta)-l5*v2*v2,
                   -soft+l5*v1*v2],
             [-soft+l5*v1*v2,
              soft/math.tan(beta)-l5*v1*v1]])
 alpha=z["alpha"]
 h=np.array([math.cos(alpha),math.sin(alpha)])
 H=np.array([-math.sin(alpha),math.cos(alpha)])
 G=np.array([math.cos(beta),math.sin(beta)])
 A=np.array([-math.sin(beta),math.cos(beta)])
 if (not math.isclose(float(h@ce@h),z["mh1"]**2,rel_tol=1e-9,abs_tol=1e-5)
  or not math.isclose(float(H@ce@H),z["mh2"]**2,rel_tol=1e-9,abs_tol=1e-5)
  or not math.isclose(float(h@ce@H),0.,rel_tol=0,abs_tol=1e-5)
  or not math.isclose(float(A@co@A),z["ma"]**2,rel_tol=1e-9,abs_tol=1e-5)
  or not math.isclose(float(G@co@G),0.,rel_tol=0,abs_tol=1e-5)):
  raise ValueError("N3 Gate6 CP-even/odd neutral Hessian spectral mismatch")
 return {"CP_even_and_CP_odd_masses_source_closed":True,
         "Goldstone_CP_odd_mass2_GeV2":float(G@co@G)}

def calculate(point,verify_numeric=True):
 """Calculates H->hh,H->AA,h->AA, no other physical-width claims."""
 p=reconstruct(point)
 tensor=neutral_tensor(p)
 checks=hessian_checks(p)
 mH=p["inputs"]["mh2"];mh=p["inputs"]["mh1"];mA=p["inputs"]["ma"]
 if verify_numeric:
  for name,left,twice,sector in (
    ("H_h_h",tensor["H_rotation"],tensor["h_rotation"],"rho"),
    ("H_A_A",tensor["H_rotation"],tensor["A_rotation"],"eta"),
    ("h_A_A",tensor["h_rotation"],tensor["A_rotation"],"eta"),
  ):
   approx=third_numeric(p,left,twice,sector)
   true=tensor[name]
   if not math.isclose(approx,true,rel_tol=3e-7,abs_tol=8e-5):
    raise ValueError(f"N3 neutral cubic independent potential derivative mismatch {name}: {approx} versus {true}")
 widths={
    "H":{
       "h_h_identical":.5*scalar_width(mH,mh,mh,tensor["H_h_h"]),
       "A_A_identical":.5*scalar_width(mH,mA,mA,tensor["H_A_A"])},
    "h":{
       "A_A_identical":.5*scalar_width(mh,mA,mA,tensor["h_A_A"])},
    "A":{},
 }
 if any(not math.isfinite(v) or v<0
        for d in widths.values() for v in d.values()):
  raise ValueError("N3 nonphysical cubic partial width")
 return {
  "candidate_id":point["id"],
  "status":STATUS,
  "neutral_scalar_pair_included_two_body_GeV":widths,
  "cubic_couplings_GeV":{key:tensor[key] for key in ("H_h_h","H_A_A","h_A_A")},
  "potential_independent_finite_difference_closed":bool(verify_numeric),
  **checks,
  "all_scalar_pair_modes_complete":False,
  "physical_five_state_total_widths":None,
  "experimental_Zee_allowed_or_excluded":None,
  "missing":["off-shell neutral scalar pairs and three-body decays",
    "neutral loop-induced, h125 offshell WWstar ZZstar, running quark mass and QCD",
    "CP-odd neutral to mixed charged pair independent potential check",
    "independent external UFO/MadWidth two-body amplitude validation",
    "complete five-state physical totals, hadronic production and HiggsBounds"],
 }
