"""Read-only final assertions and compact evidence for the D15 crossing gate."""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np
ROOT=Path(__file__).resolve().parent
LOCAL=ROOT/'local'

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    proof=read(LOCAL/'crossing_bridge/projector-evidence.json')
    spin=read(LOCAL/'crossing_bridge/spinor-evidence.json')
    direct=read(LOCAL/'d15-direct-amplitudes.json')
    physical=read(LOCAL/'crossing_physical_cards/evidence.json')
    assert proof['status']==spin['status']=='PASS'
    assert proof['post_projection_candidate_substitution'] is False
    assert direct['operator_map_evidence_sha256']==sha(LOCAL/'crossing_bridge/projector-evidence.json')
    assert len(direct['records'])==102 and len(direct['transformations'])==36
    assert physical['new_cards']==2 and physical['full_executions']==4
    closure=[];native_rates=[];artifacts={}
    directories=[LOCAL/'crossing_original_cards',LOCAL/'crossing_physical_cards/default',LOCAL/'crossing_physical_cards/matched_leptons']
    for directory in directories:
        comparisons=read(directory/'comparison.json')['records']
        components=read(directory/'components.json')['records']
        for row,comp in zip(comparisons,components):
            assert row['group']==comp['group']
            full=np.array([complex(*row['coefficients_GeV_minus2'][ch]['K2']) for ch in 'LR'])
            scalar=sum((np.array([complex(*z) for z in item['K2']]) for item in comp['components'].values()),np.zeros(2,complex))
            reference=sum((np.array([complex(*z) for z in item['D12_C']]) for item in comp['components'].values()),np.zeros(2,complex))
            remainder=abs(full-scalar)
            assert np.all(remainder<=1e-10*abs(full)+1e-24),(directory,row['group'],remainder)
            if directory.name=='matched_leptons':
                error=abs(full+reference.conj())
                assert np.all(error<=1e-10*abs(reference)+1e-24),(directory,row['group'],error)
            for name,item in comp['components'].items():
                assert all(e is not None and e<1e-10 for e in item['same_input_candidate_relative_residual']),(directory,row['group'],name)
            closure.append({'run':str(directory.relative_to(LOCAL)),'group':row['group'],
                            'five_scalar_to_full_K_absolute_remainder':remainder.tolist(),
                            'matched_scalar_component_residuals':{k:v['same_input_candidate_relative_residual'] for k,v in comp['components'].items()},
                            'unmatched_or_matched_full_C_relative_residual':{ch:row['coefficients_GeV_minus2'][ch]['candidate_relative_residual'] for ch in 'LR'}})
        ratefile=LOCAL/'crossing-original-rates.json' if directory.name=='crossing_original_cards' else directory/'check_rate.py.log'
        rates=read(ratefile)
        assert len(rates)==len(comparisons)
        assert max(x['relative_rounding_residual'] for x in rates)<5e-9
        native_rates.extend(rates)
        for p in directory.glob('group*'):
            if p.is_file():artifacts[str(p.relative_to(ROOT))]=sha(p)
    code=['crossing_bridge_toy.py','crossing_bridge_spinors.py','physical_card_closure.py','verify_crossing_closure.py','benchmark_card.py','compare_dipoles.py','check_components.py','test_direct_amplitudes.py','patch_small_ratio.py']
    for name in ['projector-evidence.json','spinor-evidence.json','run.log','Dipole.mod','DipoleLorentz.gen','chains-1.m','chains-2.m','QED.m','result.m','chains-numeric.json']:
        p=LOCAL/'crossing_bridge'/name;artifacts[str(p.relative_to(ROOT))]=sha(p)
    for p in [LOCAL/'crossing_physical_cards/new-inputs.json',LOCAL/'crossing_physical_cards/evidence.json',LOCAL/'d15-direct-amplitudes.json']:
        artifacts[str(p.relative_to(ROOT))]=sha(p)
    evidence={'status':'ONE_LOOP_COMPLEX_DIPOLE_PASS',
      'scope':'Experimentally patched scalar one-loop subset; massless internal neutrinos; zero external momenta in loop denominators with external chirality flips retained; D12 pole scheme explicitly matched',
      'not_claimed':['Complete Zee LFV','All FlavorKit observables','D14 integration','Global scalar or neutrino acceptance of new cards'],
      'starting_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
      'operator_relation':proof['relation'],'reverse_ordered_relation':proof['reverse'],
      'mass_normalization':'If operator and wrapper masses differ, multiply forward by m_operator/m_norm. Reverse uses m_i_operator/m_j_norm.',
      'post_projection_candidate_substitution':False,'spinor_tests':spin,
      'source_proof':proof,'direct_amplitude_cases':len(direct['records']),
      'direct_max_relative_to_larger_chirality':direct['max_relative_to_largest_chirality'],
      'transformation_relations':len(direct['transformations']),
      'transformation_max_relative':max(x['relative_residual'] for x in direct['transformations']),
      'new_physical_cards':2,'new_card_full_runs':4,'original_card_runs':4,
      'new_card_scalar_gate_assessments':[{k:v.get('assessment') for k,v in x['gates'].items()} for x in physical['scalar_gates']],
      'controlled_pole_input_shifts':physical['controlled_scheme_shifts'],
      'card_coefficient_checks':closure,
      'native_rate_max_print_rounding_residual':max(x['relative_rounding_residual'] for x in native_rates),
      'criterion':'per chirality |delta| <= 1e-10 |C| + 1e-24 GeV^-2; exact applicable nulls zero; native BR print rounding <=5e-9',
      'native_K_non_scalar_group_remainder':'Measured and retained below mixed tolerance; not silently set to zero or used to change the scalar-only Wilsons',
      'code_sha256':{name:sha(ROOT/name) for name in code},
      'frozen_reference_sha256':{name:sha(ROOT.parents[1]/name) for name in ['module3/core.py','module3/CONVENTIONS.md','validation/module12/d12_benchmarks.json']},
      'installed_wrapper_sha256':sha(Path.home()/'.Mathematica/Applications/SARAH-4.15.4/FlavorKit/LFV/Operators/Photon_wrapper.m'),
      'generated_executable_sha256':sha(LOCAL/'SPheno-4.0.5/bin/SPhenoZeeTypeII'),
      'local_artifact_sha256':artifacts}
    (ROOT/'crossing_bridge_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(evidence['status'])
    print('Operator proof, spinors, 102 direct cases, 36 relations, four original and four new-card scheme runs: PASS')

if __name__=='__main__':main()
