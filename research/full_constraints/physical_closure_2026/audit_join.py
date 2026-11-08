#!/usr/bin/env python3
"""Read-only source join audit. This is not a physical acceptance calculation."""
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[3]
COVER=ROOT/'research/full_constraints/higgs/COVERAGE.json'
DATA=pathlib.Path('/tmp/zee-d14c-dataset.json')
MAP=ROOT/'module14/conditional_scan/production_map_13_14.json'
D12=ROOT/'validation/module12/d12_benchmarks.json'
OUT=pathlib.Path(__file__).resolve().parent

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def require(ok,msg):
 if not ok: raise ValueError(msg)
def main():
 cov=json.loads(COVER.read_text()); dataset=json.loads(DATA.read_text()); prod=json.loads(MAP.read_text()); d12=json.loads(D12.read_text())
 require(sha(DATA)==cov['input_sha256'][str(DATA)],'dataset hash mismatch')
 require(sha(MAP)==cov['input_sha256']['module14/conditional_scan/production_map_13_14.json'],'production map hash mismatch')
 require(prod['dataset_sha256']==sha(DATA),'production map points to another dataset')
 out=[]
 for case in cov['cases']:
  for w in case['witnesses']:
   if case['id'].startswith('D14_'):
    ident=case['id'].split('_')[1]; ordering,family=w['id'].split('_')
    candidates=[r for r in dataset['rows'] if str(r['id'])==ident and r['neutrino'].get('ordering')==ordering and r['widths']['family']==int(family)]
    require(len(candidates)==1,'nonunique dataset identity '+case['id']+'/'+w['id'])
    row=candidates[0]
    require(row['scalar_sha256']==case['scalar_sha256'],'scalar hash mismatch')
    require(row['widths']['module2_input_sha256']==w['module2_input_sha256']==row['neutrino']['input_sha256'],'module2 hash mismatch')
    require(row['widths']['yukawa_sha256']==w['yukawa_sha256'],'Yukawa digest mismatch')
    families=[f for f in prod['families'] if str(f['id'])==ident and f['energy_TeV']==13 and f['module2_input_sha256']==w['module2_input_sha256']]
    require(len(families)==1,'missing production family')
    f=families[0]
    require(f['ordering']==ordering and f['family']==int(family) and f['scalar_sha256']==row['scalar_sha256'] and f['yukawa_sha256']==w['yukawa_sha256'],'production family mismatch')
    rates=[r for r in prod['rates'] if str(r['id'])==ident and r['energy_TeV']==13]
    require(len(rates)==1 and rates[0]['receipt_sha256']==f['receipt_sha256'] and rates[0]['sigma_pb']==f['sigma_pb'],'production rate mismatch')
    source='D14 dataset'; evidence='scalar/order/family/module2/Yukawa digests and production manifest matched; raw receipt and independently recomputed Yukawa hashes pending'
   else:
    candidates=[f for g in d12['groups'] for f in g['family'] if f['id']==w['id']]
    require(len(candidates)==1,'nonunique D12 witness'); require(candidates[0]['yukawa_sha256']==w['yukawa_sha256'],'D12 Yukawa hash mismatch')
    source='D12'; evidence='witness and four Yukawa hashes matched; scalar and production receipt binding pending'
   out.append({'case':case['id'],'witness':w['id'],'scalar_sha256':case['scalar_sha256'],'yukawa_sha256':w['yukawa_sha256'],'physical':case['physical'],'source':source,'join_evidence':evidence,'complete_join_verified':False,'global_acceptance':None,'status':'UNKNOWN'})
 result={'state':'INCOMPLETE_JOIN_AUDIT','source_hashes':{str(p):sha(p) for p in (COVER,DATA,MAP,D12)},'candidate_count':len(out),'fully_verified_join_count':0,'rows':out}
 (OUT/'JOIN_AUDIT_IN_PROGRESS.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
