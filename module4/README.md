# Module 4

Native SARAH vertex audit and source-specific two-loop photon coefficients.
Current scientific status: **PARTIAL**. A signed Davidson/Ilisie discrepancy
blocks coherent use of new two-loop amplitudes. They are exported as UNKNOWN
candidates; the included rate contains only validated frozen Module 3 terms.

See [CONVENTIONS.md](CONVENTIONS.md) for derivations, the conflict and omissions,
and [validation status](../validation/module4/STATUS.md) for actual residuals.

```
bash scripts/run_module4_validation.sh --all-tests
python -m module4.interface --input module4/example.json \
  --output validation/module4/local/example_output.json
```

Python: `from module4.interface import evaluate`; pass a v1 record matching
`input.schema.json`. A complete optional Module 3 output is verified and
preserved. No neutrino fit is recomputed. No experimental exclusions are made.
