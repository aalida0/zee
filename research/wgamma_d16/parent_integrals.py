"""First actual open-fermion WWW parent and its algebraic pinch at xi=1.

This is an amputated one-loop subgraph at FIXED outer scalar momentum r,
NOT a projected physical two-loop Wilson coefficient. Both orientations,
mixed/charged parents, outer integration, LSZ and counterterms remain due.
The native vertex product strips +e*g2^2*mW^2*kappa/v and i/(16*pi^2)
for the WWW-only routine. The charged lepton fixes the charge orientation.
"""
import numpy as np

from .algebra import ETA, GAMMA, METRIC, PL, slash, dot, propagator_numerator


def numerator(mu, loop, p, q, dimension=4):
    """V_{mu A B} gamma^B /n gamma^A PL, n=p-l, native photonWW order.

    All indices returned upper. Photon leaves q; the W momenta are l,
    l-q, l-r. The scalar sits BEFORE the two W currents on the lepton line.
    """
    n = slash(p-loop)
    return (-slash(loop+q)@n@GAMMA[mu]+(2-dimension)*(2*loop-q)[mu]*n+
            GAMMA[mu]@n@slash(2*q-loop))@PL


def numerator_remainder(mu, loop, p, q, dimension=4):
    """Calculated by substituting l=p-n, not by enforcing a Ward cancellation."""
    n = slash(p-loop)
    return (-slash(p+q)@n@GAMMA[mu]+(2-dimension)*(2*loop-q)[mu]*n+
            GAMMA[mu]@n@slash(2*q-p))@PL


def pointwise_pinch_residual(loop, p, q):
    n2 = dot(p-loop, p-loop)
    return max(float(np.max(abs(numerator(mu, loop, p, q)-
                     numerator_remainder(mu, loop, p, q)-2*n2*GAMMA[mu]@PL))) for mu in range(4))


def _simplex(order, n):
    x, w = np.polynomial.legendre.leggauss(order)
    x, w = (x+1)/2, w/2
    grids = np.meshgrid(*([x]*(n-1)), indexing='ij')
    wg = np.meshgrid(*([w]*(n-1)), indexing='ij')
    rest, weight, params = np.ones_like(grids[0]), np.ones_like(grids[0]), []
    for j in range(n-1):
        params.append(rest*grids[j])
        weight *= wg[j]*rest
        rest = rest*(1-grids[j])
    params.append(rest)
    return np.array([z.ravel() for z in params]), weight.ravel()


def _geometry(params, shifts, masses2):
    # D_i=(l-shift_i)^2-m_i^2. l=t+R.
    mean = params.T@np.asarray(shifts)
    delta = np.asarray(masses2)@params
    for i in range(len(shifts)):
        for j in range(i):
            delta -= params[i]*params[j]*dot(shifts[i]-shifts[j], shifts[i]-shifts[j])
    if np.min(delta) <= 0:
        raise ValueError('Parent requires a positive Delta; choose spacelike outer momenta')
    return mean, delta


