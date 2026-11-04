# D16 status: BLOCKED_GAUGE_MATCHING

`WGAMMA_GAUGE_MATCHING_PASS` has **not** been established. Physical W
`C_L,C_R` remain null/UNKNOWN, and coherent inclusion is false. Modules0–14,
the Zee Lagrangian and frozen D15 code are unchanged. All development and
evidence are confined to this directory.

Verified progress:

- Exact B cancellation for both photon attachments, unequal external masses
  and independent complex LFV chiralities.
- Exact C cancellation for the complete off-diagonal h/H sum, using native
  Yukawas after the scalar inverse propagator cancels.
- Electromagnetic Ward checks of the **Abe source** A/P/B/C plus published
  pinch, with nonzero virtuality. This is a source check, not a new W-loop sum.
- 58 fresh native SARAH vertex queries; 444 independent coefficient checks
  at two spectra and xi=.5,1,3; worst residual 1.14e-13.
- 26 inner graphs independently counted with existing FeynArts3.9;
  all inner graph integrals and general-xi parents explicitly unavailable.
- Independent source-A radial integration and corrected 2016 B.8 photon
  comparison. Ten scoped tests pass; a deliberately incomplete gauge
  prescription fails by 4.21% at the second complex point.

`evidence.json` contains the actual residuals, complex diagnostics, source
and log hashes, tool versions and frozen-tree check. `native_vertices.json`
contains actual symbolic native rules, with their returned field/tensor order.
Detailed logs, source documents, FeynArts expressions and generated SARAH
output are in ignored `local/`.

| Acceptance gate | Result | Exact gap |
|---|---|---|
| A, complete diagrams/assumptions | BLOCKED_GAUGE_MATCHING | Inner inventory complete; general-xi LFV pinch/LSZ/charged-parent completion not enumerated and reduced |
| B, independent tensors and gauge checks | BLOCKED_GAUGE_MATCHING | B/C proofs and xi=1 **source** Ward identities pass; signed regulated inner W/mixed/ghost integrals and general-xi projected parent sum missing |
| C, independent physical Wilsons and reference arbitration | NOT_EVALUATED | No independent full signed W coefficient, reverse ordered two-loop amplitude, full diagonal moment, or physical coherent interference benchmark |
| D, validated interface/integration | BLOCKED_GAUGE_MATCHING | Diagnostic interface works; returns unavailable physical coefficients; D14 integration remains excluded |

## Precise blocker and resolution

For the deterministic second example, the known native Goldstone
triangle+seagull projection changes when xi changes. At xi=3 the uncomputed
remaining graph sum must change by

```
Delta CL = +5.0475478422e-10 +4.8569087322e-10 i GeV^-2
Delta CR = -1.9418997438e-09 +1.9695905279e-09 i GeV^-2
```

relative to xi=1. At xi=.5 the independently specified compensators are
also recorded. The exact missing identity for both projected chiralities is

```
Delta_xi(C_W + C_mixed + C_ghost + C_pinch) = -Delta_xi C_G.
```

Its left side has **not been calculated**. The failing example rejects
Goldstone-only mass replacement; it is not evidence that a completed W
amplitude violates gauge independence. The native ghost coupling changes
with xi as well as its mass, and W propagators add longitudinal poles.
Those cannot be supplied by changing a named transverse kernel.

The next calculation is concrete:

1. Contract and dimensionally integrate the enumerated 26 native inner
   graphs, retaining scalar and virtual-photon off-shell invariants and all
   A/P/B/C (plus any additional general-xi) structures. First reproduce the
   xi=1 source coefficients independently; do not impose transversality
   before summing. Preserve divergent terms until their cancellations.
2. Reduce the native W/G lepton-current parents with the same momentum
   routing and general complex D. Audit physical H1/H2 and external/LSZ
   pieces using the charged sum identities only after the needed propagators
   cancel. Their residual transverse terms cannot be inferred from P alone.
3. Project both chiralities in the frozen action. Verify the compensator
   identity at xi=.5,1,3 at this one point, with integration error estimates
   and an absolute-plus-relative criterion. Then expand to other independent
   points, reverse ordering, diagonal moments, signs and coherent interference.
4. Only after those checks can the CHK/Ilisie/Abe differences be assigned to
   definite complete sets and the physical numeric interface be released.

This is unfinished analytic work, not an unavailable service or a D15
inconsistency. Existing Mathematica/SARAH/FeynArts infrastructure was usable.
No convention or result has been changed to repair the falsifier.

## Reproduction

From repository root, the minimal failing acceptance case needs only the
existing Python scientific environment:

```sh
python3 -m research.wgamma_d16.matching --example 1 --require-pass
```

It exits **2** and prints a JSON diagnostic with physical `C_L,C_R=null`.
Omit `--require-pass` to exit zero after successfully producing the diagnostic.
`--input path.json --output path.json` supplies an explicit input; input
layout is the return value of `matching.example(1)`. Example masses and D
are reproducible amplitude witnesses, not accepted neutrino-fit scan points.

```sh
python3 -m unittest research.wgamma_d16.test_d16 -v
python3 -m research.wgamma_d16.reproduce
```

The latter refreshes compact evidence, tests and diagnostic outputs. To
repeat the fresh native extraction and independent topology count as well:

```sh
python3 -m research.wgamma_d16.reproduce --native
```

That uses the installed SARAH4.15.4 through `math` and the **existing**
`research/spheno_flavorkit/local/FeynArts-3.9`. Set `D16_FEYNARTS` to another
pre-existing FeynArts3.9 directory if needed. It does not download or rebuild
dependencies, regenerate a model, compile SPheno, rerun D15 or run the
repository suite. Cached primary sources are optional for numerical
reproduction; if present their SHA256 values must match `sources.json`.

## Reference arbitration boundary

The three kernels still differ. At z=.413 the conditional values are
CHK=6.03819122247114, Ilisie=5.97525641636409,
Abe-A=5.78840763191936. Their exact differences are

```
CHK-Abe    = 3(g+h)/4
Ilisie-Abe = 3(3f-2g)/2
CHK-Ilisie = 3(h+5g-6f)/4
```

They are not constant rescalings. CHK separates W and mass-enhanced
Goldstone pieces and additional set-C diagrams. Ilisie's transverse
prescription discards additional off-shell structures while discussing their
completion. Abe constructs a pinched xi=1 EDM source; the 2016 erratum must
be used for B.8. Davidson imports CHK for a restricted flavor/decoupling
discussion. The 2017 Zee analysis is a coverage comparison, not an
independent general-xi tensor derivation. Versioned primary links and exact
retrieved hashes are in `sources.json`.

Agreement of our radial integral with corrected Abe B.8 verifies its
transcription, not its independent physical LFV completion. No kernel is
selected, no W coefficient enters D14, and no full Zee LFV constraint follows.
