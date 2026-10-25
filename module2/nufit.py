"""Read one published NuFIT 6.0/6.1 profiled delta-chi-squared section.

The release notes define native coordinates, not a joint likelihood. A file's
release/ordering/selection are declared by the caller; SHA256 binds its bytes
but does not authenticate their origin. No projections or Gaussian fits are
added together. No extrapolation or automatic minimum subtraction is used.
"""
import hashlib
import itertools
import lzma
import math
from pathlib import Path
import re
from urllib.parse import urlparse
import numpy as np
from .core import real_number

SECTIONS = (
    'T23/DMA/DCP', 'T13/T12', 'T13/DMS', 'T12/DMS', 'T13/T23',
    'T13/DMA', 'T23/DMA', 'T13/DCP', 'T23/DCP', 'DMA/DCP',
    'T12/T23', 'T12/DCP', 'T12/DMA', 'DMS/T23', 'DMS/DCP',
    'DMS/DMA', 'T13', 'T12', 'T23', 'DCP', 'DMS', 'DMA')
RELEASES = {
    'NuFIT 6.0 (2024)': ('IC19 without SK atmospheric data', 'IC24 with SK atmospheric data'),
    'NuFIT 6.1 (2025)': ('IC23 without SK atmospheric data', 'IC24 with SK atmospheric data')}


def read_projection(path, expected_sha256, section):
    """Return native axes and Cartesian grid from an XZ or UTF-8 text archive."""
    if section not in SECTIONS or re.fullmatch('[0-9a-f]{64}', expected_sha256) is None:
        raise ValueError('Invalid NuFIT section or archive SHA256')
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise ValueError('Cannot read NuFIT archive: '+str(exc)) from exc
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ValueError('NuFIT archive SHA256 mismatch')
    try:
        text = (lzma.decompress(raw) if raw.startswith(b'\xfd7zXZ\x00') else raw).decode('utf-8')
    except (lzma.LZMAError, UnicodeError) as exc:
        raise ValueError('Invalid NuFIT archive encoding/compression') from exc
    rows, active, seen = [], False, False
    dimension = len(section.split('/'))
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            tag = line[1:].strip().split()
            if tag and tag[0] in SECTIONS:
                active = tag[0] == section
                if active and seen:
                    raise ValueError('Repeated NuFIT projection section')
                seen |= active
            continue
        if active:
            try:
                values = [float(s) for s in line.split('#', 1)[0].split()]
            except ValueError as exc:
                raise ValueError('Malformed NuFIT numeric row') from exc
            if len(values) != dimension+1 or not np.isfinite(values).all():
                raise ValueError('Invalid NuFIT row columns or nonfinite value')
            rows.append(values)
    if not rows:
        raise ValueError('Missing or empty NuFIT projection section')
    rows = np.asarray(rows)
    axes = [np.unique(rows[:, i]) for i in range(dimension)]
    shape = tuple(len(a) for a in axes)
    if math.prod(shape) != len(rows):
        raise ValueError('NuFIT projection is not a complete Cartesian grid')
    grid = np.full(shape, np.nan)
    for row in rows:
        index = tuple(int(np.searchsorted(a, row[i])) for i, a in enumerate(axes))
        if not np.isnan(grid[index]):
            raise ValueError('Duplicate NuFIT grid node')
        grid[index] = row[-1]
    if not np.isfinite(grid).all():
        raise ValueError('Incomplete NuFIT grid')
    return axes, grid


def interpolate(axes, grid, point):
    """Multilinear interpolation on native axes; None outside tabulated domain."""
    if len(point) != len(axes) or grid.shape != tuple(len(a) for a in axes):
        raise ValueError('NuFIT interpolation dimensions mismatch')
    brackets = []
    for axis, coordinate in zip(axes, point):
        if not axis[0] <= coordinate <= axis[-1]:
            return None
        hi = int(np.searchsorted(axis, coordinate))
        if hi == len(axis):
            hi -= 1
        if axis[hi] == coordinate:
            brackets.append([(hi, 1.)])
        else:
            lo = hi-1
            fraction = (coordinate-axis[lo])/(axis[hi]-axis[lo])
            brackets.append([(lo, 1-fraction), (hi, fraction)])
    return float(sum(grid[tuple(i for i, _ in corner)]*math.prod(w for _, w in corner)
                     for corner in itertools.product(*brackets)))


def compare_projection(obs, dataset):
    from .schema import load_schema, validate_instance
    validate_instance(dataset, load_schema(Path(__file__).with_name('profile.schema.json')))
    source = dataset['source']
    url = urlparse(source['url'])
    if (source['version'] not in RELEASES or source['selection'] not in RELEASES[source['version']]
            or url.scheme != 'https' or url.hostname not in ('www.nu-fit.org', 'nu-fit.org')):
        raise ValueError('Unsupported NuFIT release, selection, or source URL')
    if dataset['ordering'] != obs['ordering']:
        raise ValueError('NuFIT projection ordering mismatch')
    axes, grid = read_projection(dataset['archive']['path'], dataset['archive']['sha256'], dataset['section'])
    for token, axis in zip(dataset['section'].split('/'), axes):
        if token.startswith('T') and (axis[0] < 0 or axis[-1] > 1):
            raise ValueError('NuFIT mixing coordinate outside sin-squared chart')
        if token == 'DMA' and np.any(axis*(1 if dataset['ordering'] == 'NO' else -1) <= 0):
            raise ValueError('NuFIT atmospheric grid sign contradicts declared ordering')
    result = {'status': 'PASS', 'meaning': 'Single profiled projection evaluated; no acceptance assigned',
              'dataset_id': dataset['dataset_id'], 'likelihood': 'PROFILED_DELTA_CHI2',
              'source': source, 'section': dataset['section'], 'ordering': dataset['ordering'],
              'archive_sha256': dataset['archive']['sha256'],
              'source_authentication': 'DECLARED_BY_INPUT_HASH_VERIFIED',
              'joint_likelihood': False, 'experimental_acceptance': None,
              'assumptions': dataset['assumptions'], 'interpolation': 'MULTILINEAR_NATIVE_COORDINATES',
              'minimum_subtracted': False, 'combined_with_other_data': False}
    values = []
    names = {'T12': 'sin2_theta12', 'T13': 'sin2_theta13', 'T23': 'sin2_theta23',
             'DMS': 'dm21_eV2', 'DMA': 'dm3l_eV2', 'DCP': 'delta_rad'}
    for token, axis in zip(dataset['section'].split('/'), axes):
        value = obs.get(names[token])
        if value is None:
            return dict(result, status='UNKNOWN', reason='Requested projection observable undefined')
        value = real_number(value, names[token])
        if token == 'DMS':
            if value <= 0:
                return dict(result, status='UNKNOWN', reason='Nonpositive solar splitting outside log10 chart')
            value = math.log10(value)
        elif token == 'DMA':
            value /= 1e-3  # NuFIT uses dm31 for NO and dm32 for IO.
        elif token == 'DCP':
            value = math.degrees(value % (2*math.pi))
            value += 360*math.ceil((axis[0]-value)/360)
        values.append(value)
    value = interpolate(axes, grid, values)
    if value is None:
        return dict(result, status='UNKNOWN', reason='Outside published grid; extrapolation disabled')
    return dict(result, delta_chi2=value, native_coordinates=values, dimensions=len(axes))
