#!/usr/bin/env python3
"""E6Z: complete one-loop Zee CHARGED-SCALAR h->Z gamma form factor.

Implements the finite mixed-mass B0/C0 expression of
Florentino, Romao & Silva EPJC81(2021)1148 Appendix D Eq(D.20),
including i!=j H1/H2. Numerically independent check:
equal-mass PV loop matches I1(a,b) from the standard scalar loop exactly.
The SM W/fermion (CP-even and CP-odd) LO amplitudes follow standard
I1/I2 functions. The ratio multiplies HiggsTools' SM reference Zgam
partial width; higher-order EW/QCD matching remains approximate.

All masses entering PV C0 are above m_h/2 in the E2 source cohort;
the finite integrals are real, so real Gauss quadratures suffice.
"""
from __future__ import annotations
import cmath,functools,math
import numpy as np

MH=125.
MZ=91.1876
MW=80.379
VEV=246.21965
SW2=.23122
FERMIONS=(
 ("tt",172.5,2./3.,.5,3),
 ("bb",4.18,-1./3.,-.5,3),
 ("cc",1.27,2./3.,.5,3),
 ("tautau",1.77686,-1.,-.5,1),
)


@functools.lru_cache(maxsize=4)
def quad_nodes(n):
 vals,ws=np.polynomial.legendre.leggauss(n)
 return ((vals+1)/2,ws/2)


def b0_difference(s,t,ma2,mb2,n=48):
 """UV finite [B0(s)-B0(t)] from its one-parameter MS representation."""
 x,w=quad_nodes(n)
 a=x*ma2+(1-x)*mb2
 d1=a-x*(1-x)*s
 d2=a-x*(1-x)*t
 if np.min(d1)<=0 or np.min(d2)<=0:
  raise ValueError("B0 kernel crossed physical threshold")
 return float(-np.dot(w,np.log(d1/d2)))


def c0_photon_pair(mi2,mj2,n=48):
 """C0(MZ²,0,MH²,mi²,mi²,mj²), with equal mi on photon legs.

 Sign convention: C0(0,0,s,m²,m²,m²)=-2f(s/(4m²))/s.
 Feynman x,y,z simplex: x+y+z=1, mi on x,y, mj on z;
 q_photon²=0 between x,y, Z² between y,z, h² between x,z.
 """
 x,w=quad_nodes(n)
 X=x[:,None]; U=x[None,:] # reuse same Gauss grid for the inner u
 Y=(1-X)*U
 Z=(1-X)*(1-U)
 D=mi2*(X+Y)+mj2*Z - MH*MH*X*Z-MZ*MZ*Y*Z
 if np.min(D)<=0:raise ValueError("C0 kernel crossed physical threshold")
 return float(-np.sum((w[:,None]*w[None,:])*(1-X)/D))


@functools.lru_cache(maxsize=8192)
def mixed_mass_F(mi,mj,n=48):
 """Finite curly bracket of Florentino Eq(D.20), symmetric in i,j."""
 if not(mi>MH/2 and mj>MH/2 and math.isfinite(mi) and math.isfinite(mj)):
  raise ValueError("PV loop requires real charged masses above threshold")
 mi2=mi*mi;mj2=mj*mj
 delta=MH*MH-MZ*MZ
 result=(MZ*MZ/delta*b0_difference(MH*MH,MZ*MZ,mi2,mj2,n)
         +1.+mi2*c0_photon_pair(mi2,mj2,n)
         +mj2*c0_photon_pair(mj2,mi2,n))
 if not math.isfinite(result):raise ValueError("Nonfinite hZgamma PV form factor")
 return result


def f_a(a):
 """Standard I1/2 heavy variable a=4m²/mh², physical complex sheet."""
 if a<=0 or not math.isfinite(a):raise ValueError("Invalid I1 argument")
 if a>=1:
  return complex(math.asin(1/math.sqrt(a))**2)
 z=math.sqrt(1-a)
 return -.25*(math.log((1+z)/(1-z))-1j*math.pi)**2


def g_a(a):
 if a<=0 or not math.isfinite(a):raise ValueError("Invalid I1 argument")
 if a>=1:
  return complex(math.sqrt(a-1)*math.asin(1/math.sqrt(a)))
 z=math.sqrt(1-a)
 return .5*z*(math.log((1+z)/(1-z))-1j*math.pi)


def i1(a,b):
 if abs(a-b)<1e-10*max(a,b):raise ValueError("I1 degeneracy needs limit")
 return (a*b/(2*(a-b))+
         a*a*b*b/(2*(a-b)**2)*(f_a(a)-f_a(b))+
         a*a*b/((a-b)**2)*(g_a(a)-g_a(b)))


def i2(a,b):
 if abs(a-b)<1e-10*max(a,b):raise ValueError("I2 degeneracy needs limit")
 return -(a*b)/(2*(a-b))*(f_a(a)-f_a(b))


def crosscheck_equal_mass(m):
 """A non-optional independent analytic-vs-PV check for each original mass."""
 aa=4*m*m/(MH*MH)
 bb=4*m*m/(MZ*MZ)
 expected=-(MH*MH-MZ*MZ)/(2*m*m)*i1(aa,bb)
 coarse=mixed_mass_F(m,m,32)
 fine=mixed_mass_F(m,m,48)
 if not (abs(expected.imag)<1e-9 and
         math.isclose(fine,expected.real,rel_tol=2e-8,abs_tol=1e-10)
         and math.isclose(coarse,fine,rel_tol=2e-7,abs_tol=1e-10)):
  raise ValueError("Mixed PV C0/B0 does not reduce to equal-mass I1")
 return True


