#!/usr/bin/env python3
"""Deterministic phase-minimized five-orbit-variable local descent; not a stability proof."""
import json, math, pathlib, sys, time
from fractions import Fraction as Q
import numpy as np
import sympy as sp
from scipy.optimize import minimize
from verify_independent import ROOT,run,I,add,neg,mul,scale
HERE=pathlib.Path(__file__).parent
names=('M112','M222','M12Sq','MCS2','Mu4','Lambda1','Lambda2','Lambda3','Lambda4','Lambda5','LambdaC','K1','K2','K12')
A,B,S,E,T=sp.symbols('A B S E T',real=True); p=sp.symbols('p:14',real=True); m11,m22,m12,mcs,mu,l1,l2,l3,l4,l5,lc,k1,k2,k12=p
x=A*A;y=B*B;z=S*S; u=A*B*sp.cos(E)*sp.cos(T);w=A*B*sp.cos(E)*sp.sin(T); d=A*B*sp.sin(E)
V=m11*x+m22*y-2*m12*u+mcs*z-2*sp.Abs(mu)*S*d+l1*x*x/2+l2*y*y/2+l3*x*y+l4*(u*u+w*w)+l5*(u*u-w*w)+lc*z*z+(k1*x+k2*y-2*k12*u)*z
f=sp.lambdify(((A,B,S,E,T),p),(V,[sp.diff(V,i) for i in (A,B,S,E,T)]),'numpy',cse=True)
records=json.loads((ROOT/'validation/module1/d10_vacuum_global.json').read_text())['records']; cards=json.loads((ROOT/'module1/d10_benchmarks.json').read_text())['records']; rows=json.loads((HERE/'SCALAR_ONLY_PRELIMINARY.json').read_text()); output=HERE/'FINITE_START.jsonl'
completed={}
if output.exists(): completed={(z['family'],z['k']):z for z in map(json.loads,output.read_text().splitlines())}
for row in rows:
 key=(row['family'],row['k'])
 if key in completed: continue
 rec=next(z for z in records if z['benchmark_id']==key[0]); phys=next(z['input']['physical'] for z in cards if z['input']['benchmark_id']==key[0]); pp=dict(rec['lagrangian_parameters']); pp['Mu4']=row['Mu4_GeV']; v=phys['v']
 # Work with dimensionless norm roots, scaling the dimensional parameters.
 pars=[pp[n]/v**2 if n in names[:4] else pp[n]/v if n=='Mu4' else pp[n] for n in names]
 ewA=math.cos(phys['beta'])/math.sqrt(2); ewB=math.sin(phys['beta'])/math.sqrt(2); ve=float(f([ewA,ewB,0,0,0],pars)[0]); best=None; levels={}; started=time.monotonic()
 for seed in range(512):
  rng=np.random.default_rng(seed); start=[*rng.uniform(0,2,3),rng.uniform(0,math.pi/2),rng.uniform(-math.pi,math.pi)]
  def fun(q):
   value,gradient=f(q,pars); return float(value),np.asarray(gradient,dtype=float)
  res=minimize(fun,start,method='L-BFGS-B',jac=True,bounds=[(0,12)]*3+[(0,math.pi/2),(-math.pi,math.pi)],options={'maxiter':180,'ftol':1e-12,'gtol':1e-8})
  if np.isfinite(res.fun) and (best is None or res.fun<best['value']): best={'value':float(res.fun),'orbit':[float(z) for z in res.x], 'seed':seed,'success':bool(res.success)}
  if seed+1 in (32,128,512): levels[str(seed+1)]={'best_delta_over_v4':best['value']-ve,'negative_numerical':best['value']-ve < -1e-9,'best_seed':best['seed'],'orbit':best['orbit'][:], 'seconds':time.monotonic()-started}
 # Store literal finite-start numerical evidence; proof labels come only from separately verified certs.
 result={'family':key[0],'k':key[1],'levels':levels,'total_seconds':time.monotonic()-started,'seed_rule':'numpy.default_rng(seed), seed=0..511 independently per card','global_acceptance':None}
 with output.open('a') as fp: fp.write(json.dumps(result,separators=(',',':'))+'\n')
 print(key,levels['512']['best_delta_over_v4'],round(result['total_seconds'],1),flush=True)
