#!/usr/bin/env python3
"""Numerical stationary comparison to Barroso-Ferreira (2005) Eq. 23."""
import json,math,pathlib
import mpmath as mp
import sympy as sp
from verify_independent import ROOT
R=json.loads((ROOT/'validation/module1/d10_vacuum_global.json').read_text())['records'][0]; P=R['lagrangian_parameters'];card=json.loads((ROOT/'module1/d10_benchmarks.json').read_text())['records'][0]['input']['physical']
with mp.workdps(65):
 p={k:mp.mpf(float(v)) for k,v in P.items()}; mu=mp.mpf(float(P['Mu4']*1.5)); l=p['Lambda3']+p['Lambda4']+p['Lambda5']
 a,b=mp.findroot(lambda a,b:(a*(p['M112']+p['Lambda1']*a*a/2+l*b*b/2)-p['M12Sq']*b,b*(p['M222']+p['Lambda2']*b*b/2+l*a*a/2)-p['M12Sq']*a),(card['v']*math.cos(card['beta']),card['v']*math.sin(card['beta'])))
 def pot(h,c,n,s):
  x=h*h;y=c*c+n*n;u=h*n;z=s*s
  return p['M112']*x+p['M222']*y-2*p['M12Sq']*u+p['MCS2']*z-2*mu*s*h*c+p['Lambda1']*x*x/2+p['Lambda2']*y*y/2+p['Lambda3']*x*y+(p['Lambda4']+p['Lambda5'])*u*u+p['LambdaC']*z*z+(p['K1']*x+p['K2']*y-2*p['K12']*u)*z
 init=[mp.mpf(v)/mp.sqrt(2) for v in [161.80291128209644,459.83710213975801,232.17088429845256,201.05569456314806]]
 h,c,n,t=mp.findroot(lambda h,c,n,t: tuple(mp.diff(lambda z: pot(*(h,c,n,t)[:i],z,*(h,c,n,t)[i+1:]),(h,c,n,t)[i]) for i in range(4)),init,solver='mdnewton',tol=mp.mpf('1e-55'),maxsteps=30)
 v1=a/mp.sqrt(2);v2=b/mp.sqrt(2); x0=t*t;x1=h*h;x2=c*c+n*n;x3=h*n; xn3=v1*v2
 def d0(x,y,u,z):return p['MCS2']+2*p['LambdaC']*z+p['K1']*x+p['K2']*y-2*p['K12']*u
 def d3(u,z):return -2*p['M12Sq']+2*(p['Lambda4']+p['Lambda5'])*u-2*p['K12']*z
 Qgeom=(h*v2-n*v1)**2+(v2*0-v1*c)**2
 rhs=x0*(d0(v1*v1,v2*v2,xn3,0)-d0(x1,x2,x3,x0))+(d3(x3,x0)/x3-d3(xn3,0)/xn3)*Qgeom/2
 lhs=2*(pot(h,c,n,t)-pot(v1,0,v2,0)); relative=abs(lhs-rhs)/max(abs(lhs),1)
 print('debug',mp.nstr(lhs,15),mp.nstr(rhs,15),mp.nstr(relative,8),mp.nstr(x3,8))
 assert relative<mp.mpf('1e-48')
 out={'source':'Barroso Ferreira 2005 arXiv hep-ph/0507128v3 Eq.23','normal_vevs_complex_units_GeV':[str(v1),str(v2)],'cb_fields_complex_units_GeV':[str(h),str(c),str(n),str(t)],'Mu4_GeV':str(mu),'deltaV_GeV4':str(lhs/2),'eq23_lhs_GeV4':str(lhs),'eq23_rhs_GeV4':str(rhs),'relative_residual':str(relative),'method':'65-digit stationary root in real gauge chart, not an interval root proof','global_acceptance':None}
 (pathlib.Path(__file__).parent/'CERTIFICATES'/'eq23_numerical.json').write_text(json.dumps(out,indent=2)+'\n');print('delta',mp.nstr(lhs/2,15),'relative residual',mp.nstr(relative,5))
