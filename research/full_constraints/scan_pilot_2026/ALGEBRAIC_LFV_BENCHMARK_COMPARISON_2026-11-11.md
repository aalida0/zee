# Zee Type-II charged-scalar cascade: LFV-conditioned scalar shortlist (11 November 2026)

**Completed bounded research study; report scope is explicitly partial phenomenology.**
**Repository branch:** `research/zee-full-constraints`. **No change to `main`.**
No globally allowed benchmark is claimed. No large scalar scan, 14 TeV
simulation or detector-level analysis was performed.

## 1. Reason for changing the flavor-search method

The original 2264 eight-dimensional least-squares study found a source-replayed
partial radiative LFV rate of `4.74683298035e-23`, with neutrino closure
`7.35964e-16` and a D4 cascade product `0.36763323`.
A direct signed Module4 ledger audit
[CI 43075575160](https://github.com/aalida0/zee/actions/runs/43075575160)
showed the complete included one-loop-only rate
`1.553523081314e-23` and a modest sum-of-group-norms / total-coefficient
ratio `3.2774`, not huge cancellations between individually over-limit terms.
The sufficient missing-complex-amplitude norm budget is
`1.367761492272e-12 GeV^-2`, **not a proven bound on missing diagrams**.

The two fresh family scans using the original bounded eight-real-variable
optimizer initially found 2/4 and 1/4 partial sublimit cases for scalar IDs
15591 and 15673, respectively.
[CI 43076918902](https://github.com/aalida0/zee/actions/runs/43076918902).
**These are NOT physical failures:** every unsuccessful optimizer converged
to the artificial coordinate box `|Re/Im(c_k)|<=5e-5`.
The original D14 generator permits significantly larger homogeneous coefficients.
This test showed inadequate optimizer reach, not absence of permitted neutrino
textures. The complete 8-case optimizer JSON SHA256 is
`f3e824c8da966639aa41865226f67802a124e9aa7ca6f674487b5dcb369c74e8`.

## 2. New preferred physics-directed analytic method

The native complete neutrino inverse has four complex homogeneous degrees:
```
D(c) = D0 + sum_{k=1}^4 c_k H_k.
```
For each fixed scalar, neutrino ordering and newly generated neutrino target,
construct a two-by-four complex matrix
`A = [H_k(e,mu), H_k(mu,e)]` and a two-vector
`b = -[D0(e,mu), D0(mu,e)]`. Solve
```
c_min = A^+ b
```
with a complex Moore–Penrose pseudoinverse.
Both e–μ direct neutral Yukawas then vanish within floating precision.
The source solver verifies `rank_C(A)=2`, leaving two complex linear null
directions. This **does not** remove `F†F`, charged-loop `DD†`, all neutral
loop amplitudes, LFV tau channels, non-tree mu->3e, or conversion terms.
Every original Module2 neutrino target is checked again, followed by actual
Module4 coherent retained LFV, D4 complete on-shell tree two-body branching
fractions and native leading one-loop h125 photons.

This is a **benchmark construction**, not a volume-weighted scan, global
flavor symmetry, or a novel model-independent theorem; the approximate
texture idea has precedent in Zee phenomenology.

### Exact bounded execution

- Only two source-certified historical scalar cards: `15591`, `15673`;
  both original D10 sufficient tree vacuum PASS and approximate nominal B
  compatible. **Not** yet full physics allowed.
- New seeds `20261111`, `20261112`; neutrino orderings NO and IO,
  family index 1; **8 deliberately constructed scenarios**.
- Native source runtime Python 3.10.12, numpy 2.2.6, scipy 1.15.3,
  sympy 1.14, mpmath 1.3, one BLAS/OpenMP thread.
- [Algebraic solution CI 43077967102](https://github.com/aalida0/zee/actions/runs/43077967102):
  two regression tests and all eight source evaluations **PASS**.
- Complete machine-readable scenario JSON archived in its Actions artifact:
  `zee-eight-complex-algebraic-textures-lfv-partial-not-global`;
  **unzipped JSON SHA256**
  `8ad955c9ff34b12d3bedc7c6d0fb072ce20ef8d70de9a2a1951172038dc9c27b`.

| Scalar | Ordering | New seed | Retained BR(mu→eγ) |
|---|---|---:|---:|
| 15591 | NO | 20261111 | 6.322175256e-17 |
| 15591 | NO | 20261112 | 3.230323751e-19 |
| 15591 | IO | 20261111 | 1.569562174e-15 |
| 15591 | IO | 20261112 | 3.153811957e-20 |
| 15673 | NO | 20261111 | 1.971527237e-19 |
| 15673 | NO | 20261112 | 3.062539349e-21 |
| 15673 | IO | 20261111 | 1.614218508e-21 |
| 15673 | IO | 20261112 | 9.391098754e-21 |

**8/8** are perturbative, with maximum Yukawa modulus <0.011, satisfy exact
inverse closure and fall below the repository's **retained**
MEG II 90% CL snapshot `1.5e-13` (arXiv:2504.15711).
Direct e–μ neutral Yukawas are reduced to ~1e-18–1e-21 in the constructed
families. A total physical `mu→eγ` **PASS is not established**.

Across these eight scenarios:
- Largest retained `BR(tau→mu gamma)` for 15591: `5.752863262e-10`;
  for 15673: `1.145442206e-11`.
- Largest retained `BR(tau→e gamma)` for 15591: `1.145108055e-12`;
  for 15673: `1.150078903e-15`.
- Neutral scalar tree-only `mu→3e` is extremely suppressed
  (`O(1e-48)` or below in the worst of eight).
  **The complete mu→3e and mu–e conversion observables remain unassessed.**

## 3. Local stability of the constructed flavor textures

The exact reconstructed `D_{e mu}=D_{mu e}=0` solutions for
`15591, NO, seed 20261111` and `15673, IO, seed 20261111`
were independently perturbed in all eight real homogeneous directions,
using 16 signed coordinate axes plus 24 deterministic normalized random
directions, **40 trials per radius per scalar**.

[Stability CI 43078594922](https://github.com/aalida0/zee/actions/runs/43078594922):
all tests PASS. Rates were actually reevaluated with Module2 + Module4.

| Absolute Euclidean 8-real coefficient displacement | 15591 NO partial sublimit | 15673 IO partial sublimit |
|---|---:|---:|
| 1e-7 | 40/40 | 40/40 |
| 1e-6 | 40/40 | 40/40 |
| 1e-5 | 5/40 | 11/40 |
| 1e-4 | 0/40 | 0/40 |

At radius 1e-6, the largest retained BRs were 1.323606e-14 and
4.527459e-15, both below the reference bound.
At radius 1e-5 the largest became 1.263406e-12 and 4.541663e-13.
**These are finite, intentionally chosen directional tests, not posterior
allowed fractions or a rigorous all-direction bound.**
The weak-scale direct-zero texture may require flavor-symmetry or RG
stability justification for an extrapolation to high scales.

## 4. Three original vacuum-certified/nominal-B-compatible production cards

13 TeV original generator cross sections are genuine LO
`pp→tbH2±` 5FS gb-associated (both charges, both incoming beam orders),
NNPDF30_lo_as_0130 member 0, fixed μR=μF=mH2.
They are **not** NLO, 14 TeV or detector-level rates.
Only the scalar quark-hard-process independence from changed lepton
homogeneous coefficients is assumed; the new full-flavor cards have not
received a new original-card complete-UFO production artifact.

| ID | mH1± [GeV] | mH2± [GeV] | Nominal B pull | Approx. B margin to 1.96 [BR] | Tree cascade product, newly optimized/algebraic | 13 TeV LO sigma times cascade [fb] |
|---|---:|---:|---:|---:|---:|---:|
| 15591 | 442.6 | 1035.7 | 1.6638 | ~6.99e-6 | 0.32513–0.32536 | 3.859–3.861 |
| 2264 | 674.3 | 1166.0 | 1.8245 | 3.1965e-6 | 0.367633 | 1.83868 |
| 15673 | 714.5 | 1277.4 | 1.2534 | ~1.67e-5 | 0.39283–0.39284 | 1.17361–1.17364 |

The original matching-only B reference is a **linearized** top-only
diagnostic, with independent quoted SM/exp Gaussian errors and no NP
theory uncertainty. Being nominally inside 1.96 is NOT an experimentally
validated B→Xsγ exclusion pass. ID 2264 is especially near the boundary;
ID 15673 has the largest nominal reference margin of these three.

At 3000 fb^-1, the 13 TeV **pre-detector** proxy event counts for the
source-qualified production assumption are ~11,580 (15591), 5,516 (2264),
and 3,520 (15673). These are **not** 14 TeV HL-LHC sensitivities.

## 5. Native h125 photon channels

Reused the already validated native tree-convention
h→γγ and h→Zγ one-loop kernels, full physical charged-scalar current
including the off-diagonal Z charge and two charged eigenstates, and
the actual lepton Yukawas of each new family.
No Higgs total width or HiggsTools exclusion was obtained.

| ID | Γ(h125→γγ)/ΓSM | Γ(h125→Zγ)/ΓSM |
|---|---:|---:|
| 15591, algebraic families | 0.972462–0.972476 | 0.9865905–0.9865907 |
| 2264, 8D reference | 1.003905 | 0.990813 |
| 15673, algebraic families | 1.0078065–1.0078076 | 0.99338050 |

ID 2264 native h/B source rerun PASS:
[CI 43076238654](https://github.com/aalida0/zee/actions/runs/43076238654).
Its `kappa_V=0.999862856`, `kappa_u=0.984143985`,
`kappa_d=1.017311268`; h125 is near alignment in the native
`kappa_V=cos(alpha-beta)` convention. All three scalar spectra have
`kappa_V` near 1, but this does not certify HiggsSignals χ², complete
width, heavy-neutral tau searches or acceptance.

## 6. Physics claims and what remains decisive

**Established**:
- fixed scalar D10 tree-vacuum sufficient certification on these original
  scalar points;
- actual full native neutrino inverse and algebraic closure;
- actual retained coherent radiative Module4, with all original one-loop
  and matched photon-Barr–Zee terms plus explicit missing-term ledger;
- actual new-family D4 complete on-shell tree two-body cascades;
- native leading h125 photon widths and original scalar-level 13 TeV LO
  production conditional proxies;
- source-matched directional local perturbation sensitivity.

**Not established**:
- full physical mu→eγ including uncomputed genuine Zee mixed
  electroweak two-loop terms (scoped approximation may omit higher-order
  gauge dressing, but this needs declared accuracy and exceptional leading
  structures screened);
- **leading** complete mu→3e signed non-tree operator vector and
  Type-II mu–e conversion matched to hadronic/nuclear matrix elements;
- full B→Xsγ NP rate/uncertainty, common scheme, likelihood;
- h125 total width, heavy neutral widths/production and applicable
  HiggsTools observed exclusions;
- 14 TeV production theory or any detector/recast selection efficiency;
- confidence-level scan acceptance or collider exclusion/discovery.

**A scientifically defensible paper path** is to publish a careful
`Type-II Zee charged cascade with neutrino-mass-consistent LFV-conditioned
textures and conditional 13 TeV parton-level production`, only after an
independently acceptable B and Higgs treatment at the declared accuracy,
plus clearly scoped LFV constraints. Explicitly document the published
2021 cascade precedent (arXiv:2106.08332) and the 2017 full Zee model
scan (arXiv:1701.05345): algebraic texture zeros or the cascade alone
are NOT novelty. A genuine novelty would be the correlated
Type-II flavor-neutrino/cascade/Higgs parameter-space *prediction*
and quantitative, appropriately qualified reach across validated spectra.

### Top three follow-up calculations

1. **B flavor**: physical B→Xsγ NP rate and uncertainty validation on
   15591 and 15673, with proper 2026 scheme and error prescription.
   These are more viable priorities than near-boundary 2264.
2. **Higgs**: complete relevant h125/heavy-neutral widths, experimental
   HiggsTools observed search inputs and a statistically meaningful
   comparator (or a precise, transparently limited approximation).
3. **LFV beyond the on-shell dipole**: leading one-loop mu→3e
   off-shell-photon, penguin/box and coherent interference, plus Type-II
   conversion Wilsons. Do not make a fully constrained scan without
   these, unless the paper explicitly limits itself and avoids
   unqualified full-acceptance language.

**FINAL SCIENCE GATES:**
`EIGHT_ALGEBRAIC_FLAVOR_TEXTURES_NUMERICAL_PASS`;
`LOCAL_RETAINED_LFV_STABILITY_MEASURED`;
`SCALAR_VACUUM_D10_PASS`;
`B_FULL_RATE_UNKNOWN`;
`HIGGS_FULL_UNKNOWN`;
`LFV_PHYSICAL_UNKNOWN`;
`GLOBAL_ACCEPTANCE=null`.

## Source locations

- `research/full_constraints/scan_pilot_2026/analytic_direct_lfv_textures.py`
- `research/full_constraints/scan_pilot_2026/analytic_texture_local_stability.py`
- `research/full_constraints/scan_pilot_2026/two_scalar_flavor_benchmark.py`
- `research/full_constraints/scan_pilot_2026/lfv_coherent_ledger_budget.py`
- `research/full_constraints/scan_pilot_2026/h125_b_shortlist_2264.py`
- `research/full_constraints/scan_pilot_2026/2264_fresh_8d_reference.json`

Existing frozen core Module2/3/4, D4, scanner/collector, original D14
20k source manifests and `main` were not modified.
