"""D14A preliminary deterministic scalar proposal and cheap-screen pipeline."""
import argparse
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import random
import resource
import time

from module1.scalar_constraints import validate_input, reconstruct, check_bfb, unitarity, ewpo
from module1.d10_certificate import attempt_certificate
from module11.d11b_offline_fit import target, inverse_input, perturbativity
from module2.interface import evaluate as neutrino_evaluate


def scalar_status(gates):
    values = [gates[k]['assessment'] for k in ('reconstruction', 'bfb', 'unitarity', 'ewpo', 'vacuum')]
    if 'ERROR' in values:
        return 'ERROR'
    if 'FAIL' in values:
        return 'FAIL'
    if any(v != 'PASS' for v in values):
        return 'UNKNOWN'
    return 'PASS'


def neutrino_input(row, seed, ordering, family):
    if ordering not in ('NO', 'IO') or family < 0:
        raise ValueError('Invalid family identity')
    family_seed = digest(['d14-neutrino-v1', seed, row['id'], ordering, family])
    rng = random.Random(int(family_seed, 16))
    spec = {'lightest_eV': 10**rng.uniform(-3, -1.7),
            'alpha21_rad': rng.uniform(0, 2*math.pi),
            'alpha31_rad': rng.uniform(0, 2*math.pi), 'parameters': None}
    cone = {'t': {'real': rng.uniform(-2, 2), 'imag': rng.uniform(-2, 2)},
            'scale': 10**rng.uniform(-5, -2), 'root': rng.randrange(2),
            'chart': [0, 1, 2], 'phase_rad': rng.uniform(0, 2*math.pi)}
    coefficients = [complex(rng.uniform(-0.01, 0.01), rng.uniform(-0.01, 0.01)) for _ in range(4)]
    scalar = {'kind': 'module1_input', 'record': row['scalar'], 'sha256': row['scalar_sha256']}
    inp = inverse_input(scalar, ordering, spec, cone, coefficients)
    return family_seed, spec, inp


def evaluate_family(row, seed, ordering, family, limit):
    seed_hash, spec, inp = neutrino_input(row, seed, ordering, family)
    result = {'ordering': ordering, 'family': family, 'seed_sha256': seed_hash,
              'target_spec': spec, 'input': inp, 'input_sha256': digest(inp),
              'target_sha256': digest(inp['target_eV']),
              'target_label': 'NuFIT6.1 secondary best-fit coordinates; no joint likelihood',
              'perturbativity_limit': limit}
    try:
        out = neutrino_evaluate(inp)
        metrics = perturbativity(out)
        residual = out['inverse']['family_relative_residual']
        result.update(status='PASS' if metrics['overall_max'] < limit else 'FAIL',
                      closure_status='PASS', relative_residual=residual,
                      max_abs_yukawas=metrics['max_abs'],
                      F=out['F'], D=out['D'], Ye=out['Ye'], Ye2=out['Ye2'], Mnu=out['Mnu'],
                      module2_provenance=out['provenance'])
    except Exception as exc:
        result.update(status='ERROR', closure_status='ERROR', error_type=type(exc).__name__, error=str(exc))
    return result



