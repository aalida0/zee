"""Bounded LFV source/rate audit. No model adapter, fitted points, or exclusions.

Compiles the hash-locked, unmodified FlavorKit observable body in a disposable
driver. Independently contracts four-fermion actions with Dirac spin densities.
Only the four original D12 cards are evaluated. Third-party code is not vendored.
"""
import argparse
import ast
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from module2.interface import canonical_hash, decode, evaluate as neutrino_evaluate
from module3 import tree
from module3.core import vertices
from module14.lfv import evaluate_family
from scripts.zee_d14_lfv_reference import compare

HERE = Path(__file__).resolve().parent
OPERATORS = ('SLL', 'SRR', 'SLR', 'SRL', 'VLL', 'VRR', 'VLR', 'VRL', 'TLL', 'TRR')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_check(manifest):
    """Missing or modified source is an error, never a physics PASS."""
    checked = []
    for item in manifest['artifacts']:
        path = Path(item['path_hint'])
        if not path.is_absolute():
            path = ROOT/path
        if not path.is_file() or sha(path) != item['sha256']:
            raise ValueError('Missing/changed pinned artifact: '+item['id'])
        checked.append(item['id'])
    return checked


def group_inventory(source):
    cls = next(n for n in ast.parse(Path(source).read_text()).body
               if isinstance(n, ast.ClassDef) and n.name == 'thdm')
    result = {}
    for chirality in ('L', 'R'):
        name = 'c'+chirality+'_llpg'
        fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
        rows = []
        for node in fn.body:
            if (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id.startswith(name+'_')):
                attributes = sorted({n.attr for n in ast.walk(node.value)
                                     if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
                                     and n.value.id == 'self'})
                rows.append(dict(group=node.targets[0].id[len(name)+1:], line=node.lineno,
                                 self_attributes=attributes,
                                 charged_mass_dependent=any(a == 'MHp' or a.startswith(('xHh', 'xwH'))
                                                            for a in attributes)))
        if len(rows) != 13:
            raise ValueError('Pinned radiative group inventory changed')
        result[chirality] = rows
    return result


def contact_tensor(coefficients):
    """Action: sum A_XY (ubar1 Gamma_X u)(ubar2 Gamma_Y v) - (1<->2).

    sigma=i[gamma,gamma]/2, metric (+---), full mu,nu tensor contraction.
    These are arbitrary EFT test coefficients, not Zee parameter cards.
    """
    result = np.zeros((4, 4, 4, 4), complex)
    projectors = {'L': tree.PL, 'R': tree.PR}
    metric = (1, -1, -1, -1)
    for name, value in coefficients.items():
        x, y = (projectors[c] for c in name[1:])
        if name[0] == 'S':
            terms = [(x, y, 1)]
        elif name[0] == 'V':
            terms = [(g@x, g@y, metric[mu]) for mu, g in enumerate(tree.G)]
        elif name[0] == 'T':
            terms = []
            for mu, g in enumerate(tree.G):
                for nu, h in enumerate(tree.G):
                    sigma = .5j*(g@h-h@g)
                    terms.append((sigma@x, sigma@y, metric[mu]*metric[nu]))
        else:
            raise ValueError('Unsupported action')
        result += value*sum(w*np.einsum('ab,cd->abcd', tree.G0@a, tree.G0@b)
                            for a, b, w in terms)
    return result-result.transpose(2, 1, 0, 3)


def contact_width(coefficients, mass=1., order=12):
    tensor = contact_tensor(coefficients)
    # Independent spin-density integral, average over parent and divide by 2!
    return sum(w*tree.spin_sum(tensor, ps, mass, (0., 0., 0.))/2
               for ps, _, _, w in tree.phase_grid(mass, 0., 0., 0., order))


