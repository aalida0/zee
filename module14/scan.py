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
import tempfile
import platform
import importlib.metadata
import contextlib
import io
import sys

import numpy as np


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


def file_sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def publish(path, tmp):
    # link is atomic and refuses an existing destination, including concurrent jobs.
    os.link(tmp, path)
    os.unlink(tmp)


def temporary(path):
    fd, name = tempfile.mkstemp(prefix='.' + Path(path).name + '.', dir=str(Path(path).parent))
    os.close(fd)
    return name


def scalar_gates(row):
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
    return gates


def runtime_info():
    versions = {}
    for name in ('numpy', 'scipy', 'mpmath', 'jsonschema', 'sympy'):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = 'UNAVAILABLE'
    config = io.StringIO()
    with contextlib.redirect_stdout(config):
        np.show_config()
    return {'python': sys.version, 'platform': platform.platform(),
            'machine': platform.machine(), 'dependencies': versions,
            'numpy_build_sha256': hashlib.sha256(config.getvalue().encode()).hexdigest(),
            'thread_environment': {k: os.environ.get(k) for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS')}}


def scalar_source_version():
    root = Path(__file__).resolve().parents[1]
    files = [Path(__file__).resolve()]
    for directory in ('module0', 'module1', 'scripts'):
        files.extend(p for p in (root / directory).rglob('*') if p.is_file() and p.suffix in ('.py', '.json'))
    sources = {str(p.relative_to(root)): file_sha(p) for p in sorted(files)}
    return digest({'schema': 'd14-scalar-cache-v1', 'sources': sources, 'runtime': runtime_info()})


def cached_scalar_gates(row, cache_dir, version):
    key_data = {'schema': 'd14-scalar-cache-v1', 'scalar_sha256': row['scalar_sha256'],
                'source_version': version, 'settings': 'module1-cheap-gates-d10-exact-v1'}
    key = digest(key_data)
    path = Path(cache_dir) / (key + '.json')
    if path.exists():
        entry = json.loads(path.read_text())
        if entry.get('key') != key_data or entry.get('gates_sha256') != digest(entry.get('gates')):
            raise ValueError('Corrupt or stale scalar cache entry: ' + str(path))
        return entry['gates']
    gates = scalar_gates(row)
    # Transient computational errors are never persisted.
    if any(v['assessment'] == 'ERROR' for v in gates.values()):
        return gates
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    tmp = temporary(path)
    Path(tmp).write_text(encode({'key': key_data, 'gates': gates, 'gates_sha256': digest(gates)})+'\n')
    try:
        publish(path, tmp)
    except FileExistsError:
        os.unlink(tmp)
        return cached_scalar_gates(row, cache_dir, version)
    return gates


def run(shard, output, receipt, config, families=2, limit=math.sqrt(4*math.pi), resume=False, cache_dir=None):
    if families < 1 or not math.isfinite(limit) or limit <= 0:
        raise ValueError("Invalid neutrino family settings")
    if len({Path(p).resolve() for p in (shard, output, receipt)}) != 3:
        raise ValueError('Shard, output and receipt must be distinct')
    source = file_sha(shard)
    settings = {'shard_sha256': source, 'config_sha256': digest(config),
                'families': families, 'perturbativity_limit': limit,
                'worker_sha256': file_sha(__file__),
                'source_commit': os.environ.get('ZEE_D14_SOURCE_COMMIT', 'LOCAL_UNSPECIFIED'),
                'source_bundle_sha256': os.environ.get('ZEE_D14_BUNDLE_SHA256', 'LOCAL_UNSPECIFIED'),
                'runtime': runtime_info()}
    if Path(output).exists() or Path(receipt).exists():
        if resume and Path(output).is_file() and Path(receipt).is_file():
            saved = json.loads(Path(receipt).read_text())
            if all(saved.get(k) == v for k, v in settings.items()) and saved.get('output_sha256') == file_sha(output):
                return saved
        raise FileExistsError('Output or receipt exists; use --resume for a matching completed pair, or new paths for an incomplete pair')
    scalar_version = scalar_source_version() if cache_dir else None
    start = time.monotonic()
    cpu_start = time.process_time()
    count = 0
    counts = {}
    tmp = temporary(output)
    with open(shard) as inp, open(tmp, 'w') as out:
        for line in inp:
            count += 1
            row = json.loads(line)
            if row['config_sha256'] != digest(config):
                raise ValueError('config hash mismatch')
            if digest(row['scalar']) != row['scalar_sha256']:
                raise ValueError('scalar hash mismatch')
            gates = cached_scalar_gates(row, cache_dir, scalar_version) if cache_dir else scalar_gates(row)
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
    report = dict(settings, schema='d14-worker-receipt-1', output_sha256=file_sha(tmp),
                  input_count=count, output_count=count, counts=counts,
                  elapsed_seconds=time.monotonic()-start, cpu_seconds=time.process_time()-cpu_start,
                  peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    receipt_tmp = temporary(receipt)
    Path(receipt_tmp).write_text(encode(report)+'\n')
    publish(output, tmp)
    publish(receipt, receipt_tmp)
    return report


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='action', required=True)
    g = sub.add_parser('generate'); g.add_argument('--config', required=True); g.add_argument('--output', required=True)
    w = sub.add_parser('worker'); w.add_argument('--shard', required=True); w.add_argument('--output', required=True); w.add_argument('--receipt', required=True); w.add_argument('--config', required=True); w.add_argument('--families', type=int, default=2); w.add_argument('--perturbativity-limit', type=float, default=math.sqrt(4*math.pi)); w.add_argument('--resume', action='store_true'); w.add_argument('--cache-dir')
    a = p.parse_args()
    if a.action == 'generate': generate(json.loads(Path(a.config).read_text()), a.output)
    else: run(a.shard, a.output, a.receipt, json.loads(Path(a.config).read_text()), a.families, a.perturbativity_limit, a.resume, a.cache_dir)

if __name__ == '__main__': main()
