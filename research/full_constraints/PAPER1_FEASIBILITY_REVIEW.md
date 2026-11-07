# Paper 1 feasibility review: Zee Type-II charged-scalar cascade

**7 November 2026 — evidence baseline `3c276d3391aa6c6723d2a2847f8d57e3febea98d`.**
Read with [scope decision](PAPER1_SCOPE_DECISION_2026-11-07.md) and [source-rescue audit](LITERATURE_SOURCE_RESCUE_AUDIT_2026-11-07.md). This is a publication assessment, not a scope change, scan authorization, or physical acceptance decision. Only saved records were joined; no physics program was executed or changed.

## 1. Recommendation

**NO-GO for submission or a final parameter-space campaign now.** Route A, a fully constrained parameter-space paper, is blocked. Route B, a conditional phenomenological study, is technically possible but its stand-alone novelty is **not yet demonstrated**. Recommend considering B only after explicit user approval and agreement on a narrower scientific claim. Do not start another loop project to postpone this decision.

The positive finding is substantial: the original 33 sufficient tree-vacuum certificates have an exact intersection with 16 saved production spectra and 64 neutrino-family records. Several have fb-scale conditional cascade rates. The negative finding is equally important: the same families barely change the cascade rate, and prior work already proposed this decay, its dominant daughter decay, benchmark regions, production comparisons, and a neutrino connection. We have useful benchmarks, but no established new exclusion, robust neutrino signature, or collider sensitivity result. A provenance-rich rate catalogue alone is a weak paper.

## 2. What prior work already establishes

“Type II” here specifies the quark Yukawas, with general complex leptonic Yukawas and an antisymmetric singlet coupling. Imposing the same natural-flavor-conservation restriction on leptons would change the neutrino problem. Neither seed paper covers exactly our entire chosen model and workflow; that difference alone is not a physics discovery.

