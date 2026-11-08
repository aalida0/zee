#!/usr/bin/env python3
"""Independent rational Sylvester and fixed-point root check from frozen cards."""
import json, math, pathlib, hashlib
from fractions import Fraction as Q
import mpmath as mp
import sympy as sp
ROOT=pathlib.Path(__file__).resolve().parents[4]

def I(a,b=None): return (Q(a), Q(a if b is None else b))
def add(a,b): return (a[0]+b[0],a[1]+b[1])
def neg(a): return (-a[1],-a[0])
def mul(a,b):
    t=[x*y for x in a for y in b]; return (min(t),max(t))
def scale(c,a): return mul(I(c),a)
def mag(a): return max(abs(a[0]),abs(a[1]))
def run(rec, phys, ep, radius=Q(1,10**30), root_only=False):
    p={k:Q(float(v)) for k,v in rec['lagrangian_parameters'].items()}
    e=Q(ep); l=p['Lambda3']+p['Lambda4']+p['Lambda5']
    c=sp.Matrix([[p['Lambda1']/2,(p['Lambda3']-e)/2,0,0,p['K1']/2],[(p['Lambda3']-e)/2,p['Lambda2']/2,0,0,p['K2']/2],[0,0,p['Lambda4']+p['Lambda5']+e,0,-p['K12']],[0,0,0,p['Lambda4']-p['Lambda5']+e,0],[p['K1']/2,p['K2']/2,-p['K12'],0,p['LambdaC']]])
    minors=[Q(c[:i,:i].det()) for i in range(1,6)]
    assert root_only or all(x>0 for x in minors)
    with mp.workdps(80):
        cv=lambda v:mp.mpf(v.numerator)/v.denominator
        pp={k:cv(v) for k,v in p.items()}; lm=cv(l)
        a,b=mp.findroot(lambda a,b:(a*(pp['M112']+pp['Lambda1']*a*a/2+lm*b*b/2)-pp['M12Sq']*b,b*(pp['M222']+pp['Lambda2']*b*b/2+lm*a*a/2)-pp['M12Sq']*a),(phys['v']*math.cos(phys['beta']),phys['v']*math.sin(phys['beta'])))
        z=[Q(mp.nstr(a,60)),Q(mp.nstr(b,60))]
    assert max(abs(float(z[i])-phys['v']*([math.cos,math.sin][i])(phys['beta'])) for i in range(2))<1e-8
    rad=Q(radius); assert rad > 0; box=[I(v-rad,v+rad) for v in z]; a,b=z
    f=[a*(p['M112']+p['Lambda1']*a*a/2+l*b*b/2)-p['M12Sq']*b,b*(p['M222']+p['Lambda2']*b*b/2+l*a*a/2)-p['M12Sq']*a]
    def jac(x,y):
        xx=mul(x,x); yy=mul(y,y); xy=mul(x,y)
        return [[add(I(p['M112']),add(scale(3*p['Lambda1']/2,xx),scale(l/2,yy))),add(scale(l,xy),I(-p['M12Sq']))],[add(scale(l,xy),I(-p['M12Sq'])),add(I(p['M222']),add(scale(3*p['Lambda2']/2,yy),scale(l/2,xx)))]]
    j=jac(I(a),I(b)); j=[[x[0] for x in row] for row in j]; det=j[0][0]*j[1][1]-j[0][1]*j[1][0]
    inv=[[j[1][1]/det,-j[0][1]/det],[-j[1][0]/det,j[0][0]/det]]; jb=jac(*box)
    err=[[add(I(int(i==k)),neg(add(scale(inv[i][0],jb[0][k]),scale(inv[i][1],jb[1][k])))) for k in range(2)] for i in range(2)]
    contraction=max(sum(mag(x) for x in row) for row in err)
    residual=[abs(sum(inv[i][k]*f[k] for k in range(2))) for i in range(2)]
    assert contraction<1 and all(residual[i]+sum(mag(x)*rad for x in err[i])<rad for i in range(2))
    if root_only:
        return {'neutral_center':[str(x) for x in z], 'radius':str(rad), 'contraction_upper':str(contraction)}
    aa,bb=box; norm=add(mul(aa,aa),mul(bb,bb)); ab=mul(aa,bb)
    def divide(x,y):
        assert not y[0]<=0<=y[1]; return mul(x,(1/y[1],1/y[0]))
    md=mul(norm,add(divide(I(p['M12Sq']),ab),I(-(p['Lambda4']+p['Lambda5'])/2)))
    ms=add(I(p['MCS2']),scale(Q(1,2),add(add(scale(p['K1'],mul(aa,aa)),scale(p['K2'],mul(bb,bb))),scale(-2*p['K12'],ab))))
    margins=[add(md,scale(-e/2,norm)),add(ms,I(-p['Mu4']**2/e))]
    assert all(m[0]>0 for m in margins)
    return {'source_hash':rec['lagrangian_parameters_sha256'],'epsilon':str(e),'neutral_center':[str(x) for x in z],'radius':str(rad),'contraction_upper':str(contraction),'leading_principal_minors':[str(x) for x in minors],'pivots':[str(minors[i]/(minors[i-1] if i else 1)) for i in range(5)],'margin_intervals':[[str(t) for t in m] for m in margins], 'min_pivot_approx':min(float(minors[i]/(minors[i-1] if i else 1)) for i in range(5)), 'global_acceptance':None}
def check_saved(rec, phys, eps, stored):
    digest=hashlib.sha256(json.dumps(rec['lagrangian_parameters'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
    assert digest == rec['lagrangian_parameters_sha256'], 'source coefficient hash mismatch'
    assert run(rec,phys,eps) == stored, 'certificate differs from exact recomputation'

if __name__=='__main__':
    records=json.loads((ROOT/'validation/module1/d10_vacuum_global.json').read_text())['records']; cards=json.loads((ROOT/'module1/d10_benchmarks.json').read_text())['records']
    for name,eps in [('d7_NO_neutral_near_heavy_07','1650627/250000'),('F13_heavy_0001330','1232051/200000')]:
        r=next(x for x in records if x['benchmark_id']==name); phys=next(x['input']['physical'] for x in cards if x['input']['benchmark_id']==name)
        target=pathlib.Path(__file__).parent/'CERTIFICATES'/f'{name}.json'; stored=json.loads(target.read_text()); check_saved(r,phys,eps,stored); print(name,stored['min_pivot_approx'],[float(Q(x[0])) for x in stored['margin_intervals']])
