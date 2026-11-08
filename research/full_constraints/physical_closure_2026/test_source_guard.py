import importlib.util,unittest
from pathlib import Path
P=Path(__file__).with_name('audit_join.py')
spec=importlib.util.spec_from_file_location('audit_join',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class SourceGuard(unittest.TestCase):
 def test_actual_source_mismatch_rejected_before_output(self):
  p=m.COVER;before=m.PINS[p];m.PINS[p]='0'*64
  try:
   with self.assertRaisesRegex(ValueError,'source hash mismatch'):m.main()
  finally:m.PINS[p]=before
if __name__=='__main__':unittest.main()
