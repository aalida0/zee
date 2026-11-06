#!/usr/bin/env python3
"""Compare only four original D12 cards to source-pinned public LFV terms."""
import argparse
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from module14.conditional_scan.workflow import load
from module14.scan import file_sha, encode
from module14.physics_adapters.lfv_reference import fixed_card_reference
from module3.core import vertices
from module4.amplitudes import fermion_component
from module4.couplings import quarks


def compare(source):
    path = Path('validation/module12/d12_benchmarks.json')
    result = []
    for ix, group in enumerate(load(path)['groups']):
        w = group['witnesses']['central']
        p = w['module2_input']['scalar']['record']['physical']
        ml = w['module2_input']['lepton_masses_GeV']
        D = np.array(w['yukawas']['D']['real'])+1j*np.array(w['yukawas']['D']['imag'])
        upstream, masses, alpha = fixed_card_reference(source, w)
        for channel, native in upstream.items():
            i,j = (int(k)-1 for k in channel.split('_'))
            refs = []
            for f,mass in masses.items():
                out = np.zeros(2, complex)
                for scalar,(C,mphi) in vertices(D,p,ml).items():
                    internal = C[2,2] if f=='tau' else quarks(mass,f,p)[scalar]
                    out += fermion_component((C[j,i],C[i,j].conjugate()),internal,mass,mphi,ml[i],alpha,
                              1 if f=='tau' else 3,-1 if f=='tau' else -1/3 if f=='bottom' else 2/3)[0]
                refs.append(out)
            refs = np.array(refs)
            residual = float(np.max(abs(native-refs)/abs(refs)))
            if residual > 1e-9:
                raise ValueError('Independent complex photon subset mismatch')
            result.append({'group':ix,'channel':channel,'max_relative_residual':residual,
                           'C_GeV_minus2': [[[float(z.real),float(z.imag)] for z in row] for row in native],
                           'matched_internal_masses_GeV':masses})
    return {'status':'REFERENCE_ONLY','subset_validation':'PASS','two_loop_full_Zee':'UNKNOWN',
            'double_counting':'Already present in Module4; no amplitude added',
            'source_commit':'b5035cd58d2a7e4a91e9790d045df062b97adffe',
            'input_file_sha256':file_sha(path),'comparisons':result,
            'source_thdm_sha256':file_sha(Path(source)/'thdm.py')}

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--output',required=True)
    a=p.parse_args()
    with open(a.output,'x') as f:f.write(encode(compare(a.source))+'\n')
