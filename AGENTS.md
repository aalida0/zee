# Zee D7 — first reproducible LXPLUS / HTCondor broad-mass scan pilot

## Identity, execution location and frozen evidence
Work ONLY in `aalida0/zee` branch `feature/zee-d7-lxplus-condor-scan-pilot`, forked from verified D6 HEAD `a39afed7cd0ee7f4358dabdbde32729818f1f909`. Create separate local laptop checkout **under `~/zee/workspaces/zee-condor-d7`**, and separate lxplus checkout **under `~/zee/workspaces/zee-condor-d7` on CERN LXPLUS** (those are distinct filesystems). If the parent `~/zee` is tracked, locally ignore `/workspaces/` in `.git/info/exclude`, never a tracked parent change. Do NOT manipulate D5/D6 old working trees or raw production outputs.

This is a **32-point, 4-job pilot** ONLY, not a large production scan. The goal is to prove on actual CERN batch workers the repeatable heavy-scalar, NO neutrino-input, scoped tree/EWPO gate, output/receipt/hashes and aggregation architecture. Codex can access lxplus only if the user's SSH/Kerberos works; we have NO server-side SSH tool access here. Do not assert submission or worker PASS without real CERN `condor_submit`/queue/history/jobs and output receipts. Do not submit hundreds/thousands of jobs until the 4-job pilot really works and exact results are verified.

Frozen READ-ONLY: model `models/SARAH/ZeeTypeII/`, Modules 0–8 and D0–D6 physics/generator code/tests/source pins, existing evidence, historical NuFIT data and all other branches. Edit ONLY new `module9/`, `tests/test_module9_*.py`, `scripts/zee_d7_*.sh`, `validation/module9/` and this `AGENTS.md` to correct actual bugs. Do not redo D3/D4/D5/D6, SARAH export, any MG5 production, LFV Wgamma, physical (B\to X_s\gamma), 2026 quadratic research or full profile-likelihood integration here.

## Verified scientific state and limitations
D6 confirms full unequal H1/H2 pair production ≈ Z-only at present 250–350/700 GeV: ratio 0.997–0.998; this small process is NOT the paper's headline. Associated 5FS H2 production LO around 0.0045246 pb at 13.6 TeV, frozen-Yukawa seven-point −11.61/+13.21% and separate evolved-Yukawa correlated scale −18.31/+23.22%; no PDF uncertainty. D4 calculated complete LO on-shell two-body H1/H2 decays and validated tree cascade BRs. 2021 Florentino/Romao/Silva already studied cascade+tbH; 2017 Herrero-Garcia et al. already did general Zee flavor sampling. Novelty remains to be proven by NEW constrained scalar/neutrino/LFV + charged-Higgs correlation or distinctive physical signatures. D7 is infrastructure, not physics publication novelty.

Crucial missing completeness gates: restricted scalar vacuum solver is NOT proof of global vacuum; full LFV Wgamma absent; external official NuFIT joint likelihood absent; 2026 (B\to X_s\gamma) linearized Eq4 is diagnostic, NOT a validated classifier; RG closure/other flavor/experimental collider constraints absent. **All D7 results have `global_zee_acceptance=null`, `constraints_complete=false`.** Scalar gate PASS means only reconstruction, sufficient BFB, tree unitarity and scalar STU/EWPO within declared implementation.

NO/IO: committed `module3/example.json` is an illustrative **NO** neutrino target. The archived `module2/data/nufit60_ic19_io.json` contains a diagonal-gaussian **NuFIT6.0** approximation, not a verified 2026 NuFIT6.1 full joint IO neutrino target/likelihood. **DO NOT relabel the NO matrix as IO**. D7 executes NO only. A genuinely sourced IO target and inverse seed is a later independent task.

