"""Prepare an unsubmitted D14 HTCondor directory from an exact Git commit."""
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import tarfile
import json


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--commit', required=True)
    p.add_argument('--config', required=True, type=Path)
    p.add_argument('--shard', required=True, action='append', type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--job-settings', type=Path)
    p.add_argument('--preflight-report', type=Path)
    p.add_argument('--manifest', type=Path)
    p.add_argument('--generation-receipt', type=Path)
    p.add_argument('--acknowledge-conditional-physics', action='store_true')
    a = p.parse_args()
    commit = subprocess.check_output(['git', 'rev-parse', '--verify', a.commit + '^{commit}'], text=True).strip()
    config = json.loads(a.config.read_text())
    final = config.get('schema') == 'd14-final-config-1'
    settings = None
    if final:
        # Source checkout imports are explicit for direct script invocation.
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        from module14.final_config import validate, validate_manifest, worker_settings
        from module14.final_workflow import check_source, require_preflight
        from module14.conditional_scan.workflow import load
        from module14.scan import digest, file_sha
        validate(config)
        if not a.preflight_report or not a.acknowledge_conditional_physics:
            raise ValueError('Final prepare requires preflight report and --acknowledge-conditional-physics')
        check_source(config); require_preflight(config, load(a.preflight_report), 'condor')
        if commit != config['source_commit']: raise ValueError('Config/packed commit mismatch')
        if not a.manifest or not a.generation_receipt:
            raise ValueError('Final prepare requires original manifest and generation receipt')
        validate_manifest(a.manifest, config)
        generation = load(a.generation_receipt)
        if (generation.get('schema') != 'd14-generation-1' or generation.get('manifest_sha256') != file_sha(a.manifest)
            or generation.get('config_sha256') != digest(config) or generation.get('source_commit') != commit
            or generation.get('template_sha256') != config['template_sha256']
            or generation.get('shards_sha256') != {s.name:file_sha(s) for s in a.shard}):
            raise ValueError('Original generation receipt mismatch')
        joined = hashlib.sha256()
        for s in sorted(a.shard, key=lambda s:s.name):
            with s.open('rb') as f:
                for chunk in iter(lambda:f.read(1024*1024),b''):joined.update(chunk)
        if joined.hexdigest() != file_sha(a.manifest):
            raise ValueError('Shards are not the exact original manifest partition')
        settings = worker_settings(config)
        if a.job_settings and load(a.job_settings) != settings:
            raise ValueError('Final job-settings differ from approved config')
        seen = set()
        for shard in a.shard:
            ids = validate_manifest(shard, config, require_full=False)
            if len(ids) != config['shard_size'] or ids & seen:
                raise ValueError('Invalid shard size or duplicate point IDs')
            seen.update(ids)
        if len(seen) != config['count']: raise ValueError('Final prepare requires all immutable shards')
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
    if final:
        (a.output/'job_settings.json').write_text(json.dumps(settings, sort_keys=True)+'\n')
        shutil.copyfile(a.preflight_report, a.output/'preflight.json')
    elif a.job_settings:
        shutil.copyfile(a.job_settings, a.output/'job_settings.json')
    else:
        (a.output/'job_settings.json').write_text('{}\n')
    for shard in a.shard:
        shutil.copyfile(shard, a.output/'shards'/shard.name)
    (a.output/'shards.txt').write_text(''.join(x.name+'\n' for x in a.shard))
    # Bind every mutable transfer input independently of the Git archive hash.
    # Old prepared directories without this file remain supported by worker.sh.
    files = [a.output/'config.json', a.output/'job_settings.json', a.output/'source_commit.txt',
             a.output/'scan_bundle.tar.gz', *(a.output/'shards'/s.name for s in a.shard)]
    if final: files.append(a.output/'preflight.json')
    hashes = {str(f.relative_to(a.output)): hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
    pack = {'schema': 'd14-pack-1', 'files_sha256': hashes}
    if final: pack['manifest_sha256'] = generation['manifest_sha256']
    (a.output/'pack.json').write_text(json.dumps(pack, sort_keys=True)+'\n')
    if final:
        sub = (a.output/'d14.sub').read_text()
        sub = sub.replace('queue shard from shards.txt', '')
        sub = sub.replace('request_memory = 2 GB', 'request_memory = '+str(config['runtime']['memory_mb'])+' MB')
        sub = sub.replace('request_disk = 2 GB', 'request_disk = '+str(config['runtime']['disk_mb'])+' MB')
        sub = sub.replace('job_settings.json,shards/$(shard)', 'job_settings.json,pack.json,preflight.json,shards/$(shard)')
        sub += '\nperiodic_remove = (JobStatus == 2) && ((time() - JobCurrentStartDate) > '+str(config['runtime']['timeout_seconds'])+')\nqueue shard from shards.txt\n'
        (a.output/'d14.sub').write_text(sub)
    else:
        sub = (a.output/'d14.sub').read_text().replace('job_settings.json,shards/$(shard)', 'job_settings.json,pack.json,shards/$(shard)')
        (a.output/'d14.sub').write_text(sub)
    print(commit, h.hexdigest(), len(a.shard))

if __name__ == '__main__':
    main()
