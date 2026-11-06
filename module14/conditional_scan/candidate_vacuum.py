"""Bounded D10 diagnostics for exactly the three predeclared light points."""
import argparse
import json
from pathlib import Path

from module1.d10_certificate import attempt_certificate, radial_exclusion
from module1.d10_search import constrained_search, polish_high_precision
from module1.scalar_constraints import reconstruct
from module14.scan import digest, file_sha, runtime_info
from .candidate_export import BASE, LIGHT, ROOT, VACUUM_IDS, require
from .workflow import load


def diagnose(candidate, starts=192):
    point_id = candidate['id']
    require(point_id in VACUUM_IDS, 'Only predeclared vacuum points may be searched')
    require(type(starts) is int and 16 <= starts <= 192, 'Bounded starts must be 16..192')
    x = candidate['physical']
    p, _, reconstruction = reconstruct(x)
    require(reconstruction['assessment'] == 'PASS', 'Reconstruction not validated')
    certificate = attempt_certificate(p, x)
    result = constrained_search(p, x, seed=20261106+point_id, starts=starts)
    best = result['lowest_credible_minimum']
    witness = None
    if best is not None and best['delta_over_v4'] < -1e-6:
        witness = polish_high_precision(best, p, x)
    require(not (certificate['certified'] and witness), 'Conflicting certificate and deeper witness')
    return {'id': point_id, 'scalar_sha256': candidate['scalar_sha256'],
            'lagrangian_binary64_sha256': digest(p), 'lagrangian_binary64': p,
            'original_gate_sha256': candidate['gates']['vacuum']['details_sha256'],
            'original_assessment': candidate['gates']['vacuum']['assessment'],
            'assessment': 'FAIL' if witness else 'PASS' if certificate['certified'] else 'UNKNOWN',
            'certificate_attempt': certificate, 'bounded_search': result,
            'verified_deeper_stationary_witness': witness,
            'outer_exclusion': radial_exclusion(p, x),
            'meaning': 'Finite search absence does not prove globality. PASS requires the established exact D10 certificate; FAIL requires an independently polished lower stationary minimum.',
            'lifetime': 'NOT_EVALUATED', 'loop_effective_potential': 'NOT_EVALUATED',
            'global_acceptance': None}


def run(report, output, starts=192):
    require(not output.exists(), 'Use a fresh vacuum output')
    candidates = report['tables'][LIGHT]
    require(set(VACUUM_IDS).issubset({c['id'] for c in candidates}), 'Predeclared points missing')
    rows = []
    for candidate in candidates:
        if candidate['id'] in VACUUM_IDS:
            row = diagnose(candidate, starts)
            print(candidate['id'], row['assessment'], flush=True)
        else:
            row = {'id': candidate['id'], 'scalar_sha256': candidate['scalar_sha256'],
                   'assessment': 'UNKNOWN', 'search_status': 'NOT_EVALUATED',
                   'original_gate_sha256': candidate['gates']['vacuum']['details_sha256'],
                   'original_vacuum_gate': candidate['original_vacuum_gate'],
                   'reason': 'Triage only; outside the three predeclared bounded searches',
                   'global_acceptance': None}
        rows.append(row)
    source_paths = [Path(__file__), *(ROOT/('module1/'+name) for name in
        ('d10_certificate.py', 'd10_polynomial.py', 'd10_search.py', 'potential.py', 'scalar_constraints.py'))]
    evidence = {'schema': 'd14c-bounded-vacuum-1', 'dataset_sha256': report['dataset_sha256'],
                'rows': rows, 'runtime': runtime_info(),
                'source_sha256': {str(p.relative_to(ROOT)): file_sha(p) for p in source_paths},
                'original_gates_mutated': False, 'physical_bsgamma': 'UNKNOWN', 'global_acceptance': None}
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False)+'\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidates', type=Path, default=BASE/'candidate_followup.json')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--starts', type=int, default=192)
    a = p.parse_args()
    run(load(a.candidates), a.output, a.starts)


if __name__ == '__main__':
    main()
