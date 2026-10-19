"""D1 large joined 300-Zee-flavor-configurations cohort regression controls.

These tests exercise source consistency, neuron mass closure and hard
provenance gates WITHOUT turning any partial LFV result into an exclusion.
"""
from __future__ import annotations
from pathlib import Path
import json
import math
import tempfile
import unittest
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))

from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix,antisymmetric_f_with_null_condition,
    solve_lepton_yukawa,scalar_kappa,reconstruct_neutrino,
)
from gateB2_zee_neutrino_family_scan import subset_lfv
from zee_gateD1_joint_300_neutrino_lfv_inventory import (
    STATUS,classify_theory_cases,verify_c5,load_cohort,
    candidate_flavor,summarize
)
from zee_gateC1_joined_uv_pilot import digest

def example_point():
    return {
        'id':'D1_SYNTHETIC_NOT_ALLOWED',
        'mH1':300.,'mH2':700.,'mh2':580.7,
        'ma':633.7,'alpha':1.398,'beta':1.394,'gamma':1.089
    }

def pair(x):
    z=np.asarray(x,complex)
    return {'real':z.real.tolist(),'imag':z.imag.tolist()}

def example_solution(p):
    target,_=target_neutrino_matrix()
    f,_=antisymmetric_f_with_null_condition(target)
    y,rank,_=solve_lepton_yukawa(
        f,target,kappa=scalar_kappa(p['mH1'],p['mH2'],p['gamma']))
    assert rank==5
    closure=float(np.max(abs(reconstruct_neutrino(
        f,y,kappa=scalar_kappa(p['mH1'],p['mH2'],p['gamma']))-target)))
    rates,ratios=subset_lfv(p,f,y)
    return {
        'candidate_id':p['id'],'f':pair(f),'Y':pair(y),
        'status':'NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED',
        'max_abs_f':float(np.max(abs(f))),
        'max_abs_Y':float(np.max(abs(y))),
        'mH1':p['mH1'],'mH2':p['mH2'],'gamma':p['gamma'],
        'neutrino_matrix_closure_eV':closure,
        'partial_LFV_rates_NOT_FULL':rates,
        'partial_LFV_ratios_NOT_EXCLUSION':ratios,
        'partial_LFV_score_NOT_EXCLUSION':max(ratios.values())
    }

