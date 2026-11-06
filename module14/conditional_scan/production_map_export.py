"""Validate actual native artifacts and deterministically export the finite map."""
import argparse
import csv
import json
import math
from pathlib import Path

from module8.real_run_validation import lha_values, run_settings
from module14.scan import digest, file_sha
from .candidate_export import BASE, ROOT, CERTIFIED, LIGHT, audit, require
from .production_map_run import (LOCAL, WORK, MAP_IDS, BENCHMARK_IDS,
                                 runtime_gate, load, save)
from .production_map_validate import validate_one
from .targeted_validation import validate_one as validate_original, expected_parameters
from .workflow import cascade

LIMITATIONS = {
    'physical_bsgamma': 'UNKNOWN', 'global_acceptance': None,
    'nominal_bsgamma': 'published 2026 linear LO-NP diagnostic only',
    'lfv': 'PARTIAL: original omitted amplitudes retained',
    'HiggsTools': 'INCOMPLETE: original gates unchanged; no rerun',
    'decays': 'complete on-shell tree two-body only',
    'scale_uncertainty_pb': None, 'pdf_uncertainty_pb': None,
    'decay_theory_uncertainty': None, 'detector_constraints': 'NOT_EVALUATED',
    'scale_sensitivity': 'NOT_EVALUATED',
}


def ratio(a, b):
    value = a['sigma_pb']/b['sigma_pb']
    # Quadrature assumes uncorrelated integration estimates; covariance unmeasured.
    error = value*math.hypot(a['integration_error_pb']/a['sigma_pb'],
                             b['integration_error_pb']/b['sigma_pb'])
    return value, error


