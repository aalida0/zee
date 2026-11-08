# Zγ continuation — 8 November 2026

**Result: scoped neutral heavy-fermion Zγ transfer validated against the pinned author implementation for the tested configurations. Physical LFV remains UNKNOWN.** This continuation supersedes the earlier chirality blocker in `EXECUTION_REPORT.md` and `REVIEW_ADDENDUM.md`; those original documents and their test receipts have been preserved. Their asserted source mapping and proposed repeat of the photon match are obsolete. No hZ coefficient is added.

The corrected map is `rho_l = D/sqrt(2)`, `c_L ∝ D[e,mu]/sqrt(2)`, `c_R ∝ conj(D[mu,e])/sqrt(2)` and `C_X = -c_X/(8 pi² v²)`. The independently signed photon-subset comparison already archived in `module14/physics_adapters/lfv_reference_evidence.json` establishes the source/native convention for that subset; it was not rerun or added a second time. The earlier four independent f3/f4 loop-pair comparisons remain in `TEST_RESULTS.json`; they were not rerun.

## Validation and method

`continue_zgamma.py` evaluates the complete neutral-fermion Z-exchange terms of arXiv:2410.17313v4 Eqs. (54)–(55), for t, c, b and tau and all three neutral states. It computes f3/f4 from independent one-dimensional Feynman-parameter quadratures and uses a compact separate contraction of the couplings. For the reference it reuses the archived `lfv_reference.py` AST extraction of the four author fermion assignments, with f1 and f2 set to zero in the extracted functions' global namespace; this projects the photon terms away without modifying the source or frozen modules. The two calculations share the author model input/mixing accessors and masses; they are independent in loop evaluation and coefficient assembly, not independent model-convention derivations. The corrected paper version and author implementation are compared; the full erratum equations were not independently reviewed here.

Two distinct analytic controls with complex up, down and lepton diagonal Yukawas, complex off-diagonal Yukawas, and nonzero general neutral mixing matched both complete complex chiralities. Maximum relative discrepancy was **3.03e-14**, against a predeclared code tolerance of 2e-7. Four additional one-sided checks isolate D[e,mu] and D[mu,e] for each control; the nonzero coefficient is in C_L and C_R respectively and agrees with the author. The four exact-card coefficients also agree with the author projection, worst relative discrepancy 5.30e-14. These controls cover coefficient matching, not the complete general Zee amplitude or its omitted theoretical uncertainty.

Author source: commit `b5035cd58d2a7e4a91e9790d045df062b97adffe`, `thdm.py` SHA-256 `9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193`. The existing source example electroweak inputs are used: alpha=1/129, sin²θW=0.23129, mZ=91.188 GeV, with its running quark masses and Type-II Yukawa prescription as in the archived photon reference; scalar parameters and lepton masses come from each frozen witness. This choice is a source-scheme diagnostic; no uncertainty from input schemes or missing higher orders is estimated.

The source archive SHA-256 is `f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8`. The original previously hash-verified `CARD_PROVENANCE.json` and signed `BASELINE_REPLAY.json` are reused without reconstruction or replay. Full complex values, scalar and Yukawa hashes, source inputs, baseline and summed coefficients, rates, and conditional norm budgets are in `CONTINUATION_RESULT.json`; actual control values are in `CONTINUATION_TESTS.json`.

## Four frozen texture cards

Complex coefficients below are in GeV⁻²; the rate shift is `(BR_baseline+Zγ − BR_baseline)/BR_baseline`, evaluated with the complex interference identity to avoid cancellation in a subtraction of rounded rates.

| Card | Zγ C_L | Zγ C_R | Relative partial-rate shift |
|---|---|---|---:|
| D7 NO | −1.30502e−29 − 5.22008e−29 i | 2.42971e−27 + 2.42971e−27 i | +1.02229e−12 |
| D7 IO | 4.84044e−28 + 2.17227e−27 i | 1.82228e−27 − 3.87140e−35 i | +8.05537e−13 |
| F13 NO | 6.34588e−31 + 2.24546e−30 i | 1.11080e−29 − 1.11080e−29 i | −7.35462e−15 |
| F13 IO | 5.33705e−30 − 6.92080e−30 i | 3.33240e−29 + 2.22160e−29 i | +5.48923e−14 |

The scoped BR is baseline plus this one group only. Tiny shifts do not constrain the missing amplitudes; numerical agreement between the two formulas does not quantify unknown physics or scheme uncertainties. The source is a leading general-2HDM prescription and has no Zee singlet F. Neutral hZ remains preliminary and is not included; kinetic W/G/ghost, charged-fermion W, mixed charged-scalar HZ/HW, singlet-F gauge and mixed-current contributions, μ→3e and conversion remain unassessed. No physical LFV acceptance or exclusion follows.

Reproduce from the repository root with `python research/full_constraints/lfv_transfer_2026/zgamma/continue_zgamma.py`, with the pinned author checkout in `/tmp/zee-public-source/general-2hdm-pheno-*/`; this writes only the two `CONTINUATION_*.json` results. The original pilot tests and reports are unchanged.
