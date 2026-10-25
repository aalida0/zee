#!/usr/bin/env python3
"""F17 strict source JSON and Mathematica helper regression tests."""
from pathlib import Path
import sys,unittest,json,tempfile
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from zee_paper1_F17_verify_complex_json import verify_json,SHAPES,IDS,STATUS
from zee_paper1_F16_wolfram_syntax_lint import check

def payload():
 def matrix(n,m):
  return [[[float(i+j),0.01*(i-j)] for j in range(m)] for i in range(n)]
 return {
  'status':STATUS,
  'candidate_ids':sorted(IDS),
  'full_Zee_param_card_validated':False,
  'matrices':[{
    'candidate_id':name,
    'matrices_re_im':{k:matrix(*d) for k,d in SHAPES.items()},
    'mH1_GeV':572.2,'mH2_GeV':873.2,'mA_GeV':600.,
    'mHeavyNeutral_GeV':720.,'vev_GeV':246.22,
    'alpha_rad':0.5,'beta_rad':1.3,'gamma_rad':1.1,
    'lepton_masses_GeV':[.000511,.10566,1.77686],
    'full_Zee_param_card_validated':False,
    'ufo_fermion_couplings_checked':False
  } for name in sorted(IDS)]}

class TestF17CompleteComplexJSON(unittest.TestCase):
 def test_exact_three_seven_matrix_real_imag_json(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'f17.json';p.write_text(json.dumps(payload()))
   got=verify_json(p)
   self.assertEqual(len(got['matrices']),3)
   self.assertEqual(len(got['matrices'][0]['matrices_re_im']),7)
 def test_reject_incomplete_symbolic_and_wrong_cohort(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'f17.json'
   tests=[]
   a=payload();a['matrices'][0]['matrices_re_im']['Ye2SARAH'][0][1]=['getMat',0.]
   tests.append(a)
   a=payload();a['matrices'][1]['matrices_re_im']['YeSARAH'][0].pop()
   tests.append(a)
   a=payload();a['candidate_ids']=['wrong']*3
   tests.append(a)
   a=payload();a['matrices'][2]['full_Zee_param_card_validated']=True
   tests.append(a)
   a=payload();a['matrices'][0]['matrices_re_im']['FZEE']=[1]
   tests.append(a)
   for test in tests:
    p.write_text(json.dumps(test))
    with self.assertRaises(ValueError):verify_json(p)
   p.write_text('truncated corrupt JSON {')
   with self.assertRaises(json.JSONDecodeError):verify_json(p)
 def test_actual_wolfram_export_uses_shared_helper_and_roundtrip(self):
  exp=(R/'scripts/zee_paper1_F17_exact_complex_F16_json.m').read_text()
  helper=(R/'scripts/zee_paper1_F17_exact_complex_json_helpers.m').read_text()
  selftest=(R/'scripts/zee_paper1_F17_complex_json_selftest.m').read_text()
  for script in (exp,helper,selftest):check(script)
  self.assertIn('zeeF17GetMat[o_Association,name_String,dims_List]',helper)
  self.assertNotIn('name_String_',helper)
  self.assertIn('zeeF17Matrices[o]',exp)
  self.assertIn('ExportString[payload,"RawJSON"]',exp)
  self.assertIn('ImportString[jsonText,"RawJSON"]',exp)
  self.assertIn('F17_COMPLEX_MATRIX_JSON_SELFTEST_PASS',selftest)
 def test_launcher_archives_only_invalid_generated_f17_json(self):
  sh=(R/'scripts/zee_paper1_F17_local_UFO_inspection_one_shot.sh').read_text()
  self.assertIn('F17_QUARANTINED_INVALID_GENERATED_JSON',sh)
  self.assertIn('F17_verify_complex_json.py',sh)
  self.assertIn('F17_complex_json_selftest.m',sh)
  self.assertIn('F17_FAIL_CLOSED_COMPLEX_JSON_MATHEMATICA_SELFTEST',sh)
if __name__=='__main__':unittest.main()
