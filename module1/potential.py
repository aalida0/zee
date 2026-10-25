"""Canonical real-field potential matching frozen SARAH ZeeTypeII.m.

H1=(r0+i r1,r2+i r3)/sqrt(2), H2=(r4+i r5,r6+i r7)/sqrt(2),
S=(r8+i r9)/sqrt(2). Invariants q=(|H1|²,|H2|²,Re H1†H2,Im H1†H2,|S|²).
The invariant/tensor construction follows the isolated C4/C5 reference
functions; no historical scan/RG machinery is imported.
"""
import itertools
import numpy as np

A = np.zeros((5, 10, 10))
for a, indices in ((0, range(4)), (1, range(4, 8)), (4, range(8, 10))):
    for i in indices:
        A[a, i, i] = 1
for i in range(4):
    A[2, i, i+4] = A[2, i+4, i] = .5
for i, j, sign in ((0, 5, 1), (1, 4, -1), (2, 7, 1), (3, 6, -1)):
    A[3, i, j] = A[3, j, i] = sign*.5
PAIRS = np.array(list(itertools.combinations_with_replacement(range(10), 2)))


def quartic_matrix(p):
    c = np.diag([p['Lambda1']/2, p['Lambda2']/2,
                 p['Lambda4']+p['Lambda5'], p['Lambda4']-p['Lambda5'], p['LambdaC']])
    for i, j, value in ((0, 1, p['Lambda3']/2), (0, 4, p['K1']/2),
                        (1, 4, p['K2']/2), (2, 4, -p['K12'])):
        c[i, j] = c[j, i] = value
    return c


class Potential:
    def __init__(self, parameters):
        self.p = parameters
        self.c = quartic_matrix(parameters)
        self.h2 = sum(parameters[k]*A[i] for k, i in
                      (('M112', 0), ('M222', 1), ('MCS2', 4))) - 2*parameters['M12Sq']*A[2]
        self.t3 = np.zeros((10, 10, 10))
        for indices, sign in (((8, 0, 6), 1), ((8, 1, 7), -1),
                              ((8, 2, 4), -1), ((8, 3, 5), 1),
                              ((9, 0, 7), 1), ((9, 1, 6), 1),
                              ((9, 2, 5), -1), ((9, 3, 4), -1)):
            for perm in itertools.permutations(indices):
                self.t3[perm] = sign*parameters['Mu4']/np.sqrt(2)

    def evaluate(self, r, hessian=True):
        r = np.asarray(r, float)
        if r.shape != (10,) or not np.isfinite(r).all():
            raise ValueError('Expected ten finite canonical real fields')
        q = .5*np.einsum('i,aij,j->a', r, A, r)
        dq = A@r
        cubic = np.einsum('ijk,j,k->i', self.t3, r, r)
        cq = self.c@q
        value = r@self.h2@r/2 + r@cubic/6 + q@cq
        grad = self.h2@r+cubic/2+2*dq.T@cq
        if not hessian:
            return float(value), grad
        h = self.h2+np.einsum('ijk,k->ij', self.t3, r)
        h += 2*np.einsum('a,aij->ij', cq, A)+2*dq.T@self.c@dq
        return float(value), grad, h


def component_value(r, p, quartic_only=False):
    """Alternative complex-component evaluation, independent of A,C,T tensors."""
    z = (np.asarray(r)[::2]+1j*np.asarray(r)[1::2])/np.sqrt(2)
    h1, h2, s = z[:2], z[2:4], z[4]
    x, y, w = np.vdot(h1, h1).real, np.vdot(h2, h2).real, abs(s)**2
    t = np.vdot(h1, h2)
    value = (p['Lambda1']/2*x*x+p['Lambda2']/2*y*y+p['Lambda3']*x*y
             +p['Lambda4']*abs(t)**2+p['Lambda5']*(t*t).real+p['LambdaC']*w*w
             +(p['K1']*x+p['K2']*y-2*p['K12']*t.real)*w)
    if not quartic_only:
        value += (p['M112']*x+p['M222']*y-2*p['M12Sq']*t.real+p['MCS2']*w
                  +2*p['Mu4']*(s.conjugate()*(h1[0]*h2[1]-h1[1]*h2[0])).real)
    return float(value)


def contact_tensor(p):
    c = quartic_matrix(p)
    return 2*(np.einsum('ab,aij,bkl->ijkl', c, A, A)
              +np.einsum('ab,aik,bjl->ijkl', c, A, A)
              +np.einsum('ab,ail,bjk->ijkl', c, A, A))


def scatter_matrix(p, tensor=None):
    t = contact_tensor(p) if tensor is None else tensor
    i, j = PAIRS.T
    normalization = np.sqrt(1+(i == j).astype(float))
    return t[i[:, None], j[:, None], i, j]/np.outer(normalization, normalization)


def charge_basis():
    """Unitary symmetric-pair lift of Q,Y eigenvectors; Y recorded as 2Y."""
    b = np.zeros((10, 10), complex)
    labels = []
    for k, (charge, hyper) in enumerate(((1, 1), (0, 1), (1, 1), (0, 1), (1, 2))):
        for a, sign in enumerate((1, -1)):
            b[2*k, 2*k+a] = 1/np.sqrt(2)
            b[2*k+1, 2*k+a] = sign*1j/np.sqrt(2)
            labels.append((sign*charge, sign*hyper))
    lift = np.empty((55, 55), complex)
    for n, (i, j) in enumerate(PAIRS):
        for m, (k, l) in enumerate(PAIRS):
            lift[n, m] = (b[i, k]*b[j, l]+b[i, l]*b[j, k])/np.sqrt((1+(i == j))*(1+(k == l)))
    sectors = {}
    for n, (i, j) in enumerate(PAIRS):
        label = tuple(np.array(labels[i])+labels[j])
        sectors.setdefault(label, []).append(n)
    return lift, sectors


def legacy_neutral_basis(lift):
    """13 neutral pairs in Gate6/Florentino App.C5's all-incoming basis.

    The physical Hermitian operator is B† M B; Bᵀ M B instead reproduces
    the legacy signed spectrum. They have equal singular values here.
    """
    pairs = [(0, 1), (0, 5), (0, 9), (1, 4), (4, 5), (4, 9),
             (1, 8), (5, 8), (8, 9), (2, 3), (3, 6), (2, 7), (6, 7)]
    lookup = list(map(tuple, PAIRS))
    return lift[:, [lookup.index(tuple(sorted(pair))) for pair in pairs]]


def gauge_audit(r, h):
    """Remove only broken SU2 x U1 gauge tangents, including singular strata."""
    z = (r[::2]+1j*r[1::2])/np.sqrt(2)
    pauli = [np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]]), np.diag([1, -1])]
    dzs = [np.r_[1j*t@z[:2]/2, 1j*t@z[2:4]/2, 0.] for t in pauli]
    dzs += [1j*z*np.array([.5, .5, .5, .5, 1.])]
    tangents = np.empty((10, 4))
    for k, dz in enumerate(dzs):
        tangents[::2, k] = np.sqrt(2)*dz.real
        tangents[1::2, k] = np.sqrt(2)*dz.imag
    u, s, _ = np.linalg.svd(tangents, full_matrices=True)
    rank = int(sum(s > 1e-9*max(1., np.linalg.norm(r))))
    physical = u[:, rank:]
    minimum = float(np.linalg.eigvalsh(physical.T@h@physical).min())
    ward = float(np.max(abs(h@u[:, :rank]))) if rank else 0.
    return rank, minimum, ward
