"""Reproducible synthetic NO/IO physical-mass witnesses, not a data likelihood."""
import copy
import json
from pathlib import Path
import numpy as np
from module2.interface import canonical_hash, encode

ROOT = Path(__file__).resolve().parents[1]
ML = np.array([.00051099895,.1056583755,1.77686])


def target(ordering):
    # Explicit PDG-parameterized complex matrix; chosen values are witnesses.
    s12,s13,s23 = np.sqrt([.307,.02195,.561])
    c12,c13,c23 = np.sqrt(1-np.array([.307,.02195,.561]))
    phase = np.exp(4.2j)
    u = np.array([[c12*c13,s12*c13,s13/phase],
                  [-s12*c23-c12*s23*s13*phase,c12*c23-s12*s23*s13*phase,s23*c13],
                  [s12*s23-c12*c23*s13*phase,-c12*s23-s12*c23*s13*phase,c23*c13]])
    u = u@np.diag([1,np.exp(.35j),np.exp(1.05j)])
    m0, ds = .001, 7.49e-5
    m = np.sqrt([m0*m0,m0*m0+ds,m0*m0+2.534e-3]) if ordering=='NO' else np.sqrt([m0*m0+2.510e-3-ds,m0*m0+2.510e-3,m0*m0])
    return u.conj()@np.diag(m)@u.conj().T


def example(ordering='NO', spectrum=0):
    scalar = json.loads((ROOT/'module1/example.json').read_text())
    if spectrum == 1:
        scalar['physical'].update(mh2=420.,ma=450.,mH1=375.,mH2=925.,gamma=.71,alpha=.93,beta=1.1)
    elif spectrum == 2:
        scalar['physical'].update(mh2=850.,ma=810.,mH1=500.,mH2=1100.,gamma=-.38,alpha=.73,beta=.8)
    elif spectrum != 0:
        raise ValueError('Unknown witness spectrum')
    identifier = 'module3_'+ordering+'_spectrum'+str(spectrum)
    scalar['benchmark_id'] = identifier
    inp = {'schema_version':'1.0.0','benchmark_id':identifier,'mode':'inverse','ordering':ordering,
           'scalar':{'kind':'module1_input','record':scalar,'sha256':canonical_hash(scalar)},
           'lepton_masses_GeV':ML.tolist(),'target_eV':encode(target(ordering)),
           'null_cone':{'t':{'real':.25,'imag':.1},'scale':.002,'root':spectrum%2,'chart':[0,1,2],'phase_rad':.43},
           'homogeneous_coefficients':{'real':[1e-7,-2e-7,3e-7,1e-7],'imag':[2e-7,0,-1e-7,3e-7]}}
    return {'schema_version':'1.0.0','benchmark_id':identifier,'module2_input':inp,
            'constants':{'alpha_em':1/137.035999084,'GF_GeV_minus2':1.1663787e-5,
                         'total_lepton_widths_GeV':[6.582119569e-25/2.1969811e-6,6.582119569e-25/2.903e-13],
                         'source':{'version':'Explicit illustrative normalization snapshot (not a likelihood)',
                                   'url':'https://pdg.lbl.gov/2024/reviews/rpp2024-rev-phys-constants.pdf',
                                   'selection':'alpha(0), GF, hbar; mu and tau lifetime normalizations supplied explicitly; no LFV limits'}},
            'numerics':{'tree_quadrature_order':24,'tree_relative_tolerance':2e-5}}
