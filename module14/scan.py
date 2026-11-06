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
    try:
        seed_hash, spec, inp = neutrino_input(row, seed, ordering, family)
    except Exception as exc:
        return {'ordering': ordering, 'family': family,
                'seed_sha256': digest(['d14-neutrino-v1', seed, row['id'], ordering, family]),
                'scalar_sha256': row['scalar_sha256'], 'input': None, 'input_sha256': None,
                'target_sha256': None, 'target_spec': None, 'perturbativity_limit': limit,
                'status': 'ERROR', 'closure_status': 'ERROR', 'error_phase': 'input_construction',
                'error_type': type(exc).__name__, 'error': str(exc)}
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


def correlated_point(point, arm, rng):
    """Draw a heavy-spectrum proposal; reject invalid inputs, never clamp them."""
    ranges = arm['ranges']
    x = point['physical']
    for _ in range(10000):
        x['mH2'] = rng.uniform(*ranges['mH2'])
        x['mH1'] = x['mH2'] * rng.uniform(*ranges['mH1_fraction'])
        x['beta'] = math.atan(math.exp(rng.uniform(*map(math.log, ranges['tanbeta']))))
        x['alpha'] = x['beta'] + rng.uniform(*ranges['delta_alpha'])
        for key in ('gamma', 'lc', 'k1', 'k2', 'k12'):
            x[key] = rng.uniform(*ranges[key])
        md2 = math.cos(x['gamma'])**2 * x['mH1']**2 + math.sin(x['gamma'])**2 * x['mH2']**2
        md = math.sqrt(md2)
        x['mh2'] = md + rng.uniform(*ranges['mh2_splitting'])
        x['ma'] = md + rng.uniform(*ranges['ma_splitting'])
        x['m12sq'] = md2 * math.sin(x['beta']) * math.cos(x['beta']) * rng.uniform(*ranges['m12sq_factor'])
        if x['mH2'] <= x['mH1'] + point['electroweak']['mZ'] + 20:
            continue
        try:
            validate_input(point)
        except ValueError:
            continue
        return
    raise ValueError('Correlated arm could not produce a valid input: ' + arm['name'])


