# Module4 omission sensitivity triage

**DIAGNOSTIC_ONLY.** Baseline `module3_NO_spectrum0`; frozen Module4 commit
`231e58fc35a7ea26d6f04f4735f8e9a197f1b6d3`.
This is a conditional diagnostic of the included dipoles, not a new LFV
calculation or a complete two-loop prediction. No allowance, exclusion or
global benchmark viability follows.

## Mathematics and scope

Keep the frozen operator
`L = e m_i/2 bar(l_j) sigma_munu (C_L P_L + C_R P_R) l_i F_munu + h.c.`,
with both dipoles in GeV^-2 and basis `SARAH_ZeeTypeII_Florentino_v1`.
For the signed complex vector C = sum_i C_i in C^2, define
`n = sqrt(|C_L|^2 + |C_R|^2)`, `M = max_i ||C_i||`, and
`K = sum_i ||C_i|| / n`. K measures included-component cancellation, not
missing-physics uncertainty. At n = 0, K and BR rescaling are undefined.

Conditional on a hypothetical combined missing vector satisfying
`||Delta_missing|| <= b`, the triangle and reverse-triangle inequalities give
**`max(0, n-b) <= ||C+Delta_missing|| <= n+b`**.
Both endpoints are attainable: Delta = b C/n at the upper endpoint;
Delta = -min(b,n) C/n at the lower endpoint. At n = 0 any vector of norm
between 0 and b is possible. Arbitrary phases and both chiralities are covered.

The frozen radiative width is proportional to n^2 for each fixed channel
(confirmed directly in `module3/core.py:radiative_width`). Thus for n > 0,
`partial_BR_[min,max] = included_partial_BR * (norm_[min,max]/n)^2`.
At n = 0 the diagnostic reports null BR endpoints rather than inventing a
normalization; a nonzero supplied BR at zero norm is rejected.

**The fractions 0.05/0.1/0.25/0.5/1 of M are purely hypothetical budgets.**
They are not upper bounds on physical omitted contributions, numerical
uncertainty estimates, or physical estimates of Wgamma. Budgets concern the
combined missing vector; no W candidate coefficient is used to set them.

## Actual baseline outputs

Each channel contains 40 coherently included rows: seven frozen one-loop,
27 fermion/photon and six charged-scalar/photon rows. Both W candidates stay
`UNKNOWN` / `GAUGE_MATCHING_UNRESOLVED`, with `coherent_inclusion=false`.
All omitted-topology records are preserved. Signed amplitudes below are GeV^-2.

| Channel | C_L | C_R |
|---|---:|---:|
| mu -> e gamma | -1.281683792057e-14 -2.407972376890e-14 i | 6.458736616738e-13 +9.493117846681e-13 i |
| tau -> mu gamma | 6.419208362194e-14 +6.152697445927e-14 i | -5.412407333452e-15 +3.853490327203e-15 i |
| tau -> e gamma | 1.840277837326e-15 +1.779388034784e-15 i | 4.060172769847e-15 -3.852618445238e-15 i |

| Channel | n [GeV^-2] | M [GeV^-2] | sum norms [GeV^-2] | K | Included partial BR |
|---|---:|---:|---:|---:|---:|
| mu -> e gamma | 1.1485163280e-12 | 6.6665814014e-13 | 1.3836187048e-12 | 1.2047009442e+00 | 1.0576194035e-13 |
| tau -> mu gamma | 8.9164655143e-14 | 5.2274346656e-14 | 1.0973087004e-13 | 1.2306543424e+00 | 1.1210450982e-16 |
| tau -> e gamma | 6.1547149489e-15 | 4.9592239561e-15 | 9.2301121114e-15 | 1.4996814943e+00 | 5.3984420082e-19 |

All 15 conditional scenarios follow. Norm endpoints are in GeV^-2;
BR endpoints use the fixed-channel normalization above. Full precision values
and source SHA256 pins are in [omission_triage.json](omission_triage.json).

| Channel | Hypothetical b/M | b/n | Norm min | Norm max | Partial BR min | Partial BR max |
|---|---:|---:|---:|---:|---:|---:|
| mu -> e gamma | 0.05 | 0.029023 | 1.11518342e-12 | 1.18184924e-12 | 9.97120560e-14 | 1.11989993e-13 |
| mu -> e gamma | 0.1 | 0.058045 | 1.08185051e-12 | 1.21518214e-12 | 9.38403403e-14 | 1.18396215e-13 |
| mu -> e gamma | 0.25 | 0.145113 | 9.81851793e-13 | 1.31518086e-12 | 7.72942055e-14 | 1.38683893e-13 |
| mu -> e gamma | 0.5 | 0.290226 | 8.15187258e-13 | 1.48184540e-12 | 5.32806884e-14 | 1.76060063e-13 |
| mu -> e gamma | 1 | 0.580452 | 4.81858188e-13 | 1.81517447e-12 | 1.86163077e-14 | 2.64175058e-13 |
| tau -> mu gamma | 0.05 | 0.029313 | 8.65509378e-14 | 9.17783725e-14 | 1.05628514e-16 | 1.18773162e-16 |
| tau -> mu gamma | 0.1 | 0.058627 | 8.39372205e-14 | 9.43920898e-14 | 9.93451759e-17 | 1.25634472e-16 |
| tau -> mu gamma | 0.25 | 0.146567 | 7.60960685e-14 | 1.02233242e-13 | 8.16511027e-17 | 1.47374343e-16 |
| tau -> mu gamma | 0.5 | 0.293134 | 6.30274818e-14 | 1.15301828e-13 | 5.60141213e-17 | 1.87460601e-16 |
| tau -> mu gamma | 1 | 0.586268 | 3.68903085e-14 | 1.41439002e-13 | 1.91894351e-17 | 2.82082394e-16 |
| tau -> e gamma | 0.05 | 0.040288 | 5.90675375e-15 | 6.40267615e-15 | 4.97221941e-19 | 5.84218928e-19 |
| tau -> e gamma | 0.1 | 0.080576 | 5.65879255e-15 | 6.65063734e-15 | 4.56352149e-19 | 6.30346123e-19 |
| tau -> e gamma | 0.25 | 0.201440 | 4.91490896e-15 | 7.39452094e-15 | 3.44257578e-19 | 7.79242514e-19 |
| tau -> e gamma | 0.5 | 0.402880 | 3.67510297e-15 | 8.63432693e-15 | 1.92482644e-19 | 1.06245252e-18 |
| tau -> e gamma | 1 | 0.805760 | 1.19549099e-15 | 1.11139389e-14 | 2.03678491e-20 | 1.76030760e-18 |

