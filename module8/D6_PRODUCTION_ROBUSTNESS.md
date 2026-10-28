# D6 production robustness — 2026-10-28

**D6_FULL_MIXED_PAIR_PRODUCTION_PASS; D6_LO_SCALE_SENSITIVITY_PASS; D6_D5_REFERENCE_PASS.**
**NOVELTY_UNPROVEN; GLOBAL_ZEE_ACCEPTANCE=null.**

Fifteen promoted genuine MG5 3.6.7 integrations (plus 2 superseded full-pair executions and 2 unpromoted outputs after capture failures): three full mixed-pair spectra, three matched Z-only controls, seven frozen-Yukawa 5FS associated-production scale points and two additional evolved-Yukawa points (sharing the identical central run). Errors throughout are numerical integration only. D5 evidence and all frozen files are unchanged.

## Full tree mixed pair versus matched Z-only

Both final charges and both beam orders are explicitly generated exactly once. 13.6 TeV pp; NNPDF30_lo_as_0130 member 0, LHAID 263000, 5FS; mH2=700, beta=1.394, gamma=1.089; muR=muF=700 GeV. All physical parameters, complex CKM, running-at-700 Yukawas, massless incoming quarks, mt=172.4, zero H1/H2/top external widths and internal defaults are matched to D5. No hard-process cuts.

| mH1 GeV | Full LO pb | Matched Z-only LO pb | D5 Z-only pb | Full/Z matched | Full − Z matched pb |
|---:|---:|---:|---:|---:|---:|
| 250 | 0.00016093 ± 3.2314e-07 | 0.00016119 ± 1.7615e-07 | 0.00016119 ± 1.7615e-07 | 0.998387 | -2.6e-07 |
| 300 | 0.00013415 ± 2.6967e-07 | 0.00013455 ± 1.6003e-07 | 0.0001344 ± 1.3494e-07 | 0.997027 | -4e-07 |
| 350 | 0.00011122 ± 2.1391e-07 | 0.00011155 ± 1.1348e-07 | 0.00011155 ± 1.1348e-07 | 0.997042 | -3.3e-07 |

The signed differences include interference and Monte Carlo fluctuations. They are not positive cross sections of omitted diagrams. No covariance has been measured between the integrations. The JSON also gives ratios/differences directly to the original D5 source rates. All independent Z controls agree with D5 within actual combined integration precision; the new associated central rate reproduces D5 exactly at native printed precision. Never add full P1 to its Z-only subset.

## Inspected diagrams and independent amplitudes

Each identical-flavor full graph set contains eight diagrams: s-channel photon, Z, hh1 (25), hh2 (35), Ah2 (36), and three quark-exchange diagrams. Unequal initial flavors contain six graphs: three neutral scalars and three quark exchanges. Actual generated configs.inc, matrix sources, HELAS graph vertices and PDG IDs were inspected; the versioned graph summary includes every flavor and both final charges. The mixed photon coefficient is zero analytically, with native roundoff below 5.56e-17. No appreciable extra gauge graph is present. Neutral-scalar and t-channel Yukawa graphs are retained without a forced Z propagator. All generated tree graphs have amplitude orders QED=2, QCD=HIG=HIW=0; effective loop vertices and gg loop-induced production are excluded. QED=2 is an MG upper bound, and inspection confirms every included graph actually has two powers.

The independent Python/ALOHA evaluator executed 234 fixed-kinematics comparisons: all 13 initial-flavor combinations, both charged final states, three angles and three spectra at sqrt(shat)=2 TeV. Separate Z, quark-exchange and neutral-scalar evaluations expose signed interference. At source masses, cos(theta)=0.23, b bbar → H2+ H1− gives m²(full)=9.45133071667e-5, m²(Z)=1.35186133674e-4, m²(Y)=5.08388638638e-6 and total cross-term remainder −4.57567803581e-5. The u ubar effect is below 1e-5 fraction at that point; the bottom channel has the largest effect. These dimensionless spin/color-averaged matrix values are diagnostics, not hadronic rates. The flavor-changing channels are tiny. The integrated full rates stay comparable to Z-only.

At gamma=0 and pi/2, the independent Z-only control vanishes (≤3.1e-36 in m²). The full b bbar amplitude remains m²=2.24202421191e-6 in these fixed-potential, fixed-mass mixing controls. These controls do not reconstruct viable scalar points and do not establish that the full endpoint rate vanishes.

## Associated H2 scale sensitivity

