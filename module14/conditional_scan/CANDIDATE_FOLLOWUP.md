# D14C targeted production and bounded vacuum follow-up — 2026-11-06

**TARGETED_PRODUCTION_EVIDENCE_AVAILABLE**

Three actual local MG5 integrations at **13 TeV** are executed and independently
validated. The original 225-point dataset, original gates, Modules 0–13,
original D14 worker/evidence and flavor research branch are unchanged. No large
scan, new flavor calculation or HTCondor job was launched. This status describes
production evidence, not model acceptance. Physical B→Xsγ remains **UNKNOWN**;
`global_acceptance=null` throughout.

## Exact starting sample and coverage

The immutable AF dataset was read over SSH and copied to
`/tmp/zee-d14c-dataset.json`. Its SHA256 is
`2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9`,
matching the already verified summary. This follow-up does not recollect the
20k/225 receipts. `candidate_export.py` verifies the full dataset's existing
collection identity and all **900** original family records: point IDs, full
scalar cards, scalar/module2-input/target hashes, module2 source provenance,
F/D/Ye/Ye2 hashes, NO/IO closure/status, every gate-detail digest, complete D4
channel inventory/totals/source/SM bindings and independent D3 cascade width.
It performs no scalar/neutrino/decay-worker rerun.

Derived counts: 225 points; vacuum PASS 33 and UNKNOWN 192; nominal flavor
APPROX_COMPATIBLE 77 and APPROX_DISFAVORED 148. The PASS/nominal-compatible
intersection has **16** points, none below 1 TeV. The separate sub-TeV
UNKNOWN/nominal-compatible intersection has **six**: 3582, 3821, 6850, 11920,
13512, 17671. The 148 nominally disfavored points are not physically excluded.

Auditable tables (one scalar row with four families in JSON, four rows per
scalar in CSV):

- [CERTIFIED_VACUUM_APPROX_BSG_16.json](CERTIFIED_VACUUM_APPROX_BSG_16.json)
  and [CSV](CERTIFIED_VACUUM_APPROX_BSG_16.csv).
- [SUBTEV_UNKNOWN_VACUUM_APPROX_BSG_6.json](SUBTEV_UNKNOWN_VACUUM_APPROX_BSG_6.json)
  and [CSV](SUBTEV_UNKNOWN_VACUUM_APPROX_BSG_6.csv).
- [candidate_followup.json](candidate_followup.json) contains the derived
  counts, both tables, separate bounded vacuum evidence, mapped-card provenance,
  60 independent amplitude checks, actual generator rates, artifact hashes and
  all 12 family-specific production contract hashes.

The LFV records remain PARTIAL, with omitted amplitudes explicitly retained.
HiggsTools remains DIAGNOSTIC_ONLY, with heavy-neutral searches and charged
production channels NOT_EVALUATED in the original output. Only H2 production is
added here: the original HiggsTools contract needs H1 and H2 rates and has not
been rerun. Missing production for the other 19 shortlisted scalar points
remains null, never zero. No updated original gate is implied by a separate
diagnostic or by a production contract.

## Executed model-matched production

The expected local runtime was initially absent. Read-only inspection recovered
the original D6 assets under
`/home/amine/zee/workspaces/zee-production-d6/validation/module8/local`.
Copies were staged into this checkout's ignored `validation/module8/local`;
the original workspace was not changed. All 827 relevant official MG source
files plus its launcher were compared byte-for-byte to the SHA-pinned official
3.6.7 archive. The native UFO files, SARAH model/mapping sources, LHAPDF 6.5.6
library/source archive and member-0 PDF bytes match D5 hashes. Only the copied
`lhapdf-config` absolute prefix was relocated; before/after hashes are retained.

