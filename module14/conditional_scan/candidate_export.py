"""Finite D14C export from the already verified 225-point dataset; no workers."""
import argparse
from collections import Counter, defaultdict
import csv
import json
import math
from pathlib import Path

from module14.scan import digest, file_sha
from .workflow import cascade, load

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'module14/conditional_scan'
PRODUCTION_IDS = (15591, 2264, 15673)
VACUUM_IDS = (3582, 6850, 13512)
CERTIFIED = 'CERTIFIED_VACUUM_APPROX_BSG_16'
LIGHT = 'SUBTEV_UNKNOWN_VACUUM_APPROX_BSG_6'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def shortlist(summary):
    """Derive intersections, never use a stored count as the selection."""
    points = summary['points']
    groups = {CERTIFIED: [], LIGHT: []}
    counts = {'points': len(points), 'vacuum': Counter(), 'nominal_bsgamma': Counter()}
    for key, row in sorted(points.items(), key=lambda item: int(item[0])):
        require(str(row['id']) == key, 'Point ID mismatch')
        require(digest(row['input_card']) == row['flavor']['scalar_sha256'], 'Scalar card mismatch')
        status = row['gates']['vacuum']['assessment']
        flavor = row['flavor']['bsg_nominal_classification']
        counts['vacuum'][status] += 1
        counts['nominal_bsgamma'][flavor] += 1
        require(row['globally_allowed'] is None and
                row['flavor']['bsg_physical_classification'] == 'UNKNOWN', 'Invalid acceptance')
        if flavor == 'APPROX_COMPATIBLE':
            if status == 'PASS':
                groups[CERTIFIED].append(row['id'])
            if status == 'UNKNOWN' and row['input_card']['physical']['mH2'] < 1000:
                groups[LIGHT].append(row['id'])
    counts['intersections'] = {name: len(ids) for name, ids in groups.items()}
    counts['certified_subtev'] = sum(points[str(i)]['input_card']['physical']['mH2'] < 1000
                                      for i in groups[CERTIFIED])
    return groups, counts


def verify_family(row, compact):
    """Recheck original identities and complete decay ledger, without refitting."""
    n, w, scalar = row['neutrino'], row['widths'], row['input_card']
    require(row['scalar_sha256'] == digest(scalar), 'Scalar hash mismatch')
    require(digest(n['input']) == n['input_sha256'] == compact['input_sha256'], 'Family input mismatch')
    require(digest(n['input']['target_eV']) == n['target_sha256'] == compact['target_sha256'],
            'Neutrino target mismatch')
    require(n['input']['scalar']['record'] == scalar and
            n['input']['scalar']['sha256'] == row['scalar_sha256'], 'Family scalar binding mismatch')
    provenance = n['module2_provenance']
    require(provenance['input_sha256'] == n['input_sha256'] and
            provenance['scalar']['sha256'] == row['scalar_sha256'], 'Module2 provenance mismatch')
    for name, want in provenance['code_sha256'].items():
        require(file_sha(ROOT/name) == want, 'Neutrino source changed: '+name)
    c = cascade(scalar, n, w)
    require(c['br_status'] == 'PASS' and math.isclose(c['BR_H2_H1Z'], compact['cascade_BR'],
            rel_tol=2e-13, abs_tol=1e-15), 'Compact decay mismatch')
    for field, stored in [('status', 'neutrino_status'), ('closure_status', 'closure_status')]:
        require(n[field] == compact[stored], 'Neutrino status mismatch')
    require(row['lfv']['status'] == compact['lfv_status'] and
            row['higgstools']['status'] == compact['higgstools_status'] and
            row['production']['status'] == compact['production_status'], 'Coverage mismatch')
    require(row['production']['status'] == 'NOT_EVALUATED' and row['yield_proxy_pb'] is None,
            'Unexpected original production')
    return dict(compact, module2_input_sha256=n['input_sha256'],
                seed_sha256=n['seed_sha256'], target_spec=n['target_spec'],
                yukawa_sha256={k: digest(n[k]) for k in ('F', 'D', 'Ye', 'Ye2')},
                module2_provenance=provenance, family_record_sha256=digest(n),
                decay_record_sha256=digest(w), decay_source_sha256=w['source_sha256'],
                sm_card_sha256=w['sm_card_sha256'],
                tree_two_body_total_width_GeV=c['total_width_GeV'],
                BR_scope=c['scope'], lfv_coverage={k: row['lfv'][k] for k in
                    ('status', 'complete_lfv', 'missing_contributions', 'comparison_status')},
                higgstools_coverage={k: row['higgstools'][k] for k in
                    ('status', 'charged_searches', 'heavy_neutral')},
                production=None, yield_proxy_pb=None, global_acceptance=None, physical_bsgamma='UNKNOWN')


