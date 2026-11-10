# Executed full generated Zee one-loop LFV and coherent light-quark conversion

**10 November 2026. SOURCE ONE-LOOP LFV COMPUTED; PHYSICAL GLOBAL LFV REMAINS UNKNOWN.**

This extends the source-locked exact 4-card calculation documented in `FULL_ORIGINAL_OA2_AND_ONE_LOOP_MU3E_2026-11-10.md` by executing the **missing generated strange-quark** semileptonic operators in the original SARAH 4.15.4 model, including all original tree, scalar/vector penguin and box groups for quark flavor (2,2). Together with the previous up/down pilot, the native source U,D,S input vectors are available for a source-level coherent conversion observable. All physical lepton F/D and scalar mixing inputs are from four original D7/F13 frozen low-joint witness cards, **quark CKM and masses remain explicitly illustrative**.

## Verified generator and observable source

The original generated `CalculatePengV2L2d`, `CalculatePengS2L2d`, `CalculateTreeS2L2d`, `CalculateTreeV2L2d`, `CalculateBox2L2d` are compiled and executed with (2,2) strange-quark spectator indices, not substituted from a down-quark rescaling. The source-original `Calculate_MuEconversion` uses the generated native `K1,K2` and all light-quark scalar/vector coefficients. The original generated scalar isospin expression has a **proton/neutron swap**, so the source was compiled in **two copies**: unmodified and with the single scalar isospin-sign repair. The source-copy regression verifies the vector contraction remains unchanged.

The original Fortran observable was compiled with gfortran -O0 -fcheck=all. Comparison against an independent Python transcription of the same original 2001-era nuclear approximation gives **48/48 PASS** (four cards x six nuclei x uncorrected/corrected) at max complex-rate relative residual <2e-12. The original generated Fortran source files were **not altered or pushed**; temporary copies were compiled only.

## Numerical coherent one-loop source diagnostics

| Original card | Corrected Al-27 source conversion | Corrected Au-197 source conversion |
| --- | ---: | ---: |
| D7 NO | 4.73208211e-22 | 6.98927565e-22 |
| D7 IO | 3.08529293e-21 | 4.54971780e-21 |
| F13 NO | 2.37371489e-21 | 6.34683551e-21 |
| F13 IO | 7.20525484e-21 | 1.92203807e-20 |

The scalar p/n correction changes these **particular source-computed Al rates** by <2.2e-8 relative. This does not mean the original sign bug is harmless for arbitrary couplings or nuclei.

The source one-loop mu->e gamma and mu->3e results remain:

| Card | BR(mu->e gamma) original 1-loop | BR(mu->3e) original 1-loop |
|---|---:|---:|
| D7 NO | 1.66491921e-19 | 1.08828659e-21 |
| D7 IO | 1.15779980e-18 | 7.52936205e-21 |
| F13 NO | 4.29892238e-20 | 4.54615814e-22 |
| F13 IO | 1.42668207e-19 | 1.45713157e-21 |

These are **source one-loop approximations**, not model-wide fully matched physical rates. The original conversion observable employs an old nuclear coherent model, not current complete QED/QCD running and KKO nuclear overlap prescription. Also, running charged quark masses/CKM has not been validated against precision inputs. Heavy-quark scalar/gluon contributions (c,b,t) and operator thresholds are absent. In particular, the earlier 2HDM h/H tree-only heavy quark effect is tiny for this texture, but that does not bound the loop-induced heavy/gluon terms.

## Experimental context and conditional amplitude margin

- MEG II: BR(mu->e gamma)<1.5e-13 (90% CL), published EPJC 85 (2025) 1177.
- SINDRUM: BR(mu->3e)<1e-12 (90% CL).
- SINDRUM II Au conversion <7e-13 (90% CL), in the published older Au bound.

All four native source one-loop diagnostics lie far below these limits. A **sufficient missing-radiative-amplitude** norm budget from triangle inequality ranges 1.3208e-12 to 1.3238e-12 GeV^-2 (as detailed in prior source report). This threshold **is not a bound on the actual missing two-loop Zee amplitudes**, hence no experimental global PASS follows.

## Reproducibility and scientific gate

Delivered as ZIPs in the conversation:
1. `zee_lfv_full_oa2_one_loop_continuation_2026-11-10.zip` — original full OA1/OA2 source extraction, native rate assembly, independent charged F-only checks, missing-radiative thresholds, and 6 focused tests.
2. `zee_lfv_native_1loop_conversion_addendum_2026-11-10.zip` — original five strange quark groups, full u/d/s conversion and corrected scalar p/n source, 48 rates and 4 focused tests.

**All 10 focused tests PASS.** Original source native vs independent transcription checks: 16 mu3e + 48 conversion = **64 numerical comparisons PASS**; independent 4-card charged F-only phase/chirality checks pass at <3.4e-16.

### Still missing for a fully defensible constrained phenomenology scan

1. Explicit *full mixed Zee two-loop gauge/charged W* dipole correction or a source-supported upper error bound, along with electroweak scheme and uncertainties.
2. Finite q2 virtual-photon light-internal-lepton control for physical mu3e; scalar penguin counterterm Q dependence must be resolved or bounded with an explicit physical-scope criterion.
3. Precision Type-II conversion with quark RG/threshold heavy-quark/gluon operators and updated nuclear response uncertainties, not the older generic FlavorKit approximation.
4. **No full LFV GLOBAL_PASS, physical Br or excluded benchmark** should be entered into a scan until these are validated.

**Result:** `ONE_LOOP_NATIVE_LFV_SOURCE_EXECUTED`; `PHYSICAL_LFV_UNKNOWN`; `global_acceptance=null`; do not run a large scan based on this alone.
