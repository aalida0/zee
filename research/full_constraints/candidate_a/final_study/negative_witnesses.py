#!/usr/bin/env python3
"""Independent rational root and energy enclosure for fixed-field counterexamples."""
import json, pathlib
from fractions import Fraction as Q
from verify_independent import ROOT,run,I,add,neg,mul,scale
def div(a,b):
 assert not b[0]<=0<=b[1]; return mul(a,(1/b[1],1/b[0]))
outdir=pathlib.Path(__file__).parent
records=json.loads((ROOT/'validation/module1/d10_vacuum_global.json').read_text())['records']
cards=json.loads((ROOT/'module1/d10_benchmarks.json').read_text())['records']
def compute(name, coords, mus):
 r=next(x for x in records if x['benchmark_id']==name); ph=next(x['input']['physical'] for x in cards if x['input']['benchmark_id']==name)
 root=run(r,ph,'1',root_only=True); centers=[Q(x) for x in root['neutral_center']]; rad=Q(root['radius']); a,b=[I(x-rad,x+rad) for x in centers]
 p={k:Q(v) for k,v in r['lagrangian_parameters'].items()}; x=scale(Q(1,2),mul(a,a)); y=scale(Q(1,2),mul(b,b)); u=scale(Q(1,2),mul(a,b))
 ew=I(0)
 for c,v in [(p['M112'],x),(p['M222'],y),(-2*p['M12Sq'],u),(p['Lambda1']/2,mul(x,x)),(p['Lambda2']/2,mul(y,y)),(p['Lambda3']+p['Lambda4']+p['Lambda5'],mul(x,y))]: ew=add(ew,scale(c,v))
 h,c,n,ss=map(Q,coords); xx=h*h; yy=c*c+n*n; uu=h*n; sq=ss*ss; d=-h*c
 base=p['M112']*xx+p['M222']*yy-2*p['M12Sq']*uu+p['MCS2']*sq+p['Lambda1']*xx**2/2+p['Lambda2']*yy**2/2+p['Lambda3']*xx*yy+(p['Lambda4']+p['Lambda5'])*uu**2+p['LambdaC']*sq**2+(p['K1']*xx+p['K2']*yy-2*p['K12']*uu)*sq
 slope=2*ss*d
 results={}
 norm=add(mul(a,a),mul(b,b)); md=mul(norm,add(div(I(p['M12Sq']),mul(a,b)),I(-(p['Lambda4']+p['Lambda5'])/2))); ms=add(I(p['MCS2']),scale(Q(1,2),add(add(scale(p['K1'],mul(a,a)),scale(p['K2'],mul(b,b))),scale(-2*p['K12'],mul(a,b)))))
 for m in mus:
  gap=add(I(base+Q(m)*slope),neg(ew)); det=add(mul(md,ms),scale(-Q(m)**2/2,norm)); results[str(m)]={'interval':[str(v) for v in gap], 'approx':float(sum(gap)/2),'negative':gap[1]<0, 'charged_matrix_positive':md[0]>0 and det[0]>0, 'charged_det_interval':[str(v) for v in det]}
 threshold=None if not slope else [(str((base-ew[i])/(-slope))) for i in [1,0]]
 return {'source_hash':r['lagrangian_parameters_sha256'],'root':root,'coordinates':coords,'slope':str(slope),'threshold':threshold,'checks':results,'global_acceptance':None}
fields1=['83.452326','249.215787','172.247542','100.351097']; fields2=['114.414906','325.150909','164.166593','142.168844']
a=compute('P2_beta_shift',fields1,['1316.13','1316.14','1415.1002226826096']); b=compute('P2_beta_shift',fields2,['1346.14','1346.15','1415.1002226826096']); assert not a['checks']['1316.13']['negative'] and a['checks']['1316.14']['negative'];assert b['checks']['1346.15']['negative']
# Pure singlet: choose an exact rational nearby axis field; no stationarity assumption.
c=compute('physical_deeper_singlet',['0','0','0','500'],['0']); print('singlet gap',c['checks']['0']['approx']);
if not c['checks']['0']['negative']:
 r=next(x for x in records if x['benchmark_id']=='physical_deeper_singlet'); import math
 opt=math.sqrt(-r['lagrangian_parameters']['MCS2']/(2*r['lagrangian_parameters']['LambdaC']))
 c=compute('physical_deeper_singlet',['0','0','0',str(round(opt,8))],['0'])
assert c['checks']['0']['negative']
(outdir/'CERTIFICATES'/'negative_independent.json').write_text(json.dumps({'p2_refined':a,'p2_old':b,'singlet':c},indent=2)+'\n')
for label,x in [('refined',a),('old',b),('singlet',c)]: print(label,'threshold',float(Q(x['threshold'][0])) if x['threshold'] else None,'checks',[(m,v['approx']) for m,v in x['checks'].items()])
