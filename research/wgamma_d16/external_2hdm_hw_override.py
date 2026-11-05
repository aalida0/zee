"""Source-preserving HW normalization audit; research 2HDM coefficients only.

python -m research.wgamma_d16.external_2hdm_hw_override --output PATH
No physical Zee W coefficients are provided. See HW_NORMALIZATION_AUDIT.md.
"""
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
import scipy
from scipy.integrate import quad
from scipy.optimize import brentq

from .external_2hdm import (PIN, GROUPS, capture, example_input, load_reference,
                            mapped_groups, pack, sha, strict_input)

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT/'research/wgamma_d16/local/general-2hdm-pheno'
ML = np.array([.00051099895, .1056583755, 1.77693])
CHANNELS = ((1, 0), (2, 0), (2, 1))
STATUS = '2HDM_REFERENCE_HW_OPERATOR_EDM_NORMALIZATION_VALIDATED'


def phi_integral(x, y):
    """Finite three-mass master, independent of author dilog/Clausen code.

    Integrating one Feynman parameter gives log(A/B)/(A-B),
    A=x*u+y*(1-u), B=u*(1-u). The apparent A=B pole is removable.
    All squared masses are divided by the same reference squared mass.
    """
    if min(x, y) <= 0 or not np.isfinite([x, y]).all():
        raise ValueError('Positive finite mass ratios required')
    def integrand(u):
        a, b = x*u+y*(1-u), u*(1-u)
        t = (a-b)/b
        return (1-t/2+t*t/3)/b if abs(t) < 1e-6 else np.log(a/b)/(a-b)
    value, error = quad(integrand, 0, 1, epsabs=2e-11, epsrel=2e-12, limit=250)
    if error > 2e-9*max(1., abs(value)):
        raise ArithmeticError('Uncontrolled finite-master quadrature')
    return value


def f11_integral(x, y):
    """Published reduction with independent integral masters, not a new
    derivation of the complete HW graph numerator or its gauge cancellation.
    """
    lx, ly = np.log(x), np.log(y)
    dilog = -quad(lambda t: np.log1p(-(1-x)*t)/t, 0, 1,
                  epsabs=2e-12, epsrel=2e-12)[0]
    return ((y*x-x*x+2*x-1)/(y*y*(y-x))*lx*ly
            +(2*x-y-2)/(y*(y-x))*ly
            +(2*x-1)/(x*x*(x-y))*lx*lx
            +(y*x+2*y-2*x*x)/(x*y*(y-x))*lx
            +2*(x-1)/(x*y)
            +(2*y*x*x-y*y*x-x*y-y-x**3+3*x*x-3*x+1)
            /(y*y*x*(y-x))*phi_integral(y/x, 1/x)
            +2*(y-2*x*y+x**3-2*x*x+x)/(x*x*y*y)*dilog
            +(2*x*x-4*x+1)/(x*x*(x-y))*phi_integral(x, x))


def hw_from_native(ref, model, p, D, ml, i, j, gs, integral=False):
    """Derive c from native G [mass] and neutral PL/PR Yukawas [1]."""
    from module3.core import vertices
    value = np.zeros(2, complex)
    kernel = f11_integral if integral else ref.f11
    for name, (coupling, mass) in vertices(D, p, ml).items():
        g = complex(gs[name][1, 1])
        if abs(g.imag) > 1e-10:
            raise ValueError('Diagonal Hermitian trilinear must be real')
        external = np.array([coupling[j, i], coupling[i, j].conjugate()])
        value += g.real*external/mass**2*kernel((p['mH1']/mass)**2,
                                               (model.MW/mass)**2)
    return model.alphaQED*p['v']**2/(32*np.pi*model.sw**2*ml[i])*value


