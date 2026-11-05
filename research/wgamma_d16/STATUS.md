# D16 status: BLOCKED_GAUGE_MATCHING

The continuation now computes actual signed, dimensionally regulated inner
W/Goldstone/ghost/mixed integrals. Physical `C_L,C_R` remain **null** and
`coherent_inclusion=false`. Complete two-loop gauge matching is unfinished.
All changes remain under `research/wgamma_d16/`; Modules0–14, the Zee
Lagrangian and validated D15 code are unchanged.

The latest continuation resolves the HW source/paper normalization discrepancy
in a source-preserving research adapter and validates generic complex strict
2HDM coefficient closure at nonzero Z3,Z7, for both chiralities and all three
channels. The original source retains an explicit expected-failure regression.
See [HW_NORMALIZATION_AUDIT.md](HW_NORMALIZATION_AUDIT.md) and
[GENERIC_2HDM_CLOSURE.md](GENERIC_2HDM_CLOSURE.md). The smallest nonzero
Zee-specific class, the unmixed charged-singlet scalar–Z–photon set, is now
separately calculated with triangles, contact and outer attachments accounted
for. Its restricted result and prioritized mixed extensions are documented in
[ZEE_EXTENSION_INVENTORY.md](ZEE_EXTENSION_INVENTORY.md). None supplies a full
Zee W coefficient or changes the physical matching gates below. Later sections
retain the chronological earlier partial milestones.

| Milestone | State | New evidence |
|---|---|---|
| INNER_XI1 | PASS_INNER_SCOPE | All 26 native inner integrals, UV poles and finite five-tensor coefficients; independent A/P/B/C extraction agrees with Abe |
| LONGITUDINAL_ST | PARTIAL | All inner Rxi terms integrated at xi=.5,1,3; symbolic cancellation of every inner UV pole at arbitrary xi; contracted native vertex/inverse-propagator identities; full BRST insertion functional still missing |
| PARENT_COMPLETION | PARTIAL_SUBLOOPS | Eight W/G parent subloops for one scalar placement at xi=1, independently derived/evaluated WWW neutrino pinch, general-xi finite WWW subloop at two witnesses; outer/crossed/charged/LSZ sum missing |
| PHYSICAL_GAUGE_INDEPENDENCE | NOT_EVALUATED | No independently calculated full projected CL,CR or compensator identity |

The immediate requested experimental milestone has been achieved for the
**inner** amplitude. `native_integrands.py` constructs signed vertex products
without importing a source tensor or a literature kernel. `tensor_reduction.py`
retains `d=4-2eps`, including finite rational pieces, before parameter quadrature.
The exact arbitrary-xi UV sum is zero in all five tensor coefficients.
`gauge_ledger.json` records 12 scalar/xi inner evaluations across both original
complex LFV examples, plus two independent parent witnesses and numerical
uncertainties. Full parent matrices are reproducibly generated in ignored
`local/regulated-details.json`; the ledger retains their hashes, representative
components and complex chiral spin amplitudes.

`parent_integrals.py` now gives an actual nonzero missing topology, rather
than just a required compensator. The full WWW fixed-r box is calculated;
`N_mu=2 n² gamma_mu PL+N_mu_rem` follows directly from its numerator. Cancelling
the neutrino propagator and separately integrating the resulting triangle
agrees with the box reduction at about 1.6e-18 at the first witness. All eight
W/G species assignments of this parent placement are also integrated at xi=1.
A separate finite Rxi contour integral gives the WWW subloop at xi=.5,1,3;
its replicate uncertainty is recorded and is not precision gauge validation.

Eight **new** s-G-H source queries (16 coefficient checks at two spectra)
confirm the nonzero charged-parent mass-difference identity, worst residual
2.28e-13 GeV. The old 58-vertex inventory, 26-graph count and completed B/C
reductions were not repeated. New generated gauge-fixing/gauge-transformation
sources are retained in `st_sources.json`; no model was regenerated.

## Exact remaining calculation

The first missing full topology is the **outer r integration** of
`parent_integrals.exact_parent_integrand()`. It contains all three W/G
propagators, the massless neutrino, the unpinched charged-lepton propagator,
neutral-scalar propagator and independent complex L/R vertex. Its fixed-r
subloop is no longer unknown. What remains unimplemented is the d-dimensional
outer dipole projection with the opposite scalar placement, physical H1/H2
parents and the BRST/LSZ subtraction. Finite inner subloops alone do not supply
O(eps) pieces needed if outer local UV poles survive.

The native triple-vertex contraction explicitly leaves `-b_mu b_beta/xi`
after the inverse-W, inverse-photon and mixed mass terms. This ghost/gauge-fixing
insertion kernel has not been completed into the full projected parent sum.
External/reducible photon attachments and their counterterm/LSZ contributions
remain unevaluated, with no presumed zeros. There is no unavailable external
service blocking this calculation; it is unfinished two-loop analytic work.

Therefore the independently computed identity

```
Delta_xi C_remaining = -Delta_xi C_G
```

has **not** been established for either chirality. No missing term was
constructed by negating the diagnostic Goldstone variation. The historical
Goldstone-only falsifier remains a diagnostic, and no physical W coefficient
or D14 integration has been released. The independent xi=1 inner agreement
with Abe does not arbitrate full CHK/Ilisie/Abe physical kernel differences.

## Reproduction

```
python3 -m research.wgamma_d16.tensor_reduction
python3 -m research.wgamma_d16.parent_integrals --require-completion
python3 -m unittest research.wgamma_d16.test_regulated research.wgamma_d16.test_d16 -v
python3 -m research.wgamma_d16.regulated_pilot --require-completion
```

The parent command calculates the first nonzero parent subloop and its pinch,
then exits **2** for incomplete physical matching. The pilot writes actual
signed integrals/evidence before exiting **2** for the same reason. Omit the
flag to exit zero after producing the partial research result. The historical
`matching --example 1 --require-pass` interface also correctly remains exit 2.

There are eight new integral/ST tests; the ten existing scoped D16 tests are
retained. No repository-wide test suite, D15 regeneration, Condor job, scan,
physics-source change or expensive build is needed. The detailed derivation,
exact integrands, signs, pole table and source comparison are in
[D16_GAUGE_DERIVATION.md](D16_GAUGE_DERIVATION.md). Historical `evidence.json`
and `DERIVATION.md` preserve the earlier investigation; `gauge_ledger.json`
is the new regulated-amplitude evidence.


## Published 2HDM reuse priority (2026-11-05)

The external reference now supersedes further independent outer integration
as the next D16 priority. See [EXTERNAL_2HDM_BASELINE.md](EXTERNAL_2HDM_BASELINE.md).
Corrected author-code reproduction passes. Two reconstructed Z3=Z7=0 potentials
with independent complex LFV matrices agree in the full strict-2HDM sum for
all three channels. Generic potentials retain a reproducible HW source/paper
failure: the source contains an extra inverse MW squared. The other 12 terms
agree. 128 archived-native coefficient substitutions pass. The new
[Zee extension inventory](ZEE_EXTENSION_INVENTORY.md) preserves all previous
inner/parent evidence and defines the missing mixed charged-sector completion.
Physical Zee W coefficients remain null; coherent_inclusion remains false.
