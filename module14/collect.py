"""Streaming, disk-backed D14 shard validation and cutflow collection."""
import argparse
from collections import Counter
import json
import math
import sqlite3
import tempfile
from pathlib import Path

from module14.scan import digest, file_sha, scalar_status, encode
from module5.hyperiso_patch_contract import unique_pairs

STATUSES = ('PASS', 'FAIL', 'UNKNOWN', 'NOT_EVALUATED', 'ERROR', 'DIAGNOSTIC_ONLY')
GATES = ('reconstruction', 'bfb', 'unitarity', 'ewpo', 'vacuum')


def cut():
    return {s: 0 for s in STATUSES}


def decode(text):
    value = json.loads(text, object_pairs_hook=unique_pairs)
    digest(value)  # rejects NaN, Infinity and overflowing JSON exponents recursively
    return value


def collect(manifest, config, triples, families=2, limit=math.sqrt(4*math.pi), source_commit=None, source_bundle_sha256=None, preflight_report=None, require_full_manifest=True):
    """Validate manifest and (shard, result, receipt) triples using a temporary SQLite index."""
    config_hash = digest(config)
    final = config.get('schema') == 'd14-final-config-1'
    if final:
        from module14.final_config import validate, validate_manifest
        validate(config); validate_manifest(manifest, config, require_full=require_full_manifest)
        from module14.final_workflow import require_preflight
        if preflight_report is None: raise ValueError('Final collector requires preflight report')
        require_preflight(config, preflight_report)
        if families != config['families'] or limit != config['perturbativity_limit']:
            raise ValueError('Final collector family/perturbativity settings mismatch')
        if source_commit != config['source_commit'] or not source_bundle_sha256:
            raise ValueError('Final collection requires exact source commit and bundle')
    stats = {'scalar': cut(), 'gates': {g: cut() for g in GATES},
             'neutrino': {o: cut() for o in ('NO', 'IO')}}
    stats['bsgamma'] = cut()
    stats['family_stages'] = {stage: {o: cut() for o in ('NO', 'IO')} for stage in ('lfv', 'widths', 'higgstools')}
    resources = {'elapsed_seconds_sum': 0., 'cpu_seconds_sum': 0., 'peak_rss_kib_max': 0}
    with tempfile.TemporaryDirectory(prefix='d14-collect-') as tmp:
        db = sqlite3.connect(str(Path(tmp) / 'index.sqlite'))
        db.execute('create table points (id integer primary key, row_hash text, scalar_hash text, seen integer default 0, shard integer)')
        total = 0
        with open(manifest) as f:
            for line in f:
                row = decode(line)
                if type(row['id']) is not int or row['id'] < 0:
                    raise ValueError('Manifest IDs must be nonnegative integers')
                if row['config_sha256'] != config_hash or row['scalar_sha256'] != digest(row['scalar']):
                    raise ValueError('Manifest input hash mismatch')
                try:
                    db.execute('insert into points(id,row_hash,scalar_hash) values(?,?,?)', (row['id'], digest(row), row['scalar_sha256']))
                except sqlite3.IntegrityError as e:
                    raise ValueError('Duplicate manifest point ID') from e
                total += 1
        db.commit()
        provenance = None
        lfv_settings = None
        for shard_index, (shard, output, receipt) in enumerate(triples):
            rec = decode(Path(receipt).read_text())
            if any(type(rec.get(k)) is not int or rec[k] < 0 for k in ('input_count', 'output_count', 'peak_rss_kib')):
                raise ValueError('Invalid receipt counts or RSS')
            if not isinstance(rec.get('counts'), dict) or any(type(v) is not int or v < 0 for v in rec['counts'].values()):
                raise ValueError('Invalid receipt cutflow counts')
            stage_settings = tuple(rec.get(k) for k in ('lfv_enabled', 'lfv_tree_enabled', 'bsgamma_enabled', 'higgs_enabled', 'd9b_probe_sha256', 'higgs_datasets_sha256', 'production_dir', 'worker_sha256', 'final_preflight_sha256')) + (digest(rec.get('runtime')),)
            if final:
                for key in ('lfv', 'lfv_tree', 'bsgamma', 'higgs'):
                    if rec.get(key+'_enabled') is not config['stages'][key]:
                        raise ValueError('Required backend/stage settings mismatch: '+key)
                if not rec.get('final_preflight_sha256') or rec['worker_sha256'] != file_sha(Path(__file__).with_name('scan.py')):
                    raise ValueError('Final receipt source/preflight identity missing or changed')
                if rec['final_preflight_sha256'] != preflight_report['report_sha256']:
                    raise ValueError('Worker preflight report differs from required report')
                if require_full_manifest and rec.get('manifest_sha256') != file_sha(manifest):
                    raise ValueError('Worker original manifest identity mismatch')
                rt = config['runtime']
                if any(rec.get('runtime', {}).get('dependencies', {}).get(k) != v for k, v in rt['packages'].items()):
                    raise ValueError('Worker runtime pins mismatch')
                if rec.get('d9b_probe_sha256') != rt['binaries'].get('d9b_probe', {}).get('sha256'):
                    raise ValueError('Worker backend binary checksum mismatch')
            if lfv_settings is None:
                lfv_settings = stage_settings
            elif lfv_settings != stage_settings:
                raise ValueError('Shard LFV settings mismatch')
            identity = (rec.get('source_commit'), rec.get('source_bundle_sha256'))
            if provenance is None:
                provenance = identity
            elif provenance != identity:
                raise ValueError('Shard source provenance mismatch')
            if (source_commit is not None and identity[0] != source_commit) or (source_bundle_sha256 is not None and identity[1] != source_bundle_sha256):
                raise ValueError('Source does not match required provenance')
            if rec.get('schema') != 'd14-worker-receipt-1' or rec.get('shard_sha256') != file_sha(shard) or rec.get('output_sha256') != file_sha(output):
                raise ValueError('Receipt or file hash mismatch')
            if rec.get('config_sha256') != config_hash or rec.get('families') != families or rec.get('perturbativity_limit') != limit:
                raise ValueError('Receipt settings mismatch')
            n = 0
            with open(shard) as f:
                for line in f:
                    row = decode(line)
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
            receipt_counts = Counter()
            with open(output) as f:
                for line in f:
                    result = decode(line)
                    if type(result['id']) is not int:
                        raise ValueError('Result ID must be integer')
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
                        receipt_counts[gate+':'+status] += 1
                    status = scalar_status(gates)
                    if result['scalar_status'] != status:
                        raise ValueError('Inconsistent scalar status')
                    stats['scalar'][status] += 1
                    flavor = result.get('bsgamma', 'NOT_EVALUATED')
                    fs = flavor.get('status') if isinstance(flavor, dict) else flavor
                    if fs not in STATUSES:
                        raise ValueError('Invalid flavor status')
                    stats['bsgamma'][fs] += 1
                    receipt_counts['bsgamma:'+fs] += 1
                    eligible = all(gates[k]['assessment'] == 'PASS' for k in GATES[:-1]) and gates['vacuum']['assessment'] in ('PASS', 'UNKNOWN')
                    if final and eligible and config['stages']['bsgamma'] and fs == 'NOT_EVALUATED':
                        raise ValueError('Required B backend was not evaluated')
                    for stage in ('lfv', 'widths', 'higgstools'):
                        data = result.get(stage, 'NOT_EVALUATED')
                        if data == 'NOT_EVALUATED':
                            for ordering in ('NO', 'IO'):
                                stats['family_stages'][stage][ordering]['NOT_EVALUATED'] += families
                                receipt_counts[stage+':'+ordering+':NOT_EVALUATED'] += families
                        elif isinstance(data, list):
                            seen_stage = set()
                            for entry in data:
                                key = (entry['ordering'], entry['family'])
                                st = entry['status']
                                if st == 'PARTIAL': st = 'DIAGNOSTIC_ONLY'
                                if key in seen_stage or key[0] not in ('NO', 'IO') or type(key[1]) is not int or not 0 <= key[1] < families or st not in STATUSES:
                                    raise ValueError('Invalid family stage identity or status')
                                seen_stage.add(key)
                                stats['family_stages'][stage][key[0]][st] += 1
                                receipt_counts[stage+':'+key[0]+':'+st] += 1
                            if len(seen_stage) != 2*families:
                                raise ValueError('Missing family stage result')
                        else:
                            raise ValueError('Invalid family stage')
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
                            seed_hash = digest(['d14-neutrino-v1', config['seed'], result['id'], ordering, family])
                            if inp is None:
                                if (st != 'ERROR' or item.get('closure_status') != 'ERROR' or item.get('error_phase') != 'input_construction'
                                    or item.get('scalar_sha256') != found[0] or item.get('input_sha256') is not None
                                    or item.get('target_sha256') is not None or item['seed_sha256'] != seed_hash):
                                    raise ValueError('Invalid family input-construction error provenance')
                            elif item['input_sha256'] != digest(inp) or item['target_sha256'] != digest(inp['target_eV']) or inp['scalar']['sha256'] != found[0] or digest(inp['scalar']['record']) != found[0] or inp['ordering'] != ordering or item['seed_sha256'] != seed_hash:
                                raise ValueError('Neutrino input identity mismatch')
                            stats['neutrino'][ordering][st] += 1
                            receipt_counts['neutrino:'+ordering+':'+st] += 1
                        if len(keys) != 2 * families:
                            raise ValueError('Missing neutrino families')
                        expected_keys = [(o, f) for o in ('NO', 'IO') for f in range(families)]
                        if [(n['ordering'], n['family']) for n in ns] != expected_keys:
                            raise ValueError('Noncanonical neutrino family ordering')
                        family_hashes = {(n['ordering'], n['family']): n['input_sha256'] for n in ns}
                        for stage in ('lfv', 'widths', 'higgstools'):
                            data = result.get(stage, 'NOT_EVALUATED')
                            if isinstance(data, list):
                                if [(n['ordering'], n['family']) for n in data] != expected_keys:
                                    raise ValueError('Noncanonical stage family ordering')
                                for entry in data:
                                    if entry.get('module2_input_sha256') != family_hashes[(entry['ordering'], entry['family'])]:
                                        raise ValueError('Family stage input hash mismatch')
                            enabled = stage == 'widths' or rec.get({'lfv': 'lfv_enabled', 'widths': '', 'higgstools': 'higgs_enabled'}[stage])
                            if final and enabled:
                                if not isinstance(data, list): raise ValueError('Required family stage absent: '+stage)
                                for family_item, entry in zip(ns, data):
                                    if family_item.get('closure_status') == 'PASS' and (stage == 'widths' or family_item['status'] == 'PASS') and entry['status'] == 'NOT_EVALUATED':
                                        raise ValueError('Required family backend was not evaluated: '+stage)
                    else:
                        raise ValueError('Inconsistent neutrino evaluation status')
                    db.execute('update points set seen=1 where id=?', (result['id'],))
                    seen += 1
            if seen != n or seen != rec['output_count']:
                raise ValueError('Missing shard results or receipt count mismatch')
            if rec.get('counts') != dict(receipt_counts):
                raise ValueError('Receipt cutflow does not match saved results')
            for k in ('elapsed_seconds', 'cpu_seconds'):
                if type(rec[k]) not in (int, float) or rec[k] < 0:
                    raise ValueError('Invalid receipt resources')
                resources[k + '_sum'] += rec[k]
            resources['peak_rss_kib_max'] = max(resources['peak_rss_kib_max'], rec['peak_rss_kib'])
        missing = db.execute('select count(*) from points where seen=0').fetchone()[0]
        errors = stats['scalar']['ERROR']+stats['bsgamma']['ERROR']+sum(
            stats['neutrino'][o]['ERROR']+sum(stats['family_stages'][s][o]['ERROR'] for s in stats['family_stages']) for o in ('NO', 'IO'))
        return {'status': ('INCOMPLETE' if missing else 'ERROR' if final and errors else 'COMPLETE'), 'computational_errors': errors, 'manifest_sha256': file_sha(manifest),
                'config_sha256': config_hash, 'manifest_points': total, 'evaluated_points': total-missing,
                'missing_points': missing, 'source_provenance': provenance, 'families_per_ordering': families, 'cutflow': stats, 'resources': resources}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', required=True); p.add_argument('--config', required=True)
    p.add_argument('--part', nargs=3, action='append', default=[], metavar=('SHARD', 'RESULT', 'RECEIPT'))
    p.add_argument('--families', type=int, default=2); p.add_argument('--perturbativity-limit', type=float, default=math.sqrt(4*math.pi))
    p.add_argument('--source-commit'); p.add_argument('--source-bundle-sha256')
    p.add_argument('--preflight-report')
    p.add_argument('--output', required=True)
    a = p.parse_args()
    report = collect(a.manifest, decode(Path(a.config).read_text()), a.part, a.families, a.perturbativity_limit, a.source_commit, a.source_bundle_sha256, decode(Path(a.preflight_report).read_text()) if a.preflight_report else None)
    with open(a.output, 'x') as f:
        f.write(encode(report)+'\n')
    return 0 if report['status'] == 'COMPLETE' else 2

if __name__ == '__main__':
    raise SystemExit(main())