| Source and full-text locator | Verified scope and principal results | Consequence for our claim |
|---|---|---|
| Herrero-García, Ohlsson, Riad, Wirén, [JHEP 04 (2017) 130](https://doi.org/10.1007/JHEP04(2017)130), [1701.05345v2](https://arxiv.org/abs/1701.05345v2), §§2.4–2.5, 3–4; Table 2; Figs. 3–12 | Two doublets plus charged singlet; general lepton setup, but the numerical study uses the texture in §2.4, scalar-coupling zeros in §3.1, and both quark types coupled to one doublet in §2.5. A 19-real-parameter MultiNest likelihood study treats neutrinos, LFV, Higgs and EWPO. Fig. 8 connects singlet Yukawa and charged mixing; Fig. 9 gives mass splittings. | Neutrino reconstruction, LFV correlations and charged-mixing correlations are **previously studied**. Their “full scan” is within stated restrictions, not an unrestricted theorem about our Type-II model. Our fixed-target inverse families are not a replacement likelihood fit. |
| Florentino, Romão, Silva, [EPJC 81 (2021) 1148](https://doi.org/10.1140/epjc/s10052-021-09956-2), published §§3–8, Table 2, Figs. 1–14 | Type-II scalar/quark construction; lepton constraints omitted. §4 includes B, Higgs, STU, BFB/unitarity and numerical charge-breaking searches. Fig. 9 gives the cascade mixing/mass dependence; Figs. 10–13 give four benchmark regions; Fig. 14 compares charged production × tb BR with search limits. §8 explicitly calls for neutrino/flavor completion. | The vertex, cascade, large BR, H1→tb signature, mixed-state B treatment and benchmark production comparisons are **previously done**. The proposed extension addresses their stated future work, rather than discovering the cascade. |

The published 2021 version matters: it has §8 “Perspectives for future work,” §9 conclusions, Appendix D.3 Eq. (D.20), and **14** figures. The downloaded arXiv v1 has different organization and 15 figures; its locators must not be substituted for journal locators.

Relevant subsequent and adjacent full texts further narrow the novelty:

- Heeck–Thapa, [PLB 841 (2023) 137910](https://doi.org/10.1016/j.physletb.2023.137910), [2303.13383v2](https://arxiv.org/abs/2303.13383v2), §§II–V, Figs. 3–4: general complex lepton matrices, alignment and neglected extra-doublet quark couplings; anomaly-conditioned neutrino/LFV predictions. It is not our Type-II production analysis. Its historical anomaly assumptions are not imposed here.
- Dev–Heeck–Thapa, [EPJC 84 (2024) 148](https://doi.org/10.1140/epjc/s10052-024-12496-0), [2309.06463v2](https://arxiv.org/abs/2309.06463v2), §III.A, Eqs. (4)–(9), Fig. 2: neutrino-texture/LFV/collider complementarity at μTRISTAN, including neutral-scalar production. Thus “connecting Zee neutrinos to colliders” is already too broad a novelty claim.
- [Drell–Yan constraints on charged scalars](https://arxiv.org/abs/2501.09796v1), §§2–4, Table 1, Figs. 3–6, explicitly includes Zee doublet–singlet mixing. Pair-production limits depend on gauge projection, BR and topology. These are additional applicability checks, not limits already applied to our associated-production records.
- Machado et al., [1707.06977v1](https://arxiv.org/abs/1707.06977v1), §II and Appendix A, already give a general analytic Zee solution with homogeneous freedom. Chen, [2508.18757v2](https://arxiv.org/abs/2508.18757v2), §§II–IV, discusses the null-vector identity and four free leptonic Yukawa entries. **Inverse reconstruction or freedom to suppress selected LFV entries is not itself new.** No formula is rederived or newly certified here.

**Precisely the remaining candidate contribution:** quantify how *positive full-complex tree-vacuum certificates*, exact neutrino-family reconstruction and scoped scalar EWPO coexist with source-bound Type-II cascade production, and whether this combination yields a new experimentally useful distinction. Certificate-backed benchmark retention is a defensible methodological addition relative to numerical minimum searches; claiming the first vacuum-constrained Zee cascade is false. A robust new physical correlation or a qualified new collider analysis would be the stronger addition. Neither is established by the present saved sample.

## 3. What the saved records actually support

**Join, not regeneration.** The preserved `/tmp/zee-d14c-dataset.json` contains 900 rows at 225 scalar IDs (two families per ordering). Its SHA256 matches the frozen export. All scalar IDs pass the saved reconstruction/BFB/unitarity and selected scalar-STU gates; 33 have a sufficient positive vacuum certificate, 192 are UNKNOWN. The certificates concern the exact reconstructed tree potentials, not quantum/thermal stability or a neighborhood of rounded benchmark values.

The 13 TeV map joins **16/33** certified IDs:
`2264, 2616, 3693, 4611, 8294, 8850, 9454, 11016, 13345, 14074, 14187, 14555, 14984, 15591, 15673, 16385`.
Certified IDs without mapped production are
`3771, 4110, 4802, 5420, 5602, 7771, 8523, 9305, 9540, 10200, 11590, 13100, 13991, 14210, 16622, 19181, 19211`.
Missing rates remain unknown.

For every one of the 64 mapped families, direct checks against the raw saved rows found matching scalar hash, Module2 input hash, ordering/family, exact cascade BR, positive vacuum certificate, scalar gates and neutrino closure. Global acceptance stays null. The map has one integration per scalar/energy, not four statistically independent productions. This checks saved consistency, not a rerun of certificate or generator validation.

**Selection bias:** these 16 are precisely the intersection with the old **approximate B diagnostic** shortlist. The other 17 certificates must not be discarded as physically excluded. Consequently neither the mapped mass floor nor its rate ranking defines the physical allowed region, optimum, or retention efficiency. The six nominal-compatible sub-TeV H2 opportunities remain vacuum UNKNOWN and have no mapped production. Do not fill these gaps by interpolation.

| Historical scalar ID | mH1, mH2 [GeV] | γ [rad]; tanβ | Saved H2→H1Z tree BR range | Saved σ13 × BR [fb] | Benchmark use |
|---|---:|---:|---:|---:|---|
| 15591 | 442.593, 1035.704 | 1.29691; 1.19828 | 0.326034–0.326065 | 3.86937–3.86974 | Largest rate in this shortlist |
| 8850 | 494.699, 1077.158 | 1.25682; 1.17086 | 0.350311–0.350338 | 3.45824–3.45850 | Similar rate, different daughter mass |
| 2264 | 674.274, 1165.975 | 0.85450; 1.05358 | 0.368649–0.368658 | 1.84376–1.84380 | Higher BR, lower production-weighted rate |
| 15673 | 714.508, 1277.363 | 1.25341; 1.32845 | 0.393753–0.393787 | 1.17638–1.17648 | Higher BR again, smaller rate |
| 14555 | 868.676, 1360.627 | 0.29130; 5.57280 | 0.301061–0.301086 | 0.00424918–0.00424953 | Demonstrates why sizable BR is insufficient |

Ranges span saved families, **not uncertainties**. Production is charge-summed LO 5FS bg→tH2, NNPDF30 LO, μR=μF=mH2; tree BR includes the saved on-shell two-body ledger. It excludes H1, Z and top decays, efficiency and acceptance. Numerical integration errors are approximately 0.16–0.22%; scale/PDF/decay theory errors are unknown. Separate actual 14 TeV integrations give cascade rates 5.29609–5.29660, 2.57508–2.57515 and 1.66735–1.66749 fb for 15591, 2264 and 15673. They cannot rescale the other spectra.

**At least two useful conditional benchmarks exist:** 15591 versus 2264 separates daughter mass, mixing and rate; 14555 supplies a low-production comparison. H1→tb is about 99.75–99.76% for 15591, 99.69–99.70% for 2264, but 80.81–81.03% for 14555. Saved H2 width/mass ratios across the 16 span 2.32–8.97%; even a factorized collider interpretation needs finite-width/acceptance justification. Rounded table entries must never define replacement cards.

**The correlation case is weak.** Across four families at each mapped scalar, relative cascade-BR spread is only 0.000573–0.0291%. Production is family-independent at fixed scalar input. These selected witnesses show coexistence of neutrino reconstruction and a sizable cascade, not measurable ordering discrimination or a neutrino-enforced rate prediction. EWPO/certificate selection also lacks a matched counterfactual sample, so a scatter cannot establish causation.

The independent saved [D12 audit](../../module12/D12_FLAVOR_COLLIDER_AUDIT.md) supplies a more informative caveat: at exact certified D7/F13 potentials, homogeneous Yukawa directions can change daughter leptonic BRs substantially, while selected textures suppress implemented LFV with little cascade change. Its partial LFV rates are neither upper nor lower bounds on full rates. These historical D7/F13 identities do **not** acquire the D14 production receipts by matching masses approximately. D12 supports texture dependence, not an unavoidable flavor–cascade relation.

## 4. Defensible manuscript, at most four principal figures

Suggested structure: (1) precise question and comparison with prior work; (2) model restrictions, perturbative orders and certificate method; (3) saved conditional benchmark population and selection biases; (4) production/decay and texture dependence; (5) collider interpretation limits and unresolved constraints. Use two tables only: prior-work/coverage and exact benchmark/provenance specifications.

1. **Certified historical spectra and cascade strength:** mH1 versus mH2, color saved cascade BR; distinguish 33 certificates, 192 UNKNOWN, and 16 production matches. **Previously done:** mass/mixing cascade plots (2021 Fig. 9). **Candidate new:** explicit certificate retention with exact neutrino closure. Saved sources suffice; not an allowed-space map or statistical density.
2. **Production-weighted cascade ranking:** σ13×BR versus mH2 for 16 spectra, with only three actual 14 TeV counterparts. **Previously done:** benchmark production and large BRs. **Incremental extension:** directly bound model cards, family ranges and rate/BR reordering. Saved sources suffice; show numerical errors separately from unknown theory errors. No exclusion/reach contour.
3. **Paired texture dependence:** saved D12 D7/F13 family changes in cascade and H1 leptonic BRs at fixed scalar potential; label any LFV panel “implemented subset; conditional on unimplemented constraints.” **Previously done:** Yukawa freedom and flavor/collider correlations. **Candidate new:** its quantitative effect on this cascade's daughter composition with positive certificates. Saved witnesses suffice, but no claim of inevitability or fitted population; production for these exact spectra remains missing.
4. **Conditional reserve only: collider sensitivity.** **Potentially stronger new result**, but unsupported now. Requires a distinct final state/reconstruction, matched signal, backgrounds, detector response, systematics and a statistical model. Otherwise omit this figure and all “reach” language. Three honest figures are preferable to a fourth unsupported result.

## 5. Publication routes and reviewer assessment

**A — fully constrained parameter space: NO-GO.** Scalar/tree tests, fixed-target one-loop neutrino reconstruction, scoped scalar STU, positive certificates and tree/LO cascade inputs are available within their declared scopes. They do not close B/LFV/Higgs. Required external decisions are: a flavor specialist's Wilson-dependent B uncertainty/confidence prescription; independent complete relevant LFV matching, coherent operators and corrected conversion nuclear response; and qualified Higgs rates/total widths with process/energy applicability and uncertainty. Vacuum UNKNOWN needs an explicit classification policy or restriction to positive certificates. “Complete” must be defined at a justified perturbative order; it need not mean every perturbative order. No two eigenstate-by-eigenstate 670 GeV veto is valid. Compiled SPheno is not validated full-loop physics. These are unresolved project dependencies, not assignments to implement more loops during this review.

**B — explicitly scoped phenomenology: technically feasible, publication case conditional.** Proposed title direction: “Conditional charged-scalar cascade benchmarks in a neutrino-reconstructed Zee model.” Report only certificates and applied scalar/neutrino/EWPO scope; B/LFV/Higgs remain UNAPPLIED/UNKNOWN as physical exclusions. Fixed-card h125 γγ/Zγ and width-independent ratios are calculable diagnostics; uncertified total widths do not yield absolute signal strengths. The VBF-bb width endpoint shifts in the scope decision are sensitivities, not theory-error bounds. Full-field quantum vacuum stability is not claimed. Remaining mandatory observables still prevent global acceptance, even for attractive rates.

The main likely reviewer objections are substantive:

- **“This repeats 2021.”** Correct for the decay, dominant tb daughter, large BR and basic production plots. Certificates plus exact neutrino witnesses improve rigor, but require a consequential new result to sustain a strong physics paper.
- **“The promising points may disappear once flavor/Higgs is imposed.”** Unresolved. Partial amplitudes can interfere with missing terms; neither subset failure nor small subset rates settle the full verdict. B needs an agreed uncertainty prescription. Conditioning cannot be hidden in a caption.
- **“Where is the neutrino prediction?”** Present witnesses show weak cascade dependence and broad texture freedom. Two fitted ordering examples are not an ordering test or generic correlation.
- **“Where is collider sensitivity?”** Absent. The [ATLAS tb search](https://doi.org/10.1007/JHEP06(2021)145), §§3–7, uses 139 fb−1 at 13 TeV with specific tb topology, selections and background likelihood. Its limits cannot be applied directly to tH2→tH1Z→ttbZ. A rate times luminosity is a preselection yield, not significance. No saved efficiencies, background/control-region model or CLs construction establishes HL-LHC reach. Do not transfer limits solely by final-state overlap or use S/√B as a 95% CL limit.

**Decision criterion:** approve B only if the agreed manuscript center is a demonstrably useful conditional result beyond the earlier benchmark study, with collider claims limited to rate forecasts unless a separate sensitivity study is authorized. If that scientific center cannot be agreed from these findings, postpone or revise the paper. A conditional label is necessary but does not by itself make an incremental result publishable. Any future single final scan requires a separate explicit authorization; neither route is activated here.

## 6. Evidence ledger and search limits

Read-only checks used Python standard-library JSON/CSV joins, assertions and SHA256, and `pdftotext -layout` for downloaded papers. No modules were imported, cards reconstructed, tests rerun, generators launched or scans performed. Baseline working tree was clean. Frozen feature parent remains `133a34061723b6bb45b19e8ebe29852ac8b5a9c2`.

Quantitative source SHA256 (paths relative to repository unless absolute):

```text
2d97c2a58cb65f5ec7244282a04c5e19a0cae0897b8a0581b76503180acd4be9 /tmp/zee-d14c-dataset.json
3faaf10eb8b986405a0c093800fb86d1a6ab7c0e1e3e5247adbc47315b56f0d9 module14/conditional_scan/remote_conditional_summary.json
8cd85188cfc8259b4e838f1cea990b68a86c27801c8c36b1c33eaad9bc30018a module14/conditional_scan/candidate_followup.json
95510ec92f95d4598d85e64a1163da949dc0ce529b63ef5e536f0a6a4f2f7aab module14/conditional_scan/production_map_13_14.json
7ef861c81f07422a002dbaf9db1e49c198724b6ffd2bd9fca0d7168dff811f4f module14/conditional_scan/production_map_13TeV_families.csv
a42840e948f935c8ca87bf9f56c4ffe586c08bf16402ca3e3df7e82cffb87ce9 module14/conditional_scan/production_map_scalar_rates.csv
f31ef3ccb64c3e4ff53131d35d52c21536b951a01e2c3924af766b7b2adf1cd8 validation/module12/d12_benchmarks.json
```

These committed bundles retain scalar, Yukawa, decay and production receipt hashes; full native artifacts remain under the locations in [PRODUCTION_MAP_REPORT.md](../../module14/conditional_scan/PRODUCTION_MAP_REPORT.md). The raw dataset is host-local; do not assume it survives elsewhere. D12 numbers/interpretation come from its saved report and `validation/module12/d12_benchmarks.json`; no new D12 solutions were evaluated.

Literature search on 7 November 2026 used primary arXiv/journal full texts and INSPIRE. Queries included `Florentino Romao Silva 2021 charged Higgs Zee 09956`, `Herrero Garcia Ohlsson Riad Wiren 2017 full parameter scan Zee model 130`, `"Zee" "charged" "cascade" 2023 2024 2025 2026`, and `"2106.08332" citations charged scalar 2025 2026`. INSPIRE seeds `arxiv:1701.05345` and `arxiv:2106.08332` resolve to records 1509928 and 1868828. Correct forward queries `refersto:recid:1509928` and `refersto:recid:1868828`, `size=250`, returned **73/73 and 16/16** indexed records respectively; one page each, all returned titles screened. An initial mistyped record query returned unrelated axion papers and was discarded. Bibliographies contain 123 and 56 indexed reference entries; relevant backward links screened include 2021→2017, 2021→Barroso–Ferreira (2005), 2021→Babu et al. (2020), and 2025 Yukawa→2017 analytic reconstruction. Only selected relevant full texts were read; the earlier rescue audit supplies the vacuum reference trail. Singlet-only, Zee–Babu, scotogenic, Dirac and 3HDM studies are not exact-model substitutes. Citation indexing and title screening are not exhaustive novelty proofs; no unimplemented expression is asserted absent from literature.

Forward-response SHA256 (temporary JSON, not redistributed): 2017 `daae3fdc9f928599530fe59a6c752039c003cd3c4a0562af83dff461981c636f`; 2021 `5105e39ed031fad6e920e0f19b1c102253f4a159c5af704ee38466714e4c6931`.

Downloaded seed PDF SHA256: 2017 arXiv v2 `f62a88ff26b0d84806e37874e09574f95282108fc7ef18d9e6a7dc9de6cfd62a`; 2021 journal `322bba3db966f8277a30131eb9ef8b5cbc7fd83c49a9c5c93e07e2a382519a8b`. Journal locators take precedence. The review identifies a possible contribution, not priority certification or journal acceptance.