def candidates(author_groups, replacement_hw):
    """Replace only a captured local; never modify/monkeypatch author source."""
    if set(author_groups) != set(GROUPS):
        raise ValueError('All 13 captured author groups required')
    author = sum(author_groups.values())
    corrected = {g: np.array(v, copy=True) for g, v in author_groups.items()}
    corrected['HW'] = np.asarray(replacement_hw, dtype=complex).copy()
    return dict(AUTHOR_UNMODIFIED=author, PAPER_CORRECTED_HW=sum(corrected.values()),
                difference=replacement_hw-author_groups['HW'], corrected_groups=corrected)


def capture_edm(model):
    result = {}
    old = sys.getprofile()
    def observe(frame, event, arg):
        if event == 'return' and frame.f_code.co_name == 'electron_EDM':
            for g in ('HA', 'HZ', 'HW'):
                result[g] = frame.f_locals['de_2loop_'+g]
    try:
        sys.setprofile(observe)
        model.electron_EDM()
    finally:
        sys.setprofile(old)
    if set(result) != {'HA', 'HZ', 'HW'}:
        raise RuntimeError('EDM source locals unavailable')
    return result


def solve_potential(ref, template, p, D, target):
    """Solve two linear potential conditions, then reconstruct full Hessian.
    This changes m12sq and charged mass squared, never fits G independently.
    """
    def z(point):
        x, _, _ = strict_input(ref, template, point, D, ML)
        return np.array([x['Z3'], x['absZ7']*np.cos(x['argZ7'])])
    z0 = z(p)
    soft = z(dict(p, m12sq=p['m12sq']+10000))-z0
    mass = z(dict(p, mH1=np.sqrt(p['mH1']**2+10000)))-z0
    step = np.linalg.solve(np.array([soft, mass]).T, np.asarray(target)-z0)*10000
    m2 = p['mH1']**2+step[1]
    if m2 <= 0:
        raise ValueError('Requested potential has negative charged mass squared')
    result = dict(p, m12sq=float(p['m12sq']+step[0]), mH1=float(np.sqrt(m2)))
    np.testing.assert_allclose(z(result), target, rtol=0, atol=2e-12)
    return result


def fixtures(ref, template):
    base = json.loads((ROOT/'module1/example.json').read_text())['physical']
    specs = [('G1', .75, .11, 310., 325., .8, .3),
             ('G2', .92, -.16, 360., 350., .6, -.5),
             ('G3', .65, .12, 280., 305., -.1, .2),
             ('Z3_sign', .75, .11, 310., 325., -.2, .3),
             ('Z7_sign', .75, .11, 310., 325., .8, -.3),
             ('both_signs', .75, .11, 310., 325., -.2, -.3),
             ('mass', .75, .11, 390., 325., .8, .3),
             ('angle', .75, .15, 310., 325., .8, .3)]
    out = []
    for n, (name, beta, delta, mh, ma, z3, z7) in enumerate(specs):
        rng = np.random.default_rng(241017400+(n if n < 3 else 0))
        D = .003*(rng.normal(size=(3, 3))+1j*rng.normal(size=(3, 3)))
        p = dict(base, gamma=0., k1=0., k2=0., k12=0., lc=.4, mH2=1e4,
                 beta=beta, alpha=beta-delta, mh2=mh, ma=ma, mH1=320., m12sq=40000.)
        out.append((name, solve_potential(ref, template, p, D, (z3, z7)), D, template))
    # Reuse the previously validated ZERO-potential controls exactly.
    old = json.loads((Path(__file__).with_name('external_2hdm_evidence.json')).read_text())
    for n, r in enumerate(old['records'][6::3]):
        d = np.asarray(r['D']); d = d[:, :, 0]+1j*d[:, :, 1]
        out.append(('control'+str(n+1), r['physical'], d, template))
    for mw in (76., 84.):
        name, p, D, tpl = out[0]
        out.append(('MW'+str(int(mw)), p.copy(), D.copy(), dict(tpl, MW=mw)))
    name, p, D, tpl = out[0]
    phases = np.array([.37, -.81, .22])
    out.append(('phase', p.copy(), D*np.exp(1j*(phases[None, :]-phases[:, None])), tpl))
    return out


