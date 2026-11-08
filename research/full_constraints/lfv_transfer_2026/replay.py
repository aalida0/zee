#!/usr/bin/env python3
"""Replay the exact frozen D12 cards; no new amplitude or scan."""
import hashlib,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT))
from module2.interface import canonical_hash,evaluate
from module14.lfv import evaluate_family
OUT=Path(__file__).resolve().parent
D12=ROOT/'validation/module12/d12_benchmarks.json'
EXPECTED='f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(condition,message):
 if not condition: raise ValueError(message)
def card(g,w):
 i=w['module2_input']; check(i['ordering']==g['ordering'],'ordering mismatch'); check(canonical_hash(i['scalar']['record'])==w['scalar_sha256']==g['scalar_sha256'],'scalar mismatch')
 check({k:canonical_hash(v) for k,v in w['yukawas'].items()}==w['yukawa_sha256'],'Yukawa mismatch')
 return {'id':w['id'],'type':w['design'],'ordering':g['ordering'],'scalar_sha256':w['scalar_sha256'],'yukawa_sha256':w['yukawa_sha256'],'witness_sha256':canonical_hash(w),'module2_input_sha256':canonical_hash(i),'module2_output_sha256':w['module2_output_sha256'],'module4_output_sha256':w['module4_output_sha256'],'direct_D_e_mu':{k:w['yukawas']['D'][k][0][1] for k in ('real','imag')},'direct_D_mu_e':{k:w['yukawas']['D'][k][1][0] for k in ('real','imag')},'available_fields':['full scalar record','module2 input','F','D','Ye','Ye2','signed radiative components'],'status':'HASH_VERIFIED'}
def run():
 check(sha(D12)==EXPECTED,'D12 file digest mismatch'); data=json.loads(D12.read_text()); groups=data['groups']; check(len(groups)==4,'expected four')
 provenance={}; replay=[]; ledger=[]
 for key,sel in [('texture_low_joint','low_joint'),('scale_0.001_old','central')]: provenance[key]=[card(g,g['witnesses'][sel]) for g in groups]
 for g in groups:
  w=g['witnesses']['low_joint']; i=w['module2_input']; n=evaluate(i); check(canonical_hash(n)==w['module2_output_sha256'],'Module2 receipt mismatch')
  f=dict(w['yukawas'],Mnu=n['Mnu'],input=i,input_sha256=canonical_hash(i)); out=evaluate_family(f); check(out['module4_output_sha256']==w['module4_output_sha256'],'Module4 receipt mismatch')
  c=out['channels']['mu_to_e_gamma']; s=w['signed_radiative']['mu_to_e_gamma']; z=lambda a:complex(a['real'],a['imag']); norm=math.hypot(abs(z(c['C_L'])),abs(z(c['C_R']))); old=math.hypot(abs(z(s['C_L'])),abs(z(s['C_R']))); residual=abs(norm/old-1); check(residual<=1e-10,'baseline mismatch'); check(all(z(c[k])==z(s[k]) for k in ('C_L','C_R')),'signed baseline mismatch'); check(c['partial_BR']==s['BR_implemented'],'rate mismatch')
  row={'id':w['id'],'scalar_sha256':w['scalar_sha256'],'yukawa_sha256':w['yukawa_sha256'],'module4_output_sha256':out['module4_output_sha256'],'C_L':c['C_L'],'C_R':c['C_R'],'BR_partial':c['partial_BR'],'norm_GeV_minus2':norm,'relative_norm_residual':residual,'sufficient_missing_norm_budget_GeV_minus2':1.367785824084e-12-norm,'budget_note':'conditional sufficient budget; not a bound on omitted physics'}; replay.append(row)
  ledger.append({'id':w['id'],'baseline':{'C_L':c['C_L'],'C_R':c['C_R']},'neutral_Zgamma':None,'hZ':None,'sum_scoped':None,'BR_scoped':None,'interference':None,'missing':'NOT_EVALUATED'})
 inputs=['validation/module12/d12_benchmarks.json','module1/d10_benchmarks.json','module2/interface.py','module3/core.py','module4/amplitudes.py','module4/charged_scalar.py','module4/interface.py','module14/lfv.py','research/full_constraints/lfv/experiments.json','research/full_constraints/lfv/PRACTICAL_SENSITIVITY.json','research/full_constraints/lfv/TEXTURE_COUPLING_AUDIT.json','research/full_constraints/lfv/TEXTURE_MATERIALITY_REPRODUCED.json','research/full_constraints/LFV_VALIDATION.json']
 for name,obj in [('CARD_PROVENANCE.json',{'input_sha256':sha(D12),'datasets':provenance}),('BASELINE_REPLAY.json',{'baseline_replay_pass':True,'cards':replay}),('AMPLITUDE_LEDGER.json',{'cards':ledger,'physical_lfv':'UNKNOWN'}),('INPUT_SHA256.json',{p:sha(ROOT/p) for p in inputs})]: (OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
 print('PASS: 4 texture card input and output hashes, signed complex coefficients, and rates; 4 scale card identities recorded')
if __name__=='__main__': run()
