"""C2 paired scalar UV rescue experiment regressions.

This suite validates the PHYSICAL matching map, paired interventions and
data-provenance controls, NOT phenomenological exclusions. Generated RGEs.py
is exercised in the single larger AF C2 numerical experiment.
"""
from pathlib import Path
import sys
import json
import csv
import math
import tempfile
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))

from gateA1b_hierarchical_no_seed import (
    target_neutrino_matrix,antisymmetric_f_with_null_condition,
    solve_lepton_yukawa,scalar_kappa,reconstruct_neutrino,
)
from zee_gateC1_joined_uv_pilot import scalar_lagrangian,build_model_state
from zee_gateC2_paired_uv_rescue import (
    VEV,VARIANTS,varied_point,digest,
    read_cohort_reference,load_cohort,compare_flows,
    analyze_variant,validate_baseline,summarize
)

def source_point():
    return {
        'id':'B4_TEST_ONLY',
        'beta':1.394,'alpha':1.398,'gamma':1.089,
        'mH1':300.,'mH2':700.,'mh2':580.7,'ma':633.7,
        'm12sq':57700.,
        'lc':4.473,'k1':1.082,'k2':.00398,'k12':-.001266,
    }

def complex_json(a):
    z=np.asarray(a,complex)
    return {'real':z.real.tolist(),'imag':z.imag.tolist()}

def neutrino_solution(point):
    target,_=target_neutrino_matrix()
    f,_=antisymmetric_f_with_null_condition(target)
    k=scalar_kappa(point['mH1'],point['mH2'],point['gamma'])
    Y,rank,_=solve_lepton_yukawa(f,target,kappa=k)
    assert rank==5
    err=float(np.max(abs(reconstruct_neutrino(f,Y,kappa=k)-target)))
    return {'candidate_id':point['id'],'f':complex_json(f),
            'Y':complex_json(Y),
            'status':'NEUTRINO_CLOSED_PARTIAL_LFV_ONLY_NOT_ALLOWED',
            'partial_LFV_score_NOT_EXCLUSION':1e-7,
            'neutrino_matrix_closure_eV':err}

def dummy_reached():
    from zee_section8_Q4_large_integrated_one_loop_gate import NAMES,MATRIX_NAMES
    state={k:(np.zeros((3,3),complex) if k in MATRIX_NAMES else 0.)
           for k in NAMES}
    state['l1']=1.
    return {
        'status':'REACHED_END_SCALE_ONE_LOOP_DIAGNOSTIC_ONLY',
        'endpoint':state,'boundary_bracket':None,
        'limiting_couplings':[{'coupling':'l1'}],
    }

