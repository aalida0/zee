#!/usr/bin/env python3
"""Optimize fixed-field Mu4 thresholds in an explicit physical real chart."""
import json,math,pathlib
import numpy as np
from scipy.optimize import minimize
from verify_independent import ROOT
from negative_witnesses import compute
rs=json.loads((ROOT/'validation/module1/d10_vacuum_global.json').read_text())['records'];p=rs[0]['lagrangian_parameters'];v=246.21965;beta=json.loads((ROOT/'module1/d10_benchmarks.json').read_text())['records'][0]['input']['physical']['beta'];a=v*math.cos(beta)/math.sqrt(2);b=v*math.sin(beta)/math.sqrt(2)
def base(h,c,n,s):
 x=h*h;y=c*c+n*n;u=h*n;z=s*s
 return p['M112']*x+p['M222']*y-2*p['M12Sq']*u+p['MCS2']*z+p['Lambda1']*x*x/2+p['Lambda2']*y*y/2+p['Lambda3']*x*y+(p['Lambda4']+p['Lambda5'])*u*u+p['LambdaC']*z*z+(p['K1']*x+p['K2']*y-2*p['K12']*u)*z
ve=base(a,0,b,0)
def fun(q):
 h,c,n,s=q*v
 return (base(h,c,n,s)-ve)/(2*h*c*s)
best=None
for seed in range(16):
 rng=np.random.default_rng(seed); init=rng.uniform(.2,1.4,4)
 z=minimize(fun,init,method='L-BFGS-B',bounds=[(.01,5)]*4,options={'ftol':1e-15,'gtol':1e-9,'maxiter':2000,'maxls':60})
 if best is None or z.fun<best.fun:best=z
coords=[str(round(float(t*v),6)) for t in best.x];cert=compute('P2_beta_shift',coords,['1316.13','1316.14']);print('opt',best.fun,coords,cert['threshold']); pathlib.Path(__file__).with_name('CERTIFICATES').joinpath('optimized_witness.json').write_text(json.dumps({'search_method':'16 deterministic L-BFGS-B starts 0..15; bounded feasible real chart','coords':coords,'interval_proof':cert},indent=2)+'\n')
