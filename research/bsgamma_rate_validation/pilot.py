"""Bounded public-backend pilot; no production physics module is modified."""
import hashlib
import importlib.metadata as metadata
import json
import math
import os
from pathlib import Path
import sys

os.environ.setdefault('MPLCONFIGDIR', '/tmp/bsgamma-mpl')
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'scripts'))
from zee_module5_bmu_nlo import matching
import flavio
import eos
from wilson import wcxf

OBS = 'BR(B->Xsgamma)'
EOS_OBS = 'B->X_sgamma::BR(E_min)@NLO'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + '\n')


def vector(mass, tanbeta, card, flip=False, order='LO+NLO'):
    if (card['mu0_GeV'] != 160 or
            not all(math.isfinite(card[k]) and card[k] > 0
                    for k in ('mt_MSbar_GeV', 'alpha_s_mu0'))):
        raise ValueError('This pilot requires positive matching inputs at 160 GeV')
    if (not all(math.isfinite(x) and x > 0 for x in (mass, tanbeta))
            or abs((card['mt_MSbar_GeV'] / mass)**2 - 1) < 1e-5):
        raise ValueError('Positive finite inputs away from the uncertified x=1 region required')
    if order not in ('LO', 'LO+NLO'):
        raise ValueError('Unknown matching order')
    raw = matching(mass, tanbeta, card['mt_MSbar_GeV'], card['mu0_GeV'], flip)
    a = card['alpha_s_mu0'] / (4 * math.pi) if order == 'LO+NLO' else 0
    return raw, {'C4': a * raw['C4_NLO_raw'],
                 'C7': raw['C7_LO'] + a * raw['C7_NLO_raw'],
                 'C8': raw['C8_LO'] + a * raw['C8_NLO_raw']}


def coherent(v1, v2, gamma):
    if not math.isfinite(gamma):
        raise ValueError('Finite gamma required')
    return {k: math.cos(gamma)**2 * v1[k] + math.sin(gamma)**2 * v2[k] for k in v1}


def wc_object(v):
    # The public flavio basis has no C4_bs: deliberately only supported dipoles.
    if set(v) - {'C7', 'C8'} or not all(math.isfinite(x) for x in v.values()):
        raise ValueError('Only finite ordinary NP dipoles accepted; C4 cannot be silently dropped')
    w = flavio.WilsonCoefficients()
    w.set_initial({k + '_bs': x for k, x in v.items()}, 160, eft='WET', basis='flavio')
    return w


def rate(v, par):
    return flavio.physics.bdecays.bxgamma.BRBXgamma(wc_object(v), par, 's', 1.6)


def eos_rate(overrides=None, cut=1.6, model='WET'):
    p = eos.Parameters.Defaults()
    for k, v in (overrides or {}).items():
        p[k].set(v)
    o = eos.Observable.make(EOS_OBS, p, eos.Kinematics(E_min=cut), eos.Options(model=model))
    return o.evaluate()


