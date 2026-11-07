"""Fail closed on source bytes; external dependencies are never vendored."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_source(source):
    lock=json.loads((HERE/'SOURCE_LOCK.json').read_text())
    for name,digest in lock['HEPfit_build_and_rate_files'].items():
        if sha(source/name) != digest:
            raise ValueError('HEPfit source digest mismatch: '+name)
    return len(lock['HEPfit_build_and_rate_files'])


def verify_execution(path):
    """Validate evidence, not physical confidence or a global acceptance."""
    e=json.loads(path.read_text())
    if e['full_rate_status']!='B_FULL_RATE_BLOCKED' or e['physical_bsgamma']!='UNKNOWN':
        raise ValueError('Unqualified physical promotion')
    if e['theory_sigma'] is not None or e['exclusion'] is not None:
        raise ValueError('Uncalibrated uncertainty/exclusion')
    if e['driver_sha256'] != sha(HERE/'driver.cpp') or e['runner_sha256'] != sha(HERE/'execute.py'):
        raise ValueError('Client/runner changed after execution')
    for name,r in e['runs'].items():
        log=path.parent/r['stdout']
        if sha(log)!=r['stdout_sha256'] or sha(path.parent/(name+'.txt'))!=r['input_sha256']:
            raise ValueError('Receipt digest mismatch: '+name)
        v=r['values']
        if v['cut_GeV']!=1.6: raise ValueError('Wrong photon cut')
        for order in range(3):
            for i in range(1,9):
                if f'low_{order}_{i}' not in v: raise ValueError('Incomplete order/operator vector')
        if r['mode']=='bridge':
            a=v['a_s_muw']
            for order in range(3):
                c=[r['input'].get(f'NP{order}_{i}',0.) for i in range(1,9)]
                c[6]-=c[2]/3+4*c[3]/9+20*c[4]/3+80*c[5]/9
                c[7]+=c[2]-c[3]/6+20*c[4]-10*c[5]/3
                for i in range(8):
                    want=(1 if order==0 else a if order==1 else 0)*c[i]
                    if abs(v[f'high_1_{order}_{i+1}']-want)>2e-14:
                        raise ValueError('Wrong operator/order/alpha_s map')
    if max(abs(x) for x in e['implementation_residuals'].values())>2e-13:
        raise ValueError('Implementation identity failed')
    return e


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path)
    p.add_argument('--execution',type=Path)
    a=p.parse_args()
    if a.source: print('Verified source files:',verify_source(a.source))
    if a.execution: print('Verified executed runs:',len(verify_execution(a.execution)['runs']))
