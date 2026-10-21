# F13 — Final finite heavy charged Zee flavor-aware feasibility test (21 Oct 2026)

## One AF command

```bash
cd /home/aalida/zee && git switch feature/global-scan-priority1 && git pull --ff-only && bash scripts/zee_paper1_F13_heavy_final_one_shot.sh
```

By default: *450* new Florentino-P1-inspired heavy scalar seed attempts, up to *6* genuinely scalar/EWPO-screened starts, *3200* coupled scalar/flavor-guided Metropolis proposals, up to *8* mass/mixing-distinct candidate spectra for exact fixed-NO complex neutrino reconstruction, *80* Yukawa trials each, and *2* local partial-LFV optimizations at up to *250* evaluations each. This is a **bounded final exploratory feasibility experiment**. To extend a specific axis, run the wrapper with `--steps 10000 --seed-attempts 1500 --trials 300`; such changes are new sampling and should not be confused with a larger physical CL.

### Domain and physical inputs

- (550\le m_{H_1^\pm}\le720\,\mathrm{GeV}), (m_{H_2^\pm}>m_{H_1^\pm}+m_Z), and (m_{H_2^\pm}\le1600\,\mathrm{GeV}).
- P1 Table 2 of Florentino/Romão/Silva 2021 (arXiv:2106.08332) supplies **a mass region**, not a fully specified benchmark. Seed masses, gamma, beta, neutral masses and singlet quartics are new P1-*inspired* user choices, always recorded as such.
- Every admitted seed and walk proposal is independently converted to the actual reconstructed scalar-potential parameters and screened by original B4 sufficient quartic BFB, tree 2->2 unitarity, and two correlated EWPO/STU fits. **The model-specific global minimum/charge breaking, HiggsTools, one/two-loop RGE and quark flavor alignment are NOT thereby certified.**
- At each scalar/EWPO passing proposal, the source-pinned A1S SuperIso C probe physically calculates *both* charged scalars' LO (\Delta C_7,\Delta C_8) at exactly (\mu_0=160\,\mathrm{GeV}) with the Type-II-like quark and mixing conventions, plus a same-(\tan\beta), degenerate pure-Type-II 670 GeV control. The coherent Zee Wilson vectors enter the **2026 published Eq.(4)** Misiak et al. (arXiv:2608.29863): `10^4 BR = 3.54 - 8.51*deltaC7 - 2.16*deltaC8`. The diagnostic uses experimental `3.49±0.19` and 2026 SM `3.54±0.14`, all in 1e-4.
- **True flavor-informed proposal objective**:
  `F = cascade_included_nonleptonic_proxy - 0.55 * max(0, |z_screen|-1.96) - 0.10 * max(0,|z_screen|-2.4)`.
  This is **not** a real negative log likelihood or a Bayesian posterior. Its Metropolis acceptance is an adaptive numerical search heuristic, not an inference procedure. The solver searches in the full scalar potential and mixing coordinates, NOT gamma at fixed unphysical scalar masses.
- Candidate priority: first select actual scalar/EWPO passing points with ( |z_\mathrm{screen}|<1.96) **and** included-channel proxy \(\ge0.10\), if any. If none, select nearest-border/high-proxy mass-diverse points, and report the failure explicitly rather than assigning exclusions.
- The prioritized candidates undergo **independent** E4A three-QCD-order matching probe (ONLY coefficients checked, not modern full rate) against A1S LO for H1, H2, and own-tanbeta 670 GeV Type-II; exact fixed-NO neutrino Yukawa reconstruction via existing B2 rank-five solver; existing one-loop/selected fermionic Barr–Zee + tree trilepton LFV **subset** through D2; charged Zee lepton width recalculation with B3. Neutrino likelihood is NOT the modern 2026 NO+IO oscillation likelihood. Missing LFV contributions can interfere.

### Actual CI result before the AF source-backed scan

