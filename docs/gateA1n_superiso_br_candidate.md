# Gate A1N — SuperIso v5 inclusive BR candidate and Type-II controls

**Purpose:** quantify how the confirmed SuperIso v5.0 charged-Higgs
NLO clipping defect affects **candidate** inclusive (B\to X_s\gamma)
calculations, then validate the actual SM and Type-II limits before any
Zee exclusion. **No allowed/excluded decision is made in this gate.**

Preceding validated work:
- Gate A1J: official SuperIso 5.0 `./sm.x` gives
  `BR(b->s gamma)=3.382e-04` for (E_\gamma>1.6\) GeV.
- Gate A1L: entire matched Zee Wilson-coefficient vector closes
  exactly at gamma 0, pi/2 and 1.089; original native C7/C8 NLO
  charged contributions are incorrectly zeroed.
- Gate A1M: in a separate **version-hash-pinned** SuperIso copy,
  removal of exactly four NLO limiter statements restores
  \(\Delta C_7^{(1)}(300)=1.7331863494\),
  \(\Delta C_7^{(1)}(700)=0.9519167622\),
  \(\Delta C_8^{(1)}(300)=0.7628644096\),
  \(\Delta C_8^{(1)}(700)=0.5332732317\).
  All SM, LO, NNLO and unrelated NLO matching entries remain unchanged.

## AF commands

Use the **existing**, successfully built Gate A1M isolated library.
No source modifications, new patch, or installation are made here.

```bash
cd /home/aalida/zee
git fetch origin gateA1n-superiso-br-candidate-controls
git switch gateA1n-superiso-br-candidate-controls

python3 -m unittest discover -s tests \
  -p 'test_gateA1n_br_candidate_controls.py' -v

bash scripts/gateA1n_run_br_candidate.sh \
  /home/aalida/opt/zee_tools/SuperIso_v5.0 \
  /home/aalida/zee/work/gateA1m_isolated_nlo_v1/isolated_superiso \
  work/gateA1n_br_candidate

cat work/gateA1n_br_candidate/result.json
```

The runner confirms A1M source-hash provenance; it separately links
the external C driver to the official and isolated libraries, then
calls the complete SuperIso workflow at the same scale:

```text
CW_calculator(2, C0w, C1w, C2w, muW, &param)
    -> coherent mixing of matched SM+H1+H2 coefficient vectors
    -> C_calculator_base1(...)  [QCD evolution]
    -> Cprime_calculator(...)   [stock SuperIso convention]
    -> bsgamma(...)             [Egamma>1.6 GeV]
```

The frozen input is beta=1.394 rad, gamma=1.089 rad,
mH1=300 GeV, mH2=700 GeV and Type-II quark couplings
lambda_u=cot(beta), lambda_d=-tan(beta).
The 2HDM matching flag `THDM_model=2` is a path selector,
NOT a native Zee-model implementation.

Checks run for the official/unmodified and isolated libraries:
- SM inclusive BR equals Gate A1J `sm_output.log` to rounding tolerance.
- Source-only NLO repair leaves the SM rate unchanged for all
  five tested (muW,mub) combinations.
- Direct pure-Type-II 300/700/1000/2000 GeV controls.
- Explicit gamma=0 and gamma=pi/2 BR endpoints agree with the
  corresponding one-charged Type-II rates.
- The two-state candidate rate is computed only **after**
  matching coefficients are added *before* RG and BR.
- `muW`: nominal 2*mW, half, double.
- `mub`: nominal mb_pole/2, ×0.8, ×1.5 (avoid excessive
  strong coupling in sub-GeV-scale comparisons).
- Original-vs-isolated flavour effects and the approach of
  the 2000-GeV Type-II result to the SM are reported.

**Validation stops** if the SM driver fails baseline closure,
a matching endpoint fails, the original/isolated SM differs,
unexpected primed coefficients appear, or the BR is nonfinite.

The resulting `BR` values are explicitly **CANDIDATES**. Do not
call the benchmark excluded/allowed or use them for publication,
even if the output passes. A pure Type-II numerical *control* is
not an independent reference calculation.

## AF runtime diagnostic: nonfinite TYPEII_300 (October 2026)

