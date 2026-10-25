"""Zee Type-II charged-scalar B->Xs gamma: LO C7,C8 *matching only*.

Source equations: SuperIso v3.4 arXiv:0808.3144 Appendix C.1.2
Eqs.(47)-(49); Florentino/Romao/Silva EPJC81(2021)1148
Appendix B.3 (X,Y rotations) and C (Wilson coefficient decomposition).
No RGE, NLO/NNLO, branching ratio, experimental exclusion, or viable point.
"""
import argparse
import json
import math
from pathlib import Path

BASIS = 'ZeeTypeII_FLAVOUR_XY_SuperIso_LO'
STATUS = 'LO_MATCHING_ONLY_NOT_BR_OR_EXCLUSION'

def _positive_finite(v, name):
    if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v) or v<=0:
        raise ValueError(f'{name}: expected finite positive real number')
    return float(v)

def _finite(v, name):
    if isinstance(v,bool) or not isinstance(v,(float,int)) or not math.isfinite(v):
        raise ValueError(f'{name}: expected finite real number')
    return float(v)

# Taylor series about x=1 derived independently with symbolic series to O((x-1)^7).
# This avoids catastrophic cancellation in direct rational/logarithmic expressions.
_SERIES = {
 'F7_1':(-5/48,-13/240,1/48,-17/1680,19/3360,-1/288,23/10080),
 'F8_1':(-1/16,-1/40,1/80,-1/140,1/224,-1/336,1/480),
 'F7_2':(-7/36,-5/72,1/30,-7/360,4/315,-1/112,5/756),
 'F8_2':(-1/6,-1/24,1/40,-1/60,1/84,-1/112,1/144),
}

def loop_functions(x):
    x = _positive_finite(x,'x=mt^2/mH^2')
    t=x-1
    if abs(t)<0.02:
        return {k:math.fsum(c*t**i for i,c in enumerate(coeffs))
                for k,coeffs in _SERIES.items()}
    lx=math.log(x);a=x-1
    a2=a*a;a3=a2*a;a4=a2*a2
    values={
        'F7_1':x*(7-5*x-8*x*x)/(24*a3)+x*x*(3*x-2)*lx/(4*a4),
        'F8_1':x*(2+5*x-x*x)/(8*a3)-3*x*x*lx/(4*a4),
        'F7_2':x*(3-5*x)/(12*a2)+x*(3*x-2)*lx/(6*a3),
        'F8_2':x*(3-x)/(4*a2)-x*lx/(2*a3),
    }
    if not all(math.isfinite(v) for v in values.values()):
        raise ValueError('Non-finite loop function')
    return values


def compute(mH1_GeV,mH2_GeV,beta_rad,gamma_rad,mt_MSbar_GeV,
            matching_scale_GeV):
    masses=(_positive_finite(mH1_GeV,'mH1_GeV'),
            _positive_finite(mH2_GeV,'mH2_GeV'))
    beta=_finite(beta_rad,'beta_rad');gamma=_finite(gamma_rad,'gamma_rad')
    mt=_positive_finite(mt_MSbar_GeV,'mt_MSbar_GeV')
    mu=_positive_finite(matching_scale_GeV,'matching_scale_GeV')
    if not (0 < beta < math.pi/2):
        raise ValueError('Require 0 < beta < pi/2, beta is an ANGLE not tan(beta)')
    tanb=math.tan(beta)
    if not math.isfinite(tanb) or tanb<=0:
        raise ValueError('Invalid tan(beta)')
    # Independent charged mass eigenstates, doublet admixture cos(gamma), -sin(gamma).
    # X=(tanb*cos(gamma),-tanb*sin(gamma)),
    # Y=(cotb*cos(gamma),-cotb*sin(gamma)); XY*=|admixture|^2.
    weights=(math.cos(gamma)**2,math.sin(gamma)**2)
    entries=[]
    for a,(mass,weight) in enumerate(zip(masses,weights),start=1):
        y=(mt/mass)**2
        f=loop_functions(y)
        yy=weight/tanb**2
        xy=weight
        d7_YY=yy*f['F7_1']/3
        d8_YY=yy*f['F8_1']/3
        d7_XY=xy*f['F7_2']
        d8_XY=xy*f['F8_2']
        entries.append({'scalar':f'H{a}_charged','mass_GeV':mass,
                        'x_mt2_over_mH2':y,'doublet_fraction':weight,
                        'YY_coupling_squared':yy,'XY_conjugate_coupling':xy,
                        'delta_C7_YY':d7_YY,'delta_C7_XY':d7_XY,
                        'delta_C8_YY':d8_YY,'delta_C8_XY':d8_XY,
                        'delta_C7':math.fsum((d7_YY,d7_XY)),
                        'delta_C8':math.fsum((d8_YY,d8_XY))})
    c7=math.fsum(r['delta_C7'] for r in entries)
    c8=math.fsum(r['delta_C8'] for r in entries)
    return {'schema_version':'1.0.0','status':STATUS,'basis':BASIS,
            'input':{'mH1_GeV':masses[0],'mH2_GeV':masses[1],
                     'beta_rad':beta,'gamma_rad':gamma,
                     'mt_MSbar_GeV':mt,'matching_scale_GeV':mu,
                     'top_mass_input_definition':'USER_SUPPLIED_MSbar_TOP_MASS_AT_MATCHING_SCALE_NO_RUNNING'},
            'charged_scalars':entries,'delta_C7_LO_at_matching_scale':c7,
            'delta_C8_LO_at_matching_scale':c8,
            'physics_scope':'Charged scalar LO matching contributions only, NOT SM total coefficient',
            'experimental_comparison':'NOT_EVALUATED',
            'global_zee_acceptance':None,
            'limitations':[
                'No C7/C8 NLO matching, QCD RGE, NNLO calculation or B->Xs gamma branching fraction.',
                'Common supplied matching scale used for both charged states; no multiscale threshold treatment.',
                'The user must independently provide a consistent renormalized MSbar mt(mu); no QCD running occurs.',
                'No primed coefficients, power corrections, non-SM quark flavour couplings or observable comparison.',
                'Type-II quark Yukawas and CP-conserving real charged mixing assumed, as in frozen ZeeTypeII.'
            ]}

def _unique(pairs):
    result={}
    for k,v in pairs:
        if k in result: raise ValueError('Duplicate JSON field: '+k)
        result[k]=v
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',required=True,help='JSON with six explicit physical fields')
    ap.add_argument('--output',required=True)
    args=ap.parse_args()
    raw=json.loads(Path(args.input).read_text(),object_pairs_hook=_unique,
                   parse_constant=lambda val: (_ for _ in ()).throw(ValueError('Nonfinite JSON '+val)))
    if not isinstance(raw,dict) or set(raw)!={'mH1_GeV','mH2_GeV','beta_rad','gamma_rad',
                                               'mt_MSbar_GeV','matching_scale_GeV'}:
        raise ValueError('Exactly six required physical fields; no implicit defaults')
    result=compute(**raw)
    dest=Path(args.output);dest.parent.mkdir(parents=True,exist_ok=True)
    tmp=dest.with_name(dest.name+'.tmp')
    tmp.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    tmp.replace(dest)
    print(STATUS)

if __name__=='__main__':main()