def native_potential_check(p, gs):
    """G from finite derivative of the full potential Hessian, independent of
    module4's explicit trilinear formula. Symmetric derivative is exact here.
    """
    from module1.scalar_constraints import reconstruct
    from module1.potential import Potential
    lag, inherited, closure = reconstruct(p)
    from module1.bfb import check_bfb
    from module1.scalar_constraints import unitarity
    r = np.zeros(10); r[[2, 6]] = p['v']*np.array([np.cos(p['beta']), np.sin(p['beta'])])
    charged = np.array([-np.sin(p['beta']), np.cos(p['beta']), 0.])
    step = p['v']/8
    residual = {}
    for name, direction in [('h', [np.cos(p['alpha']), np.sin(p['alpha'])]),
                             ('H', [-np.sin(p['alpha']), np.cos(p['alpha'])])]:
        dr = np.zeros(10); dr[[2, 6]] = np.array(direction)*step
        derivative = (Potential(lag).evaluate(r+dr)[2]-Potential(lag).evaluate(r-dr)[2])/(2*step)
        g = charged@derivative[np.ix_([0, 4, 8], [0, 4, 8])]@charged
        residual[name] = float(abs(g-gs[name][1, 1]))
        np.testing.assert_allclose(g, gs[name][1, 1], rtol=1e-11, atol=3e-10)
    np.testing.assert_allclose(gs['A'][1, 1], 0., atol=1e-12)
    bfb, unit = check_bfb(lag), unitarity(lag, inherited)
    return dict(closure=closure, G_hessian_abs_residual_GeV=residual,
                quartics={k: v for k, v in lag.items() if k.startswith(('Lambda', 'K'))},
                bfb=bfb, unitarity_assessment=unit['assessment'],
                unitarity_max_eigenvalue=unit['max_abs_eigenvalue'],
                other_constraints='NOT_EVALUATED; formal amplitude fixtures, not accepted points')


def scaled_input(x, factor, ref):
    x = dict(x)
    target_mt = ref.mtmt(x['MTpole'])*factor
    for key in ('MW', 'MZ', 'vev', 'Mh1', 'Mh2', 'Mh3', 'MHp', 'melectron',
                'mmuon', 'mtau', 'MTpole', 'mbmb', 'mcmc', 'ms_at_2GeV',
                'md_at_2GeV', 'mu_at_2GeV'):
        x[key] *= factor
    # Upstream's empirical pole->MSbar fit has fixed GeV constants; invert it
    # to scale the ACTUAL matched top mass rather than rescaling a fit argument.
    x['MTpole'] = brentq(lambda mass: ref.mtmt(mass)-target_mt, 1., 1e5,
                         xtol=1e-11)
    return x


