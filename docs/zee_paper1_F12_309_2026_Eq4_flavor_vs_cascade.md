# F12: 309 original scalar-screened Zee points and modern 2026 LO flavor–cascade diagnostics

**Date:** 21 October 2026. This is a **published-source LO 2026 linearized `B→X_sγ` screen** for the original 309 archived scalar points, not modern full NNLO Zee exclusion.

## One AF command

```bash
cd /home/aalida/zee && git switch feature/global-scan-priority1 && git pull --ff-only && bash scripts/zee_paper1_F12_309_2026_Eq4_one_shot.sh
```

The script automatically discovers the original SHA-validated F6 309-point archive and its pinned SuperIso v5 `src/libsuperiso.a`, re-links the already audited independent A1S `gateA1s_probe_modern_2026_lo.c`, and evaluates the actual LO new-physics C7,C8 matching at 160 GeV separately for charged masses `mH1`, `mH2`, and for the 670 GeV Type-II reference at the **same tanbeta**. The result uses *one coherent mixed Wilson coefficient before the rate*,

```text
delta_C7,Zee = cos^2(gamma)*delta_C7(mH1) + sin^2(gamma)*delta_C7(mH2)
delta_C8,Zee = cos^2(gamma)*delta_C8(mH1) + sin^2(gamma)*delta_C8(mH2)
10^4 BR(Egamma>1.6 GeV) = 3.54 -8.51*delta_C7,Zee -2.16*delta_C8,Zee .
```

This is Eq.(4) of Misiak et al. arXiv:2608.29863 (2026) which neglects **quadratic NP terms**, all higher-order BSM matching and full model-dependent uncertainties. The scalar inputs come from the immutable F6 original 309 cohort, including its `E7_included_cascade_proxy_NOT_physical_rate`. The F12 output does **not** claim neutrino fit or LFV compatibility for these 309 points.

Output folder: `work/zee_paper1_F12_309_2026_Eq4_frontier_<UTC timestamp>/`. Outputs:

- `F12_309_2026_Eq4_LO_Bsgamma_vs_included_cascade_NOT_EXCLUSION.csv`: every original physical scalar-screened source row; Wilson inputs, published 2026 linearized BR, older F6 BR, Type-II comparator, illustrative `z` value and included-channel cascade proxy.
- `F12_non_dominated_2026_Eq4_LO_CASCADE_PROXY_NOT_ALLOWED.csv`: non-dominated trade-off cases in increasing cascade proxy/decreasing linearized flavor tension. This is **not an experimental allowed frontier**.
- `summary.json`, `manifest.json`, source-probe binary and source SHA256, with the numbers of candidate rows below and above **illustrative** `|z|=1.96` and `|z|=3`.

The Gaussian **diagnostic only** uses

```text
z_screen = [BR_Eq4 - BR_exp] /
           sqrt(sigma_SM2026^2 + sigma_exp2026^2)
sigma_SM2026 = 0.14*1e-4, sigma_exp2026 = 0.19*1e-4
```

It omits the new-physics-dependent theory covariance and discarded quadratic/higher-order amplitudes. **Do not call `|z|>1.96` “excluded at 95% CL”, or a point with `|z|<1.96` “allowed”.** The mass 670 GeV is a **single-state Type-II reference**, not a direct mass limit for either Zee charged scalar.

## Interpretation against F11

F11 independently used original SuperIso E4A and A1S probes and the `flavio` rate for six newly generated B4 points. Its genuine AF results in the user's pasted file show all six central 2026 Eq.(4) predictions `4.2034–4.3052 ×10^-4` with illustrative `z = 3.02–3.45`; relative to the SM central prediction of `3.54e-4`, the shifts are `0.6634–0.7652 ×10^-4`. These are real **linearized published-source screens**, not formal Zee exclusions. They are not guaranteed to represent the original 309 model cloud.

An all-309 screen is the economical test of whether there are **any** historical scalar spectra with both a useful (not pb) cascade proxy and a small modern linearized `B→X_sγ` shift. If such a region appears, targeted full-neutrino and LFV optimization can be justified there. If no region survives the *diagnostic* screen, investigate heavier masses, parameter correlations and unrepresented scalar regions before claiming any global no-go.

## Final physics not provided by F12

2026 full-scheme NNLO (including necessary NLO/NNLO charged-Higgs new physics and correlated uncertainty, independent Type-II benchmark reproduction), the complete modern neutrino likelihood, full Barr–Zee/rare LFV, radiatively consistent quark Yukawa alignment, full all-field vacuum and HiggsTools, complete charged decay widths, and the hadronic cross-section in pb are not solved by this script. `full_Zee_allowed_or_excluded` and `paper1_GO_or_NOGO` must remain **null**.
