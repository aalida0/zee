"""Replay original-card partial widths and the selected observed-search stop gate.

Does not launch production or assign BRs. F13 HDECAY and native SARAH receipts
were executed separately; immutable source pins and raw receipts are checked.
"""
import argparse
import importlib.metadata
import json
from pathlib import Path
import tarfile

from research.full_constraints.higgs import neutral_widths as n
from research.full_constraints.higgs.decays_bridge import require_complete_width
from research.full_constraints.higgs.sushi_bridge import dump


def run(out):
    if out.exists(): raise FileExistsError(out)
    out.mkdir(parents=True)
    old = json.loads((n.HERE/'SUSHI_SOURCE_MANIFEST.json').read_text())
    n.verify_sources(old)
    production = json.loads((n.HERE/'SUSHI_EVIDENCE.json').read_text())
    if n.sha(n.HERE/'SUSHI_SOURCE_MANIFEST.json') != production['source_manifest_sha256']:
        raise ValueError('Historical SusHi manifest mismatch')
    if n.sha(n.HERE/'SUSHI_RUNS.tar.gz') != old['raw_archive_sha256']:
        raise ValueError('Historical receipt archive mismatch')
    with tarfile.open(n.HERE/'SUSHI_RUNS.tar.gz') as archive:
        d7 = archive.extractfile('anyhdecay-D7.txt').read()
    d7path = out/'anyhdecay-D7.txt'; d7path.write_bytes(d7)
    if n.sha(d7path) != old['raw_receipts']['anyhdecay-D7.txt']:
        raise ValueError('Historical D7 output changed')
    receipt = json.loads((n.HERE/'neutral_receipts/F13_EXECUTION.json').read_text())
    f13 = n.HERE/'neutral_receipts/anyhdecay-F13.stdout'
    if n.sha(f13) != receipt['stdout_sha256']:
        raise ValueError('F13 output digest mismatch')
    if n.sha(n.HERE/'neutral_receipts/native_inputs.json') != old['raw_receipts']['native_inputs.json']:
        raise ValueError('Native scalar/Yukawa rules differ from original receipt')
    if receipt['parent_manifest_sha256'] != production['source_manifest_sha256']:
        raise ValueError('F13 source lineage mismatch')
    cases = [n.calculate('D7',d7path),n.calculate('F13',f13)]
    coverage = json.loads((n.HERE/'COVERAGE.json').read_text())
    selected = next(x for x in coverage['limits'] if x['id']==200212223)
    path = Path(coverage['datasets']['HB']['path'])/selected['file']
    if n.sha(path) != selected['sha256']:
        raise ValueError('Observed-search dataset changed')
    raw = json.loads(path.read_text())
    if raw['collider']!='LHC13' or raw['process'] != [{'channels':[['ggH','tautau']]},{'channels':[['bbH','tautau']]}]:
        raise ValueError('Selected process/energy mismatch')
    import Higgs
    import Higgs.bounds as HB
    library = next(Path(Higgs.__file__).parent.glob('_Higgs*.so'))
    if importlib.metadata.version('HiggsTools')!='1.1.3' or n.sha(library)!=coverage['library_sha256']:
        raise ValueError('Pinned HiggsTools runtime mismatch')
    bounds = HB.Bounds(coverage['datasets']['HB']['path'],HB.LimitOptions(minExpRatio=0.))
    limit = next(x for x in bounds.limits() if x.id()==selected['id'])
    if str(Path(limit.loadedFrom()).resolve()) != str(path.resolve()):
        raise ValueError('Native HiggsTools selected another dataset')
    mass_grid = [x['mass'] for x in raw['analysis']['stackedLlhGrid']]
    attempts = []
    for case in cases:
        for state,row in case['states'].items():
            mass = row['photon']['mass_GeV']
            if not min(mass_grid)<=mass<=max(mass_grid):
                raise ValueError('No mass extrapolation authorized')
            rate = next(x for x in production['records'] if x['name']==case['name'] and x['state']==state)
            try:
                require_complete_width(row)
            except ValueError as error:
                rejection = str(error)
            else:
                raise RuntimeError('Unexpected complete width: requires independent signal qualification')
            attempts.append(dict(name=case['name'],state=state,mass_GeV=mass,
                mass_bracket_GeV=[max(x for x in mass_grid if x<=mass),min(x for x in mass_grid if x>=mass)],
                retained_SusHi_rates=rate['central']['rates'],retained_SusHi_uncertainties=rate['uncertainties'],
                status='MISSING_PREDICTION',consumer_rejection=rejection,
                observed_ratio=None,expected_ratio=None,BR_tautau=None,sigma_times_BR_pb=None,
                known_sum_over_mass_diagnostic=row['known_disjoint_sum_GeV']/mass))
    search = dict(status='HIGGS_SCOPED_SEARCH_BLOCKED',selected_analysis={k:v for k,v in selected.items() if k!='cases'},
        selection_reason='Both original H/A masses lie in the 13-TeV ggF/bbH tau-tau domain; production already independently validated; selected before computing any ratio',
        HiggsTools_version=importlib.metadata.version('HiggsTools'),
        native_limit_description=limit.processDesc(),dataset_sha256=n.sha(path),
        dataset_commit=coverage['datasets']['HB']['git_head'],mass_grid_GeV=mass_grid,
        interpretation='Two-production-channel observed/expected likelihood grids, not a single observed cross-section curve',
        experimental_source='https://arxiv.org/html/2002.12223v2',
        source_hypothesis='Spin-zero resonance; natural width negligible compared with resolution; ggF Powheg-Box v2 and bbH MG5_aMC@NLO signal samples; b-tag and b-veto categories',
        width_grid=None,extrapolation=False,
        remaining_signal_inputs=[
            'Qualified total widths/BRs with missing-channel bounds and correlated decay uncertainty',
            'LO SusHi scale/PDF bands do not qualify omitted QCD/EW and mass-scheme/parametric uncertainties',
            'Zee general complex tau coupling CP mixture and production kinematics acceptance transfer to the b-tag/veto selections',
            'Finite width, nearby H/A overlap and interference treatment for the full model signal',
            'Expected-sensitivity selection and observed likelihood confidence inversion with qualified signal uncertainty'],
        attempts=attempts,complete_signals_connected=0,HiggsTools_predictions_constructed=0,
        physical_higgs='UNKNOWN',exclusion=None,global_acceptance=None)
    sources = {str(p.relative_to(n.ROOT)):n.sha(p) for p in
               [n.HERE/x for x in ('neutral_widths.py','neutral_study.py','test_neutral_widths.py','native_neutral_vertices.m',
                                  'SUSHI_EVIDENCE.json','SUSHI_SOURCE_MANIFEST.json','COVERAGE.json','SOURCE_MANIFEST.json')]
               + sorted((n.HERE/'neutral_receipts').glob('*')) if p.is_file()}
    evidence = dict(status='HIGGS_SCOPED_SEARCH_BLOCKED',benchmarks=n.jsonable(cases),
        declared_accuracy='Leading one-loop gamma gamma in common physical tree inputs; tree general leptons/charged-W/u,d; HDECAY 6.60 channel-specific QCD quark/gg and neutral/vector approximations. Incomplete mixed-accuracy sum, no total precision claimed.',
        sources=sources,production_reexecuted=False,B_reexecuted=False,
        physical_higgs='UNKNOWN',exclusion=None,global_acceptance=None,final_scan_authorized=False)
    dump(out/'NEUTRAL_WIDTH_EVIDENCE.json',evidence)
    dump(out/'OBSERVED_SEARCH_COVERAGE.json',search)


if __name__=='__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True)
    run(ap.parse_args().out)
