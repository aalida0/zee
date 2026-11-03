# D11B: offline secondary-summary Zee inverse and perturbativity

Executed locally on 2026-11-03, branch `feature/zee-d11b-offline-nufit61`,
starting at `b00f815` (descendant of blocked D11 `28d85e4`). **Both NO and IO
targets close with perturbative Yukawas in both D10 certified spectra.**
This is a bounded algebraic/perturbativity study, with no oscillation likelihood.
The previous blocked D11 evidence and Modules0–5 are unchanged.

## Pinned secondary data and statistical scope

We trust the already committed [secondary snapshot](nufit61_bestfit_ranges_secondary.json),
raw-byte SHA256
`230392a4d77fef5d2e91737569b3e5650cadd47fd13cea6ac396b2f3528f732b`.
No network retrieval or official-site retry was performed. Its origin is the
[Bari comparison table](https://global-nu.org/results.html), section
“Comparison with other global analyses”, NuFIT 6.1 column, recorded as accessed
2026-11-03. Bari describes PCHIP extraction of the original NuFIT v6.1
`v61.release-TByes-NO.txt` and `v61.release-TByes-IO.txt` tables.
This is **secondary reporting**, not newly authenticated primary grids.
The original release is NuFIT 6.1 (Nov 2025), IC24 **with SK atmospheric**;
the underlying analysis reference is [JHEP12(2024)216](https://doi.org/10.1007/JHEP12(2024)216).
The pinned snapshot also cites [arXiv:2610.27270, Table 2](https://arxiv.org/abs/2610.27270)
as an independent rounded-range comparison; it was not substituted for the snapshot
or independently rechecked during this offline execution. Missing primary
hashes remain missing in the unchanged [D11 sources](sources.json).

The exact numbers used below are best-fit-like coordinates, followed by their
**separately profiled one-parameter** 3sigma intervals:

| coordinate | NO | IO |
|---|---|---|
| dm21 / eV² | 0.0000753; [0.0000724, 0.0000782] | 0.0000753; [0.0000724, 0.0000782] |
| sin²theta12 | 0.3081; [0.2893, 0.3295] | 0.308; [0.2892, 0.3295] |
| sin²theta13 | 0.0225; [0.0206, 0.0242] | 0.0226; [0.0209, 0.0244] |
| sin²theta23 | 0.4701; [0.435, 0.5844] | 0.5499; [0.4391, 0.5839] |
| deltaCP / pi | 1.17; [0.7, 2.03] | 1.53; [1.12, 1.86] |
| dm3ell / eV² | +0.0025102; [0.00245, 0.0025764] | −0.0024848; [−0.0025466, −0.0024211] |

The separately extracted coordinates need not be a common multidimensional
minimizer. Their Cartesian interval product is **not a simultaneous 3sigma
region**. Targets carry `NUFIT61_SECONDARY_SUMMARY_BENCHMARK`; endpoint
variations carry `ONE_DIMENSIONAL_MARGINAL_BOUNDS_PROPOSAL`. There is no
chi-square, covariance reconstruction, summed projection, joint acceptance or
ordering preference. Inappropriate likelihood/ordering flags are rejected.

## Exact scalar records and mass conventions

Complete scalar records come unchanged from [D10 inputs](../module1/d10_benchmarks.json).
Their canonical sorted-compact-JSON SHA256 values are checked against both
that snapshot and [D10 vacuum evidence](../validation/module1/d10_vacuum_global.json):

| representative | charged masses / GeV (display precision) | full input SHA256 |
|---|---|---|
| d7_NO_neutral_near_heavy_07 | 298.7266553444879, 532.9329127809378 | `ff0c551534e5051f223c00435293403e3b553f52e0cbec4344287da8b3dce862` |
| F13_heavy_0001330 | 572.2316243593124, 873.2076828282773 | `9117e7af53f9ad5c21f964a7c216de7af5824e903856fed54b9b237c922f4a1d` |

D10's **tree-level** global certificates apply to its specified reconstructed
binary64 potentials and enclosed EW stationary orbits; D11B does not extend
them to quantum stability. P2_beta_shift, F13_heavy_0000981 and
F13_heavy_0001003 remain `D10_UNKNOWN` and are not used as certified spectra.
All seven stored D10 input hashes, including controls, are checked.
The historical `NO` in D7's name imposes no restriction on today's IO target.

PDG `U=V(delta) diag(1,exp(i alpha21/2),exp(i alpha31/2))` gives
`Mnu=U.conj() diag(m) U.conj().T`. Mnu is complex **symmetric**; it generally
is not Hermitian. The independently diagonalized `Mnu† Mnu` is Hermitian.
Mixing inputs are sin²theta, not angles. Delta/pi has period 2: the NO
interval [0.7,2.03] wraps through zero, and 2.03 means 0.03 modulo 2.
Endpoint proposals retain the continuous interval lift before forming phases.

NO masses are `(m0,sqrt(m0²+dm21),sqrt(m0²+dm31))`;
IO masses are `(sqrt(m0²+abs(dm32)-dm21),sqrt(m0²+abs(dm32)),m0)`.
Thus dm21>0, dm31>0 for NO, dm32<0 for IO. Neutrino inputs/outputs are eV;
scalar and charged-lepton loop inputs are GeV. Charged-lepton masses are
`(0.00051099895,0.1056583755,1.77686)` GeV, v=246.21965 GeV.
The existing finite kernel performs the GeV-to-eV conversion.

## Reproducible bounded calculation

[d11b_offline_fit.py](d11b_offline_fit.py) calls the frozen Module2 interface
for actual inverse solutions, four-complex-dimensional homogeneous families,
finite forward masses, Yukawa rotation and observables. No inverse equation
was copied or changed. Reproduce with `python3 -m module11.d11b_offline_fit`.
The tracked [numerical evidence](../validation/module11/d11b_offline_fit.json)
contains all target checks, source/code hashes, exact reference/extreme
witness inputs and four Yukawa matrices, failures and controlled studies.
The deterministic full main-proposal log is ignored at
`validation/module11/local/d11b_trials.jsonl`, with its raw hash in the report.

Each ordering has nine central-summary targets: m0=(0.001,0.01,0.03) eV
crossed with (alpha21,alpha31)=(0,0),(0.7,2.1),(2.3,0.4) radians.
These masses and phases are independent **unmeasured nuisance choices**,
not oscillation fit results or a prior. A further twelve targets independently
move one oscillation coordinate to each interval endpoint, holding all other
coordinates central and using m0=0.01 eV, phases (0.7,2.1).

For each of the 21 targets and each spectrum, eight actual solver inputs vary
complex t with independent real/imaginary uniform proposals in [−2,2], both
roots, all six chart permutations and a uniform overall F phase. Seed is
611103 for NO, 611104 for IO, reset between spectra. The eight F maximum
moduli are `(1e-10,1e-7,1e-5,0.001,0.1,1,4,1e-4)`;
paired coefficient amplitudes are `(0,1e-6,1e-4,0.01,0.1,1,4,10)`.
Each of the four complex coefficients is amplitude times independent
uniform real/imaginary draws in [−1,1], in Module2's orthonormal SVD basis.
This is an explicit proposal design, not a distribution of physical models.
SVD basis orientations can differ between spectra; coefficient-count
differences have no invariant acceptance interpretation.

Additionally, all 84 target/spectrum combinations are solved at a common
orientation: t=0.25+0.1i, root=0, chart=(0,1,2), F phase=0.43 rad,
max|F|=0.001 and four coefficients zero. These isolate nuisance/endpoint
dependence. Fourteen more family inputs per spectrum/ordering separately
vary F scale (zero coefficients), then homogeneous amplitude at F=0.001.
The latter uses the normalized direction `(1+2i,−2+0.5i,0.7−i,−0.3+0.8i)`.
Totals: **672 main + 84 reference + 56 controlled = 812 physics interface
inputs**, plus seven rejection controls. The 168 rejected main inputs also
receive one core-only diagnostic replay each, explicitly never a pass.
No continuous optimization was needed to find feasible solutions. No large
scan, Condor submission or LFV infrastructure work was undertaken.

All 42 distinct targets pass independent Hermitian-eigensystem Takagi checks
(different algorithm from Module2) and oscillation/phase round trips.
Worst independent Takagi relative error is 1.02e-14; mass error <1.31e-16 eV,
sin²theta error <1.98e-14, splitting error <3.91e-18 eV², and phase error
<3.16e-14 rad modulo 2pi, including Majorana phases.

## Actual inverse and perturbativity results

We require the maximum absolute **element across all F,D,Ye,Ye2** to be
strictly less than sqrt(4pi)=3.5449077018110318, and separately compare <1.
These are user-declared perturbativity choices, not experimental limits,
RG tests or bounds on spectral norms. Frozen SARAH physical F is
antisymmetric (F=2 FChen in the archived alternative convention), and

```
S = diag(sqrt(2) ml/v)
D = -sin(beta) Ye + cos(beta) Ye2
Ye = cos(beta) S - sin(beta) D
Ye2 = sin(beta) S + cos(beta) D
Mnu = F W D + (F W D).T
```

| spectrum | ordering | main inputs | closed | all Yukawas <1 | all <sqrt(4pi) | largest accepted relative closure error |
|---|---|---:|---:|---:|---:|---:|
| D7 | NO | 168 | 126 | 66 | 83 | 7.07e-10 |
| F13_1330 | NO | 168 | 126 | 67 | 84 | 7.66e-10 |
| D7 | IO | 168 | 126 | 63 | 84 | 4.00e-10 |
| F13_1330 | IO | 168 | 126 | 63 | 84 | 5.84e-10 |

Counts refer only to these 168 proposed inputs per row; dividing by either
168 or 126 does not produce scan-independent model acceptance. Every target
has at least three main closed solutions satisfying <1. All 84 common
orientation references and all 56 controlled-family inputs close; some
controlled-family inputs intentionally fail perturbativity. Accepted main
systems have rank 5 and complex nullity 4; condition ranges are
14.51–77.26 (NO) and 12.66–1313.46 (IO), combining spectra.
Across accepted main solutions, forward-observable round-trip errors are
at most 8.49e-9 in sin²theta, 2.57e-8 rad in cyclic phases, and
2.27e-12 eV² in splittings. Reference solutions close near machine precision.

At the central summaries, m0=0.01 eV, phases (0.7,2.1), common orientation
and zero homogeneous coefficients, the actual maximum elements are:

| spectrum/ordering | max F | max D | max Ye | max Ye2 | relative closure |
|---|---:|---:|---:|---:|---:|
| D7 NO | 0.001 | 7.04055244e-5 | 0.00680724938 | 0.00760388107 | 2.11e-16 |
| F13_1330 NO | 0.001 | 5.71690375e-5 | 0.00188484880 | 0.01003020347 | 9.34e-16 |
| D7 IO | 0.001 | 8.24581240e-5 | 0.00680909470 | 0.00760222679 | 1.53e-15 |
| F13_1330 IO | 0.001 | 6.69557226e-5 | 0.00188682523 | 0.01002983093 | 1.82e-15 |

For the same F orientation/scale, the heavier spectrum needs approximately
18.8% smaller minimum-norm D. Its finite W=(−1123.217694,−232245.705551,
−3905406.919461) eV, versus D7's (−912.049498,−188582.693998,
−3170758.294615) eV: it has a stronger loop factor despite larger masses,
because the exact splitting and mixing also differ. This is a comparison of
two fixed potentials, not a universal mass-decoupling trend. The different
beta values redistribute D into Ye/Ye2: the heavier point has a larger Ye2
tau-diagonal baseline even while its required D is smaller.

At fixed orientation, the nine mass/phase targets give max D ranges:
D7 NO [6.8334e-5,1.18921e-4], heavy NO [5.5487e-5,9.6563e-5];
D7 IO [8.2458e-5,1.73887e-4], heavy IO [6.6956e-5,1.41195e-4].
Both Majorana phases and absolute mass matter, but none of these choices
obstructs perturbativity. Single-coordinate endpoints change reference max D
most strongly through theta23 for NO (−19.47% at its upper endpoint), and
deltaCP for IO (+9.49% at its lower endpoint); these are path-specific
sensitivities, not confidence intervals on Yukawas. All endpoint references
remain perturbative under <1. The per-target numbers are saved in JSON.

At fixed target/orientation and zero homogeneous coefficients, reciprocal
F/D scaling is explicit: reducing max F from 0.001 to 1e-10 raises max D
to 704.06/571.69 (NO D7/heavy), or 824.58/669.56 (IO), while increasing
F to 4 fails the conventional bound directly. At F=0.001, the controlled
homogeneous amplitude 1 gives max D=0.794/0.705 (NO) and 0.770/0.631
(IO); amplitude 4 gives 3.175/2.820 and 3.080/2.523 respectively, passing
sqrt(4pi) but failing <1. Amplitude 10 exceeds sqrt(4pi) in every case.
Thus small neutrino masses do not force every member of the inverse family
to be perturbative. D dominates the large-family bound; Ye2's diagonal
mass baseline dominates the small-family examples. Off-diagonal flavor
couplings remain unrestricted by this exercise.

## Numerical rejections, limitations and validation

Every main row rejects exactly 42 inputs: F scales 1 and 4 paired with
order-one/four homogeneous coefficients. These are cancellation failures,
not proof that the target is impossible. Core-only replays show family
relative closure errors 6.90e-9–9.70e-7, above Module2's unchanged 2e-9
tolerance, despite rank-five particular solves with condition numbers
13.99–361.21. They remain failures. No naturally rank-singular solution was
observed in this bounded design. Deliberate zero F, zero scalar mixing
(explicit deformation, not a D10 certified point), incompatible fixed F
and enormous homogeneous cancellation are rejected. Three inappropriate
statistical-output flags are also rejected. No tolerance was relaxed.

The unrestricted inverse accommodates every studied NO/IO target. This
demonstrates flexibility on this finite set and agrees with the known
null-cone/four-complex-family construction; it does not establish that all
neutrino targets have perturbative solutions in every scalar potential.
Full correlated LFV (including missing Wgamma/gauge, non-dipole and two-loop
terms), charged-lepton flavor constraints, collider/Higgs, flavor including
modern Bsgamma, RG behavior and quantum vacuum corrections are still needed.
Existing partial LFV signatures were not evaluated here; no complete LFV
exclusion follows. Astrophysical/cosmological mass bounds are **NOT EVALUATED**.
The chosen mass sums span 0.05985–0.11963 eV (NO), 0.09995–0.14571 eV (IO).
No global Zee acceptance, ordering likelihood or paper novelty is claimed.

Executed validation:

- `python3 -m unittest discover -s tests -p 'test_module11_d11b_*.py' -v`: 9 tests PASS.
- `python3 -m unittest discover -s tests -p 'test_module2_*.py' -v`: all 25 unchanged tests PASS.
- `git diff --check`: PASS.

Final classification: `D11B_OFFLINE_SECONDARY_BESTFIT_INVERSE_NO_PASS`,
`D11B_OFFLINE_SECONDARY_BESTFIT_INVERSE_IO_PASS`,
`D11B_PERTURBATIVITY_CONDITIONAL`, `D11_OFFICIAL_PROFILE_DATA_UNAVAILABLE`,
`D11_FULL_JOINT_LIKELIHOOD_NOT_AVAILABLE`; `global_zee_acceptance=null`,
`COMPLETE_LFV=false`, `Wgamma=BLOCKED`. Stop after this small study.
