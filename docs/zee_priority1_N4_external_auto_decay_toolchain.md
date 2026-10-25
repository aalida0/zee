# P1 N4 — full Zee model generator first, not another partial-width gate

## Why we changed direction

The completed AF N3 309 models found H->hh partial widths of 0.0011–0.0703 GeV for eight priority spectra. H->AA is closed. Source N2 gauge modes were much larger (e.g. A->H1 W both charges =10.55 GeV for B4_0004143). Every sample still returns HiggsBounds=0 and 309 BLOCKED_DECAY_CHANNEL_COMPLETENESS. It is inefficient to write every new tree final-state calculation by hand.

### External tool audit

ScannerS 2 (arXiv:2007.02985) is a parameter scanner for implemented extended scalar models, not an out-of-the-box fully general Zee charged-singlet+2HDM decay tool. It can be extended with an additional model, but it is not a solution to the missing gauge-invariant amplitudes.

MadGraph/MadWidth (arXiv:1402.1178) computes two-/three-body tree-level widths from a complete LO UFO and correctly matched model card. HiggsTools (higgsbounds.gitlab.io/higgstools) evaluates experimental Higgs constraints from validated rates, masses and total widths; it does not generate missing amplitudes. FlexibleDecay/FlexibleSUSY (arXiv:2106.05038) can compute automated scalar widths with several higher-order SM-like corrections in models which have correct SARAH/FlexibleSUSY implementations. The existing Type-II Zee FeynRules source is a faster entry route for initial LO MadWidth cross checks; a separate SARAH model would need a substantial implementation.

## Critical finding in the original public Zee UFO

Original Yang/Wu Zee-Model (https://github.com/YangPhy/Zee-Model) has all three neutral and two charged states, and Z H1 H2. Its original quark sector is not Type II and lacks tb H1/H2. Our existing Gate7 Type-II FeynRules patch added quark Yukawas and a local user workstation previously exported an LO UFO.

However the original UFO defines THREE f_ij and NINE Y_ij lepton Yukawas as real external parameters. This is **not compatible** with general complex Yukawa solutions in original E3. Discarding their imaginary parts is not allowed. A correct physical scalar-potential mapping between Yang/Wu Higgs basis and original E2 Florentino P2 basis is ALSO required before using any physical benchmark.

## What is newly implemented on feature/global-scan-priority1

- scripts/zee_p1_prepare_complex_flavor_feynrules.py: starting ONLY from the existing previously Type-II modified FeynRules source, creates a fresh variant in which 3 antisymmetric f and 9 charged-lepton Y inputs are complex, represented by 24 independent real/imag external SLHA parameters. Original gauge-invariant Lagrangian intact. Four blocks: ZEEFR, ZEEFI, ZEEYR, ZEEYI. Requires fresh Mathematica/FeynRules UFO export and fresh QCD NLO counterterms if NLO is ever needed. Nothing is built on /data.
- scripts/zee_p1_e3_complex_flavor_fragments.py: source-verified ORIGINAL completed E2/E3 309 optimized neutrino Yukawas -> 309 complete flavor SLHA *fragments* (not full parameter cards). All 24 entries retained, original hashes preserved, antisymmetry and finite values verified. Complex coefficients never silently discarded.
- scripts/zee_p1_ufo_model_audit.py: checks source UFO Python via AST without executing it, ensures charged/neutral states, off-diagonal Z and tb charged vertices, 6 charged W neutral vertices, charged pairs and the 24 split-complex flavor parameters. An original real-only or TypeII vertex-free UFO fails. Static success does NOT certify mass/cubic-basis mapping or Ward identities.
- scripts/zee_p1_madwidth_driver.py: generates true documented MG5 compute_widths for 25/225/226/227/228 using path=real-param-card output=separate-card body_decay=3. Optionally runs actual MG5 if supplied a binary, parses genuine output SLHA DECAY tables and source hashes, and never claims a matched physical E3 model or all-orders width.
- scripts/zee_p1_N4_complete_decay_generator_preflight.py: orchestrates the actual previous source-verified original 309 E3 complex fragment generation and derived TypeII complex FeynRules source if present on AF.

## One current AF command

~~~bash
cd /home/aalida/zee
git switch feature/global-scan-priority1
git pull --ff-only
bash scripts/zee_p1_N4_auto_decay_one_shot.sh
~~~

New output directory (refuses overwrite):
/home/aalida/zee/work/p1_auto_decay_full_ufo_N4_20261020_v1/

This exports actual 309 source-matched complex f/Y card fragments; if /home/aalida/zee/models/Zee_TypeII_FR exists, creates its complex-flavor derived FeynRules source within the output. The earlier source may only exist on the user's LOCAL Mathematica workstation; if missing on AF, the report will say so, and does NOT pretend to have a UFO. No hardcoded uncertain physical mass or trilinear mapping is inserted.

## Next full-model steps

First export the derived FeynRules model on a machine with Mathematica/FeynRules, using our existing scripts/gate7_export_typeii_ufo.m. Example environment inputs are FEYNRULES_PATH, ZEE_FR_SOURCE and ZEE_UFO_OUTPUT; set them to the actual local paths and run math -script scripts/gate7_export_typeii_ufo.m.

After exporting and transferring the UFO to AF /home, audit it with the following (replace path with actual):
~~~bash
python scripts/zee_p1_ufo_model_audit.py \
  --ufo /home/aalida/zee/work/Zee_TypeII_Complex_LO_UFO_v1 \
  --out /home/aalida/zee/work/Zee_TypeII_Complex_LO_UFO_v1_audit.json
~~~

Then perform the hard physics check: map the original E2 scalar quartics, beta, alpha, gamma, singlet portal, soft term and masses into Yang/Wu Higgs-basis parameters and validate masses, all charged/neutral trilinears, lepton amplitudes/CKM and gauge Ward identities at fixed identical benchmark. The model input parameter cards must be fully reconstructed and independently verified before interpreting any MadWidth rates as the original E3 model. The tree generator is not equivalent to QCD-corrected loop widths, complete neutrino/LFV, modern matched B->Xs gamma or physical hadronic cross sections.

## Current incomplete constraints

Modern NNLO two-charged Zee b->s gamma, complete Barr–Zee LFV and mu->e conversion, a calibrated full neutrino oscillation likelihood, the fully mapped and validated five-state physical decay totals, and all HiggsTools production predictions remain unfinished. N4 deliberately does not fabricate a full-model allowed/excluded verdict.
