# Reproduction

From repository root, Python 3.10 with SymPy 1.14.0, SciPy 1.15.3, NumPy and mpmath installed:

```
python3 -m unittest discover -s tests -p 'test_module1_d10_*.py' -v
python3 research/full_constraints/candidate_a/witness_check.py
python3 research/full_constraints/candidate_a/witness_check.py 83.452326 249.215787 172.247542 100.351097
sha256sum module1/d10_certificate.py module1/d10_polynomial.py module1/d10_search.py module1/d10_benchmarks.json module1/potential.py validation/module1/d10_vacuum_global.json models/SARAH/ZeeTypeII/ZeeTypeII.m
```

JSON output records rational intervals; compare the results with the two stored proof objects. The script trusts the frozen exact Krawczyk routine for the root enclosure, rather than independently implementing it. Inputs are binary64 coefficients interpreted as exact rationals. Decimal field values are exact complex-field coordinates and are not canonical real r components. This is an exact field-value certificate, not a stationary-point or optimization certificate. The original 9-test output is saved separately. Full package/runtime/provenance and Eq. 23 numerical verification requested by the task were not completed.