def calculate_parent(p, q, r, mw2, *, order=18):
    """Regulated four-denominator inner subgraph plus independently pinched triangle.

    Integral measure is MSbar PV; n=4 moments are I0=1/Delta^2,
    I2=-1/(2 Delta), including Gamma(4). There is no inner UV pole.
    d-dependent O(eps) pieces would still be needed if outer UV poles survive.
    """
    p, q, r = map(lambda a: np.asarray(a, float), (p, q, r))
    zero = np.zeros(4)
    params, weights = _simplex(order, 4)
    # Put the massless neutrino FIRST: Delta=(1-x)*regular and the
    # simplex Jacobian contains (1-x)^2. This resolves its endpoint exactly.
    mean, delta = _geometry(params, [p, zero, q, r], [0., mw2, mw2, mw2])
    full = np.zeros((4, 4, 4), complex)
    rem = np.zeros_like(full)
    # n^2 = (p-R)^2+t^2; cancelling the propagator gives its triangle.
    cancelled_box = 2*np.sum(weights*(np.array([dot(p-x, p-x) for x in mean])/delta**2-2/delta))
    def sl_batch(vectors):
        return np.einsum('na,aij->nij', vectors*ETA, np.asarray(GAMMA))
    n = sl_batch(p-mean)
    sn = sl_batch(mean+q)
    sq = sl_batch(2*q-mean)
    for mu in range(4):
        num = (-sn@n@GAMMA[mu]-2*(2*mean-q)[:, mu, None, None]*n+GAMMA[mu]@n@sq)@PL
        remainder = (-slash(p+q)@n@GAMMA[mu]-2*(2*mean-q)[:, mu, None, None]*n+
                     GAMMA[mu]@n@slash(2*q-p))@PL
        full[mu] = np.einsum('n,nij->ij', weights, num/delta[:, None, None]**2-
                             6*(GAMMA[mu]@PL)[None, :, :]/delta[:, None, None])
        rem[mu] = np.einsum('n,nij->ij', weights, remainder/delta[:, None, None]**2-
                            2*(GAMMA[mu]@PL)[None, :, :]/delta[:, None, None])
    params3, weights3 = _simplex(order, 3)
    _, delta3 = _geometry(params3, [zero, q, r], [mw2]*3)
    pinch_scalar = -2*np.sum(weights3/delta3)
    pinch = np.array([pinch_scalar*g@PL for g in GAMMA])
    return dict(full=full, remainder=rem, pinch=pinch, uv_pole=np.zeros_like(full),
                pinch_scalar=float(pinch_scalar), cancelled_box_scalar=float(cancelled_box),
                integral_split_residual=float(np.max(abs(full-rem-pinch))),
                order=order)


def attach_scalar_leg(block, p, r, mass, left, right):
    """The charged propagator and independent complex LFV vertex remain explicit."""
    from .algebra import PR
    return block@propagator_numerator(p-r, mass)@(left*PL+right*PR)


def native_parent_numerator(loops, p, q, r, mw2, ms2, lepton_mass, species, xi=1.):
    """All eight W/G box parents, scalar vertex before the two charged currents.

    a: s->photon, b: photon->daughter, c: s->first lepton vertex.
    s fields (a+,c-), photon fields (a-,b+), currents (b-,c+).
    Strip e*g2^2*kappa/(2v), including Goldstone-current mass factors.
    Tensor output shape is (sample, mu, Dirac row, Dirac col).
    """
    from .algebra import PR
    loops = np.asarray(loops)
    mw = np.sqrt(mw2)
    a, b, c = species
    da, db, dc = [4 if sp == 'W' else 1 for sp in species]
    npts = len(loops)
    scalar = np.zeros((npts, da, dc), complex)
    if a == c == 'W':
        scalar[:] = 2j*mw2*METRIC
    elif a == c == 'G':
        scalar[:] = -1j*ms2
    elif a == 'G':
        scalar[:, 0, :] = 1j*mw*(loops+r)
    else:
        scalar[:, :, 0] = -1j*mw*(2*r-loops)
    photon = np.zeros((npts, 4, da, db), complex)
    if a == b == 'W':
        for mu in range(4):
            for ia in range(4):
                for ib in range(4):
                    # photonWW native order lt2=a-,lt3=b+.
                    photon[:, mu, ia, ib] = 1j*(METRIC[mu, ib]*(loops-2*q)[:, ia]-
                        METRIC[ia, ib]*(2*loops-q)[:, mu]+METRIC[mu, ia]*(loops+q)[:, ib])
    elif a == b == 'G':
        photon[:, :, 0, 0] = 1j*(2*loops-q)
    else:
        if a == 'W':
            photon[:, :, :, 0] = 1j*mw*METRIC
        else:
            photon[:, :, 0, :] = 1j*mw*METRIC
    daughter = np.array([ga@PL for ga in GAMMA]) if b == 'W' else np.array([lepton_mass/mw*PL])
    first = np.array([ga@PL for ga in GAMMA]) if c == 'W' else np.array([lepton_mass/mw*PR])
    ns = np.einsum('na,aij->nij', (p-loops)*ETA, np.asarray(GAMMA))
    # Three propagators, two (-i) weak vertices, and the i neutrino propagator.
    phase = (-1)**(species.count('W')+1)
    if xi != 1.:
        # General-xi rational numerator. Only used for the exact integrand;
        # the polynomial Hessian integrator below is restricted to xi=1.
        props = []
        for sp, momenta in zip(species, (loops, loops-q, loops-r)):
            if sp == 'G':
                props.append(np.ones((npts, 1, 1)))
            else:
                p2 = np.einsum('na,a,na->n', momenta, ETA, momenta)
                cov = momenta*ETA
                props.append(METRIC[None, :, :]-(1-xi)*cov[:, :, None]*cov[:, None, :]/
                             (p2-xi*mw2)[:, None, None])
        return phase*np.einsum('nac,nmAb,Bik,nkl,Clj,naA,nbB,ncC->nmij', scalar, photon,
                                daughter, ns, first, *props, optimize=True)
    return phase*np.einsum('nac,nmab,bik,nkl,clj,a,b,c->nmij', scalar, photon,
                            daughter, ns, first, ETA if da == 4 else [1.],
                            ETA if db == 4 else [1.], ETA if dc == 4 else [1.], optimize=True)