Every point/family card is constructed with unchanged `native_card`,
`external_values` and LHA serialization from D4/D5. All scalar masses, mixing,
reconstructed quartics/cubic and complex family Yukawas are mapped; this is not
a mass substitution into a 700-GeV card. All native couplings are evaluated for
finiteness, scalar closure is checked, and both signed tbH2 chiral coefficients
and conjugates are checked against the actual frozen UFO vertices.

Unchanged D5's independent two-diagram Dirac trace and Ward test are compared
to actual MG/ALOHA amplitudes for all 12 cards at original gamma, zero,
±pi/2 and minus-original-gamma: **60 cases**, both charges each. The original
amplitude is identical across each point's four families. Both chiral quark
coefficients carry the same `-sin(gamma)` projection; the matrix tests confirm
the sin²(gamma) relation including signs/endpoints at fixed mass/Yukawas.
No Type-II table or energy rescaling is used. Cascade mixing has its separate
sin(2gamma) behavior and vanishes at zero and ±pi/2.

The three fresh process directories use exactly:

```text
generate g d3 > u3 hm3 QCD=1 QED=1
add process g d3bar > u3bar hm3c QCD=1 QED=1
add process d3 g > u3 hm3 QCD=1 QED=1
add process d3bar g > u3bar hm3c QCD=1 QED=1
```

Native hm3 is H2−; hm3c is H2+. Both charges and both incoming beam orders
are counted once. This is LO **5FS** gb-associated production; no 4FS contribution
is calculated or added. There is no mixed-pair production approximation here.
Beams are 6500+6500 GeV, PDF NNPDF30_lo_as_0130 member 0, ID 263000,
five PDF flavors, LO interpolated PDF alpha_s with alpha_s(MZ)=0.130.
muR=muF1=muF2=mH2, fixed per integration. Yukawa masses use the frozen D4
one-loop running prescription at mH2 with its separate alpha_s(91.1876)=0.118
and existing threshold prescription. They remain independent of massless
u/d/s/c/b hard kinematics; mt,kin=172.4 GeV.

| Original ID | muR=muF [GeV] | mt,Y [GeV] | mb,Y [GeV] |
|---|---:|---:|---:|
| 15591 | 1035.70370662 | 144.73153429 | 2.631443924 |
| 2264 | 1165.97481528 | 143.76999305 | 2.613961612 |
| 15673 | 1277.36328727 | 143.04135807 | 2.600713897 |

H1/H2/top widths are zero in the hard process, Z width is the mapped 2.4952
GeV, and all other external/default inputs remain bound in the full cards.
Seed 4154, 5000 requested unweighted events per point; integration sample counts
are 148894, 148444 and 134606. No shower, detector cuts or detector acceptance
is applied. The validator reuses D5's cut/PDF/statistics checks, independently
checks the new energy/scales, rederives every LHA entry from the actual family,
checks banner/original/normalized cards, generator version, process charges and
beam orders, native result/log/banner agreement, and retained source snapshots.
Madevent's on-disk seed reset to zero is explicitly checked against its banner.

| ID | Actual sigma LO [pb] | Native integration error [pb] | Tree two-body BR range | sigma × tree BR [pb], four families |
|---|---:|---:|---:|---:|
| 15591 | 0.011868 | 0.000021971 | 0.32603376–0.32606529 | 0.003869369–0.003869743 |
| 2264 | 0.0050014 | 0.0000088007 | 0.36864862–0.36865774 | 0.001843759–0.001843805 |
| 15673 | 0.0029876 | 0.0000059189 | 0.39375325–0.39378663 | 0.001176377–0.001176477 |

The ordering is 15591, 2264, 15673 within the identical energy/process/order/
charge/PDF/scale prescription. The JSON/CSV gives each family BR, rank, sigma,
proxy and propagated **integration-only** proxy error separately. These are
complete on-shell **tree two-body** BRs, not higher-order physical branching
fractions. No H1 decay, Z/top/W BR, acceptance or luminosity factor is included.
The small family spread is model-input dependence, not an uncertainty estimate.

