"""Full-domain sufficient square-completion certificate, checked over Q.

All binary float Lagrangian parameters are treated as exact rationals. A
Krawczyk contraction encloses the nearby *exact* neutral stationary root.
No floating eigenvalue or optimizer success flag can issue a certificate.
See D10_VACUUM_GLOBAL_AUDIT.md for the identity and all assumptions.
"""
from fractions import Fraction as Q
import math

import mpmath as mp
import numpy as np
from scipy.optimize import minimize_scalar


class Interval:
    """Closed exact rational interval; outward rounding is unnecessary."""
    def __init__(self, lo, hi=None):
        if isinstance(lo, Interval):
            self.lo, self.hi = lo.lo, lo.hi
        else:
            self.lo, self.hi = Q(lo), Q(lo if hi is None else hi)
        if self.lo > self.hi:
            raise ValueError('Reversed interval')

    def __add__(self, other):
        b = Interval(other)
        return Interval(self.lo+b.lo, self.hi+b.hi)

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other):
        return self+-Interval(other)

    def __rsub__(self, other):
        return Interval(other)+-self

    def __mul__(self, other):
        b = Interval(other)
        values = [a*c for a in (self.lo, self.hi) for c in (b.lo, b.hi)]
        return Interval(min(values), max(values))

    __rmul__ = __mul__

    def __truediv__(self, other):
        b = Interval(other)
        if b.lo <= 0 <= b.hi:
            raise ZeroDivisionError('Interval contains zero')
        return self*Interval(1/b.hi, 1/b.lo)

    def __rtruediv__(self, other):
        return Interval(other)/self

    def magnitude(self):
        return max(abs(self.lo), abs(self.hi))

    def serial(self):
        return [str(self.lo), str(self.hi)]


def rational_parameters(p):
    return {k: Q(float(v)) for k, v in p.items()}


def quartic_form(p):
    """q=(x,y,Re z,Im z,s); V4=q^T C q, independently constructed."""
    c = [[Q(0) for _ in range(5)] for _ in range(5)]
    for i, a in enumerate((p['Lambda1']/2, p['Lambda2']/2,
                           p['Lambda4']+p['Lambda5'], p['Lambda4']-p['Lambda5'], p['LambdaC'])):
        c[i][i] = a
    for i, j, a in ((0, 1, p['Lambda3']/2), (0, 4, p['K1']/2),
                    (1, 4, p['K2']/2), (2, 4, -p['K12'])):
        c[i][j] = c[j][i] = a
    return c


def residual_form(p, epsilon):
    c = quartic_form(p)
    c[0][1] -= epsilon/2
    c[1][0] -= epsilon/2
    c[2][2] += epsilon
    c[3][3] += epsilon
    return c


def positive_ldl(matrix):
    """Exact rational LDL^T, deliberately requires positive definite."""
    n = len(matrix)
    l = [[Q(i == j) for j in range(n)] for i in range(n)]
    d = []
    for i in range(n):
        pivot = matrix[i][i]-sum(l[i][k]*l[i][k]*d[k] for k in range(i))
        if pivot <= 0:
            return None
        d.append(pivot)
        for j in range(i+1, n):
            l[j][i] = (matrix[j][i]-sum(l[j][k]*l[i][k]*d[k] for k in range(i)))/pivot
    return d


