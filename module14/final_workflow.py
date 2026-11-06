"""No-physics preflight and source-locked final workflow entry points."""
import argparse
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile

from module14.scan import digest, encode, file_sha, publish, temporary
from module14.final_config import ROOT, LIMITATIONS, validate, worker_settings
from module14.conditional_scan.workflow import load


def source_files(root=ROOT):
    """Same source map in a checkout and its Git archive; exclude mutable evidence."""
    tracked = None
    if (Path(root)/'.git').exists():
        tracked = set(subprocess.check_output(['git', 'ls-files'], cwd=root, text=True).splitlines())
    return {str(p.relative_to(root)): file_sha(p) for name in
            ('module0', 'module1', 'module2', 'module3', 'module4', 'module5', 'module7',
             'module11', 'module12', 'module13', 'module14', 'scripts', 'models', 'validation')
            for p in sorted((Path(root)/name).rglob('*')) if p.is_file()
            and p.suffix in ('.py', '.json', '.m', '.sh', '.sub')
            and (tracked is None or str(p.relative_to(root)) in tracked)
            and not any(v in p.parts for v in ('local', '__pycache__'))}


def check_runtime(config):
    rt = config['runtime']
    if platform.python_version() != rt['python']:
        raise ValueError('Python version does not match runtime pin')
    for name, version in rt['packages'].items():
        if importlib.metadata.version(name) != version:
            raise ValueError('Runtime version mismatch: '+name)
    imports = ['module1.scalar_constraints', 'module1.d10_certificate', 'module2.interface',
               'module14.decays', 'module14.conditional_scan.flavor']
    if config['stages']['lfv']: imports.append('module14.lfv')
    if config['stages']['higgs']: imports += ['Higgs.bounds', 'Higgs.signals', 'Higgs.predictions']
    for name in imports: importlib.import_module(name)
    for name, value in rt['binaries'].items():
        p = Path(value['path'])
        if not p.is_file() or not os.access(p, os.X_OK) or file_sha(p) != value['sha256']:
            raise ValueError('Missing/modified executable: '+name)
        if name == 'd9b_probe':
            evidence = load(ROOT/'validation/module5/d9b_superiso_repair.json')
            if value['sha256'] != evidence['binary_sha256']:
                raise ValueError('D9B executable does not match validated evidence')
    if rt['higgs_data']:
        from module13.higgstools import dataset
        for name, value in rt['higgs_data'].items():
            p = Path(value['path'])
            if not p.is_dir() or digest(dataset(p)['files']) != value['sha256']:
                raise ValueError('Missing/modified HiggsTools data: '+name)
    cache = rt['cache_dir']
    if cache is not None:
        if not Path(cache).is_dir() or not os.access(cache, os.R_OK | os.W_OK):
            raise ValueError('Configured cache must exist and be readable/writable')
        # Existing entries are checked on access by the source-addressed caches;
        # no unverified cache entry is trusted by preflight.
    return {'python': platform.python_version(), 'packages': rt['packages'], 'imports': imports,
            'binaries': rt['binaries'], 'higgs_data': rt['higgs_data'],
            'cache_policy': 'source-addressed; key and value checksum verified on every hit'}


def check_source(config):
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=normal'], cwd=ROOT, text=True)
    if dirty or head != config['source_commit']:
        raise ValueError('Preflight requires a clean checkout at source_commit')
    return head


