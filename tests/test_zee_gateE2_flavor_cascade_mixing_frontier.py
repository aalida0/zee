"""Gate E2 robust 27-spectrum flavor-versus-Z-cascade vertex controls.

Prove Wilson-mixing polynomial interpolation and independent gamma
evaluation agreement; enforce fixed-mass counterfactual interpretation
(no B->Xs gamma exclusion or cascade BR claim). Verify provenance.
"""
from pathlib import Path
import json
import math
import tempfile
import unittest
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from zee_gateC1_joined_uv_pilot import digest
from zee_gateE2_flavor_cascade_mixing_frontier import (
    SOURCE_STATUS,STATUS,FLOOR_FACTORS,
    zee_z_vertex_strength_squared,mixing_quadratic_from_e1,
    eval_quadratic,optimum_under_Z_vertex_floor,verify_e1,
    calculate_row,summarize
)

def model_data(name='B4_TEST'):
    gamma=1.10
    coeff=(3.65e-4,2.e-5,1.e-5)
    x=math.cos(gamma)**2
    pure_light=sum(coeff)
    old=coeff[0]+coeff[1]*x+coeff[2]*x*x
    return {
        'candidate_id':name,'mH1':250.,
        'mH2':700.,'tanbeta':5.5,'gamma':gamma,
        'pure_light_BR':pure_light,
        'pure_heavy_BR':coeff[0],
        'SM_BR_legacy':3.38e-4,
        'B_to_Xs_gamma_legacy_Zee_BR':old,
        'NP_delta_BR_legacy':old-3.38e-4,
        'all_source_pinned_endpoints_consistent':True,
    }

