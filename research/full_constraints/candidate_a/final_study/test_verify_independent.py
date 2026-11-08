import copy, json, pathlib, unittest
from verify_independent import ROOT, run

class ProofFalsifiers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        records=json.loads((ROOT/'validation/module1/d10_vacuum_global.json').read_text())['records']
        cards=json.loads((ROOT/'module1/d10_benchmarks.json').read_text())['records']
        cls.name='d7_NO_neutral_near_heavy_07'
        cls.record=next(x for x in records if x['benchmark_id']==cls.name)
        cls.phys=next(x['input']['physical'] for x in cards if x['input']['benchmark_id']==cls.name)
    def test_valid(self):
        self.assertGreater(run(self.record,self.phys,'1650627/250000')['min_pivot_approx'],0)
    def test_negative_quartic(self):
        r=copy.deepcopy(self.record); r['lagrangian_parameters']['Lambda1']=-abs(r['lagrangian_parameters']['Lambda1'])
        with self.assertRaises((AssertionError,ValueError,ZeroDivisionError)): run(r,self.phys,'1650627/250000')
    def test_large_cubic(self):
        r=copy.deepcopy(self.record); r['lagrangian_parameters']['Mu4']*=100
        with self.assertRaises(AssertionError): run(r,self.phys,'1650627/250000')
    def test_bad_epsilon(self):
        with self.assertRaises(AssertionError): run(self.record,self.phys,'100')
    def test_wrong_neutral_location(self):
        p=copy.deepcopy(self.phys); p['v']*=2
        with self.assertRaises((AssertionError,ValueError)): run(self.record,p,'1650627/250000')
    def test_invalid_box(self):
        with self.assertRaises(AssertionError): run(self.record,self.phys,'1650627/250000',0)
    def test_tadpole_sign(self):
        r=copy.deepcopy(self.record); r['lagrangian_parameters']['M12Sq']*=-1
        with self.assertRaises((AssertionError,ValueError)): run(r,self.phys,'1650627/250000')
if __name__=='__main__': unittest.main()
