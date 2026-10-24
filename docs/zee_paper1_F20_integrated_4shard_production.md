# F20 — Four parallel CERN HTCondor large integrated Zee scans (AF not needed)

**Target:** Stop one-benchmark gate proliferation. Launch one substantial
source-anchored computational campaign now, then decide manuscript scope
from its full merged results. 24 October 2026.

The original F18, F19, F19b, F19c, F19d real CERN JSONs are the **five**
input anchors. Exact source SHA chain must pass before anything submits.
Original three physically validated F18 benchmarks serve as the seeds,
not three isolated observables to keep rechecking. The UChicago AF is
down and **will not be needed**.

## Production workload

**Four HTCondor shards concurrently**, independently seeded (no
artificially claimed statistical independence of resulting physics bins):

- 5,000 new B4 scalar parameter proposals per shard; across all four,
  **20,000 proposals**. Every accepted point passes implemented
  sufficient quartic BFB, scalar 8pi tree unitarity and correlated
  Gfitter 2026 + PDG 2025 STU scalar-oblique screening.
- At **every surviving scalar point** evaluate published analytic
  Type-II two-state LO dC7/dC8 at a fixed **illustrative**
  mtop_MSbar(160 GeV)=163 GeV, then 2026 Eq.4 linearized
  B->Xs gamma. Include the independent LO flavor-shift/cascade
  PROXY Pareto frontier. **No 2026 NNLO likelihood/CL.**
- Select 30 scalar/mass/mixing-diverse interesting points per shard;
  evaluate **exact fixed NO central target** complex f,Y Yukawa
  90 independent trial orientations and up to two local optimizations
  of previously validated coherent PARTIAL LFV. Report neutrino
  closure, max partial channel ratio, and the B3 charged decay
  *included-channel* proxy.
- For 12 high-proxy neutrino-closed points per shard, run existing
  analytic dimensionful Zee **64 multistart six-field tree-vacuum
  witness search**, with explicit no-global-proof language.
- Four-shard merger outputs overall scalar/LO-flavor table, a true
  *diagnostic* Pareto envelope (not CL), combined fixed-NO and
  partial-LFV shortlist and optional two image plots.
- All model-allowed or excluded flags stay null/UNKNOWN. The three
  original F18 MadWidth measurements are real; the new scalar
  scan points use the B4/B3 **INCLUDED-channel proxies**, not actual
  new-point MG5 widths or 13.6 TeV production cross sections.

This is a **large screening study**, not a fully validated global
likelihood or completion guarantee. It can support a sharply scoped
phenomenology paper only after missing critical observables are closed
or paper claims honestly narrowed. The repo is explicit about those
constraints in each result.

## One local preparation (Ubuntu)

```bash
cd ~/zee
git switch feature/global-scan-priority1
git pull --ff-only

# Archive only the physics scripts, not old MadGraph or AF data.
tar -czf "$HOME/F20_scripts_bundle.tar.gz" scripts
scp "$HOME/F20_scripts_bundle.tar.gz" \
    scripts/zee_paper1_F20_condor_worker.sh \
    scripts/zee_paper1_F20_prepare_submit_lxplus.sh \
    scripts/zee_paper1_F20_merge_four_production_shards.py \
    aalida@lxplus.cern.ch:~/
```

No local manual chain of microtests. The GitHub Actions workflow
syntax-checks the big integrated Python and both Bash launchers in
one pass; individual old physics backends have separate prior tests.

## ONE submission command on CERN LXPLUS

```bash
bash ~/zee_paper1_F20_prepare_submit_lxplus.sh
```

This script first verifies exact F19d source-to-original F18/F19/F19b/F19c
SHA provenance, constructs a new immutable AFS workspace,
`~/zee_F20_integrated_20261024`, copies **small JSON source**
files and the script archive, creates fresh EOS
`/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024/F20_4shards_20261024/`,
then submits one four-proc HTCondor campaign with EOSUSER output
destination. Four output archives will have names
`F20_result_shard_0.tar.gz` ... `F20_result_shard_3.tar.gz`.

**Important:** This is an HTCondor production workload, not for direct
execution on the LXPLUS login node. The four-shard setup budgets two
CPUs, 12 GB memory and 24-hour walltime *per job*; these are resource
requests, not a guarantee of completion or queue time. Do not launch
additional independent scans before evaluating the merged results.

To check status, use `condor_q $USER` or inspect
`$HOME/zee_F20_integrated_20261024/logs/` on LXPLUS.

## One merge after all four archives exist on EOS

```bash
export F20_EOS=/eos/user/a/aalida/zee/F18_lxplus_two_remaining_20261024/F20_4shards_20261024

python3 ~/zee_paper1_F20_merge_four_production_shards.py \
  --eos-results "$F20_EOS" \
  --output-dir "$HOME/zee_F20_four_shard_merged_20261024"

cat "$HOME/zee_F20_four_shard_merged_20261024/F20_PRODUCTION_exploratory_summary.json"

head -n 16 \
  "$HOME/zee_F20_four_shard_merged_20261024/F20_ALL_shards_fixed_NO_partial_LFV_shortlist_NOT_ALLOWED.csv"
```

The merger **refuses** missing, failed, truncated or inconsistently
source-provenanced shards; it does not infer success from nonempty
tarballs. A failing worker still transfers its diagnostic archive to
EOS for robust debugging. Do not claim four-shard success until the
merger succeeds.

### Decision after ONE integrated run

If the Pareto front and exact fixed-NO partial LFV families occupy
a clear favorable region, prioritize completing the *full* LFV and
precision two-state B->Xs gamma models and five-state direct-search
inputs. If not, stop Paper 1 rather than devote weeks to expanding
unvalidated benchmark tests. The nonleptonic included-channel
cascade proxy does not substitute for genuine MadWidth+production;
these may be added for a SMALL final representative set only.

**Blockers to submission even after F20**: calibrated consistent
2026 two-charged B->Xs gamma at beyond LO, full coherent
LFV (including conversion and two-loop classes), updated neutrino
NO/IO/phase likelihood, full HiggsTools five-state production/
decays and direct collider constraints, and model consistency.
A publishable scan-only paper could still be possible on a
narrower title/claim, but scientific novelty must be independently
compared with Florentino 2021 and Herrero 2017 and cannot be
declared automatically by the number of scanned points.
