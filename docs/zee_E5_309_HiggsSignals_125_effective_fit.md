# E5 — 309 original Zee spectra in REAL HiggsSignals, 125 GeV effective-coupling approximation

**Status:** Source and synthetic contract tests committed to GitHub; actual UChicago AF \`HiggsTools\` / \`HSDataSet\` execution not yet performed. Do NOT refer to this as a complete Zee HiggsSignals fit or experimentally allowed-model population.

## Motivation from uploaded E4H and alignment audit (20 October 2026)

All **309/309** E3 optimized original scalar/Yukawa configurations passed E4H *direct 125-GeV LFV reference screens* (largest \`R_h\` 4.8119e-5). The reason is that the neutral Higgs coupling to off-diagonal lepton pairs is suppressed by both mixing and the optimized Y:

\[
 C_h=\cos(\beta-\alpha)M_\ell/v-\sin(\beta-\alpha)Y^\ell .
\]

Yet the user independently found from the exact E2/E4H source rows:

- \(|\beta-\alpha|\) = min/median/max \(0.002006/0.048256/0.169219\) radians;
- \(\kappa_V\) = \(0.985717/0.998836/0.999998\);
- \(\kappa_b\) = \(0.017646/0.718072/1.041909\);
- **258/309** have \(|\kappa_b-1|>0.1\).

This demonstrates that a near-SM hVV coupling does not guarantee SM-like 125-GeV branching fractions in the Type-II-like quark ansatz: \(\kappa_b=\cos(\beta-\alpha)+\tan\beta\,\sin(\beta-\alpha)\). No arbitrary \(\kappa_b\) cut should be made: the correct test is the correlated Higgs signal-strength \(\chi^2\).

## Scope of this implemented E5

\`scripts/zee_gateE5_309_h125_higgssignals_effective.py\` uses the actual Python \`Higgs.predictions\` and \`Higgs.signals\` libraries **plus the user-selected real HiggsSignals JSON dataset**:

- Check exact 309-completed E2/E3/E4H source/manifest SHA, per-spectrum E3 optimized \`Y^\ell\`, and the full E4H direct LFV partial widths.
- Recompute the *physical* neutral tree-level lepton-coupling matrix \(C_h\) from unmodified \`gateA1d_neutral_tree_lfv.scalar_couplings()\` (via D5). The **diagonal** \(\kappa_e,\kappa_\mu,\kappa_\tau\) are COMPLEX and set individually relative to their SM Yukawas, preserving non-SM diagonal lepton couplings (not using \(\kappa_b\) for \(\tau\) or double-counting LFV).
- Use the original Type-II-like quark \(\kappa_u=\kappa_t,\kappa_d=\kappa_b\) and \(\kappa_W=\kappa_Z=\cos(\beta-\alpha)\), to build \`NeutralEffectiveCouplings\` for a single neutral \`BsmParticle("h125",charge="neutral",cp="even")\` with \(m_h=125\) GeV.
- HiggsTools effectiveCouplingInput computes rates and non-LFV widths from its built-in SM reference, including the *SM particle* top/bottom ggH and W/fermion hgamma-gamma amplitude dependence, using its default \`calcggH=True, calcHgamgam=True\`.
- Inject the three E4H independently validated exact tree LFV partial widths via \`h.setDecayWidth("emu" / "etau" / "mutau", \Gamma)\` **AFTER** effectiveCouplingInput. HiggsTools automatically recomputes the total width and all BRs. Strictly assert \(\Gamma_{\rm new}=\Gamma_{\rm effective}+\Gamma_{e\mu}+\Gamma_{e\tau}+\Gamma_{\mu\tau}\) within roundoff.
- Compute the **true HiggsSignals C++ chi2** \(\chi^2_{\rm E5,approx}\) from \`HS.Signals(dataset)(pred)\` using the user's experimental dataset and its correlation model. Evaluate the exact SM effective couplings with *the same* 125 GeV and HS dataset for a reference \(\chi^2_{\rm SM}\). Report \(\Delta\chi^2=\chi^2_{\rm E5,approx}-\chi^2_{\rm SM}\) as a **descriptive conditional fit statistic** only.
- Reuse a single \`HS.Signals\` instance for all 309 points, record loaded observable count and SHA256 of **all dataset JSON files** and code binaries' module paths, and checkpoint each model after its calculation. \`--resume\` disallows altered source/dataset/script.
- Retain the full 309-point fit table (masses, kappa, full effective width and BRs, absolute chi2, delta vs the same SM). No global CL, "allowed", "excluded" or ad hoc \(\Delta\chi^2\) significance.

### IMPORTANT limitations (all source-recorded, no hidden defaults)

1. **Not yet a complete Zee HiggsSignals/HiggsBounds calculation.** Charged eigenstates \(H_{1,2}^\pm\) contribute to \(h\to\gamma\gamma\) and \(h\to Z\gamma\) at one loop via scalar cubic couplings. Those trilinears and loop amplitudes have NOT been independently validated in the present repository. E5 uses HiggsTools effective W/top/bottom approximation only; \(\kappa_{Z\gamma}=1\) is a provisional reference. Do NOT claim the full hgamma-gamma rate is physical.
2. Heavy neutral \(H,A\) and \(H_{1,2}^\pm\) are not passed to HiggsBounds. Their full decays, widths and production are still missing. This E5 only fits the 125 GeV signal-strength measurements and cannot rule out heavy-scalar parameter points by other searches.
3. Differential production STXS acceptance changes beyond inclusive HiggsTools effective rescaling are not modeled.
4. The strict Type-II quark ansatz alongside general Zee lepton Yukawas has unproven radiative symmetry protection and matched RGE threshold consistency.
5. HiggsSignals global chi2 includes many channels and correlated measurements: \(\Delta\chi^2\) relative to the fixed SM is **not** automatically a chi-square distributed test statistic with 1,2 or 3 degrees of freedom, nor a global p-value or physical exclusion criterion.
6. The dataset must be versioned. Public HSDataSet currently shows a 2023 main revision even though HiggsTools code itself has a **September 2026 v1.3 release**. Do not claim it contains all 2026 measurements unless checked and updated.

Upstream data:
\`work/zee_E2_complete_395_original_vacua_20261020_v1\`,
\`work/zee_E3_309_multiroot_flavor_optimized_20261020_v1\`,
\`work/zee_E4h_309_direct_h125_20261020_v1\`.

## One AF setup + one full 309-point HiggsSignals run

HiggsTools Python bindings and the HSDataSet must genuinely be available in the **same** Python interpreter used for E3/E4H. The repository does not ship or fake either external dependency.

If \`import Higgs.predictions\` already works and you have a versioned HSDataSet, skip installation. Otherwise install official HiggsTools in a separate /home source checkout and use its official data:

\`\`\`bash
# All source/build work is under /home; no code executed from /data.
mkdir -p /home/aalida/tools
cd /home/aalida/tools
git clone https://gitlab.com/higgsbounds/higgstools.git
cd higgstools
git checkout v1.3
cd /home/aalida/zee
source .venv-flavor-f1/bin/activate
python -m pip install /home/aalida/tools/higgstools
python -c 'import Higgs.predictions as HP; import Higgs.signals as HS; print("HiggsTools imports OK")'

# Install separately versioned measurement data. 'HS.Signals' recursively
# loads JSON beneath the given root; record the dataset revision.
git clone https://gitlab.com/higgsbounds/hsdataset.git \
  /home/aalida/tools/hsdataset
git -C /home/aalida/tools/hsdataset rev-parse HEAD
\`\`\`

If installing on a login node is restricted, use a proper AF compute allocation. This is a normal local build and may require CMake/C++ and Python dev headers. Do NOT alter the preexisting .venv flavor packages unnecessarily; consider an isolated compatible virtual environment retaining the scientific dependencies.

Then the E5 tests and full 309 campaign:

\`\`\`bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source .venv-flavor-f1/bin/activate
set -o pipefail

python -m py_compile \
  scripts/zee_gateE5_309_h125_higgssignals_effective.py \
  tests/test_zee_gateE5_309_h125_higgssignals_effective.py
python -m unittest discover -s tests \
  -p 'test_zee_gateE5_309_h125_higgssignals_effective.py' -v

python -u scripts/zee_gateE5_309_h125_higgssignals_effective.py \
  --e2-dir work/zee_E2_complete_395_original_vacua_20261020_v1 \
  --e3-dir work/zee_E3_309_multiroot_flavor_optimized_20261020_v1 \
  --e4h-dir work/zee_E4h_309_direct_h125_20261020_v1 \
  --hs-dataset /home/aalida/tools/hsdataset \
  --output-dir work/zee_E5_309_h125_HiggsSignals_effective_v1 \
  2>&1 | tee work/zee_E5_309_h125_HiggsSignals_effective_v1_run.log
\`\`\`

Do not use the wrong HiggsSignals-2 API or an invented gaussian nuisance likelihood. E5 explicitly demands the modern \`Higgs.predictions\` Python module and a directory with actual experimental JSON files. An unavailable package/dataset fails closed rather than returning fabricated chi2 values.

If interrupted use identical input/HS dataset/script and append \`--resume\`. All outputs under \`/home/aalida/zee/work\`.

Output:

\`\`\`text
work/zee_E5_309_h125_HiggsSignals_effective_v1/
  manifest.json
  E5_309_checkpoint.jsonl
  E5_309_h125_conditional_HS_chi2_NOT_ALLOWED.jsonl
  E5_309_ranked_conditional_h125_HiggsSignals_NOT_ALLOWED.csv
  summary.json
\`\`\`

The headline \`summary.json\` reports 309 HiggsSignals **conditional effective-model** evaluations, exact SM reference chi2 on the same data, range/median delta chi2 and source fingerprints. Physically allowed Zee models remain **UNKNOWN**.

## Key references

- [HiggsTools HiggsPredictions effective-coupling API](https://higgsbounds.gitlab.io/higgstools/EffC_Refs.html): distinct complex fermion diagonal couplings and \`effectiveCouplingInput()\`, with SM-like top/bottom/W loop approximations.
- [HiggsTools particle partial-width API](https://higgsbounds.gitlab.io/higgstools/Particles.html): setting LFV \`setDecayWidth("emu",...)\` readjusts total width and other BRs.
- [HiggsSignals API](https://higgsbounds.gitlab.io/higgstools/HiggsSignalsAPI.html): \`Signals(dataset)(Predictions)\` returns correlated HiggsSignals chi2.
- [Official HiggsTools releases](https://gitlab.com/higgsbounds/higgstools/-/tags); [HSDataSet](https://gitlab.com/higgsbounds/hsdataset).

### Critical next steps to convert E5 into a physical Higgs fit

Implement and independently validate \(g_{hH_1^+H_1^-},g_{hH_2^+H_2^-}\) from the full Zee gauge-invariant scalar potential; compute charged-scalar loop amplitudes (including normalization and heavy-mass decoupling) for \(h\to\gamma\gamma,Z\gamma\); model complete diagonal/non-diagonal Higgs leptonic partial widths and Higgstools+heavy scalar HiggsBounds predictions; validate 125 rates against an independent 2HDM limiting benchmark at identical quark/Yukawa convention. Only then consider an actual exclusion prescription and joint global constraints with B→Xsγ, complete LFV and EWPO.
