"""Strict final-run configuration, without drawing or evaluating any point."""
import math
from pathlib import Path
import re

from module1.scalar_constraints import validate_input
from module14.scan import digest, file_sha
from module14.conditional_scan.workflow import load

ROOT = Path(__file__).resolve().parents[1]
RANGES = {'mH2', 'mH1_fraction', 'tanbeta', 'delta_alpha', 'gamma', 'lc',
          'k1', 'k2', 'k12', 'mh2_splitting', 'ma_splitting', 'm12sq_factor'}
PACKAGES = {'numpy': '2.2.6', 'scipy': '1.15.3', 'mpmath': '1.3.0', 'sympy': '1.14.0',
            'matplotlib': '3.10.9'}
LIMITATIONS = [
    'B->Xs gamma: Eq.(4) conditional LO-NP diagnostic; physical status UNKNOWN; NP theory sigma null.',
    'LFV: PARTIAL coherent implemented subset; additional Zee/two-loop amplitudes UNKNOWN.',
    'Vacuum: D10 sufficient certificate only; certificate misses UNKNOWN and continue to neutrino families.',
    'HiggsTools: approximate h125 DIAGNOSTIC_ONLY; unsupported heavy/charged channels NOT_EVALUATED.',
    'Production: optional exact source-bound inputs at 13 and 14 TeV separately; absent rates null.',
    'No global acceptance, calibrated production uncertainty, detector efficiency or sensitivity claim.'
]


def keys(value, expected, label):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(label + ': required keys ' + ', '.join(sorted(expected)))


def number(x, label, positive=False):
    if type(x) not in (int, float) or not math.isfinite(x) or (positive and x <= 0):
        raise ValueError(label + ': finite ' + ('positive ' if positive else '') + 'number required')
    return x


def integer(x, label, minimum=1):
    if type(x) is not int or x < minimum:
        raise ValueError(label + ': integer >= ' + str(minimum) + ' required; fill deliberate placeholders')
    return x


def sha(x, label, length=64):
    if not isinstance(x, str) or not re.fullmatch('[0-9a-f]{'+str(length)+'}', x):
        raise ValueError(label + ': full lowercase source hash required')


def pin(value, label):
    keys(value, ('path', 'sha256'), label)
    if not isinstance(value['path'], str) or not value['path'].strip():
        raise ValueError(label + ': explicit path required')
    if not Path(value['path']).is_absolute():
        raise ValueError(label + ': runtime resources require an explicit absolute path')
    sha(value['sha256'], label)


