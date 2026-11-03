# D9A physical-rate backend audit

Decision recorded before implementing a new interface (2026-11-03).

| Candidate | Version / source / license | Arbitrary BSM input; basis / order | Complete rate and calibration | Observed blocker / decision |
| --- | --- | --- | --- | --- |
| HyperIso | v1.0.3, `09d26ac6e71d1528922097a896d15693589f636b`, https://github.com/Hyperiso/Hyperiso ; GPL-3.0 | Additive matching patches; native B group through NNLO. SM mode forces BSM=0. Custom groups require explicit running rules. | Native inclusive BR, archived R3 and input cards available. | No public zero-native-BSM B-group factory identified. Custom registration overwrites the named group; identity running is not RG evolution. Existing NLO effective/ordinary concern remains. Do not repeat SM patch-drop/double-count experiments. |
| SuperIso | official v5.0 (November 2025), https://superiso.in2p3.fr/download/superiso_v5.0.tgz ; README GPL-3.0-or-later | Documented `CW_calculator`, `C_calculator_base1`, `bsgamma[_Ecut]`; arbitrary ordinary high-scale arrays and effective low-scale arrays through NNLO. | Full legacy rate, 1.6 GeV default; original source/default inputs available. Manual https://superiso.in2p3.fr/superiso4.1.pdf pp.14–16. | Selected sole executable route: unmodified public C API. Source inspection finds internal high-scale rematching for electromagnetic/power corrections, plus an NLO dipole basis concern. Quantify before accepting any injection. |

No source fork, native-group replacement, subtraction-derived BSM input, or modern-SM rescaling is authorized by this decision. A finite native BR alone will not pass the one-state injection oracle.

## Result: stop at Task B

**D9_PHYSICAL_RATE_BLOCKED**. **D9_ONE_STATE_PHYSICAL_RATE_BLOCKED**;
**D9_TWO_STATE_COHERENT_RATE_BLOCKED**;
**D9_2026_GLOBAL_FLAVOR_FILTER_NOT_READY**. `global_zee_acceptance=null`.
No two-state execution or accepted physical Zee branching ratio is produced.
The obstacle is an executed one-state backend failure, not missing LO matching.
The old HyperIso adapter and all previous calculations remain unchanged.

The sole implemented route is a standalone C client linked against the
**unmodified** official SuperIso v5.0 archive. It reuses the frozen independent
`scripts/zee_module5_bmu_nlo.py` for ordinary NLO matching. No replacement
matching implementation, response fit, or source patch is introduced.
The archive SHA256 is
`7f8400e98ae80deac50af64486b980891e1630d729a0a4660ca309a4d7706b5f`.
All **75 distributed files** are compared byte-for-byte against that archive.
This release is pinned by archive bytes, not an invented Git commit.
The successful build is upstream `make -B` in serial with GCC; an initial
parallel archive build lost members and was rebuilt normally. No compiler or
physics-source workaround is used. All downloads, libraries, executables and
raw outputs are ignored under `validation/module5/local/d9/`.

## Exact executable obstruction

In the original `src/wilson.c`, `CW_calculator` initializes all three matching
arrays to zero at **line 1597**. It evaluates the nonzero charged-Higgs NLO
dipoles, then **lines 2170 and 2174** cap their magnitudes against
`C0w[7]` and `C0w[8]`. These are still zero: the THDM LO assignments occur only
at **lines 2212–2213**. Consequently, the cap multiplies each nonzero NLO
charged-Higgs dipole by zero. C4 is not subject to this cap and survives.
The same issue affects the other dipole caps; this audit quantifies C7/C8 only.
This is an observation about the downloaded release, not a claimed upstream fix.

At M=550 GeV, tanbeta=5.3, the standalone native helper expressions give

```
uncapped C4^(1) = 0.0016355403522413496
uncapped C7^(1) = 1.1651579335639872
uncapped C8^(1) = 0.6131247098535005
native total minus SM C7^(1) = 0 exactly
native total minus SM C8^(1) = 0 exactly
```

The subtraction here is a **diagnostic of native outputs only**. It is never
used to construct a BSM input vector. All ten native mass/Yukawa probes erase
these dipoles. This defeats a complete native NLO/NNLO one-state rate oracle.
The apparently plausible finite BRs below therefore do not establish accuracy.

A second independent obstacle is in `src/bsgamma.c` **line 682**: the public
rate function calls `CW_calculator` again. The resulting high-scale native LO
dipoles feed `Kt0`, `N_E0` (lines 694–696), and the electromagnetic term
`Cem[7]`, `P_em` (lines 703–706). Supplying new low-scale Wilson arrays does
not update these terms consistently. With the *identical supplied arrays* at
550 GeV, tanbeta=5.3, changing just the native model metadata changes the rate
by **6.227462065657038e-7**; the maximum over ten probes is
**1.1443181734875716e-6**. Thus the documented low-scale API alone does not
implement a coherent arbitrary high-scale BSM contribution to the full rate.
The model-independent `deltaC` interface is a low-scale shift in
`interpreter.c`; it does not solve this internal rematching problem.

