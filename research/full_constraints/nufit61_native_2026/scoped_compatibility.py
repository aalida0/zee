"""NuFIT 6.1 scoped (not joint-likelihood) oscillation compatibility filter.

Authentic single-variable profiled curves supply 1D Delta-chi^2 <= 9;
the separate 3D T23/DMA/DCP profile supplies a nominal Wilks 3-parameter
99.73%-region criterion. These cuts are an INTERSECTION OF SCOPED SCREENS,
not a calibrated six-dimensional region or model-wide physical acceptance.

The caller must provide source-verified NuFIT 6.1 archives unchanged. Data
are loaded once per ordering/selection and can be reused over any number of
model points without repeated XZ decompression. No scalar/neutrino fit is run
here: input observables must come from the validated Module2 prediction.

Example: python -m research.full_constraints.nufit61_native_2026.scoped_compatibility \
    --archive-dir NuFIT --ordering NO --observables path/to/observables.json \
    --output /tmp/nufit61_scoped.json
"""
import argparse
import hashlib
import json
import lzma
import math
from pathlib import Path

import numpy as np

from .verify import FILES, SECTIONS

# Probability=0.9973 in chi-square with three degrees of freedom; this is
# only a nominal Wilks screen for a periodic, possibly non-Gaussian CP phase.
ONE_D_CUTOFF = 9.0
THREE_D_CUTOFF = 14.1562525005409
PROFILES = ('T12', 'T13', 'T23', 'DMS', 'DMA', 'DCP', 'T23/DMA/DCP')
NAMES = {'T12': 'sin2_theta12', 'T13': 'sin2_theta13',
         'T23': 'sin2_theta23', 'DMS': 'dm21_eV2',
         'DMA': 'dm3l_eV2', 'DCP': 'delta_rad'}


def _load_archive(path, sha, expected_minimum, ordering):
    """Load needed projections in one pass; fail closed on malformed bytes."""
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != sha:
        raise ValueError('NuFIT 6.1 archive SHA256 mismatch: ' + str(path))
    try:
        contents = lzma.decompress(raw).decode('utf-8')
    except (lzma.LZMAError, UnicodeError) as e:
        raise ValueError('Invalid XZ/UTF8 NuFIT archive') from e
    label = '### Normal Ordering' if ordering == 'NO' else '### Inverted Ordering'
    if not contents.startswith(label):
        raise ValueError('NuFIT file ordering header contradicts declared ordering')
    profiles, seen = {}, []
    active, lines = None, []

    def finish():
        if active is None or active not in PROFILES:
            return
        tokens = active.split('/')
        values = np.fromstring('\n'.join(lines), sep=' ')
        ncols = len(tokens) + 1
        if values.size == 0 or values.size % ncols:
            raise ValueError('Malformed numeric shape for ' + active)
        rows = values.reshape(-1, ncols)
        if not np.isfinite(rows).all():
            raise ValueError('Nonfinite grid entry in ' + active)
        axes = tuple(np.unique(rows[:, i]) for i in range(len(tokens)))
        shape = tuple(len(a) for a in axes)
        if math.prod(shape) != len(rows):
            raise ValueError('Incomplete grid in ' + active)
        locations = np.ravel_multi_index(
            tuple(np.searchsorted(a, rows[:, i]) for i, a in enumerate(axes)), shape)
        if len(np.unique(locations)) != len(rows):
            raise ValueError('Duplicate grid node in ' + active)
        grid = np.empty(shape, dtype=float)
        grid.ravel()[locations] = rows[:, -1]
        minimum = float(grid.min())
        if not math.isclose(minimum, expected_minimum, rel_tol=0, abs_tol=1.0e-8):
            raise ValueError('Global ordering offset is missing in ' + active)
        if active == 'DCP' and not np.isclose(grid[0], grid[-1], rtol=0, atol=1e-8):
            raise ValueError('Dirac CP phase seam mismatch')
        if active == 'DMA' and any(a * (1 if ordering == 'NO' else -1) <= 0 for a in axes[0]):
            raise ValueError('Atmospheric ordering convention mismatch')
        if active.startswith('T'):
            for token, axis in zip(tokens, axes):
                if token.startswith('T') and (axis[0] < 0 or axis[-1] > 1):
                    raise ValueError('Invalid sin-squared mixing axis')
        profiles[active] = (axes, grid, minimum)

    # The original file is a sequence of 22 sections; grid metadata is
    # recognized by exact section tags, never by commented explanatory text.
    for line in contents.splitlines():
        if line.startswith('# '):
            tag = line[2:].split()[0]
            if tag in SECTIONS:
                finish()
                if tag in seen:
                    raise ValueError('Repeated section ' + tag)
                seen.append(tag)
                active, lines = tag, []
        elif active in PROFILES and line.strip() and not line.startswith('#'):
            lines.append(line)
    finish()
    if tuple(seen) != SECTIONS or set(profiles) != set(PROFILES):
        raise ValueError('Unexpected NuFIT section inventory')
    return profiles


def _interpolate(axes, grid, point):
    """Multilinear on native axes (same rule as Module2.nufit)."""
    choices = []
    if len(point) != len(axes):
        raise ValueError('Wrong interpolation dimensionality')
    for axis, value in zip(axes, point):
        if not axis[0] <= value <= axis[-1]:
            return None
        hi = int(np.searchsorted(axis, value))
        if hi == len(axis):
            hi -= 1
        if axis[hi] == value:
            choices.append(((hi, 1.),))
        else:
            lo = hi - 1
            frac = (value - axis[lo]) / (axis[hi] - axis[lo])
            choices.append(((lo, 1.-frac), (hi, frac)))
    if len(choices) == 1:
        return float(sum(grid[i]*w for i, w in choices[0]))
    if len(choices) == 3:
        return float(sum(grid[a, b, c]*wa*wb*wc
                         for a, wa in choices[0] for b, wb in choices[1]
                         for c, wc in choices[2]))
    raise ValueError('Unimplemented dimension in scoped filter')


