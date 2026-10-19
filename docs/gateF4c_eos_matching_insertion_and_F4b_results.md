# F4b AF interpretation + F4c conditional EOS matching-insertion audit

## F4b AF results received (20 October 2026)

This note records **user-provided AF outputs**, not an independently executed job.

### Independent HEPfit high-scale matching: 40/40 numerical agreement

| Diagnostic | AF result |
|---|---|
| source-matched \(\mu_W\) | 160.0 GeV |
| low scale \(\mu_b\) | 4.2 GeV |
| \(m_t(\mu_W)\), from actual SuperIso source | 163.16587299291515 GeV |
| source \(\alpha_s(\mu_W)\) | 0.10877484993481065 |
| source \(\alpha_s(\mu_b)\) | 0.22469749369105324 |
| F4 previous flavio \(\alpha_s(\mu_b)\) | 0.22553124753926662 |
| relative source minus flavio difference | -0.00369684404 (~-0.370%) |
| Type-II points | 8 (300,580,670,1000 GeV; \(\tan\beta=5.6,50\)) |
| independent HEPfit comparisons | 40 (LO C7/C8 and NLO C4/C7/C8) |
| disagreements | **0** |
| maximum absolute discrepancy | 1.2878587085651816e-14 |
| maximum relative discrepancy | 3.71224467833047e-12 |
| full NLO rate validated | **false** |
| paper-ready 95% CL exclusions | **false** |

The independent reference is a SHA-provenance-pinned HEPfit Type-II matching *formula* implementation, not independent RG evolution or observable calculation. The 40/40 agreement proves numerical formula agreement **under aligned conventions/input masses**, not the finite-scheme matching of the two low-scale rate codes and not an independent inclusive rate. Original HEPfit NNLO disagreements remain unresolved.

### Strict-order squared effective-dipole projector

The F4b output reports the following **dimensionless NP-minus-SM \(|C_7^{\rm eff}|^2\) response**, rather than an inclusive branching fraction:

| tanβ | mH± (GeV) | \(Q_7^\mathrm{LO}\) | \(Q_7^\mathrm{O(\alpha_s)}\) | LO+NLO truncated | partial \(a_s^2\) square |
|---:|---:|---:|---:|---:|---:|
| 5.6 | 300 | 0.061759080 | -0.017548660 | 0.044210420 | 0.001126376 |
| 5.6 | 580 | 0.028304671 | -0.009093756 | 0.019210914 | 0.000608314 |
| 5.6 | 670 | 0.023429184 | -0.007758734 | 0.015670450 | 0.000523104 |
| 5.6 | 1000 | 0.013475371 | -0.004874808 | 0.008600563 | 0.000335185 |
| 50 | 300 | 0.061465480 | -0.017489095 | 0.043976385 | 0.001123363 |
| 50 | 580 | 0.028208042 | -0.009074658 | 0.019133383 | 0.000607371 |
| 50 | 670 | 0.023354758 | -0.007744190 | 0.015610568 | 0.000522394 |
| 50 | 1000 | 0.013440096 | -0.004868214 | 0.008571882 | 0.000334877 |

The partial \(a_s^2\) term amounts to approximately 2.5–3.9% of the truncated LO+NLO *dipole-only* response. It is **not** the complete NNLO rate or a missing-theory-error estimate.

At \(\tan\beta=5.6\), \(m_{H^\pm}=300\) GeV, the NLO-matching-induced contribution to the effective dipole projector is approximately \(-0.008182028\), including an \(\mathcal O(10^{-6})\) extra four-quark contribution \(+4.539206\times10^{-6}\). The relative size of this four-quark-induced projection does not directly determine its relative effect on the full inclusive EOS BR, which includes operator-dependent NLO matrix elements.