class D1JointFlavorTests(unittest.TestCase):
    def test_neutrino_closed_backend_coherent_one_loop_and_BZ(self):
        p=example_point();s=example_solution(p)
        result=candidate_flavor(p,s,1)
        self.assertLess(result['neutrino_closure_eV'],1e-9)
        self.assertEqual(set(result['radiative_channels']),{
            'mu_to_e_gamma','tau_to_mu_gamma','tau_to_e_gamma'})
        self.assertTrue(np.isfinite(
            result['joint_incomplete_LFV_score_NOT_EXCLUSION']))
        self.assertEqual(result['experimental_LFV_allowed_or_excluded'],'UNKNOWN')
        self.assertEqual(result['mu_e_conversion'],'NOT_COMPUTED')
        self.assertEqual(result['full_two_loop_LFV'],'NOT_COMPUTED')

    def test_tree_threelepton_backend_connected(self):
        p=example_point();s=example_solution(p)
        result=candidate_flavor(p,s,1)
        self.assertIn('mu_to_3e_tree',result['neutral_3lepton_tree_only_rates'])
        self.assertIn('tau_to_3mu_tree',result['neutral_3lepton_tree_only_rates'])

    def test_missing_bz_diagrams_never_labeled_complete(self):
        p=example_point();s=example_solution(p)
        result=candidate_flavor(p,s,1)
        self.assertTrue(result['photon_BZ_amplitudes_can_interfere_with_one_loop'])
        self.assertEqual(result['PMNS_likelihood'],
                         'NOT_EVALUATED_FIXED_CENTRAL_TARGET_ONLY')

    def test_negative_control_wrong_candidate_id(self):
        p=example_point();s=example_solution(p)
        s['candidate_id']='B4_WRONG'
        with self.assertRaisesRegex(ValueError,'mismatch'):
            candidate_flavor(p,s,1)

    def test_negative_control_wrong_gamma(self):
        p=example_point();s=example_solution(p)
        s['gamma']+=.05
        with self.assertRaisesRegex(ValueError,'gamma'):
            candidate_flavor(p,s,1)

    def test_negative_control_corrupted_neutrino_solution(self):
        p=example_point();s=example_solution(p)
        s['Y']['real'][0][0]+=1.
        with self.assertRaisesRegex(ValueError,'do not reconstruct requested neutrino matrix'):
            candidate_flavor(p,s,1)

    def test_negative_control_unsafe_allowed_status(self):
        p=example_point();s=example_solution(p)
        s['status']='ALLOWED'
        with self.assertRaisesRegex(ValueError,'B2 status'):
            candidate_flavor(p,s,1)

    def test_negative_control_nonperturbative_f(self):
        p=example_point();s=example_solution(p)
        s['f']['real'][0][1]=20.
        with self.assertRaises(ValueError):
            candidate_flavor(p,s,1)

    def test_C4_and_C5_classification_two_scalar_variants(self):
        c4={};c5={}
        for name in ('both_lh1_l1_1','both_lh0p4_l1_0p5'):
            c4[('TEST',name)]={'both_running_theory_screens_pass':True}
            c5[('TEST',name)]={'C4_running_theory_pass':True,
              'C5_deeper_witness':False,
              'C5_search_status':'NO_DEEPER_WITNESS_FOUND_NOT_GLOBAL_CERTIFICATE'}
        classified=classify_theory_cases('TEST',c4,c5)
        self.assertEqual(sum(x['scalar_only_candidate_for_further_flavor_work']
                             for x in classified.values()),2)
        self.assertTrue(all(not x['explicit_deeper_charge_breaking_witness']
                            for x in classified.values()))

    def test_C5_charge_breaking_witness_prevents_theory_candidate_label(self):
        c4={};c5={}
        for name in ('both_lh1_l1_1','both_lh0p4_l1_0p5'):
            c4[('TEST',name)]={'both_running_theory_screens_pass':True}
            c5[('TEST',name)]={'C4_running_theory_pass':True,
              'C5_deeper_witness':True,
              'C5_search_status':'EXPLICIT_DEEPER_TREE_POTENTIAL_WITNESS'}
        classified=classify_theory_cases('TEST',c4,c5)
        self.assertFalse(any(x['scalar_only_candidate_for_further_flavor_work']
                             for x in classified.values()))

    def test_C4_C5_status_disagreement_fails_closed(self):
        c4={};c5={}
        for name in ('both_lh1_l1_1','both_lh0p4_l1_0p5'):
            c4[('TEST',name)]={'both_running_theory_screens_pass':True}
            c5[('TEST',name)]={'C4_running_theory_pass':False,
              'C5_deeper_witness':False,
              'C5_search_status':'NO_DEEPER_WITNESS_FOUND_NOT_GLOBAL_CERTIFICATE'}
        with self.assertRaisesRegex(ValueError,'C4/C5'):
            classify_theory_cases('TEST',c4,c5)

    def test_300_aggregate_has_no_physical_acceptance_claim(self):
        fake=[];models={}
        for n in range(30):
            name=f'B4_{n:07d}'
            models[name]={
                'both_lh1_l1_1':{
                    'scalar_only_candidate_for_further_flavor_work':n<26},
                'both_lh0p4_l1_0p5':{
                    'scalar_only_candidate_for_further_flavor_work':n<27}}
            for rank in range(1,11):
                fake.append({
                    'candidate_id':name,'solution_rank_original_B2':rank,
                    'joint_incomplete_LFV_score_NOT_EXCLUSION':float(rank),
                    'stored_B2_partial_LFV_score_NOT_EXCLUSION':float(rank),
                    'radiative_channels':{'mu_to_e_gamma':{
                        'one_loop_plus_fermion_photon_BZ_subset_ratio_NOT_EXCLUSION':
                        float(rank)}}})
        rows,summary=summarize(fake,models)
        self.assertEqual(summary['spectra'],30)
        self.assertEqual(summary['independent_complex_neutrino_solutions'],300)
        self.assertEqual(summary['unique_spectra_with_theory_screens_no_vacuum_witness'],27)
        self.assertTrue(summary['no_full_LFV_exclusion_or_validation'])
        self.assertTrue(summary['B2_sample_partially_ranked_and_not_statistical_prior'])
        self.assertEqual(len(rows),30)

    def test_300_aggregate_new_ranking_by_partial_amplitudes(self):
        name='B4_A'
        models={name:{'both_lh1_l1_1':{
            'scalar_only_candidate_for_further_flavor_work':True},
            'both_lh0p4_l1_0p5':{
            'scalar_only_candidate_for_further_flavor_work':False}}}
        cases=[{
            'candidate_id':name,'solution_rank_original_B2':i,
            'joint_incomplete_LFV_score_NOT_EXCLUSION':2. if i==1 else .1,
            'stored_B2_partial_LFV_score_NOT_EXCLUSION':float(i),
            'radiative_channels':{'mu_to_e_gamma':{
                'one_loop_plus_fermion_photon_BZ_subset_ratio_NOT_EXCLUSION':.1}}
        } for i in (1,2)]
        ranked,summarized=summarize(cases,models)
        self.assertEqual(ranked[0]['new_best_incomplete_LFV_rank'],2)
        self.assertTrue(ranked[0]['min_joint_partial_diagnostic_below_one_NOT_A_PASS'])

    def test_C5_provenance_60_cases_source_checksum(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            files={name:root/f'{name}.json' for name in ('B4','B2','C2','C3','C4')}
            for k,v in files.items():v.write_text('fixture')
            target=root/'C5.json'
            rows=[{'candidate_id':f'B4_{i:07d}','variant':v}
                  for i in range(30)
                  for v in ('both_lh1_l1_1','both_lh0p4_l1_0p5')]
            target.write_text(json.dumps({
              'status':'GATE_C5_NUMERICAL_FULL_ZEE_CHARGE_BREAKING_VACUUM_NOT_ALLOWED',
              'tested':60,'rows':rows,
              'inputs_sha256':{k:digest(v) for k,v in files.items()}
            }))
            got=verify_c5(target,*files.values())
            self.assertEqual(len(got),60)
            files['C4'].write_text('changed')
            with self.assertRaisesRegex(ValueError,'C5 completed report'):
                verify_c5(target,*files.values())

    def test_b2_cohort_exact_30x10_instead_of_double_counting_variants(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            source=root/'b4.csv';target=root/'b2.json'
            head='id,mH1,mH2,mh2,ma,alpha,beta,gamma,m12sq\n'
            csv_rows=''.join(
                f'B4_{i:07d},300,700,580.7,633.7,1.398,1.394,1.089,57700\n'
                for i in range(30))
            source.write_text(head+csv_rows)
            sol=json.dumps({f'B4_{i:07d}':[
                {'candidate_id':f'B4_{i:07d}'} for j in range(10)]
                for i in range(30)})
            target.write_text(sol)
            pts,sols=load_cohort(source,target)
            self.assertEqual(len(pts),30)
            self.assertEqual(sum(len(v) for v in sols.values()),300)
            data=json.loads(target.read_text())
            del data['B4_0000000'][0]
            target.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'TEN'):
                load_cohort(source,target)

if __name__=='__main__':
    unittest.main()
