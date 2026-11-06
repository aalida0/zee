"""Collect the two original AF batches using their archived source, without jobs.

Run on AF in the D14 Python environment from a Git checkout containing d45f179.
Reports are immutable; choose a fresh --report-name for each audit.
"""
import argparse
from collections import Counter
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

COMMIT = 'd45f179870fa93fabe9bc137b753cdfd2cf0478f'


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1048576), b''): h.update(block)
    return h.hexdigest()


def tree(tar):
    return {m.name: hashlib.sha256(tar.extractfile(m).read()).hexdigest()
            for m in tar.getmembers() if m.isfile()}


def audit(data_root, batch_root, report_name):
    if Path(report_name).name != report_name:
        raise ValueError('Report name must be a filename')
    raw = subprocess.check_output(['git', 'archive', '--format=tar', COMMIT])
    with tarfile.open(fileobj=io.BytesIO(raw)) as tar: expected = tree(tar)
    results = {}
    with tempfile.TemporaryDirectory(prefix='zee-d14-audit-') as tmp:
        for name, count, shards in [('d14_heavy_20k', 20000, 80), ('d14_heavy_physics_225', 225, 9)]:
            root, batch = Path(data_root)/name, Path(batch_root)/name
            commit = (batch/'source_commit.txt').read_text().strip()
            if commit != COMMIT: raise ValueError('Unexpected source commit')
            bundle = sha(batch/'scan_bundle.tar.gz')
            if bundle != (batch/'bundle.sha256').read_text().split()[0]: raise ValueError('Bundle hash mismatch')
            source = Path(tmp)/name; source.mkdir()
            with tarfile.open(batch/'scan_bundle.tar.gz') as tar:
                if tar.pax_headers.get('comment') != COMMIT or tree(tar) != expected:
                    raise ValueError('Archive tree does not reproduce source commit')
                tar.extractall(source)
            config_path = root/'config.json' if name.endswith('225') else batch/'config.json'
            config = json.loads(config_path.read_text())
            settings = json.loads((batch/'job_settings.json').read_text())
            files = sorted((root/'scan').glob('shard_*.jsonl'))
            if len(files) != shards: raise ValueError('Expected shard count mismatch')
            triples, evidence, arms = [], [], {}
            for shard in files:
                outs = list((batch/'results').glob(shard.name+'.*.jsonl'))
                recs = list((batch/'receipts').glob(shard.name+'.*.json'))
                if len(outs) != 1 or len(recs) != 1: raise ValueError('Missing/duplicate result or receipt')
                rec = json.loads(recs[0].read_text())
                for k in ('lfv', 'lfv_tree', 'bsgamma', 'higgs'):
                    if rec[k+'_enabled'] != settings[k]: raise ValueError('Settings mismatch: '+k)
                for k in ('hb_data', 'hs_data', 'production_dir'):
                    if rec.get(k) != settings.get(k): raise ValueError('Settings path mismatch: '+k)
                if rec['worker_sha256'] != sha(source/'module14/scan.py'): raise ValueError('Worker source mismatch')
                triples.append([str(shard), str(outs[0]), str(recs[0])])
                evidence.append({'shard': shard.name, 'input_sha256': sha(shard),
                                 'output_sha256': sha(outs[0]), 'receipt_sha256': sha(recs[0])})
                with shard.open() as fi, outs[0].open() as fo:
                    for a, b in zip(fi, fo):
                        row, out = json.loads(a), json.loads(b)
                        if row['id'] != out['id']: raise ValueError('Result order mismatch')
                        arm = arms.setdefault(row['arm'], {'proposals': 0, 'stages': {}}); arm['proposals'] += 1
                        stages = {k: v['assessment'] for k, v in out['gates'].items()}
                        stages['bsgamma_legacy'] = out['bsgamma']['status']
                        for k, v in stages.items(): arm['stages'].setdefault(k, Counter())[v] += 1
                        ns = out['neutrino']
                        for ordering in ('NO', 'IO'):
                            statuses = [x['status'] for x in ns if x['ordering'] == ordering] if isinstance(ns, list) else ['NOT_EVALUATED']*settings['families']
                            for status in statuses: arm['stages'].setdefault('neutrino_'+ordering, Counter())[status] += 1
            request = {'manifest': str(root/'scan/manifest.jsonl'), 'config': config, 'triples': triples,
                       'source_commit': commit, 'source_bundle_sha256': bundle,
                       'families': settings['families'], 'limit': settings['perturbativity_limit']}
            request_path = Path(tmp)/'request.json'; request_path.write_text(json.dumps(request))
            code = 'import json,sys; from module14.collect import collect; print(json.dumps(collect(**json.load(open(sys.argv[1])))))'
            result = subprocess.run([sys.executable, '-c', code, str(request_path)], cwd=source,
                                    env=dict(os.environ, PYTHONPATH=str(source)), text=True, capture_output=True, check=True)
            report = json.loads(result.stdout)
            if report['status'] != 'COMPLETE' or report['missing_points'] or report['evaluated_points'] != count:
                raise ValueError('Incomplete collection')
            dest = root/report_name
            with dest.open('x') as f: json.dump(report, f, sort_keys=True); f.write('\n')
            results[name] = {'report': report, 'remote_report_path': str(dest), 'report_sha256': sha(dest),
                             'settings': settings, 'config': config, 'shards': evidence, 'by_arm': arms,
                             'original_source_tree_verified_against_git_commit': True}
    return results


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-root', required=True); p.add_argument('--batch-root', required=True)
    p.add_argument('--report-name', required=True); p.add_argument('--output', required=True)
    a = p.parse_args()
    result = audit(a.data_root, a.batch_root, a.report_name)
    with open(a.output, 'x') as f: json.dump(result, f, indent=2, sort_keys=True); f.write('\n')


if __name__ == '__main__': main()
