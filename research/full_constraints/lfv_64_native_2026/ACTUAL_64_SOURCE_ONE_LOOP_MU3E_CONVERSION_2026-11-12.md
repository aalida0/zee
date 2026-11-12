# Source-derived one-loop `mu -> 3e` and coherent `mu-e` conversion on the new 64 Zee textures

**12 November 2026 | one-loop operator calculation COMPLETE for the retained SARAH source approximation; physical LFV/global acceptance UNKNOWN.**

### Exact private source recovery and independent execution

The user supplied an original five-file ZeeTypeII SARAH 4.15.4 / SPheno 4.0.5 Fortran ZIP. All five files match the frozen SHA-256 manifests under `research/full_constraints/lfv/SOURCE_TO_CODE_SOURCES.json`. None of the original generated sources is copied to this public repository.

The source-derived standalone evaluator compiled the original generated `AllCouplingsReallyAll` scalar and Yukawa vertex generator; the original `CalculateGamma2l` photon OA1/OA2; the **full original generated** direct `CalculateBox4L`, `CalculatePengV4L`, `CalculatePengS4L`, `CalculateTreeS4L`, `CalculateTreeV4L`; up, down and strange spectators of their original semileptonic `2L2u/d` analogues; and the original unchanged `Calculate_Lto3Lp` rate assembler. Original `Calculate_MuEconversion` was isolated and its known scalar proton/neutron isovector sign **corrected only in a temporary copy** (two signs). Original PV C/D functions were compiled; finite, zero-invariant-momentum B0 and B1 were implemented analytically with source-convention subtraction.

All 16 original tree-vacuum-certified scalar spectra and **64 complete, newly engineered complex F and Ye2 neutrino texture inputs** were recovered from the source-locked CI artifact (workflow run 43130710614). Nothing was substituted from the four older D7/F13 textures.

### Observed source one-loop rates, Q=mZ

| One-loop source-observable | min | median | max | experimental current reference (90% CL) | LO source screens |
|---|---:|---:|---:|---:|---|
| BR(mu -> e gamma) | 1.9460e-24 | 3.6037e-20 | **1.6273e-15** | 1.5e-13 (MEG II 2025) | **64/64 nominal compatible** |
| BR(mu -> 3e) | 1.5226e-25 | 1.2001e-21 | **1.0729e-17** | 1.0e-12 (SINDRUM) | **64/64 nominal compatible** |
| R(mu Al -> e Al), corrected historical nuclear prescription | 1.6432e-24 | 2.0177e-21 | **8.7638e-18** | no separately implemented Al limit | source rate only |
| R(mu Au -> e Au), corrected historical nuclear prescription | 4.0095e-24 | 5.1417e-21 | **2.7637e-17** | 7.0e-13 (SINDRUM II) | **64/64 nominal compatible** |

The most constraining current observable of the three is the radiative channel. Even its maximum is 92.18 below the observed upper limit. The corresponding source one-loop mu3e maximum is 9.32e4 times smaller than its limit, and the Au maximum is 2.53e4 times smaller. These are **central source-approximation margins, not conservative missing-amplitude bounds**.

All four 15673 neutrino textures: BR(mu3e) from 2.994e-23 to 1.346e-21, corrected source Au 8.214e-22 to 1.853e-21. All four 15591: BR(mu3e) from 4.059e-22 to 1.073e-17, corrected source Au 1.736e-21 to 1.113e-17. All 64 retained one-loop source screens remain compatible for these three comparison channels.

### Falsification and stability tests

1. Original SHA256 hashes exact (five files).
2. 64×8 signed real/imag original photon OA1/OA2 form-factor components agree **exactly** between independent extracted photon source and the original full generated `AllCouplingsReallyAll` source. Native mu->e gamma agrees with the prior independent Module3/4 partial dipole to a stable factor 1.03677775 (the schemes are not forcibly equated).
3. The original source 3e dipole-only vs source gamma ratio equals `alpha(MZ)/(8*pi)*(16 ln(m_mu/m_e)-22)/3 = 0.00656206591689` for all 64, to numerical precision (note source `alpha(MZ)`, not gamma alpha(0)).
4. Varying an auxiliary squared-mass neutrino infrared regulator 1e-18..1e-34 GeV² leaves all 64 rate entries **bitwise unchanged**. This regulates the original intermediate zero-momentum `C0(0,0,mW²)` while keeping physical loop neutrino masses zero.
5. Multiplying every F coupling by `exp(0.812i)` leaves all source rates unchanged, worst relative residual <1.3e-12.
6. Scale Q=mZ -> 1 TeV changes worst source mu3e by <1.2e-7 and corrected Au by <1.36e-4; omitting the scalar-penguin source group yields worst variation <3e-12. This is empirical materiality on these 64, **not** a full renormalization-scheme proof.
7. The full original-source standalone replay was independently rebuilt from a clean path with `gfortran -O0 -fcheck=all` and recovered the original per-card rates, phase/scale/IR checks and SHA receipts.

### Explicit approximation ledger and publication scope

This is **source-based complete leading one-loop group coverage**, not a full physical LFV calculation:
- The original photon non-dipole form factor is evaluated at q²=0 rather than integrated with full finite-q² electron/muon thresholds in the 3e phase space.
- The initial scalar spectrum is frozen at tree level, with fixed electroweak scheme and original generated vertices.
- The standalone Type-II quark input uses illustrative light-quark masses and **CKM=identity**. An independently matched running Type-II quark input is required before using these source rates as quantitative conversion likelihoods.
- The conversion target retains original Kuno–Okada/Arganda-era nuclear responses, plus the necessary two-sign scalar p/n correction, **not** current complete LEFT/QCD RG, heavy-quark scalar/gluon thresholds or modern nuclear uncertainties.
- Scalar penguin counterterm/scheme matching is not certified, despite numerically negligible observed scale impact on these 64.
- Zee-specific mixed charged-W/Goldstone electroweak two-loop dipoles and other higher-order amplitudes remain unquantified. Their unknown sizes are not replaced by zeros or an invented uncertainty.

**Revised screen status: `LO_NATIVE_ONE_LOOP_64_COMPATIBLE` for these 3 experimental comparisons; `physical_mu3e=null`, `physical_Al=null`, `physical_Au=null`, `full_LFV='UNKNOWN'`, `global_acceptance=null`.**

This is sufficient evidence to state that the engineered 64 are **not ruled out at the retained leading-one-loop level by mu3e/conversion**. It is not a globally valid model space or a substitute for new scalar parameter-space scanning.

**Provenance:** user private downloadable replay package `zee_64_mu3e_conversion_original_source_replay_2026-11-12.zip` contains all 64 detailed JSON/CSV records, input SHA-256, original generated Fortran, standalone source-derived modules, build scripts and per-regulator/phase/scale controls. The original five user-provided Fortran sources are **not** committed to the public repository.

### Primary references

- MEG II, EPJC 85 (2025) 1177, DOI 10.1140/epjc/s10052-025-14906-3; 90% CL 1.5e-13.
- SINDRUM, U. Bellgardt et al., NPB 299 (1988) 1; BR(mu3e)<1e-12.
- SINDRUM II, W. H. Bertl et al., EPJC 47 (2006) 337; CR(muAu -> eAu)<7e-13.
- Kuno and Okada, Rev.Mod.Phys.73 (2001) 151, hep-ph/9909265.
- Kitano, Koike and Okada, Phys.Rev.D66 (2002) 096002, hep-ph/0203110.
- Herrero-García et al., JHEP 04 (2017) 130, arXiv:1701.05345.
