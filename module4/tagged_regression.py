"""Run unchanged Module3 tests in an ephemeral clone of its annotated tag.

No existing checkout or branch is switched or modified. Only the generated
clone has the historical branch name required by the unchanged branch guard.
"""
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from .native import ROOT, LOCAL

TAG='zee-lfv-module3-components-v1'
COMMIT='48735439f151fb43f2c6d50661abe66f3d440293'


def run():
    LOCAL.mkdir(parents=True,exist_ok=True)
    logpath=LOCAL/'module3_tagged_regression.log'
    with tempfile.TemporaryDirectory(prefix='module3_tag_',dir=LOCAL) as folder:
        checkout=Path(folder)/'checkout'
        with logpath.open('w') as log:
            subprocess.run(['git','clone','--quiet','--shared','--no-checkout',str(ROOT),str(checkout)],check=True,stdout=log,stderr=log)
            subprocess.run(['git','checkout','--quiet','-b','feature/zee-lfv-module3',TAG],cwd=checkout,check=True,stdout=log,stderr=log)
            def git(*args):
                return subprocess.check_output(['git',*args],cwd=checkout,text=True).strip()
            if git('rev-parse','HEAD')!=COMMIT or git('rev-parse',TAG+'^{}')!=COMMIT:
                raise ValueError('Historical tag context mismatch')
            branch=git('branch','--show-current')
            command=[sys.executable,'-m','unittest','discover','-s','tests','-p','test_module3_*.py','-v']
            process=subprocess.run(command,cwd=checkout,stdout=log,stderr=log,timeout=600)
            clean=not git('status','--porcelain','--untracked-files=no')
        content=logpath.read_text()
        count=re.search(r'Ran (\d+) tests?',content)
        failures=re.search(r'failures=(\d+)',content)
        errors=re.search(r'errors=(\d+)',content)
        skipped=re.search(r'skipped=(\d+)',content)
        report={'status':'PASS' if process.returncode==0 and count and clean else 'FAIL',
            'commit':COMMIT,'tag':TAG,'branch':branch,'tests':int(count[1]) if count else 0,
            'failures':int(failures[1]) if failures else 0,'errors':int(errors[1]) if errors else 0,
            'skipped':int(skipped[1]) if skipped else 0,'returncode':process.returncode,
            'tracked_files_unchanged':clean,'command':'python -m unittest discover -s tests -p test_module3_*.py -v',
            'context':'ephemeral isolated clone of exact annotated-tag commit; existing checkouts untouched',
            'log':str(logpath.relative_to(ROOT))}
    (LOCAL/'module3_tagged_regression.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    result=run();print(json.dumps(result));sys.exit(0 if result['status']=='PASS' else 1)
