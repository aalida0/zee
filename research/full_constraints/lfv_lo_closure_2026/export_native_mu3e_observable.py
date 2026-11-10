#!/usr/bin/env python3
"""Read-only export of native SARAH/SPheno mu->3e observable body.

The existing source ZIP contains generated Wilson coefficients but not
BR1LeptonTo3Leptons in LowEnergy_ZeeTypeII.f90. Hash-check the original
generated source and recover only the matching observable file(s).
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[3]
LOCK_REL = Path('research/full_constraints/lfv/SOURCE_TO_CODE_SOURCES.json')
TARGET_RE = re.compile(r'(?i)\bBR1LeptonTo3Leptons\b')
MAX_FILE_BYTES = 30_000_000


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def candidate_paths(pinned_generated):
    model_root = pinned_generated.parent.parent
    candidates = [model_root/'LowEnergy_ZeeTypeII.f90',
                  model_root/'LowEnergy.f90',
                  model_root/'Observables'/'LowEnergy_ZeeTypeII.f90']
    candidates.extend(sorted(model_root.glob('LowEnergy*.f90')))
    return list(dict.fromkeys(candidates))


def run(lock, output, generated_override=None):
    records = {x['id']: x for x in json.loads(Path(lock).read_text())['artifacts']}
    pin = records['generated']
    gen = Path(generated_override) if generated_override else Path(pin['path_hint'])
    if not gen.is_file():
        raise FileNotFoundError(f'Pinned generated file not found: {gen}')
    if sha(gen.read_bytes()) != pin['sha256']:
        raise ValueError('Pinned generated source hash mismatch; refusing mismatched build')
    found = []
    for candidate in candidate_paths(gen):
        if not candidate.is_file():
            continue
        if candidate.stat().st_size > MAX_FILE_BYTES:
            raise ValueError(f'Unexpectedly large file: {candidate}')
        raw = candidate.read_bytes()
        if TARGET_RE.search(raw.decode('utf-8', errors='replace')):
            found.append((candidate, raw))
    if not found:
        searched = '\n  '.join(map(str, candidate_paths(gen)))
        raise FileNotFoundError(
            'No generated file containing BR1LeptonTo3Leptons. Locations checked:\n  '+searched)
    if output.exists():
        raise FileExistsError(f'Refusing to overwrite: {output}')
    receipt = {'status': 'GENERATED_OBSERVABLE_EXPORT_ONLY_NOT_PHYSICAL_LFV',
               'original_pinned_generated_sha256': pin['sha256'],
               'files': [{'name': p.name, 'absolute_original_path': str(p),
                          'sha256': sha(raw), 'bytes': len(raw),
                          'marker': 'BR1LeptonTo3Leptons'} for p, raw in found]}
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for i, (p, raw) in enumerate(found):
            archive.writestr(f'{i:02d}_{p.name}', raw)
        archive.writestr('SOURCE_EXPORT_RECEIPT.json', json.dumps(receipt, indent=2)+'\n')
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock', type=Path, default=ROOT/LOCK_REL)
    parser.add_argument('--generated', type=Path, default=None)
    parser.add_argument('--output', type=Path,
                        default=Path.home()/'zee_lfv_mu3e_observable_source.zip')
    args = parser.parse_args()
    try:
        receipt = run(args.lock, args.output, args.generated)
    except (ValueError, FileNotFoundError, FileExistsError, OSError) as exc:
        print('SOURCE_RECOVERY_BLOCKED:', exc, file=sys.stderr)
        return 1
    print('NATIVE_MU3E_OBSERVABLE_EXPORTED', args.output)
    for row in receipt['files']:
        print('SOURCE_SHA256', row['sha256'], row['name'])
    print('NO_PHYSICAL_LFV_CLAIM. Attach this ZIP to the conversation.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
