"""Small real generation/worker/collector demonstration; outputs never overwrite."""
import argparse
import json
from pathlib import Path
import subprocess

from module14 import scan
from .workflow import join, load
from .flavor import source_hashes

HERE = Path(__file__).resolve().parent


def run(root):
    root = Path(root)
    root.mkdir(exist_ok=False, parents=True)
    card = load(HERE/'matching_card.json')
    summary = {'source_sha256': source_hashes(), 'runs': {}, 'globally_allowed': None}
    for name, config in [('followup', load(HERE/'pilot_config.json')),
                         ('legacy_control', load('module14/pilot_config.json'))]:
        if name == 'legacy_control': config.update(count=100, shard_size=25)
        directory = root/name
        directory.mkdir()
        scan.generate(config, directory/'scan')
        scan.generate(config, directory/'repeat')
        manifest = directory/'scan/manifest.jsonl'
        assert manifest.read_bytes() == (directory/'repeat/manifest.jsonl').read_bytes()
        triples = []
        for i, shard in enumerate(sorted((directory/'scan').glob('shard_*.jsonl'))):
            out, receipt = directory/f'part{i}.jsonl', directory/f'part{i}.receipt.json'
            scan.run(shard, out, receipt, config, lfv=True)
            triples.append((shard, out, receipt))
        full, fullrec = directory/'serial.jsonl', directory/'serial.receipt.json'
        scan.run(manifest, full, fullrec, config, lfv=True)
        equal = full.read_bytes() == b''.join(Path(t[1]).read_bytes() for t in triples)
        assert equal
        receipt = load(fullrec)
        result = join(manifest, config, triples, card, receipt['source_commit'], receipt['source_bundle_sha256'])
        serial = join(manifest, config, [(manifest, full, fullrec)], card, receipt['source_commit'], receipt['source_bundle_sha256'])
        assert result['rows'] == serial['rows'] and result['by_arm'] == serial['by_arm']
        with (directory/'conditional_dataset.json').open('x') as f:
            json.dump(result, f, sort_keys=True, allow_nan=False)
        summary['runs'][name] = {'config': config, 'collection': result['collection'],
            'by_arm': result['by_arm'], 'generation_repeated_bytes_equal': True,
            'serial_split_worker_bytes_equal': equal, 'serial_split_sidecar_rows_equal': True,
            'dataset_sha256': scan.file_sha(directory/'conditional_dataset.json'),
            'rows': len(result['rows']), 'ranked_rows': sum(r['rank'] is not None for r in result['rows']),
            'examples': [{k: r[k] for k in ('id', 'arm', 'input_card', 'flavor', 'cascade', 'globally_allowed')}
                         for r in result['rows'] if r['cascade'] is not None]}
    summary['source_commit'] = subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip()
    summary['source_commit_note'] = 'Parent commit plus exact sidecar source hashes; local worker receipts are LOCAL_UNSPECIFIED, not an AF source attestation.'
    with (root/'pilot_summary.json').open('x') as f: json.dump(summary, f, indent=2, sort_keys=True, allow_nan=False); f.write('\n')
    print(root/'pilot_summary.json')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True)
    run(p.parse_args().output)


if __name__ == '__main__': main()
