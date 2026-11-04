"""Translate a versioned JSON worker-settings file into worker arguments."""
import json
from pathlib import Path
import subprocess
import sys


def main():
    settings = json.loads(Path('job_settings.json').read_text())
    allowed = {'families', 'perturbativity_limit', 'lfv', 'lfv_tree', 'bsgamma', 'd9b_probe', 'higgs', 'hb_data', 'hs_data', 'cache_dir', 'production_dir'}
    if settings.keys() - allowed:
        raise ValueError('Unsupported job settings')
    command = [sys.executable, '-m', 'module14.scan', 'worker', '--shard', sys.argv[1], '--output', 'results.jsonl', '--receipt', 'receipt.json', '--config', 'config.json']
    for k,v in settings.items():
        opt = '--'+k.replace('_','-')
        if isinstance(v, bool):
            if v: command.append(opt)
        elif v is not None:
            command.extend((opt, str(v)))
    return subprocess.call(command)

if __name__ == '__main__': raise SystemExit(main())
