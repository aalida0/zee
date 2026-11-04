"""Create an exploratory D12 card; it is not a scheme-matched validation."""
import argparse
import json
import math
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from module1.scalar_constraints import reconstruct


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('template', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    group = json.loads((ROOT / 'validation/module12/d12_benchmarks.json').read_text())['groups'][0]
    witness = group['witnesses']['central']
    record = witness['module2_input']['scalar']['record']
    physical = record['physical']
    params, _, _ = reconstruct(physical)
    values = [params['Lambda'+str(i)] for i in range(1, 6)] + [params[k] for k in
              ('LambdaC', 'K1', 'K2', 'K12')] + [math.tan(physical['beta'])] + [params[k] for k in
              ('M12Sq', 'MCS2', 'Mu4')]
    sm = {2: 1/(math.sqrt(2)*physical['v']**2), 4: record['electroweak']['mZ'],
          7: witness['module2_input']['lepton_masses_GeV'][2]}
    block = ''
    lines = []
    for line in args.template.read_text().splitlines():
        match = re.match(r'\s*Block\s+(\S+)', line, re.I)
        if match:
            block = match.group(1).upper()
            if block == 'MODSEL':
                lines.append(line)
                lines.append(' 5 2 # enable complex input blocks')
                continue
        row = re.match(r'^(\s*)(\d+)\s+\S+(.*)$', line)
        if row:
            index = int(row.group(2))
            value = values[index-1] if block == 'MINPAR' and 1 <= index <= len(values) else (
                sm.get(index) if block == 'SMINPUTS' else None)
            if block == 'SPHENOINPUT' and index in (11, 16):
                value = 0
            if value is not None:
                line = f'{row.group(1)}{index} {value:.16e} {row.group(3)}'
        lines.append(line)
    # The generated reader handles both real and imaginary block names.  Last
    # occurrence is used; verify the generated input/output before validation.
    for key, name in [('F', 'FZEE'), ('Ye2', 'YEE2')]:
        for part, prefix in [('real', ''), ('imag', 'IM')]:
            lines.append(f'Block {prefix}{name}IN')
            matrix = witness['yukawas'][key][part]
            for i in range(3):
                for j in range(3):
                    lines.append(f' {i+1} {j+1} {matrix[i][j]:.16e} # matrix entry')
    lines.append('Block SPHENOINPUT # matrix terminator')
    args.output.write_text('\n'.join(lines)+'\n')
    print('Exploratory D12 candidate:', witness['id'])
    print('Not scheme matched: SM electron/muon inputs, Yukawa matching, running and phases require audit.')


if __name__ == '__main__':
    main()