def fortran_driver(body):
    """Embed original observable bytes as a subroutine, without modifying it."""
    arrays = ['K1L', 'K1R', 'K2L', 'K2R']+['O4l'+x for x in OPERATORS]
    decl = '\n'.join('complex(dp) :: '+x+('(3,3)' if x.startswith('K') else '(3,3,3,3)') for x in arrays)
    zero = '\n'.join(x+'=0' for x in arrays)
    assign = '\n'.join(x+('(2,1)' if x.startswith('K') else '(2,1,1,1)')+'=values('+str(i)+')'
                       for i, x in enumerate(arrays, 1))
    return ('''module audit
implicit none
integer,parameter :: dp=kind(1.d0)
real(dp),parameter :: Pi=acos(-1._dp), oo512pi3=1._dp/(512._dp*Pi**3)
real(dp) :: Alpha_MZ, mf_l(3), GammaMu, GammaTau
real(dp) :: BRmuTo3e, BRtauTo3e, BRtauTo3mu
'''+decl+'''
contains
subroutine observable()
'''+body+'''
end subroutine
end module
program main
use audit
implicit none
complex(dp) :: values(14)
integer :: k, ios
do
read(*,*,iostat=ios) Alpha_MZ, mf_l, GammaMu, GammaTau
if (ios/=0) exit
read(*,*) values
'''+zero+'\n'+assign+'''
call observable()
write(*,'(ES26.17E3)') BRmuTo3e
end do
end program
''')


class Observable:
    def __init__(self, source, work):
        path = Path(work)/'observable.f90'
        path.write_text(fortran_driver(Path(source).read_text()))
        self.executable = Path(work)/'observable'
        subprocess.run(['gfortran', '-O0', '-fcheck=all', '-ffree-line-length-none',
                        str(path), '-o', str(self.executable)], cwd=work, check=True,
                       capture_output=True, text=True)
        self.driver_sha256 = sha(path)

    def rate(self, coefficients, ml=(.000511, 1., 1.77686), alpha=1/137.035999084,
             width=1.):
        names = ('K1L', 'K1R', 'K2L', 'K2R')+OPERATORS
        if set(coefficients)-set(names):
            raise ValueError('Unknown observable coefficient')
        data = ' '.join(format(float(x), '.17g') for x in (alpha, *ml, width, 1.))+'\n'
        data += ' '.join('('+format(complex(coefficients.get(k, 0)).real, '.17g')+','+
                         format(complex(coefficients.get(k, 0)).imag, '.17g')+')' for k in names)+'\n'
        return float(subprocess.run([str(self.executable)], input=data, capture_output=True,
                                    text=True, check=True).stdout)


def rate_controls(observable):
    fixtures = {name: {name: 1.} for name in OPERATORS}
    fixtures.update(complex_all={k: (i+1)*.07+1j*((i%3)-1)*.13 for i, k in enumerate(OPERATORS)},
                    scalar_vector={'SLR': .31+.47j, 'VLR': -.23+.19j},
                    scalar_tensor={'SLL': .31+.47j, 'TLL': -.23+.19j})
    results = []
    for name, coefficients in fixtures.items():
        independent = contact_width(coefficients)
        actual = observable.rate(coefficients)
        residual = abs(actual/independent-1)
        if residual > 2e-12:
            raise ArithmeticError('Contact action/FlavorKit mismatch: '+name)
        isolated = sum(contact_width({k: v}) for k, v in coefficients.items())
        results.append(dict(name=name, coefficients={k: [complex(v).real, complex(v).imag]
                             for k, v in coefficients.items()}, trace_width=independent,
                            FlavorKit_width=actual, relative_residual=residual,
                            interference_width=independent-isolated))
    # Independent published dipole-dominance ratio, Kuno/Okada (hep-ph/9909265).
    alpha = 1/137.035999084
    ml = (.00051099895, .1056583755, 1.77686)
    dipole = np.array([.37+.83j, -.29+.41j])*1e-10
    gamma = alpha*ml[1]**5/4*sum(abs(dipole)**2)  # leading daughter-mass order
    ratio = alpha/(3*math.pi)*(math.log((ml[1]/ml[0])**2)-11/4)
    actual = observable.rate({'K2L': dipole[0], 'K2R': dipole[1]}, ml, alpha)
    if abs(actual/(gamma*ratio)-1) > 2e-14:
        raise ArithmeticError('Dipole normalization mismatch')
    # Check the common phase, relative phase, and K1 -> vector shift in actual source.
    base = {'K2L': .3+.7j, 'K2R': -.4+.2j, 'SLR': .2-.6j, 'SRL': -.1+.4j,
            'VLL': .5+.2j, 'VRR': -.3-.1j, 'VLR': .7-.4j, 'VRL': -.5+.3j}
    coherent = observable.rate(base)
    phased = observable.rate({k: v*np.exp(.73j) for k, v in base.items()})
    reversed_phase = observable.rate(dict(base, SLR=base['SLR'].conjugate()))
    separated = sum(observable.rate({k: v}) for k, v in base.items())
    k1 = .31+.29j
    e2 = 4*math.pi*alpha
    k1_rate = observable.rate(dict(base, K1L=k1))
    vector_rate = observable.rate(dict(base, VLL=base['VLL']+e2*k1, VLR=base['VLR']+e2*k1))
    if (abs(phased/coherent-1) > 2e-14 or abs(k1_rate/vector_rate-1) > 2e-14
            or abs(reversed_phase/coherent-1) < 1e-4 or abs(separated/coherent-1) < 1e-4):
        raise ArithmeticError('Complex interference falsifier failed')
    return dict(contact_actions=results, dipole_ratio=ratio, dipole_width=actual,
                dipole_relative_residual=abs(actual/(gamma*ratio)-1),
                phase_controls=dict(coherent=coherent, common_phase=phased,
                    conjugate_one_coefficient=reversed_phase, incoherent=separated,
                    K1_to_vector_relative_residual=abs(k1_rate/vector_rate-1)),
                scope='RATE_FUNCTION_ONLY; no Zee loop-operator or dipole/contact relative-sign validation')


