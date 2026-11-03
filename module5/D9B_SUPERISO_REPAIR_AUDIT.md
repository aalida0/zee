# D9B SuperIso local repair — 2026-11-03

**The two demonstrated source defects are repaired for the tested real, top-only
charged-scalar Q1–Q8 sector at NLO QCD.** The outcome is
`INTERNAL_CONSISTENCY_PASS`, with `D9B_MATCHING_BASIS_PASS`,
`D9B_FULL_RATE_DATAFLOW_PASS`, `D9B_ONE_STATE_RATE_PASS` and
`D9B_TWO_STATE_RATE_PASS` at that explicitly limited order.
This is a **legacy SuperIso v5.0 backend-conditional rate**, with its original
EM/power/semileptonic prescription. Independent numerical physical-rate accuracy
is **NOT_CERTIFIED**: no second calculation with matched inputs and cut passed.
The PASS labels certify the executed matching and consistent rate bridge; they
are not NNLO, a complete Zee likelihood, an exclusion or global viability.
`global_zee_acceptance=null`; `2026_GLOBAL_FLAVOR_FILTER_READY=false`.

## Preserved provenance and Gate 0

Branch `feature/zee-d9b-superiso-matched-rate` starts at user task commit
`c965e91a2bdcc64b87ba45d0af9058994a124e87`, whose direct parent is exact D9A
`5cea65b5a6a90721cb5742e0e71b8d528cfb2341` (ancestry checked).
No previous Module5 code/evidence or other modules were edited. No remote compute
or scan was used. Original D9 artifacts were copied read-only into ignored local
storage; the D9A workspace was not modified.

The freshly linked unmodified witness reproduces the complete archived 550-GeV
output exactly: native NP NLO C7=C8=0; uncapped effective NLO dipoles
1.1651579335639872 and 0.6131247098535005; identical injected low-scale arrays
change BR by 6.227462065657038e-7 when only THDM metadata changes.
The original full SM rate is 3.382293066207842e-4. All eight unchanged D9A live
regressions pass before patched execution. The runner refuses a different witness
or library hash and authenticates all 75 distributed original files.

The complete original archive is preserved untouched, both at its original path
and as `validation/module5/local/d9b/superiso_v5.0.tgz`:

`7f8400e98ae80deac50af64486b980891e1630d729a0a4660ca309a4d7706b5f`.

The clearly named ignored fork is
`validation/module5/local/d9b/SuperIso_v5.0_D9B_patched/`.
The tracked [full unified patch](patches/d9b_superiso_v5.0.patch) has SHA256
`d0607f3e9dd12bc0e2fce6c0102c5c6e756d1d9d9767b2444bca3abee890e62b`.
Every distributed fork file is compared byte-for-byte to an independent replay
of archive + patch, and reverse application is dry-run checked. Only these
three distributed files change; all original/fork hashes are in the JSON:

| Forked source | SHA256 |
| --- | --- |
| `SuperIso_v5.0/src/bsgamma.c` | `d2aec1481760f7ebdba4180ad6fe54e926edbde184571ee4be92ff211bc01538` |
| `SuperIso_v5.0/src/include.h` | `c0e53a1b4a45056dd2f892fd7a85b586cc491d1fc79b1b8a44689f16e7690feb` |
| `SuperIso_v5.0/src/wilson.c` | `9a97bccc865bee3e1b494d998b6536e6a6068da17c8945bdc725c3af7f8c7ce3` |

The patch contains original upstream tabs/trailing spaces and CRLF context from
`bsgamma.c`. The narrowly scoped `patches/.gitattributes` preserves those bytes
and exempts this embedded diff from whitespace lint; runner/tests retain normal
whitespace checks. No upstream whitespace normalization is hidden in the patch.

## Gate 1: charge, ordinary/effective basis and retained caps

