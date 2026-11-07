"""Offline falsification against retained executed data; no generators or scans."""
import copy
import json
import math
from pathlib import Path
import tarfile
import tempfile
import unittest

from research.full_constraints.higgs import sushi_bridge as s
from research.full_constraints.higgs.decays_bridge import assemble_d7, require_complete_width
from research.full_constraints.higgs.native_validation import validate

HERE=Path(__file__).resolve().parent


class ExecutedSusHiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e=json.loads((HERE/'SUSHI_EVIDENCE.json').read_text())
        cls.manifest=json.loads((HERE/'SUSHI_SOURCE_MANIFEST.json').read_text())
        cls.temp=tempfile.TemporaryDirectory();cls.raw=Path(cls.temp.name)
        with tarfile.open(HERE/'SUSHI_RUNS.tar.gz') as archive:
            for member in archive.getmembers():
                if not member.isfile() or not (cls.raw/member.name).resolve().is_relative_to(cls.raw):
                    raise ValueError('Unsafe raw receipt archive')
                archive.extract(member,cls.raw)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_all_source_and_receipt_bytes(self):
        self.assertEqual(s.sha(HERE/'SUSHI_SOURCE_MANIFEST.json'),self.e['source_manifest_sha256'])
        self.assertEqual(s.sha(HERE/'SUSHI_RUNS.tar.gz'),self.manifest['raw_archive_sha256'])
        for key in ('model_sources','bridge_sources'):
            for name,digest in self.manifest[key].items():self.assertEqual(s.sha(s.ROOT/name),digest,name)
        for name,digest in self.manifest['raw_receipts'].items():self.assertEqual(s.sha(self.raw/name),digest,name)

    def test_original_cards_and_executed_central_contracts(self):
        self.assertEqual(len(self.e['records']),4)
        for row in self.e['records']:
            s.validate_rate(row,self.e['production_metadata'],self.raw/'runs')
            b=row['central']['blocks']
            self.assertEqual(b['sushi']['4'],13000.)
            self.assertEqual((b['sushi']['5'],b['sushi']['6'],b['sushi']['7']),(0.,0.,0.))
            self.assertEqual(b['sushi']['2'],12 if row['state']=='H' else 21)
            self.assertGreater(row['central']['rates']['ggF']['sigma_pb'],0)
            self.assertLess(abs(row['independent_relative_residual']),2e-6)
            self.assertLess(abs(row['independent_bbH_relative_residual']),2e-6)

    def test_wrong_energy_pdf_cp_order_flavour_scheme_sources_rejected(self):
        for key,value in [('energy_GeV',14000),('PDF','MMHT2014nlo68cl'),('PDF_member',1),
                          ('QCD_order','NNLO'),('CP_scheme','unshifted alpha'),('units','fb'),
                          ('flavours',4),('ggF_mb_scheme','MSbar'),('archive_sha256','0'*64)]:
            bad=dict(self.e['production_metadata']);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                s.validate_rate(self.e['records'][0],bad,self.raw/'runs')
        for key,value in [('state','H1'),('mass_GeV',500),('scalar_sha256','0'*64)]:
            bad=copy.deepcopy(self.e['records'][0]);bad[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):
                s.validate_rate(bad,self.e['production_metadata'],self.raw/'runs')

    def test_missing_nan_negative_or_tampered_rates_rejected(self):
        for value in (None,float('nan'),-1.,0.,3.):
            bad=copy.deepcopy(self.e['records'][0]);bad['central']['rates']['ggF']['sigma_pb']=value
            with self.subTest(value=value),self.assertRaises((TypeError,ValueError)):
                s.validate_rate(bad,self.e['production_metadata'],self.raw/'runs')
        with self.assertRaises(ValueError):s.card('new_point','H')
        for kwargs in (dict(member=51),dict(scale=(0,1)),dict(factors=(1,float('nan'),1))):
            with self.assertRaises(ValueError):s.card('D7','H',**kwargs)

    def test_native_signed_quark_and_extra_vertices(self):
        native=json.loads((self.raw/'native_vertices.json').read_text())
        result=validate(native)
        self.assertEqual(result,self.e['native_vertex_validation'])
        self.assertEqual(result['complex_coefficients_checked'],28)
        bad=copy.deepcopy(native)
        bad['cases'][0]['coefficients'][3][0]['real']*=-1
        with self.assertRaises(ValueError):validate(bad)
        self.assertEqual(s.sha(self.raw/'native_inputs.json'),native['input_sha256'])

    def test_nonzero_loop_interference_and_cp_functions(self):
        for row in self.e['records']:
            k=row['couplings'];cp='even' if row['state']=='H' else 'odd'
            a,t=s.lo_amplitude(row['mass_GeV'],cp,k['top'],k['bottom'],mc=row['central']['blocks']['internalmasses']['40'])
            self.assertGreater(abs(t[1]),0.)
            self.assertGreater(abs(abs(a)**2-sum(abs(x)**2 for x in t)),1e-6)
            for tag,factors in [('top',(0,1,0)),('bottom',(0,0,1)),('charm',(1,0,0)),
                                ('flip_bottom',(1,1,-1)),('double_all',(2,2,2)),
                                ('unit_quarks',(1/k['top'],1/k['top'],1/k['bottom']))]:
                cf,tf,bf=factors
                ref=abs(tf*t[0]+bf*t[1]+cf*t[2])**2/abs(a)**2
                parsed=s.blocks(self.raw/'runs'/f"{row['name']}_{row['state']}_{tag}.out")
                actual=parsed['sushiggh'][1]/row['central']['rates']['ggF']['sigma_pb']
                self.assertAlmostEqual(actual/ref,1.,places=6)
            wrong=s.lo_amplitude(row['mass_GeV'],'odd' if cp=='even' else 'even',k['top'],k['bottom'])[0]
            self.assertGreater(abs(abs(wrong)**2/abs(a)**2-1),.1)
        self.assertAlmostEqual(s.lo_amplitude(1.,'even',1,0,kc=0,mt=1e5)[0].real,4/3,places=9)
        self.assertAlmostEqual(s.lo_amplitude(1.,'odd',1,0,kc=0,mt=1e5)[0].real,2,places=9)

    def test_scale_pdf_uncertainties_recomputed(self):
        for row in self.e['records']:
            self.assertEqual(len(row['scale_variations']),7);self.assertEqual(len(row['PDF_members']),51)
            for proc in ('ggF','bbH'):
                v=row['central']['rates'][proc]['sigma_pb'];u=row['uncertainties'][proc]
                scale=[r['rates'][proc]['sigma_pb'] for r in row['scale_variations']]
                self.assertAlmostEqual(u['scale_up_pb'],max(scale)-v)
                self.assertAlmostEqual(u['scale_down_pb'],v-min(scale))
                pdf=row['PDF_members'];key=proc+'_pb'
                uncertainty=.5*math.sqrt(sum((pdf[2*i+1][key]-pdf[2*i+2][key])**2 for i in range(25)))
                self.assertAlmostEqual(u['PDF_symmetric_68_percent_pb'],uncertainty)
                self.assertGreater(uncertainty,0.)

    def test_transferable_widths_and_native_extras_recomputed(self):
        d=assemble_d7(self.raw/'anyhdecay-D7.txt')
        self.assertEqual(d,self.e['decays'])
        self.assertAlmostEqual(d['Hhh_independent_GeV'],.0006081272378254598)
        self.assertAlmostEqual(d['AhZ_independent_GeV'],.0656930403440257)
        for state in ('H','A'):
            w=d['states'][state]
            self.assertGreater(w['partial_widths_GeV']['H1+ W- plus conjugate'],.9)
            self.assertEqual(w['partial_widths_GeV']['H2+ W- plus conjugate'],0.)
            self.assertAlmostEqual(w['R2HDM_branching_sum'],1.)
            self.assertIsNone(w['total_width_GeV']);self.assertIsNone(w['branching_fractions'])
            with self.assertRaises(ValueError):require_complete_width(w)

    def test_total_and_invisible_double_counting_cannot_pass(self):
        w=dict(status='COMPLETE',missing=[],total_width_GeV=3.,partial_widths_GeV={'ZZ':2.,'inv_derived':2.})
        with self.assertRaises(ValueError):require_complete_width(w)
        w['total_width_GeV']=4.
        with self.assertRaises(ValueError):require_complete_width(w)
        for missing in (['Zgamma'],['off-shell charged W']):
            w['missing']=missing;w['total_width_GeV']=4.
            with self.assertRaises(ValueError):require_complete_width(w)

    def test_no_exclusion_and_exact_per_id_missing_gate(self):
        matrix=json.loads((HERE/'COVERAGE.json').read_text());gate=s.analysis_gate(matrix)
        self.assertEqual(gate,self.e['HiggsTools']);self.assertEqual(len(gate['analyses']),310)
        self.assertEqual(gate['complete_signals_connected'],0)
        self.assertIsNone(gate['exclusion']);self.assertIsNone(gate['global_acceptance'])
        self.assertEqual({r['status'] for x in gate['analyses'] for r in x['cases'].values()},
                         {'MISSING_PREDICTION','NOT_APPLICABLE'})


if __name__=='__main__':unittest.main()
