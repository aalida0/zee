# Conditional D14 scan readiness — 2026-11-06

**CONDITIONAL_SCAN_READY_REMOTE**

The optional sidecar reuses the validated ordinary LO two-state matching,
published 2026 linear Eq.(4), D3 cascade kernel and complete D4 tree two-body
decays. Original workers, acceptance, Modules 0–13 and historical evidence
are unchanged. No scan jobs, HTCondor submissions, new flavor backends or
production integrations were launched. The authors have already been
contacted without a reply; this work adds no further outreach or uncertainty
literature search.

## Phase 0: actual AF evidence

SSH to the configured `uchicago` host succeeded. Existing AF files were
read, not inferred from local summaries. Both batches were collected with
the **original collector extracted from their saved source archive** into
fresh immutable reports:

- `/data/aalida/zee/d14_heavy_20k/conditional_audit_20261106.json`
- `/data/aalida/zee/d14_heavy_physics_225/conditional_audit_20261106.json`

Both reports are `COMPLETE`, with respectively 80/80 and 9/9 shard/result/
receipt triples and `missing_points=0`. Source commit:
`d45f179870fa93fabe9bc137b753cdfd2cf0478f`; source archive SHA256:
`d73b7028d30a726f846829c1a27318e46c260f97d9f40913f08a87f651db7bd0`.
The archive commit header and all **402 source file hashes** were independently
compared to this commit using local `git archive`. Both batches use the same
archive hash. Receipt worker hashes match archived code. Collection verifies
manifest records, settings, source identity, input/output hashes, all expected
family records and neutrino input/target/seed identities. Saved job stage flags
were also checked. Receipts attest to recorded bytes/settings, not an
independent attestation of the execution host.

Both use config SHA256
`293085452732c2a91287dc3edbcde5b96e6d326966ff40f6412e030d9116e19f`.
Manifest SHA256 values:

- 20k: `44eb985d387b950c8f774590728c12d02ef857da76f2d6b4b33f1f9f316d5c88`
- 225: `190b9c566795c6956e18e729bc2c2c4ee386f83ce9d1a74a85a1e209f7f165c3`

[remote_audit.json](conditional_scan/remote_audit.json) freezes the actual
reports, settings, configurations, per-shard hashes and arm counts.
The 225 manifest retains original point IDs, cards and config provenance.

| Stage | 20,000 proposals | 225-point follow-up |
|---|---|---|
| Reconstruction | 20,000 PASS | 225 PASS |
| BFB | 2,977 PASS; 16,015 FAIL; 1,008 UNKNOWN | 225 PASS |
| Unitarity | 4,476 PASS; 15,524 FAIL | 225 PASS |
| EWPO | 10,771 PASS; 9,229 FAIL | 225 PASS |
| D10 sufficient vacuum certificate | 33 PASS; 192 UNKNOWN; 19,775 NOT_EVALUATED | 33 PASS; 192 UNKNOWN |
| Aggregate scalar status | 33 PASS; 19,734 FAIL; 233 UNKNOWN | 33 PASS; 192 UNKNOWN |
| NO closure/perturbativity, 2 families/point | 450 PASS; 39,550 NOT_EVALUATED | 450 PASS |
| IO closure/perturbativity, 2 families/point | 450 PASS; 39,550 NOT_EVALUATED | 450 PASS |
| D4 complete tree two-body tables, both orderings | 900 PASS; 79,100 NOT_EVALUATED | 900 PASS |
| Partial LFV, both orderings | 900 DIAGNOSTIC_ONLY; 79,100 NOT_EVALUATED | 900 DIAGNOSTIC_ONLY |
| D9B legacy rate | 20,000 NOT_EVALUATED | 225 DIAGNOSTIC_ONLY |
| HiggsTools, both orderings | 80,000 NOT_EVALUATED | 900 DIAGNOSTIC_ONLY |
| Model-matched production | NOT_EVALUATED | NOT_EVALUATED |

There are no recorded ERROR outcomes. Stage counts are not a sequential
cutflow: scalar tests overlap, BFB UNKNOWN can stop neutrino reconstruction,
and vacuum certificate failure is not a physical vacuum FAIL. NO/IO targets
are NuFIT6.1 secondary best-fit coordinates with deterministic inverse-family
provenance and a perturbativity limit sqrt(4 pi), not a joint fit likelihood.
Partial LFV omits W-gamma/other amplitudes. HiggsTools' approximate h125 fit
omits charged-scalar loop effects; charged production and complete heavy-neutral
channels remain NOT_EVALUATED. No missing input becomes a zero rate or PASS.

## Phases 1–2: conditional flavor and cascade workflow

`flavor.py` calls unchanged C1 `make_contract` and `run_contract`: ordinary,
real, unprimed, top-only alpha_s^0 matching at 160 GeV, with coherent
cos²(gamma)/sin²(gamma) contributions before a single Eq.(4) evaluation.
There is no NLO injection, SM-baseline rescaling or separate 670 GeV cut.
Complete original scalar cards and an explicit top/scale/scheme/provenance
card are mandatory. The supplied reference is mt_MSbar(160)=
163.96892236746697 GeV, inherited from C1/C2's pinned HyperIso LHA, not
recalibrated to the 2026 SM fit. Input cards, hashes and contribution splits
are retained.

The predeclared reference sensitivity uses
`pull=(10^4 BR_linear - 3.49)/sqrt(0.14^2+0.19^2)`, symmetric Gaussian
quoted errors, rho=0, and **no NP error estimate**. The absolute-pull reference
threshold is 1.959963984540054, with a fixed ±0.01 pull boundary band.
Labels are APPROX_COMPATIBLE, APPROX_DISFAVORED and APPROX_BOUNDARY;
they are conditional-only references, not validated 95% CL tests or hard gates.
The code rejects invalid/incomplete inputs rather than fabricating a label.