The frozen [Module5 convention](BSGAMMA_2026_CONVENTION.md) fixes
`L_Y=+sqrt(2)/v H+ bar u V (mt Y PL+mb X PR)d+h.c.`,
`H_eff=-4 GF/sqrt(2) Vts*Vtb sum C_i Q_i`,
`Q7=e mb/(16 pi²) (bar s_L sigma b_R)F` and analogous `Q8` with gs and T^a.
In [BMU hep-ph/9904413v1](https://arxiv.org/html/hep-ph/9904413v1),
Eqs.(4),(13)–(29), the internal fermion is t, scalar phi is H−:
`Qpsi=2/3`, `Qphi=-1`, color Casimirs `4/3,0`, and xi=1.
For real Type-II `X=tanβ`, `Y=cotβ`, the products are
`N R1=x cot²β/2`, `N R2=x/2`, `x=mt_MSbar(mu0)²/M²`.
SuperIso uses `lu=cotβ`, `ld=-tanβ`; its `-lu*ld` is therefore positive.
Reversing ld is a diagnostic Yukawa choice, not physical Type-II.

We reuse the independent, frozen 70-digit BMU evaluator
[`zee_module5_bmu_nlo.py`](../scripts/zee_module5_bmu_nlo.py), with its full
fixed-product derivative prescription. No helper from the fork constructs the
injected coefficients. It supplies ordinary ΔC7/8^(0), ΔC4/7/8^(1);
all other NP Q1–Q8 entries vanish at this order.

[Borzumati–Greub hep-ph/9802391v1](https://arxiv.org/html/hep-ph/9802391v1),
Eq.(13), Appendix A4, and [SuperIso manual](https://superiso.in2p3.fr/superiso4.1.pdf)
Eq.(343), distinguish ordinary from effective dipoles:

```
C7eff = C7 - C3/3 - 4 C4/9 - 20 C5/3 - 80 C6/9
C8eff = C8 + C3 - C4/6 + 20 C5 - 10 C6/3
C = C^(0) + a_s C^(1) + a_s² C^(2), a_s=alpha_s/(4 pi)
```

At NP NLO only C4 among Q1–Q6 is nonzero. Original native
`G7H+Delta7H L-4 EH/9`, `G8H+Delta8H L-EH/6` are effective matching,
whereas `C_calculator_base1` expects ordinary matching and applies those maps.
The patch removes the two charged-Higgs finite shifts at their definition,
restoring ordinary BMU coefficients; evolution applies the map **once**.
It does not change SM matching or remove C4. This is certified numerically for
all eight ordinary coefficients, not just a fitted dipole rate.

The LO assignment block moves ahead of the existing convergence caps. Those
caps compare `|a_s C_NP^(1)|` with `|C_total^(0)|`: their mathematical role is a
heuristic perturbative-size limiter, not an EFT matching identity or proof of
accuracy. Previously the reference was still its zero-initialized array value.
Every cap is retained. The C7/C8 caps are inactive at every validated point,
including the sign control. No physical prediction is certified where a cap
changes a coefficient. The reorder also affects other native model branches;
SUSY and semileptonic C9/C10 are outside this validation.

The exact matching inputs are mu0=160 GeV, mt(mu0)=163.16587299291515 GeV,
alpha_s(mu0)=0.10877484993481065, hence a_s=0.0086560275256021228.
The full ordinary NP vectors have zero entries except:

| M, GeV | ΔC7^(0) | ΔC8^(0) | ΔC4^(1) | ΔC7^(1) | ΔC8^(1) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 550 | -0.05924467746457921 | -0.06413402661914894 | 0.00163554035224135 | 1.165884840387206 | 0.6133972999122068 |
| 900 | -0.03111938141710166 | -0.0360581723090789 | 0.0009066055940462791 | 0.7614882690327276 | 0.4574057334128651 |

At 550 GeV the actual a_s-weighted NLO increments are
(1.4157282308234114e-5, 0.010091931270073889, 0.005309583912170083)
for (C4,C7,C8). No extra alpha_s factor is inserted.
The maximum full-vector residual over eleven one-state controls is
6.661338147750939e-16. A native THDM with both Yukawa couplings zero reproduces
all eight SM LO/NLO coefficients and the supported SM rate exactly.
The JSON also retains C9/C10 outputs, which the rate never reads and for which
this BMU Q1–Q8 comparison makes no claim.

## Gate 2: one explicit matching object and controlled perturbative order

`struct d9b_matching` contains complete C^(0), C^(1), C^(2) arrays, matching
scale, ordinary-NDR/MSbar-top scheme tag, requested order and a primed vector
(which must vanish in the supported scope). `d9b_bsgamma` passes those same
arrays to `C_calculator_base1` and `bsgamma_Ecut_core`. No global callback,
model-subtraction input, second model match or state BR addition is used.

The exact dependencies are:

- `CW_calculator` supplies ordinary native LO/NLO Q1–Q8 after the patch.
  Its native NNLO arrays retain upstream formulas and remain uncertified.
- `C_calculator_base1`, fork lines 2256–2263, applies the full finite maps
  separately at LO/NLO/NNLO; it then uses U0/U1/U2. In particular
  `C1b=eta[U0 C1w_eff+U1 C0w_eff]`, eta=alpha_s(mu0)/alpha_s(mu_b).
  C2w does not feed C0b or C1b. Low-scale dipoles are effective.
- `bsgamma_Ecut_core`, lines 681–686, reads the provided high-scale vectors
  instead of calling `CW_calculator` on the explicit-input path. The only
  high-scale rate reads are C0w7/8 in `Kt0 -> N_E0` and `Cem7 -> P_em`.
  NLO/NNLO matching arrays enter through evolution; the retained leading power
  and leading EM terms require LO matching, not new arbitrary higher-order terms.
- `alphas_running`, `running_mass`, `C_BXlnu` and the phi/r matrix-element helpers
  use the common SM/hadronic inputs; they do not rematch THDM coefficients.
  Kc0/Cem2 assume LO current-current C2=1 and C1,C3–6=0. The API rejects other
  LO four-quark vectors, complex coefficients, nonzero primed input or a different
  scheme. It is not a general arbitrary-operator EFT backend.

The original `bsgamma_Ecut`/`bsgamma` entry points and native-rematching policy
are retained as wrappers of the same otherwise unchanged legacy kernel, and
are exercised side-by-side. The unmodified implementation also remains in the
complete archive and untouched D9 source copy. At full native matching their
BR equals the explicit-input order=2 diagnostic exactly at every point.

For **order=1**, P=P0+a_b(P11+P12), with a_b=alpha_s(mu_b)/(4 pi);
all a_b² P2 terms are explicitly removed. It is not sufficient just to set the
NNLO matching arrays to zero. Both compared paths use zero C^(2) matching and
exactly this NLO numerator. The historical C_BXlnu normalization, alpha_s/mass
running, leading EM and power terms remain the backend prescription. Therefore
we claim NLO QCD matching/evolution/numerator with those explicit conventions,
not a newly derived uniformly truncated QCD+QED/HQE calculation.

C^(2) here denotes perturbative NNLO matching, not operator Q2: Q2^(0)=1 is
retained. No NP NNLO matching is needed for the accepted NLO calculation.
The native NP NNLO basis and missing higher operators have **not** passed an
independent test, so no NNLO physical rate is accepted or combined in two states.
The SM primed contribution used in D9A is consistently omitted here, along with
NP primed matching. The original nonzero ms is retained as the phi88 collinear
regulator. This reduced-sector SM baseline is separately labeled.

The legacy heuristic drops P2 when its relative impact exceeds 0.4. All eleven
native order=2 diagnostics have ratios between −0.048468 and −0.042615 and keep
P2; their finite BRs are **diagnostics only**. A deliberately artificial
C7^(2)+=1e5 gives ratio −19.722394811503086 at 550 GeV, activates the original
fallback, gives P2=0 and reproduces the explicit NLO rate exactly. This tests the
branch without treating clipping as physics. At order=1 P2 is always zero,
independently of that heuristic; `nnlo_dropped` reports the heuristic alone.

Identical matching vectors with SM/THDM metadata give exactly identical BR,
P0, P1, P2, P_em and N_E0. At 550 GeV, adding +0.01 to high-scale C7^(0)
changes P0, P_em and N_E0, and changes BR to 4.012195833829323e-4.
Omitting C4 changes BR by 5.169330721344154e-9; double-applying its effective
map changes BR by 7.3441328953e-9; adding an extra a_s to the NP NLO matching
gives 4.225711224663187e-4. These executed falsifiers reject the old hybrid,
dipole-only and extra-alpha_s paths.

## Gates 3–4: actual rates and numerical residuals

E_gamma>1.6 GeV; mu_b=2.393749465308278 GeV. All SM/hadronic inputs are the
backend's own D9A defaults, retained in the JSON. At mu0=160 GeV, the supported
unprimed **NLO-numerator SM baseline is 3.5427236527176535e-04**.
Its proximity to the 2026 SM number is coincidental: no rescaling or input fit
is performed. The original D9A full legacy SM number remains unchanged.

The native column below means corrected native ordinary matching followed by
the explicit NLO rate path. Injection means SM + independent ordinary BMU
matching, with the identical order, RG, internal matching, normalization and cut.
Residual = injected BR − native BR. Roundoff bounds are 5e-11 for matching and
5e-13 for rates; they are implementation tolerances, not theory uncertainties.

| M, GeV | tanβ | Yukawa | Native NLO BR | Absolute residual | Relative residual |
| ---: | ---: | --- | ---: | ---: | ---: |
| 550 | 5.3 | Type-II | 4.1053057979897618e-04 | 5.421e-20 | 1.320e-16 |
| 900 | 5.3 | Type-II | 3.8226733278886292e-04 | 0.000e+00 | 0.000e+00 |
| 2000 | 5.3 | Type-II | 3.6205017435766952e-04 | 0.000e+00 | 0.000e+00 |
| 10000 | 5.3 | Type-II | 3.5466959976022288e-04 | 0.000e+00 | 0.000e+00 |
| 100000 | 5.3 | Type-II | 3.5427496749916695e-04 | 0.000e+00 | 0.000e+00 |
| 550 | 2 | Type-II | 4.1199049065457572e-04 | 0.000e+00 | 0.000e+00 |
| 900 | 2 | Type-II | 3.8286789238246806e-04 | 0.000e+00 | 0.000e+00 |
| 2000 | 2 | Type-II | 3.6218179471266362e-04 | 0.000e+00 | 0.000e+00 |
| 10000 | 2 | Type-II | 3.5467524884439885e-04 | 0.000e+00 | 0.000e+00 |
| 100000 | 2 | Type-II | 3.5427502838430080e-04 | 0.000e+00 | 0.000e+00 |
| 550 | 5.3 | opposite-ld control | 3.0232315739104720e-04 | 0.000e+00 | 0.000e+00 |

Maximum rate residual is 5.421010862427522e-20, relative 1.3204889304670117e-16.
The 2–100 TeV points test decoupling, not high-mass precision: integrating all
heavy particles out at one weak scale leaves large logarithms at extreme masses.
The secondary tanβ=2 and opposite-ld control test coupling dependence.
No independent published numerical one-state rate at these exact inputs has
been reproduced. BG supplies an independent matching/basis reference, not a
second rate execution. The result is explicitly `INTERNAL_CONSISTENCY_PASS`.

Only after those executed one-state gates passed was the two-state vector
formed. Module5 `bsgamma_lo.py:67–76` and the native convention above give
`a=(cos gamma,-sin gamma)`. Both |Y|² and XY* are proportional to a², so the
orientation is **cos²gamma for m1, sin²gamma for m2**, including C4^(1).
The ordinary vectors are weighted coherently and injected once. NNLO NP is not
invented. The rate retains interference and NP squares at its stated NLO order.

The example uses m1=550 GeV, m2=900 GeV, gamma=1.09, tanβ=5.3:

| Control | NLO BR |
| --- | ---: |
| decoupled | 3.5427496749916695e-04 |
| equal_masses | 4.1053057979897623e-04 |
| example | 3.8822991154838086e-04 |
| gamma_half_pi | 3.8226733278886292e-04 |
| gamma_zero | 4.1053057979897623e-04 |
| interchanged | 3.8822991154838086e-04 |
| mu0_120 | 3.8808081606364679e-04 |
| mu0_200 | 3.8779332906608774e-04 |
| opposite_ld | 3.2196627408443470e-04 |

All endpoint/equal-mass/interchange BR residuals are exactly zero in this run.
At the example the coherent rate differs from the weighted average of one-state
BRs by −8.272386614453266e-8, explicitly falsifying addition of state rates.
Scale controls recompute the running top and all BMU matching at 120/200 GeV;
they are sensitivity checks, not an assigned uncertainty envelope. The
opposite-ld rows are sign controls, not Type-II physical points.

## Reproduction, checks, scope and sharing

Host: `Linux-6.8.0-138-generic-x86_64-with-glibc2.35`. Compiler: `gcc (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0`.
The fork is built serially with `make -B`, upstream flags
`-O3 -pipe -fomit-frame-pointer -DVERSION=\"v5.0\" -DYEAR=2025`, no OpenMP,
GNU ar `rcsU`. Client: GCC `-O2 -I <fork>/src <probe.c> <libsuperiso.a> -lm`.
Exact commands, flags, full vectors, source/library/binary/log SHA256 checksums
and primary reference pointers are in
[`d9b_superiso_repair.json`](../validation/module5/d9b_superiso_repair.json).
The build retains upstream warnings; no warning-suppression or source workaround
is used. Archive member timestamps make the static library hash specific to the
recorded build; source replay and numerical reproducibility are checked directly.

With the original D9 artifacts copied into ignored `validation/module5/local/d9/`,
run locally:

```bash
python scripts/zee_d9b_rate_validate.py --tests
python -m unittest discover -s tests -p 'test_module5_d9b_*.py' -v
python -m unittest discover -s tests -p 'test_module5_d9_*.py' -v
git diff --check
git diff --cached --check
```

The runner creates the fork by unpacking the pinned archive and applying the
tracked patch if it is absent; existing sources must match a complete replay.
`--skip-build` reuses an already built fork. It never rewrites D9A JSON.
Nine new tests pass (zero failures/errors/skips), executing 21 patched client
calls. All eight unchanged D9A tests pass (11 unmodified client calls).
The recorded validator run separately executes 23 patched calls and one newly
linked unmodified witness. No fabricated fixtures or physics test counts are
used. The JSON stores the actual unittest report checksum and counts.

Unresolved accuracy work: no matched independent rate oracle, no certification
of native NP NNLO matching/effective basis, no source-matched uncertainty model
or covariance, and no numerical bounds on active u/c, finite-ms or primed
matching, enhanced down-Yukawa, electroweak, scalar/tensor or extra Zee lepton
operators. The retained SM matrix-element ms regulator does not bound omitted
NP terms. These limit interpretation and prohibit a global flavor filter or a
670-GeV exclusion; no claim is made for LFV, NuFIT, vacuum or global viability.
A modern 2026 calculation would require its actual kernels/inputs and independent
validation, not normalization of these numbers to 3.54e-4.

The upstream README licenses SuperIso under **GPL-3.0-or-later**. This is a
clearly marked investigative local fork, not an upstream-certified correction.
The modifications/patch are shared under that license. If distributing the
fork or binaries, preserve notices/license and change/date notices and provide
the complete corresponding source (original source **plus** modifications and
build material) under GPL terms. A binary accompanied only by this patch is not
a substitute for the required complete corresponding source. The complete
original archive remains available locally and is never replaced by the patch.
