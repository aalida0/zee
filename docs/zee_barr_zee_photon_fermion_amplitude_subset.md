# Zee preliminary Barr-Zee fermion–photon dipole amplitudes

**Scope:** preliminary top, bottom and tau photon-mediated Barr–Zee
complex dipole amplitudes, not a complete Zee model LFV rate or
exclusion. The amplitude backend is an explicit opt-in and defaults
OFF pending AF testing.

## Physics source and convention

Sacha Davidson, EPJC 76 (2016) 258, Eqs. (21)-(23):
https://link.springer.com/article/10.1140/epjc/s10052-016-4076-y

For neutral scalar phi=h,H,A and loop fermion f, z=m_f²/m_phi².
The dimensionless f(z) and g(z) follow the independently tested Haber
Barr-Zee loop kernels, already in zee_barr_zee_kernels.py.

Davidson uses an A_L,A_R operator with rate
BR(mu->e gamma)=384 pi² (|A_L|²+|A_R|²).
Herrero-Garcia (2017) uses
BR(l_i->l_j gamma)/BR(l_i->l_j nu nu)=
48 pi³ alpha/G_F² (|C_L|²+|C_R|²).
Conjugating the external field ordering gives
C_X=(4 sqrt(2) G_F/e) conj(A_X).
Therefore Davidson's Eq.(21) becomes

C_X(f,phi) =
 -alpha/(8*pi³ m_parent m_f) * Nc * Q_f²
 * F_X(daughter,parent,phi) * F_X(f,f,phi)
 * [f(z) for h,H; g(z) for A].

In the established general Zee neutral lepton convention from
gateA1d_neutral_tree_lfv.py:
F_L(daughter,parent)=C_phi[daughter,parent],
F_R(daughter,parent)=conj(C_phi[parent,daughter]),
C_A=i Y_ell.
The Type-II-like quark ansatz defines eta_u=cotbeta, eta_d=-tanbeta,
d=beta-alpha. The quark neutral vertices are
F_L(q,h)=mq/v*(cos d - eta_q sin d),
F_L(q,H)=mq/v*(sin d + eta_q cos d).
With the A-field rephasing matching the lepton A coupling,
F_L(t,A)=-i (mt/v)*cotbeta, and
F_L(b,A)=+i (mb/v)*eta_d.
The CP-odd signs must reproduce top H/A constructive and bottom H/A
destructive interference in Davidson's aligned, quasi-degenerate limit.

This quark-plus-general-lepton texture is a phenomenological
Yukawa hypothesis, not a UV symmetry proof.

## What the new backend calculates

- All three radiative channels mu->e gamma, tau->mu gamma,
  tau->e gamma, each with separate complex top, bottom and tau
  fermion–photon Barr-Zee C_L,C_R for h,H,A.
- The existing coherent scalar one-loop C_L,C_R is independently
  recomputed for each saved B2 solution and its branching fraction
  must reproduce that saved B2 rate.
- It computes one-loop-only, fermion-photon-only and
  one-loop-plus-fermion-photon coherent SUBSET branching fractions.
  None is a complete model physical branching fraction.

**Not implemented:** W-loop gauge-complete Barr-Zee, charged-scalar
loops, photon/Z two-loop remainder, scheme-matched heavy fermion
Yukawas, independent full-BSM amplitude benchmark, complete LFV
3-body amplitudes, mu-e conversion and correlated likelihoods.

Never promote an over-limit ratio in the subset calculation to a
full-model exclusion, or a small ratio to an allowed statement.
Missing amplitudes can interfere in either direction.

## AF tests and standalone run (existing 150 solutions)

First update the branch, then test:

    cd /home/aalida/zee
    git switch gateA1p-independent-hepfit-typeii-matching
    git pull --ff-only
    source ~/fccee_zh/scripts/setup_key4hep.sh
    python3 -m unittest discover -s tests -p 'test_zee_barr_zee_fermion_dipoles.py' -v

Reuse the already completed B2 solution database:

    python3 scripts/zee_barr_zee_fermion_dipoles.py \
      --points work/gateB4_zee_adaptive_pilot/diverse_candidates_for_B2_NOT_ALLOWED.csv \
      --b2-json work/zee_pipeline_b4pilot_v2/B2_neutrino/top_neutrino_Yukawa_matrices_NOT_ALLOWED.json \
      --output-dir work/zee_barr_zee_fermion_photon_B4pilot

Expected 30 scalar candidates, 150 Yukawa configurations,
and 450 radiative partial-amplitude diagnostic rows.

The following new tests are committed but not yet run on AF:
- Davidson Eq.21 to Herrero Eq.3.12 dipole prefactor conversion.
- Correct complex chirality and a vanishing flavor-diagonal limit.
- Heavy H/A constructive top and destructive bottom signs.
- B2 independent one-loop rate closure.
- Strict fail-closed inputs and output naming.

Outputs are photon_fermion_BZ_dipoles_ONLY_NOT_ALLOWED.csv,
details_preliminary_NO_FULL_LFV.json and summary.json.

If those regressions pass, the unified scanner exposes optional
barr_zee_fermion_photon_subset.enabled=true in the config.
The flag defaults false and full_LFV.enabled must remain false.

## Next physics gates

First validate the whole finite fermionic amplitude numerically
against a separately published 2HDM point. Then add complete W-loop,
charged-scalar and Z-mediated terms with gauge consistency, and
combine complex amplitudes rather than squared rates. A calibrated
experimental LFV likelihood comes strictly after those steps.
