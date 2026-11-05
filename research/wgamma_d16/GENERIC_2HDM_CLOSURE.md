# Generic nonzero-potential common-limit closure

**PASS for the complete complex reference coefficients after the independently
audited HW normalization replacement.** Original author code retains its HW
normalization failure. This is the CP-conserving, lambda6=lambda7=0 scalar
potential common to the frozen Zee model and general 2HDM, with general complex
lepton D. It is not validation of arbitrary CP-violating scalar potentials,
all higher-order Yukawa corrections, or full Zee gauge matching.

`hw_generic_evidence.json` contains 13 reconstructed spectra/variations,
39 complex channel comparisons (both L and R), 39 integral-master witnesses,
39 diagonal EDM class checks and 78 common-scale comparisons. The three new
independent generic potentials use full nonzero complex D matrices from
NumPy default_rng seeds **241017400, 241017401, 241017402**, respectively,
normal real/imaginary entries with scale .003. Inputs and hashes are stored.

## Consistent potentials and separate scalar constraints

All use `mh1=125.0`, `v=246.21965` GeV, gamma=0, F=0, portals=0,
`mH2=10000` GeV (removed singlet placeholder), LambdaC=.4. The two old
Z3=Z7=0 controls retain their original LambdaC and exact inputs. For each
new potential two linear equations for Z3,Z7 determine m12sq and charged
mass squared, with the neutral masses and angles fixed. Negative squared
mass solutions are rejected, never clamped. Full original-potential
Hessian/mixing/tadpole reconstruction is mandatory. Thus masses and scalar
trilinears are not arbitrary independent inputs.

| Fixture | mH1 [GeV] | mh2,ma [GeV] | alpha,beta | m12sq [GeV²] | Z3,Z7 | BFB/unitarity |
|---|---:|---|---|---:|---|---|
| G1 | 210.093243347 | 310,325 | .64,.75 | 14368.736703420 | .8,.3 | PASS/PASS |
| G2 | 329.003810513 | 360,350 | 1.08,.92 | 50252.986456275 | .6,-.5 | PASS/PASS |
| G3 | 236.083903768 | 280,305 | .53,.65 | 33291.123300427 | -.1,.2 | PASS/PASS |

BFB and tree unitarity use actual frozen Module1 APIs; sufficient-certificate
misses are not fabricated passes. These are amplitude fixtures, not neutrino
fits or accepted model points. Vacuum globality, EWPO and experimental
constraints are not evaluated. Seed/potential selection uses algebraic
spectrum consistency and scalar conditions, not optimization of dipoles.

Additional controlled probes independently change Z3 sign at fixed Z7, Z7
sign at fixed Z3, both signs, mh2, the neutral mixing angle, MW=76 or84 GeV,
and lepton rephasing. Changing Z3,Z7 in this restricted potential changes
the solved soft/charged mass inputs too; it is not a derivative at fixed
all Higgs-basis coefficients. Changing MW updates `sw²=1-MW²/MZ²`,
`g2=2MW/v`, `alpha=g2²sw²/(4pi)` consistently. Those EW probes are formal,
not measured EW benchmarks. Every variation reconstructs its own potential.

G1, G2, G3, Z3_sign, angle, MW76, MW84 and phase pass BFB/unitarity.
Z7_sign, both_signs and mass fail BFB and pass unitarity. Historical control1
fails BFB and passes unitarity; control2 fails both. These failures remain
explicit in the evidence; none of those fixtures is advertised as allowed.
All Hessians have the specified positive physical eigenvalues and Goldstones.
G_h,G_H are independently checked by differentiating the **full potential
Hessian**, and against the Higgs-basis rotation; G_A diagonal vanishes.

## Complete signed coefficients

The following are **two-loop only**, dimensionless corrected cL,cR. The
evidence also contains all 13 captured author groups, full one+two-loop
coherent totals, corrected HW, original totals, differences and converted
dimensionful C. Channels use parent/daughter labels.

