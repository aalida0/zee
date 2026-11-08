#!/usr/bin/env python3
"""Independent fixed-card arithmetic controls, not complete physical predictions."""
import hashlib,json,math,sys
from pathlib import Path
from statistics import NormalDist
R=Path(__file__).resolve().parents[3]; O=Path(__file__).resolve().parent
TABLE=Path('/tmp/zee-hepfit/HEPfit-322bd73a2dadd94ce94a6d71cb79d616e569120a/THDM/tabs/bsgammatable.dat')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cm(z):return complex(z['real'],z['imag'])
def matrix(z):return [[complex(a,b) for a,b in zip(r,i)] for r,i in zip(z['real'],z['imag'])]
def main():
 d=json.loads((R/'validation/module12/d12_benchmarks.json').read_text()); ref=json.loads((R/'research/full_constraints/lfv/TEXTURE_COUPLING_AUDIT.json').read_text()); saved={x['id']:x for x in ref['cards']};lim=1.3677858240837514e-12
 records=[]
 for g in d['groups']:
  w=g['witnesses']['low_joint']; x=w['signed_radiative']['mu_to_e_gamma']; cl,cr=cm(x['C_L']),cm(x['C_R']); f=matrix(w['yukawas']['F']); inv=sum(f[k][0].conjugate()*f[k][1] for k in range(3)); norm=math.hypot(abs(cl),abs(cr)); orig=saved[w['id']]
  cs=math.sqrt(sum(abs(f[k][0])**2 for k in range(3))*sum(abs(f[k][1])**2 for k in range(3)))
  assert abs(inv)<=cs*(1+1e-14)
  assert math.isclose(abs(inv),orig['FdagF_em']['abs'],rel_tol=2e-14)
  assert math.isclose(norm,orig['retained_norm'],rel_tol=2e-14)
  for j,c in enumerate((cl,cr)):
   z=sum((cm(v[j]) for v in x['grouped_amplitudes'].values()),0j); assert abs(z-c)<1e-29
  records.append({'id':w['id'],'ordering':g['ordering'],'scalar_sha256':g['scalar_sha256'],'yukawa_sha256':w['yukawa_sha256'],'retained_CL_abs':abs(cl),'retained_CR_abs':abs(cr),'retained_norm':norm,'FdagF_em_abs':abs(inv),'FdagF_cauchy_upper_bound':cs,'sufficient_missing_norm_budget':lim-norm,'missing_bound':None,'status':'UNKNOWN','BR_retained':x['BR_implemented']})
 assert digest(TABLE)=='4ab62f2e4ab2897232e284060aa14349f54a47b9e47f70c883a8b11e4749a6f8'
 rows=[list(map(float,line.split())) for line in TABLE.read_text().splitlines() if line.strip() and not line.lstrip().startswith('#')]; grid={(x,y):z for x,y,z in rows};ys=sorted(y for x,y in grid if x==2.0)
 def rate(m):
  y=math.log10(m);lo=max(v for v in ys if v<=y);hi=min(v for v in ys if v>y);return grid[2.,lo]+(grid[2.,hi]-grid[2.,lo])*(y-lo)/(hi-lo)
 z=NormalDist().inv_cdf(.95);ex=3.43e-4;sig=math.hypot(.21,.07)*1e-4
 def pull(m):return (rate(m)-ex)/math.hypot(sig,.07*rate(m))
 lo,hi=300.,800.
 for i in range(80):
  mid=(lo+hi)/2
  if pull(mid)>z:lo=mid
  else:hi=mid
 root=(lo+hi)/2;assert abs(root-473.1082454034481)<1e-8
 h=json.loads((R/'research/full_constraints/higgs/H125_VBF_BB_MATERIALITY.json').read_text()); d10=json.loads((R/'module1/d10_benchmarks.json').read_text())['records']; hcontrols=[]
 for case in h['cases']:
  card=next(r for r in d10 if r['input_sha256']==case['scalar_sha256']); p=card['input']['physical']; vals={}
  for key in ('mH1','mH2','ma','mh2'):
   m=p[key];bound=1/(m*m-p['mh1']**2); scanned=max(1/(m*m-(p['mh1']**2)*i/1000) for i in range(1001)); assert math.isclose(bound,scanned,rel_tol=1e-14);assert math.isclose(bound,case['heavy_scalar_propagator_bounds'][key]['max_abs_GeV_minus2'],rel_tol=1e-14);vals[key]=bound
  A=case['retained_WW_ZZ_proxy_GeV'];delta=min(abs(x) for x in case['signed_delta_to_68_endpoints_GeV']);B=(math.sqrt(A+delta)-math.sqrt(A))**2;assert math.isclose(B,case['conditional_Cauchy_BSM_norm_target_GeV'],rel_tol=1e-14)
  hcontrols.append({'case':case['name'],'propagator_maxima_GeV_minus2':vals,'conditional_B_target_GeV':B,'physical_B_bound':None,'note':'kinematic propagator maximum and conditional budget only, not a 4f width bound'})
 output={'higgs':hcontrols,'lfv':records,'b_control':{'table_sha256':digest(TABLE),'cut_GeV':1.6,'tanbeta':100,'theory_fraction_illustrative':.07,'observed':ex,'experimental_sigma':sig,'interpolated_root_GeV':root,'published_rounded_GeV':480,'BR_at_480':rate(480),'physical_zee_theory_sigma':None,'physical_95_exclusion':None}}
 (O/'INDEPENDENT_CONTROLS.json').write_text(json.dumps(output,indent=2)+'\n');print('4 LFV complex replays; 8 Higgs propagator bounds; historical table root:',root)
if __name__=='__main__':main()
