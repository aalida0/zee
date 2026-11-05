"""Prepare and check NEW mixed sGH potential vertices, not the old inventory."""
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from module4.couplings import rotations
from module4.native import wl
from module1.scalar_constraints import reconstruct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    native = json.loads((HERE/'native_vertices.json').read_text())
    code = ['out=FileNameJoin[{Directory[],"research","wgamma_d16","local"}];',
            'raw=Get[FileNameJoin[{out,"st_vertices_raw.m"}]];', 'checks={};']
    for ip, p in enumerate(native['physical_inputs']):
        zh, _, zp = rotations(p)
        lag, _, _ = reconstruct(p)
        rules = [f'{name}[{a+1},{b+1}]->{wl(value)}'
                 for name, matrix in (('ZH', zh), ('ZP', zp))
                 for a, row in enumerate(matrix) for b, value in enumerate(row)]
        rules += [f'{name}->{wl(value)}' for name, value in dict(lag,
                   v1=p['v']*np.cos(p['beta']), v2=p['v']*np.sin(p['beta'])).items()]
        code.append('rules={'+','.join(rules)+'};')
        for k in (1, 2):
            ms = p['mh1'] if k == 1 else p['mh2']
            for a in (2, 3):
                mh = p['mH1'] if a == 2 else p['mH2']
                overlap = float(zh[k-1]@zp[a-1, :2])
                expected = -1j*(ms*ms-mh*mh)*overlap/p['v']
                for c in (1, 2):
                    key = '{'+f'{k}, {a}, {c}'+'}'
                    code.append(f'actual=N[raw[{json.dumps(key)}][[2,1]]/.rules];')
                    code.append(f'AppendTo[checks,<|"point"->{ip},"key"->{json.dumps(key)},'
                                f'"actual"->{{Re[actual],Im[actual]}},"expected"->{{{wl(expected.real)},{wl(expected.imag)}}},'
                                f'"residual"->Abs[actual-({wl(expected)})]|>];')
    code += ['Export[FileNameJoin[{out,"st_checks.json"}],checks,"RawJSON"];',
             'Print["D16_ST_NEW_VERTEX_RESIDUAL ",Max[Lookup[checks,"residual"]]];',
             'Exit[If[Max[Lookup[checks,"residual"]]<1.*^-8,0,1]];']
    script = HERE/'local/check_st_vertices.m'
    script.write_text('\n'.join(code)+'\n')
    result = subprocess.run(['math', '-script', str(script)], cwd=ROOT, capture_output=True, text=True)
    (HERE/'local/st-checks.log').write_text(result.stdout+result.stderr)
    if result.returncode:
        raise RuntimeError((HERE/'local/st-checks.log').read_text())
    raw = json.loads((HERE/'local/st_sources.json').read_text())
    checks = json.loads((HERE/'local/st_checks.json').read_text())
    raw.update(checks=checks, max_abs_residual=max(c['residual'] for c in checks),
               frozen_source_sha256=native['frozen_source_sha256'],
               input_sha256=hashlib.sha256(json.dumps(native['physical_inputs'], sort_keys=True).encode()).hexdigest(),
               formula='V_sG-H+ = -i*(Ms^2-MH^2)*(ZH_s dot ZP_H,doublet)/v; both charges',
               extraction_sha256=hashlib.sha256((HERE/'extract_st_sources.m').read_bytes()).hexdigest(),
               validation_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE/'st_sources.json').write_text(json.dumps(raw, indent=2, sort_keys=True)+'\n')
    print('New ST potential vertices:', len(checks), 'max residual', raw['max_abs_residual'])


if __name__ == '__main__':
    main()
