"""Strict versioned JSON/JSONL interface; all scalar and mass inputs explicit."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from module2.interface import (canonical_hash, strict_loads, finite_json, decode,
                               evaluate as neutrino_evaluate, scalar_input,
                               validate_schema as neutrino_validate)
from module2.schema import validate_instance
from .core import (vertices, dipole_ledger, combine, radiative_width,
                   neutral_width, universality, MISSING, OPERATOR, BASIS)
from . import tree

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def foundations():
    pin = json.loads((ROOT/'module3/foundations.json').read_text())
    for name, digest in pin['sha256'].items():
        if sha(ROOT/name) != digest:
            raise ValueError('Frozen foundation hash mismatch: '+name)
    return pin


def encode(x):
    if isinstance(x, np.ndarray):
        return encode(x.tolist())
    if isinstance(x, (complex,np.complexfloating)):
        return {'real':float(x.real),'imag':float(x.imag)}
    if isinstance(x, dict):
        return {k:encode(v) for k,v in x.items()}
    if isinstance(x, (tuple,list)):
        return [encode(v) for v in x]
    if isinstance(x,np.generic):
        return x.item()
    return x


def validate(record, filename):
    finite_json(record)
    validate_instance(record,json.loads((ROOT/'module3'/filename).read_text()))


def evaluate(data):
    validate(data,'input.schema.json')
    pin = foundations()
    inp = data['module2_input']
    neutrino_validate(inp,'input.schema.json')
    if inp['scalar']['kind'] not in ('module1_input','module1_output'):
        raise ValueError('Module3 needs a full Module1 scalar record including neutral masses and alpha')
    nout = neutrino_evaluate(inp)
    if 'module2_output' in data:
        neutrino_validate(data['module2_output'],'output.schema.json')
        # Recompute ALL complex neutrino matrices and the full homogeneous
        # family, Yukawa mass rotation, scalar gates, and input/source hashes.
        if canonical_hash(data['module2_output']) != canonical_hash(nout):
            raise ValueError('Module2 output does not reproduce its supplied input and frozen provenance')
    if data['benchmark_id'] != inp['benchmark_id']:
        raise ValueError('Module2/3 benchmark identity mismatch')
    p, scalar_provenance = scalar_input(inp['scalar'])
    ml = np.array(inp['lepton_masses_GeV'])
    if min(p[k] for k in ['mh1','mh2','ma','mH1','mH2']) < 20*ml[2]:
        raise ValueError('External-invariant loop expansion requires every scalar mass >=20*m_tau')
    F,D = decode(nout['F']),decode(nout['D'])
    constants = data['constants']
    scalars = vertices(D,p,ml)
    ledger, observables = {}, {}
    for name,i,j in [('mu_to_e_gamma',1,0),('tau_to_e_gamma',2,0),('tau_to_mu_gamma',2,1)]:
        pieces = dipole_ledger(F,D,p,ml,i,j)
        ledger[name] = pieces
        c = combine(pieces)
        w = radiative_width(c,ml[i],ml[j],constants['alpha_em'])
        observables[name] = {'status':'PASS','physical_status':'SCALAR_ONE_LOOP_APPROXIMATION',
                             'C_L':c[0],'C_R':c[1],'width_GeV':w,
                             'partial_BR':w/constants['total_lepton_widths_GeV'][i-1],
                             'experimental_comparison':'NOT_EVALUATED'}
    order = data['numerics']['tree_quadrature_order']
    tol = data['numerics']['tree_relative_tolerance']
    for name,i,a,b in [('mu_to_3e',1,0,0),('tau_to_3e',2,0,0),('tau_to_3mu',2,1,1),
                        ('tau_to_mu_ee',2,1,0),('tau_to_e_mumu',2,0,1)]:
        low = tree.width(scalars,i,a,b,ml,order)
        high = tree.width(scalars,i,a,b,ml,2*order)
        residual = abs(high-low)/max(abs(high),np.finfo(float).tiny)
        observables[name] = {'status':'PASS' if residual <= tol else 'UNKNOWN',
                             'physical_status':'TREE_SUBSET_ONLY',
                             'width_GeV':high,'partial_BR':high/constants['total_lepton_widths_GeV'][i-1],
                             'quadrature_relative_change':residual,
                             'experimental_comparison':'NOT_EVALUATED'}
        ledger[name] = {'neutral_tree':{'C_L':None,'C_R':None,
                          'wilsons_GeV_minus2':tree.wilsons(scalars,i,a,b),
                          'normalization':tree.TREE_OPERATOR,'loop_order':0,'basis':BASIS,
                          'provenance':'Frozen SARAH component vertices; exact massive spin sum and scalar propagators',
                          'validation_status':observables[name]['status']}}
    for name,(C,mass) in scalars.items():
        for i,j in [(0,1),(0,2),(1,2)]:
            key = name+'_to_'+['e','mu','tau'][i]+['_e','_mu','_tau'][j]
            observables[key] = {'status':'PASS','physical_status':'LO_TWO_BODY_PARTIAL_WIDTH',
                                'width_GeV':2*neutral_width(C,mass,i,j,ml),
                                'charge_orientations':2,'experimental_comparison':'NOT_EVALUATED'}
    out = {'schema_version':'1.0.0','benchmark_id':data['benchmark_id'],
           'status':'SCOPED_LFV_COMPUTED','COMPLETE_LFV':False,'global_zee_acceptance':None,
           'gates':{'provenance':'PASS','tree':'PASS' if all(v['status']=='PASS' for k,v in observables.items() if k.endswith(('3e','3mu','ee','mumu'))) else 'UNKNOWN',
                    'scalar_one_loop_approximation':'PASS','exact_one_loop':'UNKNOWN',
                    'higgs_widths':'PASS','universality_subset':'PASS','full_lfv':'NOT_EVALUATED'},
           'units':{'masses':'GeV','widths':'GeV','dipoles':'GeV^-2','angles':'rad'},
           'ledger':ledger,'observables':observables,'universality':universality(F,p,constants['GF_GeV_minus2']),
           'missing_contributions':MISSING,
           'provenance':{'input_sha256':canonical_hash(data),'module2_input_sha256':canonical_hash(inp),
                         'module2_output_sha256':canonical_hash(nout),
                         'module2_dataset_sha256':canonical_hash(inp['dataset']) if 'dataset' in inp else None,
                         'constants_dataset_sha256':canonical_hash(constants),
                         'scalar':scalar_provenance,'foundation_commits':{k:v for k,v in pin.items() if k!='sha256'},
                         'code_sha256':{str(q.relative_to(ROOT)):sha(q) for q in sorted((ROOT/'module3').glob('*')) if q.suffix in ('.py','.json','.md')},
                         'dipole_normalization':OPERATOR,'basis':BASIS},
           'limitations':['Authentic official NuFIT 6.1 archive validation remains pending in frozen Module2.',
                          'No experimental LFV likelihood or exclusion is evaluated.',
                          'CP-conserving potential and Type-II quarks are the frozen ansatz; lambda6/7 RG closure remains unproved.',
                          'Raw archived SARAH complex neutral/charged vertex output is absent in this snapshot; source identities and E3 fixtures are cross-checked, not a fresh SARAH run.',
                          'Partial rates can change when missing amplitudes interfere; no cancellation claim applies to the full model.']}
    out = encode(out)
    validate(out,'output.schema.json')
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',default='-')
    parser.add_argument('--output',default='-')
    parser.add_argument('--jsonl',action='store_true')
    args = parser.parse_args()
    src = sys.stdin if args.input=='-' else open(args.input)
    dst = sys.stdout if args.output=='-' else open(args.output,'w')
    failed = False
    try:
        for line in src if args.jsonl else [src.read()]:
            data = None
            try:
                data = strict_loads(line)
                out = evaluate(data)
            except (ValueError,TypeError,KeyError,ArithmeticError,np.linalg.LinAlgError) as exc:
                failed = True
                out = {'schema_version':'1.0.0','benchmark_id':data.get('benchmark_id') if isinstance(data,dict) and isinstance(data.get('benchmark_id'),str) else None,
                       'status':'INPUT_OR_EVALUATION_ERROR','COMPLETE_LFV':False,
                       'global_zee_acceptance':None,'error':str(exc)}
            dst.write(json.dumps(out,sort_keys=True,allow_nan=False)+'\n')
            dst.flush()
    finally:
        if src is not sys.stdin:src.close()
        if dst is not sys.stdout:dst.close()
    return 2 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