Standard seven-point LO sensitivity around 700 GeV: muR/muF ratios 1/4 and 4 removed. Yukawa masses are frozen at the D5 running-at-700 values mt,Y=148.0414556305571 and mb,Y=2.69162343131315 GeV. Only hard alpha_s and factorization/PDF scale dependence is varied. A separate correlated-three-point evolved-Yukawa diagnostic is reported below, with the identical central run shared between schemes. Both charges and both incoming orders are included; the source mH1=300 card is used throughout.

| muR GeV | muF GeV | sigma LO pb | / central |
|---:|---:|---:|---:|
| 350 | 350 | 0.0051224 ± 9.5007e-06 | 1.132122 |
| 350 | 700 | 0.0049348 ± 9.0013e-06 | 1.090660 |
| 700 | 350 | 0.0046962 ± 9.1315e-06 | 1.037926 |
| 700 | 700 | 0.0045246 ± 8.2534e-06 | 1.000000 |
| 700 | 1400 | 0.0043316 ± 8.4933e-06 | 0.957344 |
| 1400 | 700 | 0.0041776 ± 7.6202e-06 | 0.923308 |
| 1400 | 1400 | 0.0039994 ± 7.8418e-06 | 0.883923 |

Actual minimum/maximum: **0.0039994–0.0051224 pb**, central 0.0045246 pb; **-11.608% / +13.212%**. This is LO sensitivity, not a calibrated NLO error or statistical confidence interval. Only PDF member 0000 exists: **PDF_UNCERTAINTY_UNKNOWN**. Integration errors remain separate.

Evolved-Yukawa correlated-3-point diagnostic: (350,350) GeV: 0.0055751 ± 1.034e-05 pb; (700,700) GeV: 0.0045246 ± 8.2534e-06 pb; (1400,1400) GeV: 0.0036962 ± 7.2473e-06 pb.

Its separate range is 0.0036962–0.0055751 pb (-18.309% / +23.218%). This includes the extra Yukawa mass-scheme effect and is not a seven-point envelope. D4 mass evolution retains alpha_s(MZ)=0.118; production alpha_s continues to come from the LO PDF.

## Source locks, validation and conditional decays

The exact D5 base is e15e9badb8be8be848b1ec8737977086f5ba8e20. Its six original runs were revalidated read-only in the D5 workspace before copying minimal sources, native cards/UFO, central PDF and installed LHAPDF runtime into D6 ignored local/. No D5 event/process directory was reused for execution. All new outputs are under d6_F, d6_Z, d6_A and d6_receipts. The pinned D5 JSON, frozen code/model sources, mapped LHA cards, source archives and PDFs are SHA-checked.

Fresh independent native evaluation repeats all 5,904 signed comparisons across 36 native cards. The official MG5 release archive is pinned to the D5 SHA; 827 relevant Python/Fortran/C++/include files across madgraph/aloha/models/Template are compared byte-for-byte against the actual D6 runtime tree with zero differences. This selection differs from the historical D5 846-file check; it is an actual new comparison, not a recycled count. LHAPDF 6.5.6 shared-library and central-grid hashes match D5. The official source and UFO are unmodified. Only installed lhapdf-config paths were relocated into D6; this is recorded in versioned input provenance.

New D6 receipts bind launcher source, command, seed 4154, mapped cards, executable/matrix manifests, original/normalized cards, actual event banners, logs, results and source/PDF archives. The validator checks actual native version, charges/orders, beam energy, no applicable cuts, finite numerical errors, native log/banner/result agreement, all LHA values and active scales. MG resets the disk seed to zero after running; the banner must preserve 4154. Compiled vector.inc is generated as scalar WARP_SIZE=NB_WARP=VECSIZE_MEMMAX=1 and is checked explicitly; run_card.inc/param_card.inc are generated constants checked through banner cards. MG helicity recycling rewrites matrix1_optim.f when masses change; the first two shifted full-pair executions are retained but superseded, and new d6v3 reruns archive every compiled source per run. Optimized source snapshots are hashed and checked independently of later active runs; immutable original interaction code is rehashed against pre-execution manifests. A snapshot-capture loop variable initially shadowed the completed subprocess object; those two outputs are retained with null native exit codes and are not promoted. Fresh captures use the corrected code. The initial source full-pair manifest contains the immutable original matrix/templates before helicity recycling. Final whitespace checks removed one extra EOF newline from each new capture launcher after execution. The exact executed bytes are archived by SHA, and validation permits precisely that one-newline difference; the versioned input provenance records both hashes. D5 source-file hash invariants are not applied to new D6 scripts.

