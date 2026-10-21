# F11: Six real Zee cascade benchmarks into flavio inclusive B -> X_s gamma

**Status as of 2026-10-21**: Implemented, unit-tested and genuine flavio SM/dipole-response validated in GitHub Actions. The **actual six AF historical F10 points still require the F11 numerical AF run**. This workflow is an honest older published-era inclusive-rate / **LO new-physics C7,C8** prediction; NOT a full 2026 NNLO Zee-model experimental exclusion.

## One AF command

```bash
cd /home/aalida/zee && git switch feature/global-scan-priority1 && git pull --ff-only && bash scripts/zee_paper1_F11_real_flavio_one_shot.sh
```

The launcher creates or reuses `.venv_paper1_F11_flavio` inside /home/aalida/zee, installs pinned `flavio==2.7.1`, `wilson==2.5.2` and `particle==0.26.2`, runs source-contract unit tests, checks that the 2022 PDG data file exists, then runs all six original source-specific models and all 18 independent Type-II controls. **Do not upgrade the `particle` dependency to 1.0.x**: it removes `particle2022.csv`, which flavio 2.7.1 currently reads at import. Original F10 output directory: `work/zee_paper1_F10_legacy_six_20261021T113910Z`. Original P1 seed scan: `work/zee_paper1_florentino_pilot_20261021T111413Z`.

Output directory: `work/zee_paper1_F11_real_flavio_six_<UTC timestamp>/`.
Files: F11 six rows CSV, `summary.json`, `manifest.json`, the compiled source-pinned `f11_same_source_E4A_matching`. Input F10 and original P1 files are immutable. New outputs always have source SHA256 and are never merged with previous models without checking provenance.

## Observable and matching

The original static isolated SuperIso v5 library used by F6 and F10 is SHA256-verified and relinked with the unmodified `zee_gateE4a_full_order_matching_probe.c`, with `mu0=160 GeV`.

The probe emits operator C1-C8 across matching orders 0/1/2 for SM, pure-light, pure-heavy, and mixture. Each physical scalar choice uses Type-II-like quark charged couplings and the mixing convention

```text
dC_i^Zee(mu0) = cos^2(gamma) * dC_i^TypeII(mH1,mu0)
             + sin^2(gamma) * dC_i^TypeII(mH2,mu0).
```

For the rate, **ONLY LO C7 and C8** NP coefficients are injected into `flavio.WilsonCoefficients.set_initial` with `eft=WET`, `basis=flavio`, `scale=160 GeV`. The real `flavio` package computes `np_prediction("BR(B->Xsgamma)",wc)`, which includes its existing published-era SM normalization, interference and quadratic response. It does **not** transfer incompatible NNLO raw four-quark SuperIso coefficients between differing operator schemes. Crucially,

```text
BR(SM + cos²(gamma)*NP_H1 + sin²(gamma)*NP_H2)
  != cos²(gamma)*BR(SM + NP_H1) + sin²(gamma)*BR(SM + NP_H2)
```

in general, owing to the quadratic terms. F11 combines **Wilson coefficients first**.

For each of the six models F11 also performs an independent **same-tanbeta 670-GeV pure Type-II** matching calculation with precisely the same real `flavio` response, and reports

```text
R_flavio_670 = [BR_flavio(Zee) - BR_flavio(SM)] /
               [BR_flavio(TypeII,670, same tanbeta) - BR_flavio(SM)] .
```

This provides a second cross-kernel flavor-tension *diagnostic* to compare with F10 historical SuperIso ratios, but neither is a validated 2026 95%-CL threshold.

The included signal proxy is still NOT `sigma(pp->tbH2)*BR(H2->H1 Z)*BR(H1->tb)` in pb, and six points have no full Zee allowed/excluded status.

## Real GitHub Actions validation

- GitHub CI source interface: `tests/test_zee_paper1_F11_six_real_flavio_LO_NP_rate.py` passed 5/5, plus earlier F10 4/4 and Paper1 scan 7/7.
- `flavio==2.7.1` with `particle==0.26.2` and `wilson==2.5.2` imported and executed actual model-independent SM and Wilson perturbation controls:
  - `BR_SM^flavio = 3.3096922701754877e-4` (flavio-default parameters);
  - `dBR/dC7 = -9.264100563596606e-4` at `mu0=160 GeV`;
  - `dBR/dC8 = -2.1690712123542634e-4`.
- Derivative deviations relative to Misiak et al. 2015 Eq.(10): 12.7%, 9.0%, inside predeclared **25% provisional basis comparison envelope** from the earlier F1 source. This is *not* a precision 2026 matching proof.
- The CI did not have access to the user's AF-only pinned SuperIso library or actual six F10 files; it did **not** compute the six actual physical matching coefficients or their rates.
- The local test simulates six operator vectors only to catch algebraic failures; never call mock numeric rates real Zee predictions.

## Core physical limitation

Misiak et al., arXiv:2608.29863 (30 August 2026) give the modern 2026 result `BR_SM = (3.54 +- 0.14) * 10^-4`, experiment `(3.49 +- 0.19) * 10^-4`, and a 95% CL **single-charged Type-II** mass reference of 670 GeV. The complete 2026 scheme-dependent NNLO matrix-element kernel and correlated nuisance likelihood cannot be reconstructed by adding the F11 LO NP shift to the 2026 SM central value, applying the 670 GeV limit to one Zee scalar, or treating the F10 ratio to Type-II-670 as a confidence level.

**Until genuine modern 2026 NNLO-compatible two-scalar matching/rate/nuisance source and independent TypeII limit calibration are available, F11 explicitly outputs `modern_NNLO_Zee_2026_95CL: null`, `fully_Zee_allowed_or_excluded: null`, `paper1_GO_or_NOGO: null`.**

It also omits complete general Zee leptonic LFV, dynamic quark alignment/FCNC fit, complete HiggsTools and scalar vacuum certifications, and hadronic production. None can be inferred from an F11 b -> s gamma partial rate.