The GitHub Actions heavy seed workflow exercised real scalar BFB, unitarity and correlated EWPO. Using **160** structured P1-inspired trials at seed 20261021, it found **three** physically reconstructed scalar+EWPO screened starts:
- mH1≈611.299 GeV, mH2≈930.346 GeV, gamma≈0.54626, Gfitter chi2≈0.3425;
- mH1≈551.242 GeV, mH2≈1043.581 GeV, gamma≈0.68433, Gfitter chi2≈0.1359;
- mH1≈666.251 GeV, mH2≈773.234 GeV, gamma≈1.27254, Gfitter chi2≈6.0044.

**Seven F13 tests** passed (GitHub Actions run [39602466160](https://github.com/aalida0/zee/actions/runs/39602466160)). They exercised a 48-proposal actual scalar+EWPO walk with a *synthetic mock* Wilson source, and also ran the **actual heavy-scalar complex neutrino + implemented LFV + lepton-width solver** at `F13_heavy_P1_seed_0073`: status `NEUTRINO_EXACT_WITH_PARTIAL_LFV_AND_INCLUDED_CASCADE_ONLY`, maximum implemented partial LFV diagnostic `1.88315949e-05`. This validates integration of the heavy scalar into the real neutrino/LFV code, not the modern oscillation likelihood or complete LFV. The **AF run is required** to use original source-compiled and F6 source-hash-validated SuperIso A1S/E4A coefficient probes. Neither the CI mock inputs nor the three heavy scalar seed points are physical Zee model allowed points. On CI, the exact F13 original F6 source compilation cannot run because the user's AF-local pinned vendor is unavailable.

### Outputs (new timestamped folder)

The one-shot wrapper creates `/home/aalida/zee/work/zee_paper1_F13_heavy_final_<UTCstamp>/`, logs to `<folder>_console.log`, never overwrites old sources:

- `F13_heavy_P1_seeds_NOT_ALLOWED.csv` — genuine scalar/EWPO seed records.
- `F13_all_heavy_scalar_2026LO_flavor_screen_NOT_ALLOWED.csv` — newly evaluated scalar potential points, original B4 screen, source-matched LO C7/C8, Eq.4 BR, illustrative z, same-tanbeta Type-II670 comparator, included-channel cascade proxy.
- `F13_selected_priority_scalar_2026LO_NOT_ALLOWED.csv` — selected for leptonic flavor solving and independent A1S/E4A crosscheck.
- `F13_priority_01_NOT_ALLOWED.json`, etc. — exact complex Yukawa solution, partial LFV, modified lepton widths, full source parameters and explicit missing-physics.
- `F13_ranked_heavy_neutrino_LFV_2026Eq4_NOT_ALLOWED.csv` — the *same* prioritized scalar spectra with fixed-NO neutrino, partial LFV and included-channel corrected cascade proxy.
- `summary.json`, `manifest.json`, source hashes, compiled A1S/E4A source binaries.

### Finite decision, NOT publication claim

F13 prints one of:

- `PRELIM_SCREEN_GO_ONLY_CONTINUE_FULL_THEORY_NO_PAPER_GO`: at least one heavy scalar model meets the **illustrative** Eq4 `|z|<1.96`, included-channel proxy >=0.10, fixed-NO neutrino target and implemented **partial** LFV references.
- `SCALAR_FLAVOR_DIAGNOSTIC_EXISTS_BUT_NEUTRINO_SUBSET_UNRESOLVED`: scalar/flavor diagnostic configurations exist but pilot does not establish the fixed-NO plus partial-LFV coexistence.
- `NO_HIGH_CASCADE_BELOW_FLAVOR_DIAGNOSTIC_IN_FINITE_HEAVY_PILOT`: finite seeded search failed. This is NOT an exclusion of unsearched scalar regions, or an established Zee cascade no-go.

**None** is a physical Zee allowed/excluded statement, 2026 calibrated 95% CL, actual pb hadronic rate, or a scientific paper GO. The unsolved work remains full NNLO-consistent BSM rate and theory covariance, modern neutrino oscillation likelihood, LFV boxes/conversion and all Barr–Zee contributions, HiggsTools, quark-alignment FCNC, global charge-breaking vacuum, all full widths and 13.6/14 TeV production.