The uncapped dipole formulas also contain the finite shifts `-4 C4^(1)/9`
and `-C4^(1)/6` relative to our ordinary BMU coefficients, while
`C_calculator_base1`, lines 2250 and 2254, applies those effective-dipole maps
again. The uncapped helpers agree with the independent BMU results after the
explicit inverse conversion across all ten probes. This is a basis concern
requiring an independently certified one-state rate before any proposed repair
could be trusted; deleting the clipping alone would not settle it.

## Fixed inputs and real numbers

All numbers use E_gamma>1.6 GeV in the B rest frame, common matching scale
160 GeV, and mu_b=mb_pole/2=2.393749465308278 GeV. SuperIso defaults are
initialized by its actual `Init_param` and `slha_adjust` routines, without an
external spectrum generator or input fit. Key runtime inputs are:

| Input | Value |
| --- | ---: |
| mt pole / mt(mt), GeV | 172.57 / 162.93425607976874 |
| mt MSbar(160), GeV | 163.16587299291515 |
| alpha_s(MZ) / alpha_s(160) | 0.118 / 0.10877484993481065 |
| mb MSbar(mb) / pole, GeV | 4.183 / 4.787498930616556 |
| mc MSbar(mc), GeV | 1.273 |
| ms input, GeV | 0.0935 |
| MW / MZ, GeV | 80.3692 / 91.188 |
| inverse alpha_em input / rate prefactor | 127.93 / 137.036 |
| measured semileptonic BR | 0.1065 |
| C semileptonic normalization | 0.5734569447384359 |
| CKM ratio squared | 0.9641482620654571 |
| lambda2, GeV squared | 0.12 |

The full fixed inputs, complex CKM entries, HQE parameters, input/output
coefficient vectors, commands, byte hashes and raw-log hashes are in
[`d9_bsgamma_rate.json`](../validation/module5/d9_bsgamma_rate.json).
The rate uses its original kinetic-mass prescription `mb=mb_MSbar+0.37`,
its own `C_BXlnu` parameterization and historical NNLO charm interpolation.
The source has a heuristic that drops its NNLO rate terms when their relative
size exceeds 0.4 (`bsgamma.c:674`); it does not expose the branch as metadata.
We do not certify uniform NNLO accuracy, even apart from the clipping failure.

The native **SM** result is **3.382293066207842e-4** at mu0=160 GeV.
At the upstream default mu0=2 MW it is 3.382457724040796e-4. Independently
running the original `sm.x` prints **3.382e-4**, consistent with its limited
output precision. `sm.c` intentionally returns 1 after successful printing;
the evidence preserves that exit code. This is a second executable path in
the same backend, not a second independent physical calculation.

The following are **raw native outputs with the identified defect**, not
accepted physical Type-II predictions or a validated rate oracle:

| M, GeV | tanbeta | down Yukawa | native BR |
| ---: | ---: | --- | ---: |
| 300 | 5.3 | Type-II | 4.684484544706808e-4 |
| 550 | 5.3 | Type-II | 4.040163792273112e-4 |
| 900 | 5.3 | Type-II | 3.730084991247022e-4 |
| 2000 | 5.3 | Type-II | 3.493041478838059e-4 |
| 100000 | 5.3 | Type-II | 3.382478483759300e-4 |
| 550 | 0.5 | Type-II | 4.325325437306471e-4 |
| 550 | 50 | Type-II | 4.037674917748961e-4 |
| 550 | 5.3 | opposite-ld diagnostic | 2.786738493892079e-4 |

The sign-flipped rows are general-Yukawa controls, **not physical Type-II**.
Both endpoint masses 550 and 900 GeV have been probed independently; the
gamma-dependent two-state calculation is gated off. Decoupling and plausible
sign response do not rescue the NLO oracle failure.

For an additional controlled comparison, both paths have *all* C^(2)
matching inputs set to zero, keeping the same RG/rate function and identical
native metadata. At 550 GeV, tanbeta=5.3:

| Diagnostic | BR-like output |
| --- | ---: |
| native LO+NLO matching arrays | 4.018965773196438e-4 |
| SM arrays + independent ordinary BMU LO+NLO vector, native metadata | 3.909823960458480e-4 |
| same injected arrays, SM metadata | 3.903596498392823e-4 |

