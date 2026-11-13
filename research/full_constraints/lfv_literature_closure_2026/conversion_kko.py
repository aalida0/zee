"""Coherent mu->e conversion at leading scalar/vector/dipole order.

Operator conventions: Primulando, Julio & Uttayarat, EPJC 82 (2022) 253,
Eqs. (31), (32), (38), (41)-(43); KKO PRD 66 (2002) 096002.
The published Eq. (41) has no neutron VECTOR term because its vector
coefficients are exclusively electromagnetic (and hence neutron zero).
Here the KKO-generalized neutron vector term is retained for arbitrary
Z-penguin/box UV Wilson coefficients. This is a rate interpreter, NOT UV
matching, QED/QCD running, a calibrated nuclear likelihood, or an LFV PASS.

Inputs: cL,cR and g_{LS,RS,LV,RV}^q are dimension -2 GeV^-2 in the
published 2022 Eq. (38) convention. Do not pass SARAH/FlavorKit K2, O4q,
or flavio WET coefficients without a separately VERIFIED mapping.
Scalar f_q^N and quark masses are mandatory for any scalar Wilson input.
Nuclear overlaps below are KKO-era reference choices, NOT 2026 precision
nuclear response functions; nucleus-dependent uncertainties are not supplied.
"""
from dataclasses import dataclass
import math

ALPHA0 = 1/137.035999084
MMU = 0.1056583755  # GeV
TAU_MU = 2.1969811e-6  # s
HBAR = 6.582119569e-25  # GeV*s
MP = 0.93827208816
MN = 0.93956542052
Q = {'u': 2/3, 'd': -1/3, 's': -1/3, 'c': 2/3, 'b': -1/3, 't': 2/3}

@dataclass(frozen=True)
class Target:
    D: float
    Sp: float
    Sn: float
    Vp: float
    Vn: float
    capture_per_s: float

# The dimensionless D,S,V are multiplied by m_mu^(5/2) in KKO convention.
TARGETS = {
    'Al27': Target(.0362, .0155, .0167, .0161, .0173, .7054e6),
    'Ti48': Target(.0864, .0368, .0435, .0396, .0468, 2.59e6),
    'Au197': Target(.189, .0614, .0918, .0974, .146, 13.07e6),
}


def coefficient(z):
    if isinstance(z, bool):
        raise ValueError('Coefficient must be complex or real, not bool')
    try:
        z = complex(z)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError('Coefficient must be finite') from exc
    if not (math.isfinite(z.real) and math.isfinite(z.imag)):
        raise ValueError('Coefficient nonfinite')
    return z


def _quark_wilsons(values):
    if values is None:
        return {}
    if not isinstance(values, dict) or set(values)-set(Q):
        raise ValueError('Expected dictionary over u,d,s,c,b,t')
    return {key:coefficient(value) for key,value in values.items()}


def photon_monopole_vector(a, alpha=ALPHA0):
    """2022 Eq. (38)-(39): g_V^q=-8*pi*alpha*Q_q*a (GeV^-2)."""
    a=coefficient(a)
    return {key:-8*math.pi*alpha*charge*a for key,charge in Q.items()}


def vector_nucleon(g):
    """Valence-current normalization: proton=2u+d, neutron=u+2d."""
    g=_quark_wilsons(g)
    return 2*g.get('u',0j)+g.get('d',0j),g.get('u',0j)+2*g.get('d',0j)