def validate(config, root=ROOT):
    keys(config, ('schema', 'source_commit', 'template', 'template_sha256', 'count', 'seed',
                  'shard_size', 'sampling_mode', 'cascade_margin_GeV', 'arms', 'families',
                  'perturbativity_limit', 'stages', 'runtime'), 'config')
    if config['schema'] != 'd14-final-config-1' or config['sampling_mode'] != 'correlated_heavy_v1':
        raise ValueError('Unsupported final schema/sampling mode')
    sha(config['source_commit'], 'source_commit', 40)
    integer(config['count'], 'count'); integer(config['seed'], 'seed', 0)
    integer(config['shard_size'], 'shard_size')
    if config['count'] % config['shard_size']:
        raise ValueError('count must be divisible by shard_size')
    integer(config['families'], 'families')
    number(config['perturbativity_limit'], 'perturbativity_limit', True)
    if number(config['cascade_margin_GeV'], 'cascade_margin_GeV') != 20:
        raise ValueError('Current correlated generator supports exactly the documented 20 GeV cascade margin')
    path = Path(config['template'])
    if path.is_absolute() or '..' in path.parts or not (Path(root)/path).is_file():
        raise ValueError('template must be an existing source-relative file')
    sha(config['template_sha256'], 'template_sha256')
    if file_sha(Path(root)/path) != config['template_sha256']:
        raise ValueError('template checksum mismatch')
    template = load(Path(root)/path)
    validate_input(template)
    if not isinstance(config['arms'], list) or not config['arms']:
        raise ValueError('Select at least one sampling arm explicitly')
    names = set()
    for arm in config['arms']:
        keys(arm, ('name', 'weight', 'ranges'), 'arm')
        if not isinstance(arm['name'], str) or not re.fullmatch('[A-Za-z0-9_]+', arm['name']) or arm['name'] in names:
            raise ValueError('Arm names must be unique alphanumeric identities')
        names.add(arm['name']); integer(arm['weight'], 'arm weight')
        keys(arm['ranges'], RANGES, 'arm ranges')
        r = arm['ranges']
        for name, bounds in r.items():
            if not isinstance(bounds, list) or len(bounds) != 2:
                raise ValueError('Range requires two bounds: '+name)
            for b in bounds: number(b, name)
            if bounds[0] > bounds[1]: raise ValueError('Reversed range: '+name)
        for name in ('mH2', 'tanbeta', 'mH1_fraction'):
            if r[name][0] <= 0: raise ValueError('Positive range required: '+name)
        if r['mH1_fraction'][1] >= 1:
            raise ValueError('Charged masses must be ordered: mH1_fraction < 1')
        if not -math.pi/2 <= r['gamma'][0] <= r['gamma'][1] <= math.pi/2:
            raise ValueError('gamma outside signed principal interval')
        if r['mH2'][1]*(1-r['mH1_fraction'][0]) <= template['electroweak']['mZ']+20:
            raise ValueError('Arm cannot reach the on-shell cascade margin')
        # md is a convex mass-squared combination; this conservative bound
        # rejects ranges that can make either neutral mass nonpositive.
        md_min = r['mH2'][0]*r['mH1_fraction'][0]
        for name in ('mh2_splitting', 'ma_splitting'):
            if md_min+r[name][0] <= 0: raise ValueError('Neutral mass range can be nonpositive: '+name)
    st = config['stages']
    keys(st, ('lfv', 'lfv_tree', 'bsgamma', 'higgs', 'conditional_flavor'), 'stages')
    if any(type(v) is not bool for v in st.values()): raise ValueError('Stage choices must be boolean')
    if st['lfv_tree'] and not st['lfv']: raise ValueError('lfv_tree requires lfv')
    if not st['conditional_flavor']: raise ValueError('Final export requires separate conditional_flavor sidecar')
    rt = config['runtime']
    keys(rt, ('python', 'packages', 'binaries', 'higgs_data', 'cpus', 'memory_mb',
              'disk_mb', 'timeout_seconds', 'cache_dir'), 'runtime')
    if not isinstance(rt['python'], str) or not re.fullmatch(r'3\.10\.\d+', rt['python']):
        raise ValueError('Pin an exact Python 3.10 patch version')
    expected = dict(PACKAGES, **({'HiggsTools': '1.1.3'} if st['higgs'] else {}))
    if rt['packages'] != expected: raise ValueError('runtime packages must equal the validated pinned versions: '+str(expected))
    keys(rt['binaries'], ('d9b_probe',) if st['bsgamma'] else (), 'binaries')
    for name, value in rt['binaries'].items(): pin(value, name)
    keys(rt['higgs_data'], ('HB', 'HS') if st['higgs'] else (), 'higgs_data')
    for name, value in rt['higgs_data'].items(): pin(value, name)
    if integer(rt['cpus'], 'cpus') != 1: raise ValueError('Current worker supports one CPU per shard')
    if integer(rt['memory_mb'], 'memory_mb') < 2048 or integer(rt['disk_mb'], 'disk_mb') < 2048:
        raise ValueError('Request at least 2048 MB RAM and disk')
    integer(rt['timeout_seconds'], 'timeout_seconds')
    if rt['cache_dir'] is not None and (not isinstance(rt['cache_dir'], str) or not rt['cache_dir'].strip()):
        raise ValueError('cache_dir must be null or explicit path')
    if rt['cache_dir'] is not None and not Path(rt['cache_dir']).is_absolute():
        raise ValueError('cache_dir requires an explicit absolute path')
    return config


def worker_settings(config):
    rt, st = config['runtime'], config['stages']
    return dict(families=config['families'], perturbativity_limit=config['perturbativity_limit'],
                **{k: st[k] for k in ('lfv', 'lfv_tree', 'bsgamma', 'higgs')},
                d9b_probe=rt['binaries'].get('d9b_probe', {}).get('path'),
                hb_data=rt['higgs_data'].get('HB', {}).get('path'),
                hs_data=rt['higgs_data'].get('HS', {}).get('path'), cache_dir=rt['cache_dir'])


def validate_manifest(path, config, require_full=True):
    from module14.conditional_scan.workflow import lines
    seen = set(); arms = {a['name'] for a in config['arms']}
    for row in lines(path):
        if type(row['id']) is not int or row['id'] < 0 or row['id'] >= config['count'] or row['id'] in seen:
            raise ValueError('Duplicate or invalid manifest ID')
        seen.add(row['id'])
        if row['config_sha256'] != digest(config) or row['scalar_sha256'] != digest(row['scalar']) or row['arm'] not in arms:
            raise ValueError('Manifest config/card/arm mismatch')
        validate_input(row['scalar'])
        if config.get('schema') == 'd14-final-config-1':
            p = row['scalar']['physical']
            if p['mH2'] <= p['mH1']+row['scalar']['electroweak']['mZ']+config['cascade_margin_GeV']:
                raise ValueError('Manifest cascade margin mismatch')
    if require_full and len(seen) != config['count']:
        raise ValueError('Manifest count does not match the immutable config')
    return seen
