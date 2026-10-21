# Paper 1: executable Florentino-region feasibility campaign (21 October 2026)

## One command on UChicago AF

```bash
cd /home/aalida/zee && git switch feature/global-scan-priority1 && git pull --ff-only && bash scripts/zee_paper1_scan_one_shot.sh
```

This command first compiles the new source and runs the seven small structural/physics-interface tests, then **starts the actual scan**. It writes live progress and per-spectrum checkpoints in a uniquely timestamped `work/zee_paper1_florentino_pilot_*Z/` directory. It produces a saved terminal summary and a ranked CSV. To increase statistics, pass scanner flags through the launcher, e.g. `--scalar-steps 3000 --trials 300 --max-spectra 30 --optimize-evals 600`, without editing source. The default is deliberately a 240-proposal/6-scalar/50-Yukawa-trial scoped physical feasibility campaign.

## Data provenance and fallback

The launcher autodiscovers `work/**/E2_all_original_B4_no_deeper_witness_NOT_ALLOWED.csv` and checks its SHA256 against the original E2 report, including the actual 309 no-deeper-tree-witness cohort count and explicit NOT-ALLOWED status. If multiple copies differ, it stops rather than arbitrarily mixing physics sources. With no E2 archive, it constructs a **new**, transparently source-inspired Florentino Table-2 P2 scalar seed with `mH1=300`, `mH2=700`, `beta=1.394`, `gamma=1.089`, `k12=0`. This is **not** an exact paper Table-2 benchmark or a globally allowed model. Supply `--seed-csv /home/.../E2_all_original_B4_no_deeper_witness_NOT_ALLOWED.csv` if autodiscovery is ambiguous.

## Actual calculations executed

1. Real B4 correlated scalar proposals: reconstruct physical scalar mass matrices/quartics and check existing sufficient BFB, 2->2 tree unitarity, correlated Gfitter/PDG S,T,U screens. Archive all accepted screened *bins*, explicitly NOT model-allowed; seed and code digests are saved.
2. Select six mass/mixing-diverse high-LO included-channel cascade geometries.
3. Real B2 neutrino fit **to the historical fixed central NO target matrix** (not a modern likelihood): exact linear solution with rank-five operator, antisymmetric f null-direction choices and four complex Yukawa null dimensions. Over 50 trials per spectrum by default; retain complex real/imag independent components and reject nonperturbative or nonclosed Yukawas. This tests algebraic existence, NOT NO/IO oscillation likelihood/cosmology.
4. Optimize the strongest saved LFV-subset seeds with the existing D2 Powell objective in four complex Yukawa homogeneous directions plus real f scale. Recompute the source one-loop and fermion-photon Barr--Zee partial amplitude combinations and five neutral-scalar tree trilepton subset channels, with 240 max evaluations per local seed by default.
5. Recompute general-Zee e/mu/tau charged-scalar widths with B3 **at exactly the optimized same scalar/f/Y**. Replace the deprecated Type-II tau-neutrino width in the included-channel LO inventory. Save the resulting two cascade *included-channel* fractions and doublet-weighted geometry proxy.
6. Compare the source scalar upper proxy against the same-scalar solution's lepton-width-corrected **included-channel** proxy. This is NOT a physical pb rate, a full branching ratio, a CL exclusion, or an unbiased global optimum.
7. Source SHA and per-point JSON checkpoints, ranked CSV, status, completeness limitations.

## Outputs

- `manifest_start.json`: source, seed class, hashes, random seed, attempted scan launch;
- `new_B4_scalar_EWPO_NOT_ALLOWED.csv`: newly screened scalar points;
- `selected_scalar_spectra_NOT_ALLOWED.csv`: diverse scalar cases injected into neutrino;
- `point_01_NOT_ALLOWED.json` etc.: actual optimized complex f/Y, neutrino mass closure, partial LFV channels and charged included-channel widths, missing stages;
- `ranked_florentino_injection_NOT_ALLOWED.csv`: same-scalar before/after lepton inclusion, but **not a pb cross section**;
- `summary.json`, `manifest.json`: source hashes, counts, missing physics and explicit `paper1_GO_or_NOGO: null`.

## Why this DOES NOT complete full Paper 1 viability

Existing modules do not provide a certified modern two-state **NNLO-consistent inclusive** `B->Xs gamma` observable with BSM theory uncertainty and a comparable reference likelihood; complete charged/neutral widths, 5-state HiggsTools inputs, hadron rates (4FS/5FS), full LFV including W/Z/charged-scalar Barr--Zee, boxes and mu-e conversion, and proper NuFIT 6.1 phase/IO likelihood also remain incomplete. New scalar points lack paired full 26-RGE Yukawa trajectories and all-field vacuum certificate. The general lepton + Type-II-like quark texture requires finite alignment/FCNC validation.

These are substantive theoretical/computational tasks, NOT a missing Python wrapper or failure of the scan launcher. Our present command starts and finishes an actual **numerical feasibility screening** but cannot honestly provide final allowed/excluded Zee conclusions or publication-ready rate contours. A green test is not independent higher-order physics validation.

## Scientific GO/NO-GO once missing physics is validated

Only a fully consistent source benchmark passing measured neutrino+LFV+quark flavor+global vacuum+all Higgs exclusions, with complete `pp->tbH2` production and proper cascade branching fractions, can qualify as a model-allowed candidate. Then compare the real maximum `R_tbZ` envelope against the scalar-only Florentino baseline. One surviving point is a prerequisite, not publication novelty. Strong new exclusion/correlation or a new quantitatively significant collider envelope is a conditional Paper-1 GO; negligible change relative to 2021 is standalone Paper-1 NO-GO. Never transfer single-charged Type-II 670 GeV mass bound directly to mixed Zee model.

## Literature

- Herrero-García et al. JHEP 2017, arXiv:1701.05345.
- Florentino, Romão, Silva EPJC 2021, arXiv:2106.08332.
- Primulando, Julio, Uttayarat EPJC 2022, arXiv:2201.01960.
- Heeck & Thapa PLB 2023, arXiv:2303.13383.
- Schmidt & Vandeleur JHEP 2026, arXiv:2512.17235.
- Lopes, Milagre, Silva, general singlet/doublet unitarity, arXiv:2510.02434.
