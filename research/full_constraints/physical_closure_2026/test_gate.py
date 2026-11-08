import copy,unittest,hashlib,tempfile
from pathlib import Path
from gate import MANDATORY,classify
class Gate(unittest.TestCase):
 def setUp(self):
  v={'status':'VALIDATED_PASS','source':'fixture','scope':'fixture','uncertainty':'fixture','coverage_complete':True,'theory_sigma':1,'all_applicable_widths':True,'complete_operator_basis':True,'phase_supported':True}
  self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup);p=Path(self.temp.name)/'source';p.write_text('fixture')
  self.c={'join_verified':True,'source_files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()},'scalar_sha256':'abc','source_scalar_sha256':'abc','yukawa_sha256':{'F':'def'},'source_yukawa_sha256':{'F':'def'},'ordering':'NO','source_ordering':'NO','constraints':{k:copy.deepcopy(v) for k in MANDATORY}}
 def test_pass(self):self.assertEqual(classify(self.c),('GLOBAL_PASS',True))
 def test_unknown(self):self.c['constraints']['mu_e_gamma']['status']='UNKNOWN';self.assertEqual(classify(self.c),('UNKNOWN',None))
 def test_fail(self):self.c['constraints']['bfb']['status']='VALIDATED_FAIL';self.c['constraints']['mu_e_gamma']['status']='UNKNOWN';self.assertEqual(classify(self.c),('PHYSICAL_FAIL',False))
 def test_join_missing(self):self.c['join_verified']=False;self.assertEqual(classify(self.c),('UNKNOWN',None))
 def test_hash(self):self.c['source_files'][next(iter(self.c['source_files']))]='0'*64;self.assertRaises(ValueError,classify,self.c)
 def test_misjoined_scalar(self):self.c['source_scalar_sha256']='bad';self.assertRaises(ValueError,classify,self.c)
 def test_misjoined_yukawa(self):self.c['source_yukawa_sha256']={'F':'bad'};self.assertRaises(ValueError,classify,self.c)
 def test_order(self):self.c['source_ordering']='IO';self.assertRaises(ValueError,classify,self.c)
 def test_missing_field(self):del self.c['constraints']['bfb'];self.assertRaises(ValueError,classify,self.c)
 def test_missing_width(self):self.c['constraints']['higgs']['all_applicable_widths']=False;self.assertRaises(ValueError,classify,self.c)
 def test_missing_H2_width(self):self.c['constraints']['charged_widths']['all_applicable_widths']=False;self.assertRaises(ValueError,classify,self.c)
 def test_missing_b_sigma(self):self.c['constraints']['bsgamma']['theory_sigma']=None;self.assertRaises(ValueError,classify,self.c)
 def test_missing_operator(self):self.c['constraints']['mu_3e']['complete_operator_basis']=False;self.assertRaises(ValueError,classify,self.c)
 def test_phase(self):self.c['constraints']['mu_e_gamma']['phase_supported']=False;self.assertRaises(ValueError,classify,self.c)
if __name__=='__main__':unittest.main()