def original_cards(observable):
    path = ROOT/'validation/module12/d12_benchmarks.json'
    if sha(path) != 'f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8':
        raise ValueError('Original D12 cards changed')
    results = []
    experiments = json.loads((HERE/'experiments.json').read_text())
    for index, group in enumerate(json.loads(path.read_text())['groups']):
        w = group['witnesses']['central']
        inp = w['module2_input']
        scalar_sha = canonical_hash(inp['scalar']['record'])
        if scalar_sha != w['scalar_sha256'] or scalar_sha != group['scalar_sha256']:
            raise ValueError('Original scalar binding mismatch')
        nout = neutrino_evaluate(inp)
        if canonical_hash(nout) != w['module2_output_sha256']:
            raise ArithmeticError('Frozen neutrino receipt mismatch')
        family = dict(w['yukawas'], Mnu=nout['Mnu'], input=inp, input_sha256=canonical_hash(inp))
        output = evaluate_family(family, tree_enabled=True)
        p = inp['scalar']['record']['physical']
        ml = np.array(inp['lepton_masses_GeV'])
        scalar = vertices(decode(w['yukawas']['D']), p, ml)
        # Direct ordered coefficient, same action as the frozen tree tensor.
        wilsons = tree.wilsons(scalar, 1, 0, 0)
        coefficients = {x: sum(row['direct'][x] for row in wilsons.values())
                        for x in ('LL', 'RR', 'LR', 'RL')}
        coefficients = {'S'+k: v for k, v in coefficients.items()}
        alpha = json.loads((ROOT/'module3/example.json').read_text())['constants']['alpha_em']
        width = json.loads((ROOT/'module3/example.json').read_text())['constants']['total_lepton_widths_GeV'][0]
        # Exact source routine is a massless-final-state/contact approximation.
        native = observable.rate(coefficients, ml, alpha, width)
        trace = contact_width(coefficients, mass=ml[1])/width
        if abs(native/trace-1) > 2e-12:
            raise ArithmeticError('D12 complex tree action normalization mismatch')
        full_tree = output['mu_to_3e']['tree_subset_BR']
        if full_tree != w['mu_to_3e_tree']:
            raise ArithmeticError('Frozen tree receipt mismatch')
        for name, channel in output['channels'].items():
            if channel['partial_BR'] != w['radiative'][name]:
                raise ArithmeticError('Frozen partial dipole receipt mismatch')
        c = output['channels']['mu_to_e_gamma']
        K = {k: -complex(c[ch]['real'], c[ch]['imag']).conjugate()
             for k, ch in [('K2L', 'C_L'), ('K2R', 'C_R')]}
        diagnostic = observable.rate(K, ml, alpha, width)
        results.append(dict(group=index, id=w['id'],
            scalar_sha256=scalar_sha, neutrino_input_sha256=canonical_hash(inp),
            witness_sha256=canonical_hash(w), module4_output_sha256=output['module4_output_sha256'],
            scalar_contact_coefficients={k: [v.real, v.imag] for k, v in coefficients.items()},
            partial_dipole_coefficients={k: c[k] for k in ('C_L', 'C_R')},
            total_mu_width_GeV=width, alpha_em=alpha, tree_BR=full_tree,
            massless_contact_tree_BR=native, independent_trace_tree_BR=trace,
            contact_trace_relative_residual=abs(native/trace-1),
            finite_mass_propagator_relative_shift=full_tree/native-1,
            partial_mu_gamma_BR=c['partial_BR'],
            partial_mu_gamma_to_observed_limit_DIAGNOSTIC=c['partial_BR']/experiments['limits']['mu_to_e_gamma']['upper_limit'],
            partial_dipole_only_mu3e_BR_DIAGNOSTIC=diagnostic,
            partial_dipole_only_mu3e_to_observed_limit_DIAGNOSTIC=diagnostic/experiments['limits']['mu_to_3e']['upper_limit'],
            dipole_only_to_tree=diagnostic/full_tree,
            physical_comparison='UNKNOWN', exclusion=None))
    return results


