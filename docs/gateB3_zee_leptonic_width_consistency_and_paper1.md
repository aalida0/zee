# Gate B3 — Physical leptonic-width consistency in the general Zee model

**STATUS: implementation committed, AF tests and B3 output not yet executed.**
This is a prerequisite for the *constraint-only* first paper. It does NOT
imply any allowed benchmark or complete collider branching fraction.

## Why Gate B3 is necessary

Previous Gate 6/B1 partial charged-Higgs widths were computed with a
Type-II **charged-lepton** Yukawa coupling
`y_tau = m_tau * tanbeta/v`. Gate B2 instead solves the general-Zee
neutrino relation using an **independent Higgs-basis leptonic**
Yukawa matrix `Y^ell` and antisymmetric `f`.

These are **different models in the lepton sector**. We cannot
combine a generic `Y^ell` neutrino fit with Type-II tau-nu widths.
Keep the *Type-II-like QUARK Yukawa* hypothesis where justified.
DO NOT simultaneously assume Type-II charged leptons once a
general `Y^ell` is introduced.

From Chen, [arXiv:2508.18757](https://arxiv.org/abs/2508.18757),
Eq.(3)-(6), in the Higgs basis,
```
-L contains sqrt(2) ellbar_R Y^ell nu_L H_D^-
         + 2 nu_L^T C f ell_L chi^+ + h.c.

H1+ = cos(gamma) H_D+ + sin(gamma) chi+
H2+ = -sin(gamma) H_D+ + cos(gamma) chi+
```

Neglecting neutrino masses and charged lepton mass interference, for
each charged lepton `a`,
```
Gamma(H1+ -> l_a+ nu) =
 mH1/(16pi) * [2 cos²gamma sum_i |Y[a,i]|²
             + 4 sin²gamma sum_i |f[i,a]|²] (1-ml_a²/mH1²)²

Gamma(H2+ -> l_a+ nu) =
 mH2/(16pi) * [2 sin²gamma sum_i |Y[a,i]|²
             + 4 cos²gamma sum_i |f[i,a]|²] (1-ml_a²/mH2²)²
```
The two terms couple opposite charged-lepton chiralities; neutrino
masses are neglected. The charged-conjugate width is identical in
the CP-conserving mass spectrum for these summed channels.
**Validate these normalization factors against the gauge-complete
Zee UFO before a physical BR is published.**

This implementation automatically **subtracts/replaces** the
legacy Type-II tau-nu partial width in Gate 6; it never double counts
it. The `f=0, Y_tau=m_tau*tanbeta/v` limit reproduces the old
Type-II tau-width normalization as a unit test.

Saved B2 `f,Y` matrices are revalidated against the same target
complex neutrino mass matrix before widths are computed.

## AF execution

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only
source ~/fccee_zh/scripts/setup_key4hep.sh

python3 -m unittest discover -s tests \
  -p 'test_gateB3_general_zee_charged_lepton_widths.py' -v

python3 scripts/gateB3_general_zee_charged_lepton_widths.py \
  --b1-csv work/gateB1_zee_seed_scan/all_screened_candidates_NOT_ALLOWED.csv \
  --b2-json work/gateB2_zee_neutrino_family/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json \
  --top 10 \
  --output-dir work/gateB3_zee_leptonic_widths
```

Output:
- `cascade_width_corrected_NOT_ALLOWED.csv`:
  each benchmark B2 Yukawa solution's mass, new included-only
  cascade BR and production-weighted proxy.
- `all_width_details_NOT_ALLOWED.json`:
  flavor-resolved `e,mu,tau` widths of H1 and H2, all original
  included bosonic/quark widths, the old Type-II tau numbers for
  transparent comparison and neutrino closure.

The current code assumes B1's *fixed* singlet quartics
lambdaC,k1,k2,k12; if they are later scanned they MUST be serialized
in B1 and ingested here rather than reconstructed from defaults.

The revised cascade fractions remain conditional on included LO
channels. Higher-order QCD, off-shell, model-complete decay inventories,
HiggsTools direct searches and full flavor observables are not present.

## How this supports Paper 1, without Delphes

**Proposed paper question:** Under a self-consistent neutrino and
quark/flavor parameter point, how much of the H2 -> H1 Z rate remains,
and which present/future measurements eliminate its parameter regions?

Required physics deliverables for a standalone paper:

1. **Sequential constraint ablation and allowed-envelope plot**:
   maximum [sigma(tbH2) x BR(H2->H1Z) x BR(H1->tb)]
   versus masses before/after neutrino, full LFV, HiggsTools, EWPO,
   theory and scheme-consistent b->s gamma requirements.
   Distinguish a real rate from the sin²gamma mixing *proxy*.
2. **Flavor–cascade complementarity plots**:
   conditional cascade BR/rate against mu->e gamma, mu->3e,
   mu-e conversion, tau LFV and neutrino parameters.
   Verify whether any correlation survives marginalization over
   the four complex neutrino-compatible Yukawa directions.
3. **Current vs projected experimental reach** using
   independently sourced and dated assumptions for Mu3e,
   MEG II, COMET/Mu2e, Belle II and LHC Higgs searches.
4. **Robustness tests**:
   both neutrino orderings, oscillation covariance ranges,
   variable CP phases and lepton Yukawa textures; checked
   gauge-consistent quark flavor hypothesis; potential/global
   vacuum constraints; full perturbative/hadronic uncertainties.
5. **Public reproducible benchmark table**, with explicit
   probability meaning of allowed regions and full width budget.

Relevant PRIOR work and limits on novelty:
- [Florentino–Romão–Silva, EPJC 81 1148 (2021)](
  https://doi.org/10.1140/epjc/s10052-021-09956-2): the
  H2->H1Z collider concept, scalar constraints, HiggsSignals/Bounds,
  B->Xs gamma and qualitative connection of neutrino mass scale
  to charged mixing are ALREADY known.
- [Herrero-García et al., JHEP 04 (2017) 130](
  https://doi.org/10.1007/JHEP04(2017)130): full general Zee neutrino
  and LFV studies, including two-loop Barr-Zee, ALREADY exist.
- [Aristizabal Sierra–Restrepo, JHEP 08 (2006) 036](
  https://arxiv.org/abs/hep-ph/0604012): charged-scalar leptonic
  decays as probes of neutrino mass are also established.
- [Heeck–Thapa, Phys Lett B 841 (2023) 137910](
  https://doi.org/10.1016/j.physletb.2023.137910): newer Zee LFV work.

The publishable question is therefore the **joint quantitative
cascade-signal envelope** and experimental complementarity,
not the Zee neutrino relation, the Z off-diagonal vertex, a standalone
neutrino/LFV scan or the charged leptonic width formula.

## Most consequential STOP issue: common symmetry assumptions

Florentino et al. explicitly noted the generic tension between a
strict Z2 symmetry protecting Type-II quark Yukawas and unrestricted
general lepton-sector Zee Yukawas. Before calling the points fully
physical, specify how the quark Yukawa ansatz is protected or justified
under radiative corrections; check any induced wrong-doublet couplings.
The present Type-II-like quark matching is a phenomenological
ansatz, not a UV-proven symmetry construction.

## Other mandatory blockers

- Full LFV amplitudes and calibrated likelihood, not B2 partial scores
  (especially Barr-Zee and mu->3e, mu-e conversion).
- Model-specific neutrino parameters with full oscillation/cosmology
  likelihood and both orderings; not just one fixed Mnu.
- **2026** NNLO-consistent b->s gamma prediction and uncertainties:
  [Misiak et al. arXiv:2608.29863](
  https://arxiv.org/abs/2608.29863). Current legacy SuperIso
  A1V grid values are NOT an exclusion decision.
- Model-complete neutral and charged widths and HiggsTools
  (correct treatment of two charged states and missing searches).
- Global-vacuum scan and parameter sampling broader than the narrow
  2021-inspired slice.

**No standalone first-paper submission until at least one robust
new constraint/viable-envelope conclusion is demonstrated.**
