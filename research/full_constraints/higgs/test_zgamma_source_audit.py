"""Source mismatch is the expected physics finding, not a swallowed test failure."""
import json
import math
import unittest
import numpy as np

from research.full_constraints.higgs import zgamma_source_audit as z


class SourceAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e=json.loads((z.HERE/'ZGAMMA_SOURCE_EVIDENCE.json').read_text())

    def test_pinned_sources_and_original_cards(self):
        for path,digest in self.e['source_pins'].items():
            self.assertEqual(z.sha(z.ROOT/path),digest,path)
        self.assertEqual([r['name'] for r in self.e['cases']],['D7','F13'])
        for r in self.e['cases']:
            self.assertEqual(r['scalar_sha256'],z.benchmark(r['name'])[0]['input_sha256'])

    def test_original_signed_couplings_and_native_library_pins(self):
        old=json.loads((z.ROOT/'research/full_constraints/HIGGS_VALIDATION.json').read_text())
        def real_matrix(mat):
            return np.array([[complex(v['real'],v['imag']).real if isinstance(v,dict) else v for v in row] for row in mat])
        for r in self.e['cases']:
            saved=old['h125'][r['name']]
            self.assertEqual(r['scalar_sha256'],saved['scalar_sha256'])
            self.assertEqual(r['yukawa_sha256'],saved['yukawa_sha256'])
            np.testing.assert_allclose(r['G_GeV'],real_matrix(saved['gamma']['g_h_charged_GeV']),rtol=0,atol=1e-11)
            np.testing.assert_allclose(r['Z_current'],real_matrix(saved['gamma']['Z_current']),rtol=0,atol=1e-15)
        manifest=json.loads((z.HERE/'ZGAMMA_SOURCE_MANIFEST.json').read_text())
        for path,digest in manifest['native']['files'].items():self.assertEqual(z.sha(path),digest)
        self.assertEqual(self.e['native_receipt']['executable_sha256'],manifest['native']['probe_executable_sha256'])

    def test_native_library_matches_parameter_integrals(self):
        for row in self.e['native_checks']:
            for k,r in row['absolute_residuals'].items():
                reference=row['parameter_reference'][k]
                # Tensor reductions have cancellations; this is numerical
                # library agreement, never a theory uncertainty.
                self.assertLess(r,2e-10*max(abs(reference),1e-6),(k,row['request']))

    def test_independent_adaptive_integral_and_equal_mass_I1(self):
        for row in self.e['cases']:
            self.assertLess(abs(row['quadrature_relative_K_residual']),2e-12)
            for eq in row['equal_mass_controls']:
                self.assertLess(abs(eq['K']/eq['I1_over_4m2']-1),2e-8)

    def test_literal_mixed_mismatch_survives_quadrature_refinement(self):
        for row in self.e['cases']:
            s,t=row['s_GeV2'],row['t_GeV2'];a,b=np.square(row['charged_masses_GeV'])
            ab=z.parameters(s,t,a,b,120);ba=z.parameters(s,t,b,a,120)
            literal=z.bracket(s,t,a,b,ab,ba,'literal_LoopTools')
            self.assertAlmostEqual(literal,row['literal_bracket'],places=13)
            self.assertGreater(abs(row['literal_relative_kernel_mismatch']),1e-4)
            self.assertLess(abs(row['corrected_relative_kernel_residual']),2e-10)

    def test_Ward_including_seagull_distinguishes_routings(self):
        for row in self.e['cases']:
            self.assertLess(abs(row['candidate_Ward_reduced_residual']),5e-13)
            self.assertGreater(abs(row['literal_Ward_reduced_residual']),1e-7)
        for residual in self.e['native_Ward_residuals']:
            self.assertLess(abs(complex(residual['real'],residual['imag'])),2e-10)

    def test_UV_and_scale_cancellation(self):
        checks=self.e['native_checks']
        for i in range(0,len(checks),2):
            a,b=(checks[i+j]['LoopTools'] for j in (0,1))
            for k in ('db','cp','cr','k'):
                difference=complex(a[k]['real']-b[k]['real'],a[k]['imag']-b[k]['imag'])
                self.assertLess(abs(difference),2e-12)
            shift=7+math.log(19)
            self.assertAlmostEqual(b['c00']['real']-a['c00']['real'],shift/4,places=11)
            self.assertAlmostEqual(b['bs']['real']-a['bs']['real'],shift,places=11)

    def test_species_order_rephasing_and_nonzero_mixed_terms(self):
        for row in self.e['cases']:
            g=np.array(row['G_GeV']);v=np.array(row['Z_current']);s=row['s_GeV2'];t=row['t_GeV2']
            m=np.square(row['charged_masses_GeV'])
            k=np.array([[z.parameters(s,t,a,b)['k'] for b in m] for a in m])
            total=np.sum(g*v.T*k);p=[1,0]
            self.assertAlmostEqual(total,np.sum(g[np.ix_(p,p)]*v.T[np.ix_(p,p)]*k[np.ix_(p,p)]),places=14)
            phase=np.diag([1,-1])
            self.assertAlmostEqual(total,np.sum((phase@g@phase)*(phase@v@phase).T*k),places=14)
            self.assertGreater(abs(row['scalar_X_diagnostics']['literal_LoopTools']['mixed_X']),.001)
            self.assertTrue(99<row['fixed_coupling_heavy_mass_K_ratio']<103)

    def test_degenerate_mass_basis_trace_and_mixing_endpoints(self):
        for row in self.e['cases']:
            g=np.array(row['G_GeV']);v=np.array(row['Z_current']);trace=np.trace(g@v)
            for theta in (0,math.pi/4,math.pi/2):
                r=np.array([[math.cos(theta),math.sin(theta)],[-math.sin(theta),math.cos(theta)]])
                self.assertAlmostEqual(np.sum((r@g@r.T)*(r@v@r.T).T),trace,places=12)
                # Doublet/singlet Z mixing endpoints forbid a mixed current.
                current=r@np.diag([.5-.223,-.223])@r.T
                if theta in (0,math.pi/2):self.assertLess(abs(current[0,1]),1e-15)

    def test_threshold_and_missing_prediction_fail_closed(self):
        with self.assertRaises(ValueError):z.parameters(4*300**2,91.1876**2,300**2,530**2)
        with self.assertRaises(ValueError):z.physical_width('D7','h')
        self.assertIsNone(self.e['physical_width_GeV'])
        self.assertFalse(self.e['complete_leading_one_loop_validated'])
        self.assertFalse(self.e['H_A_extension_executed'])

    def test_nonidentical_two_body_width_normalization(self):
        # Explicit transverse Z/photon polarization sum gives 2(pZ.pA)^2.
        for row in self.e['cases']:
            s,t=row['s_GeV2'],row['t_GeV2'];M=math.sqrt(s);p=(s-t)/(2*M);dot=(s-t)/2
            width=p/(8*math.pi*s)*2*dot**2
            self.assertAlmostEqual(width,M**3/(32*math.pi)*(1-t/s)**3,places=10)
            # F21=alpha X/(2pi v) gives alpha^2 M^3/(128pi^3 v^2).

    def test_retained_materiality_replay_is_not_a_physical_BR(self):
        saved=json.loads((z.HERE/'TAUTAU_MATERIALITY_REPLAY.json').read_text())
        self.assertEqual(saved,z.materiality_replay())
        for row in saved['rows']:
            self.assertIsNone(row['certified_BR_upper'])
            self.assertIsNone(row['certified_signal_upper'])
            self.assertIsNone(row['physical_BR'])
            self.assertIsNone(row['exclusion'])
        for path,digest in saved['inputs'].items():self.assertEqual(z.sha(z.ROOT/path),digest)


if __name__=='__main__':unittest.main(verbosity=2)
