#!/usr/bin/env python3
"""Fail-closed, strictly conditional LFV source-rate headroom check.

For each process, if the omitted *full integrated amplitude norm* obeys
  ||A_missing|| <= kappa ||A_source||,
then the triangle inequality implies
  BR_full <= (1+kappa)**2 * BR_source.
This is a mathematical implication, NOT a physics-derived kappa bound.
Source normalization, quark/nuclear schemes and missing topology effects
must be independently controlled before it can become a physical constraint.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

LIMITS_90CL={
    'muegamma':1.5e-13,
    'mu3e':1e-12,
    'muAu':7e-13,
}
SOURCE={
    'D7_NO':{'muegamma':1.6649192127405279e-19,
             'mu3e':1.08828659e-21,
             'muAu':6.98927565e-22},
    'D7_IO':{'muegamma':1.1577998043523288e-18,
             'mu3e':7.52936205e-21,
             'muAu':4.54971780e-21},
    'F13_NO':{'muegamma':4.298922382583583e-20,
              'mu3e':4.54615814e-22,
              'muAu':6.34683551e-21},
    'F13_IO':{'muegamma':1.4266820660184817e-19,
              'mu3e':1.45713157e-21,
              'muAu':1.92203807e-20}
}

def evaluate(kappa:float=300.0,source=SOURCE,limits=LIMITS_90CL)->dict:
    if not math.isfinite(kappa) or kappa<0:
        raise ValueError('kappa must be nonnegative finite')
    if set(limits)!={'muegamma','mu3e','muAu'}:
        raise ValueError('Source limit scope changed')
    out={}
    for card,obs in source.items():
        if set(obs)!=set(limits):raise ValueError('Incomplete source-process coverage')
        out[card]={}
        for process,rate in obs.items():
            bound=limits[process]
            if not math.isfinite(rate) or rate<=0 or not math.isfinite(bound) or bound<=0:
                raise ValueError('Rates/limits must be finite positive')
            maximum=math.sqrt(bound/rate)-1
            upper=(1+kappa)**2*rate
            out[card][process]={
                'source_one_loop_diagnostic_rate':rate,
                'experimental_90CL_upper_limit':bound,
                'max_assumed_missing_amplitude_over_source_amplitude':maximum,
                'worst_case_rate_given_assumption':upper,
                'conditional_sufficient_pass':upper<bound,
                'physical_pass':None,
            }
    return {
        'status':'CONDITIONAL_NORM_ENVELOPE_ONLY_NOT_PHYSICAL_LFV',
        'kappa_assumption':kappa,
        'assumption':'For each complete process, ||A_missing||_Hilbert <= kappa ||A_source||_Hilbert in the same physical phase-space and nuclear scheme.',
        'critical_scope':'Source approximations and experimental normalization held fixed; this script does NOT derive the kappa bound or provide a physical acceptance certificate.',
        'source_approximation':'native SARAH 4.15.4 one-loop e gamma/e e e; original light-uds nuclear conversion scalar pn repaired; finite-q2 and scalar scheme unqualified',
        'experimental_context':['MEG II 2025 1.5e-13','SINDRUM mu3e 1e-12','SINDRUM II Au 7e-13'],
        'all_conditional_sufficient_pass':all(p['conditional_sufficient_pass'] for row in out.values() for p in row.values()),
        'physical_lfv':'UNKNOWN',
        'global_acceptance':None,
        'cards':out,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--kappa',type=float,default=300.0)
    p.add_argument('--output',type=Path,default=Path('CONDITIONAL_FOUR_CARD_ENVELOPE.json'))
    args=p.parse_args()
    result=evaluate(args.kappa)
    if args.output.exists():raise FileExistsError(f'Refusing overwrite {args.output}')
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],'KAPPA',args.kappa,
          'ALL_CONDITIONAL_SUFFICIENT_PASS',result['all_conditional_sufficient_pass'])
    print('PHYSICAL_LFV UNKNOWN; not a certified Zee model exclusion/acceptance')

if __name__=='__main__':main()
