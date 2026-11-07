"""Compare actual fresh SARAH vertices to the mapped fixed-card amplitudes."""
import math
from module4.couplings import quarks
from module7.d4_inputs import native_card, yukawa_masses, SM
from module7.d4_native import expected_coefficients
from research.full_constraints.higgs.decays_bridge import neutral_hhh
from research.full_constraints.higgs.sushi_bridge import benchmark


def validate(native):
    if native['sarah_version']!='4.15.4' or len(native['cases'])!=2:
        raise ValueError('Native source/version/case mismatch')
    residuals=[];normalized={}
    for case in native['cases']:
        name=case['id'];r,w=benchmark(name);p=r['input']['physical']
        masses=yukawa_masses(p['mh2'])
        actual=[[complex(z['real'],z['imag']) for z in row] for row in case['coefficients']]
        expected=[];norms={}
        for state in ('H','A'):
            for f,m in [('top',masses[2]),('bottom',masses[5])]:
                C=quarks(m,f,p)[state];expected.append([-1j*C,-1j*C.conjugate()])
                norms[state+'_'+f]=(C/(m/p['v'])).imag if state=='A' else (C/(m/p['v'])).real
        card=native_card(p,w['yukawas'],p['mh2'],name);c=expected_coefficients(card)
        expected.extend([c[i] for i in (38,42,44,46)])
        expected.append([-1j*neutral_hhh(p)])
        expected.append([SM['EW']['mZ']/p['v']*math.sin(p['beta']-p['alpha'])])
        if len(actual)!=len(expected):raise ValueError('Native query inventory mismatch')
        for x,y in zip(actual,expected):
            if len(x)!=len(y):raise ValueError('Native chirality inventory mismatch')
            for xx,yy in zip(x,y):
                residuals.append(abs(xx-yy))
                if not math.isclose(abs(xx-yy),0.,abs_tol=2e-10):
                    raise ValueError('Native quark/scalar/gauge vertex mismatch')
        normalized[name]=norms
    return dict(status='NATIVE_SIGNED_CHIRAL_VERTICES_VALIDATED',
                max_absolute_residual=max(residuals),complex_coefficients_checked=len(residuals),
                normalized_quark_couplings=normalized,
                CP_convention='L=-S qbar(C PL+C* PR)q; C_A=+i m_q/v kappa_A; native A not rephased')
