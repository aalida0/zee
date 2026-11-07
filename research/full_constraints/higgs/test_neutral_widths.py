"""Independent fixed-card physics controls. No new parameter points or scans."""
import copy
import json
import math
import tarfile
import tempfile
import unittest

import numpy as np

from module1.d10_polynomial import evaluate
from module1.scalar_constraints import reconstruct
from module3.core import neutral_width, vertices
from module2.interface import decode
from module4.couplings import rotations, trilinears
from module7.d4_inputs import SM
from module7.d4_tree_kernels import scalar_vector
from research.full_constraints.higgs import neutral_widths as n
from research.full_constraints.higgs.decays_bridge import require_complete_width
from research.full_constraints.higgs.diphoton import amplitude, benchmark as light, MASSES
from research.full_constraints.higgs.test_higgs import integral_loops

EVIDENCE = {}


class NeutralWidthsTests(unittest.TestCase):
    def test_heavy_amplitudes_against_logarithmic_parameter_integrals(self):
        residuals = []
        for name in ('D7','F13'):
            p = n.benchmark(name)[0]['input']['physical']
            for state in ('H','A'):
                out = n.photons(name,state); M = out['mass_GeV']
                even = out['kV']*integral_loops((M/(2*MASSES['W']))**2)[2]; odd = 0j
                for f,k in out['kappas'].items():
                    fs = integral_loops((M/(2*MASSES[f]))**2)
                    weight = 4/3 if f in ('u','c','t') else 1/3 if f in ('d','s','b') else 1
                    even += weight*k.real*fs[1]; odd += weight*k.imag*fs[3]
                for m,g,q in out['charged']:
                    even += q*q*g*p['v']/(2*m*m)*integral_loops((M/(2*m))**2)[0]
                residuals.extend((abs(even-out['amplitude']['even']),abs(odd-out['amplitude']['odd'])))
                width = out['alpha_em']**2*M**3/(256*math.pi**3*p['v']**2)*(abs(even)**2+abs(odd)**2)
                self.assertAlmostEqual(width/out['amplitude']['width_GeV'],1,delta=2e-12)
        EVIDENCE['heavy_amplitudes_log_integral_max_abs'] = float(max(residuals))
        self.assertLess(max(residuals),2e-11)

    def test_H_and_A_trilinears_against_expanded_real_potential(self):
        residuals = []
        for name in ('D7','F13'):
            p = n.benchmark(name)[0]['input']['physical']; lag = reconstruct(p)[0]
            zh,za,zp = rotations(p); r = np.zeros(10)
            r[2] = p['v']*math.cos(p['beta']); r[6] = p['v']*math.sin(p['beta'])
            for state,row,indices in (('H',zh[1],[2,6]),('A',za[1],[3,7])):
                d = np.zeros(10); d[indices] = row; eps = .25
                hessian = (evaluate(r+eps*d,lag)[2]-evaluate(r-eps*d,lag)[2])/(2*eps)
                g = hessian[np.ix_([0,4,8],[0,4,8])]-1j*hessian[np.ix_([0,4,8],[1,5,9])]
                ref = zp@g@zp.T; got = trilinears(p,lag)[state]
                residuals.append(float(np.max(abs(ref-got))))
                self.assertLess(residuals[-1],2e-9)
        EVIDENCE['heavy_trilinear_polynomial_max_abs_GeV'] = max(residuals)

    def test_fresh_signed_SARAH_H_and_A_vertices(self):
        raw = json.loads((n.HERE/'neutral_receipts/native_vertices.json').read_text())
        self.assertEqual(raw['sarah_version'],'4.15.4')
        self.assertEqual(raw['input_sha256'],n.sha(n.HERE/'neutral_receipts/native_inputs.json'))
        residuals = []
        for case in raw['cases']:
            p = n.benchmark(case['id'])[0]['input']['physical']
            expected = np.concatenate([(-1j*trilinears(p,reconstruct(p)[0])[s][1:,1:]).flatten() for s in ('H','A')])
            actual = np.array([complex(x[0]['real'],x[0]['imag']) for x in case['coefficients']])
            residuals.extend(abs(actual-expected))
        EVIDENCE['native_signed_trilinear_max_abs_GeV'] = float(max(residuals))
        self.assertLess(max(residuals),2e-10)
        self.assertEqual(len(residuals),16)

    def test_CP_and_flavour_trace_proof_for_photons(self):
        for name in ('D7','F13'):
            h = n.photons(name,'H'); a = n.photons(name,'A')
            self.assertEqual(a['kV'],0)
            self.assertEqual(a['charged'],[])
            self.assertLess(np.max(abs(np.diag(a['G_charged_GeV']))),1e-10)
            # A single off-diagonal insertion has zero trace for arbitrary
            # unequal-mass diagonal propagators, for triangle AND QQ seagull.
            offdiag = np.array([[0,2j],[-2j,0]])
            d1,d2,d3 = (np.diag(v) for v in ((.3,.7),(.2,.4),(.8,.1)))
            self.assertEqual(np.trace(offdiag@d1@d2@d3),0)
            self.assertEqual(np.trace(offdiag@d1@d2),0)
            self.assertGreater(abs(h['G12_Z21_GeV']),1)
            self.assertGreater(abs(h['amplitude']['even_terms']['H1']),0)
            self.assertGreater(abs(h['amplitude']['even_terms']['H2']),0)
            # Complex diagonal leptons leave both tensors; scalar CP does not
            # justify dropping the general-lepton CP-even A amplitude.
            self.assertGreater(abs(a['amplitude']['even']),0)
            self.assertGreater(abs(a['amplitude']['odd']),0)

    def test_charge_summed_vector_width_independent_rest_frame_polarizations(self):
        metric = np.diag([1.,-1.,-1.,-1.])
        for name in ('D7','F13'):
            p = n.benchmark(name)[0]['input']['physical']
            for state in ('H','A'):
                M = p['mh2' if state=='H' else 'ma']; ms = p['mH1']; mv = SM['EW']['mW']
                ev = (M*M+mv*mv-ms*ms)/(2*M); mom = math.sqrt(ev*ev-mv*mv)
                parent = np.array([M,0,0,0]); daughter = np.array([M-ev,0,0,-mom])
                polarizations = [np.array([0.,1,0,0]),np.array([0.,0,1,0]),np.array([mom/mv,0,0,ev/mv])]
                c = mv/p['v']*math.cos(p['gamma'])*(math.cos(p['beta']-p['alpha']) if state=='H' else 1)
                squared = sum(abs(c*(parent+daughter)@metric@pol)**2 for pol in polarizations)
                reference = 2*mom/(8*math.pi*M*M)*squared
                calculated = n.extra_widths(name)[state]['H1+ W- plus conjugate']
                self.assertAlmostEqual(reference/calculated,1,delta=3e-14)
                self.assertEqual(scalar_vector(ms+mv,ms,mv,c),0)
                self.assertEqual(scalar_vector(ms+mv-1,ms,mv,c),0)

    def test_lepton_width_independent_scalar_pseudoscalar_and_LFV_counting(self):
        ml = SM['lepton_masses']
        for name in ('D7','F13'):
            r,w = n.benchmark(name); p = r['input']['physical']
            for state,(C,M) in vertices(decode(w['yukawas']['D']),p,ml).items():
                for i,m in enumerate(ml):
                    beta = math.sqrt(1-4*m*m/M**2)
                    ref = M/(8*math.pi)*(C[i,i].real**2*beta**3+C[i,i].imag**2*beta)
                    self.assertAlmostEqual(neutral_width(C,M,i,i,ml)/ref,1,delta=1e-14)
                if state in ('H','A'):
                    self.assertEqual(n.extra_widths(name)[state]['mu tau both charges'],2*neutral_width(C,M,1,2,ml))

    def test_original_h125_regression(self):
        for name,ref in (('D7',.9317959556087543),('F13',.9750252263683726)):
            r,w = n.benchmark(name)
            self.assertAlmostEqual(light(r['input']['physical'],w)['ratio_to_SM'],ref,delta=2e-14)

    def test_fixed_card_evidence_and_no_incomplete_normalization(self):
        evidence = json.loads((n.HERE/'NEUTRAL_WIDTH_EVIDENCE.json').read_text())
        with tempfile.TemporaryDirectory() as tmp:
            d7 = n.Path(tmp)/'D7.txt'
            with tarfile.open(n.HERE/'SUSHI_RUNS.tar.gz') as archive:
                d7.write_bytes(archive.extractfile('anyhdecay-D7.txt').read())
            for case in evidence['benchmarks']:
                raw = d7 if case['name']=='D7' else n.HERE/'neutral_receipts/anyhdecay-F13.stdout'
                self.assertEqual(n.jsonable(n.calculate(case['name'],raw)),case)
                for state,row in case['states'].items():
                    self.assertAlmostEqual(math.fsum(row['partial_widths_GeV'].values()),row['known_disjoint_sum_GeV'])
                    self.assertIsNone(row['total_width_GeV']); self.assertIsNone(row['branching_fractions'])
                    with self.assertRaises(ValueError): require_complete_width(row)
                    bad = copy.deepcopy(row); bad['status']='COMPLETE'; bad['total_width_GeV']=row['known_disjoint_sum_GeV']
                    with self.assertRaises(ValueError): require_complete_width(bad)
        self.assertEqual(evidence['status'],'HIGGS_SCOPED_SEARCH_BLOCKED')

    def test_historical_source_pins_and_tampering(self):
        manifest = json.loads((n.HERE/'SUSHI_SOURCE_MANIFEST.json').read_text())
        n.verify_sources(manifest)
        bad = copy.deepcopy(manifest); bad['model_sources']['module4/couplings.py']='0'*64
        with self.assertRaises(ValueError): n.verify_sources(bad)


if __name__ == '__main__':
    unittest.main(verbosity=2)
