"""SHA-bound D2 replay and cascade diagnostic. No vacuum or flavor reruns."""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from module1.scalar_constraints import validate_input, reconstruct, check_bfb, unitarity, ewpo
from module2.interface import canonical_hash, strict_loads
from module6.d2_scalar_prefilter import neighborhood
from module6.d2_family_runner import DIRECTIONS, compare as compare_families
from module7.cascade_z import cascade_width

ROOT = Path(__file__).resolve().parents[1]
PARENT = '9c9630e6191d149ec23bd640ad4f327c8d4c69a8'
D2_SHA = '79f4164b1bf74b21576e2711960dca3a415cc9eb03f133eb5a885ad10b607b84'
STATUS = 'D3_COUPLED_DIAGNOSTIC_PASS'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def scope_guard(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            low = k.lower()
            require(low not in ('allowed','excluded','is_allowed','is_excluded'), 'Invented allowed/excluded flag')
            if low in ('complete_lfv','constraints_complete','2026_linearized_flavor_filter_ready'):
                require(v is False, 'Invented completeness flag')
            if low == 'global_zee_acceptance':
                require(v is None, 'Invented global acceptance')
            if low in ('total_width_gev', 'branching_fraction', 'cascade_br',
                       'production_cross_section_pb', 'physical_collider_acceptance'):
                require(v is None, 'Invented collider quantity: '+k)
            require(not isinstance(v, float) or math.isfinite(v), 'Nonfinite number')
            scope_guard(v)
    elif isinstance(obj, list):
        for v in obj:
            scope_guard(v)


def rebuild(seed, name, offsets):
    """Full input reconstruction, independent of D2 candidate()/generate()."""
    row = copy.deepcopy(seed)
    tag = 'd2_'+row['module2_input']['ordering']+'_'+name
    row['benchmark_id'] = row['module2_input']['benchmark_id'] = tag
    wrapper = row['module2_input']['scalar']
    record = wrapper['record']
    record['benchmark_id'] = tag
    for key, delta in offsets.items():
        record['physical'][key] = float(record['physical'][key]+delta)
    wrapper['sha256'] = canonical_hash(record)
    return row


def scalar_width(record):
    x, ew, _, _ = validate_input(record)
    return cascade_width(dict(mH1_GeV=x['mH1'], mH2_GeV=x['mH2'],
        gamma_rad=x['gamma'], v_GeV=x['v'], mW_GeV=ew['mW'], mZ_GeV=ew['mZ']))


def verify_sources(seed_raw, evidence_raw):
    evidence = strict_loads(evidence_raw.decode())
    seed = strict_loads(seed_raw.decode())
    scope_guard(evidence)
    require(sha(evidence_raw) == D2_SHA, 'Complete D2 byte SHA mismatch')
    archived = subprocess.check_output(['git', 'show', PARENT+':validation/module6/d2_scoped_scan.json'], cwd=ROOT)
    require(sha(archived) == D2_SHA, 'D2 parent evidence SHA mismatch')
    require(sha(seed_raw) == evidence['seed_bytes_sha256'], 'Complete seed byte SHA mismatch')
    require(canonical_hash(seed) == evidence['source_input_sha256'], 'Complete seed canonical SHA mismatch')
    require(canonical_hash(evidence['source_sha256']) == evidence['source_manifest_sha256'], 'Source manifest SHA mismatch')
    final = evidence['validation']['final_source_sha256']
    for path, expected in evidence['source_sha256'].items():
        # The task-scoped AGENTS is intentionally replaced in D3. Its historical
        # execution hash remains authenticated by the complete parent evidence.
        if path != 'AGENTS.md':
            require(sha((ROOT/path).read_bytes()) == final.get(path, expected), 'Frozen source SHA mismatch: '+path)
    seed_scalar = seed['module2_input']['scalar']
    require(canonical_hash(seed_scalar['record']) == seed_scalar['sha256'], 'Stale seed scalar SHA')
    require(seed['benchmark_id'] == seed['module2_input']['benchmark_id'] == seed_scalar['record']['benchmark_id'], 'Seed benchmark IDs')
    require(seed['module2_input']['ordering'] == 'NO', 'Exact D2 NO target required')
    return seed, evidence


def attach_point(seed, spectrum, point, manifest):
    scope_guard(point)
    label = point['family_name']
    changes = dict(DIRECTIONS).get(label)
    require(changes is not None, 'Unknown family')
    row = rebuild(seed, spectrum['name']+'_'+label, spectrum['offsets'])
    coeff = seed['module2_input']['homogeneous_coefficients']
    vector = np.array(coeff['real'])+1j*np.array(coeff['imag'])
    factors = {}
    for index, (magnitude, phase) in changes.items():
        factor = magnitude*complex(math.cos(phase), math.sin(phase))
        vector[index] *= factor
        factors[str(index)] = dict(magnitude=magnitude, phase_rad=phase, real=factor.real, imag=factor.imag)
    row['module2_input']['homogeneous_coefficients'] = dict(real=vector.real.tolist(), imag=vector.imag.tolist())
    wrapper = row['module2_input']['scalar']
    for key, expected in dict(benchmark_id=row['benchmark_id'], spectrum_name=spectrum['name'],
            input_sha256=canonical_hash(row), module2_input_sha256=canonical_hash(row['module2_input']),
            bound_scalar_sha256=canonical_hash(wrapper['record']), physical=wrapper['record']['physical'],
            homogeneous_coefficients=row['module2_input']['homogeneous_coefficients'],
            per_index_multipliers=factors, changed_indices=sorted(changes),
            target_sha256=canonical_hash(seed['module2_input']['target_eV']),
            source_manifest_sha256=manifest).items():
        require(point[key] == expected, 'Point linkage mismatch: '+key)
    x, ew, _, _ = validate_input(wrapper['record'])
    fc = dict(mH1_GeV=x['mH1'], mH2_GeV=x['mH2'], beta_rad=x['beta'], gamma_rad=x['gamma'],
              mt_MSbar_GeV=163.96892236746697, matching_scale_GeV=160.)
    require(point['flavor_derived_input_sha256'] == canonical_hash(fc), 'Flavor input SHA mismatch')
    require(point['execution_status'] == 'COMPLETED_SCOPED' and point['scalar_status'] == 'SCALAR_PIPELINE_UNKNOWN', 'Unexpected execution/scalar status')
    require(point['scalar_gates']['vacuum']['assessment'] == 'UNKNOWN', 'Unexpected vacuum status')
    require(point['target_vs_reconstructed_relative_error'] < 2e-9, 'Target closure failed')
    selected_scalar = rebuild(seed, spectrum['name'], spectrum['offsets'])['module2_input']['scalar']['record']
    without_id = lambda r: {k:v for k,v in r.items() if k != 'benchmark_id'}
    require(without_id(wrapper['record']) == without_id(selected_scalar), 'Point scalar/EW differs from selected spectrum')
    require(point['scalar_gates']['ewpo']['STU'] == spectrum['gates']['ewpo']['STU'] and
            point['scalar_gates']['ewpo']['selected_fit_result']['chi2_relative_to_fit_minimum'] == spectrum['gates']['ewpo']['chi2'], 'Point EWPO linkage mismatch')
    # Full scalar/EW values are rebuilt, never inferred from the copied point floats.
    result = scalar_width(wrapper['record'])
    return dict(benchmark_id=row['benchmark_id'], spectrum_name=spectrum['name'], family_name=label,
        full_scalar_input=wrapper['record'], bound_scalar_sha256=wrapper['sha256'], input_sha256=canonical_hash(row),
        scalar_EW_without_benchmark_id_sha256=canonical_hash(without_id(wrapper['record'])),
        scalar_vacuum='UNKNOWN', target_closure='PASS', COMPLETE_LFV=False,
        flavor_scope='CONDITIONAL_LO_LINEAR_DIAGNOSTIC_ONLY', global_zee_acceptance=None,
        cascade=result, **{k: point[k] for k in ('delta_C7','delta_C8','conditional_linear_value_1e_minus4',
        'radiative_subset_BR','higgs_lfv_widths_GeV','D_sha256')})


def compare(seed_raw, evidence_raw):
    seed, d2 = verify_sources(seed_raw, evidence_raw)
    screen = d2['scalar_screen']
    require(screen['source_input_sha256'] == canonical_hash(seed), 'Screen source SHA mismatch')
    specs = neighborhood()
    require([(p['name'], p['offsets']) for p in screen['points']] == specs, 'Duplicate or changed screen support')
    spectra = []
    cutflow = {k: dict(PASS=0, FAIL=0, UNKNOWN=0) for k in ('reconstruction','bfb','unitarity','ewpo')}
    for point, (name, offsets) in zip(screen['points'], specs):
        row = rebuild(seed, name, offsets)
        record = row['module2_input']['scalar']['record']
        require(point['scalar_sha256'] == canonical_hash(record), 'Stale screen scalar SHA')
        require(point['benchmark_id'] == row['benchmark_id'], 'Screen benchmark ID')
        x, ew, _, _ = validate_input(record)
        require(point['physical'] == {k:x[k] for k in point['physical']}, 'Tampered screen mass/mixing')
        pars, inherited, rec = reconstruct(x)
        direct = dict(reconstruction=rec, bfb=check_bfb(pars), unitarity=unitarity(pars,inherited), ewpo=ewpo(x,ew,record['ew_fit']))
        for key, gate in direct.items():
            cutflow[key][gate['assessment']] += 1
            require(point['gates'][key]['assessment'] == gate['assessment'] and point['gates'][key]['status'] == gate['status'], 'Scalar gate mismatch')
        fit = direct['ewpo']['alternative_fits_not_combined'][record['ew_fit']]
        require(point['gates']['ewpo']['STU'] == direct['ewpo']['STU'] and point['gates']['ewpo']['chi2'] == fit['chi2_relative_to_fit_minimum'], 'EWPO replay mismatch')
        passed = all(g['assessment'] == 'PASS' for g in direct.values())
        require(point['passes_scoped_tree_and_EWPO'] is passed, 'Screen eligibility mismatch')
        spectra.append(dict(name=name, full_scalar_input=record, scalar_sha256=canonical_hash(record),
            eligible_for_scoped_comparison=passed, control_only=not passed,
            cascade=scalar_width(record), STU=direct['ewpo']['STU'], chi2=fit['chi2_relative_to_fit_minimum']))
    require(cutflow == d2['scalar_screen_cutflow'], 'Cutflow mismatch')
    require(sum(p['eligible_for_scoped_comparison'] for p in spectra) == 29 and len(spectra) == 35, '29/6 cutflow required')
    selected = d2['selected_spectra']
    require([s['name'] for s in selected] == ['source','mH1_m50p0','mH1_p50p0'], 'Wrong selected spectra')
    for s in selected:
        require(s == next(p for p in screen['points'] if p['name'] == s['name']), 'Selected screen record mismatch')
    expected_pairs = {(s['name'], label) for s in selected for label,_ in DIRECTIONS}
    require(len(d2['points']) == 12 and {(p['spectrum_name'],p['family_name']) for p in d2['points']} == expected_pairs, 'Duplicate or missing family points')
    attached = [attach_point(seed, next(s for s in selected if s['name']==p['spectrum_name']), p, d2['source_manifest_sha256']) for p in d2['points']]
    variations = compare_families(d2['points'])
    require(variations == d2['comparisons'], 'Archived family comparisons mismatch')
    for name, group in variations['within_spectrum'].items():
        widths = [p['cascade']['partial_width_GeV'] for p in attached if p['spectrum_name']==name]
        require(max(widths)-min(widths) == 0., 'Gauge family invariance failed')
        group['cascade_width_max_minus_min_GeV'] = max(widths)-min(widths)
        require(len({p['scalar_EW_without_benchmark_id_sha256'] for p in attached if p['spectrum_name']==name}) == 1, 'Fixed-spectrum full scalar/EW mismatch')
    baseline = next(p for p in attached if p['spectrum_name']=='source' and p['family_name']=='baseline')
    for contrast in variations['cross_spectrum_baseline']:
        point = next(p for p in attached if p['spectrum_name']==contrast['spectrum_name'] and p['family_name']=='baseline')
        contrast['second_minus_source']['cascade_partial_width_GeV'] = point['cascade']['partial_width_GeV']-baseline['cascade']['partial_width_GeV']
    unique = {}
    for p in spectra:
        if p['eligible_for_scoped_comparison']:
            c = p['cascade']; x = c['input']
            key = (x['mH1_GeV'],x['mH2_GeV'],x['gamma_rad'])
            unique.setdefault(key, c['partial_width_GeV'])
    values = list(unique.values())
    return dict(schema_version='1.0.0', status=STATUS, D2_parent=PARENT, D2_bytes_sha256=sha(evidence_raw),
        seed_bytes_sha256=sha(seed_raw), source_input_sha256=canonical_hash(seed),
        source_manifest_sha256=d2['source_manifest_sha256'], scalar_gate_cutflow=cutflow,
        scoped_pass=29, control_only_fail=6, linked_points=12, scalar_spectra=spectra, points=attached,
        comparisons=variations, distinct_charged_spectra=len(unique),
        deduplicated_width_range_GeV=[min(values),max(values)],
        sampling_scope='SOURCE_CENTERED_DEVELOPMENT_GRID_NOT_PROBABILITY_PRIOR_OR_REPRESENTATIVE_SCAN',
        repeated_vacuum_searches=0, COMPLETE_LFV=False, constraints_complete=False,
        **{'2026_LINEARIZED_FLAVOR_FILTER_READY':False},
        BR_status='BR_NOT_EVALUATED', physical_LHC_status='PHYSICAL_LHC_CLAIM_NOT_EVALUATED',
        global_zee_acceptance=None)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seed', required=True, type=Path)
    ap.add_argument('--d2-evidence', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    require(args.output.resolve().is_relative_to((ROOT/'validation/module7/local').resolve()), 'Output must be in scoped local directory')
    require(args.output.resolve() not in (args.seed.resolve(), args.d2_evidence.resolve()), 'Output overwrites input')
    result = compare(args.seed.read_bytes(),args.d2_evidence.read_bytes())
    args.output.parent.mkdir(parents=True,exist_ok=True)
    tmp = args.output.with_suffix('.tmp')
    tmp.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    tmp.replace(args.output)
    print(STATUS, '29/6 spectra; 12 linked points')


if __name__ == '__main__':
    main()
