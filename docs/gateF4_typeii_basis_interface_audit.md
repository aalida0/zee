# F4: effective-dipole basis-interface audit — conditional Type-II pilot

**Status:** `NOT_YET_VALIDATED` if the pilot runs successfully; `BLOCKED` on source/probe errors. This is not an independently validated inclusive NLO rate or a Zee exclusion.

## 1. Finding and why it matters

The committed F3 probe `scripts/zee_gateF3_fullNLO_rg_probe.c` feeds `CW_calculator` (high-scale C0/C1/C2) to `C_calculator_base1` (low-scale C0b/C1b/C2b). The F3 Python `net_low` combines NP deltas as C0b + alpha_s(mu_b)/(4 pi) C1b and submits C1..C8 without a dipole inverse transformation through `RatePair.eos_rate`.

In a public modern SuperIso source implementation, `C_calculator_base1` defines `C0w7/8`, `C1w7/8` and `C2w7/8` as **effective** combinations and evolves them into its `Cnb[ie]` output using `U0, U1, U2`. The exact isolated A1M modified AF source must pass the same signatures and its SHA256 manifest; a similar publicly available repository is **not** equivalent to proving the A1M source.

EOS (pinned inspected upstream commit `3eb16b5b7265df7023363e615179fd44a1a02d00`, file `eos/rare-b-decays/inclusive-b-to-s-gamma.cc` lines 344–354) applies the **effective rotation** when evaluating `c7eff(wc)` and `c8eff(wc)`. It constructs an amplitude `D = c7eff(wc) + alpha_s/(4 pi) * [r_i + gamma_i7 log] * c_i` (lines 356–384) and evaluates squared amplitudes at NLO (lines 537–541). EOS's installed Python-package C++ source and version have **not** yet been fingerprinted to this public commit.

If the AF source-pinned routine indeed returns effective low-scale dipoles, supplying them directly as EOS raw c7,c8 applies the rotation twice. That invalidates interpretation of F3's full-source-NLO conditional EOS numbers **until recalculated**. It does not retroactively establish a particular numeric correction.

Standard effective weights in the tested source and EOS:
- `y7={C3:-1/3,C4:-4/9,C5:-20/3,C6:-80/9}`.
- `y8={C3:+1,C4:-1/6,C5:+20,C6:-10/3}`.

The F4 pilot reconstructs `C7_raw = C7_eff - sum(y7_i*C_i)`, likewise C8, checks round-trip algebra, and compares conditional EOS direct versus inverse-basis rates. The **C1..C6 finite renormalization / evanescent operator scheme mapping remains unverified**. Even a perfectly closed algebraic transformation cannot certify the NLO scheme.

## 2. Perturbative bookkeeping and limitations

The EOS kernel includes terms quadratic in injected NLO Wilson shifts and NLO-kernel-times-NLO-coefficient cross terms. To expose nonlinear contamination the pilot measures `[R(C0+h)-R(C0-h)]/2` and `[R(C0+h)+R(C0-h)]/2-R(C0)`, where `h` is the difference between low coefficients evolved with LO versus full NLO *high-scale* NP matching. The **even** part is at least quadratic in this insertion, hence formally higher order; the **odd** part can still contain NLO matrix element times NLO matching corrections, so is NOT a fully isolated strict fixed-order NLO coefficient. A strict fixed-order extraction requires expanding both amplitude and rate kernels consistently.

The inherited F3 `lo=net_low(mode0)` contains NLO **running induced by LO high-scale matching**. It is *not* the LO-QCD-only evolution.

The F4 pilot uses real EOS and SuperIso on AF, but may not be used for 95% CL classifications. No 27-spectrum runs are authorized by this gate.

## 3. Explicit gate table

| Test | Acceptance criterion | Meaning |
|---|---|---|
| A1M source identity | `check_superiso_source` SHA256/provenance succeeds | Audited isolated vendor, not substituted source |
| Six effective definitions | all high-order 0/1/2 C7eff/C8eff terms and signs match exactly | Source-level rotation established |
| Low output trace | U0/U1/U2 evolve effective Cw7/8; no explicit inverse low Cb7/8 assignment | Suspected effective low outputs supported by source |
| Algebraic closure | corrected raw C7/8 re-effective under EOS standard weights within 2e-14 scaled | No purely algebraic double rotation |
| Actual Type-II benchmark | exactly 8 rows: masses 300/580/670/1000 GeV each at tanbeta 5.6 and 50 | Controlled pilot, no all-27 rerun |
| Nonzero NLO matching | at least one NLO C4 matching input materially nonzero | Probe exercises four-quark channel |
| EOS diagnostics | conditional original/direct and inverse rates, NLO insertion odd/even components, complete CSV | Quantifies numerical impact |
| EOS installed kernel provenance | EOS version recorded, C++ build not source-pinned | **Still blocks** physical mapping |
| NLO scheme + independent reference | finite renormalization, C1..C6 scheme and NLO Type-II rate/scale test | **Still blocks** paper-ready prediction |

## 4. UChicago AF commands (fresh results only)

```bash
cd /home/aalida/zee
git fetch origin gateA1p-independent-hepfit-typeii-matching
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source .venv-flavor-f1/bin/activate
python -m pip check
python -m py_compile scripts/zee_gateF4_typeii_basis_interface_pilot.py \
  tests/test_zee_gateF4_typeii_basis_interface.py
python -m unittest discover -s tests \
  -p 'test_zee_gateF4_typeii_basis_interface.py' -v

# Choose another fresh directory if this exists. No code executed on /data.
python -u scripts/zee_gateF4_typeii_basis_interface_pilot.py \
  --vendor-root work/gateA1m_isolated_nlo_v1/isolated_superiso \
  --a1m-provenance work/gateA1m_isolated_nlo_v1/source_patch_provenance.json \
  --output-dir work/gateF4_typeII_basis_inverse_8_v1 \
  2>&1 | tee work/gateF4_typeII_basis_inverse_8_v1_run.log

cat work/gateF4_typeII_basis_inverse_8_v1/summary.json
cat work/gateF4_typeII_basis_inverse_8_v1/F4_8_TypeII_basis_interface_CONDITIONAL.csv
```

**Return** the full unit-test output; the `F4_STATUS` line and `summary.json` status/source checks; and the eight numerical CSV rows. The EOS and SuperIso installed source identities must then be checked before advancing to a strict fixed-order and independently matched NLO calculation.

## 5. References

- Repository F3: `scripts/zee_gateF3_fullNLO_rg_probe.c`, `scripts/zee_gateF3_fullNLO_source_RG_27.py`, `scripts/zee_gateF2_eos_flavio_nlo_27_validation.py`.
- Exact A1M source: AF-only `work/gateA1m_isolated_nlo_v1/isolated_superiso/src/wilson.c`, checked using `source_patch_provenance.json`.
- Inspected analogous SuperIso file: https://github.com/YancyW/SuperISO_GPU_Batch/blob/39e7c45243cad2935059e063d03f5b83f8a2cb2f/src/wilson.c
- Inspected EOS source: https://github.com/eos/eos/blob/3eb16b5b7265df7023363e615179fd44a1a02d00/eos/rare-b-decays/inclusive-b-to-s-gamma.cc
- Independent Type-II source: HEPfit `THDMMatching::setWCbsg`, anchored to prior A1P source/manifest.
- Peer-reviewed physics: Chetyrkin, Misiak, Münz, Phys. Lett. B400 (1997) 206; Hermann, Misiak and Steinhauser, JHEP 11 (2012) 036; Misiak and Steinhauser, EPJC77 (2017) 201.

**No AF run performed by this GitHub-only commit.**
