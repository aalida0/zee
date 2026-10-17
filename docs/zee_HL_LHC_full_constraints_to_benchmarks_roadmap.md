# HL-LHC Zee H2+- -> H1+- Z: complete-constraint and benchmark roadmap (17 October 2026)

**Scope.** General Zee model with two Higgs doublets and one charged singlet, mixed charged states H1+-, H2+-, heavy production pp -> t(b)H2+- at sqrt(s)=14 TeV, H2+- -> H1+- Z, H1+- -> tb. Run both charge conjugates. HL-LHC illustrative luminosity 3 ab^-1 and high-pileup O(200). Distinguish a *model-independent collider reach projection* from a *physically viable full Zee-model interpretation*. The former can begin while the latter remains incomplete.

**Important topology:** pp -> t(b)H2 -> t(b)(H1 Z) -> t(b)(tb)Z contains **ONE H1**, unlike mu+mu- -> H1 H2 -> H1 H1 Z. Hence pp signal rate uses BR(H1->tb) **once**, not squared. A 4-flavor associated spectator b may be present; 5-flavor gb->tH2 treats it inclusively. Don't mix 4FS and 5FS rates/events without explicit matching.

**Known status of three provisional seeds (not allowed):**

| seed | mH1, mH2 GeV | gamma | R_670 legacy A1V | B3 rank1 included BR(H2->H1Z) | BR(H1->tb) | status |
|---|---|---:|---:|---:|---:|---|
| P2L_0002092 | 300.632,866.992 | 1.18357 | 0.966 | 0.71436082 | 0.99999269 | scalar/EWPO screened; neutrino reconstructed; full flavor/experimental unknown |
| P2L_0000784 | 285.733,748.002 | 1.31096 | 0.9823 | 0.60332851 | 0.99993546 | same |
| P2L_0000654 | 270.126,761.505 | 1.33337 | 0.95055 | 0.59464994 | 0.97813396 | same |

The new 2026 Misiak et al. single-Type-II 670 GeV lower bound (arXiv:2608.29863) does **not** directly apply as a CL to the Zee two-state model. Ratios R_670 from existing A1V are relative **legacy response diagnostics**, not an NNLO matched likelihood. A1V SM is consistently 3.382458e-4; Misiak 2026 SM is 3.54 +- 0.14 e-4. Do not add A1V NP shifts to the modern SM and claim NNLO.

## What counts as a benchmark?

Three separate labels; never infer a stronger label from a weaker one:

- S = **SIMPLIFIED_SIGNAL_REACH_ONLY:** assigned (m1,m2) and rate sigma x BR; model-independent search optimization; **not asserted Zee-allowed**.
- C = **ZEE_CONDITIONAL_SCREENED_NOT_ALLOWED:** scalar mass reconstruction, tree theory and correlated STU plus documented subset of optional calculations; incomplete experimental claims explicitly enumerated.
- A = **FULL_ZEE_CONSTRAINTS_TESTED_CANDIDATE:** physical theory and quark/lepton Higgs constraints checked with *validated* implementations and stated statistical assumptions. Even A means “not excluded by the tested inputs,” not absolute proof of nature; omit “allowed” if any required input is incomplete.

Every row must preserve provenance and report missing tests as **NOT_EVALUATED**, not PASS.

## Full constraints with problem and practical solution

### G0. Model definition and gauge-consistent implementation (BLOCKING)

