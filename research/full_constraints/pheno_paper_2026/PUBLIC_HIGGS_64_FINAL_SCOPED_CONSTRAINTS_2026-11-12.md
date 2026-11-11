# Zee charged-cascade paper: public Higgs-code integration and combined 64-family results

**Research freeze:** 11–12 November 2026, branch `research/zee-full-constraints`.  
**Scientific status:** `HIGGS_NAMED_PUBLIC_SOURCE_SCREENS_EXECUTED_64`, **not** a full physical Higgs exclusion, **not** a globally allowed Zee scan.

## 1. Public code reuse completed, without changing the physical Zee model

- The original physical Zee model, spectrum, charged mixing, general complex lepton Yukawas and neutrino inverse remain in source Modules 0–14. Do **not** replace them with Type-II 2HDMC lepton Yukawas or a single charged Higgs.
- **HDECAY/AnyHdecay:** source-executed at all 16 original scalar inputs. Transfer only validated 2HDM-compatible QCD quark and neutral channels, plus original Zee (H/A\to H_i^\pm W^\mp), trilinears, general lepton and mixed charged states. **64 mixed-order positive known partial-width sums**; no physical total-width certification.
- **SusHi 1.7.0 + LHAPDF 6.5.3 / MMHT2014lo68cl:** actual independent **32 H/A 13 TeV LO** ggF and bbH calculations; not old D7/F13 rescalings.
- **HiggsTools 1.1.3** pinned full h125 HiggsSignals dataset, selected HiggsBounds h125 dataset, HiggsTools public 4FS/5FS matched (tbH_1\) and (tbH_2\) production tables for source-scaled Type-II quark couplings, plus native D4 exotic-inclusive charged widths. All **64** applied.
- **HiggsBounds (H/A\)** actual 13 TeV LO SusHi production and source native/HDECAY positive channels, with declared additional-positive-width scenarios 0%, 10%, 25%. **These rates are intentionally optimistic conditional envelopes and cannot be global search exclusions.**

### Reproducible successful source CI

