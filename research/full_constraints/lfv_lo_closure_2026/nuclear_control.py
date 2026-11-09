"""Reproduce comparison with pinned source implementations; writes only here."""
import hashlib, json, tempfile
from pathlib import Path
from research.full_constraints.lfv.source_to_code import nuclear_driver
from adapter import al_kernel, HERE, ROOT
lock=json.loads((ROOT/'research/full_constraints/lfv/SOURCE_TO_CODE_SOURCES.json').read_text())
items={x['id']:x for x in lock['artifacts']}
paths={}
for name in ('fs_conversion','fk_conversion'):
 p=Path(items[name]['path_hint']); assert hashlib.sha256(p.read_bytes()).hexdigest()==items[name]['sha256']; paths[name]=p
with tempfile.TemporaryDirectory(dir=HERE) as d:
 x=nuclear_driver(paths['fs_conversion'],paths['fk_conversion'],Path(d))
 rows=[r for r in x['flexiblesusy_nucleon_controls'] if r['target']=='Al']
 inputs=[(5.1,4.3,0,0),(0,0,2,1),(1,-1,0,0),(0,0,1,-1),(1,-1,1,-1)]
 for r,(sp,sn,vp,vn) in zip(rows,inputs):
  left,_,rate=al_kernel(0,0,vp,vn,0,0,0,0,sp,sn)
  r['new_adapter_left']=left.real; r['new_adapter_rate']=rate; r['new_adapter_relative_residual']=abs(left/r['left_current_GeV_5o2']-1)
  assert r['new_adapter_relative_residual']<1e-14
 (HERE/'NUCLEAR_SOURCE_CONTROLS.json').write_text(json.dumps({'controls':rows,'caveat':x['caveat'],'flavorkit_isovector':x['flavorkit_pure_isovector_and_interference']},indent=2)+'\n')
 print('Al source controls:',len(rows),'max residual',max(r['new_adapter_relative_residual'] for r in rows))