def audit(dataset_path, summary_path=BASE/'remote_conditional_summary.json'):
    summary = load(summary_path)
    require(file_sha(dataset_path) == summary['dataset_sha256'], 'Immutable dataset SHA256 mismatch')
    data = load(dataset_path)
    require(data['collection'] == summary['collection'] and
            data['collection']['status'] == 'COMPLETE' and data['collection']['missing_points'] == 0,
            'Original collection mismatch')
    groups, counts = shortlist(summary)
    by_id = defaultdict(list)
    for row in data['rows']:
        by_id[row['id']].append(row)
    require(set(by_id) == {int(k) for k in summary['points']}, 'Dataset point IDs mismatch')
    tables = {name: [] for name in groups}
    selected = set(sum(groups.values(), []))
    for point_id, rows in sorted(by_id.items()):
        point = summary['points'][str(point_id)]
        require(len(rows) == 4 and {(r['neutrino']['ordering'], r['neutrino']['family']) for r in rows}
                == {('NO', 0), ('NO', 1), ('IO', 0), ('IO', 1)}, 'Missing/duplicate family')
        compact = {(f['ordering'], f['family']): f for f in point['families']}
        require(len(compact) == 4, 'Compact family inventory mismatch')
        families = []
        for row in rows:
            require(row['input_card'] == point['input_card'], 'Dataset scalar card mismatch')
            require(all(digest(row['gates'][k]) == v['details_sha256'] and
                        row['gates'][k]['assessment'] == v['assessment']
                        for k, v in point['gates'].items()), 'Gate detail mismatch')
            require(all(row['flavor'][k] == v for k, v in point['flavor'].items()), 'Flavor record mismatch')
            families.append(verify_family(row, compact[row['neutrino']['ordering'], row['neutrino']['family']]))
        if point_id in selected:
            x = point['input_card']['physical']
            candidate = {'id': point_id, 'arm': point['arm'], 'input_card': point['input_card'],
                'scalar_sha256': digest(point['input_card']), 'physical': x,
                'tanbeta': math.tan(x['beta']), 'gates': point['gates'],
                'original_vacuum_gate': rows[0]['gates']['vacuum'],
                'original_witness_search': 'NOT_EVALUATED: D14 worker only attempted sufficient certificate',
                'conditional_pull': point['flavor']['conditional_pull'],
                'bsg_nominal_classification': point['flavor']['bsg_nominal_classification'],
                'physical_bsgamma': 'UNKNOWN', 'global_acceptance': None,
                'production_status': 'PRODUCTION_PENDING', 'families': families}
            for name, ids in groups.items():
                if point_id in ids:
                    tables[name].append(candidate)
    return {'schema': 'd14c-targeted-followup-1', 'status': 'TARGETED_PRODUCTION_PENDING',
            'dataset_path': summary['dataset_path'], 'dataset_sha256': summary['dataset_sha256'],
            'summary_sha256': file_sha(summary_path), 'original_collection': data['collection'],
            'counts': counts, 'verified_family_records': len(data['rows']),
            'tables': tables, 'production_point_order': PRODUCTION_IDS, 'vacuum_point_order': VACUUM_IDS,
            'physical_bsgamma': 'UNKNOWN', 'global_acceptance': None,
            'source_sha256': {str(p.relative_to(ROOT)): file_sha(p) for p in
                (Path(__file__), ROOT/'module14/conditional_scan/workflow.py')}}


def write_tables(report, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for name, rows in report['tables'].items():
        (output/(name+'.json')).write_text(json.dumps(rows, indent=2, sort_keys=True, allow_nan=False)+'\n')
        flat = []
        for row in rows:
            for f in row['families']:
                flat.append({'id': row['id'], 'scalar_sha256': row['scalar_sha256'],
                    **{k: row['physical'][k] for k in ('mH1', 'mH2', 'mh1', 'mh2', 'ma', 'gamma')},
                    'tanbeta': row['tanbeta'], 'conditional_pull': row['conditional_pull'],
                    'vacuum': row['gates']['vacuum']['assessment'],
                    **{k: f[k] for k in ('ordering', 'family', 'module2_input_sha256', 'cascade_BR',
                        'closure_status', 'neutrino_status', 'lfv_status', 'higgstools_status')},
                    'yukawa_sha256': json.dumps(f['yukawa_sha256'], sort_keys=True),
                    'production_status': f['production_status'], 'tree_two_body_only': True,
                    'sigma_pb': None if not f['production'] else f['production']['sigma_pb'],
                    'integration_error_pb': None if not f['production'] else f['production']['integration_error_pb'],
                    'yield_proxy_pb': f['yield_proxy_pb'], 'rank': f['rank'],
                    'physical_bsgamma': 'UNKNOWN', 'global_acceptance': 'null'})
        with (output/(name+'.csv')).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(flat[0]), lineterminator='\n')
            writer.writeheader(); writer.writerows(flat)
    (output/'candidate_followup.json').write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+'\n')


