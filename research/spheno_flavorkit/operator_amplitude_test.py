"""Independent on-shell D12 dipole matrix-element identities.

This tests the tensor, Ward identity, Fourier sign and Hermitian conjugate.
It deliberately does not assert a FormCalc-to-SPheno mapping: its overall
crossing phase still has to be tied to the installed generated projector.
"""
import numpy as np

I2 = np.eye(2, dtype=complex)
z = np.zeros((2, 2), dtype=complex)
s = [np.array([[0,1],[1,0]],complex), np.array([[0,-1j],[1j,0]]), np.diag([1.,-1.]).astype(complex)]
g = [np.block([[I2,z],[z,-I2]])] + [np.block([[z,x],[-x,z]]) for x in s]
g5 = 1j*g[0]@g[1]@g[2]@g[3]
PL, PR = (np.eye(4)-g5)/2, (np.eye(4)+g5)/2
metric = np.array([1.,-1.,-1.,-1.])


def slash(p):
    return sum(metric[i]*p[i]*g[i] for i in range(4))


def u(p, m, spin):
    chi = np.eye(2, dtype=complex)[:, spin]
    return np.r_[np.sqrt(p[0]+m)*chi,
                 sum(p[i+1]*s[i] for i in range(3))@chi/np.sqrt(p[0]+m)]


def bar(x):
    return x.conj()@g[0]


def tensor(q, eps):
    # sigma^{mu nu} q_mu eps_nu
    qc, ec = metric*q, metric*eps
    return sum((0.5j*(g[a]@g[b]-g[b]@g[a]))*qc[a]*ec[b]
               for a in range(4) for b in range(4))


def run():
    mi, mj = 3., .7
    energy = (mi*mi-mj*mj)/(2*mi)
    direction = np.array([1., 2., 3.])/np.sqrt(14.)
    q = np.r_[energy, energy*direction]
    p = np.array([mi, 0., 0., 0.])
    k = p-q
    # Add a gauge component so p.epsilon is nonzero; q.epsilon remains zero.
    eps = np.r_[0., np.array([2.,-1.,0.])/np.sqrt(5.)] + .4*q
    cl, cr = .37+.83j, -.29+.41j
    coeff = cl*PL+cr*PR
    conj_coeff = cr.conjugate()*PL+cl.conjugate()*PR
    assert abs(q@ (metric*q)) < 1e-14
    assert abs(q@ (metric*eps)) < 1e-14
    assert abs(p@(metric*eps)) > 0.1
    for a in range(2):
        for b in range(2):
            ui, uj = u(p,mi,a), u(k,mj,b)
            assert np.linalg.norm((slash(p)-mi*np.eye(4))@ui) < 1e-14
            assert np.linalg.norm((slash(k)-mj*np.eye(4))@uj) < 1e-14
            t = bar(uj)@tensor(q,eps)@coeff@ui
            # Outgoing-created photon: F_{mu nu}=+i(q_mu eps_nu-q_nu eps_mu).
            direct = 1j*mi*t
            # sigma(q,eps)=i qslash epsslash, for q.eps=0.
            independent = -mi*(bar(uj)@slash(q)@slash(eps)@coeff@ui)
            assert abs(direct-independent) < 1e-13
            assert abs(bar(uj)@tensor(q,q)@coeff@ui) < 1e-13
            # Dirac adjoint exchanges chiral labels and conjugates couplings.
            reverse = bar(ui)@tensor(q,eps)@conj_coeff@uj
            assert abs(reverse-t.conjugate()) < 1e-13
            # Gordon reduction keeps the vector term: the scalar projector
            # alone is not the complete gauge-invariant matrix element.
            swapped = cl*PR+cr*PL
            scalar = bar(uj)@coeff@ui
            vectors = bar(uj)@slash(eps)@(mi*swapped+mj*coeff)@ui
            reduced = 1j*(2*(p@(metric*eps))*scalar-vectors)
            assert abs(t-reduced) < 1e-13
            # Actual recovered projector ordering: vbar(k1) [6 or 7] u(k2).
            # Analytic crossing chooses k1=-p, k2=k, so v(k1)=u(p)
            # is a legitimate continuation of (k1slash+mi)v=0.
            # Overall external-state crossing phases remain a convention.
            k1, k2 = -p, k
            crossed_q = k1+k2
            v1, u2 = ui, uj
            assert np.linalg.norm((slash(k1)+mi*np.eye(4))@v1) < 1e-14
            crossed_t = bar(v1)@tensor(crossed_q,eps)@conj_coeff@u2
            crossed_vectors = bar(v1)@slash(eps)@(mi*conj_coeff+mj*(cr.conjugate()*PR+cl.conjugate()*PL))@u2
            crossed_reduced = -1j*(2*(k1@(metric*eps))*(bar(v1)@conj_coeff@u2)+crossed_vectors)
            assert abs(crossed_t-crossed_reduced) < 1e-13
            # Calculate the two Fourier signs explicitly from F_mu_nu.
            qc, ec = metric*q, metric*eps
            def insertion(sign):
                field = sign*1j*(np.outer(qc,ec)-np.outer(ec,qc))
                sigma_f = sum(0.5j*(g[x]@g[y]-g[y]@g[x])*field[x,y]
                              for x in range(4) for y in range(4))
                return mi/2*(bar(uj)@sigma_f@coeff@ui)
            assert abs(insertion(1)-direct) < 1e-13
            assert abs(insertion(-1)+direct) < 1e-13
    print('PASS: explicit spinors, on-shell tensor, Ward identity, Fourier sign, Hermitian conjugation')


if __name__ == '__main__':
    run()