Exactly three central integrations were run. **Seven-point scale sensitivity is
NOT_EVALUATED**, PDF uncertainty UNKNOWN, and theory sigma null. No 13.6/14-TeV
rate was substituted or inferred. A later scale study would keep the central
Yukawas frozen and use scale pairs (muR,muF)/mH2 = (1,1), (1/2,1/2),
(1/2,1), (1,1/2), (1,2), (2,1), (2,2), with the central result shared.
It requires separately validated new integrations and is not run by this pilot.
Even a measured LO envelope would not supply a full NP theory sigma.

## Bounded vacuum result and triage

The actual immutable gate details show only the D10 sufficient certificate;
the original D14 worker did **not** execute witness searches. All six original
gate hashes and certificate blockers are retained. UNKNOWN is not instability.
For 3582, 6850 and 13512 only, unchanged D10 Gram-orbit SLSQP is run with
192 deterministic random starts plus seven fixed singular/charged/CP/EW starts,
seed 20261106+ID, the existing norm-root bound 12, maxiter 500 and ftol 2e-13.
Full ten-field gradients, Hessian/transverse modes and gauge Ward checks reject
spurious stationary candidates. A deeper credible candidate would require
the existing 80-digit independent stationary polish before a FAIL label.

| ID | Starts | Optimizer success | Full-space credible runs | Outer-bound hits | Lowest credible DeltaV/v^4 | Separate result |
|---|---:|---:|---:|---:|---:|---|
| 3582 | 199 | 199 | 4 | 0 | +3.24e-17 | UNKNOWN |
| 6850 | 199 | 199 | 7 | 0 | 0 | UNKNOWN |
| 13512 | 199 | 199 | 3 | 0 | -5.27e-17 | UNKNOWN |

Credible-run counts do not count distinct gauge orbits. These depths agree with
EW within floating precision; there is no verified deeper stationary witness.
All three sufficient certificate reattempts fail the residual Gram positive
definiteness condition, which is not necessary for stability. No PASS is issued.
The SLSQP implementation reports clipped intermediate steps for two points;
final full-space/boundary checks, rather than optimizer flags, determine witness
credibility. The searches do not cover the full field domain.

The existing exact radial-exclusion certificate applies to 3582 only:
sqrt(x+y+s)>=30097 GeV implies V>=0>V_EW. Its canonical radius is about
172.87 v, well outside the finite search region; the interior is unresolved.
The same sufficient radial bound is unavailable for 6850 and 13512. Their
null bound is not absence of compactness or a stability verdict. The other
three points (3821,11920,17671) have triage-only NOT_EVALUATED searches and
unchanged UNKNOWN vacuum status. No lifetime, loop/RG/thermal or global Zee
acceptance statement follows.

## Decision and optional next proposal

The 1.0–1.3 TeV region has a measurable conditional LO cascade proxy in these
three integrations. Point 15591 has the largest proxy despite its smaller BR;
ranking BR alone would reverse the useful ordering. These three points also
vary tanbeta/mixing and the lighter spectrum, so they establish neither a
universal mass trend nor an optimum or exclusion boundary. The six lighter
points remain unresolved and have no new production calculation here.

A future conditional sample can prioritize this window while retaining lower
masses and controls. [next20k_proposal.json](next20k_proposal.json) is a separate,
**unexecuted** recommendation: seed 20261107, count 20000, shard_size 250;
10000 proposals at mH2=1000–1350 GeV, 6000 at 500–1000 GeV, and 4000 broad
controls at 500–2200 GeV. It copies the existing conditional proposal's other
ranges, tanbeta=1–15 and correlated open-Z margin, without fitting a flavor
threshold or promoting UNKNOWN vacua. The allocation is a sampling choice,
not a model-volume probability. No candidates, shards or Condor package have
been generated from it. Production scale/PDF/higher-order robustness and all
unresolved physics gates still limit interpretation of any future sample.

