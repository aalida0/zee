# Zee LFV — coherent tree/dipole matrix-element calculation and native SARAH handoff

**10 November 2026 | Completed restricted source-reuse calculation, not a full-model LFV prediction.**

## Exact scope and novel calculation

The four frozen `D7 NO/IO` and `F13 NO/IO` Zee witnesses are read through
the original SHA-256 pinned `validation/module12/d12_benchmarks.json` source.
The `tau_coherent_tree_dipole_phase_scan.py` implementation now evaluates,
*at the amplitude level*:

1. Full neutral h/H/A tree exchange including identical-electron antisymmetrization,
   complex Yukawas and the exact finite-mass three-body phase space
   (`module3.tree` source-validated implementation).
2. The complete tree-level virtual-photon **constant-K2** dipole amplitude,
   including both photon permutations for identical final leptons,
   with exact finite lepton masses and the original Zee one-loop Module3
   complex coefficients plus **only** the corrected general-2HDM
   *neutral-fermion* Barr–Zee amplitude.
3. The phase-space integrated **complex interference overlap**
   `I = int <M_tree, M_photon> dPhi`.
   For identical negative leptons, the exact exchange identity
   `1/2 int T*(P_direct-P_cross) = int T*P_direct`
   avoids numerically unresolved crossed photon collinear endpoints.
4. The mathematically sharp interval for an *unmatched overall relative phase*:
   `B(phi)=[Gamma_tree+Gamma_dipole+2 Re(exp(-i phi) I)]/Gamma_tau`.
   The interval endpoints are `B_center +/- 2 abs(I)/Gamma_tau`.
   These are bounds **only for the two named partial amplitudes**, not physical total
   Zee branching-ratio bounds or bounds on any omitted amplitudes.

Original corrected `general-2hdm-pheno` source at GitLab commit prefix
`b5035cd5`, `thdm.py` SHA256
`9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193`,
was cloned and executed unchanged; author Type-II `rho_u,rho_d` use the
author's internally run `MSbar` quark masses at the `mt` scale.
The known signed matching in Module3 convention is
`CL = - K2R_native`, `CR=-K2L_native`,
with BZ mapped via `K2L_native=cR/(8*pi²*v²)`,
`K2R_native=cL/(8*pi²*v²)`.

**CRITICAL**: The original compiled generated SARAH **complex** `K2L,K2R` for
the four frozen cards are NOT present in this GitHub repository or its
available Actions artifacts. These runs therefore used the independently
validated analytic Module3 one-loop complex `CL,CR`, **not the original
compiled full OA2 complex source**. Their radiative BR agreement with the
saved original source is at 3 ppm for tau->e gamma and ~1.06% for tau->mu gamma
(primarily the `(1-m_mu²/m_tau²)^3=0.9894297281` massless-final-state source
approximation). After corrected BZ inclusion, rates differ from saved
original source partial rates by ~1.5–1.6% tau->e gamma and 0.44–0.46% tau->mu gamma.
No source-matched final phase is thereby certified.

## Validated numerical results (56×20 photon/integral nodes; tree order 24)

Numbers represent source approximations **for constant K2 and neutral h/H/A tree
only**, with an arbitrary overall relative phase.

| Frozen witness | BR tau->3mu dipole | BR tau->3mu neutral tree | restricted phase interval tau->3mu |
|---|---:|---:|---|
| D7 NO | 4.180659037e-14 | 8.066207952e-16 | [4.249856653e-14,4.272785580e-14] |
| D7 IO | 4.786837821e-14 | 1.201634827e-15 | [4.843285345e-14,4.970717263e-14] |
| F13 NO | 5.572214252e-18 | 2.898158205e-21 | [5.549102482e-18,5.601122339e-18] |
| F13 IO | 6.380055599e-18 | 6.859465498e-21 | [6.338860013e-18,6.434970115e-18] |