- Parameters: scalar masses (h125,H,A,H1+,H2+), alpha,beta,gamma, m12^2, singlet quartics lc,k1,k2,k12; complex antisymmetric f and general charged-lepton Yukawa Y in an explicitly documented **Higgs basis**; Type-II-like up/down quark Yukawas and the exact symmetry/alignment assumption.
- **Difficulty:** an exact global Type-II Z2 acting on doublets and all fermions conflicts with unrestricted general Zee lepton Yukawas under naive assignments. Type-II *quark* couplings can be used as a phenomenological flavor alignment ansatz, but one must say how protection survives quantum corrections, or specify a consistent symmetry/spurion/UV completion. Florentino–Romao–Silva 2021 explicitly flags this as an unresolved issue for the joint quark/lepton fit. Other hazards: complex Yukawas vs original real-coupling UFO; theta, gamma and charge conventions, tadpoles, mass eigenstate rotation, and missing interactions.
- **Fix:** freeze one Lagrangian and flavor assumptions, derive field rotations and mixing matrices with an independent symbolic checker, implement/reexport complex-capable FeynRules UFO, compare vertices (H2 H1 Z, H_i tb, H_i nu ell, neutral LFV) and widths against analytic formulas, test gauge/Goldstone and process-level Ward identities where applicable; validate selected channels and charge conjugates against MadGraph and analytic partial widths. If quark alignment is treated as EFT at scale Lambda, state running scale and sensitivity to generated FCNCs.
- **Artifacts:** model_conventions.md, UFO hash and vertex tests, machine-readable parameters. NO experimental “allowed” status before this definition is consistent.

### G1. Scalar theory: spectrum, BFB, unitarity, perturbativity, vacuum (HARD)

- Use existing gate6_benchmark.py for exact mass-to-potential inversion, reconstructed eigenmasses, a **sufficient** BFB test, all implemented tree 2->2 scalar unitarity channels (<8pi), and quartic export.
- **Difficulty:** positivity of quartic and local EW stationary point does not prove **global charge-preserving neutral vacuum**. The Zee cubic charged-singlet/doublet term can create deeper charge-breaking vacua. Large quartics and trilinears can also invalidate loop expansion, and thresholds/RGE may alter stability.
- **Fix:** multi-start numerical minimization of complete tree-level scalar potential over all independent neutral/charged/CP directions after gauge fixing; Hessian eigenvalues; compare all stationary minima by V; for metastable EW vacuum evaluate tunneling/lifetime with a validated bounce solver (not merely |phi| checks). Test with published Florentino examples and independent random seeds. Add an explicit perturbativity margin (not just <8pi), optional 1-loop RG running and chosen cutoff scale; report scale and scheme.
- **Output:** theory_pass, vacuum_global_or_metastable, V_EW_minus_V_min, minimum eigenvalues, unitarity margins, cutoff.

### G2. Electroweak precision + nonoblique vertices (MEDIUM/HARD)

- Existing gateA1h_correlated_stu_ewpo.py computes scalar one-loop S,T,U and screens both Gfitter2026 and PDG2025 correlated 3D Gaussian ellipsoids. This is an implemented approximate screen, not a complete EW fit.
- **Difficulty:** large charged/neutral splittings strongly affect T; oblique summaries depend on assumptions and correlations; model-specific Zbb, Zll, W universality and other vertex corrections may be non-negligible; naively adding M_W likelihood to an STU fit that already uses it double counts.
- **Fix:** retain one well-defined **primary** published covariance/central value with the other as robustness check; add independent scalar vertex corrections if numerically relevant; document reference SM masses, input scheme and assumptions; do not double-count observables.
- **Output:** S,T,U, chi2, fit source/CL and nonoblique coverage status.

### G3. Quark flavor / precision B decays — **highest-risk blocker** (HARD)