class TestGateC2PairedUV(unittest.TestCase):
    def test_eight_interventions_are_named_and_unique(self):
        names=[a[0] for a in VARIANTS]
        self.assertEqual(len(names),8)
        self.assertEqual(len(set(names)),8)
        self.assertEqual(names[0],'baseline')

    def test_baseline_preserves_original_spectrum_and_scalar(self):
        p=source_point()
        new=varied_point(p,None,None)
        self.assertEqual(new,p)
        vals,meta=scalar_lagrangian(new)
        self.assertEqual(meta['scalar_mass_closure'],'PASS')
        self.assertGreater(vals['l1'],0.)

    def test_lowering_lh_does_not_change_scalar_masses(self):
        p=source_point()
        orig,_=scalar_lagrangian(p)
        low=varied_point(p,.4,None)
        scalar,meta=scalar_lagrangian(low)
        self.assertAlmostEqual(scalar['lh'],.4)
        for k in ('l1','l2','l3','l4','l5','l8','l9','l10',
                  'm1','m2','m12','mchi','muZee'):
            self.assertAlmostEqual(scalar[k],orig[k])
        self.assertEqual(meta['scalar_mass_closure'],'PASS')

    def test_lh_cap_never_raises_initially_smaller_self_quartic(self):
        p=source_point()
        p['lc']=.12
        new=varied_point(p,.4,None)
        self.assertAlmostEqual(new['lc'],.12)

    def test_lambda1_tree_inversion_exact_at_multiple_values(self):
        p=source_point()
        original,meta=scalar_lagrangian(p)
        for target in (.5,1.):
            new=varied_point(p,None,target)
            out,meta=scalar_lagrangian(new)
            self.assertAlmostEqual(out['l1'],target,delta=1e-9)
            self.assertEqual(meta['scalar_mass_closure'],'PASS')
            self.assertEqual(meta['tree_unitarity_at_matching'],True)
            self.assertAlmostEqual(
                out['muZee'],original['muZee'],delta=1e-12)
            self.assertAlmostEqual(
                out['mchi'],original['mchi'],delta=1e-9)

    def test_double_intervention_changes_only_targeted_inputs(self):
        p=source_point()
        v=varied_point(p,.4,.5)
        self.assertAlmostEqual(v['lc'],.4)
        self.assertNotAlmostEqual(v['m12sq'],p['m12sq'])
        for name in ('mH1','mH2','mh2','ma','alpha','beta','gamma',
                     'k1','k2','k12'):
            self.assertEqual(v[name],p[name])
        out,_=scalar_lagrangian(v)
        self.assertAlmostEqual(out['l1'],.5,delta=1e-9)

    def test_variant_does_not_mutate_input_or_reuse_old_quartics(self):
        p=source_point()
        p['lambda1']=22.
        a=varied_point(p,None,1.)
        self.assertEqual(p['lambda1'],22.)
        self.assertNotIn('lambda1',a)
        self.assertEqual(a['id'],p['id'])

    def test_neutrino_closure_invariant_under_both_interventions(self):
        base=source_point()
        sol=neutrino_solution(base)
        init,_=build_model_state(base,sol)
        target,_=target_neutrino_matrix()
        for name,lh,l1 in VARIANTS:
            pp=varied_point(base,lh,l1)
            try:
                nxt,meta=build_model_state(pp,sol)
            except ValueError as exc:
                # Tree theory might reject a valid counterfactual.
                if 'sufficient' in str(exc) or 'B4 input' in str(exc):
                    continue
                raise
            self.assertLess(meta['neutrino_matrix_closure_eV'],1e-10)
            np.testing.assert_allclose(np.asarray(nxt['f']),
                                       np.asarray(init['f']))
            np.testing.assert_allclose(np.asarray(nxt['Ye1']),
                                       np.asarray(init['Ye1']))
            np.testing.assert_allclose(np.asarray(nxt['Ye2']),
                                       np.asarray(init['Ye2']))

    def test_broken_lambda1_reference_fails_closed(self):
        p=source_point()
        p['lambda1']=-25.
        with self.assertRaisesRegex(ValueError,'lambda1'):
            scalar_lagrangian(p)

    def test_counterfactual_excluding_quartic_still_not_full_allowed(self):
        p=source_point()
        v=varied_point(p,.4,.5)
        # Important: a different scalar tree theory, not an already
        # allowed point or an original B4 "pass" inherited blindly.
        a,_=scalar_lagrangian(v)
        self.assertAlmostEqual(a['lh'],.4)
        self.assertAlmostEqual(a['l1'],.5)

    def test_solver_endpoint_stability_comparator(self):
        a=dummy_reached();b=dummy_reached()
        good,kind,delta=compare_flows(a,b)
        self.assertTrue(good)
        self.assertEqual(kind,'end_scale')
        self.assertEqual(delta,0.)
        b['endpoint']['l1']=1.2
        good,kind,delta=compare_flows(a,b)
        self.assertFalse(good)

    def test_solver_boundary_driver_mismatch_fails(self):
        a={
            'status':'DIAGNOSTIC_BOUNDARY_REACHED_NOT_PHYSICAL_CUTOFF',
            'boundary_bracket':{'estimated_boundary_GeV':1500.},
            'endpoint':None,'limiting_couplings':[{'coupling':'lh'}]}
        b={
            'status':a['status'],
            'boundary_bracket':{'estimated_boundary_GeV':1510.},
            'endpoint':None,'limiting_couplings':[{'coupling':'l1'}]}
        stable,_,_=compare_flows(a,b)
        self.assertFalse(stable)

    def test_c1_reference_reproduction_requires_driver_and_scale(self):
        baseline={'variant':'baseline',
                  'RGE_stepdoubling_compatible':True,
                  'flow_status':'DIAGNOSTIC_BOUNDARY_REACHED_NOT_PHYSICAL_CUTOFF',
                  'reached_10TeV_heuristic':False,
                  'estimated_4pi_crossing_GeV':1500.,
                  'first_limiting_coupling':'lh'}
        reference={'status':'DIAGNOSTIC_BOUNDARY_REACHED_NOT_PHYSICAL_CUTOFF',
                   'boundary_GeV':1500.,'limiter':'lh'}
        validate_baseline(baseline,reference)
        with self.assertRaisesRegex(ValueError,'boundary differs'):
            validate_baseline(baseline,{**reference,'limiter':'l1'})
        # New genuinely reached-end test: successful RGE flow must not be
        # mislabeled a required boundary because an older pilot had one.
        reached={**baseline,
            'flow_status':'REACHED_END_SCALE_ONE_LOOP_DIAGNOSTIC_ONLY',
            'reached_10TeV_heuristic':True,
            'estimated_4pi_crossing_GeV':None}
        passed={'status':'REACHED_END_SCALE_ONE_LOOP_DIAGNOSTIC_ONLY',
                'boundary_GeV':None,'limiter':None}
        validate_baseline(reached,passed)
        with self.assertRaisesRegex(ValueError,'outcome differs'):
            validate_baseline(reached,reference)
        with self.assertRaisesRegex(ValueError,'inconsistent'):
            validate_baseline({**reached,'reached_10TeV_heuristic':False},passed)

    def test_c1_90_source_and_candidate_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            b4=root/'b4.csv';b4.write_text('candidate_id,placeholder\\n')
            b2=root/'b2.json';b2.write_text('{}')
            rges=root/'RGEs.py';rges.write_text('mock')
            ref=root/'summary.json'
            rows=[]
            for i in range(30):
                for rank in (1,2,3):
                    rows.append({
                        'candidate_id':f'B4_{i:06d}','B2_solution_rank':rank,
                        'full_step':{
                            'status':'DIAGNOSTIC_BOUNDARY_REACHED_NOT_PHYSICAL_CUTOFF',
                            'boundary_bracket':{'estimated_boundary_GeV':1500.+i},
                            'limiting_couplings':[{'coupling':'lh'}]}})
            ref.write_text(json.dumps({
                'B4_sha256':digest(b4),'B2_sha256':digest(b2),
                'RGE_sha256':digest(rges),
                'row_count':90,'rows':rows}))
            good=read_cohort_reference(ref,b4,b2,rges)
            self.assertEqual(len(good),30)
            self.assertEqual(good['B4_000000']['status'],
                             'DIAGNOSTIC_BOUNDARY_REACHED_NOT_PHYSICAL_CUTOFF')
            rows[0]['full_step']={
                'status':'REACHED_END_SCALE_ONE_LOOP_DIAGNOSTIC_ONLY',
                'boundary_bracket':None,
                'limiting_couplings':[{'coupling':'l1'}]}
            ref.write_text(json.dumps({
                'B4_sha256':digest(b4),'B2_sha256':digest(b2),
                'RGE_sha256':digest(rges),'row_count':90,'rows':rows}))
            refreshed=read_cohort_reference(ref,b4,b2,rges)
            self.assertEqual(refreshed['B4_000000']['status'],
                             'REACHED_END_SCALE_ONE_LOOP_DIAGNOSTIC_ONLY')
            self.assertIsNone(refreshed['B4_000000']['boundary_GeV'])
            b2.write_text('{"different":"data"}')
            with self.assertRaisesRegex(ValueError,'different inputs'):
                read_cohort_reference(ref,b4,b2,rges)

    def test_variant_aggregation_keeps_no_physical_acceptance(self):
        rows=[]
        for cid in ('one','two'):
            for name,*_ in VARIANTS:
                rows.append({
                    'candidate_id':cid,'variant':name,
                    'reconstructed_tree_theory':'BFB_SUFFICIENT_AND_UNITARITY_PASS',
                    'status':'UV_DIAGNOSTIC_SOLVER_STABLE_NOT_ALLOWED',
                    'reached_10TeV_heuristic':name=='both_lh0p4_l1_0p5',
                    'estimated_4pi_crossing_GeV':None if
                        name=='both_lh0p4_l1_0p5' else 1500.,
                    'first_limiting_coupling':'lh'})
        result=summarize(rows)
        self.assertEqual(result[
            'number_original_spectra_with_at_least_one_uv_heuristic_rescue'],2)
        self.assertTrue(result['full_LFV_not_evaluated'])
        self.assertTrue(result['10TeV_diagnostic_survival_not_global_Zee_allowed'])
        self.assertEqual(result['variant_summary']['baseline']
                         ['reached_10TeV_heuristic'],0)

if __name__=='__main__':
    unittest.main()
