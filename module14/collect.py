"""Streaming, disk-backed D14 shard validation and cutflow collection."""
import argparse
import json
import math
import sqlite3
import tempfile
from pathlib import Path

from module14.scan import digest, file_sha, scalar_status, encode

STATUSES = ('PASS', 'FAIL', 'UNKNOWN', 'NOT_EVALUATED', 'ERROR')
GATES = ('reconstruction', 'bfb', 'unitarity', 'ewpo', 'vacuum')


def cut():
    return {s: 0 for s in STATUSES}


def collect(manifest, config, triples, families=2, limit=math.sqrt(4*math.pi)):
    """Validate manifest and (shard, result, receipt) triples using a temporary SQLite index."""
    config_hash = digest(config)
    stats = {'scalar': cut(), 'gates': {g: cut() for g in GATES},
             'neutrino': {o: cut() for o in ('NO', 'IO')}}
    resources = {'elapsed_seconds_sum': 0., 'cpu_seconds_sum': 0., 'peak_rss_kib_max': 0}
    with tempfile.TemporaryDirectory(prefix='d14-collect-') as tmp:
        db = sqlite3.connect(str(Path(tmp) / 'index.sqlite'))
        db.execute('create table points (id integer primary key, row_hash text, scalar_hash text, seen integer default 0, shard integer)')
        total = 0
        with open(manifest) as f:
            for line in f:
                row = json.loads(line)
                if row['config_sha256'] != config_hash or row['scalar_sha256'] != digest(row['scalar']):
                    raise ValueError('Manifest input hash mismatch')
                try:
                    db.execute('insert into points(id,row_hash,scalar_hash) values(?,?,?)', (row['id'], digest(row), row['scalar_sha256']))
                except sqlite3.IntegrityError as e:
                    raise ValueError('Duplicate manifest point ID') from e
                total += 1
        db.commit()
        for shard_index, (shard, output, receipt) in enumerate(triples):
            rec = json.loads(Path(receipt).read_text())
            if rec.get('schema') != 'd14-worker-receipt-1' or rec.get('shard_sha256') != file_sha(shard) or rec.get('output_sha256') != file_sha(output):
                raise ValueError('Receipt or file hash mismatch')
            if rec.get('config_sha256') != config_hash or rec.get('families') != families or rec.get('perturbativity_limit') != limit:
                raise ValueError('Receipt settings mismatch')
            n = 0
            with open(shard) as f:
                for line in f:
                    row = json.loads(line)
                    found = db.execute('select row_hash,shard from points where id=?', (row['id'],)).fetchone()
                    if found is None or found[0] != digest(row):
                        raise ValueError('Unexpected or modified shard point')
                    if found[1] is not None:
                        raise ValueError('Duplicate point across or within shards')
                    db.execute('update points set shard=? where id=?', (shard_index, row['id']))
                    n += 1
            if n != rec['input_count']:
                raise ValueError('Receipt shard count mismatch')
            seen = 0
            with open(output) as f:
                for line in f:
                    result = json.loads(line)
                    found = db.execute('select scalar_hash,seen,shard from points where id=?', (result['id'],)).fetchone()
                    if found is None or found[2] != shard_index:
                        raise ValueError('Unexpected result or wrong shard')
                    if found[1]:
                        raise ValueError('Duplicate result')
                    if result['scalar_sha256'] != found[0] or result['config_sha256'] != config_hash:
                        raise ValueError('Result identity hash mismatch')
                    gates = result['gates']
                    for gate in GATES:
                        status = gates[gate]['assessment']
                        if status not in STATUSES:
                            raise ValueError('Invalid gate status')
                        stats['gates'][gate][status] += 1
                    status = scalar_status(gates)
                    if result['scalar_status'] != status:
                        raise ValueError('Inconsistent scalar status')
                    stats['scalar'][status] += 1
                    ns = result['neutrino']
                    eligible = all(gates[k]['assessment'] == 'PASS' for k in GATES[:-1]) and gates['vacuum']['assessment'] in ('PASS', 'UNKNOWN')
                    if ns == 'NOT_EVALUATED' and not eligible:
                        for ordering in ('NO', 'IO'):
                            stats['neutrino'][ordering]['NOT_EVALUATED'] += families
                    elif isinstance(ns, list) and eligible:
                        keys = set()
                        for item in ns:
                            ordering, family, st = item['ordering'], item['family'], item['status']
                            key = (ordering, family)
                            if ordering not in ('NO', 'IO') or type(family) is not int or not 0 <= family < families or key in keys or st not in STATUSES:
                                raise ValueError('Invalid or duplicate neutrino family')
                            keys.add(key)
                            inp = item['input']
                            if item['input_sha256'] != digest(inp) or item['target_sha256'] != digest(inp['target_eV']) or inp['scalar']['sha256'] != found[0] or digest(inp['scalar']['record']) != found[0] or inp['ordering'] != ordering or item['seed_sha256'] != digest(['d14-neutrino-v1', config['seed'], result['id'], ordering, family]):
                                raise ValueError('Neutrino input identity mismatch')
                            stats['neutrino'][ordering][st] += 1
                        if len(keys) != 2 * families:
                            raise ValueError('Missing neutrino families')
                    else:
                        raise ValueError('Inconsistent neutrino evaluation status')
                    db.execute('update points set seen=1 where id=?', (result['id'],))
                    seen += 1
            if seen != n or seen != rec['output_count']:
                raise ValueError('Missing shard results or receipt count mismatch')
            for k in ('elapsed_seconds', 'cpu_seconds'):
                resources[k + '_sum'] += rec[k]
            resources['peak_rss_kib_max'] = max(resources['peak_rss_kib_max'], rec['peak_rss_kib'])
        missing = db.execute('select count(*) from points where seen=0').fetchone()[0]
        return {'status': 'COMPLETE' if not missing else 'INCOMPLETE', 'manifest_sha256': file_sha(manifest),
                'config_sha256': config_hash, 'manifest_points': total, 'evaluated_points': total-missing,
                'missing_points': missing, 'families_per_ordering': families, 'cutflow': stats, 'resources': resources}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', required=True); p.add_argument('--config', required=True)
    p.add_argument('--part', nargs=3, action='append', default=[], metavar=('SHARD', 'RESULT', 'RECEIPT'))
    p.add_argument('--families', type=int, default=2); p.add_argument('--perturbativity-limit', type=float, default=math.sqrt(4*math.pi))
    p.add_argument('--output', required=True)
    a = p.parse_args()
    report = collect(a.manifest, json.loads(Path(a.config).read_text()), a.part, a.families, a.perturbativity_limit)
    with open(a.output, 'x') as f:
        f.write(encode(report)+'\n')
    return 0 if report['status'] == 'COMPLETE' else 2

if __name__ == '__main__':
    raise SystemExit(main())
