"""Rebuild concise evidence from actual inherited, independent and CLI runs."""
import hashlib
import importlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import unittest

import mpmath
import numpy
import scipy
import sympy
from .scalar_constraints import ROOT, VERSION, provenance, strict_loads, digest


def write_json(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n')


def main():
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    if branch != 'feature/zee-scalar-module1':
        raise RuntimeError('Run validation on the isolated Module1 branch')
    logs = ROOT/'.module1_logs'; logs.mkdir(exist_ok=True)
    outdir = ROOT/'validation/module1'; outdir.mkdir(parents=True, exist_ok=True)
    # Fail-closed report is written first so a failed/interrupted rerun cannot
    # leave stale PASS evidence as the current report.
    write_json(outdir/'results.json', {'status': 'INCOMPLETE_VALIDATION', 'version': VERSION})
    (outdir/'STATUS.md').write_text('# Module 1 — validation in progress\n\nNo current acceptance; see local logs.\n')
    print('Running inherited gates, independent tests and seven full JSONL points.', flush=True)
    prov = provenance()
    sys.path.insert(0, str(ROOT/'tests'))
    inherited_names = ['test_gate6_benchmark', 'test_gateA1g_zee_oblique_T', 'test_gateA1h_correlated_stu_ewpo']
    baseline = {}
    success = True
    with (logs/'validation.log').open('w') as log:
        modules = [importlib.import_module(name) for name in inherited_names]
        inherited_suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(m) for m in modules)
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(inherited_suite)
        baseline['tests'] = result.testsRun
        success &= result.wasSuccessful()
        commands = [('gate6', ['scripts/gate6_benchmark.py']),
                    ('vacuum', ['scripts/gate6_vacuum_search.py', '--nstarts', '12']),
                    ('T', ['scripts/gateA1g_zee_oblique_T.py']),
                    ('STU', ['scripts/gateA1h_correlated_stu_ewpo.py'])]
        for name, args in commands:
            completed = subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True)
            (logs/f'inherited_{name}.log').write_text(completed.stdout+completed.stderr)
            baseline[name+'_exit'] = completed.returncode
            success &= completed.returncode == 0
        independent = importlib.import_module('test_module1_scalar')
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(independent))
        success &= result.wasSuccessful()
    if not success:
        write_json(outdir/'results.json', {'status': 'VALIDATION_FAILED', 'version': VERSION,
                                         'inherited': baseline, 'independent_tests': result.testsRun,
                                         'failures': [str(t) for t, _ in result.failures+result.errors]})
        (outdir/'STATUS.md').write_text('# Module 1 — validation FAILED\n\nSee `.module1_logs/validation.log`. No acceptance.\n')
        print('Validation failed; details: .module1_logs/validation.log', file=sys.stderr)
        return 1
    point_inputs = independent.points()
    input_file = logs/'benchmarks.jsonl'
    input_file.write_text(''.join(json.dumps(d, sort_keys=True)+'\n' for d in point_inputs))
    output_file = logs/'points.jsonl'
    completed = subprocess.run([sys.executable, '-m', 'module1.scalar_constraints', '--jsonl', '--input', str(input_file),
                                '--output', str(output_file)], cwd=ROOT, text=True, capture_output=True)
    (logs/'batch.log').write_text(completed.stdout+completed.stderr)
    if completed.returncode:
        raise RuntimeError('Full JSONL validation failed; see .module1_logs/batch.log')
    rows = [strict_loads(line) for line in output_file.read_text().splitlines()]
    if len(rows) != len(point_inputs) or [r['benchmark_id'] for r in rows] != [r['benchmark_id'] for r in point_inputs]:
        raise RuntimeError('JSONL order/count mismatch')
    single_file = logs/'point.json'
    completed = subprocess.run([sys.executable, '-m', 'module1.scalar_constraints', '--input', str(ROOT/'module1/example.json'),
                                '--output', str(single_file)], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode or strict_loads(single_file.read_text()) != rows[0]:
        raise RuntimeError('One-point CLI / batch reproducibility mismatch')
    summaries = []
    for row in rows:
        g = row['gates']
        if 'gates' not in row or g['reconstruction']['assessment'] != 'PASS' or row['global_zee_acceptance'] is not None:
            raise RuntimeError('Invalid complete point output')
        summaries.append({'benchmark_id': row['benchmark_id'], 'status': row['status'],
                          'physical': row['input']['physical'],
                          'gates': {k: {'status': v['status'], 'assessment': v['assessment']} for k, v in g.items()},
                          'tadpole_over_v3': g['reconstruction']['tadpole_max_over_v3'],
                          'hessian_spectrum_residual': g['reconstruction']['spectrum_max_relative_residual'],
                          'mixing_residual_GeV2': g['reconstruction']['mixing_max_residual_GeV2'],
                          'max_unitarity_eigenvalue': g['unitarity']['max_abs_eigenvalue'],
                          'charge_block_residual': g['unitarity']['off_block_residual'],
                          'legacy_neutral_basis_residual': g['unitarity']['gate6_neutral_all_incoming_residual'],
                          'legacy_neutral_signed_differences': g['unitarity']['gate6_neutral_signed_eigenvalues_absent_from_physical_spectrum'],
                          'STU': g['ewpo'].get('STU'),
                          'chi2_by_alternative_fit': {k: v['chi2_relative_to_fit_minimum']
                                                     for k, v in g['ewpo'].get('alternative_fits_not_combined', {}).items()},
                          'quadrature_delta': g['ewpo'].get('quadrature_max_delta'),
                          'vacuum_attempts': sum(r['attempts'] for r in g['vacuum'].get('runs', [])),
                          'vacuum_credible_minima': sum(r['credible_stationary_minima'] for r in g['vacuum'].get('runs', [])),
                          'vacuum_deeper_witness': g['vacuum'].get('deeper_witness')})
    ids = {r['benchmark_id']: r for r in summaries}
    expected = [('negative_doublet_bfb', 'bfb', 'FAIL'), ('singlet_unitarity_failure', 'unitarity', 'FAIL'),
                ('physical_deeper_singlet', 'vacuum', 'FAIL'), ('P2_beta_shift', 'vacuum', 'UNKNOWN')]
    for point, gate, status in expected:
        if ids[point]['gates'][gate]['assessment'] != status:
            raise RuntimeError('End-to-end falsifying fixture was not recognized: '+point)
    inherited_sources = json.loads((ROOT/'module1/foundation.json').read_text())['sha256']
    source_paths = [*inherited_sources, 'validation/module0/report/inventory.json', 'AGENTS.md', '.gitignore',
                    'scripts/run_module1_validation.sh', *['tests/'+n+'.py' for n in inherited_names],
                    'scripts/gate6_width_inventory.py', 'tests/test_module1_scalar.py']
    source_paths += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'module1').iterdir()) if p.is_file()]
    refs = {'reference/scalar/scripts/zee_section8_Q3_generic_scalar_bfb_witness.py':
            ['quartic', 'minimize_singlet_exact', 'deterministic_counterexamples'],
            'reference/scalar/scripts/zee_gateC4_running_55channel_unitarity.py':
            ['amplitude_response', 'scatter_matrix', 'scattering_limit'],
            'reference/scalar/scripts/zee_gateC5_charge_breaking_vacuum_search.py':
            ['potential_gradient_hessian', 'electroweak_check', 'candidate_starts', 'evaluate_multistart']}
    source_paths += list(refs)
    source_paths += [f'reference/scalar/tests/{name}' for name in
                     ('test_zee_section8_Q3_generic_scalar_bfb_witness.py', 'test_zee_gateC4_running_55channel_unitarity.py',
                      'test_zee_gateC5_charge_breaking_vacuum_search.py')]
    manifest = {'version': VERSION, 'provenance': prov,
                'tested_checkout_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'source_hashes_authoritative': True,
                'source_sha256': {name: digest(ROOT/name) for name in sorted(set(source_paths))},
                'read_only_reference_functions_consulted': refs,
                'environment': {'python': platform.python_version(), 'numpy': numpy.__version__, 'scipy': scipy.__version__,
                                'sympy': sympy.__version__, 'mpmath': mpmath.__version__},
                'local_evidence_sha256': {str(p.relative_to(ROOT)): digest(p) for p in
                                         [logs/'validation.log', input_file, output_file, single_file,
                                          *[logs/f'inherited_{n}.log' for n in ('gate6', 'vacuum', 'T', 'STU')]]}}
    write_json(outdir/'source_manifest.json', manifest)
    statuses = {'reconstruction': 'PASS', 'bfb': 'PASS_SUFFICIENT_CERTIFICATES_AND_WITNESSES_UNKNOWN_OTHERWISE',
                'unitarity': 'PASS', 'vacuum': 'PARTIAL_NUMERICAL_WITNESS_SEARCH_NOT_GLOBAL_PROOF',
                'ewpo': 'PASS_SCALAR_OBLIQUE_ONLY_BELOW_THRESHOLD', 'interface': 'PASS',
                'module0_tag_ancestry': 'BLOCKED_MISSING_GIT_OBJECT_SOURCE_HASHES_VERIFIED'}
    results = {'schema_version': VERSION, 'status': 'PARTIAL', 'gate_validation': statuses,
               'inherited': baseline, 'independent_tests': result.testsRun,
               'independent_test_failures': len(result.failures)+len(result.errors),
               'single_point_equals_batch_repeated_seed_run': True,
               'independent_residuals': independent.METRICS,
               'tolerances': {'tadpole_over_v3': 1e-9, 'spectrum_per_eigenvalue_relative': 1e-7,
                              'independent_spectrum_over_max_mass_squared': 2e-12, 'unitarity_agreement': 2e-8,
                              'STU_quadrature': 2e-8, 'negative_V4_witness_per_quartic_scale': -1e-10,
                              'vacuum_depth_over_v4': -1e-6, 'vacuum_gradient_over_v3': 2e-7,
                              'vacuum_transverse_curvature_over_v2': 2e-7},
               'benchmarks': summaries, 'source_manifest_sha256': digest(outdir/'source_manifest.json'),
               'unresolved': ['Finite vacuum search is not global stability proof.',
                              'BFB certificates are sufficient; uncertified nonnegative directions remain UNKNOWN.',
                              'EWPO is scalar oblique-only; above-threshold real-integral implementation is unsupported.',
                              'Lambda6/7 absent; RGE closure unproven; most general Zee scalar potential unsupported.',
                              'Requested Module0 tag/SHA absent locally; native archive and exact snapshot source hashes verified.'],
               'reproduce': 'bash scripts/run_module1_validation.sh'}
    write_json(outdir/'results.json', results)
    m = independent.METRICS; p2 = ids['P2_beta_shift']
    (outdir/'STATUS.md').write_text(f'''# Module 1 — PARTIAL (interface 1.0.0)

Actual validation: {baseline['tests']} inherited + {result.testsRun} independent tests, zero failures;
four inherited CLI runs and seven complete physical JSONL benchmarks. Source hashes:
[source_manifest.json](source_manifest.json). Numerical results: [results.json](results.json).
Detailed actual logs and full per-point outputs remain ignored in `.module1_logs/`.

| Gate | Validation status |
|---|---|
| Physical → SARAH Lagrangian | PASS: independent polynomial, tadpoles, Goldstones, all Hessians and signed mixing |
| BFB | PASS for sufficient all-orientation certificates and verified negative witnesses; UNKNOWN otherwise |
| 55-channel tree unitarity | PASS: canonical normalization, Q/Y blocks, basis rotations, analytic limits |
| Neutral/charge-breaking vacuum | PARTIAL: reproducible stationary-minimum witnesses; no global proof |
| Scalar one-loop S,T,U | PASS within below-threshold scalar oblique approximation |
| Versioned one-point/JSONL interface | PASS |
| Requested Module0 tag ancestry | BLOCKED: Git object/tag absent; frozen sources match archived native validation |

Independent maxima: tadpole/v³ {m['tadpole_max_over_v3']:.3e};
mass-spectrum difference/max(m²) {m['independent_mass_max_scaled_residual']:.3e};
Hessian difference/v² {m['hessian_max_difference_over_v2']:.3e};
fourth-derivative tensor {m['fourth_derivative_max_residual']:.3e};
unitarity basis eigenvalues {m['unitarity_basis_max_eigenvalue_residual']:.3e};
analytic versus quadrature loop functions {m['loop_closed_form_max_residual']:.3e}.

P2: max unitarity eigenvalue {p2['max_unitarity_eigenvalue']:.11f} < 8π;
S,T,U = {p2['STU']}; vacuum remains UNKNOWN.
The physical singlet-minimum fixture independently reproduces analytic V=-MCS2²/(4 LambdaC),
with gradient/v³ {m['deeper_stationary_witness']['gradient_over_v3']:.3e} and positive transverse Hessian.
Negative doublet BFB, complex orientation/portal runaways, tree unitarity failure,
and a deeper charge-breaking vacuum are explicitly falsified by real calculations.

The inherited neutral 13x13 matrix has signed differences from physical scattering:
an explicit all-incoming basis lift reproduces them; absolute spectra and bound agree.
The disputed EWPO -1/2 coefficient shifts P2 T by {m['disputed_T_shift']:.9f}; use Grimus -2.
Alternative covariance fits are never combined. Fixed 125 GeV SM subtraction also
works for arbitrary light-Higgs inputs.

Scientific limits: sufficient BFB is not necessary; marginal/uncertified points are UNKNOWN.
Numerical vacuum sampling never means globally stable. Only the restricted CP-conserving
scalar potential is implemented; complex lepton Yukawas do not make it the most general
scalar potential. Lambda6/7 RG closure is unproven. No global Zee acceptance, scan cohort
classification, collider/flavour acceptance, native SARAH rerun or RG result is claimed.
Frozen Module0 scripts/model and the original `~/zee` working tree are unchanged.

Reproduce: `bash scripts/run_module1_validation.sh`.
Use: `python3 -m module1.scalar_constraints --input module1/example.json`.
Contract and derivations: [../../module1/README.md](../../module1/README.md).
''')
    print(f"PARTIAL: {baseline['tests']} inherited + {result.testsRun} independent tests passed; 7 complete benchmarks.")
    print('Reports: validation/module1/{STATUS.md,results.json,source_manifest.json}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