- Start with B->X_s gamma at E_gamma>1.6 GeV: modern Misiak et al. (Aug 2026) BR_SM=(3.54+-0.14)e-4, exp=(3.49+-0.19)e-4, single Type-II 95% lower bound ~670 GeV. With the Zee quark alignment convention, at Wilson matching two states contribute through positive doublet weights cos^2(gamma),sin^2(gamma), with individual Type-II functions evaluated at their own masses; include C7,C8 (and required other operators/order consistency).
- Existing A1V validates internally closed legacy b->s gamma response. **R_670<1 for 3 heavier points does not mean “passes b->s gamma”.** No 2026 two-state NNLO result exists in repo.
- **Difficulty:** preserving mixed high/low Wilson contributions; older SuperIso absolute SM != 2026 prediction; heavy-scale matching, RG evolution, perturbative orders, electroweak inputs, complex phases and experimental/theory covariance; naive weighted BRs or adding legacy delta to modern SM are invalid. Type-II ansatz needs to be symmetry protected or FCNC issues rise.
- **Fix:** independently implement/verify **two-charged-state C7,C8 Wilson coefficients at the matching scale** through the order supported by the reference calculation. For a single-state limit decouple one charged scalar to reproduce published modern Type-II rates/bound; reproduce SM normalization and scale variations; integrate both charged contributions *before* RG evolution/observable evaluation with correct operator basis. Document uncertainties and construct actual 95% CL comparison to measured B->Xsgamma (with uncertainties). If NNLO BSM matching cannot be completed, use an appropriately conservative explicitly NLO/theory-uncertainty-labeled flavor *screen*, and never call it a modern 95% CL exclusion.
- Further B/K flavor after b->s gamma: Delta M_Bs,d, Bs->mumu, B->tau nu, B->D^(*)tau nu, b->sll, epsilon_K and relevant charm/kaon observables depending on Yukawa textures/phases. Reuse vetted flavio or an independent published 2HDM calculation **only if the matching and input contract really covers this model**; do not claim a package automatically supports the entire Zee model.
- **Output:** bsgamma_SM_validation, C7,8_NP_at_matching, bsgamma_BSM_order, exp/theory pulls, flavor pass with assumptions.

### G4. Neutrino masses and oscillation fit (EXISTS ALGEBRAICALLY, NOT FULL FIT)

- Existing gateA1b/gateB2 impose one-loop Majorana matrix Mnu = kappa*(f M_ell Y + (f M_ell Y)^T) with antisymmetric f, complex Y, and scalar-dependent kappa. Previous three heavier candidates yielded 200/200 numeric-closure samples each. B2 samples four complex Y-null directions and chooses low **partial** LFV scores.
- **Difficulty:** exact numerical matrix closure to a single hand-picked normal-ordering PMNS target does **not** establish consistency across global correlated oscillation ranges. m_lightest, ordering, deltaCP, two Majorana phases and Yukawa null directions remain incompletely scanned; complex phases matter to LFV/EDM. Neutrino Yukawa conventions must match the UFO exactly.
- **Fix:** read numerical global-fit likelihood/projections (NuFIT 6.1, fit as of Nov 2025) and sample both NO/IO if justified, mixing correlations where provided, m_lightest, delta_CP and two Majorana phases. Use exact Takagi factorization plus matrix reconstruction checks, positivity and perturbativity, constrain cosmological sum mnu as a **dataset/prior-dependent** optional likelihood; compare m_beta and 0nu beta beta where model applicable. Promote f,Y optimization to a *joint* neutrino+LFV+collider objective; do not select minimum ||Y|| solely for algebraic ease. Check running of neutrino parameters if high matching scales are used (Schmidt–Vandeleur JHEP June 2026).
- **Output:** neutrino dataset/version/order, correlated chi2 or permitted samples, max Mnu reconstruction error, masses, phases, f/Y matrices/hash, 0nubb/cosmology assumptions.

### G5. Leptonic LFV / universality (HARD, full likelihood missing)