def scalar_nucleon(g, f_light, masses):
    """KKO/2022 Eq.(42-43): m_N sum_q f_q^N*g_S^q/m_q, heavy 2/27.

    The numerical scale/scheme of g_S and quark masses must be consistent;
    this function intentionally performs NO RG evolution or threshold matching.
    """
    g=_quark_wilsons(g)
    if not g:
        return 0j,0j
    if not isinstance(f_light,dict) or set(f_light)!={'p','n'}:
        raise ValueError('Supply p,n scalar fractions explicitly')
    if not isinstance(masses,dict) or set(masses)!=set(Q):
        raise ValueError('Supply all six quark masses in GeV, same scheme as Wilsons')
    if any((not math.isfinite(float(m)) or float(m)<=0) for m in masses.values()):
        raise ValueError('Invalid quark mass')
    out=[]
    for nuc,mass_N in [('p',MP),('n',MN)]:
        fs=f_light[nuc]
        if not isinstance(fs,dict) or set(fs)!={'u','d','s'}:
            raise ValueError('Supply u,d,s scalar mass fractions separately for p,n')
        if any(not math.isfinite(float(v)) or float(v)<0 for v in fs.values()):
            raise ValueError('Invalid scalar fractions')
        total_light=sum(float(v) for v in fs.values())
        if total_light>=1:
            raise ValueError('Invalid scalar fractions: sum >= 1')
        f_heavy=(2/27)*(1-total_light)
        out.append(sum(g.get(q,0j)*mass_N*(float(fs[q]) if q in fs else f_heavy)/float(masses[q])
                       for q in Q))
    return tuple(out)


def conversion_rate(target, *, cL=0, cR=0, gLS=None,gRS=None,gLV=None,gRV=None,
                    f_light=None, masses=None, alpha=ALPHA0):
    """KKO coherent conversion rate with full scalar/vector/dipole interference.

    Convention: first (outgoing-e_L-like) block pairs cR,gLS,gLV, second
    cL,gRS,gRV as in 2022 Eq.(41). Uses the KKO general Vn term as needed.
    Returns numeric rate but NEVER a physical compatibility certification.
    """
    if target not in TARGETS:
        raise ValueError('Use an explicit supported nuclear target')
    if not (math.isfinite(alpha) and alpha>0):
        raise ValueError('Invalid alpha_em')
    t=TARGETS[target]
    cL,cR=coefficient(cL),coefficient(cR)
    spL,snL=scalar_nucleon(gLS,f_light,masses)
    spR,snR=scalar_nucleon(gRS,f_light,masses)
    vpL,vnL=vector_nucleon(gLV)
    vpR,vnR=vector_nucleon(gRV)
    e=math.sqrt(4*math.pi*alpha)
    aL = -e/(16*math.pi**2)*cR*t.D + spL*t.Sp + snL*t.Sn + vpL*t.Vp + vnL*t.Vn
    aR = -e/(16*math.pi**2)*cL*t.D + spR*t.Sp + snR*t.Sn + vpR*t.Vp + vnR*t.Vn
    common=MMU**5/(HBAR*t.capture_per_s)
    cr=common*(abs(aL)**2+abs(aR)**2)
    if not math.isfinite(cr):
        raise ValueError('Conversion rate overflow')
    return {'target':target,'conversion_ratio':cr,
            'partial_norm_left':abs(aL)**2,'partial_norm_right':abs(aR)**2,
            'amplitude_left':(aL.real,aL.imag), 'amplitude_right':(aR.real,aR.imag),
            'rate_convention':'2022_EQ41_KKO_WITH_GENERALIZED_NEUTRON_VECTOR',
            'independent_physical_qualification':None,
            'Zee_UV_Wilson_source_verified':None, 'LFV_exclusion':None,
            'required_missing_checks':['model-specific Wilson mapping','CKM and quark scheme',
                  'threshold/RG corrections','nuclear uncertainties','higher-order materiality']}


def radiative_br(cL,cR,alpha=ALPHA0):
    """2022 Eq.(32), mu->e gamma dipole branching ratio in same convention."""
    cL,cR=coefficient(cL),coefficient(cR)
    width=alpha*MMU**5*(abs(cL)**2+abs(cR)**2)/(64*math.pi**4)
    return width/(HBAR/TAU_MU)


def dipole_ratio(target):
    """Analytic alpha-independent CR(mu A->e A)/BR(mu->e gamma)."""
    if target not in TARGETS:
        raise ValueError('Unsupported target')
    t=TARGETS[target]
    return math.pi*t.D*t.D/(TAU_MU*t.capture_per_s)
