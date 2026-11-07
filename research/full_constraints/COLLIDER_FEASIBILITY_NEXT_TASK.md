# Next execution — freeze Paper 1 scoped constraints and test 13.6/14 TeV Zee cascade collider feasibility

**Date:** 2026-11-07. **Research branch:** `research/zee-full-constraints`.
**User approval:** proceed with a **bounded collider feasibility pilot and a documented applied-subset constraint methodology**, **NOT** a new parameter-space scan, all-loop calculation or heavy production campaign.
**Read first:** `research/full_constraints/PAPER1_CONSTRAINT_AND_COLLIDER_FEASIBILITY_2026-11-07.md`, `research/full_constraints/PAPER1_FEASIBILITY_REVIEW.md`, `module14/conditional_scan/PRODUCTION_MAP_REPORT.md`, and the LFV/B/Higgs source coverage documents.

## Phase 0 — reproduce existing data, then freeze applied constraint policy

1. Execute and test `python3 research/full_constraints/collider/raw_decay_budget.py` and `python3 -m unittest discover -s research/full_constraints/collider -p 'test_*.py' -v` using untouched source `module14/conditional_scan/production_map_14TeV_families.csv`. Check exact 12 family rows, original source hash, that 14 TeV charge-summed production is used once, and PDG decay factors. Expected **raw, not selected** three-light-lepton yields at 3000 fb⁻¹ are 15591≈306.83–306.92, 2264≈149.10–149.13, 15673≈96.44–96.59.
2. Inspect the **entire** current applied/diagnostic/unknown constraints ledger. Prepare `research/full_constraints/PAPER1_CONSTRAINT_CONTRACT.json` and concise method text for a scoped paper. Implement **no new physical hard veto** from partial LFV, uncalibrated B likelihood, HiggsTools missing widths or unknown vacuum. `global_acceptance=null` always. Distinguish:
   - applied tree scalar/BFB/unitarity/perturbativity/vacuum-positive-certificate and scoped S,T,U, 1-loop neutrino closure;
   - B→Xsγ NLO real/two-state **diagnostic** uncertainty stress;
   - photon-Barr–Zee LFV partial **diagnostic** (including selected texture caveats);
   - only Higgs partial widths and ratios with complete source evidence;
   - totally unassessed `μ-e` conversion and incomplete Higgs searches.
   Put measured input, perturbative order, uncertainty type, status, code/source hash and exact exclusion authority per row.
