"""Full-vector EOS native-evolution experiment. Physical accuracy remains uncertified."""
import ctypes as ct
import json
import math
from pathlib import Path
import numpy as np
import ckmutil.ckm
from wilson import wcxf
from wilson.translate.wet import get_parameters
from pilot import HERE, ROOT, eos, eos_rate, matching, digest, write_json

KEYS=['b->s::c1','b->s::c2','b->s::c3','b->s::c4','b->s::c5','b->s::c6','b->s::Re{c7}','b->s::c8']
P=ct.POINTER(ct.c_double)


def direct_jms(c4,c7,c8,scale=160,parameters=None):
    """Analytic operator expansion; see BRIDGE.md. No numerical inversion."""
    if not all(math.isfinite(x) for x in (c4,c7,c8)):
        raise ValueError('Finite real coefficients required')
    p=get_parameters(scale,f=5,input_parameters=parameters)
    v=ckmutil.ckm.ckm_tree(p['Vus'],p['Vub'],p['Vcb'],p['gamma'])
    k=4*p['GF']/math.sqrt(2)*v[2,2]*v[2,1].conjugate()
    d={f'V8udLL_{j}{j}23':k*c4 for j in (1,2)}
    d.update({f'V8duLR_23{j}{j}':k*c4 for j in (1,2)})
    d.update({f'V8ddLR_23{j}{j}':k*c4 for j in (1,2,3)})
    d.update({'VddLL_1123':-k*c4/6,'VddLL_1231':k.conjugate()*c4/2,
              'VddLL_2223':k*c4/3,'VddLL_2333':k*c4/3,
              'dgamma_23':k*math.sqrt(4*math.pi*p['alpha_e'])*p['m_b']/(16*math.pi**2)*c7,
              'dG_23':k*math.sqrt(4*math.pi*p['alpha_s'])*p['m_b']/(16*math.pi**2)*c8})
    w=wcxf.WC('WET','JMS',scale,wcxf.WC.dict2values({x:y for x,y in d.items() if y!=0}))
    w.validate()
    return w,k


class Native:
    def __init__(self):
        if eos.__version__ != '1.0.21':
            raise RuntimeError('This native wrapper requires the pinned EOS 1.0.21 ABI')
        self.lib=ct.CDLL(str(HERE/'local/eos_evolve_probe.so'))
        self.lib.zee_evolve.argtypes=[P,P,P,ct.c_double,ct.c_double,P]
        self.lib.zee_sm.argtypes=[ct.c_double,P];self.lib.zee_sm.restype=ct.c_int
        self.lib.zee_rate_diagnostics.argtypes=[ct.POINTER(ct.c_char_p),P,ct.c_uint,P]
        self.lib.zee_rate_diagnostics.restype=ct.c_int
        self.low=eos.Parameters.Defaults()['sb::mu'].evaluate()
        self.sm,self.asb,_=self.sm_at(self.low)
        _,self.as0,self.mt=self.sm_at(160)

    def sm_at(self,mu):
        o=np.zeros(18)
        if self.lib.zee_sm(mu,o.ctypes.data_as(P)): raise RuntimeError('EOS SM call failed')
        if max(abs(o[8:16]))>1e-12: raise ValueError('Complex SM coefficients unsupported')
        return o[:8],o[16],o[17]

    def evolve(self,a,b,c,as0=None,asb=None):
        if any(np.shape(x)!=(15,) or not np.all(np.isfinite(x)) for x in (a,b,c)):
            raise ValueError('Three finite real 15-component perturbative vectors required')
        out=np.zeros(30)
        self.lib.zee_evolve(*(np.ascontiguousarray(x,dtype=float).ctypes.data_as(P) for x in (a,b,c)),
                            self.as0 if as0 is None else as0,self.asb if asb is None else asb,out.ctypes.data_as(P))
        if max(abs(out[15:]))>1e-10: raise ValueError('Unexpected imaginary evolution')
        return out[:15]

    def np_coefficients(self,raw):
        if set(raw)!={'C7_LO','C8_LO','C4_NLO_raw','C7_NLO_raw','C8_NLO_raw'} or not all(math.isfinite(x) for x in raw.values()):
            raise ValueError('Complete raw ordinary matching required')
        a=np.zeros(15);b=a.copy();c=a.copy()
        b[3]=raw['C4_NLO_raw'];b[11]=raw['C7_LO'];b[12]=raw['C8_LO']
        c[11]=raw['C7_NLO_raw'];c[12]=raw['C8_NLO_raw']
        def physical(t):
            r=self.evolve(a,b,c,self.as0*t,self.asb*t)
            if max(abs(r[6:11]))>1e-12:
                raise ValueError('Additional EOS operators generated outside the rate interface')
            return np.r_[r[:6],r[11:13]/(self.asb*t/(4*math.pi))]
        r1,r2=physical(1),physical(2)
        # At fixed eta the library output is exactly a degree-two series in a_s.
        # NP four-quarks start at a_s: discard their a_s^2 terms; retain NLO dipoles.
        result=r1.copy();result[:6]=2*r1[:6]-.5*r2[:6]
        return result

    def br(self,raw,cut=1.6):
        np_low=self.np_coefficients(raw)
        return eos_rate(dict(zip(KEYS,self.sm+np_low)),cut),np_low

    def diagnostics(self,overrides):
        k=(ct.c_char_p*len(overrides))(*(s.encode() for s in overrides))
        v=np.array(list(overrides.values()),float);o=np.zeros(2)
        if self.lib.zee_rate_diagnostics(k,v.ctypes.data_as(P),len(v),o.ctypes.data_as(P)):
            raise RuntimeError('EOS diagnostic call failed')
        return o.tolist()


