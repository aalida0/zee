"""Independent GWW partner calculation; still no complete W class."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import numpy as np
import sympy as s
from sympy.parsing.mathematica import parse_mathematica
from .reproduce_w_outer import PINS,HERE
from .external_2hdm import pack,sha
from .w_vacuum import (gww_numerator,gww_mass_difference,ibp_input,master_combination,
                       pole_identity,W)


def main():
    fc=Path(os.environ['D16_FEYNCALC_ROOT'])
    if any(sha(fc/k)!=v for k,v in PINS.items()):
        raise ValueError('Unpinned algebra tools')
    out=Path(tempfile.mkdtemp(prefix='gww_outer_',dir=HERE/'local'))
    env=dict(os.environ,D16_OUTPUT_DIR=str(out))
    def run(name,output):
        with (out/(name+'.log')).open('w') as log:
            subprocess.run(['math','-script',str(HERE/(name+'.m'))],env=env,
                           stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
        if not (out/output).is_file():raise RuntimeError('No result: '+name)
    run('gww_dimensional_projection','gww_projection.json')
    proj=json.loads((out/'gww_projection.json').read_text())
    expr=parse_mathematica(proj['dipole_numerator']).subs(s.Symbol('mw')**2,W)
    if s.cancel(expr-gww_numerator())!=0:raise ArithmeticError('GWW projection mismatch')
    ibp_input(out/'w_ibp_input.m',gww_numerator())
    run('w_master_reduction','w_ibp_coefficients.json')
    co=out/'w_ibp_coefficients.json'
    if pole_identity(co)!=(0,s.Rational(1,4)):
        raise ArithmeticError('Unexpected GWW subdivergence')
    reference=master_combination(2.,co)
    rows=[]
    for ms in (125.,310.):
        h=(ms/80.379)**2
        reduced=master_combination(h,co);value,error=gww_mass_difference(h)
        difference=abs(reduced['laurent'][2]-reference['laurent'][2]-value)
        if difference>max(2e-9,8*(error+reduced['error'][2]+reference['error'][2])):
            raise ArithmeticError('GWW two-loop integrals disagree')
        rows.append(dict(ms=ms,finite_mass_difference=dict(value=value,error=error),ibp=reduced,discrepancy=difference))
    result=dict(status='REGULATED_GWW_PARENT_TOPOLOGY_ONLY',projection=proj,
        ibp=json.loads(co.read_text()),exact_UV_poles=['0','1/4'],reference_h=2.,reference=reference,witnesses=rows,
        native_normalization='native numerator = +MW² gamma_mu slash(p-l) slash(l+r) PL; half the WWW prefactor',
        full_C_LR=None,full_BR=None,coherent_inclusion=False,
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),tool_sources=PINS,
        files={str(f.relative_to(HERE)):sha(f) for f in sorted(out.iterdir())},
        code_sha256={p.name:sha(p) for p in (HERE/'w_vacuum.py',HERE/'gww_dimensional_projection.m',HERE/'w_master_reduction.m',Path(__file__))})
    (HERE/'gww_outer_evidence.json').write_text(json.dumps(pack(result),indent=2,sort_keys=True)+'\n')
    print(result['status'],'nonzero 1/(4 eps) subdivergence; independent finite mass differences')


if __name__=='__main__':
    main()
