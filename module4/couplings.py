"""Frozen-model couplings; native all-incoming rules are -i C PL, -i C* PR."""
import math
import numpy as np


def quarks(mass, species, p):
    """Neutral Type-II vertices from -Yd H1* d q + Yu H2 u q + h.c.

    Neutral diagonal vertices contain no CKM matrix. CP-odd conjugation
    reverses sign for up quarks. Unlike the old reference A is NOT rephased.
    """
    a,b,v = p['alpha'],p['beta'],p['v']
    if species in ('up','charm','top'):
        return {'h':mass/v*math.sin(a)/math.sin(b),
                'H':mass/v*math.cos(a)/math.sin(b),
                'A':1j*mass/v/math.tan(b)}
    if species in ('down','strange','bottom'):
        return {'h':mass/v*math.cos(a)/math.cos(b),
                'H':-mass/v*math.sin(a)/math.cos(b),
                'A':1j*mass/v*math.tan(b)}
    raise ValueError('Unknown Type-II quark')


def rotations(p):
    ca,sa,cb,sb,cg,sg = [f(p[k]) for f,k in
        [(math.cos,'alpha'),(math.sin,'alpha'),(math.cos,'beta'),
         (math.sin,'beta'),(math.cos,'gamma'),(math.sin,'gamma')]]
    return (np.array([[ca,sa],[-sa,ca]]),
            np.array([[cb,sb],[-sb,cb]]),
            np.array([[cb,sb,0],[-sb*cg,cb*cg,sg],[sb*sg,-cb*sg,cg]]))


def trilinears(p, lagrangian):
    """G_s,kl = d^3 V / ds dH-_k dH+_l (GeV), including CP-odd A.

    Differentiating the gauge charged mass matrix with respect to phi1/phi2
    gives these two symmetric matrices. Rotate BOTH charged legs; off-diagonal
    interactions are retained, including A's imaginary off-diagonal entries.
    """
    q=lagrangian
    v1,v2=p['v']*math.cos(p['beta']),p['v']*math.sin(p['beta'])
    l1,l2,l3,l45 = q['Lambda1'],q['Lambda2'],q['Lambda3'],q['Lambda4']+q['Lambda5']
    mu=q['Mu4']/math.sqrt(2)
    g1=np.array([[l1*v1,l45*v2/2,0],[l45*v2/2,l3*v1,-mu],
                 [0,-mu,q['K1']*v1-q['K12']*v2]])
    g2=np.array([[l3*v2,l45*v1/2,mu],[l45*v1/2,l2*v2,0],
                 [mu,0,q['K2']*v2-q['K12']*v1]])
    zh,_,zp=rotations(p)
    result={s:zp@(row[0]*g1+row[1]*g2)@zp.T for s,row in zip(('h','H'),zh)}
    _,za,_=rotations(p)
    a1,a2=za[1]
    c12=.5*(q['Lambda4']-q['Lambda5'])*(v2*a1-v1*a2)
    ga=1j*np.array([[0,c12,-mu*a2],[-c12,0,mu*a1],[mu*a2,-mu*a1,0]])
    result['A']=zp@ga@zp.T
    return result
