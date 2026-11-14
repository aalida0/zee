"""Executable tests for the real local-only Zee LFV source workflow.

Mocked SPheno physics is only a control-flow test: it is NEVER used as
evidence that private original Fortran has run or that the full model passes.
"""
import json,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
from . import finish_repaired64_local as main

def fixture():
    return {
      'n_original_16x4':64,'n_neutrino_exact_perturbative':64,
      'n_below_MEGII_one_loop':64,'n_below_JILA_pure_2HDM_proxy':64,
      'records':[{'id':1000+i//4,
          'ordering':('NO' if (i%4)//2==0 else 'IO'),
          'seed':20261111+i%2, 'full_physical_LFV':None,
          'global_acceptance':None} for i in range(64)]
    }

class LocalFinishTests(unittest.TestCase):
    def test_accepts_only_complete_source_json_zip(self):
        with tempfile.TemporaryDirectory() as t:
            d=Path(t);raw=json.dumps(fixture())
            f=d/'input.json';f.write_text(raw)
            self.assertEqual(len(json.loads(main.source_json(f,d).read_text())['records']),64)
            z=d/'source.zip'
            with zipfile.ZipFile(z,'w') as ar:
                ar.writestr('out/EDM_SUPPRESSED_64_NEUTRINO_AND_2HDM.json',raw)
            self.assertEqual(main.source_json(z,d).name,main.ZIP_MEMBER)
            bad=fixture();bad['records'].pop()
            f.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):main.source_json(f,d)
            bad=fixture();bad['records'][0]['full_physical_LFV']='PASS'
            f.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):main.source_json(f,d)

    def test_reject_missing_native_source_before_partial_run(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            with self.assertRaises(FileNotFoundError):
                main.preflight(root,root/'missing-original-template')
            self.assertFalse((root/'results').exists())

    def test_mocked_end_to_end_reports_loop_order_not_physical_pass(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t); source=root/'src.json';source.write_text(json.dumps(fixture()))
            tpl=root/'template.in';tpl.write_text('dummy')
            exe=root/'binary';exe.write_bytes(b'fixture-only')
            with patch.object(main,'preflight',return_value=(exe,root/'receipt',{})), \
                 patch.object(main,'stage_cards',return_value={
                    'n_cards':64,'template_provenance':'VALIDATED_USER_NATIVE'}), \
                 patch.object(main,'run_native',return_value={
                    'all_source1loop_three_bounds':64,'n_new_edm3zero_cases':64,
                    'max_1loop_source_observables':{'mu_to_e_gamma':1e-15,
                       'mu_to_3e':1e-17,'mu_to_e_conversion_Au197':1e-17}
                    }):
                result=main.finalize(source,root,tpl,root/'out')
            self.assertEqual(result['status'],'LFV_SOURCE_ONE_LOOP_SCREEN_COMPLETED')
            self.assertIsNone(result['physical_LFV'])
            self.assertIsNone(result['global_zee_acceptance'])
            self.assertEqual(result['full_Zee_two_loop_EDM_and_LFV'],'UNKNOWN')
            self.assertTrue((root/'out'/'SOURCE_ONE_LOOP_FINAL_REPAIR64_RECEIPT.json').is_file())
if __name__=='__main__':unittest.main()