The existing 225 outputs were joined without rerunning their workers:

| Original proposal arm | Original proposals | Follow-up points | APPROX_COMPATIBLE | APPROX_DISFAVORED |
|---|---:|---:|---:|---:|
| heavy_700_1100 | 6,000 | 134 | 19 | 115 |
| heavy_1100_1500 | 6,000 | 66 | 41 | 25 |
| heavy_1500_2000 | 6,000 | 24 | 17 | 7 |
| broad_control | 2,000 | 1 | 0 | 1 |
| Total | 20,000 | 225 | 77 | 148 |

There are no boundary points in this fixed sample. These counts describe
proposal-dependent screening, not a model-space volume or exclusion fraction.
All 225 physical B classifications remain **UNKNOWN**; every row retains
`np_theory_sigma=None`, `bsg_exclusion=None`, `globally_allowed=None`.
Method robustness is **NOT_EVALUATED**: no EOS/SuperIso/NLO reruns or
invented method sigma were needed. The separate research branch was fetched
and its M2026 route/results/handoff read without merging or editing it.
It still supplies no validated Zee NP uncertainty. Its older unsent-outreach
wording is superseded by the user's already-contacted/no-reply instruction.

The complete dataset is stored immutably on AF at
`/data/aalida/zee/d14_heavy_physics_225/conditional_dataset_20261106.json`,
SHA256 `2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9`.
[remote_conditional_summary.json](conditional_scan/remote_conditional_summary.json)
retains complete scalar cards, matching inputs/splits, per-point reference
results, gate assessments/detail hashes and 900 family provenance/status/BR
records. Full gate/width/family records remain in the hash-addressed remote
dataset. Every remote flavor row was also reproduced numerically with the
final local adapter (relative tolerance 1e-13, absolute tolerance 1e-15;
all classifications identical). AF Python 3.9 and local Python 3.10 differ
at floating-point rounding level; these tolerances are not physical accuracy
bounds. Both executed and final adapter source hashes are recorded.

Cascade checks enforce ordered masses and the open on-shell Z channel.
The coupling vanishes exactly at gamma=0 and ±pi/2; these endpoints and
threshold closure are tested. Full D4 channel inventories, totals, scalar/
Yukawa/SM/source hashes and the independent D3 partial width are checked
before using a BR. The 900 AF family BRs span 0.0444692–0.805150 within
the complete **on-shell tree two-body** scope. Off-shell/loop corrections
and decay uncertainties remain uncomputed.

**Zero rows are ranked**, because no same-point documented production was
supplied. No partial width was used as a BR or yield. The workflow accepts
explicit same-point production cards with hashed artifacts and groups ranks
by energy, process, charge definition, order, PDF and scale scheme. It computes
sigma×BR only with complete widths and documented production. No 13/13.6/14
TeV substitution is allowed. Candidates retain the label “Conditional
benchmark requiring further flavor/vacuum/LFV validation.”

## Phase 3: readiness and next manual scan

[followup_config.json](conditional_scan/followup_config.json) preserves the
original correlated generator, seed 20261106, and a 3:3:2 allocation over
sub-TeV (mH2 500–1000 GeV), higher-mass (1000–2000 GeV) and broad-control
(500–2200 GeV) arms. The first two use gamma 0.15–1.4; the broad arm keeps
both signs and wider neutral/misalignment/soft ranges. The original open-Z
20 GeV margin remains. No tolerance or sampling range was fitted to produce
a lighter-mass reference survivor.

The real local pilot generated and evaluated 16 proposals (6/6/4 by arm),
then repeated workers serially versus two shards. All 16 fail BFB; downstream
neutrinos/widths remain NOT_EVALUATED. This small sample does not establish
the efficiency of a new scan. A separate 100-point committed-config control
reproduced the original two scalar-screen survivors, one vacuum PASS and one
UNKNOWN, with eight complete family decay tables and partial LFV. Neither
control survivor passes the nominal reference comparison; no physics
exclusion follows. Both pilots reproduce generation bytes, serial/split worker
bytes, sidecar rows and arm cutflows. No production was fabricated.

[pilot_summary.json](conditional_scan/pilot_summary.json) freezes configs,
collection results, stage counts, examples, resources and source/data hashes.
Scratch manifests/results/receipts and full local datasets remain under
`/tmp/zee-conditional-pilot-final-20261106`. Local source receipts explicitly
say LOCAL_UNSPECIFIED; the final source hashes, rather than a false committed
bundle identity, describe these development runs.

[AF_COMMANDS.md](conditional_scan/AF_COMMANDS.md) gives exact original-run
recollection, sidecar, small-pilot and manual follow-up preparation/submission/
collection commands. The new 20k configuration is prepared for manual use,
with 80 shards, 1 CPU/2 GB RAM/2 GB disk per job. It has **not been launched**.

Validation: 9 conditional workflow tests plus the unchanged D14 tests (32
total), and 11 frozen C1 tests pass. Tests cover the frozen numeric reference,
coherent splitting, reference boundaries, missing/nonfinite inputs, gamma
endpoints, threshold closure, real original-card family joins, incomplete or
duplicate collections, wrong source, decay inventory/binding, documented
production and separate energy ranks, and deterministic arm/shard generation.
`git diff --check` passes. Only the new optional sidecar, conditional tests
and this readiness report are changed.

Remaining limitations prevent a final fully constrained result: unknown
joint nonlinear flavor response/NP uncertainty, 192 unresolved vacuum
certificates, incomplete LFV/HiggsTools coverage, absent production, and
uncomputed higher-order/off-shell decay effects. They do not prevent a
reproducible conditional scan workflow. This readiness label implies no
publication-level or global Zee acceptance.
