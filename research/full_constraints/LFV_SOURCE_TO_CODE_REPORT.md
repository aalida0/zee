# Source-to-code execution, 7 November 2026

**LFV_ONE_LOOP_BLOCKED.** The bounded backend attempt and published-subset
fallback were executed. Complete tree-plus-one-loop mu→3e coefficients remain
UNKNOWN. No physical BR, exclusion, adapter, or global acceptance is supplied.
Frozen Modules0–13, Module14 and saved D12 cards are unchanged.

## Executed independent backend attempt

FlexibleSUSY commit `913bbbf107d2b4aa2741dfbaa87c780853e39ca4`
(5 July 2026) was downloaded and source-pinned. Its README requires FeynArts
≥3.10 and FormCalc ≥9.8 for NPointFunctions. Mathematica 15.0.1 is usable.

1. `configure --enable-feynarts --enable-formcalc` with optional library
   interfaces disabled failed at `Needs["SARAH`"]`.
2. The **one focused repair** prepended the existing `.Mathematica/Applications`
   directory to Mathematica 15's search path through a disposable math wrapper.
   Configure then detected SARAH 4.15.4, but failed at `Needs["FeynArts`"]`.

Both attempts exited 1. Logs and the wrapper are in
[lfv/source_to_code_logs](lfv/source_to_code_logs). Archived local FeynArts
3.5/3.9 and FormCalc 7.5 are older than the pinned requirements; they were not
substituted. No installation was changed. **Generation never reached the Zee
model**, so this is an exact prerequisite failure, not evidence that FlexibleSUSY
cannot support Zee. No generated diagrams, gauge/ghost/Goldstone/self-energy
coverage, or full coefficient arrays can be certified from this attempt.
No SPheno spectrum or decay executable was run.

## Published mixed charged-scalar box

