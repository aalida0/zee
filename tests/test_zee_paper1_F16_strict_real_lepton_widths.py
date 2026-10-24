#!/usr/bin/env python3
"""F16 regression: strict numeric lepton width checks before independent SARAH PASS."""
import sys, unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'scripts'))
from zee_paper1_F16_wolfram_syntax_lint import check
class TestF16RealWidth(unittest.TestCase):
 def test_sarah_requires_numeric_3x2_lepton_widths(self):
  s=(R/'scripts/zee_paper1_F16_SARAH_three_heavy_vertex_audit.m').read_text()
  check(s)
  self.assertIn('zeeF16RelativeLeptonWidthResidual[lepW,o["LeptonicWidths"]]',s)
  self.assertIn('F16_LEPTON_WIDTH_NONREAL_OR_SYMBOLIC',s)
  self.assertIn('passedCases=!=3',s)
  self.assertIn('F16_CASE_NUMERICAL_PASS',s)
  self.assertNotIn('Map[Max[#,1.*^-14]&,Flatten',s)
 def test_actual_complex_source_matrix_validator(self):
  s=(R/'scripts/zee_paper1_F16_strict_real_lepton_width_residual.m').read_text()
  check(s)
  for piece in ['Dimensions[aa]=!={3,2}', 'Dimensions[bb]=!={3,2}',
                'Im[aa]', 'Im[bb]', 'ar=Re[aa];br=Re[bb]',
                'Abs[#1-#2]/Max[Abs[#2],floor]', 'Return[$Failed]']:
   self.assertIn(piece,s)
 def test_local_mathematica_selftest_in_launcher(self):
  s=(R/'scripts/zee_paper1_F16_strict_real_lepton_width_selftest.m').read_text()
  check(s)
  self.assertIn('F16_LEPTON_WIDTH_NUMERICAL_SELFTEST_PASS',s)
  self.assertIn('F16UnknownSymbol',s)
  sh=(R/'scripts/zee_paper1_F16_local_SARAH_three_heavy_one_shot.sh').read_text()
  self.assertIn('F16_local_lepton_width_selftest.log',sh)
  self.assertIn('F16_FAIL_CLOSED_NONNUMERIC_CHARGED_LEPTON_WIDTH_REGRESSION',sh)
if __name__=='__main__': unittest.main()
