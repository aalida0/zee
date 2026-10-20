"""Read-only A1P finite-three-loop probe arithmetic and parser tests."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from gateA1p_audit_nnlo_finite_functions import (
    read_finite,decompose,raw_hepfit,MASSES,
    select_existing_library_dirs,recover_hepfit_runtime)
from gateA1p_audit_effective_operator_basis import HEPFIT_CODE_Z,Y

def fixture():
    rows=[
        "STATUS GATE_A1P_ACTUAL_SUPERISO_THREE_LOOP_FINITE_HELPERS_NO_BR",
        "INPUT mt_fixed_GeV=163.10709645657508",
    ]
    for m in MASSES:
        for op in (7,8):
            rows.append(f"FINITE mH={m:.17g} op={op} term=ct value={op*.125:.17g}")
            rows.append(f"FINITE mH={m:.17g} op={op} term=fr value={-op*.5:.17g}")
    return rows

class TestA1PFiniteMatching(unittest.TestCase):
    def test_stale_saved_runtime_directory_does_not_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            working=root/"workinglib"
            working.mkdir()
            binary=root/"reference"
            binary.write_text("fixture not executed")
            log=root/"saved_paths.txt"
            stale=str(root/"stale_lib")
            log.write_text(f"LD_LIBRARY_PATH={stale}:{working}\n")
            ldd=subprocess.CompletedProcess(
                args=["ldd",str(binary)],returncode=0,
                stdout="libgsl.so.28 => /valid/libgsl.so.28\n"
                       "libopenblas.so.0 => /valid/libopenblas.so.0\n",
                stderr="")
            with patch.dict(os.environ,{
                    "LD_LIBRARY_PATH":"",
                    "GATE_A1P_KEY4HEP_ROOT":str(root/"absent_release")}), \
                 patch("gateA1p_audit_nnlo_finite_functions.subprocess.run",
                       return_value=ldd) as check:
                env=recover_hepfit_runtime(binary,log,root)
            self.assertEqual(env["LD_LIBRARY_PATH"],str(working))
            self.assertIn(stale,
                __import__("json").loads(
                    (root/"hepfit_finite_runtime_paths.json").read_text()
                )["ignored_stale_LD_LIBRARY_PATH_entries"])
            self.assertEqual(check.call_count,1)

    def test_stale_runtime_is_rejected_only_when_ldd_dependency_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            lib=root/"available"
            lib.mkdir()
            binary=root/"reference"
            binary.write_text("fixture")
            saved=root/"saved.txt"
            saved.write_text(f"LD_LIBRARY_PATH={root/'stale'}:{lib}\n")
            ldd=subprocess.CompletedProcess(
                args=["ldd",str(binary)],returncode=0,
                stdout="libgsl.so.28 => not found\n",
                stderr="")
            with patch.dict(os.environ,{
                    "LD_LIBRARY_PATH":"",
                    "GATE_A1P_KEY4HEP_ROOT":str(root/"absent_release")}), \
                 patch("gateA1p_audit_nnlo_finite_functions.subprocess.run",
                       return_value=ldd):
                with self.assertRaisesRegex(
                    ValueError,r"unresolved=\['libgsl.so.28'\]"):
                    recover_hepfit_runtime(binary,saved,root)
            self.assertTrue((root/"hepfit_finite_runtime_ldd.log").is_file())

    def test_key4hep_matching_gsl_openblas_discovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            prefix=root/"key4hep_release"
            gsl=prefix/"gsl"/"2.8-test"/"lib"
            openblas=prefix/"openblas"/"0.3-test"/"lib"
            gsl.mkdir(parents=True)
            openblas.mkdir(parents=True)
            (gsl/"libgsl.so.28").write_text("fixture soname")
            (openblas/"libopenblas.so.0").write_text("fixture soname")
            binary=root/"reference"
            binary.write_text("fixture")
            saved=root/"saved.txt"
            saved.write_text(f"LD_LIBRARY_PATH={root/'stale'}\n")
            ldd=subprocess.CompletedProcess(
                args=["ldd",str(binary)],returncode=0,
                stdout=(f"libgsl.so.28 => {gsl}/libgsl.so.28\n"
                        f"libopenblas.so.0 => {openblas}/libopenblas.so.0\n"),
                stderr="")
            with patch.dict(os.environ,{
                    "LD_LIBRARY_PATH":"",
                    "GATE_A1P_KEY4HEP_ROOT":str(prefix)},clear=True), \
                 patch("gateA1p_audit_nnlo_finite_functions.subprocess.run",
                       return_value=ldd):
                env=recover_hepfit_runtime(binary,saved,root)
            chosen=env["LD_LIBRARY_PATH"].split(":")
            self.assertIn(str(gsl),chosen)
            self.assertIn(str(openblas),chosen)
            self.assertEqual(len(chosen),2)

    def test_reject_bad_explicit_library_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            binary=root/"reference"
            binary.write_text("fixture")
            with patch.dict(os.environ,{
                "GATE_A1P_GSL_LIBDIR":str(root/"missing_gsl")}), \
                 self.assertRaisesRegex(ValueError,"does not contain libgsl.so.28"):
                recover_hepfit_runtime(binary,None,root)

    def test_filter_runtime_paths_preserves_order_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            valid=root/"good"
            valid.mkdir()
            active,missing=select_existing_library_dirs(
                [str(root/"stale"),str(valid),str(valid),"",str(root/"stale")])
            self.assertEqual(active,[str(valid)])
            self.assertEqual(missing,[str(root/"stale")])

    def test_direct_cot2_and_cross_term_decomposition(self):
        cot_part,fr_part=5.72,-1.333
        t1,t2=5.597170833164245,2*5.597170833164245
        d1=cot_part/t1**2+fr_part
        d2=cot_part/t2**2+fr_part
        c,f=decompose(d1,d2,t1,t2)
        self.assertAlmostEqual(c,cot_part,places=12)
        self.assertAlmostEqual(f,fr_part,places=12)

    def test_finite_parser_completeness(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"finite.txt"
            f.write_text("\n".join(fixture())+"\n")
            data=read_finite(f,163.10709645657508)
            self.assertEqual(len(data),16)
            self.assertAlmostEqual(data[700.,8,"ct"],1.)

    def test_finite_parser_rejects_missing_point(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"finite.txt"
            f.write_text("\n".join(fixture()[:-1])+"\n")
            with self.assertRaisesRegex(ValueError,"Missing/unexpected"):
                read_finite(f,163.10709645657508)

    def test_finite_parser_rejects_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"finite.txt"
            lines=fixture()
            f.write_text("\n".join(lines+[lines[2]])+"\n")
            with self.assertRaisesRegex(ValueError,"Duplicated"):
                read_finite(f,163.10709645657508)

    def test_finite_parser_rejects_wrong_mt(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"finite.txt"
            f.write_text("\n".join(fixture())+"\n")
            with self.assertRaisesRegex(ValueError,"top mass mismatch"):
                read_finite(f,163.0)

    def test_hepfit_actual_c8_minus20_shift(self):
        vec={(2,i):i*0.043 for i in (3,4,5,6,7,8)}
        code_direct=vec[2,8]-sum(HEPFIT_CODE_Z[i]*vec[2,i]
                                   for i in (3,4,5,6))
        self.assertAlmostEqual(raw_hepfit(vec,8),code_direct)
        standard_wrong=vec[2,8]-sum(
            {3:1,4:-1/6,5:20,6:-10/3}[i]*vec[2,i]
            for i in (3,4,5,6))
        self.assertAlmostEqual(
            raw_hepfit(vec,8)-standard_wrong,40.*vec[2,5])

    def test_hepfit_c7_basis_uses_y_vector(self):
        vec={(2,i):i*.01 for i in (3,4,5,6,7,8)}
        reference=vec[2,7]-sum(Y[i]*vec[2,i] for i in (3,4,5,6))
        self.assertAlmostEqual(raw_hepfit(vec,7),reference)

    def test_degenerate_tanbeta_controls_rejected(self):
        with self.assertRaisesRegex(ValueError,"degenerate"):
            decompose(1.,2.,5.,5.)

if __name__=="__main__":
    unittest.main()