3. Confirm [2017 JHEP](https://doi.org/10.1007/JHEP04(2017)130), [2021 EPJC](https://doi.org/10.1140/epjc/s10052-021-09956-2) and [ATLAS 2025 trilepton ttll](https://doi.org/10.1140/epjc/s10052-025-14695-9) in the paper's comparison/analysis section. Do not claim first cascade, first neutrino reconstruction or full constraints.

## Phase 1 — **actual available background and generator inventory**, source-bound

4. Check the user's existing 13.6 TeV ATLAS HepMC samples **only if explicitly accessible**, plus any genuine same-energy `ttZ(+heavy-flavor)`, `tWZ`, `tZq`, `WZ` samples. Locate inputs through known runbooks, configured directories and existing manifests, not indiscriminate recursion over user/group storage. For every useful file/dataset record exact energy, production process, scheme/order, generator and shower, PDF, sample size, cross section and filter efficiency, `sumw`, `sumw2`, negative weight fraction, overlap with inclusive/HF components, access path and input SHA256 where affordable. Avoid copying private institutional files into Git or leaking their locations. If missing, use status `NOT_AVAILABLE` and do not invent rates.
5. Check existing pinned MG5 UFO and D14 native production cards / command, actual model scalar ID `15591` and `2264` (option `15673` only if trivial). The 5FS 14 TeV native process is `gb → tH2−` plus conjugate and both incoming orders; hard H2 and tops are stable before decay; do not double-charge or add 4FS spectator b incoherently. Validate that its decay chain matches H2→H1Z→tbZ at the **same scalar/Yukawa card**. Note source 13/14 TeV production rates cannot be substituted for exact 13.6 TeV pilot cross section.
6. Decide the matched-energy path:
   - **Preferred:** if meaningful existing 13.6 TeV background samples exist, make the pilot at **13.6 TeV**, generating signal from the exact saved IDs with `ebeam1=ebeam2=6800 GeV` (or authoritative generator equivalent). All signal and background selections, cross sections, weights and cuts are then at 13.6 TeV. **Do not rescale stored 14 TeV raw yields into sensitivity claims.**
   - **Alternate:** if validated 14 TeV backgrounds *already* exist, use 14 TeV for the pilot; source-bound 14 TeV signal integration is available but signal shower/decays still needed.
   - **Missing backgrounds:** report `BACKGROUND_MODEL_BLOCKED` and stop short of any limit. Do not create expensive fresh background samples or purport a valid CLs.

## Phase 2 — **one small actual event-based feasibility pilot**, only if sources exist

7. User has approved feasibility, not large-scale production. If a valid generator environment exists, generate at most **2 existing-ID signal cards × 2000 events each**, in ignored scratch/data space, with full seed, model/UFO/source/card/process hashes, shower config, decay method, and event statistics; exact cuts/forces and branchings recorded. **Do not run Condor** or launch a high-cost background generation without separate user approval. Avoid reusing 13 TeV `sigma` or spectrum-dependent reweight factors at 13.6. Use the user's already available background HepMC samples **only if applicable**. If only parton-level signal is possible, report truth-level feasibility without fake detector selection.
8. For a Delphes pilot, one consistent Delphes card for all signal/background at the same energy. Initial candidate SR: exactly 3 e/μ with OSSF pair around mZ (±10 GeV), ≥3 b-tagged jets, ≥2 non-b jets, modest MET; reconstruct hadronic top `bjj`, H1 `tb` and H2 `tbZ`. Do not confuse the 5FS 3-decay-b topology with a mandatory fourth hard spectator b. Separate leptonic-top branch and neutrino-pz ambiguity; test mass closure against truth, avoid wishful mass peaks. Alternative two-b region can constrain `ttZ`.
9. Correct normalization is essential: `sum(w)` (including negative weights), `sum(w²)`, filter efficiencies, sample effective luminosity and N_eff per histogram bin. For overlapping `ttZ`+HF/inclusive categories, choose exclusive definitions; do not double count. Show signal/background cutflows with MC statistical error, `m(tb)`, `m(tbZ)`, b-jet multiplicity, pT(Z), HT. Use realistic b-tag/lepton efficiencies supported by the chosen Delphes card, not guessed 5/10% acceptances as measured values.
10. If adequate statistics and actual background normalization exist, **OPTIONAL** simple `pyhf` Asimov multi-bin comparison of signal+background, with explicit ttZ+HF rate/shape nuisance options e.g. 10%,20%,30% **as hypothetical stress**, plus MC stat. Source-bound expected CLs only; otherwise leave `expected_CLs=null`. Even `S/√B` is diagnostic only and not a physical 95% limit. Never claim a 14 TeV reach based on a 13.6 TeV background.

## Deliverable and stop policy

Produce `research/full_constraints/COLLIDER_FEASIBILITY_PILOT_REPORT.md` and small source-bound JSON under `research/full_constraints/collider/`. Record what files/generators were available, exact center-of-mass energy and normalization, whether pilot simulations ACTUALLY ran, yields/acceptance/plots/stat model or explicit null, and a candid **GO/NO-GO** decision for a full collider study or scoped first manuscript. Include signal-family mismatch warning: F13 D12 flavor texture has **no identical D14 LO cross section**.

Frozen Modules0–13, D14 original scan/production cards/data, B/Higgs/LFV original receipts untouched; only isolated study adapters and compact report changes on research branch. No new parameter points, final scan, 14 TeV background fabrication, unbounded two-loop work, Condor, or heavy production. Stop upon absent inputs rather than reusing incompatible samples.

Commit/push validated artifacts to `research/zee-full-constraints`, run syntax/tests/record git status, and report actual evidence. **No automatic scan authorization or global model acceptance change.**
