"""Scalar vertices and one-loop matching, GeV units; see CONVENTIONS.md.

No historical scan backend is imported. Loop kernels are Lavoura (2003),
eqs. 40--42, with external invariants omitted in denominators only.
"""
import math
import mpmath as mp
import numpy as np

BASIS = 'SARAH_ZeeTypeII_Florentino_v1'
OPERATOR = 'L=e*m_i/2*bar(l_j)*sigma_munu*(CL*PL+CR*PR)*l_i*F_munu+h.c.;GeV^-2;v1'
APPROXIMATION = 'm_nu=0; external invariant masses omitted in loop denominators; external chirality masses retained'
MISSING = [
    'Two-loop fermion-gamma Barr-Zee (Type-II quarks and charged leptons)',
    'Two-loop W-gamma Barr-Zee including gauge completion',
    'Two-loop charged-scalar-gamma Barr-Zee',
    'Two-loop Z-photon Barr-Zee',
    'Two-loop W-Z Barr-Zee and remaining two-loop matching',
    'Three-body off-shell photon non-dipole and dipole, Z penguins, boxes, and all interference with tree exchange',
    'Muon-electron conversion: tree semileptonic scalar, photon/Z penguins, boxes, nuclear matrix elements',
    'QED running, real/virtual radiation and higher-order corrections',
    'Universality charged-doublet D operators, mixed F-D operators and quadratic dimension-six rates',
    'Finite-neutrino-mass scalar chirality mixing and W/Goldstone GIM terms',
    'External-invariant corrections to radiative scalar matching',
]


def vertices(D, p, ml):
    """L=-S bar(e)_a [C_ab PL+C_ba* PR] e_b.

    ZH rows (cos alpha,sin alpha),(-sin alpha,cos alpha).
    ZA physical row (-sin beta,cos beta). D has right-Weyl row index.
    """
    delta = p['beta']-p['alpha']
    sm = np.diag(np.asarray(ml)/p['v'])
    y = D/np.sqrt(2)
    return {'h': (math.cos(delta)*sm-math.sin(delta)*y, p['mh1']),
            'H': (math.sin(delta)*sm+math.cos(delta)*y, p['mh2']),
            'A': (-1j*y, p['ma'])}


def kernels(t):
    """Return A_neutral, B_internal_flip, A_charged, stable at t=1.

    High precision prevents cancellation near unity. Independent positive
    Feynman-parameter quadratures are in the validation tests.
    """
    if not math.isfinite(t) or t < 0:
        raise ValueError('Nonnegative finite mass ratio required')
    if t == 0:
        return 1/6, math.inf, 1/12
    if t == 1:
        return 1/24, 1/3, 1/24
    with mp.workdps(100):
        x = mp.mpf(t)
        a = (x*x-5*x-2)/(12*(x-1)**3)+x*mp.log(x)/(2*(x-1)**4)
        b = (x-3)/(2*(x-1)**2)+mp.log(x)/(x-1)**3
        c = (2*x*x+5*x-1)/(12*(x-1)**3)-x*x*mp.log(x)/(2*(x-1)**4)
        return float(a), float(b), float(c)


def neutral_dipole(C, mass, i, j, ml):
    """Positive neutral sign in the declared L_eff convention.

    Lavoura L_ki=C_ki, R_ki=C_ik*, QF=-1, QB=0;
    C_here=-sigma_Lavoura/(i*m_i). Common sign fixed by scalar g-2.
    """
    mi, mj = ml[i], ml[j]
    left = right = 0j
    for k, mk in enumerate(ml):
        lam = C[k,j].conjugate()*C[k,i]
        rho = C[j,k]*C[i,k].conjugate()
        ups = C[j,k]*C[k,i]
        zet = C[k,j].conjugate()*C[i,k].conjugate()
        a, b, _ = kernels((mk/mass)**2)
        left += (rho+lam*mj/mi)*a+ups*mk/mi*b
        right += (lam+rho*mj/mi)*a+zet*mk/mi*b
    return np.array([left, right])/(16*np.pi**2*mass**2)