The unchanged isolated A1M hashes are SHA256(\`wilson.c\`) \`a9c12d12e7879354518e2b6d5d777c4f25997b9477d0a4dc35750c3c7a61d03e\`; SHA256(\`libsuperiso.a\`) \`5d688deae4effd9f5916cd8976a9ca49f8a7fb598299d0f80f014e76b5c3a986\`.

## Next narrow step: F4c — EOS quadratic-in-Wilson matching response

\`scripts/zee_gateF4c_eos_matching_insertion_audit.py\` is a **source-linked conditional EOS sensitivity audit**, not a strict O(\(\alpha_s\)) inclusive-rate calculation.

EOS v1.1 inclusive implementation: https://github.com/eos/eos/blob/v1.1/eos/rare-b-decays/inclusive-b-to-s-gamma.cc .
The file's pinned Git blob SHA is \`3bbb034b920709503b767fb372f35338ae427877\`, corresponding to tag \`v1.1\`, but the actual AF-installed binary's build-source identity has not yet been certified.

At fixed EOS model parameters and a fixed \(\alpha_s\) inside the EOS kernel, the complete NLO EOS observable, as a *function of inserted low-scale Wilson coefficient deltas*, is quadratic. This follows from the structure \(|D|^2+A+|C_7^{eff}|^2 hqe\) where each \(D\) is linear in WCs and \(A\) is WC-bilinear with a coupling-dependent prefactor.

Construct the SuperIso low-scale vectors from the same source-matched \(\alpha_s^\mathrm{SuperIso}(\mu_b)\):
- \(\delta C^\mathrm{LOhigh}\): LO high-scale matching, NLO source RG;
- \(\delta C^\mathrm{DIP}\): additional NLO high-scale dipole matching;
- \(\delta C^\mathrm{FULL}\): additional NLO high-scale C3..6 matching.

Convert the low-scale **effective** dipoles to EOS **raw** dipoles using the previously source-checked inverse. Define \(h_D=\delta C^\mathrm{DIP}-\delta C^\mathrm{LOhigh}\) and \(h_Q=\delta C^\mathrm{FULL}-\delta C^\mathrm{DIP}\).

For each of eight Type-II points, probe

\[
R(t) = R_{\rm EOS}^{\rm NLO\,kernel}[\delta C^\mathrm{LOhigh} + t (h_D+h_Q)] .
\]

At **fixed EOS coupling and input parameters**, decompose this into

\[
R(t)=R(0)+tL+t^2 Q,
\quad L=\frac{R(1)-R(-1)}{2},
\quad Q=\frac{R(1)+R(-1)}{2}-R(0).
\]

Verify the polynomial against independent \(t=\pm1/2\) and \(t=2\) probes. Repeat with \(h_D,h_Q\) individually. Report the linear responses \(L_D,L_Q\) and quadratic interference cross term \(Q_\times = Q_{\rm total}-Q_D-Q_Q\).

**Critical interpretation:** \(L\) and \(Q\) are linear and quadratic in the **NLO matching insertion**, *not* a proof that the full inclusive observable is strictly truncated in \(\alpha_s\). In particular \(L\) itself contains formal \(\mathcal O(\alpha_s^2)\) contributions when EOS NLO matrix elements act on inserted NLO WCs. \(Q\) is formally beyond NLO in that insertion. The complete strict fixed-order EOS rate, including its NLO matrix elements, bremsstrahlung and power corrections, remains unimplemented.

The source \(\alpha_s\) differs from flavio's previous low-scale coupling, and EOS evaluates its own \(\alpha_s\) internally. F4c explicitly reports this inconsistency instead of silently treating the mixed-input conditional rates as physical results.

### AF run

~~~bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source .venv-flavor-f1/bin/activate
set -o pipefail

python -m py_compile scripts/zee_gateF4c_eos_matching_insertion_audit.py \
  tests/test_zee_gateF4c_eos_matching_insertion_audit.py

python -m unittest discover -s tests \
  -p 'test_zee_gateF4c_eos_matching_insertion_audit.py' -v

python -u scripts/zee_gateF4c_eos_matching_insertion_audit.py \
  --f4-summary work/gateF4_typeII_basis_inverse_8_v1/summary.json \
  --f4b-summary work/gateF4b_dipole_order_8_v1/summary.json \
  --f4b-hepfit-summary work/gateF4b_independent_hepfit_8_v1/summary.json \
  --output-dir work/gateF4c_EOS_matching_quadratic_8_v1 \
  2>&1 | tee work/gateF4c_EOS_matching_quadratic_8_v1.log

cat work/gateF4c_EOS_matching_quadratic_8_v1/summary.json
cat work/gateF4c_EOS_matching_quadratic_8_v1/F4c_8_TypeII_quadratic_EOS_matching_insertion.csv
~~~

If any status is \`F4C_BLOCKED_NOT_STRICT_NLO\`, inspect the full traceback; do not overwrite the old work directory. If the source or binary fingerprint mismatches, do not relax the check.

### Following step after this audit

A true full NLO calculation needs independently verified C1..C8 operator definitions, NDR/evanescent conventions, matched \(\alpha_s\) and mass schemes; then a source-pinned order-by-order extraction of EOS's \(D\), \(A\), and HQE contributions with explicit expansion to \(\mathcal O(\alpha_s)\), and comparison with an independent Type-II inclusive result including scale variation. These are **not** certified by F4b or F4c.

**Publication-quality Zee \(B\to X_s\gamma\) exclusions remain UNKNOWN.**
