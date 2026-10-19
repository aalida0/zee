# F1 — One large real flavio/wilson observable calculation for 27 Zee spectra

**Status as coded, 2026-10-19:** runnable implementation committed on branch \`gateA1p-independent-hepfit-typeii-matching\`, **not yet executed on AF**. NO allowed/excluded Zee benchmark is asserted. Avoid any use of the unreviewed 2026 Misiak et al. normalization.

## Published physics choices

**Primary peer-reviewed framework:**
- Misiak et al., PRL 114, 221801 (2015), doi:10.1103/PhysRevLett.114.221801 (arXiv:1503.01789). Their SM inclusive branching ratio at \`Egamma > 1.6 GeV\` is \`(3.36 ± 0.23)×10^-4\`, and Eq.(10) gives the **linearized** high-scale (\`mu0 = 160 GeV\`) response \`BR ×10^4 = 3.36 - 8.22 ΔC7 - 1.99 ΔC8\`. Eq.(10) is used **only as a derivative normalization/basis sign test**, not as the NP observable itself.
- Hermann, Misiak & Steinhauser, JHEP 11 (2012) 036, doi:10.1007/JHEP11(2012)036. Analytic high-order Type-II matching formulae underlie the E4A source-pinned coefficients. The original 2012 matching and the E4A SuperIso source have KNOWN unresolved C3–C6 NNLO discrepancies; don't pass those coefficients to another code as if fully validated.
- Misiak & Steinhauser, EPJC 77, 201 (2017), doi:10.1140/epjc/s10052-017-4776-y. The *published full NNLO* single-Type-II conservative charged mass bound around 580 GeV (95% CL, their choice of experimental R_gamma average and Feldman–Cousins interval) is a **historical target but NOT reproduced by this program**, and NEVER a per-eigenstate Zee bound.

**Actual public numerical observable source inspected:**
- \`flavio/physics/bdecays/bxgamma.py\`: https://github.com/flav-io/flavio/blob/master/flavio/physics/bdecays/bxgamma.py ; quadratic Wilson-rate response \`P0 + αs Kij^(1) + αs² Kij^(2)\` (the latter partially populated), nonperturbative terms and nuisance \`delta_BXsgamma\`. The file explicitly cites Misiak 2015 and says some input arrays came via private communication. It is NOT proven to reproduce arbitrary new-physics FULL NNLO corrections.
- \`flavio/physics/bdecays/wilsoncoefficients.py\`: https://github.com/flav-io/flavio/blob/master/flavio/physics/bdecays/wilsoncoefficients.py ; uses the **non-effective** WET \`C7_bs\`, \`C8_bs\` inputs at the high scale, then creates \`C7eff_bs\`, \`C8eff_bs\` from \`C3..6\` at the low scale. DO NOT double rotate to effective basis.
- \`wilson\`: https://github.com/wilson-eft/wilson ; high-scale to bottom-scale RG evolution under \`WET/flavio\`. The WET \`C7_bs\`/\`C8_bs\` convention must be verified numerically by differentiating the *full* flavio observable versus \`ΔC7, ΔC8\` and comparing with the 2015 Eq.(10) coefficients.
- \`EOS\`: https://github.com/eos/eos/blob/master/eos/rare-b-decays/inclusive-b-to-s-gamma.cc ; a useful genuinely separate NLO inclusive implementation, but it has NOT been integrated as a runnable comparator in this F1 commit. Do not claim EOS cross-validation.
- SuperIso E1: old source-pinned physical BR, **comparative only**; differences in scheme, baseline, higher orders and missing pieces are NOT absorbed by recentering.

The code uses the actual \`flavio.np_prediction("BR(B->Xsgamma)",wc)\` and \`wc.set_initial({"C7_bs": ΔC7, "C8_bs": ΔC8},160,eft="WET",basis="flavio")\` for each point. The charged NP inputs are the **LO** E4A \`light_NP\` and \`heavy_NP\` at order zero and operator C7/8, combined before RG at fixed physical gamma. It NEVER inserts NNLO E4A raw C3-C6, never sums BRs or grafts 2020/2026 SM central values. This constitutes **LO BSM matching + published-era observable with quadratic response and selected higher-order terms**, not the complete NLO/NNLO Type-II/ Zee prediction.

## The ONE integrated F1 test/run

**Outputs:** \`summary.json\`, \`F1_27_Zee_flavio_hybrid_LO_NP.csv\`, \`F1_18_TypeII_flavio_hybrid_LO_NP.csv\`.

Included validations:
1. Exact source identity: read all 648 E4A source-pinned entries / 27 Zee spectra, require completed E4A 216-source-call/5184 coefficient bookkeeping and verify matching superposition of every 24-entry original vector. Optional E1 hash check against E4A stored E1 ancestry.
2. \`flavio\` SM prediction near 2015 \`(3.36 ± 0.23)×10^-4\`. *Numerical acceptance envelope:* \`0.20×10^-4\` reflecting upstream flavio's own test on master; not a claimed 1σ reproduction.
3. Finite-difference derivative \`dBR/dC7\` and \`dBR/dC8\` near the SM point in the SAME WET scheme; compare signs and magnitudes with peer-reviewed 2015 Eq.(10) \`-8.22×10^-4\` / \`-1.99×10^-4\` (25% deliberately conservative check tolerance). The source check is not a calibrated truncation error.
4. Nine pure Type-II benchmark masses 300,450,550,600,650,670,700,800,1000 GeV at both \`tanbeta=5.6\` and 50, each using actual E4A LO delta C7,C8. Constructive sign and decoupling tests, with no 580 GeV exclusion reproduced/claimed.
5. Twenty-seven original physical Zee spectra, each with pure H1 endpoint, pure H2 endpoint, physical gamma mixed prediction, and exactly degenerate-doublet-weight closure. Track full quadratic Wilson interference rather than affine BR interpolation.
6. Compare independent legacy E1 physical BRs, *displayed side by side* with no cross-scheme subtraction used to generate physical predictions. The 2015 absolute SM \`3.36±0.23\` and current exp \`3.49±0.19\` enter ONLY a labeled diagnostic Gaussian distance (error-only or experimental plus assumed 2015 SM theory error); 2015 theory ±0.23 may not capture additional mixed-order charged-Higgs uncertainties. **No 95% confidence labels or model exclusions permitted.**
7. If the SM normalization/basis derivatives/TypeII constructive limits fail, output status \`F1_OBSERVABLE_OR_BASIS_VALIDATION_FAILED_NO_EXCLUSION\` and exit nonzero, but retain a summary and source diagnostic CSVs.

**Single large regression:** \`tests/test_zee_gateF1_single_integrated_flavio_observable.py\` tests the *entire 27 + 18 logic* with a deterministic synthetic quadratic observable and deliberately corrupted source & Wilson sign. Passing this fast test **is not evidence of actual flavio numerical performance**. The real AF command below separately runs external real libraries.

## Confirmed Python dependency incompatibility (October 2026)

A real AF attempt failed during **import of flavio**, before running the original 27 model sample, with `FileNotFoundError ... site-packages/particle/data/particle2022.csv`. This is not an E4A input failure and not a physics rejection. `particle` 1.0.0 removed PDG2022 tables, while `flavio` 2.7.1 still attempted to load them. Cross-checked source-pinned compatible combination:
- `flavio==2.7.0` (published March 2026) declares `particle>=0.21.0`.
- `particle==0.26.2` (April 2026) has `particle2022.csv` and `nuclei2022.csv` in its packaged data tree.
- `flavio==2.7.1` (June 2026) declares `particle>=1.0.0`; DO NOT just force an incompatible particle pin under that version.

Inside `.venv-flavor-f1`, install:
```bash
python -m pip install "flavio==2.7.0" "particle==0.26.2"
python -m pip check
python - <<'PY'
import flavio, particle, wilson
print("flavio",flavio.__version__, "particle",particle.__version__)
print("SM",flavio.sm_prediction("BR(B->Xsgamma)"))
PY
```
Then re-run the F1 real physics calculation with a **fresh** output directory. The 27 lines from `test_zee_gateF1_single_integrated_flavio_observable.py` are SYNTHETIC test fixtures, not Zee physical predictions.

## AF setup and ONE execution

Use a clean venv under **/home** (not /data) and system Python 3.12 where possible, because your active Key4hep Python 3.13 and its \`LD_LIBRARY_PATH\` may conflict with wheel packages:

\`\`\`bash
cd /home/aalida/zee
git pull --ff-only

/usr/bin/python3.12 -m venv .venv-flavor-f1
source .venv-flavor-f1/bin/activate
python -m pip install --upgrade pip
python -m pip install 'flavio==2.7.0' 'particle==0.26.2' 'wilson'\npython -m pip check
python -c 'import flavio,wilson; print("flavio",flavio.__version__,"wilson",getattr(wilson,"__version__","unknown"))'

python -m py_compile \
  scripts/zee_gateF1_peerreviewed_flavio_27_observable.py \
  tests/test_zee_gateF1_single_integrated_flavio_observable.py
python -m unittest discover -s tests \
  -p 'test_zee_gateF1_single_integrated_flavio_observable.py' -v && \
python -u scripts/zee_gateF1_peerreviewed_flavio_27_observable.py \
  --e4a-summary work/gateE4a_large_matching_typeII_27_v1/summary.json \
  --e1-summary work/gateE1_joined_27_legacy_bsgamma_v1/summary.json \
  --output-dir work/gateF1_flavio_peerreviewed_LO_matching_27_v1
\`\`\`

If the environment has conflicting libraries, in the same terminal run \`unset LD_LIBRARY_PATH PYTHONHOME PYTHONPATH\` **before** activating the new venv; this does not alter the pinned physics inputs in already-completed E4A/E1. Set up and install package sources only once. Future runs should save \`python -m pip freeze\`, \`git rev-parse HEAD\` alongside source hashes.

**What success means:** F1 demonstrates that an open-source code actually returned physical **historical-scheme hybrid** BR predictions for all 27 source-pinned Zee spectra, and that these predictions have correct 2015 SM and LO C7/C8 basis behavior plus plausible Type-II mass dependence. They will be suitable for provisional flavor diagnostics and a further accuracy/uncertainty study. **Not** an independently reproduced 2017 Type-II >580GeV 95% limit. The credible model-viability result requires stronger matching/observable accuracy, physics-complete model inputs, and a statistically justified likelihood.

If F1 data or tests fail, send complete console error and report. Do not bypass independent derivative or SM checks merely to force completion.
