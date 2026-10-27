#!/usr/bin/env python3
"""Fail-closed launcher/build support for the conditional two-state LO adapter."""
import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from module5.hyperiso_patch_contract import make_contract, unique_pairs, INPUT_FIELDS
from zee_module5_hyperiso_runtime import verify_checkout, verify_build, sha

ROOT = Path(__file__).resolve().parents[1]


def run(args, cwd, check=True):
    p = subprocess.run(list(map(str, args)), cwd=cwd, capture_output=True, text=True, timeout=240)
    if check and p.returncode:
        raise RuntimeError(f'{args}: {p.returncode}: {p.stderr[-3000:]}')
    return p


def build(upstream, binary, dest):
    upstream, binary, dest = upstream.resolve(), binary.resolve(), dest.resolve()
    verify_checkout(upstream)
    provenance = verify_build(upstream, binary)
    head = run(['git', 'rev-parse', 'HEAD', 'v1.0.3^{}', 'v1.0.3'], upstream).stdout.splitlines()
    if head[:2] != ['09d26ac6e71d1528922097a896d15693589f636b'] * 2:
        raise ValueError('Release peel mismatch')
    version = run([binary, '--version'], upstream).stdout.strip()
    if version != '1.0.3':
        raise ValueError('Version mismatch')
    folder = Path(provenance['build_directory'])
    dest.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).with_suffix('.cpp').resolve()
    commands = json.loads((folder/'compile_commands.json').read_text())
    cli = next(x for x in commands if x['file'].endswith('/UserInterface/main.cpp'))
    args = shlex.split(cli['command'])
    obj, exe = dest/'two_state.o', dest/'two_state'
    args[args.index('-o')+1] = str(obj)
    args[args.index('-c')+1] = str(source)
    run(args, folder)
    link = run(['ninja', '-C', folder, '-t', 'commands', 'hyperiso-ui'], upstream).stdout.splitlines()[-1]
    args = shlex.split(link)
    start = args.index('&&')+1
    args = args[start:args.index('&&', start)]
    args[args.index('-o')+1] = str(exe)
    args = [str(obj) if x.endswith('/hyperiso-ui.dir/main.cpp.o') else x for x in args]
    run(args, folder)
    return exe, dict(provenance, head=head[0], peeled_commit=head[1], tag_hash=head[2],
                     version=version, adapter_binary_sha256=sha(exe))


def validate_contract(record):
    expected = make_contract({k: record['input'][k] for k in INPUT_FIELDS})
    # Only the CLI's optional raw-input hash may extend the canonical contract.
    if {k:v for k,v in record.items() if k != 'input_sha256'} != expected:
        raise ValueError('Contract differs from frozen signed source/provenance')
    if record['matching_scale_GeV'] != 160.:
        raise ValueError('Only qmatch=160 supported')
    return record


def command(exe, contract, qhad, lha):
    c = validate_contract(contract)
    args = [str(exe), '--lha', str(Path(lha).resolve()), '--spectrum', 'true', '--mode', 'patch', '--model', 'SM', '--contribution', 'BSM',
            '--order', 'LO', '--top-scheme', 'MSBAR_AT_QMATCH', '--qmatch', '160',
            '--qhad', str(qhad), '--mt', str(c['top_mass_MSbar_at_matching_scale_GeV'])]
    for key in ('C7', 'C8'):
        args += ['--'+key.lower(), str(c['coefficients'][key]['real']),
                 '--'+key.lower()+'-imag', str(c['coefficients'][key]['imag'])]
    return args


def parse_output(text):
    result = {'mt': float(re.search(r'^C0 MT (\S+)$', text, re.M)[1]), 'BEFORE': {}, 'AFTER': {}}
    for stage, coeff, cont, mr, mi, rr, ri in re.findall(
            r'^C0 (BEFORE|AFTER) (C\d) (\d+) \(([^,]+),([^\)]+)\) \(([^,]+),([^\)]+)\)$', text, re.M):
        result[stage].setdefault(coeff, {})[int(cont)] = (complex(float(mr), float(mi)), complex(float(rr), float(ri)))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--upstream', type=Path, required=True)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--contract', type=Path, required=True)
    p.add_argument('--qhad', type=float, required=True)
    p.add_argument('--lha', type=Path, required=True, help='Explicit SM parameter source; top mass is checked at runtime')
    p.add_argument('--local', type=Path, default=ROOT/'validation/module5/local/two_state')
    a = p.parse_args()
    c = validate_contract(json.loads(a.contract.read_text(), object_pairs_hook=unique_pairs))
    exe, _ = build(a.upstream, a.binary, a.local)
    r = run(command(exe, c, a.qhad, a.lha), a.upstream, check=False)
    print(r.stdout, end='');print(r.stderr, end='', file=sys.stderr)
    return r.returncode


if __name__ == '__main__':
    sys.exit(main())