- Existing B2: coherent selected one-loop charged+neutral scalar dipoles. Existing B5: h/H/A tree l->3l, f-only universality. Existing Barr-Zee fermion-photon subset is explicitly preliminary and incomplete. Existing B3 inserts general f/Y charged-lepton partial widths.
- **Difficulty:** tiny partial-LFV ratios do NOT rule out dominant two-loop Barr-Zee top/W/charged-scalar contributions and full mu->3e or mu->e conversion photon/Z penguin, boxes, scalar operators and interference. Phases and different amplitudes interfere coherently. Some LFV processes bound off-diagonal neutral Yukawas much more strongly than raw charged scalar decays.
- **Fix:** complete gauge-invariant one-/two-loop amplitudes and include W, fermions, charged-scalar and Z exchange, coherent interference, and full mu->3e/ tau->3l / mu->e conversion contributions with validated published 2HDM/Zee limits. Add universality and muon-decay GF extraction, LEP Z->ll/LFV, h125-> e mu, e tau, mu tau, and tau radiative modes. Current example MEG II 2025: BR(mu->e gamma)<1.5e-13 (90% CL); use experiment-specific CL consistently. Validate against known limiting cases and numerical scans; do not sum channel probabilities by hand.
- **Output:** named observables, individual amplitudes, full predicted rates, interference tests, pulls, current dataset/date, lepton-likelihood pass. B2 previous best partial-LFV ratios (P2L_0002092 5.14e-9; P2L_0000784 2.41e-8; P2L_0000654 1.37e-6) are not physical passes.

### G6. 125-GeV Higgs and heavy/charged Higgs constraints with HiggsTools (HARD ADAPTER)

- HiggsSignals: measured h125 production and decays (SM-like rates and STXS), mass, relevant correlations. HiggsBounds: observed direct searches for additional neutral and charged scalars, model-compatible channels. **Use both.**
- **Difficulty:** HiggsTools is not a Zee parameter scanner: supply full HiggsPredictions object with h125, H, A, H1+, H2+, masses, total widths, couplings, partial BRs, hadronic production rates, and cascades. HiggsTools may not encode every charge-changing nonstandard cascade, process acceptance, or model-specific LFV decay. Incomplete widths produce incorrect branching ratios; importing pure 2HDM coupling modifiers misses charged-singlet loops h->gamma gamma and h->Zgamma. HiggsBounds allowed flag means only “not excluded by implemented applicable limits”.
- **Fix:** build a version-pinned Zee -> HiggsPredictions adapter (Higgs.predictions, Higgs.bounds, Higgs.signals, optional Higgs.tools.Input.predictionsFromDict). Unit-test SM decoupling and pure Type-II limit; compare h125 signal strengths and charged/neutral partial widths to an independent implementation; feed both charged particles and all relevant neutral states, physical width/cross-section inputs, plus documented production k-factors; identify unsupported H2->H1Z cascades for manual analysis/recasting. Store selected limiting analysis IDs/observed-to-expected ratios; don't assume every ATLAS/CMS exotic cascade is in HiggsBounds. Also manually recast updated H+->tb, tau nu, W h and h->Zgamma/ LFV searches where relevant.
- **Output:** HiggsTools version/data hash, Signals chi2 and delta chi2 convention, Bounds allowed + selected analysis IDs and ratios, uncovered channels. HiggsTools docs: https://higgsbounds.gitlab.io/higgstools/ ; API and input: /HiggsBoundsAPI.html, /HiggsSignalsAPI.html, /alternative_input.html

### G7. Remaining precision/rare phenomenology (CONDITIONAL but document)

- Scalar electroweak/charged loops: h125->gamma gamma, h125->Z gamma, h125 LFV rates; EDMs (electron/neutron) if complex CP phases; g-2 and electroweak/lepton universality; muon decay and GF consistency; 0nu beta beta constraints and 3-neutrino absolute-mass/cosmology assumptions. Neutrino-lifetime/NSI constraints if relevant.
- **Difficulty:** observable depends on interference, UV phases, conventions and shared measurements. Cosmology bounds strongly depend on model and data combination.
- **Fix:** classify REQUIRED if predicted significant at benchmark and otherwise document explicit justified negligibility. No cherry-picking experimental inputs. Apply independent published amplitudes and consistency tests.

### G8. Physical widths, exclusive branching ratios and perturbative resonance consistency (HARD)

