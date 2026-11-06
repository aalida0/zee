"""Compile a thin wrapper and an unchanged upstream regression; never rebuild EOS."""
import json
import os
from pathlib import Path
import subprocess
from pilot import HERE, digest, write_json

local=HERE/'local'
src=local/'eos-1.0.21'
libs=local/'venv/lib/python3.10/site-packages/_eos_libs'
if not (src/'eos/models/wilson-coefficients.hh').exists():
    raise SystemExit('Download and unpack the pinned archive as documented in BRIDGE.md')
if digest(local/'eos_v1.0.21.tar.gz') != '4440b059c5069b0fe4b3057e80b98eab2c083a35da26392341635711b22482e1':
    raise SystemExit('EOS archive checksum mismatch')
if digest(src/'eos/models/wilson-coefficients.hh') != 'e1fffd044535df92a9246a57daf1ed5ee7782731a99e20f1854f230b8afc1698':
    raise SystemExit('EOS evolution header checksum mismatch')
config=local/'build-config';config.mkdir(exist_ok=True)
(config/'config.h').write_text('// No optional test-generation macros enabled.\n')
base=['g++','-std=c++20','-O2','-I',str(src),'-I',str(config)]
link=['-L',str(libs),'-Wl,-rpath,$ORIGIN/venv/lib/python3.10/site-packages/_eos_libs',
      '-Wl,--no-as-needed','-l:libeos.so.0','-l:libeosmodels.so.0','-l:libeosutils.so.0',
      '-l:libeosrarebdecays.so.0']
cmds=[base+['-shared','-fPIC',str(HERE/'eos_evolve_probe.cc')]+link+['-o',str(local/'eos_evolve_probe.so')],
      base+[str(src/'eos/models/wilson-coefficients_TEST.cc'),str(src/'test/test.cc')]+link+
      ['-l:libgsl.so.25','-o',str(local/'eos_wilson_test')]]
logs=[]
for c in cmds:
    r=subprocess.run(c,text=True,capture_output=True)
    logs.append({'command':c,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    if r.returncode: print(r.stderr);raise SystemExit(r.returncode)
env=dict(os.environ,EOS_HOME=str(libs.parent/'_eos_data'))
r=subprocess.run([str(local/'eos_wilson_test')],env=env,text=True,capture_output=True)
logs.append({'command':['local/eos_wilson_test'],'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
write_json(local/'native_build.json',logs)
print(r.stdout.strip(), 'exit=',r.returncode)
raise SystemExit(r.returncode)
