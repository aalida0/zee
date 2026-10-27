"""Six real, source-bound D1 probes; computational execution is not acceptance."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import time
import traceback

import numpy as np
from module2.interface import (canonical_hash, strict_loads, scalar_input, decode,
                               evaluate as neutrino_evaluate, validate_schema as validate2)
from module3.interface import validate as validate3
from module6.coherent_pilot import pilot, SOURCE_TOP_MS_160, LHA_SOURCE_SHA256, STATUS
from module6.d1_family_grid import generate

ROOT = Path(__file__).resolve().parents[1]
D0 = 'bb3834c5b3679dbfd9cb4cf4a530eecb460fc32e'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n')
    tmp.replace(path)


def matching_provenance(mu, mt, lha):
    for x in (mu, mt):
        if type(x) not in (int, float) or not math.isfinite(x):
            raise ValueError('Finite numerical matching inputs required')
    if mu != 160. or mt != SOURCE_TOP_MS_160 or lha != LHA_SOURCE_SHA256:
        raise ValueError('Exact frozen mu=160, top mass and LHA provenance required')


def validate_row(row):
    validate3(row, 'input.schema.json')
    m2 = row['module2_input']
    validate2(m2, 'input.schema.json')
    if m2['mode'] != 'inverse' or m2['scalar']['kind'] != 'module1_input':
        raise ValueError('Full SHA-bound scalar and inverse input required')
    p, _ = scalar_input(m2['scalar'])
    if not row['benchmark_id'] == m2['benchmark_id'] == m2['scalar']['record']['benchmark_id']:
        raise ValueError('Swapped benchmark IDs')
    return p


def scoped(result):
    # Missing keys fail closed. PASS is limited to declared computations.
    canonical_hash(result)
    if (result['status'] != STATUS or result['constraints_complete'] is not False
            or result['global_zee_acceptance'] is not None
            or result['neutrino_lfv']['COMPLETE_LFV'] is not False
            or result['neutrino_lfv']['gates']['full_lfv'] != 'NOT_EVALUATED'
            or result['neutrino_lfv']['gates']['exact_one_loop'] != 'UNKNOWN'
            or result['neutrino_lfv']['module4_Barr_Zee_and_W_completion'] != 'NOT_EVALUATED'
            or result['neutrino']['gates']['data_comparison'] != 'NOT_EVALUATED'
            or result['scalar']['global_vacuum_certification'] != 'NOT_ESTABLISHED'
            or result['bsgamma']['experiment_comparison'] != 'NOT_EVALUATED'
            or result['bsgamma']['flavor_classification'] != 'UNCLASSIFIED'
            or result['bsgamma']['nonlinear_reliability'] != 'UNKNOWN'):
        raise ValueError('Unexpected complete/physical acceptance claim')
    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ('experimental_comparison', 'experiment_comparison', 'experimental_LFV_comparison') and v != 'NOT_EVALUATED':
                    raise ValueError('Unexpected experimental comparison')
                if k == 'global_zee_acceptance' and v is not None:
                    raise ValueError('Unexpected global acceptance')
                if isinstance(v, str) and v.upper() in ('ALLOWED', 'EXCLUDED'):
                    raise ValueError('Unexpected classification')
                walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(result)


def scalar_evidence(gates):
    """Keep numerical gate evidence compact; full eigenvectors/search stay local."""
    fields = {
        'reconstruction': ('tadpole_max_over_v3', 'spectrum_max_relative_residual', 'mixing_max_residual_GeV2'),
        'bfb': ('certificate', 'necessary_and_sufficient', 'negative_witness'),
        'unitarity': ('max_abs_eigenvalue', 'strict_limit', 'eigenvalue_count'),
        'ewpo': ('STU', 'selected_fit', 'quadrature_max_delta'),
        'vacuum': ('all_attempts_converged', 'deeper_witness', 'global_stability_proven',
                   'neutral_value_over_v4', 'field_bound_in_units_v', 'runs')}
    out = {}
    for key, keep in fields.items():
        gate = gates[key]
        out[key] = {k: gate[k] for k in ('status', 'assessment', 'order', 'reason', *keep) if k in gate}
        if key == 'ewpo' and 'alternative_fits_not_combined' in gate:
            out[key]['selected_fit_result'] = gate['alternative_fits_not_combined'][gate['selected_fit']]
    return out


def summarize(row, result, nout):
    scoped(result)
    p = validate_row(row)
    m2 = row['module2_input']
    if result['benchmark_id'] != row['benchmark_id'] or result['ordering'] != m2['ordering']:
        raise ValueError('Output identity mismatch')
    if result['neutrino']['output_sha256'] != canonical_hash(nout):
        raise ValueError('Independent neutrino output mismatch')
    target, reconstructed = decode(m2['target_eV']), decode(nout['Mnu'])
    difference = reconstructed-target
    residual = float(np.linalg.norm(difference)/np.linalg.norm(target))
    if residual > 2e-9:
        raise ValueError('Original target closure failed')
    for k in ('mH1', 'mH2'):
        if result['bsgamma']['matching_input'][k+'_GeV'] != p[k]:
            raise ValueError('Flavor spectrum mismatch')
    for k in ('beta', 'gamma'):
        if result['bsgamma']['matching_input'][k+'_rad'] != p[k]:
            raise ValueError('Flavor mixing mismatch')
    matching_provenance(result['bsgamma']['matching_input']['matching_scale_GeV'],
                        result['bsgamma']['matching_input']['mt_MSbar_GeV'],
                        result['provenance']['hyperiso_reference_LHA_sha256'])
    obs = result['neutrino_lfv']['observables']
    return {
        'ordering': m2['ordering'], 'module2_input_sha256': canonical_hash(m2),
        'bound_scalar_sha256': m2['scalar']['sha256'],
        'scalar_status': result['scalar']['status'], 'scalar_gates': scalar_evidence(result['scalar']['gates']),
        'neutrino_gates': result['neutrino']['gates'],
        'lfv_gates': result['neutrino_lfv']['gates'],
        'missing_contributions': result['neutrino_lfv']['missing_contributions'],
        'target_sha256': canonical_hash(m2['target_eV']),
        'target_vs_reconstructed_relative_error': residual,
        'target_vs_reconstructed_max_abs_eV': float(np.max(abs(difference))),
        'inverse_family_relative_residual': result['neutrino']['inverse_family_relative_residual'],
        'matrix_frobenius_norms': {k: float(np.linalg.norm(decode(nout[k]))) for k in ('F', 'D', 'Ye', 'Ye2', 'Mnu')},
        'delta_C7': result['bsgamma']['delta_C7'], 'delta_C8': result['bsgamma']['delta_C8'],
        'conditional_linear_value_1e_minus4': result['bsgamma']['linearized_value_in_1e_minus4'],
        'radiative_subset_BR': {k: v['subset_partial_BR'] for k, v in result['neutrino_lfv']['radiative_subset_only'].items()},
        'higgs_lfv_widths_GeV': {k: v['width_GeV'] for k, v in obs.items() if '_to_' in k and k.startswith(('h_to_', 'H_to_', 'A_to_'))},
        'per_sector_output_sha256': {k: result[k]['output_sha256'] for k in ('scalar', 'neutrino', 'neutrino_lfv', 'bsgamma')},
        'flavor_derived_input_sha256': result['bsgamma']['source_input_sha256'],
        'constraints_complete': False, 'global_zee_acceptance': None, 'COMPLETE_LFV': False,
        'flavor_experimental_comparison': 'NOT_EVALUATED'}


def comparisons(points):
    good = [p for p in points if p['execution_status'] == 'PASS_SCOPED']
    fields = ('delta_C7', 'delta_C8', 'conditional_linear_value_1e_minus4')
    groups = {}
    for p in good: groups.setdefault(p['spectrum_name'], []).append(p)
    within = {}
    for key, rows in groups.items():
        spread = {k: max(r[k] for r in rows)-min(r[k] for r in rows) for k in fields}
        if any(abs(v) > 1e-13 for v in spread.values()):
            raise ValueError('Fixed-spectrum flavor invariance falsified')
        within[key] = {'points': len(rows), 'flavor_max_minus_min': spread,
                       'mu_to_e_gamma_BR_max_over_min': max(r['radiative_subset_BR']['mu_to_e_gamma'] for r in rows)/min(r['radiative_subset_BR']['mu_to_e_gamma'] for r in rows)}
    cross = []
    for a in good:
        for b in good:
            if a['spectrum_name'] == 'source_spectrum' and b['spectrum_name'] != a['spectrum_name'] and b['family_name'] == a['family_name']:
                cross.append({'family_name': a['family_name'], 'second_minus_source': {k: b[k]-a[k] for k in fields},
                              'mu_to_e_gamma_BR_second_over_source': b['radiative_subset_BR']['mu_to_e_gamma']/a['radiative_subset_BR']['mu_to_e_gamma']})
    return {'fixed_spectrum': within, 'changed_spectrum': cross}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ('seed', 'inputs', 'manifest', 'output-dir', 'summary'):
        ap.add_argument('--'+name, type=Path, required=True)
    ap.add_argument('--mu-GeV', type=float, required=True)
    ap.add_argument('--mt-MSbar-160', type=float, required=True)
    ap.add_argument('--reference-lha-sha256', required=True)
    args = ap.parse_args()
    matching_provenance(args.mu_GeV, args.mt_MSbar_160, args.reference_lha_sha256)
    d0 = strict_loads((ROOT/'validation/module6/pilot.json').read_text())
    sources = dict(d0['source_sha256'])
    for name, expected in sources.items():
        if sha((ROOT/name).read_bytes()) != expected:
            raise ValueError('Frozen D0 source changed: '+name)
    for name in ('module6/d1_family_grid.py', 'module6/d1_run_grid.py', 'tests/test_module6_d1_family_grid.py', 'tests/test_module6_d1_run_grid.py', 'validation/module6/pilot.json', 'AGENTS.md'):
        sources[name] = sha((ROOT/name).read_bytes())
    seed_raw, input_raw, manifest_raw = (p.read_bytes() for p in (args.seed, args.inputs, args.manifest))
    if sha(seed_raw) != sources['module3/example.json']:
        raise ValueError('D1 requires exact D0 source input bytes')
    rows = [strict_loads(line) for line in input_raw.decode().splitlines()]
    manifest = strict_loads(manifest_raw.decode())
    expected_rows, expected_entries = generate(strict_loads(seed_raw.decode()))
    if (rows != expected_rows or manifest['points'] != expected_entries
            or manifest['constraints_complete'] is not False or manifest['COMPLETE_LFV'] is not False
            or manifest['global_zee_acceptance'] is not None
            or manifest['flavor_experimental_comparison'] != 'NOT_EVALUATED'
            or manifest['source_input_bytes_sha256'] != sha(seed_raw)):
        raise ValueError('Grid differs from exact six source-bound probes')
    # Independent schema/hash checks, beyond the generator's own validation.
    for row in rows: validate_row(row)
    source = d0['top_mass_source']
    lha_path = Path(source['reference_lha_path_read_only'])
    if sha(lha_path.read_bytes()) != LHA_SOURCE_SHA256:
        raise ValueError('Reference LHA bytes mismatch')
    total_start = time.perf_counter()
    points = []
    for row, entry in zip(rows, expected_entries):
        start = time.perf_counter()
        point = dict(entry, execution_status='BLOCKED_ERROR', input_sha256=canonical_hash(row),
                     source_manifest_sha256=canonical_hash(sources), error=None)
        try:
            result = pilot(row, args.mt_MSbar_160, args.reference_lha_sha256)
            nout = neutrino_evaluate(row['module2_input'])
            point.update(summarize(row, result, nout))
            output = args.output_dir/(row['benchmark_id']+'.json')
            write(output, {'pilot': result, 'independent_neutrino': nout})
            point.update(execution_status='PASS_SCOPED', output_bytes_sha256=sha(output.read_bytes()),
                         output_path=str(output), pilot_output_canonical_sha256=canonical_hash(result))
        except Exception as exc:
            error = {'type': type(exc).__name__, 'message': str(exc), 'traceback': traceback.format_exc()}
            error_path = args.output_dir/(row['benchmark_id']+'.error.json')
            write(error_path, error)
            point.update(error=error, error_sha256=canonical_hash(error))
        point['runtime_seconds'] = time.perf_counter()-start
        points.append(point)
        print(row['benchmark_id'], point['execution_status'], flush=True)
    regression = {}
    if points[0]['execution_status'] == 'PASS_SCOPED':
        for key, expected in (('delta_C7', -.05955354444399845), ('delta_C8', -.06299918381959017),
                              ('conditional_linear_value_1e_minus4', 4.182878900268742),
                              ('mu_to_e_gamma_BR', 5.117059759419609e-19)):
            actual = points[0]['radiative_subset_BR']['mu_to_e_gamma'] if key == 'mu_to_e_gamma_BR' else points[0][key]
            regression[key] = {'D0': expected, 'D1': actual, 'absolute_difference': actual-expected,
                               'matches': math.isclose(actual, expected, rel_tol=2e-12, abs_tol=0.)}
    error = None
    try: comparison = comparisons(points)
    except ValueError as exc: comparison, error = {}, str(exc)
    success = all(p['execution_status'] == 'PASS_SCOPED' for p in points) and len(regression) == 4 and all(v['matches'] for v in regression.values()) and error is None
    summary = {'schema_version': '1.0.0', 'status': 'D1_REAL_GRID_EXECUTED_NOT_PHYSICAL_ACCEPTANCE' if success else 'D1_REAL_GRID_BLOCKED',
               'D0_commit': D0, 'points': points, 'real_points_executed': sum(p['execution_status']=='PASS_SCOPED' for p in points),
               'generated_points': len(rows), 'input_jsonl_bytes': len(input_raw), 'input_jsonl_sha256': sha(input_raw),
               'manifest_bytes_sha256': sha(manifest_raw), 'source_seed_bytes_sha256': sha(seed_raw),
               'source_sha256': sources, 'top_mass_provenance': source, 'reference_lha_rehashed': True,
               'matching_scale_GeV': args.mu_GeV, 'mt_MSbar_160_GeV': args.mt_MSbar_160,
               'runtime_seconds': time.perf_counter()-total_start, 'vacuum_memoization': False,
               'environment': {'python': platform.python_version(), 'numpy': np.__version__},
               'D0_regression': regression, 'comparisons': comparison, 'comparison_error': error,
               'constraints_complete': False, 'global_zee_acceptance': None, 'COMPLETE_LFV': False,
               'flavor_experimental_comparison': 'NOT_EVALUATED'}
    write(args.summary, summary)
    return 0 if success else 2


if __name__ == '__main__':
    raise SystemExit(main())
