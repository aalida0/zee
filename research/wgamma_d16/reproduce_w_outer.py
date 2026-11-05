"""Run the new regulated parent calculation, preserving all historical evidence.

D16_FEYNCALC_ROOT=/path/to/FeynCalc python -m research.wgamma_d16.reproduce_w_outer
"""
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile
import time
import warnings
import numpy as np
import scipy
from scipy.integrate import IntegrationWarning
from sympy.parsing.mathematica import parse_mathematica
import sympy as s
from .external_2hdm import pack,sha
from .w_vacuum import (dipole_numerator,ibp_input,master_combination,direct,
                       pole_identity,topology_pair,D,X,Y,Z,W)

HERE=Path(__file__).resolve().parent
PINS={'FeynCalc.m':'4238350af2ff91a6687ea937446b9e6077318914593afe963d4d10026dfc5165',
      'AddOns/TARCER/TARCERSource.m':'1a47d7ad0f522f7df85122cdc4650bf7f5949e6669c1e1bd69e6dcc221d7ff2a'}


def main():
    start=time.perf_counter()
    fc=Path(os.environ['D16_FEYNCALC_ROOT']).resolve()
    for name,pin in PINS.items():
        if sha(fc/name)!=pin:
            raise ValueError('Unexpected FeynCalc/TARCER source: '+name)
    out=Path(tempfile.mkdtemp(prefix='w_outer_',dir=HERE/'local'))
    env=dict(os.environ,D16_OUTPUT_DIR=str(out))
    def run(script,expected):
        with (out/(script+'.log')).open('w') as log:
            subprocess.run(['math','-script',str(HERE/(script+'.m'))],env=env,
                           stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        if not (out/expected).is_file():
            raise RuntimeError('Wolfram aborted without result: '+script)
    run('w_dimensional_projection','w_projection.json')
    projection=json.loads((out/'w_projection.json').read_text())
    native=parse_mathematica(projection['dipole_numerator']).subs(s.Symbol('mw')**2,W)
    if s.cancel(native-dipole_numerator())!=0:
        raise ArithmeticError('Independent open-Dirac projection disagrees')
    terms=ibp_input(out/'w_ibp_input.m')
    run('w_master_reduction','w_ibp_coefficients.json')
    co=out/'w_ibp_coefficients.json'
    poles=pole_identity(co)
    if poles!=(0,0):
        raise ArithmeticError('Exact UV cancellation failed: '+str(poles))
    witnesses=[]
    with warnings.catch_warnings():
        warnings.simplefilter('error',IntegrationWarning)
        for ms,left,right,kappa in ((125.,.03+.02j,-.01+.04j,.7),
                                   (310.,-.02+.013j,.017-.031j,-.4)):
            h=(ms/80.379)**2
            ibp=master_combination(h,co)
            value,error=direct(h)
            discrepancy=abs(ibp['laurent'][2]-value)
            if discrepancy>max(2e-9,8*(ibp['error'][2]+error)):
                raise ArithmeticError('Independent two-loop integrations disagree')
            witnesses.append(dict(ms=ms,h=h,ibp=ibp,direct=dict(value=value,error=error),
                discrepancy=discrepancy,
                topology=topology_pair(80.379,ms,246.21965,kappa,.1056583755,left,right)))
    exact4=s.factor(dipole_numerator().subs(D,4)-
                    (X/3+3*Z-4*Z**2/(3*Y)+W*Z/(X-W)))
    if exact4!=0:
        raise ArithmeticError('Four-dimensional finite numerator limit failed')
    result=dict(status='REGULATED_WWW_PARENT_TOPOLOGY_ONLY',acceptance=False,
        full_C_LR=None,full_BR=None,coherent_inclusion=False,
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        tool_sources=PINS,projection=projection,partial_fraction_terms=terms,
        ibp=json.loads(co.read_text()),exact_UV_poles=list(map(str,poles)),
        finite_d4_residual=str(exact4),witnesses=witnesses,
        environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        files={str(p.relative_to(HERE)):sha(p) for p in sorted(out.iterdir()) if p.is_file()},
        code_sha256={p.name:sha(p) for p in (HERE/'w_vacuum.py',HERE/'reproduce_w_outer.py',
            HERE/'w_dimensional_projection.m',HERE/'w_master_reduction.m',HERE/'parent_integrals.py')},
        elapsed_seconds=time.perf_counter()-start)
    (HERE/'w_outer_evidence.json').write_text(json.dumps(pack(result),indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(result['status'],len(witnesses),'independent master comparisons; exact poles',poles)


if __name__=='__main__':
    main()