def assemble(dataset):
    original = audit(dataset)  # all 900 family records, original gates and decays
    full = load(dataset)['rows']
    by_id = {i: [r for r in full if r['id'] == i] for i in MAP_IDS}
    runtime = runtime_gate()
    mapping = load(WORK/'mapping.json'); matrix = load(WORK/'matrix_checks.json')
    require(mapping['status'] == 'D14D_NATIVE_CARD_MAPPING_PASS' and len(mapping['cases']) == 64,
            'Incomplete mapping')
    require(matrix['status'] == 'D14D_INDEPENDENT_MG_MATRIX_PASS' and len(matrix['rows']) == 320,
            'Incomplete independent matrix coverage')
    for evidence in (mapping, matrix):
        for name, want in evidence['source_sha256'].items():
            require(file_sha(ROOT/name) == want, 'Physics source changed: '+name)
    for i in MAP_IDS:
        gamma = by_id[i][0]['input_card']['physical']['gamma']
        control = [r for r in matrix['rows'] if r['id'] == i and r['gamma_control'] == gamma]
        require(len(control) == 4 and len({(r['ordering'], r['family']) for r in control}) == 4,
                'Missing original-family amplitude')
        m2 = [r['MG_m2']['minus'] for r in control]
        require(max(m2)/min(m2)-1 < 1e-13, 'Family-dependent production')
    require(file_sha(LOCAL/'d14c/validated_production.json') ==
            load(BASE/'candidate_followup.json')['production_evidence_sha256'],
            'Immutable D14C evidence differs from committed provenance')
    original_evidence = load(LOCAL/'d14c/validated_production.json')
    rates = []
    for energy, ids in ((13, MAP_IDS), (14, BENCHMARK_IDS)):
        for i in ids:
            if energy == 13 and i in BENCHMARK_IDS:
                r = validate_original(i, by_id[i])
                require(r == next(x for x in original_evidence['rates'] if x['id'] == i),
                        'Original production changed')
                rates.append(dict(r, origin='D14C_REUSED_UNCHANGED'))
            elif (WORK/f'receipt_{i}_{energy}TeV/receipt.json').exists():
                rates.append(dict(validate_one(i, energy, by_id[i]), origin='D14D_ACTUAL_INTEGRATION'))
            else:
                rates.append({'id': i, 'energy_TeV': energy, 'status': 'NOT_EVALUATED',
                              'sigma_pb': None, 'integration_error_pb': None})
    rate_index = {(r['id'], r['energy_TeV']): r for r in rates}
    candidates = {r['id']: r for r in original['tables'][CERTIFIED]}
    require(set(candidates) == set(MAP_IDS), 'Shortlist changed')
    families = []
    for energy, ids in ((13, MAP_IDS), (14, BENCHMARK_IDS)):
        for i in ids:
            for row in by_id[i]:
                n = row['neutrino']; physical = row['input_card']['physical']
                case = next(c for c in mapping['cases'] if c['module2_input_sha256'] == n['input_sha256'])
                card = LOCAL/case['card']
                require(file_sha(card) == case['card_sha256'] and
                        file_sha(card.with_suffix('.json')) == case['native_input_sha256'] and
                        lha_values(card.read_text()) == expected_parameters(row), 'Family card mismatch')
                c = cascade(row['input_card'], n, row['widths'])
                require(c['br_status'] == 'PASS', 'Incomplete decay BR')
                f = next(f for f in candidates[i]['families'] if f['module2_input_sha256'] == n['input_sha256'])
                r = rate_index[i, energy]; sigma = r['sigma_pb']; br = c['BR_H2_H1Z']
                h1 = row['widths']['mothers']['H1']
                h1total = h1['total']['total_width_GeV']
                binding = {'scalar_sha256': row['scalar_sha256'],
                           'module2_input_sha256': n['input_sha256'],
                           'yukawa_sha256': {k: digest(n[k]) for k in ('F', 'D', 'Ye', 'Ye2')},
                           'mapped_card_sha256': case['card_sha256'],
                           'receipt_sha256': r.get('receipt_sha256'), 'energy_TeV': energy}
                families.append({
                    'id': i, 'ordering': n['ordering'], 'family': n['family'],
                    **binding, 'binding_sha256': digest(binding), 'mH1_GeV': physical['mH1'],
                    'mH2_GeV': physical['mH2'], 'tanbeta': math.tan(physical['beta']),
                    'gamma_rad': physical['gamma'], 'vacuum': 'PASS',
                    'nominal_bsgamma': 'APPROX_COMPATIBLE', 'production_status': r['status'],
                    **{k: f[k] for k in ('neutrino_status', 'closure_status', 'width_status')},
                    'decay_scope': 'complete_on_shell_tree_two_body_only',
                    'detector_constraints': 'NOT_EVALUATED',
                    'sigma_pb': sigma, 'integration_error_pb': r['integration_error_pb'],
                    'BR_H2_H1Z': br, 'H2_total_width_GeV': c['total_width_GeV'],
                    'H1_total_width_GeV': h1total,
                    'H1_decay_BR_separate': {x['channel']: x['width_GeV']/h1total for x in h1['channels']},
                    'decay_record_sha256': f['decay_record_sha256'],
                    'decay_source_sha256': f['decay_source_sha256'], 'sm_card_sha256': f['sm_card_sha256'],
                    'sigma_times_BR_pb': None if sigma is None else sigma*br,
                    'integration_error_on_sigma_times_BR_pb': None if sigma is None else r['integration_error_pb']*br,
                    'physical_bsgamma': 'UNKNOWN', 'global_acceptance': None,
                    'scale_uncertainty_pb': None, 'pdf_uncertainty_pb': None,
                    'decay_theory_uncertainty': None, 'rank_at_energy': None,
                    'lfv_coverage': f['lfv_coverage'], 'higgstools_coverage': f['higgstools_coverage'],
                })
    for energy in (13, 14):
        ranked = sorted((f for f in families if f['energy_TeV'] == energy and f['sigma_pb'] is not None),
                        key=lambda f: (-f['sigma_times_BR_pb'], f['id'], f['ordering'], f['family']))
        for rank, f in enumerate(ranked, 1):
            f['rank_at_energy'] = rank
    comparisons = []
    for i in BENCHMARK_IDS:
        a, b = rate_index[i, 14], rate_index[i, 13]
        value, error = (None, None) if a['sigma_pb'] is None else ratio(a, b)
        if a['sigma_pb'] is not None:
            old = LOCAL/'d14c'/f'receipt_{i}'
            new = WORK/f'receipt_{i}_14TeV'
            require(lha_values((old/'param_card.dat').read_text()) ==
                    lha_values((new/'param_card.dat').read_text()), '13/14 full model mismatch')
            settings13 = run_settings((old/'run_card.dat').read_text())
            settings14 = run_settings((new/'run_card.dat').read_text())
            for key in ('ebeam1', 'ebeam2'):
                require(float(settings13.pop(key)) == 6500 and float(settings14.pop(key)) == 7000,
                        '13/14 beam mismatch')
            require(settings13 == settings14, '13/14 non-beam run settings mismatch')
        comparisons.append({'id': i, 'sigma14_over_sigma13': value,
                            'full_model_and_nonbeam_settings_identical': value is not None,
                            'integration_error_uncorrelated_quadrature': error,
                            'integration_covariance': None,
                            'error_assumption': 'uncorrelated estimates; same seed recipe, covariance not measured',
                            'scope': 'spectrum/process specific; no universal energy factor'})
    complete13 = all(rate_index[i, 13]['sigma_pb'] is not None for i in MAP_IDS)
    complete14 = all(rate_index[i, 14]['sigma_pb'] is not None for i in BENCHMARK_IDS)
    return {'schema': 'd14d-production-map-1',
            'production_13TeV_gate': 'PRODUCTION_MAP_13TEV_COMPLETE' if complete13 else 'PRODUCTION_MAP_PARTIAL',
            'production_14TeV_gate': 'PRODUCTION_14TEV_PILOT_COMPLETE' if complete14 else 'PRODUCTION_14TEV_PILOT_PARTIAL',
            'dataset_sha256': file_sha(dataset), 'source_sha256': {
                str(p.relative_to(ROOT)): file_sha(p) for p in
                (Path(__file__), BASE/'production_map_run.py', BASE/'production_map_validate.py')},
            'original_production_evidence_sha256': file_sha(LOCAL/'d14c/validated_production.json'),
            'runtime': runtime, 'mapping': mapping, 'mapping_sha256': file_sha(WORK/'mapping.json'),
            'matrix_checks': matrix, 'matrix_checks_sha256': file_sha(WORK/'matrix_checks.json'),
            'rates': rates, 'families': families, 'energy_comparisons': comparisons,
            'limitations': LIMITATIONS, 'global_acceptance': None,
            'unresolved_subTeV_opportunities': original['tables'][LIGHT],
            'conditional_scalar_scatter': [
                {'id': r['id'], 'mH1_GeV': r['input_card']['physical']['mH1'],
                 'mH2_GeV': r['input_card']['physical']['mH2'], 'vacuum': r['gates']['vacuum']['assessment'],
                 'nominal_bsgamma': r['flavor']['bsg_nominal_classification'],
                 'physical_bsgamma': 'UNKNOWN', 'global_acceptance': None}
                for r in load(BASE/'remote_conditional_summary.json')['points'].values()]}


