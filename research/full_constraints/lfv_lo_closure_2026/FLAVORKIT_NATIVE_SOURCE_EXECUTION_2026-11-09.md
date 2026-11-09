# Native generated Zee FlavorKit LFV source: independent executable audit

**9 November 2026 — PASS on source-locked charged-photon monopoles; FULL PHYSICAL LFV UNKNOWN.**

The user supplied the ZIP exported by `export_flavorkit_sources.py`. Each archived generated file exactly matches its earlier pinned SHA-256:

| Source | SHA-256 |
|---|---|
| `generated.f90` | `2d30006d8d4759b2b7bfe76e2e4795bd2cf2f19ef5cb5772390ed3155b1bc41d` |
| `couplings.f90` | `a0de851498f3e68e7421538098b3979381a3ecf5245021fce9d1c2df46a42e8c` |
| `loops.f90` | `8142a813fcc00283d1de2865266be04ff1de25c09422b24b04d57523a6595a24` |

## Executed, not just algebraically compared

The original `SmallDifference`, `MonopoleFSS` and `MonopoleSFF` Fortran functions were extracted **unchanged** from `loops.f90`, compiled using `gfortran -O0 -fcheck=all` and evaluated for 18 combinations of scalar mass and internal e/mu/tau masses. Every test passes:

```text
MonopoleFSS(0,M^2,M^2) = -1/(18*M^2)
MonopoleSFF(M^2,m_l^2,m_l^2) = Gc(m_l^2/M^2)/(6*M^2)
Gc(x) = [16-45*x+36*x^2-7*x^3+6*(2-3*x)*ln(x)]/[6*(1-x)^4]
Max relative neutral difference = 6.28e-16
Max relative charged difference = 0
```

**Stronger independent test:** the unmodified native generated vertex subroutines `CouplingFvFecHmT`, `CouplingcFeFvHmT`, `CouplingHmcHmVPT` and `MonopoleFSS` were compiled with the two literal original `OA1L/OA1R` charged-FSS amplitude lines extracted from `CalculateGamma2l`. The test input is a **synthetic complex F and doublet Yukawa pair** chosen to exactly reproduce each frozen D7/F13 `(F^dagger F)_{e mu}` and `(D D^dagger)_{e mu}` invariant; original charged masses/mixing are retained. It does **not** claim to reconstruct the physical point's full F and D matrices. Both chirality coefficients agree with the independent Hundi-style formulas:

```text
A1L_F = -(F^dag F)_{e mu} [s_gamma^2/m1^2 + c_gamma^2/m2^2]/(288*pi^2)
A1R_D = -(D D^dag)_{e mu} [c_gamma^2/m1^2 + s_gamma^2/m2^2]/(288*pi^2)
```

| Invariant input | Complex relative residual F | Complex relative residual D |
|---|---:|---:|
| D7 NO | 3.31e-16 | 1.16e-16 |
| D7 IO | 2.13e-16 | 2.31e-16 |
| F13 NO | 1.06e-16 | 2.30e-16 |
| F13 IO | 6.10e-17 | 8.14e-17 |

**This is an executable source-level proof of the restricted charged F and D photon monopole sectors**, including phase orientation, the original native vertices, charged photon vertex and both mass eigenstates. It is not a proof of the entire `CalculateGamma2l` or its gauge completion.

## Generated Wilson grouping discovered

The original generated module contains the following distinct groups:

- `CalculateGamma2l` (lines **46280–46984**): 17 generic diagrams, 14 `Monopole*` invocations; dipole `OA2lSL/SR` and monopoles `OA1L/R`.
- `CalculatePengV4L` (lines **25146–27793**): 46 generic diagrams, including wave and triangle Z exchange with zero-invariant `B0C0check` and `C0check`; `CalculatePengV4Lcross` (lines **40721–45911**) has 92 structures.
- `CalculateBox4L` (lines **18631–20171**): 31 generic box topologies; crossed `CalculateBox4Lcross` (lines **28069–30665**) has 52.
- `CalculatePengS4L` (lines **20173–25144**) and its crossed partner include additional scalar-penguin groups.
- Both `2L2u` and `2L2d` vector/scalar penguins, trees and box routines exist for conversion. They require the actual Type-II quark vertices, which were not instantiated in the standalone test.

The original `CalculateGamma2l` sets several external-wave `OA1` terms to zero. This *may* reflect its transverse decomposition; it is **not evidence of a bug by itself**. Photon Ward/transversality and common signed action still need a full coefficient test.

## Remaining scientific blockers

1. **Neutral e/mu and tau off-shell form factors:** the original `MonopoleSFF` exactly reproduces the published zero-external-invariant kernel for e, mu and tau, but the physical `mu -> 3e` virtual photon has a nontrivial `q^2` range. Simply using a `q^2=0` loop approximation for light internal e/mu is not a source-qualified full result.
2. **Complete Z and scalar penguins:** generated source *exists* but the full physical vertex arrays, wave+triangle group and UV/scale cancellation remain uncompiled/unverified together.
3. **Full D/F/gauge boxes and crossed ordering:** prior F-only box extraction does not certify the full generated operator vector; physical card-specific complex phases must be checked in one rate basis.
4. **Conversion:** native Type-II semileptonic operators and the corrected proton/neutron scalar matching, plus full interference, are still necessary.
5. **Radiative two-loop groups:** selected Barr–Zee sectors are source checked, but material missing W/gauge/mixed pieces still prevent full global LFV acceptance.

**Physics verdict:** `FULL_LEADING_LFV_INCOMPLETE`, `physical_mu3e_BR=null`, `physical_conversion=null`, `physical_lfv=UNKNOWN`, `global_acceptance=null`. No new parameter scan.

The reproducible Python extraction/compilation scripts, 18 original-kernel measurements, eight complex original-native-vertex checks, source function inventory and machine-readable audit are supplied as a downloadable audit archive in the originating chat. Original archived Fortran bytes are intentionally not redistributed or pushed to GitHub.
