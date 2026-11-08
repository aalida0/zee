#!/usr/bin/env python3
import collections,csv,json,math,pathlib,sys
import numpy as np
from fractions import Fraction as Q
from verify_independent import ROOT
sys.path.insert(0,str(ROOT))
from module1.potential import Potential,gauge_audit
HERE=pathlib.Path(__file__).parent
rows=json.loads((HERE/'SCALAR_ONLY_PRELIMINARY.json').read_text()); searches={(z['family'],z['k']):z for z in map(json.loads,(HERE/'FINITE_START.jsonl').read_text().splitlines())}; records=json.loads((ROOT/'validation/module1/d10_vacuum_global.json').read_text())['records'];cards=json.loads((ROOT/'module1/d10_benchmarks.json').read_text())['records']
for row in rows:
 name=row['family'];rec=next(z for z in records if z['benchmark_id']==name);ph=next(z['input']['physical'] for z in cards if z['input']['benchmark_id']==name);p=dict(rec['lagrangian_parameters']);p['Mu4']=row['Mu4_GeV']; v=ph['v'];q=np.zeros(10);q[2]=v*math.cos(ph['beta']);q[6]=v*math.sin(ph['beta']);_,g,H=Potential(p).evaluate(q);rank,minimum,ward=gauge_audit(q,H);row['local_ew_transverse_min_GeV2']=minimum;row['ew_tadpole_residual_GeV3']=max(abs(g));row['gauge_rank']=rank;row['local_ew_positive_numerical']=bool(rank==3 and minimum>0 and ward<1e-6);row['local_bfb_unitarity']=bool(row['local_ew_positive_numerical'] and row['tree_bfb']=='PASS' and row['tree_unitarity']=='PASS');row['local_full_EW_hessian']='numerical full Hessian, EW Goldstones projected';row['proof']='independent exact root and fixed-field witness' if name=='P2_beta_shift' and row['vacuum_status']=='CERTIFIED_DEEPER_VACUUM' else row['proof']
 sr=searches[(name,row['k'])];row['starts_32_negative']=sr['levels']['32']['negative_numerical'];row['starts_128_negative']=sr['levels']['128']['negative_numerical'];row['starts_512_negative']=sr['levels']['512']['negative_numerical'];row['search_seconds']=sr['total_seconds'];
 # Explicit rest-frame physical polarization sum for derivative vertex: g*(p_parent+p_daughter) dot eps.
 M=row['mH2_GeV'];m=row['mH1_GeV'];mz=ph.get('mZ',91.1876);mz=91.1876
 if row['on_shell_open']:
  mom=math.sqrt((M*M-(m+mz)**2)*(M*M-(m-mz)**2))/(2*M); ed=(M*M+m*m-mz*mz)/(2*M);ez=(M*M-m*m+mz*mz)/(2*M); current=np.array([M+ed,0.,0.,-mom]); eps=np.array([mom/mz,0.,0.,ez/mz]); amp=current[0]*eps[0]-np.dot(current[1:],eps[1:]); width=row['abs_gZ12']**2*amp**2*mom/(8*math.pi*M*M); assert math.isclose(width,row['width_GeV'],rel_tol=1e-12,abs_tol=1e-12);row['polarization_width_GeV']=width
 else:row['polarization_width_GeV']=0. if M and m else None
 row['global_acceptance']=None
(HERE/'SCALAR_ONLY_RESULT_TABLE.json').write_text(json.dumps(rows,indent=2)+'\n')
with (HERE/'SCALAR_ONLY_RESULT_TABLE.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0],lineterminator="\n");w.writeheader();w.writerows(rows)
for fam in sorted(set(r['family'] for r in rows)):
 rs=[r for r in rows if r['family']==fam];print(fam,'status',dict(collections.Counter(r['vacuum_status'] for r in rs)),'local',sum(r['local_bfb_unitarity'] for r in rs),'numerical detects',*[sum(r[f'starts_{n}_negative'] for r in rs) for n in (32,128,512)],'sec',round(sum(r['search_seconds'] for r in rs),2))