def export(report, output):
    output.mkdir(parents=True, exist_ok=True)
    save(output/'production_map_13_14.json', report)
    for energy in (13, 14):
        rows = sorted([f for f in report['families'] if f['energy_TeV'] == energy],
                      key=lambda f: (f['rank_at_energy'] is None, f['rank_at_energy'] or 0,
                                     f['id'], f['ordering'], f['family']))
        flat = [{k: json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else
                 'null' if v is None else v for k, v in r.items()} for r in rows]
        with (output/f'production_map_{energy}TeV_families.csv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=sorted(flat[0]), lineterminator='\n')
            writer.writeheader(); writer.writerows(flat)
    if 'rates' in report:
        scalars = []
        for rate in report['rates']:
            members = [f for f in report['families'] if (f['id'], f['energy_TeV']) ==
                       (rate['id'], rate['energy_TeV'])]
            first = members[0]
            measured = [f['sigma_times_BR_pb'] for f in members if f['sigma_times_BR_pb'] is not None]
            scalars.append({**{k: rate.get(k) for k in ('id', 'energy_TeV', 'status', 'sigma_pb',
                'integration_error_pb', 'integration_samples', 'pdf', 'order', 'scale_scheme', 'receipt_sha256')},
                **{k: first[k] for k in ('mH1_GeV', 'mH2_GeV', 'tanbeta', 'gamma_rad')},
                'sigma_times_BR_min_pb': min(measured) if measured else None,
                'sigma_times_BR_max_pb': max(measured) if measured else None,
                'vacuum': 'PASS', 'nominal_bsgamma': 'APPROX_COMPATIBLE',
                'physical_bsgamma': 'UNKNOWN', 'global_acceptance': None,
                'lfv': 'PARTIAL', 'HiggsTools': 'INCOMPLETE_NOT_RERUN',
                'decay_scope': 'complete_on_shell_tree_two_body_only',
                'scale_uncertainty_pb': None, 'pdf_uncertainty_pb': None,
                'decay_theory_uncertainty': None, 'detector_constraints': 'NOT_EVALUATED'})
        scalars.sort(key=lambda r: (r['energy_TeV'], r['sigma_pb'] is None,
                                    -(r['sigma_times_BR_max_pb'] or 0), r['id']))
        with (output/'production_map_scalar_rates.csv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=sorted(scalars[0]), lineterminator='\n')
            writer.writeheader()
            writer.writerows({k: 'null' if v is None else v for k, v in r.items()} for r in scalars)
    manifest = {p.name: file_sha(p) for p in sorted(output.glob('production_map_*')) if p.is_file()
                and p.name != 'production_map_hashes.json'}
    save(output/'production_map_hashes.json', manifest)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    require(not a.output.exists(), 'Use fresh output directory')
    report = assemble(a.dataset)
    export(report, a.output)
    print(report['production_13TeV_gate'], report['production_14TeV_gate'], flush=True)


if __name__ == '__main__':
    main()
