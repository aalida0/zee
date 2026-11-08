#!/usr/bin/env python3
"""Finite exact rational orbit B&B fallback; returns UNKNOWN while boxes remain."""
import json, math, pathlib
from fractions import Fraction as Q
from verify_independent import ROOT,run,I,add,neg,mul,scale
r=json.loads((ROOT/'validation/module1/d10_vacuum_global.json').read_text())['records'][0]; ph=json.loads((ROOT/'module1/d10_benchmarks.json').read_text())['records'][0]['input']['physical'];p={k:Q(v) for k,v in r['lagrangian_parameters'].items()};p['Mu4']=Q(float(Q(p['Mu4'])*Q(27,20)))
k=Q(r['rigorous_radial_exclusion']['quartic_norm_lower_coefficient']); cubic=abs(p['Mu4'])/2; mass=Q(r['rigorous_radial_exclusion']['quadratic_norm_upper_coefficient_GeV2']);R=math.ceil((float(cubic)+math.sqrt(float(cubic*cubic+4*k*mass)))/(2*float(k)))+2
while k*R*R-cubic*R-mass<=0:R+=1
N=Q(R*R); boxes=[[(Q(0),N)]*3+[(-N/2,N/2)]*2];processed=0;excluded=0;infeasible=0
root=run(r,ph,'1',root_only=True);rad=Q(root['radius']); a,b=[I(Q(z)-rad,Q(z)+rad) for z in root['neutral_center']]; x0=scale(Q(1,2),mul(a,a));y0=scale(Q(1,2),mul(b,b));u0=scale(Q(1,2),mul(a,b));ew=I(0)
for c,z in [(p['M112'],x0),(p['M222'],y0),(-2*p['M12Sq'],u0),(p['Lambda1']/2,mul(x0,x0)),(p['Lambda2']/2,mul(y0,y0)),(p['Lambda3']+p['Lambda4']+p['Lambda5'],mul(x0,y0))]:ew=add(ew,scale(c,z))
def square(a):
 lo,hi=a;return (Q(0) if lo<=0<=hi else min(lo*lo,hi*hi),max(lo*lo,hi*hi))
def sqrt_up(v):
 if v<=0:return Q(0)
 return Q(math.isqrt(v.numerator*v.denominator)+1,v.denominator)
def lower(box):
 x,y,z,u,w=box; xy=mul(x,y); u2=square(u);w2=square(w)
 if x[0]+y[0]+z[0]>N or u2[0]+w2[0]>xy[1]: return None
 D=max(Q(0),xy[1]-u2[0]-w2[0]); terms=[scale(p['M112'],x),scale(p['M222'],y),scale(-2*p['M12Sq'],u),scale(p['MCS2'],z),scale(p['Lambda1']/2,square(x)),scale(p['Lambda2']/2,square(y)),scale(p['Lambda3'],xy),scale(p['Lambda4']+p['Lambda5'],u2),scale(p['Lambda4']-p['Lambda5'],w2),scale(p['LambdaC'],square(z)),scale(p['K1'],mul(x,z)),scale(p['K2'],mul(y,z)),scale(-2*p['K12'],mul(u,z))]
 return sum(t[0] for t in terms)-2*abs(p['Mu4'])*sqrt_up(z[1]*D)
while boxes and processed<2000:
 box=boxes.pop();processed+=1; lo=lower(box)
 if lo is None: infeasible+=1;continue
 if lo>=ew[1]:excluded+=1;continue
 i=max(range(5),key=lambda j:box[j][1]-box[j][0]); l,h=box[i]; mid=(l+h)/2
 for pair in [(l,mid),(mid,h)]:
  b=box.copy();b[i]=pair;boxes.append(b)
result={'card':'P2 k=27','Mu4_exact':str(p['Mu4']),'radial_bound_GeV':R,'boxes_processed':processed,'infeasible':infeasible,'excluded_by_lower_bound':excluded,'remaining':len(boxes),'status':'UNKNOWN' if boxes else 'CERTIFIED_STABLE','note':'exact rational natural interval bounds and conservative rational sqrt upper; finite run does not prove unprocessed boxes','global_acceptance':None}
(pathlib.Path(__file__).parent/'CERTIFICATES'/'orbit_bnb_attempt.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