The baseline audit was corrected to reject changed reference scales/mixing/masses and mismatched linked BR/error entries. It remains reference arithmetic only. Native tests include recomputed-hash falsifiers for missing beam order, seed, nonfinite results, empty source manifests and changed top width, plus scale/scheme and failed-execution checks.

| mH1 GeV | D4 BR2×BR1² | Full P1 × tree BR pb |
|---:|---:|---:|
| 250 | 0.813770411038 | 0.000130960072 ± 2.6296e-07 |
| 300 | 0.803078208115 | 0.000107732942 ± 2.1657e-07 |
| 350 | 0.774061539557 | 8.60911244e-05 ± 1.6558e-07 |

Source P2 has D4 BR2×BR1=0.805915491239, conditional central rate 0.003646445232 pb and frozen-Yukawa scale range 0.003223178416–0.004128221512 pb. Products attach the exact D4 benchmark IDs and ledger SHA through D5; no additional charge factor is used. D4 BRs are uncorrected on-shell tree two-body values with unquantified higher-order corrections. No Z/top/W decays, detector acceptance or physical yields are inferred.

## Publication stop/go and remaining gates

**STOP mixed pair as a first-paper headline at these reference benchmarks.** Full tree rates are comparable to Z-only and much smaller than associated production. This does not establish a substantively new mechanism beyond the [2021 Zee cascade/tbH study](https://arxiv.org/abs/2106.08332) and [2025 charged-scalar DY/mixing study](https://arxiv.org/html/2501.09796v1). The [2017 general-Zee flavor scan](https://arxiv.org/abs/1701.05345v2) also precedes general flavor correlations. The targeted searches listed in the JSON do not prove bibliographic absence; NOVELTY_UNPROVEN remains.

Required D6 production blockers: **none**. Physical prediction gates remain incomplete: LFV Wgamma, full 2026 B→Xs gamma, vacuum certification, complete NuFIT likelihood, PDF replica uncertainty, higher-order production/decay corrections and detector backgrounds/efficiencies. GLOBAL_ZEE_ACCEPTANCE=null. No detector reach, discoverability, exclusion or 95% CL claim. No 4FS execution or 4FS+5FS sum.

Next physics priority is a separately declared broad scan of H1/H2 (including heavier masses), neutrals, beta and gamma, real scalar/tree EWPO screening, NO+IO genuine neutrino solutions, uncertainties and flavor gating. A missing critical gate keeps point acceptance UNKNOWN. H2=700 here isolates production uncertainties and does not exhaust the search space. This future scan is outside D6.

## Reproduction

Use isolated copies of the SHA-verified D5 native inputs and official runtime under D6 local/. Keep D5 read-only. Fresh-generation/run commands refuse existing outputs.

```sh
python -m unittest discover -s tests -p 'test_module8_d6_baseline.py' -v
python -m module8.d6_baseline --d5-evidence validation/module8/d5_production.json --output validation/module8/local/d6_baseline.json
python -m module8.d6_production generate
# Run F at source; shifted F spectra use the snapshot capture below:
python -m module8.d6_production run --kind F --spectrum source
python -m module8.d6_production run --kind Z --spectrum source
python -m module8.d6_production run --kind Z --spectrum mH1_m50p0
python -m module8.d6_production run --kind Z --spectrum mH1_p50p0
# Run A at (700,700),(350,350),(350,700),(700,350),(700,1400),(1400,700),(1400,1400):
python -m module8.d6_production run --kind A --mur 700 --muf 700
python -m module8.d6_production run --kind A --mur 350 --muf 350
python -m module8.d6_production run --kind A --mur 350 --muf 700
python -m module8.d6_production run --kind A --mur 700 --muf 350
python -m module8.d6_production run --kind A --mur 700 --muf 1400
python -m module8.d6_production run --kind A --mur 1400 --muf 700
python -m module8.d6_production run --kind A --mur 1400 --muf 1400
python -c "from module8.d6_capture import execute; execute('F','mH1_m50p0'); execute('F','mH1_p50p0')"
python -c "from module8.d6_evolved import execute; execute('A','source',350.,350.); execute('A','source',1400.,1400.)"
python -m module8.d6_matrix_checks
python -m module8.d6_generator_validate
python -m unittest discover -s tests -p 'test_module8_d6_*.py' -v
python -m module8.d6_rate_report
git diff --check
```

Compact production evidence, per-run hashes, settings, exact D5 controls, scale points and source links are in [d6_production.json](../validation/module8/d6_production.json). Raw native artifacts remain ignored under validation/module8/local/.
