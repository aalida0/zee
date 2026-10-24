# F19c — exact F18/F19/F19b six-field Zee tree-vacuum witness audit

## Purpose and scientific status

This stage uses the three heavy Zee benchmarks whose actual F18
two+three-body charged scalar widths and cascade BR were source validated.
All three also passed F19 sufficient quartic BFB, tree 8pi scalar
unitarity and published oblique STU screens. Their exact F17f complex
f/Y reproduce a fixed normal-ordering neutrino matrix and yield small
**partial** coherent radiative LFV rates in F19b.

**Real F19b CERN output (24 October 2026):**

| candidate | fixed NO neutrino closure (eV) | max f | max Y | inclusive subset mu->e gamma BR | maximal partial/reference ratio | full-model allowed |
|---|---:|---:|---:|---:|---:|---|
| F13_heavy_0001330 | 1.7312641707e-14 | 0.00448851 | 6.66864e-5 | 3.70953663e-17 | 0.000247302442 | UNKNOWN |
| F13_heavy_0000981 | 1.4231849983e-14 | 0.00522231 | 1.50265e-5 | 6.88563291e-18 | 0.0000459042194 | UNKNOWN |
| F13_heavy_0001003 | 5.1903208757e-15 | 0.00778574 | 5.17695e-6 | 5.77747379e-17 | 0.000385164920 | UNKNOWN |

Source input SHA256 `3876c06620bb091eca9b3bc056ef10bd67a6ee60e2240f2d50966cd6fda4cb1e`.
F19b predecessor F19 ledger SHA256
`85883e6aade33cbb2459d13059a1c66081e5a9ba2af5d5725776421ad1fd0538`.
F19b driver SHA256
`3dd094ede7ecd1947448e7f54ce4162b02aa85362f0439008dc022b201c19272`.
These are the **user-reported real LXPLUS outputs**, not unit-test fixtures.

F19c adds a **different, independent scientific constraint** absent from
quartic BFB: even when the scalar potential grows positive at large fields,
the dimensionful Zee cubic `muZee` can induce an energetically deeper
charge-breaking vacuum than the desired electroweak stationary point.

Reuse the existing analytically checked `zee_gateC5_charge_breaking_vacuum_search.py`
and `zee_gateC1_joined_uv_pilot.scalar_lagrangian` from the **original
script archive already stored on EOS**. Importing C1 does not run its
approximate CKM-identity Yukawa/RGE workflow; here only the independently
reconstructed scalar potential is used. The search checks:

1. Source-hash locks: original F18 merged JSON → F19 actual
   scalar/EWPO ledger → F19b exact complex LFV JSON. Require
   original three case IDs and the identical F18 cascade BRs.
2. Independently recompute the dimensionful scalar potential:
   `m1,m2,m12,mchi,muZee,l1..l10` including the Zee trilinear.
3. Verify all three Goldstone modes, seven scalar mass eigenvalues and
   stationarity gradient at the original electroweak configuration.
4. Search six physical gauge-fixed real fields, including charged Higgs,
   singlet and CP breaking directions. Initially 64 multistart seeds
   plus EW and -EW controls, with boundary ±12v.
5. At each minimum trial, evaluate the exact 10-real-field quartic,
   cubic and quadratic potential independently, and only flag a
   `DEEPER_TREE_POTENTIAL_WITNESS` if
   `(Vtrial-VEW)/v^4 < -1e-6`.
6. **Interpretation**:
   - Explicit deeper point: the chosen EW vacuum is NOT the deepest
     configuration of the tree potential.
   - No deeper witness: not a proof of global neutral vacuum. Sampling
     is finite and loop tunneling/metastability are not computed.
   - In either case: NO full Zee experimental allowed/excluded status.

## Local Ubuntu — updated scripts and source-safety unit tests

```bash
cd ~/zee
git switch feature/global-scan-priority1
git pull --ff-only

python3 -m unittest discover -s tests \
  -p 'test_zee_paper1_F19c_exact_three_vacuum_witness.py' -v
bash -n scripts/zee_paper1_F19c_one_shot_lxplus.sh

scp scripts/zee_paper1_F19c_exact_three_vacuum_witness.py \
    scripts/zee_paper1_F19c_one_shot_lxplus.sh \
    aalida@lxplus.cern.ch:~/
```

## CERN LXPLUS — actual three-benchmark 64-seed audit

```bash
export F18_EOS=/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024
export F18_FINAL="$HOME/zee_f18_lxplus_submit_20261024/F18_final_three_benchmarks/F18_CONDOR_three_source_verified.json"
export F19_LEDGER="$HOME/zee_f19_scalar_ewpo_20261024/F19_results/F19_integrated_three_constraint_ledger_NOT_ALLOWED.json"
export F19B_RESULT="$HOME/zee_f19b_exact_neutrino_partial_LFV_20261024/F19b_results/F19b_exact_complex_neutrino_partial_LFV_NOT_ALLOWED.json"

bash ~/zee_paper1_F19c_one_shot_lxplus.sh \
 "$F18_EOS" "$F18_FINAL" "$F19_LEDGER" "$F19B_RESULT" \
 "$HOME/zee_f19c_three_vacuum_witness_64_20261024" 64 350
```

Review:

```bash
column -s, -t \
 "$HOME/zee_f19c_three_vacuum_witness_64_20261024/F19c_results/F19c_three_vacuum_witness_summary.csv"
```

**Resource caution:** this is a genuine repeated nonconvex six-field
minimization, substantially more work than three STU integrals. The
initial 64-seed campaign is a source-checked pilot, not an exhaustive
global vacuum scan. If LXPLUS interactive load is restrictive, move
one case per CERN HTCondor job rather than launching much larger
multistart counts interactively. For further evidence, run a
separate 256/512-seed campaign with a fresh output folder and seed,
especially for cases with no deeper witness.

On success preserve results in `$F18_EOS/F19c_vacuum_witness_20261024/`;
do not delete or overwrite F18, F19, or F19b results.

## Next physics blockers for an EPJC paper

A no-witness outcome plus small partial LFV does NOT establish the
model is viable. We still require a full lepton-flavor prediction and
global neutrino fit over phases/orderings, coherent two-charged
B->Xs gamma beyond original LO linearized screens, HiggsTools five-state
inputs, direct LHC searches, and physical pp->t(b)H2 rates at 13.6/14
TeV. The 2021 cascade itself is already known, so the novelty claim
rests on **complete simultaneous neutrino/LFV/flavor constraints**.
