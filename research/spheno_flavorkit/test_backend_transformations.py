"""Run two bounded complex and zero-F checks on the instrumented backend."""
import argparse
import json
import re
import subprocess
from pathlib import Path

from check_components import pairs

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT/'research/spheno_flavorkit/local'

def change(card, conjugate=False, zero_f=False):
    block = ''
    rows = []
    for line in card.splitlines():
        match = re.match(r'\s*Block\s+(\S+)', line, re.I)
        if match:
            block = match.group(1).upper()
        m = re.match(r'^(\s*\d+\s+\d+\s+)(\S+)(.*)$', line)
        if m and (block in ('FZEEIN', 'IMFZEEIN', 'IMYEE2IN')):
            value = float(m.group(2))
            if zero_f and block in ('FZEEIN', 'IMFZEEIN'):
                value = 0.
            if conjugate and block.startswith('IM'):
                value = -value
            line = f'{m.group(1)}{value:.16e}{m.group(3)}'
        rows.append(line)
    return '\n'.join(rows)+'\n'

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--executable', type=Path, default=LOCAL/'SPheno-4.0.5/bin/SPhenoZeeTypeII')
    p.add_argument('--card', type=Path, default=LOCAL/'d15_runs/group0.in')
    p.add_argument('--outdir', type=Path, default=LOCAL/'d15_transformations')
    a = p.parse_args()
    a.outdir.mkdir(parents=True, exist_ok=True)
    result = {}
    f_vertex_max = {}
    for name, options in [('original', {}), ('conjugated', {'conjugate':True}), ('zero_F', {'zero_f':True})]:
        card, spectrum = a.outdir/f'{name}.in', a.outdir/f'{name}.spc'
        card.write_text(change(a.card.read_text(), **options))
        run = subprocess.run([str(a.executable.resolve()), str(card.resolve()), str(spectrum.resolve())], cwd=a.outdir, capture_output=True, text=True, check=True)
        (a.outdir/f'{name}.log').write_text(run.stdout+run.stderr)
        amplitudes = []
        for ch in 'LR':
            matches = [pairs(line) for line in run.stdout.splitlines() if 'PILOT_K2'+ch+'_21' in line]
            if len(matches) != 1 or len(matches[0]) != 1:
                raise ValueError('Missing K2 readback')
            amplitudes.append(matches[0][0])
        result[name] = amplitudes
        vertices = [pairs(line) for line in run.stdout.splitlines() if 'D15_VERTEX ' in line]
        if len(vertices) != 27:
            raise ValueError('Missing charged vertices')
        f_vertex_max[name] = max(max(abs(row[0]), abs(row[3])) for row in vertices)
    residual = [abs(y-x.conjugate())/abs(x) for x,y in zip(result['original'],result['conjugated'])]
    # F=0 suppresses the dominant charged F contraction but need not null
    # neutral LFV or the D contribution; no full-amplitude null is asserted.
    payload = {'conjugation_relative_residual':residual, 'coefficients':{k:[[z.real,z.imag] for z in v] for k,v in result.items()},
               'conjugation_pass':max(residual)<1e-10, 'F_vertex_max':f_vertex_max,
               'zero_F_vertex_pass': f_vertex_max['zero_F']==0 and f_vertex_max['original']>0,
               'zero_F_interpretation':'diagnostic only: neutral LFV and D terms remain'}
    (a.outdir/'results.json').write_text(json.dumps(payload,indent=2)+'\n')
    print(json.dumps(payload,indent=2))
    if not payload['conjugation_pass'] or not payload['zero_F_vertex_pass']:
        raise SystemExit('Complex conjugation check failed')

if __name__ == '__main__':
    main()
