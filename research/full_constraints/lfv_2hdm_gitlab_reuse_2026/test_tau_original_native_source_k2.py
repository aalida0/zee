"""Four-card exact complex one-loop SARAH replay vs independent analytic Module3.

The source-replayed local K2 inputs are source-hash + radiative-rate gated.
This is NOT a two-loop Zee calculation or physical tau three-body acceptance.
"""
import json
import unittest
from pathlib import Path

import numpy as np

from module2.interface import decode
from module3.core import combine, dipole_ledger
from research.full_constraints.lfv_2hdm_transfer_2026.evaluate import read_cards
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_native_sarah_complex_import import (
    validate,
)

HERE = Path(__file__).resolve().parent
DATA = HERE / "ORIGINAL_NATIVE_TAU_K2_REPLAY_2026-11-10.json"


class SourceReplayK2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.input = json.loads(DATA.read_text(encoding="utf-8"))
        cls.validated = validate(cls.input)
        cls.witnesses = read_cards()

    def test_pinned_eight_channels_and_source_norms(self):
        self.assertEqual(self.input["source_replay_scope"].startswith(
            "Original SARAH GenerateGamma2l"), True)
        self.assertEqual(self.input["physical_lfv"], "UNKNOWN")
        self.assertIsNone(self.input["global_acceptance"])
        self.assertEqual(len(self.input["cards"]), 4)
        self.assertLess(self.input["source_replay_max_relative_BR_deviation_vs_frozen_report"],3e-6)
        self.assertEqual(self.validated["physical_lfv"],"UNKNOWN")
        self.assertFalse(self.validated["original_fortran_executed_in_this_validation"])

    def test_original_complex_K2_vs_module3_analytic_one_loop(self):
        # A sign/chirality check at COMPLEX amplitude level, not only |A|².
        # This approximation neglects external invariants and may differ
        # from the generated native source by finite mass effects.
        ids=("D7_NO","D7_IO","F13_NO","F13_IO")
        for short,w in zip(ids,self.witnesses):
            scalar=w["module2_input"]["scalar"]["record"]["physical"]
            ml=w["module2_input"]["lepton_masses_GeV"]
            F=decode(w["yukawas"]["F"])
            D=decode(w["yukawas"]["D"])
            saved=self.validated["cards"][short]
            for channel, j in (("tauegamma",0),("taumugamma",1)):
                ref=np.asarray(combine(dipole_ledger(F,D,scalar,ml,2,j)),dtype=complex)
                item=saved[channel]
                original=np.asarray([
                    complex(*item["module3_CL_from_native"]),
                    complex(*item["module3_CR_from_native"]),
                ])
                residual=np.linalg.norm(ref-original)/max(np.linalg.norm(original),1e-300)
                self.assertLess(residual,0.012,
                     f"{short} {channel}: original SARAH/analytic complex mismatch {residual}")

    def test_reject_arbitrary_phase_even_if_rate_unchanged_by_extra_claim(self):
        # Norm alone cannot prove phase: a source-phase assertion must
        # be backed by the *actual* original local Fortran execution
        # (the provided JSON records that limited replay).
        import copy
        x=copy.deepcopy(self.input)
        v=x["cards"][0]["channels"]["tauegamma"]
        a,b=v["K2L"]
        v["K2L"]=[-b,a]
        # This test demonstrates a limitation of the source INPUT CONTRACT.
        y=validate(x)
        self.assertFalse(y["input_phases_independently_verified"])
        self.assertFalse(y["cards"]["D7_NO"]["tauegamma"]["can_phase_be_verified_from_rate_alone"])

    def test_disallow_full_zee_acceptance_promotion(self):
        self.assertFalse(self.input["full_Zee_two_loop_calculated"])
        self.assertEqual(self.input["physical_lfv"],"UNKNOWN")
        self.assertIsNone(self.input["global_acceptance"])


if __name__=="__main__":
    unittest.main()
