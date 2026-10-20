# F8: original 309 Zee full-legacy b->s gamma vs same-kernel Type-II 670 GeV comparator

**Aim.** Test whether B4_0004143 and the other E7 Pareto candidates generate a stronger or weaker **full legacy SuperIso** b->s gamma rate than a standard Type-II 2HDM charged boson of 670 GeV under EXACTLY identical vendor inputs and normalizations. 670 GeV is cited from Misiak et al. arXiv:2608.29863 (2026) as the NEW Type-II 95% CL reference mass, **NOT a Zee-model mass exclusion boundary**. An inequality between legacy rates is NOT automatically an inequality in the 2026 modern likelihood.

## Source of truth: F6 and F7

The F6 AF output completed all 309 original Zee full legacy inclusive BR calculations. Same-vendor SM baseline = 0.0003382457724040796; original Zee median legacy rate = 0.00039484940936; 309/309 legacy NP shifts are positive. F7 ran 309 hypothetical modern-SM+legacy-NP 36-scenario Gaussian sensitivity tests: nominal illustrative pulls [1.963906,2.610230,3.733671] min/median/max, no physical exclusions, and B4_0004143 at 2.3043 would need a hypothetical factor 0.83547 on the old NP shift to reach a 1.96 Gaussian line.

## New physically meaningful source comparison

Load original F6 summary, manifest and all 309 JSONL/CSV rows through the already source-validated `zee_gateF7_309_2026_bsgamma_tension_sensitivity.load_f6()`; this also pins exact F6 source-code SHA and rejects fabricated acceptance flags. Reopen **exact same compiled A1U full legacy SuperIso C executable** from the original F6 archive and assert its compiled binary SHA from the F6 provenance. Never recompile a different vendor version.

Before the full campaign, rerun six ACTUAL source E7 Pareto point (mH1,mH2,gamma,tanbeta) and require their old F6 inclusive BR source values to agree within numerical reproducibility. Also test for 670-GeV degenerate charged masses that gamma=0, gamma=pi/2 and gamma=0.8 yield the identical pure-Type-II full legacy BR, which checks the charged-doublet mixing sum rule in the complete rate engine.

For EACH OF ALL 309 ORIGINAL Zee spectra, evaluate the actual legacy Type-II 670-GeV charged-Higgs rate `A1U(m1=670,m2=670,gamma=0,tanbeta=t_original)`, and define
[
R_{670}^{\rm legacy}(p)=
\frac{\mathcal B_{\rm Zee}^{\rm old}(p)-\mathcal B_{\rm SM}^{\rm old}}
{\mathcal B_{\rm TypeII,670}^{\rm old}(\tan\beta_p)
 -\mathcal B_{\rm SM}^{\rm old}}.
]
This is a SAME-kernel source-response COMPARATOR, not a CL statistic. An original point with R>1 has a bigger historical inclusive NP rate shift than the Type-II 670GeV historical reference at its tanbeta. **This does not demonstrate 2026 Zee exclusion**, because the 2026 Type-II limit was obtained from its own modern mass-dependent NNLO matching and a nontrivial uncertain likelihood.

## Six charged mixing `gamma` counterfactuals

For the six E7 Pareto B4 IDs [0004143,0003582,0003854,0004380,0002315,0017640], fix the original mH1, mH2 and tanbeta, vary gamma over 21 grid nodes from 0 to pi/2 **and include the exact original gamma** (normally 22 total per benchmark, 132 rows), recompute the complete old SuperIso inclusive BR for every counterfactual. Also save EXACT gauge geometry:
- `w1=cos^2(gamma)` quark doublet H1 fraction;
- `w2=sin^2(gamma)` quark doublet H2 fraction; sum=1;
- `G_ZH1H2^2 / maximum = sin^2(2gamma)`.

The geometry measures **only the off-diagonal gauge-coupling strength**. It is not a signal cascade rate, not a physical BR, and not an acceptance. Holding masses/tanbeta fixed while changing gamma does **not** preserve the original scalar quartics, mu4, neutrino Yukawa reconstruction, optimized LFV constraints, RGE or vacuum. The counterfactual slices are **unphysical until a new consistent scalar/flavor scan finds such solutions**. These slices are an identifiability/existence diagnostic for the conflict between charged mixing and bsgamma, not "allowed points."

The six actual source gamma values must lie in the counterfactual lists and reproduce F6 exactly. All files and every JSON row explicitly preserve null allowed/excluded labels. No Type-II >670 GeV 95% CL result is applied to Zee.

## One original AF command

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
bash scripts/zee_gateF8_one_shot.sh
```

Source:
- `scripts/zee_gateF8_309_670TypeII_same_legacy_kernel_and_mixing.py`;
- `tests/test_zee_gateF8_309_670TypeII_same_legacy_kernel_and_mixing.py`;
- `scripts/zee_gateF8_one_shot.sh`;
- `.github/workflows/f8-670TypeII-same-kernel-tests.yml`.

It runs prior F6 and F7 suites plus eight F8 synthetic tests, source validates original 309 records and compiled exact binary, then computes **309 actual Type-II670 comparisons + 6*22 mixing counterfactuals**. No prior source or physics result is altered. Outputs under fresh `work/zee_F8_309_670TypeII_same_kernel_mixing_20261020_v1/`:
- `F8_309_Zee_legacy_vs_670TypeII_NOT_EXCLUSION.jsonl`
- `F8_309_legacy_typeII_670_same_kernel_DIAGNOSTIC.csv`
- `F8_six_fixed_mass_gamma_counterfactual_NOT_MODEL_POINTS.csv`
- `summary.json`, `manifest.json`.

## Scientific decision after F8

If R>1 for high-cascade original spectra at similar tanbeta, they are at least as bsgamma-sensitive in the historical inclusive kernel as the new 670GeV Type-II reference. That raises tension but does not yield a valid 2026 CL classification.

If reduced gamma can lower the legacy response while retaining a sizeable sin^2(2gamma), then seek **physically independent reoptimized B4/E3 scalar and flavor scan points** in that region, preserving E2 RGE, E3 neutrino and full LFV constraints. If no such region survives even in this counterfactual diagnostic, priority shifts toward heavier H1, more singlet-like light H1, or alternate allowed quark-flavor sectors.

**After F8 a genuine paper must still implement model-consistent 2026 full b->s gamma matching, five-state HiggsBounds, LFV including Barr-Zee/mu-e conversion, neutrino likelihood and global vacuum certificate. Nothing here declares a Zee configuration fully allowed or experimentally excluded.**
