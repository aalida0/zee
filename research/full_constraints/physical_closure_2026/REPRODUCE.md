# Reproduction

Python 3.10.12; run from repository root, using the existing research environment (NumPy, SciPy and the original saved optional native dependencies). No package install, production run or Git write is required. The ignored historical dataset must already exist at `/tmp/zee-d14c-dataset.json`, SHA-256 `2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9`; it is ephemeral and is not distributed by this output. The existing HEPfit table must be at the path in `controls.py`, SHA-256 `4ab62f2e4ab2897232e284060aa14349f54a47b9e47f70c883a8b11e4749a6f8`. Missing or changed inputs stop the audit; they are not zeros. The raw D14 production receipts are absent in this checkout and cannot be recreated by these commands.

```bash
export PYTHONDONTWRITEBYTECODE=1
python3 research/full_constraints/physical_closure_2026/audit_join.py
python3 research/full_constraints/physical_closure_2026/controls.py
python3 research/full_constraints/physical_closure_2026/sector_snapshot.py
python3 research/full_constraints/physical_closure_2026/sector_tables.py
python3 research/full_constraints/physical_closure_2026/gate.py
python3 research/full_constraints/physical_closure_2026/test_gate.py -v
python3 research/full_constraints/physical_closure_2026/test_source_guard.py -v
python3 research/full_constraints/physical_closure_2026/test_outputs.py -v
python3 -m unittest research.full_constraints.lfv.test_source_to_code -v
PYTHONPATH=research/full_constraints/bsgamma_hepfit python3 -m unittest research.full_constraints.bsgamma_hepfit.test_uncertainty -v
python3 -m unittest research.full_constraints.higgs.test_zgamma research.full_constraints.higgs.test_zgamma_source_audit -v
python3 -m unittest discover -s tests -p test_module1_d10_global.py -v
```

`python3 research/full_constraints/physical_closure_2026/finalize.py` runs the focused checks and writes the result after they pass.

The source guard intentionally corrupts an in-memory expected hash and checks refusal before output. Tests and their scopes are in `FINAL_TEST_LOG.txt`; they do not independently compute missing LFV, B or Higgs observables. Historical full-suite failures remain described in `research/full_constraints/candidate_a/final_study/TEST_RECEIPT.md`. This recipe does not rerun the previous vacuum or flavor–cascade materiality exercises.
