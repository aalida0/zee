# Exploratory D12 benchmark comparison

**Overall status: NOT_EVALUATED** as an amplitude-level validation. The
executable ran and the checks below are diagnostic; the candidate convention
map has not been derived and the EW inputs are not fully matched. No LFV
exclusion or full Zee acceptance follows from this run.

The input is `validation/module12/d12_benchmarks.json` group 0, central witness
`d7_NO_neutral_near_heavy_07/NO/scale_0.001`, source SHA-256
`f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8`.
`benchmark_card.py` reconstructs scalar parameters with Module1, inserts F and
Ye2's real and imaginary parts, and uses `MODSEL 5 2`. SPheno reader source
explicitly skips imaginary blocks for smaller `i_cpv` values. The first card
attempt failed because the generated `ReadMatrixC` requires a fourth token on
matrix rows; the generator now supplies comments and a trailing block. Full
failed-run log SHA-256
`cdb5df09d9dacfc5a0d9c424e569dcc1c25783ded301e8902534b248d9907b64`.

**PASS (execution, not physics validation).** Reduced executable exit 0,
log reports low-energy calculation and output completion. Input card SHA-256
`9f482fff50757228a2919ea1565f48d034349cb34efb99746bc9dce2dd6499c5`,
spectrum SHA-256
`50100797c1334b25ea5cf5f06bda121fc7801d55448ac9f961e0ff492916f129`,
run log SHA-256
`e08ad7ed9e338f8199e33839fba89474de32485adb9370361b65d513b356fda8`.
F and Ye2 real/imaginary entries in the spectrum reproduce inputs at the
printed eight-digit precision; reconstructed Ye also agrees approximately,
subject to the slightly different lepton input masses and matching scheme.
Tree scalar masses in GeV: h1 125.000000, h2 492.430783, A 493.161317,
H1+ 298.726655, H2+ 532.932913, matching the input at displayed precision.
ZH rows match the reference up to row signs `(+, -)`; ZA `(-, +)` and ZP
`(+, -, -)`. These sign freedoms must also be carried into vertex comparisons.
Charged-scalar complex couplings have not yet been compared explicitly.

**NOT_EVALUATED (complex amplitude convention).** We inserted two print
statements in an ignored copy of generated `LowEnergy_ZeeTypeII.f90` after
FlavorKit's normalization, then rebuilt. Generated K2 coefficients and the
existing D12 coherent *scalar-one-loop subset* (not D12's two-loop-containing
total) are:

| coefficient | SPheno K2(2,1), GeV^-2 | existing C, GeV^-2 |
|---|---:|---:|
| L | -6.13047238e-18 + 7.24847422e-18 i | 6.13036702e-18 + 7.24831411e-18 i |
| R | -4.25909343e-15 + 5.01008588e-15 i | 4.25920181e-15 + 5.01020539e-15 i |

Numerically, `K2 / (-conj(C))` is approximately
`1.00002004 - 0.00000242 i` (L), and
`0.99997548 - 0.00000079 i` (R). This minus-conjugation is an inferred
candidate mapping, not a derived operator/fermion-order convention and not
proof of agreement; it may also depend on external field phases. The existing
operator is `L=e*m_i/2 * bar(l_j) sigma (C_L P_L+C_R P_R) l_i F + h.c.`;
generated FlavorKit uses its own K2 normalization and incoming field order.
The SPheno source's radiative routine includes neutral charged-lepton and
charged-scalar/neutrino vertices, but a diagram-by-diagram and gauge-complete
comparison is outstanding.

Generated `BR(mu->e gamma)=3.46721262e-18`; existing scalar-one-loop subset
is `3.4671398685e-18` (ratio 1.00002098). This numerical rate proximity alone
is not an amplitude validation. Existing full implemented partial value is
`1.3872844851e-10` and includes selected two-loop terms; it is inappropriate
to compare this to SPheno's one-loop number as a failure or success.
Generated three-body and conversion rates are unvalidated and are not being
used as physics evidence.

The instrumented log SHA-256 is
`5254085d370350b343e02acc00d12f8d98735442bb7d6a3cc3ae4a308ca58bac`;
instrumented generated source SHA-256
`ebb12d415ee7fd6690541e670a4936cb42971a5a16cacc190efc9afab5dac071`.
SPheno's calculated W mass 80.348464 GeV differs from the benchmark's
on-shell input 80.379 GeV, and the generated calculation reports Q=160 GeV.
These and the default light-fermion parameters must be matched before a
precision comparison. The full build's one-loop decay failure, the reduced
build options, and coverage limitations are in [REPORT.md](REPORT.md).