The baseline K values are 1.205, 1.231 and 1.500, respectively: no extreme
included cancellation occurs in this example. For the hypothetical b = M
scenario, b/n is 0.580, 0.586 and 0.806. These numbers describe conditional
sensitivity only. They cannot establish whether physical omitted Wgamma
is small, even for this baseline.

## Audit, verification and provenance

The original seven tests passed. Direct counterexamples then confirmed the
original diagnostic accepted an empty W-candidate ledger, promoted W status,
and a wrong dipole convention. Scoped fixes require both frozen W rows,
unresolved/excluded status and compatible conventions; reject W rows in the
coherent ledger and non-boolean inclusion flags; preserve excluded ledgers
and source provenance by deep copy; expose signed totals and reproduced sums.
No physics coefficients, kernels, schemas or foundation records changed.

The expanded suite passes **11 tests, 0 failures, 0 errors, 0 skips**.
It covers analytic complex sums and K, independent/common phases, aligned
and anti-aligned endpoint attainment (including b > n), large cancellation,
zero included amplitude, invalid budgets, malformed/duplicate/nonfinite JSON,
input-byte SHA256, unchanged output on invalid input, provenance/conventions,
and fail-closed W exclusion and ledger preservation. BR assertions use
relative tolerances appropriate to the small values.

An independent baseline check used 80-digit Decimal arithmetic without
importing the diagnostic or physics kernels. It recomputed all signed sums,
norms, largest/summed component norms, K, the fixed-channel BR normalization,
and all 15 norm/BR envelopes; constructed endpoint perturbations; checked
exact preservation of provenance, candidate and omission ledgers; verified
every supplied Module4 source hash against disk and the frozen Git blobs;
and checked the canonical example-input hash and raw-input SHA256.
The maximum relative numeric residual was 1.20105603e-15
(acceptance tolerance 3e-14). Maximum real/imag signed-sum residuals were
2.24861289909e-28, 1.1228317743e-29 and 2.0388255371105e-30 GeV^-2
for mu/e, tau/mu and tau/e, respectively.

- Raw Module4 output SHA256: `783849ef9299b09f8355710402dd1ed82ace412d75b1716f6febdd2bcea2aa7e`.
- Diagnostic output SHA256: `496a038b30b4c6ed6f8c2dc32d72bb505d037cf90c009d04492a3897b4349dae`.
- Source hashes, signed sums, norms, scenarios and verification status are
  recorded in the companion JSON. Hashes establish this run's provenance;
  the diagnostic is not an independent authentication of arbitrary input
  claims or a replacement for Module4 physical validation.
- Git ancestry confirms the frozen base; the final diff contains only scoped
  triage files and the task-specific AGENTS.md. Modules 0–3, SARAH, existing
  Module4 physics/tests and prior validation records remain unchanged.
- This run uses the real supplied baseline and its already computed neutrino
  output. No neutrino fit, NO/IO witness search, or literature search was run.

Reproduction (run from repository root):

```bash
python -m unittest discover -s tests -p 'test_zee_omission_triage.py' -v
mkdir -p validation/module4/local
python -m module4.interface --input module4/example.json --output validation/module4/local/triage_input.json
python scripts/zee_omission_triage.py --input validation/module4/local/triage_input.json --output validation/module4/local/triage_output.json
```

Raw inputs/outputs and the local independent arithmetic checker remain in
ignored `validation/module4/local/`. The concise verified records are committed.

## Prioritized next physics milestone

1. Complete the signed off-shell W/Goldstone/ghost plus non-Barr–Zee pinch
   LFV matching in the frozen GeV^-2 operator. Explicitly project the remaining
   B,C structures and demonstrate R_xi independence at the retained external
   mass order, then identify and independently validate the completed
   transverse kernel. This is the first priority identified by the frozen
   matching audit; all W candidates stay excluded until it succeeds.
2. Only after that validation, include the matched W vector coherently and
   quantify its actual interference. A justified bound on the combined
   remaining amplitudes would be needed to interpret conditional envelopes
   as controlled physical ranges.
3. Continue the missing electroweak topology and mass/Yukawa-scheme program
   (Zgamma, mixed charged-current/additional bosonic terms and retained-order
   corrections) before any complete-rate or phenomenological claim.

There is no execution blocker for this diagnostic. The unresolved physics
blocker is the complete signed gauge matching described above, together with
the remaining omitted amplitudes and frozen-model limitations.
