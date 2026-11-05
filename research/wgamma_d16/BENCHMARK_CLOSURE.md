# Bounded D16 numerical closure

**Partial research result, not full radiative LFV acceptance.** Four actual
frozen Module2 inverse solutions (NO/IO, two scalar spectra) and two separate
mixed amplitude fixtures were calculated. All three ordered decay channels
retain complex L/R and per-class errors. Detailed input/result files remain
ignored under `local/`, bound by `two_loop_evidence.json`.

## Mixed-current witnesses

The G1/G2 doublet inputs and independent complex D matrices are reused from
the existing validated reference evidence. They now have charged spectra
`(210.0932433465,540)` and `(329.0038105129,670)` GeV, gamma=.34 and −.27,
respectively, and portals `(K1,K2,K12)=(.3,.18,−.04)`. These are reconstructed
amplitude fixtures with F=0, not neutrino fits. Both pass sufficient BFB and
tree unitarity. EWPO and vacuum are not evaluated for these two fixtures.

New mu→e **off-diagonal charged-pair current** coefficients, GeV−2:

| Fixture | C_L, a≠b | C_R, a≠b |
|---|---|---|
| Mixed G1 | +4.508180006e−14 +2.364676231e−14 i | +5.732603325e−14 −1.985761173e−15 i |
| Mixed G2 | −7.032165591e−14 +5.309842569e−14 i | +6.608546490e−14 +1.671389834e−14 i |

Their full diagonal-plus-off-diagonal **radiative-current subset** gives
`CL=(5.058796396+2.653491116i)e−13`,
`CR=(6.432767326−.2228296442i)e−13` for G1 and
`CL=(1.715719009−1.295503883i)e−12`,
`CR=(−1.612363743−.4077883653i)e−12` for G2. Absolute quadrature estimates
are at most 4.19e−21 here; they exclude matching/truncation/input uncertainty.
No whole mixed-potential-sector or W coefficient is claimed by these values.

At generic off-shell momenta the longitudinal Z tensor norms are .005186
and .002233. The largest independently integrated Z/G0 identity residual
is 3.91e−15, photon Ward residual 5.89e−16, and projected Goldstone current
2.78e−16. Thus off-shell nonconservation is exhibited, not silently discarded.
ξ=.5,1,3,7 comparisons are real-photon **current-tensor** tests with independent
complex L/R probe currents; they are not complete Zee W Wilson comparisons.
Eight mixed-HZ tests also cover soft extraction, two radial parameterizations,
both strict limits, dense charged-basis rotations, phases and nulls.

## Actual neutrino witnesses and coherent included-only rates

These use the frozen `module3.witnesses.example(ordering,spectrum)` and
`module2.interface.evaluate`, with their exact complex target and family
coefficients. Forward and inverse gates pass independently for all four.
Spectrum0 passes sufficient BFB, tree unitarity and scalar EWPO. Spectrum1
has a sufficient BFB certificate miss (UNKNOWN), passes unitarity, and fails
EWPO. Vacuum is NOT_EVALUATED throughout. These classifications are not
changed to make amplitude benchmarks appear allowed.

| Input | Included-only BR(mu→eγ) | Included-only BR(tau→eγ) | Included-only BR(tau→muγ) |
|---|---:|---:|---:|
| NO, spectrum0 | 1.189718948e−13 | 5.592445495e−19 | 1.262507260e−16 |
| IO, spectrum0 | 4.480238989e−13 | 9.911479103e−19 | 2.087075671e−16 |
| NO, spectrum1 | 4.739696771e−13 | 2.353426576e−18 | 9.340373688e−16 |
| IO, spectrum1 | 3.329886592e−12 | 1.717514789e−17 | 1.095131295e−14 |

Every full BR is **null**. These partial rates are not comparisons to limits.
For spectrum0, `2 Re(C_one† C_two,included)` is positive in mu→eγ and
negative in both tau channels, demonstrating coherent constructive and
destructive interference rather than adding squared subset rates.

For the NO spectrum0 mu channel, the new physical scalar Z current is
`CL=4.147436538e−18+7.794732569e−18 i`,
`CR=−2.088301669e−16−3.063200300e−16 i` GeV−2. The IO result is separately
recorded. A relative correction to the **complete** Zee answer cannot be
quoted while its missing complex denominator is unknown. Per-class ratios
to the included partial answer are calculable from the stored coefficients,
but are not that physical relative correction.

All virtual gauge couplings use tree on-shell MW,MZ,v, shared by photon
and new Z rows. The emitted-photon rate uses the explicit alpha(0) snapshot
and the frozen massive phase-space formula
`Γ=alpha(0) mi^5/4 (1−mj²/mi²)^3 (|CL|²+|CR|²)`.
The quark masses are the explicit Module4 illustrative **NOMINAL_UNMATCHED**
dataset, not a precision running-mass fit. The complete input, scheme and
error boundary are present in every detailed output.

## Reproduce

```bash
python -m unittest research.wgamma_d16.test_zee_mixed_hz research.wgamma_d16.test_zee_two_loop -v
python -m research.wgamma_d16.reproduce_two_loop
python -m research.wgamma_d16.zee_two_loop --witness NO --output research/wgamma_d16/local/cli_NO.json --require-completion
python -m research.wgamma_d16.zee_two_loop --witness IO --spectrum 1 --output research/wgamma_d16/local/cli_IO.json --require-completion
python -m research.wgamma_d16.w_outer_reduction --output research/wgamma_d16/local/w_outer_reduction.json --require-completion
```

The 14 focused tests pass. The three `--require-completion` commands write
their real results then exit **2**, because full amplitudes remain missing.
The bounded evidence generation takes a few seconds (actual timing and RSS
are recorded). No D15 revalidation, 39-channel replay, full test suite,
scan, model rebuild, remote job, or Module0–14 modification was performed.
The exact W master reduction and F² UV obstruction are explained in
`ZEE_TWO_LOOP_DERIVATION.md`; the minimum next calculation is its complete
d-dimensional numerator/crossed/charged/BRST/LSZ reduction. No D14 overlay
is produced before the required full acceptance.
