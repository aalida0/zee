"""Reproduce the isolated D16 partial result and its precise blocked status.

python3 -m research.wgamma_d16.reproduce --native
No network, model regeneration, SPheno compilation or global tests.
"""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys

import numpy
import scipy
import sympy

from .algebra import (abe_A_double_integral, angular_projection, corrected_abe_B8_photon,
                      projected_source_check, reference_kernels)
from .matching import HERE, ROOT, conditional_source_A, encode, evaluate, example
from .symbolic_reductions import reductions

D15 = 'f6676356a95517f2820dea79298a938cc8786968'
FROZEN_SOURCES = ['models/SARAH/ZeeTypeII/'+name+'.m' for name in
                  ('ZeeTypeII', 'parameters', 'particles')] + [
    'module1/scalar_constraints.py', 'module1/example.json', 'module3/core.py',
    'module4/MATCHING_AUDIT.md', 'module4/CONVENTIONS.md', 'module4/couplings.py',
    'research/spheno_flavorkit/CROSSING_BRIDGE.md']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_log(cmd, log):
    with log.open('w') as stream:
        result = subprocess.run(cmd, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'{cmd[0]} exited {result.returncode}; see {log}')


def materialize_native():
    local = HERE/'local'
    raw = json.loads((local/'vertices.json').read_text())
    checked = json.loads((local/'vertex_checks.json').read_text())
    counted = json.loads((local/'fa-count.json').read_text())
    if checked['status'] != 'PASS' or counted['status'] != 'PASS':
        raise RuntimeError('Native coefficient/topology checks did not pass')
    inputs = json.loads((local/'vertex_inputs.json').read_text())
    native = dict(status='PASS', scope='Tree vertices only; loop matching BLOCKED_GAUGE_MATCHING',
        query_count=raw['query_count'], raw=raw['raw'],
        coefficient_validation=dict(status=checked['status'], check_count=len(checked['checks']),
                                    max_abs_residual=checked['max_abs_residual'],
                                    points=2, xis=[.5, 1., 3.]),
        returned_structures=checked['returned_structures'],
        frozen_source_sha256={p: sha(ROOT/p) for p in FROZEN_SOURCES},
        driver_sha256={p: sha(HERE/p) for p in ('extract_vertices.m', 'prepare_vertices.py',
                                                'validate_vertices.m', 'count_inner.m')},
        mathematica_version=raw['mathematica_version'], sarah_version=raw['sarah_version'],
        topology_crosscheck={k: counted[k] for k in ('status', 'scope', 'classes_amplitudes', 'feynarts_version')},
        input_sha256=sha(local/'vertex_inputs.json'),
        physical_inputs=[r['physical'] for r in inputs],
        raw_package_sha256=sha(local/'vertices_raw.m'),
        raw_json_sha256=sha(local/'vertices.json'),
        full_coefficient_checks_sha256=sha(local/'vertex_checks.json'))
    (HERE/'native_vertices.json').write_text(json.dumps(native, indent=2, sort_keys=True)+'\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', action='store_true', help='Refresh native SARAH and independent FeynArts topology evidence')
    args = parser.parse_args()
    local = HERE/'local'
    local.mkdir(exist_ok=True)
    if args.native:
        run_log([sys.executable, '-m', 'research.wgamma_d16.prepare_vertices'], local/'prepare.log')
        for script, log in [('extract_vertices.m', 'native.log'), ('validate_vertices.m', 'vertex-checks.log'),
                            ('count_inner.m', 'count-inner.log')]:
            run_log(['math', '-script', str(HERE/script)], local/log)
        materialize_native()
    elif not (HERE/'native_vertices.json').exists():
        materialize_native()
    # Assert the frozen tracked trees, independently of current working-tree status.
    protected = ['module'+str(i) for i in range(15)] + ['models', 'research/spheno_flavorkit']
    for revision in (D15, 'HEAD'):
        tree = subprocess.check_output(['git', 'ls-tree', revision, '--', *protected], cwd=ROOT)
        if revision == D15:
            original_tree = tree
        elif tree != original_tree:
            raise RuntimeError('Frozen source trees differ from the D15 milestone')
    subprocess.run(['git', 'diff', '--exit-code', D15, '--', *protected], cwd=ROOT, check=True)
    for spec in json.loads((HERE/'sources.json').read_text()).values():
        cached = local/spec['local_cache']
        if cached.exists() and sha(cached) != spec['sha256']:
            raise RuntimeError('Cached primary source hash differs: '+str(cached))
    run_log([sys.executable, '-m', 'unittest', 'research.wgamma_d16.test_d16', '-v'], local/'tests.log')
    runs = []
    for index in (0, 1):
        inp = example(index)
        (local/f'input-{index}.json').write_text(json.dumps(inp, indent=2)+'\n')
        result = evaluate(inp)
        (local/f'result-{index}.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
        kernel, _ = conditional_source_A(inp)
        integral, _ = conditional_source_A(inp, method='double-integral')
        runs.append(dict(input_sha256=result['provenance']['input_sha256'],
            result_sha256=sha(local/f'result-{index}.json'),
            conditional_A_only_C_L=encode(kernel[0]), conditional_A_only_C_R=encode(kernel[1]),
            conditional_A_radial_relative_residual=float(max(abs(kernel-integral)/abs(kernel))),
            mass_replacement_falsifier=result['gauge_falsifier']))
    sources = {str(p.relative_to(ROOT)): sha(p) for p in HERE.iterdir()
               if p.suffix in ('.py', '.m', '.md') or p.name in ('.gitignore', 'sources.json', 'native_vertices.json')}
    code_sha = hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()
    source_checks = []
    for delta, masses in ((.73, (125., 437.)), (-.29, (172., 653.))):
        source_checks.append(dict(delta=delta, neutral_masses_GeV=masses,
                                  residuals=projected_source_check(delta=delta, masses=masses)))
    evidence = dict(status='BLOCKED_GAUGE_MATCHING', physical_status='UNKNOWN',
        acceptance_target='WGAMMA_GAUGE_MATCHING_PASS', acceptance_reached=False,
        physical_W_C_L=None, physical_W_C_R=None, coherent_inclusion=False,
        starting_D15_commit=D15,
        source_parent_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        frozen_tree_listing_sha256=hashlib.sha256(original_tree).hexdigest(),
        source_sha256=sources, source_bundle_sha256=code_sha,
        environment=dict(python=platform.python_version(), numpy=numpy.__version__, scipy=scipy.__version__,
                         sympy=sympy.__version__),
        tests=dict(status='PASS', count=10, scope='Only research.wgamma_d16.test_d16; not full gauge amplitude'),
        native=json.loads((HERE/'native_vertices.json').read_text())['coefficient_validation'],
        symbolic=reductions(), source_tensor_checks=source_checks,
        angular_projection_abs_residual=angular_projection(),
        reference_checks=[dict(z=z, **reference_kernels(z),
                               independent_A_radial=abe_A_double_integral(z),
                               erratum_B8_photon_over_2e=corrected_abe_B8_photon(z)/2)
                          for z in (.013, .413, 2.7)],
        diagnostic_points=runs,
        full_projected_Rxi=dict(status='NOT_EVALUATED', xis_requested=[.5, 1., 3.],
                               coefficients=[None, None, None]),
        minimal_missing_identity='Delta_xi(C_W+C_mixed+C_ghost+C_pinch)=-Delta_xi C_G',
        logs={str(p.relative_to(ROOT)): sha(p) for p in local.iterdir()
              if p.name in ('native.log', 'vertex-checks.log', 'count-inner.log', 'tests.log',
                            'vertices_raw.m', 'vertex_checks.json', 'fa-inner.m', 'fa-inner-amplitudes.m')})
    (HERE/'evidence.json').write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False)+'\n')
    print('10 scoped tests PASS; 444 native checks PASS; physics BLOCKED_GAUGE_MATCHING')
    print('Evidence:', HERE/'evidence.json')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
