"""F4c exact quadratic EOS-WC insertion check (synthetic only)."""
import hashlib
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from zee_gateF4c_eos_matching_insertion_audit import (
    quadratic_path, add, checked_vector, validate_prior, STATUS
)
class F4cQuadraticAuditTests(unittest.TestCase):
    def test_quadratic_polynomial_reconstructed(self):
        base={n:0.0 for n in range(1,9)}
        shift={n:0.0 for n in range(1,9)}
        shift[7]=.05
        shift[4]=.003
        def rate(c):
            return 0.00036 + 0.00008*c[7] + 0.0006*c[7]*c[7] \
                   + 0.0002*c[4]*c[7] - 0.00007*c[4]
        result=quadratic_path(rate,base,shift)
        self.assertAlmostEqual(
            result["matching_shift_linear_response"],.00008*.05-.00007*.003)
        self.assertAlmostEqual(
            result["matching_shift_quadratic_response"],
            .0006*.05*.05+.0002*.003*.05)
        self.assertLess(result["max_abs_polynomial_closure"],1e-16)
        self.assertTrue(result[
            "quadratic_only_in_matching_insertion_NOT_alpha_s_order"])

    def test_cubic_refused(self):
        zero={n:0.0 for n in range(1,9)}
        h=dict(zero);h[7]=1.
        with self.assertRaises(ValueError):
            quadratic_path(lambda x: .00036 + 1e-7*x[7]**3,zero,h)

    def test_missing_nonfinite_inputs_refused(self):
        with self.assertRaises(ValueError):
            checked_vector({7:.1},"missing")
        zero={n:0.0 for n in range(1,9)}
        h=dict(zero);h[7]=float("inf")
        with self.assertRaises(ValueError):
            add(zero,h,1.)

    def test_chain_hashes_and_status_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            f4=root/"f4.json"
            f4b=root/"f4b.json"
            hp=root/"hepfit.json"
            rows=[{"mass_GeV":m,"tanbeta":t}
                  for t in (5.6,50.) for m in (300.,580.,670.,1000.)]
            f4_data={"status":"NOT_YET_VALIDATED","a1m_sha256":"same",
                     "controls":rows}
            f4.write_text(json.dumps(f4_data)+"\n")
            fb_data={
                "status":"F4B_ORDER_RESOLVED_DIPOLE_PROJECTOR_NOT_FULL_NLO_RATE",
                "source_wilson_sha256":"same","num_typeII_controls":8,
                "EOS_source_rate_strictly_expanded":False,
                "typeII_results":rows,
                "f4_prior_summary_sha256":hashlib.sha256(f4.read_bytes()).hexdigest()}
            f4b.write_text(json.dumps(fb_data)+"\n")
            hp_data={
                "status":"F4B_INDEPENDENT_MATCHING_LO_NLO_8_NUMERICALLY_CONSISTENT_NOT_RATE",
                "tested_rows":40,"matching_disagreements":0,
                "prior_F4b_summary_sha256":hashlib.sha256(f4b.read_bytes()).hexdigest()}
            hp.write_text(json.dumps(hp_data)+"\n")
            _,_,_,old,new=validate_prior(f4,f4b,hp)
            self.assertEqual(len(old),8)
            self.assertEqual(len(new),8)
            hp_data["matching_disagreements"]=1
            hp.write_text(json.dumps(hp_data))
            with self.assertRaises(ValueError):
                validate_prior(f4,f4b,hp)

    def test_status_remains_explicitly_non_strict(self):
        self.assertIn("NOT_STRICT_NLO", STATUS)

if __name__=="__main__":
    unittest.main()
