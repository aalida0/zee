# Gate A1K — audit the installed SuperIso 5.0 Type-II/Wilson API

**Status:** READ-ONLY vendor source inspection. No Type-II or Zee physics
calculation is made in this gate. The SuperIso v5.0 SM baseline passed
Gate A1J on AF: BR(B→Xsγ) = 3.382e-4, despite the vendor sm.c ending
in return 1.

The official SuperIso [v5.0 release notes](https://superiso.in2p3.fr/download/)
identify new `scan_coeffs.c` and `predict.c`. The SuperIso [v4.1
manual](https://superiso.in2p3.fr/superiso4.1.pdf) describes its
`thdm.c` Type-I/II/III/IV driver as using 2HDMC for Higgs and
Yukawa inputs; do not assume v5.0 matches that behavior without
inspecting the installed source. In SuperIso, `src/wilson.c` houses
matching and running machinery, while `src/bsgamma.c` evaluates
the observable. We need their exact v5 interfaces.

## AF commands

```bash
cd /home/aalida/zee
git fetch origin gateA1k-superiso-wilson-api-audit
git switch gateA1k-superiso-wilson-api-audit

python3 -m unittest discover -s tests \
  -p 'test_gateA1k_superiso_wilson_source_audit.py' -v

python3 scripts/gateA1k_superiso_wilson_source_audit.py \
  --superiso-dir /home/aalida/opt/zee_tools/SuperIso_v5.0 \
  --output work/gateA1k_superiso_source_audit.json \
  --text-report work/gateA1k_superiso_source_audit.txt

# Short, useful summaries of actual v5 symbols:
grep -E '^(## |SYMBOL |PATTERN |STATUS:)' \
    work/gateA1k_superiso_source_audit.txt | head -n 130
```

Then provide either the report text or selected `src/wilson.c`,
`thdm.c`, `scan_coeffs.c` sections corresponding to charged-Higgs
Wilson matching. The script records source SHA256, line numbers and
bounded snippets without editing or executing vendor files.

## Required physics validation next

1. Establish which parameter/SLHA fields encode Type-II couplings in
   the actual v5 SuperIso source.
2. Validate conventional *single charged* Type-II controls at several
   charged masses and the SM limit using a documented same-SM setup.
3. Identify *all* LO/NLO (and any available NNLO) charged-Higgs
   matching orders contributing to Wilson operators, not just C7/C8.
4. Only then add the Zee `cos²gamma` and `sin²gamma` pieces
   **separately at the matching-amplitude level** and run SuperIso
   perturbative evolution for the *combined coefficients*.
5. Use a clearly defined photon-energy threshold, same perturbative
   conventions, current HFLAV experimental average and theoretical
   uncertainties. Never average two final Type-II branching ratios.

NO model viability claim arises from a source audit. The generic
SuperIso/2HDMC tool interfaces do not automatically implement a
gauge-complete Zee scalar potential or both charged eigenstates.
