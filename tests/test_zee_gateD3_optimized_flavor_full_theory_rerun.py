"""D3 joined 27x2 optimized-Zee RG-theory recheck regression tests.

Covers D2->D3 source provenance, full neutrino mass and LFV roundtrip,
optimized-vs-saved Yukawa rotation, 24/48 theory classification,
explicit failure scenarios and 1% null-neutrino local sensitivity.
"""
from __future__ import annotations
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))

from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix,antisymmetric_f_with_null_condition,
    scalar_kappa,solve_lepton_yukawa,reconstruct_neutrino
)
from gateB2_zee_neutrino_family_scan import subset_lfv
from zee_gateC1_joined_uv_pilot import scalar_lagrangian,build_model_state,digest
from zee_gateC2_paired_uv_rescue import varied_point
from zee_gateD1_joint_300_neutrino_lfv_inventory import candidate_flavor
from zee_gateD2_neutrino_exact_partial_LFV_optimization import (
    STATUS as D2_STATUS,neutrino_family,make_yukawas,amplitude_subset,
    optimize_kernels_cache
)
from zee_gateD3_optimized_flavor_full_theory_rerun import (
    STATUS,verify_d2,check_flavor_input,local_lfv_robustness,classify_flow,
    summarize
)

def point():
    return {
        'id':'D3_SYNTHETIC_NOT_ALLOWED',
        'beta':1.394,'alpha':1.398,'gamma':1.089,
        'mH1':300.,'mH2':700.,'mh2':580.7,'ma':633.7,
        'm12sq':57700.,
        'lc':4.473,'k1':1.082,'k2':.00398,'k12':-.001266,
    }

def pack(m):
    m=np.asarray(m,complex)
    return {'real':m.real.tolist(),'imag':m.imag.tolist()}

def neutrino_root(p):
    target,_=target_neutrino_matrix()
    f,_=antisymmetric_f_with_null_condition(target)
    pref=scalar_kappa(p['mH1'],p['mH2'],p['gamma'])
    Y,rank,_=solve_lepton_yukawa(f,target,kappa=pref)
    if rank!=5:raise AssertionError('Unexpected rank')
    br,ratios=subset_lfv(p,f,Y)
    closure=float(np.max(abs(reconstruct_neutrino(f,Y,kappa=pref)-target)))
    return {
        'candidate_id':p['id'],
        'mH1':p['mH1'],'mH2':p['mH2'],'gamma':p['gamma'],
        'f':pack(f),'Y':pack(Y),
        'status':'NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED',
        'partial_LFV_rates_NOT_FULL':br,
        'partial_LFV_ratios_NOT_EXCLUSION':ratios,
        'partial_LFV_score_NOT_EXCLUSION':max(ratios.values()),
        'neutrino_matrix_closure_eV':closure,
    }

def fake_flow(*,reach=True,bfb=True,unitary=True,cross=None,witness=False):
    return {
        'reached_end_scale':reach,
        'BFB_sufficient_at_all_sampled_steps':bfb,
        'tree_unitarity_8pi_at_all_sampled_steps':unitary,
        'BFB_negative_witness':witness,
        'first_tree_unitarity_crossing':
            None if cross is None else {'first_failure_GeV':float(cross)},
    }

