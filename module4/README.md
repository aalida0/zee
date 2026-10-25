# Module 4

Native SARAH vertex audit and signed fermion/photon Barr–Zee amplitudes.
Implementation 1.1.0; scientific status **PARTIAL**. Validated fermion/photon
terms are coherently included with the frozen Module3 components. W candidates
remain excluded pending complete off-shell LFV gauge matching.

See [MATCHING_AUDIT.md](MATCHING_AUDIT.md) for the source-to-equation derivation
and exact W discrepancy, [CONVENTIONS.md](CONVENTIONS.md) for the interface,
and [validation status](../validation/module4/STATUS.md) for actual residuals.

```
bash scripts/run_module4_validation.sh --all-tests
python -m module4.interface --input module4/example.json \
  --output validation/module4/local/example_output.json
```

Python: `from module4.interface import evaluate`; pass a v1 record matching
`input.schema.json`. An optional complete Module3 output is verified and
preserved. No neutrino fit is recomputed. No exclusions are inferred.
