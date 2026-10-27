# Zee Module 5 Gate C2 — precision budget for 2026 B -> X_s gamma

## Identity and immutable inputs
Branch `feature/zee-bsgamma-2026-accuracy-audit` of `aalida0/zee`, EXACT ancestor `429a9d6de26a072dc0290db6ca1d050a362f5ecf`. This is a bounded accuracy/validity study for our FIRST Zee phenomenology paper, not another loop-convention calculation, not an approved exclusion, and not a new HyperIso feature.

C1 established `GATE_C1_NUMERICAL_DIAGNOSTIC_PASS` and `EXTERNAL_CONVENTION_PASS` for real top-only ms=0 LO dipoles through original Bobeth–Misiak–Urban (BMU) hep-ph/9904413v1. 2026 `B->Xs gamma` LO-linear Eq.(4) for one two-state reference benchmark gives `3.9494799731787267e-4`, delta `0.40947997317872675e-4`, or about 11.6% of SM. **This is NOT a validated scan constraint**. Do NOT re-open matching sign unless a falsifying contradiction emerges.

Frozen (read-only): `models/SARAH/ZeeTypeII/`, Modules 0–4, `module5/bsgamma_lo.py`, `module5/hyperiso_patch_contract.py`, `module5/bsgamma_2026_linear_diagnostic.py`, their established tests, previous audit reports and evidence, and pinned HyperIso sources. Do not touch main or any other checkout. No runtime use of the broken HyperIso SM BSM patch; C0 established SM drops it, THDM+patch double-counts.

### Read only these first
`module5/bsgamma_matching_accuracy.py` and `tests/test_module5_matching_accuracy.py` (prewritten, unverified scaffold); `module5/BSGAMMA_2026_CONVENTION.md`; `module5/HYPERISO_BRIDGE.md`; `module5/TWO_STATE_PATCH_AUDIT.md`; `module5/FLAVOR_2026_SOURCES.md`; `validation/module5/linear_2026.json`; `scripts/zee_module5_hyperiso_bridge.py`; `scripts/zee_module5_hyperiso_probe.cpp`. Read only directly relevant source/matching APIs thereafter.

## Pinned scientific references
1. Misiak et al. **arXiv:2608.29863v1**, 30 Aug 2026, `https://arxiv.org/html/2608.29863v1`, Sec IV Eq.(4), `mu0=160 GeV`, `Egamma>1.6 GeV`: `10^4 BR=(3.54 +/-0.14) -8.51 DeltaC7 -2.16 DeltaC8`, experimental `(3.49 +/-0.19)*1e-4`. The paper **explicitly** recommends LO NP matching as a generic small-effect approximation and drops quadratic NP terms. It explains that more refined matching includes `O(alpha_s)` corrections available generically from BMU; its own Type-II **670 GeV lower bound** uses higher-order one-state treatment and is NOT a per-state Zee mass cut.
2. Bobeth–Misiak–Urban **hep-ph/9904413v1**, `https://arxiv.org/html/hep-ph/9904413v1`, Sec 2 Eqs.(9)–(11), (13)–(29) gives signed generic LO and NLO `b->s gamma,sg` Wilson matching including `C4^(1)`. Respect `L_eff=+4GF/sqrt2 Vts* Vtb sum C_iP_i`, usual negative Hamiltonian, and its `C=C^(0)+alpha_s/(4pi)C^(1)+...`.
3. HyperIso **v1.0.3** `https://github.com/Hyperiso/Hyperiso`, PEELED `09d26ac6e71d1528922097a896d15693589f636b`; v1.0.3 R1–R7 and C1 same-scale LO Type-II comparisons already passed. Reuse existing pinned checkout/build if actually present (historical path `~/zee-hyperiso-runtime-bridge/validation/module5/local/HyperIso`), else build clean into ignored `validation/module5/local/`. Check HEAD, source integrity and CLI version. Never vendor binaries, edit upstream or repeat entire R1–R7 if unchanged.
4. Florentino et al. arXiv:2106.08332v1 fixes charged mixing; ordinary one-Higgs limit and two weighted state sum are prior art.