def preflight(config, backend, output_dir, bundle=None):
    validate(config); head = check_source(config); runtime = check_runtime(config)
    if backend not in ('local', 'condor'): raise ValueError('Unsupported backend')
    if backend == 'condor' and shutil.which('condor_submit') is None:
        raise ValueError('Condor client unavailable; use local backend for fixture verification')
    p = Path(output_dir)
    if not p.is_dir(): raise ValueError('Preflight output directory must already exist')
    free = shutil.disk_usage(p).free
    if free < config['runtime']['disk_mb']*1024**2:
        raise ValueError('Insufficient output filesystem free space')
    # Same-directory exclusive hard links are the worker publication primitive.
    with tempfile.TemporaryDirectory(dir=p, prefix='.d14-preflight-') as tmp:
        a, b = Path(tmp)/'a', Path(tmp)/'b'; a.write_text('probe')
        os.link(a, b)
        try: os.link(a, b)
        except FileExistsError: pass
        else: raise ValueError('Filesystem lacks exclusive atomic hard links')
    if (os.cpu_count() or 0) < config['runtime']['cpus']:
        raise ValueError('Insufficient CPUs')
    memory = os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES')
    if memory < config['runtime']['memory_mb']*1024**2:
        raise ValueError('Insufficient host RAM')
    bundle_sha = None
    if bundle:
        import tarfile
        with tarfile.open(bundle, 'r:gz') as archive:
            if archive.pax_headers.get('comment') != head: raise ValueError('Packed bundle commit mismatch')
            files = source_files()
            for name, sha in files.items():
                member = archive.extractfile(name)
                if member is None or __import__('hashlib').sha256(member.read()).hexdigest() != sha:
                    raise ValueError('Packed bundle source mismatch: '+name)
        bundle_sha = file_sha(bundle)
    report = {'schema': 'd14-preflight-1', 'status': 'PASS', 'backend': backend,
              'config_sha256': digest(config), 'source_commit': head, 'source_files_sha256': source_files(),
              'bundle_sha256': bundle_sha, 'runtime': runtime, 'output_free_bytes': free,
              'atomic_link': 'PASS', 'resources': {k: config['runtime'][k] for k in
                  ('cpus', 'memory_mb', 'disk_mb', 'timeout_seconds')},
              'stages': {k: ('DIAGNOSTIC_ONLY' if v else 'NOT_EVALUATED') for k, v in config['stages'].items()},
              'physics_status': 'PHYSICS_CONDITIONAL', 'limitations': LIMITATIONS,
              'global_acceptance': None}
    report['report_sha256'] = digest(report)
    return report


def require_preflight(config, report, backend=None):
    payload = {k: v for k, v in report.items() if k != 'report_sha256'}
    if (report.get('schema') != 'd14-preflight-1' or report.get('status') != 'PASS'
        or report.get('report_sha256') != digest(payload) or report.get('config_sha256') != digest(config)
        or report.get('source_commit') != config['source_commit']
        or report.get('source_files_sha256') != source_files()
        or (backend is not None and report.get('backend') != backend)):
        raise ValueError('Stale/modified/incompatible preflight report')
    check_runtime(config)


def write_atomic(path, data):
    path = Path(path)
    tmp = temporary(path)
    try:
        Path(tmp).write_text(encode(data)+'\n')
        publish(path, tmp)
    finally:
        if Path(tmp).exists(): Path(tmp).unlink()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    v = sub.add_parser('validate'); v.add_argument('--config', required=True)
    f = sub.add_parser('preflight')
    for name in ('config', 'output-dir', 'output'): f.add_argument('--'+name, required=True)
    f.add_argument('--backend', required=True, choices=('local', 'condor')); f.add_argument('--bundle')
    g = sub.add_parser('generate', help='Requires separate user authorization; never a test command')
    for name in ('config', 'preflight-report', 'output'): g.add_argument('--'+name, required=True)
    g.add_argument('--acknowledge-conditional-physics', action='store_true')
    a = p.parse_args(); c = validate(load(a.config))
    if a.action == 'validate': print('CONFIG_VALID'); return
    if a.action == 'preflight':
        r = preflight(c, a.backend, a.output_dir, a.bundle); write_atomic(a.output, r)
        print('PREFLIGHT_PASS PHYSICS_CONDITIONAL\n'+'\n'.join(LIMITATIONS)); return
    if not a.acknowledge_conditional_physics:
        p.error('Explicit --acknowledge-conditional-physics required')
    check_source(c); require_preflight(c, load(a.preflight_report))
    from module14.scan import generate
    generate(c, a.output)


if __name__ == '__main__': main()
