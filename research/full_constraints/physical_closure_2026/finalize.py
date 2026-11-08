#!/usr/bin/env python3
"""Run focused controls and emit selected-card result, never infer physics passes."""
import hashlib,json,os,re,subprocess,sys
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 required=['INPUT_PROVENANCE.json','COVERAGE_BEFORE.json','JOINED_CARD_MATRIX.csv','JOINED_CARD_MATRIX.json','LFV_COMPLETENESS.json','BSGAMMA_COMPLETENESS.json','HIGGS_COMPLETENESS.json','EVIDENCE_DIFF.md','SECTOR_ATTEMPTS.md','REPRODUCE.md','PUBLIC_SOURCE_DOWNLOADS.json','INDEPENDENT_CONTROLS.json','WORK_CHECKPOINT.md','audit_join.py','controls.py','gate.py']
 for n in required:
  if not (O/n).is_file():raise RuntimeError('missing artifact: '+n)
 report=R/'research/full_constraints/PHYSICAL_CONSTRAINT_CLOSURE_REPORT_2026-11-08.md'
 if not report.is_file():raise RuntimeError('missing report')
 env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
 commands=[([sys.executable,str(O/'test_gate.py'),'-v'],14,None),([sys.executable,str(O/'test_source_guard.py'),'-v'],1,None),([sys.executable,'-m','unittest','research.full_constraints.lfv.test_source_to_code','-v'],4,None),([sys.executable,'-m','unittest','research.full_constraints.bsgamma_hepfit.test_uncertainty','-v'],5,'research/full_constraints/bsgamma_hepfit'),([sys.executable,'-m','unittest','research.full_constraints.higgs.test_zgamma','research.full_constraints.higgs.test_zgamma_source_audit','-v'],20,None),([sys.executable,'-m','unittest','discover','-s','tests','-p','test_module1_d10_global.py','-v'],9,None),([sys.executable,str(O/'test_outputs.py'),'-v'],4,None)]
 logs=[];tests=[]
 for cmd,n,pythonpath in commands:
  e=env.copy()
  if pythonpath:e['PYTHONPATH']=pythonpath
  p=subprocess.run(cmd,cwd=R,env=e,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
  logs.append('$ '+' '.join(cmd)+'\n'+p.stdout)
  found=re.search(r'Ran (\d+) tests? in',p.stdout)
  tests.append({'command':cmd,'passed':int(found.group(1)) if found and p.returncode==0 else 0,'expected':n,'returncode':p.returncode})
  if p.returncode or not found or int(found.group(1))!=n:
   (O/'FINAL_TEST_LOG.txt').write_text('\n'.join(logs));raise RuntimeError('test failed: '+str(cmd))
 (O/'FINAL_TEST_LOG.txt').write_text('\n'.join(logs))
 matrix=read(O/'JOINED_CARD_MATRIX.json')['rows'];joined=[r for r in matrix if r['join_verified']];unjoined=[r for r in matrix if not r['join_verified']]
 if len(matrix)!=68 or len(joined)!=66 or len(unjoined)!=2:raise RuntimeError('unexpected join counts')
 counts={key:sum(r['global_status']==key for r in joined) for key in ('GLOBAL_PASS','PHYSICAL_FAIL','UNKNOWN')}
 if counts!={'GLOBAL_PASS':0,'PHYSICAL_FAIL':0,'UNKNOWN':66}:raise RuntimeError('unexpected physical gate outcome')
 if any(r['global_acceptance'] is not None for r in matrix):raise RuntimeError('unexpected non-null acceptance')
 provenance=read(O/'INPUT_PROVENANCE.json')
 for name,digest in provenance['source_hashes'].items():
  if sha(Path(name))!=digest:raise RuntimeError('source changed: '+name)
 result={'status':'NO_VALIDATED_BENCHMARKS_YET','status_scope':'66 selected documentary-joined cards; two additional IO candidates unjoined and unknown; no statement about all model parameter space','join_count':len(joined),'unjoined_candidate_count':len(unjoined),'pass_count':counts['GLOBAL_PASS'],'fail_count':counts['PHYSICAL_FAIL'],'unknown_count':counts['UNKNOWN'],'raw_production_receipts_verified':0,'global_acceptance':None,'sector_gates':{'LFV':'UNKNOWN','B_to_Xs_gamma':'UNKNOWN; THEORY_SIGMA_UNKNOWN; no physical 95% exclusion','HIGGS':'UNKNOWN; incomplete widths and applicable signals','vacuum':'positive sufficient tree certificates for exact saved potentials only','neutrinos':'partial target closure; modern global likelihood not established','charged_collider':'UNKNOWN'},'source_hashes':provenance['source_hashes'],'tests':{'focused_passed':sum(x['passed'] for x in tests),'focused_failed':0,'commands':tests,'log':'FINAL_TEST_LOG.txt','historical_full_suite':{'total':474,'failures':3,'errors':16,'skips':20,'new_run':False}},'remaining_blockers':['complete gauge-invariant mixed-F and charged-current LFV amplitudes or justified bounds and complete mu3e/conversion operators','Wilson-dependent B theory and experimental covariance, omitted-operator materiality and one-state confidence calibration','complete Higgs widths, production, applicable search inputs and uncertainty/acceptance qualification','source qualification of raw production receipts and two IO production associations','full neutrino, electroweak, collider, cosmology and other applicable constraints'], 'final_artifacts_ready':True,'final_physics_complete':False,'notes':'Final report and conservative gate are ready; physical constraints remain incomplete. No commit or push.'}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ('status','join_count','unjoined_candidate_count','pass_count','fail_count','unknown_count','final_artifacts_ready','final_physics_complete')},indent=2))
if __name__=='__main__':main()
