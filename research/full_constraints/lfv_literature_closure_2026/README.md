# Zee LFV literature transfer and coherent conversion — 13 November 2026

**Branch:** `research/zee-lfv-literature-20261113`. Source-frozen modules and scan unchanged. **Physical Zee LFV remains UNKNOWN**; the outputs are scoped leading-order controls, not a new complete LFV limit.

## What has actually been implemented and checked

- `conversion_kko.py`: coherent `mu N -> e N` rate with **complex** dipole, scalar and vector operators, proton **and neutron** overlap integrals for Al27/Ti48/Au197, heavy-quark scalar `2/27` rule, dipole–scalar–vector interference and strict input-schema guards. Its conventions are from Primulando–Julio–Uttayarat EPJC82 (2022) 253, Eqs. (31),(32),(38),(41)-(43) and Kitano–Koike–Okada PRD66 (2002) 096002. The 2022 Eq.(41) omits `V(n)` only because *its* vector was photonic; this implementation retains KKO's neutron-vector term for arbitrary UV Z penguins. **The original SARAH/FlavorKit Wilsons cannot be inserted without a sign, chirality and normalization bridge.** This module does not perform UV matching or QCD/QED running, and KKO overlaps are not a fully modern nuclear likelihood.
- `materiality.py`: recomputes norms and coherent complex sums of **already executed** corrected published general-2HDM source groups, using the four frozen low-texture D7/F13 controls and the official GitLab `thdm.py` SHA `9b4af7aa4bf7bf533a7b82c8c2603d118346424e3b7b5f9f06ab8cb41bc4e193`. Reuses the separately completed original 12-Nov **64-source one-loop Zee** extrema. This does **not** compute new physical two-loop Zee amplitudes or new per-card 64 predictions.
- `test_conversion_kko.py`, `test_materiality.py`: **9/9 local tests passed**, both uploaded and verified byte-for-byte. Numerical recheck on the real official four-card JSON shows coherent-group closure at relative error `<1.8e-16`. The original upstream 2HDM program was **not rerun** in this task.

### Corrected single-charged-state 2HDM proxy only

| Old benchmark | norm(2-loop)/norm(1-loop) |
|---|---:|
| D7 NO | 3.0633344e-10 |
| D7 IO | 9.7751890e-11 |
| F13 NO | 4.9094696e-11 |
| F13 IO | 4.8378712e-11 |

The particular source textures suppress direct e-mu Yukawas; setting those exactly to zero gives vanishing 2HDM two-loop source groups. **No transfer of these tiny ratios to the physical mixed Zee `F` sector or new 64 Yukawa cards is justified.** The corrected reference is JHEP06(2025)156 **plus JHEP07(2026)184 erratum**, not the uncorrected 2025 expressions.

### Existing 64 Zee one-loop source rates: conservative headroom calculation

| Observable | Max source rate | 90% upper bound | Bound/max | Conditional `sqrt(bound/max)-1` |
|---|---:|---:|---:|---:|
| BR(mu->e gamma) | 1.6273e-15 | 1.5e-13 | 92.1772 | **8.6009** |
| BR(mu->3e) | 1.0729e-17 | 1.0e-12 | 93205.3 | **304.2955** |
| CR(mu Au->e Au), historical source prescription | 2.7637e-17 | 7.0e-13 | 25328.4 | **158.1489** |

Last column is a *sufficient conditional* missing-amplitude bound from the triangle inequality, **NOT** an estimate of missing physics. `full_physical_LFV=null`.

### Independent KKO dipole-only normalization

With dipole coefficients only, the code reproduces `CR/BRgamma=pi*D^2/(tau_mu*Gamma_capture)`: Al27 **0.00265647**, Ti48 **0.00412146**, Au197 **0.00390815**. Heeck–Thapa 2023 Eq.(5) quotes approximately 0.0027 for Al in its **dipole-only restricted setup**. Non-photonic neutron and scalar operators can invalidate dipole-only scaling in Type-II Zee.

## Reproduce in the repository root

```bash
git fetch origin && git switch research/zee-lfv-literature-20261113
git pull --ff-only origin research/zee-lfv-literature-20261113
python3 -m unittest \
  research.full_constraints.lfv_literature_closure_2026.test_conversion_kko \
  research.full_constraints.lfv_literature_closure_2026.test_materiality -v
python3 -m research.full_constraints.lfv_literature_closure_2026.materiality \
  --official-proxy-json research/full_constraints/lfv_2hdm_gitlab_reuse_2026/OFFICIAL_CORRECTED_GITLAB_COMPLEX_WILSON_GROUPS_2026-11-10.json \
  --output /tmp/zee_lfv_literature_materiality_20261113.json
```

## Remaining physics gate — exact dependencies

1. Re-extract the **actual signed 64-card SARAH coefficients** `cL,cR,gLS,gRS,gLV,gRV` and independently match them into the paper Eq.(38) normalization. The private original 64 source replay ZIP was not available in this execution; its reported aggregate rates were reused, not silently substituted as Wilson coefficients.
2. Supply consistent CKM/running quarks, heavy thresholds, RG and modern nucleon/nuclear errors. Verify scalar–vector interference against a second code (e.g. MuonConverter/MuonBridge).
3. Explicitly screen genuinely Zee mixed `F`/W/Goldstone/two-charged-state leading/enhanced two-loop dipoles. The small pure-2HDM proxy does **not** establish their size. A fully general two-loop calculation is not required by default **if** numerical materiality can be justified.
4. Use observed tau and other muon LFV bounds at the same declared accuracy. Do not classify missing processes as zero.

**Gate:** `source_one_loop_64=SCOPED_PASS`, `KKO_operator_kernel=SCOPED_PASS`, `pure_2HDM_source_reuse=PASS_ON_FOUR_PROXY_CARDS`, `physical_LFV=UNKNOWN`, `global_Zee_acceptance=null`.

### Papers

- Primulando et al., EPJC82(2022)253, DOI 10.1140/epjc/s10052-022-10189-0.
- Kitano et al., PRD66(2002)096002, DOI 10.1103/PhysRevD.66.096002 (and 2007 erratum).
- Altmannshofer et al., JHEP06(2025)156, DOI 10.1007/JHEP06(2025)156; erratum JHEP07(2026)184, DOI 10.1007/JHEP07(2026)184.
- Herrero-García et al., JHEP04(2017)130, DOI 10.1007/JHEP04(2017)130.
- Heeck–Thapa, PLB841(2023)137910, DOI 10.1016/j.physletb.2023.137910.
