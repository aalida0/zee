# F14 — 13 TeV physical-unit production-normalized Zee cascade estimate

Source: LHCHXSWG 2016-02-05 Santander-matched Type-II 2HDM heavy charged-Higgs production, original file mflechl_xsec_13TeV_tHp_2016_2_5.txt. Cite LHCHXSWG charged-Higgs guide and arXiv:1507.02549, 1409.5615, 1610.07922.

## AF command

    cd /home/aalida/zee
    git switch feature/global-scan-priority1
    git pull --ff-only
    bash scripts/zee_paper1_F14_LHCHXSWG_13TeV_one_shot.sh

If the original grid is absent, the launcher fetches it from CERN. To override: set environment variable ZEE_LHCHXSWG_13TEV to an absolute local file path. The grid's exact known original SHA256 is 45f9aa7e0f0a117894daaf9364f7e6b2c81e5273de9c50b8f7f593e5261681da. Source-checked real grid has 2484 data points, 36 masses and 69 tanbeta nodes. GitHub Actions run 39608093044 fetched and validated the real file, not only a synthetic test table.

## Numerical method and physical scope

Each of the eight original source-pinned F13 selected benchmark points is joined to the actual optimized neutrino Yukawa/leptonic width result by ID and source SHA. At 13 TeV, the Type-II matched production sigma(mH2,tanbeta) is interpolated in log(sigma) bilinearly in (mass, log tanbeta). Relative down/up uncertainties are interpolated over the same grid coordinates, then multiplied back by the interpolated sigma. Grid holes, duplicates, modified headers and extrapolation are forbidden. This interpolation is a documented numerical choice, not independently assessed LHCHXSWG interpolation uncertainty.

Assuming an aligned Type-II-like quark sector without singlet quark couplings, Zee H2 production is sin^2(gamma) times the official Type-II production. The F13 corrected included-channel cascade proxy already contains sin^2(gamma). The 13 TeV included-channel estimate in pb is consequently:

    R_included = sigma_TypeII_13TeV(mH2,tanbeta) * P_F13_corrected

There is NO additional sin^2(gamma) multiplication. Conditional included-channel BR product is P_F13/sin^2(gamma). These are not complete physical branching ratios: five-state total widths, missing decay channels and precision QCD effects are not fully validated. Production errors only are propagated; there is no branching fraction or EFT/RGE-alignment uncertainty. An approximate Z->ee+mu mu factor of 0.0673 is also output, without detector efficiencies.

The original source-grid charge/conjugate-process normalization has not yet been independently established, so no arbitrary factor of 2 is applied. The input is 13 TeV only; it must not be reused as 13.6 or 14 TeV.

## Approximate results using the rounded benchmark parameters in the chat

F13 ID | official Type-II 13TeV sigma fb | corrected included-cascade estimate fb
--- | ---: | ---:
heavy_0000981 | 1.5341 | 0.5688
heavy_0001330 | 1.6482 | 0.5824
heavy_0000272 | 1.6547 | 0.5546
heavy_0001003 | 1.5680 | 0.5180
heavy_0000238 | 1.8623 | 0.5033
heavy_0003194 | 1.0270 | 0.2377
heavy_0002790 | 2.1762 | 0.4610
heavy_0001692 | 1.6606 | 0.2705

The production-normalized leading point changes from heavy_0000981 to heavy_0001330. Leading central included-cascade estimate is 0.582 fb with about +/-0.084 fb grid production uncertainty. Its included-only Z->e/e+mu/mu estimate is approximately 0.0392 fb. Actual exact F13 values may change the displayed rounding.

## Output

The launcher produces a timestamped folder work/zee_paper1_F14_LHCHXSWG_13TeV_production_*/ containing: eight-model source-checked CSV with Type-II and rescaled Zee production, cascade estimates, production-only uncertainties and Z leptonic decay factor; flavor-best scalar-only control JSON without neutrino fit; and SHA-validated summary and manifest JSON.

This does NOT establish an allowed Zee point, real full signal rate, experimental exclusion, or detector-level reach. Key remaining tasks: full calibrated 2026 two-charged b->s gamma beyond LO Eq4, all LFV amplitudes, modern oscillation likelihood, quark FCNC/RG alignment, HiggsTools, all-field vacuum, complete widths, 13.6/14 TeV current production reference, charge normalization, detector acceptance/background.
