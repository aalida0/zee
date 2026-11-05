"""Proved zeros of charged-scalar-only A-Z/G0 two-point insertions.

No assertion about fermion, W/charged-scalar, or full reducible EW amplitudes.
"""
import sympy as s


def prove():
    cb,sb,cg,sg,mu,delta,v,sw,cw=s.symbols('cb sb cg sg mu delta v sw cw',real=True)
    # Higgs basis (G+,HD+,S+) before physical charged mixing. Exact native
    # potential derivative: c12=-delta*v/2; physical A block vanishes.
    A=s.I*s.Matrix([[0,-delta*v/2,-mu],[delta*v/2,0,0],[mu,0,0]])
    G0=s.I*s.Matrix([[0,0,0],[0,0,mu], [0,-mu,0]])
    R=s.Matrix([[1,0,0],[0,cg,sg],[0,-sg,cg]])
    charge=s.diag(s.Rational(1,2)-sw**2,s.Rational(1,2)-sw**2,-sw**2)/(sw*cw)
    aa=s.expand(R*A*R.T);gg=s.expand(R*G0*R.T);zz=s.expand(R*charge*R.T)
    # Independent arbitrary diagonal propagator/mass functions: a topology
    # vanishes before loop integration, without assuming mass degeneracy.
    f=s.diag(*s.symbols('f0:3'));g=s.diag(*s.symbols('g0:3'))
    residuals={
        'A_Z_two_point':s.expand(s.trace(aa*f*zz*g)),
        'A_G0_two_point':s.expand(s.trace(aa*f*gg*g)),
    }
    if any(x!=0 for x in residuals.values()):
        raise ArithmeticError('Charged scalar support proof failed')
    return dict(status='PROVED_ZERO_CHARGED_SCALAR_LOOP_SUBSET',
        residuals={k:str(x) for k,x in residuals.items()},
        A_matrix=str(aa),G0_matrix=str(gg),Z_matrix=str(zz),
        photon_attachments='Q=I and diagonal propagators preserve the disjoint support; internal/external attachments of these zero two-point loops also vanish',
        missing='A-G+-H+- with W, fermion A-Z/G0, other reducible mixing and LSZ are not proved zero',
        full_reducible_C_LR=None)
