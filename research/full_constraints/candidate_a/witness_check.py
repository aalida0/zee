#!/usr/bin/env python3
"""Exact rational fixed-field P2 witness; frozen Krawczyk root enclosure."""
import json, math, pathlib, sys
from fractions import Fraction as Q
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from module1.d10_certificate import neutral_enclosure, rational_parameters

root=pathlib.Path(__file__).resolve().parents[3]
data=json.loads((root/'validation/module1/d10_vacuum_global.json').read_text())
cards=json.loads((root/'module1/d10_benchmarks.json').read_text())['records']
r=next(a for a in data['records'] if a['benchmark_id']=='P2_beta_shift')
physical=next(a['input']['physical'] for a in cards if a['input']['benchmark_id']=='P2_beta_shift')
p=rational_parameters(r['lagrangian_parameters'])
a,b=neutral_enclosure(r['lagrangian_parameters'], physical)[0]
x0,y0,u0=a*a/2,b*b/2,a*b/2
vew=p['M112']*x0+p['M222']*y0-2*p['M12Sq']*u0+p['Lambda1']*x0*x0/2+p['Lambda2']*y0*y0/2+(p['Lambda3']+p['Lambda4']+p['Lambda5'])*x0*y0
# Real complex-field components, not canonical real fields. Rounded fixed decimals are exact rationals.
coordinates = sys.argv[1:] or ['114.414906','325.150909','164.166593','142.168844']
if len(coordinates) != 4: raise ValueError('supply four exact decimal complex-field coordinates')
h10,h2p,h20,s=map(Q,coordinates)
x=h10*h10; y=h2p*h2p+h20*h20; u=h10*h20; ss=s*s; d=-h10*h2p
v0=p['M112']*x+p['M222']*y-2*p['M12Sq']*u+p['MCS2']*ss+p['Lambda1']*x*x/2+p['Lambda2']*y*y/2+p['Lambda3']*x*y+(p['Lambda4']+p['Lambda5'])*u*u+p['LambdaC']*ss*ss+(p['K1']*x+p['K2']*y-2*p['K12']*u)*ss
slope=2*s*d
assert slope<0
threshold=(v0-vew)/(-slope)
checks={}
for m in ['943.4001484550731','1179.2501855688414','1316.13','1316.14','1346.14','1350','1415.1002226826096']:
    gap=v0+Q(m)*slope-vew
    checks[m]={'delta_interval_GeV4':gap.serial(),'delta_approx_GeV4':float((gap.lo+gap.hi)/2),'strictly_deeper':gap.hi<0}
assert checks['1415.1002226826096']['strictly_deeper']
out={'schema':'fixed-field-rational-v1','global_acceptance':None,'field_complex_real_GeV':{'H1plus':'0','H10':str(h10),'H2plus':str(h2p),'H20':str(h20),'Splus':str(s)},'lagrangian_input_sha256':r['lagrangian_parameters_sha256'],'ew_root':'frozen exact rational Krawczyk enclosure', 'slope_GeV3':str(slope),'threshold_GeV_interval':threshold.serial(),'threshold_approx_GeV':float((threshold.lo+threshold.hi)/2),'checks':checks,'interpretation':'Necessary upper bound on positive Mu4 for this fixed-coefficient slice only; does not certify stability below threshold.'}
print(json.dumps(out,indent=2))
