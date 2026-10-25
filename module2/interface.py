"""Strict v1 JSON and JSONL interface. Python evaluate raises on invalid input."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np
from .core import forward, matrix, lepton_masses, solve_fixed_f, null_cone, yukawa_rotation, NumericalUnknown
from .observables import observables
from .data import compare
from .schema import load_schema, validate_instance

ROOT = Path(__file__).resolve().parents[1]
CONVENTION = 'SARAH_ZeeTypeII_Florentino_v1'


def canonical_hash(record):
    return hashlib.sha256(json.dumps(record, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def strict_loads(text):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise ValueError('Duplicate JSON key: '+k)
            out[k] = v
        return out
    out = json.loads(text, object_pairs_hook=pairs, parse_constant=lambda x: (_ for _ in ()).throw(ValueError('Nonfinite JSON constant')))
    finite_json(out)
    return out


def finite_json(x):
    if isinstance(x, dict):
        for v in x.values():
            finite_json(v)
    elif isinstance(x, list):
        for v in x:
            finite_json(v)
    elif isinstance(x, float) and not math.isfinite(x):
        raise ValueError('Nonfinite JSON number')


def decode(x, shape=(3, 3)):
    if not isinstance(x, dict) or set(x) != {'real', 'imag'}:
        raise ValueError('Complex arrays require real and imag')
    def numeric(a):
        v = np.asarray(a)
        if v.shape != shape or v.dtype.kind not in 'ifu' or not np.isfinite(v).all():
            raise ValueError('Invalid real/imag numeric array shape')
        return v.astype(float)
    return numeric(x['real'])+1j*numeric(x['imag'])


def encode(x):
    if isinstance(x, np.ndarray):
        if np.iscomplexobj(x):
            return {'real': x.real.tolist(), 'imag': x.imag.tolist()}
        return x.tolist()
    if isinstance(x, dict):
        return {k: encode(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [encode(v) for v in x]
    if isinstance(x, np.generic):
        return x.item()
    return x


def validate_schema(record, name):
    schema = load_schema(ROOT/'module2'/name)
    validate_instance(record, schema)
    finite_json(record)


def scalar_input(wrapper):
    r = wrapper['record']
    if canonical_hash(r) != wrapper['sha256']:
        raise ValueError('Scalar record SHA256 mismatch')
    kind = wrapper['kind']
    if kind == 'explicit':
        p = r['physical']
        if not (0 < p['mH1'] <= p['mH2'] and p['v'] > 0 and
                .01 < p['beta'] < math.pi/2-.01 and abs(p['gamma']) <= math.pi/2):
            raise ValueError('Invalid scalar mixing chart')
        return p, {'kind': kind, 'sha256': wrapper['sha256'], 'scalar_gates': 'NOT_EVALUATED'}
    from module1.scalar_constraints import validate_input, provenance, reconstruct
    if kind == 'module1_output':
        schema = json.loads((ROOT/'module1/output.schema.json').read_text())
        validate_instance(r, schema)
        if 'input' not in r or r['global_zee_acceptance'] is not None:
            raise ValueError('Module1 output must contain a successful input/output record')
        data = r['input']
        prov = provenance()
        for k in ('module1_version', 'frozen_sources_sha256', 'implementation_sha256', 'schema_sha256', 'output_schema_sha256'):
            if r['provenance'].get(k) != prov[k]:
                raise ValueError('Module1 output provenance mismatch: '+k)
        if r['benchmark_id'] != data['benchmark_id']:
            raise ValueError('Module1 benchmark identity mismatch')
        p, _, _, _ = validate_input(data)
        pars, _, _ = reconstruct(p)
        if any(not math.isclose(r['lagrangian']['parameters'][k], v, rel_tol=2e-12, abs_tol=1e-12) for k, v in pars.items()):
            raise ValueError('Module1 output Lagrangian inconsistent with embedded input')
        gates = r['gates']
    else:
        data = r
        p, _, _, _ = validate_input(data)
        provenance()
        gates = 'NOT_EVALUATED'
    return p, {'kind': kind, 'sha256': wrapper['sha256'], 'module1_version': '1.0.0',
               'benchmark_id': data['benchmark_id'], 'scalar_gates': gates}


def evaluate(data):
    validate_schema(data, 'input.schema.json')
    p, scalar_provenance = scalar_input(data['scalar'])
    ml = lepton_masses(data['lepton_masses_GeV'])
    kw = dict(m1=p['mH1'], m2=p['mH2'], gamma=p['gamma'], ml=ml)
    inverse = None
    if data['mode'] == 'inverse':
        M = matrix(decode(data['target_eV']), 'symmetric')
        if 'F' in data:
            F = matrix(decode(data['F']), 'antisymmetric')
        else:
            cone = data['null_cone']
            t = complex(cone['t']['real'], cone['t']['imag'])
            free_x = complex(cone['free_x']['real'], cone['free_x']['imag']) if 'free_x' in cone else None
            F, _ = null_cone(M, t, cone['scale'], cone['root'], tuple(cone['chart']), free_x=free_x)
            F *= np.exp(1j*cone['phase_rad'])
        inverse = solve_fixed_f(F, M, **kw)
        coeff = decode(data['homogeneous_coefficients'], (4,))
        D = inverse['D0']+np.einsum('k,kij->ij', coeff, inverse['homogeneous'])
    else:
        F = matrix(decode(data['F']), 'antisymmetric')
        if 'D' in data:
            D = matrix(decode(data['D']))
        else:
            # The real diagonal mass combination fixes Ye once unrestricted Ye2
            # is specified. No extra alignment condition is imposed.
            Ye2 = matrix(decode(data['Ye2']))
            S = np.diag(np.sqrt(2)*ml/p['v'])
            Ye = (S-math.sin(p['beta'])*Ye2)/math.cos(p['beta'])
            D = -math.sin(p['beta'])*Ye+math.cos(p['beta'])*Ye2
    Mout = forward(F, D, **kw)
    if inverse is not None:
        err = float(np.linalg.norm(Mout-M)/max(np.linalg.norm(M), np.finfo(float).tiny))
        if err > 2e-9:
            raise NumericalUnknown('Chosen homogeneous coefficients lost forward closure')
        inverse['family_relative_residual'] = err
    Ye, Ye2 = yukawa_rotation(D, p['beta'], p['v'], ml)
    obs = observables(Mout, data['ordering'])
    comparison = compare(obs, data.get('dataset'))
    out = {'schema_version': '1.0.0', 'benchmark_id': data['benchmark_id'],
           'status': 'NEUTRINO_COMPUTED', 'global_zee_acceptance': None,
           'gates': {'forward': 'PASS', 'inverse': 'PASS' if inverse is not None else 'NOT_EVALUATED',
                     'observables': obs['mixing_status'], 'data_comparison': comparison['status'],
                     'lfv': 'NOT_EVALUATED', 'global_vacuum': 'NOT_EVALUATED', 'rg_closure': 'NOT_EVALUATED'},
           'units': {'Mnu': 'eV', 'Yukawas': '1', 'angles': 'rad'},
           'Mnu': Mout, 'F': F, 'D': D, 'Ye': Ye, 'Ye2': Ye2,
           'inverse': inverse, 'observables': obs, 'comparison': comparison,
           'provenance': {'input_sha256': canonical_hash(data), 'scalar': scalar_provenance,
                          'basis': CONVENTION, 'kernel': 'FULL_FINITE_LEPTON_ANALYTIC_60_DIGITS',
                          'code_sha256': {str(q.relative_to(ROOT)): hashlib.sha256(q.read_bytes()).hexdigest()
                                          for q in sorted((ROOT/'module2').glob('*.py'))}},
           'limitations': ['Algebraic neutrino closure is not experimental or global Zee acceptance.',
                           'Restricted CP-conserving scalar sector; unrestricted complex lepton Yukawas.',
                           'LFV/Barr-Zee, SPheno, collider/flavor, RG closure and global vacuum proof not evaluated.']}
    out = encode(out)
    validate_schema(out, 'output.schema.json')
    return out


def main():
    pa = argparse.ArgumentParser(description=__doc__)
    pa.add_argument('--input', default='-')
    pa.add_argument('--output', default='-')
    pa.add_argument('--jsonl', action='store_true')
    args = pa.parse_args()
    src = sys.stdin if args.input == '-' else open(args.input)
    dst = sys.stdout if args.output == '-' else open(args.output, 'w')
    failed = False
    try:
        for text in src if args.jsonl else [src.read()]:
            data = None
            try:
                data = strict_loads(text)
                result = evaluate(data)
            except (ValueError, TypeError, KeyError, OverflowError, np.linalg.LinAlgError) as exc:
                failed = True
                result = {'schema_version': '1.0.0', 'benchmark_id': data.get('benchmark_id') if isinstance(data, dict) and isinstance(data.get('benchmark_id'), str) else None,
                          'status': 'UNKNOWN' if isinstance(exc, NumericalUnknown) else 'INPUT_OR_EVALUATION_ERROR',
                          'global_zee_acceptance': None, 'error': str(exc)}
            dst.write(json.dumps(result, allow_nan=False, sort_keys=True)+'\n')
            dst.flush()
    finally:
        if src is not sys.stdin:
            src.close()
        if dst is not sys.stdout:
            dst.close()
    return 2 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