class TestD3OptimizedFullTheory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        optimize_kernels_cache()

    def test_D2_previous_27_model_54_optimization_provenance(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)
            inputs={k:base/f'{k}.txt' for k in (
                'B4','B2','C2','C3','C4','C5','D1')}
            for k,v in inputs.items():v.write_text(k+'-fixture')
            p=base/'D2.json'
            rows=[]
            chosen={}
            for i in range(27):
                name=f'B4_{i:07d}'
                rows.append({'candidate_id':name,
                    'best_optimized_from_rank':1,
                    'new_best_partial_score_NOT_EXCLUSION':1.e-5})
                chosen[name]={
                    'parent_rank':1,
                    'chosen':{'solution':{'candidate_id':name},'best_score':1.e-5}}
            p.write_text(json.dumps({
                'status':D2_STATUS,'tested_spectra':27,'optimization_runs':54,
                'rows':rows,'optimized_full_f_Y_and_partial_flavor_provenance':chosen,
                'inputs_SHA256':{k:digest(path) for k,path in inputs.items()}
            }))
            out=verify_d2(p,*inputs.values())
            self.assertEqual(len(out),27)
            inputs['B2'].write_text('altered')
            with self.assertRaisesRegex(ValueError,'source-provenance mismatch'):
                verify_d2(p,*inputs.values())

    def test_duplicate_D2_entry_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)
            inputs=[base/f'{i}.txt' for i in range(7)]
            for i,p in enumerate(inputs):p.write_text(str(i))
            details={f'C{i}':{'parent_rank':1,'chosen':{
                'best_score':1e-5,'solution':{'candidate_id':f'C{i}'}}}
                for i in range(27)}
            rows=[{'candidate_id':f'C{i}','best_optimized_from_rank':1,
                   'new_best_partial_score_NOT_EXCLUSION':1e-5}
                  for i in range(27)]
            rows[3]['candidate_id']='C0'
            doc=base/'D2.json'
            doc.write_text(json.dumps({
                'status':D2_STATUS,'tested_spectra':27,
                'optimization_runs':54,
                'rows':rows,
                'optimized_full_f_Y_and_partial_flavor_provenance':details,
                'inputs_SHA256':{k:digest(v) for k,v in zip(
                    ('B4','B2','C2','C3','C4','C5','D1'),inputs)}
            }))
            with self.assertRaisesRegex(ValueError,'duplicate'):
                verify_d2(doc,*inputs)

    def test_D2_partial_score_recalculation_matches_previous_D1(self):
        from unittest.mock import patch
        p=point();sol=neutrino_root(p)
        # The synthetic A1B starting root need not have score <1.
        # Simulate a valid D2-optimized D1 result in the threshold logic,
        # while D2's own separate test suite checks actual backend equality.
        checked={'joint_incomplete_LFV_score_NOT_EXCLUSION':0.03,
                 'neutrino_closure_eV':1e-16}
        with patch('zee_gateD3_optimized_flavor_full_theory_rerun.candidate_flavor',
                   return_value=checked) as mock:
            got=check_flavor_input(
                p,{'new_best_partial_score_NOT_EXCLUSION':0.03},
                {'solution':sol})
        self.assertEqual(got,checked)
        mock.assert_called_once()

    def test_corrupted_D2_score_rejected(self):
        from unittest.mock import patch
        p=point();sol=neutrino_root(p)
        with patch('zee_gateD3_optimized_flavor_full_theory_rerun.candidate_flavor',
                   return_value={
                       'joint_incomplete_LFV_score_NOT_EXCLUSION':0.08,
                       'neutrino_closure_eV':1e-16}):
            with self.assertRaisesRegex(ValueError,'D2/D1'):
                check_flavor_input(
                    p,{'new_best_partial_score_NOT_EXCLUSION':0.001},
                    {'solution':sol})

    def test_partial_LFV_above_one_never_called_revalidated(self):
        from unittest.mock import patch
        p=point();sol=neutrino_root(p)
        with patch('zee_gateD3_optimized_flavor_full_theory_rerun.candidate_flavor',
                   return_value={
                       'joint_incomplete_LFV_score_NOT_EXCLUSION':1.01,
                       'neutrino_closure_eV':1e-16}):
            with self.assertRaisesRegex(ValueError,'does not meet'):
                check_flavor_input(
                    p,{'new_best_partial_score_NOT_EXCLUSION':1.01},
                    {'solution':sol})

    def test_new_optimized_input_maintains_tree_scalar_matching(self):
        p=point();sol=neutrino_root(p)
        for cap,target in ((1.,1.),(.4,.5)):
            modified=varied_point(p,cap,target)
            scalar,closure=scalar_lagrangian(modified)
            self.assertAlmostEqual(scalar['l1'],target,delta=1e-9)
            state,info=build_model_state(modified,sol)
            self.assertEqual(info['scalar_mass_closure'],'PASS')
            self.assertLess(info['neutrino_matrix_closure_eV'],1e-9)
            self.assertEqual(set(scalar).difference(state),set())

    def test_optimized_neutrino_Yukawas_change_beta_initial_conditions(self):
        p=point();sol=neutrino_root(p)
        family=neutrino_family(p,sol)
        x=family['starting_coords'].copy()
        x[0]+=.31;x[1]+=.35
        f,Y=make_yukawas(family,x)
        changed=dict(sol)
        changed['f']=pack(f);changed['Y']=pack(Y)
        changed['neutrino_matrix_closure_eV']=float(np.max(abs(
            reconstruct_neutrino(f,Y,kappa=family['kappa'])-family['target'])))
        modified=varied_point(p,.4,.5)
        orig,_=build_model_state(modified,sol)
        other,_=build_model_state(modified,changed)
        self.assertGreater(float(np.linalg.norm(other['f']-orig['f'])),1e-6)
        self.assertGreater(float(np.linalg.norm(other['Ye1']-orig['Ye1'])),1e-6)
        self.assertAlmostEqual(other['l1'],orig['l1'])
        self.assertAlmostEqual(other['lh'],orig['lh'])

    def test_local_1percent_probe_preserves_neutrino(self):
        p=point();sol=neutrino_root(p)
        result=local_lfv_robustness(p,sol,seed=20261019,trials=4)
        self.assertEqual(len(result),2)
        self.assertEqual(result[0]['relative_null_coordinate_perturbation'],1e-3)
        self.assertEqual(result[1]['relative_null_coordinate_perturbation'],1e-2)
        self.assertTrue(all(e['trials_attempted']==4 for e in result))
        self.assertTrue(all(e['max_score'] is None or e['max_score']>=0
                            for e in result))

    def test_grid_agrees_on_10TeV_pass(self):
        a=fake_flow()
        good,relative=classify_flow(a,fake_flow())
        self.assertTrue(good)
        self.assertIsNone(relative)

    def test_grid_agrees_on_unitarity_failure(self):
        a=fake_flow(unitary=False,cross=5700.)
        b=fake_flow(unitary=False,cross=5750.)
        good,relative=classify_flow(a,b)
        self.assertFalse(good)
        self.assertLess(relative,.05)

    def test_grid_unitarity_crossing_discrepancy_fails(self):
        a=fake_flow(unitary=False,cross=5700.)
        b=fake_flow(unitary=False,cross=7700.)
        with self.assertRaisesRegex(ValueError,'crossing mismatch'):
            classify_flow(a,b)

    def test_grid_bfb_certification_conflict_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'classification changed'):
            classify_flow(fake_flow(bfb=True),fake_flow(bfb=False))

    def test_grid_perturbativity_inconsistent_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'reach disagreement'):
            classify_flow(fake_flow(reach=False),fake_flow(reach=True))

    def test_grid_negative_witness_disagreement_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'witness disagreement'):
            classify_flow(fake_flow(witness=True),fake_flow(witness=False))

    def test_54_cases_count_and_deduplicated_spectrum_summary(self):
        rows=[]
        for i in range(27):
            for v in ('both_lh1_l1_1','both_lh0p4_l1_0p5'):
                rows.append({
                    'candidate_id':str(i),'variant':v,
                    'optimized_RGE_reaches_10TeV':True,
                    'optimized_BFB_sufficient_to_10TeV':True,
                    'optimized_55channel_unitarity_to_10TeV':True,
                    'D3_joint_running_theory_screen_pass':i%2==0,
                    'C5_no_deeper_witness_NOT_global_certification':True,
                    'old_C4_rank1_family_running_screen_pass':True,
                })
        summary=summarize(rows)
        self.assertEqual(
            summary['neutrino_optimized_theory_spectra_tested'],27)
        self.assertEqual(
            summary['unique_spectra_with_at_least_one_revalidated_theory_variant'],14)
        self.assertTrue(summary['full_LFV_and_other_experimental_constraints_unknown'])

if __name__=='__main__':
    unittest.main()
