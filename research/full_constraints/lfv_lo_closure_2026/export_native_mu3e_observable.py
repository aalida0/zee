#!/usr/bin/env python3
"""Read-only export of native SARAH/FlavorKit mu->3e observable source.

SARAH 4.15 uses Calculate_Lto3Lp in FlavorKit_Observables_[Model].f90.
Older SARAH used BR1LeptonTo3Leptons in LowEnergy_[Model].f90.
If neither model source exists, export the installed SARAH generic Lto3Lp
process body separately; do NOT call that a model-specific validated rate.
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
MARKER_RE = re.compile(r'(?i)\b(Calculate_Lto3Lp|BR1LeptonTo3Leptons)\b')
MAX_FILE_BYTES = 30_000_000


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def model_root_from(pinned_generated):
    parent = pinned_generated.parent
    return parent.parent if parent.name.lower() == 'observables' else parent


def candidate_paths(pinned_generated):
    root = model_root_from(pinned_generated)
    paths = []
    for folder in (root, root/'Observables'):
        for pattern in ('FlavorKit_Observables*.f90', 'LowEnergy*.f90',
                        '*Lto3Lp*.f90', '*LeptonTo3Leptons*.f90'):
            paths.extend(sorted(folder.glob(pattern)))
    return list(dict.fromkeys(paths))


def generic_candidates(sarah_root):
    if sarah_root is None:
        return []
    root = Path(sarah_root)/'FlavorKit'/'LFV'/'Processes'
    if not root.is_dir():
        return []
    paths = []
    for pattern in ('Lto3Lp.f90','*Lto3Lp*.f90','*3Leptons*.f90'):
        paths.extend(sorted(root.glob(pattern)))
    return list(dict.fromkeys(paths))


def run(lock, output, generated_override=None, sarah_root=None):
    records = {x['id']: x for x in json.loads(Path(lock).read_text())['artifacts']}
    pin = records['generated']
    gen = Path(generated_override) if generated_override else Path(pin['path_hint'])
    if not gen.is_file():
        raise FileNotFoundError(f'Pinned generated file not found: {gen}')
    if sha(gen.read_bytes()) != pin['sha256']:
        raise ValueError('Pinned generated source hash mismatch; refusing mismatched build')

    found = []
    searched = []
    for candidate in candidate_paths(gen):
        if not candidate.is_file():
            continue
        searched.append(str(candidate))
        if candidate.stat().st_size > MAX_FILE_BYTES:
            raise ValueError(f'Unexpectedly large file: {candidate}')
        raw = candidate.read_bytes()
        if MARKER_RE.search(raw.decode('utf-8',errors='replace')):
            found.append((candidate,raw,'MODEL_SPECIFIC'))

    if not found:
        for candidate in generic_candidates(sarah_root):
            if candidate.stat().st_size > MAX_FILE_BYTES:
                raise ValueError(f'Unexpectedly large generic file: {candidate}')
            found.append((candidate,candidate.read_bytes(),'GENERIC_TEMPLATE_ONLY'))

    if not found:
        root = model_root_from(gen)
        raise FileNotFoundError(
            'No Calculate_Lto3Lp or BR1LeptonTo3Leptons observable at '
            f'{root} or its Observables directory. The model observable may not '
            'have been generated. Supply --sarah-root /path/to/SARAH for '
            'FlavorKit/LFV/Processes/Lto3Lp.f90. A public reference exists at '
            'restrepo/Zee-Toolbox/SPHENO/Zee/FlavorKit_Observables_Zee.f90; '
            'this is an older model and NOT a full ZeeTypeII physics result.')
    if output.exists():
        raise FileExistsError(f'Refusing to overwrite existing archive: {output}')
    status = ('MODEL_SPECIFIC_OBSERVABLE_NOT_VALIDATED'
              if found[0][2]=='MODEL_SPECIFIC' else 'GENERIC_TEMPLATE_ONLY')
    receipt = {'status': status, 'original_pinned_generated_sha256': pin['sha256'],
               'searched_model_files': searched,
               'notes': 'No physical mu3e rate, matching or scan acceptance claimed.',
               'files': []}
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for i,(candidate,raw,scope) in enumerate(found):
            name = f'{i:02d}_{candidate.name}'
            archive.writestr(name,raw)
            receipt['files'].append({
                'name':candidate.name,'original_path':str(candidate),
                'archive_name':name,'sha256':sha(raw),'bytes':len(raw),'scope':scope
            })
        archive.writestr('SOURCE_EXPORT_RECEIPT.json',
                         json.dumps(receipt,indent=2)+'\n')
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise IOError('Archive corruption')
        for item in receipt['files']:
            if sha(archive.read(item['archive_name'])) != item['sha256']:
                raise IOError('Archived SHA256 mismatch')
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
