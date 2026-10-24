# F19: exact F18 → real Zee scalar BFB/unitarity + correlated STU intake

**As of 24 October 2026:** F18 completed 3/3 on local Ubuntu +
CERN HTCondor, with independently checked original SARAH/complex-lepton
input cards and genuine MadWidth 2+3-body tables. This is the first F19
**physics calculation**, not an assertion of full Zee viability.

## Why we start here

Our target EPJC contribution is not rediscovery of the 2021
H2+ -> H1+ Z cascade: Florentino, Romao and Silva 2021 already studied it.
The scientific novelty must come from a reproducible intersection of
**neutrino masses, complete LFV, quark constraints, scalar/Higgs
phenomenology and the cascade signal**.

Existing repository modules:

- `gate6_benchmark.py`: full Zee scalar mass inversion, *sufficient
  but not necessary* quartic boundedness and four sector tree 2-to-2
  perturbative unitarity. **Does not establish global neutral vacuum.**
- `gateA1h_correlated_stu_ewpo.py`: scalar S,T,U, published Gfitter
  2026 and PDG 2025 3D correlated Gaussian regions, **not a complete EW fit**.
- `gateB2_zee_neutrino_family_scan.py` and later F13/F17: exact complex
  f,Y closure for a **single chosen neutrino mass target**, not a modern
  oscillation/cosmology phase likelihood.
- F11-F13: published 2026 Eq(4) **linearized LO C7/C8**
  B->Xs gamma screens, not two-charged NNLO-exclusion likelihoods.
- `zee_priority1_higgstools.py`: API only; it refuses incomplete
  five-particle cross section, widths, production map; not full HB/HS input.
- F18: genuine tree-level MadWidth, including 2/3 body modes; no
  QCD-corrected total widths or full constraint allowance.

## This F19 stage evaluates on exactly the three F18 benchmarks

The new `zee_paper1_F19_integrated_scalar_EWPO_constraints.py` verifies:

1. F18 merged 3/3 SUCCESS status, original source cohort and no false
   QCD or model-allowed labels.
2. Source archive `F18_source_bundle.tar.gz` real original
   `F16_three_exact_F13_Zee_input_reconstruction.json`.
3. F17f report SHA against the F18 merged source manifest; each of
   the *three* original full-CKM SLHA card SHA values against the
   completed F18 per-case results.
4. Actual scalar masses of all five model particles from the cards
   against F16 original scalar parameters, and H2 charged mixing
   if present in the F18 numerical result.
5. Gate6 independently reconstructs charged and neutral eigenmasses
   and calculates sufficient quartic BFB and all implemented scalar
   unitarity eigenvalues. BFB false = **NOT_CERTIFIED**, not definitive
   instability (test is sufficient but not necessary).
6. Gate A1H evaluates physical scalar S,T,U against both
   correlated 3D Gaussian fits. Outside the region = a **screen
   red flag**, not an independent global 95% physical exclusion.
7. Join the real F18 charged widths and actual H2->H1Z->tbZ
   cascade fractions. **Never** substitute Gate6 truncated proxies.

Output per source benchmark:
- `F19_three_scalar_EWPO_vs_cascade_NOT_ALLOWED.csv`
- `F19_integrated_three_constraint_ledger_NOT_ALLOWED.json`

Unresolved constraints are literally `NOT_EVALUATED`, and all three
`physical_Zee_fully_allowed_or_excluded` remain `null`.

## One-shot CERN LXPLUS run using ALREADY TRANSFERRED EOS files

On **your local Ubuntu PC**:

```bash
cd ~/zee
git switch feature/global-scan-priority1
git pull --ff-only
scp scripts/zee_paper1_F19_integrated_scalar_EWPO_constraints.py \
    scripts/zee_paper1_F19_one_shot_lxplus.sh \
    aalida@lxplus.cern.ch:~/
```

On **LXPLUS**:

```bash
export F18_EOS=/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024

bash ~/zee_paper1_F19_one_shot_lxplus.sh \
  "$F18_EOS" \
  "$HOME/zee_f18_lxplus_submit_20261024/F18_final_three_benchmarks/F18_CONDOR_three_source_verified.json" \
  "$HOME/zee_f19_scalar_ewpo_20261024"
```

Only existing small `F18_scripts_bundle.tar.gz` is unpacked in AFS;
all large F16/F17 source and MadWidth archives remain in EOS. The script
requires `python3` with `numpy` and `scipy`; if missing in interactive
LXPLUS Python, load a CERN-supported LCG view for your actual OS/compiler
only after inspecting the error. No GPU or batch slot needed: a
three-scalar-point oblique integral calculation is a short interactive job.

Inspect:

```bash
column -t -s, \
  "$HOME/zee_f19_scalar_ewpo_20261024/F19_results/F19_three_scalar_EWPO_vs_cascade_NOT_ALLOWED.csv"

cat "$HOME/zee_f19_scalar_ewpo_20261024/F19_run.log"
```

After success copy only the final outputs to EOS (never delete originals):

```bash
mkdir -p "$F18_EOS/F19_scalar_EWPO_20261024"
cp -av "$HOME/zee_f19_scalar_ewpo_20261024"/F19_results/. \
   "$F18_EOS/F19_scalar_EWPO_20261024/"
```

## What would make the EPJC contribution new?

A single benchmark `BR(H2->H1Z)≈45%` is not novel relative to the
2021 study. The credible next scientific milestone is a *complete*
constraint and likelihood workflow, applied to the **same fully complex
model parameters** and scanned over neutrino phase/Yukawa null
directions and scalar parameters. There must be explicit independent
reference tests and uncertainty models for each observable.

The next F19 extensions should be **actual calculations**, not
extra proxy-only scans:

1. Build a source-complete **2026 two-charged b->s gamma**
   prediction, matching both states coherently in the same order,
   scheme and uncertainty model; calibrate against Type-II limits.
2. Implement or validate complete **charged LFV** (at minimum
   mu->e gamma with all relevant one/two-loop terms, mu->3e,
   conversion, tau observables). The existing partial amplitudes
   can rank but cannot certify viability.
3. Sample neutrino oscillation ranges, orderings and physical phases;
   same actual f,Y as LFV and collider widths.
4. Global vacuum and quark-sector alignment/RG consistency.
5. Complete HiggsTools five-state predictions and direct charged
   searches, with explicit analysis coverage.
6. Only after these are validated, perform a broad **joint scan**
   and mark points fully constraint-tested. Use true F18 widths
   for a small priority set; avoid assuming they hold over the scan.

No benchmark is called experimentally allowed without full evidence.