def run(reference=REFERENCE):
    ref = load_reference(reference); template = example_input(reference)
    records, edm_checks, master_checks, homogeneity = [], [], [], []
    for name, p, D, tpl in fixtures(ref, template):
        x, gs, _ = strict_input(ref, tpl, p, D, ML)
        model = ref.thdm(x)
        scalar = native_potential_check(p, gs)
        channels = []
        for i, j in CHANNELS:
            total, groups = capture(model, i+1, j+1)
            hw = hw_from_native(ref, model, p, D, ML, i, j, gs)
            result = candidates(groups, hw)
            mapped = mapped_groups(ref, model, p, D, ML, i, j, gs)
            residuals = {}
            for g in GROUPS:
                actual = result['corrected_groups'][g]
                residuals[g] = float(max(abs(mapped[g]-actual))/max(1e-25, max(abs(actual))))
                np.testing.assert_allclose(mapped[g], actual, rtol=3e-11, atol=3e-18, err_msg=name+g)
            corrected = result['PAPER_CORRECTED_HW']
            np.testing.assert_allclose(sum(mapped.values()), corrected, rtol=3e-11, atol=3e-18)
            np.testing.assert_allclose(hw/model.MW**2, groups['HW'], rtol=3e-11, atol=2e-21)
            # Leave-one-out detects a missing group even in coherent cancellation.
            loo = {g: float(max(abs(corrected-(sum(mapped.values())-mapped[g])))) for g in GROUPS}
            scale = -1/(8*np.pi**2*p['v']**2)
            channels.append(dict(channel=[i+1, j+1], author_groups=groups,
                AUTHOR_UNMODIFIED=total, PAPER_CORRECTED_HW=corrected, difference=result['difference'],
                corrected_HW=hw, corrected_two_loop=corrected-groups['1loop'],
                mapped_two_loop=sum(mapped[g] for g in GROUPS if g != '1loop'),
                corrected_C_LR_GeV_minus2=scale*corrected, group_relative_residual=residuals,
                leave_one_out_abs_residual=loo, HW_zero_falsifier_abs=float(max(abs(hw))),
                source_original_homogeneity='FAIL' if max(abs(hw)) > 1e-12 else 'NULL_CONTROL'))
        records.append(dict(name=name, physical=p, D=D, author_input=x, scalar=scalar,
                            G_native_GeV={k: v[1, 1] for k, v in gs.items()}, channels=channels))
        # Independent diagonal operator check: capture actual EDM locals, do not
        # transcribe the EDM expression as an oracle. Single chiral pair, no
        # double counting the h.c. upon taking equal flavor indices.
        # Upstream refuses i=j. Realize the diagonal flavor spurion with its
        # allowed (2,1) channel and equal external masses; only potential locals
        # are used. This auxiliary operator check is not a model benchmark.
        dx = dict(x, mmuon=ML[0])
        dd = D.copy(); dd[0, 1] = dd[1, 0] = D[0, 0]
        for a, b in ((1, 2), (2, 1)):
            dx[f'absrhol{a}{b}'] = float(abs(D[0, 0]/np.sqrt(2)))
            dx[f'argrhol{a}{b}'] = float(np.angle(D[0, 0]))
        dmodel = ref.thdm(dx)
        _, diag_groups = capture(dmodel, 2, 1)
        diag_ml = ML.copy(); diag_ml[1] = ML[0]
        diag_hw = hw_from_native(ref, dmodel, p, dd, diag_ml, 1, 0, gs)
        edm = capture_edm(model)
        factor = model.el*ML[0]/(8*np.pi**2*p['v']**2)
        diag = dict(diag_groups, HW=diag_hw)
        for g in ('HA', 'HZ', 'HW'):
            predicted = factor*diag[g][1].imag
            np.testing.assert_allclose(diag[g][0], diag[g][1].conjugate(), rtol=1e-12, atol=1e-16)
            np.testing.assert_allclose(predicted, edm[g], rtol=4e-11, atol=1e-25)
            edm_checks.append(dict(name=name, group=g, captured_EDM_GeV_minus1=edm[g],
                operator_prediction_GeV_minus1=predicted,
                original_source_prediction_GeV_minus1=factor*diag_groups[g][1].imag))
        # Independent integral master check for each actual neutral mass ratio.
        for mass in (p['mh1'], p['mh2'], p['ma']):
            xx, yy = (p['mH1']/mass)**2, (model.MW/mass)**2
            analytic, integral = ref.f11(xx, yy), f11_integral(xx, yy)
            np.testing.assert_allclose(analytic, integral, rtol=5e-9, atol=2e-8)
            master_checks.append(dict(name=name, x=xx, y=yy, author=analytic, integral=integral,
                                      abs_difference=abs(analytic-integral)))
        # Scale the native potential too (quartics fixed; m12sq has dimension 2).
        for lam in (.5, 2.):
            sp = dict(p, **{k: p[k]*lam for k in ('mh1','mh2','ma','mH1','mH2','v')},
                      m12sq=p['m12sq']*lam**2)
            sx, sgs, _ = strict_input(ref, scaled_input(tpl, lam, ref), sp, D, ML*lam)
            smodel = ref.thdm(sx)
            for i, j in CHANNELS:
                _, sg = capture(smodel, i+1, j+1)
                shw = hw_from_native(ref, smodel, sp, D, ML*lam, i, j, sgs)
                base = channels[CHANNELS.index((i,j))]
                np.testing.assert_allclose(shw, base['corrected_HW'], rtol=3e-10, atol=1e-16)
                residuals = {}
                # Light quark input scale is fixed at 2 GeV in upstream running;
                # these omitted species do not enter any of the 13 groups.
                for g in GROUPS:
                    expected = base['author_groups'][g]/(lam**2 if g == 'HW' else 1)
                    np.testing.assert_allclose(sg[g], expected, rtol=3e-10, atol=2e-15)
                    residuals[g] = float(max(abs(sg[g]-expected)))
                homogeneity.append(dict(name=name, channel=[i+1,j+1], factor=lam,
                    original_HW=sg['HW'], corrected_HW=shw, abs_residuals=residuals))
    tracked = ['module1/scalar_constraints.py','module1/potential.py','module3/core.py',
               'module4/charged_scalar.py','module4/couplings.py',
               'research/wgamma_d16/matching.py','research/wgamma_d16/gauge_ledger.json',
               'research/spheno_flavorkit/d15_component_evidence.json']
    # Re-read and validate author files after all calculations.
    load_reference(reference)
    return pack(dict(status=STATUS, source_commit=subprocess.check_output(
        ['git','rev-parse','HEAD'], text=True).strip(), author_pin=PIN,
        author_files={n:sha(Path(reference)/n) for n in ('thdm.py','rge.py','adm.py','example.py','LICENSE.txt')},
        code_sha256={n:sha(Path(__file__).with_name(n)) for n in
                     ('external_2hdm_hw_override.py','zee_singlet_hz.py','test_hw_normalization.py','external_2hdm.py')},
        input_sha256={n:sha(ROOT/n) for n in ('module1/example.json',
            'research/wgamma_d16/external_2hdm_evidence.json',
            'research/wgamma_d16/external_2hdm_native_evidence.json')},
        frozen_hashes={n:sha(ROOT/n) for n in tracked},
        environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        evidence_scope='Complex common-limit coefficient closure using shared reduction functions; independent EDM operator identity and master quadrature; not an independent full two-loop diagram derivation',
        physical_Zee_W=dict(C_L=None,C_R=None,coherent_inclusion=False),
        records=records, edm_checks=edm_checks, master_checks=master_checks,
        homogeneity=homogeneity, original_source_failure='EXPECTED_FAIL_HW_EXTRA_INVERSE_MW_SQUARED'))