The first AF integration run passed all six synthetic tests and
verified the A1M source hashes. Its independent SM prediction was
`3.38246e-4`, reproducing official `sm.x` to printed precision.
The Type-II 300 GeV BR then returned NaN. **This was not a physics
exclusion**.

Code review identified a driver parameter-propagation defect:
`run_typeII()` sets `mass_H=300` (or another mass) in a local
matching parameter structure, but the original `evaluate()`
used a fresh copy with **mass_H=0** when invoking
`C_calculator_base1`, `Cprime_calculator` and `bsgamma`.
The revised driver restores the corresponding charged mass in
the low-scale parameter context. The failure was not traced
all the way to its originating elementary operation; a new AF
run is therefore needed to determine whether this is sufficient.

The revised driver also:
- checks low-scale Wilson coefficients explicitly for nonfinite
  numbers before running the BR calculation and prints affected
  order, index, scale and residual charged mass;
- evaluates the **same** Zee Wilson vector twice, first with a
  residual `mass_H=300`, then with `mass_H=700`. If the results or
  chirality-flipped coefficients depend on this arbitrary single
  mass, the candidate is **blocked** until all such dependence is
  mapped to the actual two-state model;
- preserves the SM and original-vs-isolated comparisons.

**Do not paper over NaN**, force `Cprime=0`, or silently
replace the Type-II mass with an arbitrary value. If the
updated code still fails, capture
`work/gateA1n_br_candidate/vendor.txt` plus the terminal
error and inspect `bsgamma_Ecut` in the installed SuperIso.

## AF residual-mass blocker: matched Zee vector is not sufficient

An updated AF run (October 2026) completed every candidate BR. The
strict validator properly rejected the two-state Zee prediction:
the **identical** matched high-scale Zee Wilson-coefficient vector
gave different inclusive BRs depending on whether the remaining
`point.mass_H` was assigned 300 or 700 GeV:

```text
vendor, nominal:
residual mass_H 300: 4.04149861020259e-4
residual mass_H 700: 4.034169165308966e-4
relative difference: about 0.181 percent
```

The printed `C7prime` and `C8prime` values were the same,
so the origin must be traced. **Neither is a physical Zee rate
or an exclusion.** Do not choose either residual mass or
replace the two Higgses with an effective mass.

Revised Gate A1N performs stage-by-stage debugging without
altering any physics formula:

- It prints **all** complex Wilson coefficients at `mu_b`
  from `C_calculator_base1` for both Zee residual mass contexts.
- It prints the complete primed vector from `Cprime_calculator`
  for both.
- The new `gateA1n_trace_mass_context.py` reports whether
  the first difference arises in evolved coefficients, primed
  coefficients, or the `bsgamma` call/its parameter structure,
  and inventories exact `mass_H`/`THDM_model` references in
  the installed `src/bsgamma.c` and `src/wilson.c` with SHA256.
- It writes `mass_context_diagnostic.json` **before** the strict
  candidate validation.
- The validator still **exits nonzero** and writes an explicit
  `result.json` with `BR_CANDIDATE_BLOCKED_VALIDATION_FAILURE`
  if any essential condition fails.

```bash
cd /home/aalida/zee
git switch gateA1n-superiso-br-candidate-controls
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_gateA1n_br_candidate_controls.py' -v
bash scripts/gateA1n_run_br_candidate.sh \
  /home/aalida/opt/zee_tools/SuperIso_v5.0 \
  /home/aalida/zee/work/gateA1m_isolated_nlo_v1/isolated_superiso \
  work/gateA1n_br_candidate
cat work/gateA1n_br_candidate/mass_context_diagnostic.json
cat work/gateA1n_br_candidate/result.json
```

The key immediate question is whether `mass_H` appears in
`bsgamma_Ecut` outside the Wilson-vector interface (for example,
as a power-suppressed term). If so, it is **model-dependent** and
must be generalized coherently to both charged scalar masses or
excluded only with an explicit justified approximation. The
current source excerpt is not sufficient to assert which.

## A1N source-log evidence: post-RG drift is not yet identified as physics

In the user's uploaded A1N stage report:

- Native SuperIso: max differences in **post-RG** Wilson vectors 4.0925351;
  isolated version: 4.1108845, at nominal scales.
- Complete primed Wilson vectors have maximum difference **exactly 0**.
- The same nominal residual context BR difference, 7.32944489e-7,
  occurs in both native and isolated libraries (~0.18%).
