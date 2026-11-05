"""Check newly queried oriented HZ/G0/A/contact vertices at two native spectra."""
import json
from pathlib import Path
import subprocess

import numpy as np
from module1.scalar_constraints import reconstruct
from module4.couplings import rotations, trilinears
from module4.native import wl
from .external_2hdm import sha
from .zee_mixed_hz import charges, goldstone_trilinear

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main():
    native = json.loads((HERE/'native_vertices.json').read_text())
    code = ['out=FileNameJoin[{Directory[],"research","wgamma_d16","local"}];',
        'raw=Get[FileNameJoin[{out,"mixed_hz_raw.m"}]];',
        'expanded=Map[Function[x,x//.HoldPattern[sum[ind_,lo_Integer,hi_Integer,body_]]:>Total[Table[body,{ind,lo,hi}]]],raw];',
        'checks={};',
        'record[key_,structure_,expected_,rules_]:=Module[{actual,res},',
        'actual=N[If[expanded[key]===0,0,Total[Cases[Rest[expanded[key]],{c_,s_}/;s===structure:>c]]]/.rules];',
        'res=If[NumericQ[actual],Abs[actual-expected],1.*^300];',
        'AppendTo[checks,<|"key"->key,"structure"->ToString[structure,InputForm],"actual"->{Re[actual],Im[actual]},"expected"->{Re[expected],Im[expected]},"residual"->res|>]];']
    for p in native['physical_inputs']:
        lag, _, _ = reconstruct(p)
        zh, za, zp = rotations(p)
        T, e, sw, cw = charges(p, 80.379, 91.1876)
        tri = trilinears(p, lag)
        tri['G0'] = np.zeros((3, 3), complex)
        tri['G0'][1:, 1:] = goldstone_trilinear(p, lag)
        rules = [f'{n}[{a+1},{b+1}]->{wl(v)}' for n, mat in
                 (('ZH', zh), ('ZA', za), ('ZP', zp))
                 for a, row in enumerate(mat) for b, v in enumerate(row)]
        rules += [f'{n}->{wl(v)}' for n, v in dict(lag,
            v1=p['v']*np.cos(p['beta']), v2=p['v']*np.sin(p['beta']),
            g2=e/sw, g1=e/cw, ThetaW=np.arcsin(sw)).items()]
        code.append('rules={'+','.join(rules)+'};')
        for a in (2, 3):
            for b in (2, 3):
                for name, field in [('h','hh[{1}]'), ('H','hh[{2}]'),
                                    ('A','Ah[{2}]'), ('G0','Ah[{1}]')]:
                    key = '{'+f'{field}, {a}, {b}'+'}'
                    code.append(f'record[{json.dumps(key)},1,{wl(-1j*tri[name][a-1,b-1])},rules];')
                momentum = f'Mom[conj[Hm[{{{b}}}]],lt3]-Mom[Hm[{{{a}}}],lt3]'
                for field, val in [('VP', -1j*e*(a == b)), ('VZ', -1j*e*T[a-2,b-2])]:
                    key = '{'+f'{field}, {a}, {b}'+'}'
                    code.append(f'record[{json.dumps(key)},{momentum},{wl(val)},rules];')
                key = '{"AZ", '+f'{a}, {b}'+'}'
                code.append(f'record[{json.dumps(key)},g[lt3,lt4],{wl(2j*e*e*T[a-2,b-2])},rules];')
        for a, b in ((1,2),(2,1),(1,3),(3,1)):
            key = '{'+f'Ah[{{2}}], {a}, {b}'+'}'
            code.append(f'record[{json.dumps(key)},1,{wl(-1j*tri["A"][a-1,b-1])},rules];')
    code += ['Export[FileNameJoin[{out,"mixed_hz_checks.json"}],checks,"RawJSON"];',
             'Print["D16_MIXED_HZ_CHECKS ",Length[checks]," MAX ",Max[Lookup[checks,"residual"]]];',
             'Exit[If[Max[Lookup[checks,"residual"]]<1.*^-8,0,1]];']
    script = HERE/'local/check_mixed_hz.m'
    script.write_text('\n'.join(code)+'\n')
    result = subprocess.run(['math', '-script', str(script)], cwd=ROOT, capture_output=True, text=True)
    (HERE/'local/mixed_hz_source_check.log').write_text(result.stdout+result.stderr)
    if result.returncode:
        raise RuntimeError(result.stdout+result.stderr)
    checks = json.loads((HERE/'local/mixed_hz_checks.json').read_text())
    raw = json.loads((HERE/'local/mixed_hz_raw.json').read_text())
    raw.update(status='NATIVE_MIXED_HZ_VERTICES_PASS', checks=checks,
        max_abs_residual=max(z['residual'] for z in checks), physical_inputs=native['physical_inputs'],
        sources_sha256={str(f.relative_to(ROOT)):sha(f) for f in
            [ROOT/'models/SARAH/ZeeTypeII/ZeeTypeII.m', HERE/'extract_mixed_hz.m', Path(__file__)]},
        raw_sha256=sha(HERE/'local/mixed_hz_raw.m'))
    (HERE/'mixed_hz_sources.json').write_text(json.dumps(raw, indent=2, sort_keys=True)+'\n')
    print(raw['status'], len(checks), raw['max_abs_residual'])


if __name__ == '__main__':
    main()
