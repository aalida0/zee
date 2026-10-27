"""Bounded D2 development probes; execution never implies physical acceptance."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import platform
import time
import traceback

import numpy as np
from module1.scalar_constraints import validate_input, reconstruct, check_bfb, unitarity, ewpo
from module2.interface import canonical_hash, strict_loads, decode, evaluate as neutrino_evaluate
from module6.coherent_pilot import pilot, SOURCE_TOP_MS_160, LHA_SOURCE_SHA256
from module6.d1_run_grid import matching_provenance, validate_row, summarize, write, scoped as d1_scoped
from module6.d2_scalar_prefilter import candidate, neighborhood, FIELDS, STEP

ROOT = Path(__file__).resolve().parents[1]
# Independent coefficient-index directions; no shared rescaling or probability prior.
DIRECTIONS = (
    ("baseline", {}),
    ("index0", {0: (12., .7)}),
    ("index2", {2: (18., -1.1)}),
    ("mixed13", {1: (9., .4), 3: (15., 1.3)}),
)
COEFFICIENT_BOUND = 1e-3  # numerical development bound, not perturbativity
CLOSURE_TOLERANCE = 2e-9  # frozen Module2 interface forward-closure gate
FLAVOR_FIELDS = ("delta_C7", "delta_C8", "conditional_linear_value_1e_minus4")
SELECTION_RULE = ("Source then greedy maximin squared distance in (mH1/10,mH2/15,gamma/.02); "
                  "ties use all five STEP-normalized fields then ascending name; physical duplicates removed. "
                  "No flavor value or experimental flavor cut used.")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def scoped(result):
    """Retain frozen scope controls and reject invented Boolean acceptance flags."""
    d1_scoped(result)
    def walk(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key.lower() in ('allowed', 'excluded', 'is_allowed', 'is_excluded'):
                    raise ValueError('Invented allowed/excluded flag')
                if key.lower() in ('complete_lfv', 'constraints_complete', '2026_linearized_flavor_filter_ready') and child is not False:
                    raise ValueError('Invented completeness flag')
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(result)


def select_spectra(seed, screen):
    if screen['source_input_sha256'] != canonical_hash(seed):
        raise ValueError('Screen source SHA mismatch')
    specs = neighborhood()
    if [(p['name'], p['offsets']) for p in screen['points']] != specs:
        raise ValueError('Screen support differs from declared neighborhood')
    eligible = []
    for p in screen['points']:
        if (p['status'] == 'PASSES_SCOPED_TREE_AND_EWPO'
                and p['passes_scoped_tree_and_EWPO'] is True
                and set(p['gates']) == {'reconstruction', 'bfb', 'unitarity', 'ewpo'}
                and all(g['assessment'] == 'PASS' for g in p['gates'].values())):
            eligible.append(p)
    source = next((p for p in eligible if p['name'] == 'source'), None)
    if source is None:
        raise ValueError('Source does not pass scoped scalar gates')
    chosen = [source]
    def physical_key(p):
        return tuple(p['physical'][k] for k in FIELDS)
    def distance(a, b, keys):
        return sum(((a['physical'][k]-b['physical'][k])/STEP[k][0])**2 for k in keys)
    while len(chosen) < 3:
        pool = [p for p in eligible if physical_key(p) not in {physical_key(c) for c in chosen}]
        if not pool:
            break
        pool.sort(key=lambda p: (-min(distance(p, c, ('mH1','mH2','gamma')) for c in chosen),
                                 -min(distance(p, c, FIELDS) for c in chosen), p['name']))
        chosen.append(pool[0])
    if len(chosen) < 2:
        raise ValueError('D2_NO_ALTERNATIVE_SCOPED_SCALAR')
    # Independent direct frozen re-evaluation of every selected screen row.
    for p in chosen:
        row, x = candidate(seed, p['name'], p['offsets'])
        scalar = row['module2_input']['scalar']['record']
        if (p['scalar_sha256'] != canonical_hash(scalar)
                or any(p['physical'][k] != x[k] for k in p['physical'])):
            raise ValueError('Stale selected spectrum')
        _, ew, _, _ = validate_input(scalar)
        pars, inherited, rec = reconstruct(x)
        direct = {'reconstruction': rec, 'bfb': check_bfb(pars),
                  'unitarity': unitarity(pars, inherited), 'ewpo': ewpo(x, ew, scalar['ew_fit'])}
        if any(g['assessment'] != 'PASS' for g in direct.values()):
            raise ValueError('Selected spectrum failed direct scoped check')
        fit = direct['ewpo']['alternative_fits_not_combined'][scalar['ew_fit']]
        if (fit['chi2_relative_to_fit_minimum'] != p['gates']['ewpo']['chi2']
                or direct['ewpo']['STU'] != p['gates']['ewpo']['STU']):
            raise ValueError('Independent STU comparison failed')
    return chosen


def generate(seed, selected):
    if seed['module2_input']['ordering'] != 'NO':
        raise ValueError('D2 requires exact illustrative NO source')
    coeff = decode(seed['module2_input']['homogeneous_coefficients'], (4,))
    # Check components before multiplication, including baseline, to avoid overflow.
    if any(abs(z.real) > COEFFICIENT_BOUND/36 or abs(z.imag) > COEFFICIENT_BOUND/36 for z in coeff):
        raise ValueError('Original coefficients exceed bounded development support')
    rows, entries = [], []
    for spectrum in selected:
        for label, changes in DIRECTIONS:
            row, x = candidate(seed, spectrum['name']+'_'+label, spectrum['offsets'])
            transformed = coeff.copy()
            factors = {}
            for index, (magnitude, phase) in changes.items():
                factor = magnitude*complex(math.cos(phase), math.sin(phase))
                transformed[index] *= factor
                factors[str(index)] = {'magnitude': magnitude, 'phase_rad': phase,
                                       'real': factor.real, 'imag': factor.imag}
            if not np.isfinite(transformed).all() or np.max(abs(transformed)) > COEFFICIENT_BOUND:
                raise ValueError('Transformed coefficient bound exceeded')
            vector = {'real': transformed.real.tolist(), 'imag': transformed.imag.tolist()}
            row['module2_input']['homogeneous_coefficients'] = vector
            validate_row(row)
            canonical_hash(row)  # finite JSON
            if row['module2_input']['target_eV'] != seed['module2_input']['target_eV']:
                raise ValueError('Changed Majorana target')
            rows.append(row)
            entries.append({'benchmark_id': row['benchmark_id'], 'spectrum_name': spectrum['name'],
                            'family_name': label, 'homogeneous_coefficients': vector,
                            'per_index_multipliers': factors, 'changed_indices': sorted(changes),
                            'physical': copy.deepcopy(row['module2_input']['scalar']['record']['physical']),
                            'input_sha256': canonical_hash(row),
                            'bound_scalar_sha256': row['module2_input']['scalar']['sha256']})
    if not 4 <= len(rows) <= 12 or len({r['benchmark_id'] for r in rows}) != len(rows):
        raise ValueError('Invalid D2 point budget or duplicate IDs')
    return rows, entries


def compare(points):
    good = [p for p in points if p['execution_status'] == 'COMPLETED_SCOPED']
    groups = {}
    for p in good:
        groups.setdefault(p['spectrum_name'], []).append(p)
    within = {}
    for name, rows in groups.items():
        spread = {k: max(p[k] for p in rows)-min(p[k] for p in rows) for k in FLAVOR_FIELDS}
        if any(v != 0. for v in spread.values()):
            raise ValueError('Exact fixed-spectrum flavor invariance falsified')
        def variation(field):
            result = {}
            for channel in rows[0][field]:
                vals = [p[field][channel] for p in rows]
                low, high = min(vals), max(vals)
                result[channel] = {'min': low, 'max': high, 'max_minus_min': high-low,
                                   'max_over_min': high/low if low else None}
            return result
        within[name] = {'completed': len(rows), 'flavor_max_minus_min': spread,
                        'distinct_D_outputs': len({p['D_sha256'] for p in rows}),
                        'radiative_subset_BR': variation('radiative_subset_BR'),
                        'higgs_lfv_widths_GeV': variation('higgs_lfv_widths_GeV')}
    base = next((p for p in good if p['spectrum_name'] == 'source' and p['family_name'] == 'baseline'), None)
    cross = []
    if base:
        for p in good:
            if p['spectrum_name'] != 'source' and p['family_name'] == 'baseline':
                cross.append({'spectrum_name': p['spectrum_name'],
                              'second_minus_source': {k: p[k]-base[k] for k in FLAVOR_FIELDS}})
    pinned = {'delta_C7': -.05955354444399845, 'delta_C8': -.06299918381959017,
              'conditional_linear_value_1e_minus4': 4.182878900268742,
              'mu_to_e_gamma_subset_BR': 5.117059759419609e-19}
    regression = {}
    if base:
        for k, expected in pinned.items():
            actual = base['radiative_subset_BR']['mu_to_e_gamma'] if k == 'mu_to_e_gamma_subset_BR' else base[k]
            regression[k] = {'pinned_D0_D1': expected, 'D2': actual, 'difference': actual-expected,
                             'matches': math.isclose(actual, expected, rel_tol=2e-12, abs_tol=0.)}
    return {'within_spectrum': within, 'cross_spectrum_baseline': cross, 'D0_D1_regression': regression}


def run(seed_path, screen_path, output_dir, summary_path, mu, mt, lha):
    matching_provenance(mu, mt, lha)
    seed_raw = seed_path.read_bytes()
    seed = strict_loads(seed_raw.decode())
    d0 = strict_loads((ROOT/'validation/module6/pilot.json').read_text())
    sources = dict(d0['source_sha256'])
    for name, expected in sources.items():
        if sha((ROOT/name).read_bytes()) != expected:
            raise ValueError('Frozen D0 source changed: '+name)
    if sha(seed_raw) != sources['module3/example.json']:
        raise ValueError('Require exact frozen source seed bytes')
    lha_path = Path(d0['top_mass_source']['reference_lha_path_read_only'])
    if sha(lha_path.read_bytes()) != lha:
        raise ValueError('Reference LHA bytes mismatch')
    for name in ('module6/d1_family_grid.py', 'module6/d1_run_grid.py',
                 'module6/D1_FAMILY_SCAN_AUDIT.md', 'validation/module6/d1_family_scan.json',
                 'module6/d2_scalar_prefilter.py', 'module6/d2_family_runner.py',
                 'tests/test_module6_d2_scalar_prefilter.py', 'tests/test_module6_d2_family_runner.py', 'AGENTS.md'):
        sources[name] = sha((ROOT/name).read_bytes())
    screen = strict_loads(screen_path.read_text())
    selected = select_spectra(seed, screen)
    rows, entries = generate(seed, selected)
    output_dir.mkdir(parents=True, exist_ok=True)
    write(output_dir/'inputs.json', rows)
    start = time.perf_counter()
    points = []
    for row, entry in zip(rows, entries):
        begin = time.perf_counter()
        point = dict(entry, execution_status='BLOCKED_ERROR', source_manifest_sha256=canonical_hash(sources))
        try:
            result = pilot(row, mt, lha)  # fresh full frozen vacuum on EVERY point
            nout = neutrino_evaluate(row['module2_input'])  # independent real closure
            full_path = output_dir/(row['benchmark_id']+'.json')
            write(full_path, {'input': row, 'pilot': result, 'independent_neutrino': nout})
            scoped(result)
            point.update(summarize(row, result, nout))
            point.update(matrix_max_abs_entries={k: float(np.max(abs(decode(nout[k])))) for k in ('F','D','Ye','Ye2')},
                         D_sha256=canonical_hash(nout['D']), execution_status='COMPLETED_SCOPED',
                         output_path=str(full_path), output_bytes_sha256=sha(full_path.read_bytes()),
                         pilot_output_sha256=canonical_hash(result), vacuum_execution='FRESH_FULL_FROZEN_SEARCH')
        except Exception as exc:
            point['error'] = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
            write(output_dir/(row['benchmark_id']+'.error.json'), point['error'])
        point['runtime_seconds'] = time.perf_counter()-begin
        points.append(point)
        print(row['benchmark_id'], point['execution_status'], flush=True)
    comparison_error = None
    try:
        contrasts = compare(points)
    except ValueError as exc:
        contrasts, comparison_error = {}, str(exc)
    complete = len([p for p in points if p['execution_status'] == 'COMPLETED_SCOPED'])
    regression = contrasts.get('D0_D1_regression', {})
    success = (complete == len(rows) and len(regression) == 4
               and all(v['matches'] for v in regression.values()) and comparison_error is None)
    decision = (success and len(selected) >= 2
                and all(g['distinct_D_outputs'] == 4 for g in contrasts['within_spectrum'].values())
                and any(g['higgs_lfv_widths_GeV']['h_to_e_tau']['max_over_min'] > 1.01
                        for g in contrasts['within_spectrum'].values()))
    summary = {'schema_version': '1.0.0', 'status': 'D2_EXECUTED_EXPLORATORY' if success else 'D2_BLOCKED_OR_FALSIFIED',
               'source_input_sha256': canonical_hash(seed), 'seed_bytes_sha256': sha(seed_raw),
               'source_sha256': sources, 'source_manifest_sha256': canonical_hash(sources),
               'scalar_screen': screen, 'screen_bytes_sha256': sha(screen_path.read_bytes()),
               'selection_rule': SELECTION_RULE, 'selected_spectra': selected,
               'attempted_coherent_points': len(rows), 'completed_coherent_points': complete,
               'blocked_coherent_points': len(rows)-complete, 'points': points, 'comparisons': contrasts,
               'comparison_error': comparison_error, 'runtime_seconds': time.perf_counter()-start,
               'closure_tolerance': CLOSURE_TOLERANCE, 'closure_tolerance_source': 'module2/interface.py:148',
               'top_mass_source': d0['top_mass_source'], 'matching_scale_GeV': mu,
               'python': platform.python_version(), 'numpy': np.__version__,
               'D3_development_gate': 'CONSIDER_DECLARED_PRIOR_IO_AND_DECAYS' if decision else 'PIVOT_SAMPLER_OR_OBSERVABLES',
               'constraints_complete': False, 'COMPLETE_LFV': False, '2026_LINEARIZED_FLAVOR_FILTER_READY': False,
               'global_zee_acceptance': None, 'experimental_comparison': 'NOT_EVALUATED'}
    write(summary_path, summary)
    print(summary['status'], complete, '/', len(rows), flush=True)
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('seed', 'screen', 'output-dir', 'summary'):
        ap.add_argument('--'+name, type=Path, required=True)
    ap.add_argument('--mu-GeV', type=float, required=True)
    ap.add_argument('--mt-MSbar-160', type=float, required=True)
    ap.add_argument('--reference-lha-sha256', required=True)
    a = ap.parse_args()
    # Prevent writes overwriting inputs or arbitrary existing evidence through the CLI.
    local = (ROOT/'validation/module6/local').resolve()
    if (not a.output_dir.resolve().is_relative_to(local)
            or a.summary.resolve() != (ROOT/'validation/module6/d2_scoped_scan.json').resolve()
            or len({a.seed.resolve(), a.screen.resolve(), a.summary.resolve()}) != 3):
        raise ValueError('Distinct inputs, scoped D2 summary and ignored local output directory required')
    summary = run(a.seed, a.screen, a.output_dir, a.summary, a.mu_GeV,
                  a.mt_MSbar_160, a.reference_lha_sha256)
    return 0 if summary['status'] == 'D2_EXECUTED_EXPLORATORY' else 2


if __name__ == '__main__':
    raise SystemExit(main())