- Existing gate6_width_inventory gives LO included-only scalar/quark channels. Existing B3 replaces Type-II tau nu with general Zee f/Y lepton widths; results for three heavy points H2->H1Z=0.7144/.6033/.59465 and H1->tb=.999993/.999935/.97813 are **conditional**. H2 may also decay to H1 h, W h/H/A, tb, leptons and other kinematically open channels; H1 likewise.
- **Difficulty:** missing QCD corrections, offshell 3-body channels near thresholds, exotic scalar pair channels, double counting W-mediated 3-body decays, incorrect h125 trilinears, missing complex Yukawa/flavor sums, broad widths and propagator interference.
- **Fix:** build complete tree-level 2-body inventory from one UFO and independently compare analytic formulas; add key 3-/4-body off-shell modes where relevant, NLO QCD corrected tb partial widths, explicit completeness of sum of BRs and competing channels, total Gamma/m ratios; check narrow-width approx by comparing factorized full-chain and matrix-element simulations at representative points.
- **Output:** BR_H2_H1Z_PHYSICAL, BR_H1_tb_PHYSICAL, widths, decay coverage, NWA validity, param hashes.

### G9. Direct LHC searches and signal generation (MEDIUM/HARD)

- Do not copy model-independent mass exclusions across decay hypotheses. Compare **sigma(pp->t(b)H_i) x BR(H_i->tb/tau nu/Wh/H1Z)** in same final-state assumptions and production schemes. Search coverage must include h/H/A neutral signatures (tau tau, tt, bb, Zh, hh, etc.).
- For production at 14 TeV: generate pp -> t b H2^- and charge conjugate in **4FS** (associated spectator b resolved) and the appropriate **5FS** gb -> t H2^- inclusive process as a cross-check; do not add them as separate independent rates. Use appropriate heavy charged-Higgs NLO QCD predictions/4FS–5FS matching and scale/PDF uncertainties. Consistently apply Type-II-like quark mixing: heavy H2 doublet fraction sin²gamma in the repo convention; don't multiply its decay rate by the same production factor twice.
- **Difficulty:** 4FS/5FS scheme dependence, NLO virtual loops/UFO complex Yukawa consistency, interference with SM ttbbZ final states, parton shower matching, finite widths, phase space and double-counted b partons.
- **Fix:** initial LO UFO closure and sample pilot, then NLO normalization and uncertainty via validated source; explicit 4FS/5FS envelope, matching; truth-level mass reconstruction, NWA versus complete process on few points.
- **Output:** sigma14_4FS_NLO (or LO clearly labeled), 5FS cross-check, PDF/scale bands, process cards, SLHA/UFO hash, physical fiducial normalization.

### G10. HL-LHC detector analysis, expected limits (START IN PARALLEL AS SIMPLIFIED MODEL)