def _native_value(token, value, axis):
    if token == 'DMS':
        return math.log10(value) if value > 0 else None
    if token == 'DMA':
        return value / 1e-3
    if token == 'DCP':
        angle = math.degrees(value % (2*math.pi))
        angle += 360*math.ceil((axis[0]-angle)/360)
        return angle
    return value


class NuFIT61Compatibility:
    """Cache a single NuFIT dataset and screen many independently fitted points."""

    def __init__(self, archive_dir, ordering, selection='IC24'):
        if selection not in ('IC23', 'IC24') or ordering not in ('NO', 'IO'):
            raise ValueError('Choose IC23/IC24 and NO/IO explicitly')
        tag = 'TByes' if selection == 'IC24' else 'TBoff'
        filename = f'v61.release-{tag}-{ordering}.txt.xz'
        expected_ordering, source_name, sha, minimum = FILES[filename]
        assert expected_ordering == ordering
        path = Path(archive_dir)/filename
        self.profiles = _load_archive(path, sha, minimum, ordering)
        self.source = {'release': 'NuFIT 6.1 (2025)', 'selection':selection,
                       'ordering':ordering, 'archive': filename,
                       'sha256':sha, 'source_authentication':
                       'USER_UPLOADED_HASH_VERIFIED_UPSTREAM_UNVERIFIED',
                       'published_global_offset':minimum}
        self.ordering = ordering

    def evaluate(self, observables):
        """Return scoped status; NEVER claim a global six-parameter likelihood."""
        if not isinstance(observables, dict):
            raise ValueError('Expected a Module2-like observables object')
        if observables.get('ordering') != self.ordering:
            raise ValueError('NuFIT point ordering mismatch')
        results = {}
        for section in PROFILES:
            tokens = section.split('/')
            axes, grid, minimum = self.profiles[section]
            native = []
            reason = None
            for token, axis in zip(tokens, axes):
                raw = observables.get(NAMES[token])
                if raw is None:
                    reason = 'Observable undefined: '+NAMES[token]
                    break
                if isinstance(raw, (bool, str, dict, list)):
                    raise ValueError('Non-real observable: '+NAMES[token])
                try:
                    raw = float(raw)
                except (TypeError, ValueError, OverflowError) as exc:
                    raise ValueError('Non-real observable: '+NAMES[token]) from exc
                if not math.isfinite(raw):
                    raise ValueError('Nonfinite observable: '+NAMES[token])
                if token.startswith('T') and not 0 <= raw <= 1:
                    raise ValueError('Invalid sin-squared mixing: '+NAMES[token])
                value = _native_value(token, raw, axis)
                if value is None:
                    reason = 'Nonpositive solar splitting'
                    break
                native.append(value)
            cutoff = THREE_D_CUTOFF if section == 'T23/DMA/DCP' else ONE_D_CUTOFF
            if reason is not None:
                results[section] = {'status':'UNKNOWN', 'reason':reason,
                                    'cutoff': cutoff}
                continue
            value = _interpolate(axes, grid, native)
            if value is None:
                results[section] = {'status':'UNKNOWN',
                                    'reason':'Outside native NuFIT tabulation; no extrapolation',
                                    'native_coordinates': native, 'cutoff':cutoff}
                continue
            relative = value-minimum
            if relative < -1.e-6:
                raise ValueError('NuFIT negative relative chi-square outside roundoff')
            relative = max(relative, 0.)
            results[section] = {'status': 'PASS' if relative <= cutoff else 'FAIL',
                'absolute_delta_chi2':value, 'ordering_local_delta_chi2':relative,
                'cutoff':cutoff, 'native_coordinates':native}
        status = ('SCOPED_FAIL' if any(v['status']=='FAIL' for v in results.values())
                  else 'SCOPED_UNKNOWN' if any(v['status']=='UNKNOWN' for v in results.values())
                  else 'SCOPED_PASS')
        return {'status':status, 'method':'INDIVIDUAL_1D_DELTA_CHI2_AND_SEPARATE_3D_PROFILE',
                'source':self.source, 'sections':results,
                'one_dimensional_threshold':ONE_D_CUTOFF,
                'three_dimensional_threshold':THREE_D_CUTOFF,
                'threshold_interpretation':'Nominal Wilks individual 3sigma and 3-parameter 99.73pct screens; joint six-parameter confidence NOT calibrated',
                'projection_sums_used':False, 'global_six_dimensional_likelihood':False,
                'experimental_confidence_region':None, 'full_model_neutrino_acceptance':None,
                'global_zee_acceptance':None,
                'note':'IO ordering preference reported in absolute profiles, not used as an ordering veto.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive-dir', type=Path, required=True)
    p.add_argument('--ordering', choices=['NO', 'IO'], required=True)
    p.add_argument('--selection', choices=['IC23', 'IC24'], default='IC24')
    p.add_argument('--observables', type=Path, required=True,
                   help='JSON with Module2 observables including ordering')
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    model = NuFIT61Compatibility(a.archive_dir, a.ordering, a.selection)
    result = model.evaluate(json.loads(a.observables.read_text()))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(result['status'], result['sections']['T23/DMA/DCP'], flush=True)
    print('SAVED', a.output)


if __name__ == '__main__':
    main()
