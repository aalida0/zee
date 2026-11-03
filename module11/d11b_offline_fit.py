"""Bounded offline secondary-summary benchmarks; no oscillation likelihood.

Run python3 -m module11.d11b_offline_fit from the repository root.
All inverse/forward equations and Yukawa normalization remain in Module2.
"""
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform

import mpmath
import numpy as np

from module2.core import NumericalUnknown, forward, null_cone, solve_fixed_f, weights
from module2.interface import canonical_hash, decode, encode, evaluate
from module2.observables import observables

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'module11/nufit61_bestfit_ranges_secondary.json'
SOURCE_SHA256 = '230392a4d77fef5d2e91737569b3e5650cadd47fd13cea6ac396b2f3528f732b'
BENCHMARKS = ('d7_NO_neutral_near_heavy_07', 'F13_heavy_0001330')
ML = np.array([.00051099895, .1056583755, 1.77686])
YUKAWAS = ('F', 'D', 'Ye', 'Ye2')
TARGET_LABEL = 'NUFIT61_SECONDARY_SUMMARY_BENCHMARK'
PROPOSAL_LABEL = 'ONE_DIMENSIONAL_MARGINAL_BOUNDS_PROPOSAL'
SEED = 611103


def file_hash(path):
    return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def load_source():
    if file_hash(SOURCE) != SOURCE_SHA256:
        raise ValueError('Pinned secondary summary SHA256 mismatch')
    return json.loads((ROOT/SOURCE).read_text())


def scalar_records():
    """Bind complete scalar inputs to stored D10 evidence, including UNKNOWNs."""
    snapshot = json.loads((ROOT/'module1/d10_benchmarks.json').read_text())
    evidence = json.loads((ROOT/'validation/module1/d10_vacuum_global.json').read_text())
    stored = {r['benchmark_id']: r for r in evidence['records']}
    selected, statuses = {}, {}
    for r in snapshot['records']:
        name = r['input']['benchmark_id']
        digest = canonical_hash(r['input'])
        if digest != r['input_sha256'] or digest != stored[name]['input_sha256']:
            raise ValueError('D10 full scalar input SHA256 mismatch: '+name)
        statuses[name] = stored[name]['status']
        if name in BENCHMARKS:
            if statuses[name] != 'D10_GLOBAL_CERTIFIED':
                raise ValueError('Uncertified D10 spectrum')
            selected[name] = {'kind': 'module1_input', 'record': r['input'], 'sha256': digest}
    if set(selected) != set(BENCHMARKS):
        raise ValueError('Missing certified spectrum')
    return selected, statuses


def phase_error(a, b):
    return float(abs(np.angle(np.exp(1j*(a-b)))))


def marginal_contains(value, interval, period=None):
    lo, hi = interval
    if period is None:
        return lo <= value <= hi
    return (value-lo) % period <= hi-lo+1e-14


def target(ordering, lightest, alpha21, alpha31, parameters=None):
    """PDG phases in radians; dm3ell is signed dm31 (NO) or dm32 (IO)."""
    if ordering not in ('NO', 'IO'):
        raise ValueError('Explicit NO or IO required')
    central = load_source()['oscillation_parameters'][ordering]
    p = {k: v['bestfit'] for k, v in central.items()} if parameters is None else dict(parameters)
    if set(p) != set(central):
        raise ValueError('Require exactly six summary coordinates; no likelihood flags')
    if not np.isfinite(list(p.values())+[lightest, alpha21, alpha31]).all() or lightest <= 0:
        raise ValueError('Finite parameters and positive lightest mass required')
    ds, dl = p['dm21_eV2'], p['dm3ell_eV2']
    if ds <= 0 or (dl <= ds if ordering == 'NO' else dl >= -ds):
        raise ValueError('Inconsistent ordering/signed dm3ell')
    q = np.array([p['sin2theta12'], p['sin2theta13'], p['sin2theta23']])
    if np.any(q <= 0) or np.any(q >= 1):
        raise ValueError('Require sin-squared mixing parameters in (0,1)')
    s12, s13, s23 = np.sqrt(q)
    c12, c13, c23 = np.sqrt(1-q)
    phase = np.exp(1j*math.pi*(p['deltaCP_over_pi'] % 2))
    U = np.array([[c12*c13, s12*c13, s13/phase],
                  [-s12*c23-c12*s23*s13*phase, c12*c23-s12*s23*s13*phase, s23*c13],
                  [s12*s23-c12*c23*s13*phase, -c12*s23-s12*c23*s13*phase, c23*c13]])
    U = U@np.diag([1, np.exp(.5j*alpha21), np.exp(.5j*alpha31)])
    m = np.sqrt([lightest**2, lightest**2+ds, lightest**2+dl]) if ordering == 'NO' else np.sqrt(
        [lightest**2+abs(dl)-ds, lightest**2+abs(dl), lightest**2])
    M = U.conj()@np.diag(m)@U.conj().T
    return M, m, U, p


