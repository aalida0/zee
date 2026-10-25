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


## Real CERN LXPLUS F19 result — 24 October 2026

User ran the actual F19 one-shot successfully with complete F18 3/3.
Note: the local 4/4 regression tests use synthetic data, not the
numerical results below. The following are user-reported real LXPLUS
results; the numerical output files themselves have not been uploaded
to the repository.

- F18 source EOS archive SHA256:
  `3876c06620bb091eca9b3bc056ef10bd67a6ee60e2240f2d50966cd6fda4cb1e`.
- Merged F18 source-verified result SHA256:
  `f56235d5200dfcf1bbb1d164875c25e17671d6b770520da543396c995527b33f`.
- F19 driver SHA256:
  `3ad03298ee5ecf1cb097b09a1cd3fabbd64c2effda8ed2b450a18ee148c186a5`.

| Case | mH1 GeV | mH2 GeV | 8pi max eigenvalue | sufficient BFB | 8pi unitarity | S | T | U | Gfitter2026 chi2 | PDG2025 chi2 | MadWidth cascade BR |
|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|
| F13_heavy_0001330 | 572.2316 | 873.2077 | 24.6969918 | true | true | -0.0026570691 | 0.0319316276 | 0.0000254590 | 1.654779 | 0.204195 | 0.44634835 |
| F13_heavy_0000981 | 552.6457 | 885.7888 | 21.0565185 | true | true | -0.0026011219 | 0.0363474723 | 0.0000247646 | 2.245594 | 0.295210 | 0.46387734 |
| F13_heavy_0001003 | 580.5073 | 881.4622 | 21.5681141 | true | true | -0.0027683359 | 0.0316463079 | 0.0000224248 | 1.629589 | 0.202309 | 0.42032289 |

All are inside Gfitter 2026 and PDG 2025 scalar STU correlated
3D Gaussian 95% regions. The quartic BFB criterion is sufficient,
not necessary, and does not prove the EW neutral vacuum is global.

At 0001330, the maximal scalar scattering eigenvalue 24.697 is
only 0.43575 below 8pi=25.13274, or 1.73% of the bound.
Screen robustness to stricter perturbativity and higher-order
effects is a concern. The largest cascade BR (46.39%) is at
0000981, with a larger 8pi margin (~16.2%).

**EPJC caution:** Florentino et al. 2021 already considered the
cascade and scalar/quark constraints. The F19 success is independent
model implementation validation, not new evidence of a fully
experimentally viable neutrino-LFV-consistent region. The 2026
two-charged B->Xs gamma matched likelihood, complete LFV,
neutrino likelihood, global vacuum, Higgs/charged searches, etc.
remain uncalculated. All three full-model-allowed entries remain
UNKNOWN. The original three point full prediction CSV + JSON
should be preserved in the original user EOS project.

Next high-value scientific gates: source-matched global vacuum,
full complex Zee LFV including relevant two-loop amplitudes,
modern two-charged B->Xs gamma scheme-consistent precision, and
HiggsTools full five-state input. Do not convert existing
LO/flavor/proxy diagnostics into confidence levels.
