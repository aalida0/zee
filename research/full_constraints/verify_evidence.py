#!/usr/bin/env python3
"""Verify saved provenance and identities; never execute matching, rates or scans."""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def close(a, b, tolerance=2e-14):
    require(math.isfinite(a) and math.isfinite(b) and abs(a-b) <= tolerance,
            f'Saved identity mismatch: {a}, {b}')


def verify(check_external=False, rate_workspace=None):
    manifest = load(HERE/'SOURCE_MANIFEST.json')
    for relative, digest in manifest['repository_inputs'].items():
        require(sha(ROOT/relative) == digest, 'Changed frozen input: '+relative)
    external_count = 0
    if check_external:
        for item in manifest['public_sources']:
            require(sha(Path(item['local_hint'])) == item['sha256'],
                    'Changed public source: '+item['id'])
            external_count += 1
    reuse_count = 0
    if rate_workspace:
        for relative, item in manifest['reuse']['files'].items():
            require(sha(rate_workspace/relative) == item['sha256'],
                    'Changed prior evidence: '+relative)
            reuse_count += 1
        prior = load(rate_workspace/'research/bsgamma_rate_validation/m2026_legacy_results.json')
        require(prior['responses'] == load(HERE/'REUSED_RATE_RESPONSE.json')['responses'],
                'Copied legacy response differs')

    cards = load(ROOT/'module1/d10_benchmarks.json')['records']
    cards = {r['input']['benchmark_id']: r for r in cards}
    d12 = load(ROOT/'validation/module12/d12_benchmarks.json')['B_to_Xs_gamma']
    d9b = load(ROOT/'validation/module5/d9b_superiso_repair.json')
    require(d12['previous_evidence_sha256'] == sha(ROOT/'validation/module5/d9b_superiso_repair.json'),
            'D12 does not bind frozen D9B receipt')
    require(d12['patch_sha256'] == d9b['patch_sha256'], 'Different rate patch')
    close(d12['baseline']['SM_BR'], d9b['baseline']['SM_BR'])
    require(d9b['max_matching_residual'] < 6.67e-16, 'Matching evidence residual changed')
    require(d9b['max_rate_residual'] < 5.43e-20, 'Rate evidence residual changed')
    for value in d9b['endpoint_residuals'].values():
        close(value, 0.)

    rows = {}
    for name in ('d7_NO_neutral_near_heavy_07', 'F13_heavy_0001330'):
        card = cards[name]['input']
        digest = hashlib.sha256(json.dumps(card, sort_keys=True, separators=(',', ':'),
                                          allow_nan=False).encode()).hexdigest()
        row = d12['rows'][name]
        require(digest == cards[name]['input_sha256'] == row['scalar_sha256'],
                'Original scalar card binding differs: '+name)
        p = card['physical']
        close(row['masses_GeV'][0], p['mH1'])
        close(row['masses_GeV'][1], p['mH2'])
        close(row['tanbeta'], math.tan(p['beta']))
        close(row['gamma'], p['gamma'])
        close(sum(row['weights']), 1.)
        close(row['weights'][0], math.cos(p['gamma'])**2)
        close(row['weights'][1], math.sin(p['gamma'])**2)
        for key, total in row['ordinary_total'].items():
            close(total, sum(w*r[key] for w, r in zip(row['weights'], row['ordinary_parts'])))
        close(row['family_repeat_absolute_difference'], 0.)
        require(row['BR_legacy_NLO'] > 0, 'Invalid saved rate')
        rows[name] = {k: row[k] for k in ('masses_GeV', 'tanbeta', 'gamma',
                                         'ordinary_total', 'BR_legacy_NLO', 'scalar_sha256')}
        rows[name]['one_state_controls_reused'] = {
            str(i): d12['controls'][name+f'_single_{i}']['BR_legacy_NLO'] for i in (1, 2)}
    return {
        'audit_status': 'SAVED_EVIDENCE_INTEGRITY_PASS',
        'physics_gate': 'B_FULL_RATE_BLOCKED', 'physical_bsgamma': 'UNKNOWN',
        'exclusion': None, 'theory_sigma': None, 'global_acceptance': None,
        'new_matching_executions': 0, 'new_rate_executions': 0, 'new_parameter_points': 0,
        'repository_inputs_checked': len(manifest['repository_inputs']),
        'public_source_artifacts_checked': external_count,
        'prior_evidence_files_checked': reuse_count,
        'source_manifest_sha256': sha(HERE/'SOURCE_MANIFEST.json'),
        'verifier_sha256': sha(Path(__file__)),
        'archived_SM_BR_D12_prescription': d12['baseline']['SM_BR'],
        'reused_benchmarks': rows,
        'independent_physical_rate_agreement': 'NOT_ESTABLISHED',
        'uncertainty_and_confidence_validation': 'NOT_ESTABLISHED',
        'note': 'Arithmetic and provenance replay; prior physics checks are reused, not rerun.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-external', action='store_true',
                        help='Also verify inspected source bytes at manifest local hints')
    parser.add_argument('--rate-workspace', type=Path,
                        help='Read-only checkout containing the pinned separate-branch evidence')
    parser.add_argument('--output', type=Path, help='Create a new report; existing files are refused')
    args = parser.parse_args()
    report = verify(args.check_external, args.rate_workspace)
    payload = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+'\n'
    if args.output:
        with args.output.open('x') as stream:
            stream.write(payload)
    print(json.dumps({k: v for k, v in report.items() if k != 'reused_benchmarks'}, sort_keys=True))
