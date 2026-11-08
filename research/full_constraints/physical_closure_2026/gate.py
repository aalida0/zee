#!/usr/bin/env python3
"""Conservative closure decision on explicit, source-bound evidence."""
from pathlib import Path
import json,hashlib,csv
HERE=Path(__file__).resolve().parent
MANDATORY=('bfb','unitarity','ewpo','tree_vacuum','neutrinos','mu_e_gamma','tau_l_gamma','mu_3e','mu_e_conversion','bsgamma','higgs','charged_widths','charged_collider','cosmology','other_applicable_constraints')
STATUSES={'VALIDATED_PASS','VALIDATED_FAIL','PARTIAL','UNKNOWN','NOT_APPLICABLE'}
def classify(card):
 if not card.get('join_verified',False):return 'UNKNOWN',None
 if card.get('ordering') not in ('NO','IO') or card.get('ordering')!=card.get('source_ordering'):raise ValueError('ordering mismatch')
 if not card.get('source_files'):raise ValueError('missing source files')
 for path,want in card['source_files'].items():
  try: got=hashlib.sha256(Path(path).read_bytes()).hexdigest()
  except OSError as e: raise ValueError('unavailable source') from e
  if got!=want:raise ValueError('bad source hash')
 if not card.get('scalar_sha256') or card.get('scalar_sha256')!=card.get('source_scalar_sha256'):raise ValueError('scalar identity mismatch')
 if not card.get('yukawa_sha256') or card.get('yukawa_sha256')!=card.get('source_yukawa_sha256'):raise ValueError('Yukawa identity mismatch')
 items=card.get('constraints',{})
 if set(items)!=set(MANDATORY):raise ValueError('missing mandatory constraint')
 for key,v in items.items():
  if v.get('status') not in STATUSES:raise ValueError('unknown status')
  if v['status'] in ('VALIDATED_PASS','VALIDATED_FAIL','NOT_APPLICABLE'):
   if not all(v.get(k) for k in ('source','scope','uncertainty')):raise ValueError('missing scientific evidence')
   if not v.get('coverage_complete'):raise ValueError('incomplete observable')
   if key=='bsgamma' and v.get('theory_sigma') is None:raise ValueError('missing B theory sigma')
   if key in ('higgs','charged_widths') and not v.get('all_applicable_widths'):raise ValueError('missing widths')
   if key in ('mu_e_gamma','tau_l_gamma','mu_3e','mu_e_conversion') and (not v.get('complete_operator_basis') or not v.get('phase_supported')):raise ValueError('missing operators or unsupported phase')
 if any(v['status']=='VALIDATED_FAIL' for v in items.values()):return 'PHYSICAL_FAIL',False
 if all(v['status'] in ('VALIDATED_PASS','NOT_APPLICABLE') for v in items.values()):return 'GLOBAL_PASS',True
 return 'UNKNOWN',None

def main():
 audit=json.loads((HERE/'JOIN_AUDIT_IN_PROGRESS.json').read_text()); sector=json.loads((HERE/'SECTOR_SNAPSHOT_IN_PROGRESS.json').read_text()); indexed={(r['case'],r['witness']):r for r in sector['rows']};rows=[]
 for x in audit['rows']:
  # Documentary joins are useful triage but raw receipt qualification is absent.
  statuses={k:{'status':'UNKNOWN'} for k in MANDATORY}
  for key in ('neutrinos','mu_e_gamma','bsgamma','higgs','charged_widths'):
   statuses[key]={'status':'PARTIAL','source':'SECTOR_SNAPSHOT_IN_PROGRESS.json','scope':'saved partial prediction; not a full physical pass','uncertainty':'incomplete'}
  snapshot=indexed[(x['case'],x['witness'])]
  for key in ('bfb','unitarity'):
   if snapshot['SCALAR_GATES'][key]=='PASS':statuses[key]={'status':'VALIDATED_PASS','source':'pinned original D14 dataset','scope':'sufficient tree BFB' if key=='bfb' else 'tree-level perturbative unitarity','uncertainty':'tree-level source scope; no loop or RG uncertainty','coverage_complete':True}
  if snapshot['SCALAR_GATES']['ewpo']=='PASS':statuses['ewpo']={'status':'PARTIAL','source':'pinned original D14 dataset','scope':'one-loop scalar oblique approximation only','uncertainty':'not a complete electroweak fit'}
  v=snapshot['VACUUM']
  if v['source_assessment']=='PASS' and v['source_certificate']:
   statuses['tree_vacuum']={'status':'VALIDATED_PASS','source':'saved D10 exact certificate, pinned source','scope':v['scope'],'uncertainty':'exact sufficient tree-level statement; quantum corrections not included','coverage_complete':True} 
  c={'id':x['case']+'/'+x['witness'],'ordering':x['witness'].split('/')[-2] if '/' in x['witness'] else x['witness'].split('_')[0], 'source_ordering':x['witness'].split('/')[-2] if '/' in x['witness'] else x['witness'].split('_')[0], 'scalar_sha256':x['scalar_sha256'],'yukawa_sha256':x['yukawa_sha256'],'join_verified':x['complete_join_verified'],'source_files':audit['source_hashes'],'source_scalar_sha256':x['scalar_sha256'],'source_yukawa_sha256':x['yukawa_sha256'],'constraints':statuses,'join_evidence':x['join_evidence']}
  c['global_status'],c['global_acceptance']=classify(c);rows.append(c)
 (HERE/'JOINED_CARD_MATRIX.json').write_text(json.dumps({'status':'DOCUMENTARY_JOINS_PHYSICS_INCOMPLETE','rows':rows},indent=2)+'\n')
 with (HERE/'JOINED_CARD_MATRIX.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['id','ordering','scalar_sha256','join_verified','global_status','global_acceptance']);w.writeheader();w.writerows({k:r[k] for k in w.fieldnames} for r in rows)
 print('Candidate rows:',len(rows),'validated joins:',sum(r['join_verified'] for r in rows),'provisional UNKNOWN:',sum(r['global_status']=='UNKNOWN' for r in rows))
if __name__=='__main__':main()