def run():
    n=Native(); zero={k:0. for k in ('C7_LO','C8_LO','C4_NLO_raw','C7_NLO_raw','C8_NLO_raw')}
    rows=[]
    def record(label,raw):
        br,low=n.br(raw)
        no4=dict(raw,C4_NLO_raw=0.)
        br0,_=n.br(no4)
        br4minus,_=n.br(dict(raw,C4_NLO_raw=-raw['C4_NLO_raw']))
        lo7,lo8=raw['C7_LO'],raw['C8_LO']
        lo={**zero,'C7_LO':lo7,'C8_LO':lo8}
        brlo,_=n.br(lo)
        neg={k:-v for k,v in raw.items()};brneg,_=n.br(neg)
        sm,_=n.br(zero)
        x={'label':label,'status':'DIAGNOSTIC_ONLY','raw_matching':raw,'NP_low_C1_to_C8':low.tolist(),
           'BR_native_prescription':br,'C4_BR_difference':br-br0,
           'C4_odd_half_difference':(br-br4minus)/2,
           'C4_even_half_sum_minus_zero':(br+br4minus)/2-br0,
           'NLO_matching_increment':br-brlo,
           'even_NP_rate_piece':(br+brneg)/2-sm}
        rows.append(x);return x
    record('zero_NP',zero)
    one={}
    for m,tb,flip in [(550,5.3,False),(900,5.3,False),(550,2,False),(900,50,False),(100000,5.3,False),(550,5.3,True)]:
        raw=matching(m,tb,n.mt,160,flip);one[m,tb,flip]=raw
        record(f'M{m}_tb{tb}_flip{flip}',raw)
    a=one[550,5.3,False];b=one[900,5.3,False]
    def mix(x,y,g):return {k:math.cos(g)**2*x[k]+math.sin(g)**2*y[k] for k in x}
    ex=record('two_state',mix(a,b,1.09));ids={}
    for label,x,y,g,ref in [('gamma_zero',a,b,0,n.br(a)[0]),('gamma_half_pi',a,b,math.pi/2,n.br(b)[0]),
                           ('equal_mass',a,a,1.09,n.br(a)[0]),('interchange',b,a,math.pi/2-1.09,ex['BR_native_prescription'])]:
        ids[label]=record(label,mix(x,y,g))['BR_native_prescription']-ref
    phases={}
    for g in (1e-8,1.27):
        w,k=direct_jms(.01,-.03,-.04,parameters={'gamma':g})
        phases[str(g)]={'kappa':[k.real,k.imag],
                        'JMS':{x:[complex(y).real,complex(y).imag] for x,y in w.dict.items()},
                        'EOS_translation':{x:[complex(y).real,complex(y).imag] for x,y in
                                           w.translate('EOS',parameters={'gamma':g}).dict.items() if abs(y)>1e-12}}
    card=json.loads((HERE/'input_card.json').read_text())
    r={'conclusion':'RATE_BRIDGE_BLOCKED','status':'DIAGNOSTIC_ONLY','full_vector_physical_accuracy':'NOT_EVALUATED',
       'publishability':'UNKNOWN','exclusion_readiness_2026':'UNKNOWN','mu0_GeV':160,'mu_b_GeV':n.low,
       'mt_MSbar_mu0_GeV':n.mt,'alpha_s_mu0':n.as0,'alpha_s_mu_b':n.asb,'SM_low_C1_to_C8':n.sm.tolist(),
       'SM_direct_rate':eos_rate(model='SM'),'records':rows,'identities':ids,
       'coherent_minus_weighted_BR':ex['BR_native_prescription']-(math.cos(1.09)**2*n.br(a)[0]+math.sin(1.09)**2*n.br(b)[0]),
       'JMS_translation_probes':phases,'EOS_upstream_CMM_labelled_ratio_diagnostics':n.diagnostics(card['eos_regression_overrides']),
       'physical_one_state_matched_reference':'NOT_EVALUATED: no matched independent reference established',
       'global_zee_acceptance':None,
       'evolution_accuracy':'Native EOS gamma0/gamma1/gamma2 with inverse-gs dipoles; retained NP ordinary NLO projection',
       'observable_accuracy':'EOS NLO-labelled prescription retains additional higher-order terms; uniform NLO physical accuracy NOT_EVALUATED',
       'omitted_effects_status':{k:'NOT_EVALUATED' for k in ['NP_QED','finite_ms_NP','primed_NP','light_quark_NP','enhanced_down_Yukawas','theory_covariance','updated_2026_SM']},
       'CMM_physical_reference':{'source':'https://arxiv.org/abs/hep-ph/9612313v3',
                                 'Eq48':{'delta':.99,'R_quark':.00312,'EOS_cut_supported':False},
                                 'Eq49':{'delta':.29**2,'R_quark':.00286,'matched_prescription':False}},
       'native_build':json.loads((HERE/'local/native_build.json').read_text())}
    write_json(HERE/'bridge_results.json',r)
    print(json.dumps({k:r[k] for k in ['conclusion','mt_MSbar_mu0_GeV','alpha_s_mu0','SM_direct_rate','identities']}))
    print([(x['label'],x['BR_native_prescription'],x['C4_BR_difference']) for x in rows[:8]])

if __name__=='__main__':run()
