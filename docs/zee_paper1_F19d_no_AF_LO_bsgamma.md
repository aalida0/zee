# F19d — AF outage bypass for three original F18 Zee heavy points: analytic LO B->Xs gamma

**Situation (24 October 2026):** original F13 Monte Carlo-selected
`F13_selected_priority_scalar_2026LO_NOT_ALLOWED.csv` is only on
unavailable UChicago AF. We MUST NOT pretend that file is accessible,
guess its exact original SuperIso outputs, or block research awaiting
an indefinite facility restoration.

**Working alternative:** three original benchmarks have already been
reconstructed source-by-source and physically recalculated on CERN
in F18/F19/F19b/F19c. The complete exact scalar parameters (including
mH1, mH2, beta, gamma) are retained in the F19 JSON. F19d evaluates a
new, separately identified **analytical LO two-charged-state screening**
directly on those same physical parameters, on LXPLUS, with no AF,
SuperIso vendor archive, scipy, MadGraph or MadWidth.

Physics source:

- Mahmoudi & Stål, PRD81, 035016 (2010), arXiv:0907.1791,
  Eqs. (17)–(18), WET Q7/Q8 LO loop functions F^(1), F^(2);
- Type-II `lambda_tt=cot(beta),lambda_bb=-tan(beta)`, hence
  `dC7,8(m)=F7,8^(1)(mt(mu0)^2/m^2)/(3 tan(beta)^2)+F7,8^(2)(...)`.
- Zee CP-conserving charged doublet fractions
  `dC7,8^Zee=cos(gamma)^2 dC7,8(mH1)+sin(gamma)^2 dC7,8(mH2)`.
- Misiak et al. 2026 arXiv:2608.29863 Eq. (4),
  `1e4 BR=3.54-8.51 dC7-2.16 dC8`, linear in LO NP and at
  `mu0=160 GeV`.

**Mass scheme warning:** The unavailable AF A1S/SuperIso calculation
obtained `mt_running_at_160` from its versioned QCD `running_mass()`
code. This workflow **does not know** the exact original running-top
value and does not reproduce the original scheme/matching numerically.
It explicitly labels its specified **160/163/166 GeV** running-`mt(mu0)`
input values as three *illustrative input scenarios*, not a calibrated
theory uncertainty. It is independently sourced from the analytical
equations but not cross-code A1S validated at these 3 points.

The ratio to a `mH=670 GeV` single-state Type-II result is always
taken **at the same tanbeta and mt input**, and is just a ratio of
linearized LO NP shifts, never a ratio of experimental exclusions. The
670-GeV single-state published bound is NOT a model-independent Zee
two-state limit. Missing quadratic NP, NLO/NNLO matching and a
correlated modern theory+experiment likelihood prevent interpreting
this as a 95%-CL bound.

## Local Ubuntu — update, test, copy ONLY new small script

```bash
cd ~/zee
git switch feature/global-scan-priority1
git pull --ff-only
python3 -m unittest discover -s tests \
 -p 'test_zee_paper1_F19d_AF_independent_analytic_LO_bsgamma.py' -v
scp scripts/zee_paper1_F19d_AF_independent_analytic_LO_bsgamma.py \
 aalida@lxplus.cern.ch:~/
```

## CERN LXPLUS — original 4-source SHA-joined one-shot

```bash
export F18_FINAL="$HOME/zee_f18_lxplus_submit_20261024/F18_final_three_benchmarks/F18_CONDOR_three_source_verified.json"
export F19_LEDGER="$HOME/zee_f19_scalar_ewpo_20261024/F19_results/F19_integrated_three_constraint_ledger_NOT_ALLOWED.json"
export F19B_RESULT="$HOME/zee_f19b_exact_neutrino_partial_LFV_20261024/F19b_results/F19b_exact_complex_neutrino_partial_LFV_NOT_ALLOWED.json"
export F19C_RESULT="$HOME/zee_f19c_three_vacuum_witness_64_20261024/F19c_results/F19c_three_vacuum_witnesses_NOT_GLOBAL.json"

python3 -u ~/zee_paper1_F19d_AF_independent_analytic_LO_bsgamma.py \
 --f18 "$F18_FINAL" \
 --f19 "$F19_LEDGER" \
 --f19b "$F19B_RESULT" \
 --f19c "$F19C_RESULT" \
 --output-dir "$HOME/zee_f19d_analytic_LO_bsgamma_20261024" \
 --mt-cases 160 163 166

column -s, -t \
 "$HOME/zee_f19d_analytic_LO_bsgamma_20261024/F19d_analytic_two_charged_2026_linearized_LO_NOT_CL.csv"
```

This is 9 computations (3 physical Zee points x 3 chosen running-top
input scenarios), plus Type-II 670-GeV references with identical
`tanbeta` and `mt`. All expected to be near-instantaneous and
require only Python standard library. Previous F18, F19, F19b, F19c
source and results are NEVER modified.

After numerical success, optionally copy results to:

```bash
export F18_EOS=/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024
mkdir -p "$F18_EOS/F19d_analytic_LO_bsgamma_20261024"
cp -av "$HOME/zee_f19d_analytic_LO_bsgamma_20261024/." \
 "$F18_EOS/F19d_analytic_LO_bsgamma_20261024/"
```

## Scientific interpretation and what is still required

F19c user-reported genuine CERN run: 66/66 numerical vacuum field
evaluations successful at each of the three exact model points;
**no explicit deeper neutral/charge/CP breaking potential witness
was found**, with residual negative V-V_EW ~1e-17 v^4. This is
**not a global tree minimum proof**, nor a one-loop metastability result.

From F18-F19b, three exact models have cascade BRs 44.63%, 46.39%,
42.03%; pass sufficient scalar BFB/8pi unitary and scalar STU 3D
screens; each fixes the chosen normal-ordering neutrino-mass matrix
to ~1e-14 eV and gives small **partial** LFV scores, but no complete
general Zee LFV exclusion.

F19d is a diagnostic F13 flavor data recovery BY RECOMPUTATION,
not restoration of F13 CSV. We cannot claim the analytical numbers
are the original AF A1S result or an NNLO 2026 exclusion.
Once a trusted SuperIso build (possible on CERN/local Ubuntu) is
available, calibrate analytical LO dC7/8 against A1S/E4A at exactly
matched running mt and mu0, then upgrade modern NP matching.
Full LFV, global oscillation/CP-phase likelihood, model Higgs searches
and full quark alignment remain unresolved.
