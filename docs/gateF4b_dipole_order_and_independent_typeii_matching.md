# Gate F4b — Strict-order dipole projector and independent Type-II NLO matching

**State:** Implemented in GitHub, awaiting *real* UChicago AF execution. This is **not** an implementation of the complete inclusive \(\overline B\to X_s\gamma\) NLO observable. No statistical allowed/excluded labels.

## A. Why this is a new, narrower physical test

F4 successfully diagnosed the effective-dipole interface, and the eight-point source-inverse correction was numerically small. The full EOS v1.1 inclusive observable involves

\[
D = C_7^{\rm eff} + a_b \sum_{i=1}^{8} (r_i+\gamma_{i7}\log[m_b/\mu_b])C_i^{\rm (eff\ where\ appropriate)},\qquad
a_b=\alpha_s(\mu_b)/(4\pi),
\]

together with bremsstrahlung, nonperturbative/HQE terms, and an overall phase-space/CKM/mass normalization. EOS's implementation squares \(D\) and contains an exponential in the bremsstrahlung contribution. Merely setting NLO Wilson coefficients in EOS is **not** a strict fixed-order truncation.

We therefore make **no** claim yet that we have extracted the *complete* strict NLO EOS rate. Instead we isolate the exactly order-truncated **low-scale effective-dipole squared-amplitude sector** using the real A1M/SuperIso C0b/C1b outputs, matched source \(\alpha_s(\mu_b)\), and an explicit \(\mathcal O(\alpha_s)\) projector.

The source-derived decomposition for real coefficients is

\[
\begin{aligned}
c_0 &= C_{7,\rm SM}^{(0)}+\Delta C_7^{(0)},\\
c_1 &= C_{7,\rm SM}^{(1)}+\Delta C_7^{(1)},\\
|c_0+a_b c_1|^2
&= c_0^2+2a_b c_0 c_1 +a_b^2c_1^2.
\end{aligned}
\]

All \(C_7\) in this expression mean **effective** coefficients output by the isolated A1M source, including any four-quark-to-dipole mixing accounted for by its evolution. The NP-minus-SM projector is always formed by subtracting the corresponding order-matched SM expression, not by dropping the SM NLO term.

In particular the strictly order-\(\alpha_s\) change caused by high-scale **NLO matching**, relative to exactly the same NLO RG evolution with LO high-scale BSM matching, is

\[
\Delta Q_7^{\rm matching,NLO}
=2a_b \big[C^{(0)}_{7,\rm SM}+\Delta C_7^{(0)}\big]\,
   \big[\Delta C_{7,\rm full\ highNLO}^{(1)} -
        \Delta C_{7,\rm LO\ high}^{(1)}\big].
\]

The program resolves this into (i) source NLO C7/C8 high-scale matching and (ii) extra NLO four-quark-matching-induced low C7eff, using the F3 modes 0/1/2. Its reported \(a_b^2\) term is only a **partial** formally NNLO squared-dipole term; it is not a calculation of the full NNLO corrections and cannot be used to estimate missing theory errors.

This quantity \(Q_7\) is **dimensionless** and is **not an absolute branching ratio**. The observable's NLO matrix elements, bremsstrahlung, finite four-quark scheme, HQE terms, normalization, and higher-order pieces have not been incorporated. Unlike the F4 EOS-rate pilot, F4b's core projector requires **no EOS Python package**; the prior F4 run itself still requires EOS and must match source fingerprints.

## B. Source and provenance safeguards