def sm_zgam_lo(c):
 """CP-even and -odd SM particle amplitudes in Eq. D.20 normalization.

 W: standard cot(thetaW)*{[5+2/a-(1+2/a)tW²]I1
                            -4(3-tW²)I2}.
 Fermions: -2 N Q(T3-2Q*sW²)/(sW cW) (I1-I2), and
 CP-odd pseudoscalar 2 N Q(T3-2QsW²)/(sW cW) I2.
 """
 s=math.sqrt(SW2);cw=math.sqrt(1-SW2);tw2=SW2/(1-SW2)
 a=4*MW*MW/(MH*MH);b=4*MW*MW/(MZ*MZ)
 w=cw/s*((5+2/a-(1+2/a)*tw2)*i1(a,b)-
         4*(3-tw2)*i2(a,b))
 even=float(c["WW"])*w;odd=0j
 for name,mass,Q,T3,N in FERMIONS:
  a=4*mass*mass/(MH*MH)
  b=4*mass*mass/(MZ*MZ)
  factor=2*N*Q*(T3-2*Q*SW2)/(s*cw)
  coup=complex(c[name])
  even+=-factor*coup.real*(i1(a,b)-i2(a,b))
  odd+=factor*coup.imag*i2(a,b)
 return even,odd


def scalar_zgam(p,tril):
 """Sum BOTH unequal-mass and diagonal charged scalar loops, Eq(D.20).

 Our g_ij are V potential derivatives: L contains -g_ij h Hi- Hj+.
 Z_ij=(T3-sW²Q)_ij, including nonzero i!=j after doublet-singlet mixing.
 The physical normalized scalar contribution is
   A_scalar=-2v/(sW cW*(mh²-mZ²)) SUM_ij g_ij Z_ij F(mi,mj).
 Equal mass gives +g*v*Z/(sW cW*m²)*I1, fixing relative normalization.
 """
 ms=(p["scalar"]["mH1"],p["scalar"]["mH2"])
 for m in ms:crosscheck_equal_mass(float(m))
 h=np.array([
  [tril["g_h_H1plus_H1minus_GeV"],tril["g_h_H1plus_H2minus_GeV"]],
  [tril["g_h_H1plus_H2minus_GeV"],tril["g_h_H2plus_H2minus_GeV"]]])
 z=np.asarray(tril["Z_generator_T3_minus_sW2_mass_basis"],float)
 if h.shape!=(2,2) or z.shape!=(2,2):
  raise ValueError("Wrong Zee charged scalar mixing matrices")
 fine=np.array([[mixed_mass_F(float(mi),float(mj),48)
                 for mj in ms] for mi in ms])
 # Symmetry also tests the ordered (i,j)+(j,i) multiplicity.
 if not np.allclose(fine,fine.T,rtol=2e-10,atol=2e-12):
  raise ValueError("Mixed-mass Zgamma scalar loop symmetry failed")
 coarse=np.array([[mixed_mass_F(float(mi),float(mj),32)
                 for mj in ms] for mi in ms])
 if not np.allclose(fine,coarse,rtol=2e-7,atol=1e-10):
  raise ValueError("Mixed-mass Zgamma loop quadrature disagrees")
 weighted=h*z*fine
 A=-2*VEV/(math.sqrt(SW2*(1-SW2))*(MH*MH-MZ*MZ))
 contributions=A*weighted
 return {
  "sum_scalar_Zgamma_LO_amplitude":float(np.sum(contributions)),
  "ordered_diagonal_H1_and_H2_amplitudes":[float(contributions[0,0]),
                                              float(contributions[1,1])],
  "ordered_mixed_H1H2_and_H2H1_amplitudes":[float(contributions[0,1]),
                                             float(contributions[1,0])],
  "mixed_PV_F_H1H2":float(fine[0,1]),
  "full_offdiagonal_ZH1H2_included":True,
  "PV_32_48_quadrature_and_equal_mass_I1_checked":True,
  "source":"Florentino/Romao/Silva EPJC81(2021)1148 Eq D20",
 }


def zgam_ratio(pack,tril):
 sm,odd=sm_zgam_lo(pack["effective_couplings"])
 smunit={**pack["effective_couplings"]}
 for key in ("tt","bb","cc","tautau"):
  smunit[key]=1+0j
 smunit["WW"]=1.
 denom,_=sm_zgam_lo(smunit)
 if not(abs(denom)>1e-3 and math.isfinite(abs(denom))):
  raise ValueError("LO SM hZgamma amplitude zero/invalid")
 exotic=scalar_zgam(pack,tril)
 scalar=exotic["sum_scalar_Zgamma_LO_amplitude"]
 numerator=abs(sm+scalar)**2+abs(odd)**2
 rate=numerator/abs(denom)**2
 if not math.isfinite(rate) or rate<=0:
  raise ValueError("Zee hZgamma scalar+SM ratio invalid")
 return {
   **exotic,
   "LO_SM_particle_even_Zgamma_amplitude":[sm.real,sm.imag],
   "LO_SM_particle_odd_Zgamma_amplitude":[odd.real,odd.imag],
   "LO_SM_reference_even_Zgamma_amplitude":[denom.real,denom.imag],
   "full_charged_scalar_plus_modified_SM_LO_hZgamma_over_SM_LO_width":rate,
   "higher_order_theory_matching_not_calibrated":True,
 }
