import copy
import json
import math
from pathlib import Path
import tempfile
import unittest

from module14 import scan
from module14.conditional_scan.flavor import evaluate, classification, REFERENCE
from module14.conditional_scan.workflow import cascade, join, load, production
from module14.fixtures.replay import materialize, saved

BASE = Path('module14/conditional_scan')


class FlavorTests(unittest.TestCase):
    def setUp(self):
        self.scalar = load('module1/example.json')
        self.scalar['physical'].update(mH1=550., mH2=900., beta=math.atan(5.3), gamma=1.09)
        self.card = load(BASE/'matching_card.json')

    def test_frozen_reference_and_coherent_splits(self):
        r = evaluate(self.scalar, self.card)
        self.assertAlmostEqual(r['DeltaC7_LO'], -0.03737804303348145, places=15)
        self.assertAlmostEqual(r['DeltaC8_LO'], -0.04231149396472201, places=15)
        self.assertAlmostEqual(r['BR_linear_2026'], 3.949479973178727e-4, places=17)
        for c in ('C7', 'C8'):
            self.assertAlmostEqual(sum(s['delta_'+c] for s in r['contribution_splits']), r['Delta'+c+'_LO'], places=15)
        self.assertEqual(r['bsg_physical_classification'], 'UNKNOWN')
        for k in ('np_theory_sigma', 'bsg_exclusion', 'globally_allowed'): self.assertIsNone(r[k])
        self.assertEqual(r['method_robustness'], 'NOT_EVALUATED')

    def test_predeclared_boundary_and_decoupling(self):
        t = REFERENCE['absolute_pull_threshold']
        for sign in (-1, 1):
            self.assertEqual(classification(sign*t), 'APPROX_BOUNDARY')
            self.assertEqual(classification(sign*(t-0.02)), 'APPROX_COMPATIBLE')
            self.assertEqual(classification(sign*(t+0.02)), 'APPROX_DISFAVORED')
        self.scalar['physical'].update(mH1=1e5, mH2=2e5)
        self.assertLess(abs(evaluate(self.scalar, self.card)['BR_linear_2026']-3.54e-4), 2e-8)

    def test_missing_scheme_and_nonfinite_rejected(self):
        with self.assertRaises(ValueError): classification(float('nan'))
        for key in self.card:
            c = dict(self.card); del c[key]
            with self.assertRaises(ValueError): evaluate(self.scalar, c)
        for key, val in [('matching_scale_GeV', 80), ('mt_MSbar_GeV', True),
                         ('mt_MSbar_GeV', float('nan')), ('quark_scheme', 'pole')]:
            c = dict(self.card); c[key] = val
            with self.assertRaises(ValueError): evaluate(self.scalar, c)
        with self.assertRaises((ValueError, KeyError)): evaluate({'id': 50}, self.card)

    def test_cascade_endpoints_and_threshold(self):
        for g in (0., math.pi/2, -math.pi/2):
            self.scalar['physical']['gamma'] = g
            r = cascade(self.scalar, None, None)
            self.assertEqual(r['partial_width_GeV'], 0.)
            self.assertIsNone(r['BR_H2_H1Z'])
        self.scalar['physical'].update(gamma=1.09, mH2=600)
        self.assertFalse(cascade(self.scalar, None, None)['is_kinematically_open'])


class JoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(); cls.root = Path(cls.tmp.name)
        cls.config, cls.manifest, cls.triples = materialize(cls.root/'scan', {50,91})
        cls.args = (cls.manifest, cls.config, cls.triples, load(BASE/'matching_card.json'),
                    'LOCAL_UNSPECIFIED', 'LOCAL_UNSPECIFIED')

    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()

    def test_real_join_preserves_unknowns_and_complete_br(self):
        r = join(*self.args)
        self.assertEqual(r['collection']['status'], 'COMPLETE')
        self.assertEqual(len(r['rows']), 8)
        self.assertEqual(r['collection']['cutflow']['gates']['vacuum']['UNKNOWN'], 1)
        for row in r['rows']:
            self.assertIsNone(row['rank']); self.assertIsNone(row['yield_proxy_pb'])
            self.assertIsNone(row['globally_allowed'])
            self.assertEqual(row['production']['status'], 'NOT_EVALUATED')
            self.assertEqual(row['cascade']['br_status'], 'PASS')
            self.assertEqual(row['lfv']['status'], 'PARTIAL')

    def test_corrupt_receipt_partial_manifest_and_wrong_source_fail_closed(self):
        args = list(self.args); args[2] = []
        with self.assertRaises(ValueError): join(*args)
        args = list(self.args); args[4] = 'wrong'
        with self.assertRaises(ValueError): join(*args)
        args = list(self.args); args[2] = self.triples*2
        with self.assertRaises(ValueError): join(*args)

    def test_decay_inventory_and_binding(self):
        r = join(*self.args)['rows'][0]
        bad = copy.deepcopy(r['widths']); bad['mothers']['H2']['channels'].pop()
        with self.assertRaises(ValueError): cascade(r['input_card'], r['neutrino'], bad)
        bad = copy.deepcopy(r['widths']); bad['scalar_sha256'] = '0'*64
        with self.assertRaises(ValueError): cascade(r['input_card'], r['neutrino'], bad)

    def test_documented_production_ranking_and_energy_groups(self):
        rows = join(*self.args)['rows']
        prod = self.root/'production'; prod.mkdir(exist_ok=True)
        (prod/'evidence.txt').write_text('Synthetic test fixture, not a physical rate.\n')
        for i,row in enumerate(rows):
            n = row['neutrino']
            card = {'scalar_sha256': row['scalar_sha256'], 'yukawa_sha256': {k: scan.digest(n[k]) for k in ('F','D','Ye','Ye2')},
                    'module2_input_sha256': n['input_sha256'], 'sigma_pb': i+1., 'energy_TeV': 13. if i<4 else 14.,
                    'state': 'H2', 'model': 'ZeeTypeII', 'process': 'pp_tbH2', 'charge_definition': 'both',
                    'order': 'LO', 'pdf': 'test-only', 'scale_scheme': 'fixed', 'documentation': 'TEST_ONLY',
                    'uncertainty': 'unknown; synthetic fixture', 'artifacts_sha256': {'evidence.txt':scan.file_sha(prod/'evidence.txt')}}
            (prod/(n['input_sha256']+'.json')).write_text(json.dumps(card))
        result = join(*self.args, production_dir=prod)
        self.assertEqual(sorted(r['rank'] for r in result['rows']), [1,1,2,2,3,3,4,4])
        r = rows[0]; path = prod/(r['neutrino']['input_sha256']+'.json')
        card = load(path); card['scalar_sha256'] = '0'*64; path.write_text(json.dumps(card))
        with self.assertRaises(ValueError): production(path, r['input_card'], r['neutrino'])

    def test_generation_shards_and_arms(self):
        # Repartition original bytes; the generator and kernels are never run.
        with tempfile.TemporaryDirectory() as tmp:
            _, a, ap = materialize(Path(tmp)/'a', shard_size=25)
            _, b, bp = materialize(Path(tmp)/'b', shard_size=50)
            self.assertEqual(a.read_bytes(), b.read_bytes())
            self.assertEqual(b''.join(t[0].read_bytes() for t in ap), a.read_bytes())
            self.assertEqual(b''.join(t[1].read_bytes() for t in ap), b''.join(t[1].read_bytes() for t in bp))


if __name__ == '__main__': unittest.main()
