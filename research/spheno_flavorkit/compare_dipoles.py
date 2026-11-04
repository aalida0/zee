"""Reproduce exploratory D12 comparisons; no operator map is certified."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / 'research/spheno_flavorkit/local'
DATA = ROOT / 'validation/module12/d12_benchmarks.json'
CARD = ROOT / 'research/spheno_flavorkit/benchmark_card.py'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=LOCAL / 'd15_comparison.json')
    p.add_argument('--executable', type=Path, default=LOCAL / 'SPheno-4.0.5/bin/SPhenoZeeTypeII')
    p.add_argument('--template', type=Path, default=LOCAL / 'output/ZeeTypeII/EWSB/SPheno/Input_Files/LesHouches.in.ZeeTypeII')
    a = p.parse_args()
    exe, template = a.executable.resolve(), a.template.resolve()
    work = LOCAL / 'd15_runs'
    work.mkdir(parents=True, exist_ok=True)
    records = []
    for index, group in enumerate(json.loads(DATA.read_text())['groups']):
        witness = group['witnesses']['central']
        card, spectrum, log = (work / f'group{index}.{suffix}' for suffix in ('in', 'spc', 'log'))
        subprocess.run([sys.executable, str(CARD), str(template), str(card), '--group', str(index)], check=True, capture_output=True, text=True, cwd=ROOT)
        run = subprocess.run([str(exe), str(card), str(spectrum)], cwd=work, capture_output=True, text=True, check=True)
        log.write_text(run.stdout + run.stderr)
        vals = {}
        for ch in 'LR':
            matches = re.findall(r'PILOT_K2' + ch + r'_21\s*\(\s*([^,]+),\s*([^\)]+)\)', run.stdout)
            if len(matches) != 1:
                raise RuntimeError('Expected one instrumented coefficient for K2' + ch)
            vals[ch] = complex(*(float(x.replace('D', 'E')) for x in matches[0]))
        match = re.search(r'^\s*701\s+(\S+)\s+#\s*BR\(mu->e gamma\)', spectrum.read_text(), re.M)
        if not match:
            raise RuntimeError('Missing mu to e gamma rate')
        rad = witness['signed_radiative']['mu_to_e_gamma']
        cs = rad['grouped_amplitudes']['scalar_one_loop']
        cvals = [complex(x['real'], x['imag']) for x in cs]
        pack = lambda x: [x.real, x.imag]
        rows = {}
        for ch, c in zip('LR', cvals):
            k = vals[ch]
            rows[ch] = {'K2': pack(k), 'C': pack(c), 'candidate_K_over_minus_conj_C': pack(k / -c.conjugate()) if c else None,
                        'candidate_relative_residual': abs(k + c.conjugate()) / abs(c) if c else None}
        br = float(match.group(1))
        records.append({'group': index, 'id': witness['id'], 'ordering': group['ordering'], 'card_sha256': sha(card), 'log_sha256': sha(log), 'spectrum_sha256': sha(spectrum), 'coefficients_GeV_minus2': rows, 'spheno_BR': br, 'module3_scalar_BR': rad['grouped_BR']['scalar_one_loop'], 'rate_ratio': br / rad['grouped_BR']['scalar_one_loop']})
    output = {'status': 'NOT_EVALUATED', 'interpretation': 'Exploratory unmatched input diagnostic; candidate conversion is not derived.', 'd12_sha256': sha(DATA), 'executable_sha256': sha(exe), 'template_sha256': sha(template), 'records': records}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()