- Define sigma_vis_core = sigma(pp->t(b)H2+H.c.) * BR(H2->H1Z) * BR(H1->tb). **ONE H1 branching factor**. With Z->ee or mumu multiply by ~0.0673; with one of two top W bosons leptonic (e,mu) and other hadronic multiply approximately 2*0.216*0.674 ~0.291; then detector acceptance and efficiencies. For BR(H2->H1Z)=0.714 and BR(H1->tb)=1, at L=3000 fb^-1, N(onshell Zll before top decays/selection) ~= 144 * [sigma(pp->t(b)H2) in fb]. Requiring exactly one direct W->e/mu and one hadronic top W gives ~42 * sigma_fb truth events. These are *illustrative provisional factors* not a rate prediction (sigma(pp->H2) not computed).
- Primary clean region: Z->ee/mumu + one W->e/mu (3 isolated charged leptons, 2 from Z) + >=3 b tags (+ multiple jets and MET). Complementary Zll+both tops hadronic (2 leptons, high jets/b), and Z->jj + semileptonic top (1 lepton/high multib); assess all in a common fit with disjoint regions. 4FS signal typically offers an additional b vs inclusive 5FS selection; evaluate both.
- Backgrounds: ttZ+jets with extra heavy flavor, ttbbZ (irreducible depending 4FS selection), ttH, tZq+HF, ttW and tt+jets with nonprompt leptons/fake Z, diboson+heavy flavor, possibly tttt. Carefully distinguish ttZ inclusive and ttZbb exclusive samples to avoid overlaps.
- Discriminants: m(top+b) reconstructs H1, m(H1+Z) reconstructs H2; constrain opposite top chain and exploit two-mass relation, 3b/4b tags, top tagger, mass-aware PNN/BDT, mZ and kinematic fit; verify truth assignment/combinatorial closure and data-driven background realism.
- Fast detector: 14-TeV HL-LHC card with documented high pileup (~200), upgraded detector b-tag/lepton assumptions, MET/pileup mitigation and scenario variations; vanilla Run2 Delphes/no-pileup cannot support a realistic HL-LHC sensitivity claim.
- Stats: binned profile likelihood/pyhf, expected background-only 95% CL limits on sigma_vis_core (fb) versus m1,m2, 68/95% expected bands, separately reported expected discovery significance; include b-tag, ttZ+HF modeling, JES/JER, luminosity, pileup, signal scale/PDF, MC statistical nuisance and correlations. Validate closure, Asimov, injection, asymptotics/toys where low counts. Never turn a luminosity-only significance rescale into a detector-level projection.
- **Novelty:** Florentino–Romao–Silva EPJC 81 (2021) 1148 already proposed H2->H1Z LHC benchmarks. Contribution must be an actual HL-LHC full-chain reach with defensible backgrounds, realistic collider assumptions and properly constrained Zee interpretation, not another gauge-coupling benchmark scan. Compare their original P1–P4, 2025 ATLAS H+->tb/Wh/tau nu and newest relevant Run 3 direct searches.

## Benchmark table: columns and acceptance rule

Keep machine-readable per-row, not benchmark-by-benchmark ad hoc text. Suggested minimal columns:

ID; mh125,mH,mA,mH1,mH2 [GeV]; alpha,beta,gamma [rad]; tanbeta,m12sq,lc,k1,k2,k12,mu4; f,Y complex matrix file hash; neutrino ordering and fit version; BFB,unitarity,global_vacuum,perturbative_cutoff; S,T,U,EWPO_covariance_id,chi2; bsgamma BR+uncertainty and order,C7,C8,other quark flavor; NuFIT chi2 and neutrino mass sum; mu->e gamma,mu->3e,mu->e conversion,tau radiative/3body,LFV likelihood; HiggsSignals chi2,HiggsBounds selected limit+ratio; total Gamma1, Gamma2, BR2_H1Z, BR1_tb, branching completeness; sigma14_pp_t(b)H2 [fb]+order+scheme+uncert; sigma_vis_core [fb]; generated 3ab yields Zll and Zhad; expected sigma_vis 95% CL; all constraint statuses, missing tests, code/data versions, param hash, model_convention_ID.

A final *physical* benchmark table needs **>=3 distinct points** if the viable region permits: BP-low mH2 near lowest acceptable flavor contour, BP-high-cascade-BR, BP-best-HL-LHC-yield, and optional BP-alternative neutral spectrum (different mH/mA but same charged masses). Only label as fully tested when missing-critical-constraints count=0.

**Pilot geometry (S-level only, not claimed Zee allowed):** select a sparse 3 x 3 mass grid mH1 in 250,300,350 GeV and mH2 in 700,850,1000 GeV (enforce mH2>mH1+mZ and top threshold), plus published Florentino P1–P4 mass coordinates for comparison. Scan sigma_vis_core as a *free normalization* for expected limits. Use physical P2L_0002092, P2L_0000784, P2L_0000654 **only as provisional C-level parameter points** until all gates pass.