def encode(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(x):
    return hashlib.sha256(encode(x).encode()).hexdigest()


def generate(config, output):
    template = json.loads(Path(config['template']).read_text())
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    manifest = (output / 'manifest.jsonl').open('w')
    shard = None
    for i in range(config['count']):
        if i % config['shard_size'] == 0:
            if shard: shard.close()
            shard = (output / ('shard_%06d.jsonl' % (i // config['shard_size']))).open('w')
        rng = random.Random(int(digest([config['seed'], i]), 16))
        arm = config['arms'][i % len(config['arms'])]
        point = copy.deepcopy(template)
        point['benchmark_id'] = 'd14_%08d' % i
        for key, bounds in arm['ranges'].items():
            point['physical'][key] = rng.uniform(*bounds)
        row = {'id': i, 'arm': arm['name'], 'config_sha256': digest(config),
               'scalar_sha256': digest(point), 'scalar': point}
        line = encode(row) + '\n'
        manifest.write(line)
        shard.write(line)
    if shard: shard.close()
    manifest.close()


def run(shard, output, receipt, config, families=2, limit=math.sqrt(4*math.pi)):
    if families < 1 or not math.isfinite(limit) or limit <= 0:
        raise ValueError("Invalid neutrino family settings")
    start = time.monotonic()
    source = hashlib.sha256(Path(shard).read_bytes()).hexdigest()
    counts = {}
    tmp = str(output) + '.tmp'
    with open(shard) as inp, open(tmp, 'w') as out:
        for line in inp:
            row = json.loads(line)
            if row['config_sha256'] != digest(config):
                raise ValueError('config hash mismatch')
            if digest(row['scalar']) != row['scalar_sha256']:
                raise ValueError('scalar hash mismatch')
            gates = {k: {'assessment': 'NOT_EVALUATED'} for k in ('reconstruction', 'bfb', 'unitarity', 'ewpo', 'vacuum')}
            try:
                x, ew, _, _ = validate_input(row['scalar'])
                p, inherited, gates['reconstruction'] = reconstruct(x)
                for name, fn in [('bfb', lambda: check_bfb(p)), ('unitarity', lambda: unitarity(p, inherited)), ('ewpo', lambda: ewpo(x, ew, row['scalar']['ew_fit']))]:
                    try: gates[name] = fn()
                    except Exception as exc: gates[name] = {'assessment': 'ERROR', 'reason': str(exc)}
                if all(gates[k]['assessment'] == 'PASS' for k in ('reconstruction', 'bfb', 'unitarity', 'ewpo')):
                    try:
                        cert = attempt_certificate(p, x)
                        gates['vacuum'] = {'assessment': 'PASS' if cert['certified'] else 'UNKNOWN', 'certificate': cert}
                    except Exception as exc:
                        gates['vacuum'] = {'assessment': 'ERROR', 'reason': str(exc)}
            except Exception as exc:
                gates['reconstruction'] = {'assessment': 'ERROR', 'reason': str(exc)}
            for name, result in gates.items():
                key = name + ':' + result['assessment']
                counts[key] = counts.get(key, 0) + 1
            status = scalar_status(gates)
            eligible = all(gates[k]['assessment'] == 'PASS' for k in ('reconstruction', 'bfb', 'unitarity', 'ewpo')) and gates['vacuum']['assessment'] in ('PASS', 'UNKNOWN')
            neutrinos = [evaluate_family(row, config['seed'], ordering, family, limit)
                         for ordering in ('NO', 'IO') for family in range(families)] if eligible else []
            for n in neutrinos:
                key = 'neutrino:' + n['ordering'] + ':' + n['status']
                counts[key] = counts.get(key, 0) + 1
            result = {'id': row['id'], 'config_sha256': row['config_sha256'], 'scalar_sha256': row['scalar_sha256'], 'scalar_status': status, 'gates': gates,
                      'neutrino': neutrinos if eligible else 'NOT_EVALUATED', 'lfv': 'NOT_EVALUATED', 'bsgamma': 'NOT_EVALUATED', 'widths': 'NOT_EVALUATED', 'production': 'NOT_EVALUATED', 'higgstools': 'NOT_EVALUATED'}
            out.write(encode(result) + '\n')
    os.replace(tmp, output)
    Path(receipt).write_text(encode({'shard_sha256': source, 'output_sha256': hashlib.sha256(Path(output).read_bytes()).hexdigest(), 'counts': counts, 'elapsed_seconds': time.monotonic()-start, 'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})+'\n')


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='action', required=True)
    g = sub.add_parser('generate'); g.add_argument('--config', required=True); g.add_argument('--output', required=True)
    w = sub.add_parser('worker'); w.add_argument('--shard', required=True); w.add_argument('--output', required=True); w.add_argument('--receipt', required=True); w.add_argument('--config', required=True); w.add_argument('--families', type=int, default=2); w.add_argument('--perturbativity-limit', type=float, default=math.sqrt(4*math.pi))
    a = p.parse_args()
    if a.action == 'generate': generate(json.loads(Path(a.config).read_text()), a.output)
    else: run(a.shard, a.output, a.receipt, json.loads(Path(a.config).read_text()), a.families, a.perturbativity_limit)

if __name__ == '__main__': main()