def exact_parent_integrand(loop, outer, p, q, mw2, ms2, lepton_mass,
                           left, right, species=('W', 'W', 'W'), xi=1.):
    """Executable missing TWO-loop integrand, excluding common vertex/measure factors.

    It contains all four inner denominators, scalar propagator, unpinched
    charged lepton propagator, and complex X. This is a 4D integrand witness,
    NOT an unregulated quadrature prescription for a divergent loop sum.
    DR gamma algebra and eps terms must precede general-xi integration.
    """
    if not np.isfinite(xi) or xi <= 0:
        raise ValueError('Positive finite xi required')
    loop, outer, p, q = map(lambda a: np.asarray(a, float), (loop, outer, p, q))
    denominators = [dot(loop-v, loop-v)-mw2*(1 if sp == 'W' else xi)
                    for v, sp in zip((np.zeros(4), q, outer), species)]
    denominators += [dot(p-loop, p-loop), dot(outer, outer)-ms2]
    if any(abs(z) < 1e-12 for z in denominators):
        raise ValueError('Choose a witness away from propagator poles')
    block = native_parent_numerator(loop[None, :], p, q, outer, mw2, ms2,
                                    lepton_mass, species, xi=xi)[0]
    return attach_scalar_leg(block, p, outer, lepton_mass, left, right)/np.prod(denominators)


def calculate_native_parents(p, q, r, mw2, ms2, lepton_mass, *, order=14):
    """Actual finite W/G parent subloops, still before OUTER integration/LSZ.

    Polynomial degree <=3. The centered second difference is an EXACT
    Hessian for this degree, rather than a numerical loop-momentum cutoff.
    d=4 is allowed for these individually UV-finite subloops only.
    """
    from itertools import product
    p, q, r = map(lambda a: np.asarray(a, float), (p, q, r))
    params, weights = _simplex(order, 4)
    means, delta = _geometry(params, [p, np.zeros(4), q, r], [0., mw2, mw2, mw2])
    output = {}
    for species in product(('W', 'G'), repeat=3):
        def num(loops):
            return native_parent_numerator(loops, p, q, r, mw2, ms2, lepton_mass, species)
        center = num(means)
        laplacian = np.zeros_like(center)
        # mW-sized steps avoid cancellation of the large cubic coefficients.
        for a in range(4):
            step = np.eye(4)[a]*np.sqrt(mw2)
            laplacian += ETA[a]*(num(means+step)+num(means-step)-2*center)/mw2
        output[''.join(species)] = np.einsum('n,nmij->mij', weights,
            center/delta[:, None, None, None]**2-laplacian/(4*delta[:, None, None, None]))
    return output


