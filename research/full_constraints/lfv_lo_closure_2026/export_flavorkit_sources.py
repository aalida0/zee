#!/usr/bin/env python3
"""Export source-hashed generated Zee/FlavorKit Fortran for independent LFV checks.

Read-only. Uses research/full_constraints/lfv/SOURCE_TO_CODE_SOURCES.json.
No models are regenerated, no executables are run, and no Git state is changed.
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
LOCK = ROOT / 'research/full_constraints/lfv/SOURCE_TO_CODE_SOURCES.json'
NEEDED = ('generated', 'couplings', 'loops')
MAX_BYTES = 80_000_000


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_index(text: str) -> dict:
    """Lightweight lexical index, NOT evidence of topology completeness."""
    subs = re.findall(r'(?im)^\s*subroutine\s+([a-z][a-z0-9_]*)\s*\(', text)
    calls = re.findall(r'(?im)^\s*call\s+([a-z][a-z0-9_]*)\s*\(', text)
    return {
        'subroutines_total': len(subs),
        'subroutines_lfv_named': sorted(set(s for s in subs if re.search(r'peng|box|photon|gamma|4l|4q|mono',s,re.I))),
        'lfv_related_call_names': sorted(set(s for s in calls if re.search(r'peng|box|photon|gamma|4l|4q|mono',s,re.I))),
        'token_occurrences': {key: len(re.findall(r'\b'+re.escape(key)+r'\b',text,re.I))
                              for key in ('K1L','K1R','K2L','K2R','BO4lVLL','CalculatePengV4L','CalculateBox4L','OlluuVLL','OllddVLL')},
        'note': 'Text token counts, not verified independent physical operators.',
    }


def collect(lock: Path, overrides: dict[str, Path]) -> tuple[dict, dict]:
    contract = json.loads(lock.read_text())
    entries = {e['id']: e for e in contract['artifacts']}
    missing = [k for k in NEEDED if k not in entries]
    if missing:
        raise ValueError('Missing required source IDs in hash contract: '+','.join(missing))
    report = {'status': 'SOURCE_EXPORT_ONLY_NO_PHYSICS_CLAIM',
              'original_lock_sha256': sha256(lock.read_bytes()), 'entries': {}}
    payload = {}
    errors = []
    for key in NEEDED:
        record = entries[key]
        candidate = overrides.get(key, Path(record['path_hint']).expanduser())
        note = {'file': candidate.name, 'sha256_expected': record['sha256'],
                'found': candidate.is_file()}
        if not note['found']:
            errors.append(f'{key}: source not found at {candidate}')
            report['entries'][key] = note
            continue
        if candidate.stat().st_size > MAX_BYTES:
            errors.append(f'{key}: source exceeds {MAX_BYTES} bytes')
            report['entries'][key] = note
            continue
        raw = candidate.read_bytes()
        digest = sha256(raw)
        note.update(size_bytes=len(raw), sha256_actual=digest,
                    hash_matches_contract=(digest == record['sha256']))
        if digest != record['sha256']:
            errors.append(f'{key}: SHA256 MISMATCH at {candidate}; actual {digest}')
        else:
            try:
                content = raw.decode('utf-8')
            except UnicodeDecodeError:
                errors.append(f'{key}: source is not UTF-8')
            else:
                note['lexical_index'] = source_index(content)
                payload[key+'.f90'] = raw
        report['entries'][key] = note
    if errors:
        raise RuntimeError('\n'.join(errors)+'\nNo archive was produced. You may override paths using --generated/--couplings/--loops.')
    return report, payload


def export(lock: Path, output: Path, overrides: dict[str,Path]) -> dict:
    report, payload = collect(lock, overrides)
    if output.exists():
        raise FileExistsError(f'Refusing to overwrite existing archive: {output}')
    output.parent.mkdir(parents=True, exist_ok=True)
    names = sorted(payload)
    names += ['SOURCE_EXPORT_RECEIPT.json']
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in names:
            data = (json.dumps(report, indent=2, sort_keys=True).encode('utf-8')+b'\n'
                    if name == 'SOURCE_EXPORT_RECEIPT.json' else payload[name])
            info = zipfile.ZipInfo(name, date_time=(1980,1,1,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        assert set(archive.namelist()) == set(names)
        for name in names[:-1]:
            assert sha256(archive.read(name)) == report['entries'][name[:-4]]['sha256_expected']
    report['archive'] = str(output)
    report['archive_size_bytes'] = output.stat().st_size
    return report


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lock',type=Path,default=LOCK)
    parser.add_argument('--output',type=Path,default=Path.home()/'zee_lfv_source_bundle.zip')
    for key in NEEDED:
        parser.add_argument('--'+key,type=Path,help='Override location of hash-pinned '+key+' Fortran')
    args=parser.parse_args(argv)
    try:
        overrides={key:getattr(args,key) for key in NEEDED if getattr(args,key) is not None}
        result=export(args.lock,args.output.expanduser(),overrides)
    except (OSError, ValueError, RuntimeError) as exc:
        print('EXPORT_BLOCKED:',exc,file=sys.stderr)
        return 1
    print('SOURCE_EXPORT_PASS',result['archive'])
    print('ARCHIVE_BYTES',result['archive_size_bytes'])
    for key in NEEDED:
        print('HASH_VERIFIED',key,result['entries'][key]['sha256_actual'])
    print('NEXT: attach this ZIP to the ChatGPT conversation for full one-loop coefficient review.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
