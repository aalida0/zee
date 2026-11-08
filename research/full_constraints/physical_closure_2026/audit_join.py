#!/usr/bin/env python3
"""Read-only source join audit. This is not a physical acceptance calculation."""
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[3]
COVER=ROOT/'research/full_constraints/higgs/COVERAGE.json'
DATA=pathlib.Path('/tmp/zee-d14c-dataset.json')
MAP=ROOT/'module14/conditional_scan/production_map_13_14.json'
D12=ROOT/'validation/module12/d12_benchmarks.json'
D10=ROOT/'module1/d10_benchmarks.json'
D13=ROOT/'validation/module13/higgstools_production_inputs.json'
OUT=pathlib.Path(__file__).resolve().parent
PINS={COVER:'0a8aead96843aae22ac3a5038ba8b3888892695253ccea13803bb7e0055d027b',DATA:'2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9',MAP:'95510ec92f95d4598d85e64a1163da949dc0ce529b63ef5e536f0a6a4f2f7aab',D12:'f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8',D10:'d354481895850cdaa6846a0728e1114a5ada6a7c1210260f350b79c1aba65015',D13:'514215b7a67195c963afb73912202265bd930941cd1c41e5486157df7a1981ca'}

def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 return h.hexdigest()
def digest(x):
 return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',', ':'),allow_nan=False).encode()).hexdigest()
def require(ok,msg):
 if not ok: raise ValueError(msg)
def main():
 for path,want in PINS.items():require(sha(path)==want,'source hash mismatch: '+str(path))
 cov=json.loads(COVER.read_text()); dataset=json.loads(DATA.read_text()); prod=json.loads(MAP.read_text()); d12=json.loads(D12.read_text()); d10=json.loads(D10.read_text()); d13=json.loads(D13.read_text())
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
    require(row['widths']['yukawa_sha256']==w['yukawa_sha256']=={k:digest(row['neutrino'][k]) for k in ('F','D','Ye','Ye2')},'Yukawa digest mismatch')
    require(digest(row['input_card'])==row['scalar_sha256'],'scalar card digest mismatch')
    families=[f for f in prod['families'] if str(f['id'])==ident and f['energy_TeV']==13 and f['module2_input_sha256']==w['module2_input_sha256']]
    require(len(families)==1,'missing production family')
    f=families[0]
    require(f['ordering']==ordering and f['family']==int(family) and f['scalar_sha256']==row['scalar_sha256'] and f['yukawa_sha256']==w['yukawa_sha256'],'production family mismatch')
    rates=[r for r in prod['rates'] if str(r['id'])==ident and r['energy_TeV']==13]
    require(len(rates)==1 and rates[0]['receipt_sha256']==f['receipt_sha256'] and rates[0]['sigma_pb']==f['sigma_pb'],'production rate mismatch')
    binding={k:f[k] for k in ('scalar_sha256','module2_input_sha256','yukawa_sha256','mapped_card_sha256','receipt_sha256','energy_TeV')}
    require(digest(binding)==f['binding_sha256'],'production binding digest mismatch')
    require(rates[0]['process']=='pp_tbH2_5FS_gb' and rates[0]['order']=='LO_QCD' and rates[0]['energy_TeV']==13,'production process mismatch')
    source='D14 dataset'; evidence='scalar/order/family/module2/Yukawa digests and production manifest matched; raw production receipt pending'
   else:
    candidates=[f for g in d12['groups'] for f in g['family'] if f['id']==w['id']]
    require(len(candidates)==1,'nonunique D12 witness'); require(candidates[0]['yukawa_sha256']==w['yukawa_sha256'],'D12 Yukawa hash mismatch')
    group=next(g for g in d12['groups'] if g['scalar_sha256']==case['scalar_sha256'] and g['ordering']=='NO')
    actual=group['witnesses']['low_joint']; require(actual['id']==w['id'] and {k:digest(v) for k,v in actual['yukawas'].items()}==w['yukawa_sha256'],'D12 stored Yukawas mismatch')
    record=next(r for r in d10['records'] if r['input']['benchmark_id']==group['scalar']); require(digest(record['input'])==record['input_sha256']==group['scalar_sha256'],'D10 scalar mismatch')
    rates=[r for r in d13['records'] if r['name']==case['id'] and r['energy_TeV']==13]
    require(len(rates)==2 and {r['state'] for r in rates}=={1,2},'D12 production states missing')
    require(all(r['benchmark']['scalar_sha256']==case['scalar_sha256'] and r['benchmark']['D12_yukawa_sha256']==w['yukawa_sha256'] and r['benchmark']['physical']==case['physical'] for r in rates),'D12 production binding mismatch')
    source='D12'; evidence='D10 scalar, D12 Yukawas and D13 production manifest matched; raw receipt qualification pending'
   out.append({'case':case['id'],'witness':w['id'],'scalar_sha256':case['scalar_sha256'],'yukawa_sha256':w['yukawa_sha256'],'physical':case['physical'],'source':source,'join_evidence':evidence,'complete_join_verified':True,'receipt_content_verified':False,'global_acceptance':None,'status':'UNKNOWN'})
 for group in d12['groups']:
  if group['ordering']!='IO':continue
  w=group['witnesses']['low_joint']; record=next(r for r in d10['records'] if r['input']['benchmark_id']==group['scalar'])
  require(digest(record['input'])==record['input_sha256']==group['scalar_sha256']==w['scalar_sha256'],'IO scalar mismatch')
  require({k:digest(v) for k,v in w['yukawas'].items()}==w['yukawa_sha256'],'IO Yukawa mismatch')
  name='D7' if group['scalar'].startswith('d7_') else 'F13'
  out.append({'case':name,'witness':w['id'],'scalar_sha256':group['scalar_sha256'],'yukawa_sha256':w['yukawa_sha256'],'physical':record['input']['physical'],'source':'D12','join_evidence':'D10 scalar and D12 IO Yukawa digests matched; production manifest binds NO witness, IO production association unverified','complete_join_verified':False,'global_acceptance':None,'status':'UNKNOWN'})
 result={'state':'INCOMPLETE_JOIN_AUDIT','source_hashes':{str(p):sha(p) for p in (COVER,DATA,MAP,D12,D10,D13)},'candidate_count':len(out),'documentary_join_count':sum(x['complete_join_verified'] for x in out),'raw_production_receipts_verified':0,'rows':out}
 (OUT/'JOIN_AUDIT_IN_PROGRESS.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