## Roadmap with deliverables, priority and stop criteria

**Track A: collider reach now, without falsely claiming allowed Zee.**
1. Freeze 14 TeV signal topology/4FS vs 5FS and compare to published Florentino final-state proposal.
2. Validate a complex-UFO, mass/width and coupling closure with a tiny 14 TeV production pilot; start with externally assigned sigma_vis_core if full UFO is not ready.
3. Produce quick truth-level Zll trilepton / Zll dilepton / Zhad single lepton cutflow, SM ttZ+HF/ttbbZ benchmarks, reconstruct mH1 and mH2, then upgraded Delphes high-pileup projection.
4. Publishable core endpoint: expected 95% CL exclusion contours on sigma_vis_core(mH1,mH2) (plus optional significance) with defensible systematic variations **regardless of whether any complete Zee benchmark passes**.

**Track B: model-complete physical constraints in parallel.**
1. **G0 model consistency + UFO**: exact scalar-quark-general-lepton conventions and symmetry/alignment assumption, charged/neutral analytic closures.
2. **G3 flavor first**: full modern two-state B->Xs gamma. Preserve A1V as a legacy diagnostic only; add other quark observables. If impossible to implement at adequate order, no fully-qualified allowed benchmarks.
3. **G6 HiggsTools adapter** with fully specified h/H/A/H1/H2 predictions and modern datasets. Iteratively fill G8 widths/cross sections; avoid false passes on missing BRs.
4. **G1 vacuum + G2 EWPO** existing scalar/EWPO screens extended to charge-breaking minimum and relevant vertex effects; perturbativity RG as appropriate.
5. **G4 NuFIT comprehensive neutrino variations plus G5 full LFV**, with fixed-scalar Yukawa optimization. Important: fit **same f,Y** used in complete lepton widths/UFO and Higgs phenomenology; do not join unrelated optimizers' best solutions.
6. **G7 remaining precision/EDM/cosmology** as required by phases; final explicit coverage audit.
7. **G8 complete widths, G9 calibrated 14 TeV cross sections** and finally overlay accepted physical benchmark predictions onto Track A expected limits.

**Stop decisions:** 
- If no fully validated model point exists, present **simplified reach only**, NOT a claim about model viability.
- If 14 TeV model-independent reach fails even for optimistic sigma_vis_core near physically plausible ranges, reassess channel before extensive full fit.
- If physical benchmarks only survive where sigma_vis_core lies far below the HL-LHC expected sensitivity, report model comparison honestly, do not advertise discovery potential.

## Reliable primary external references (check revisions before paper freeze)

- Florentino, Romao, Silva (2021), original off-diagonal-Z charged-scalar LHC signal and explicit no complete lepton-sector fit: https://doi.org/10.1140/epjc/s10052-021-09956-2
- Misiak et al. (submitted 30 Aug 2026), B->Xs gamma precision and 670-GeV *single-Type-II* limit: https://arxiv.org/abs/2608.29863
- HiggsTools official: https://higgsbounds.gitlab.io/higgstools/
- NuFIT 6.1 official (data through Nov 2025): https://www.nu-fit.org/?q=node%2F309
- MEG II mu->e gamma, EPJC (2025), <1.5e-13 at 90% CL: https://doi.org/10.1140/epjc/s10052-025-14906-3
- Herrero-Garcia et al. (2017) full Zee scan: https://arxiv.org/abs/1701.05345
- Schmidt, Vandeleur (2026), RG effects on Zee neutrino parameters: https://doi.org/10.1007/JHEP06(2026)006
- ATLAS H+->tb (2021): https://arxiv.org/abs/2102.10076
- ATLAS H+->Wh (2025): https://arxiv.org/abs/2411.03969
- ATLAS H+->tau nu (2025): https://doi.org/10.1103/PhysRevD.111.072006
- Delphes pileup guide: https://delphes.github.io/workbook/pile-up/