def conversion_sign_control(source, work):
    """Execute original MuEconversion body on one EFT u-scalar insertion.

    The independent reference is Z*g_p+N*g_n, equivalently published Eq.(27)
    of arXiv:1405.1434v3. This is a source regression, not a Zee prediction.
    """
    names = ['K1L', 'K1R', 'K2L', 'K2R']
    names += ['Oll'+q+x for q in ('uu', 'dd') for x in OPERATORS if x[0] != 'T']
    outputs = ['CRMuE'+x for x in ('Al', 'Ti', 'Sr', 'Sb', 'Au', 'Pb')]
    declarations = '\n'.join('complex(dp) :: '+x+('(3,3)' if x.startswith('K') else '(3,3,3,3)')
                             for x in names)
    text = '''module audit_conversion
implicit none
integer,parameter :: dp=kind(1.d0)
real(dp),parameter :: Pi=acos(-1._dp), oo8pi2=1._dp/(8._dp*Pi**2)
real(dp),parameter :: Alpha=1._dp/137.035999084_dp, Alpha_MZ=Alpha, G_F=1.1663787e-5_dp
real(dp),parameter :: mf_l(3)=[.00051099895_dp,.1056583755_dp,1.77686_dp]
'''+declarations+'\nreal(dp) :: '+','.join(outputs)+'''
contains
subroutine observable()
'''+Path(source).read_text()+'''
end subroutine
end module
program main
use audit_conversion
implicit none
'''+ '\n'.join(x+'=0' for x in names)+'''
! With the actual normalization this produces gLS(up)=1, all other g's=0.
OlluuSLL(2,1,1,1)=-sqrt(2._dp)*G_F
call observable()
'''+ '\n'.join("write(*,'(ES26.17E3)') "+x for x in outputs)+'''
end program
'''
    path = Path(work)/'conversion.f90'
    path.write_text(text)
    executable = Path(work)/'conversion'
    subprocess.run(['gfortran', '-O0', '-fcheck=all', '-ffree-line-length-none',
                    str(path), '-o', str(executable)], cwd=work, check=True, capture_output=True)
    actual = np.array([float(x) for x in subprocess.check_output([str(executable)], text=True).split()])
    nuclei = [('Al', 13, 14, 11.5, .64, 4.64079e-19),
              ('Ti', 22, 26, 17.6, .54, 1.70422e-18),
              ('Sr', 38, 42, 25., .39, 4.61842e-18),
              ('Sb', 51, 70, 29., .32, 6.71711e-18),
              ('Au', 79, 118, 33.5, .16, 8.59868e-18),
              ('Pb', 82, 125, 34., .15, 8.84868e-18)]
    results = []
    for value, (target, z, n, zeff, fp, capture) in zip(actual, nuclei):
        expected_current = z*5.1+n*4.3
        exchanged_current = z*4.3+n*5.1
        prefactor = .1056583755**5*(1.1663787e-5)**2*(1/137.035999084)**3
        prefactor *= zeff**4*fp**2/(8*math.pi**2*z*capture)
        reference = prefactor*expected_current**2
        swapped = prefactor*exchanged_current**2
        # Original GSp/GSn literals lack _dp: single precision before assignment.
        if abs(value/swapped-1) > 1e-7 or abs(value/reference-1) < 1e-4:
            raise ArithmeticError(f'Conversion scalar sign discrepancy not reproduced: {target} '
                                  f'{value=}, {swapped=}, {reference=}')
        results.append(dict(target=target, source_rate=value, direct_proton_neutron_rate=reference,
                            source_over_reference=value/reference,
                            swapped_rounding_relative_residual=abs(value/swapped-1),
                            expected_scalar_current=expected_current,
                            source_scalar_current=exchanged_current))
    return dict(status='SOURCE_DISCREPANCY_REPRODUCED', driver_sha256=sha(path),
                expected='Z*g_p+N*g_n; plus scalar isovector term in published Eq.(27)',
                source='Z*g_n+N*g_p in scalar sector; vector sector retains correct assignment',
                scope='EFT scalar-only source control; no Zee Wilsons or physical conversion exclusion',
                numerical_tolerance=1e-7,
                tolerance_reason='Original GSp/GSn decimal literals are default-real before double assignment',
                records=results)


