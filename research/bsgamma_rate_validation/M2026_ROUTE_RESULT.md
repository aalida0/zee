# Published 2026 NP route — 2026-11-06

**M2026_DIAGNOSTIC_ONLY_AUTHOR_INPUT_REQUIRED. VALIDITY_DOMAIN_UNKNOWN.**
Every point returns `status=DIAGNOSTIC_ONLY`, `classification=UNKNOWN`,
`exclusion=None`, and no NP theory sigma or complete remainder bound.
No confidence test or operative scan filter was created. Modules 0–14,
historical evidence and D14 acceptance logic remain untouched.

## Source and applicability

The current [Letter record](https://arxiv.org/abs/2608.29863) and
[companion record](https://arxiv.org/abs/2608.29864) still list only v1,
30 August 2026. Neither record nor the inspected official KIT entries lists
a journal update. A focused official-domain search found no additional result;
this is a bounded negative finding, not a claim about all possible sources.

The actual versioned [Letter](https://arxiv.org/html/2608.29863v1), PDF p.4,
Sec.IV Eq.(4), gives

```
10^4 BR_linear = (3.54 ± 0.14) - 8.51 DeltaC7 - 2.16 DeltaC8.
```

The paragraph before Eq.(4) specifies matching at **mu0=160 GeV**, NP
**alpha_s^0** coefficients. Immediately afterward it says “quadratic terms”
“have been neglected”; the following discussion distinguishes more refined
operator/NLO matching treatments and the NNLO matching used in its Type-II
analysis. Its 670 GeV limit is not a test of this LO linear equation.

The CP- and isospin-averaged observable has E_gamma>1.6 GeV in the meson
rest frame (p.1/Eq.(1)). Eq.(2), PDF p.2, defines ordinary unprimed
Q7=e mb/(16pi²)(sbar_L sigma b_R)F and
Q8=gs mb/(16pi²)(sbar_L sigma T^a b_R)G.
The existing C1 bridge to cited BMU Eqs.(9)–(11) fixes
H_eff=−4GF/sqrt(2)Vts*Vtb sum C_i Q_i. The Letter does not independently
display this Hamiltonian. **No extra alpha_s/(4pi), sign or finite effective-basis
conversion multiplies its LO DeltaC7/8.** NLO C4/7/8 are not injected.

`m2026_route.py` wraps the unchanged C1 `make_contract`/`run_contract`.
C1 already established the ordinary/sign bridge, coherent matching identities
and 27-point diagnostic; C2 independently checked the frozen BMU matching.
This work adds an audit interface and a finite grid, not new matching or RG.
It uses C1's explicit mt_MSbar(160)=163.96892236746697 GeV, with provenance
retained in the JSON; that reference input was not fitted to the 2026 SM card.
The retained sector is real, top-only and ms=0. Scalar contributions enter
once as cos²gamma*C_i(H1)+sin²gamma*C_i(H2).

## Numerical evidence

The frozen reference (550,900 GeV; tanbeta=5.3; gamma=1.09) is reproduced:

| Quantity | Value |
| --- | ---: |
| DeltaC7_LO | −0.03737804303348145 |
| DeltaC8_LO | −0.04231149396472201 |
| signed C7 contribution to BR | +3.180871462149272e-5 |
| signed C8 contribution to BR | +9.139282696379955e-6 |
| BR_linear_2026 | 3.949479973178727e-4 |

The **72-point** grid covers the requested ordered mass pairs, tanbeta
2/5.3/50 and gamma 0/1.09/pi/2. Its central diagnostic spans
3.724555766777898e-4 to 4.815373073504542e-4;
DeltaC7 spans [−0.12044520,−0.01657639] and DeltaC8
[−0.11591873,−0.02013456]. These sampled ranges are **not** certified
accuracy domains. All 72 points remain UNKNOWN. The tracked D14 pilot
summaries supply point IDs/rates without complete matching input cards;
no D14 points were reconstructed or rerun.

At tanbeta=50 the one-state diagnostic 10^4 BR decreases with mass:
300→4.773856, 550→4.184125, 700→4.018455, 900→3.883985,
1400 GeV→3.724556. This enhancement/decoupling trend is qualitatively
consistent with Letter Fig.3. No attempt is made to reproduce its refined
670 GeV confidence limit. No independent author-supplied numerical
linear-formula test point was located; the reference above is our frozen C1
calculation, not an author benchmark.

For the requested joint legacy diagnostic, five previous zero/axis calls are
reused, four joint sign corners and two held-out points are newly executed.
Both inputs are ordinary high-scale LO NP dipoles at 160 GeV; all NP NLO
matching inputs are zero. mu_b=4.2 GeV and E_gamma>1.6 GeV are common.
Existing EOS 1.0.21 evolution and exact D9B SuperIso 5.0 binaries are reused,
with runtime/binary hashes checked. No backend is rebuilt.

For **10^4 BR = b0+s7*c7+s8*c8+q77*c7²+q78*c7*c8+q88*c8²**:

| Response | b0 | s7 | s8 | q77 | q78 | q88 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Published Eq.(4) | 3.54 | −8.51 | −2.16 | omitted | omitted | omitted |
| EOS diagnostic | 3.222339 | −8.426197 | −2.010068 | 5.669027 | 2.632701 | 0.403327 |
| SuperIso D9B diagnostic | 3.425772 | −9.304048 | −2.129365 | 5.913047 | 2.913880 | 0.409380 |

The symmetric difference step is 0.01 in each high-scale coefficient.
q78 is the polynomial coefficient (twice the symmetric tensor off-diagonal).
The grid is {−0.01,0,+0.01}²; held-out points are (−0.017,+0.023) and
(+0.026,−0.019). Absolute held-out residuals are below 9e-19 in raw BR.
This verifies the measured legacy polynomial, **not** its physical accuracy
or a 2026 remainder. Baselines were neither shifted nor rescaled. EOS uses
its own evolution for these slopes, added once to the preserved common SM
ordinary low vector; the SI-evolved NP vector is not substituted into EOS.

As documented in `FINAL_VALIDATION.md`/`BRIDGE.md`, the implementations
differ in RG details, SM normalization, charm/mass prescriptions, QED,
matrix elements, retained higher-order pieces and hadronic/nonperturbative
prescriptions. Matching scales, cut and selected common inputs do not remove
these differences. Their disagreement is not a theory error or backend failure.
Prior C4/NLO sensitivity remains read-only. C2's reference naive NLO-dipole
increment is −0.07219409 in 10^4 BR, 17.63% of the LO shift; it omits the
consistent C4 response and therefore supplies neither a corrected BR nor a sigma.

## Missing remainder and stop decision

The refreshed [official companion data](https://www.ttp.kit.edu/preprints/2026/ttp26-034)
archive is still 2793 bytes and byte-identical to the C3 inventory. It contains
only README and G27_3P.m, analytic charm O2–O7 interference functions;
it is not a high-scale generic-NP response executable. The Letter's KIT entry
links PDF/arXiv only. Paper license: CC BY 4.0; no independent ancillary
software license was identified. Ancillary code was inspected, not reused.
Current source-byte hashes and qualified findings are in `m2026_sources.json`.

No source-supported finite complete remainder was obtained for joint
quadratic NP, NLO C4/7/8 and truncation, finite-ms/primed/light-quark or
other operators, electroweak/scalar effects, coefficient-dependent resolved
photons, or correlated NP parameter uncertainties. Parametric suppression
alone is not a numerical bound. The companion's low-scale bilinear framework
and SM covariance are available, but the previous reconstruction is not
reopened. No finite accuracy boundary was set or independently certified.

The exact published measurements, (3.54±0.14)e-4 SM and (3.49±0.19)e-4
experiment, are stored separately. The SM sigma does not cover these omitted
Zee contributions. Combining only those two errors cannot justify a Zee
95% confidence test. A central value inside an experimental interval provides
no validity certification. The bounded stop rule is satisfied;
`AUTHOR_QUESTION_DRAFT.md` is prepared and **unsent**. Author response/error
information and independent holdouts are required before reconsidering a filter.

Paper-safe statement: *The published 2026 LO-NP formula is evaluated for
coherent two-charged-scalar matching as a diagnostic only. Its finite Zee
accuracy domain and NP uncertainty remain unknown; no exclusion, full NNLO
Zee accuracy or per-scalar universal mass bound follows.*

## Reproduce and verify

Use the existing Python 3.10 environment and `requirements.lock` setup from
`README.md`/`BRIDGE.md` and frozen-probe setup in `FINAL_VALIDATION.md`.
External binaries/sources stay in ignored `local/`; GPL EOS/SuperIso sources
or binaries are not vendored. The linear adapter itself needs no backend runtime.
The source audit is a frozen human assessment with downloadable URLs/hashes;
later source changes require a new assessment, not automatic promotion.

From the repository root:

```sh
research/bsgamma_rate_validation/local/venv/bin/python research/bsgamma_rate_validation/m2026_legacy.py
research/bsgamma_rate_validation/local/venv/bin/python research/bsgamma_rate_validation/m2026_route.py
research/bsgamma_rate_validation/local/venv/bin/python -m unittest discover -s research/bsgamma_rate_validation -p 'test_m2026_route.py' -v
research/bsgamma_rate_validation/local/venv/bin/python -m unittest discover -s tests -p 'test_module5_bsgamma_2026_linear.py' -v
research/bsgamma_rate_validation/local/venv/bin/python -m unittest discover -s research/bsgamma_rate_validation -p 'test_final_validation.py' -v
research/bsgamma_rate_validation/local/venv/bin/python -m unittest discover -s research/bsgamma_rate_validation -p 'test_bridge.py' -v
research/bsgamma_rate_validation/local/venv/bin/python -m unittest discover -s research/bsgamma_rate_validation -p 'test_pilot.py' -v
git diff --check
```

Eight new focused tests, eleven frozen C1 tests and twenty-two prior
pilot/bridge/final-validation tests pass (41 total). Tests cover signs/units, endpoints,
interchange/equal masses/decoupling, no NLO injection, zero NP, recorded
inputs/hashes, joint response/heldouts and UNKNOWN handling.
