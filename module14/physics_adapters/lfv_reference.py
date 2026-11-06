"""Read pinned upstream neutral-fermion photon terms for reference comparisons.

No total 2HDM rate is exposed as a Zee prediction. This subset overlaps the
existing Module4 ledger and must NEVER be added to it a second time.
"""
import ast
import importlib.util
import math
from pathlib import Path

import numpy as np

from module14.public_reuse import probe
from module14.scan import digest, file_sha
from module14.conditional_scan.workflow import load


def load_reference(source):
    source = Path(source)
    report = probe('general_2hdm', source)
    if report['failed_files']:
        raise ValueError('Pinned public LFV source mismatch')
    spec = importlib.util.spec_from_file_location('d14_lfv_reference', source/'thdm.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    tree = ast.parse((source/'thdm.py').read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'thdm')
    functions = {}
    for chirality in ('L', 'R'):
        name = 'c'+chirality+'_llpg'
        fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
        names = [name+'_'+x for x in ('th', 'ch', 'bh', 'tauh')]
        selected = [n for n in fn.body if isinstance(n, ast.Assign)
                    and isinstance(n.targets[0], ast.Name) and n.targets[0].id in names]
        if len(selected) != 4:
            raise ValueError('Upstream subset structure mismatch')
        fn.body = selected+[ast.Return(ast.Tuple([ast.Name(x, ast.Load()) for x in names], ast.Load()))]
        env = vars(module).copy()
        exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])),
                     str(source/'thdm.py'), 'exec'), env)
        functions[chirality] = env[name]
    dictionary = next(n.value for n in ast.parse((source/'example.py').read_text()).body
                      if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name)
                      and t.id == 'testinput' for t in n.targets))
    inputs = eval(compile(ast.Expression(dictionary), '<pinned-example>', 'eval'), {'__builtins__': {}})
    return module, functions, inputs


def fixed_card_reference(source, witness):
    """All three radiative channels, four neutral-fermion photon species.

    Paper Eqs.11,48: rho_l=D/sqrt(2); theta12=beta-alpha,
    theta13=theta23=0; C_(L,R)=-c_(L,R)/(8*pi²*v²).
    Only the vZ_e factors in these fermionic expressions are set to zero to
    project the separately transverse photon exchange. No bosonic gauge
    group is split. The neutral subset is independent of F/mixed H+.
    """
    reference = Path(__file__).resolve().parents[2]/'validation/module12/d12_benchmarks.json'
    if file_sha(reference) != 'f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8':
        raise ValueError('Original D12 reference checksum mismatch')
    if digest(witness) not in {digest(g['witnesses']['central']) for g in load(reference)['groups']}:
        raise ValueError('Only the four original D12 central cards are authorized')
    module, functions, inputs = load_reference(source)
    p = witness['module2_input']['scalar']['record']['physical']
    ml = witness['module2_input']['lepton_masses_GeV']
    d = witness['yukawas']['D']
    rho = (np.array(d['real'])+1j*np.array(d['imag']))/math.sqrt(2)
    inputs.update(theta12=p['beta']-p['alpha'], theta13=0., theta23=0.,
                  Mh1=p['mh1'], Mh2=p['mh2'], Mh3=p['ma'], MHp=p['mH1'],
                  vev=p['v'], melectron=ml[0], mmuon=ml[1], mtau=ml[2])
    for f in ('u', 'd', 'l'):
        matrix = rho if f == 'l' else np.zeros((3, 3), complex)
        for i in range(3):
            for j in range(3):
                inputs[f'absrho{f}{i+1}{j+1}'] = abs(matrix[i,j])
                inputs[f'argrho{f}{i+1}{j+1}'] = np.angle(matrix[i,j])
    control = module.thdm(inputs)
    masses = {'top': control.mt, 'charm': control.mc, 'bottom': control.mb, 'tau': control.mtau}
    for f, k, mass, factor in [('u',3,control.mt,1/math.tan(p['beta'])),
                              ('u',2,control.mc,1/math.tan(p['beta'])),
                              ('d',3,control.mb,-math.tan(p['beta']))]:
        value = mass/p['v']*factor
        inputs[f'absrho{f}{k}{k}'] = abs(value)
        inputs[f'argrho{f}{k}{k}'] = 0. if value >= 0 else math.pi
    model = module.thdm(inputs)
    model.vZe = 0.
    coefficients = {}
    for i, j in ((2,1), (3,1), (3,2)):
        vals = {c: functions[c](model, i, j) for c in functions}
        coefficients[f'{i}_{j}'] = -np.array([vals['L'], vals['R']]).T/(8*math.pi**2*p['v']**2)
    return coefficients, masses, model.alphaQED
