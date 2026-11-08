# Reproduction

Run from repository root with Python 3, NumPy, SciPy, SymPy and mpmath. Frozen model and input file hashes are in START_SOURCE_SHA256.txt. `global_acceptance` is null on every row. No event generation, neutrino/LFV fitting, or model-source edits are needed.

```
python research/full_constraints/candidate_a/final_study/verify_independent.py
python research/full_constraints/candidate_a/final_study/verify_symbolic_identity.py
python research/full_constraints/candidate_a/final_study/full_field_check.py
python research/full_constraints/candidate_a/final_study/negative_witnesses.py
python research/full_constraints/candidate_a/final_study/eq23_check.py
python research/full_constraints/candidate_a/final_study/orbit_branch_bound.py
python research/full_constraints/candidate_a/final_study/continuation_preliminary.py
OPENBLAS_NUM_THREADS=1 python research/full_constraints/candidate_a/final_study/finite_start.py
python research/full_constraints/candidate_a/final_study/analyze_study.py
python -m unittest discover -s research/full_constraints/candidate_a/final_study -p 'test_verify_independent.py' -v
python -m unittest discover -s tests -p 'test_module1_d10_global.py' -v
```

The finite-start script resumes from FINITE_START.jsonl; for a full rerun, move that file aside first and restore it afterwards if byte-for-byte provenance is required. Walltimes are machine-dependent. Exact proof scripts intentionally compare regenerated outputs to stored rational records; equation-23 and negative-field scripts write task-local proof objects. `orbit_branch_bound.py` deliberately stops after 2000 nodes and is UNKNOWN. The frozen full test suite was also attempted; its unrelated environment and source-branch failures are recorded in TEST_RECEIPT.md.

The independent fixed-field optimization can also be rerun with `python research/full_constraints/candidate_a/final_study/optimize_witness.py`. The source-level Git delivery blocker and precise resume commands are in WORK_CHECKPOINT.md.
