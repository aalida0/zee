# F2 — Peer-reviewed EOS NLO response versus flavio on the 27 original Zee points

**Status:** implementation committed, actual AF EOS/flavio evaluation NOT YET EXECUTED. Strict physical exclusion status UNKNOWN. This is ONE integrated 27-source-spectrum + dense Type-II controlled experiment, not a new scan.

## Scientific goal and essential distinctions

F1 finished using real flavio 2.7.0 + particle 0.26.2 (rather than incompatible flavio 2.7.1/particle 1.x) with 27 original B4 IDs; BR median 4.011324684×10^-4, range 3.947436208–4.170724872×10^-4. SM flavio baseline = 3.309692270×10^-4. F1 includes **LO charged Higgs matching** only and selected NNLO matrix-element terms; no 95% CL exclusion. **Never report the earlier synthetic test 27 B4_0000000...0026 output as physical!**

F2 uses real **EOS** public code:
- https://eoshep.org/doc/v1.0/observables.html , `B->X_sgamma::BR(E_min)@NLO` (E_min=1.6 GeV).
- https://github.com/eos/eos/blob/master/eos/rare-b-decays/inclusive-b-to-s-gamma.cc explicitly contains NLO `C1..C8`, virtual plus bremsstrahlung, chirality-flipped terms and an `E_min` cut. It is an older NLO formula, not Misiak et al 2015 full NNLO.
- WET EOS `model='WET'`, `b->s::c1 ... b->s::Re{c7}`, `b->s::c8` with EOS's **own default SM coefficients** (see https://eoshep.org/doc/reference/parameters.html ). At the EOS low scale `sb::mu=4.2GeV`, add only **NP DELTAS** RG-evolved from E4A high-scale matching using flavio's `WilsonCoefficients.get_wc('bsee',4.2,..., nf_out=5)` (which uses `wilson`).
- Real flavio independent inclusive matrix-element calculation: `flavio.np_prediction('BR(B->Xsgamma)',wc)`, same high-scale source. EOS **SM default** differs from flavio SM, so compare **`(BR_NP-BR_SM)` enhancements** within each program. Do NOT compare absolute branchings as an engine agreement threshold and do NOT renormalize EOS to flavio.

**Two input matching orders**, each consistently source-derived at E4A mu0=160GeV:
1. `LO`: `DeltaC7,DeltaC8` source LO with `cos²γ` and `sin²γ`. Source-pinned to F1 high-scale inputs. F2 must recalculate *every* real flavio F1 BR to absolute precision 3e-10 or STOP.
2. `NLO_matching`: include original SuperIso `CW_calculator` NLO `DeltaC3...C8` with factor `alpha_s^(5)(160)/(4pi)`; use same underlying raw operator definitions as E4A. Reject nonzero `C1,C2`. **This is NOT an independently verified full NLO BSM observable or complete NNLO matching**. SuperIso NLO dipoles were previously source-audited, but the scheme conversion and anomalous-dimension effects need independent confirmation. Retain the LO and NLO-matched comparisons side-by-side, and NEVER relabel the rate NLO/NNLO BSM accurate just because EOS is tagged `@NLO`.
3. **Do not include raw disputed NNLO SuperIso `C3...C6`** (A1Q discrepancy versus author supplement). Those unresolved residuals are a separate accuracy blocker.

**Dense Type-II curve:** F2 uses the already compiled E4A source-pinned probe binary `work/gateE4a_large_matching_typeII_27_v1/gateE4A_source_pinned_multiorder_matching` at equal H1/H2 masses and γ=0. It generates 300..1000GeV in 25GeV increments, plus 570,580,670GeV at both tanβ=5.6 and 50. Its 18 published E4A LO/NLO matching reference anchors are rechecked to <=3e-10 on both dipoles. This curve checks constructive signs and decoupling against both EOS and flavio; it DOES NOT reproduce the full-NNLO, historically quoted 2017 Type-II bound 580GeV because experimental average, nuisance and precision differ.

