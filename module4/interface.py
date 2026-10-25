"""Strict versioned input/output; never calls a neutrino fit or Module3 evaluate."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from module2.interface import (canonical_hash, strict_loads, finite_json, decode,
                               scalar_input, validate_schema as validate2)
from module2.core import forward, yukawa_rotation
from module2.schema import validate_instance
from module3.interface import validate as validate3, foundations, sha, encode
from module3.core import dipole_ledger, OPERATOR, BASIS, radiative_width
from .amplitudes import ledger, CHANNELS, MISSING, combine
from .charged_scalar import ledger as charged_scalar_ledger

ROOT=Path(__file__).resolve().parents[1]


def validate(record,name):
    finite_json(record)
    validate_instance(record,json.loads((ROOT/'module4'/name).read_text()))


def code_hashes(directory):
    return {str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/directory).glob('*'))
            if p.suffix in (('.py',) if directory=='module2' else ('.py','.json','.md'))}


def unpack(data):
    validate(data,'input.schema.json')
    foundations()
    inp,nout=data['module3_input'],data['module2_output']
    validate3(inp,'input.schema.json');validate2(inp['module2_input'],'input.schema.json')
    validate2(nout,'output.schema.json')
    ninput=inp['module2_input']
    if (nout.get('status')!='NEUTRINO_COMPUTED' or nout['benchmark_id']!=inp['benchmark_id'] or
        ninput['benchmark_id']!=inp['benchmark_id'] or
        nout['provenance']['input_sha256']!=canonical_hash(ninput) or
        nout['provenance']['code_sha256']!=code_hashes('module2') or
        nout['provenance']['basis']!=BASIS or nout['gates']['forward']!='PASS'):
        raise ValueError('Module2 provenance/status mismatch')
    if ninput['scalar']['kind'] not in ('module1_input','module1_output'):
        raise ValueError('Complete frozen scalar record required')
    p,sp=scalar_input(ninput['scalar'])
    scalar_record=ninput['scalar']['record']
    scalar_record=scalar_record.get('input',scalar_record)
    if data['two_loop_inputs']['mW_GeV']!=scalar_record['electroweak']['mW']:
        raise ValueError('W mass must match the supplied frozen scalar electroweak record')
    if nout['provenance']['scalar']!=sp:
        raise ValueError('Scalar provenance mismatch')
    ml=np.array(ninput['lepton_masses_GeV'])
    if min(p[k] for k in ('mh1','mh2','ma','mH1','mH2'))<20*ml[2]:
        raise ValueError('Outside frozen external-mass expansion regime')
    F,D=decode(nout['F']),decode(nout['D'])
    if np.max(abs(F+F.T))>1e-12:
        raise ValueError('Nonantisymmetric F')
    # Verify supplied algebraic output; no inverse solver, oscillation fit,
    # likelihood, or scalar fit runs here.
    calculated=forward(F,D,m1=p['mH1'],m2=p['mH2'],gamma=p['gamma'],ml=ml)
    if not np.allclose(calculated,decode(nout['Mnu']),rtol=2e-9,atol=1e-12):
        raise ValueError('Supplied Module2 forward closure mismatch')
    if ninput['mode']=='inverse' and not np.allclose(calculated,decode(ninput['target_eV']),rtol=2e-9,atol=1e-12):
        raise ValueError('Supplied target mismatch')
    for key,expected in zip(('Ye','Ye2'),yukawa_rotation(D,p['beta'],p['v'],ml)):
        if not np.allclose(decode(nout[key]),expected,rtol=2e-12,atol=1e-16):
            raise ValueError('Yukawa mass rotation mismatch')
    if 'module2_output' in inp and canonical_hash(inp['module2_output'])!=canonical_hash(nout):
        raise ValueError('Embedded Module2 output mismatch')
    if 'module3_output' in data:
        old=data['module3_output'];validate3(old,'output.schema.json')
        if old.get('status')!='SCOPED_LFV_COMPUTED' or old['benchmark_id']!=inp['benchmark_id']:
            raise ValueError('Complete successful Module3 output required')
        prov=old['provenance']
        expected={'input_sha256':canonical_hash(inp),'module2_input_sha256':canonical_hash(ninput),
                  'module2_output_sha256':canonical_hash(nout),'constants_dataset_sha256':canonical_hash(inp['constants']),
                  'scalar':sp,'code_sha256':code_hashes('module3'),'dipole_normalization':OPERATOR,'basis':BASIS,
                  'foundation_commits':{k:v for k,v in foundations().items() if k!='sha256'},
                  'module2_dataset_sha256':canonical_hash(ninput['dataset']) if 'dataset' in ninput else None}
        if prov!=expected or old['gates']['provenance']!='PASS':
            raise ValueError('Module3 complete provenance mismatch')
    return inp,nout,p,ml,F,D


def evaluate(data):
    inp,nout,p,ml,F,D=unpack(data)
    constants=inp['constants'];extra=data['two_loop_inputs']
    channels={}
    for channel,(i,j) in CHANNELS.items():
        original=dipole_ledger(F,D,p,ml,i,j)
        if 'module3_output' in data:
            supplied=data['module3_output']['ledger'][channel]
            if canonical_hash(encode(original))!=canonical_hash(supplied):
                raise ValueError('Module3 dipoles fail signed component reproduction')
            obs=data['module3_output']['observables'][channel]
            expected=np.array([sum(r[k] for r in original.values()) for k in ('C_L','C_R')])
            for key,val in zip(('C_L','C_R'),expected):
                if complex(**obs[key])!=val:
                    raise ValueError('Module3 signed sum mismatch')
        rows={}
        for name,r in original.items():
            rows['module3_'+name]=dict(r,status='PASS',validation_status='VALIDATION_PASS',
                operator_convention=r['normalization'],source=r['provenance'],scalar=name.split('_')[0],
                loop_species='charged_leptons' if name in ('h','H','A') else 'massless_neutrinos',
                gauge_subset='frozen_scalar_one_loop_approximation',numerical_error=0.,
                uncertainty='Frozen approximation; numerical_error=0 is not a truncation-error estimate')
        candidates=ledger(D,p,ml,constants['alpha_em'],extra['fermion_masses_GeV'],extra['mW_GeV'],i,j)
        rows.update({k:r for k,r in candidates.items() if r['coherent_inclusion']})
        candidates={k:r for k,r in candidates.items() if not r['coherent_inclusion']}
        rows.update(charged_scalar_ledger(D,p,ml,constants['alpha_em'],i,j))
        total=combine(rows)
        width=radiative_width(total,ml[i],ml[j],constants['alpha_em'])
        channels[channel]={'ledger':rows,'two_loop_candidates':candidates,
            'omitted_topologies':{name:{'status':'UNKNOWN' if name=='W_gamma' else 'NOT_EVALUATED',
                'C_L':None,'C_R':None,'scalar':None,'loop_species':name,'loop_order':2,
                'source':reason,'gauge_subset':'NOT_MATCHED','operator_convention':OPERATOR,
                'numerical_error':None} for name,reason in MISSING.items()},
            'coherent_blocker':'W GAUGE_MATCHING_UNRESOLVED: W candidates excluded; validated fermion- and charged-scalar-photon subsets included; see matching audits',
            'C_L':total[0],'C_R':total[1],
            'width_GeV':width,'partial_BR':width/constants['total_lepton_widths_GeV'][i-1],
            'rate_scope':'INCLUDED_TOPOLOGIES_ONLY','physical_status':'PREDICTION_INCOMPLETE',
            'experimental_comparison':'NOT_EVALUATED',
            'numerical_error_C_absolute_sum':sum(r['numerical_error'] for r in rows.values())}
    out=encode({'schema_version':'1.0.0','benchmark_id':inp['benchmark_id'],'status':'PARTIAL',
        'COMPLETE_LFV':False,'global_zee_acceptance':None,'channels':channels,
        'module3_output':data.get('module3_output'),
        'missing_contributions':MISSING,'provenance':{
            'input_sha256':canonical_hash(data),'module2_output_sha256':canonical_hash(nout),
            'module3_output_sha256':canonical_hash(data['module3_output']) if 'module3_output' in data else None,
            'operator_convention':OPERATOR,'basis':BASIS,'code_sha256':code_hashes('module4'),
            'two_loop_inputs':extra,'native_vertex_evidence':'validation/module4/results.json; scope and blockers apply'},
        'limitations':['Fermion- and charged-scalar-photon two-loop terms included after direct signed matching; W candidates remain excluded pending complete off-shell gauge matching.',
            'Nominal unmatched mass/Yukawa scheme; no full rate or exclusion.',
            'External momentum/mass corrections and omitted amplitudes may change interference.',
            'Module0-3 covariance, global vacuum, RG and phenomenology limitations remain open.',
            'Three-body interference and mu-e conversion are outside Module4.']})
    validate(out,'output.schema.json')
    return out


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',required=True);ap.add_argument('--output',required=True)
    args=ap.parse_args()
    try:
        result=evaluate(strict_loads(Path(args.input).read_text()))
    except (ValueError,KeyError,TypeError,ArithmeticError) as exc:
        print('INPUT_OR_EVALUATION_ERROR: '+str(exc),file=sys.stderr)
        return 2
    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    return 0


if __name__=='__main__':
    sys.exit(main())
