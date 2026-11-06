"""Materialize immutable historical pilot bytes; never generate physics inputs."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

from module14.scan import digest, encode, file_sha

BASE = Path(__file__).resolve().parent


def saved():
    hashes = json.loads((BASE/'hashes.json').read_text())['files_sha256']
    content = {}
    for name, sha in hashes.items():
        p = BASE/name
        data = p.read_bytes() if p.exists() else gzip.decompress((BASE/(name+'.gz')).read_bytes())
        if hashlib.sha256(data).hexdigest() != sha: raise ValueError('Frozen fixture checksum mismatch: '+name)
        content[name] = data
    return content


def materialize(directory, ids=None, shard_size=None):
    """Sliced receipts are explicit replay fixtures, never remote attestations."""
    content = saved(); directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    config = json.loads(content['pilot_config.json'])
    manifest = [json.loads(s) for s in content['pilot_manifest.jsonl'].splitlines()]
    outputs = {r['id']: r for r in map(json.loads, content['pilot_output.jsonl'].splitlines())}
    if ids is not None: manifest = [r for r in manifest if r['id'] in ids]
    path = directory/'manifest.jsonl'; path.write_text(''.join(encode(r)+'\n' for r in manifest))
    size = shard_size or len(manifest); triples = []
    for start in range(0, len(manifest), size):
        selected = manifest[start:start+size]
        shard = directory/f'shard_{start//size:06d}.jsonl'; output = directory/f'output_{start//size:06d}.jsonl'
        receipt = directory/f'receipt_{start//size:06d}.json'
        shard.write_text(''.join(encode(r)+'\n' for r in selected))
        output.write_text(''.join(encode(outputs[r['id']])+'\n' for r in selected))
        rec = json.loads(content['pilot_receipt.json'])
        counts = Counter()
        for r in selected:
            out = outputs[r['id']]
            for name, gate in out['gates'].items(): counts[name+':'+gate['assessment']] += 1
            for n in out['neutrino'] if isinstance(out['neutrino'], list) else []:
                counts['neutrino:'+n['ordering']+':'+n['status']] += 1
            counts['bsgamma:'+out['bsgamma']['status']] += 1
            for stage in ('lfv', 'widths', 'higgstools'):
                for order in ('NO', 'IO'):
                    statuses = [n['status'] for n in out[stage] if n['ordering'] == order] if isinstance(out[stage], list) else ['NOT_EVALUATED']*rec['families']
                    for st in statuses: counts[stage+':'+order+':'+('DIAGNOSTIC_ONLY' if st == 'PARTIAL' else st)] += 1
        rec.update(input_count=len(selected), output_count=len(selected), counts=counts,
                   shard_sha256=file_sha(shard), output_sha256=file_sha(output),
                   replay_slice={'original_receipt_sha256': hashlib.sha256(content['pilot_receipt.json']).hexdigest(),
                                 'selected_ids': [r['id'] for r in selected], 'remote_attestation': False})
        receipt.write_text(encode(rec)+'\n'); triples.append((shard, output, receipt))
    return config, path, triples
