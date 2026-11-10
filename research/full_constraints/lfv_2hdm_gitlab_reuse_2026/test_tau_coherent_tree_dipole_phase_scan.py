import math
import json
import tempfile
import os
import unittest
from pathlib import Path

import numpy as np
from module3 import tree
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_coherent_tree_dipole_phase_scan import (
    CHANNELS, pairs_to_complex, interference_width, neutral_tree_tensor,compute,
)
from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_exact_dipole_phase_space import (
    photon_tensors, spin_inner,
)


class CoherentTreeDipoleTests(unittest.TestCase):
    def test_complex_pairs_fail_closed(self):
        a=pairs_to_complex([[1.,2.],[3.,-4.]])
        np.testing.assert_array_equal(a,[1+2j,3-4j])
        for bad in ([],[[1,2]],[[float("nan"),0],[1,0]],[[1,2],[0]]):
            with self.assertRaises(ValueError):pairs_to_complex(bad)

    def test_interference_zero_tree(self):
        M,ma,mb=1.77686,0.1056583755,0.1056583755
        ml=np.array([0.00051099895,ma,M])
        c=np.zeros((3,3),complex)
        val=interference_width({"H":(c,400.)},ml,1,1,1e-10,2e-10,ns=16,nz=8)
        self.assertEqual(val,0j)

    def test_local_scalar_tensor_consistency(self):
        M=1.77686;ml=np.array([0.00051099895,0.1056583755,M])
        c=np.diag([0.001,0.01,0.02]).astype(complex)
        c[1,2]=.003+.002j
        sc={"H":(c,420.)}
        ps=tree.momenta(M,(ml[1],ml[1],ml[1]),s=.6,z=.12)
        d,cross,ms=tree.tensors(sc,2,1,1)
        T=neutral_tree_tensor(d,cross,ms,ps)
        self.assertGreater(tree.spin_sum(T,ps,M,(ml[1],)*3),0)
        p,_=photon_tensors(ps,M,1e-9+2e-9j,0.4e-9j,identical=False)
        I=spin_inner(T,p,ps,M,(ml[1],)*3)
        self.assertTrue(math.isfinite(I.real))
        self.assertTrue(math.isfinite(I.imag))

    def test_cp_scaling_and_phase_rephasing_of_interference(self):
        M=1.77686;ml=np.array([0.00051099895,0.1056583755,M])
        c=np.diag([0.001,0.01,0.02]).astype(complex)
        c[1,2]=.003+.002j
        sc={"H":(c,420.)}
        a=interference_width(sc,ml,1,1,1e-9,2e-9j,ns=18,nz=8)
        b=interference_width(sc,ml,1,1,3e-9,6e-9j,ns=18,nz=8)
        self.assertLess(abs(b/a-3),1e-12)
        theta=.57
        rot=complex(math.cos(theta),math.sin(theta))
        co=interference_width(sc,ml,1,1,rot*1e-9,rot*2e-9j,ns=18,nz=8)
        self.assertLess(abs(co/a-rot.conjugate()),2e-12)

    def test_claimed_original_native_json_requires_gate_and_never_becomes_physical(self):
        from research.full_constraints.lfv_2hdm_gitlab_reuse_2026.test_tau_native_sarah_complex_import import (
            synthetic_fixture,
        )
        source=os.environ.get("ZEE_2HDM_PINNED_SOURCE")
        if not source:
            self.skipTest("Pinned corrected source required")
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"SYNTHETIC_TEST_ONLY_NOT_ORIGINAL_SARAH_K2.json"
            path.write_text(json.dumps(synthetic_fixture()))
            r=compute(Path(source),"b5035cd5",ns=20,nz=12,tree_order=10,
                      native_original_json=path)
            self.assertEqual(r["physical_lfv"],"UNKNOWN")
            self.assertIsNone(r["global_acceptance"])
            self.assertTrue(r["source"]["native_source_JSON_imported_norm_checked"])
            self.assertFalse(r["source"]["native_source_JSON_phase_independently_replayed"])
            for card in r["cards"].values():
                for channel in card["channels"].values():
                    self.assertEqual(channel["complex_coefficient_input"],
                                     "claimed_original_native_K2_norm_checked_plus_corrected_neutral_BZ")
                    self.assertTrue(channel["imported_native_source_K2_norm_checked"])
                    self.assertFalse(channel["original_native_complex_source_K2_recovered"])
                    self.assertIsNone(channel["physical_total_BR"])
            bad=synthetic_fixture()
            bad["fortran_sha256"]["generated"]="0"*64
            path.write_text(json.dumps(bad))
            with self.assertRaises(ValueError):
                compute(Path(source),"b5035cd5",ns=20,nz=12,tree_order=10,
                        native_original_json=path)

    def test_four_card_source_fail_closed(self):
        upstream=os.environ.get("ZEE_2HDM_PINNED_SOURCE")
        if not upstream:
            self.skipTest("The source-integration test requires pinned corrected original upstream")
        r=compute(Path(upstream),"b5035cd5",ns=36,nz=16,tree_order=14)
        self.assertEqual(r["physical_lfv"],"UNKNOWN")
        self.assertIsNone(r["global_acceptance"])
        self.assertEqual(len(r["cards"]),4)
        for card,row in r["cards"].items():
            self.assertEqual(len(row["channels"]),len(CHANNELS))
            for name,p in row["channels"].items():
                self.assertTrue(p["relative_phase_not_source_matched"])
                self.assertFalse(p["original_native_complex_source_K2_recovered"])
                self.assertIsNone(p["physical_total_BR"])
                self.assertGreater(p["dipole_constant_K2_BR"],0)
                self.assertGreater(p["tree_BR"],0)
                self.assertGreaterEqual(p["phase_freedom_lower_BR"],0)
                self.assertLessEqual(p["phase_freedom_lower_BR"],p["phase_freedom_upper_BR"])
                self.assertGreaterEqual(p["phase_freedom_upper_BR"],p["tree_dipole_coherent_center_BR"])


if __name__=="__main__":
    unittest.main()