## Gate C2.A: executed, truly independent two-state NLO **matching sensitivity**
1. First audit/run prewritten pure-Python `module5/bsgamma_matching_accuracy.py` and `tests/test_module5_matching_accuracy.py`:
```bash
python -m unittest discover -s tests -p 'test_module5_matching_accuracy.py' -v
python -m unittest discover -s tests -p 'test_module5_bsgamma_2026_linear.py' -v
```
Tests are **synthetic harness tests** and not upstream NLO verification; fix any bugs before proceeding. Do not infer NLO/NNLO physics from passing mock tests.
2. Create a narrowly scoped executable external `scripts/zee_module5_nlo_probe.cpp` (or minimal extension of the proven Gate B client) and launcher/validator as needed. Query HyperIso **native one-charged-Higgs Type-II** BSM contributions separately at the two distinct physical masses, `m1,m2` and `tanbeta`, at a **COMMON** `mu0=160 GeV`, with the exact reference-LHA top mass `mt_MSbar(160)=163.96892236746697 GeV` and `alpha_s(160)` retrieved at runtime from its QCD helper. Query raw `C7^(0),C8^(0),C4^(1),C7^(1),C8^(1)` in ordinary matching basis (and if justified `C3,5,6` at other orders), using public `getM` and `getFM` to distinguish UNMULTIPLIED NLO coefficient from the `alpha_s/(4pi)` multiplied full result. Check `getFM(NLO)-getFM(LO) = alpha_s/(4pi)*getM(NLO)` numerically for every coefficient where defined. Confirm that C1–C6 BSM contributions vanish at LO but NOT necessarily at NLO.
3. For quark-sector Type-II charged mixing, at the given gamma, weight separate native one-state **full** LO and NLO matching by `w1=cos²gamma, w2=sin²gamma`. At this charged-scalar/gluon order each diagram has one charged scalar and two Yukawa vertices, so no inter-scalar mixing in the QCD loops; challenge this assumption against BMU/HyperIso source. This should yield full **two-state NLO matching**, not full two-state decay. Cross-check the native LO numbers against frozen Python and C1 (C7,C8) before accepting any NLO witness. Check both masses and interchange, gamma=0/pi2, equal masses, heavy decoupling, tanbeta variation, source sign, matching scale. Include distinct positive and negative witness/controls where meaningful.
4. Source-audit HyperIso NLO functions `C4_THDM,C7_THDM,C8_THDM` against independent BMU 1999 or pinned trusted reference at at least several nontrivial points. Independent matching should not rely solely on re-evaluating the *same* code. If independent BMU formula is too large, document precisely the limit and status `NLO_INDEPENDENCE_PARTIAL`; do not fabricate PASS. No extra alpha_s factor or automatic scale conversion. **Do not claim** full NP correction just from C7/C8: NLO C4 enters under running/matrix elements.
5. Produce a **real executable witness JSON** matching the scaffold's strict schema and SHA provenance; note that 64-char hashes are provenance labels, not independently authenticated by syntactic validation: verify actual local artifacts against each SHA in the launcher. Verify `alpha_s(160)` and mass calibration against source, compare at mu=160; optional mu=80/320 studies must be labeled *matching-scale variation with separately run mass/alpha_s inputs*, never fed to Eq4 with wrong scale.
6. Compute with scaffold (candidate; amend only if needed):
```bash
python -m module5.hyperiso_patch_contract --input validation/module5/local/2026_reference_input.json --output validation/module5/local/c2_contract.json
python -m module5.bsgamma_matching_accuracy --contract validation/module5/local/c2_contract.json --witness validation/module5/local/c2_native_nlo_witness.json --output validation/module5/local/c2_nlo_impact.json
```
If 2026_reference_input.json is absent, reconstruct the six-field input from **C1 evidence** with explicit reference-LHA mt at 160 and verify source SHA; do not invent a matching mass or silently fall back to 163 GeV. If actual upstream NLO execution unavailable, gate `NLO_RUNTIME_BLOCKED`.

## Gate C2.B: truncation/nonlinear validity and missing operators **without invented precision**
- Quantify the *measurable* numerical impact of NLO matching on C7,C8. Report the induced difference **if naively substituted into the 2026 Eq4 slopes** as `NLO_MATCHING_DIPOLE_ONLY_SENSITIVITY`, NOT a corrected 2026 BR: the formula is stated at LO NP, while C4^(1) effects require proper RGE and rate matrix elements.
- The C1 reference point has a relatively large `delta BR/BR_SM ~= 11.6%`. Seek an independent published or explicitly implemented **quadratic-in-NP** coefficient expansion in exactly the same 160-GeV operator basis, photon cut and normalization. If available, run falsifying one-state benchmarks and give a trustworthy curvature/validity comparison. **Never derive a universal quadratic coefficient simply by squaring Eq4, fitting unrelated HyperIso R3 outputs, or borrowing an older SM central value.** If unavailable, mark `QUADRATIC_VALIDITY_UNKNOWN`, recommend a controlled domain study and do not invent a 10% threshold.
- Inventory other potentially relevant LEFT operators and `m_s`-suppressed/primed amplitudes in our *specific Type-II Zee quark sector*; distinguish parametric suppression from a demonstrated negligible rate. Explicitly cover C4 generated at NLO.
- Compare central SM/experimental values and 0.14/0.19 errors from 2026 only as separately published measurements; **DO NOT combine them into an exclusion** without a justified covariance/NP uncertainty prescription. Do not invent uncertainties by promoting NLO–LO differences into one-sigma error bars. Optional illustrative sensitivity envelopes must be clearly **conditional**, not CL/exclusion.

## Completion artifacts and next action
Create:
- `module5/BSGAMMA_2026_ACCURACY.md`: source-pinned NLO equations, actual weighted native outputs, scheme, order, top/alpha_s provenance, Eq4 effects, quadratic/incomplete-operator status, bounded remaining work and plan toward robust scan filter.
- `validation/module5/accuracy_2026.json`: actual tests, hashes, residuals, numerical sensitivity and separate honest PASS/PARTIAL/BLOCKED gates.
- Brief appended Gate C2 paragraph in `validation/module5/STATUS.md` preserving all previous audit evidence.

Gate statuses:
`C2_NATIVE_NLO_MATCHING_PASS` only with real pinned native runs and LO reproduction, `C2_INDEPENDENT_NLO_PASS` only with genuine independent BMU/source validation, `C2_CURVATURE_VALIDATED` only with same-basis nonlinear evidence, `2026_LINEARIZED_FLAVOR_FILTER_READY` remains **false** without documented domain, uncertainties and statistical treatment. No physical Zee BR at NLO, no exclusion, likelihood, global acceptance, collider inference, and no per-scalar 670 GeV cut.

Run focused tests, `git diff --check`, commit scoped files only to `feature/zee-bsgamma-2026-accuracy-audit`, push, verify `git rev-parse HEAD` = `git ls-remote origin refs/heads/feature/zee-bsgamma-2026-accuracy-audit`. Report SHA, URL, actual tests/NLO values and blockers. Report `PUSH_BLOCKED` if needed. Minimize tokens: detail in files; do not do global searches or rerun SARAH/old loops/full R1–R7.