def neutral_enclosure(parameters, physical):
    """Exact rational Krawczyk self-map/contraction in a 2D neutral box."""
    p = rational_parameters(parameters)
    mix = p['Lambda3']+p['Lambda4']+p['Lambda5']

    def f(a, b):
        return [a*(p['M112']+p['Lambda1']*a*a/2+mix*b*b/2)-p['M12Sq']*b,
                b*(p['M222']+p['Lambda2']*b*b/2+mix*a*a/2)-p['M12Sq']*a]

    def jac(a, b):
        off = mix*a*b-p['M12Sq']
        return [[p['M112']+3*p['Lambda1']*a*a/2+mix*b*b/2, off],
                [off, p['M222']+3*p['Lambda2']*b*b/2+mix*a*a/2]]

    with mp.workdps(90):
        conv = lambda q: mp.mpf(q.numerator)/q.denominator
        pp = {k: conv(v) for k, v in p.items()}
        lm = pp['Lambda3']+pp['Lambda4']+pp['Lambda5']
        a, b = mp.findroot(lambda a, b: (
            a*(pp['M112']+pp['Lambda1']*a*a/2+lm*b*b/2)-pp['M12Sq']*b,
            b*(pp['M222']+pp['Lambda2']*b*b/2+lm*a*a/2)-pp['M12Sq']*a),
            (physical['v']*math.cos(physical['beta']), physical['v']*math.sin(physical['beta'])),
            tol=mp.mpf('1e-80'))
        center = [Q(mp.nstr(a, 75)), Q(mp.nstr(b, 75))]
    requested = [physical['v']*math.cos(physical['beta']), physical['v']*math.sin(physical['beta'])]
    if max(abs(float(a)-b) for a, b in zip(center, requested)) > 1e-8:
        raise ValueError('Neutral root is not the requested EW candidate')
    radius = Q(1, 10**40)
    box = [Interval(c-radius, c+radius) for c in center]
    if any(a.lo <= 0 for a in box):
        raise ValueError('Positive neutral chart required')
    j = jac(*center)
    det = j[0][0]*j[1][1]-j[0][1]*j[1][0]
    inverse = [[j[1][1]/det, -j[0][1]/det], [-j[1][0]/det, j[0][0]/det]]
    jbox = jac(*box)
    error = [[Interval(int(i == k))-sum(inverse[i][j]*jbox[j][k] for j in range(2))
              for k in range(2)] for i in range(2)]
    values = f(*center)
    image = [center[i]-sum(inverse[i][j]*values[j] for j in range(2))
             +sum(error[i][j]*Interval(-radius, radius) for j in range(2)) for i in range(2)]
    contraction = max(sum(a.magnitude() for a in row) for row in error)
    if not (contraction < 1 and all(x.lo < k.lo <= k.hi < x.hi for x, k in zip(box, image))):
        raise ValueError('Exact Krawczyk inclusion failed')
    return box, {'method': 'EXACT_RATIONAL_KRAWCZYK_CONTRACTION',
                 'neutral_fields_GeV_intervals': [b.serial() for b in box],
                 'radius_GeV': str(radius), 'contraction_upper': str(contraction),
                 'root_unique_in_box': True}


def attempt_certificate(parameters, physical):
    """Numerically propose epsilon, then verify every sufficient inequality exactly."""
    p = rational_parameters(parameters)
    c = np.array(quartic_form(p), float)
    beta, v = physical['beta'], physical['v']
    a, b = v*math.cos(beta), v*math.sin(beta)
    md = (a*a+b*b)*(float(p['M12Sq'])/(a*b)-float(p['Lambda4']+p['Lambda5'])/2)
    ms = float(p['MCS2'])+(float(p['K1'])*a*a+float(p['K2'])*b*b-2*float(p['K12'])*a*b)/2
    lower, upper = max(1e-8, float(p['Mu4'])**2/ms) if ms > 0 else math.inf, 2*md/v**2
    out = {'certified': False, 'ansatz': 'FULL_COMPLEX_GRAM_SQUARE_COMPLETION',
           'epsilon_search_interval': [lower if math.isfinite(lower) else None, upper]}
    if not lower < upper:
        out['blocker'] = 'No positive epsilon interval in this sufficient ansatz'
        return out
    delta = np.zeros((5, 5)); delta[0, 1] = delta[1, 0] = .5
    delta[2, 2] = delta[3, 3] = -1
    result = minimize_scalar(lambda e: -np.linalg.eigvalsh(c-e*delta)[0],
                             bounds=(lower, upper), method='bounded', options={'xatol': 1e-12})
    epsilon = Q(round(float(result.x)*10**6), 10**6)
    out.update(epsilon=str(epsilon), numerical_best_min_eigenvalue=-float(result.fun))
    pivots = positive_ldl(residual_form(p, epsilon))
    if pivots is None:
        out['blocker'] = 'Residual Gram quadratic is not positive definite; not a necessary condition'
        return out
    box, proof = neutral_enclosure(parameters, physical)
    a, b = box
    norm = a*a+b*b
    md = norm*(p['M12Sq']/(a*b)-(p['Lambda4']+p['Lambda5'])/2)
    ms = p['MCS2']+(p['K1']*a*a+p['K2']*b*b-2*p['K12']*a*b)/2
    margins = [md-epsilon*norm/2, ms-p['Mu4']**2/epsilon]
    out.update(neutral_root=proof, exact_ldl_pivots=[str(d) for d in pivots],
               nonnegative_coefficient_intervals_GeV2=[m.serial() for m in margins])
    out['certified'] = all(m.lo > 0 for m in margins)
    if not out['certified']:
        out['blocker'] = 'Exact neutral-root coefficient intervals did not remain positive'
    return out