def generate(config, output):
    template_path = Path(config['template'])
    if config.get('schema') == 'd14-final-config-1':
        from module14.final_config import validate, ROOT
        validate(config)
        template_path = ROOT/template_path
    template = json.loads(template_path.read_text())
    mode = config.get('sampling_mode', 'independent_uniform')
    if mode not in ('independent_uniform', 'correlated_heavy_v1'):
        raise ValueError('Unsupported sampling mode')
    if mode == 'correlated_heavy_v1':
        arms = config['arms']
        if not arms or any(type(a.get('weight')) is not int or a['weight'] <= 0 for a in arms):
            raise ValueError('Correlated arm weights must be positive integers')
        keys = {'mH2', 'mH1_fraction', 'tanbeta', 'delta_alpha', 'gamma', 'lc',
                'k1', 'k2', 'k12', 'mh2_splitting', 'ma_splitting', 'm12sq_factor'}
        for arm in arms:
            ranges = arm['ranges']
            if ranges.keys() != keys:
                raise ValueError('Invalid correlated arm ranges')
            for bounds in ranges.values():
                if (not isinstance(bounds, list) or len(bounds) != 2
                        or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in bounds)
                        or bounds[0] > bounds[1]):
                    raise ValueError('Invalid correlated range')
            if ranges['tanbeta'][0] <= 0 or ranges['mH2'][0] <= 0 or ranges['mH1_fraction'][0] <= 0:
                raise ValueError('Masses, mass fractions and tanbeta must be positive')
        # Cumulative integer weights preserve the original slot schedule
        # without allocating memory proportional to user-supplied weights.
        total_weight = sum(a['weight'] for a in arms)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    manifest = (output / 'manifest.jsonl').open('w')
    shard = None
    for i in range(config['count']):
        if i % config['shard_size'] == 0:
            if shard: shard.close()
            shard = (output / ('shard_%06d.jsonl' % (i // config['shard_size']))).open('w')
        rng = random.Random(int(digest([config['seed'], i]), 16))
        if mode == 'correlated_heavy_v1':
            slot = i % total_weight
            for arm in arms:
                if slot < arm['weight']: break
                slot -= arm['weight']
        else:
            arm = config['arms'][i % len(config['arms'])]
        point = copy.deepcopy(template)
        point['benchmark_id'] = 'd14_%08d' % i
        if mode == 'correlated_heavy_v1':
            correlated_point(point, arm, rng)
        else:
            for key, bounds in arm['ranges'].items():
                point['physical'][key] = rng.uniform(*bounds)
        row = {'id': i, 'arm': arm['name'], 'config_sha256': digest(config),
               'scalar_sha256': digest(point), 'scalar': point}
        line = encode(row) + '\n'
        manifest.write(line)
        shard.write(line)
    if shard: shard.close()
    manifest.close()
    if config.get('schema') == 'd14-final-config-1':
        from module14.final_workflow import write_atomic
        write_atomic(output/'generation_receipt.json', {
            'schema': 'd14-generation-1', 'config_sha256': digest(config),
            'source_commit': config['source_commit'], 'template_sha256': config['template_sha256'],
            'manifest_sha256': file_sha(output/'manifest.jsonl'),
            'shards_sha256': {p.name: file_sha(p) for p in sorted(output.glob('shard_*.jsonl'))}})


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
    for name in ('numpy', 'scipy', 'mpmath', 'jsonschema', 'sympy', 'HiggsTools', 'matplotlib'):
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


def run(shard, output, receipt, config, families=2, limit=math.sqrt(4*math.pi), resume=False, cache_dir=None, lfv=False, lfv_tree=False, bsgamma=False, d9b_probe=None, higgs=False, hb_data=None, hs_data=None, production_dir=None, preflight_report=None):
    final_lock = None
    if config.get('schema') == 'd14-final-config-1':
        from module14.final_config import validate, worker_settings, validate_manifest
        from module14.final_workflow import require_preflight
        from module14.conditional_scan.workflow import load
        validate(config)
        if not preflight_report: raise ValueError('Final worker requires a pinned preflight report')
        report = load(preflight_report); require_preflight(config, report)
        actual = dict(families=families, perturbativity_limit=limit, cache_dir=cache_dir,
                      lfv=lfv, lfv_tree=lfv_tree, bsgamma=bsgamma, d9b_probe=d9b_probe,
                      higgs=higgs, hb_data=hb_data, hs_data=hs_data)
        if actual != worker_settings(config) or production_dir is not None:
            raise ValueError('Worker settings do not match final config; production enrichment is postprocessing')
        if os.environ.get('ZEE_D14_SOURCE_COMMIT') != config['source_commit']:
            raise ValueError('Final worker source commit mismatch')
        if len(validate_manifest(shard, config, require_full=False)) != config['shard_size']:
            raise ValueError('Final worker requires one complete bounded shard')
        final_lock = report['report_sha256']
    if resume and production_dir:
        raise ValueError('Resume with mutable production directory is unsupported; use fresh outputs')
    if lfv_tree and not lfv:
        raise ValueError('Three-body calculation requires LFV')
    if families < 1 or not math.isfinite(limit) or limit <= 0:
        raise ValueError("Invalid neutrino family settings")
    if len({Path(p).resolve() for p in (shard, output, receipt)}) != 3:
        raise ValueError('Shard, output and receipt must be distinct')
    source = file_sha(shard)
    settings = {'shard_sha256': source, 'config_sha256': digest(config),
                'families': families, 'perturbativity_limit': limit, 'lfv_enabled': lfv, 'lfv_tree_enabled': lfv_tree, 'bsgamma_enabled': bsgamma, 'd9b_probe_sha256': file_sha(d9b_probe) if d9b_probe and Path(d9b_probe).is_file() else None, 'higgs_enabled': higgs, 'hb_data': hb_data, 'hs_data': hs_data, 'production_dir': production_dir,
                'worker_sha256': file_sha(__file__),
                'source_commit': os.environ.get('ZEE_D14_SOURCE_COMMIT', 'LOCAL_UNSPECIFIED'),
                'source_bundle_sha256': os.environ.get('ZEE_D14_BUNDLE_SHA256', 'LOCAL_UNSPECIFIED'),
                'runtime': runtime_info()}
    if final_lock is not None:
        settings['final_preflight_sha256'] = final_lock
        settings['manifest_sha256'] = os.environ.get('ZEE_D14_MANIFEST_SHA256')
        from module14.final_config import sha
        sha(settings['manifest_sha256'], 'Original manifest SHA256')
    if higgs and hb_data and hs_data and Path(hb_data).is_dir() and Path(hs_data).is_dir():
        from module13.higgstools import dataset
        settings['higgs_datasets_sha256'] = digest({'HB': dataset(Path(hb_data)), 'HS': dataset(Path(hs_data))})
    if Path(output).exists() or Path(receipt).exists():
        if resume and Path(output).is_file() and Path(receipt).is_file():
            saved = json.loads(Path(receipt).read_text())
            if all(saved.get(k) == v for k, v in settings.items()) and saved.get('output_sha256') == file_sha(output):
                from module14.collect import collect
                audit = collect(shard, config, [(shard, output, receipt)], families, limit,
                                settings['source_commit'], settings['source_bundle_sha256'],
                                report if final_lock else None, require_full_manifest=False)
                if audit['status'] == 'COMPLETE' and not audit['computational_errors']:
                    return saved
        raise FileExistsError('Output or receipt exists; use --resume for a matching completed pair, or new paths for an incomplete pair')
    scalar_version = scalar_source_version() if cache_dir else None
    start = time.monotonic()
    cpu_start = time.process_time()
    count = 0
    point_ids = set()
    counts = {}
    lfv_seconds = 0.0
    bsgamma_seconds = 0.0
    higgs_seconds = 0.0
    tmp = temporary(output)
    with open(shard) as inp, open(tmp, 'w') as out:
        for line in inp:
            count += 1
            row = json.loads(line)
            if type(row['id']) is not int or row['id'] in point_ids:
                raise ValueError('Invalid or duplicate shard point ID')
            point_ids.add(row['id'])
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
            flavor = {'status': 'NOT_EVALUATED', 'reason': 'B to Xs gamma disabled' if not bsgamma else 'Scalar screening did not pass'}
            if bsgamma and eligible:
                stage_start = time.monotonic()
                try:
                    from module14.external import bsgamma as run_bsgamma
                    flavor = run_bsgamma(row['scalar'], d9b_probe, cache_dir)
                except Exception as exc:
                    flavor = {'status': 'ERROR', 'error_type': type(exc).__name__, 'reason': str(exc)}
                bsgamma_seconds += time.monotonic() - stage_start
            neutrinos = [evaluate_family(row, config['seed'], ordering, family, limit)
                         for ordering in ('NO', 'IO') for family in range(families)] if eligible else []
            for n in neutrinos:
                key = 'neutrino:' + n['ordering'] + ':' + n['status']
                counts[key] = counts.get(key, 0) + 1
            lfv_results = 'NOT_EVALUATED'
            if lfv and neutrinos:
                lfv_results = []
                for family in neutrinos:
                    item = {'ordering': family['ordering'], 'family': family['family'],
                            'module2_input_sha256': family['input_sha256']}
                    if family['status'] != 'PASS' or family['closure_status'] != 'PASS':
                        item.update(status='NOT_EVALUATED', reason='Neutrino family did not pass closure and perturbativity')
                    else:
                        t = time.monotonic()
                        try:
                            from module14.lfv import evaluate_family as evaluate_lfv
                            item.update(evaluate_lfv(family, lfv_tree))
                        except Exception as exc:
                            item.update(status='ERROR', error_type=type(exc).__name__, reason=str(exc))
                        finally:
                            lfv_seconds += time.monotonic() - t
                    lfv_results.append(item)
            widths = 'NOT_EVALUATED'
            if neutrinos:
                widths = []
                decay_calculator = None
                decay_error = None
                for family in neutrinos:
                    item = {'ordering': family['ordering'], 'family': family['family'],
                            'module2_input_sha256': family['input_sha256']}
                    if family['closure_status'] != 'PASS':
                        item.update(status='NOT_EVALUATED', reason='Neutrino inverse reconstruction did not succeed')
                    else:
                        try:
                            if decay_error is not None:
                                raise RuntimeError(decay_error)
                            if decay_calculator is None:
                                from module14.decays import DecayCalculation
                                try:
                                    decay_calculator = DecayCalculation(row['scalar'], family)
                                except Exception as exc:
                                    decay_error = str(exc)
                                    raise
                            item.update(decay_calculator.evaluate(family))
                        except Exception as exc:
                            item.update(status='ERROR', error_type=type(exc).__name__, reason=str(exc))
                    widths.append(item)
            collider = 'NOT_EVALUATED'
            if higgs and neutrinos:
                stage_start = time.monotonic()
                collider = []
                for family in neutrinos:
                    item = {'ordering': family['ordering'], 'family': family['family'], 'module2_input_sha256': family['input_sha256']}
                    if family['status'] != 'PASS':
                        item.update(status='NOT_EVALUATED', reason='Neutrino family did not pass perturbativity and closure')
                    else:
                        try:
                            from module14.external import higgstools
                            production = None
                            if production_dir:
                                prod_file = Path(production_dir)/(family['input_sha256']+'.json')
                                if prod_file.exists():
                                    production = json.loads(prod_file.read_text())
                            decay = next((w for w in widths if w['ordering'] == family['ordering'] and w['family'] == family['family']), None) if isinstance(widths, list) else None
                            item.update(higgstools(row['scalar'], family, hb_data, hs_data, decay, production))
                        except Exception as exc:
                            item.update(status='ERROR', error_type=type(exc).__name__, reason=str(exc))
                    collider.append(item)
                higgs_seconds += time.monotonic() - stage_start
            key = 'bsgamma:' + flavor['status']
            counts[key] = counts.get(key, 0) + 1
            for stage, data in (('lfv', lfv_results), ('widths', widths), ('higgstools', collider)):
                for ordering in ('NO', 'IO'):
                    statuses = [item['status'] for item in data if item['ordering'] == ordering] if isinstance(data, list) else ['NOT_EVALUATED'] * families
                    for st in statuses:
                        if st == 'PARTIAL': st = 'DIAGNOSTIC_ONLY'
                        key = stage + ':' + ordering + ':' + st
                        counts[key] = counts.get(key, 0) + 1
            result = {'id': row['id'], 'config_sha256': row['config_sha256'], 'scalar_sha256': row['scalar_sha256'], 'scalar_status': status, 'gates': gates,
                      'neutrino': neutrinos if eligible else 'NOT_EVALUATED', 'lfv': lfv_results, 'bsgamma': flavor, 'widths': widths, 'production': 'NOT_EVALUATED', 'higgstools': collider}
            out.write(encode(result) + '\n')
    report = dict(settings, schema='d14-worker-receipt-1', output_sha256=file_sha(tmp),
                  input_count=count, output_count=count, counts=counts, lfv_elapsed_seconds=lfv_seconds, bsgamma_elapsed_seconds=bsgamma_seconds, higgs_elapsed_seconds=higgs_seconds,
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
    w = sub.add_parser('worker'); w.add_argument('--shard', required=True); w.add_argument('--output', required=True); w.add_argument('--receipt', required=True); w.add_argument('--config', required=True); w.add_argument('--families', type=int, default=2); w.add_argument('--perturbativity-limit', type=float, default=math.sqrt(4*math.pi)); w.add_argument('--resume', action='store_true'); w.add_argument('--cache-dir'); w.add_argument('--lfv', action='store_true'); w.add_argument('--lfv-tree', action='store_true'); w.add_argument('--bsgamma', action='store_true'); w.add_argument('--d9b-probe'); w.add_argument('--higgs', action='store_true'); w.add_argument('--hb-data'); w.add_argument('--hs-data'); w.add_argument('--production-dir')
    w.add_argument('--preflight-report')
    a = p.parse_args()
    if a.action == 'generate': generate(json.loads(Path(a.config).read_text()), a.output)
    else: run(a.shard, a.output, a.receipt, json.loads(Path(a.config).read_text()), a.families, a.perturbativity_limit, a.resume, a.cache_dir, a.lfv, a.lfv_tree, a.bsgamma, a.d9b_probe, a.higgs, a.hb_data, a.hs_data, a.production_dir, a.preflight_report)

if __name__ == '__main__': main()