def calculate_parent_rxi(p, q, r, mw2, ms2, lepton_mass, species=('W', 'W', 'W'),
                         *, xi=1., power=12, replicates=4, seed=16083):
    """Finite inner parent at general xi by a safe Euclidean contour and RQMC.

    The COMPLETE Rxi propagator falls as l^-2; these box subloops have UV
    degree <=-1 (WWW has -2), so DR has no pole and its finite eps^0 term
    equals this convergent 4D integral. No unitary-piece UV term is dropped.
    Shift n=p-l before Wick rotation; all massive-line time shifts must be
    below their masses. Antithetic n and -n cancel the odd UV tail.
    The reported uncertainty is the standard error across scrambled Sobol
    replicates, not a bound and not a physical two-loop error estimate.
    """
    from scipy.special import ndtri
    from scipy.stats import qmc
    p, q, r = map(lambda a: np.asarray(a, float), (p, q, r))
    if xi <= 0 or replicates < 2:
        raise ValueError('Require xi>0 and at least two randomized replicates')
    masses = np.array([mw2*(1 if sp == 'W' else xi) for sp in species])
    shifts = [np.zeros(4), q, r]
    if any(abs((p-v)[0]) >= np.sqrt(m) for v, m in zip(shifts, masses)):
        raise ValueError('Unproved Euclidean contour for these time shifts')
    results = []
    scale = np.sqrt(mw2)
    for rep in range(replicates):
        u = qmc.Sobol(5, scramble=True, seed=seed+rep).random_base2(power)
        direction = ndtri(u[:, :4])
        direction /= np.linalg.norm(direction, axis=1)[:, None]
        z = u[:, 4]
        radius = scale*np.sqrt(z/(1-z))
        euclidean = radius[:, None]*direction
        wick = euclidean.astype(complex)
        wick[:, 0] *= 1j
        # 2*pi^2 angular measure / pi^2 PV measure times R^3 dR.
        weight = scale**4*z/(1-z)**3
        estimate = np.zeros((4, 4, 4), complex)
        for sign in (-1, 1):
            loops = p-sign*wick
            numerator = native_parent_numerator(loops, p, q, r, mw2, ms2,
                                                 lepton_mass, species, xi=xi)
            denom = -radius**2+0j
            for v, mass in zip(shifts, masses):
                momentum = loops-v
                denom = denom*(np.einsum('na,a,na->n', momentum, ETA, momentum)-mass)
            estimate += .5*np.mean(numerator*(weight/denom)[:, None, None, None], axis=0)
        results.append(estimate)
    results = np.asarray(results)
    return dict(finite=np.mean(results, axis=0),
                standard_error=np.sqrt(np.sum(abs(results-results.mean(axis=0))**2, axis=0)/
                                       (replicates*(replicates-1))),
                uv_pole=np.zeros((4, 4, 4), complex), xi=xi, power=power,
                replicates=replicates, seed=seed)


def example_parent(order=18):
    from .algebra import decay_momenta
    p, pj, q = decay_momenta(3., .7)
    r = np.array([.8, 31., -17., 29.])
    result = calculate_parent(p, q, r, 80.379**2, order=order)
    lower = calculate_parent(p, q, r, 80.379**2, order=max(6, order//2))
    return result, float(np.max(abs(result['full']-lower['full'])))


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-completion', action='store_true')
    args = parser.parse_args()
    result, change = example_parent(24)
    print(json.dumps(dict(status='BLOCKED_GAUGE_MATCHING',
        computed='WWW parent fixed-r subloop and independently derived neutrino pinch',
        uv_pole=float(np.max(abs(result['uv_pole']))),
        finite_block_max=float(np.max(abs(result['full']))),
        pinch_triangle=result['pinch_scalar'],
        independent_box_triangle_residual=result['integral_split_residual'],
        quadrature_change=change, missing_integrand='exact_parent_integrand',
        exact_next_step='d-dimensional outer r projection, opposite scalar placement and ST/LSZ sum',
        physical=dict(C_L=None, C_R=None, coherent_inclusion=False)), indent=2))
    raise SystemExit(2 if args.require_completion else 0)