| Frozen witness | restricted phase interval tau->3e | tau->e- mu- mu+ | tau->mu- e- e+ |
|---|---|---|---|
| D7 NO | [4.847099170,4.847121536]e-16 | [9.779404864,9.779404864]e-17 | [1.891737197,1.891737197]e-13 |
| D7 IO | [2.890185985,2.890188856]e-15 | [5.869724759,5.869724759]e-16 | [2.170119045,2.170119045]e-13 |
| F13 NO | [6.224767749,6.224775145]e-20 | [1.229602909,1.229602909]e-20 | [2.521320082,2.521320082]e-17 |
| F13 IO | [3.792878620,3.792882606]e-19 | [7.497057807,7.497057807]e-20 | [2.892182973,2.892182973]e-17 |

Some mixed-flavor scalar-photon interferences are numerically zero at
the reported precision in this restricted source computation. This is **not**
evidence that all neutral scalar or four-lepton diagrams physically vanish.

A special numerical issue was found for certain very small complex dipoles
in tau->mu ee near the photon collinear endpoint: direct gamma-matrix traces
can fail positivity due cancellation. The final implementation uses the
previously source-tested positive-Hermitian 2×2 chirality kernel evaluated
from four unit-probe amplitudes. Full complex chirality interference is
preserved. The initial CI failures remain visible in the history and do not
certify the earlier unstable implementation.

## Native original SARAH K2 input contract

`tau_native_sarah_complex_import.py` implements a **fail-closed** original
source-input contract: correct archived `generated`, `couplings`, `loops`
SHA256s; compiler mode; frozen D7/F13 card ordering; explicit native
`K2=-OA2/(2*e*m_tau)` convention; and the complex norm of each imported
`K2L,K2R` reproduces original one-loop tau gamma BR with the original
source's massless-final-state normalization.

**A hash plus a rate match never establishes a complex phase or source execution.**
The import output explicitly sets `original_fortran_executed_in_this_validation=false`,
`input_phases_independently_verified=false`,
`physical_lfv=UNKNOWN`. Synthetic test vectors are created *only* inside
the regression suite and never saved as physics data.

An optional `--native-original-json` switch in the coherent phase scan
can consume a four-card norm-validated JSON once an original compiled replay
is actually available; it still refuses physical acceptance because a rate
and source hash are insufficient proof of the phases or omitted Zee diagrams.

The existing `export_flavorkit_sources.py` can export the three original
private source files from the user's local paths after SHA validation; they
have not been copied into this public repository or regenerated.

## CI and reproducibility

- Exact two-amplitude phase integration run and machine-readable artifact:
  https://github.com/aalida0/zee/actions/runs/42824361882
- Original native complex K2 import (synthetic only, source not reexecuted):
  https://github.com/aalida0/zee/actions/runs/42824984406
- Current optional-import test includes synthetic native K2 vectors and checks
  every physical-rate field remains null; the CI result is logged by
  `.github/workflows/zee-lfv-tau-coherent-phase-scan.yml`.

```sh
python3 -m research.full_constraints.lfv_2hdm_gitlab_reuse_2026.tau_coherent_tree_dipole_phase_scan \
  --source /path/to/pinned/general-2hdm-pheno --commit b5035cd5 \
  --ns 56 --nz 20 --tree-order 24 --output tau_two_amplitude_phase_scan.json
```

## Unresolved physics

- The original complex native SARAH tau `K2L,K2R` output and its executable
  source replay/phase convention: **not recoverable from committed public
  repository and checked CI artifacts**.
- The unique signed physical tree/dipole relative phase: **not certified**.
- The off-shell photon `K1(q²)`, `K2(q²)`, Z penguin, box, scalar
  renormalization, QED/LEFT and genuinely Zee-specific mixed charged/gauge
  two-loop amplitudes: **not included**.

**Machine gate: SOURCE_RESTRICTED_COHERENT_AMPLITUDE_TEST_PASS;
ORIGINAL_NATIVE_COMPLEX_K2_NOT_ARCHIVED; ALL_PHYSICAL_LFV_UNKNOWN;
GLOBAL_ACCEPTANCE_NULL. No scan-wide exclusion/acceptance claims.**
