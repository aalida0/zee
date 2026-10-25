"""Module 1 v1.0.0: one-point JSON or streaming JSONL scalar pipeline.

Run: python -m module1.scalar_constraints --input benchmark.json
     python -m module1.scalar_constraints --jsonl --input points.jsonl
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from gate6_benchmark import benchmark
from gateA1g_zee_oblique_T import oblique_T, F
from gateA1h_correlated_stu_ewpo import stu_S_U, grimus_Ghat, correlated_fit, FITS
from .potential import Potential, scatter_matrix, charge_basis, legacy_neutral_basis
from .bfb import check_bfb
from .vacuum import search_vacuum

VERSION = '1.0.0'
CONVENTION = 'SARAH_ZeeTypeII_Florentino_v1'
MODEL = 'ZeeTypeII_Module0_v1_restricted_CP'
BASE = '00bc58869358501bf3f3ef583e2c759a23a4f39a'
UNITS = {'masses': 'GeV', 'angles': 'rad', 'mass_squared': 'GeV^2', 'quartics': '1'}
KEYS = {'mh1', 'mh2', 'ma', 'mH1', 'mH2', 'alpha', 'beta', 'gamma', 'm12sq', 'lc', 'k1', 'k2', 'k12', 'v'}
WARNINGS = ['Restricted CP-conserving scalar potential; complex lepton Yukawas; lambda6/7 absent; RGE closure unproven.',
            'Finite tree vacuum search cannot certify global stability.',
            'Scalar oblique-only Gaussian likelihood; no full electroweak or global Zee acceptance.',
            'Requested Module0 tag/commit is absent in this isolated snapshot; exact frozen file hashes are pinned.']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def provenance():
    pins = json.loads((ROOT/'module1/foundation.json').read_text())
    for name, expected in pins['sha256'].items():
        if digest(ROOT/name) != expected:
            raise ValueError('Frozen foundation hash mismatch: '+name)
    native = ROOT/pins['module0_native_validation_inventory']
    if digest(native) != pins['native_inventory_sha256']:
        raise ValueError('Module0 native inventory hash mismatch')
    return {'module1_version': VERSION, 'requested_model_tag': 'zee-sarah-module0-v1',
            'requested_model_commit': BASE, 'snapshot_commit': pins['snapshot_commit'],
            'requested_ancestry_verified': False, 'frozen_sources_sha256': pins['sha256'],
            'module0_native_source_commit': pins['module0_native_source_commit'],
            'module0_native_potential_hash_matches': pins['native_potential_hash_matches'],
            'implementation_sha256': {str(p.relative_to(ROOT)): digest(p)
                                      for p in sorted((ROOT/'module1').glob('*.py'))},
            'schema_sha256': digest(ROOT/'module1/input.schema.json'),
            'output_schema_sha256': digest(ROOT/'module1/output.schema.json'),
            'literature_versions': ['0802.4353v1', '2106.08332v1', '1701.05345v2', '1205.3781v3'],
            'fit_snapshot': 'Gfitter web verified 2026-10-25; PDG2025 review revised November2025, PDF dated 2026-04-15'}


def validate_input(data):
    required = {'schema_version', 'benchmark_id', 'model', 'parameter_convention', 'units', 'physical', 'electroweak', 'ew_fit'}
    if not isinstance(data, dict) or not required <= data.keys() or data.keys()-required-{'search'}:
        raise ValueError('Missing or unsupported input fields')
    for key, value in (('schema_version', VERSION), ('model', MODEL), ('parameter_convention', CONVENTION), ('units', UNITS)):
        if data[key] != value:
            raise ValueError('Unsupported '+key)
    if not isinstance(data['benchmark_id'], str) or not data['benchmark_id'].strip():
        raise ValueError('benchmark_id must be nonempty')
    x = data['physical']
    if not isinstance(x, dict) or x.keys() != KEYS:
        raise ValueError('Every physical input is required; unsupported scalar operators are rejected')
    ew = data['electroweak']
    if not isinstance(ew, dict) or ew.keys() != {'mW', 'mZ', 'SM_reference_mh', 'scheme'} or ew['scheme'] != 'on_shell_MW_MZ':
        raise ValueError('Unsupported electroweak inputs or scheme')
    for value in [*x.values(), ew['mW'], ew['mZ'], ew['SM_reference_mh']]:
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError('All scalar/EW numbers must be finite JSON numbers')
    if (not 0 < x['mh1'] <= x['mh2'] or not 0 < x['mH1'] <= x['mH2'] or x['ma'] <= 0
            or x['v'] <= 0 or not .01 < x['beta'] < math.pi/2-.01 or abs(x['gamma']) > math.pi/2):
        raise ValueError('Unsupported spectrum or singular angle convention')
    if not 0 < ew['mW'] < ew['mZ'] or ew['SM_reference_mh'] != 125.:
        raise ValueError('Fits use fixed 125 GeV reference Higgs; require 0<MW<MZ')
    if not isinstance(data['ew_fit'], str) or data['ew_fit'] not in FITS:
        raise ValueError('Select exactly one supported correlated STU fit')
    search = data.get('search', {})
    if not isinstance(search, dict) or search.keys()-{'starts', 'seeds'}:
        raise ValueError('Unsupported search configuration')
    n, seeds = search.get('starts', 64), search.get('seeds', [123, 104852])
    if type(n) is not int or not 64 <= n <= 4096:
        raise ValueError('Require 64<=starts<=4096 per full chart per seed')
    if (not isinstance(seeds, list) or len(seeds) != 2
            or any(type(s) is not int or not 0 <= s < 2**32 for s in seeds) or len(set(seeds)) != 2):
        raise ValueError('Require two distinct unsigned 32-bit seeds')
    return x, ew, n, seeds


def reconstruct(x):
    # Reuse frozen inversion. Extend only the continuous signed/endpoint
    # gamma convention; all other formulas are inherited unchanged.
    opts = dict(x)
    opts['gamma'] = min(max(abs(x['gamma']), 1e-30), math.nextafter(math.pi/2, 0))
    inherited = benchmark(**opts)
    mu = math.copysign(inherited['mu4_GeV'], x['gamma'])
    if abs(x['gamma']) in (0., math.pi/2):
        mu = 0.
    p = {'Lambda'+str(i): inherited['quartics']['lambda'+str(i)] for i in range(1, 6)}
    p.update(LambdaC=x['lc'], K1=x['k1'], K2=x['k2'], K12=x['k12'],
             Mu4=mu, MCS2=inherited['mc2_GeV2'], M12Sq=x['m12sq'])
    cb, sb = math.cos(x['beta']), math.sin(x['beta'])
    l345 = p['Lambda3']+p['Lambda4']+p['Lambda5']; v = x['v']
    p['M112'] = x['m12sq']*sb/cb-v*v/2*(p['Lambda1']*cb*cb+l345*sb*sb)
    p['M222'] = x['m12sq']*cb/sb-v*v/2*(p['Lambda2']*sb*sb+l345*cb*cb)
    if not all(math.isfinite(value) for value in p.values()):
        raise ValueError('Reconstruction exceeds finite numerical range')
    r = np.zeros(10); r[[2, 6]] = [v*cb, v*sb]
    _, grad, h = Potential(p).evaluate(r)
    expected = np.sort([0., 0., 0., x['mh1']**2, x['mh2']**2, x['ma']**2,
                        x['mH1']**2, x['mH1']**2, x['mH2']**2, x['mH2']**2])
    eig = np.linalg.eigvalsh(h)
    residual = float(np.max(abs(eig-expected)/np.maximum(1., expected)))
    ca, sa, cg, sg = (f(x[k]) for f, k in ((math.cos, 'alpha'), (math.sin, 'alpha'),
                                          (math.cos, 'gamma'), (math.sin, 'gamma')))
    zh = np.array([[ca, sa], [-sa, ca]])
    za = np.array([[cb, sb], [-sb, cb]])
    zp = np.array([[cb, sb, 0], [-sb*cg, cb*cg, sg], [sb*sg, -cb*sg, cg]])
    rotations = [(zh, [2, 6], [x['mh1']**2, x['mh2']**2]),
                 (za, [3, 7], [0., x['ma']**2]),
                 (zp, [0, 4, 8], [0., x['mH1']**2, x['mH2']**2]),
                 (zp, [1, 5, 9], [0., x['mH1']**2, x['mH2']**2])]
    mixing = max(float(np.max(abs(z@h[np.ix_(ix, ix)]@z.T-np.diag(m)))) for z, ix, m in rotations)
    gn = float(max(abs(grad))/v**3)
    if (not all(math.isfinite(value) for value in (residual, gn, mixing)) or residual > 1e-7
            or gn > 1e-9 or mixing/max(1., expected.max()) > 1e-10):
        raise ValueError('Independent full-potential Hessian/mixing/tadpole closure failed')
    return p, inherited, {'status': 'RECONSTRUCTION_VALIDATED', 'assessment': 'PASS', 'order': 'tree',
                          'tadpole_max_over_v3': gn, 'spectrum_max_relative_residual': residual,
                          'mixing_max_residual_GeV2': mixing, 'full_hessian_eigenvalues_GeV2': eig.tolist(),
                          'mixing_rows': {'ZH': zh.tolist(), 'ZA': za.tolist(), 'ZP': zp.tolist()}}


def unitarity(p, inherited):
    matrix = scatter_matrix(p)
    eig = np.linalg.eigvalsh(matrix)
    maximum = float(max(abs(eig)))
    lift, sectors = charge_basis()
    transformed = lift.conj().T@matrix@lift
    mask = np.ones((55, 55), bool)
    blocks = {}
    for (q, y), indices in sorted(sectors.items()):
        mask[np.ix_(indices, indices)] = False
        blocks[f'Q={q},2Y={y}'] = len(indices)
    leakage = float(np.max(abs(transformed[mask])))
    agreement = abs(maximum-inherited['max_abs_unitarity_eigenvalue'])
    neutral_basis = legacy_neutral_basis(lift)
    incoming = neutral_basis.T@matrix@neutral_basis
    legacy_residual = float(max(abs(np.linalg.eigvalsh(incoming.real)-inherited['unitarity_eigenvalues']['Q0Y0'])))
    signed_differences = [z for z in inherited['unitarity_eigenvalues']['Q0Y0'] if min(abs(eig-z)) > 2e-8]
    if leakage > 1e-9:
        raise ValueError('Contact matrix violates charge/hypercharge blocks')
    return {'status': 'TREE_UNITARITY_PASS' if maximum < 8*math.pi else 'TREE_UNITARITY_FAIL',
            'assessment': 'PASS' if maximum < 8*math.pi else 'FAIL', 'order': 'tree_contact_high_energy',
            'eigenvalue_count': 55, 'eigenvalues': eig.tolist(), 'max_abs_eigenvalue': maximum,
            'max_abs_a0': maximum/(16*math.pi), 'strict_limit': 8*math.pi,
            'normalization': 'Tijkl/sqrt((1+delta_ij)(1+delta_kl)); a0=M/(16*pi); |Re a0|<1/2',
            'charge_hypercharge_multiplicities': blocks, 'off_block_residual': leakage,
            'gate6_max_eigenvalue_residual': agreement, 'gate6_disagreement': bool(agreement > 2e-8),
            'gate6_neutral_all_incoming_residual': legacy_residual,
            'gate6_neutral_signed_eigenvalues_absent_from_physical_spectrum': signed_differences,
            'gate6_neutral_convention': 'App.C5 uses B.T M B (all incoming); physical operator uses B.conj().T M B. Signed differences retained; absolute bound agrees.'}


def ewpo(x, ew, selected):
    kw = {k: x[j] for k, j in (('mh', 'mh1'), ('mH', 'mh2'), ('mA', 'ma'), ('m1', 'mH1'),
                                ('m2', 'mH2'), ('alpha', 'alpha'), ('beta', 'beta'), ('gamma', 'gamma'))}
    kw.update(mW=ew['mW'], mZ=ew['mZ'])
    mh, ref = x['mh1'], ew['SM_reference_mh']
    mz, mw = ew['mZ'], ew['mW']; denom = 16*math.pi*(1-(mw/mz)**2)*mw**2
    reference_T = 3*(F(mz, mh)-F(mw, mh)-F(mz, ref)+F(mw, ref))/denom
    t, _ = oblique_T(**kw)
    alternative, _ = oblique_T(coefficient=.5, **kw)

    def values(n):
        su = stu_S_U(n=n, **kw)
        gh = lambda mass, q: grimus_Ghat(mass*mass, q*q, n=n)
        s = su['S']+(math.log(mh*mh/(ref*ref))+gh(mh, mz)-gh(ref, mz))/(24*math.pi)
        u = su['U']+(gh(mh, mw)-gh(mh, mz)-gh(ref, mw)+gh(ref, mz))/(24*math.pi)
        return np.array([s, t+reference_T, u])

    old = values(80); delta = math.inf
    for n in (160, 320, 640):
        val = values(n); delta = float(max(abs(val-old)))
        if delta < 2e-8:
            break
        old = val
    if not np.isfinite(val).all() or delta >= 2e-8:
        raise ValueError('STU quadrature nonconvergence')
    fits = {name: correlated_fit(*val, name) for name in FITS}
    inside = fits[selected]['inside_95percent_3D_gaussian_ellipsoid']
    return {'status': 'SCALAR_OBLIQUE_INSIDE_95' if inside else 'SCALAR_OBLIQUE_OUTSIDE_95',
            'assessment': 'PASS' if inside else 'FAIL', 'order': 'one_loop_scalar',
            'scope': 'scalar oblique-only likelihood, not full electroweak acceptance',
            'STU': dict(zip(('S', 'T', 'U'), val.tolist())), 'SM_reference_mh_GeV': ref,
            'quadrature_nodes': n, 'quadrature_max_delta': delta, 'selected_fit': selected,
            'alternative_fits_not_combined': fits, 'charged_pair_coefficient': -2.,
            'disputed_coefficient_minus_half_T': alternative+reference_T,
            'disputed_T_shift': alternative-t}


def evaluate(data):
    x, ew, starts, seeds = validate_input(data)
    prov = provenance()
    p, inherited, reconstruction = reconstruct(x)
    gates = {'reconstruction': reconstruction}
    calls = {'bfb': lambda: check_bfb(p), 'unitarity': lambda: unitarity(p, inherited),
             'vacuum': lambda: search_vacuum(p, x, starts, seeds),
             'ewpo': lambda: ewpo(x, ew, data['ew_fit'])}
    for name, call in calls.items():
        try:
            gates[name] = call()
        except (ValueError, FloatingPointError, OverflowError, np.linalg.LinAlgError) as exc:
            gates[name] = {'status': 'UNKNOWN', 'assessment': 'UNKNOWN', 'reason': str(exc)}
        gates[name].setdefault('order', {'bfb': 'tree_quartic', 'unitarity': 'tree_contact_high_energy',
                                       'vacuum': 'tree', 'ewpo': 'one_loop_scalar'}[name])
    assessment = 'FAIL' if any(g['assessment'] == 'FAIL' for g in gates.values()) else 'UNKNOWN'
    return {'schema_version': VERSION, 'benchmark_id': data['benchmark_id'], 'status': 'SCALAR_PIPELINE_'+assessment,
            'global_zee_acceptance': None, 'input': data, 'provenance': prov, 'warnings': WARNINGS,
            'lagrangian': {'parameters': p, 'units': {'M112': 'GeV^2', 'M222': 'GeV^2', 'M12Sq': 'GeV^2',
                                                      'MCS2': 'GeV^2', 'Mu4': 'GeV', 'all_other': '1'},
                           'lambda6': 0., 'lambda7': 0., 'convention': CONVENTION}, 'gates': gates}


def strict_loads(text):
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d:
                raise ValueError('Duplicate JSON key: '+k)
            d[k] = v
        return d
    return json.loads(text, object_pairs_hook=pairs,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError('Nonfinite JSON number '+s)))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input', type=Path, help='stdin if omitted')
    ap.add_argument('--output', type=Path, help='stdout if omitted')
    ap.add_argument('--jsonl', action='store_true')
    args = ap.parse_args()
    source = args.input.open() if args.input else sys.stdin
    target = args.output.open('w') if args.output else sys.stdout
    failed = False
    try:
        records = source if args.jsonl else [source.read()]
        for line in records:
            data = None
            try:
                data = strict_loads(line)
                out = evaluate(data)
                json.dumps(out, allow_nan=False)  # Reject nonfinite diagnostics per record.
            except Exception as exc:
                failed = True
                recovered_id = data.get('benchmark_id') if isinstance(data, dict) else None
                out = {'schema_version': VERSION, 'benchmark_id': recovered_id if isinstance(recovered_id, str) else None,
                       'status': 'INPUT_OR_EVALUATION_ERROR', 'error': str(exc), 'global_zee_acceptance': None}
            target.write(json.dumps(out, sort_keys=True, allow_nan=False, indent=None if args.jsonl else 2)+'\n')
            target.flush()
    finally:
        if args.input:
            source.close()
        if args.output:
            target.close()
    return 2 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