- The automatic direct-token search found zero occurrences of
  `mass_H` or `THDM_model` in `src/bsgamma.c`, and the reported
  `src/wilson.c` occurrences of `mass_H` lie outside
  `C_calculator_base1`; neither fact rules out indirect dependencies.

**Correction to previous interpretation:** the current diagnostic says
only that two *sequential evaluations* produce different evolved
vectors. It cannot yet show that the difference is caused by
`mass_H`; mutable high-scale arrays or hidden per-call state would
produce the same observation.

The latest A1N update explicitly copies `C0w,C1w,C2w` to local,
mutable buffers before calling `C_calculator_base1` (no cast of
shared `const` memory), measures modifications to those buffers,
runs independent repeat cases with the **same mass** in the same
process, and reports the operator index and perturbative order of the
largest returned RGE mismatch.

Use the unchanged strict validation criteria and run on AF:

```bash
cd /home/aalida/zee
git switch gateA1n-superiso-br-candidate-controls
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_gateA1n_br_candidate_controls.py' -v
bash scripts/gateA1n_run_br_candidate.sh \
  /home/aalida/opt/zee_tools/SuperIso_v5.0 \
  /home/aalida/zee/work/gateA1m_isolated_nlo_v1/isolated_superiso \
  work/gateA1n_br_candidate
python3 - <<'PY'
import json
r=json.load(open("work/gateA1n_br_candidate/mass_context_diagnostic.json"))
for name,lib in r["libraries"].items():
    print(name,lib["stage_diagnosis"])
    print(json.dumps(lib["scales"][0],indent=2))
PY
cat work/gateA1n_br_candidate/result.json
```

If the same-mass repeat changes, **do not** infer a physical
mass-dependent anomalous dimension. Investigate array mutation,
uninitialized variables and call order first. If repeat closures
pass but two mass choices still yield distinct evolved WCs,
audit explicit and indirect parameter dependencies in
`C_calculator_base1` and child functions before changing any physics.

## AF result: defensive evolution buffers fixed the apparent RG difference

The AF experiment with independent, mutable input buffers for
`C_calculator_base1` demonstrated that earlier large differences
between evolved Wilson vectors were **aliasing/call-order artefacts**:

- Native and isolated libraries: all 30 evolved Wilson entries
  agree between both charged-mass contexts to machine precision.
- Every primed Wilson coefficient agrees.
- Each identical-mass repeated call gives exactly the same BR.
- The vendor mutates its incoming high-scale coefficient buffers;
  maximum change is about 10.46/10.50 for the two library builds.
  This behavior requires private input copies to keep matched
  Zee Wilson data invariant across evaluations.
- A **0.18%** candidate BR residual remains, independently of the
  NLO bugfix, **even when final evolved and primed Wilson vectors
  agree**.
- The previous automated largest-difference location
  (index=10,order=2,imaginary) had no meaning with a maximum
  difference of zero; new reports give `null` in that case.

The next diagnostic is a controlled isolated replay of `bsgamma`
with identical snapshots of the evolved and primed Wilson-coefficient
arrays, identical full parameter context except for explicitly
switching `point.mass_H=300` or `700` GeV. Separate copies are
supplied each time to prevent mutation contamination.

```bash
cd /home/aalida/zee
git switch gateA1n-superiso-br-candidate-controls
git pull --ff-only
python3 -m unittest discover -s tests \
  -p 'test_gateA1n_br_candidate_controls.py' -v
bash scripts/gateA1n_run_br_candidate.sh \
  /home/aalida/opt/zee_tools/SuperIso_v5.0 \
  /home/aalida/zee/work/gateA1m_isolated_nlo_v1/isolated_superiso \
  work/gateA1n_br_candidate
python3 - <<'PY'
import json
p="work/gateA1n_br_candidate/mass_context_diagnostic.json"
r=json.load(open(p))
for name,entry in r["libraries"].items():
  row=entry["scales"][0]
  print(name,entry["stage_diagnosis"])
  print("fixed-WC bsgamma 300/700:",
        row["bsgamma_clone_with_original_mass300"])
  print("max BR replay discrepancy:",
        row["max_original_vs_replayed_bsgamma_same_mass_difference"])
PY
```

**Interpretation:**

