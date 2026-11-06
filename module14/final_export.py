"""Deterministic final conditional JSONL/CSV exports from verified saved rows."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path

from module14.scan import digest, encode, file_sha
from module14.final_config import LIMITATIONS
from module14.conditional_scan.workflow import cascade, join, load, production

COLUMNS = ('schema', 'id', 'arm', 'ordering', 'family', 'scalar_sha256',
           'module2_input_sha256', 'scalar_status', 'vacuum_status', 'neutrino_status',
           'lfv_status', 'widths_status', 'higgstools_status', 'conditional_bsgamma', 'bsg_physical_status',
           'BR_H2_H1Z', 'BR_H1_tb', 'sigma_13_pb', 'sigma_14_pb',
           'cascade_tb_13_pb', 'cascade_tb_14_pb', 'rank_13', 'rank_14', 'global_acceptance')


def status(value):
    return value.get('status', 'NOT_EVALUATED') if isinstance(value, dict) else value


def export(dataset, output, production_dir=None, contracts=None):
    if dataset.get('status') != 'CONDITIONAL_DATASET' or dataset['collection']['status'] != 'COMPLETE' or dataset['collection']['missing_points']:
        raise ValueError('Verified complete saved dataset required')
    if production_dir is not None and not contracts:
        raise ValueError('Explicit production contracts required for enrichment')
    if contracts:
        for energy, contract in contracts.items():
            if energy not in ('13', '14') or contract.get('energy_TeV') != int(energy):
                raise ValueError('Production contract channel/energy mismatch')
    rows = []; seen = set(); groups = {}
    by_arm = {}
    original = sorted(dataset['rows'], key=lambda r: (r['id'],
                      r['neutrino'].get('ordering', '') if isinstance(r['neutrino'], dict) else '',
                      r['neutrino'].get('family', -1) if isinstance(r['neutrino'], dict) else -1))
    scalar_seen = set()
    for original_row in original:
        r = original_row
        n = r['neutrino'] if isinstance(r['neutrino'], dict) else None
        identity = (r['id'], n['ordering'] if n else None, n['family'] if n else None)
        if identity in seen: raise ValueError('Duplicate export point/family')
        seen.add(identity)
        if r.get('globally_allowed') is not None or r['bsg_physical_classification'] != 'UNKNOWN':
            raise ValueError('Unsupported physical acceptance claim in conditional dataset')
        if r['scalar_sha256'] != digest(r['input_card']): raise ValueError('Export scalar binding mismatch')
        decays = cascade(r['input_card'], n, r['widths'] if isinstance(r['widths'], dict) else None) if n else None
        data = {'schema': 'd14-final-family-1', 'id': r['id'], 'arm': r['arm'],
                'ordering': n['ordering'] if n else None, 'family': n['family'] if n else None,
                'scalar_sha256': r['scalar_sha256'], 'module2_input_sha256': n['input_sha256'] if n else None,
                'scalar_status': r['scalar_status'], 'vacuum_status': r['gates']['vacuum']['assessment'],
                'neutrino_status': n['status'] if n else 'NOT_EVALUATED',
                'lfv_status': status(r['lfv']), 'higgstools_status': status(r['higgstools']),
                'widths_status': status(r['widths']),
                'conditional_bsgamma': r['flavor']['bsg_nominal_classification'], 'bsg_physical_status': 'UNKNOWN',
                'BR_H2_H1Z': decays.get('BR_H2_H1Z') if decays else None,
                'BR_H1_tb': decays.get('BR_H1_tb') if decays else None, 'global_acceptance': None,
                'np_theory_sigma': None, 'production': {}, 'saved_results': r,
                'provenance': {'manifest_sha256': dataset['collection']['manifest_sha256'],
                               'config_sha256': dataset['collection']['config_sha256'],
                               'worker_source': dataset['collection']['source_provenance'],
                               'sidecar_source_sha256': dataset['source_sha256'],
                               'matching_card_sha256': dataset['matching_card_sha256']},
                'omissions': LIMITATIONS, 'rank_reason': {}}
        stage_counter = by_arm.setdefault(r['arm'], {'points': 0, 'families': 0, 'statuses': {}})
        if r['id'] not in scalar_seen:
            scalar_seen.add(r['id']); stage_counter['points'] += 1
            for name, gate in r['gates'].items():
                stage_counter['statuses'].setdefault(name, Counter())[gate['assessment']] += 1
            stage_counter['statuses'].setdefault('conditional_bsgamma', Counter())[data['conditional_bsgamma']] += 1
        if n:
            stage_counter['families'] += 1
            for name in ('neutrino_status', 'lfv_status', 'widths_status', 'higgstools_status'):
                stage_counter['statuses'].setdefault(name+'_'+n['ordering'], Counter())[data[name]] += 1
        else:
            for order in ('NO', 'IO'):
                for name in ('neutrino_status', 'lfv_status', 'widths_status', 'higgstools_status'):
                    stage_counter['statuses'].setdefault(name+'_'+order, Counter())['NOT_EVALUATED'] += dataset['collection']['families_per_ordering']
        for energy in ('13', '14'):
            data.update({f'sigma_{energy}_pb': None, f'cascade_tb_{energy}_pb': None, f'rank_{energy}': None})
            path = Path(production_dir)/(n['input_sha256']+f'.{energy}TeV.json') if n and production_dir else None
            contract = contracts.get(energy) if contracts else None
            if path and path.exists() and contract is None:
                raise ValueError('Supplied production channel lacks expected contract')
            prod = production(path, r['input_card'], n, contract)
            data['production'][energy] = prod
            data['rank_reason'][energy] = 'Missing source-bound production or complete on-shell BR/family; no physical acceptance implied'
            hard = any(g['assessment'] in ('FAIL', 'ERROR') for g in r['gates'].values())
            if prod['status'] == 'SUPPLIED_DOCUMENTED':
                data[f'sigma_{energy}_pb'] = prod['sigma_pb']
                if (not hard and n['status'] == 'PASS' and n['closure_status'] == 'PASS'
                    and decays['br_status'] == 'PASS' and decays['is_kinematically_open']):
                    rate = prod['sigma_pb']*decays['BR_H2_H1Z']*decays['BR_H1_tb']
                    data[f'cascade_tb_{energy}_pb'] = rate
                    data['rank_reason'][energy] = 'Descending exact sigma*BR(H2->H1Z)*BR(H1->tb) within the declared production contract; conditional diagnostic only'
                    groups.setdefault((energy, digest(contract)), []).append(data)
        encode(data); rows.append(data)
    for (energy, _), group in groups.items():
        for rank, row in enumerate(sorted(group, key=lambda r: (-r[f'cascade_tb_{energy}_pb'], r['id'], r['ordering'], r['family'])), 1):
            row[f'rank_{energy}'] = rank
    output = Path(output); output.mkdir(parents=True, exist_ok=False)
    (output/'families.jsonl').write_text(''.join(encode(r)+'\n' for r in rows))
    with (output/'families.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore', lineterminator='\n')
        w.writeheader(); w.writerows(rows)
    (output/'cutflows.json').write_text(encode(by_arm)+'\n')
    (output/'collection.json').write_text(encode(dataset['collection'])+'\n')
    benchmarks = [{k: r[k] for k in COLUMNS} | {'rank_reason': r['rank_reason']} for r in rows
                  if any(r[f'rank_{e}'] is not None for e in ('13', '14'))]
    (output/'benchmarks.json').write_text(encode(benchmarks)+'\n')
    audit = {'schema': 'd14-final-export-1', 'status': 'COMPLETE', 'rows': len(rows), 'points': len(scalar_seen),
             'global_acceptance': None, 'limitations': LIMITATIONS,
             'input_sha256': digest(dataset), 'contracts_sha256': digest(contracts),
             'files_sha256': {p.name: file_sha(p) for p in sorted(output.iterdir())}}
    (output/'audit.json').write_text(encode(audit)+'\n')
    return audit


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('manifest', 'config', 'matching-card', 'source-commit', 'source-bundle-sha256', 'output'):
        p.add_argument('--'+name, required=True)
    p.add_argument('--part', nargs=3, action='append', required=True)
    p.add_argument('--families', type=int, default=2); p.add_argument('--production-dir'); p.add_argument('--production-contract')
    p.add_argument('--preflight-report')
    a = p.parse_args(); config = load(a.config)
    parts = sorted(a.part, key=lambda t: file_sha(t[0]))
    result = join(a.manifest, config, parts, load(a.matching_card), a.source_commit,
                  a.source_bundle_sha256, config.get('families', a.families),
                  preflight_report=load(a.preflight_report) if a.preflight_report else None)
    audit = export(result, a.output, a.production_dir, load(a.production_contract) if a.production_contract else None)
    print(encode(audit))


if __name__ == '__main__': main()
