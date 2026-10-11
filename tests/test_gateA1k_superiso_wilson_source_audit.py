"""Synthetic source-map tests. These do not certify SuperIso physics."""
import pathlib
import sys
import tempfile
import unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from gateA1k_superiso_wilson_source_audit import audit, inspect_file, make_text_report

class TestSuperIsoSourceAudit(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=pathlib.Path(self.tmp.name)
        (self.root/"src").mkdir()
        for path,text in {
            "Makefile": "thdm: 2HDMC\nscan_coeffs: predict\n",
            "thdm.c": "int main(int argc,char **argv){return 0;}\n",
            "src/2hdmc.c": "/* THDM bridge */\n",
            "src/wilson.c": """/* THDM Type-II */
void CW_calculator(struct parameters *p) {
  double C7=0;
  double C8=0;
}
void C_calculator_base1(void) {}
void C_calculator_base2(void) {}
""",
            "src/bsgamma.c": "double bsgamma(void) { return 0; }\n",
            "src/include.h": "struct parameters {int THDM_model;};\n",
            "scan_coeffs.c": "int main(void){return 0;}\n",
            "predict.c": "int main(void){return 0;}\n",
        }.items():
            (self.root/path).write_text(text)

    def test_locates_symbols_and_preserves_line_numbers(self):
        result=audit(self.root)
        wilson=result["files"]["src/wilson.c"]
        self.assertEqual(wilson["matching_signatures"]["CW_calculator"],[2])
        self.assertEqual(wilson["matching_signatures"]["C_calculator_base1"],[6])
        self.assertEqual(wilson["matches"][0]["line_numbers_first"],[2])
        self.assertEqual(len(wilson["sha256"]),64)

    def test_never_infers_zee_match_from_source_names(self):
        r=audit(self.root)
        self.assertIn("NOT_TWO_CHARGED",r["status"])
        self.assertFalse(r["observations"]["two_charged_state_Zee_implementation_verified"])
        self.assertFalse(r["observations"]["typeII_2HDM_control_calculated"])
        self.assertFalse(r["observations"]["physical_B_to_Xs_gamma_Zee_calculated"])

    def test_missing_mandatory_source_is_explicit(self):
        (self.root/"src/wilson.c").unlink()
        r=audit(self.root)
        self.assertIn("wilson.c",r["critical_missing"][0])
        self.assertIn("INCOMPLETE",r["status"])

    def test_missing_vendor_directory_rejected(self):
        with self.assertRaises(ValueError):
            audit(self.root/"nonexistent")

    def test_bounded_excerpt_and_report(self):
        r=audit(self.root,max_hits=1)
        d=r["files"]["src/wilson.c"]
        self.assertEqual(d["matches"][0]["line_numbers_first"],[2])
        self.assertIn("L     2",make_text_report(r))
        self.assertIn("NO ZEE",make_text_report(r))

    def test_capture_does_not_modify_sources(self):
        path=self.root/"src/wilson.c"
        before=path.read_bytes()
        audit(self.root)
        self.assertEqual(before,path.read_bytes())

if __name__=="__main__":
    unittest.main()
