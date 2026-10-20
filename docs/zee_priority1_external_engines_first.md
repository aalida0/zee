# Zee Priority-1: external-physics-first toolchain (2026-10-20)

**Canonical development branch:** `feature/global-scan-priority1`. All E2/E3/previous N1–N4 outputs remain immutable. An installed package is NOT evidence that the five-state Zee model is implemented or experimentally allowed.

## Why package-first rather than more hand-derived channels

The completed N3 original 309 calculation added very small `H->hh` widths (e.g. B4_0004143 0.006477 GeV; H included sum 6.764956 GeV). N2 `A->H1 W` and other gauge modes were far larger. Do **not** continue indefinitely appending manually computed decay channels. Use a model compiler and compare **two separately defined Lagrangians**.

## Physics responsibilities and acceptance gates

| Workstream | Primary engine | Independent check | Required PASS evidence |
|---|---|---|---|
| Full general Zee Lagrangian, two charged states, complex f/Y | **SARAH** non-SUSY model; explicit Type-II quark ansatz | Existing **FeynRules** Type-II+complex-f/Y source | Scalar potential, mass eigenvalues/Goldstones, all mixing matrices, Yukawa/phases, gauge/charge-conjugation Ward checks |
| Spectra, RGEs, two-body decay modes | **SARAH-generated SPheno** | **FlexibleSUSY**, run for identical matched parameter point | Spectra, pole vs running schemes, thresholds, dominant tree partial widths |
| Scalar decay precision | **FlexibleDecay** | SPheno + **MG5/MadWidth** LO source from independent FeynRules UFO | Each of five physical scalar mode inventories, off-shell treatment, SM-like QCD/EW corrections and scheme comparability |
| LFV and rare quark decay amplitudes | **SARAH FlavorKit/SPheno** | existing E3/D1–D4/SuperIso calculations | Explicit dipole Wilson coefficients, chirality, full neutrino loop consistency; additional Barr–Zee and \(\mu\to e\) conversion treatment checked by topology |
| \(B\to X_s\gamma\) | matched modern two-charged state Wilson coefficients and inclusive kernel | FlavorKit one-loop Wilson coefficients + original full old SuperIso as LO cross-check | QCD operator basis / matching / running / scheme / errors verified. **Do not** substitute generic FlavorKit output for 2026 NNLO rate |
| Global scalar minima, charge-breaking | **Vevacious++** and/or **VacStab** | original C5 multistart | Input all relevant vev directions, global minima witnesses/tunneling stability; no unjustified global-certification claim |
| Direct Higgs experimental constraints | **HiggsTools** | prior E5/E6 HS and independently validated predictions | 5-state complete physical decay+production inputs; modes/cross sections and confidence level |
| Collider rates | **MadGraph5_aMC**, optional NLO on consistent QCD UFO | independently matched analytic partonic checks | SM PDFs, masses, CKM, coupling normals, 4FS/5FS scheme etc and hadronic production validation |
| Scan orchestration | **BSMArt v2**, native tools for SPheno, FlexibleSUSY, HiggsTools, Vevacious, flavio and MadGraph | P1 immutable SHA manifests | Every backend exit code, input SLHA and output source hashes, point ID, version, model basis, allowed UNKNOWN unless all required likelihoods complete |