def check_target(M, masses, U, ordering, p, alpha21, alpha31):
    """Independent Hermitian eigensystem Takagi check, separate from Module2."""
    K = M.conj().T@M
    vals, V = np.linalg.eigh(K)
    idx = [0, 1, 2] if ordering == 'NO' else [1, 2, 0]
    V, vals = V[:, idx], vals[idx]
    V = V@np.diag(np.exp(-.5j*np.angle(np.diag(V.T@M@V))))
    diag = V.T@M@V
    o = observables(M, ordering)
    errors = {
        'symmetry_relative': float(np.linalg.norm(M-M.T)/np.linalg.norm(M)),
        'mass_squared_hermiticity_relative': float(np.linalg.norm(K-K.conj().T)/np.linalg.norm(K)),
        'independent_takagi_relative': float(np.linalg.norm(diag-np.diag(masses))/np.linalg.norm(masses)),
        'independent_mass_max_error_eV': float(max(abs(np.sqrt(np.maximum(vals, 0))-masses))),
        'input_takagi_relative': float(np.linalg.norm(U.T@M@U-np.diag(masses))/np.linalg.norm(masses)),
        'angle_max_error': max(abs(o['sin2_theta'+k]-p['sin2theta'+k]) for k in ('12', '13', '23')),
        'splitting_max_error_eV2': max(abs(o['dm21_eV2']-p['dm21_eV2']), abs(o['dm3l_eV2']-p['dm3ell_eV2'])),
        'phase_max_error_rad': max(phase_error(o['delta_rad'], math.pi*p['deltaCP_over_pi']),
                                   phase_error(o['alpha21_rad'], alpha21), phase_error(o['alpha31_rad'], alpha31))}
    if max(errors.values()) > 2e-10:
        raise NumericalUnknown('Target round-trip failed: '+str(errors))
    return errors


def target_specs(ordering):
    p = {k: v['bestfit'] for k, v in load_source()['oscillation_parameters'][ordering].items()}
    specs = []
    for m, (a, b) in itertools.product((.001, .01, .03), ((0., 0.), (.7, 2.1), (2.3, .4))):
        specs.append(dict(id=f'm{m}_a{a}_b{b}', lightest_eV=m, alpha21_rad=a, alpha31_rad=b,
                          parameters=p.copy(), label=TARGET_LABEL, varied_parameter=None))
    for k, item in load_source()['oscillation_parameters'][ordering].items():
        for end, value in zip(('lo', 'hi'), item['marginal3sigma']):
            varied = dict(p, **{k: value})
            specs.append(dict(id=k+'_'+end, lightest_eV=.01, alpha21_rad=.7, alpha31_rad=2.1,
                              parameters=varied, label=PROPOSAL_LABEL, varied_parameter=k))
    return specs


def inverse_input(scalar, ordering, spec, cone, coefficients):
    M, _, _, _ = target(ordering, spec['lightest_eV'], spec['alpha21_rad'], spec['alpha31_rad'], spec['parameters'])
    return dict(schema_version='1.0.0', benchmark_id='D11B_'+scalar['record']['benchmark_id']+'_'+ordering,
                mode='inverse', ordering=ordering, scalar=scalar, lepton_masses_GeV=ML.tolist(),
                target_eV=encode(M), null_cone=cone, homogeneous_coefficients=encode(np.asarray(coefficients, complex)))


def perturbativity(out):
    maxima = {k: float(np.max(abs(decode(out[k])))) for k in YUKAWAS}
    largest = max(maxima, key=maxima.get)
    overall = maxima[largest]
    return dict(max_abs=maxima, largest_yukawa=largest, overall_max=overall,
                below_one=overall < 1, below_sqrt4pi=overall < math.sqrt(4*math.pi))