**Exploratory basis-response acceptance:** Both EOS NLO and flavio should exhibit constructive Type-II response and decreasing new-physics enhancement with larger charged mass. F2 reports the relative discrepancy of EOS and flavio **delta BRs**, requiring max <60% solely to flag gross basis normalization mistakes. Such a loose threshold is NOT a theory uncertainty, and passing DOES NOT mean NLO agreement to any publication accuracy. Use the numerical residuals for further diagnosis, including Wilson coefficient normalization, low-scale gamma conventions, `alpha_s` and differences between EOS's NLO and flavio's selected NNLO treatment.

**SuperIso comparison:** Optional `--e1-summary /path/to/original_E1/summary.json` performs a genuine SHA-verified 27-model comparison with original legacy SuperIso branching ratios. The code checks this E1 file's SHA256 against the `E4A` original `fingerprints_sha256.E1` and never substitutes a different dataset. Without that option, the comparison is explicitly absent.  E1 original separate-scheme predictions (3.8633–4.0419×10^-4) are NOT ingested into the F2 EOS likelihood. To compare them side-by-side, use real F1 `Zee_27_results` (legacy `old_SuperIso_BR_separate_scheme` only if E1 hash-matched) or the E1 report. F2 directly compares to F1 real flavio predictions, not a synthetic rate.

**No 2026 preprint** contributes constants or theory likelihood. Published calibration references: Misiak et al PRL 114 (2015) 221801, Hermann/Misiak/Steinhauser JHEP 11 (2012) 036, Misiak/Steinhauser EPJC 77 (2017) 201, and EOS EPJC 82 (2022) 290 DOI:10.1140/epjc/s10052-022-10177-4.

## How to run on UChicago AF (/home work; data elsewhere)

Use existing working F1 environment; do NOT upgrade flavio to 2.7.1 because particle 2022 table was removed in 1.x:

```bash
cd /home/aalida/zee
git pull --ff-only
source .venv-flavor-f1/bin/activate
python -m pip install 'eoshep'
python -m pip check
python - <<'PY'
import flavio, eos, wilson, particle
print('flavio',flavio.__version__, 'eos',getattr(eos,'__version__','unknown'),
      'particle',particle.__version__)
o = eos.Observable.make('B->X_sgamma::BR(E_min)@NLO',
                        eos.Parameters.Defaults(),
                        eos.Kinematics(E_min=1.6),eos.Options(model='WET'))
print('EOS_NLO_sm_test',o.evaluate())
PY

python -m py_compile \
  scripts/zee_gateF2_eos_flavio_nlo_27_validation.py \
  tests/test_zee_gateF2_integrated_eos_nlo_27.py

python -m unittest discover -s tests -p 'test_zee_gateF2_integrated_eos_nlo_27.py' -v && \
python -u scripts/zee_gateF2_eos_flavio_nlo_27_validation.py \
  --e4a-summary work/gateE4a_large_matching_typeII_27_v1/summary.json \
  --f1-summary work/gateF1_flavio_real_v3/summary.json \
  --output-dir work/gateF2_eos_flavio_nlo_validation_27_v1
```

F2 expects the E4A probe binary inside the E4A work directory; specify the explicit full path using `--e4a-probe` only if the binary was moved. `python -m pip install eoshep` installs the **EOS** Python package (do not `pip install eos`).

**Outputs:** `summary.json`; `F2_54_Zee_LO_NLOmatching_real_EOS_flavio.csv`; `F2_TypeII_dense_EOS_flavio_LO_NLOmatching.csv`. If EOS is missing/incompatible or coefficients disagree, **F2 exits non-zero**, records `F2_EOS_OR_MATCHING_OR_BASIS_VALIDATION_BLOCKED_NO_EXCLUSION`, and prints a complete traceback path. The single offline Python unittest uses an explicit **TOY** quadratic response, never physical rates.

**Never interpret F2's reported 60% exploratory residual tolerance as validation of perturbative uncertainty.** Full Zee allowed-point claims require proper NLO/NNLO matching implementation, uncertainty calibration, neutrino/LFV/full-theory and scalar-vacuum viability checks. The 2017 Type-II bound is not an automatic Zee per-state exclusion.