## Reproduction and retained artifacts

Raw cards, compiled-source snapshots, native logs/results/banners/events and
receipts remain ignored under `validation/module8/local/d14c`. They are actual
executed artifacts, not committed binaries/logs or synthetic proof files. The
full per-run hashes, card hashes, 60 matrix results, source mapping, validator
hash and original dataset hash are committed in `candidate_followup.json`.
Each scalar result is bound to four files named `MODULE2_INPUT_SHA256.json`
under `validation/module8/local/d14c/production`, using the strict
[AF_COMMANDS.md](AF_COMMANDS.md) schema and real copied artifacts. These family
cards share the actual scalar-level receipt; they do not assert four independent
generator integrations. The original HiggsTools H1/H2 interface remains separate.

Read/re-export on this host, without new physics integrations:

```bash
python -m module14.conditional_scan.candidate_export \
  --dataset /tmp/zee-d14c-dataset.json \
  --production validation/module8/local/d14c/validated_production.json \
  --vacuum /tmp/zee-d14c-vacuum-01.json \
  --output /tmp/zee-d14c-review-export
D14C_DATASET=/tmp/zee-d14c-dataset.json \
  python -m unittest discover -s tests -p 'test_module14_conditional_*.py' -v
python -m unittest discover -s tests -p 'test_module1_d10_*.py' -v
python -m unittest discover -s tests -p 'test_module8_*gates.py' -v
git diff --check
```

To reproduce from scratch, use a fresh checkout of this branch with no
`validation/module8/local` directory, and copy the immutable dataset from its
recorded AF path (verify its SHA above). Supply a read-only D6 local-assets
directory containing the pinned native/MG/PDF/LHAPDF assets; a random MG/model
installation cannot replace it. Commands below execute at most these three
points, sequentially; they never submit jobs. Keep matrix generation in ignored
local/ because MG/PLY writes parser caches in its working directory.

```bash
python -m module14.conditional_scan.candidate_export \
  --dataset /tmp/zee-d14c-dataset.json --output /tmp/zee-d14c-base-export
python -m module14.conditional_scan.candidate_vacuum \
  --candidates /tmp/zee-d14c-base-export/candidate_followup.json \
  --output /tmp/zee-d14c-bounded-vacuum.json
python -m module14.conditional_scan.targeted_production stage \
  --source-local /home/amine/zee/workspaces/zee-production-d6/validation/module8/local
python -m module14.conditional_scan.targeted_production map \
  --dataset /tmp/zee-d14c-dataset.json
REPO="$PWD"
( cd validation/module8/local/d14c
  PYTHONPATH="$REPO" python -m module14.conditional_scan.targeted_production matrix )
python -m module14.conditional_scan.targeted_production run --point 15591
# After reviewing the first native integration, the other two finite probes:
python -m module14.conditional_scan.targeted_production run --point 2264
python -m module14.conditional_scan.targeted_production run --point 15673
python -m module14.conditional_scan.targeted_production validate \
  --dataset /tmp/zee-d14c-dataset.json
python -m module14.conditional_scan.candidate_export \
  --dataset /tmp/zee-d14c-dataset.json \
  --production validation/module8/local/d14c/validated_production.json \
  --vacuum /tmp/zee-d14c-bounded-vacuum.json --output /tmp/zee-d14c-new-final
```

Fresh runs have new artifact hashes and statistical errors; the committed
rates are the actual original executions, not exact deterministic predictions.
If the pinned assets are absent, stop at PRODUCTION_PENDING and provision them
manually; do not invoke the fixed-mass D6 runner on these arbitrary cards.
Validation and export refuse inconsistent hashes and existing output directories.

Validation performed: the final D14 suite passes **43 tests with no skips**,
including all 20 conditional tests with the full dataset and retained native
artifacts. Nine unchanged D10 tests and four unchanged D5 native-gate tests
also pass. `git diff --check` passes.
