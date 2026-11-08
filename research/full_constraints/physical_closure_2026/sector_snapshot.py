#!/usr/bin/env python3
"""Read-only extraction of saved sector evidence; not full physics validation."""
import json,math
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent

def c(z):return complex(z['real'],z['imag'])
def main():
 audit=json.loads((O/'JOIN_AUDIT_IN_PROGRESS.json').read_text()); d=json.loads(Path('/tmp/zee-d14c-dataset.json').read_text());coverage=json.loads((R/'research/full_constraints/higgs/COVERAGE.json').read_text());controls=json.loads((O/'INDEPENDENT_CONTROLS.json').read_text());lfv={r['id']:r for r in controls['lfv']};rows=[]
 for x in audit['rows']:
  if x['source']=='D14 dataset':
   ident=int(x['case'][4:]);ordering,family=x['witness'].split('_');q=next(r for r in d['rows'] if r['id']==ident and r['neutrino']['ordering']==ordering and r['neutrino']['family']==int(family)); y=q['lfv']['channels']['mu_to_e_gamma'];norm=math.hypot(abs(c(y['C_L'])),abs(c(y['C_R']))); status=q['gates']['vacuum']['assessment']; scalar_gates={k:q['gates'][k]['assessment'] for k in ('bfb','unitarity','ewpo')}; vac={'source_assessment':status,'source_certificate':q['gates']['vacuum'].get('certificate',{}).get('ansatz'),'scope':'exact pinned tree potential; inherited evidence, not independently rechecked'}; lr={'retained_CL_abs':abs(c(y['C_L'])),'retained_CR_abs':abs(c(y['C_R'])),'retained_norm':norm,'retained_BR':y['partial_BR'],'missing_bound':None,'physical_status':'UNKNOWN'}; b={'diagnostic_BR_linear':q['flavor']['BR_linear_2026'],'theory_sigma':None,'exclusion':None}; neu={'target':q['neutrino']['target_label'],'closure_relative':q['neutrino']['relative_residual'],'qualification':'saved target closure; not a global oscillation likelihood'}
  else:
   scalar_gates={'bfb':'UNKNOWN','unitarity':'UNKNOWN','ewpo':'UNKNOWN'};a=lfv[x['witness']];lr={'retained_CL_abs':a['retained_CL_abs'],'retained_CR_abs':a['retained_CR_abs'],'retained_norm':a['retained_norm'],'retained_BR':a['BR_retained'],'missing_bound':None,'physical_status':'UNKNOWN'};vac={'source_assessment':'PASS','source_certificate':'D10 sufficient certificate; Candidate A independent exact control','scope':'exact pinned tree potential only'};b={'nlo_HEPfit_BR':4.17955384241e-4 if x['case']=='D7' else 3.83711422745e-4,'theory_sigma':None,'exclusion':None};neu={'qualification':'saved target closure, not modern global oscillation likelihood'}
  lr['sufficient_missing_norm_budget']=max(0.,1.3677858240837514e-12-lr['retained_norm']);lr['budget_note']='conditional sufficient norm only; never estimate of missing contribution'
  rows.append({'case':x['case'],'witness':x['witness'],'scalar_sha256':x['scalar_sha256'],'LFV':lr,'B':b,'HIGGS':{'mass_domain_inventory':coverage['summary'][x['case']],'physical_status':'UNKNOWN','total_width':None,'qualification':'inventory overcounts potentially applicable analyses; missing != zero'},'VACUUM':vac,'SCALAR_GATES':scalar_gates,'NEUTRINOS':neu,'join_verified':x['complete_join_verified'],'global_acceptance':None})
 (O/'SECTOR_SNAPSHOT_IN_PROGRESS.json').write_text(json.dumps({'rows':rows,'status':'PARTIAL_NOT_PHYSICAL_ACCEPTANCE'},indent=2)+'\n');print('saved sector snapshots',len(rows))
if __name__=='__main__':main()