The first two differ by -1.091418127379572e-5. These are **diagnostics**:
the engine still retains NNLO evolution/rate kernels and its dynamic fallback,
so they are neither complete NNLO calculations nor strict NLO truncations.
Comparing the native full matching rate with NLO-only injection is explicitly
**NOT_COMPARABLE**. No matching-order difference is treated as a numerical
precision error or absorbed into an uncertainty. In the injection, omitting
only C4 changes the diagnostic rate by 3.535744819594278e-9: its contribution
is carried and measured rather than assumed zero.

## Source scope and statistical stop

Primary sources were downloaded as versioned HTML and hashed, not inferred
from software agreement:

- [BMU hep-ph/9904413v1](https://arxiv.org/html/hep-ph/9904413v1), Sec.2,
  Eqs.(9)–(29), fixes the ordinary Q4/Q7/Q8 matching and the expansion
  C=C^(0)+alpha_s/(4 pi) C^(1), NDR, MSbar top. The existing independent
  implementation is reused at the *backend's* actual running top, not the
  earlier HyperIso reference top.
- [2026 Letter v1](https://arxiv.org/html/2608.29863v1), Eq.(4), remains a
  linearized generic LO NP diagnostic; it explicitly drops quadratic NP
  terms. Its separately published SM (3.54+/-0.14)e-4 and experimental
  (3.49+/-0.19)e-4 values refer to the 1.6-GeV cut. Neither is substituted
  for a backend baseline or turned into a two-state exclusion.
- [2026 companion v1](https://arxiv.org/html/2608.29864v1) includes the
  updated exact-charm dominant NNLO treatment, kinetic/HQE normalization
  and nonperturbative prescription. SuperIso v5.0 predates it; D9 does not
  claim to reproduce that calculation.
- [Misiak–Steinhauser 1702.04571v1](https://arxiv.org/html/1702.04571v1)
  treats R_gamma and one-state mass/statistical prescriptions with older
  inputs. R_gamma includes s+d and semileptonic normalization; it is not
  interchangeable with the branching ratio here.
- [Misiak et al. 2002.01548v2](https://arxiv.org/html/2002.01548v2) quotes
  SM (3.40+/-0.17)e-4 for E0=1.6 GeV with its own parameters and charm
  interpolation. The backend SM is numerically nearby; **NOT_COMPARABLE**
  as a precision oracle without matched inputs. No independent published
  numerical one-state oracle has passed.
- [Benzke et al. 1003.5012v2](https://arxiv.org/html/1003.5012v2) identifies
  nonlocal resolved-photon contributions and historical uncertainty.
  These are not a universal Zee NP error. The backend's nuisance input
  retains `bsgamma_rand=0 +/- 0.04`; no arbitrary NP error or likelihood is
  assigned. The updated 2026 treatment is distinct.

Scope is the real, top-only charged-scalar QCD matching through NLO plus
the SM Q1–Q8 sector. C4 is retained and evolves into the rate. No neutral
tree b-s coupling arises in this Type-II quark sector. The backend's primed
routine returns SM primed dipoles for THDM, so it does not certify Zee
charged-scalar primed effects. Active u/c, finite-ms, down-Yukawa-enhanced
terms, electroweak effects, scalar/tensor operators and additional lepton
effects have no demonstrated numerical bound here. This is not completeness
of the full Zee theory; current theory/experimental covariance and a numerical
accuracy domain remain unestablished. No vacuum, LFV or NuFIT claim follows.

## Reproduction and minimal next action

With the ignored original archive unpacked at
`validation/module5/local/d9/SuperIso_v5.0/` and the six hashed primary
HTML files in `validation/module5/local/d9/`, run:

```bash
python scripts/zee_d9_rate_validate.py --tests
python -m unittest discover -s tests -p 'test_module5_d9_*.py' -v
git diff --check
```

Eight live executable falsifiers pass with zero failures/errors/skips. They
test SM executable agreement; same-input LO mass/Yukawa matching; uncapped
NLO/C4 basis comparison; erased native NLO dipoles and oracle failure;
hidden rematching; C4 rate sensitivity; decoupling/sign response; and repeated
executable precision (maximum repeated difference zero). The validator uses
12 client calls plus one original SM executable; tests independently execute
11 client calls. Numerical tolerances (5e-13 absolute rate, 5e-11 coefficient)
are conservative floating-point bounds, not theory errors. Passing these
regressions records a **falsified physics gate**, not eight physics PASSes.

Minimal next action: reproduce the zeroed NLO dipoles with the supplied
550-GeV client, obtain a source-supported correction to the pre-assignment
cap, and resolve the ordinary/effective C4 mapping against a published rate
oracle. A full-input interface must then use the same coherent high-scale
vector for evolution **and** internal power/electromagnetic corrections.
Only after equal-order native/injected one-state rates pass can Task C run.
No upstream modification, author contact, second backend implementation,
or repair experiment is performed in this bounded attempt.