class TestE2FlavorCascadeFrontier(unittest.TestCase):
    def test_Z_vertex_zero_at_both_pure_endpoints(self):
        self.assertAlmostEqual(zee_z_vertex_strength_squared(0.),0.)
        self.assertAlmostEqual(zee_z_vertex_strength_squared(math.pi/2),0.)

    def test_Z_vertex_maximum_at_equal_doublet_singlet_mixing(self):
        self.assertAlmostEqual(
            zee_z_vertex_strength_squared(math.pi/4),1.,places=14)

    def test_fixed_E1_pure_and_mixed_three_point_interpolation(self):
        r=model_data()
        a,b,c=mixing_quadratic_from_e1(r)
        self.assertAlmostEqual(a,3.65e-4,delta=1e-14)
        self.assertAlmostEqual(b,2.e-5,delta=1e-14)
        self.assertAlmostEqual(c,1.e-5,delta=1e-14)
        for gamma in (0.,r['gamma'],math.pi/2):
            self.assertAlmostEqual(
                eval_quadratic((a,b,c),gamma),
                a+b*math.cos(gamma)**2+c*math.cos(gamma)**4,
                delta=1e-14)

    def test_nontrivial_27_gamma_mixing_quadratic(self):
        row=model_data()
        coeff=mixing_quadratic_from_e1(row)
        for g in (.13,.41,.79,1.33):
            x=math.cos(g)**2
            expected=3.65e-4+2e-5*x+1e-5*x*x
            self.assertAlmostEqual(eval_quadratic(coeff,g),expected,
                                   delta=1e-14)

    def test_interpolation_rejects_nearly_pure_original(self):
        row=model_data()
        row['gamma']=1e-8
        with self.assertRaisesRegex(ValueError,'pure-state boundary'):
            mixing_quadratic_from_e1(row)

    def test_optimal_flavor_at_full_original_Z_strength(self):
        r=model_data()
        p=mixing_quadratic_from_e1(r)
        got=optimum_under_Z_vertex_floor(p,r['gamma'],1.)
        self.assertAlmostEqual(got['minimum_legacy_BR'],
                               r['B_to_Xs_gamma_legacy_Zee_BR'],delta=1e-14)
        self.assertAlmostEqual(
            got['optimal_Z_vertex_squared'],
            zee_z_vertex_strength_squared(r['gamma']),delta=1e-12)

    def test_50_percent_Z_vertex_retention_allows_lower_legacy_rate(self):
        r=model_data()
        p=mixing_quadratic_from_e1(r)
        got=optimum_under_Z_vertex_floor(p,r['gamma'],.5)
        self.assertLess(got['minimum_legacy_BR'],
                        r['B_to_Xs_gamma_legacy_Zee_BR'])
        self.assertGreaterEqual(
            got['optimal_Z_vertex_squared'],
            .5*zee_z_vertex_strength_squared(r['gamma'])-1e-12)

    def test_no_Z_vertex_floor_allows_pure_heavy(self):
        r=model_data()
        p=mixing_quadratic_from_e1(r)
        got=optimum_under_Z_vertex_floor(p,r['gamma'],0.)
        self.assertAlmostEqual(got['minimum_legacy_BR'],r['pure_heavy_BR'],
                               delta=1e-14)
        self.assertAlmostEqual(got['optimal_gamma_rad'],math.pi/2)

    def test_Z_floor_invalid_rejected(self):
        with self.assertRaisesRegex(ValueError,'retention'):
            optimum_under_Z_vertex_floor((.0003,.00002,.00001),1.,-1.)
        with self.assertRaisesRegex(ValueError,'retention'):
            optimum_under_Z_vertex_floor((.0003,.00002,.00001),1.,1.1)

    def test_nonconvex_quadratic_solution_is_boundary_not_spurious_peak(self):
        p=(.00034,.00003,-.00004)
        sol=optimum_under_Z_vertex_floor(p,1.1,.4)
        zmin=.4*zee_z_vertex_strength_squared(1.1)
        self.assertGreaterEqual(sol['optimal_Z_vertex_squared'],zmin-1e-12)
        x=sol['optimal_light_doublet_fraction_cos2gamma']
        dx=.01
        if 0<=x-dx<=1 and 4*(x-dx)*(1-(x-dx))>=zmin:
            self.assertLessEqual(sol['minimum_legacy_BR'],
                                 p[0]+p[1]*(x-dx)+p[2]*(x-dx)**2+1e-13)

    def test_direct_vendor_validation_4_angles_and_all_frontiers(self):
        r=model_data()
        def fake_eval(exe,m1,m2,g,t):
            xx=math.cos(g)**2
            return {'full_Zee_BR':3.65e-4+2e-5*xx+1e-5*xx*xx},'MOCK'
        with patch('zee_gateE2_flavor_cascade_mixing_frontier.evaluate',
                   side_effect=fake_eval) as monitored:
            out=calculate_row(r,Path('/not/executed'))
        self.assertEqual(monitored.call_count,4)
        self.assertEqual(len(out['retained_Z_vertex_coupling_frontier']),5)
        self.assertEqual(len(out['direct_A1V_vendor_checks']),4)
        self.assertLess(out['maximum_direct_vendor_crosscheck_residual_BR'],1e-14)
        self.assertEqual(out['experiment_exclusion_or_allowed'],'UNKNOWN')
        self.assertEqual(out['complete_h2_to_h1Z_branching_fraction'],
                         'NOT_COMPUTED_CHANGED_GAMMA')

    def test_vendor_mixing_polynomial_discrepancy_fails_closed(self):
        def fake_eval(exe,m1,m2,g,t):
            return {'full_Zee_BR':.0009},'BROKEN'
        with patch('zee_gateE2_flavor_cascade_mixing_frontier.evaluate',
                   side_effect=fake_eval):
            with self.assertRaisesRegex(ValueError,'closure failed'):
                calculate_row(model_data(),Path('/not/executed'))

    def test_source_pin_E1_a1v_exact_files_and_27_endpoints(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            a1v=root/'A1V_source_pinned_kernel'
            a1v.mkdir()
            prior=a1v/'gateA1v_legacy_response.json'
            prior.write_text(json.dumps({'n_scan_points':27}))
            a1m=root/'A1M.json';a1u=root/'A1U.json'
            a1m.write_text('source-pinned');a1u.write_text('A1U pinned')
            report=root/'summary.json'
            data={
                'status':SOURCE_STATUS,'tested':27,
                'rows':[model_data(f'B4_{i:07d}') for i in range(27)],
                'cohort':{'all_endpoint_controls_pass':True},
                'BtoXsGamma_physical_exclusions':None,
                '2026_NNLO_full_two_state_validated':False,
                'provenance_sha256':{
                    'A1V_report':digest(prior),
                    'A1M':digest(a1m),'A1U':digest(a1u)}}
            report.write_text(json.dumps(data))
            with patch('zee_gateE2_flavor_cascade_mixing_frontier.check_superiso_source',
                       return_value={'bsgamma_internal_CW_reload_detected':False}),\
                 patch('zee_gateE2_flavor_cascade_mixing_frontier.audit_affine_internal_matching',
                       return_value={'internal_CW_mode':'helper_reload'}):
                original,b=verify_e1(report,root,a1m,a1u)
                self.assertEqual(len(original['rows']),27)
                a1u.write_text('new A1U')
                with self.assertRaisesRegex(ValueError,'provenance changed'):
                    verify_e1(report,root,a1m,a1u)

    def test_cohort_summary_consistency_and_no_physical_claim(self):
        outputs=[]
        for i in range(27):
            original=model_data(f'B4_{i:07d}')
            def fake_eval(exe,m1,m2,g,t):
                x=math.cos(g)**2
                return {'full_Zee_BR':3.65e-4+2e-5*x+1e-5*x*x},'MOCK'
            with patch('zee_gateE2_flavor_cascade_mixing_frontier.evaluate',
                       side_effect=fake_eval):
                outputs.append(calculate_row(original,Path('/not/executed')))
        result=summarize(outputs)
        self.assertEqual(result['spectra'],27)
        self.assertEqual(result['vendor_independent_gamma_crosschecks'],108)
        self.assertEqual(
            result['number_with_BR_reduction_at_same_or_higher_Z_vertex_strength_squared'],0)
        self.assertEqual(
            result['number_with_BR_reduction_at_at_least_half_original_Z_vertex_strength_squared'],27)
        self.assertTrue(result['no_claim_about_cascade_branching_ratios'])
        self.assertIsNone(result['gamma_counterfactuals_physical_allowed_or_excluded'])

if __name__=='__main__':
    unittest.main()
