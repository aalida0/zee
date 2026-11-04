# D15 loop-function continuation

The experimental patch now audits all four ratio branches in each of `C1g`
and `C0C1C2`. Installed SARAH and frozen modules remain untouched.

For r=min(mass-squared)/max(mass-squared), with the common inverse larger
mass-squared factored out, define

```
A = (-1+4r-3r²+2r² log r)/(4(r-1)³)
B = (3-4r+r²+2 log r)/(4(r-1)³)
C = (-1+r²-2r log r)/(2(r-1)³)
```

| Arguments | C1g | C0C1C2 |
|---|---:|---:|
| (r,r,1) | B | -B |
| (1,1,r) | A | -A |
| (1,r,r) | B | -C |
| (r,1,1) | A | -C |

Only B diverges at positive r approaching zero. Finite small-r limits A=1/4
and C=1/2 are retained for exact zero; positive inputs now use the analytic
formula rather than prematurely replacing them by these limits. The existing
relative adjacent-mass equality guards remain unchanged. In particular their
0/0 behavior, including the legacy (1,0,0) and (0,0,0) zero placeholders, is
preserved. First/third equality alone and three distinct masses remain
unsupported zero sentinels; **these are not physical zero integrals**.

For d=1-r the stable series are

```
A = sum[n>=0] d^n/((n+1)(n+2)(n+3))
B = sum[n>=0] d^n/(2(n+3))
C = sum[n>=0] d^n/((n+2)(n+3))
```

They follow independently by expanding the denominators in
`A=integral (1-x)^2/(2(1-d x))`, `B=integral x²/(2(1-d x))`,
`C=integral x(1-x)/(1-d x)`, on x in [0,1]. The patch uses Horner
summation through n=18 for d<0.1. The positive tail is bounded by the first
omitted coefficient times d^19/(1-d), below double precision here.
This replaces the quadratic Taylor branch and prevents cancellation near
r=0.999. No epsilon guard elsewhere in the library is removed.

`tests/test_loop_precision.py` compiles both actual corrected functions and
pristine functions from the installed generator. It checks 492 positive
cases, all four supported permutations, scales 1, 125² and 1e-12, ratios
1e-30 through 1e-6, both sides of 1e-10, both sides of the new series switch,
0.9989/0.999/0.9991 and near/exact degeneracy. Seven exact-zero/unsupported
cases retain the original outputs. Independent 80-digit quadratures also
check all three reference expressions. Maximum errors are 5.01e-12 and
2.51e-12; the maxima occur within the retained relative mass equality guard.
`C1g(1,1e-11,1e-11)=11.9142180118346778...`, instead of zero.

Reproduction after generating the reduced backend:

```sh
python3 research/spheno_flavorkit/patch_small_ratio.py research/spheno_flavorkit/local/SPheno-4.0.5/ZeeTypeII/Observables/FlavorKit_LFV_ZeeTypeII.f90
python3 research/spheno_flavorkit/tests/test_loop_precision.py
python3 research/spheno_flavorkit/tests/test_small_ratio.py
```

The patch accepts pristine code or the earlier two-guard experiment, refuses
repeat application, and constructs the entire corrected text before writing.
It remains experimental: other loop functions and unsupported mass orderings
have not been repaired by this work.