def singlet_demo(evidence):
    from .zee_singlet_hz import singlet_hz, hz_radial_kernel
    from module4.charged_scalar import scalar_qed_tensor
    from module1.scalar_constraints import reconstruct
    from module1.potential import Potential
    row = evidence['records'][0]
    p = dict(row['physical'], mH2=540., k1=.3, k2=.18, k12=-.04)
    d = np.asarray(row['D']); d = d[:, :, 0]+1j*d[:, :, 1]
    f = np.zeros((3, 3), complex)
    results, decoupling = [], []
    for i,j in CHANNELS:
        result = singlet_hz(d,f,p,ML,80.379,91.1876,i,j)
        zero = singlet_hz(d,f,dict(p,k1=0.,k2=0.,k12=0.),ML,80.379,91.1876,i,j)
        np.testing.assert_array_equal(zero['class_C_LR_GeV_minus2'], np.zeros(2))
        heavy = singlet_hz(d,f,dict(p,mH2=5400.),ML,80.379,91.1876,i,j)
        results.append(dict(channel=[i+1,j+1], **result))
        decoupling.append(float(max(abs(heavy['class_C_LR_GeV_minus2']))/
                                max(abs(result['class_C_LR_GeV_minus2']))))
    # The actual native full potential, third derivative with charged-singlet
    # legs, independently tests both portal trilinears in the restricted class.
    lag, _, _ = reconstruct(p)
    r = np.zeros(10); r[[2,6]] = p['v']*np.array([np.cos(p['beta']),np.sin(p['beta'])])
    gres = {}
    for name, direction in [('h',[np.cos(p['alpha']),np.sin(p['alpha'])]),
                             ('H',[-np.sin(p['alpha']),np.cos(p['alpha'])])]:
        dr = np.zeros(10); step=p['v']/8; dr[[2,6]] = step*np.array(direction)
        native = (Potential(lag).evaluate(r+dr)[2][8,8]-Potential(lag).evaluate(r-dr)[2][8,8])/(2*step)
        gres[name] = abs(native-results[0]['rows'][name]['G_GeV'])
        assert gres[name] < 1e-10
    a=np.array([.2,.3,-.4,.1]); b=np.array([1.,.3,.2,-.2])
    triangle,contact=scalar_qed_tensor(a,b)
    tz=results[0]['positive_singlet_Z_charge_over_e']; total=tz*(triangle+contact)
    ward=dict(photon=float(max(abs(a@total))), Z=float(max(abs(total@b))),
              without_seagull=float(max(abs(a@(tz*triangle)))))
    assert max(ward['photon'],ward['Z']) < 2e-13 and ward['without_seagull'] > .01
    return pack(dict(physical=p,D=d,F=f,results=results,zero_portal='PASS_EXACT_ZERO',
        decoupling_at_10x_mass_ratios=decoupling, G_hessian_abs_residual_GeV=gres,
        ward=ward, equal_outer_mass_f10=hz_radial_kernel(1.7,1.),
        complete_Zee_matching=False, coherent_inclusion=False))


