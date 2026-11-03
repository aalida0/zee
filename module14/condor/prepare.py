"""Prepare an unsubmitted D14 HTCondor directory from an exact Git commit."""
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import tarfile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--commit', required=True)
    p.add_argument('--config', required=True, type=Path)
    p.add_argument('--shard', required=True, action='append', type=Path)
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    commit = subprocess.check_output(['git', 'rev-parse', '--verify', a.commit + '^{commit}'], text=True).strip()
    if len({x.name for x in a.shard}) != len(a.shard):
        raise ValueError('Duplicate shard names')
    import re
    if any(not re.fullmatch(r'shard_[0-9]+\.jsonl', x.name) for x in a.shard):
        raise ValueError('Invalid shard filename')
    a.output.mkdir(parents=True, exist_ok=False)
    for d in ('shards', 'logs', 'results', 'receipts'):
        (a.output/d).mkdir()
    archive = a.output/'scan_bundle.tar.gz'
    subprocess.run(['git', 'archive', '--format=tar.gz', '-o', str(archive.resolve()), commit], check=True)
    with tarfile.open(archive, 'r:gz') as tar:
        if tar.pax_headers.get('comment') != commit:
            raise ValueError('Git archive commit mismatch')
        for name in ('worker.sh', 'd14.sub'):
            member = tar.extractfile('module14/condor/' + name)
            if member is None:
                raise ValueError('Missing committed Condor file')
            (a.output/name).write_bytes(member.read())
    (a.output/'worker.sh').chmod(0o755)
    h = hashlib.sha256()
    with archive.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    (a.output/'bundle.sha256').write_text(h.hexdigest() + '  scan_bundle.tar.gz\n')
    (a.output/'source_commit.txt').write_text(commit+'\n')
    shutil.copyfile(a.config, a.output/'config.json')
    for shard in a.shard:
        shutil.copyfile(shard, a.output/'shards'/shard.name)
    (a.output/'shards.txt').write_text(''.join(x.name+'\n' for x in a.shard))
    print(commit, h.hexdigest(), len(a.shard))

if __name__ == '__main__':
    main()
