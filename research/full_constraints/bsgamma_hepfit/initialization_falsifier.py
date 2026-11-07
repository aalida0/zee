"""Execute the original-constructor witness; no result is a physics prediction."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
from provenance import sha

HERE=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--scratch',type=Path,required=True)
    p.add_argument('--root-prefix',type=Path,required=True)
    a=p.parse_args();root=a.scratch.resolve()
    with tarfile.open(root/'source.tar.gz') as t:
        data=t.extractfile('HEPfit-322bd73a2dadd94ce94a6d71cb79d616e569120a/THDM/src/THDMMatching.cpp').read()
    assert hashlib.sha256(data).hexdigest()=='29a27053026acd083c70cd679542651b0af093b0f1864471fc438dd030f16d21'
    src=root/'original_THDMMatching.cpp';src.write_bytes(data)
    cmd=json.loads((HERE/'receipts/driver-build-fixed.log').read_text().splitlines()[0])
    cmd.insert(cmd.index('-Wl,--start-group'),str(src));cmd[-1]=str(root/'driver_original_initialization')
    proc=subprocess.run(cmd,capture_output=True,text=True,check=True)
    (HERE/'receipts/initialization-falsifier-build.log').write_text(json.dumps(cmd)+'\n'+proc.stdout+proc.stderr)
    inp=HERE/'execution/d7_NO_neutral_near_heavy_07_central.txt'
    env=dict(os.environ,LD_LIBRARY_PATH=f'{root}/compat/usr/lib/x86_64-linux-gnu:{a.root_prefix.resolve()}/lib',
             HEPFITTABS=str(root/'HEPfit-322bd73a2dadd94ce94a6d71cb79d616e569120a'))
    argv=[cmd[-1],'bridge',str(inp)]
    proc=subprocess.run(argv,env=env,capture_output=True,text=True,check=True)
    log=HERE/'receipts/initialization-falsifier.log';log.write_text(proc.stdout+proc.stderr)
    receipt={'scope':'Unpatched nonzero-storage initialization falsifier ONLY; not an accepted rate',
      'argv':argv,'driver_sha256':sha(HERE/'driver.cpp'),'original_matching_sha256':sha(src),
      'binary_sha256':sha(cmd[-1]),'stdout_sha256':sha(log),'returncode':proc.returncode}
    (HERE/'receipts/initialization-falsifier.json').write_text(json.dumps(receipt,indent=2)+'\n')

if __name__=='__main__': main()