| Potential | Channel | cL two-loop | cR two-loop |
|---|---|---|---|
| G1 | mu→e | -.01146208445-.006012171031i | -.01457517238+.000504843238i |
| G1 | tau→e | +.004486949829-.002402674554i | -.0003409975822-.0004427325753i |
| G1 | tau→mu | -.0009097297297+.00004367470154i | -.0003729201067+.001995971589i |
| G2 | mu→e | +.02142879609-.01618147787i | -.02013823293-.005093889467i |
| G2 | tau→e | -.001257611382+.0008908919208i | +.001284190824+.001135571339i |
| G2 | tau→mu | -.0006472114741+.001727335813i | +.001239272051-.001590459709i |
| G3 | mu→e | -.03666132094-.06811024751i | +.06780538459-.02533691705i |
| G3 | tau→e | -.0002667502009+.002378023248i | +.002767954904+.0008199486969i |
| G3 | tau→mu | -.0008169874778+.002936567122i | -.001054694183+.000248834649i |

Compare the independent native-field-basis sums with captured groups,
replacing only HW in the reference aggregate. Maximum relative residual,
over nonzero-potential cases, three channels and two chiralities:

| Group | Maximum relative residual |
|---|---:|
| 1loop, author truncation | 4.45e-15 |
| th | 6.39e-16 |
| ch | 6.60e-16 |
| bh | 4.13e-14 |
| tauh | 1.01e-15 |
| tHp | 5.60e-16 |
| cHp | 5.88e-16 |
| tauHp | 5.69e-16 |
| hZ | 4.30e-16 |
| kin, complete published aggregate | 1.03e-13 |
| HA | 8.46e-16 |
| HZ | 6.88e-16 |
| HW, independently audited replacement | 6.63e-12 |

The maximum coherent two-loop component absolute residual is `4.45e-15`.
The near-zero potential groups of controls are compared with an absolute
tolerance; their relative roundoff is not a meaningful precision measure.
Original-versus-corrected group difference is **exactly zero for 12 groups**;
the retained HW difference accounts for the entire coherent-total shift.
Per-group leave-one-out checks and a separate HW=0 falsifier prevent missing
groups from hiding behind a coherent cancellation. Every generic channel
has nonzero complex HW and every leave-one-out difference is nonzero.
Both original and corrected totals transform with the predicted common
external-lepton phase. Reversing/truncating imaginary pieces is detectable.

## Validation boundary and reproducibility

The normalization argument, including the diagonal Hermitian-pair factor,
is in [HW_NORMALIZATION_AUDIT.md](HW_NORMALIZATION_AUDIT.md). The converted
operator is exactly `C_X=-c_X/(8pi²v²)`, including sign, with no chirality
swap. The original expected-failure regression remains visible in unittest.

All 13 sums reuse the reference master functions; HW masters also have
independent parameter quadrature checks. Frozen Module4 photon kernels
give additional independent signed overlap checks in the retained old six
tests. This constitutes complete **complex coefficient common-limit
closure**, not independent reproduction of the entire authors' two-loop
derivation or gauge-parameter cancellation. The author approximation keeps
specified leading Yukawa/external-mass terms and weak-scale quark masses,
uses the unit-CKM approximation in charged quark terms and omits QED running.

Frozen Module3 one-loop coefficients retain finite daughter/internal mass
effects absent from the author's expansion. Historical tests continue to
record those nonzero differences. They are not changed or folded into a
false exact-one-loop agreement. All old D15/D16 evidence, source and matching
gates are preserved. No physical full Zee W coefficient, scan result or D14
integration is released.

```bash
python -m research.wgamma_d16.external_2hdm_hw_override --output research/wgamma_d16/hw_generic_evidence.json
python -m unittest research.wgamma_d16.test_hw_normalization research.wgamma_d16.test_external_2hdm -v
git diff --check
```

The reference checkout is pinned at
`b5035cd58d2a7e4a91e9790d045df062b97adffe`; reuse installation instructions in
`EXTERNAL_2HDM_BASELINE.md` if it is absent. Python/NumPy/SciPy versions,
original author file hashes, new code hashes, unchanged frozen source hashes,
input/evidence hashes and detailed-output SHA are in `hw_generic_evidence.json`.
`hw_validation.json` binds the actual local CLI/test logs and preserved-source
checks. Detailed repeat records and logs are ignored under `local/`.
