# D5 completion checkpoint — 2026-10-28

Work resumed from the 2026-10-27 pause without regenerating or overwriting any
completed native export, generator run, receipt, PDF or event directory.

- Workspace: `/home/amine/zee/workspaces/zee-production-d5`
- Branch: `feature/zee-d5-parton-production`
- Origin: `https://github.com/aalida0/zee.git`
- Verified exact D4 ancestor: `d0a276950dfbe0417c6cd22731b7f62f3285d789`
- Frozen Modules0–7 and model files remain unchanged against that ancestor.

The authoritative deliverables are `module8/D5_PRODUCTION_AUDIT.md` and
`validation/module8/d5_production.json`. The real-data schema is
`d5-real-two-process-1.0.0`. All six final five-flavor v2 runs passed the full
real-run validator. Native UFO, executable matrix and independent analytical PDF
checks pass. Eleven scoped tests pass, including seven required arithmetic tests.
The final audit records the integration errors, BR products, source hashes,
physical assumptions and reproduction steps.

Ignored persistent evidence under `validation/module8/local/`:

- `native/`, `export.log`, `ufo_audit.json`, `cards/`: fresh native SARAH4.15.4 /
  Wolfram15.0.1 UFO and 5,904 signed vertex comparisons across 36 cards.
- `P1_full/`, `P2_full/`: completed MG5 3.6.7 process/event directories.
- `receipts/d5_v2_source/`, `receipts/d5_v2_low/`, `receipts/d5_v2_high/`:
  final P1/P2 receipts at mH1=300,250,350 GeV respectively.
- `pdf/NNPDF30_lo_as_0130/`: final five-flavor central PDF, ID263000.
- `mg_matrix_checks.json`, `partonic_checks.json`: executed independent checks.
- `validated_rates.json`, `real_run_validation.log`: final six-run validation.
- `arithmetic_tests.log`, `tests.log`: scoped verification logs.
- Official source archives, extracted MG/LHAPDF trees, release comparison and
  compiled PDF bridge are retained locally. Older receipts are superseded
  diagnostics and must not replace the v2 results.

To revalidate retained evidence (no native reruns needed):

```sh
python -m module8.real_run_validation
python -m unittest discover -s tests -p 'test_module8_production_composition.py' -v > validation/module8/local/arithmetic_tests.log 2>&1
python -m unittest discover -s tests -p 'test_module8_*.py' -v > validation/module8/local/tests.log 2>&1
python -m module8.build_report
git diff --check
```

P3 is not executed: separate 4F PDF / massive-bottom setup absent. Never add 4FS
and 5FS. Production rates are charge-inclusive stable-particle LO reference
benchmarks; P1 is the justified Z-only contribution. No scale/PDF uncertainties,
NLO physical BRs, detector acceptance or reach are claimed.

D5_NOVELTY_NOT_ESTABLISHED remains: 2021 already covers tbH production and the
cascade hierarchy. General-Zee neutrino/LFV correlations need new constrained
work; minute D4 family BR shifts do not establish measurable discrimination.
2026_LINEARIZED_FLAVOR_FILTER_READY=false; COMPLETE_LFV=false;
global_zee_acceptance=null; all D2 vacuum results UNKNOWN; physical 2026 B→Xsγ
incomplete. The audit preserves these independent gates.