## First read / scaffold (UNEXECUTED at setup)
Read first `module9/d7_prepare.py`, `module9/d7_worker.py`, `module9/d7_collect.py`, `module9/condor/worker.sh`, `module9/condor/d7_pilot.sub`, `scripts/zee_d7_stage.sh`, `tests/test_module9_d7_batch.py`. Then read `module3/example.json`, `module6/d2_scalar_prefilter.py`, `module2/interface.py`, `module1/scalar_constraints.py`, and D2/D6 audits only as necessary. The newly prewritten D7 code is candidate scaffolding: audit/fix independently before treating tests as validation.

D7 design: 32 deterministic SHA-bound Module3/2/1 inverse inputs using LHS development support, with 16 broad charged/neutral mass/angle points and 16 points whose heavy neutral masses lie near charged H2. mH1 approximately 250–1200 GeV, H2 = mH1 + approximately 105–900 GeV, including heavy spectra >1 TeV; gamma, beta, alpha, m12sq, mh2 and ma vary. Every point is kinematically open for H2->H1 Z, but that alone does not guarantee its dynamical viability. These ranges are **exploratory numerical sampling, NOT justified priors, representativeness or exclusion thresholds**. The original 4 complex inverse-family coefficients and NO target are retained for D7; broaden lepton-Yukawa families after pipeline PASS. Every varied scalar record receives a new canonical SHA; Module3, Module2 and Module1 benchmark IDs must agree. Do not quietly replace incompatible inputs or source physical parameters from a separate card.

## A: local deterministic + real one-point validation before CERN
Run:
```bash
python3 -m unittest discover -s tests -p 'test_module9_d7_batch.py' -v
python3 -m module9.d7_prepare --seed module3/example.json --output-dir validation/module9/local/local_prepare
python3 -m module9.d7_worker --shard validation/module9/local/local_prepare/shards/part_000.jsonl --output validation/module9/local/local_prepare/test_results_0.jsonl --receipt validation/module9/local/local_prepare/test_receipt_0.json
```
The worker may produce scoped FAIL or EVALUATION_ERROR for unphysical/inconsistent points; this is evidence, not an allowed-points PASS. An actual D0/NO source worker test must reproduce its established inverse closure; failing that blocks physical-stage submission. Avoid nonempty output directory overwrite on repeats: use fresh versioned paths. Ensure every nonfinite, duplicate, stale SHA, input mismatch, bad mass order and wrong dataset is rejected. Keep the proper separation between `SCOPED_FAIL_OR_UNKNOWN` (physical screen) and `EVALUATION_ERROR` (numeric/infrastructure), with no silent accepted points.

## B: CERN LXPLUS preflight and HTCondor four-job submission
Official source anchors: CERN Batch Docs `https://batchdocs.web.cern.ch/workarounds/job-retry.html`; CERN/Key4HEP Indico 2024 PDF discusses HTCondor and EOS `https://indico.cern.ch/event/1307378/contributions/5729652/attachments/2789482/4864493/fccphysweek24_atd_240130.pdf`; current HTCondor submit file docs `https://htcondor.readthedocs.io/en/main/users-manual/submitting-a-job.html`. Do not assume those historical examples fix a 2026 site config. Check actual `condor_version`, `condor_submit -version`, `python3 --version`, imports `numpy,scipy,jsonschema`, batch OS/CPU, CVMFS, AFS/EOS access, available memory/quota/JobFlavour and auth from the actual lxplus host. All CERN credentials/tokens stay on the CERN host: NEVER copy .keytab/proxy/passwords/tokens into Git or the tarball.
- If SSH to lxplus fails (network, credentials, CERN service outage), record `D7_LXPLUS_ACCESS_BLOCKED` with exact message and STOP; local simulated worker is NOT Condor execution PASS.
- If packages unavailable on worker, use a **documented pinned CERN CVMFS LCG view or environment** selected after real site checks. Avoid guessing `/cvmfs/` release paths or `pip install` from worker nodes. Adjust new D7 worker/setup/submit template with verified environment, record view/OS/Python/Pip SHA and add versioned tests; *getenv=FALSE* intentionally avoids leaking the user's entire submit environment.
- Submit four jobs using a small AFS submit directory, with sandbox file transfer, separate per-job logs. Keep large-scale outputs in EOS only after validating EOS permissions/credentials and an explicit transfer/cleanup policy. No direct `/eos/` paths as scheduler log/error/output, no AFS-intensive per-event logs.
- Stage **after committing the final D7 source** so `git archive HEAD` exactly matches executed code:
```bash
# On lxplus in fresh checkout of feature/zee-d7-lxplus-condor-scan-pilot
bash scripts/zee_d7_stage.sh
cd validation/module9/local/d7_pilot
sha256sum -c bundle.sha256
condor_submit d7_pilot.sub
condor_q
# when finished, inspect condor_history and returned logs/receipts
```
The packaging tool refuses existing directories and embeds source commit+bundle hashes into `manifest.json`; worker verifies a transferred SHA before importing any source; collector validates each receipt's origin. The user's actual CERN project/account quota and job policies take precedence over our template; use resource requests supported on lxplus. Do not use `condor_submit` without knowing which user's account will be billed.