def singlet_axis_proof(parameters, physical):
    """Exact analytic local-minimum/depth test in the Mu4=0 singlet control."""
    p = rational_parameters(parameters)
    if p['Mu4'] != 0 or p['MCS2'] >= 0 or p['LambdaC'] <= 0:
        return None
    s = -p['MCS2']/(2*p['LambdaC'])
    aa, bb = p['M112']+p['K1']*s, p['M222']+p['K2']*s
    off = -p['M12Sq']-p['K12']*s
    if not (aa > 0 and bb > 0 and aa*bb-off*off > 0):
        return None
    box, _ = neutral_enclosure(parameters, physical)
    a, b = box
    x, y, u = a*a/2, b*b/2, a*b/2
    neutral = (p['M112']*x+p['M222']*y-2*p['M12Sq']*u
               +p['Lambda1']*x*x/2+p['Lambda2']*y*y/2
               +(p['Lambda3']+p['Lambda4']+p['Lambda5'])*x*y)
    value = -p['MCS2']**2/(4*p['LambdaC'])
    gap = value-neutral
    if gap.hi >= 0:
        return None
    return {'stationary_fields': 'all zero except r8=sqrt(-MCS2/LambdaC)',
            'singlet_norm_GeV2': str(s), 'value_GeV4': str(value),
            'delta_GeV4_interval': gap.serial(), 'doublet_diagonal_GeV2': [str(aa), str(bb)],
            'doublet_determinant_GeV4': str(aa*bb-off*off),
            'radial_singlet_mass_squared_GeV2': str(-2*p['MCS2']),
            'gauge_zero_modes': 1, 'positive_transverse_modes': 9}


def radial_exclusion(parameters, physical):
    """Exact conservative radius outside which V>=0>V_EW.

    N=x+y+s, t=sqrt(N); V >= k*t^4-b*t^3-M*t^2.
    This compactifies a future interval/SOS search, without proving its interior.
    """
    p = rational_parameters(parameters)
    if not (p['K1'] >= 0 and p['K2'] >= 0 and p['K1']*p['K2'] >= p['K12']**2
            and min(p['Lambda1'], p['Lambda2'], p['LambdaC']) > 0):
        return None
    a, b = p['Lambda1']/2, p['Lambda2']/2
    cross = p['Lambda3']+min(Q(0), p['Lambda4']-abs(p['Lambda5']))
    cd = min(a, b)/2
    if cross < 0:
        for _ in range(80):
            if a-cd > 0 and b-cd > 0 and (a-cd)*(b-cd)-(cross/2-cd)**2 > 0:
                break
            cd /= 2
        else:
            return None
    k = min(cd, p['LambdaC'])/2
    cubic = abs(p['Mu4'])/2  # 2/(3 sqrt(3)) < 1/2, exact conservative bound.
    mass = max(abs(p['M112'])+abs(p['M12Sq']), abs(p['M222'])+abs(p['M12Sq']), abs(p['MCS2']))
    approximate = (float(cubic)+math.sqrt(float(cubic)**2+4*float(k*mass)))/(2*float(k))
    bound = max(1, math.ceil(approximate)+1)
    while k*bound**2-cubic*bound-mass <= 0:
        bound += 1
    # Past the positive root the quadratic increases; bound also exceeds its vertex.
    assert 2*k*bound > cubic
    box, _ = neutral_enclosure(parameters, physical)
    aa, bb = box; x, y, u = aa*aa/2, bb*bb/2, aa*bb/2
    value = p['M112']*x+p['M222']*y-2*p['M12Sq']*u+p['Lambda1']*x*x/2+p['Lambda2']*y*y/2
    value += (p['Lambda3']+p['Lambda4']+p['Lambda5'])*x*y
    if value.hi >= 0:
        return None
    return {'quartic_norm_lower_coefficient': str(k), 'cubic_norm_upper_coefficient_GeV': str(cubic),
            'quadratic_norm_upper_coefficient_GeV2': str(mass),
            'sqrt_x_plus_y_plus_s_bound_GeV': bound,
            'canonical_field_radius_squared_bound_GeV2': 2*bound**2,
            'exact_positive_quadratic_at_bound_GeV2': str(k*bound**2-cubic*bound-mass),
            'EW_value_GeV4_interval': value.serial(),
            'meaning': 'V>=0>V_EW outside this radius; interior unresolved unless separately certified'}