References: [BSMArt v2 docs](https://bsmart-hep.github.io/core/), [tools](https://bsmart-hep.github.io/core/guides/Tools.html), [scan methods](https://bsmart-hep.github.io/core/guides/scans.html), [install](https://bsmart-hep.github.io/core/guides/Installation.html); [SPheno/SARAH FlavorKit](https://arxiv.org/abs/1405.1434); [FlexibleDecay](https://arxiv.org/abs/2106.05038); [FlexibleSUSY repository](https://github.com/FlexibleSUSY/FlexibleSUSY).

### Important limitations, not hidden by automation

1. A ready-made, **validated** original *Type-II general Zee* SARAH model (2 doublets, charged singlet, general complex f/Y) has **not** been identified or compiled in this project. Existing 2HDM SARAH models are NOT interchangeable. The full physically consistent model definition is required before building.
2. Two binaries generated from the **same SARAH source are correlated** cross-checks. Independent model-implementation validation requires the separate FeynRules source, numerical vertices and Ward identities. SPheno and FlexibleSUSY may also differ in renormalization schemes and precision; raw rates should not be demanded to match without matched definitions.
3. SARAH/SPheno is NOT assumed to get the loop-induced Zee neutrino mass, complete two-loop LFV/Barr–Zee, or modern \(B\to X_s\gamma\) NNLO automatically. These require explicit operator/topology and numerical validation. FlavorKit handles broad general tree/one-loop operators, not every higher-order result.
4. FlexibleDecay is an add-on to generated FlexibleSUSY models. BSM scalar decays may only be LO, while known SM-like Higgs corrections are applied where available; a generic UFO is not a plug-and-play FlexibleDecay model.
5. BSMArt orchestrates; it is not a replacement for an unimplemented Zee Lagrangian, modern flavor kernels or detector-level predictions.

## AF software and model readiness audit (implemented, no fake acceptance)

~~~bash
cd /home/aalida/zee
git fetch origin && git switch feature/global-scan-priority1 && git pull --ff-only
source .venv-flavor-f1/bin/activate
python3 -m unittest discover -s tests -p 'test_zee_p1_standard_stack_audit.py' -v
python3 -u scripts/zee_p1_standard_stack_audit.py \
 --sarah-model-dir /home/aalida/zee/models/SARAH/ZeeTypeII \
 --out /home/aalida/zee/work/p1_external_toolchain_audit_20261020_v1.json
~~~

Only reports actual available binaries/python modules and SARAH model source files; it **will not run a scan or claim the model is validated**. It is safe if no external tools are installed or if the SARAH Zee model directory has not yet been created.

BSMArt 2 installation is documented by the upstream project (do this in its **own** isolated virtual environment under /home, never by pip-installing into the existing analysis environment):

~~~bash
cd /home/aalida/zee
python3 -m venv .venv-bsmart
source .venv-bsmart/bin/activate
python -m pip install bsmart
BSMArt-CheckPackages --scan Random --tool SPheno HiggsTools
~~~

The upstream `BSMArt-PrepareModel --All ZeeTypeII` workflow is appropriate **ONLY AFTER** the SARAH ZeeTypeII model is complete, its source has been vetted and SARAH/Mathematica is installed. BSMArt can orchestrate SPheno, FlexibleSUSY, HiggsTools, Vevacious++, etc., and its `read_csv`/`read_dir` scans can ingest our existing evidence cohorts without recreating physics. Do not launch it on a fake Zee SPheno spectrum executable.

## Computational scan policy

**No more micro-optimization-only continuation on the 309 archival sample as the central discovery strategy.** Use the original P2 mass/mixing/soft inputs and independent **complex** lepton texture parameters to generate broad blind samples. Three stages:

- **Cheap**: millions of random/QMC proposals with necessary tree BFB/unitarity, perturbativity, EWPO and neutrino algebraic closure; keep rejection statistics and hashes. These are screening only.
- **Medium**: SARAH-generated SPheno spectrum, model-specific FlavorKit, complete source-matched decay widths, scalar RGE and HiggsTools on screened subset. Track detailed status even for errors/timeouts.
- **Expensive**: modern \(B\to X_s\gamma\) reevaluation, Barr–Zee+conversion, Vevacious++ full vacuum, MG5 real hadronic rates and NLO checks on promising **diverse** accepted candidates, not a tiny fixed set.

BSMArt offers Random, MCMC, active learning, CMA-ES, MultiNest and read_csv/read_dir scans. Choose broad Random/QMC for coverage and later adaptive methods for efficiency; scanning 1e6 expensive SPheno+Vevacious/HiggsTools points is not automatically computationally wise.

### Current deliverables vs missing research physics

**Available**: original E2–F9 source/audits, N1–N3 included LO channels on 309 original points, original independently exported (but not scalar/flavor fully matched) FeynRules LO UFO, N4 309 source-matched *fragments*, 309 E2->Yang/Wu source scalar quartic basis map, new standard-toolchain package/model audit and CI.

**Not available yet**: compiled SARAH original Zee model, validated model-specific SPheno spectrum and FlavorKit, compiled FlexibleSUSY/FlexibleDecay variant, full external MadWidth comparisons, exact two-loop LFV and modern two-charged-inclusive \(B\to X_s\gamma\), complete five-state HiggsTools predictions, and a full physical exclusion surface. Do not mark any of these `PASS` based on names of tools or CI adapter tests.

**Development decision**: prioritize SARAH model generation and cross-check against FeynRules, then SPheno and FlexibleDecay; retire further custom N4/N5 narrow width gates as the primary implementation path. Never label a point fully allowed or excluded until constraints/uncertainties are complete.
