# Gate A1I: SuperIso mixed-charged matching preflight

This gate is a TOOLING CONTRACT AND LO MATCHING DIAGNOSTIC, not a physical
BR(B->Xs gamma) calculation or a constraint pass.

The A1H point passes the specified correlated scalar-sector STU tests.
However, its Type-II quark sector has TWO charged Higgs bosons with
m(H1+)=300 GeV, m(H2+)=700 GeV, gamma=1.089.
At one LO matching scale, DeltaC7 and DeltaC8 must be combined
LINEARLY at the Wilson level with weights cos(gamma)^2 and
sin(gamma)^2. Gate8a gives DeltaC7=-0.0629608244163 and
DeltaC8=-0.0661219067725 at a fixed mt=172 GeV input.
Neither number alone is a BR or exclusion.

A single Type-II 2HDM charged mass reproducing DeltaC7 would be
551.364 GeV, while that reproducing DeltaC8 would be 563.248 GeV.
These distinct values demonstrate why calling standard SuperIso
2HDM with ONE proxy mass cannot certify the Zee NLO/NNLO prediction.
Averaging two SuperIso BRs is also forbidden.

SuperIso official download: https://superiso.in2p3.fr/download/
Version 5.0 was released November 23, 2025. It provides updated
Wilson-coefficient tools scan_coeffs.c and predict.c, but these
have NOT been audited for direct Zee-model two-state NNLO support.

## Run on the AF

    cd /home/aalida/zee
    git fetch origin gateA1i-superiso-v5-mixed-charged-preflight
    git switch gateA1i-superiso-v5-mixed-charged-preflight
    python3 -m unittest discover -s tests -p 'test_gateA1i_superiso_preflight.py' -v
    python3 scripts/gateA1i_superiso_preflight.py --output work/gateA1i_superiso_preflight.json

If a source tree is available, add:

    --superiso-dir /path/to/superiso_v5.0

The script records hashes and possible C source entry points. It
does not execute unverified binaries, install software or infer support
from names alone.

## Required next physics gate

Audit the actual SuperIso 5.0 C7/C8 LO/NLO/NNLO matching API and
implement BOTH charged masses consistently, then compare to pure
Type-II limits gamma=0 and gamma=pi/2 (and a standalone SM value)
before predicting the physical branching fraction with coherent
uncertainties and current HFLAV data.

References:
- Florentino et al., arXiv:2106.08332.
- SuperIso, https://superiso.in2p3.fr/.
- Gate8a existing local LO Wilson-code tests.

Conclusion: NOT YET a SuperIso physical fit. This gate prevents
mistaking a one-charged-Higgs 2HDM output for a two-charged-Higgs
Zee calculation.
