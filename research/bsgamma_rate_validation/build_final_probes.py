"""Replay the frozen D9B patch locally; never change historical evidence."""
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
from pilot import HERE, ROOT, digest, write_json

LOCAL = HERE / 'local'
ARCHIVE_SHA = '7f8400e98ae80deac50af64486b980891e1630d729a0a4660ca309a4d7706b5f'
PATCH_SHA = 'd0607f3e9dd12bc0e2fce6c0102c5c6e756d1d9d9767b2444bca3abee890e62b'


def build():
    archive = LOCAL / 'superiso_v5.0.tgz'
    patch = ROOT / 'module5/patches/d9b_superiso_v5.0.patch'
    assert digest(archive) == ARCHIVE_SHA
    assert digest(patch) == PATCH_SHA
    evidence = {'archive_sha256': digest(archive), 'patch_sha256': digest(patch),
                'license': 'SuperIso GPL-3.0-or-later; EOS GPL-2.0-only; no combined binary',
                'builds': {}}
    for label in ('original', 'd9b'):
        dest = Path(tempfile.mkdtemp(prefix='final_si_' + label + '_', dir=LOCAL))
        # Fresh build only, to avoid silently accepting modified external sources.
        with tarfile.open(archive) as t:
            for member in t.getmembers():
                if not (dest / member.name).resolve().is_relative_to(dest.resolve()):
                    raise ValueError('Unsafe archive path')
                if member.issym() or member.islnk():
                    raise ValueError('Unexpected link')
            t.extractall(dest)
        src = dest / 'SuperIso_v5.0'
        commands = []
        if label == 'd9b':
            commands.append((['patch', '--batch', '-p1', '-i', str(patch)], src))
        commands.append((['make', '-B'], src))
        exe = LOCAL / ('final_si_' + label + '_probe')
        commands.append((['gcc', '-O2', *(['-DD9B'] if label == 'd9b' else []),
                         '-I', str(src / 'src'), str(HERE / 'final_superiso_probe.c'),
                         str(src / 'src/libsuperiso.a'), '-lm', '-o', str(exe)], HERE))
        logs = []
        for command, cwd in commands:
            r = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
            logs.append(dict(command=command, cwd=str(cwd), exit_code=r.returncode,
                             stdout=r.stdout, stderr=r.stderr))
            if r.returncode:
                write_json(LOCAL / ('final_build_' + label + '.json'), logs)
                raise RuntimeError((r.stderr + r.stdout)[-2000:])
        log = LOCAL / ('final_build_' + label + '.json')
        write_json(log, logs)
        evidence['builds'][label] = {'commands': [x['command'] for x in logs],
            'client_sha256': digest(HERE / 'final_superiso_probe.c'),
            'log_sha256': digest(log), 'binary_sha256': digest(exe),
            'library_sha256': digest(src / 'src/libsuperiso.a'),
            'source_sha256': {str(p.relative_to(src)): digest(p) for p in sorted(src.rglob('*'))
                              if p.is_file() and p.suffix in ('.c', '.h', '.md')},
            'exit_codes': [x['exit_code'] for x in logs]}
    write_json(LOCAL / 'final_build.json', evidence)
    print('Built original SuperIso and exact D9B replay.')


if __name__ == '__main__':
    build()
