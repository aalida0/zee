# Zee Type-II charged-cascade: B → X_s γ validation handoff (11 November 2026)

**Branch:** `research/zee-full-constraints`  
**Scope:** The specifically requested B-physics constraint (item 2), **not** LFV, Higgs or collider certification.  
**Final decision:** `B_LO_NP_PUBLISHED_EQ4_VERIFIED`, `B_NLO_FULL_VECTOR_SUPERISO_REPLAY_PASS`, `B_PHYSICAL_2026_NNLO_LIKELIHOOD_UNKNOWN`, `GLOBAL_ACCEPTANCE=null`.  
Do **not** interpret the 16 source scalar spectra as globally allowed.

## 1. Executive conclusion

We now have a **genuine, independently compiled source-pinned NLO** rate for the two-charged Zee system, in addition to the 2026 Misiak *leading-NP* analytic reference, flavio v2.7.1, and the earlier HEPfit/SuperIso validation. Both charged eigenstates enter the ordinary real BMU/NDR Wilson coefficients as `cos²(gamma) * C_i(mH1) + sin²(gamma) * C_i(mH2)`; all NP coefficients are combined before the rate's RG evolution and interference terms are computed.

The NLO SuperIso calculation includes native SM matching, top-only NP `C7^0, C8^0, C4^1, C7^1, C8^1`, the underlying Q1–Q8 evolution, and SuperIso's retained low-scale P, electromagnetic and nonperturbative/HQE pieces. It is *not* the full August 2026 NNLO physical-rate prediction. No new-physics theory covariance or meaningful 95% CL model-specific exclusion has been derived.

The official archive `superiso_v5.0.tgz` was downloaded directly from the official site, SHA-256 verified as
`7f8400e98ae80deac50af64486b980891e1630d729a0a4660ca309a4d7706b5f`,
built as a fresh static library with precisely the previously audited
`module5/patches/d9b_superiso_v5.0.patch`,
and executed via `scripts/zee_d9b_rate_probe.c`.
The historic D7/F13 reference branching fractions were **both reproduced with exactly zero residual**.

**Successful source-pinned GitHub run:** https://github.com/aalida0/zee/actions/runs/43091722057.
The Actions artifact includes full rate evidence and 67 source-probe logs. It expires according to Actions retention; download it for long-term preservation.

## 2. Published 2026 leading-NP reference

Misiak et al., arXiv:2608.29863v1, p.4 Eq.(4), with \(E_\gamma>1.6\) GeV and \(\mu_0=160\) GeV:

```text
10^4 * BR(B -> X_s gamma) = (3.54 +/- 0.14)
                              - 8.51 DeltaC7(160 GeV)
                              - 2.16 DeltaC8(160 GeV).
Experiment: BR(B -> X_s gamma) = (3.49 +/- 0.19) x 10^-4.
```

This is explicitly linear in the leading NP coefficients: it does not include
quadratic terms, NP NLO/NNLO matching, or a Zee-specific theory covariance.

A simple independent-Gaussian two-sided 95% diagnostic would have an upper
rate `3.952568109917516e-4`; this is **not the published 2026 exclusion likelihood**.
The one-state Type-II published full-order lower mass bound `m_H+ > 670 GeV`
cannot be applied to either Zee charged mass separately.

## 3. Replayed 16-scalar full-vector NLO SuperIso results

All numbers below are *in units of 10^-4*. Original source scalar spectra
satisfy their historical D10 tree-level sufficient vacuum witness but NOT
necessarily physical B/Higgs/LFV experimental acceptance.

| scalar ID | Published 2026 Eq4 LO-NP rate ×10⁴ | Fresh SuperIso full-vector NLO rate ×10⁴ | Same-SuperIso NLO NP shift ×10⁴ |
|---:|---:|---:|---:|
| 2264 | 3.920603 | 3.858470 | 0.315746 |
| 2616 | 3.816926 | 3.763893 | 0.221169 |
| 3693 | 3.886865 | 3.826450 | 0.283726 |
| 4611 | 3.841445 | 3.785106 | 0.242383 |
| 8294 | 3.857240 | 3.799881 | 0.257157 |
| 8850 | 3.871762 | 3.813841 | 0.271117 |
| 9454 | 3.917701 | 3.853482 | 0.310759 |
| 11016 | 3.750460 | 3.705768 | 0.163044 |
| 13345 | 3.882882 | 3.822424 | 0.279700 |
| 14074 | 3.738752 | 3.696142 | 0.153419 |
| 14187 | 3.849442 | 3.792704 | 0.249981 |
| 14555 | 3.887817 | 3.825454 | 0.282731 |
| 14984 | 3.830219 | 3.775810 | 0.233087 |
| **15591** | **3.882671** | **3.823575** | **0.280852** |
| **15673** | **3.785804** | **3.736800** | **0.194076** |
| 16385 | 3.848643 | 3.791690 | 0.248966 |

**Verified:** the source-pinned SuperIso SM rate was
`3.5427236527176535e-4` in **that implementation**. It is numerically close
to the August 2026 SM value but has a **different scheme/order**; do not subtract
one SM baseline from the other to claim a matched physical rate.

The NLO NP effect relative to the published leading-NP shift is 0.820
for 15591, 0.790 for 15673, and 0.830 for 2264 (different backend
prescriptions, so **not a perturbative-error estimate**).

The separately switched-off NLO `C4^(1)` effects in the SuperIso rate:
- 15591: **5.0242333541066116e-8**,
- 15673: **2.984364835188465e-8**,
- 2264: **7.109910994310522e-8**.

