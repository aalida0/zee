"""Capture actual scratch build provenance, without distributing binaries."""
import argparse
import ctypes
import ctypes.util
import json
import os
from pathlib import Path
import platform
import subprocess
from provenance import sha, verify_source

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--scratch',type=Path,required=True)
    ap.add_argument('--root-prefix',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args(); root=a.scratch.resolve(); rp=a.root_prefix.resolve()
    source=root/'HEPfit-322bd73a2dadd94ce94a6d71cb79d616e569120a'
    count=verify_source(source)
    env=dict(os.environ,LD_LIBRARY_PATH=str(root/'compat/usr/lib/x86_64-linux-gnu')+':'+str(rp/'lib'))
    commands={'compiler':['g++','--version'],'cmake':['cmake','--version'],
        'root':[str(rp/'bin/root-config'),'--version'],
        'gsl_headers':['gsl-config','--version'],'boost':['dpkg-query','-W','libboost-dev'],
        'ldd':['ldd',str(root/'driver')]}
    versions={k:subprocess.check_output(cmd,text=True,env=env,stderr=subprocess.STDOUT).strip() for k,cmd in commands.items()}
    ctypes.CDLL(ctypes.util.find_library('gslcblas'),mode=ctypes.RTLD_GLOBAL)
    gsl=ctypes.CDLL(str(root/'compat/usr/lib/x86_64-linux-gnu/libgsl.so.25'))
    versions['GSL_runtime']=ctypes.c_char_p.in_dll(gsl,'gsl_version').value.decode()
    artifacts=[root/'driver',root/'superiso_probe',root/'superiso_inputs',root/'build/CMakeCache.txt',
        root/'rge-build/CMakeCache.txt',root/'deps/lib/libRGESolver.a',
        root/'compat/usr/lib/x86_64-linux-gnu/libgsl.so.25.1.0',
        root/'compat/usr/lib/x86_64-linux-gnu/libtbb.so.2',rp/'bin/root-config',
        rp/'lib/libMathMore.so',rp/'lib/libMathCore.so']
    artifacts.extend(root/'build'/m/f'lib{m}.a' for m in ['StandardModel','THDM','Flavour','LeptonFlavour','LoopFunctions'])
    r={'platform':platform.platform(),'versions':versions,'verified_source_files':count,
       'artifacts':{str(p):sha(p) for p in artifacts},
       'flags':{str(p.relative_to(root/'build')):p.read_text() for p in (root/'build').glob('*/CMakeFiles/*.dir/flags.make')
                if any(k in str(p) for k in ['StandardModel','THDM','Flavour','LeptonFlavour','LoopFunctions'])},
       'scope':'Scratch build; upstream algorithms unchanged except constructor zero initialization; no third-party binary/source distribution.'}
    a.output.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')

if __name__=='__main__': main()
