"""Translate a versioned JSON worker-settings file into worker arguments."""
import json
from pathlib import Path
import subprocess
import sys
import hashlib
import os


def main():
    settings = json.loads(Path('job_settings.json').read_text())
    config = json.loads(Path('config.json').read_text())
    final = config.get('schema') == 'd14-final-config-1'
    if final or Path('pack.json').exists():
        pack = json.loads(Path('pack.json').read_text())
        if pack.get('schema') != 'd14-pack-1': raise ValueError('Unsupported pack schema')
        for name in ('config.json', 'job_settings.json', 'source_commit.txt', 'scan_bundle.tar.gz',
                     'shards/'+Path(sys.argv[1]).name, *(('preflight.json',) if final else ())):
            path = Path(sys.argv[1]) if name.startswith('shards/') else Path(name)
            if hashlib.sha256(path.read_bytes()).hexdigest() != pack['files_sha256'].get(name):
                raise ValueError('Changed pack input: '+name)
        if final:
            from module14.final_config import sha
            sha(pack.get('manifest_sha256'), 'Original manifest SHA256')
            os.environ['ZEE_D14_MANIFEST_SHA256'] = pack['manifest_sha256']
    allowed = {'families', 'perturbativity_limit', 'lfv', 'lfv_tree', 'bsgamma', 'd9b_probe', 'higgs', 'hb_data', 'hs_data', 'cache_dir', 'production_dir'}
    if settings.keys() - allowed:
        raise ValueError('Unsupported job settings')
    command = [sys.executable, '-m', 'module14.scan', 'worker', '--shard', sys.argv[1], '--output', 'results.jsonl', '--receipt', 'receipt.json', '--config', 'config.json']
    if final:
        from module14.final_config import validate, worker_settings
        validate(config)
        if settings != worker_settings(config): raise ValueError('Final worker settings mismatch')
        command += ['--preflight-report', str(Path('preflight.json').resolve())]
    for k,v in settings.items():
        opt = '--'+k.replace('_','-')
        if isinstance(v, bool):
            if v: command.append(opt)
        elif v is not None:
            command.extend((opt, str(v)))
    try:
        return subprocess.call(command, timeout=config['runtime']['timeout_seconds'] if final else None)
    except subprocess.TimeoutExpired:
        print('Shard interrupted by configured timeout; no COMPLETE receipt', file=sys.stderr)
        return 124

if __name__ == '__main__': raise SystemExit(main())