def component(clcr, source):
    return {'C_L': complex(clcr[0]), 'C_R': complex(clcr[1]),
            'normalization': OPERATOR, 'loop_order': 1, 'basis': BASIS,
            'provenance': source, 'validation_status': 'PASS',
            'physical_status': 'SCALAR_ONE_LOOP_APPROXIMATION',
            'approximation': APPROXIMATION}


def dipole_ledger(F, D, p, ml, i, j):
    out = {name: component(neutral_dipole(C, mass, i, j, ml),
                           'Lavoura hep-ph/0302221 eqs.26-42; frozen ZH/ZA')
           for name, (C, mass) in vertices(D, p, ml).items()}
    # From H+ bar(N_k)(L_ki PL+R_ki PR)e_i: L=-s*F_ki,
    # R=-d*D_ik*. QB=+1, QF=0 for BOTH contractions.
    # Distinct neutrino chirality sectors do not mix at m_nu=0.
    rho = (D@D.conj().T)[j,i]
    lam = (F.conj().T@F)[j,i]
    ratio = ml[j]/ml[i]
    for state, mass, d, s in [('H1', p['mH1'], math.cos(p['gamma']), math.sin(p['gamma'])),
                              ('H2', p['mH2'], -math.sin(p['gamma']), math.cos(p['gamma']))]:
        fac = -1/(192*np.pi**2*mass**2)
        out[state+'_D'] = component(fac*d*d*rho*np.array([1, ratio]),
                                    'Lavoura eq.41 t=0; R=-d*D*')
        out[state+'_F'] = component(fac*s*s*lam*np.array([ratio, 1]),
                                    'Lavoura eq.41 t=0; L=-s*F; F=2*f_Chen')
    return out


def combine(pieces):
    """Reject any mismatched operator, basis, order or approximation."""
    if not pieces:
        raise ValueError('No amplitudes to combine')
    for row in pieces.values():
        if (row['normalization'] != OPERATOR or row['basis'] != BASIS or
                row['loop_order'] != 1 or row['approximation'] != APPROXIMATION or
                row['validation_status'] != 'PASS'):
            raise ValueError('Incompatible or unvalidated amplitude')
    return np.array([sum(r['C_L'] for r in pieces.values()),
                     sum(r['C_R'] for r in pieces.values())])


def radiative_width(clcr, mi, mj, alpha_em):
    return float(alpha_em*mi**5/4*(1-(mj/mi)**2)**3*np.sum(abs(clcr)**2))


def neutral_width(C, mass, i, j, ml):
    """One charge orientation, with exact two-body fermion masses."""
    a, b = ml[i], ml[j]
    if mass <= a+b:
        return 0.
    lam = (mass**2-(a+b)**2)*(mass**2-(a-b)**2)
    trace = ((abs(C[i,j])**2+abs(C[j,i])**2)*(mass**2-a*a-b*b)
             -4*a*b*(C[i,j]*C[j,i]).real)
    return float(math.sqrt(lam)*trace/(16*np.pi*mass**3))


def universality(F, p, gf):
    """Leading O(F²/M²) rate shifts, with muon-GF subtraction.

    Fierz of physical F gives deltaG/G=|F_ab|²*w/(4 sqrt(2) GF).
    Rate shift=2 deltaG/G. No f^4 or D contribution is included.
    """
    w = math.sin(p['gamma'])**2/p['mH1']**2+math.cos(p['gamma'])**2/p['mH2']**2
    shift = {name: float(abs(F[a,b])**2*w/(2*np.sqrt(2)*gf))
             for name, a, b in [('mu_e',0,1), ('tau_e',0,2), ('tau_mu',1,2)]}
    return {'status': 'PASS', 'physical_status': 'SUBSET_DIAGNOSTIC',
            'rate_shifts_before_GF_subtraction': shift,
            'delta_GF_mu_over_GF': shift['mu_e']/2,
            'g_tau_over_g_mu_squared_minus1': shift['tau_e']-shift['mu_e'],
            'g_tau_over_g_e_squared_minus1': shift['tau_mu']-shift['mu_e'],
            'g_mu_over_g_e_squared_minus1': shift['tau_mu']-shift['tau_e'],
            'experimental_comparison': 'NOT_EVALUATED',
            'provenance': 'Herrero-Garcia 1701.05345 eqs.3.26-3.33; F=2f; general f_e_mu restored'}
