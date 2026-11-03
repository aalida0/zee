#!/usr/bin/env python3
"""Bounded D10 study; preserves the frozen scalar pipeline and prior evidence.

First recover locally staged inputs with --recover; subsequent runs need only
the tracked snapshot. Run from any directory with the repository Python stack.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import mpmath
import numpy as np
import scipy
import sympy

from module1.d10_certificate import attempt_certificate, singlet_axis_proof, radial_exclusion
from module1.d10_polynomial import evaluate as independent
from module1.d10_search import constrained_search, high_precision_check, verify, polish_high_precision
from module1.potential import Potential, component_value
from module1.scalar_constraints import evaluate, provenance, reconstruct


def canonical_hash(d):
    return hashlib.sha256(json.dumps(d, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def file_hash(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def recover():
    from module9.d7_prepare import design, make_point
    from module9.d7_inputs import seed_input
    records = []
    example = json.loads((ROOT/'module1/example.json').read_text())
    records.append({'role': 'representative', 'input': example,
                    'source': 'module1/example.json', 'source_sha256': file_hash(ROOT/'module1/example.json')})
    identity = 'd7_NO_neutral_near_heavy_07'
    for name, _, physical in design():
        if name == identity:
            regenerated = make_point(seed_input(), name, physical)
            record = regenerated['module2_input']['scalar']['record']
    staged = Path('/home/amine/zee/workspaces/zee-condor-d7/validation/module9/local/staged_local_v1/shards/part_002.jsonl')
    rows = [json.loads(line) for line in staged.read_text().splitlines()]
    row = next(row for row in rows if row['point_id'] == identity)
    assert row['input'] == regenerated
    records.append({'role': 'representative', 'input': record,
                    'source': str(staged), 'source_sha256': file_hash(staged),
                    'staged_nested_input_sha256': row['input_sha256'],
                    'deterministic_regeneration_equal_to_staged_input': True,
                    'generator_sha256': file_hash(ROOT/'module9/d7_prepare.py')})
    staged = Path('/home/amine/zee/work/zee_paper1_F16_exact_SARAH_three_heavy_20261021T143647Z/F16_three_exact_F13_Zee_input_reconstruction.json')
    for name, row in sorted(json.loads(staged.read_text()).items()):
        record = copy.deepcopy(example); record['benchmark_id'] = name
        record['physical'].update({k: row['scalar'][k] for k in record['physical'] if k in row['scalar']})
        # mh1,v are independently checked against the staged spectrum/VEVs.
        assert row['expected_Gate6_vertices']['masses_GeV'][0] == record['physical']['mh1']
        rules = row['sarah_2VEV_lagrangian_rules']
        assert abs(np.hypot(rules['v1'], rules['v2'])-record['physical']['v']) < 1e-10
        p, _, _ = reconstruct(record['physical'])
        discrepancy = max(abs(p[k]-rules[k])/max(1, abs(rules[k])) for k in p)
        assert discrepancy < 1e-10
        records.append({'role': 'representative', 'input': record, 'source': str(staged),
                        'source_sha256': file_hash(staged), 'source_record_sha256': canonical_hash(row),
                        'staged_SARAH_parameter_max_scaled_difference': discrepancy,
                        'staged_scalar_record': row['scalar'], 'staged_SARAH_parameters': rules})
    historical = json.loads((ROOT/'validation/module1/results.json').read_text())
    for identity in ('aligned_decoupling_1500', 'physical_deeper_singlet'):
        row = next(r for r in historical['benchmarks'] if r['benchmark_id'] == identity)
        record = copy.deepcopy(example); record['benchmark_id'] = identity; record['physical'] = row['physical']
        records.append({'role': 'control', 'input': record, 'source': 'validation/module1/results.json',
                        'source_sha256': file_hash(ROOT/'validation/module1/results.json')})
    for row in records:
        row['input_sha256'] = canonical_hash(row['input'])
    path = ROOT/'module1/d10_benchmarks.json'
    path.write_text(json.dumps({'hash_convention': 'SHA256 sorted compact JSON; file hashes are raw bytes',
                                'records': records}, indent=2, allow_nan=False)+'\n')
    print('Recovered', len(records), 'source-bound inputs', flush=True)


def numerical_checks(p, x):
    rng = np.random.default_rng(10510); v = x['v']
    r = np.zeros(10); r[[2, 6]] = [v*np.cos(x['beta']), v*np.sin(x['beta'])]
    configs = [r, np.zeros(10), *[v*rng.normal(size=10) for _ in range(8)]]
    worst = np.zeros(3)
    for r in configs:
        old = Potential(p).evaluate(r); new = independent(r, p)
        worst = np.maximum(worst, [np.max(np.abs(a-b))/v**power for a, b, power in zip(old, new, [4, 3, 2])])
    return {'independent_points': len(configs), 'max_value_difference_over_v4': worst[0],
            'max_gradient_difference_over_v3': worst[1], 'max_hessian_difference_over_v2': worst[2],
            'EW_independent_validation': verify(configs[0], p, x)}


def cubic_deformations(base):
    """Five controlled changes of Mu4 alone; not a new physical survivor scan."""
    x = base['physical']; p, _, _ = reconstruct(x); v = x['v']
    rows = []
    for scale in (0., .5, 1., 1.25, 1.5):
        q = dict(p, Mu4=scale*p['Mu4'])
        ew = np.zeros(10); ew[[2, 6]] = [v*np.cos(x['beta']), v*np.sin(x['beta'])]
        h = independent(ew, q)[2]
        sb, cb = np.sin(x['beta']), np.cos(x['beta'])
        transform = np.array([[-sb, cb, 0], [0, 0, 1]])
        charged = transform@h[np.ix_([0, 4, 8], [0, 4, 8])]@transform.T
        eig = np.linalg.eigvalsh(charged)
        gamma = .5*np.arctan2(max(0., -2*charged[0, 1]), charged[1, 1]-charged[0, 0])
        search = constrained_search(q, x, starts=12)
        best = search['lowest_credible_minimum']
        witness = polish_high_precision(best, q, x) if best and best['delta_over_v4'] < -1e-6 else None
        rows.append({'benchmark_id': 'P2_Mu4_scale_'+str(scale), 'role': 'controlled_deformation',
                     'global_zee_acceptance': None,
                     'status': 'D10_DEEPER_VACUUM_WITNESS' if witness else 'D10_UNKNOWN',
                     'Mu4_scale': scale, 'Mu4_GeV': q['Mu4'], 'effective_gamma_rad': float(gamma),
                     'effective_charged_masses_GeV': np.sqrt(np.maximum(0, eig)).tolist(),
                     'lagrangian_parameters_sha256': canonical_hash(q),
                     'EW_independent_validation': verify(ew, q, x),
                     'search': search, 'verified_deeper_witness': witness,
                     'vacuum_decay_lifetime': 'NOT_EVALUATED'})
        print('Mu4 scale', scale, rows[-1]['status'], flush=True)
    return {'base_input_sha256': canonical_hash(base), 'held_fixed': 'All Lagrangian coefficients except Mu4; neutral EW VEVs unchanged',
            'scalar_survivor_claim': False, 'records': rows}


def test_evidence(local):
    out = {}
    for name in ('focused_tests', 'module1_tests', 'full_tests', 'baseline_failures'):
        path = local/(name+'.log')
        if not path.exists():
            continue
        log = path.read_text()
        out[name] = {'log_sha256': file_hash(path),
                     'tests_run': sum(int(n) for n in re.findall(r'^Ran (\d+) tests?', log, re.M)),
                     'failure_entries': len(re.findall(r'^FAIL:', log, re.M)),
                     'error_entries': len(re.findall(r'^ERROR:', log, re.M)),
                     'summaries': re.findall(r'^(?:OK(?: \([^\n]*\))?|FAILED \([^\n]*\))$', log, re.M)}
    return out


def run():
    local = ROOT/'validation/module1/local/d10'; local.mkdir(parents=True, exist_ok=True)
    (local/'.gitignore').write_text('*\n')
    result = {'schema_version': 'd10-1.0.0', 'global_zee_acceptance': None,
              'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'environment': {'python': platform.python_version(), 'numpy': np.__version__,
                              'scipy': scipy.__version__, 'sympy': sympy.__version__, 'mpmath': mpmath.__version__},
              'frozen_provenance': provenance(), 'records': []}
    for source in json.loads((ROOT/'module1/d10_benchmarks.json').read_text())['records']:
        start = time.monotonic(); d = source['input']; name = d['benchmark_id']
        assert canonical_hash(d) == source['input_sha256']
        print('Running', name, flush=True)
        full = evaluate(d)
        (local/(name+'_module1.json')).write_text(json.dumps(full, indent=2, allow_nan=False)+'\n')
        p = full['lagrangian']['parameters']; x = d['physical']
        proof = attempt_certificate(p, x)
        constrained = constrained_search(p, x)
        candidates = [full['gates']['vacuum'].get('deeper_witness'), constrained['lowest_credible_minimum']]
        witnesses = [verify(w['fields_GeV'], p, x) for w in candidates if w]
        witnesses = [w for w in witnesses if w['credible_stationary_minimum'] and w['delta_over_v4'] < -1e-6]
        witness = min(witnesses, key=lambda w: w['value_over_v4']) if witnesses else None
        if witness:
            analytic = singlet_axis_proof(p, x)
            if analytic:
                r = np.zeros(10); r[8] = np.sqrt(-p['MCS2']/p['LambdaC'])
                witness = verify(r, p, x)
                witness['exact_singlet_axis_proof'] = analytic
            witness['independent_80digit'] = high_precision_check(witness['fields_GeV'], p, x)
            assert float(witness['independent_80digit']['delta_GeV4']) < -1e-6*x['v']**4
        assert not (witness and proof['certified'])
        status = 'D10_DEEPER_VACUUM_WITNESS' if witness else 'D10_GLOBAL_CERTIFIED' if proof['certified'] else 'D10_UNKNOWN'
        out = {'benchmark_id': name, 'role': source['role'], 'input_sha256': source['input_sha256'],
               'status': status, 'global_zee_acceptance': None, 'lagrangian_parameters': p,
               'lagrangian_parameters_sha256': canonical_hash(p),
               'scalar_gates': {k: {a: g[a] for a in ('status', 'assessment')} for k, g in full['gates'].items()},
               'bfb_certificate': full['gates']['bfb'].get('certificate'),
               'unitarity_max_abs_eigenvalue': full['gates']['unitarity'].get('max_abs_eigenvalue'),
               'STU': full['gates']['ewpo'].get('STU'), 'certificate_attempt': proof,
               'rigorous_radial_exclusion': radial_exclusion(p, x),
               'independent_checks': numerical_checks(p, x), 'module1_vacuum': full['gates']['vacuum'],
               'independent_constrained_search': constrained, 'verified_deeper_witness': witness,
               'charged_mixing': {'Mu4_GeV': p['Mu4'], 'gamma_rad': x['gamma'],
                                  'mass_gap_GeV': x['mH2']-x['mH1'],
                                  'mass_squared_gap_GeV2': x['mH2']**2-x['mH1']**2},
               'vacuum_decay_lifetime': 'NOT_EVALUATED', 'elapsed_seconds': time.monotonic()-start}
        result['records'].append(out)
        print(name, status, 'seconds', round(out['elapsed_seconds'], 1), flush=True)
    result['controlled_cubic_study'] = cubic_deformations(json.loads((ROOT/'module1/example.json').read_text()))
    result['source_sha256'] = {str(p.relative_to(ROOT)): file_hash(p) for p in [
        *sorted((ROOT/'module1').glob('*.py')), ROOT/'module1/d10_benchmarks.json',
        ROOT/'scripts/zee_d10_vacuum_global.py', ROOT/'models/SARAH/ZeeTypeII/ZeeTypeII.m',
        ROOT/'tests/test_module1_d10_global.py', ROOT/'module1/D10_VACUUM_GLOBAL_AUDIT.md',
        ROOT/'module9/d7_prepare.py', ROOT/'module9/d7_inputs.py']}
    result['test_evidence'] = test_evidence(local)
    path = ROOT/'validation/module1/d10_vacuum_global.json'
    path.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(path, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recover', action='store_true', help='Recover original staged local records before running')
    args = parser.parse_args()
    if args.recover:
        recover()
    run()
