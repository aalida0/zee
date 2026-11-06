#!/usr/bin/env python3
"""Replay the immutable collected 225-point data and committed production map."""
import argparse
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from module14.conditional_scan.candidate_export import audit
from module14.conditional_scan.workflow import load
from module14.final_export import export
from module14.final_workflow import write_atomic
from module14.scan import file_sha

EXPECTED = '2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset', required=True); p.add_argument('--output', required=True)
    p.add_argument('--export-dir')
    a = p.parse_args()
    if file_sha(a.dataset) != EXPECTED: raise ValueError('Historical dataset checksum mismatch')
    data = load(a.dataset); checked = audit(a.dataset)
    base = ROOT/'module14/conditional_scan'
    hashes = load(base/'production_map_hashes.json')
    for name, want in hashes.items():
        if file_sha(base/name) != want: raise ValueError('Historical production map changed: '+name)
    mapping = load(base/'production_map_13_14.json')
    rows = {(r['id'], r['neutrino']['ordering'], r['neutrino']['family']): r for r in data['rows']}
    for f in mapping['families']:
        row = rows[f['id'], f['ordering'], f['family']]
        if f['module2_input_sha256'] != row['neutrino']['input_sha256'] or f['scalar_sha256'] != row['scalar_sha256']:
            raise ValueError('Historical production family mismatch')
        if not math.isclose(f['sigma_times_BR_pb'], f['sigma_pb']*f['BR_H2_H1Z'], rel_tol=2e-13):
            raise ValueError('Historical production product mismatch')
    report = {'schema': 'd14-saved-evidence-replay-1', 'status': 'PASS', 'dataset_sha256': EXPECTED,
              'scalar_points': len({r['id'] for r in data['rows']}),
              'family_records': checked['verified_family_records'],
              'production_13TeV_rates': sum(r['energy_TeV'] == 13 for r in mapping['rates']),
              'production_14TeV_rates': sum(r['energy_TeV'] == 14 for r in mapping['rates']),
              'production_family_bindings': len(mapping['families']),
              'scope': 'Saved immutable records only; no worker, production or vacuum execution',
              'code_sha256': {name:file_sha(ROOT/name) for name in
                  ('scripts/zee_d14_replay_saved.py', 'module14/final_export.py',
                   'module14/conditional_scan/workflow.py', 'module14/collect.py', 'module14/scan.py')},
              'raw_225_shard_recollection': 'NOT_EVALUATED; original remote manifest/shard/receipt triples not present locally',
              'global_acceptance': None}
    if a.export_dir: report['export'] = export(data, a.export_dir)
    write_atomic(a.output, report)


if __name__ == '__main__': main()
