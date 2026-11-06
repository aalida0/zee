"""Deterministic final conditional JSONL/CSV exports from verified saved rows."""
import argparse
from collections import Counter
import csv
import json
import os
import sqlite3
import tempfile
from contextlib import ExitStack

from module14.disk_rows import DiskRows, streaming_digest
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


def _export(dataset, output, production_dir=None, contracts=None):
    if dataset.get('status') != 'CONDITIONAL_DATASET' or dataset['collection']['status'] != 'COMPLETE' or dataset['collection']['missing_points']:
        raise ValueError('Verified complete saved dataset required')
    if production_dir is not None and not contracts:
        raise ValueError('Explicit production contracts required for enrichment')
    if contracts:
        for energy, contract in contracts.items():
            if energy not in ('13', '14') or contract.get('energy_TeV') != int(energy):
                raise ValueError('Production contract channel/energy mismatch')
    rows = DiskRows()
    rows.db.execute('CREATE UNIQUE INDEX unique_family ON rows(id, IFNULL(ordering, ""), IFNULL(family,-1))')
    rows.db.execute('CREATE TABLE scalars(id INTEGER PRIMARY KEY)')
    rows.db.execute('CREATE TABLE ranks(energy TEXT, contract TEXT, rate REAL, id INTEGER, ordering TEXT, family INTEGER, seq INTEGER)')
    by_arm = {}
    original = dataset['rows']
    # Spool even a legacy iterable: ordering and duplicate detection stay on disk.
    source = DiskRows()
    try:
        for row in original:
            source.append(row)
        return _write(dataset, output, production_dir, contracts, rows, source, by_arm)
    finally:
        rows.close()
        source.close()


def _write(dataset, output, production_dir, contracts, rows, source, by_arm):
    for original_row in source.sorted():
        r = original_row
        n = r['neutrino'] if isinstance(r['neutrino'], dict) else None
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
        if rows.db.execute('INSERT OR IGNORE INTO scalars VALUES(?)',(r['id'],)).rowcount:
            stage_counter['points'] += 1
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
                    rows.db.execute('INSERT INTO ranks VALUES(?,?,?,?,?,?,?)', (energy,digest(contract),rate,r['id'],n['ordering'],n['family'],len(rows)))
        try:
            rows.append(data)
        except sqlite3.IntegrityError as exc:
            raise ValueError('Duplicate export point/family') from exc
    for energy, seq, rank in rows.db.execute(
            'SELECT energy, seq, ROW_NUMBER() OVER (PARTITION BY energy, contract ORDER BY rate DESC, id, ordering, family) FROM ranks'):
        row = rows[seq]
        row[f'rank_{energy}'] = rank
        rows.db.execute('UPDATE rows SET data=? WHERE seq=?',(encode(row),seq))
    output = Path(output)
    with (output/'families.jsonl').open('w') as f:
        for row in rows:
            f.write(encode(row)+'\n')
    with (output/'families.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction='ignore', lineterminator='\n')
        w.writeheader(); w.writerows(rows)
    (output/'cutflows.json').write_text(encode(by_arm)+'\n')
    (output/'collection.json').write_text(encode(dataset['collection'])+'\n')
    with (output/'benchmarks.json').open('w') as f:
        f.write('[')
        first = True
        for row in rows:
            if any(row[f'rank_{e}'] is not None for e in ('13', '14')):
                if not first:
                    f.write(',')
                f.write(encode({k: row[k] for k in COLUMNS} | {'rank_reason': row['rank_reason']}))
                first = False
        f.write(']\n')
    audit = {'schema': 'd14-final-export-1', 'status': 'COMPLETE', 'rows': len(rows), 'points': rows.db.execute('SELECT COUNT(*) FROM scalars').fetchone()[0],
             'global_acceptance': None, 'limitations': LIMITATIONS,
             'input_sha256': streaming_digest(dataset), 'contracts_sha256': digest(contracts),
             'files_sha256': {p.name: file_sha(p) for p in sorted(output.iterdir())}}
    (output/'audit.json').write_text(encode(audit)+'\n')
    return audit


def export(dataset, output, production_dir=None, contracts=None):
    """Validate/spool first; publish a complete directory with one atomic rename.

    A sibling exclusive lock prevents concurrent exporters to the same target.
    Exceptions/interruption remove scratch; no partial output is published.
    """
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    lock = output.with_name(output.name+'.export-lock')
    with ExitStack() as stack:
        stack.enter_context(lock.open('x'))
        stack.callback(lock.unlink)
        if output.exists():
            raise FileExistsError(output)
        tmp = stack.enter_context(tempfile.TemporaryDirectory(prefix='.'+output.name+'-', dir=output.parent))
        audit = _export(dataset, tmp, production_dir, contracts)
        if output.exists():
            raise FileExistsError(output)
        os.rename(tmp, output)
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
                  preflight_report=load(a.preflight_report) if a.preflight_report else None, streaming=True)
    try:
        audit = export(result, a.output, a.production_dir, load(a.production_contract) if a.production_contract else None)
    finally:
        result['rows'].close()
    print(encode(audit))


if __name__ == '__main__': main()