[Mitsuda–Sasaki](https://arxiv.org/abs/hep-ph/0103202),
DOI 10.1016/S0370-2693(01)00842-5, Eqs.16,26,27, gives a **restricted F-only**
box with two charged scalars and massless neutrinos. We use native `F=2f`,
singlet weights `(sin²γ,cos²γ)`, and

`J(a,b)=log(a/b)/(a-b)`, `J(a,a)=1/a`, with squared masses `a,b`.
The mixed kernel is `sum_i,j w_i w_j J(M_i²,M_j²)`, including both unequal-mass
orientations. It is independently checked by radial quadrature.

The pinned generated `CalculateBox4L` block at lines 19546–19590, its **actual
native charged vertex subroutines**, and `KilianD00` were extracted and compiled
with gfortran. Other couplings are zero in this explicitly labelled analytic
F-only control; `MMD0=0` follows from its two zero neutrino masses. The full
generated box routine and general doublet Yukawa sector are **not** validated
by extracting this block. Both Hermitian-conjugate native vertices are used;
the real singlet rotation signs enter all four vertices.
The massless, fully summed internal neutrinos permit a unitary basis choice
`UV=I` in this F-only control; finite neutrino masses/mixing corrections are
not bounded by it.

On all four original central D7/F13 cards, raw ordered `B_VLL` agrees with
`F_mu,tau F_e,tau* sum_k |F_e,k|² kernel/(64π²)`. Maximum complex relative
residual across **28** card/control evaluations is **3.90e-16**.
The raw coefficients, in GeV^-2, are:

| Saved card | NO | IO |
|---|---|---|
| D7 | −1.6057243264e−21 − 2.0540401856e−21 i | −5.2159159097e−21 − 1.0341460149e−20 i |
| F13 | −3.9549225788e−22 − 5.0591311187e−22 i | −1.2846877426e−21 − 2.5471168101e−21 i |

Paper Eq.26 defines **minus** the Lagrangian with `(1−γ5)` currents. Thus its
Lagrangian PL×PL coefficient is the **negative** of the displayed raw generated
coefficient. We retain this sign distinction: no independently proven common
ordered-action map to all penguin/dipole coefficients is available here.
No incoherent Eq.28 rate is used. F→0, equal masses, both mixing endpoints,
state exchange and a complex external-flavor rephasing all pass. These limits
are analytic controls, not new physical cards or a parameter scan.

## Published Z vertex: useful calculation, incompatible comparison kinematics

[Ghosal–Koide–Fusaoka](https://arxiv.org/abs/hep-ph/0104104),
DOI 10.1103/PhysRevD.64.053012, Eqs.4.1–4.7, is an **on-shell** F-sector vertex
at `q²=mZ²`. We evaluated F, both unequal-mass orientations of H, and the real
printed G of Appendix A.3, retaining both charged states. Independent integration
of Eq.4.4, using `G=3/4+I+ξ dI/dξ` and an analytic y integral, agrees with A.3
within **5.31e-12 absolute**. Eq.A.5 independently checks H. Equal-mass H=0,
heavy-mass F/G behavior, and quadrature refinement pass.

Printed real K is **−2.5474885331e−4** (D7) and **−1.2448452864e−4** (F13).
Full precision kernels and explicitly labelled candidate complex flavor factors
are saved. The paper uses real restricted Yukawas; its absorptive completion
and the general complex ordered-action continuation are **not** validated here.
The candidate flavor factor is consequently not a physical Wilson coefficient.

The saved `CalculatePengV4L` takes no external q² argument and uses zero-invariant
`B0`, `C0check`, and `B0C0check` functions. It is a low-energy four-lepton routine,
not an on-shell Z vertex. Direct numerical equality to the published on-shell
formula would compare different kinematics. The comparator is **null**, with
this exact reason; substituting mZ²→0 into the on-shell result is not a validated
off-shell matching calculation. Full off-shell Z_L/R, monopoles, scalar penguins,
mixed D/F and gauge boxes and their relative phases remain unvalidated.

## Conversion discrepancy resolved at the nucleon-current level

Unmodified FlavorKit `MuEconversion` was compiled again for scalar-up,
vector-up, pure scalar/vector isovector, and coherent isovector EFT insertions.
Separately, the **unaltered current expressions, overlap and capture functions**
extracted from pinned FlexibleSUSY's `l_to_l_conversion.cpp.in` were compiled
with g++. This is executable nuclear matching, not generated Zee UV matching.
Au and Al currents agree with direct proton/neutron contraction to 2.23e-16.

FlavorKit defines `g1S=(g_p−g_n)/2`, but uses
`(Z+N)g0S − (Z−N)g1S = Z*g_n+N*g_p`. Its vector term retains the plus sign.
FlexibleSUSY instead contracts `g_pS*S_p+g_nS*S_n` and
`g_pV*V_p+g_nV*V_n`, consistent with
[Kitano–Koike–Okada](https://arxiv.org/abs/hep-ph/0203110) and
[Primulando et al. Eq.41](https://arxiv.org/abs/2201.01960).

For scalar-up Au, the expected/source currents are **910.3/941.5** and the
rate ratio remains **1.0697235742499855**, including original literal rounding.
This is a proton/neutron interchange, **not** an assigned nuclear uncertainty.
The six saved FlavorKit targets were replayed; vector-up assignments pass.
Pure scalar and vector isovector rates alone hide the scalar sign. A coherent
Au control with `g_pS=g_pV=1`, `g_nS=g_nV=−1` gives FlavorKit
**8.1406e−14**, versus the correct common-prefactor result **2.54597762547**:
the source almost cancels instead of adding. Arbitrary EFT insertions are not
physical Zee conversion predictions. Default-real GSp/GSn rounding explains
the small residual in this nominal cancellation.

Different nuclear approximations must not be conflated. FlexibleSUSY uses
KKO Table 2 Au overlaps `(D,Sp,Sn,Vp,Vn)=(.1670,.0523,.0610,.0859,.1080)`.
Its Au capture literal is `8.84868e−18 GeV`, whereas FlavorKit Au uses
`8.59868e−18`; the former equals FlavorKit's Pb literal. KKO Table 8 lists
Au/Pb capture rates **13.07/13.45 million s^-1**. This target-input mismatch
also prevents treating the untouched public FlexibleSUSY conversion routine
as an already validated reference total. Its source additionally assigns
`CXYs=-photon_s-npf_d` although `npf_s` is computed. We record this source
routing issue; no strange-sector model calculation or upstream patch is claimed.
Neither issue changes the demonstrated proton/neutron sign diagnosis.

## Deliverables, tests and limits

[LFV_OPERATOR_MATRIX.json](lfv/LFV_OPERATOR_MATRIX.json) distinguishes validated
subsets, published limits, unvalidated generated sectors and missing pieces.
[LFV_FIXED_CARD_RESULTS.json](lfv/LFV_FIXED_CARD_RESULTS.json) contains freshly
computed tree contact coefficients, raw F-box and printed Z kernels, complex
values, explicit nulls for the **complete** 14-component vector, hashes, stdout,
compiler versions, and independent nuclear controls.
[SOURCE_TO_CODE_SOURCES.json](lfv/SOURCE_TO_CODE_SOURCES.json) pins papers,
equations, restrictions, code and setup logs. External source bytes are not
redistributed. The prior 65-artifact manifest is checked before and after.

Reproduce after restoring source bytes at the hash-bound path hints:

```bash
python3 -m research.full_constraints.lfv.source_to_code --output /tmp/new-lfv-fixed-card-results.json
python3 -m unittest research.full_constraints.lfv.test_source_to_code -v
python3 -m unittest research.full_constraints.lfv.test_validate -v
```

The output path must not already exist. New integration tests: **4/4 PASS**;
prior research suite: **5/5 PASS**; frozen D14 LFV: **2/2 PASS**.
Frozen Modules3/4: **73/75**, with the same two historical branch-name
assertions failing on the required research branch. No assertions were edited.
Gauge-parameter cancellation, full SU(2) Ward identities and full coefficient
matching are **NOT_TESTED**, rather than inferred from these subset controls.

The source-first audit and its selected reference/citing-work checks were used;
no new literature-absence claim or broad inventory is made. Bilenky–Santamaria
Eqs.4.8–4.21 and Sec.6 remain the heavy unmixed-singlet EFT limit, and Crivellin
et al. supplies the low-energy running framework, neither completing this Zee
UV match. The stop condition is reached: one setup attempt, one repair, useful
executed published-subset and nuclear evidence. Complete one-loop LFV remains
blocked; materially interfering two-loop Wγ/charged-current/gauge contributions
remain separately unvalidated. Module4's neutral fermion/photon subset is
already included and was not added again.