def execute(inp):
    out = evaluate(inp)  # actual frozen inverse, family, finite forward and phase extraction
    selection = perturbativity(out)
    expected = decode(inp['target_eV'])
    closure = float(np.linalg.norm(decode(out['Mnu'])-expected)/np.linalg.norm(expected))
    reference, actual = observables(expected, inp['ordering']), out['observables']
    roundtrip = dict(
        angle_max_error=max(abs(actual[k]-reference[k]) for k in ('sin2_theta12', 'sin2_theta13', 'sin2_theta23')),
        phase_max_error_rad=max(phase_error(actual[k], reference[k]) for k in ('delta_rad', 'alpha21_rad', 'alpha31_rad')),
        splitting_max_error_eV2=max(abs(actual[k]-reference[k]) for k in ('dm21_eV2', 'dm3l_eV2')))
    return dict(input_sha256=canonical_hash(inp), selection=selection, closure_relative=closure,
                observable_roundtrip=roundtrip,
                condition=out['inverse']['condition'], rank=out['inverse']['rank'],
                nullity_complex=out['inverse']['nullity_complex'],
                inverse_relative_residual=out['inverse']['relative_residual'],
                homogeneous_relative_residual=out['inverse']['homogeneous_relative_residual']), out


def failure_diagnostics(inp):
    """One core-only replay; diagnostic numbers NEVER turn a rejection into PASS."""
    c = inp['null_cone']
    M = decode(inp['target_eV'])
    F, _ = null_cone(M, complex(c['t']['real'], c['t']['imag']), c['scale'], c['root'], c['chart'])
    F *= np.exp(1j*c['phase_rad'])
    kw = loop_inputs(inp['scalar'])
    sol = solve_fixed_f(F, M, **kw)
    D = sol['D0']+np.einsum('k,kij->ij', decode(inp['homogeneous_coefficients'], (4,)), sol['homogeneous'])
    return dict(condition=sol['condition'], rank=sol['rank'],
                inverse_relative_residual=sol['relative_residual'],
                rejected_family_closure_relative=float(np.linalg.norm(forward(F, D, **kw)-M)/np.linalg.norm(M)),
                cancellation_norm_bound=float(2*np.linalg.norm(F*weights(**kw))*np.linalg.norm(D)/np.linalg.norm(M)))


def controlled_family(scalar, ordering, spec):
    """Fixed orientation: reciprocal F/D scaling, then independent family amplitude."""
    cone = dict(t=dict(real=.25, imag=.1), scale=.001, root=0, chart=[0, 1, 2], phase_rad=.43)
    records = []
    direction = np.array([1+2j, -2+.5j, .7-1j, -.3+.8j])
    direction /= np.linalg.norm(direction)
    for mode, values in [('F_scale', [1e-10, 1e-7, 1e-5, .001, .1, 1., 4.]),
                         ('homogeneous_amplitude', [0., 1e-4, .01, .1, 1., 4., 10.])]:
        for value in values:
            c = dict(cone, scale=value if mode == 'F_scale' else .001)
            z = np.zeros(4, complex) if mode == 'F_scale' else value*direction
            inp = inverse_input(scalar, ordering, spec, c, z)
            try:
                metrics, out = execute(inp)
                records.append(dict(mode=mode, value=value, metrics=metrics,
                                    D0_frobenius=float(np.linalg.norm(decode(out['inverse']['D0'])))))
            except (ValueError, np.linalg.LinAlgError) as exc:
                records.append(dict(mode=mode, value=value, failure=str(exc)))
    return records


def counterexamples(scalar):
    spec = target_specs('NO')[4]
    cone = dict(t=dict(real=.25, imag=.1), scale=.001, root=0, chart=[0, 1, 2], phase_rad=.43)
    base = inverse_input(scalar, 'NO', spec, cone, np.zeros(4))
    records = []
    cases = {}
    zero = copy.deepcopy(base)
    zero.pop('null_cone')
    zero['F'] = encode(np.zeros((3, 3), complex))
    cases['zero_F'] = zero
    gamma = copy.deepcopy(base)
    gamma['scalar']['record']['physical']['gamma'] = 0.
    gamma['scalar']['sha256'] = canonical_hash(gamma['scalar']['record'])
    cases['zero_scalar_mixing_DEFORMATION_NOT_D10'] = gamma
    bad = copy.deepcopy(base)
    bad.pop('null_cone')
    bad['F'] = encode(np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 0]], complex)*.001)
    cases['incompatible_fixed_F'] = bad
    huge = copy.deepcopy(base)
    huge['homogeneous_coefficients'] = encode(np.ones(4, complex)*1e10)
    cases['unresolved_homogeneous_cancellation'] = huge
    for flag in ('NUFIT61_PROFILED_DELTA_CHI2_PASS', 'joint_3sigma_acceptance', 'ordering_preference'):
        bad = copy.deepcopy(base)
        bad[flag] = True
        cases[flag] = bad
    for name, inp in cases.items():
        try:
            evaluate(inp)
        except (ValueError, np.linalg.LinAlgError) as exc:
            records.append(dict(case=name, input=inp, rejected=True, error=str(exc)))
        else:
            raise AssertionError('Counterexample unexpectedly passed: '+name)
    return records