## C: aggregation and physics gate
Collect only from the **real** four worker executions (or explicitly mark local simulation). From lxplus checkout:
```bash
python3 -m module9.d7_collect \
 --manifest validation/module9/local/d7_pilot/manifest.json \
 --shards validation/module9/local/d7_pilot/shards \
 --results validation/module9/local/d7_pilot/results \
 --receipts validation/module9/local/d7_pilot/status \
 --output validation/module9/local/d7_pilot/summary.json
```
Verify 32 distinct inputs/32 returned results, exact shard bytes, worker return statuses, matching source tar SHA and commit, per-job host/runtime/library, zero hidden edits. A `SCOPED_FAIL_OR_UNKNOWN` is NOT a computational failure; zero survivors is a legitimate pilot result. A missing job or `EVALUATION_ERROR` makes `D7_BATCH_PILOT_COMPLETE=false`; never count it as a physics exclusion. For survivors, inverse neutrino target closure is algebraic, NOT a NuFIT likelihood. Do not extrapolate this 32-point developmental cutflow to a model-wide allowed fraction.

Important: site batch may allow use of AFS/EOS or file transfer differently depending on 2026 configuration. The template is NOT proof of runtime behavior. If the full pilot is blocked, report precise environment/permission issue, scoped dry-run evidence and the minimal patch, not a made-up CERN job ID or success.

## D: proof and next publication-directed step
Create a concise `module9/D7_CONDOR_SCAN_AUDIT.md` and `validation/module9/d7_pilot.json` with all real checks, exact staged source SHA, job Cluster/Proc IDs if actually submitted, Python/CERN batch setup, time/memory, 32-point cutflow, scalar and NO residuals, explicit failures/errors, selected heavier mass examples and how many survive. Track `D7_GRID_GENERATION_PASS`, `D7_LOCAL_WORKER_PASS`, `D7_LXPLUS_CONDOR_EXECUTION_PASS/BLOCKED` and `D7_AGGREGATE_PASS/BLOCKED` separately. Missing global gates always UNKNOWN. Do not commit large raw scan input/output/log tarballs; only compact evidence, hashes and reproducible commands.

Then recommend next real D8: expand a **declared, physically motivated** multi-TeV NO+genuine IO scan with efficient scalar screening, representative complex inverse-Yukawa families and full D4 charged decays; conditional Module5 flavor and LFV must remain labeled incomplete. Prioritize potential flavor–collider correlations and backgrounds/reach only after calibrated physical signal selection. Do not implement D8 now or promise EPJC novelty.

Run all focused tests, `git diff --check`. Commit only new D7 files/docs/evidence, push branch `feature/zee-d7-lxplus-condor-scan-pilot`, verify local `git rev-parse HEAD` equals `git ls-remote origin refs/heads/feature/zee-d7-lxplus-condor-scan-pilot`. No new commits to older branches. Report exact SHA, CERN submitted/executed counts and ID if present, tests, scoped survivor count and blockers concisely. If push fails `PUSH_BLOCKED`. 