- If switching only `mass_H` inside `bsgamma` with frozen inputs
  reproduces the BR difference, inspect its **indirect** helper calls
  and mass-dependent `struct parameters` access; the absence of
  literal `mass_H` in `src/bsgamma.c` does not rule out calls
  into other source files.
- If the two cloned `bsgamma` results coincide but contexts
  propagated through evolution yield distinct BRs, audit changes
  to **other fields of the parameter struct** during earlier stages.
- If the cloned result differs from the original even with the
  same residual mass, investigate mutation by the `bsgamma`
  routine or non-reentrant auxiliary state before interpreting it.
- Until these distinctions are established, **both the original
  and isolated Zee BR candidates are unvalidated.**

No experimental comparison or exclusion decision is made.

## Frozen-WC replay: final SuperIso `bsgamma()` rematching hypothesis

The latest AF replay confirms conclusively that when all evolved and
primed Wilson coefficients are **frozen**, switching only the residual
`param.mass_H` inside `bsgamma()` changes its output by exactly
`7.32944489362404e-7`, for both vendor and NLO-patched libraries.
The result is reproducible; the different residual masses do not
change the post-RG or primed Wilson vectors.

The historical SuperIso 3.3 source publicly available at
`andrewfowlie/superpy/superiso_v3.3/src/bsgamma.c` contains **an
internal call to CW_calculator** within the inclusive BR routine.
The internally obtained high-scale `C0w[7]` and `C0w[8]` enter
nonperturbative and electromagnetic terms `N_E0`, `P_em`.
This architecture would produce exactly the observed single-state
mass-context leakage if retained in SuperIso v5.

**Do not assume the v5 code has the same internal structure before
auditing it.** The direct-token source scan saw no `mass_H` inside
v5 `bsgamma.c`, which is compatible with indirect matching
through `CW_calculator`.

Run source-only audit on AF (no rebuild or source patch):

```bash
cd /home/aalida/zee
git switch gateA1n-superiso-br-candidate-controls
git pull --ff-only
python3 scripts/gateA1n_audit_bsgamma_hidden_matching.py \
  --superiso-dir /home/aalida/opt/zee_tools/SuperIso_v5.0 \
  --output work/gateA1n_bsgamma_hidden_matching_audit.txt
cat work/gateA1n_bsgamma_hidden_matching_audit.txt
```

The audit returns every internal matching/C0w occurrence and
line-numbered context for `N_E0`, `P_em`, and `Cem`.
On confirmation, a **correct** Zee implementation must thread the
coherent high-scale vector `C0w_Zee` through those pieces *as well
as* through RGE. It must not simulate the effect with an arbitrary
single `mass_H`, average final rates, or ignore an internally
recomputed NP contribution.

Any subsequent source-level adaptation should be made in a distinct,
version-pinned SuperIso copy and reproduce the native SM and both
single-Type-II endpoints before reporting a candidate Zee branching
ratio. An independent NLO/NNLO Type-II check remains a separate gate.

## Remaining required gates

1. Obtain a known Type-II NNLO reference **prediction curve**
   for multiple charged-Higgs masses at the **same top-mass scheme,
   photon-energy threshold, alpha_s, masses and SM inputs**.
   A published *lower bound* like 570–800 GeV alone is not a
   numerical prediction to validate line-by-line.
2. Independently validate the charged-Higgs NLO and NNLO Wilson
   matching against the calculations of Hermann, Misiak and
   Steinhauser (arXiv:1208.2788), not merely against a SuperIso
   version exhibiting the same formula family.
3. Check SuperIso's `Cprime_calculator` / Type-II and Zee
   chirality-changing contributions, missing off-diagonal
   charged-singlet couplings, and matching thresholds.
4. Quantify numerical and perturbative scale dependence and
   theoretical/experimental covariance, then construct a
   documented CL consistency test.
5. Compare to at least one independent implementation and
   establish numerical uncertainties before declaring a
   model point allowed or excluded.

External reference SM prediction:
Misiak, Rehman, Steinhauser,
[JHEP 06 (2020) 175](https://arxiv.org/abs/2002.01548),
`BR(B->Xs gamma)=(3.40 +/- 0.17)e-4` at
`Egamma>1.6 GeV`. This is **context**, not a guaranteed
identical-SM-input validation of our SuperIso configuration.
