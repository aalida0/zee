"""Receipt-level physics/dataflow falsifiers; no scans or theory-error fitting."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from execute import IDS, ordinary, parse
from provenance import sha, verify_execution, verify_source

HERE=Path(__file__).resolve().parent
EFILE=HERE/'execution/HEPFIT_EXECUTION.json'


class EvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.e=verify_execution(EFILE)

    def values(self,name): return self.e['runs'][name]['values']

    def reject(self,change):
        e=copy.deepcopy(self.e); change(e)
        # Only replace the JSON document; real receipt bytes remain authenticated.
        original=Path.read_text
        def read(p,*a,**k):
            return json.dumps(e) if p==EFILE else original(p,*a,**k)
        with patch.object(Path,'read_text',read), self.assertRaises(ValueError): verify_execution(EFILE)

    def test_receipt_authentication_and_full_order_vectors(self):
        self.assertEqual(len(self.e['runs']),37)
        for r in self.e['runs'].values():
            v=r['values']
            self.assertAlmostEqual(v['BR_NLO'],v['overall']*(v['P_NLO']+v['N']),places=17)
            self.assertAlmostEqual(v['P_NLO'],v['P_LO']+v['P11_weighted']+v['P21_weighted']+v['P_Vub_NLO']+v['P_EW_NLO'],places=14)

    def test_original_cards_and_SuperIso_receipts_reproduced(self):
        want=[4.2262508129385407e-4,3.886651979064471e-4]
        for bid,br in zip(IDS,want):
            self.assertAlmostEqual(self.e['comparisons'][bid]['SuperIso']['injected_BR'],br,places=17)

    def test_source_native_matching_independent_BMU_and_endpoints(self):
        self.assertLess(max(abs(x) for x in self.e['implementation_residuals'].values()),2e-13)

    def test_published_table_interpolation_is_not_NLO_rate_matching(self):
        for bid in IDS:
            r=self.values(bid+'_native_m1')
            self.assertLess(abs(r['BR_TypeII_table']-self.e['comparisons'][bid]['published_NNLO_table']),2e-18)
            self.assertGreater(abs(r['BR_NLO']-r['BR_TypeII_table']),1e-7)
        self.assertEqual(self.e['independent_rate_status'],'INDEPENDENT_RATE_MISMATCH')

    def test_constructor_initialization(self):
        for r in self.e['runs'].values():
            if r['mode']!='sm':
                self.assertEqual(r['values']['initialized_unused_LO_C1'],0.)
                self.assertEqual(r['values']['initialized_unused_NNLO_C1'],0.)

    def test_wrong_cut_falsifier(self):
        self.reject(lambda e:e['runs']['SM_reference']['values'].__setitem__('cut_GeV',1.9))

    def test_missing_operator_order_falsifier(self):
        self.reject(lambda e:e['runs'][IDS[0]+'_central']['values'].pop('low_1_4'))

    def test_extra_alpha_s_falsifier(self):
        def change(e):
            v=e['runs'][IDS[0]+'_central']['values'];v['high_1_1_7']*=v['a_s_muw']
        self.reject(change)

    def test_wrong_C4_finite_map_falsifier(self):
        def change(e):
            r=e['runs'][IDS[0]+'_central'];r['values']['high_1_1_7']+=r['values']['a_s_muw']*4*r['input']['NP1_4']/9
        self.reject(change)

    def test_duplicate_SM_falsifier(self):
        self.reject(lambda e:e['implementation_residuals'].__setitem__(IDS[0]+'_zero_SM',self.values('SM_reference')['BR_NLO']))

    def test_missing_uncertainty_cannot_promote(self):
        self.reject(lambda e:e.__setitem__('full_rate_status','B_FULL_RATE_VALIDATED'))
        self.reject(lambda e:e.__setitem__('theory_sigma',.04*self.values('SM_reference')['BR_NLO']))

    def test_source_digest_falsifier(self):
        lock=json.loads((HERE/'SOURCE_LOCK.json').read_text())
        first=next(iter(lock['HEPfit_build_and_rate_files']))
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/first;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('tampered source')
            with self.assertRaisesRegex(ValueError,'digest mismatch'):verify_source(Path(d))

    def test_unpatched_constructor_is_rejected_by_witness(self):
        raw=(HERE/'receipts/initialization-falsifier.log').read_text()
        vals=parse(raw)
        self.assertGreater(abs(vals['initialized_unused_LO_C1']),1e-6)
        self.assertGreater(abs(vals['initialized_unused_NNLO_C1']),1e-6)

    def test_signed_C4_C7_C8_response(self):
        for name in ['C4_NLO','C7_LO','C8_LO']:
            minus=self.values('probe_'+name+'_minus')['BR_NLO']
            plus=self.values('probe_'+name+'_plus')['BR_NLO']
            self.assertGreater(abs(plus-minus),1e-10)
        self.assertLess(self.values('probe_C7_LO_plus')['BR_NLO'],self.values('probe_C7_LO_minus')['BR_NLO'])

    def test_independent_heldout_bilinear_cross_term(self):
        b=self.values('SM_reference')['BR_NLO'];h=.02
        plus=lambda c:self.values('probe_'+c+'_LO_plus')['BR_NLO']
        minus=lambda c:self.values('probe_'+c+'_LO_minus')['BR_NLO']
        s7=(plus('C7')-minus('C7'))/(2*h); s8=(plus('C8')-minus('C8'))/(2*h)
        q7=(plus('C7')+minus('C7')-2*b)/(2*h*h);q8=(plus('C8')+minus('C8')-2*b)/(2*h*h)
        q78=(self.values('probe_joint')['BR_NLO']-b-(s7+s8)*h-(q7+q8)*h*h)/(h*h)
        c7,c8=-.017,.023
        expected=b+s7*c7+s8*c8+q7*c7*c7+q8*c8*c8+q78*c7*c8
        self.assertGreater(abs(q78),1e-6)
        self.assertLess(abs(expected-self.values('probe_heldout')['BR_NLO']),2e-16)

    def test_coherence_is_not_weighted_rate_average(self):
        for bid in IDS:self.assertGreater(abs(self.e['comparisons'][bid]['coherent_minus_incoherent']),1e-9)

    def test_source_decomposition_closes_without_intercept_fit(self):
        for c in self.e['comparisons'].values():
            for key in ['default_decomposition','shared_decomposition','shared_SM_decomposition']:
                d=c[key]
                self.assertLess(abs(d['normalization']+d['perturbative_including_EM']+d['power']-d['direct_difference']),2e-18)

    def test_scale_controls_recompute_running_top(self):
        for bid in IDS:
            lo=self.values(bid+'_scale_120');hi=self.values(bid+'_scale_200')
            self.assertGreater(lo['mt_MSbar_mut'],hi['mt_MSbar_mut'])
            self.assertNotEqual(lo['BR_NLO'],hi['BR_NLO'])


if __name__=='__main__':unittest.main()
