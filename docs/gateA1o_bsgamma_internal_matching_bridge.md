# Gate A1O: coherent Zee matching in SuperIso's hidden inclusive-BR correction

**Status: unexecuted AF candidate software integration, not a physics exclusion.**

## Actual source diagnosis (A1N)

The installed SuperIso v5.0 `src/bsgamma.c` has
SHA256 `ab754c8596d0610a3efe3920acefb18ff34b5cc7bac66072a965d6a1e971c196`.
In the function evaluating the inclusive branching ratio, after all
low-scale Wilson coefficients have been supplied and evolved,
there is a **second** high-scale matching call:

```c
/* bsgamma.c:681-682 */
double complex Cem[9],C0w[11],C1w[11],C2w[11];
CW_calculator(2,C0w,C1w,C2w,mu_W,param);
```

Those recomputed high-scale coefficients enter the nonperturbative
correction (line 694) and electromagnetic correction (line 703):

```c
/* line 694: schematically */
Kt0 = ... * (Re(C0w[7])+23./36.) -
       ... * (Re(C0w[8])+1./3.);
/* line 703: schematically */
Cem[7] = ...*C0w[7] + Cem[8]*C0w[8] + Cem[2];
```

These terms feed `N_E0` and `P_em`, respectively, in the final
BR. This is **a verified double-matching bug in our external
two-state interface**, NOT necessarily a bug in stock single-state
SuperIso: its internal C0w is consistent for a native SM/Type-II run.

The AF frozen-WC replay established that all low-scale Wilson and
primed coefficients are identical between two residual `mass_H`
contexts but the inclusive rate differs by exactly
`7.32944489362404e-7` (~0.18%) in both native and NLO-patched
builds. Changing only `mass_H` in the final BR routine reproduces
this difference. A1O targets exactly this missing interface.

## A1O design: isolated, explicitly controlled internal override

- Clone the **already patched A1M source**, verifying A1M wilson.c
  hash against `source_patch_provenance.json`.
- Refuse any input `bsgamma.c` whose hash differs from the audited
  official v5.0 SHA.
- Make exactly one additional source patch in **copied**
  `src/bsgamma.c`, leaving every other source file unchanged.
- Introduce guarded, thread-local `gateA1o_set_internal_C0w78`
  and `gateA1o_clear_internal_C0w78` functions. The default flag is
  disabled, so ordinary SuperIso single-state calls are not affected.
- After the internal matching call, override **only** C0w[7] and
  C0w[8] with the external already-matched values. These are exactly
  the matching coefficients used by `Kt0`, `N_E0`, `Cem[7]`, and
  `P_em` in the audited source. The remaining high-scale entries
  are untouched, because the source does not use them in these
  two additions to the inclusive rate.
- Compile the existing Gate A1N diagnostic driver with
  `-DGATE_A1O_MATCHED_C0W`; it passes the same complete matching
  vectors to RG evolution and the internally matched C0w[7/8]
  correction. Each call is explicitly bracketed with set/clear,
  including its frozen-input replay.

**Implementation caveat:** The current C interface uses
thread-local state to avoid altering SuperIso's published
function signatures. This is a **controlled serial diagnostic**,
not a re-entrant production implementation or general C API.
For a publication-quality tool, replace this with a clean
per-call `C0w` argument to an internal `bsgamma` variant once
the numerical and independent physics controls pass.

## AF commands

```bash
cd /home/aalida/zee
git fetch origin gateA1o-bsgamma-internal-matching-bridge
git switch gateA1o-bsgamma-internal-matching-bridge

python3 -m unittest discover -s tests \
  -p 'test_gateA1o_bsgamma_bridge.py' -v

bash scripts/gateA1o_run_bsgamma_bridge.sh \
  /home/aalida/zee/work/gateA1m_isolated_nlo_v1/isolated_superiso \
  work/gateA1o_bsgamma_bridge_v1

cat work/gateA1o_bsgamma_bridge_v1/result.json
```

**Do not reuse the same destination directory for a new run.** A1O
refuses to overwrite an existing isolated source tree.
The build is serial (`make -j1`) to avoid the known vendor
archive race.

## Required acceptance checks

1. Source hashes and exact internal matching call match the audited
   version. No vendor or A1M source is modified.
2. **SM** BR in A1O equals the A1M baseline and independent official
   SuperIso `sm.x` prediction (`3.382e-4`) to printed precision.
3. Type-II BRs at **300, 700, 1000, 2000 GeV** and gamma=0,
   gamma=pi/2 endpoints agree **exactly** between A1M and A1O.
   This controls the injection for every pure single-state case.
4. The *same* Zee Wilson vectors return the same rate with arbitrary
   residual `mass_H=300` or `700` in A1O, for nominal and four
   scale-variation points.
5. The original A1M code must still reproduce its known nonzero
   mass-context discrepancy, to avoid a false-positive comparison.
6. The primed coefficients must remain unchanged in both versions,
   and same-mass repeats must be deterministic.
7. The result JSON is explicitly **candidate-only**; no allowed or
   excluded benchmark classification.

If any acceptance check fails, the A1O checker exits nonzero and
writes a `GATE_A1O_BLOCKED_VALIDATION_FAILURE` JSON.

## Still missing before physical claims

- Independent NLO/NNLO charged-Higgs matching and complete Type-II
  predictions over many masses with consistent schemes/inputs.
  Removal of the original v5 premature NLO clipping is **not** an
  independent analytic validation.
- Full assessment of quark-flavour assumptions and possible extra
  two-charged-state contributions beyond the weighted doublet-loop
  structure.
- Sensible perturbative matching/low-scale variations, correlated
  theory errors, world-average experimental inputs and confidence
  intervals.
- A documented, reproducible public-friendly interface that passes
  the combined high-scale matching explicitly **without** relying
  on thread-local diagnostic overrides.

**No benchmark exclusion or viability status should be inferred
from a successful A1O software check.**
