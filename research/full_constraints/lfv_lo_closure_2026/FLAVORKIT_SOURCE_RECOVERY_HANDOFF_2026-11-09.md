# Source recovery: complete Zee FlavorKit Wilson coefficients

**9 November 2026 — Full leading LFV still UNKNOWN. A hash-checked exporter is available.**

## Verified state

The research branch contains source manifests and numerical partial controls, but not the generated Zee SPheno/FlavorKit Fortran. The complete generated photon, low-q² Z and box groups have never been validated. The restricted F-only box was compiled from original local generated files, but that does not verify other groups.

Required filenames and SHA-256:

| ID | Filename | SHA-256 |
|---|---|---|
| generated | FlavorKit_LFV_ZeeTypeII.f90 | 2d30006d8d4759b2b7bfe76e2e4795bd2cf2f19ef5cb5772390ed3155b1bc41d |
| couplings | Couplings_ZeeTypeII.f90 | a0de851498f3e68e7421538098b3979381a3ecf5245021fce9d1c2df46a42e8c |
| loops | LoopFunctions.f90 | 8142a813fcc00283d1de2865266be04ff1de25c09422b24b04d57523a6595a24 |

These hashes are pinned in research/full_constraints/lfv/SOURCE_TO_CODE_SOURCES.json. The user-controlled original absolute paths are contained there.

## One-command source export, read only

From the research branch, after a fast-forward pull:

    python3 -m research.full_constraints.lfv_lo_closure_2026.export_flavorkit_sources

This creates ~/zee_lfv_source_bundle.zip with three exact hash-checked Fortran sources and SOURCE_EXPORT_RECEIPT.json. It does not regenerate the model, inspect credentials, modify source files, run physics, or push a public code upload. Attach the resulting ZIP in the current chat for direct analysis. The exporter rejects missing or modified sources and accepts explicit --generated, --couplings, --loops path overrides.

A standalone 3-test synthetic suite checked the archive, source immutability, missing-path rejection and SHA mismatch. Those tests passed in the assistant runtime. The repo checkout tests have not been executed on the user's machine.

## Targeted follow-up on those exact bytes

1. Identify generated photon K1L/R, Z low-q², scalar penguin and full box operator groups, including native vertex calls and loop functions.
2. Compile bounded original source blocks, comparing pure F and pure D source limits and the two-state complex phases against existing literature-backed controls.
3. Validate common chiral sign, gauge/scale cancellation and operator ordering before summing with dipole or nuclear currents.
4. Build a full signed mu3e and Al LEFT rate only for complete leading operator sets; otherwise issue a precise source-line blocker with null physical rate.

Correct the known original FlavorKit scalar proton/neutron interchange in an isolated adapter; do not assume the published nuclear converter is valid unmodified. Finishing one-loop mu3e and Al does NOT automatically close the separately unresolved radiative two-loop electroweak amplitudes.

**No new scan or claims of accepted benchmarks.** physical_lfv=UNKNOWN, global_acceptance=null.
