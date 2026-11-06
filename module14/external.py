"""Conditional adapters to frozen D9B and D13; no global acceptance claims."""
import hashlib
import functools
import os
import tempfile
import importlib.metadata
import json
import math
from pathlib import Path
import subprocess
import sys

from module2.interface import canonical_hash

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bsgamma(scalar, probe=None, cache_dir=None):
    if not probe or not Path(probe).is_file():
        return {'status': 'NOT_EVALUATED', 'reason': 'D9B rate_probe executable not supplied or unavailable', 'input_sha256': canonical_hash(scalar)}
    evidence = json.loads((ROOT/'validation/module5/d9b_superiso_repair.json').read_text())
    if sha(probe) != evidence['binary_sha256']:
        return {'status': 'ERROR', 'reason': 'D9B probe SHA256 does not match validated binary', 'input_sha256': canonical_hash(scalar)}
    key = canonical_hash({'scalar': scalar, 'probe': sha(probe), 'patch': evidence['patch_sha256'],
                          'matching': sha(ROOT/'scripts/zee_module5_bmu_nlo.py'),
                          'adapter': sha(__file__), 'mu': 160., 'cut_GeV': 1.6})
    path = Path(cache_dir)/('bsgamma_'+key+'.json') if cache_dir else None
    if path and path.exists():
        data = json.loads(path.read_text())
        if data.get('key') != key or data.get('value_sha256') != canonical_hash(data.get('value')):
            raise ValueError('Corrupt B to Xs gamma cache entry')
        return data['value']
    sys.path.insert(0, str(ROOT/'scripts'))
    from zee_module5_bmu_nlo import matching
    p = scalar['physical']; mu = 160.; tb = math.tan(p['beta'])
    mt = evidence['legacy_default_inputs']['mt_match']
    pieces = [matching(p[k], tb, mt, mu=mu, flip=False) for k in ('mH1', 'mH2')]
    weights = [math.cos(p['gamma'])**2, math.sin(p['gamma'])**2]
    keys = ('C7_LO','C8_LO','C4_NLO_raw','C7_NLO_raw','C8_NLO_raw')
    coeff = {k: sum(w*x[k] for w,x in zip(weights,pieces)) for k in keys}
    cmd = [str(Path(probe).resolve()), str(p['mH1']), str(tb), '0', *(str(coeff[k]) for k in keys), str(mu)]
    run = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=True)
    values = {k: float(v) for k,v in (line.split() for line in run.stdout.splitlines())}
    rate = values['injected_BR']
    if not math.isfinite(rate) or rate <= 0:
        raise ValueError('D9B nonfinite or nonpositive rate')
    result = {'status': 'DIAGNOSTIC_ONLY', 'input_sha256': canonical_hash(scalar),
              'branching_ratio': rate, 'measurement': {'value': 3.49e-4, 'uncertainty': 0.19e-4, 'source': 'D12 PDG2026 reference'},
              'comparison_status': 'DIAGNOSTIC_ONLY', 'theory_uncertainty': 'NOT_CALIBRATED',
              'scope': evidence['accuracy'], 'independent_accuracy': evidence['independent_physical_accuracy'],
              'probe_sha256': sha(probe), 'patch_sha256': evidence['patch_sha256'],
              'matching_source_sha256': sha(ROOT/'scripts/zee_module5_bmu_nlo.py'),
              'matching_scale_GeV': mu, 'weights': weights, 'coefficients': coeff}
    result['output_sha256'] = canonical_hash(result)
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.bsgamma.')
        with os.fdopen(fd, 'w') as f:
            json.dump({'key': key, 'value': result, 'value_sha256': canonical_hash(result)}, f, sort_keys=True, allow_nan=False)
        try:
            os.link(tmp, path)
        except FileExistsError:
            os.unlink(tmp)
            return bsgamma(scalar, probe, cache_dir)
        os.unlink(tmp)
    return result


@functools.lru_cache(maxsize=4)
def tools_runtime(hb_data, hs_data):
    import Higgs.bounds as HB
    import Higgs.signals as HS
    from module13.higgstools import dataset
    return (HB.Bounds(hb_data, HB.LimitOptions(minExpRatio=0.)), HS.Signals(hs_data),
            {'HB': dataset(Path(hb_data)), 'HS': dataset(Path(hs_data))})


