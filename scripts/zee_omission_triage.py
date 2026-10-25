#!/usr/bin/env python3
"""Conditional worst-case dipole-amplitude sensitivity; NOT a Zee exclusion.

For complex two-chirality amplitude C and assumed ||Delta||_2<=b,
the sharp possible norm range is [max(0,||C||-b), ||C||+b].
The assumed b is NOT a physical bound on missing Zee amplitudes.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

BASE_COMMIT = '231e58fc35a7ea26d6f04f4735f8e9a197f1b6d3'
DEFAULT_FRACTIONS = (0.05, 0.1, 0.25, 0.5, 1.0)
CHANNELS = ('mu_to_e_gamma', 'tau_to_mu_gamma', 'tau_to_e_gamma')


def finite_float(x, name):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        raise ValueError(f'{name}: finite real number required')
    return float(x)


def complex_value(z, name):
    if not isinstance(z, dict) or set(z) != {'real', 'imag'}:
        raise ValueError(f'{name}: expected complex {{real,imag}}')
    return complex(finite_float(z['real'], name+'.real'),
                   finite_float(z['imag'], name+'.imag'))


def vector_norm(z):
    return math.hypot(abs(z[0]), abs(z[1]))


def summed_components(rows):
    return tuple(complex(math.fsum(z[k].real for z in rows),
                         math.fsum(z[k].imag for z in rows)) for k in ('C_L','C_R'))


def sharp_envelope(c, budget, partial_br):
    """Sharp norm envelope and fixed-channel BR rescaling only."""
    n = vector_norm(c)
    budget = finite_float(budget, 'budget')
    if budget < 0:
        raise ValueError('Nonnegative missing-amplitude budget required')
    br = finite_float(partial_br, 'partial_BR')
    if br < 0:
        raise ValueError('Negative partial_BR')
    lo, hi = max(0., n-budget), n+budget
    if not math.isfinite(hi):
        raise ValueError('Amplitude overflow')
    if n == 0:
        return dict(norm_min=lo, norm_max=hi, partial_BR_min=None,
                    partial_BR_max=None, BR_undefined_reason='zero included norm')
    br_lo = br * (lo/n)**2
    br_hi = br * (hi/n)**2
    if not math.isfinite(br_lo) or not math.isfinite(br_hi):
        raise ValueError('BR rescaling overflow')
    return dict(norm_min=lo, norm_max=hi, partial_BR_min=br_lo,
                partial_BR_max=br_hi, BR_undefined_reason=None)


def examine_channel(ch, fractions):
    if not isinstance(ch, dict) or ch.get('rate_scope') != 'INCLUDED_TOPOLOGIES_ONLY' or ch.get('physical_status') != 'PREDICTION_INCOMPLETE' or ch.get('experimental_comparison') != 'NOT_EVALUATED':
        raise ValueError('Only explicitly incomplete Module4 channels accepted')
    ledger = ch.get('ledger')
    if not isinstance(ledger, dict) or not ledger:
        raise ValueError('Nonempty validated ledger required')
    rows = []
    for name, r in ledger.items():
        if (not isinstance(r, dict) or r.get('validation_status') != 'VALIDATION_PASS'
                or r.get('coherent_inclusion', True) is False):
            raise ValueError(f'Unvalidated/incoherent ledger row: {name}')
        rows.append({'C_L': complex_value(r['C_L'], name+'.C_L'),
                     'C_R': complex_value(r['C_R'], name+'.C_R')})
    c = (complex_value(ch['C_L'], 'channel.C_L'), complex_value(ch['C_R'], 'channel.C_R'))
    reproduced = summed_components(rows)
    scale = math.fsum(vector_norm((r['C_L'], r['C_R'])) for r in rows)
    if any(abs(c[i]-reproduced[i]) > 1e-10*max(scale, 1e-300) for i in (0, 1)):
        raise ValueError('Channel C does not match coherent ledger sum')
    candidates = ch.get('two_loop_candidates')
    if not isinstance(candidates, dict):
        raise ValueError('Excluded two-loop candidate ledger required')
    for name, r in candidates.items():
        if not isinstance(r, dict) or r.get('coherent_inclusion') is not False:
            raise ValueError('Candidate incorrectly included in coherent sum: '+name)
    omission = ch.get('omitted_topologies')
    if not isinstance(omission, dict) or 'W_gamma' not in omission or omission['W_gamma'].get('status') != 'UNKNOWN':
        raise ValueError('W_gamma omission must remain UNKNOWN')
    br = finite_float(ch['partial_BR'], 'partial_BR')
    if br < 0:
        raise ValueError('Negative partial_BR')
    max_piece = max(vector_norm((r['C_L'],r['C_R'])) for r in rows)
    n = vector_norm(c)
    entries = []
    for fraction in fractions:
        b = fraction*max_piece
        env = sharp_envelope(c,b,br)
        entries.append({'assumed_budget_fraction_of_largest_component':fraction,
                        'assumed_missing_amplitude_norm_bound_GeV_minus2':b,
                        'budget_over_included_norm':b/n if n>0 else None,
                        **env})
    return {'included_norm_GeV_minus2':n,
            'largest_included_component_norm_GeV_minus2':max_piece,
            'sum_included_component_norm_GeV_minus2':scale,
            'cancellation_index_sum_over_result':scale/n if n>0 else None,
            'included_partial_BR':br,
            'included_components':len(rows),
            'unmatched_candidate_components':len(candidates),
            'conditional_scenarios':entries,
            'physical_conclusion':'UNDETERMINED_MISSING_AMPLITUDES_NOT_BOUNDED',
            'experimental_comparison':'NOT_EVALUATED'}


def analyze(record, fractions=DEFAULT_FRACTIONS):
    fractions=tuple(finite_float(x, 'budget fraction') for x in fractions)
    if not fractions or any(x<0 for x in fractions) or len(set(fractions))!=len(fractions):
        raise ValueError('Distinct nonnegative fractions required')
    if (not isinstance(record,dict) or record.get('schema_version')!='1.0.0'
            or record.get('status')!='PARTIAL' or record.get('COMPLETE_LFV') is not False
            or record.get('global_zee_acceptance', 'MISSING') is not None):
        raise ValueError('Not a partial Module4 output')
    channels = record.get('channels')
    if not isinstance(channels,dict) or set(channels)!=set(CHANNELS):
        raise ValueError('Expected exactly the three radiative channels')
    return {'schema_version':'1.0.0','task':'MODULE4_MISSING_AMPLITUDE_CONDITIONAL_SENSITIVITY',
            'baseline_commit':BASE_COMMIT,'benchmark_id':record.get('benchmark_id'),
            'status':'DIAGNOSTIC_ONLY_NOT_LFV_CONSTRAINT',
            'budget_kind':'HYPOTHETICAL_NORM_BOUND_NOT_PHYSICAL_W_GAMMA_ESTIMATE',
            'method':'sharp triangle/reverse-triangle inequality for complex (C_L,C_R)',
            'channels':{k:examine_channel(channels[k],fractions) for k in CHANNELS},
            'limitations':['No independently established bound on omitted Wgamma or other diagrams.',
                           'Fractions of largest included component are sensitivity parameters, not theoretical errors.',
                           'The sharp bounds concern a hypothetical bound on the combined missing complex dipole vector.',
                           'Cannot determine exclusion or acceptance from any scenario.']}


def _reject_duplicates(pairs):
    d={}
    for k,v in pairs:
        if k in d: raise ValueError('Duplicate JSON key: '+k)
        d[k]=v
    return d


def cli():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True,help='Actual module4.interface JSON output')
    p.add_argument('--output',required=True)
    p.add_argument('--fractions',nargs='+',type=float,default=DEFAULT_FRACTIONS)
    args=p.parse_args()
    raw=Path(args.input).read_bytes()
    data=json.loads(raw,object_pairs_hook=_reject_duplicates,
                    parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Invalid JSON constant '+x)))
    result=analyze(data,args.fractions)
    result['input_sha256']=hashlib.sha256(raw).hexdigest()
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    tmp=out.with_name(out.name+'.tmp')
    tmp.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n')
    tmp.replace(out)
    print('DIAGNOSTIC_ONLY_NOT_LFV_CONSTRAINT',result['benchmark_id'])


if __name__ == '__main__':
    cli()
