"""Read-only source probes and bounded upstream LFV controls; never a Zee gate."""
import argparse
import ast
import importlib.util
import math
from pathlib import Path

from module14.scan import file_sha
from module14.conditional_scan.workflow import load
from module14.final_workflow import write_atomic

BASE = Path(__file__).resolve().parent


def probe(tool, source):
    lock = load(BASE/'public_source_lock.json')['tools'][tool]
    source = Path(source)
    failures = [name for name, sha in lock['files_sha256'].items()
                if not (source/name).is_file() or file_sha(source/name) != sha]
    return {'tool': tool, 'source_version': lock['source_version'],
            'source_status': 'SOURCE_MATCH' if not failures else 'UNAVAILABLE_OR_CHANGED',
            'failed_files': failures, 'zee_physics_status': 'UNVALIDATED',
            'operative_constraint': False}


def lfv_control(source):
    report = probe('general_2hdm', source)
    if report['failed_files']: raise ValueError('Pinned public LFV source mismatch')
    source = Path(source)
    tree = ast.parse((source/'example.py').read_text())
    dictionary = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == 'testinput' for t in n.targets))
    # Only the byte-pinned upstream example dictionary is evaluated; never
    # execute example.py or accept a caller-provided parameter card here.
    inputs = eval(compile(ast.Expression(dictionary), '<pinned-upstream-example>', 'eval'), {'__builtins__': {}})
    spec = importlib.util.spec_from_file_location('d14_pinned_thdm_control', source/'thdm.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    model = module.thdm(inputs); reference = load(BASE/'public_lfv_control.json')
    results = {}
    for i, j in ((2, 1), (3, 1), (3, 2)):
        cr, cl = model.cR_llpg(i, j), model.cL_llpg(i, j)
        rate = model.Gamma_l_to_lp_gamma(i, j)
        expected = reference['example'][f'{i}_{j}']
        for key, value in (('cR', cr), ('cL', cl)):
            target = complex(**expected[key])
            if abs(value-target) > 2e-12*abs(target): raise ValueError('Upstream complex control regression')
        identity = model.ml(i)**5*model.alphaQED/(256*math.pi**4*model.vev**4)*(abs(cr)**2+abs(cl)**2)
        if not math.isclose(rate, identity, rel_tol=2e-14) or not math.isclose(rate, expected['Gamma_GeV'], rel_tol=2e-12):
            raise ValueError('Upstream rate control regression')
        results[f'{i}_{j}'] = rate
    # Analytic flavor-conserving limiting case, at the original upstream
    # spectrum. This is not a parameter proposal or a Zee benchmark.
    for i in (1, 2, 3):
        for j in (1, 2, 3):
            if i != j: inputs[f'absrhol{i}{j}'] = 0.
    model = module.thdm(inputs)
    null = [model.Gamma_l_to_lp_gamma(i, j) for i, j in ((2, 1), (3, 1), (3, 2))]
    if null != [0., 0., 0.]: raise ValueError('Flavor-diagonal null control failed')
    return dict(report, control_status='PASS', scope='UPSTREAM_CONTROL_ONLY',
                rates_GeV=results, flavor_diagonal_null_GeV=null,
                zee_adapter='UNVALIDATED', complete_zee_lfv=None)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('probe', 'lfv-control'))
    p.add_argument('--tool', choices=tuple(load(BASE/'public_source_lock.json')['tools']), default='general_2hdm')
    p.add_argument('--source', required=True); p.add_argument('--output', required=True)
    a = p.parse_args()
    if a.action == 'lfv-control' and a.tool != 'general_2hdm': p.error('Only the pinned upstream LFV control is executable')
    r = lfv_control(a.source) if a.action == 'lfv-control' else probe(a.tool, a.source)
    write_atomic(a.output, r)
    return 0 if r['source_status'] == 'SOURCE_MATCH' else 2


if __name__ == '__main__': raise SystemExit(main())
