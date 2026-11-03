"""Bounded HiggsTools evaluation of frozen D10/D12 predictions; no generators."""
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from module2.interface import decode
from module3.core import neutral_width, vertices

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'validation/module13'
IDS = {'D7': 'd7_NO_neutral_near_heavy_07', 'F13': 'F13_heavy_0001330'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def inputs(name):
    records = json.loads((ROOT/'module1/d10_benchmarks.json').read_text())['records']
    record = next(r for r in records if r['input']['benchmark_id'] == IDS[name])
    groups = json.loads((ROOT/'validation/module12/d12_benchmarks.json').read_text())['groups']
    group = next(g for g in groups if g['scalar'] == IDS[name] and g['ordering'] == 'NO')
    digest = hashlib.sha256(json.dumps(record['input'], sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    assert digest == record['input_sha256'] == group['scalar_sha256']
    return record, group['witnesses']['low_joint']


def production(name, state, witness):
    """Absent production stays None, never becomes a physical zero."""
    rows = json.loads((OUT/'higgstools_production_inputs.json').read_text())['records']
    rows = [r for r in rows if r['name'] == name and r['state'] == state and r['energy_TeV'] == 13.]
    if not rows:
        return None
    assert len(rows) == 1
    row = rows[0]
    record, _ = inputs(name)
    assert row['benchmark']['scalar_sha256'] == record['input_sha256']
    assert row['benchmark']['physical'] == record['input']['physical']
    assert row['benchmark']['D12_yukawa_sha256'] == witness['yukawa_sha256']
    assert row['sigma_LO_pb'] > 0
    return row


def h125(pred, physical, witness, sm=False):
    """Reuse the existing tree vertices and HiggsTools effective-coupling approximation."""
    import Higgs.predictions as HP
    h = pred.addParticle(HP.NeutralScalar('h', HP.CP.even))
    h.setMass(physical['mh1'])
    ml = np.array([.00051099895, .1056583755, 1.77686])
    C = vertices(decode(witness['yukawas']['D']), physical, ml)['h'][0]
    kappas = np.diag(C)*physical['v']/ml
    ku = math.sin(physical['alpha'])/math.sin(physical['beta'])
    kd = math.cos(physical['alpha'])/math.cos(physical['beta'])
    kv = math.cos(physical['alpha']-physical['beta'])
    c = HP.NeutralEffectiveCouplings()
    for attr in ('uu', 'cc', 'tt'):
        setattr(c, attr, complex(1 if sm else ku))
    for attr in ('dd', 'ss', 'bb'):
        setattr(c, attr, complex(1 if sm else kd))
    for attr, value in zip(('ee', 'mumu', 'tautau'), kappas):
        setattr(c, attr, complex(1 if sm else value))
    c.WW = c.ZZ = 1 if sm else kv
    HP.effectiveCouplingInput(h, c, reference=HP.ReferenceModel.SMHiggsEW)
    if not sm:
        for i, j, mode in [(0, 1, 'emu'), (0, 2, 'etau'), (1, 2, 'mutau')]:
            h.setDecayWidth(getattr(HP.Decay, mode), 2*neutral_width(C, physical['mh1'], i, j, ml))
    return dict(kappa_u=ku, kappa_d=kd, kappa_V=kv,
                kappa_leptons=[dict(real=float(z.real), imag=float(z.imag)) for z in kappas],
                total_width_GeV=h.totalWidth())


def applied(value):
    lim = value.limit()
    return dict(id=lim.id(), analysis=str(lim), reference=lim.reference(),
                particles=value.contributingParticles(), observed_ratio=value.obsRatio(),
                expected_ratio=value.expRatio(),
                status='EXCLUDED' if value.obsRatio() > 1 else 'NOT_EXCLUDED')


def hb_result(bounds, pred):
    result = bounds(pred)
    return dict(selected={k: applied(v) for k, v in result.selectedLimits.items()},
                applied=[applied(v) for v in result.appliedLimits],
                scope='Only explicitly populated production/decay channels; missing channels are UNEVALUATED',
                status=('EXCLUDED' if not result.allowed else 'NOT_EXCLUDED') if result.appliedLimits else 'UNEVALUATED')


def dataset(root):
    manifest = {str(p.relative_to(root)): sha(p) for p in sorted(root.rglob('*.json'))}
    head = subprocess.check_output(['git', '-C', str(root), 'rev-parse', 'HEAD'], text=True).strip()
    date = subprocess.check_output(['git', '-C', str(root), 'log', '-1', '--format=%cs'], text=True).strip()
    return dict(path=str(root), git_head=head, commit_date=date, files=manifest)


def charged_coverage_reason(lim, physical, rows):
    if rows:
        return 'EVALUATED', 'Explicit 13 TeV tb-associated input'
    desc = lim.processDesc()
    if 'vbfHpm' in desc and 'WZ' in desc:
        return 'NOT_APPLICABLE', 'Validated Zee tree H+-WZ vertex vanishes; no VBF-WZ limit transfer'
    if 'brtHpb' in desc or str(lim.collider()) == 'Collider.LEP':
        return 'NOT_APPLICABLE', 'Both charged masses exceed top-decay/LEP mass coverage'
    data = json.loads(Path(lim.loadedFrom()).read_text())
    grid = data.get('analysis', {}).get('grid', {}).get('mass')
    if grid and not any(min(grid) <= physical[f'mH{s}'] <= max(grid) for s in (1, 2)):
        return 'NOT_APPLICABLE', 'Both charged masses outside the published grid; no extrapolation'
    return 'UNEVALUATED', 'Missing production input for this energy/topology; no physical zero assumed'


def run():
    import Higgs
    import Higgs.predictions as HP
    import Higgs.bounds as HB
    import Higgs.signals as HS
    hbroot = Path('/home/amine/Tools/hbdataset')
    hsroot = Path('/home/amine/Tools/hsdataset')
    # Retain tiny positive tau rates rather than discarding them at default 1e-4.
    bounds = HB.Bounds(str(hbroot), HB.LimitOptions(minExpRatio=0.))
    signals = HS.Signals(str(hsroot))
    result = dict(scope='HiggsTools only; two D10 scalars, D12 NO low_joint Yukawa witnesses',
                  version=importlib.metadata.version('HiggsTools'),
                  library_sha256=sha(next(Path(Higgs.__file__).parent.glob('_Higgs*.so'))),
                  datasets=dict(HB=dataset(hbroot), HS=dataset(hsroot)),
                  source_sha256={p: sha(ROOT/p) for p in [
                      'module1/d10_benchmarks.json', 'validation/module12/d12_benchmarks.json',
                      'module3/core.py', 'module2/interface.py', 'module13/higgstools.py',
                      'validation/module13/higgstools_production_inputs.json']},
                  benchmarks={}, global_zee_acceptance=None)
    for name in IDS:
        record, witness = inputs(name)
        p = record['input']['physical']
        pred = HP.Predictions()
        charged_inputs = []
        for state in (1, 2):
            row = production(name, state, witness)
            decay = witness['decays'][f'H{state}']['total']
            br = decay['branching_fractions']
            h = pred.addParticle(HP.ChargedScalar(f'H{state}'))
            h.setMass(p[f'mH{state}'])
            h.setTotalWidth(decay['total_width_GeV'])
            if row is not None:
                h.setCxn(HP.Collider.LHC13, HP.Production.Hpmtb, row['sigma_LO_pb'])
            for mode, key in [('tb', 't anti-b'), ('cs', 'c anti-s'), ('cb', 'c anti-b'),
                              ('ud', 'u anti-d'), ('us', 'u anti-s'), ('ub', 'u anti-b'),
                              ('cd', 'c anti-d'), ('enu', 'e nu_all'),
                              ('munu', 'mu nu_all'), ('taunu', 'tau nu_all')]:
                h.setBr(getattr(HP.Decay, mode), br.get(key, 0.))
            charged_inputs.append(dict(particle=f'H{state}', mass_GeV=h.mass(),
                total_width_GeV=h.totalWidth(), branching_fractions=br,
                Hpmtb_LHC13_pb=None if row is None else row['sigma_LO_pb']))
        charged = hb_result(bounds, pred)
        # Audit every loaded charged analysis, including missing-energy production.
        catalog = []
        for lim in bounds.limits():
            if '/singleCharge/' not in lim.loadedFrom():
                continue
            rows = [a for a in charged['applied'] if a['id'] == lim.id()]
            status, reason = charged_coverage_reason(lim, p, rows)
            catalog.append(dict(id=lim.id(), analysis=str(lim), results=rows,
                status=status, reason=reason))
        neutral = HP.Predictions()
        h_input = h125(neutral, p, witness)
        chi = signals(neutral)
        sm = HP.Predictions()
        h125(sm, p, witness, sm=True)
        chi_sm = signals(sm)
        measurements = [dict(id=m.id(), reference=m.reference(), n_observables=m.nSubMeasurements(),
                             chi2=m(neutral), chi2_SM=m(sm)) for m in signals.measurements()]
        result['benchmarks'][name] = dict(benchmark_id=IDS[name], scalar_sha256=record['input_sha256'],
            witness_id=witness['id'], yukawa_sha256=witness['yukawa_sha256'], physical=p,
            charged_inputs=charged_inputs, charged_HB=charged, charged_analysis_coverage=catalog,
            h125_HB_approximation=hb_result(bounds, neutral),
            HiggsSignals=dict(status='UNEVALUATED_FULL_MODEL; APPROXIMATE_FIT_EXECUTED',
                inputs=h_input, chi2=chi, chi2_SM=chi_sm, delta_chi2=chi-chi_sm,
                observable_count=signals.observableCount(), measurements=measurements,
                missing=['charged scalar contributions to h->gamma gamma and Z gamma',
                         'validated complete h125 loop BRs; fit parameter count/acceptance prescription'],
                interpretation='No excluded/not-excluded classification from an uncalibrated delta chi2'),
            heavy_neutral=dict(status='UNEVALUATED',
                missing=['complete H/A widths and BRs including hh, charged-scalar W and other scalar modes',
                         'H/A ggH, bbH and other relevant production or validated effective-coupling input']),
            missing_production=['Hpmtb at 8 TeV for older charged limits',
                'charged pair and associated charged-neutral production at the energies required by each limit',
                'other nonvanishing charged production modes required by specific dataset channels',
                'complete heavy-neutral production; h125 uses the built-in effective-coupling approximation'],
            global_zee_acceptance=None)
    dump(OUT/'d13_higgstools.json', result)
    print('HiggsTools', result['version'], 'HB limits', len(bounds.limits()), 'HS observables', signals.observableCount())
    for name, b in result['benchmarks'].items():
        print(name, b['charged_HB']['status'],
              {k: v['observed_ratio'] for k, v in b['charged_HB']['selected'].items()},
              'HS chi2', b['HiggsSignals']['chi2'])
    return result


if __name__ == '__main__':
    run()