def run(manifest_path):
    manifest = json.loads(Path(manifest_path).read_text())
    checked = source_check(manifest)
    by_id = {x['id']: x for x in manifest['artifacts']}
    with tempfile.TemporaryDirectory(prefix='zee-lfv-') as work:
        native = Observable(by_id['flavorkit_Lto3Lp']['path_hint'], work)
        controls = rate_controls(native)
        cards = original_cards(native)
        driver_sha = native.driver_sha256
        conversion = conversion_sign_control(by_id['flavorkit_MuEconversion']['path_hint'], work)
    reference = compare(Path(by_id['general_2hdm_thdm']['path_hint']).parent)
    if reference != json.loads((ROOT/'module14/physics_adapters/lfv_reference_evidence.json').read_text()):
        raise ArithmeticError('Frozen public-reference evidence replay mismatch')
    source_check(manifest)  # third-party/frozen bytes must remain unchanged
    return dict(schema='zee-lfv-validation-1', date='2026-11-07',
                status='LFV_FULL_COVERAGE_BLOCKED', physical_lfv='UNKNOWN',
                scoped_observable_validated=False, complete_lfv=False,
                exclusion=None, global_acceptance=None, added_amplitudes=[],
                new_model_cards=0, scans=0, native_spectrum_runs=0,
                manifest_sha256=sha(manifest_path), checked_artifacts=checked,
                experimental_snapshot_sha256=sha(HERE/'experiments.json'),
                code_sha256=sha(__file__), driver_sha256=driver_sha,
                environment=dict(python=platform.python_version(), numpy=np.__version__,
                    gfortran=subprocess.check_output(['gfortran', '--version'], text=True).splitlines()[0]),
                rate_controls=controls, original_D12_cards=cards,
                public_2hdm_group_inventory=group_inventory(by_id['general_2hdm_thdm']['path_hint']),
                conversion_scalar_isovector_control=conversion,
                frozen_neutral_fermion_photon_replay=dict(comparisons=len(reference['comparisons']),
                    max_relative_residual=max(r['max_relative_residual'] for r in reference['comparisons']),
                    double_counting=reference['double_counting']),
                unvalidated=['Zee full two-loop dipoles', 'fixed-physical-scheme one-loop four-lepton operators',
                    'dipole/contact relative ordered-action bridge', 'complete coherent three-body rates',
                    'semileptonic matching and nuclear conversion', 'materiality and theory uncertainties'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=HERE/'sources.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Refusing to overwrite an evidence receipt')
    result = run(args.manifest)
    with args.output.open('x') as handle:
        json.dump(result, handle, indent=2, allow_nan=False)
        handle.write('\n')
    print(result['status']+'; four original cards; rate controls PASS; physical_lfv=UNKNOWN')
