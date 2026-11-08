#!/usr/bin/env python3
"""Predeclared fixed-potential continuation: preliminary, incomplete gates."""
import csv, json, math, pathlib
from fractions import Fraction as Q
from verify_independent import ROOT, run

OUT=pathlib.Path(__file__).parent
records=json.loads((ROOT/'validation/module1/d10_vacuum_global.json').read_text())['records']
cards=json.loads((ROOT/'module1/d10_benchmarks.json').read_text())['records']
threshold=json.loads((ROOT/'research/full_constraints/candidate_a/CERTIFICATES/p2_refined_witness.json').read_text())['threshold_GeV_interval']
hi=Q(threshold[1]); families=[('P2_beta_shift',None),('d7_NO_neutral_near_heavy_07','1650627/250000'),('F13_heavy_0001330','1232051/200000')]
rows=[]
for name,eps in families:
 r=next(x for x in records if x['benchmark_id']==name); phys=next(x['input']['physical'] for x in cards if x['input']['benchmark_id']==name); parent=r['lagrangian_parameters']; v=phys['v']; a=v*math.cos(phys['beta']); b=v*math.sin(phys['beta'])
 md=v*v*(parent['M12Sq']/(a*b)-(parent['Lambda4']+parent['Lambda5'])/2)
 ms=parent['MCS2']+(parent['K1']*a*a+parent['K2']*b*b-2*parent['K12']*a*b)/2
 for k in range(31):
  p=dict(parent); p['Mu4']=float(Q(parent['Mu4'])*Q(k,20)); rr=dict(r); rr['lagrangian_parameters']=p
  off=p['Mu4']*v/math.sqrt(2); gap=math.hypot(md-ms,2*off); lo=(md+ms-gap)/2; up=(md+ms+gap)/2
  m1=math.sqrt(lo) if lo>0 else None; m2=math.sqrt(up) if up>0 else None; sintwo=2*off/gap if gap else 0
  mz=91.1876; mw=80.379; coupling=mz*sintwo/(2*v); width=None; opened=False
  if m1 is not None and m2 is not None:
   opened=m2>m1+mz
   lam=((m2*m2-(m1+mz)**2)*(m2*m2-(m1-mz)**2))
   width=sintwo*sintwo*max(lam,0)**1.5/(64*math.pi*v*v*m2**3) if opened else 0.
  status='UNKNOWN'; proof='none'
  if eps:
   try:
    run(rr,phys,eps); status='CERTIFIED_STABLE'; proof='independent exact root and fixed epsilon Sylvester'
   except (AssertionError,ValueError,ZeroDivisionError): pass
  elif Q(p['Mu4'])>hi:
   status='CERTIFIED_DEEPER_VACUUM'; proof='reused archived exact P2 fixed-field threshold; independent verification pending'
  rows.append({'family':name,'k':k,'Mu4_GeV':p['Mu4'],'Mu4_exact_binary64':str(Q(p['Mu4'])),'parent_scalar_sha256':r['lagrangian_parameters_sha256'],'source':'original' if k==20 else 'intentional_deformation','tree_bfb':r['scalar_gates']['bfb']['assessment'],'tree_unitarity':r['scalar_gates']['unitarity']['assessment'],'quartic_gate':'reused parent (unchanged quartics)','local_charged_positive_numerical':lo>0,'local_full_EW_hessian':'NOT_EVALUATED','vacuum_status':status,'proof':proof,'mH1_GeV':m1,'mH2_GeV':m2,'sin_2gamma_convention_positive_mu':sintwo,'abs_gZ12':abs(coupling),'on_shell_open':opened,'width_GeV':width,'global_acceptance':None})
(OUT/'SCALAR_ONLY_PRELIMINARY.json').write_text(json.dumps(rows,indent=2)+'\n')
with (OUT/'SCALAR_ONLY_PRELIMINARY.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
from collections import Counter
for name,_ in families:
 print(name,Counter(row['vacuum_status'] for row in rows if row['family']==name))
