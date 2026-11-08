# Reproduction

From repository root, with Python 3, NumPy and SciPy and the pinned source checkout cached at `/tmp/zee-public-source/general-2hdm-pheno-*/` (author commit b5035cd58d2a7e4a91e9790d045df062b97adffe; thdm.py SHA-256 in INPUT_MANIFEST.json):

```
python3 research/full_constraints/lfv_integrated_2026/run_integrated.py
python3 research/full_constraints/lfv_integrated_2026/test_integrated.py
```

The script verifies source and original archive hashes, reads immutable prior results, extracts the two author hZ assignments, and writes only this directory. The archived quadrature differences are rounded and use a slightly different Z mass, so the hZ comparison is a diagnostic; see report. Runtime versions appear in TEST_RESULTS.json. This is not a rerun of Zγ or the previous provenance checks.
