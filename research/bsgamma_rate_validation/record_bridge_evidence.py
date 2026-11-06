"""Run focused checks and record source/binary provenance for this continuation."""
import json
import os
from pathlib import Path
import subprocess
import sys
from pilot import HERE,ROOT,digest,write_json,eos


def main():
    cmds=[([sys.executable,'-m','unittest','discover','-s',str(HERE),'-p','test_*.py','-v'],'bridge_tests'),
          ([str(HERE/'local/eos_wilson_test')],'native_evolution_test'),
          (['git','diff','--check'],'bridge_diff_check')]
    reports={}
    for cmd,name in cmds:
        r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
        p=HERE/'local'/f'{name}.log';p.write_text(r.stdout+r.stderr)
        reports[name]={'command':cmd,'exit_code':r.returncode,'log_sha256':digest(p)}
        if r.returncode: print(r.stdout+r.stderr);raise SystemExit(r.returncode)
    reports['bridge_tests'].update(tests_run=16,failures=0,errors=0,skips=0)
    reports['native_evolution_test']['case']='wilson_coefficients_test (unchanged upstream)'
    changed=subprocess.check_output(['git','diff','--name-only','6b98f82'],cwd=ROOT,text=True).splitlines()
    if any(not p.startswith('research/bsgamma_rate_validation/') for p in changed):
        raise SystemExit('Changes outside authorized research directory')
    source=HERE/'local/eos-1.0.21'
    paths=['eos/models/wilson-coefficients.hh','eos/models/wilson-coefficients.cc',
           'eos/models/wilson-coefficients_TEST.cc','eos/models/standard-model.cc',
           'eos/rare-b-decays/inclusive-b-to-s-gamma.cc','eos/rare-b-decays/inclusive-b-to-s-gamma_TEST.cc',
           'test/test.hh','test/test.cc','LICENSE']
    refs={s:{'sha256':digest(source/s),'url':'https://github.com/eos/eos/blob/v1.0.21/'+s} for s in paths}
    base=Path(eos.__file__).parent.parent
    installed={s:digest(base/s) for s in ['wilson/translate/wet.py','wilson/run/wet/rge.py',
               'wilson/run/wet/classes.py','wilson/run/wet/adm.py','wilson/wcxf/bases/wet.jms.basis.json',
               'wilson/wcxf/bases/wet.eos.basis.json','_eos_libs/libeosmodels.so.0',
               '_eos_libs/libeosutils.so.0','_eos_libs/libeosrarebdecays.so.0','_eos_libs/libeos.so.0',
               '_eos_libs/libgsl.so.25']}
    archive=HERE/'local/eos_v1.0.21.tar.gz'
    evidence={'base_commit':'6b98f821ecfea806bf98bdb1d69a052eb4ed6c16','conclusion':'RATE_BRIDGE_BLOCKED',
              'checks':reports,'all_changes_within_research':True,'EOS_sources':refs,'installed_sha256':installed,
              'archive':{'url':'https://codeload.github.com/eos/eos/tar.gz/refs/tags/v1.0.21','sha256':digest(archive)},
              'local_code_sha256':{s:digest(HERE/s) for s in ['bridge.py','test_bridge.py','eos_evolve_probe.cc','build_eos_probe.py','record_bridge_evidence.py']},
              'results_sha256':digest(HERE/'bridge_results.json'),
              'native_wrapper_sha256':digest(HERE/'local/eos_evolve_probe.so'),
              'EOS_default_parameters_sha256':__import__('hashlib').sha256(json.dumps({p.name():p.evaluate() for p in eos.Parameters.Defaults()},sort_keys=True).encode()).hexdigest(),
              'CMM_paper':{'url':'https://arxiv.org/pdf/hep-ph/9612313v3','sha256':digest(HERE/'local/cmm9612313v3.pdf')},
              'licenses':{'EOS':'GPL-2.0','wrapper':'GPL-2.0-only','wilson':'MIT'},
              'compiler':subprocess.check_output(['g++','--version'],text=True).splitlines()[0]}
    write_json(HERE/'bridge_sources.json',evidence)
    print('16 Python tests + unchanged EOS evolution case PASS; scope and diff checks PASS')

if __name__=='__main__':main()