def higgstools(scalar, family, hb_data, hs_data, widths=None, production=None):
    missing = [name for name, path in [('HiggsBounds dataset', hb_data), ('HiggsSignals dataset', hs_data)] if not path or not Path(path).is_dir()]
    if missing:
        return {'status': 'NOT_EVALUATED', 'reason': 'Missing '+', '.join(missing)}
    try:
        import Higgs.predictions as HP
        import Higgs.bounds as HB
        import Higgs.signals as HS
        from module13.higgstools import h125, hb_result, dataset
        if importlib.metadata.version('HiggsTools') != '1.1.3':
            raise ValueError('HiggsTools 1.1.3 required')
    except ImportError as exc:
        return {'status': 'NOT_EVALUATED', 'reason': 'HiggsTools unavailable: '+str(exc)}
    bounds, signals, datasets = tools_runtime(str(hb_data), str(hs_data))
    pred = HP.Predictions()
    p = scalar['physical']; witness = {'yukawas': {'D': family['D']}}
    inputs = h125(pred, p, witness)
    fit = float(signals(pred))
    limits = hb_result(bounds, pred)
    charged = {'status': 'NOT_EVALUATED', 'reason': 'No validated per-point matched charged production input',
               'analyses': [{'id': lim.id(), 'status': 'NOT_EVALUATED', 'reason': 'Missing matched production'}
                            for lim in bounds.limits() if '/singleCharge/' in lim.loadedFrom()]}
    if production is not None:
        # The old shorthand was not a source-qualified production contract.
        # Validate an actual H2 card before feeding a charged production mode.
        from module14.conditional_scan.workflow import production as validate_production
        if not isinstance(production, dict) or not production.get('validated_card_path'):
            raise ValueError('Charged HiggsTools production requires validated_card_path and expected_contract')
        supplied = validate_production(production['validated_card_path'], scalar, family,
                                       production.get('expected_contract'))
        if (production.get('expected_contract') is None or supplied['energy_TeV'] != 13
            or supplied['process'] != 'pp_tbH2' or supplied['charge_definition'] != 'both'):
            raise ValueError('HiggsTools Hpmtb requires explicit 13 TeV both-charge pp_tbH2 contract')
        production = dict(supplied, charged_Hpmtb_13TeV_pb={'H2': supplied['sigma_pb']})
        expected_scalar = canonical_hash(scalar)
        yukawas = {k: canonical_hash(family[k]) for k in ('F', 'D', 'Ye', 'Ye2')}
        if production.get('scalar_sha256') != expected_scalar or production.get('yukawa_sha256') != yukawas:
            raise ValueError('Production input does not match scalar and Yukawa hashes')
        if not widths or widths.get('status') != 'PASS':
            charged['reason'] = 'Complete matched charged decay widths missing'
        else:
            entries = production.get('charged_Hpmtb_13TeV_pb', {})
            if set(entries) - {'H1', 'H2'}:
                raise ValueError('Unsupported charged production entries')
            results = []
            for state, cross_section in entries.items():
                if isinstance(cross_section, bool) or not isinstance(cross_section, (int, float)) or not math.isfinite(cross_section) or cross_section <= 0:
                    raise ValueError('Invalid charged production cross section')
                cp = HP.Predictions()
                h = cp.addParticle(HP.ChargedScalar(state))
                h.setMass(p['m'+state]); total = widths['mothers'][state]['total']
                h.setTotalWidth(total['total_width_GeV'])
                h.setCxn(HP.Collider.LHC13, HP.Production.Hpmtb, cross_section)
                br = total['branching_fractions']
                for mode, key in [('tb','t anti-b'),('cs','c anti-s'),('cb','c anti-b'),('ud','u anti-d'),('us','u anti-s'),('ub','u anti-b'),('cd','c anti-d'),('enu','e nu_all'),('munu','mu nu_all'),('taunu','tau nu_all')]:
                    h.setBr(getattr(HP.Decay, mode), br.get(key, 0.))
                results.append({'state': state, 'result': hb_result(bounds, cp)})
            charged['per_state'] = results
            for analysis in charged['analyses']:
                found = [x for r in results for x in r['result']['applied'] if x['id'] == analysis['id']]
                if found:
                    analysis.update(status='DIAGNOSTIC_ONLY', results=found, reason='Matched 13 TeV tb-associated input only')
            if results:
                charged.update(status='DIAGNOSTIC_ONLY', reason='Only explicitly supplied production modes evaluated', production_sha256=canonical_hash(production))
    result = {'status': 'DIAGNOSTIC_ONLY', 'scalar_sha256': canonical_hash(scalar),
              'module2_input_sha256': family['input_sha256'], 'h125_inputs': inputs,
              'h125_higgsbounds': limits, 'higgs_signals': {'chi2': fit, 'status': 'DIAGNOSTIC_ONLY',
              'reason': 'Charged-scalar loop contributions and complete widths missing'},
              'charged_searches': charged,
              'heavy_neutral': {'status': 'NOT_EVALUATED', 'reason': 'Complete heavy-neutral widths and matched production unavailable'},
              'version': importlib.metadata.version('HiggsTools'), 'datasets': {k: {'path': v['path'], 'git_head': v['git_head'], 'commit_date': v['commit_date'], 'manifest_sha256': canonical_hash(v['files'])} for k,v in datasets.items()},
              'source_sha256': sha(ROOT/'module13/higgstools.py')}
    result['output_sha256'] = canonical_hash(result)
    return result
