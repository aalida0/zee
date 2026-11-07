#!/usr/bin/env python3
"""Read-only reconstruction of saved D12 witnesses and exact D14 map families."""
import csv, hashlib, json, math
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parents[3]
paths=['validation/module12/d12_benchmarks.json','validation/module12/d12_validation.json','module14/conditional_scan/production_map_13TeV_families.csv','module14/conditional_scan/production_map_14TeV_families.csv']
sources={p:{'bytes':(R/p).stat().st_size,'sha256':hashlib.sha256((R/p).read_bytes()).hexdigest()} for p in paths}
x=json.loads((R/paths[0]).read_text()); assert x['global_zee_acceptance'] is None and x['evaluated_solution_count']==136
witness=[]; pairs=[]
for g in x['groups']:
 assert len(g['family'])==28 and len(g['texture_sensitivity'])==6
 ws={}
 for label,w in g['witnesses'].items():
  assert w['scalar_sha256']==g['scalar_sha256'] and w['global_zee_acceptance'] is None
  obs={}
  for h in ('H1','H2'):
   d=w['decays'][h]; t=d['total']; total=t['total_width_GeV']; br=t['branching_fractions']; channels={c['channel']:c['width_GeV'] for c in g['nonleptonic_decay_channels'][h]+d['channels']}
   assert math.isclose(sum(channels.values()),total,rel_tol=1e-12)
   assert math.isclose(sum(br.values()),1,rel_tol=1e-12)
   for c,b in br.items(): assert math.isclose(channels[c]/total,b,rel_tol=1e-12,abs_tol=1e-15)
   obs[h]={'total_width_GeV':total,'tb':br['t anti-b'],'e':br['e nu_all'],'mu':br['mu nu_all'],'tau':br['tau nu_all'],'lnu':sum(br[a+' nu_all'] for a in ('e','mu','tau'))}
   if h=='H2': obs[h]['H1Z']=br['H1 Z']
  z=obs['H2']['H1Z']; a=obs['H1']; obs['cascade']={k:z*a[k] for k in ('tb','e','mu','tau','lnu')}; obs['cascade']['lnu_over_tb']=a['lnu']/a['tb'] if a['tb'] else None
  row={'id':w['id'],'label':label,'scalar':g['scalar'],'scalar_sha256':g['scalar_sha256'],'ordering':g['ordering'],'target':w['target'],'yukawa_sha256':w['yukawa_sha256'],'closure_relative':w['metrics']['closure_relative'],'perturbativity':w['metrics']['selection'],'vacuum':w['tree_vacuum'],'global_acceptance':None,'production_pb':None,'production_reason':'No exact D12 production receipt','objective':w['objective'],'observables':obs}
  ws[label]=row; witness.append(row)
 for label in ('high_F','high_joint','low_joint'):
  a,b=ws['central'],ws[label]; assert a['target']==b['target']
  oa,ob=a['observables'],b['observables']; base=oa['cascade']['lnu']; new=ob['cascade']['lnu']
  pairs.append({'scalar':g['scalar'],'ordering':g['ordering'],'from':a['id'],'to':b['id'],'same_scalar_sha256':g['scalar_sha256'],'same_target':True,'delta_H1_lnu':ob['H1']['lnu']-oa['H1']['lnu'],'delta_H1_tb':ob['H1']['tb']-oa['H1']['tb'],'cascade_lnu_ratio':new/base if base else None,'delta_cascade_lnu':new-base,'H1_width_ratio':ob['H1']['total_width_GeV']/oa['H1']['total_width_GeV'],'H2_width_ratio':ob['H2']['total_width_GeV']/oa['H2']['total_width_GeV'],'absolute_material_0p10':abs(ob['H1']['lnu']-oa['H1']['lnu'])>=.1,'cascade_factor_2':new/base>=2 or new/base<=.5 if base and new else None})
