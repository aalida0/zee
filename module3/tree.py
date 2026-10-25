"""Coherent neutral exchange, including crossed contractions and masses.

Deterministic phase-space quadrature; no massless final-state substitution.
The tensor is evaluated before squaring, including the Fermi minus sign.
"""
from functools import lru_cache
import math
import numpy as np

I2 = np.eye(2, dtype=complex)
O2 = np.zeros((2,2), complex)
G0 = np.block([[I2,O2],[O2,-I2]])
PAULI = [np.array([[0,1],[1,0]]), np.array([[0,-1j],[1j,0]]), np.diag([1,-1])]
G = [G0]+[np.block([[O2,s],[-s,O2]]) for s in PAULI]
G5 = 1j*G[0]@G[1]@G[2]@G[3]
PL, PR = (np.eye(4)-G5)/2, (np.eye(4)+G5)/2
TREE_OPERATOR = 'M=sum_s[(ubar_a Gamma_ai u_i)(ubar_b Gamma_bb v_b)/(m_s^2-s23)-(ubar_b Gamma_bi u_i)(ubar_a Gamma_ab v_b)/(m_s^2-s13)];Gamma=C*PL+Cdag*PR'


def slash(p):
    return p[0]*G0-sum(p[k]*G[k] for k in range(1,4))


def kallen(a,b,c):
    return (a-b-c)**2-4*b*c


def momenta(M, masses, s, z):
    a,b,c = masses
    q = math.sqrt(max(0.,kallen(M*M,a*a,s)))/(2*M)
    eq = (M*M-a*a+s)/(2*M)
    e1 = (M*M+a*a-s)/(2*M)
    root = math.sqrt(s)
    e2 = (s+b*b-c*c)/(2*root)
    e3 = (s+c*c-b*b)/(2*root)
    k = math.sqrt(max(0.,kallen(s,b*b,c*c)))/(2*root)
    x = k*math.sqrt(max(0.,1-z*z))
    boost, beta = eq/root, q/eq
    p2 = np.array([boost*(e2+beta*k*z),x,0.,boost*(k*z+beta*e2)])
    p3 = np.array([boost*(e3-beta*k*z),-x,0.,boost*(-k*z+beta*e3)])
    return [np.array([M,0.,0.,0.]),np.array([e1,0.,0.,-q]),p2,p3]


def tensors(scalars, i, a, b):
    direct, crossed, masses = [], [], []
    for C, mass in scalars.values():
        def vertex(j,k):
            return G0@(C[j,k]*PL+C[k,j].conjugate()*PR)
        direct.append(np.einsum('ab,cd->abcd',vertex(a,i),vertex(b,b)))
        crossed.append(np.einsum('cb,ad->abcd',vertex(b,i),vertex(a,b)))
        masses.append(mass)
    return np.array(direct), np.array(crossed), np.array(masses)


def spin_sum(T, ps, M, masses):
    """Unpolarized parent; spin densities u u† and v v†."""
    ds = [(slash(p)+m*np.eye(4))@G0 for p,m in zip(ps,[M,*masses[:2],-masses[2]])]
    u = np.einsum('ea,abcd->ebcd',ds[1],T)
    u = np.einsum('bf,ebcd->efcd',ds[0],u)
    u = np.einsum('gc,efcd->efgd',ds[2],u)
    u = np.einsum('dh,efgd->efgh',ds[3],u)
    value = np.sum(u*T.conjugate())/2
    if abs(value.imag) > 2e-11*max(abs(value.real),1e-300) or value.real < -1e-25:
        raise ArithmeticError('Nonphysical spin sum')
    return max(0.,float(value.real))


@lru_cache(maxsize=64)
def phase_grid(M, a, b, c, order):
    """s=lo+(hi-lo)sin²(theta) smooths massive endpoints."""
    nodes, weights = np.polynomial.legendre.leggauss(order)
    lo, hi = (b+c)**2, (M-a)**2
    out = []
    for x,w in zip(nodes,weights):
        theta = (x+1)*np.pi/4
        s = lo+(hi-lo)*math.sin(theta)**2
        jac = (hi-lo)*math.sin(2*theta)*np.pi/4
        phase = math.sqrt(max(0.,kallen(M*M,a*a,s)*kallen(s,b*b,c*c)))
        phase /= 512*np.pi**3*M**3*s
        for z,v in zip(nodes,weights):
            ps = momenta(M,(a,b,c),s,z)
            s13p = ps[1]+ps[3]
            s13 = s13p[0]**2-np.dot(s13p[1:],s13p[1:])
            out.append((ps,s,s13,w*v*jac*phase))
    return out


def width(scalars, i, a, b, ml, order, contact=False):
    M, masses = ml[i], (ml[a],ml[b],ml[b])
    if M <= sum(masses):
        return 0.
    direct, crossed, ms = tensors(scalars,i,a,b)
    if min(ms) <= M:
        raise ValueError('On-shell scalar region requires widths/resonance treatment')
    total = 0.
    for ps,s23,s13,w in phase_grid(M,*masses,order):
        dprop = 1/(ms**2-(0 if contact else s23))
        eprop = 1/(ms**2-(0 if contact else s13))
        T = np.einsum('s,sabcd->abcd',dprop,direct)-np.einsum('s,sabcd->abcd',eprop,crossed)
        total += w*spin_sum(T,ps,M,masses)
    return total/(2 if a == b else 1)


def wilsons(scalars, i, a, b):
    """Contact coefficients of direct and exchanged ordered bilinears.

    No factor 1/2 in a contracted amplitude. Identical-particle division
    belongs to phase space, after coherent antisymmetrization.
    """
    out = {}
    for name,(C,mass) in scalars.items():
        def coef(x,y,z,w):
            return {u+v: complex(l*r/mass**2)
                    for u,l in [('L',C[x,y]),('R',C[y,x].conjugate())]
                    for v,r in [('L',C[z,w]),('R',C[w,z].conjugate())]}
        out[name] = {'direct':coef(a,i,b,b),'exchanged':coef(b,i,a,b)}
    return out