| Component | Original passing workflow |
|---|---|
| h125 HiggsSignals / h125 HiggsBounds / matched H1+H2 charged observed limits | [43122649490](https://github.com/aalida0/zee/actions/runs/43122649490) |
| Public HDECAY 16 spectra and 64 Zee H/A partial-width join | [43119479264](https://github.com/aalida0/zee/actions/runs/43119479264) |
| Public SusHi 32 actual H/A 13 TeV rates | [43122137634](https://github.com/aalida0/zee/actions/runs/43122137634) |
| Heavy H/A HiggsBounds three declared width scenarios | [43122729249](https://github.com/aalida0/zee/actions/runs/43122729249) |
| **Join the 64 source-identical case keys across four experimental diagnostics** | **[43123642816](https://github.com/aalida0/zee/actions/runs/43123642816)** |

Machine-readable join generator: `pheno_paper_2026/join_higgs_public_64.py`. Its source artifact records the SHA256 hashes of all four inputs, scalar ID/ordering/seed and individual selected observed limits, and preserves `global_acceptance=null`. Its 3 tamper/identity tests pass.

## 2. Combined 16 original scalar spectra × 4 engineered lepton families

All numbers are scoped experimental **diagnostics**, *not* globally allowed physics. The HiggsSignals statistic compares each (h(125)) effective coupling against the SM **using the same dataset**, but is **not yet a calibrated 95% CL likelihood-ratio test**. `R_charged` is the largest HiggsBounds selected observed-limit ratio for the public matched 13 TeV H1/H2 (tbH^\pm) mode, and `R_HA` is the largest **selected** (H/A) source-LO observed ratio under the optimistic known-channel denominator. All numbers are maxima over the four selected neutrino families, except the range in h125 `deltaChi2`.

| Scalar | h125 `Δχ²` range | max selected charged R | max selected H/A R |
|---:|---:|---:|---:|
| 2264 | 1.103–1.528 | **0.7928** | 0.0090 |
| 2616 | 1.032–1.300 | 0.4356 | 0.0024 |
| 3693 | **10.162–10.252** | 0.5527 | 0.1104 |
| 4611 | 0.413–0.419 | 0.1316 | 0.0001 |
| 8294 | 0.508–0.582 | 0.7449 | 0.0006 |
| 8850 | **10.917–37.253** | 0.2262 | 0.0339 |
| 9454 | 0.476–0.483 | 0.2837 | 0.0082 |
| 11016 | 0.453–0.497 | 0.1100 | 0.0002 |
| 13345 | 7.667–7.884 | 0.5624 | 0.0332 |
| 14074 | 0.597–0.606 | 0.0898 | 0.0004 |
| 14187 | 0.957–4.128 | 0.4719 | 0.0081 |
| 14555 | **74.321–75.672** | 0.0269 | 0.0562 |
| 14984 | 0.570–0.627 | 0.1424 | 0.0008 |
| 15591 | 1.734–1.929 | 0.3156 | 0.0053 |
| **15673** | **0.121–0.273** | **0.0922** | **0.0016** |
| 16385 | **9.404–37.508** | 0.4052 | 0.0556 |

Source combined summary:
- **64/64** constructed cases have evaluated named *direct-search subsets* below their applicable HiggsBounds selected observed limits; none is a global model approval.
- **16/64** (four scalar centers: 3693, 8850, 14555, 16385) have **h125 Δχ² >9**; this is a *tension diagnostic*, not a calibrated 95%-CL exclusion. Particularly 14555 is severely disfavored relative to the SM under the current effective-coupling prescription.
- Preferred **15673** has small h125 relative χ² and small selected charged and heavy-neutral search ratios, at the specified order. Do **not** call it an experimentally allowed Zee benchmark until missing physics is accounted for.
- The old MG5 LO 5FS to public 4FS/5FS matched H2 rates is about **2.06** at 15673. Charged H1 at 2264 has selected observed ratio **0.793**, making it materially closer to the limit than its H2 counterpart.

## 3. What this does and does not finish

**Complete at explicitly declared source scope:** matched original scalar and complex lepton input cards, h125 effective-coupling datasets, public charged associated production with both physical charged states and native exotic-inclusive D4 widths, actual SusHi LO H/A rates, transferred HDECAY quark partial widths and heavy searches at explicit width scenarios, entire 64-case joined experimental diagnostic artifact. This is a genuine implementation, not a proposed integration.

**Still scientifically missing before *unqualified* physical Higgs acceptance:**

1. A defensible 95%-CL `h125` fit statistic and systematic treatment (including appropriate signal-strength covariance), consistent full h125 width/exotic decay error treatment, and actual model production/acceptance.
2. Complete heavy (H/A) widths and validated shape/acceptance and interference for (t\bar t) resonances with known partial `Γ/M` up to several percent; source 15673 has (H) sum/ mass **5.69%** and (A) **4.75%**.
3. Explicit observed searches for (H/A\to H_i^\pm W^\mp), neutral scalar cascades and relevant H1 and H2 production at other energies/final states. Some processes have no public HiggsBounds dataset entry; missing coverage is `UNKNOWN`, never `PASS`.
4. Neutral production scale/PDF and NLO/reweighting validation; source SusHi is genuinely LO. Public charged 4FS/5FS matching is improved but still has theory/experimental signal-hypothesis uncertainties.
5. Independent check of the accepted approximate Higgs screens on a **representative** scalar + lepton scan, not just 16 scalar witnesses × 4 deliberately LFV-suppressed Yukawa constructions.

**Decision:** For a normal EPJC phenomenology *leading-order constrained charged-cascade-survival* paper, the named Higgs screens are now operational and scan-ready **as approximation diagnostics**. No precision three-loop calculations or ATLAS detector-level study need be undertaken solely to extend these source-defined screens. The required next scientific step is a representative scan with the full missing-observable ledger; a headline claim of a globally allowed Zee region remains unproven.

## Code
- `research/full_constraints/pheno_paper_2026/h125_higgssignals_probe.py`
- `research/full_constraints/pheno_paper_2026/charged_h1h2_public_64.py`
- `research/full_constraints/pheno_paper_2026/hdecay_16_bridge.py`
- `research/full_constraints/pheno_paper_2026/merge_hdecay_64.py`
- `research/full_constraints/pheno_paper_2026/sushi_16.py`
- `research/full_constraints/pheno_paper_2026/heavy_HA_higgsbounds_envelope.py`
- `research/full_constraints/pheno_paper_2026/join_higgs_public_64.py`