def attach_evidence(report, dataset_path, production_path=None, vacuum_path=None):
    """Attach separate verified follow-up evidence; never mutate original gates."""
    if vacuum_path:
        vacuum = load(vacuum_path)
        require(vacuum['dataset_sha256'] == report['dataset_sha256'], 'Vacuum dataset mismatch')
        for name, want in vacuum['source_sha256'].items():
            require(file_sha(ROOT/name) == want, 'Vacuum diagnostic source mismatch')
        candidates = {r['id']: r for r in report['tables'][LIGHT]}
        require({r['id'] for r in vacuum['rows']} == set(candidates), 'Vacuum diagnostic inventory mismatch')
        for row in vacuum['rows']:
            candidate = candidates[row['id']]
            require(row['scalar_sha256'] == candidate['scalar_sha256'] and row['assessment'] in ('PASS', 'FAIL', 'UNKNOWN'),
                    'Vacuum diagnostic point mismatch')
            if row['assessment'] == 'PASS':
                require(row.get('certificate_attempt', {}).get('certified') is True, 'Uncertified vacuum PASS')
            if row['assessment'] == 'FAIL':
                w = row.get('verified_deeper_stationary_witness')
                require(w and w['credible_stationary_minimum'] and w['delta_over_v4'] < -1e-6,
                        'Unverified instability witness')
            candidate['separate_vacuum_diagnostic'] = row
        report['vacuum_diagnostic_sha256'] = file_sha(vacuum_path)
    if production_path:
        from .targeted_validation import validate_one
        from .workflow import production
        evidence = load(production_path)
        require(evidence['status'] == 'TARGETED_PRODUCTION_EVIDENCE_AVAILABLE' and
                evidence['dataset_sha256'] == report['dataset_sha256'], 'Production evidence mismatch')
        require(file_sha(ROOT/'module14/conditional_scan/targeted_validation.py') ==
                evidence['validation_source_sha256'], 'Production validator changed')
        full = load(dataset_path)['rows']
        candidates = {r['id']: r for r in report['tables'][CERTIFIED]}
        rates = {r['id']: r for r in evidence['rates']}
        require(bool(rates) and set(rates).issubset(PRODUCTION_IDS), 'Production scope mismatch')
        for point_id, rate in rates.items():
            require(validate_one(point_id, [r for r in full if r['id'] == point_id]) == rate,
                    'Retained native evidence changed')
            candidates[point_id]['production_status'] = 'EVIDENCE_AVAILABLE'
            candidates[point_id]['scalar_level_production'] = rate
        for family in evidence['families']:
            candidate = candidates[family['id']]
            f = next(f for f in candidate['families'] if f['module2_input_sha256'] == family['module2_input_sha256'])
            original = next(r for r in full if r['neutrino']['input_sha256'] == f['module2_input_sha256'])
            path = ROOT/'validation/module8/local'/family['contract_path']
            require(file_sha(path) == family['contract_sha256'], 'Bound production contract changed')
            card = production(path, original['input_card'], original['neutrino'])
            require(card['sigma_pb'] == rates[family['id']]['sigma_pb'] and
                    math.isclose(card['sigma_pb']*f['cascade_BR'], family['yield_proxy_pb'], rel_tol=2e-13),
                    'Production/yield mismatch')
            f.update(original_production_status=f['production_status'], production_status='SUPPLIED_DOCUMENTED',
                     production={k: card[k] for k in ('sigma_pb', 'energy_TeV', 'integration_error_pb', 'process',
                         'charge_definition', 'order', 'pdf', 'scale_scheme', 'scalar_level_receipt_sha256')},
                     yield_proxy_pb=family['yield_proxy_pb'], rank=family['rank'],
                     integration_error_on_proxy_pb=family['integration_error_on_proxy_pb'],
                     production_contract_sha256=family['contract_sha256'])
        require(len(evidence['families']) == 4*len(rates) and
                len({f['module2_input_sha256'] for f in evidence['families']}) == 4*len(rates),
                'Missing/duplicate production binding')
        report.update(status=evidence['status'], production_evidence=evidence,
                      production_evidence_sha256=file_sha(production_path))
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--production', type=Path)
    p.add_argument('--vacuum', type=Path)
    a = p.parse_args()
    require(not a.output.exists(), 'Use a fresh export directory')
    report = audit(a.dataset)
    attach_evidence(report, a.dataset, a.production, a.vacuum)
    write_tables(report, a.output)
    print(json.dumps(report['counts'], sort_keys=True))


if __name__ == '__main__':
    main()
