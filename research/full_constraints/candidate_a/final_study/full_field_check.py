#!/usr/bin/env python3
"""Termwise independent SARAH complex Lagrangian polynomial versus D10 tensor evaluator."""
import json,pathlib,sys
import numpy as np
import sympy as s
from verify_independent import ROOT
sys.path.insert(0,str(ROOT))
from module1.potential import Potential,gauge_audit
r=s.symbols('r:10',real=True); names=('M112','M222','M12Sq','MCS2','Mu4','Lambda1','Lambda2','Lambda3','Lambda4','Lambda5','LambdaC','K1','K2','K12'); p=s.symbols('p:14',real=True); m1,m2,m12,mc,mu,l1,l2,l3,l4,l5,lc,k1,k2,k12=p
z=[(r[i]+s.I*r[i+1])/s.sqrt(2) for i in range(0,10,2)]; zc=[s.conjugate(q) for q in z]; x=zc[0]*z[0]+zc[1]*z[1];y=zc[2]*z[2]+zc[3]*z[3];q=zc[0]*z[2]+zc[1]*z[3];qc=s.conjugate(q);ss=zc[4]*z[4];d=z[0]*z[3]-z[1]*z[2];dc=s.conjugate(d)
# Terms matched one by one to LagNoHC and LagHC, with hermitian conjugates explicit.
V=m1*x+m2*y+mc*ss+l1*x*x/2+l2*y*y/2+l3*x*y+l4*q*qc+lc*ss*ss+k1*ss*x+k2*ss*y-m12*(q+qc)+l5*(q*q+qc*qc)/2-k12*ss*(q+qc)+mu*(zc[4]*d+z[4]*dc)
V=s.expand_complex(V); grad=[s.diff(V,t) for t in r]; hess=s.hessian(V,r); F=s.lambdify((r,p),(V,grad,hess),'numpy',cse=True)
rr=json.loads((ROOT/'validation/module1/d10_vacuum_global.json').read_text())['records']; rng=np.random.default_rng(72026); tests=[]
for rec in [rr[0],rr[1],rr[4]]:
 pp=rec['lagrangian_parameters']
 for variant in ('original','flip_mu','flip_k12','flip_portals'):
  par=dict(pp)
  if variant=='flip_mu': par['Mu4']*=-1
  if variant=='flip_k12': par['K12']*=-1
  if variant=='flip_portals': par['K1']*=-1;par['K2']*=-1
  choices=[rng.normal(0,180,10),np.array([0,0,100,0,0,0,200,0,0,0.]),np.array([0,0,0,0,100,30,150,-80,50,40.]),np.array([100,30,150,-80,0,0,0,0,50,40.]),np.array([30,20,100,10,60,40,200,20,0,0.]),np.array([0,0,100,0,120,30,200,80,90,-55.])]
  for v in choices:
   a,g,h=F(v,[par[k] for k in names]);b,g2,h2=Potential(par).evaluate(v)
   aa=complex(a); gg=np.asarray(g,dtype=complex).flatten(); hh=np.asarray(h,dtype=complex)
   assert abs(aa.imag)<1e-12*max(1,abs(aa.real)) and np.max(abs(gg.imag))<1e-12*max(1,np.max(abs(gg.real))) and np.max(abs(hh.imag))<1e-12*max(1,np.max(abs(hh.real)))
   assert np.allclose(aa.real,b,rtol=2e-12,atol=1e-5) and np.allclose(gg.real,g2,rtol=2e-11,atol=1e-6) and np.allclose(hh.real,h2,rtol=2e-11,atol=1e-7)
   tests.append((abs(aa.real-b),np.max(abs(gg.real-g2)),np.max(abs(hh.real-h2))))
# Gauge zero modes checked on exact-root representatives at EW; floating Hessian numerical tolerance.
for name in ('d7_NO_neutral_near_heavy_07','F13_heavy_0001330'):
 rec=next(t for t in rr if t['benchmark_id']==name); proof=json.loads((pathlib.Path(__file__).parent/'CERTIFICATES'/f'{name}.json').read_text()); r0=np.zeros(10);r0[[2,6]]=[float(s.Rational(t)) for t in proof['neutral_center']]; val,g,H=Potential(rec['lagrangian_parameters']).evaluate(r0); rank,trans,ward=gauge_audit(r0,H); assert rank==3 and trans>0 and ward<1e-7
print('PASS: 72 complex/boundary/sign controls; max |dV|, |dgrad|, |dH|',np.max(tests,axis=0),'and EW Goldstones')