records={}; spreads=[]
for energy,p in [('13',paths[2]),('14',paths[3])]:
 with (R/p).open() as f: rows=list(csv.DictReader(f))
 assert len(rows)==({'13':64,'14':12}[energy]); groups=defaultdict(list)
 for r in rows:
  assert r['energy_TeV']==energy and r['global_acceptance']=='null' and r['vacuum']=='PASS' and r['neutrino_status']=='PASS'
  d=json.loads(r['H1_decay_BR_separate']); assert math.isclose(sum(d.values()),1,rel_tol=1e-12)
  z=float(r['BR_H2_H1Z']); sig=float(r['sigma_pb']); assert math.isclose(sig*z,float(r['sigma_times_BR_pb']),rel_tol=1e-12)
  o={'H2_H1Z':z,'H1_tb':d['t anti-b'],'H1_e':d['e nu_all'],'H1_mu':d['mu nu_all'],'H1_tau':d['tau nu_all'],'H1_lnu':sum(d[a+' nu_all'] for a in ('e','mu','tau')),'sigma_pb':sig,'sigma_times_cascade_pb':sig*z,'sigma_times_cascade_tb_pb':sig*z*d['t anti-b'],'sigma_times_cascade_lnu_pb':sig*z*sum(d[a+' nu_all'] for a in ('e','mu','tau')),'H1_total_width_GeV':float(r['H1_total_width_GeV']),'H2_total_width_GeV':float(r['H2_total_width_GeV']),'H2_tb':None,'H2_lnu':None,'missing_reason':'H2 channel widths absent from family CSV'}
  row={'id':r['id'],'ordering':r['ordering'],'family':r['family'],'scalar_sha256':r['scalar_sha256'],'mapped_card_sha256':r['mapped_card_sha256'],'module2_input_sha256':r['module2_input_sha256'],'receipt_sha256':r['receipt_sha256'],'global_acceptance':None,'observables':o}; groups[r['id']].append(row)
 assert len(groups)==({'13':16,'14':3}[energy])
 for id,rs in groups.items():
  assert len(rs)==4 and len({(r['ordering'],r['family']) for r in rs})==4
  assert len({r['scalar_sha256'] for r in rs})==len({r['receipt_sha256'] for r in rs})==len({r['observables']['sigma_pb'] for r in rs})==1 and len({r['mapped_card_sha256'] for r in rs})==4
  vals=[r['observables']['H2_H1Z'] for r in rs]; spreads.append({'energy':energy,'id':id,'relative_spread_percent':100*(max(vals)-min(vals))/min(vals),'min':min(vals),'max':max(vals)})
 records[energy]=[r for rs in groups.values() for r in rs]
assert {r['id'] for r in records['14']} <= {r['id'] for r in records['13']}
out={'semantics':{'null':'not computed or not source-bound; not zero or pass','status':'conditional on saved tree two-body prescription; not independent physics validation','global_acceptance':None,'full_B_LFV_Higgs':'UNKNOWN'},'sources':sources,'D12_family_summaries':[{'scalar':g['scalar'],'scalar_sha256':g['scalar_sha256'],'ordering':g['ordering'],'family':g['family'],'sensitivity':g['texture_sensitivity']} for g in x['groups']],'D12_witnesses':witness,'D12_pairs':pairs,'D14_rows':records,'D14_spreads':spreads}
p=R/'research/full_constraints/flavor_cascade/NOVELTY_WITNESS_MATRIX.json'; p.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
print('PASS: 16 D12 witness ledgers, 12 same-target pairs; 64 + 12 D14 rows; width, BR, identity, receipt and rate checks')
print('D14 13 TeV relative spread percent range:',min(s['relative_spread_percent'] for s in spreads if s['energy']=='13'),max(s['relative_spread_percent'] for s in spreads if s['energy']=='13'))
for p in pairs: print(p['scalar'],p['ordering'],p['to'].split('/')[-1],p['delta_H1_lnu'],p['cascade_lnu_ratio'],p['H1_width_ratio'],p['H2_width_ratio'])