## 4. Built-in falsification and scale diagnostics

Historical pinned rate controls reproduced *exactly*:
- `D7_NO_neutral_near_heavy_07`: expected/replayed
  `0.00042262508129385407`; residual 0;
- `F13_heavy_0001330`: expected/replayed
  `0.0003886651979064471`; residual 0.

Both \(\gamma\to0\) pure-m1 limits reproduce the source's native one-state
Type-II rate for 15591, 15673 and 2264. \(\gamma\to\pi/2\) separately
reproduces the pure-m2 injected limit. Equal- and exchanged-state endpoint
identities already passed in the source D9B audit.

Matched-\(\mu_0\) scale variations \(\mu_0=120,160,200\) GeV (all with a
newly recomputed running top and matching) give these *same-SuperIso* NP shifts:

| ID | NP shift at 120 GeV | NP shift at 160 GeV | NP shift at 200 GeV |
|---:|---:|---:|---:|
| 15591 | 2.752020e-5 | 2.808518e-5 | 2.842438e-5 |
| 15673 | 1.895837e-5 | 1.940761e-5 | 1.967944e-5 |
| 2264 | 3.096557e-5 | 3.157462e-5 | 3.193837e-5 |

This is a useful local scale-dependence diagnostic (roughly −2% / +1–1.4%
on the NP shift); it is **not a complete uncertainty**, because missing
hard higher-order matching, matrix elements, theory systematics, operator
schemes and correlations must be considered.

### Independent uncertainty / quadratic diagnostics

[GitHub run 43089287057](https://github.com/aalida0/zee/actions/runs/43089287057)
decomposed the flavio 2.7.1 *historical-scheme* rate into odd (linear)
and even (quadratic) shifts by evaluating `±DeltaC` and `±2DeltaC`.
The **positive quadratic** components were:
`1.0999309591e-6` (15591),
`5.6562979198e-7` (15673),
`1.3571821916e-6` (2264).
The 2026 LO-NP Gaussian positive-shift *headrooms* were, respectively:
`6.9896943277e-6`, `1.6676452978e-5`, `3.1964838884e-6`.
These are sufficient margins only under the declared Gaussian *diagnostic*;
the old-backend quadratic values are neither a rigorous bound nor certified
2026 NNLO NP additions.

[GitHub run 43090182524](https://github.com/aalida0/zee/actions/runs/43090182524)
tested inserting the independently validated BMU `C7^(1),C8^(1)` matching
into Eq4 **solely as a materiality diagnostic**. In the one-state Type-II
\(\tan\beta=50\) test, the bare Eq4 approximate two-sided 95% root is
about **785 GeV** and the dipole-NLO-only root about **681 GeV**, while the
published full calculation gives **670 GeV**. This explains why one can
find apparently close rates without having the actual full 2026 likelihood.
The agreement near a single reference mass does not calibrate the missing
Zee NP uncertainty.

## 5. Physics conclusion and EXACT remaining work to close item 2

**Complete and executed now:**
1. Real top-only LO ordinary BMU source/operator matching, two-state
   weights, external convention.
2. Full real top-only NLO C4/C7/C8 matching with existing D9B source validation.
3. Full-vector coherent NLO b→sγ rate *in the pinned SuperIso 5.0 scheme* for
   **all 16 original scalar spectra**, with 67 source-probe jobs/logs.
4. Direct published 2026 Eq4 LO-NP comparison.
5. Independent flavio 2.7.1 Wilson response, quadratic decomposition, and
   three matching-scale diagnostics.
6. Independent one-state controls and exact historical rate replay.

**Not scientifically finished:**
1. A rate consistently matched to the complete **August 2026 NNLO SM+NP**
   framework, including model-specific C4 and additional relevant BSM terms.
2. A meaningful **model-specific NP theory uncertainty/covariance**, and
   a reproducible confidence procedure that reproduces the original Type-II
   670 GeV benchmark before applying it to mixed Zee states.
3. Numerical check against public experimental and theory nuisance inputs in
   the same scheme. A rate from a different scheme may not be assigned the
   2026 published uncertainty just because its SM central values coincide.

**Do NOT call 15591, 15673 or any of the 16 scalar cards physically allowed
at 95% CL yet.** Best candidate prioritization remains 15673 (strongest
leading-NP B margin) then 15591 (highest historical 13 TeV cascade rate).
2264 remains a numerical control, given its method-sensitive Eq4 crosscheck.

**Final B gate:** `B_RETAINED_NLO_FULL_VECTOR_VALIDATED` /
`B_PHYSICAL_2026_NNLO_WITH_CALIBRATED_NP_SIGMA_BLOCKED`.

## 6. Reproducibility

From the repository root, the source-pinned entry point and complete build
contract are committed at:
- `.github/workflows/zee-B-superiso-full-vector-16.yml`
- `research/full_constraints/bsgamma_superiso_2026/full_vector_nlo_16.py`
- `module5/patches/d9b_superiso_v5.0.patch`
- `scripts/zee_d9b_rate_probe.c`

The successful Actions job, including the source logs:
https://github.com/aalida0/zee/actions/runs/43091722057

The original validated 2026 Wilson and cross-backend probes:
https://github.com/aalida0/zee/actions/runs/43085380420
https://github.com/aalida0/zee/actions/runs/43089287057
https://github.com/aalida0/zee/actions/runs/43090182524

All code and reproducibility text are stored on `research/zee-full-constraints`.
Existing Modules0–14 and `main` have not been modified for the B restoration.
