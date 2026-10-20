# Consolidated Zee global scan: Priority 1

Canonical target branch: **feature/global-scan-priority1**. The previous minimal branch was used as a source of functionality; its separate entry point is superseded by the canonical CLI. Do not delete old branches while AF checkouts may still reference them.

## One pipeline entry point

- scripts/zee_priority1_cli.py — B4 scalar candidate CSV and five independently supplied backend exports; all incomplete experimental constraints remain blocked.
- --stream-coverage — reads B4 CSV or JSONL sequentially, disk-backed SQLite uniqueness, atomic source records, no giant point list in RAM.
- --stream-coverage --scalar-physics — calls the original gateB4 scalar_screen and correlated STU ewpo_screen on each COMPLETE twelve-parameter original scalar row. The result is a theory/EWPO screen, never a fully allowed model.
- scripts/zee_priority1_neutrino_gaussian.py — real Takagi/PMNS numerical extraction, NO/IO correlated Gaussian fit when calibrated user data are supplied, not full NuFIT likelihood.
- scripts/zee_priority1_coherent_lfv.py — real complex-amplitude interference when full correct coefficients have been supplied; does not compute missing two-loop diagrams or mu-e conversion.
- scripts/zee_priority1_higgstools.py — actual five-state HiggsTools API adapter, blocked until all physical widths and hadronic mode predictions are complete and mode mapped.

## NEW real calculated subset: E3 optimized f,Y -> B3 LO charged widths

Run on UChicago AF with the exact completed prior E2/E3 source cohorts:

~~~bash
cd /home/aalida/zee
python scripts/zee_priority1_charged_width_export.py \
  --points work/REPLACE_WITH_E2/E2_all_original_B4_no_deeper_witness_NOT_ALLOWED.csv \
  --e3 work/REPLACE_WITH_E3/E3_all_309_multi_neutrino_partial_LFV_diagnostics.jsonl \
  --out work/p1_original_309_B3_charged_included_LO_v1.json
~~~

- SHA verifies the E3 completed 309 original model source, exact ID/mass/Yukawa association with original E2.
- Recalculates the actual B3 general-Zee leptonic H1 and H2 LO widths after exact neutrino matrix reconstruction, replacing obsolete Type-II tau-nu from Gate6 while retaining the Gate6 INCLUDED LO boson and tb modes. Numerically closes sums and derived cascade included-channel fractions.
- Produces a real, source-referenced partial decay stage export, but the canonical HiggsTools adapter MUST reject it as a complete input: no neutral-H/A widths, missing charged physical channels, off-shell and QCD, no physically complete branching ratios.
- A new 309-point runtime computation has NOT been claimed until actually executed on AF.

## NEW actual-generator production input (not generation)

~~~bash
python scripts/zee_priority1_production_lhe.py \
  --runs work/your_existing_actual_MG5_run_manifest.json \
  --out work/p1_actual_MG5_partial_production_v1.json
~~~

Manifest format is JSON:
~~~json
{"runs":[{"candidate_id":"B4_0004143","state":"H2","mode":"pp_to_H2_tb","lhe":"/home/aalida/zee/work/MG5_run/Events/run_01/unweighted_events.lhe","process_card":"/home/aalida/zee/work/MG5_run/Cards/proc_card_mg5.dat","parameter_card":"/home/aalida/zee/work/MG5_run/Cards/param_card.dat","generator":"MG5_aMC","model":"actual_original_UFO_model_name"}]}
~~~

The program reads **actual LHE init XSECUP** subprocess cross sections (in pb) for proton beams at 13, 13.6 or 14 TeV; hashes the original LHE, process/parameter cards, and preserves subprocess-reported errors. It never guesses rates, does not invent missing processes, and does not infer a physically complete five-state production model. A validated consistent Zee UFO, external generation, rate cross checks, PDF/scale uncertainties and physical HiggsTools mode coverage are still missing.

## Recommended one-shot AF validation

~~~bash
cd /home/aalida/zee
git fetch origin
git switch feature/global-scan-priority1
git pull --ff-only
bash scripts/zee_priority1_one_shot.sh
~~~

This reruns original feature contracts and numeric regressions, plus seven new source/streaming/charged widths/LHE regressions. CI synthetic/regression success does NOT imply the full E3-E7 physics campaign was recomputed.

## Missing Priority-1 research-grade calculations

1. Modern full matched Zee two-charged B->Xs gamma rate (NLO/NNLO), theory uncertainty and proper experimental likelihood.
2. Exhaustive one- and two-loop Zee LFV, nuclear mu-e conversion and independent amplitude/operator validation.
3. Calibrated NO/IO oscillation experimental likelihood with free neutrino parameters, not just a Gaussian proxy.
4. Complete h/H/A/H1/H2 partial/total widths including off-shell/QCD channels and independent mode mapping.
5. Actual validated hadronic cross sections across relevant LHC channels, with complete production-mode coverage and scheme/PDF/scale uncertainties.

**No model is certified allowed or excluded, and no complete physical HiggsBounds run is yet possible.** This merge creates one coherent engineering foundation without manufacturing missing physics.