def run_study():
    source = load_source()
    scalars, statuses = scalar_records()
    local = ROOT/'validation/module11/local'
    local.mkdir(parents=True, exist_ok=True)
    log_path = local/'d11b_trials.jsonl'
    groups, targets = [], {}
    with log_path.open('w') as log:
        for ordering in ('NO', 'IO'):
            specs = target_specs(ordering)
            targets[ordering] = []
            for spec in specs:
                M, m, U, p = target(ordering, spec['lightest_eV'], spec['alpha21_rad'], spec['alpha31_rad'], spec['parameters'])
                targets[ordering].append(dict(spec=spec, masses_eV=m.tolist(), sum_m_eV=float(sum(m)),
                    target_sha256=canonical_hash(encode(M)),
                    checks=check_target(M, m, U, ordering, p, spec['alpha21_rad'], spec['alpha31_rad'])))
            for name, scalar in scalars.items():
                # Reset seed across spectra: exactly paired dimensionless proposals.
                rng = np.random.default_rng(SEED+(ordering == 'IO'))
                successful, failures, per_target = [], [], []
                witnesses = {}
                for spec in specs:
                    current = []
                    for j, scale in enumerate((1e-10, 1e-7, 1e-5, .001, .1, 1., 4., 1e-4)):
                        t = complex(*rng.uniform(-2, 2, 2))
                        cone = dict(t=dict(real=t.real, imag=t.imag), scale=scale, root=j % 2,
                                    chart=list(list(itertools.permutations(range(3)))[j % 6]), phase_rad=float(rng.uniform(0, 2*math.pi)))
                        # All four complex coefficients are sampled in Module2's orthonormal H basis.
                        amplitude = (0., 1e-6, 1e-4, .01, .1, 1., 4., 10.)[j]
                        z = amplitude*(rng.uniform(-1, 1, 4)+1j*rng.uniform(-1, 1, 4))
                        inp = inverse_input(scalar, ordering, spec, cone, z)
                        entry = dict(target_id=spec['id'], trial=j, input=inp)
                        try:
                            metrics, out = execute(inp)
                            successful.append(metrics)
                            current.append(metrics)
                            entry.update(metrics=metrics, status='CLOSED')
                            score = metrics['selection']['overall_max']
                            for key, better in [('smallest_max', lambda old: score < old), ('largest_max', lambda old: score > old)]:
                                if key not in witnesses or better(witnesses[key]['metrics']['selection']['overall_max']):
                                    witnesses[key] = dict(target_id=spec['id'], input=inp, metrics=metrics,
                                                         Yukawas={k: out[k] for k in YUKAWAS})
                        except (ValueError, np.linalg.LinAlgError) as exc:
                            entry.update(status='UNKNOWN_OR_FAILURE', error=str(exc))
                            diagnostic = failure_diagnostics(inp)
                            entry['diagnostics_NOT_PASS'] = diagnostic
                            failures.append(dict(target_id=spec['id'], trial=j, error=str(exc), diagnostics_NOT_PASS=diagnostic))
                        log.write(json.dumps(entry, sort_keys=True, allow_nan=False)+'\n')
                    # A common orientation and zero homogeneous coefficients isolate
                    # mass, Majorana and single oscillation-coordinate dependence.
                    cone = dict(t=dict(real=.25, imag=.1), scale=.001, root=0, chart=[0, 1, 2], phase_rad=.43)
                    ref_input = inverse_input(scalar, ordering, spec, cone, np.zeros(4))
                    ref_metrics, ref_out = execute(ref_input)
                    reference = dict(metrics=ref_metrics,
                        D0_frobenius=float(np.linalg.norm(decode(ref_out['inverse']['D0']))))
                    if spec['id'] == specs[4]['id']:
                        witnesses['reference_bestfit'] = dict(target_id=spec['id'], input=ref_input,
                            metrics=ref_metrics, Yukawas={k: ref_out[k] for k in YUKAWAS})
                    per_target.append(dict(target_id=spec['id'], attempted=8, closed=len(current),
                        below_one=sum(r['selection']['below_one'] for r in current),
                        below_sqrt4pi=sum(r['selection']['below_sqrt4pi'] for r in current),
                        smallest_max=min((r['selection']['overall_max'] for r in current), default=None),
                        fixed_orientation_reference=reference))
                w = weights(**loop_inputs(scalar))
                groups.append(dict(benchmark_id=name, ordering=ordering, scalar_input_sha256=scalar['sha256'],
                    physical=scalar['record']['physical'], vacuum_status=statuses[name], loop_weights_eV=w.tolist(),
                    attempted=168, closed=len(successful), failures=failures,
                    below_one=sum(r['selection']['below_one'] for r in successful),
                    below_sqrt4pi=sum(r['selection']['below_sqrt4pi'] for r in successful),
                    closure_max=max((r['closure_relative'] for r in successful), default=None),
                    observable_roundtrip_max={k: max(r['observable_roundtrip'][k] for r in successful)
                        for k in successful[0]['observable_roundtrip']} if successful else {},
                    condition_range=[min(r['condition'] for r in successful), max(r['condition'] for r in successful)] if successful else None,
                    max_abs_ranges={k: [min(r['selection']['max_abs'][k] for r in successful), max(r['selection']['max_abs'][k] for r in successful)] for k in YUKAWAS} if successful else {},
                    per_target=per_target, witnesses=witnesses, controlled_family_target_id=specs[4]['id'],
                    controlled_family=controlled_family(scalar, ordering, specs[4])))
    paths = [SOURCE, 'module1/d10_benchmarks.json', 'validation/module1/d10_vacuum_global.json',
             'module1/D10_VACUUM_GLOBAL_AUDIT.md', 'module11/D11_NUFIT_OSCILLATION_AUDIT.md',
             'validation/module11/d11_nufit.json', 'module11/sources.json', 'module11/d11b_offline_fit.py',
             'tests/test_module11_d11b_offline_fit.py']
    paths += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'module2').glob('*.py'))]
    return dict(schema_version='D11B_OFFLINE_STUDY_V1', source=source, source_sha256={p: file_hash(p) for p in paths},
        environment=dict(python=platform.python_version(), numpy=np.__version__, mpmath=mpmath.__version__),
        labels=['D11B_OFFLINE_SECONDARY_BESTFIT_INVERSE_'+o+('_PASS' if all(
            t['closed'] > 0 for g in groups if g['ordering'] == o for t in g['per_target']) else '_BLOCKED') for o in ('NO', 'IO')]+[
            'D11B_PERTURBATIVITY_CONDITIONAL', 'D11_OFFICIAL_PROFILE_DATA_UNAVAILABLE', 'D11_FULL_JOINT_LIKELIHOOD_NOT_AVAILABLE'],
        global_zee_acceptance=None, COMPLETE_LFV=False, oscillation_chi2=None, ordering_likelihood=None,
        target_label=TARGET_LABEL, proposal_label=PROPOSAL_LABEL, seed=SEED, scalar_vacuum_statuses=statuses,
        perturbativity_criteria=dict(quantities=list(YUKAWAS), strict_max_abs_lt=1., conventional_max_abs_lt=math.sqrt(4*math.pi), interpretation='User-declared elementwise criteria, not experimental constraints'),
        sampling_interpretation='Counts depend on this finite proposal design; no statistical prior or scan-independent acceptance',
        execution_counts=dict(main_interface_inputs=672, fixed_orientation_interface_inputs=84,
            controlled_family_interface_inputs=56, counterexample_interface_inputs=7,
            failure_diagnostic_core_replays=sum(len(g['failures']) for g in groups)),
        target_checks=targets, groups=groups, counterexamples=counterexamples(scalars[BENCHMARKS[0]]),
        trial_log=dict(path=str(log_path.relative_to(ROOT)), sha256=file_hash(log_path.relative_to(ROOT)), lines=672),
        astrophysical_mass_limits='NOT_EVALUATED', Wgamma='BLOCKED', LFV='NOT_EVALUATED')


def loop_inputs(scalar):
    p = scalar['record']['physical']
    return dict(m1=p['mH1'], m2=p['mH2'], gamma=p['gamma'], ml=ML)


if __name__ == '__main__':
    report = run_study()
    dest = ROOT/'validation/module11/d11b_offline_fit.json'
    dest.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+'\n')
    for g in report['groups']:
        print(g['benchmark_id'], g['ordering'], {k: g[k] for k in ('attempted', 'closed', 'below_one', 'below_sqrt4pi', 'closure_max', 'condition_range')})