def run():
    card = json.loads((HERE / 'input_card.json').read_text())
    par = flavio.default_parameters.get_central_all()
    # Parameter defaults are locked by release and authenticated as a whole.
    parhash = hashlib.sha256(json.dumps(par, sort_keys=True).encode()).hexdigest()
    if parhash != card['flavio_default_parameters_sha256']:
        raise RuntimeError('Parameter defaults changed')
    records = []
    low_scale = flavio.config['renormalization scale']['bxgamma']
    def record(label, full, raw=None, **fields):
        dip = {k: full[k] for k in ('C7', 'C8')}
        w = wc_object(dip)
        low = flavio.physics.bdecays.wilsoncoefficients.wctot_dict(w, 'bsee', low_scale, par)
        r = dict(label=label, status='DIAGNOSTIC_ONLY', ordinary_NP_mu0=full,
                 injected_NP_mu0=dip, omitted_C4_mu0=full.get('C4', 0),
                 BR=rate(dip, par), raw_matching=raw,
                 total_low_scale={k: float(complex(low[k]).real) for k in
                                  ['C4_bs','C7_bs','C8_bs','C7eff_bs','C8eff_bs']}, **fields)
        records.append(r)
        return r
    sm = record('zero_NP', dict(C4=0., C7=0., C8=0.))
    one = {}
    for order in ('LO', 'LO+NLO'):
        for mass, tb, flip in [(550,2,False),(550,5.3,False),(550,50,False),
                              (900,2,False),(900,5.3,False),(900,50,False),
                              (100000,5.3,False),(550,5.3,True)]:
            raw, v = vector(mass,tb,card,flip,order)
            label = f'{order}_M{mass}_tb{tb}_flip{flip}'
            one[order,mass,tb,flip] = record(label,v,raw,mass_GeV=mass,tanbeta=tb,
                                            opposite_coupling_sign=flip,matching_order=order)
    v1=one['LO+NLO',550,5.3,False]['ordinary_NP_mu0']
    v2=one['LO+NLO',900,5.3,False]['ordinary_NP_mu0']
    example=record('two_state_example',coherent(v1,v2,1.09),gamma=1.09)
    identities={}
    for label,a,b,g,target in [
        ('gamma_zero',v1,v2,0,one['LO+NLO',550,5.3,False]['BR']),
        ('gamma_half_pi',v1,v2,math.pi/2,one['LO+NLO',900,5.3,False]['BR']),
        ('equal_mass',v1,v1,1.09,one['LO+NLO',550,5.3,False]['BR']),
        ('interchange',v2,v1,math.pi/2-1.09,example['BR'])]:
        identities[label]=record(label,coherent(a,b,g))['BR']-target
    probes={}
    for k in ('C7','C8'):
        rs={}
        for s in (-1,1):
            v=dict(C4=0.,C7=0.,C8=0.);v[k]=s*0.01
            rs[s]=record(f'{k}_{s:+d}',v)['BR']
        probes[k]={'step':.01,'odd_half_difference':(rs[1]-rs[-1])/2,
                   'even_half_sum_minus_SM':(rs[1]+rs[-1])/2-sm['BR']}
    eos_probes={}
    e0=eos_rate()
    for k in ('b->s::c4','b->s::Re{c7}','b->s::c8'):
        p=eos.Parameters.Defaults(); c=p[k].evaluate()
        rp,rm=eos_rate({k:c+.01}),eos_rate({k:c-.01})
        eos_probes[k]={'step':.01,'BR_plus':rp,'BR_minus':rm,
                       'even_half_sum_minus_baseline':(rp+rm)/2-e0}
    import numpy as np
    np.random.seed(7219)
    uncertainty=float(flavio.sm_uncertainty(OBS,N=64))
    eph=hashlib.sha256(json.dumps({p.name():p.evaluate() for p in eos.Parameters.Defaults()},sort_keys=True).encode()).hexdigest()
    result={
        'status':'DIAGNOSTIC_ONLY','publishability':'UNKNOWN','exclusion_readiness_2026':'UNKNOWN',
        'full_Zee_rate_validated':False,'global_zee_acceptance':None,
        'versions':{n:metadata.version(n) for n in ('flavio','wilson','eoshep','particle','numpy','scipy','mpmath')},
        'input_card_sha256':digest(HERE/'input_card.json'),
        'matching_implementation_sha256':digest(ROOT/'scripts/zee_module5_bmu_nlo.py'),
        'flavio_default_parameters_sha256':parhash,'eos_default_parameters_sha256':eph,
        'flavio_low_scale_GeV':low_scale,'records':records,'identities_BR_residual':identities,
        'signed_high_scale_dipole_probes':probes,
        'coherent_minus_weighted_BR':example['BR']-(math.cos(1.09)**2*one['LO+NLO',550,5.3,False]['BR']+math.sin(1.09)**2*one['LO+NLO',900,5.3,False]['BR']),
        'flavio_public_C4_supported':'C4_bs' in wcxf.Basis['WET','flavio'].all_wcs,
        'wilson_EOS_translators':[list(x) for x in wcxf.Translator.instances if 'EOS' in x],
        'eos':{'SM':eos_rate(model='SM'),'WET_default_total_coefficients':e0,
               'low_scale_total_coefficient_probes':eos_probes,
               'upstream_regression':[{'cut_GeV':c,'BR':eos_rate(card['eos_regression_overrides'],c),
                                       'reference':r} for c,r in [(1.6,3.13699e-4),(1.8,3.09211e-4),(2.,3.00017e-4)]]},
        'uncertainty_interface_probe':{'SM_MC_sigma':uncertainty,'N':64,'seed':7219,
                                       'NP_covariance_status':'NOT_EVALUATED'},
        'legacy_comparison':'NOT_EVALUATED: inputs, order and normalization not matched',
    }
    write_json(HERE/'results.json',result)
    print(json.dumps({'SM':sm['BR'],'example_dipole_only':example['BR'],'identities':identities,
                      'EOS_regression':result['eos']['upstream_regression']}))

if __name__=='__main__':
    run()
