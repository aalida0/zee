# P1 N2: neutral Zee gauge and charged-pair LO two-body partial widths

## Source and scope

The preceding genuine AF N1 result completed 309/309 scalar/neutrino optimized Yukawa configurations, 309 h125 exact LFV width closure, and HiggsBounds=0. Its neutral included-channel sums are not physical total widths and are subject to missing neutral gauge/scalar and h125 off-shell decays.

The new N2 code uses original scalar CP-conserving Zee mixing conventions from Florentino, Romão and Silva, *Eur. Phys. J. C* **81** (2021) 1148, doi:10.1140/epjc/s10052-021-09956-2, the original Gate6_Benchmark reconstructed potential and the unmodified Gate6 source vector and scalar width phase-space conventions.

### New genuine gauge-kinetic channels

- Neutral h/H to A Z when open, and CP-odd A to Z h or Z H. Alignment delta=beta-alpha, hAZ coupling magnitude proportional to sin(delta), HAZ coupling magnitude proportional to cos(delta), and hWW normalized to cos(delta).
- Neutral h/H/A to each charged H1/H2 and W gauge boson. Both W-charge conjugate final states are counted independently and summed. Charged doublet content is cos(gamma) for H1, sin(gamma) for H2; neutral weights are sin(delta) for h, cos(delta) for H and 1 for A.

### New genuine scalar-potential channels

Use the exact original Gate6 weak-basis charged-scalar mass-Hessian derivatives dM_charged²/dv1 and dM_charged²/dv2 to compute the neutral h/H cubic coupling to H_i+ H_j-. Rotate with the original charged Goldstone-H1-H2 orthogonal eigenvectors. The offdiagonal h/H-H1-H2 coupling must close exactly against the original unmodified Gate6 trilinears source for each E2 scalar model, otherwise fail. Calculate h/H->H1+H1-, H1+H2- plus its charge conjugate, H2+H2-. Mixed charge final states get a factor two, diagonal charged pairs do not.

All channels use on-shell tree-level phase space only. The next actual 309 calculation will quantify H->H1+H1- and A->H1± W∓ contributions for the eight original priority spectra, relative to the N1 included sums.

**N2 is still NOT a complete decay model.** Omitted neutral scalar cubic H->hh, H->AA, possibly A->mixed charged pairs, loop and off-shell decay rates, running quark masses, QCD radiative corrections and other heavy Higgs channels remain. N1/N2 numbers are INCLUDED ONLY. The current Type-II-like quark Yukawas are still an ansatz. No production calculations or experimental HiggsBounds exclusions are assigned.

## One AF command (reuses completed N1 source)

~~~bash
cd /home/aalida/zee
git switch feature/global-scan-priority1
git pull --ff-only
bash scripts/zee_priority1_N2_one_shot.sh
~~~

The runner executes original B3 and N1 tests, seven numerical N2 gauge/pair source regressions and five N1-to-N2 preservation tests; checks the original N1 summary/export SHA and source-unchanged original E2/E3/charged 309 parent source; computes N2 additional modes for ALL ORIGINAL 309 points; and builds a *new* source-pinned five-state partial decay export joined through the canonical Priority-1 CLI.

Output directory: work/p1_original_309_neutral_bosonic_N2_20261020_v1/
- P1_N2_309_h_H_A_H1_H2_MORE_PARTIAL_LO_NOT_COMPLETE.json
- joined_five_gate_report/summary.json
- summary.json (N1-vs-N2 neutral sums and new H1H1, H1W widths for the eight original priority benchmarks)

Expected P1 gate: 309 BLOCKED_DECAY_CHANNEL_COMPLETENESS, zero HiggsBounds calculations, no allowed/excluded model claims. Previous E2/E3/B3/N1 files are only read, never changed.

The next priority within scalar widths is deriving and validating H->hh and H->AA from the full neutral potential; then realistic off-shell/loop/QCD corrections, validated full production and HiggsBounds. None is claimed complete by N2.