def compact(evidence, details_path):
    """Retain complex group comparisons; put repetitive scale runs in scratch."""
    import copy
    result = copy.deepcopy(evidence)
    result['details_sha256'] = sha(details_path)
    result['details_path'] = str(details_path.relative_to(ROOT))
    hom = result.pop('homogeneity')
    result['homogeneity_summary'] = dict(evaluations=len(hom), factors=[.5,2.],
        per_group_max_abs_residual={g:max(h['abs_residuals'][g] for h in hom) for g in GROUPS},
        original_HW_scaling='lambda^-2 (EXPECTED FAIL)', corrected_HW_scaling='lambda^0 (PASS)')
    for row in result['records']:
        raw = json.dumps(row['author_input'],sort_keys=True,allow_nan=False).encode()
        import hashlib
        row['author_input_sha256'] = hashlib.sha256(raw).hexdigest()
        row['matched_EW_and_potential'] = {k:row['author_input'][k] for k in
            ('MW','MZ','vev','sw2','alphaQED','Z3','absZ7','argZ7')}
        del row['author_input']
    sources = json.loads(Path(__file__).with_name('external_2hdm_sources.json').read_text())
    local = Path(__file__).parent/'local/external_2hdm_reference'
    for key, name in [('paper','paper-v4.pdf'),('erratum','erratum-2026.pdf')]:
        digest = sha(local/name)
        if digest != sources[key]['pdf_sha256']:
            raise ValueError('Changed reference PDF: '+name)
        result[key] = dict(url=sources[key].get('url'), pdf_sha256=digest)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', type=Path, default=REFERENCE)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--details', type=Path, default=Path(__file__).parent/'local/hw_generic_details.json')
    args = ap.parse_args()
    evidence = run(args.reference)
    evidence['singlet_HZ'] = singlet_demo(evidence)
    args.details.write_text(json.dumps(evidence, indent=2, sort_keys=True, allow_nan=False)+'\n')
    args.output.write_text(json.dumps(compact(evidence,args.details.resolve()), indent=2, sort_keys=True, allow_nan=False)+'\n')
    print(evidence['status'], len(evidence['records'])*3, 'complex channel comparisons')


if __name__ == '__main__':
    main()
