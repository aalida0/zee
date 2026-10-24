# F19b — Exact F17f complex f/Y neutrino closure and coherent PARTIAL LFV

## Scope / status

The original three F18 genuine MadWidth cases were independently screened
by F19 scalar BFB/8pi unitarity and published correlated STU; all three
passed those restricted screens, **not** a full general Zee-model likelihood.

F19b is the first direct per-benchmark observable recalculation from the
**same exact original F17f complex SLHA lepton matrices**, not newly
optimized families or a synthetic benchmark input.

Source matching:

1. Verify F19 predecessor JSON SHA against the actual complete F18 merged
   JSON, and exact original F16/F17f EOS tarball SHA.
2. Independently load the original F17 numerical *complex* matrix JSON,
   and F17f CKM source-matched SLHA cards from the same original tarball.
3. Require all 3x3 complex FZEE,YE,YEE2 SLHA entries (real and imaginary)
   and close them numerically against original F17 source JSON.
4. Rebuild the Chen Higgs-basis matrices with exact source convention:
   `f_Chen = FZEE_SARAH/2`;
   `Y_Chen=(-sin(beta)*Ye+cos(beta)*Ye2)/sqrt(2)`.
   Verify original F17 YChen, charged lepton mass-diagonal relation and
   antisymmetric f to high precision.
5. Using the same exact H1/H2 masses and gamma from F19 and F18,
   reconstruct the one-loop Zee neutrino matrix against the historical
   **FIXED normal-ordering central-value target** from A1B/F13,
   and require matrix closure < 1e-9 eV.
6. Evaluate the already implemented **coherent subset** of 3 radiative
   channels: scalar one-loop plus fermion-gamma Barr-Zee
   (top,bottom,tau) and CP-even W-gamma Barr-Zee; add COMPLEX
   amplitudes before squaring, never add branching ratios.
   Check one-loop outputs versus B2 backend and one-loop+fermion
   versus D2 source backend. This is not all two-loop LFV.
7. Independently add neutral h/H/A tree-only pieces for five
   3-lepton modes, validating against D2, and f-only lepton universality.

Historical single-observable upper limits are only denominators of
**partial scores** and are not calibrated 2026 full-model confidence
levels. Omitted amplitudes (charged-scalar two-loop, W-Z, Z-penguins,
photonic 3-body, boxes, mu-e conversion, full Y universality) may
interfere; a partial ratio below/above one is not a full exclusion/pass.
The neutrino target is fixed old central NO, **not** a full NO+IO
oscillation+CP phase likelihood. At no point is a user point labelled
phenomenologically allowed or experimentally excluded.

## On local Ubuntu: source-safe regression and tiny script transfer

```bash
cd ~/zee
git switch feature/global-scan-priority1
git pull --ff-only

python3 -m unittest discover -s tests \
  -p 'test_zee_paper1_F19b_exact_F17f_neutrino_partial_LFV.py' -v
bash -n scripts/zee_paper1_F19b_one_shot_lxplus.sh

scp scripts/zee_paper1_F19b_exact_F17f_neutrino_partial_LFV.py \
    scripts/zee_paper1_F19b_one_shot_lxplus.sh \
    aalida@lxplus.cern.ch:~/
```

## CERN LXPLUS: one-shot numerical audit with original EOS sources

```bash
export F18_EOS=/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024
export F18_FINAL="$HOME/zee_f18_lxplus_submit_20261024/F18_final_three_benchmarks/F18_CONDOR_three_source_verified.json"
export F19_LEDGER="$HOME/zee_f19_scalar_ewpo_20261024/F19_results/F19_integrated_three_constraint_ledger_NOT_ALLOWED.json"

bash ~/zee_paper1_F19b_one_shot_lxplus.sh \
 "$F18_EOS" \
 "$F18_FINAL" \
 "$F19_LEDGER" \
 "$HOME/zee_f19b_exact_neutrino_partial_LFV_20261024"
```

This source bundle contains all original physics backends in an archive.
They are extracted to an AFS working directory, while the large tarball
remains on EOS. No new Condor slots, MadGraph integration or Mathematica
run is necessary. The working directory must not exist beforehand, to
preserve previous provenance.

Review:

```bash
column -s, -t \
  "$HOME/zee_f19b_exact_neutrino_partial_LFV_20261024/F19b_results/F19b_three_exact_Yukawa_partial_LFV_NOT_ALLOWED.csv"

cat "$HOME/zee_f19b_exact_neutrino_partial_LFV_20261024/F19b_run.log"
```

After **successful actual numerical completion**, store results on EOS:

```bash
mkdir -p "$F18_EOS/F19b_exact_neutrino_partial_LFV_20261024"
cp -av "$HOME/zee_f19b_exact_neutrino_partial_LFV_20261024/F19b_results/." \
  "$F18_EOS/F19b_exact_neutrino_partial_LFV_20261024/"
cp -av "$HOME/zee_f19b_exact_neutrino_partial_LFV_20261024/F19b_outputs_SHA256.txt" \
  "$F18_EOS/F19b_exact_neutrino_partial_LFV_20261024/"
```

## Scientific next steps

This one-shot diagnoses whether the *exact three* established scalar and
width benchmarks have already significant LFV contributions in the
included diagrams. A too-large partial score is a **warning**, not a
complete exclusion: interference from missing diagrams may shift rates.
A tiny partial score is **not permission to call allowed**. Full
general Zee LFV calculations and updated mu-e conversion experimental
constraints, full 2026 NO/IO neutrino fit, and matched two-charged
b->s gamma remain primary EPJC viability blockers. A robust joint scan
should come only after those are independently validated.

The full 2021 Zee charged cascade result is not novel by itself. Our
prospective EPJC novelty is the **correlated neutrino+LFV+charged
cascade constraint surface**, if it survives these additional checks.
