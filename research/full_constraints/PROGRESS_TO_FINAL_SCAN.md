# Progress to one final full-constraint scan — 2026-11-07

**h125 signal-strength task:** [report](HIGGS_H125_SIGNAL_STRENGTH_REPORT.md) releases three width-independent rate ratios, a corrected-charm standard/LFV width ledger, and original-card h125-only LO production ratios. Absolute μ and the scoped experimental comparison remain UNKNOWN: virtual-exotic/invisible materiality and uncertainty/acceptance gates are open. No final-scan authorization or full-Higgs milestone increase.

**Status:** NOT_AUTHORIZED / FULL_CONSTRAINTS_BLOCKED.
**Evidence HEAD at start:** `e72c7b4a177d2b98aa9167ba3afda4d711e85825`.
**Interpretation:** Bars below count defined validation milestones, **not** percentage of physics theory completed, probability of success or compute time. A partial observable is not a physical exclusion.

| Stage | Milestones completed | Progress | Gate |
| --- | ---: | --- | --- |
| Scan/Condor/recovery/streaming export | 6/6 | ██████████ | CODE_READY (actual AF preflight still pending) |
| Scalar reconstruction/BFB/unitarity | 4/4 | ██████████ | PASS within declared tree/sufficient-certificate scope |
| EWPO | 3/3 | ██████████ | PASS scoped scalar one-loop STU |
| Radiative neutrino fit | 3/3 | ██████████ | PASS scoped fixed target/NO/IO reconstruction |
| Full-field vacuum | 2/4 | █████░░░░░ | Tree potential and D10 sufficient certificate; global exhaustive classification UNKNOWN |
| B→Xsγ physical exclusion | 2/5 | ████░░░░░░ | BLOCKED: HEPfit now executes coherent NLO rates; matched physical reference, NP uncertainty and confidence remain open |
| Full-model LFV exclusion | 2/6 | ███░░░░░░░ | BLOCKED: missing gauge aggregates, full three-body/conversion operator vectors and physical comparison |
| Full Higgs exclusion | 2/6 | ███░░░░░░░ | BLOCKED: Zγ/full h125, H/A, H1/extra energy/process rates, fit/uncertainty |
| Validated charged-cascade publication inputs | 2/3 | ██████░░░░ | D4 tree full 2-body rates and 16 point-source H2 LO production; broader rates conditional/deferred |
| Final AF config, preflight and authorization | 0/3 | ░░░░░░░░░░ | NOT STARTED; user will choose count, seed, arms/shards and authorize one large scan |

## Explicit milestone definitions

- **B (2/5):** ✓ coherent two-charged-state LO/NLO matching; ✓ executable internally checked nonlinear kernel; ☐ independently matched physical SM/one-state reference; ☐ defensible NP theory/parametric uncertainty and omitted effects; ☐ qualified confidence/exclusion adapter.
- **LFV (2/6):** ✓ source-matched one-loop dipoles; ✓ photon-mediated two-loop subsets; ☐ full gauge-invariant leading two-loop sum; ☐ complete three-body source-matched operator vector including interference; ☐ complete conversion rate and target nuclear response; ☐ full experimental physical comparison. Independent contact-rate trace validation is extra evidence, not proof of its missing model coefficients.
- **Higgs (2/6):** ✓ 310 HB limits + 159 HS observable applicability inventory; ✓ independently validated full leading h125 γγ amplitude with H1/H2; ☐ h125 Zγ and coherent width/production; ☐ H/A production, competing widths (**partial advance:** actual SusHi 1.7.0 13-TeV ggF/bbH on original D7/F13, independently validated; HDECAY D7 partial widths and native Zee charged-W/lepton additions executed; complete widths still missing); ☐ H1 plus missing H2 production energies/channels and signal-model qualification; ☐ full valid HB/HS theory/experimental confidence interpretation.
- **Vacuum (2/4):** ✓ ten-field polynomial/potential check; ✓ D10 **sufficient** PASS certificate method; ☐ complete gauge-reduced model stationary-point enumeration; ☐ independently certified global energy ordering for required points. 33 of previous 225 certificates PASS, 192 UNKNOWN — these are data counts, not 15% 'validation progress'.
- **Collider (2/3):** ✓ tree on-shell decay inventory; ✓ real sourced H2 LO production at 16 historical points; ☐ matched production for other chosen benchmarks and qualified theory/recast as needed. This last point may be post-scan and does not excuse omitted mandatory theory constraints.
- **AF (0/3):** ☐ choose immutable final configuration/seed/shards/arms; ☐ actual AF source/runtime/disk/resource preflight; ☐ explicit user authorization to generate and submit one final scan.

**Critical mandatory physics hard gates: B, LFV and Higgs = 0/3 complete.**
The user additionally seeks a defensible treatment of vacuum UNKNOWN.
The code being ready does NOT authorize the final full-constrained scan.
All scanned outcomes must continue to use `global_acceptance=null` while any mandatory observable is unvalidated.

## Source of truth

- `research/full_constraints/FEASIBILITY_GATE.md`
- `research/full_constraints/bsgamma_hepfit/HEPFIT_RATE_REPORT.md` — 37 real HEPfit runs, published NNLO table interpolation, coherent NLO bridge and shared-input SuperIso decomposition; 18 tests pass; full B milestone count remains 2/5.
- `research/full_constraints/LFV_EXECUTION_REPORT.md`
- `research/full_constraints/HIGGS_EXECUTION_REPORT.md`
- `research/full_constraints/HIGGS_SUSHI_EXECUTION.md` — actual neutral production and partial-width advance, no new physical exclusion; milestone count remains 2/6.
- `research/full_constraints/CONSTRAINT_COMPLETION_READINESS.md`
- Frozen code: `module14/FINAL_PHYSICS_FREEZE.md`

**Update this scorecard only when new independent source/numerical evidence passes the corresponding gate.** Do not automatically increment on a new file, passing unit test, source inventory, or package build. Prioritize a real physical observable over inflated percentage-complete indicators.

[Neutral-width update](HIGGS_NEUTRAL_WIDTH_SEARCH_REPORT.md): F13 HDECAY
and independently validated leading H/A gamma gamma on original D7/F13
are now executed (35 Higgs tests pass). This advances the partial H/A
prediction evidence, but does not finish that milestone: mixed H Zgamma,
off-shell/finite-daughter effects, loop A WW/ZZ and uncertainty/acceptance
qualification remain missing. ATLAS ID 200212223 rejects all four
incomplete signals before BR construction. Higgs remains 2/6, no new
physical exclusions, final scan NOT_AUTHORIZED.


Fixed-card uncertainty gate: [UNCERTAINTY_REPORT.md](bsgamma_hepfit/UNCERTAINTY_REPORT.md) records 69 new nuisance/scale executions, correlated partial errors and an unresolved Wilson-dependent theory budget. Historical table confidence root 473.1 GeV does not exactly reproduce 480 GeV. Specialist input required; B_FULL_RATE_BLOCKED, physical_bsgamma=UNKNOWN, exclusion=null, theory_sigma=null. Milestones unchanged.
