# Gate B2 — neutrino-compatible Zee Yukawa families for B1 candidates

**Status: implementation committed; AF regression and numerical run pending.**
This is a *partial LFV diagnostic and neutrino algebraic scan*, not
a proof that either candidate is experimentally viable.

## Input evidence from 13 October 2026 AF scan

Gate B1 was executed with 300 samples. It found
- 296 rejected by conservative scalar theory screen,
- 2 rejected by correlated scalar S,T,U Gaussian screen,
- 2 with scalar/EWPO pre-screen pass and algebraic neutrino closure.

One of the two survivors, ID=0, is the deliberately inserted seed.
Only ID=32 was randomly sampled. The 2/300 count is **not a global
acceptance fraction**, and the collider rates below are conditional
on a truncated LO partial-width inventory.

| Feature | Candidate 32 | Candidate 0 |
|---|---:|---:|
| mH1 [GeV] | 208.76954048 | 300 |
| mH2 [GeV] | 681.85192434 | 700 |
| mhheavy [GeV] | 597.71981693 | 580.7 |
| mA [GeV] | 635.22647781 | 633.7 |
| tan(beta) | 5.64746 | 5.59717 |
| gamma [rad] | 1.12012593 | 1.089 |
| Gfitter chi2 | 0.18037 | 0.87262 |
| included-only BR(H2->H1Z) | 0.8077945 | 0.7623963 |
| included-only BR(H1->tb) | 0.8146216 | 0.9559329 |
| production mixing weighted cascade proxy | 0.5332019 | 0.5723167 |
| mu->e gamma selected one-loop squared rate / MEG II limit | 4.17e-5 | 1.01e-5 |

The actual Gate A1V follow-up had
`NUM_FLAVOUR_ONLY_POINTS 2` but did NOT display each point's
`BR(B->Xs gamma)`. The values reside in
`work/gateA1v_B1_flavour/scan_flavour_only.csv`.
No 2026-matched NNLO likelihood or 95% exclusion has been computed.

## Why scanning the leptonic Yukawa family matters

The fixed normal-ordering target from Gate A1B satisfies, in the
chosen Chen Higgs-basis convention,

`Mnu = kappa * [f M_lepton Y + (f M_lepton Y)^T]`.

The antisymmetric `f` has rank 2 and null vector `n`. For any
complex choice `n=(1,x,t)`, solvability requires `n.T Mnu n=0`.
We solve this complex quadratic for x, choose either root, and set
`f = c*[[0,t,-x],[-t,0,1],[x,-1,0]]`.

At fixed nonzero kappa and f, there are only five independent
complex linear equations among the six symmetric entries of Mnu.
The 6x9 linear map has complex rank 5; thus a **four-dimensional
complex homogeneous Yukawa nullspace** survives. Gate B2 correctly
builds `Y = Y_particular + sum(z_i N_i)`, with all four complex
null modes, and checks the exact matrix closure every time.

The scan varies:
- The two real coordinates of complex null-vector parameter `t`,
  with both algebraic roots allowed;
- The absolute f normalization;
- All four complex Yukawa null directions;
- Per-point scalar masses and gamma, entering `kappa`.

The present target neutrino mass matrix is still fixed at the
Gate A1B selected NuFIT-inspired normal-ordering central values,
with fixed Dirac/Majorana phases. Hence **this is NOT a full
neutrino-oscillation likelihood scan**.

## What the LFV score means

The coherent subset includes exactly those contributions already
implemented by Gates A1C–A1F:
- Neutral scalar one-loop dipoles,
- Charged f-only one-loop dipoles,
- Charged doublet-Y one-loop dipoles,
- Partial neutral tree tau->3mu and tau->e mu mu.

The code evaluates each included amplitude consistently at the
individual candidate's mH1/mH2/mhheavy/mA/alpha/beta/gamma.
The diagnostic score is the maximum of selected partial branching
fractions relative to historical/reference published bounds. It
is ONLY a ranking tool. Even a very small score **DOES NOT**
imply experimentally allowed because omitted diagrams can
interfere either constructively or destructively.

Missing calculations include two-loop Barr-Zee (top/bottom,
gauge and scalar), mu->3e, mu-e conversion, charged lepton
universality, EDMs where relevant, full Zee lepton/charged
scalar widths, HiggsTools and precision two-state B->Xs gamma.

## AF execution

```bash
cd /home/aalida/zee
git switch gateA1p-independent-hepfit-typeii-matching
git pull --ff-only

python3 -m unittest discover -s tests \
  -p 'test_gateB2_zee_neutrino_family_scan.py' -v

python3 scripts/gateB2_zee_neutrino_family_scan.py \
  --b1-csv work/gateB1_zee_seed_scan/all_screened_candidates_NOT_ALLOWED.csv \
  --trials-per-candidate 300 \
  --top 10 --seed 20261014 \
  --output-dir work/gateB2_zee_neutrino_family
```

Outputs:
- `ranked_partial_LFV_NOT_ALLOWED.csv`
- `top_neutrino_Yukawa_matrices_NOT_ALLOWED.json`
- `summary.json`

To inspect the SuperIso observable for both candidate points:

```bash
python3 - <<'PY'
import csv
path='work/gateA1v_B1_flavour/scan_flavour_only.csv'
for r in csv.DictReader(open(path)):
    print('mH1',r['mH1'],'mH2',r['mH2'],'gamma',r['gamma'],
          'legacy_bsgamma',r['full_Zee_BR'])
PY
```

Do NOT claim that candidate 32 or 0 is allowed yet.

## Gate B3 priorities

1. Develop and independently validate **complete** Zee amplitudes
   for mu->e gamma including Barr-Zee, mu->3e and mu-e
   conversion; scan Y's complex nullspace and neutrino
   phases simultaneously. Add full lepton decay widths.
2. Implement full Zee scalar + quark + lepton prediction adapter
   for HiggsTools, including both charged mass eigenstates and
   all competitive Higgs decay channels. Document which searches
   are not covered by HiggsTools.
3. Build correlated experimental and theory likelihoods and apply
   them as actual pass/fail criteria, including b->s gamma with
   consistent SM and two-state NP precision and uncertainties.
4. Test global vacuum and broaden scalar parameter sampler to
   discover allowed physical points efficiently.
5. ONLY THEN rank confirmed allowed points by true physical
   BR(H2->H1Z) and the hadronic signal rate.

Sources: Florentino et al. 2106.08332; Herrero-Garcia et al.
1701.05345; Chen 2508.18757; MEG II EPJC 85 (2025) 1177,
BR(mu->e gamma)<1.5e-13 at 90% CL.