1. Recheck existing pinned A1M \`wilson.c\`, \`bsgamma.c\`, source provenance, six effective-dipole rotations, and full F4 status/cohort.
2. Compare prior F4 SHA256 hashes for the **compiled A1M library** and **F3 RG C probe source** to their current files. Reject source/binary changes.
3. Build a small new **C source probe** linked to the same A1M library; record \(\alpha_s(160),\alpha_s(4.2),m_t(160)\) from SuperIso *itself* rather than borrowing flavio's \(\alpha_s\). Record the difference from F4 flavio \(\alpha_s(4.2)\).
4. Compile the unchanged F3 source-RG probe again in a fresh F4b output directory. Read all 24 mode/operator rows per benchmark, and fail on nonfinite, missing, or nonmatching LO/SM coefficients across source matching modes.
5. Require exactly eight pure Type-II controls: masses 300, 580, 670, 1000 GeV for each \(\tan\beta=5.6,50\). **No Zee spectrum or new scan.**
6. At each point calculate LO dipole projector, NLO RG-induced term, NLO dipole-matching term, NLO four-quark-matching-induced term, strict LO+NLO projector, and the *partial* squared NLO-dipole remainder.
7. Separate independent HEPfit high-scale check: use the prior A1P **immutable original source blob** \`8029be52c3e2f83490dfe3199f80e5db484dd23b\`, generated GPL harness and prior SHA manifest. Compare exactly 8 × 5 = 40 coefficients: LO C7/C8 and NLO C4/C7/C8 at the **new** \(\mu_W=160\) GeV and \(\tan\beta=5.6,50\) with the source-evaluated \(m_t(\mu_W)\). Do not conflate this with independent RG or rate checking. The earlier HEPfit NNLO C3–C6 and C8 convention discrepancy remains open.

## C. Exact AF commands

Run only from the repository under \`/home\`:

~~~bash
set -o pipefail
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source .venv-flavor-f1/bin/activate
python -m pip check

python -m py_compile \
  scripts/zee_gateF4b_fixed_order_dipole_projector.py \
  scripts/zee_gateF4b_hepfit_matching_8.py \
  tests/test_zee_gateF4b_fixed_order_dipole.py \
  tests/test_zee_gateF4b_hepfit_matching_8.py

python -m unittest discover -s tests \
  -p 'test_zee_gateF4b_*.py' -v

python -u scripts/zee_gateF4b_fixed_order_dipole_projector.py \
  --vendor-root work/gateA1m_isolated_nlo_v1/isolated_superiso \
  --a1m-provenance work/gateA1m_isolated_nlo_v1/source_patch_provenance.json \
  --f4-summary work/gateF4_typeII_basis_inverse_8_v1/summary.json \
  --output-dir work/gateF4b_dipole_order_8_v1 \
  2>&1 | tee work/gateF4b_dipole_order_8_v1.log

cat work/gateF4b_dipole_order_8_v1/summary.json
cat work/gateF4b_dipole_order_8_v1/F4b_8_TypeII_fixed_order_C7eff_projector.csv
~~~

Only after that first F4b status is correct, run the **independent matching** component. The A1P existing directory must still contain its real HEPfit binary, source, and provenance. F4b uses the exact source fingerprint and detects missing GSL/OpenBLAS shared libraries without modifying the original matching source. It can recover the previous AF runtime library path list from that directory; any unexpected/missing library stops the comparison.

~~~bash
python -u scripts/zee_gateF4b_hepfit_matching_8.py \
  --f4b-summary work/gateF4b_dipole_order_8_v1/summary.json \
  --a1p-existing-dir work/gateA1p_hepfit_typeii_v1 \
  --output-dir work/gateF4b_independent_hepfit_8_v1 \
  2>&1 | tee work/gateF4b_independent_hepfit_8_v1.log

cat work/gateF4b_independent_hepfit_8_v1/summary.json
cat work/gateF4b_independent_hepfit_8_v1/F4b_independent_TypeII_LO_NLO_matching_40.csv
~~~

## D. Return these results

Return the full \`unittest\` lines and both F4b status lines, the summary sections \`source_running_parameters\`, \`num_typeII_controls\`, \`worst_relative_residual\` and \`matching_disagreements\`, and the 8-row dipole CSV plus any failing rows from the 40-row HEPfit comparison. Keep both full \`summary.json\` files on AF for provenance. If anything fails, **do not** rerun in the same nonempty directory: inspect the error and use a fresh directory after a source-correct fix.

## E. What remains blocked after F4b

- The **full inclusive EOS v1.1 observable** still needs a source-pinned, independently tested strict \(\mathcal O(\alpha_s)\) extraction including NLO matrix elements, bremsstrahlung and any HQE/radiative improvement effects. The EOS v1.1 Git blob for \`inclusive-b-to-s-gamma.cc\` is \`3bbb034b920709503b767fb372f35338ae427877\`, but the AF-installed EOS 1.1 binary has not been mapped to that exact build source.
- The finite renormalization/evanescent-operator convention connecting A1M standard-basis C3..C6 and EOS WET input still requires an independent review; effective-dipole inverse algebra alone is insufficient.
- Source-matched \(\alpha_s\) is required for the strict projector, and \(\alpha_s\) differences with EOS/flavio must be characterized before mixing normalizations or interpreting a \(\Delta\mathrm{BR}\).
- Scale variation \((\mu_W,\mu_b)\) requires rerunning both the matching and the RG with consistent running masses and \(\alpha_s\), not just varying one program's scale parameter.
- An independently source-validated **Type-II NLO rate curve**, nuisance treatment, and theory error are prerequisites for a physical Zee likelihood. Reproducing the historical **NNLO** 580 GeV bound is a separate, future problem.
- Neutrino/LFV, HiggsTools, EWPO, vacuum, full widths and collider checks also remain required for **allowed** Zee points.

**No Type-II or Zee exclusion or 95% CL bound can be quoted from these projections.**
